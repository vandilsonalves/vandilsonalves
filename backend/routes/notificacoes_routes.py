# /app/backend/routes/notificacoes_routes.py
# Módulo de Notificações

from fastapi import APIRouter, Depends

from config import db
from models import Notificacao
from routes.auth_routes import get_current_user

router = APIRouter(tags=["Notificações"])


# ==================== NOTIFICAÇÕES ENDPOINTS ====================

@router.get("/notificacoes")
async def get_notificacoes(current_user: dict = Depends(get_current_user)):
    """Retorna notificações do usuário"""
    notificacoes = await db.notificacoes.find(
        {"usuario_id": current_user["id"]},
        {"_id": 0}
    ).sort("data_criacao", -1).limit(50).to_list(None)
    
    nao_lidas = sum(1 for n in notificacoes if not n.get("lida", False))
    
    return {
        "notificacoes": notificacoes,
        "nao_lidas": nao_lidas
    }


@router.post("/notificacoes/{notificacao_id}/ler")
async def marcar_notificacao_lida(notificacao_id: str, current_user: dict = Depends(get_current_user)):
    """Marca notificação como lida"""
    await db.notificacoes.update_one(
        {"id": notificacao_id, "usuario_id": current_user["id"]},
        {"$set": {"lida": True}}
    )
    return {"message": "Notificação marcada como lida"}


@router.post("/notificacoes/ler-todas")
async def marcar_todas_lidas(current_user: dict = Depends(get_current_user)):
    """Marca todas notificações como lidas"""
    await db.notificacoes.update_many(
        {"usuario_id": current_user["id"]},
        {"$set": {"lida": True}}
    )
    return {"message": "Todas notificações marcadas como lidas"}


# ==================== HELPER FUNCTION ====================

async def criar_notificacao(usuario_id: str, tipo: str, titulo: str, mensagem: str, dados_extras: dict = {}):
    """Helper para criar notificação"""
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        dados_extras=dados_extras
    )
    await db.notificacoes.insert_one(notificacao.model_dump())
    return notificacao
