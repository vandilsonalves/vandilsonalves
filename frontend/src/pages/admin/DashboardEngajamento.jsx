import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import {
  Send, Eye, EyeOff, TrendingUp, Award, Loader2, Users, Zap
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardEngajamento = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchEngajamento();
  }, []);

  const fetchEngajamento = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/mensagens/engajamento`, { headers });
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.error('Erro ao buscar engajamento:', e);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-20 text-slate-400">
        Erro ao carregar dados de engajamento.
      </div>
    );
  }

  const { resumo, melhor_mensagem, timeline } = data;

  // Prepare chart data (reversed for chronological order)
  const chartData = [...timeline].reverse().map((item) => ({
    nome: item.titulo.length > 15 ? item.titulo.substring(0, 15) + '...' : item.titulo,
    titulo_completo: item.titulo,
    enviados: item.total_enviados,
    lidas: item.total_lidas,
    taxa: item.taxa_leitura,
    data: formatDate(item.data)
  }));

  return (
    <div className="space-y-6" data-testid="dashboard-engajamento">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-white dark:bg-slate-800 border-0 shadow-lg">
          <CardContent className="p-3 sm:p-5">
            <div className="flex items-center justify-between">
              <div className="min-w-0">
                <p className="text-[10px] sm:text-xs text-slate-500 uppercase font-medium tracking-wide">Total Mensagens</p>
                <p className="text-2xl sm:text-3xl font-bold text-slate-800 dark:text-white mt-1">{resumo.total_mensagens}</p>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-blue-500/10 flex items-center justify-center shrink-0">
                <Send className="w-5 h-5 sm:w-6 sm:h-6 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white dark:bg-slate-800 border-0 shadow-lg">
          <CardContent className="p-3 sm:p-5">
            <div className="flex items-center justify-between">
              <div className="min-w-0">
                <p className="text-[10px] sm:text-xs text-slate-500 uppercase font-medium tracking-wide">Notif. Enviadas</p>
                <p className="text-2xl sm:text-3xl font-bold text-slate-800 dark:text-white mt-1">{resumo.total_enviados}</p>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center shrink-0">
                <Users className="w-5 h-5 sm:w-6 sm:h-6 text-emerald-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white dark:bg-slate-800 border-0 shadow-lg">
          <CardContent className="p-3 sm:p-5">
            <div className="flex items-center justify-between">
              <div className="min-w-0">
                <p className="text-[10px] sm:text-xs text-slate-500 uppercase font-medium tracking-wide">Total Lidas</p>
                <p className="text-2xl sm:text-3xl font-bold text-emerald-600 mt-1">{resumo.total_lidas}</p>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-green-500/10 flex items-center justify-center shrink-0">
                <Eye className="w-5 h-5 sm:w-6 sm:h-6 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white dark:bg-slate-800 border-0 shadow-lg">
          <CardContent className="p-3 sm:p-5">
            <div className="flex items-center justify-between">
              <div className="min-w-0">
                <p className="text-[10px] sm:text-xs text-slate-500 uppercase font-medium tracking-wide">Taxa Média</p>
                <p className="text-2xl sm:text-3xl font-bold text-amber-500 mt-1">{resumo.taxa_media_leitura}%</p>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-amber-500/10 flex items-center justify-center shrink-0">
                <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-amber-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Melhor Mensagem */}
      {melhor_mensagem && (
        <Card className="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 border-amber-200 dark:border-amber-700 shadow-lg">
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                <Award className="w-5 h-5 text-amber-600" />
              </div>
              <div className="flex-1">
                <p className="text-xs text-amber-600 font-semibold uppercase tracking-wide">Mensagem com Melhor Engajamento</p>
                <p className="font-bold text-slate-800 dark:text-white">{melhor_mensagem.titulo}</p>
                <div className="flex items-center gap-3 mt-1">
                  <Badge className="bg-green-100 text-green-700 text-xs">
                    <Eye className="w-3 h-3 mr-1" /> {melhor_mensagem.taxa_leitura}% leram
                  </Badge>
                  <span className="text-xs text-slate-500">
                    {melhor_mensagem.total_lidas}/{melhor_mensagem.total_enviados} destinatários
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart - Enviados vs Lidas */}
        <Card className="bg-white dark:bg-slate-800 border-0 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Send className="w-4 h-4 text-blue-500" />
              Enviados vs Lidos por Mensagem
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                  <XAxis dataKey="data" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#fff' }}
                    formatter={(value, name) => [value, name === 'enviados' ? 'Enviados' : 'Lidos']}
                    labelFormatter={(label, payload) => payload?.[0]?.payload?.titulo_completo || label}
                  />
                  <Bar dataKey="enviados" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Enviados" />
                  <Bar dataKey="lidas" fill="#10b981" radius={[4, 4, 0, 0]} name="Lidos" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-slate-400 py-10">Sem dados de mensagens</p>
            )}
          </CardContent>
        </Card>

        {/* Area Chart - Taxa de Leitura */}
        <Card className="bg-white dark:bg-slate-800 border-0 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-500" />
              Taxa de Leitura ao Longo do Tempo
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <defs>
                    <linearGradient id="taxaGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                  <XAxis dataKey="data" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} unit="%" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#fff' }}
                    formatter={(value) => [`${value}%`, 'Taxa de Leitura']}
                    labelFormatter={(label, payload) => payload?.[0]?.payload?.titulo_completo || label}
                  />
                  <Area type="monotone" dataKey="taxa" stroke="#10b981" strokeWidth={2} fill="url(#taxaGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-slate-400 py-10">Sem dados</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Timeline Table */}
      <Card className="bg-white dark:bg-slate-800 border-0 shadow-lg">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Zap className="w-4 h-4 text-purple-500" />
            Detalhamento por Mensagem
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm min-w-[700px]" data-testid="engajamento-table">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="text-left py-3 px-3 text-slate-500 font-medium">Mensagem</th>
                  <th className="text-center py-3 px-3 text-slate-500 font-medium">Data</th>
                  <th className="text-center py-3 px-3 text-slate-500 font-medium">Enviados</th>
                  <th className="text-center py-3 px-3 text-slate-500 font-medium">Lidos</th>
                  <th className="text-center py-3 px-3 text-slate-500 font-medium">Não Lidos</th>
                  <th className="text-center py-3 px-3 text-slate-500 font-medium">Taxa</th>
                  <th className="text-center py-3 px-3 text-slate-500 font-medium">Filtro</th>
                </tr>
              </thead>
              <tbody>
                {timeline.map((item, idx) => (
                  <tr key={idx} className="border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                    <td className="py-3 px-3 font-medium text-slate-800 dark:text-white max-w-[200px] truncate">{item.titulo}</td>
                    <td className="py-3 px-3 text-center text-slate-500 text-xs">{formatDate(item.data)}</td>
                    <td className="py-3 px-3 text-center">
                      <Badge variant="secondary" className="text-xs">{item.total_enviados}</Badge>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className="text-green-600 font-semibold">{item.total_lidas}</span>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className="text-red-500 font-semibold">{item.total_nao_lidas}</span>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-16 bg-slate-200 dark:bg-slate-700 rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${
                              item.taxa_leitura >= 70 ? 'bg-green-500' :
                              item.taxa_leitura >= 40 ? 'bg-amber-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${Math.min(item.taxa_leitura, 100)}%` }}
                          />
                        </div>
                        <span className={`text-xs font-semibold ${
                          item.taxa_leitura >= 70 ? 'text-green-600' :
                          item.taxa_leitura >= 40 ? 'text-amber-600' : 'text-red-500'
                        }`}>
                          {item.taxa_leitura}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <Badge variant="outline" className="text-xs capitalize">{item.filtro_tipo}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {timeline.length === 0 && (
            <p className="text-center text-slate-400 py-10">Nenhuma mensagem enviada ainda</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardEngajamento;
