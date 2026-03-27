import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DollarSign, TrendingUp, CreditCard, QrCode,
  ArrowUpRight, ArrowDownRight, RefreshCw, Loader2,
  CheckCircle, Clock, XCircle, BarChart3
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MESES_PT = {
  '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
  '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
  '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez',
};

function formatCurrency(val) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
}

function MiniBarChart({ data, height = 120, color = '#10b981' }) {
  if (!data || data.length === 0) return null;
  const maxVal = Math.max(...data.map(d => d.valor), 1);

  return (
    <div className="flex items-end gap-[2px] w-full" style={{ height }} data-testid="mini-bar-chart">
      {data.map((d, i) => {
        const h = Math.max((d.valor / maxVal) * 100, 2);
        return (
          <div
            key={i}
            className="flex-1 rounded-t transition-all duration-300 hover:opacity-80 group relative"
            style={{ height: `${h}%`, backgroundColor: d.valor > 0 ? color : '#1f2937', minWidth: '4px' }}
          >
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-gray-800 text-white text-[10px] px-1.5 py-0.5 rounded whitespace-nowrap z-10 border border-gray-700">
              {d.data ? d.data.slice(8) : d.mes?.slice(5)}: {formatCurrency(d.valor)}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function DonutChart({ pix, cartao }) {
  const total = pix + cartao;
  if (total === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-500 text-sm">
        Sem dados
      </div>
    );
  }
  const pixPct = (pix / total) * 100;
  const cartaoPct = (cartao / total) * 100;
  const circumference = 2 * Math.PI * 40;
  const pixArc = (pixPct / 100) * circumference;
  const cartaoArc = (cartaoPct / 100) * circumference;

  return (
    <div className="flex items-center gap-6" data-testid="donut-chart">
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="40" fill="none" stroke="#1f2937" strokeWidth="12" />
        <circle
          cx="50" cy="50" r="40" fill="none"
          stroke="#10b981" strokeWidth="12"
          strokeDasharray={`${pixArc} ${circumference}`}
          strokeDashoffset="0"
          transform="rotate(-90 50 50)"
          className="transition-all duration-700"
        />
        <circle
          cx="50" cy="50" r="40" fill="none"
          stroke="#6366f1" strokeWidth="12"
          strokeDasharray={`${cartaoArc} ${circumference}`}
          strokeDashoffset={`-${pixArc}`}
          transform="rotate(-90 50 50)"
          className="transition-all duration-700"
        />
        <text x="50" y="50" textAnchor="middle" dominantBaseline="central" className="fill-white text-xs font-bold">
          {total}
        </text>
      </svg>
      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500" />
          <span className="text-gray-300">PIX: {pixPct.toFixed(0)}%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-indigo-500" />
          <span className="text-gray-300">Cartao: {cartaoPct.toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
}

export default function DashboardFinanceiro() {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [visao, setVisao] = useState('diaria');

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/financeiro/resumo`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const d = await res.json();
        setData(d);
      } else {
        toast.error('Erro ao carregar dados financeiros');
      }
    } catch {
      toast.error('Erro de conexao');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20" data-testid="financeiro-loading">
        <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
        <span className="ml-2 text-gray-400">Carregando dados financeiros...</span>
      </div>
    );
  }

  if (!data) return null;

  const { totais, distribuicao_gateway, receita_diaria, receita_mensal, transacoes_recentes } = data;

  const statusIcon = (s) => {
    if (s === 'paid') return <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />;
    if (s === 'pending') return <Clock className="w-3.5 h-3.5 text-amber-400" />;
    return <XCircle className="w-3.5 h-3.5 text-red-400" />;
  };

  const statusLabel = (s) => {
    if (s === 'paid') return 'Pago';
    if (s === 'pending') return 'Pendente';
    return s;
  };

  return (
    <div className="space-y-6" data-testid="dashboard-financeiro">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Dashboard Financeiro</h2>
          <p className="text-sm text-gray-400 mt-0.5">Transacoes PIX e Cartao de Credito</p>
        </div>
        <Button
          onClick={fetchData}
          variant="outline"
          size="sm"
          className="border-gray-700 text-gray-300 hover:bg-gray-800"
          data-testid="btn-refresh-financeiro"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Atualizar
        </Button>
      </div>

      {/* Cards KPI */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gray-900 border-gray-800 p-4" data-testid="kpi-receita-total">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 uppercase tracking-wider">Receita Total</span>
            <div className="w-8 h-8 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white">{formatCurrency(totais.receita_total)}</p>
          <p className="text-xs text-gray-500 mt-1">{totais.transacoes_pagas} pagas de {totais.total_transacoes}</p>
        </Card>

        <Card className="bg-gray-900 border-gray-800 p-4" data-testid="kpi-receita-pix">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 uppercase tracking-wider">Receita PIX</span>
            <div className="w-8 h-8 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <QrCode className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-emerald-400">{formatCurrency(totais.receita_pix)}</p>
          <p className="text-xs text-gray-500 mt-1">{distribuicao_gateway.pix.count} transacoes</p>
        </Card>

        <Card className="bg-gray-900 border-gray-800 p-4" data-testid="kpi-receita-cartao">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 uppercase tracking-wider">Receita Cartao</span>
            <div className="w-8 h-8 bg-indigo-500/10 rounded-lg flex items-center justify-center">
              <CreditCard className="w-4 h-4 text-indigo-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-indigo-400">{formatCurrency(totais.receita_cartao)}</p>
          <p className="text-xs text-gray-500 mt-1">{distribuicao_gateway.cartao.count} transacoes</p>
        </Card>

        <Card className="bg-gray-900 border-gray-800 p-4" data-testid="kpi-ticket-medio">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 uppercase tracking-wider">Ticket Medio</span>
            <div className="w-8 h-8 bg-amber-500/10 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-amber-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white">{formatCurrency(totais.ticket_medio)}</p>
          <p className="text-xs text-gray-500 mt-1">{totais.transacoes_pendentes} pendentes</p>
        </Card>
      </div>

      {/* Graficos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Receita por periodo */}
        <Card className="bg-gray-900 border-gray-800 p-5 lg:col-span-2" data-testid="grafico-receita">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Receita por Periodo</h3>
            <div className="flex rounded-md overflow-hidden border border-gray-700">
              <button
                onClick={() => setVisao('diaria')}
                className={`px-3 py-1 text-xs font-medium transition-colors ${
                  visao === 'diaria' ? 'bg-emerald-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'
                }`}
                data-testid="tab-diaria"
              >
                Diaria
              </button>
              <button
                onClick={() => setVisao('mensal')}
                className={`px-3 py-1 text-xs font-medium transition-colors ${
                  visao === 'mensal' ? 'bg-emerald-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'
                }`}
                data-testid="tab-mensal"
              >
                Mensal
              </button>
            </div>
          </div>
          {visao === 'diaria' ? (
            <>
              <MiniBarChart data={receita_diaria} height={140} color="#10b981" />
              <div className="flex justify-between mt-2 text-[10px] text-gray-600">
                <span>{receita_diaria[0]?.data?.slice(5)}</span>
                <span>Ultimos 30 dias</span>
                <span>{receita_diaria[receita_diaria.length - 1]?.data?.slice(5)}</span>
              </div>
            </>
          ) : (
            <>
              <MiniBarChart data={receita_mensal} height={140} color="#6366f1" />
              <div className="flex justify-between mt-2 text-[10px] text-gray-600">
                {receita_mensal.length > 0 && (
                  <>
                    <span>{MESES_PT[receita_mensal[0]?.mes?.slice(5)] || receita_mensal[0]?.mes?.slice(5)}</span>
                    <span>Ultimos 12 meses</span>
                    <span>{MESES_PT[receita_mensal[receita_mensal.length - 1]?.mes?.slice(5)] || ''}</span>
                  </>
                )}
              </div>
            </>
          )}
        </Card>

        {/* Distribuicao por gateway */}
        <Card className="bg-gray-900 border-gray-800 p-5" data-testid="grafico-distribuicao">
          <h3 className="text-sm font-semibold text-white mb-4">Distribuicao por Gateway</h3>
          <DonutChart
            pix={distribuicao_gateway.pix.count}
            cartao={distribuicao_gateway.cartao.count}
          />
          <div className="mt-4 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <QrCode className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-gray-400">PIX (Efi Bank)</span>
              </div>
              <span className="text-white font-medium">{formatCurrency(distribuicao_gateway.pix.valor)}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <CreditCard className="w-3.5 h-3.5 text-indigo-400" />
                <span className="text-gray-400">Cartao (Stripe)</span>
              </div>
              <span className="text-white font-medium">{formatCurrency(distribuicao_gateway.cartao.valor)}</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Transacoes Recentes */}
      <Card className="bg-gray-900 border-gray-800 p-5" data-testid="tabela-transacoes">
        <h3 className="text-sm font-semibold text-white mb-4">Transacoes Recentes</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left text-xs text-gray-500 pb-3 font-medium">Atleta</th>
                <th className="text-left text-xs text-gray-500 pb-3 font-medium">Gateway</th>
                <th className="text-left text-xs text-gray-500 pb-3 font-medium">Valor</th>
                <th className="text-left text-xs text-gray-500 pb-3 font-medium">Status</th>
                <th className="text-left text-xs text-gray-500 pb-3 font-medium">Data</th>
              </tr>
            </thead>
            <tbody>
              {transacoes_recentes.map((tx, i) => (
                <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition" data-testid={`transacao-row-${i}`}>
                  <td className="py-3 pr-3">
                    <p className="text-white text-sm truncate max-w-[160px]">{tx.user_nome || '-'}</p>
                    <p className="text-gray-500 text-xs truncate max-w-[160px]">{tx.user_email || '-'}</p>
                  </td>
                  <td className="py-3 pr-3">
                    <Badge
                      variant="outline"
                      className={tx.gateway === 'efi_bank'
                        ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/5'
                        : 'border-indigo-500/30 text-indigo-400 bg-indigo-500/5'
                      }
                    >
                      {tx.gateway === 'efi_bank' ? (
                        <><QrCode className="w-3 h-3 mr-1" /> PIX</>
                      ) : (
                        <><CreditCard className="w-3 h-3 mr-1" /> Cartao</>
                      )}
                    </Badge>
                  </td>
                  <td className="py-3 pr-3">
                    <span className="text-white font-medium">{formatCurrency(tx.amount)}</span>
                    {tx.parcelas > 1 && (
                      <span className="text-gray-500 text-xs ml-1">({tx.parcelas}x {formatCurrency(tx.valor_parcela)})</span>
                    )}
                  </td>
                  <td className="py-3 pr-3">
                    <div className="flex items-center gap-1.5">
                      {statusIcon(tx.payment_status)}
                      <span className={`text-xs ${
                        tx.payment_status === 'paid' ? 'text-emerald-400' :
                        tx.payment_status === 'pending' ? 'text-amber-400' : 'text-red-400'
                      }`}>
                        {statusLabel(tx.payment_status)}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 text-gray-400 text-xs whitespace-nowrap">
                    {tx.data_criacao ? new Date(tx.data_criacao).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '-'}
                  </td>
                </tr>
              ))}
              {transacoes_recentes.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-10 text-center text-gray-500">
                    Nenhuma transacao encontrada
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
