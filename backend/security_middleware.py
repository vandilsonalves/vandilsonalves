# /app/backend/security_middleware.py
# Middleware de segurança para produção - Ranking Run Pro

import time
import os
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# ==================== RATE LIMITER ====================

class RateLimitStore:
    """Armazena contadores de requisições por IP em memória"""
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_rate_limited(self, ip: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        now = time.time()
        cutoff = now - window_seconds
        # Limpar requisições antigas
        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
        if len(self.requests[ip]) >= max_requests:
            return True
        self.requests[ip].append(now)
        return False
    
    def get_remaining(self, ip: str, max_requests: int = 60, window_seconds: int = 60) -> int:
        now = time.time()
        cutoff = now - window_seconds
        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
        return max(0, max_requests - len(self.requests[ip]))


rate_limit_store = RateLimitStore()

# Limites por tipo de rota
RATE_LIMITS = {
    "default": (200, 60),      # 200 req/min geral
    "auth": (30, 60),          # 30 tentativas de login/min por IP
    "export": (15, 60),        # 15 exports/min
    "api_heavy": (120, 60),    # 120 req/min para rotas pesadas
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown").split(",")[0].strip()
        path = request.url.path
        
        # Determinar limite baseado na rota
        if "/auth/login" in path or "/auth/register" in path or "/auth/cadastro" in path:
            max_req, window = RATE_LIMITS["auth"]
        elif "/exportar" in path or "/export" in path:
            max_req, window = RATE_LIMITS["export"]
        elif "/ranking/" in path or "/dashboard/" in path:
            max_req, window = RATE_LIMITS["api_heavy"]
        else:
            max_req, window = RATE_LIMITS["default"]
        
        if rate_limit_store.is_rate_limited(ip, max_req, window):
            remaining = 0
            logger.warning(f"[RATE LIMIT] IP {ip} bloqueado em {path} ({max_req} req/{window}s)")
            return JSONResponse(
                status_code=429,
                content={"detail": "Muitas requisições. Tente novamente em alguns instantes."},
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(max_req),
                    "X-RateLimit-Remaining": "0",
                }
            )
        
        remaining = rate_limit_store.get_remaining(ip, max_req, window)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_req)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


# ==================== SECURITY HEADERS ====================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Cache control para API
        if "/api/" in request.url.path:
            if any(x in request.url.path for x in ["/admin/", "/auth/", "/efi/", "/pagamentos/"]):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            else:
                response.headers["Cache-Control"] = "public, max-age=30, s-maxage=60"
        
        # Remover headers que expõem informações do servidor
        if "server" in response.headers:
            del response.headers["server"]
        
        return response
