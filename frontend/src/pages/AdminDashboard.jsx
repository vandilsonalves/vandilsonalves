import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { 
  CheckCircle, XCircle, ExternalLink, Calendar, MapPin, Trophy, Clock, 
  ArrowLeft, Users, AlertCircle, TrendingUp, BarChart3, PieChart,
  UserCheck, UserX, Activity
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPie, Pie, Cell } from 'recharts';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, token, isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  
  // Stats
  const [stats, setStats] = useState(null);
  const [statsEstados, setStatsEstados] = useState([]);
  const [statsCategorias, setStatsCategorias] = useState(null);
  const [statsFaixa, setStatsFaixa] = useState([]);
  const [loadingStats, setLoadingStats] = useState(true);
  
  // Pendentes
  const [pendentes, setPendentes] = useState([]);
  const [loadingPendentes, setLoadingPendentes] = useState(true);
  
  // Modal
  const [showReprovarModal, setShowReprovarModal] = useState(false);
  const [selectedResultado, setSelectedResultado] = useState(null);
  const [motivoReprovacao, setMotivoReprovacao] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (!isAdmin) {
      navigate('/');
      return;
    }
    fetchAllData();
  }, [isAdmin]);

  const fetchAllData = async () => {
    await Promise.all([
      fetchStats(),
      fetchPendentes()
    ]);
  };

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      const [statsRes, estadosRes, categoriasRes, faixaRes] = await Promise.all([
        axios.get(`${API}/admin/stats`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/estados`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/categorias`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/faixa-etaria`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      setStats(statsRes.data);
      setStatsEstados(estadosRes.data);
      setStatsCategorias(categoriasRes.data);
      setStatsFaixa(faixaRes.data);
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
    } finally {
      setLoadingStats(false);
    }
  };

  const fetchPendentes = async () => {
    setLoadingPendentes(true);
    try {
      const response = await axios.get(`${API}/admin/pendentes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendentes(response.data);
    } catch (error) {
      console.error('Erro ao buscar pendentes:', error);
    } finally {
      setLoadingPendentes(false);
    }
  };

  const handleAprovar = async (resultadoId) => {
    if (!window.confirm('Confirma a aprovação deste resultado?')) return;

    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/aprovar/${resultadoId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Resultado aprovado com sucesso!');
      fetchPendentes();
      fetchStats();
    } catch (error) {
      alert(error.response?.data?.detail || 'Erro ao aprovar');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReprovar = async () => {
    setActionLoading(true);
    try {
      await axios.post(
        `${API}/admin/reprovar/${selectedResultado.id}`,
        { motivo: motivoReprovacao },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      alert('Resultado reprovado');
      setShowReprovarModal(false);
      setMotivoReprovacao('');
      setSelectedResultado(null);
      fetchPendentes();
    } catch (error) {
      alert(error.response?.data?.detail || 'Erro ao reprovar');
    } finally {
      setActionLoading(false);
    }
  };

  // Preparar dados para gráficos
  const prepareCategoriasData = () => {
    if (!statsCategorias) return [];
    return [
      { name: 'Normal M', value: statsCategorias.normal_m || 0, color: '#10B981' },
      { name: 'Normal F', value: statsCategorias.normal_f || 0, color: '#3B82F6' },
      { name: 'PCD M', value: statsCategorias.pcd_m || 0, color: '#F59E0B' },
      { name: 'PCD F', value: statsCategorias.pcd_f || 0, color: '#EF4444' },
      { name: 'Cadeirante M', value: statsCategorias.cadeirante_m || 0, color: '#8B5CF6' },
      { name: 'Cadeirante F', value: statsCategorias.cadeirante_f || 0, color: '#EC4899' }
    ];
  };

  const prepareGeneroData = () => {
    if (!stats) return [];
    return [
      { name: 'Masculino', value: stats.total_homens || 0, color: '#3B82F6' },
      { name: 'Feminino', value: stats.total_mulheres || 0, color: '#EC4899' }
    ];
  };

  if (!isAdmin) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-6 px-4">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1" data-testid="admin-title">
              Painel Administrativo
            </h1>
            <p className="text-slate-400">Gerenciamento do Ranking Run Pró</p>
          </div>
          <Button onClick={() => navigate('/')} variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar ao Ranking
          </Button>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 lg:grid-cols-3 mb-6 bg-slate-800/50">
            <TabsTrigger value="overview" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white" data-testid="tab-overview">
              <BarChart3 className="w-4 h-4 mr-2" />
              Visão Geral
            </TabsTrigger>
            <TabsTrigger value="pendentes" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white" data-testid="tab-pendentes">
              <AlertCircle className="w-4 h-4 mr-2" />
              Pendentes ({pendentes.length})
            </TabsTrigger>
            <TabsTrigger value="graficos" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white" data-testid="tab-graficos">
              <PieChart className="w-4 h-4 mr-2" />
              Gráficos
            </TabsTrigger>
          </TabsList>

          {/* Tab: Visão Geral */}
          <TabsContent value="overview">
            {loadingStats ? (
              <div className="text-center py-12 text-slate-400">Carregando estatísticas...</div>
            ) : (
              <div className="space-y-6">
                {/* Cards de Estatísticas */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Card className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border-emerald-500/30">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-emerald-300 font-medium">Total de Atletas</p>
                          <p className="text-3xl font-bold text-white mt-1" data-testid="stat-total-atletas">{stats?.total_atletas || 0}</p>
                        </div>
                        <div className="h-12 w-12 rounded-full bg-emerald-500/20 flex items-center justify-center">
                          <Users className="h-6 w-6 text-emerald-400" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-amber-500/20 to-amber-600/10 border-amber-500/30">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-amber-300 font-medium">Resultados Pendentes</p>
                          <p className="text-3xl font-bold text-white mt-1" data-testid="stat-pendentes">{stats?.resultados_pendentes || 0}</p>
                        </div>
                        <div className="h-12 w-12 rounded-full bg-amber-500/20 flex items-center justify-center">
                          <AlertCircle className="h-6 w-6 text-amber-400" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 border-blue-500/30">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-blue-300 font-medium">Atletas Masculinos</p>
                          <p className="text-3xl font-bold text-white mt-1" data-testid="stat-homens">{stats?.total_homens || 0}</p>
                        </div>
                        <div className="h-12 w-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                          <UserCheck className="h-6 w-6 text-blue-400" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-pink-500/20 to-pink-600/10 border-pink-500/30">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-pink-300 font-medium">Atletas Femininas</p>
                          <p className="text-3xl font-bold text-white mt-1" data-testid="stat-mulheres">{stats?.total_mulheres || 0}</p>
                        </div>
                        <div className="h-12 w-12 rounded-full bg-pink-500/20 flex items-center justify-center">
                          <UserX className="h-6 w-6 text-pink-400" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Gráficos lado a lado */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Atletas por Estado */}
                  <Card className="bg-slate-800/50 border-slate-700">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-emerald-400" />
                        Atletas por Estado
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={statsEstados.slice(0, 10)} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis type="number" stroke="#9CA3AF" />
                            <YAxis dataKey="estado" type="category" stroke="#9CA3AF" width={40} />
                            <Tooltip 
                              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                              labelStyle={{ color: '#F3F4F6' }}
                            />
                            <Bar dataKey="total" fill="#10B981" radius={[0, 4, 4, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Distribuição por Gênero */}
                  <Card className="bg-slate-800/50 border-slate-700">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <PieChart className="w-5 h-5 text-emerald-400" />
                        Distribuição por Gênero
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <RechartsPie>
                            <Pie
                              data={prepareGeneroData()}
                              cx="50%"
                              cy="50%"
                              labelLine={false}
                              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                              outerRadius={100}
                              fill="#8884d8"
                              dataKey="value"
                            >
                              {prepareGeneroData().map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                              ))}
                            </Pie>
                            <Tooltip 
                              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                            />
                          </RechartsPie>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Atletas com selo P */}
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-4">
                      <div className="h-14 w-14 rounded-full bg-orange-500/20 flex items-center justify-center">
                        <Activity className="h-7 w-7 text-orange-400" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-400 font-medium">Atletas com Selo "P" (Pendente de Corridas)</p>
                        <p className="text-2xl font-bold text-white">{stats?.atletas_pendentes_corridas || 0}</p>
                        <p className="text-xs text-slate-500 mt-1">Atletas que ainda não completaram o mínimo de corridas para a premiação</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* Tab: Pendentes */}
          <TabsContent value="pendentes">
            {loadingPendentes ? (
              <div className="text-center py-12 text-slate-400">Carregando...</div>
            ) : pendentes.length === 0 ? (
              <Alert className="bg-emerald-500/10 border-emerald-500/30">
                <CheckCircle className="h-4 w-4 text-emerald-400" />
                <AlertDescription className="text-emerald-300 ml-2">
                  Não há resultados pendentes de aprovação.
                </AlertDescription>
              </Alert>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {pendentes.map((resultado) => (
                  <Card key={resultado.id} className="bg-slate-800/50 border-slate-700 hover:border-slate-600 transition-colors" data-testid={`resultado-${resultado.id}`}>
                    <CardHeader className="bg-slate-800/80 rounded-t-lg">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg text-white">
                            {resultado.nome_competicao}
                          </CardTitle>
                          <p className="text-sm text-slate-400 mt-1">
                            <strong className="text-slate-300">Atleta:</strong> {resultado.atleta_nome} ({resultado.atleta_equipe})
                          </p>
                          <Badge variant="outline" className="mt-2 border-slate-600 text-slate-300">
                            {resultado.atleta_categoria?.toUpperCase()}
                          </Badge>
                        </div>
                        <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30">
                          Pendente
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-3">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center gap-2 text-slate-300">
                          <Trophy className="w-4 h-4 text-amber-500" />
                          <span><strong>Colocação:</strong> {resultado.colocacao}º</span>
                        </div>
                        <div className="flex items-center gap-2 text-slate-300">
                          <Clock className="w-4 h-4 text-blue-400" />
                          <span><strong>Tempo:</strong> {resultado.tempo}</span>
                        </div>
                        <div className="flex items-center gap-2 text-slate-300">
                          <MapPin className="w-4 h-4 text-emerald-400" />
                          <span>{resultado.cidade_competicao}/{resultado.estado_competicao}</span>
                        </div>
                        <div className="flex items-center gap-2 text-slate-300">
                          <Calendar className="w-4 h-4 text-slate-400" />
                          <span>{new Date(resultado.data_competicao).toLocaleDateString('pt-BR')}</span>
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-700">
                        <p className="text-sm text-slate-300"><strong>Distância:</strong> {resultado.distancia}</p>
                        <p className="text-sm mt-1 text-slate-300">
                          <strong>Link:</strong>{' '}
                          <a
                            href={resultado.link_resultado}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1"
                          >
                            Ver resultado <ExternalLink className="w-3 h-3" />
                          </a>
                        </p>
                        {resultado.foto_podio_url && (
                          <div className="mt-3">
                            <p className="text-sm font-semibold mb-2 text-slate-300">Foto do Pódio:</p>
                            <img
                              src={`${BACKEND_URL}${resultado.foto_podio_url}`}
                              alt="Pódio"
                              className="w-full h-40 object-cover rounded-lg border border-slate-600"
                            />
                          </div>
                        )}
                      </div>

                      <div className="flex gap-2 pt-4">
                        <Button
                          onClick={() => handleAprovar(resultado.id)}
                          disabled={actionLoading}
                          className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                          data-testid={`btn-aprovar-${resultado.id}`}
                        >
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Aprovar
                        </Button>
                        <Button
                          onClick={() => {
                            setSelectedResultado(resultado);
                            setShowReprovarModal(true);
                          }}
                          disabled={actionLoading}
                          variant="destructive"
                          className="flex-1"
                          data-testid={`btn-reprovar-${resultado.id}`}
                        >
                          <XCircle className="w-4 h-4 mr-2" />
                          Reprovar
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Tab: Gráficos */}
          <TabsContent value="graficos">
            {loadingStats ? (
              <div className="text-center py-12 text-slate-400">Carregando gráficos...</div>
            ) : (
              <div className="space-y-6">
                {/* Distribuição por Categoria */}
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-emerald-400" />
                      Distribuição por Categoria e Gênero
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[400px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={prepareCategoriasData()}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                          <XAxis dataKey="name" stroke="#9CA3AF" />
                          <YAxis stroke="#9CA3AF" />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                            labelStyle={{ color: '#F3F4F6' }}
                          />
                          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                            {prepareCategoriasData().map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                {/* Distribuição por Faixa Etária */}
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-emerald-400" />
                      Distribuição por Faixa Etária
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={statsFaixa}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                          <XAxis dataKey="faixa" stroke="#9CA3AF" />
                          <YAxis stroke="#9CA3AF" />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                            labelStyle={{ color: '#F3F4F6' }}
                          />
                          <Bar dataKey="total" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Modal de Reprovação */}
        <Dialog open={showReprovarModal} onOpenChange={setShowReprovarModal}>
          <DialogContent className="bg-slate-800 border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">Reprovar Resultado</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <p className="text-sm text-slate-400">
                Informe o motivo da reprovação (será enviado ao atleta):
              </p>
              <Textarea
                value={motivoReprovacao}
                onChange={(e) => setMotivoReprovacao(e.target.value)}
                placeholder="Ex: Resultado não encontrado no link fornecido, foto ilegível, etc."
                rows={4}
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setShowReprovarModal(false);
                  setMotivoReprovacao('');
                }}
                className="border-slate-600 text-slate-300"
              >
                Cancelar
              </Button>
              <Button
                variant="destructive"
                onClick={handleReprovar}
                disabled={actionLoading}
              >
                Reprovar
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default AdminDashboard;
