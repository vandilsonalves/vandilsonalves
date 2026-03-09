import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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

  useEffect(() => {
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  // Buscar notificações periodicamente
  useEffect(() => {
    if (token && user) {
      fetchNotificacoes();
      const interval = setInterval(fetchNotificacoes, 30000); // A cada 30 segundos
      return () => clearInterval(interval);
    }
  }, [token, user]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      
      // Se for admin, buscar permissões
      if (response.data.role === 'admin') {
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
      setNotificacoes(response.data.notificacoes);
      setNaoLidas(response.data.nao_lidas);
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
    const { token: newToken, user: userData } = response.data;
    
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
    
    // Se for admin, tentar login RBAC para obter permissões
    if (userData.role === 'admin') {
      try {
        const rbacResponse = await axios.post(`${API}/rbac/login`, { email, password });
        if (rbacResponse.data.user) {
          const adminData = rbacResponse.data.user;
          localStorage.setItem('adminData', JSON.stringify(adminData));
          setAdminPermissoes(adminData.permissoes || []);
          setTipoAdmin(adminData.tipo_admin);
          setIsSuperAdmin(adminData.is_super_admin || false);
        }
      } catch (e) {
        // Fallback para admin legado
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
    const { token: newToken, user: userData } = response.data;
    
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
    
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('adminData');
    setToken(null);
    setUser(null);
    setNotificacoes([]);
    setNaoLidas(0);
    setAdminPermissoes([]);
    setTipoAdmin(null);
    setIsSuperAdmin(false);
  };

  const isAdmin = user?.role === 'admin';
  
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
      temPermissao
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
