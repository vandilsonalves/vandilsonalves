import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DollarSign, TrendingUp, CreditCard, QrCode,
  ArrowUpRight, ArrowDownRight, RefreshCw, Loader2,
  CheckCircle, Clock, XCircle, BarChart3, Users, Eye, ShoppingCart, ArrowDown,
  Download, FileSpreadsheet, FileText, HelpCircle, UserCheck
} from 'lucide-react';
import { toast } from 'sonner';
import { downloadFile, downloadCSVContent } from '@/utils/downloadHelper';

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

function FunnelVisual({ data }) {
  const steps = [
    {
      label: 'Visitantes',
      value: data.visitantes_unicos || 0,
      icon: Eye,
      color: 'blue',
      bgFrom: 'from-blue-500/20',
      bgTo: 'to-blue-500/5',
      borderColor: 'border-blue-500/30',
      textColor: 'text-blue-400',
    },
    {
      label: 'Cadastros',
      value: data.cadastros || 0,
      icon: Users,
      color: 'amber',
      bgFrom: 'from-amber-500/20',
      bgTo: 'to-amber-500/5',
      borderColor: 'border-amber-500/30',
      textColor: 'text-amber-400',
      rate: data.taxa_visitante_cadastro,
      rateLabel: 'dos visitantes',
    },
    {
      label: 'Pagamentos',
      value: data.pagamentos || 0,
      icon: ShoppingCart,
      color: 'emerald',
      bgFrom: 'from-emerald-500/20',
      bgTo: 'to-emerald-500/5',
      borderColor: 'border-emerald-500/30',
      textColor: 'text-emerald-400',
      rate: data.taxa_cadastro_pagamento,
      rateLabel: 'dos cadastrados',
    },
  ];

  return (
    <div className="space-y-2" data-testid="funnel-visual">
      {steps.map((step, i) => {
        const Icon = step.icon;
        const widthPercent = i === 0 ? 100 : Math.max(20, (step.value / (steps[0].value || 1)) * 100);
        return (
          <div key={step.label}>
            {i > 0 && (
              <div className="flex items-center justify-center py-1">
                <ArrowDown className="w-4 h-4 text-gray-600" />
                {step.rate !== undefined && (
                  <span className={`text-xs ml-2 font-medium ${step.rate > 0 ? step.textColor : 'text-gray-600'}`}>
                    {step.rate}% {step.rateLabel}
                  </span>
                )}
              </div>
            )}
            <div
              className={`relative bg-gradient-to-r ${step.bgFrom} ${step.bgTo} border ${step.borderColor} rounded-lg p-4 transition-all duration-500`}
              style={{ width: `${widthPercent}%`, marginLeft: 'auto', marginRight: 'auto' }}
              data-testid={`funnel-step-${step.label.toLowerCase()}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className={`w-4 h-4 ${step.textColor}`} />
                  <span className="text-sm text-gray-300">{step.label}</span>
                </div>
                <span className={`text-xl font-bold ${step.textColor}`}>
                  {step.value.toLocaleString('pt-BR')}
                </span>
              </div>
            </div>
          </div>
        );
      })}

      {/* Conversion Rate Summary */}
      <div className="mt-4 pt-4 border-t border-gray-800 grid grid-cols-3 gap-3">
        <div className="text-center">
          <p className="text-2xl font-bold text-blue-400">{data.taxa_visitante_cadastro || 0}%</p>
          <p className="text-[11px] text-gray-500">Visitante &rarr; Cadastro</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-amber-400">{data.taxa_cadastro_pagamento || 0}%</p>
          <p className="text-[11px] text-gray-500">Cadastro &rarr; Pagamento</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-emerald-400">{data.taxa_conversao_total || 0}%</p>
          <p className="text-[11px] text-gray-500">Conversao Total</p>
        </div>
      </div>

      {data.receita !== undefined && (
        <div className="mt-3 text-center">
          <p className="text-sm text-gray-500">
            Receita no periodo: <span className="text-emerald-400 font-semibold">{formatCurrency(data.receita)}</span>
          </p>
        </div>
      )}
    </div>
  );
}

export default function DashboardFinanceiro() {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [visao, setVisao] = useState('diaria');
  const [conversao, setConversao] = useState(null);
  const [loadingConversao, setLoadingConversao] = useState(true);
  const [periodoConversao, setPeriodoConversao] = useState('30d');
  const [showExport, setShowExport] = useState(false);
  const [exporting, setExporting] = useState(false);

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

  const fetchConversao = async () => {
    setLoadingConversao(true);
    try {
      const res = await fetch(`${API}/admin/financeiro/conversao`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const d = await res.json();
        setConversao(d);
      }
    } catch {
      // silent
    } finally {
      setLoadingConversao(false);
    }
  };

  useEffect(() => { fetchData(); fetchConversao(); }, []);

  const handleExport = async (formato) => {
    setExporting(true);
    setShowExport(false);
    try {
      downloadFile(`/api/admin/financeiro/exportar/${formato}`);
      toast.success(`Relatório ${formato.toUpperCase()} exportado!`);
    } catch {
      toast.error('Erro ao exportar');
    } finally {
      setExporting(false);
    }
  };

  // Auto-refresh quando receber notificacao de pagamento via WebSocket
  useEffect(() => {
    const handlePaymentAlert = (e) => {
      const alert = e.detail;
      if (alert?.alert_type?.includes('pagamento')) {
        fetchData();
      }
    };
    window.addEventListener('admin-alert', handlePaymentAlert);
    return () => window.removeEventListener('admin-alert', handlePaymentAlert);
  }, []);

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

  const statusIcon = (s, isManual) => {
    if (s === 'paid' && isManual) return <HelpCircle className="w-3.5 h-3.5 text-amber-400" />;
    if (s === 'paid') return <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />;
    if (s === 'pending') return <Clock className="w-3.5 h-3.5 text-amber-400" />;
    return <XCircle className="w-3.5 h-3.5 text-red-400" />;
  };

  const statusLabel = (s, isManual) => {
    if (s === 'paid' && isManual) return 'Pago?';
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
        <div className="flex items-center gap-2">
          <Button
            onClick={fetchData}
            variant="outline"
            size="sm"
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            data-testid="btn-refresh-financeiro"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Atualizar
          </Button>
          <div className="relative">
            <Button
              onClick={() => setShowExport(!showExport)}
              variant="outline"
              size="sm"
              disabled={exporting}
              className="border-emerald-700 text-emerald-400 hover:bg-emerald-900/30"
              data-testid="btn-exportar-dados"
            >
              {exporting ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Download className="w-3.5 h-3.5 mr-1.5" />}
              Exportar Dados
            </Button>
            {showExport && (
              <div className="absolute right-0 top-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 overflow-hidden" data-testid="export-dropdown">
                <button
                  onClick={() => handleExport('pdf')}
                  className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
                  data-testid="btn-export-pdf"
                >
                  <FileText className="w-4 h-4 text-red-400" /> Exportar PDF
                </button>
                <button
                  onClick={() => handleExport('excel')}
                  className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
                  data-testid="btn-export-excel"
                >
                  <FileSpreadsheet className="w-4 h-4 text-green-400" /> Exportar Excel
                </button>
              </div>
            )}
          </div>
        </div>
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
                <span className="text-gray-400">Cartao (Efi Bank)</span>
              </div>
              <span className="text-white font-medium">{formatCurrency(distribuicao_gateway.cartao.valor)}</span>
            </div>
            {distribuicao_gateway.manual?.count > 0 && (
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <UserCheck className="w-3.5 h-3.5 text-amber-400" />
                  <span className="text-gray-400">Manual/Cortesia</span>
                </div>
                <span className="text-amber-400 font-medium">{distribuicao_gateway.manual.count}x</span>
              </div>
            )}
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
              {transacoes_recentes.map((tx, i) => {
                const isManual = tx.is_manual || tx.gateway === 'admin_manual';
                return (
                <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition" data-testid={`transacao-row-${i}`}>
                  <td className="py-3 pr-3">
                    <p className="text-white text-sm truncate max-w-[160px]">{tx.user_nome || '-'}</p>
                    <p className="text-gray-500 text-xs truncate max-w-[160px]">{tx.user_email || '-'}</p>
                  </td>
                  <td className="py-3 pr-3">
                    {isManual ? (
                      <Badge variant="outline" className="border-amber-500/30 text-amber-400 bg-amber-500/5">
                        <UserCheck className="w-3 h-3 mr-1" /> Manual
                      </Badge>
                    ) : tx.tipo === 'pix' ? (
                      <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 bg-emerald-500/5">
                        <QrCode className="w-3 h-3 mr-1" /> PIX
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="border-indigo-500/30 text-indigo-400 bg-indigo-500/5">
                        <CreditCard className="w-3 h-3 mr-1" /> Cartao
                      </Badge>
                    )}
                  </td>
                  <td className="py-3 pr-3">
                    {isManual ? (
                      <span className="text-gray-500 text-xs italic">Cortesia</span>
                    ) : (
                      <>
                        <span className="text-white font-medium">{formatCurrency(tx.amount)}</span>
                        {tx.parcelas > 1 && (
                          <span className="text-gray-500 text-xs ml-1">({tx.parcelas}x {formatCurrency(tx.valor_parcela)})</span>
                        )}
                      </>
                    )}
                  </td>
                  <td className="py-3 pr-3">
                    <div className="flex items-center gap-1.5 group relative">
                      {statusIcon(tx.payment_status, isManual)}
                      <span className={`text-xs ${
                        isManual ? 'text-amber-400' :
                        tx.payment_status === 'paid' ? 'text-emerald-400' :
                        tx.payment_status === 'pending' ? 'text-amber-400' : 'text-red-400'
                      }`}>
                        {statusLabel(tx.payment_status, isManual)}
                      </span>
                      {isManual && (
                        <div className="hidden group-hover:block absolute left-0 bottom-full mb-1 bg-gray-800 border border-gray-700 rounded-lg p-2 z-50 whitespace-nowrap shadow-xl">
                          <p className="text-xs text-amber-400 font-medium">Autorizado manualmente</p>
                          <p className="text-[10px] text-gray-400">{tx.admin_nome ? `Por: ${tx.admin_nome}` : 'Pagamento externo ou cortesia'}</p>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="py-3 text-gray-400 text-xs whitespace-nowrap">
                    {tx.data_criacao ? new Date(tx.data_criacao).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '-'}
                  </td>
                </tr>
                );
              })}
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

      {/* Funil de Conversao */}
      <Card className="bg-gray-900 border-gray-800 p-6" data-testid="painel-conversao">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Funil de Conversao</h3>
          </div>
          <div className="flex gap-1 bg-gray-800 rounded-lg p-0.5">
            {['7d', '30d', 'total'].map(p => (
              <button
                key={p}
                onClick={() => setPeriodoConversao(p)}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${periodoConversao === p ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
                data-testid={`btn-periodo-${p}`}
              >
                {p === '7d' ? '7 dias' : p === '30d' ? '30 dias' : 'Total'}
              </button>
            ))}
          </div>
        </div>

        {loadingConversao ? (
          <div className="flex items-center justify-center py-10">
            <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
          </div>
        ) : conversao && conversao[periodoConversao] ? (
          <div>
            {/* Funnel Steps */}
            <FunnelVisual data={conversao[periodoConversao]} />

            {/* Daily Trend (only for 7d and 30d) */}
            {conversao.funil_diario && periodoConversao !== 'total' && (
              <div className="mt-6 pt-6 border-t border-gray-800">
                <h4 className="text-sm text-gray-400 mb-3">Tendencia Diaria (14 dias)</h4>
                <div className="flex items-end gap-[3px] h-24" data-testid="trend-chart">
                  {conversao.funil_diario.map((d, i) => {
                    const maxV = Math.max(...conversao.funil_diario.map(x => x.visitantes || 1), 1);
                    const hV = Math.max((d.visitantes / maxV) * 100, 3);
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center gap-0.5 group relative">
                        <div className="w-full rounded-t bg-blue-500/60" style={{ height: `${hV}%`, minHeight: '2px' }} />
                        {d.cadastros > 0 && <div className="w-full h-1 bg-amber-500 rounded" />}
                        {d.pagamentos > 0 && <div className="w-full h-1 bg-emerald-500 rounded" />}
                        <div className="absolute bottom-full mb-1 hidden group-hover:block bg-gray-800 text-[10px] text-gray-300 px-2 py-1 rounded border border-gray-700 whitespace-nowrap z-10">
                          {d.data?.slice(5)}: {d.visitantes}v / {d.cadastros}c / {d.pagamentos}p
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="flex gap-4 mt-2 text-[10px] text-gray-500">
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-blue-500/60 rounded" />Visitantes</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-amber-500 rounded" />Cadastros</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-emerald-500 rounded" />Pagamentos</span>
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-10">Nenhum dado disponivel</p>
        )}
      </Card>
    </div>
  );
}
