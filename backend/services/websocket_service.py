# /app/backend/services/websocket_service.py
"""
Serviço de WebSocket para notificações em tempo real
- Gerencia conexões por usuário
- Suporta broadcast e mensagens direcionadas
- Reconexão automática
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        # Mapa de user_id -> conjunto de conexões WebSocket
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Mapa de WebSocket -> user_id (para lookup reverso)
        self.connection_users: Dict[WebSocket, str] = {}
        # Conexões de admins (para broadcast de alertas)
        self.admin_connections: Set[WebSocket] = set()
        # Estatísticas
        self.stats = {
            "total_connections": 0,
            "messages_sent": 0,
            "reconnections": 0
        }
    
    async def connect(self, websocket: WebSocket, user_id: str, is_admin: bool = False):
        """Aceita nova conexão WebSocket"""
        await websocket.accept()
        
        # Adicionar ao mapa de conexões do usuário
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_users[websocket] = user_id
        
        if is_admin:
            self.admin_connections.add(websocket)
        
        self.stats["total_connections"] += 1
        
        logger.info(f"🔌 WebSocket conectado: user_id={user_id}, is_admin={is_admin}, total={len(self.connection_users)}")
        
        # Enviar confirmação de conexão
        await self.send_personal(websocket, {
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove conexão WebSocket"""
        user_id = self.connection_users.get(websocket)
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Remover entrada se não houver mais conexões
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        self.connection_users.pop(websocket, None)
        self.admin_connections.discard(websocket)
        
        logger.info(f"🔌 WebSocket desconectado: user_id={user_id}, total={len(self.connection_users)}")
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Envia mensagem para uma conexão específica"""
        try:
            await websocket.send_json(message)
            self.stats["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """Envia mensagem para todas as conexões de um usuário"""
        connections = self.active_connections.get(user_id, set())
        
        if not connections:
            logger.debug(f"Usuário {user_id} não está conectado")
            return False
        
        # Adicionar timestamp se não tiver
        if "timestamp" not in message:
            message["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Enviar para todas as conexões do usuário (pode ter múltiplas abas)
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
                self.stats["messages_sent"] += 1
            except Exception as e:
                logger.error(f"Erro ao enviar para {user_id}: {e}")
                disconnected.append(websocket)
        
        # Limpar conexões mortas
        for ws in disconnected:
            self.disconnect(ws)
        
        return True
    
    async def broadcast_to_admins(self, message: dict):
        """Envia mensagem para todos os admins conectados"""
        if "timestamp" not in message:
            message["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        disconnected = []
        for websocket in self.admin_connections:
            try:
                await websocket.send_json(message)
                self.stats["messages_sent"] += 1
            except Exception:
                disconnected.append(websocket)
        
        for ws in disconnected:
            self.disconnect(ws)
        
        logger.info(f"📢 Broadcast para {len(self.admin_connections)} admins")
    
    async def broadcast_all(self, message: dict):
        """Envia mensagem para todos os usuários conectados"""
        if "timestamp" not in message:
            message["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        all_websockets = list(self.connection_users.keys())
        disconnected = []
        
        for websocket in all_websockets:
            try:
                await websocket.send_json(message)
                self.stats["messages_sent"] += 1
            except Exception:
                disconnected.append(websocket)
        
        for ws in disconnected:
            self.disconnect(ws)
        
        logger.info(f"📢 Broadcast para {len(all_websockets)} conexões")
    
    def is_user_online(self, user_id: str) -> bool:
        """Verifica se usuário está online"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_online_users(self) -> list:
        """Retorna lista de usuários online"""
        return list(self.active_connections.keys())
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do WebSocket"""
        return {
            **self.stats,
            "active_users": len(self.active_connections),
            "active_connections": len(self.connection_users),
            "admin_connections": len(self.admin_connections)
        }


# Instância global do gerenciador
ws_manager = ConnectionManager()


# ==================== FUNÇÕES DE NOTIFICAÇÃO ====================

async def notify_user(user_id: str, notification_type: str, title: str, message: str, 
                      data: dict = None, save_to_db: bool = True):
    """
    Envia notificação para um usuário (tempo real + persistência)
    """
    from config import db
    
    notification = {
        "id": str(uuid.uuid4()),
        "type": notification_type,
        "title": title,
        "message": message,
        "data": data or {},
        "read": False,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Salvar no banco se solicitado
    if save_to_db:
        db_notification = {
            **notification,
            "usuario_id": user_id,
            "lida": False,
            "data_criacao": notification["timestamp"]
        }
        await db.notificacoes.insert_one(db_notification)
    
    # Enviar em tempo real
    ws_notification = {
        "type": "notification",
        "notification": notification
    }
    
    sent = await ws_manager.send_to_user(user_id, ws_notification)
    
    logger.info(f"🔔 Notificação enviada: user={user_id}, type={notification_type}, realtime={sent}")
    
    return notification


async def notify_resultado_aprovado(user_id: str, competicao: str, pontos: int, modalidade: str = "profissional"):
    """Notifica atleta que resultado foi aprovado"""
    return await notify_user(
        user_id=user_id,
        notification_type="resultado_aprovado",
        title="🎉 Resultado Aprovado!",
        message=f"Seu resultado na {competicao} foi aprovado! +{pontos} pontos.",
        data={"competicao": competicao, "pontos": pontos, "modalidade": modalidade}
    )


async def notify_resultado_reprovado(user_id: str, competicao: str, motivo: str):
    """Notifica atleta que resultado foi reprovado"""
    return await notify_user(
        user_id=user_id,
        notification_type="resultado_reprovado",
        title="❌ Resultado Reprovado",
        message=f"Seu resultado na {competicao} foi reprovado. Motivo: {motivo}",
        data={"competicao": competicao, "motivo": motivo}
    )


async def notify_nova_conquista(user_id: str, conquista_nome: str, conquista_icone: str, descricao: str):
    """Notifica atleta sobre nova conquista"""
    return await notify_user(
        user_id=user_id,
        notification_type="conquista",
        title=f"🏆 Nova Conquista: {conquista_nome}!",
        message=descricao,
        data={"conquista": conquista_nome, "icone": conquista_icone}
    )


async def notify_aniversario(user_id: str, mensagem: str):
    """Notifica atleta de mensagem de aniversário"""
    return await notify_user(
        user_id=user_id,
        notification_type="aniversario",
        title="🎂 Feliz Aniversário!",
        message=mensagem,
        data={}
    )


async def notify_ranking_atualizado(user_id: str, nova_posicao: int, posicao_anterior: int):
    """Notifica atleta sobre mudança no ranking"""
    direcao = "subiu" if nova_posicao < posicao_anterior else "desceu"
    diferenca = abs(nova_posicao - posicao_anterior)
    
    return await notify_user(
        user_id=user_id,
        notification_type="ranking",
        title=f"📊 Ranking Atualizado!",
        message=f"Você {direcao} {diferenca} posição(ões)! Agora está em {nova_posicao}º lugar.",
        data={"nova_posicao": nova_posicao, "posicao_anterior": posicao_anterior}
    )


async def notify_admin_alert(alert_type: str, message: str, details: dict = None):
    """Envia alerta para todos os admins conectados"""
    alert = {
        "type": "admin_alert",
        "alert": {
            "id": str(uuid.uuid4()),
            "alert_type": alert_type,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    
    await ws_manager.broadcast_to_admins(alert)
    logger.warning(f"⚠️ Admin Alert: {alert_type} - {message}")
