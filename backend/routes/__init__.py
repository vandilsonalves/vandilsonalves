# /app/backend/routes/__init__.py
# Exporta todos os routers modulares
#
# STATUS: 7 routers ATIVOS
# Refatoração em andamento - endpoints podem existir duplicados no server.py

# Routers ativos
from .rbac import router as rbac_router
from .auth_routes import router as auth_routes_router, get_current_user, get_admin_user
from .notificacoes_routes import router as notificacoes_router, criar_notificacao
from .conquistas_routes import router as conquistas_router, verificar_conquistas
from .atletas_routes import router as atletas_router
from .resultados_routes import router as resultados_router
from .ranking_routes import router as ranking_router

# Lista de todos os routers para registro
all_routers = [
    (rbac_router, "/api"),
    (auth_routes_router, "/api"),
    (notificacoes_router, "/api"),
    (conquistas_router, "/api"),
    (atletas_router, "/api"),
    (resultados_router, "/api"),
    (ranking_router, "/api"),
]
