# /app/backend/routes/__init__.py
# Exporta todos os routers modulares
#
# NOTA: Os módulos estão prontos mas ainda não foram ativados no server.py
# para evitar duplicação de endpoints. Ativar gradualmente conforme
# os endpoints correspondentes forem removidos do server.py.

# Módulos ativos
from .rbac import router as rbac_router

# Módulos prontos (não ativados ainda - importados para referência)
from .auth_routes import router as auth_routes_router, get_current_user, get_admin_user
from .notificacoes_routes import router as notificacoes_router, criar_notificacao
from .conquistas_routes import router as conquistas_router, verificar_conquistas
from .atletas_routes import router as atletas_router
from .resultados_routes import router as resultados_router

# Lista de todos os routers para registro
all_routers = [
    # Ativos
    (rbac_router, "/api"),
    
    # Prontos para ativação (remover do comentário quando endpoints forem removidos do server.py)
    # (auth_routes_router, "/api"),
    # (notificacoes_router, "/api"),
    # (conquistas_router, "/api"),
    # (atletas_router, "/api"),
    # (resultados_router, "/api"),
]
