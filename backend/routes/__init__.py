# /app/backend/routes/__init__.py
# Exporta todos os routers

from .auth import router as auth_router
from .rbac import router as rbac_router

# Lista de todos os routers para registro
all_routers = [
    (auth_router, "/api"),
    (rbac_router, "/api"),
]
