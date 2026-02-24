import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { 
  CheckCircle, XCircle, ExternalLink, Calendar, MapPin, Trophy, Clock, 
  Users, AlertCircle, TrendingUp, BarChart3, PieChart,
  Activity, Home, Settings, FileText, Bell, ChevronRight, Award, Database
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPie, Pie, Cell, LineChart, Line, AreaChart, Area } from 'recharts';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

// Menu items para sidebar
const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Home },
  { id: 'pendentes', label: 'Aprovações', icon: AlertCircle },
  { id: 'graficos', label: 'Gráficos', icon: BarChart3 },
  { id: 'ranking', label: 'Rankings', icon: Trophy },
];

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, token, isAdmin } = useAuth();
  const [activeMenu, setActiveMenu] = useState('dashboard');
  
  // Stats
  const [stats, setStats] = useState(null);
  const [statsEstados, setStatsEstados] = useState([]);
  const [statsCategorias, setStatsCategorias] = useState(null);
  const [statsFaixa, setStatsFaixa] = useState([]);
  const [corridasPorMes, setCorridasPorMes] = useState([]);
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
      const [statsRes, estadosRes, categoriasRes, faixaRes, corridasRes] = await Promise.all([
        axios.get(`${API}/admin/stats`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/estados`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/categorias`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/faixa-etaria`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/corridas-por-mes`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      setStats(statsRes.data);
      setStatsEstados(estadosRes.data);
      setStatsCategorias(categoriasRes.data);
      setStatsFaixa(faixaRes.data);
      setCorridasPorMes(corridasRes.data);
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
    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/aprovar/${resultadoId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
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
    <div className="min-h-screen flex bg-slate-100 dark:bg-slate-950">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-slate-800 to-slate-900 text-white fixed h-full shadow-xl">
        {/* Logo */}
        <div className="p-6 border-b border-slate-700/50">
          <h1 className="text-xl font-bold text-emerald-400">Ranking Run Pró</h1>
          <p className="text-xs text-slate-400 mt-1">Painel Administrativo</p>
        </div>

        {/* Menu */}
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveMenu(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  activeMenu === item.id 
                    ? 'bg-emerald-500/20 text-emerald-400 border-l-4 border-emerald-400' 
                    : 'text-slate-400 hover:bg-slate-700/50 hover:text-white'
                }`}
                data-testid={`menu-${item.id}`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
                {item.id === 'pendentes' && pendentes.length > 0 && (
                  <Badge className="ml-auto bg-red-500 text-white text-xs">
                    {pendentes.length}
                  </Badge>
                )}
                {activeMenu === item.id && (
                  <ChevronRight className="w-4 h-4 ml-auto" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer da Sidebar */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700/50">
          <Button 
            onClick={() => navigate('/')} 
            variant="ghost" 
            className="w-full justify-start text-slate-400 hover:text-white"
          >
            <Home className="w-4 h-4 mr-2" />
            Voltar ao Site
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64 flex-1 p-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white">
            {menuItems.find(m => m.id === activeMenu)?.label || 'Dashboard'}
          </h2>
          <p className="text-slate-500">
            Bem-vindo, {user?.nome}
          </p>
        </div>

        {/* Dashboard View */}
        {activeMenu === 'dashboard' && (
          <div className="space-y-6">
            {/* Cards de Estatísticas - Estilo KPI */}
            {loadingStats ? (
              <div className="text-center py-12">Carregando...</div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {/* Total Atletas */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 overflow-hidden">
                    <div className="h-1 bg-gradient-to-r from-emerald-400 to-emerald-600" />
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-4xl font-bold text-slate-800 dark:text-white">{stats?.total_atletas || 0}</p>
                          <p className="text-sm text-slate-500 mt-1">Atletas Ativos</p>
                        </div>
                        <div className="h-14 w-14 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                          <Users className="h-7 w-7 text-emerald-600" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Pendentes */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 overflow-hidden">
                    <div className="h-1 bg-gradient-to-r from-amber-400 to-amber-600" />
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-4xl font-bold text-slate-800 dark:text-white">{stats?.resultados_pendentes || 0}</p>
                          <p className="text-sm text-slate-500 mt-1">Aguardando Aprovação</p>
                        </div>
                        <div className="h-14 w-14 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                          <AlertCircle className="h-7 w-7 text-amber-600" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Total Corridas */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 overflow-hidden">
                    <div className="h-1 bg-gradient-to-r from-blue-400 to-blue-600" />
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-4xl font-bold text-slate-800 dark:text-white">{stats?.total_corridas || 0}</p>
                          <p className="text-sm text-slate-500 mt-1">Corridas Registradas</p>
                        </div>
                        <div className="h-14 w-14 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                          <Trophy className="h-7 w-7 text-blue-600" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Selo P */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 overflow-hidden">
                    <div className="h-1 bg-gradient-to-r from-purple-400 to-purple-600" />
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-4xl font-bold text-slate-800 dark:text-white">{stats?.atletas_pendentes_corridas || 0}</p>
                          <p className="text-sm text-slate-500 mt-1">Atletas com Selo "P"</p>
                        </div>
                        <div className="h-14 w-14 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                          <Activity className="h-7 w-7 text-purple-600" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Gráficos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Corridas por Mês */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                    <CardHeader>
                      <CardTitle className="text-lg font-semibold flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-emerald-500" />
                        Corridas por Mês
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={corridasPorMes}>
                            <defs>
                              <linearGradient id="colorCorridas" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                                <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                            <XAxis dataKey="mes" stroke="#9CA3AF" fontSize={12} tickFormatter={(v) => v.split('-')[1]} />
                            <YAxis stroke="#9CA3AF" fontSize={12} />
                            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                            <Area type="monotone" dataKey="total" stroke="#10B981" strokeWidth={2} fill="url(#colorCorridas)" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Distribuição por Gênero */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                    <CardHeader>
                      <CardTitle className="text-lg font-semibold flex items-center gap-2">
                        <PieChart className="w-5 h-5 text-emerald-500" />
                        Distribuição por Gênero
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[280px] flex items-center justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                          <RechartsPie>
                            <Pie
                              data={prepareGeneroData()}
                              cx="50%"
                              cy="50%"
                              innerRadius={60}
                              outerRadius={100}
                              paddingAngle={5}
                              dataKey="value"
                            >
                              {prepareGeneroData().map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                              ))}
                            </Pie>
                            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                            <Legend />
                          </RechartsPie>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Atletas por Estado */}
                <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                  <CardHeader>
                    <CardTitle className="text-lg font-semibold flex items-center gap-2">
                      <Database className="w-5 h-5 text-emerald-500" />
                      Atletas por Estado (Top 10)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={statsEstados.slice(0, 10)} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                          <XAxis type="number" stroke="#9CA3AF" />
                          <YAxis dataKey="estado" type="category" stroke="#9CA3AF" width={40} />
                          <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                          <Bar dataKey="total" radius={[0, 4, 4, 0]}>
                            {statsEstados.slice(0, 10).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        )}

        {/* Pendentes View */}
        {activeMenu === 'pendentes' && (
          <div>
            {loadingPendentes ? (
              <div className="text-center py-12">Carregando...</div>
            ) : pendentes.length === 0 ? (
              <Alert className="bg-emerald-50 border-emerald-200">
                <CheckCircle className="h-4 w-4 text-emerald-600" />
                <AlertDescription className="text-emerald-700 ml-2">
                  Não há resultados pendentes de aprovação.
                </AlertDescription>
              </Alert>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {pendentes.map((resultado) => (
                  <Card key={resultado.id} className="bg-white dark:bg-slate-800 shadow-lg border-0" data-testid={`resultado-${resultado.id}`}>
                    <CardHeader className="bg-slate-50 dark:bg-slate-800/80 rounded-t-lg border-b">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">
                            {resultado.nome_competicao}
                          </CardTitle>
                          <p className="text-sm text-slate-500 mt-1">
                            <strong>Atleta:</strong> {resultado.atleta_nome}
                          </p>
                          <Badge variant="outline" className="mt-2">
                            {resultado.atleta_categoria?.toUpperCase()}
                          </Badge>
                        </div>
                        <Badge className="bg-amber-100 text-amber-700 border-0">
                          Pendente
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-3">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <Trophy className="w-4 h-4 text-amber-500" />
                          <span><strong>Colocação:</strong> {resultado.colocacao}º</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-blue-500" />
                          <span><strong>Tempo:</strong> {resultado.tempo}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-emerald-500" />
                          <span>{resultado.cidade_competicao}/{resultado.estado_competicao}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-slate-400" />
                          <span>{new Date(resultado.data_competicao).toLocaleDateString('pt-BR')}</span>
                        </div>
                      </div>

                      <div className="pt-3 border-t">
                        <p className="text-sm"><strong>Distância:</strong> {resultado.distancia}</p>
                        <p className="text-sm mt-1">
                          <strong>Link:</strong>{' '}
                          <a
                            href={resultado.link_resultado}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-emerald-600 hover:underline inline-flex items-center gap-1"
                          >
                            Ver resultado <ExternalLink className="w-3 h-3" />
                          </a>
                        </p>
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
          </div>
        )}

        {/* Gráficos View */}
        {activeMenu === 'graficos' && (
          <div className="space-y-6">
            {loadingStats ? (
              <div className="text-center py-12">Carregando...</div>
            ) : (
              <>
                {/* Distribuição por Categoria */}
                <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                  <CardHeader>
                    <CardTitle className="text-lg font-semibold flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-emerald-500" />
                      Distribuição por Categoria e Gênero
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[400px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={prepareCategoriasData()}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                          <XAxis dataKey="name" stroke="#9CA3AF" />
                          <YAxis stroke="#9CA3AF" />
                          <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
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
                <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                  <CardHeader>
                    <CardTitle className="text-lg font-semibold flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-emerald-500" />
                      Distribuição por Faixa Etária
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[350px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={statsFaixa}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                          <XAxis dataKey="faixa" stroke="#9CA3AF" />
                          <YAxis stroke="#9CA3AF" />
                          <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                          <Bar dataKey="total" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        )}

        {/* Ranking View - Redireciona para página principal */}
        {activeMenu === 'ranking' && (
          <div className="text-center py-12">
            <Trophy className="h-16 w-16 text-emerald-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Gerenciar Rankings</h3>
            <p className="text-slate-500 mb-4">Acesse a página principal para visualizar e gerenciar os rankings.</p>
            <Button onClick={() => navigate('/')} className="bg-emerald-600">
              Ir para Rankings
            </Button>
          </div>
        )}

        {/* Modal de Reprovação */}
        <Dialog open={showReprovarModal} onOpenChange={setShowReprovarModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Reprovar Resultado</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <p className="text-sm text-slate-600">
                O atleta receberá uma notificação com o motivo da reprovação e poderá submeter novamente.
              </p>
              <Textarea
                value={motivoReprovacao}
                onChange={(e) => setMotivoReprovacao(e.target.value)}
                placeholder="Ex: Resultado não encontrado no link fornecido, foto ilegível, etc."
                rows={4}
              />
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setShowReprovarModal(false);
                  setMotivoReprovacao('');
                }}
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
