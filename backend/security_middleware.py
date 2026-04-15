# /app/backend/security_middleware.py
# Middleware de segurança para produção - Ranking Run Pro

import os
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


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
