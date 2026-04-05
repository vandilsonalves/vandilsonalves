# /app/backend/middleware/metrics_middleware.py
"""
Middleware para coleta automática de métricas de requisições
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, metrics_collector):
        super().__init__(app)
        self.metrics_collector = metrics_collector
    
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in ["/api/health", "/health"] or path.startswith("/uploads"):
            return await call_next(request)
        
        # Track unique visitors (by IP + User-Agent hash per day)
        if not path.startswith("/api/admin") and request.method == "GET":
            try:
                from config import db as _db
                import hashlib
                from datetime import datetime, timezone
                client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
                ua = request.headers.get("user-agent", "")
                visitor_hash = hashlib.sha256(f"{client_ip}:{ua}".encode()).hexdigest()
                hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                await _db.visitas_diarias.update_one(
                    {"data": hoje},
                    {"$addToSet": {"visitors": visitor_hash}, "$inc": {"total_hits": 1}},
                    upsert=True
                )
            except Exception:
                pass
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            self.metrics_collector.record_request(
                path=path,
                method=request.method,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            
            self.metrics_collector.record_request(
                path=path,
                method=request.method,
                status_code=500,
                duration=duration
            )
            
            raise e
