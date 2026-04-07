import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Shield } from 'lucide-react';

const CONSENT_KEY = 'rr_cookie_consent';

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const consent = localStorage.getItem(CONSENT_KEY);
    if (!consent) setVisible(true);
  }, []);

  const accept = () => {
    localStorage.setItem(CONSENT_KEY, 'accepted');
    setVisible(false);
  };

  const reject = () => {
    localStorage.setItem(CONSENT_KEY, 'rejected');
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[9999] p-3 sm:p-4 animate-in slide-in-from-bottom duration-500" data-testid="cookie-consent-banner">
      <div className="max-w-4xl mx-auto bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-5">
        <Shield className="w-8 h-8 text-emerald-400 shrink-0 hidden sm:block" />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-slate-300 leading-relaxed">
            Utilizamos cookies essenciais para o funcionamento da plataforma e manutenção da sua sessão. Ao continuar navegando, você concorda com nossa{' '}
            <button onClick={() => navigate('/politica-de-privacidade')} className="text-emerald-400 hover:text-emerald-300 underline underline-offset-2 font-medium">
              Política de Privacidade
            </button>
            , em conformidade com a LGPD (Lei n. 13.709/2018).
          </p>
        </div>
        <div className="flex gap-2 shrink-0 w-full sm:w-auto">
          <Button onClick={accept} size="sm" className="bg-emerald-600 hover:bg-emerald-700 flex-1 sm:flex-none" data-testid="cookie-accept">
            Aceitar
          </Button>
          <Button onClick={reject} size="sm" variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 flex-1 sm:flex-none" data-testid="cookie-reject">
            Recusar
          </Button>
        </div>
      </div>
    </div>
  );
}
