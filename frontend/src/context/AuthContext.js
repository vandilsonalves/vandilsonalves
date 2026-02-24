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
    } catch (error) {
      console.error('Erro ao buscar usuário:', error);
      logout();
    } finally {
      setLoading(false);
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
    setToken(null);
    setUser(null);
    setNotificacoes([]);
    setNaoLidas(0);
  };

  const isAdmin = user?.role === 'admin';

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
      marcarTodasLidas
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
