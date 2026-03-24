# /app/backend/routes/websocket_routes.py
"""
Endpoints WebSocket para notificações em tempo real
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import json
import logging
from jose import jwt, JWTError

from config import db
from services.websocket_service import ws_manager, notify_user
from routes.auth_routes import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


async def get_user_from_token(token: str) -> Optional[dict]:
    """Valida token JWT e retorna dados do usuário"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await db.usuarios.find_one({"id": user_id}, {"_id": 0, "senha": 0})
        return user
    except JWTError:
        return None


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint para receber notificações em tempo real.
    
    Conexão: ws://host/api/ws/notifications?token=JWT_TOKEN
    
    Mensagens recebidas:
    - type: "connection_established" - Conexão aceita
    - type: "notification" - Nova notificação
    - type: "admin_alert" - Alerta para admins
    - type: "ping" - Keep-alive
    
    Mensagens que podem ser enviadas pelo cliente:
    - {"type": "ping"} - Keep-alive
    - {"type": "mark_read", "notification_id": "..."} - Marcar como lida
    """
    
    # Validar token
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=4001, reason="Token inválido")
        return
    
    user_id = user["id"]
    is_admin = user.get("role") == "admin"
    
    # Conectar
    await ws_manager.connect(websocket, user_id, is_admin)
    
    try:
        # Loop para manter conexão e processar mensagens do cliente
        while True:
            try:
                # Receber mensagem do cliente (timeout de 30s para keep-alive)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                msg_type = message.get("type")
                
                if msg_type == "ping":
                    # Responder com pong
                    await websocket.send_json({"type": "pong"})
                
                elif msg_type == "mark_read":
                    # Marcar notificação como lida
                    notification_id = message.get("notification_id")
                    if notification_id:
                        await db.notificacoes.update_one(
                            {"id": notification_id, "usuario_id": user_id},
                            {"$set": {"lida": True}}
                        )
                        await websocket.send_json({
                            "type": "notification_marked_read",
                            "notification_id": notification_id
                        })
                
                elif msg_type == "get_unread_count":
                    # Retornar contagem de não lidas
                    count = await db.notificacoes.count_documents({
                        "usuario_id": user_id,
                        "lida": False
                    })
                    await websocket.send_json({
                        "type": "unread_count",
                        "count": count
                    })
                
            except json.JSONDecodeError:
                logger.warning(f"Mensagem inválida de {user_id}")
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Erro no WebSocket de {user_id}: {e}")
        ws_manager.disconnect(websocket)


# ==================== ENDPOINTS HTTP AUXILIARES ====================

from routes.auth_routes import get_current_user, get_admin_user


@router.get("/notifications/ws-status")
async def get_websocket_status(current_user: dict = Depends(get_admin_user)):
    """Retorna status do servidor WebSocket (apenas admin)"""
    stats = ws_manager.get_stats()
    online_users = ws_manager.get_online_users()
    
    return {
        "status": "online",
        **stats,
        "online_user_ids": online_users[:20]  # Limitar para não expor todos
    }


@router.post("/notifications/send-test")
async def send_test_notification(current_user: dict = Depends(get_current_user)):
    """Envia notificação de teste para o usuário atual"""
    notification = await notify_user(
        user_id=current_user["id"],
        notification_type="test",
        title="🔔 Notificação de Teste",
        message="Esta é uma notificação de teste em tempo real!",
        data={"test": True},
        save_to_db=False  # Não salvar teste no banco
    )
    
    return {
        "message": "Notificação de teste enviada",
        "notification": notification,
        "user_online": ws_manager.is_user_online(current_user["id"])
    }


@router.post("/notifications/broadcast-admin")
async def broadcast_to_admins(
    dados: dict,
    current_user: dict = Depends(get_admin_user)
):
    """Envia mensagem para todos os admins conectados (apenas admin)"""
    from services.websocket_service import notify_admin_alert
    
    await notify_admin_alert(
        alert_type=dados.get("type", "info"),
        message=dados.get("message", "Mensagem do sistema"),
        details=dados.get("details", {})
    )
    
    return {"message": "Broadcast enviado para admins"}


@router.get("/notifications/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    """Retorna contagem de notificações não lidas"""
    count = await db.notificacoes.count_documents({
        "usuario_id": current_user["id"],
        "lida": False
    })
    
    return {"unread_count": count}


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Marca notificação como lida"""
    result = await db.notificacoes.update_one(
        {"id": notification_id, "usuario_id": current_user["id"]},
        {"$set": {"lida": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return {"message": "Notificação marcada como lida"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    """Marca todas as notificações como lidas"""
    result = await db.notificacoes.update_many(
        {"usuario_id": current_user["id"], "lida": False},
        {"$set": {"lida": True}}
    )
    
    return {"message": f"{result.modified_count} notificações marcadas como lidas"}
