import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { CheckCircle, Loader2, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL;

export default function PagamentoSucessoPage() {
  const [searchParams] = useSearchParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [status, setStatus] = useState('polling'); // polling, success, error
  const [info, setInfo] = useState(null);
  const polledRef = useRef(false);

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (!sessionId || !token || polledRef.current) return;
    polledRef.current = true;
    pollStatus(0);
  }, [sessionId, token]);

  const pollStatus = async (attempt) => {
    const maxAttempts = 8;
    const interval = 2500;

    if (attempt >= maxAttempts) {
      setStatus('error');
      return;
    }

    try {
      const res = await fetch(`${API}/api/pagamentos/status/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) {
        throw new Error('Erro ao verificar status');
      }
      const data = await res.json();
      setInfo(data);

      if (data.payment_status === 'paid') {
        setStatus('success');
        return;
      }
      if (data.status === 'expired') {
        setStatus('error');
        return;
      }

      // Continuar polling
      setTimeout(() => pollStatus(attempt + 1), interval);
    } catch (err) {
      console.error(err);
      setTimeout(() => pollStatus(attempt + 1), interval);
    }
  };

  if (!sessionId) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white">
        <p>Sessao de pagamento nao encontrada.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-4" data-testid="pagamento-sucesso-page">
      <div className="max-w-md w-full text-center">
        {status === 'polling' && (
          <div className="space-y-4" data-testid="status-polling">
            <Loader2 className="w-16 h-16 text-emerald-400 animate-spin mx-auto" />
            <h2 className="text-xl font-bold">Verificando pagamento...</h2>
            <p className="text-gray-400 text-sm">Aguarde enquanto confirmamos seu pagamento.</p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-6" data-testid="status-success">
            <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle className="w-10 h-10 text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold">Pagamento Confirmado!</h2>
            <p className="text-gray-400">
              Seu plano <strong className="text-white">Atleta Premium</strong> esta ativo.
            </p>
            {info?.validade && (
              <p className="text-sm text-gray-500">
                Valido ate {new Date(info.validade + 'T00:00:00').toLocaleDateString('pt-BR')}
              </p>
            )}
            <div className="flex flex-col gap-3 pt-4">
              <Button
                onClick={() => navigate('/')}
                className="bg-emerald-600 hover:bg-emerald-500 text-white"
                data-testid="btn-ir-ranking"
              >
                Ir para o Ranking
              </Button>
              <Button
                onClick={() => navigate('/perfil')}
                variant="outline"
                className="border-gray-700 text-gray-300 hover:bg-gray-800"
                data-testid="btn-ir-perfil"
              >
                Ver meu Perfil
              </Button>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-6" data-testid="status-error">
            <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto">
              <XCircle className="w-10 h-10 text-red-400" />
            </div>
            <h2 className="text-2xl font-bold">Pagamento nao confirmado</h2>
            <p className="text-gray-400 text-sm">
              Nao foi possivel confirmar seu pagamento. Se o valor foi debitado, entre em contato com o suporte.
            </p>
            <div className="flex flex-col gap-3 pt-4">
              <Button
                onClick={() => navigate('/pagamento')}
                className="bg-emerald-600 hover:bg-emerald-500 text-white"
                data-testid="btn-tentar-novamente"
              >
                Tentar Novamente
              </Button>
              <Button
                onClick={() => navigate('/')}
                variant="outline"
                className="border-gray-700 text-gray-300 hover:bg-gray-800"
                data-testid="btn-voltar"
              >
                Voltar ao Ranking
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
