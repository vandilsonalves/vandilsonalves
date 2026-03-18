import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { 
  Users, Trophy, TrendingUp, MapPin, Award, RefreshCw, Loader2, Eye, CheckCircle,
  Download, Edit, UserCog, Bell, X, Mail, Phone, Calendar, Target, BadgeCheck, ShieldCheck, Filter
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart as RechartsPie, Pie, Cell, LineChart, Line, Legend
} from 'recharts';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
  setLigaCidade,
  token
}) => {
  // Estado do modal de detalhes
  const [showDetalhesModal, setShowDetalhesModal] = useState(false);
  const [assessoriaDetalhes, setAssessoriaDetalhes] = useState(null);
  const [loadingDetalhes, setLoadingDetalhes] = useState(false);
  const [membrosAssessoria, setMembrosAssessoria] = useState([]);

  // Estados para filtros locais da tabela
  const [filtroEstadoLocal, setFiltroEstadoLocal] = useState('');
  const [filtroCidadeLocal, setFiltroCidadeLocal] = useState('');
  const [cidadesFiltroLocal, setCidadesFiltroLocal] = useState([]);

  // Lista de estados do Brasil
  const estadosBrasil = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
    'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
  ];

  // Buscar cidades do IBGE quando mudar o estado do filtro local
  useEffect(() => {
    const fetchCidadesIBGE = async () => {
      if (!filtroEstadoLocal) {
        setCidadesFiltroLocal([]);
        setFiltroCidadeLocal('');
        return;
      }
      try {
        const response = await fetch(
          `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${filtroEstadoLocal}/municipios`
        );
        const data = await response.json();
        setCidadesFiltroLocal(data.map(c => c.nome).sort());
      } catch (error) {
        console.error('Erro ao buscar cidades:', error);
        setCidadesFiltroLocal([]);
      }
    };
    fetchCidadesIBGE();
  }, [filtroEstadoLocal]);

  // Filtrar assessorias
  const getAssessoriasFiltradas = () => {
    let resultado = ligaRanking || [];

    if (filtroEstadoLocal) {
      resultado = resultado.filter(a => a.estado === filtroEstadoLocal);
    }

    if (filtroCidadeLocal) {
      resultado = resultado.filter(a => 
        a.cidade?.toLowerCase().includes(filtroCidadeLocal.toLowerCase())
      );
    }

    return resultado;
  };

  const assessoriasFiltradas = getAssessoriasFiltradas();

  const limparFiltrosLocais = () => {
    setFiltroEstadoLocal('');
    setFiltroCidadeLocal('');
  };

  // Buscar detalhes completos da assessoria
  const handleViewDetalhes = async (nomeAssessoria) => {
    setLoadingDetalhes(true);
    setShowDetalhesModal(true);
    
    try {
      // Buscar dados da assessoria na liga
      const response = await axios.get(`${API}/liga-assessorias/assessoria/${encodeURIComponent(nomeAssessoria)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const data = response.data;
      
      // Calcular se é verificada
      const isVerificada = Boolean(
        data.responsavel_nome && 
        data.total_atletas >= 10 && 
        data.total_resultados >= 5
      );
      
      // Mapear dados para o formato esperado pelo modal
      setAssessoriaDetalhes({
        ...data,
        dono_nome: data.responsavel_nome || data.dono?.nome || 'Não definido',
        dono_email: data.dono?.email,
        dono_foto: data.dono?.foto_url,
        posicao: data.posicao_nacional,
        verificada: isVerificada
      });
      
      // Preparar lista de membros com marcação do dono
      const membros = (data.atletas || []).map(m => ({
        ...m,
        is_dono: m.id === data.responsavel_id
      }));
      setMembrosAssessoria(membros);
      
    } catch (error) {
      console.error('Erro ao buscar detalhes:', error);
      toast.error('Erro ao carregar detalhes da assessoria');
      
      // Usar dados do ranking como fallback
      const assessoriaRanking = ligaRanking.find(a => a.nome === nomeAssessoria);
      if (assessoriaRanking) {
        setAssessoriaDetalhes({
          ...assessoriaRanking,
          dono_nome: assessoriaRanking.dono_nome || 'Não definido',
          membros: []
        });
      }
    } finally {
      setLoadingDetalhes(false);
    }
  };

  // Exportar lista de assessorias
  const handleExportAssessorias = (tipoExport) => {
    let dadosParaExportar = [];
    let nomeArquivo = '';
    const dados = assessoriasFiltradas;

    if (tipoExport === 'estado') {
      // Agrupar por estado
      const porEstado = {};
      dados.forEach(eq => {
        const estado = eq.estado || 'N/A';
        if (!porEstado[estado]) porEstado[estado] = [];
        porEstado[estado].push(eq);
      });

      const header = ['Estado', 'Posição', 'Assessoria', 'Dono', 'Cidade', 'Atletas', '1º Lugares', 'Resultados', 'Pontos', 'Selo'];
      dadosParaExportar = [header.join(';')];

      Object.keys(porEstado).sort().forEach(estado => {
        porEstado[estado].forEach((eq, idx) => {
          dadosParaExportar.push([
            estado,
            eq.posicao || idx + 1,
            eq.nome || '',
            eq.dono_nome || 'N/A',
            eq.cidade || '',
            eq.total_atletas || 0,
            eq.total_primeiros || 0,
            eq.total_resultados || 0,
            eq.pontos_total || 0,
            eq.selo?.toUpperCase() || 'N/A'
          ].join(';'));
        });
      });

      nomeArquivo = `assessorias_por_estado_${new Date().toISOString().slice(0,10)}.csv`;
    } else if (tipoExport === 'cidade') {
      // Agrupar por cidade
      const porCidade = {};
      dados.forEach(eq => {
        const cidade = eq.cidade || 'N/A';
        if (!porCidade[cidade]) porCidade[cidade] = [];
        porCidade[cidade].push(eq);
      });

      const header = ['Cidade', 'Estado', 'Posição', 'Assessoria', 'Dono', 'Atletas', '1º Lugares', 'Resultados', 'Pontos', 'Selo'];
      dadosParaExportar = [header.join(';')];

      Object.keys(porCidade).sort().forEach(cidade => {
        porCidade[cidade].forEach((eq, idx) => {
          dadosParaExportar.push([
            cidade,
            eq.estado || '',
            eq.posicao || idx + 1,
            eq.nome || '',
            eq.dono_nome || 'N/A',
            eq.total_atletas || 0,
            eq.total_primeiros || 0,
            eq.total_resultados || 0,
            eq.pontos_total || 0,
            eq.selo?.toUpperCase() || 'N/A'
          ].join(';'));
        });
      });

      nomeArquivo = `assessorias_por_cidade_${new Date().toISOString().slice(0,10)}.csv`;
    }

    // Criar e baixar arquivo
    const csvContent = '\ufeff' + dadosParaExportar.join('\n'); // BOM para UTF-8
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = nomeArquivo;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast.success(`Exportado ${dados.length} assessorias com sucesso!`);
  };

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
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <CardTitle className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500" />
              Ranking das Assessorias
              <Badge variant="secondary">{assessoriasFiltradas.length} assessorias</Badge>
            </CardTitle>
            <Select onValueChange={(v) => handleExportAssessorias(v)}>
              <SelectTrigger className="w-[180px]" data-testid="btn-exportar-assessorias">
                <Download className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Exportar Dados" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="estado">Por Estado</SelectItem>
                <SelectItem value="cidade">Por Cidade</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filtros Locais */}
          <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <div className="flex flex-wrap items-center gap-3">
              <Filter className="w-4 h-4 text-slate-500" />
              
              {/* Filtro Estado */}
              <div className="flex items-center gap-2">
                <Select value={filtroEstadoLocal || "__all__"} onValueChange={(v) => {
                  setFiltroEstadoLocal(v === "__all__" ? "" : v);
                  setFiltroCidadeLocal('');
                }}>
                  <SelectTrigger className="w-[120px]">
                    <SelectValue placeholder="Estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__all__">Todos</SelectItem>
                    {estadosBrasil.map(uf => (
                      <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Filtro Cidade */}
              <div className="flex items-center gap-2">
                <Select 
                  value={filtroCidadeLocal || "__all__"} 
                  onValueChange={(v) => setFiltroCidadeLocal(v === "__all__" ? "" : v)}
                  disabled={!filtroEstadoLocal}
                >
                  <SelectTrigger className="w-[160px]">
                    <SelectValue placeholder={filtroEstadoLocal ? "Cidade" : "Selecione UF"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__all__">Todas</SelectItem>
                    {cidadesFiltroLocal.map(cidade => (
                      <SelectItem key={cidade} value={cidade}>{cidade}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Limpar Filtros */}
              {(filtroEstadoLocal || filtroCidadeLocal) && (
                <Button variant="ghost" size="sm" onClick={limparFiltrosLocais}>
                  <X className="w-4 h-4 mr-1" />
                  Limpar
                </Button>
              )}

              <div className="ml-auto text-xs text-slate-500">
                Mostrando {assessoriasFiltradas.length} de {ligaRanking.length} assessorias
              </div>
            </div>
          </div>

          {loadingLiga ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
            </div>
          ) : assessoriasFiltradas.length === 0 ? (
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
                    <th className="text-left py-3 px-4 font-semibold">Dono</th>
                    <th className="text-left py-3 px-4 font-semibold">UF</th>
                    <th className="text-center py-3 px-4 font-semibold">Atletas</th>
                    <th className="text-center py-3 px-4 font-semibold">1º Lugares</th>
                    <th className="text-center py-3 px-4 font-semibold">Resultados</th>
                    <th className="text-right py-3 px-4 font-semibold">Pontos</th>
                    <th className="text-center py-3 px-4 font-semibold">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {assessoriasFiltradas.map((eq, idx) => (
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
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{eq.nome}</span>
                          {eq.verificada && (
                            <span title="Assessoria Verificada: 10+ atletas, 5+ resultados, dono definido">
                              <BadgeCheck className="w-5 h-5 text-blue-500" />
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <UserCog className="w-4 h-4 text-slate-400" />
                          <span className={eq.dono_nome ? 'text-slate-700' : 'text-slate-400 italic'}>
                            {eq.dono_nome || 'Não definido'}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4">{eq.estado}</td>
                      <td className="py-3 px-4 text-center">{eq.total_atletas}</td>
                      <td className="py-3 px-4 text-center">{eq.total_primeiros || 0}</td>
                      <td className="py-3 px-4 text-center">{eq.total_resultados}</td>
                      <td className="py-3 px-4 text-right font-bold text-amber-600">{eq.pontos_total}</td>
                      <td className="py-3 px-4 text-center">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleViewDetalhes(eq.nome)}
                          title="Ver detalhes da assessoria"
                          className="hover:bg-amber-100"
                        >
                          <Eye className="w-4 h-4 text-amber-600" />
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

      {/* Modal de Detalhes da Assessoria */}
      <Dialog open={showDetalhesModal} onOpenChange={setShowDetalhesModal}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl">
              <Trophy className="w-6 h-6 text-amber-500" />
              {assessoriaDetalhes?.nome || 'Detalhes da Assessoria'}
            </DialogTitle>
          </DialogHeader>
          
          {loadingDetalhes ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
            </div>
          ) : assessoriaDetalhes && (
            <div className="space-y-6">
              {/* Informações Principais */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
                  <CardContent className="pt-6">
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                      <Award className="w-5 h-5 text-amber-500" />
                      Informações Gerais
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Posição:</span>
                        <Badge className="bg-amber-500">{assessoriaDetalhes.posicao || 'N/A'}º lugar</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Selo:</span>
                        <Badge className={getSeloColor(assessoriaDetalhes.selo)}>
                          {getSeloIcon(assessoriaDetalhes.selo)} {assessoriaDetalhes.selo?.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Localização:</span>
                        <span className="font-medium">{assessoriaDetalhes.cidade}/{assessoriaDetalhes.estado}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Pontos Total:</span>
                        <span className="font-bold text-amber-600 text-lg">{assessoriaDetalhes.pontos_total}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Status:</span>
                        {assessoriaDetalhes.verificada ? (
                          <Badge className="bg-blue-500 text-white flex items-center gap-1">
                            <BadgeCheck className="w-4 h-4" />
                            Verificada
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-slate-500">
                            Não verificada
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                  <CardContent className="pt-6">
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                      <UserCog className="w-5 h-5 text-green-500" />
                      Dono da Assessoria
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <Avatar className="w-12 h-12 border-2 border-green-300">
                          <AvatarImage src={assessoriaDetalhes.dono_foto} />
                          <AvatarFallback className="bg-green-100 text-green-700">
                            {assessoriaDetalhes.dono_nome?.charAt(0) || '?'}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-semibold">{assessoriaDetalhes.dono_nome || 'Não definido'}</p>
                          {assessoriaDetalhes.dono_email && (
                            <p className="text-sm text-slate-500 flex items-center gap-1">
                              <Mail className="w-3 h-3" />
                              {assessoriaDetalhes.dono_email}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Estatísticas */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="pt-4 text-center">
                    <Users className="w-8 h-8 mx-auto text-blue-500 mb-2" />
                    <p className="text-2xl font-bold">{assessoriaDetalhes.total_atletas}</p>
                    <p className="text-sm text-slate-500">Atletas</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-4 text-center">
                    <CheckCircle className="w-8 h-8 mx-auto text-green-500 mb-2" />
                    <p className="text-2xl font-bold">{assessoriaDetalhes.total_resultados}</p>
                    <p className="text-sm text-slate-500">Resultados</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-4 text-center">
                    <Trophy className="w-8 h-8 mx-auto text-amber-500 mb-2" />
                    <p className="text-2xl font-bold">{assessoriaDetalhes.total_primeiros || 0}</p>
                    <p className="text-sm text-slate-500">1º Lugares</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-4 text-center">
                    <Target className="w-8 h-8 mx-auto text-purple-500 mb-2" />
                    <p className="text-2xl font-bold">{assessoriaDetalhes.pontos_total}</p>
                    <p className="text-sm text-slate-500">Pontos</p>
                  </CardContent>
                </Card>
              </div>

              {/* Critérios de Verificação */}
              <Card className={assessoriaDetalhes.verificada ? 'bg-blue-50 border-blue-200' : 'bg-slate-50'}>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 mb-3">
                    <ShieldCheck className={`w-5 h-5 ${assessoriaDetalhes.verificada ? 'text-blue-500' : 'text-slate-400'}`} />
                    <span className="font-semibold">Critérios para Selo de Verificação</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className={`flex items-center gap-2 ${assessoriaDetalhes.total_atletas >= 10 ? 'text-green-600' : 'text-slate-400'}`}>
                      {assessoriaDetalhes.total_atletas >= 10 ? <CheckCircle className="w-4 h-4" /> : <X className="w-4 h-4" />}
                      10+ atletas ({assessoriaDetalhes.total_atletas}/10)
                    </div>
                    <div className={`flex items-center gap-2 ${assessoriaDetalhes.total_resultados >= 5 ? 'text-green-600' : 'text-slate-400'}`}>
                      {assessoriaDetalhes.total_resultados >= 5 ? <CheckCircle className="w-4 h-4" /> : <X className="w-4 h-4" />}
                      5+ resultados ({assessoriaDetalhes.total_resultados}/5)
                    </div>
                    <div className={`flex items-center gap-2 ${assessoriaDetalhes.dono_nome ? 'text-green-600' : 'text-slate-400'}`}>
                      {assessoriaDetalhes.dono_nome ? <CheckCircle className="w-4 h-4" /> : <X className="w-4 h-4" />}
                      Dono definido
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Lista de Membros */}
              {membrosAssessoria.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="w-5 h-5 text-blue-500" />
                      Membros da Equipe ({membrosAssessoria.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
                      {membrosAssessoria.slice(0, 15).map((membro, idx) => (
                        <div key={idx} className="flex items-center gap-3 p-2 rounded-lg bg-slate-50 hover:bg-slate-100">
                          <Avatar className="w-8 h-8">
                            <AvatarImage src={membro.foto_url} />
                            <AvatarFallback className="bg-blue-100 text-blue-700 text-xs">
                              {membro.nome?.charAt(0) || '?'}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{membro.nome}</p>
                            <p className="text-xs text-slate-500">{membro.cidade}/{membro.estado}</p>
                          </div>
                          {membro.is_dono && (
                            <Badge className="bg-green-500 text-xs">Dono</Badge>
                          )}
                        </div>
                      ))}
                      {membrosAssessoria.length > 15 && (
                        <div className="col-span-full text-center text-sm text-slate-500 py-2">
                          ... e mais {membrosAssessoria.length - 15} membros
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetalhesModal(false)}>
              <X className="w-4 h-4 mr-2" />
              Fechar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardAssessorias;
