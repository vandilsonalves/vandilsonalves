# /app/backend/security_middleware.py
# Camada de segurança para produção - Ranking Run Pro

import time
import hashlib
import os
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

ALLOWED_ORIGINS = set(
    os.environ.get("CORS_ORIGINS", "https://app.rankingrun.com.br").split(",")
)


# ==================== RATE LIMITER POR USUARIO ====================

class UserRateLimiter:
    """Rate limit por token/usuario - NÃO por IP (evita bloqueio atrás de proxy)"""

    def __init__(self):
        self.user_requests = defaultdict(list)
        self.anon_requests = defaultdict(list)

    def _cleanup(self, bucket, key, window):
        now = time.time()
        bucket[key] = [t for t in bucket[key] if t > now - window]

    def check_user(self, user_id: str, max_req: int = 120, window: int = 60) -> bool:
        """Retorna True se bloqueado"""
        self._cleanup(self.user_requests, user_id, window)
        if len(self.user_requests[user_id]) >= max_req:
            return True
        self.user_requests[user_id].append(time.time())
        return False

    def check_anon(self, fingerprint: str, max_req: int = 30, window: int = 60) -> bool:
        """Rate limit para requisições anônimas (sem token) - mais restritivo"""
        self._cleanup(self.anon_requests, fingerprint, window)
        if len(self.anon_requests[fingerprint]) >= max_req:
            return True
        self.anon_requests[fingerprint].append(time.time())
        return False


rate_limiter = UserRateLimiter()


# ==================== SUSPICIOUS ACTIVITY DETECTOR ====================

class SuspiciousActivityTracker:
    """Detecta padrões de scraping e uso abusivo"""

    def __init__(self):
        self.sequential_access = defaultdict(list)  # user -> [paths]
        self.blocked_users = {}  # user -> unblock_time

    def track(self, user_id: str, path: str) -> bool:
        """Retorna True se comportamento suspeito detectado"""
        now = time.time()

        # Verificar se está bloqueado
        if user_id in self.blocked_users:
            if now < self.blocked_users[user_id]:
                return True
            del self.blocked_users[user_id]

        # Rastrear sequência de acessos (últimos 60s)
        self.sequential_access[user_id] = [
            (t, p) for t, p in self.sequential_access[user_id] if t > now - 60
        ]
        self.sequential_access[user_id].append((now, path))

        # Detectar paginação sequencial abusiva (>10 pages em 60s)
        recent_paths = [p for _, p in self.sequential_access[user_id]]
        page_requests = sum(1 for p in recent_paths if "page=" in p)
        if page_requests > 15:
            self.blocked_users[user_id] = now + 300  # block 5 min
            logger.warning(f"[SECURITY] Scraping detectado: {user_id} - {page_requests} paginações em 60s")
            return True

        return False


activity_tracker = SuspiciousActivityTracker()


# ==================== MAIN SECURITY MIDDLEWARE ====================

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers.append("X-Content-Type-Options", "nosniff")
        response.headers.append("X-Frame-Options", "DENY")
        response.headers.append("X-XSS-Protection", "1; mode=block")
        response.headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.append("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.append("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

        # Cache control para API
        path = request.url.path
        if "/api/" in path:
            if any(x in path for x in ["/admin/", "/auth/", "/efi/", "/pagamentos/"]):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
                response.headers["Pragma"] = "no-cache"
            else:
                response.headers["Cache-Control"] = "private, max-age=15"

        return response


# ==================== API PROTECTION MIDDLEWARE ====================

class APIProtectionMiddleware(BaseHTTPMiddleware):
    """Proteção avançada: rate limit por usuario, anti-scraping, validação de origin"""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip non-API, OPTIONS, health, websocket
        if not path.startswith("/api/") or request.method == "OPTIONS":
            return await call_next(request)
        if path in ["/api/health", "/api/ws/notifications"]:
            return await call_next(request)
        if "/ws/" in path:
            return await call_next(request)

        # 1. Extrair identidade do usuario do token (se presente)
        auth_header = request.headers.get("authorization", "")
        token_param = request.query_params.get("token", "")
        user_id = None

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            user_id = self._extract_user_id(token)
        elif token_param:
            user_id = self._extract_user_id(token_param)

        # 2. Rate limit
        if user_id:
            # Usuário autenticado: 120 req/min (generoso)
            if rate_limiter.check_user(user_id, max_req=120, window=60):
                logger.warning(f"[RATE LIMIT] User {user_id[:8]}... em {path}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Limite de requisicoes atingido. Aguarde um momento."},
                    headers={"Retry-After": "30"},
                )
        else:
            # Anônimo: 30 req/min (restritivo)
            fp = hashlib.md5(
                f"{request.headers.get('user-agent', '')}{request.headers.get('accept-language', '')}".encode()
            ).hexdigest()[:12]

            # Endpoints públicos que anônimos podem acessar
            public_paths = [
                "/api/temporadas/", "/api/financeiro/config-precos-publico",
                "/api/ranking/povao/stats", "/api/efi/pagamento/status",
                "/api/auth/login", "/api/auth/cadastro",
                "/api/corridas-eventos", "/api/ranking-corridas",
            ]
            is_public = any(path.startswith(p) for p in public_paths)

            if is_public and rate_limiter.check_anon(fp, max_req=30, window=60):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Muitas requisicoes. Faca login para continuar."},
                    headers={"Retry-After": "60"},
                )

        # 3. Anti-scraping (paginação sequencial)
        if user_id and "page=" in str(request.url.query):
            if activity_tracker.track(user_id, str(request.url)):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Atividade suspeita detectada. Acesso temporariamente limitado."},
                    headers={"Retry-After": "300"},
                )

        return await call_next(request)

    def _extract_user_id(self, token: str) -> str:
        """Extrai user_id do JWT sem validar (apenas para rate limit)"""
        try:
            import base64, json
            parts = token.split(".")
            if len(parts) != 3:
                return None
            payload = parts[1] + "=" * (4 - len(parts[1]) % 4)
            data = json.loads(base64.urlsafe_b64decode(payload))
            return data.get("sub")
        except Exception:
            return None
