import { createContext, useContext, useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { toast } from 'sonner';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configurações do WebSocket
const WS_RECONNECT_DELAY = 3000;
const WS_PING_INTERVAL = 25000;
const TIPOS_IMPORTANTES = [
  'conquista', 'resultado_aprovado', 'resultado_reprovado',
  'aprovacao', 'reprovacao', 'mensagem_assessoria', 
  'parabens', 'promocao', 'aniversario'
];
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

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [notificacoes, setNotificacoes] = useState([]);
  const [naoLidas, setNaoLidas] = useState(0);
  
  // Permissões do admin
  const [adminPermissoes, setAdminPermissoes] = useState([]);
  const [tipoAdmin, setTipoAdmin] = useState(null); // 'Super Admin', 'Colaborador', etc.
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);
  
  // WebSocket para notificações em tempo real
  const wsRef = useRef(null);
  const pingIntervalRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  // Buscar notificações periodicamente (polling como fallback do WebSocket)
  useEffect(() => {
    if (token && user) {
      fetchNotificacoes();
      // Polling mais frequente quando WebSocket não está conectado
      const pollInterval = wsConnected ? 30000 : 10000;
      const interval = setInterval(fetchNotificacoes, pollInterval);
      return () => clearInterval(interval);
    }
  }, [token, user, wsConnected]);

  // Conectar WebSocket quando usuário estiver autenticado
  useEffect(() => {
    if (token && user) {
      connectWebSocket();
    }
    return () => {
      disconnectWebSocket();
    };
  }, [token, user]);

  // Função para conectar WebSocket
  const connectWebSocket = () => {
    if (!token || wsRef.current?.readyState === WebSocket.OPEN) return;

    const wsProtocol = BACKEND_URL.startsWith('https') ? 'wss' : 'ws';
    const wsHost = BACKEND_URL.replace(/^https?:\/\//, '');
    const wsUrl = `${wsProtocol}://${wsHost}/api/ws/notifications?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('🔔 WebSocket conectado - Notificações em tempo real ativas');
        setWsConnected(true);
        
        // Keep-alive ping
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, WS_PING_INTERVAL);

        // Solicitar contagem inicial
        ws.send(JSON.stringify({ type: 'get_unread_count' }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Erro ao processar mensagem WS:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket desconectado');
        setWsConnected(false);
        clearInterval(pingIntervalRef.current);

        // Reconectar automaticamente
        if (event.code !== 4001 && token) {
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, WS_RECONNECT_DELAY);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket erro:', error);
      };
    } catch (error) {
      console.error('Erro ao criar WebSocket:', error);
    }
  };

  // Função para desconectar WebSocket
  const disconnectWebSocket = () => {
    clearTimeout(reconnectTimeoutRef.current);
    clearInterval(pingIntervalRef.current);
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setWsConnected(false);
  };

  // Processar mensagens do WebSocket
  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'connection_established':
        console.log('✅ Conexão WebSocket confirmada');
        break;

      case 'notification':
        const notification = data.notification;
        if (!notification) break;

        // Atualizar lista de notificações
        setNotificacoes(prev => {
          const exists = prev.some(n => n.id === notification.id);
          if (exists) return prev;
          return [{ ...notification, lida: false, data_criacao: notification.timestamp }, ...prev];
        });
        setNaoLidas(prev => prev + 1);

        // Mostrar toast para notificações importantes
        if (TIPOS_IMPORTANTES.includes(notification.type)) {
          const icon = NOTIFICATION_ICONS[notification.type] || '🔔';
          const title = notification.title || 'Nova notificação';
          const message = notification.message || '';

          if (['conquista', 'resultado_aprovado', 'aprovacao', 'parabens', 'promocao', 'aniversario'].includes(notification.type)) {
            toast.success(`${icon} ${title}`, { description: message, duration: 6000 });
          } else if (['resultado_reprovado', 'reprovacao'].includes(notification.type)) {
            toast.error(`${icon} ${title}`, { description: message, duration: 6000 });
          } else {
            toast.info(`${icon} ${title}`, { description: message, duration: 5000 });
          }
          playNotificationSound();
        }
        break;

      case 'unread_count':
        setNaoLidas(data.count);
        break;

      case 'notification_marked_read':
        setNotificacoes(prev => prev.map(n => 
          n.id === data.notification_id ? { ...n, lida: true } : n
        ));
        setNaoLidas(prev => Math.max(0, prev - 1));
        break;

      case 'admin_alert':
        if (data.alert) {
          toast.warning(data.alert.message, { description: `Alerta: ${data.alert.alert_type}`, duration: 8000 });
        }
        break;

      default:
        break;
    }
  };

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      
      // Se for admin, buscar permissões
      if (response.data.role === 'admin' || response.data.role === 'super_admin') {
        await fetchAdminPermissoes();
      }
    } catch (error) {
      console.error('Erro ao buscar usuário:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const fetchAdminPermissoes = async () => {
    try {
      // Tentar fazer login via RBAC para obter permissões
      const storedUser = JSON.parse(localStorage.getItem('adminData') || 'null');
      if (storedUser && storedUser.permissoes) {
        setAdminPermissoes(storedUser.permissoes);
        setTipoAdmin(storedUser.tipo_admin);
        setIsSuperAdmin(storedUser.is_super_admin || false);
      } else {
        // Fallback: admin legado tem todas as permissões
        setAdminPermissoes([
          'aprovar_corridas', 'reprovar_corridas', 'aprovar_resultados',
          'moderar_avaliacoes', 'visualizar_atletas', 'editar_atletas',
          'excluir_atletas', 'visualizar_assessorias', 'gerenciar_assessorias',
          'enviar_mensagens', 'criar_admins', 'editar_admins', 'excluir_admins',
          'visualizar_logs', 'configuracoes_sistema', 'exportar_dados',
          'dados_financeiros', 'alterar_pontuacao', 'restaurar_dados'
        ]);
        setTipoAdmin('Super Admin');
        setIsSuperAdmin(true);
      }
    } catch (error) {
      console.error('Erro ao buscar permissões:', error);
    }
  };

  const fetchNotificacoes = async () => {
    try {
      const response = await axios.get(`${API}/notificacoes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const novasNotificacoes = response.data.notificacoes || [];
      const novoNaoLidas = response.data.nao_lidas || 0;
      
      // Detectar notificações novas (para mostrar toast via polling)
      if (notificacoes.length > 0 && novasNotificacoes.length > notificacoes.length) {
        const notificacoesNovas = novasNotificacoes.filter(
          n => !notificacoes.some(old => old.id === n.id)
        );
        
        // Mostrar toast para cada notificação nova e importante (se não veio via WebSocket)
        if (!wsConnected) {
          notificacoesNovas.forEach(notification => {
            if (TIPOS_IMPORTANTES.includes(notification.tipo) && !notification.lida) {
              const icon = NOTIFICATION_ICONS[notification.tipo] || '🔔';
              const title = notification.titulo || 'Nova notificação';
              const message = notification.mensagem || '';
              
              if (['conquista', 'aprovacao', 'parabens', 'promocao', 'aniversario'].includes(notification.tipo)) {
                toast.success(`${icon} ${title}`, { description: message, duration: 6000 });
              } else if (['reprovacao'].includes(notification.tipo)) {
                toast.error(`${icon} ${title}`, { description: message, duration: 6000 });
              } else {
                toast.info(`${icon} ${title}`, { description: message, duration: 5000 });
              }
              playNotificationSound();
            }
          });
        }
      }
      
      setNotificacoes(novasNotificacoes);
      setNaoLidas(novoNaoLidas);
    } catch (error) {
      console.error('Erro ao buscar notificações:', error);
    }
  };

  const marcarLida = async (notificacaoId) => {
    try {
      await axios.post(`${API}/notificacoes/${notificacaoId}/ler`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchNotificacoes();
    } catch (error) {
      console.error('Erro ao marcar notificação:', error);
    }
  };

  const marcarTodasLidas = async () => {
    try {
      await axios.post(`${API}/notificacoes/ler-todas`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchNotificacoes();
    } catch (error) {
      console.error('Erro ao marcar todas:', error);
    }
  };

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    const { token: newToken, refresh_token: refreshToken, user: userData } = response.data;
    
    localStorage.setItem('token', newToken);
    if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
    setToken(newToken);
    setUser(userData);
    
    // Se for admin, tentar login RBAC para obter permissões
    if (userData.role === 'admin' || userData.role === 'super_admin') {
      try {
        const rbacResponse = await axios.post(`${API}/rbac/login`, { email, password });
        if (rbacResponse.data.user) {
          const adminData = rbacResponse.data.user;
          localStorage.setItem('adminData', JSON.stringify(adminData));
          setAdminPermissoes(adminData.permissoes || []);
          setTipoAdmin(adminData.tipo_admin);
          setIsSuperAdmin(adminData.is_super_admin || userData.role === 'super_admin');
        }
      } catch (e) {
        // Fallback para admin legado ou super_admin
        const isSuperAdminRole = userData.role === 'super_admin';
        setIsSuperAdmin(isSuperAdminRole);
        setAdminPermissoes([
          'aprovar_corridas', 'reprovar_corridas', 'aprovar_resultados',
          'moderar_avaliacoes', 'visualizar_atletas', 'editar_atletas',
          'excluir_atletas', 'visualizar_assessorias', 'gerenciar_assessorias',
          'enviar_mensagens', 'criar_admins', 'editar_admins', 'excluir_admins',
          'visualizar_logs', 'configuracoes_sistema', 'exportar_dados',
          'dados_financeiros', 'alterar_pontuacao', 'restaurar_dados'
        ]);
        setTipoAdmin('Super Admin');
        setIsSuperAdmin(true);
      }
    }
    
    return userData;
  };

  const register = async (dados) => {
    const response = await axios.post(`${API}/auth/register`, dados);
    const { token: newToken, refresh_token: refreshToken, user: userData } = response.data;
    
    localStorage.setItem('token', newToken);
    if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
    setToken(newToken);
    setUser(userData);
    
    return userData;
  };

  const logout = () => {
    // Desconectar WebSocket
    disconnectWebSocket();
    
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('adminData');
    setToken(null);
    setUser(null);
    setNotificacoes([]);
    setNaoLidas(0);
    setAdminPermissoes([]);
    setTipoAdmin(null);
    setIsSuperAdmin(false);
  };

  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin';
  
  // Função para verificar se tem uma permissão específica
  const temPermissao = (permissao) => {
    if (isSuperAdmin) return true;
    return adminPermissoes.includes(permissao);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading, 
      login, 
      register, 
      logout, 
      isAdmin,
      notificacoes,
      naoLidas,
      fetchNotificacoes,
      marcarLida,
      marcarTodasLidas,
      // Novas propriedades RBAC
      adminPermissoes,
      tipoAdmin,
      isSuperAdmin,
      temPermissao,
      // WebSocket
      wsConnected
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
