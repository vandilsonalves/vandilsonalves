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
        self.user_requests_min = defaultdict(list)    # per-minute window
        self.user_requests_day = defaultdict(list)    # per-day window
        self.anon_requests = defaultdict(list)
        self.blocked = {}  # key -> unblock_time (10 min ban)

    def _cleanup(self, bucket, key, window):
        now = time.time()
        bucket[key] = [t for t in bucket[key] if t > now - window]

    def is_blocked(self, key: str) -> bool:
        if key in self.blocked:
            if time.time() < self.blocked[key]:
                return True
            del self.blocked[key]
        return False

    def block(self, key: str, duration: int = 600):
        self.blocked[key] = time.time() + duration

    def check_user(self, user_id: str, max_per_min: int = 100, max_per_day: int = 1000) -> tuple:
        """Retorna (bloqueado: bool, motivo: str)"""
        if self.is_blocked(user_id):
            return True, "block"

        now = time.time()

        # Per-minute check
        self._cleanup(self.user_requests_min, user_id, 60)
        if len(self.user_requests_min[user_id]) >= max_per_min:
            self.block(user_id, 600)  # 10 min ban
            logger.warning(f"[RATE LIMIT] User {user_id[:8]}... BLOQUEADO 10min (>{max_per_min}/min)")
            return True, "minute"

        # Per-day check
        self._cleanup(self.user_requests_day, user_id, 86400)
        if len(self.user_requests_day[user_id]) >= max_per_day:
            return True, "day"

        self.user_requests_min[user_id].append(now)
        self.user_requests_day[user_id].append(now)
        return False, ""

    def check_anon(self, fingerprint: str, max_req: int = 30, window: int = 60) -> bool:
        """Rate limit para requisições anônimas (sem token) - mais restritivo"""
        if self.is_blocked(fingerprint):
            return True
        self._cleanup(self.anon_requests, fingerprint, window)
        if len(self.anon_requests[fingerprint]) >= max_req:
            self.block(fingerprint, 600)
            return True
        self.anon_requests[fingerprint].append(time.time())
        return False


rate_limiter = UserRateLimiter()


# ==================== ANTI-BOT / SCRAPING DETECTOR ====================

class SuspiciousActivityTracker:
    """Detecta padrões de scraping e uso abusivo"""

    def __init__(self):
        self.request_times = defaultdict(list)     # user -> [timestamps]
        self.sequential_access = defaultdict(list)  # user -> [(time, path)]
        self.blocked_users = {}                     # user -> unblock_time

    def track(self, user_id: str, path: str) -> bool:
        """Retorna True se comportamento suspeito detectado"""
        now = time.time()

        # Verificar se está bloqueado
        if user_id in self.blocked_users:
            if now < self.blocked_users[user_id]:
                return True
            del self.blocked_users[user_id]

        # 1. Detectar intervalos < 50ms (bot behavior - mais rigoroso que navegação normal)
        self.request_times[user_id] = [
            t for t in self.request_times[user_id] if t > now - 10
        ]
        if len(self.request_times[user_id]) >= 5:
            intervals = [
                self.request_times[user_id][i] - self.request_times[user_id][i-1]
                for i in range(1, len(self.request_times[user_id]))
            ]
            fast_requests = sum(1 for gap in intervals if gap < 0.05)
            if fast_requests >= 8:
                self.blocked_users[user_id] = now + 600  # block 10 min
                logger.warning(f"[ANTI-BOT] Bot detectado: {user_id[:8]}... - {fast_requests} reqs < 50ms em 10s")
                return True
        self.request_times[user_id].append(now)

        # 2. Detectar paginação sequencial abusiva (>15 pages em 60s)
        self.sequential_access[user_id] = [
            (t, p) for t, p in self.sequential_access[user_id] if t > now - 60
        ]
        self.sequential_access[user_id].append((now, path))

        recent_paths = [p for _, p in self.sequential_access[user_id]]
        page_requests = sum(1 for p in recent_paths if "page=" in p)
        if page_requests > 15:
            self.blocked_users[user_id] = now + 600  # block 10 min
            logger.warning(f"[ANTI-BOT] Scraping detectado: {user_id[:8]}... - {page_requests} paginacoes em 60s")
            return True

        return False


activity_tracker = SuspiciousActivityTracker()


# ==================== TOKEN BLACKLIST ====================

