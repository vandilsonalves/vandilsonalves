import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, Trophy, TrendingUp, MapPin, Activity, Target, Award, BarChart3 } from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  PieChart as RechartsPie, Pie, Cell, AreaChart, Area
} from 'recharts';

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

const DashboardGeral = ({ 
  stats, 
  statsEstados, 
  statsCategorias, 
  statsFaixa, 
  corridasPorMes,
  statsModalidade,
  statsPovao,
  statsEquipes,
  loadingStats 
}) => {
  if (loadingStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
        <span className="ml-4 text-slate-500">Carregando estatísticas...</span>
      </div>
    );
  }

  // Se não há dados, mostrar mensagem
  if (!stats) {
    return (
      <div className="text-center py-12 text-slate-500">
        <Activity className="w-12 h-12 mx-auto mb-4 opacity-30" />
        <p>Nenhum dado disponível</p>
      </div>
    );
  }

  // Preparar dados para gráficos
  const modalidadeData = [
    { name: 'Profissional/Amador', value: statsModalidade?.profissional || 0 },
    { name: 'Povão (Pace Livre)', value: statsModalidade?.povao || 0 }
  ];

  const categoriaData = statsCategorias ? [
    { name: 'Masculino', value: statsCategorias.masculino || 0, fill: '#3B82F6' },
    { name: 'Feminino', value: statsCategorias.feminino || 0, fill: '#EC4899' },
    { name: 'PCD M', value: statsCategorias.pcd_m || 0, fill: '#10B981' },
    { name: 'PCD F', value: statsCategorias.pcd_f || 0, fill: '#F59E0B' },
    { name: 'Cad. M', value: statsCategorias.cadeirante_m || 0, fill: '#8B5CF6' },
    { name: 'Cad. F', value: statsCategorias.cadeirante_f || 0, fill: '#06B6D4' }
  ] : [];

  return (
    <div className="space-y-6">
      {/* Cards de Estatísticas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Total de Atletas</p>
                <p className="text-3xl font-bold">{stats?.total_atletas || 0}</p>
              </div>
              <Users className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Total de Corridas</p>
                <p className="text-3xl font-bold">{stats?.total_corridas || 0}</p>
              </div>
              <Trophy className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-500 to-orange-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-amber-100 text-sm">Pendentes</p>
                <p className="text-3xl font-bold">{stats?.pendentes || 0}</p>
              </div>
              <Activity className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Selo "P" Ativos</p>
                <p className="text-3xl font-bold">{stats?.selo_p || 0}</p>
              </div>
              <Award className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos Principais */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribuição por Modalidade */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-green-500" />
              Distribuição por Modalidade
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie
                    data={modalidadeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {modalidadeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Distribuição por Categoria */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              Distribuição por Categoria
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoriaData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={80} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {categoriaData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Corridas por Mês */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-500" />
              Corridas por Mês
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={corridasPorMes || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mes" tick={{ fontSize: 11 }} />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="total" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Distribuição por Estado */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-purple-500" />
              Top Estados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={(statsEstados || []).slice(0, 8)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="estado" tick={{ fontSize: 11 }} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="total" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Ranking do Povão Stats */}
      {statsPovao && (
        <Card className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-purple-500" />
              Ranking do Povão - Estatísticas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-white dark:bg-slate-800 rounded-lg">
                <p className="text-2xl font-bold text-purple-600">{statsPovao.total_atletas || 0}</p>
                <p className="text-sm text-slate-500">Atletas Povão</p>
              </div>
              <div className="text-center p-4 bg-white dark:bg-slate-800 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{statsPovao.total_provas || 0}</p>
                <p className="text-sm text-slate-500">Provas Registradas</p>
              </div>
              <div className="text-center p-4 bg-white dark:bg-slate-800 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{statsPovao.total_pontos || 0}</p>
                <p className="text-sm text-slate-500">Pontos Totais</p>
              </div>
              <div className="text-center p-4 bg-white dark:bg-slate-800 rounded-lg">
                <p className="text-2xl font-bold text-amber-600">{statsPovao.media_pontos?.toFixed(1) || 0}</p>
                <p className="text-sm text-slate-500">Média por Atleta</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top 10 Equipes */}
      {statsEquipes && statsEquipes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-green-500" />
              Top 10 Equipes / Assessorias
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statsEquipes} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="equipe" type="category" width={120} tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="total" fill="#10B981" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Faixa Etária */}
      {statsFaixa && statsFaixa.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-500" />
              Distribuição por Faixa Etária
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
              {statsFaixa.map((faixa, idx) => (
                <div key={idx} className="text-center p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <p className="text-lg font-bold" style={{ color: COLORS[idx % COLORS.length] }}>
                    {faixa.total}
                  </p>
                  <p className="text-xs text-slate-500">{faixa.faixa}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DashboardGeral;
