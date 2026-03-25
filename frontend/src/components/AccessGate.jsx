import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Lock, CreditCard, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * AccessGate - Componente que bloqueia acesso de usuarios expirados.
 * Envolve paginas premium e mostra overlay com CTA de pagamento quando
 * o usuario nao tem acesso.
 * 
 * Props:
 * - children: conteudo a ser renderizado se tiver acesso
 * - recurso: nome do recurso para exibicao (ex: "Raio-X", "Feed")
 */
export default function AccessGate({ children, recurso = "este recurso" }) {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null); // null = loading, object = data
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token || !user) {
      setLoading(false);
      return;
    }
    // Admin sempre passa
    if (user.role === 'admin' || user.role === 'super_admin') {
      setStatus({ tem_acesso_premium: true, status: 'admin' });
      setLoading(false);
      return;
    }
    checkAccess();
  }, [token, user]);

  const checkAccess = async () => {
    try {
      const res = await fetch(`${API}/api/pagamentos/meu-plano`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      // Em caso de erro, libera acesso para nao bloquear por falha tecnica
      setStatus({ tem_acesso_premium: true, status: 'fallback' });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-pulse text-gray-500 text-sm">Verificando acesso...</div>
      </div>
    );
  }

  // Se nao esta logado, deixa a pagina lidar (redirect para login)
  if (!token || !user) {
    return children;
  }

  // Se tem acesso, renderiza o conteudo normalmente
  if (status?.tem_acesso_premium) {
    return children;
  }

  // Bloqueado - mostrar overlay
  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="access-gate-blocked">
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
          <Lock className="w-10 h-10 text-red-400" />
        </div>
        <h2 className="text-2xl font-bold mb-3">Acesso Restrito</h2>
        <p className="text-gray-400 mb-2">
          Seu periodo de teste expirou. Para acessar <strong className="text-white">{recurso}</strong>, assine o plano Atleta Premium.
        </p>
        <p className="text-gray-500 text-sm mb-8">
          Plano unico de R$ 97,00 com validade ate 31/12/2026.
        </p>
        <div className="flex flex-col gap-3">
          <Button
            onClick={() => navigate('/pagamento')}
            className="bg-emerald-600 hover:bg-emerald-500 text-white h-11"
            data-testid="btn-assinar-premium"
          >
            <CreditCard className="w-4 h-4 mr-2" /> Assinar Atleta Premium
          </Button>
          <Button
            onClick={() => navigate('/')}
            variant="outline"
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            data-testid="btn-voltar-ranking"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Voltar ao Ranking
          </Button>
        </div>
      </div>
    </div>
  );
}
