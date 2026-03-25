import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Shield, CheckCircle, Lock, CreditCard, Star, BarChart3, Users, Activity, Clock, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

export default function PagamentoPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [planoInfo, setPlanoInfo] = useState(null);
  const [loadingPlano, setLoadingPlano] = useState(true);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchPlano();
  }, [token]);

  const fetchPlano = async () => {
    try {
      const res = await fetch(`${API}/api/pagamentos/meu-plano`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setPlanoInfo(data);
      if (data.tem_acesso_premium && data.status === 'autorizado') {
        toast.success('Voce ja possui acesso Premium!');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPlano(false);
    }
  };

  const iniciarPagamento = async () => {
    setLoading(true);
    try {
      const origin = window.location.origin;
      const res = await fetch(`${API}/api/pagamentos/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ origin_url: origin })
      });

      if (!res.ok) {
        const err = await res.json();
        toast.error(err.detail || 'Erro ao iniciar pagamento');
        return;
      }

      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (err) {
      toast.error('Erro de conexao. Tente novamente.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const recursos = [
    { icon: BarChart3, label: 'Raio-X completo do atleta' },
    { icon: Activity, label: 'Integracao Strava' },
    { icon: Users, label: 'Feed social: curtir, comentar e postar' },
    { icon: Star, label: 'Stories e compartilhamento' },
    { icon: Shield, label: 'Edicao completa do perfil' },
  ];

  if (loadingPlano) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Carregando...</div>
      </div>
    );
  }

  const pv = planoInfo?.plano_vigente;
  const isLancamento = pv?.id === 'atleta_premium_lancamento';

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="pagamento-page">
      <div className="max-w-2xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-4 py-1.5 mb-6">
            <Star className="w-4 h-4 text-emerald-400" />
            <span className="text-sm text-emerald-400 font-medium">Atleta Premium</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold mb-3">
            Desbloqueie todo o potencial
          </h1>
          <p className="text-gray-400 text-base">
            Acesso completo a todas as funcionalidades do Ranking Run Pro
          </p>
        </div>

        {/* Status atual */}
        {planoInfo && (
          <div className={`rounded-xl p-4 mb-8 border ${
            planoInfo.status === 'autorizado' ? 'bg-emerald-500/10 border-emerald-500/30' :
            planoInfo.status === 'em_teste' ? 'bg-amber-500/10 border-amber-500/30' :
            'bg-red-500/10 border-red-500/30'
          }`} data-testid="status-plano">
            <div className="flex items-center gap-3">
              {planoInfo.status === 'autorizado' ? (
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              ) : planoInfo.status === 'em_teste' ? (
                <Shield className="w-5 h-5 text-amber-400" />
              ) : (
                <Lock className="w-5 h-5 text-red-400" />
              )}
              <div>
                <p className="font-medium text-sm">
                  {planoInfo.status === 'autorizado' ? 'Plano Premium Ativo' :
                   planoInfo.status === 'em_teste' ? `Periodo de Teste - ${planoInfo.dias_restantes} dias restantes` :
                   'Acesso Expirado'}
                </p>
                {planoInfo.expira_em && (
                  <p className="text-xs text-gray-400 mt-0.5">
                    Valido ate {new Date(planoInfo.expira_em).toLocaleDateString('pt-BR')}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Card de preco */}
        <div className="bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden mb-8 relative" data-testid="plano-card">
          {/* Badge de oferta */}
          {isLancamento && (
            <div className="absolute top-0 right-0 bg-red-500 text-white text-xs font-bold px-3 py-1.5 rounded-bl-xl" data-testid="badge-oferta">
              OFERTA
            </div>
          )}

          <div className="p-8 text-center border-b border-gray-800">
            {isLancamento ? (
              <>
                <p className="text-gray-500 line-through text-lg mb-1" data-testid="preco-original">
                  De R$ 197,00
                </p>
                <div className="text-5xl font-bold mb-1" data-testid="preco-atual">
                  R$ 97<span className="text-lg text-gray-400 font-normal">,00</span>
                </div>
                <p className="text-gray-400 text-sm">Pagamento unico - Valido ate 31/12/2026</p>
                <div className="inline-flex items-center gap-1.5 mt-3 bg-amber-500/10 border border-amber-500/20 rounded-full px-3 py-1">
                  <Clock className="w-3.5 h-3.5 text-amber-400" />
                  <span className="text-xs text-amber-400 font-medium">Oferta valida ate 14/12/2026</span>
                </div>
              </>
            ) : (
              <>
                <div className="text-5xl font-bold mb-1" data-testid="preco-atual">
                  12x R$ 119<span className="text-lg text-gray-400 font-normal">,00</span>
                </div>
                <p className="text-gray-400 text-sm">Plano anual - Acesso completo por 12 meses</p>
              </>
            )}
          </div>

          <div className="p-6">
            <p className="text-sm text-gray-400 mb-4 font-medium uppercase tracking-wider">O que esta incluso</p>
            <ul className="space-y-3">
              {recursos.map((r, i) => (
                <li key={i} className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                    <r.icon className="w-4 h-4 text-emerald-400" />
                  </div>
                  <span className="text-sm text-gray-200">{r.label}</span>
                </li>
              ))}
              <li className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                  <CreditCard className="w-4 h-4 text-emerald-400" />
                </div>
                <span className="text-sm text-gray-200">
                  {isLancamento ? 'Acesso ate 31/12/2026' : 'Acesso por 12 meses'}
                </span>
              </li>
            </ul>
          </div>

          <div className="p-6 pt-0">
            {planoInfo?.status === 'autorizado' ? (
              <Button
                className="w-full bg-gray-700 text-gray-300 cursor-not-allowed"
                disabled
                data-testid="btn-ja-premium"
              >
                <CheckCircle className="w-4 h-4 mr-2" /> Voce ja e Premium
              </Button>
            ) : (
              <Button
                onClick={iniciarPagamento}
                disabled={loading}
                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-12 text-base font-medium"
                data-testid="btn-assinar"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                    Processando...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Zap className="w-4 h-4" /> {isLancamento ? 'Aproveitar Oferta - R$ 97,00' : 'Assinar por 12x R$ 119,00'}
                  </span>
                )}
              </Button>
            )}
          </div>
        </div>

        {/* Voltar */}
        <div className="text-center">
          <button
            onClick={() => navigate('/')}
            className="text-sm text-gray-500 hover:text-gray-300 transition"
            data-testid="btn-voltar-ranking"
          >
            Voltar ao Ranking
          </button>
        </div>
      </div>
    </div>
  );
}
