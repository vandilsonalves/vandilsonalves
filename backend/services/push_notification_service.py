# /app/backend/services/push_notification_service.py
# Serviço de Push Notifications com Web Push API

import os
import json
import asyncio
from typing import Optional, Dict, List
from datetime import datetime, timezone

# Conexões WebSocket ativas (user_id -> lista de sids)
active_connections: Dict[str, List[str]] = {}

# Referência ao Socket.IO server (será setado pelo server.py)
sio = None

def set_socketio_server(socketio_server):
    """Define a referência do servidor Socket.IO"""
    global sio
    sio = socketio_server


async def enviar_notificacao_tempo_real(
    usuario_id: str,
    tipo: str,
    titulo: str,
    mensagem: str,
    dados_extras: dict = None
):
    """
    Envia notificação em tempo real via WebSocket.
    Tipos importantes: conquista, aprovacao, reprovacao, mensagem_assessoria, parabens
    """
    global sio
    
    if not sio:
        print("Socket.IO não inicializado")
        return False
    
    if dados_extras is None:
        dados_extras = {}
    
    # Verificar se é um tipo importante
    tipos_importantes = ['conquista', 'aprovacao', 'reprovacao', 'mensagem_assessoria', 'parabens', 'promocao']
    
    if tipo not in tipos_importantes:
        return False
    
    notificacao_data = {
        "tipo": tipo,
        "titulo": titulo,
        "mensagem": mensagem,
        "dados_extras": dados_extras,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Enviar para todas as conexões do usuário
        if usuario_id in active_connections:
            for sid in active_connections[usuario_id]:
                await sio.emit('nova_notificacao', notificacao_data, room=sid)
            print(f"✅ Notificação enviada para {usuario_id}: {titulo}")
            return True
        else:
            print(f"⚠️ Usuário {usuario_id} não está conectado via WebSocket")
            return False
    except Exception as e:
        print(f"❌ Erro ao enviar notificação: {e}")
        return False


def registrar_conexao(user_id: str, sid: str):
    """Registra uma nova conexão WebSocket"""
    if user_id not in active_connections:
        active_connections[user_id] = []
    if sid not in active_connections[user_id]:
        active_connections[user_id].append(sid)
    print(f"🔗 Conexão registrada: user={user_id}, sid={sid}, total={len(active_connections[user_id])}")


def remover_conexao(user_id: str, sid: str):
    """Remove uma conexão WebSocket"""
    if user_id in active_connections:
        if sid in active_connections[user_id]:
            active_connections[user_id].remove(sid)
        if not active_connections[user_id]:
            del active_connections[user_id]
    print(f"🔌 Conexão removida: user={user_id}, sid={sid}")


def get_usuarios_online() -> List[str]:
    """Retorna lista de IDs de usuários online"""
    return list(active_connections.keys())


def is_usuario_online(user_id: str) -> bool:
    """Verifica se um usuário está online"""
    return user_id in active_connections and len(active_connections[user_id]) > 0
