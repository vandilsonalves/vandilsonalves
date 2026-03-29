import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export function useFeedNaoLidos(token, equipe) {
  const [naoLidos, setNaoLidos] = useState(0);

  const fetch = useCallback(async () => {
    if (!token || !equipe || ['Individual', 'individual', 'SEM EQUIPE', ''].includes(equipe)) return;
    try {
      const res = await axios.get(`${API}/equipe/feed/nao-lidos`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNaoLidos(res.data.nao_lidos || 0);
    } catch { /* silent */ }
  }, [token, equipe]);

  useEffect(() => {
    fetch();
    const interval = setInterval(fetch, 15000);
    return () => clearInterval(interval);
  }, [fetch]);

  const marcarLido = useCallback(async () => {
    if (!token) return;
    try {
      await axios.post(`${API}/equipe/feed/marcar-lido`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNaoLidos(0);
    } catch { /* silent */ }
  }, [token]);

  return { naoLidos, marcarLido, refresh: fetch };
}
