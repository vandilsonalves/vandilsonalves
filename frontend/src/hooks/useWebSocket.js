// /app/frontend/src/hooks/useWebSocket.js
/**
 * Hook para conexão WebSocket com notificações em tempo real
 * - Reconexão automática
 * - Gerenciamento de estado
 * - Keep-alive com ping/pong
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'sonner';

const WS_RECONNECT_DELAY = 3000; // 3 segundos
const WS_PING_INTERVAL = 25000; // 25 segundos

// Tipos de notificações importantes que mostram toast
const TIPOS_IMPORTANTES = [
  'conquista', 'resultado_aprovado', 'resultado_reprovado',
  'aprovacao', 'reprovacao', 'mensagem_assessoria', 
  'parabens', 'promocao', 'aniversario'
];

// Ícones por tipo de notificação
const NOTIFICATION_ICONS = {
  conquista: '🏆',
  resultado_aprovado: '✅',
  aprovacao: '✅',
  parabens: '🎊',
  promocao: '🎉',
  aniversario: '🎂',
  mensagem_assessoria: '💬',
  resultado_reprovado: '❌',
  reprovacao: '❌',
};

// Tocar som de notificação
const playNotificationSound = () => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    gainNode.gain.value = 0.1;
    
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.15);
  } catch (error) {
    // Ignorar erros de áudio
  }
};

export const useWebSocket = (token) => {
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [lastMessage, setLastMessage] = useState(null);
  
  const wsRef = useRef(null);
  const pingIntervalRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const shouldReconnectRef = useRef(true);

  // Construir URL do WebSocket
  const getWebSocketUrl = useCallback(() => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    // Converter HTTP para WS
    const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = backendUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${wsHost}/api/ws/notifications?token=${token}`;
  }, [token]);

  // Conectar ao WebSocket
  const connect = useCallback(() => {
    if (!token || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = getWebSocketUrl();
    console.log('🔌 Conectando WebSocket...');

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        setIsConnected(true);
        
        // Iniciar ping keep-alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, WS_PING_INTERVAL);

        // Solicitar contagem de não lidas
        ws.send(JSON.stringify({ type: 'get_unread_count' }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);

          switch (data.type) {
            case 'connection_established':
              console.log('🔗 Conexão estabelecida:', data.user_id);
              break;

            case 'notification':
              // Nova notificação recebida
              const notification = data.notification;
              setNotifications(prev => [notification, ...prev]);
              setUnreadCount(prev => prev + 1);
              
              // Mostrar toast para notificações importantes
              if (notification && TIPOS_IMPORTANTES.includes(notification.type)) {
                const icon = NOTIFICATION_ICONS[notification.type] || '🔔';
                const title = notification.title || 'Nova notificação';
                const message = notification.message || '';
                
                // Escolher estilo do toast baseado no tipo
                if (['conquista', 'resultado_aprovado', 'aprovacao', 'parabens', 'promocao', 'aniversario'].includes(notification.type)) {
                  toast.success(`${icon} ${title}`, {
                    description: message,
                    duration: 6000,
                  });
                } else if (['resultado_reprovado', 'reprovacao'].includes(notification.type)) {
                  toast.error(`${icon} ${title}`, {
                    description: message,
                    duration: 6000,
                  });
                } else {
                  toast.info(`${icon} ${title}`, {
                    description: message,
                    duration: 5000,
                  });
                }
                
                // Tocar som
                playNotificationSound();
              }
              
              // Disparar evento customizado para outros componentes
              window.dispatchEvent(new CustomEvent('new-notification', { 
                detail: notification 
              }));
              break;

            case 'admin_alert':
              // Alerta de admin
              window.dispatchEvent(new CustomEvent('admin-alert', { 
                detail: data.alert 
              }));
              break;

            case 'unread_count':
              setUnreadCount(data.count);
              break;

            case 'notification_marked_read':
              // Atualizar estado local
              setNotifications(prev => 
                prev.map(n => 
                  n.id === data.notification_id ? { ...n, read: true } : n
                )
              );
              setUnreadCount(prev => Math.max(0, prev - 1));
              break;

            case 'pong':
              // Keep-alive response
              break;

            default:
              console.log('📩 Mensagem WS:', data);
          }
        } catch (error) {
          console.error('Erro ao processar mensagem WS:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ Erro WebSocket:', error);
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket desconectado:', event.code, event.reason);
        setIsConnected(false);
        
        // Limpar ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Reconectar automaticamente se não foi fechamento intencional
        if (shouldReconnectRef.current && event.code !== 4001) {
          console.log(`🔄 Reconectando em ${WS_RECONNECT_DELAY/1000}s...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, WS_RECONNECT_DELAY);
        }
      };

    } catch (error) {
      console.error('Erro ao criar WebSocket:', error);
    }
  }, [token, getWebSocketUrl]);

  // Desconectar
  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  // Marcar notificação como lida
  const markAsRead = useCallback((notificationId) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'mark_read',
        notification_id: notificationId
      }));
    }
  }, []);

  // Enviar mensagem customizada
  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Conectar quando token estiver disponível
  useEffect(() => {
    if (token) {
      shouldReconnectRef.current = true;
      connect();
    }

    return () => {
      disconnect();
    };
  }, [token, connect, disconnect]);

  return {
    isConnected,
    notifications,
    unreadCount,
    lastMessage,
    markAsRead,
    sendMessage,
    connect,
    disconnect,
    setUnreadCount
  };
};

export default useWebSocket;
