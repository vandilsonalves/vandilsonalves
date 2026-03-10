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
        # Ignorar endpoints de health check e static files para não poluir métricas
        path = request.url.path
        if path in ["/api/health", "/health"] or path.startswith("/uploads"):
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Registrar métrica
            self.metrics_collector.record_request(
                path=path,
                method=request.method,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            
            # Registrar erro
            self.metrics_collector.record_request(
                path=path,
                method=request.method,
                status_code=500,
                duration=duration
            )
            
            raise e
