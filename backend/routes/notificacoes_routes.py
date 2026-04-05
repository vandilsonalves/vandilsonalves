# /app/backend/routes/notificacoes_routes.py
# Módulo de Notificações

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from config import db
from models import Notificacao
from routes.auth_routes import get_current_user

router = APIRouter(tags=["Notificações"])


# ==================== MODELOS ====================

class EnviarMensagemRequest(BaseModel):
    destinatarios: List[str]  # Lista de IDs de usuários
    mensagem: str
    tipo: str = "mensagem_assessoria"
    titulo: str = ""


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


@router.post("/notificacoes/enviar")
async def enviar_mensagem(request: EnviarMensagemRequest, current_user: dict = Depends(get_current_user)):
    """
    Envia mensagem/notificação para múltiplos usuários.
    Usado pelo dono de assessoria para enviar mensagens aos atletas.
    """
    # Verificar se é dono de assessoria ou admin
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria ou admins podem enviar mensagens")
    
    if not request.destinatarios:
        raise HTTPException(status_code=400, detail="Nenhum destinatário informado")
    
    if not request.mensagem.strip():
        raise HTTPException(status_code=400, detail="Mensagem não pode estar vazia")
    
    # Criar notificações para cada destinatário
    notificacoes_criadas = 0
    agora = datetime.now(timezone.utc).isoformat()
    
    for destinatario_id in request.destinatarios:
        # Verificar se o destinatário existe
        usuario_destino = await db.usuarios.find_one(
            {"id": destinatario_id},
            {"_id": 0, "id": 1}
        )
        
        if not usuario_destino:
            continue
        
        notificacao = {
            "id": str(uuid.uuid4()),
            "usuario_id": destinatario_id,
            "tipo": request.tipo,
            "titulo": request.titulo or f"Mensagem de {current_user.get('equipe', 'Assessoria')}",
            "mensagem": request.mensagem,
            "lida": False,
            "data_criacao": agora,
            "remetente_id": current_user["id"],
            "remetente_nome": current_user.get("nome", ""),
            "remetente_equipe": current_user.get("equipe", "")
        }
        
        await db.notificacoes.insert_one(notificacao)
        notificacoes_criadas += 1
    
    return {
        "message": f"Mensagem enviada para {notificacoes_criadas} atleta(s)",
        "total_enviados": notificacoes_criadas
    }


@router.get("/notificacoes/splash-pendente")
async def splash_pendente(current_user: dict = Depends(get_current_user)):
    """Retorna splash screen pendente do usuário (não lido)"""
    splash = await db.notificacoes.find_one(
        {"usuario_id": current_user["id"], "tipo": "splash_admin", "lida": False},
        {"_id": 0}
    )
    return {"splash": splash}


@router.post("/notificacoes/splash/{notificacao_id}/confirmar")
async def confirmar_splash(notificacao_id: str, current_user: dict = Depends(get_current_user)):
    """Marca splash screen como lido/confirmado"""
    result = await db.notificacoes.update_one(
        {"id": notificacao_id, "usuario_id": current_user["id"], "tipo": "splash_admin"},
        {"$set": {"lida": True, "data_leitura": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Splash não encontrado")

    # Also mark the original notification as read
    splash = await db.notificacoes.find_one({"id": notificacao_id}, {"_id": 0, "mensagem_id": 1, "usuario_id": 1})
    if splash and splash.get("mensagem_id"):
        await db.notificacoes.update_many(
            {"mensagem_id": splash["mensagem_id"], "usuario_id": current_user["id"], "tipo": "mensagem_admin"},
            {"$set": {"lida": True}}
        )

    return {"message": "Splash confirmado"}


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


@router.delete("/notificacoes/{notificacao_id}")
async def excluir_notificacao(notificacao_id: str, current_user: dict = Depends(get_current_user)):
    """Exclui uma notificação específica do usuário"""
    result = await db.notificacoes.delete_one({
        "id": notificacao_id,
        "usuario_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return {"message": "Notificação excluída com sucesso"}


@router.get("/notificacoes/{notificacao_id}")
async def get_notificacao_detalhes(notificacao_id: str, current_user: dict = Depends(get_current_user)):
    """Retorna detalhes completos de uma notificação"""
    notificacao = await db.notificacoes.find_one(
        {"id": notificacao_id, "usuario_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return notificacao


# ==================== HELPER FUNCTION ====================

async def criar_notificacao(usuario_id: str, tipo: str, titulo: str, mensagem: str, dados_extras: dict = None):
    """Helper para criar notificação e enviar via WebSocket"""
    if dados_extras is None:
        dados_extras = {}
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        dados_extras=dados_extras
    )
    await db.notificacoes.insert_one(notificacao.model_dump())
    
    # Tentar enviar via WebSocket em tempo real
    try:
        from services.websocket_service import send_notification
        await send_notification(
            user_id=usuario_id,
            notification_type=tipo,
            title=titulo,
            message=mensagem,
            data=dados_extras
        )
    except Exception as e:
        # Se falhar, não é crítico - o polling vai pegar
        print(f"⚠️ Não foi possível enviar notificação via WebSocket: {e}")
    
    return notificacao