class TokenBlacklist:
    """Blacklist em memória para tokens invalidados (refresh rotation)"""

    def __init__(self):
        self.blacklisted = {}  # token_hash -> expiry_time

    def add(self, token: str, ttl: int = 700):
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        self.blacklisted[token_hash] = time.time() + ttl

    def is_blacklisted(self, token: str) -> bool:
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        if token_hash in self.blacklisted:
            if time.time() < self.blacklisted[token_hash]:
                return True
            del self.blacklisted[token_hash]
        return False

    def cleanup(self):
        now = time.time()
        expired = [k for k, v in self.blacklisted.items() if v < now]
        for k in expired:
            del self.blacklisted[k]


token_blacklist = TokenBlacklist()


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


# ==================== PUBLIC PATHS ====================

PUBLIC_PATHS = [
    "/api/auth/login", "/api/auth/register", "/api/auth/cadastro",
    "/api/auth/recuperar-senha", "/api/auth/login-emergencia",
    "/api/auth/refresh",
    "/api/register", "/api/login", "/api/rbac/login",
    "/api/health", "/api/health/detailed",
    "/api/webhook/pix", "/api/whatsapp/webhook",
    "/api/strava/callback", "/api/strava/sync-status",
    "/api/cloud-files/", "/api/storage/health",
    "/api/uploads/",
    "/api/temporadas/ativa", "/api/temporadas/historico", "/api/temporadas/",
    "/api/financeiro/config-precos-publico",
    "/api/pagamento/status", "/api/planos",
    "/api/regulamento", "/api/termo-avaliacao",
    "/api/configuracoes/regras",
    "/api/parceiros",
    "/api/corridas-eventos/template",
    "/api/corridas-eventos",
    "/api/corridas-parceiras/config", "/api/corridas-parceiras",
    "/api/assessorias/lista",
    "/api/ranking-corridas/stats", "/api/ranking-corridas/estados", "/api/ranking-corridas/cidades",
    "/api/premiacao/ativas", "/api/premiacao/todas", "/api/premiacao/status",
    "/api/premiacao/p/",
    "/api/conquistas/disponiveis",
    "/api/feed/reacoes-disponiveis",
    "/api/indicacao/verificar-codigo/", "/api/indicacao/registrar",
    "/api/admin/mensagens/arquivo/", "/api/admin/autorizacoes/mensagens/arquivo/",
    "/api/admin/avaliacoes/termo",
    "/api/efi/pagamento/status",
]


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
        raw_token = None

        if auth_header.startswith("Bearer "):
            raw_token = auth_header[7:]
            user_id = self._extract_user_id(raw_token)
        elif token_param:
            raw_token = token_param
            user_id = self._extract_user_id(raw_token)

        # 1b. Check token blacklist
        if raw_token and token_blacklist.is_blacklisted(raw_token):
            return JSONResponse(
                status_code=401,
                content={"detail": "Token invalidado. Faca login novamente."},
            )

        # 2. Rate limit
        if user_id:
            blocked, reason = rate_limiter.check_user(user_id, max_per_min=100, max_per_day=1000)
            if blocked:
                retry = "600" if reason == "block" else ("30" if reason == "minute" else "3600")
                msg = {
                    "block": "Acesso temporariamente bloqueado por uso excessivo. Tente novamente em 10 minutos.",
                    "minute": "Limite de requisicoes por minuto atingido. Aguarde.",
                    "day": "Limite diario de requisicoes atingido (1000/dia)."
                }.get(reason, "Limite atingido.")
                logger.warning(f"[RATE LIMIT] User {user_id[:8]}... - {reason} em {path}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": msg},
                    headers={"Retry-After": retry},
                )
        else:
            # Anônimo: 30 req/min (restritivo)
            fp = hashlib.md5(
                f"{request.headers.get('user-agent', '')}{request.headers.get('accept-language', '')}".encode()
            ).hexdigest()[:12]

            is_public = any(path.startswith(p) for p in PUBLIC_PATHS)

            if is_public and rate_limiter.check_anon(fp, max_req=30, window=60):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Muitas requisicoes. Faca login para continuar."},
                    headers={"Retry-After": "60"},
                )

        # 3. Anti-scraping + anti-bot (apenas em rotas de ranking/dados competitivos)
        if user_id and any(x in path for x in ["/ranking", "/liga-assessorias", "/strava-atividades", "/badges/ranking"]):
            if activity_tracker.track(user_id, str(request.url)):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Atividade suspeita detectada. Acesso temporariamente limitado."},
                    headers={"Retry-After": "600"},
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
