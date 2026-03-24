import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { X, ExternalLink, Paperclip, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SplashScreen = ({ token, onDismiss }) => {
  const [splash, setSplash] = useState(null);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (!token) return;
    const fetchSplash = async () => {
      try {
        const res = await axios.get(`${API}/notificacoes/splash-pendente`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.data.splash) {
          setSplash(res.data.splash);
        }
      } catch (err) {
        console.error('Erro ao buscar splash:', err);
      }
    };
    fetchSplash();
  }, [token]);

  const handleConfirm = async () => {
    if (!splash) return;
    setConfirming(true);
    try {
      await axios.post(`${API}/notificacoes/splash/${splash.id}/confirmar`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSplash(null);
      onDismiss?.();
    } catch (err) {
      console.error('Erro ao confirmar splash:', err);
    } finally {
      setConfirming(false);
    }
  };

  if (!splash) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 backdrop-blur-sm"
      data-testid="splash-screen-overlay"
    >
      <div className="relative w-full max-w-lg mx-4 animate-in fade-in zoom-in-95 duration-300">
        {/* Card */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-700">
          {/* Header gradient */}
          <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-white/70 text-xs font-medium uppercase tracking-wider">Mensagem Importante</p>
                <h2 className="text-white text-lg font-bold leading-tight">{splash.titulo}</h2>
              </div>
            </div>
          </div>

          {/* Body */}
          <div className="px-6 py-5 space-y-4 max-h-[50vh] overflow-y-auto">
            <p className="text-slate-700 dark:text-slate-300 text-base leading-relaxed whitespace-pre-wrap">
              {splash.mensagem}
            </p>

            {splash.link && (
              <a
                href={splash.link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-medium text-sm bg-emerald-50 dark:bg-emerald-900/20 px-4 py-2.5 rounded-lg transition-colors"
                data-testid="splash-link"
              >
                <ExternalLink className="w-4 h-4" />
                {splash.link.length > 50 ? splash.link.substring(0, 50) + '...' : splash.link}
              </a>
            )}

            {splash.anexos?.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs text-slate-500 font-medium uppercase">Anexos</p>
                {splash.anexos.map((anexo, i) => (
                  <a
                    key={i}
                    href={`${BACKEND_URL}${anexo.url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 hover:text-emerald-600 bg-slate-50 dark:bg-slate-800 px-3 py-2 rounded-lg"
                  >
                    <Paperclip className="w-3.5 h-3.5" />
                    {anexo.original_name || anexo.filename}
                  </a>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-700">
            <Button
              onClick={handleConfirm}
              disabled={confirming}
              className="w-full h-12 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-base rounded-xl"
              data-testid="splash-confirm-btn"
            >
              {confirming ? 'Confirmando...' : 'Entendido'}
            </Button>
            <p className="text-center text-xs text-slate-400 mt-2">
              Enviado por {splash.remetente_nome || 'Administração'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;
