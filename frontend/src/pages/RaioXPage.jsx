// /app/frontend/src/pages/RaioXPage.jsx
// Página RAIO-X do Atleta - Análise completa de performance

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ComposedChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, RadialBarChart, RadialBar
} from 'recharts';
import {
  Loader2, ChevronLeft, Download, TrendingUp, TrendingDown, Trophy,
  Target, Zap, Calendar, Clock, Activity, Award, Flame, Star,
  ArrowUpRight, ArrowDownRight, Minus, BarChart3, PieChart as PieIcon
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Cores para gráficos
const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
const GRADIENT_COLORS = {
  green: ['#10b981', '#059669'],
  blue: ['#3b82f6', '#2563eb'],
  orange: ['#f59e0b', '#d97706'],
  purple: ['#8b5cf6', '#7c3aed']
};

// Componente de KPI Widget
const KPIWidget = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = "emerald" }) => {
  const colorClasses = {
    emerald: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    blue: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    orange: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    purple: "bg-purple-500/10 text-purple-500 border-purple-500/20"
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-slate-400">{title}</p>
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
            {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
          </div>
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
        {trend !== undefined && (
          <div className="flex items-center gap-1 mt-2">
            {trend > 0 ? (
              <ArrowUpRight className="w-4 h-4 text-emerald-400" />
            ) : trend < 0 ? (
              <ArrowDownRight className="w-4 h-4 text-red-400" />
            ) : (
              <Minus className="w-4 h-4 text-slate-400" />
            )}
            <span className={`text-xs ${trend > 0 ? 'text-emerald-400' : trend < 0 ? 'text-red-400' : 'text-slate-400'}`}>
              {trend > 0 ? '+' : ''}{trendValue || trend}%
            </span>
            <span className="text-xs text-slate-500">vs mês anterior</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Componente de Record Card
const RecordCard = ({ title, value, subtitle, date, icon: Icon, highlight }) => (
  <div className={`p-4 rounded-lg border ${highlight ? 'bg-yellow-500/10 border-yellow-500/30' : 'bg-slate-700/50 border-slate-600'}`}>
    <div className="flex items-center gap-2 mb-2">
      <Icon className={`w-4 h-4 ${highlight ? 'text-yellow-400' : 'text-slate-400'}`} />
      <span className="text-sm text-slate-400">{title}</span>
    </div>
    <p className={`text-xl font-bold ${highlight ? 'text-yellow-400' : 'text-white'}`}>{value}</p>
    {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
    {date && <p className="text-xs text-slate-500 mt-1">{date}</p>}
  </div>
);

const RaioXPage = () => {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('visao-geral');

  useEffect(() => {
    if (token) {
      fetchRaioX();
    }
  }, [token]);

  const fetchRaioX = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/raio-x/completo`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setData(response.data);
    } catch (error) {
      console.error('Erro ao carregar RAIO-X:', error);
      toast.error('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = () => {
    toast.info('Gerando PDF... (funcionalidade em desenvolvimento)');
    // TODO: Implementar exportação PDF
  };

  const exportToExcel = () => {
    toast.info('Gerando Excel... (funcionalidade em desenvolvimento)');
    // TODO: Implementar exportação Excel
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-emerald-500 mx-auto" />
          <p className="text-slate-400 mt-4">Analisando seus dados...</p>
        </div>
      </div>
    );
  }

  if (!data || !data.evolucao?.tem_dados) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Card className="bg-slate-800 border-slate-700 max-w-md">
          <CardContent className="p-8 text-center">
            <Activity className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Sem dados suficientes</h2>
            <p className="text-slate-400 mb-4">
              Você precisa ter corridas registradas para ver seu RAIO-X.
              Comece registrando suas corridas!
            </p>
            <Button onClick={() => navigate('/submeter-resultado')} className="bg-emerald-500 hover:bg-emerald-600">
              Registrar Corrida
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { evolucao, records, comparativo, previsoes, score, heatmap, atleta } = data;

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/perfil')}
                className="text-white hover:bg-white/20"
              >
                <ChevronLeft className="w-6 h-6" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Zap className="w-7 h-7" />
                  RAIO-X do Atleta
                </h1>
                <p className="text-white/80">Análise completa de performance - {atleta?.nome}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={exportToPDF} className="border-white/30 text-white hover:bg-white/20">
                <Download className="w-4 h-4 mr-2" />
                PDF
              </Button>
              <Button variant="outline" size="sm" onClick={exportToExcel} className="border-white/30 text-white hover:bg-white/20">
                <Download className="w-4 h-4 mr-2" />
                Excel
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Score de Consistência - Destaque */}
      <div className="container mx-auto px-4 -mt-4">
        <Card className="bg-gradient-to-r from-slate-800 to-slate-700 border-slate-600">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="relative w-32 h-32">
                <ResponsiveContainer>
                  <RadialBarChart
                    innerRadius="70%"
                    outerRadius="100%"
                    data={[{ value: score.score_mes_atual, fill: '#10b981' }]}
                    startAngle={90}
                    endAngle={-270}
                  >
                    <RadialBar dataKey="value" cornerRadius={10} background={{ fill: '#334155' }} />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-white">{score.score_mes_atual}%</span>
                  <span className="text-xs text-slate-400">Consistência</span>
                </div>
              </div>
              <div className="flex-1 text-center md:text-left">
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span className="text-2xl">{score.emoji}</span>
                  <h3 className="text-xl font-bold text-white">{score.classificacao}</h3>
                </div>
                <p className="text-slate-400 mt-1">{score.dica}</p>
                <div className="flex items-center gap-4 mt-3 justify-center md:justify-start">
                  <div className="text-center">
                    <p className="text-lg font-bold text-emerald-400">{score.corridas_mes_atual}</p>
                    <p className="text-xs text-slate-500">Corridas este mês</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-blue-400">{score.media_6_meses}%</p>
                    <p className="text-xs text-slate-500">Média 6 meses</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-orange-400">{evolucao.totais?.total_provas || 0}</p>
                    <p className="text-xs text-slate-500">Total de provas</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Conteúdo Principal */}
      <div className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-slate-800 border-slate-700 mb-6">
            <TabsTrigger value="visao-geral">Visão Geral</TabsTrigger>
            <TabsTrigger value="evolucao">Evolução</TabsTrigger>
            <TabsTrigger value="records">Records (RP)</TabsTrigger>
            <TabsTrigger value="comparativo">Comparativo</TabsTrigger>
            <TabsTrigger value="previsoes">Previsões IA</TabsTrigger>
          </TabsList>

          {/* Aba: Visão Geral */}
          <TabsContent value="visao-geral">
            {/* KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <KPIWidget
                title="Distância Total"
                value={`${evolucao.totais?.distancia_total_km || 0} km`}
                icon={TrendingUp}
                trend={comparativo.variacoes?.distancia}
                color="emerald"
              />
              <KPIWidget
                title="Tempo Total"
                value={`${evolucao.totais?.tempo_total_horas || 0}h`}
                icon={Clock}
                color="blue"
              />
              <KPIWidget
                title="Total de Provas"
                value={evolucao.totais?.total_provas || 0}
                icon={Trophy}
                trend={comparativo.variacoes?.provas}
                color="orange"
              />
              <KPIWidget
                title="Melhor Pace"
                value={records.records?.melhor_pace?.valor_formatado || '-'}
                subtitle="/km"
                icon={Zap}
                color="purple"
              />
            </div>

            {/* Gráfico de Evolução + Heatmap */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              {/* Gráfico de Área - Evolução de Distância */}
              <Card className="bg-slate-800 border-slate-700 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-emerald-400" />
                    Evolução de Distância
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={evolucao.evolucao_mensal}>
                      <defs>
                        <linearGradient id="colorDist" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                        labelStyle={{ color: '#fff' }}
                      />
                      <Area
                        type="monotone"
                        dataKey="distancia_total_km"
                        stroke="#10b981"
                        fillOpacity={1}
                        fill="url(#colorDist)"
                        name="Distância (km)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Heatmap - Dias da Semana */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-blue-400" />
                    Dias Favoritos
                  </CardTitle>
                  <CardDescription className="text-slate-400">
                    Dia favorito: <span className="text-blue-400 font-medium">{heatmap.dia_favorito}</span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(heatmap.dias_semana).map(([dia, count]) => {
                      const max = Math.max(...Object.values(heatmap.dias_semana));
                      const percent = max > 0 ? (count / max) * 100 : 0;
                      return (
                        <div key={dia} className="flex items-center gap-2">
                          <span className="text-sm text-slate-400 w-8">{dia}</span>
                          <div className="flex-1 bg-slate-700 rounded-full h-4 overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all"
                              style={{ width: `${percent}%` }}
                            />
                          </div>
                          <span className="text-sm text-white w-6 text-right">{count}</span>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Records por Categoria + Radar */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Records por Categoria */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-yellow-400" />
                    Records Pessoais (RP)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {['5km', '10km', '21km', '42km'].map((cat) => {
                      const rp = records.records?.por_categoria?.[cat];
                      return (
                        <RecordCard
                          key={cat}
                          title={cat}
                          value={rp?.tempo || '-'}
                          subtitle={rp ? `Pace: ${rp.pace}` : 'Sem registro'}
                          date={rp?.data ? new Date(rp.data).toLocaleDateString('pt-BR') : null}
                          icon={Trophy}
                          highlight={!!rp}
                        />
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Gráfico Radar - Performance */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <PieIcon className="w-5 h-5 text-purple-400" />
                    Perfil de Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <RadarChart
                      data={[
                        { subject: 'Consistência', value: score.score_mes_atual, fullMark: 100 },
                        { subject: 'Volume', value: Math.min((evolucao.totais?.total_provas || 0) * 10, 100), fullMark: 100 },
                        { subject: 'Velocidade', value: records.records?.melhor_pace ? Math.max(100 - (records.records.melhor_pace.valor * 10), 20) : 30, fullMark: 100 },
                        { subject: 'Distância', value: Math.min((evolucao.totais?.distancia_total_km || 0) / 5, 100), fullMark: 100 },
                        { subject: 'Regularidade', value: score.media_6_meses, fullMark: 100 }
                      ]}
                    >
                      <PolarGrid stroke="#334155" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar
                        name="Performance"
                        dataKey="value"
                        stroke="#8b5cf6"
                        fill="#8b5cf6"
                        fillOpacity={0.3}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Aba: Evolução */}
          <TabsContent value="evolucao">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Gráfico de Linha - Evolução do Pace */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Evolução do Pace Médio</CardTitle>
                  <CardDescription className="text-slate-400">Menor pace = melhor performance</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={evolucao.evolucao_mensal.filter(e => e.pace_medio_valor)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} domain={['auto', 'auto']} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                        formatter={(value) => [`${value.toFixed(2)} min/km`, 'Pace']}
                      />
                      <Line
                        type="monotone"
                        dataKey="pace_medio_valor"
                        stroke="#f59e0b"
                        strokeWidth={3}
                        dot={{ fill: '#f59e0b', strokeWidth: 2 }}
                        name="Pace médio"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Gráfico de Barras - Número de Provas */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Provas por Mês</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={evolucao.evolucao_mensal}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                      <Bar dataKey="num_provas" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Provas" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Gráfico Composto - Distância x Tempo */}
              <Card className="bg-slate-800 border-slate-700 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white">Distância vs Tempo Total</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <ComposedChart data={evolucao.evolucao_mensal}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis yAxisId="left" stroke="#10b981" fontSize={12} />
                      <YAxis yAxisId="right" orientation="right" stroke="#8b5cf6" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                      <Legend />
                      <Bar yAxisId="left" dataKey="distancia_total_km" fill="#10b981" name="Distância (km)" radius={[4, 4, 0, 0]} />
                      <Line yAxisId="right" type="monotone" dataKey="tempo_total_horas" stroke="#8b5cf6" strokeWidth={2} name="Tempo (h)" />
                    </ComposedChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Aba: Records */}
          <TabsContent value="records">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Melhor Pace */}
              <Card className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border-yellow-500/30">
                <CardContent className="p-6 text-center">
                  <Trophy className="w-12 h-12 text-yellow-400 mx-auto mb-3" />
                  <h3 className="text-lg text-slate-300">Melhor Pace</h3>
                  <p className="text-4xl font-bold text-yellow-400 my-2">
                    {records.records?.melhor_pace?.valor_formatado || '-'}
                  </p>
                  <p className="text-slate-400">/km</p>
                  {records.records?.melhor_pace && (
                    <>
                      <p className="text-sm text-slate-400 mt-2">{records.records.melhor_pace.corrida}</p>
                      <p className="text-xs text-slate-500">{records.records.melhor_pace.distancia} km</p>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Maior Distância */}
              <Card className="bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border-emerald-500/30">
                <CardContent className="p-6 text-center">
                  <TrendingUp className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                  <h3 className="text-lg text-slate-300">Maior Distância</h3>
                  <p className="text-4xl font-bold text-emerald-400 my-2">
                    {records.records?.maior_distancia?.valor || '-'}
                  </p>
                  <p className="text-slate-400">km</p>
                  {records.records?.maior_distancia && (
                    <p className="text-sm text-slate-400 mt-2">{records.records.maior_distancia.corrida}</p>
                  )}
                </CardContent>
              </Card>

              {/* Score de Consistência */}
              <Card className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-purple-500/30">
                <CardContent className="p-6 text-center">
                  <Flame className="w-12 h-12 text-purple-400 mx-auto mb-3" />
                  <h3 className="text-lg text-slate-300">Consistência</h3>
                  <p className="text-4xl font-bold text-purple-400 my-2">{score.media_6_meses}%</p>
                  <p className="text-slate-400">Média 6 meses</p>
                  <Badge className="mt-2 bg-purple-500/30 text-purple-300">{score.classificacao}</Badge>
                </CardContent>
              </Card>
            </div>

            {/* Tabela de Records por Categoria */}
            <Card className="bg-slate-800 border-slate-700 mt-6">
              <CardHeader>
                <CardTitle className="text-white">Records por Distância</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="py-3 px-4 text-left text-slate-400">Distância</th>
                        <th className="py-3 px-4 text-center text-slate-400">Melhor Tempo</th>
                        <th className="py-3 px-4 text-center text-slate-400">Pace</th>
                        <th className="py-3 px-4 text-left text-slate-400">Corrida</th>
                        <th className="py-3 px-4 text-center text-slate-400">Data</th>
                      </tr>
                    </thead>
                    <tbody>
                      {['5km', '10km', '21km', '42km'].map((cat) => {
                        const rp = records.records?.por_categoria?.[cat];
                        return (
                          <tr key={cat} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                            <td className="py-3 px-4">
                              <span className="font-medium text-white">{cat}</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              {rp ? (
                                <span className="text-emerald-400 font-bold">{rp.tempo}</span>
                              ) : (
                                <span className="text-slate-500">-</span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-center text-slate-300">{rp?.pace || '-'}</td>
                            <td className="py-3 px-4 text-slate-300">{rp?.corrida || '-'}</td>
                            <td className="py-3 px-4 text-center text-slate-400">
                              {rp?.data ? new Date(rp.data).toLocaleDateString('pt-BR') : '-'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Aba: Comparativo */}
          <TabsContent value="comparativo">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Comparativo Este Mês vs Mês Anterior */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Este Mês vs Mês Anterior</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Distância */}
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-slate-400">Distância Total</span>
                        <div className="flex items-center gap-2">
                          {comparativo.variacoes?.distancia > 0 ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                          ) : comparativo.variacoes?.distancia < 0 ? (
                            <ArrowDownRight className="w-4 h-4 text-red-400" />
                          ) : null}
                          <span className={comparativo.variacoes?.distancia > 0 ? 'text-emerald-400' : comparativo.variacoes?.distancia < 0 ? 'text-red-400' : 'text-slate-400'}>
                            {comparativo.variacoes?.distancia > 0 ? '+' : ''}{comparativo.variacoes?.distancia || 0}%
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-white">{comparativo.mes_atual?.metricas?.distancia_total_km || 0}</p>
                          <p className="text-xs text-slate-400">km este mês</p>
                        </div>
                        <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-slate-400">{comparativo.mes_anterior?.metricas?.distancia_total_km || 0}</p>
                          <p className="text-xs text-slate-500">km mês passado</p>
                        </div>
                      </div>
                    </div>

                    {/* Provas */}
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-slate-400">Número de Provas</span>
                        <div className="flex items-center gap-2">
                          {comparativo.variacoes?.provas > 0 ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                          ) : comparativo.variacoes?.provas < 0 ? (
                            <ArrowDownRight className="w-4 h-4 text-red-400" />
                          ) : null}
                          <span className={comparativo.variacoes?.provas > 0 ? 'text-emerald-400' : comparativo.variacoes?.provas < 0 ? 'text-red-400' : 'text-slate-400'}>
                            {comparativo.variacoes?.provas > 0 ? '+' : ''}{comparativo.variacoes?.provas || 0}%
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-white">{comparativo.mes_atual?.metricas?.num_provas || 0}</p>
                          <p className="text-xs text-slate-400">este mês</p>
                        </div>
                        <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-slate-400">{comparativo.mes_anterior?.metricas?.num_provas || 0}</p>
                          <p className="text-xs text-slate-500">mês passado</p>
                        </div>
                      </div>
                    </div>

                    {/* Pace */}
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-slate-400">Pace Médio</span>
                        <div className="flex items-center gap-2">
                          {comparativo.variacoes?.pace > 0 ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                          ) : comparativo.variacoes?.pace < 0 ? (
                            <ArrowDownRight className="w-4 h-4 text-red-400" />
                          ) : null}
                          <span className={comparativo.variacoes?.pace > 0 ? 'text-emerald-400' : comparativo.variacoes?.pace < 0 ? 'text-red-400' : 'text-slate-400'}>
                            {comparativo.variacoes?.pace > 0 ? '+' : ''}{comparativo.variacoes?.pace || 0}%
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-white">{comparativo.mes_atual?.metricas?.pace_medio || '-'}</p>
                          <p className="text-xs text-slate-400">/km este mês</p>
                        </div>
                        <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-slate-400">{comparativo.mes_anterior?.metricas?.pace_medio || '-'}</p>
                          <p className="text-xs text-slate-500">/km mês passado</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Melhor Performance do Mês */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Star className="w-5 h-5 text-yellow-400" />
                    Melhor Performance do Mês
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {comparativo.melhor_performance_mes ? (
                    <div className="text-center py-4">
                      <Award className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
                      <h3 className="text-xl font-bold text-white">{comparativo.melhor_performance_mes.corrida}</h3>
                      <p className="text-slate-400 mt-2">{new Date(comparativo.melhor_performance_mes.data).toLocaleDateString('pt-BR')}</p>
                      <div className="flex justify-center gap-6 mt-4">
                        <div>
                          <p className="text-2xl font-bold text-emerald-400">{comparativo.melhor_performance_mes.distancia} km</p>
                          <p className="text-xs text-slate-500">Distância</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-blue-400">{comparativo.melhor_performance_mes.tempo}</p>
                          <p className="text-xs text-slate-500">Tempo</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-orange-400">{comparativo.melhor_performance_mes.pace}</p>
                          <p className="text-xs text-slate-500">Pace</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Activity className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                      <p className="text-slate-400">Nenhuma corrida registrada este mês</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Gráfico de Comparação Histórica */}
              <Card className="bg-slate-800 border-slate-700 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white">Histórico de Consistência</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={score.historico}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                      <Bar dataKey="score" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Score (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Aba: Previsões IA */}
          <TabsContent value="previsoes">
            <Card className="bg-slate-800 border-slate-700 mb-6">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  Previsões Inteligentes
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Baseado nas suas últimas {previsoes.corridas_analisadas || 0} corridas
                </CardDescription>
              </CardHeader>
              <CardContent>
                {previsoes.tem_dados ? (
                  <>
                    <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
                      <p className="text-slate-400">Seu pace base atual:</p>
                      <p className="text-3xl font-bold text-emerald-400">{previsoes.pace_base} /km</p>
                      <p className="text-sm text-slate-500 mt-1">{previsoes.dica}</p>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(previsoes.previsoes || {}).map(([dist, prev]) => (
                        <Card key={dist} className="bg-slate-700 border-slate-600">
                          <CardContent className="p-4 text-center">
                            <p className="text-lg font-bold text-white">{prev.distancia}</p>
                            <p className="text-2xl font-bold text-blue-400 my-2">{prev.tempo_previsto}</p>
                            <p className="text-sm text-slate-400">Pace: {prev.pace_previsto}</p>
                            <Badge className="mt-2" variant={prev.confianca === 'Alta' ? 'default' : 'secondary'}>
                              {prev.confianca}
                            </Badge>
                          </CardContent>
                        </Card>
                      ))}
                    </div>

                    <div className="mt-6 p-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg border border-purple-500/30">
                      <div className="flex items-center gap-3">
                        <Target className="w-8 h-8 text-purple-400" />
                        <div>
                          <p className="text-white font-medium">Probabilidade de bater RP na próxima corrida</p>
                          <p className="text-2xl font-bold text-purple-400">{previsoes.probabilidade_rp_proxima}</p>
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <Activity className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400">{previsoes.mensagem}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default RaioXPage;
