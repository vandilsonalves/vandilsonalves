import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, TrendingUp, TrendingDown, Users, Trophy, Target, Medal, MapPin, BarChart3, PieChart as PieChartIcon } from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Treemap
} from 'recharts';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mapa do Brasil - GeoJSON simplificado dos estados
const BRAZIL_GEO_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson";

// Cores para os gráficos
const COLORS = ['#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#EF4444', '#06B6D4', '#84CC16'];

const RelatoriosAssessoria = ({ equipe, token }) => {
  const [loading, setLoading] = useState(true);
  const [dados, setDados] = useState(null);

  useEffect(() => {
    fetchRelatorios();
  }, [equipe]);

  const fetchRelatorios = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/dono-assessoria/relatorios/${encodeURIComponent(equipe)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDados(response.data);
    } catch (error) {
      console.error('Erro ao buscar relatórios:', error);
      toast.error('Erro ao carregar relatórios');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
      </div>
    );
  }

  if (!dados) {
    return (
      <div className="text-center text-slate-400 py-8">
        Nenhum dado disponível para relatórios
      </div>
    );
  }

  const { indicadores, grafico_genero, grafico_categoria, grafico_faixa_etaria, 
          mapa_estados, evolucao_mensal, radar_performance, ranking_atletas, 
          sunburst_colocacoes, evolucao_cadastros } = dados;

  // Custom tooltip para os gráficos
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 shadow-lg">
          <p className="text-white font-medium">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color || '#F59E0B' }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Cor para o mapa baseada na quantidade de atletas
  const getMapColor = (estado) => {
    const item = mapa_estados?.find(m => m.estado === estado);
    if (!item) return '#1F2937';
    const count = item.atletas;
    if (count >= 10) return '#F59E0B';
    if (count >= 5) return '#FBBF24';
    if (count >= 2) return '#FCD34D';
    if (count >= 1) return '#FDE68A';
    return '#1F2937';
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white flex items-center gap-2">
        <BarChart3 className="w-6 h-6 text-amber-500" />
        Relatórios e Análises
      </h2>

      {/* Indicadores Principais */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-amber-600 to-amber-700">
          <CardContent className="p-4 text-white text-center">
            <p className="text-3xl font-bold">{indicadores.total_atletas}</p>
            <p className="text-xs opacity-80">Atletas Ativos</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-emerald-600 to-emerald-700">
          <CardContent className="p-4 text-white text-center">
            <p className="text-3xl font-bold">{indicadores.total_resultados}</p>
            <p className="text-xs opacity-80">Total Resultados</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-blue-600 to-blue-700">
          <CardContent className="p-4 text-white text-center">
            <p className="text-3xl font-bold">{indicadores.total_pontos}</p>
            <p className="text-xs opacity-80">Pontos Totais</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600">
          <CardContent className="p-4 text-white text-center">
            <p className="text-3xl font-bold">{indicadores.total_primeiros}</p>
            <p className="text-xs opacity-80">1º Lugares</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-600 to-purple-700">
          <CardContent className="p-4 text-white text-center">
            <p className="text-3xl font-bold">{indicadores.total_podios}</p>
            <p className="text-xs opacity-80">Pódios</p>
          </CardContent>
        </Card>
      </div>

      {/* Indicadores Percentuais */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-xs">Média Pontos/Atleta</p>
                <p className="text-2xl font-bold text-amber-500">{indicadores.media_pontos_atleta}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center">
                <Target className="w-6 h-6 text-amber-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-xs">Média Corridas/Atleta</p>
                <p className="text-2xl font-bold text-emerald-500">{indicadores.media_corridas_atleta}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-emerald-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-xs">Taxa de Pódio</p>
                <p className="text-2xl font-bold text-blue-500">{indicadores.taxa_podio}%</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                <Medal className="w-6 h-6 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-xs">Taxa de Vitória</p>
                <p className="text-2xl font-bold text-yellow-500">{indicadores.taxa_vitoria}%</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-yellow-500/20 flex items-center justify-center">
                <Trophy className="w-6 h-6 text-yellow-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos - Linha 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Linha - Evolução Mensal */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-amber-500" />
              Evolução Mensal (Resultados e Pontos)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={evolucao_mensal}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="left" stroke="#9CA3AF" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="right" orientation="right" stroke="#9CA3AF" tick={{ fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="resultados" stroke="#F59E0B" strokeWidth={2} dot={{ fill: '#F59E0B' }} name="Resultados" />
                <Line yAxisId="right" type="monotone" dataKey="pontos" stroke="#10B981" strokeWidth={2} dot={{ fill: '#10B981' }} name="Pontos" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de Barras - Faixa Etária */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-500" />
              Distribuição por Faixa Etária
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={grafico_faixa_etaria} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9CA3AF" tick={{ fontSize: 11 }} />
                <YAxis dataKey="faixa" type="category" stroke="#9CA3AF" tick={{ fontSize: 10 }} width={60} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="atletas" fill="#3B82F6" radius={[0, 4, 4, 0]} name="Atletas" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos - Linha 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gráfico de Pizza - Gênero */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <PieChartIcon className="w-4 h-4 text-pink-500" />
              Distribuição por Gênero
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={grafico_genero}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {grafico_genero.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de Pizza - Categoria */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <PieChartIcon className="w-4 h-4 text-purple-500" />
              Distribuição por Categoria
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={grafico_categoria}
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                  labelLine={false}
                >
                  {grafico_categoria.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico Radar - Performance */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <Target className="w-4 h-4 text-amber-500" />
              Radar de Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={radar_performance}>
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis dataKey="metrica" stroke="#9CA3AF" tick={{ fontSize: 9 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#9CA3AF" tick={{ fontSize: 9 }} />
                <Radar name="Performance" dataKey="valor" stroke="#F59E0B" fill="#F59E0B" fillOpacity={0.5} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos - Linha 3 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mapa do Brasil */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-500" />
              Distribuição Geográfica dos Atletas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative">
              <ComposableMap
                projection="geoMercator"
                projectionConfig={{
                  scale: 600,
                  center: [-55, -15]
                }}
                style={{ width: '100%', height: '300px' }}
              >
                <Geographies geography={BRAZIL_GEO_URL}>
                  {({ geographies }) =>
                    geographies.map((geo) => {
                      const sigla = geo.properties.sigla || geo.properties.UF_05;
                      return (
                        <Geography
                          key={geo.rsmKey}
                          geography={geo}
                          fill={getMapColor(sigla)}
                          stroke="#1F2937"
                          strokeWidth={0.5}
                          style={{
                            default: { outline: 'none' },
                            hover: { fill: '#F59E0B', outline: 'none', cursor: 'pointer' },
                            pressed: { outline: 'none' }
                          }}
                        />
                      );
                    })
                  }
                </Geographies>
              </ComposableMap>
              {/* Legenda */}
              <div className="absolute bottom-2 right-2 bg-slate-900/90 p-2 rounded-lg text-xs">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-3 h-3 bg-amber-500 rounded"></div>
                  <span className="text-slate-300">10+ atletas</span>
                </div>
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-3 h-3 bg-amber-400 rounded"></div>
                  <span className="text-slate-300">5-9 atletas</span>
                </div>
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-3 h-3 bg-amber-300 rounded"></div>
                  <span className="text-slate-300">2-4 atletas</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-amber-200 rounded"></div>
                  <span className="text-slate-300">1 atleta</span>
                </div>
              </div>
            </div>
            {/* Lista de estados com atletas */}
            <div className="mt-4 flex flex-wrap gap-2">
              {mapa_estados?.filter(e => e.atletas > 0).map((item) => (
                <Badge key={item.estado} variant="outline" className="text-amber-400 border-amber-500/50">
                  {item.estado}: {item.atletas}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Ranking Interno de Atletas */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <Trophy className="w-4 h-4 text-yellow-500" />
              Top 10 Atletas da Equipe
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-[300px] overflow-y-auto">
              {ranking_atletas?.map((atleta, index) => (
                <div 
                  key={atleta.pos}
                  className={`flex items-center justify-between p-2 rounded-lg ${
                    index === 0 ? 'bg-gradient-to-r from-yellow-500/20 to-transparent border border-yellow-500/30' :
                    index === 1 ? 'bg-gradient-to-r from-slate-400/20 to-transparent border border-slate-400/30' :
                    index === 2 ? 'bg-gradient-to-r from-amber-700/20 to-transparent border border-amber-700/30' :
                    'bg-slate-900/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      index === 0 ? 'bg-yellow-500 text-white' :
                      index === 1 ? 'bg-slate-400 text-white' :
                      index === 2 ? 'bg-amber-700 text-white' :
                      'bg-slate-700 text-slate-300'
                    }`}>
                      {atleta.pos}º
                    </span>
                    <div>
                      <p className="text-white font-medium text-sm">{atleta.nome}</p>
                      <p className="text-slate-400 text-xs">{atleta.corridas} corridas</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-amber-500 font-bold">{atleta.pontos}</p>
                    <p className="text-slate-500 text-xs">pontos</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos - Linha 4 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico Treemap - Distribuição de Colocações (Sunburst alternativo) */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <Medal className="w-4 h-4 text-amber-500" />
              Distribuição de Colocações
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sunburst_colocacoes?.[0]?.children && (
              <ResponsiveContainer width="100%" height={250}>
                <Treemap
                  data={sunburst_colocacoes[0].children}
                  dataKey="size"
                  aspectRatio={4/3}
                  stroke="#1F2937"
                  fill="#F59E0B"
                >
                  {sunburst_colocacoes[0].children.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                  <Tooltip 
                    content={({ payload }) => {
                      if (payload && payload.length) {
                        return (
                          <div className="bg-slate-800 p-2 rounded border border-slate-700">
                            <p className="text-white font-medium">{payload[0].payload.name}</p>
                            <p className="text-amber-500">{payload[0].payload.size} resultados</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </Treemap>
              </ResponsiveContainer>
            )}
            {/* Legenda manual */}
            <div className="flex flex-wrap gap-2 mt-4 justify-center">
              {sunburst_colocacoes?.[0]?.children?.map((item, index) => (
                <div key={item.name} className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                  <span className="text-slate-400 text-xs">{item.name}: {item.size}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Gráfico de Área - Evolução de Cadastros */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <Users className="w-4 h-4 text-emerald-500" />
              Evolução de Novos Atletas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={evolucao_cadastros}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
                <YAxis stroke="#9CA3AF" tick={{ fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Area 
                  type="monotone" 
                  dataKey="novos" 
                  stroke="#10B981" 
                  fill="#10B981" 
                  fillOpacity={0.3} 
                  name="Novos Atletas"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RelatoriosAssessoria;
