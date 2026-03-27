import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Shield, CheckCircle, Lock, CreditCard, Star, BarChart3, Users, Activity, Clock, Zap, Timer, Copy, QrCode, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

function PixCheckout({ token, planoInfo }) {
  const [gerando, setGerando] = useState(false);
  const [pixData, setPixData] = useState(null);
  const [polling, setPolling] = useState(false);
  const pollingRef = useRef(null);

  const gerarPix = async () => {
    setGerando(true);
    try {
      const res = await fetch(`${API}/api/efi/pix/criar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({}),
      });
      if (!res.ok) {
        const err = await res.json();
        toast.error(err.detail || 'Erro ao gerar PIX');
        return;
      }
      const data = await res.json();
      setPixData(data);
      toast.success('QR Code PIX gerado!');
      startPolling(data.txid);
    } catch (err) {
      toast.error('Erro de conexao. Tente novamente.');
      console.error(err);
    } finally {
      setGerando(false);
    }
  };

  const startPolling = (txid) => {
    setPolling(true);
    if (pollingRef.current) clearInterval(pollingRef.current);
    pollingRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API}/api/efi/pix/status/${txid}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          if (data.payment_status === 'paid') {
            clearInterval(pollingRef.current);
            setPolling(false);
            toast.success('Pagamento confirmado! Bem-vindo ao Premium!');
            setTimeout(() => window.location.reload(), 2000);
          }
        }
      } catch {}
    }, 5000);
  };

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const copiarCodigoPix = () => {
    if (pixData?.qrcode?.qrcode) {
      navigator.clipboard.writeText(pixData.qrcode.qrcode);
      toast.success('Codigo PIX copiado!');
    }
  };

  if (pixData) {
    return (
      <div className="space-y-5" data-testid="pix-resultado">
        <div className="text-center">
          <p className="text-sm text-gray-400 mb-4">Escaneie o QR Code ou copie o codigo PIX</p>
          {pixData.qrcode?.imagemQrcode && (
            <div className="flex justify-center mb-4">
              <div className="bg-white rounded-xl p-3 inline-block">
                <img
                  src={pixData.qrcode.imagemQrcode}
                  alt="QR Code PIX"
                  className="w-52 h-52"
                  data-testid="pix-qrcode-img"
                />
              </div>
            </div>
          )}
          <div className="bg-gray-800/60 rounded-lg p-3 mb-4">
            <p className="text-xs text-gray-500 mb-1.5">PIX Copia e Cola</p>
            <p className="text-xs text-gray-300 font-mono break-all leading-relaxed select-all" data-testid="pix-copia-cola">
              {pixData.qrcode?.qrcode?.substring(0, 80)}...
            </p>
          </div>
          <Button
            onClick={copiarCodigoPix}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-11"
            data-testid="btn-copiar-pix"
          >
            <Copy className="w-4 h-4 mr-2" /> Copiar Codigo PIX
          </Button>
          {polling && (
            <div className="mt-4 flex items-center justify-center gap-2 text-amber-400" data-testid="pix-aguardando">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span className="text-sm">Aguardando confirmacao do pagamento...</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="text-center" data-testid="pix-gerar">
      <div className="mb-5">
        <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
          <QrCode className="w-8 h-8 text-emerald-400" />
        </div>
        <p className="text-gray-400 text-sm">Pague com PIX e tenha acesso imediato</p>
      </div>
      <Button
        onClick={gerarPix}
        disabled={gerando}
        className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-12 text-base font-medium"
        data-testid="btn-gerar-pix"
      >
        {gerando ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            Gerando PIX...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <QrCode className="w-4 h-4" /> Gerar QR Code PIX - R$ 97,00
          </span>
        )}
      </Button>
    </div>
  );
}

export default function PagamentoPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [planoInfo, setPlanoInfo] = useState(null);
  const [loadingPlano, setLoadingPlano] = useState(true);
  const [metodo, setMetodo] = useState('pix');

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
        headers: { Authorization: `Bearer ${token}` },
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

  const iniciarPagamentoStripe = async () => {
    setLoading(true);
    try {
      const origin = window.location.origin;
      const res = await fetch(`${API}/api/pagamentos/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ origin_url: origin }),
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

  const dataLimite = new Date('2026-12-14T23:59:59Z');
  const agora = new Date();
  const diffMs = dataLimite - agora;
  const diasRestantesOferta = Math.max(0, Math.ceil(diffMs / (1000 * 60 * 60 * 24)));
  const mostrarContagem = diasRestantesOferta <= 30 && diasRestantesOferta > 0;

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

        {/* Banner contagem regressiva */}
        {mostrarContagem && (
          <div className="mb-8 rounded-xl overflow-hidden" data-testid="banner-contagem">
            <div className="bg-gradient-to-r from-red-600 to-orange-500 p-4 flex items-center justify-center gap-3">
              <Timer className="w-5 h-5 text-white animate-pulse" />
              <p className="text-white font-bold text-sm sm:text-base">
                {diasRestantesOferta === 1
                  ? 'Ultimo dia! A oferta encerra amanha!'
                  : `Faltam ${diasRestantesOferta} dias para o fim da oferta!`}
              </p>
            </div>
            <div className="bg-gray-900 border border-t-0 border-orange-500/30 px-4 py-2.5 text-center">
              <p className="text-xs text-gray-400">
                Apos 14/12/2026, o valor sera de <span className="text-white font-semibold">12x R$ 119,00</span>
              </p>
            </div>
          </div>
        )}

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
          <div className="absolute top-0 right-0 bg-red-500 text-white text-xs font-bold px-3 py-1.5 rounded-bl-xl" data-testid="badge-oferta">
            OFERTA
          </div>

          <div className="p-8 text-center border-b border-gray-800">
            <p className="text-gray-500 line-through text-lg mb-1" data-testid="preco-original">
              De R$ 197,00
            </p>
            <div className="flex items-baseline justify-center gap-1" data-testid="preco-atual">
              <span className="text-lg text-gray-400">5x de</span>
              <span className="text-5xl font-bold">R$ 19</span>
              <span className="text-lg text-gray-400 font-normal">,40</span>
            </div>
            <p className="text-gray-400 text-sm mt-2">ou R$ 97,00 a vista - Valido ate 31/12/2026</p>
            <div className="inline-flex items-center gap-1.5 mt-3 bg-amber-500/10 border border-amber-500/20 rounded-full px-3 py-1">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-xs text-amber-400 font-medium">Oferta valida ate 14/12/2026</span>
            </div>
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
                <span className="text-sm text-gray-200">Acesso ate 31/12/2026</span>
              </li>
            </ul>
          </div>

          {/* Metodos de pagamento */}
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
              <div className="space-y-4">
                {/* Tabs de metodo */}
                <div className="flex rounded-lg overflow-hidden border border-gray-700" data-testid="metodo-tabs">
                  <button
                    onClick={() => setMetodo('pix')}
                    className={`flex-1 py-2.5 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                      metodo === 'pix'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:text-gray-200'
                    }`}
                    data-testid="tab-pix"
                  >
                    <QrCode className="w-4 h-4" /> PIX
                  </button>
                  <button
                    onClick={() => setMetodo('cartao')}
                    className={`flex-1 py-2.5 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                      metodo === 'cartao'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:text-gray-200'
                    }`}
                    data-testid="tab-cartao"
                  >
                    <CreditCard className="w-4 h-4" /> Cartao
                  </button>
                </div>

                {/* Conteudo do metodo selecionado */}
                {metodo === 'pix' ? (
                  <PixCheckout token={token} planoInfo={planoInfo} />
                ) : (
                  <div data-testid="cartao-checkout">
                    <Button
                      onClick={iniciarPagamentoStripe}
                      disabled={loading}
                      className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-12 text-base font-medium"
                      data-testid="btn-assinar-cartao"
                    >
                      {loading ? (
                        <span className="flex items-center gap-2">
                          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                          Processando...
                        </span>
                      ) : (
                        <span className="flex items-center gap-2">
                          <CreditCard className="w-4 h-4" /> Pagar com Cartao - 5x R$ 19,40
                        </span>
                      )}
                    </Button>
                    <p className="text-xs text-gray-500 text-center mt-2">Pagamento seguro via Stripe</p>
                  </div>
                )}
              </div>
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
