// /app/frontend/src/pages/admin/DashboardEstrategico.jsx
// Dashboard Estratégico com 31 Gráficos para Super Admin

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ComposedChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import {
  Users, TrendingUp, Calendar, Award, MapPin, Activity,
  Target, Clock, Zap, BarChart2, PieChart as PieChartIcon,
  Map, Building, Trophy, UserCheck, Timer, Repeat, Heart
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Cores do tema
const COLORS = {
  primary: '#10B981',
  secondary: '#3B82F6',
  tertiary: '#8B5CF6',
  quaternary: '#F59E0B',
  danger: '#EF4444',
  success: '#22C55E',
  info: '#06B6D4',
  chart: ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#EC4899', '#06B6D4', '#84CC16']
};

// Componente de Card de Estatística
const StatCard = ({ title, value, icon: Icon, color = 'primary', subtitle }) => (
  <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-gray-600 transition-all">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-400 text-sm">{title}</p>
        <p className="text-2xl font-bold text-white mt-1">{value}</p>
        {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-3 rounded-lg bg-${color}-500/20`}>
        <Icon className={`w-6 h-6 text-${color}-500`} style={{ color: COLORS[color] || COLORS.primary }} />
      </div>
    </div>
  </div>
);

// Componente de Gráfico com Loading
const ChartCard = ({ title, children, loading, height = 300, icon: Icon }) => (
  <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
    <div className="flex items-center gap-2 mb-4">
      {Icon && <Icon className="w-5 h-5 text-emerald-500" />}
      <h3 className="text-lg font-semibold text-white">{title}</h3>
    </div>
    {loading ? (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
      </div>
    ) : (
      <div style={{ height }}>
        {children}
      </div>
    )}
  </div>
);

// Componente de Ranking
const RankingList = ({ data, valueKey, labelKey, icon: Icon }) => (
  <div className="space-y-2">
    {data.map((item, index) => (
      <div key={index} className="flex items-center justify-between p-2 bg-gray-700/50 rounded-lg">
        <div className="flex items-center gap-3">
          <span className={`w-6 h-6 flex items-center justify-center rounded-full text-sm font-bold ${
            index === 0 ? 'bg-yellow-500 text-black' :
            index === 1 ? 'bg-gray-400 text-black' :
            index === 2 ? 'bg-orange-600 text-white' :
            'bg-gray-600 text-white'
          }`}>
            {index + 1}
          </span>
          <span className="text-white text-sm">{item[labelKey]}</span>
        </div>
        <span className="text-emerald-400 font-semibold">{item[valueKey]}</span>
      </div>
    ))}
  </div>
);

// Mapa do Brasil simplificado (SVG inline)
const BrazilMap = ({ data }) => {
  const statePositions = {
    'AC': { x: 80, y: 180 }, 'AL': { x: 420, y: 200 }, 'AP': { x: 240, y: 60 },
    'AM': { x: 140, y: 120 }, 'BA': { x: 380, y: 220 }, 'CE': { x: 400, y: 150 },
    'DF': { x: 310, y: 240 }, 'ES': { x: 390, y: 280 }, 'GO': { x: 300, y: 260 },
    'MA': { x: 340, y: 130 }, 'MT': { x: 220, y: 230 }, 'MS': { x: 240, y: 310 },
    'MG': { x: 340, y: 280 }, 'PA': { x: 260, y: 120 }, 'PB': { x: 430, y: 170 },
    'PR': { x: 280, y: 360 }, 'PE': { x: 420, y: 180 }, 'PI': { x: 360, y: 170 },
    'RJ': { x: 370, y: 320 }, 'RN': { x: 420, y: 155 }, 'RS': { x: 270, y: 420 },
    'RO': { x: 150, y: 200 }, 'RR': { x: 160, y: 50 }, 'SC': { x: 290, y: 390 },
    'SP': { x: 310, y: 320 }, 'SE': { x: 410, y: 210 }, 'TO': { x: 300, y: 190 }
  };

  const maxCount = Math.max(...data.map(d => d.count), 1);

  return (
    <div className="relative w-full h-full">
      <svg viewBox="0 0 500 480" className="w-full h-full">
        {data.map((estado) => {
          const pos = statePositions[estado.estado];
          if (!pos) return null;
          const radius = Math.max(8, Math.min(25, (estado.count / maxCount) * 25 + 8));
          const opacity = Math.max(0.4, estado.count / maxCount);
          
          return (
            <g key={estado.estado}>
              <circle
                cx={pos.x}
                cy={pos.y}
                r={radius}
                fill={COLORS.primary}
                opacity={opacity}
                className="cursor-pointer hover:opacity-100 transition-opacity"
              />
              <text
                x={pos.x}
                y={pos.y + 4}
                textAnchor="middle"
                fill="white"
                fontSize="10"
                fontWeight="bold"
              >
                {estado.estado}
              </text>
              <text
                x={pos.x}
                y={pos.y + radius + 12}
                textAnchor="middle"
                fill="#9CA3AF"
                fontSize="9"
              >
                {estado.count}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

// Componente Principal
const DashboardEstrategico = () => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [visaoGeral, setVisaoGeral] = useState(null);
  const [graficos, setGraficos] = useState({});

  // Lista de gráficos a carregar
  const graficosEndpoints = [
    'crescimento-atletas', 'atletas-ativos', 'crescimento-eventos',
    'crescimento-donos-assessoria', 'crescimento-assessorias', 'resultados-registrados',
    'corridas-mes', 'distribuicao-estados', 'distribuicao-cidades',
    'distribuicao-faixa-etaria', 'distribuicao-sexo', 'distancias-mais-corridas',
    'media-corridas-atleta', 'eventos-populares', 'assessorias-mais-atletas',
    'assessorias-mais-pontos', 'atletas-mais-ativos', 'atletas-maior-pontuacao',
    'evolucao-pontuacao', 'tempo-medio-corridas', 'pace-medio-distancia',
    'participacao-media-evento', 'taxa-retorno-atletas', 'novos-vs-recorrentes',
    'engajamento-plataforma', 'atletas-por-assessoria', 'crescimento-regional',
    'provas-competitivas', 'evolucao-rankings', 'donos-assessoria-mapa',
    'distribuicao-etnia', 'distribuicao-tipo-corredor', 'distribuicao-terreno-preferido'
  ];

  // Carregar dados
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      // Carregar visão geral
      const visaoRes = await fetch(`${API_URL}/api/dashboard/visao-geral`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (visaoRes.ok) {
        setVisaoGeral(await visaoRes.json());
      }

      // Carregar gráficos em paralelo (em lotes de 5)
      const newGraficos = {};
      for (let i = 0; i < graficosEndpoints.length; i += 5) {
        const batch = graficosEndpoints.slice(i, i + 5);
        const results = await Promise.all(
          batch.map(async (endpoint) => {
            try {
              const res = await fetch(`${API_URL}/api/dashboard/grafico/${endpoint}`, {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              if (res.ok) {
                return { endpoint, data: await res.json() };
              }
            } catch (e) {
              console.error(`Erro ao carregar ${endpoint}:`, e);
            }
            return { endpoint, data: { dados: [] } };
          })
        );
        results.forEach(r => newGraficos[r.endpoint] = r.data);
      }
      setGraficos(newGraficos);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading && !visaoGeral) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-white">Carregando Dashboard Estratégico...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-[1800px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Dashboard Estratégico</h1>
            <p className="text-gray-400 mt-1">Visão completa da plataforma com 31 indicadores</p>
          </div>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            <Repeat className="w-4 h-4" />
            Atualizar
          </button>
        </div>

        {/* ====== VISÃO GERAL - 12 CARDS ====== */}
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <BarChart2 className="w-6 h-6 text-emerald-500" />
            Visão Geral da Plataforma
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <StatCard
              title="Total de Atletas"
              value={visaoGeral?.total_atletas || 0}
              icon={Users}
              color="primary"
            />
            <StatCard
              title="Total de Corridas"
              value={visaoGeral?.total_corridas || 0}
              icon={Activity}
              color="secondary"
            />
            <StatCard
              title="Total de Resultados"
              value={visaoGeral?.total_resultados || 0}
              icon={Award}
              color="tertiary"
            />
            <StatCard
              title="Total de Assessorias"
              value={visaoGeral?.total_assessorias || 0}
              icon={Building}
              color="quaternary"
            />
            <StatCard
              title="Região Top"
              value={visaoGeral?.regioes_top?.[0]?.estado || 'N/A'}
              icon={MapPin}
              subtitle={`${visaoGeral?.regioes_top?.[0]?.count || 0} atletas`}
            />
            <StatCard
              title="Novos Prof/Amador"
              value={visaoGeral?.novos_prof_amador || 0}
              icon={UserCheck}
              subtitle="Este mês"
              color="success"
            />
            <StatCard
              title="Novos Galera"
              value={visaoGeral?.novos_povao || 0}
              icon={Users}
              subtitle="Este mês"
              color="info"
            />
            <StatCard
              title="Novas Corridas"
              value={visaoGeral?.novas_corridas || 0}
              icon={Calendar}
              subtitle="Este mês"
            />
            <StatCard
              title="Novos Donos Assess."
              value={visaoGeral?.novos_donos_assessoria || 0}
              icon={Building}
              subtitle="Este mês"
            />
            <StatCard
              title="Distância Top"
              value={visaoGeral?.distancias_top?.[0]?.distancia || 'N/A'}
              icon={Target}
              subtitle={`${visaoGeral?.distancias_top?.[0]?.count || 0} corridas`}
            />
            <StatCard
              title="Tempo Médio P/A"
              value={visaoGeral?.tempo_medio_prof_amador || 'N/A'}
              icon={Timer}
              subtitle="Prof/Amador"
            />
            <StatCard
              title="Pace Médio Galera"
              value={visaoGeral?.pace_medio_povao || 'N/A'}
              icon={Clock}
              subtitle="Galera"
            />
          </div>
        </div>

        {/* ====== GRÁFICOS 1-4: CRESCIMENTO ====== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico 1: Crescimento de Atletas */}
          <ChartCard title="1. Crescimento de Atletas na Plataforma" loading={!graficos['crescimento-atletas']} icon={TrendingUp}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graficos['crescimento-atletas']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Legend />
                <Line type="monotone" dataKey="novos_atletas" name="Novos Atletas" stroke={COLORS.primary} strokeWidth={2} dot={{ fill: COLORS.primary }} />
                <Line type="monotone" dataKey="total_acumulado" name="Total Acumulado" stroke={COLORS.secondary} strokeWidth={2} dot={{ fill: COLORS.secondary }} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 2: Atletas Ativos */}
          <ChartCard title="2. Total de Atletas Ativos por Mês" loading={!graficos['atletas-ativos']} icon={Activity}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graficos['atletas-ativos']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="atletas_ativos" name="Atletas Ativos" stroke={COLORS.secondary} strokeWidth={2} dot={{ fill: COLORS.secondary }} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 3: Crescimento de Eventos */}
          <ChartCard title="3. Crescimento de Eventos de Corrida" loading={!graficos['crescimento-eventos']} icon={Calendar}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graficos['crescimento-eventos']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="eventos" name="Eventos" fill={COLORS.tertiary} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 4: Crescimento Donos de Assessoria */}
          <ChartCard title="4. Crescimento de Donos de Assessoria" loading={!graficos['crescimento-donos-assessoria']} icon={Building}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graficos['crescimento-donos-assessoria']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="novos_donos" name="Novos Donos" stroke={COLORS.quaternary} strokeWidth={2} dot={{ fill: COLORS.quaternary }} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ====== GRÁFICOS 5-7: ASSESSORIAS E RESULTADOS ====== */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Gráfico 5: Crescimento de Assessorias */}
          <ChartCard title="5. Crescimento de Assessorias Esportivas" loading={!graficos['crescimento-assessorias']} icon={Building}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graficos['crescimento-assessorias']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={10} />
                <YAxis stroke="#9CA3AF" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="novas_assessorias" name="Novas" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 6: Resultados Registrados */}
          <ChartCard title="6. Resultados Registrados na Plataforma" loading={!graficos['resultados-registrados']} icon={Award}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graficos['resultados-registrados']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={10} />
                <YAxis stroke="#9CA3AF" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="resultados" name="Resultados" stroke={COLORS.success} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 7: Corridas por Mês */}
          <ChartCard title="7. Corridas Registradas por Mês" loading={!graficos['corridas-mes']} icon={Activity}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graficos['corridas-mes']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={10} />
                <YAxis stroke="#9CA3AF" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="corridas" name="Corridas" fill={COLORS.secondary} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ====== GRÁFICOS 8-9: MAPAS E DISTRIBUIÇÃO GEOGRÁFICA ====== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico 8: Distribuição por Estado (Mapa) */}
          <ChartCard title="8. Distribuição de Atletas por Estado" loading={!graficos['distribuicao-estados']} height={400} icon={Map}>
            <BrazilMap data={graficos['distribuicao-estados']?.dados || []} />
          </ChartCard>

          {/* Gráfico 9: Top Cidades */}
          <ChartCard title="9. Distribuição de Atletas por Cidade (Top 15)" loading={!graficos['distribuicao-cidades']} height={400} icon={MapPin}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graficos['distribuicao-cidades']?.dados?.slice(0, 10) || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9CA3AF" fontSize={10} />
                <YAxis dataKey="cidade" type="category" stroke="#9CA3AF" fontSize={10} width={100} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="count" name="Atletas" fill={COLORS.info} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ====== GRÁFICOS 10-12: DISTRIBUIÇÕES (PIZZA) ====== */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Gráfico 10: Faixa Etária */}
          <ChartCard title="10. Distribuição por Faixa Etária" loading={!graficos['distribuicao-faixa-etaria']} icon={Users}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={graficos['distribuicao-faixa-etaria']?.dados || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="count"
                  nameKey="faixa"
                  label={({ faixa, percentual }) => `${faixa}: ${percentual}%`}
                  labelLine={false}
                >
                  {(graficos['distribuicao-faixa-etaria']?.dados || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.chart[index % COLORS.chart.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 11: Distribuição por Sexo */}
          <ChartCard title="11. Distribuição por Sexo" loading={!graficos['distribuicao-sexo']} icon={Users}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={graficos['distribuicao-sexo']?.dados || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="genero"
                  label={({ genero, percentual }) => `${genero}: ${percentual}%`}
                >
                  <Cell fill={COLORS.secondary} />
                  <Cell fill={COLORS.danger} />
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 31: Distribuição por Etnia */}
          <ChartCard title="31. Distribuição por Etnia" loading={!graficos['distribuicao-etnia']} icon={Heart}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={graficos['distribuicao-etnia']?.dados || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="count"
                  nameKey="etnia"
                  label={({ etnia, percentual }) => `${etnia}: ${percentual}%`}
                  labelLine={false}
                >
                  {(graficos['distribuicao-etnia']?.dados || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.chart[index % COLORS.chart.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ====== GRÁFICO 12: DISTÂNCIAS ====== */}
        <ChartCard title="12. Distâncias Mais Corridas" loading={!graficos['distancias-mais-corridas']} height={250} icon={Target}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={graficos['distancias-mais-corridas']?.dados || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="distancia" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
              <Bar dataKey="count" name="Corridas" fill={COLORS.quaternary} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* ====== GRÁFICOS 13-16: MÉTRICAS DE ENGAJAMENTO ====== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico 13: Média de Corridas por Atleta */}
          <ChartCard title="13. Número Médio de Corridas por Atleta" loading={!graficos['media-corridas-atleta']} icon={Activity}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graficos['media-corridas-atleta']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="media_corridas" name="Média" stroke={COLORS.info} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 14: Eventos Populares */}
          <ChartCard title="14. Eventos Mais Populares" loading={!graficos['eventos-populares']} icon={Trophy}>
            <RankingList 
              data={graficos['eventos-populares']?.dados || []}
              valueKey="participantes"
              labelKey="evento"
            />
          </ChartCard>

          {/* Gráfico 15: Assessorias com Mais Atletas */}
          <ChartCard title="15. Assessorias com Mais Atletas" loading={!graficos['assessorias-mais-atletas']} icon={Building}>
            <RankingList 
              data={graficos['assessorias-mais-atletas']?.dados || []}
              valueKey="atletas"
              labelKey="assessoria"
            />
          </ChartCard>

          {/* Gráfico 16: Assessorias com Mais Pontos */}
          <ChartCard title="16. Assessorias com Mais Pontos no Ranking" loading={!graficos['assessorias-mais-pontos']} icon={Award}>
            <RankingList 
              data={graficos['assessorias-mais-pontos']?.dados || []}
              valueKey="pontos"
              labelKey="assessoria"
            />
          </ChartCard>
        </div>

        {/* ====== GRÁFICOS 17-18: RANKINGS DE ATLETAS ====== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico 17: Atletas Mais Ativos */}
          <ChartCard title="17. Atletas Mais Ativos" loading={!graficos['atletas-mais-ativos']} icon={Zap}>
            <RankingList 
              data={graficos['atletas-mais-ativos']?.dados || []}
              valueKey="total_corridas"
              labelKey="atleta"
            />
          </ChartCard>

          {/* Gráfico 18: Atletas com Maior Pontuação */}
          <ChartCard title="18. Atletas com Maior Pontuação" loading={!graficos['atletas-maior-pontuacao']} icon={Trophy}>
            <RankingList 
              data={graficos['atletas-maior-pontuacao']?.dados || []}
              valueKey="pontos"
              labelKey="atleta"
            />
          </ChartCard>
        </div>

        {/* ====== GRÁFICOS 19-22: MÉTRICAS DE PERFORMANCE ====== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico 19: Evolução de Pontuação */}
          <ChartCard title="19. Evolução de Pontuação do Ranking" loading={!graficos['evolucao-pontuacao']} icon={TrendingUp}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graficos['evolucao-pontuacao']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="pontos_totais" name="Pontos Totais" stroke={COLORS.tertiary} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 20: Tempo Médio das Corridas */}
          <ChartCard title="20. Tempo Médio das Corridas" loading={!graficos['tempo-medio-corridas']} icon={Timer}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graficos['tempo-medio-corridas']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="tempo_medio_min" name="Tempo (min)" stroke={COLORS.quaternary} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 21: Pace Médio por Distância */}
          <ChartCard title="21. Pace Médio por Distância" loading={!graficos['pace-medio-distancia']} icon={Clock}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graficos['pace-medio-distancia']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="distancia" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                  formatter={(value, name, props) => [props.payload.pace_medio, 'Pace']}
                />
                <Bar dataKey="pace_segundos" name="Pace" fill={COLORS.info} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 22: Participação Média por Evento */}
          <ChartCard title="22. Participação Média por Evento" loading={!graficos['participacao-media-evento']} icon={Users}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graficos['participacao-media-evento']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="media_participantes" name="Média" fill={COLORS.success} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ====== GRÁFICOS 23-26: RETENÇÃO E ENGAJAMENTO ====== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico 23: Taxa de Retorno */}
          <ChartCard title="23. Taxa de Retorno de Atletas (%)" loading={!graficos['taxa-retorno-atletas']} icon={Repeat}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graficos['taxa-retorno-atletas']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="taxa_retorno" name="Taxa (%)" stroke={COLORS.success} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 24: Novos vs Recorrentes */}
          <ChartCard title="24. Atletas Novos vs Recorrentes" loading={!graficos['novos-vs-recorrentes']} icon={UserCheck}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={graficos['novos-vs-recorrentes']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="novos" name="Novos" fill={COLORS.primary} stackId="a" />
                <Bar dataKey="recorrentes" name="Recorrentes" fill={COLORS.secondary} stackId="a" />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 25: Engajamento na Plataforma */}
          <ChartCard title="25. Engajamento na Plataforma (30 dias)" loading={!graficos['engajamento-plataforma']} icon={Activity}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={graficos['engajamento-plataforma']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="dia" stroke="#9CA3AF" fontSize={10} />
                <YAxis stroke="#9CA3AF" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="atividades" name="Atividades" fill={COLORS.primary} />
                <Line type="monotone" dataKey="logins" name="Logins" stroke={COLORS.quaternary} strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 26: Atletas por Assessoria */}
          <ChartCard title="26. Atletas por Assessoria" loading={!graficos['atletas-por-assessoria']} icon={Building}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graficos['atletas-por-assessoria']?.dados?.slice(0, 10) || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9CA3AF" fontSize={10} />
                <YAxis dataKey="assessoria" type="category" stroke="#9CA3AF" fontSize={10} width={120} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="atletas" name="Atletas" fill={COLORS.tertiary} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ====== GRÁFICOS 27-30: REGIONAL E COMPETIÇÃO ====== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gráfico 27: Crescimento Regional */}
          <ChartCard title="27. Crescimento Regional" loading={!graficos['crescimento-regional']} height={350} icon={Map}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graficos['crescimento-regional']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="regiao" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="count" name="Atletas" fill={COLORS.primary} radius={[4, 4, 0, 0]}>
                  {(graficos['crescimento-regional']?.dados || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.chart[index % COLORS.chart.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 28: Provas Mais Competitivas */}
          <ChartCard title="28. Provas Mais Competitivas" loading={!graficos['provas-competitivas']} icon={Trophy}>
            <RankingList 
              data={graficos['provas-competitivas']?.dados || []}
              valueKey="atletas_unicos"
              labelKey="evento"
            />
          </ChartCard>

          {/* Gráfico 29: Evolução de Rankings */}
          <ChartCard title="29. Evolução de Rankings" loading={!graficos['evolucao-rankings']} icon={TrendingUp}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={graficos['evolucao-rankings']?.dados || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="movimentacoes" name="Movimentações" fill={COLORS.quaternary} />
                <Line type="monotone" dataKey="total_ranking" name="Total no Ranking" stroke={COLORS.primary} strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 30: Donos de Assessoria por Estado (Mapa) */}
          <ChartCard title="30. Donos de Assessoria por Estado" loading={!graficos['donos-assessoria-mapa']} height={350} icon={Map}>
            <BrazilMap data={graficos['donos-assessoria-mapa']?.dados || []} />
          </ChartCard>

          {/* Gráfico 31: Tipo de Corredor (Pizza) */}
          <ChartCard title="31. Tipo de Corredor" loading={!graficos['distribuicao-tipo-corredor']} icon={Target}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={graficos['distribuicao-tipo-corredor']?.dados || []}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="tipo"
                  label={({ tipo, percentual }) => `${tipo} (${percentual}%)`}
                >
                  {(graficos['distribuicao-tipo-corredor']?.dados || []).map((entry, index) => (
                    <Cell key={`cell-tc-${index}`} fill={COLORS.chart[index % COLORS.chart.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [value, 'Atletas']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Gráfico 32: Terreno Preferido (Pizza) */}
          <ChartCard title="32. Terreno Preferido" loading={!graficos['distribuicao-terreno-preferido']} icon={MapPin}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={graficos['distribuicao-terreno-preferido']?.dados || []}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="terreno"
                  label={({ terreno, percentual }) => `${terreno} (${percentual}%)`}
                >
                  {(graficos['distribuicao-terreno-preferido']?.dados || []).map((entry, index) => (
                    <Cell key={`cell-tp-${index}`} fill={COLORS.chart[index % COLORS.chart.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [value, 'Atletas']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm py-4">
          Dashboard Estratégico • Atualizado em {new Date().toLocaleString('pt-BR')}
        </div>
      </div>
    </div>
  );
};

export default DashboardEstrategico;
