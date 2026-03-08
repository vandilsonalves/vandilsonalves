import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Users, Trophy, TrendingUp, MapPin, Award, RefreshCw, Loader2, Eye, CheckCircle
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart as RechartsPie, Pie, Cell, LineChart, Line, Legend
} from 'recharts';

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

const DashboardAssessorias = ({ 
  ligaRanking, 
  ligaStats, 
  ligaTipo,
  setLigaTipo,
  ligaEstado,
  setLigaEstado,
  estadosComAssessorias,
  loadingLiga,
  onRefresh,
  onViewAssessoria,
  fetchCidades,
  cidadesComAssessorias,
  ligaCidade,
  setLigaCidade
}) => {
  const getSeloIcon = (selo) => {
    switch(selo) {
      case 'ouro': return '🥇';
      case 'prata': return '🥈';
      case 'bronze': return '🥉';
      default: return '🏅';
    }
  };

  const getSeloColor = (selo) => {
    switch(selo) {
      case 'ouro': return 'bg-gradient-to-r from-yellow-500 to-amber-600 text-white';
      case 'prata': return 'bg-gradient-to-r from-slate-400 to-slate-500 text-white';
      case 'bronze': return 'bg-gradient-to-r from-amber-700 to-orange-800 text-white';
      default: return 'bg-slate-600 text-white';
    }
  };

  // Preparar dados para gráficos
  const topEquipesData = (ligaRanking || []).slice(0, 10).map(eq => ({
    nome: eq.nome?.substring(0, 15) || 'N/A',
    pontos: eq.pontos_total || 0,
    atletas: eq.total_atletas || 0
  }));

  const selosDistribuicao = [
    { name: 'Ouro', value: ligaRanking.filter(e => e.selo === 'ouro').length, fill: '#F59E0B' },
    { name: 'Prata', value: ligaRanking.filter(e => e.selo === 'prata').length, fill: '#94A3B8' },
    { name: 'Bronze', value: ligaRanking.filter(e => e.selo === 'bronze').length, fill: '#B45309' }
  ];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      {ligaStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-amber-500 to-orange-600 text-white">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-100 text-sm">Total Assessorias</p>
                  <p className="text-3xl font-bold">{ligaStats.total_assessorias || 0}</p>
                </div>
                <Trophy className="w-10 h-10 opacity-80" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm">Atletas Vinculados</p>
                  <p className="text-3xl font-bold">{ligaStats.total_atletas_vinculados || 0}</p>
                </div>
                <Users className="w-10 h-10 opacity-80" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm">Resultados Aprovados</p>
                  <p className="text-3xl font-bold">{ligaStats.total_resultados_aprovados || 0}</p>
                </div>
                <CheckCircle className="w-10 h-10 opacity-80" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm">Estados Ativos</p>
                  <p className="text-3xl font-bold">{ligaStats.distribuicao_estados?.length || 0}</p>
                </div>
                <MapPin className="w-10 h-10 opacity-80" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Sistema de Pontuação */}
      <Card className="bg-amber-50 dark:bg-amber-900/20 border-amber-200">
        <CardContent className="pt-6">
          <p className="text-sm font-medium mb-3">Sistema de Pontuação ROE-RR:</p>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="bg-white dark:bg-slate-700">
              <Users className="w-3 h-3 mr-1" /> Atleta = +0,5
            </Badge>
            <Badge variant="outline" className="bg-white dark:bg-slate-700">
              <CheckCircle className="w-3 h-3 mr-1" /> Resultado = +1,0
            </Badge>
            <Badge variant="outline" className="bg-white dark:bg-slate-700">
              🥈 2º-5º = +0,5
            </Badge>
            <Badge variant="outline" className="bg-white dark:bg-slate-700">
              🥇 1º = +1,0
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Label className="text-sm font-medium">Tipo:</Label>
              <Select value={ligaTipo} onValueChange={(v) => {
                setLigaTipo(v);
                setLigaEstado('');
                setLigaCidade('');
              }}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="nacional">🌍 Nacional</SelectItem>
                  <SelectItem value="estadual">🗺️ Estadual</SelectItem>
                  <SelectItem value="cidade">🏙️ Por Cidade</SelectItem>
                  <SelectItem value="historico">📊 Histórico</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {ligaTipo === 'estadual' && (
              <div className="flex items-center gap-2">
                <Label className="text-sm">Estado:</Label>
                <Select value={ligaEstado} onValueChange={(v) => {
                  setLigaEstado(v);
                  if (fetchCidades) fetchCidades(v);
                }}>
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    {estadosComAssessorias.map(uf => (
                      <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {ligaTipo === 'cidade' && (
              <>
                <div className="flex items-center gap-2">
                  <Label className="text-sm">Estado:</Label>
                  <Select value={ligaEstado} onValueChange={(v) => {
                    setLigaEstado(v);
                    setLigaCidade('');
                    if (fetchCidades) fetchCidades(v);
                  }}>
                    <SelectTrigger className="w-28">
                      <SelectValue placeholder="UF" />
                    </SelectTrigger>
                    <SelectContent>
                      {estadosComAssessorias.map(uf => (
                        <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                {ligaEstado && (
                  <div className="flex items-center gap-2">
                    <Label className="text-sm">Cidade:</Label>
                    <Select value={ligaCidade} onValueChange={setLigaCidade}>
                      <SelectTrigger className="w-36">
                        <SelectValue placeholder="Selecione" />
                      </SelectTrigger>
                      <SelectContent>
                        {cidadesComAssessorias.map(c => (
                          <SelectItem key={c} value={c}>{c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </>
            )}

            <Button variant="outline" size="sm" onClick={onRefresh} disabled={loadingLiga}>
              <RefreshCw className={`w-4 h-4 mr-2 ${loadingLiga ? 'animate-spin' : ''}`} />
              Atualizar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 10 Equipes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-500" />
              Top 10 Assessorias por Pontos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topEquipesData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="nome" type="category" width={100} tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="pontos" fill="#F59E0B" radius={[0, 4, 4, 0]} name="Pontos" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Distribuição de Selos */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-500" />
              Distribuição de Selos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie
                    data={selosDistribuicao}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {selosDistribuicao.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabela de Ranking */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-500" />
            Ranking das Assessorias
            <Badge variant="secondary">{ligaRanking.length} assessorias</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingLiga ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
            </div>
          ) : ligaRanking.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Award className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>Nenhuma assessoria encontrada</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-amber-50 dark:bg-amber-900/20">
                    <th className="text-left py-3 px-4 font-semibold">Pos</th>
                    <th className="text-left py-3 px-4 font-semibold">Selo</th>
                    <th className="text-left py-3 px-4 font-semibold">Assessoria</th>
                    <th className="text-left py-3 px-4 font-semibold">UF</th>
                    <th className="text-center py-3 px-4 font-semibold">Atletas</th>
                    <th className="text-center py-3 px-4 font-semibold">1º Lugares</th>
                    <th className="text-center py-3 px-4 font-semibold">Resultados</th>
                    <th className="text-right py-3 px-4 font-semibold">Pontos</th>
                    <th className="text-center py-3 px-4 font-semibold">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {ligaRanking.map((eq, idx) => (
                    <tr key={eq.nome} className="border-b hover:bg-slate-50 dark:hover:bg-slate-800">
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${
                          idx < 3 ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'
                        }`}>
                          {eq.posicao || idx + 1}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <Badge className={getSeloColor(eq.selo)}>
                          {getSeloIcon(eq.selo)} {eq.selo?.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 font-medium">{eq.nome}</td>
                      <td className="py-3 px-4">{eq.estado}</td>
                      <td className="py-3 px-4 text-center">{eq.total_atletas}</td>
                      <td className="py-3 px-4 text-center">{eq.total_primeiros || 0}</td>
                      <td className="py-3 px-4 text-center">{eq.total_resultados}</td>
                      <td className="py-3 px-4 text-right font-bold text-amber-600">{eq.pontos_total}</td>
                      <td className="py-3 px-4 text-center">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => onViewAssessoria(eq.nome)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardAssessorias;
