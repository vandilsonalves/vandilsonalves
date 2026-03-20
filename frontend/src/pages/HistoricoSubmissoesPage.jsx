import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ArrowLeft, Clock, CheckCircle, XCircle, AlertCircle, 
  Trophy, Calendar, MapPin, Timer, Upload, Eye, 
  ChevronLeft, ChevronRight, Filter, TrendingUp
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HistoricoSubmissoesPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [submissoes, setSubmissoes] = useState([]);
  const [estatisticas, setEstatisticas] = useState(null);
  const [resumo, setResumo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubmissao, setSelectedSubmissao] = useState(null);
  const [showModal, setShowModal] = useState(false);
  
  // Filtros
  const [statusFilter, setStatusFilter] = useState('all');
  const [periodoFilter, setPeriodoFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [paginacao, setPaginacao] = useState(null);

  useEffect(() => {
    if (token) {
      fetchHistorico();
      fetchResumo();
    }
  }, [token, statusFilter, periodoFilter, page]);

  const fetchHistorico = async () => {
    try {
      let url = `${API}/historico/submissoes?page=${page}&limit=10`;
      if (statusFilter !== 'all') url += `&status=${statusFilter}`;
      if (periodoFilter !== 'all') url += `&periodo=${periodoFilter}`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSubmissoes(response.data.submissoes);
      setEstatisticas(response.data.estatisticas);
      setPaginacao(response.data.paginacao);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchResumo = async () => {
    try {
      const response = await axios.get(`${API}/historico/resumo`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResumo(response.data);
    } catch (error) {
      console.error('Erro ao carregar resumo:', error);
    }
  };

  const getStatusConfig = (status) => {
    switch (status) {
      case 'aprovado':
        return { icon: CheckCircle, color: 'text-emerald-500', bg: 'bg-emerald-100', label: 'Aprovado' };
      case 'reprovado':
        return { icon: XCircle, color: 'text-red-500', bg: 'bg-red-100', label: 'Reprovado' };
      default:
        return { icon: Clock, color: 'text-amber-500', bg: 'bg-amber-100', label: 'Pendente' };
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR');
    } catch {
      return dateStr;
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="p-6 text-center">
          <p className="text-slate-600 mb-4">Faça login para ver seu histórico</p>
          <Button onClick={() => navigate('/login')}>Entrar</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-8 px-4" data-testid="historico-page">
      <div className="container mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-6">
          <Button variant="outline" onClick={() => navigate(-1)} className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </Button>
          
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                <Upload className="w-6 h-6 text-emerald-500" />
                Histórico de Submissões
              </h1>
              <p className="text-slate-600 text-sm mt-1">
                Acompanhe o status de todas as suas submissões de resultados
              </p>
            </div>
            <Button onClick={() => navigate('/submeter-resultado')} className="bg-emerald-600 hover:bg-emerald-700" data-testid="btn-nova-submissao">
              <Upload className="w-4 h-4 mr-2" />
              Nova Submissão
            </Button>
          </div>
        </div>

        {/* Resumo Cards */}
        {resumo && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Card className="bg-gradient-to-br from-slate-800 to-slate-900 text-white">
              <CardContent className="pt-4 text-center">
                <Trophy className="w-8 h-8 mx-auto mb-2 text-amber-400" />
                <p className="text-2xl font-bold">{resumo.corridas.total}</p>
                <p className="text-xs text-slate-400">Corridas Aprovadas</p>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
              <CardContent className="pt-4 text-center">
                <TrendingUp className="w-8 h-8 mx-auto mb-2" />
                <p className="text-2xl font-bold">{resumo.corridas.pontos_totais}</p>
                <p className="text-xs text-emerald-100">Pontos Totais</p>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white">
              <CardContent className="pt-4 text-center">
                <Clock className="w-8 h-8 mx-auto mb-2" />
                <p className="text-2xl font-bold">{resumo.submissoes.pendentes}</p>
                <p className="text-xs text-amber-100">Pendentes</p>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
              <CardContent className="pt-4 text-center">
                <CheckCircle className="w-8 h-8 mx-auto mb-2" />
                <p className="text-2xl font-bold">{resumo.submissoes.taxa_aprovacao}%</p>
                <p className="text-xs text-purple-100">Taxa Aprovação</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filtros */}
        <Card className="mb-6">
          <CardContent className="pt-4">
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-slate-500" />
                <span className="text-sm text-slate-600">Filtros:</span>
              </div>
              
              <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="pendente">Pendentes</SelectItem>
                  <SelectItem value="aprovado">Aprovados</SelectItem>
                  <SelectItem value="reprovado">Reprovados</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={periodoFilter} onValueChange={(v) => { setPeriodoFilter(v); setPage(1); }}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Período" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todo período</SelectItem>
                  <SelectItem value="7d">Últimos 7 dias</SelectItem>
                  <SelectItem value="30d">Últimos 30 dias</SelectItem>
                  <SelectItem value="90d">Últimos 90 dias</SelectItem>
                </SelectContent>
              </Select>
              
              {estatisticas && (
                <div className="ml-auto flex gap-2">
                  <Badge variant="outline" className="bg-emerald-50">
                    {estatisticas.aprovados} aprovados
                  </Badge>
                  <Badge variant="outline" className="bg-amber-50">
                    {estatisticas.pendentes} pendentes
                  </Badge>
                  <Badge variant="outline" className="bg-red-50">
                    {estatisticas.reprovados} reprovados
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Lista de Submissões */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Suas Submissões</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
              </div>
            ) : submissoes.length === 0 ? (
              <div className="text-center py-12">
                <Upload className="w-12 h-12 mx-auto text-slate-300 mb-4" />
                <p className="text-slate-500">Nenhuma submissão encontrada</p>
                <Button onClick={() => navigate('/submeter-resultado')} className="mt-4" data-testid="btn-submeter-primeiro">
                  Submeter Primeiro Resultado
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {submissoes.map((sub) => {
                  const statusConfig = getStatusConfig(sub.status);
                  const StatusIcon = statusConfig.icon;
                  
                  return (
                    <div 
                      key={sub.id}
                      className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-4 rounded-lg border hover:bg-slate-50 transition-colors cursor-pointer"
                      onClick={() => { setSelectedSubmissao(sub); setShowModal(true); }}
                    >
                      {/* Status Badge */}
                      <div className={`p-2 rounded-full ${statusConfig.bg}`}>
                        <StatusIcon className={`w-5 h-5 ${statusConfig.color}`} />
                      </div>
                      
                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="font-semibold text-slate-800 truncate">
                            {sub.nome_competicao}
                          </h3>
                          <Badge className={statusConfig.bg + ' ' + statusConfig.color.replace('text-', 'text-')}>
                            {statusConfig.label}
                          </Badge>
                        </div>
                        <div className="flex flex-wrap gap-3 mt-1 text-sm text-slate-500">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {formatDate(sub.data_competicao)}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {sub.distancia}
                          </span>
                          {sub.colocacao && (
                            <span className="flex items-center gap-1">
                              <Trophy className="w-3 h-3" />
                              {sub.colocacao}º lugar
                            </span>
                          )}
                          {sub.tempo && sub.tempo !== 'N/A' && (
                            <span className="flex items-center gap-1">
                              <Timer className="w-3 h-3" />
                              {sub.tempo}
                            </span>
                          )}
                        </div>
                        
                        {/* Motivo de rejeição */}
                        {sub.status === 'reprovado' && sub.motivo_reprovacao && (
                          <Alert className="mt-2 bg-red-50 border-red-200 py-2">
                            <AlertDescription className="text-red-700 text-xs">
                              <strong>Motivo:</strong> {sub.motivo_reprovacao}
                            </AlertDescription>
                          </Alert>
                        )}
                      </div>
                      
                      {/* Data de submissão */}
                      <div className="text-right text-xs text-slate-400">
                        <p>Enviado em</p>
                        <p className="font-medium">{formatDate(sub.data_submissao)}</p>
                      </div>
                      
                      <Button variant="ghost" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}
            
            {/* Paginação */}
            {paginacao && paginacao.total_pages > 1 && (
              <div className="flex justify-center gap-2 mt-6">
                <Button 
                  variant="outline" 
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <span className="flex items-center px-4 text-sm text-slate-600">
                  Página {page} de {paginacao.total_pages}
                </span>
                <Button 
                  variant="outline" 
                  size="sm"
                  disabled={page >= paginacao.total_pages}
                  onClick={() => setPage(p => p + 1)}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Modal de Detalhes */}
        <Dialog open={showModal} onOpenChange={setShowModal}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Detalhes da Submissão</DialogTitle>
            </DialogHeader>
            
            {selectedSubmissao && (
              <div className="space-y-4">
                {/* Status */}
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Status:</span>
                  <Badge className={getStatusConfig(selectedSubmissao.status).bg}>
                    {getStatusConfig(selectedSubmissao.status).label}
                  </Badge>
                </div>
                
                {/* Dados da corrida */}
                <div className="bg-slate-50 rounded-lg p-4 space-y-2">
                  <h3 className="font-semibold text-lg">{selectedSubmissao.nome_competicao}</h3>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-slate-500">Data:</span>
                      <p className="font-medium">{formatDate(selectedSubmissao.data_competicao)}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Distância:</span>
                      <p className="font-medium">{selectedSubmissao.distancia}</p>
                    </div>
                    {selectedSubmissao.colocacao && (
                      <div>
                        <span className="text-slate-500">Colocação:</span>
                        <p className="font-medium">{selectedSubmissao.colocacao}º lugar</p>
                      </div>
                    )}
                    {selectedSubmissao.tempo && (
                      <div>
                        <span className="text-slate-500">Tempo:</span>
                        <p className="font-medium">{selectedSubmissao.tempo}</p>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Foto do pódio */}
                {selectedSubmissao.foto_podio_url && (
                  <div>
                    <span className="text-slate-600 text-sm">Foto enviada:</span>
                    <img 
                      src={`${BACKEND_URL}${selectedSubmissao.foto_podio_url}`}
                      alt="Comprovante"
                      className="mt-2 rounded-lg max-h-48 object-cover w-full"
                    />
                  </div>
                )}
                
                {/* Motivo de rejeição */}
                {selectedSubmissao.status === 'reprovado' && selectedSubmissao.motivo_reprovacao && (
                  <Alert className="bg-red-50 border-red-200">
                    <XCircle className="w-4 h-4 text-red-500" />
                    <AlertDescription className="text-red-700">
                      <strong>Motivo da rejeição:</strong><br/>
                      {selectedSubmissao.motivo_reprovacao}
                    </AlertDescription>
                  </Alert>
                )}
                
                {/* Ação para reenviar */}
                {selectedSubmissao.status === 'reprovado' && (
                  <Button 
                    className="w-full bg-emerald-600 hover:bg-emerald-700"
                    onClick={() => { setShowModal(false); navigate('/submeter-resultado'); }}
                    data-testid="btn-submeter-novamente"
                  >
                    Submeter Novamente
                  </Button>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default HistoricoSubmissoesPage;
