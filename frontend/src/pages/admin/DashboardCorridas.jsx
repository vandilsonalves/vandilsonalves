import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { 
  Star, Trophy, MapPin, Plus, Edit, Trash2, Loader2, 
  Calendar, CalendarDays, ExternalLink, BarChart3, Award, TrendingUp,
  Search, Download, Upload, FileSpreadsheet, Globe, AlertCircle,
  ArrowUpAZ, ArrowDownAZ, Filter, X, CheckSquare, Square
} from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

const DashboardCorridas = ({ 
  rankingCorridasDashboard,
  corridasEventos,
  loadingRankingCorridas,
  corridaFormData,
  setCorridaFormData,
  showCorridaModal,
  setShowCorridaModal,
  corridaEditando,
  setCorridaEditando,
  onSaveCorrida,
  onDeleteCorrida,
  onRefresh
}) => {
  // Estados para cidades do IBGE
  const [cidadesIBGE, setCidadesIBGE] = useState([]);
  const [loadingCidadesIBGE, setLoadingCidadesIBGE] = useState(false);

  // Estados para Scraping
  const [scrapingUrl, setScrapingUrl] = useState('');
  const [loadingScraping, setLoadingScraping] = useState(false);
  const [scrapingResultado, setScrapingResultado] = useState(null);
  const [showScrapingModal, setShowScrapingModal] = useState(false);

  // Estados para Importação
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [loadingImport, setLoadingImport] = useState(false);
  const fileInputRef = useRef(null);

  // Estados para seleção múltipla e exclusão em lote
  const [selectedCorridas, setSelectedCorridas] = useState([]);
  const [loadingExcluirLote, setLoadingExcluirLote] = useState(false);

  // Estados para filtros
  const [filtroEstado, setFiltroEstado] = useState('');
  const [filtroCidade, setFiltroCidade] = useState('');
  const [cidadesFiltro, setCidadesFiltro] = useState([]);

  // Estados para filtro de data
  const [filtroPeriodo, setFiltroPeriodo] = useState(''); // '', 'proximos30', 'proximos90', 'passados30', 'passados90', 'custom'
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');

  // Estado para ordenação
  const [ordenacao, setOrdenacao] = useState(''); // '', 'asc', 'desc'

  // Buscar cidades do IBGE para o filtro
  useEffect(() => {
    const fetchCidadesFiltro = async () => {
      if (!filtroEstado) {
        setCidadesFiltro([]);
        setFiltroCidade('');
        return;
      }
      try {
        const response = await axios.get(
          `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${filtroEstado}/municipios`
        );
        const cidadesOrdenadas = response.data
          .map(cidade => cidade.nome)
          .sort((a, b) => a.localeCompare(b));
        setCidadesFiltro(cidadesOrdenadas);
      } catch (error) {
        console.error('Erro ao buscar cidades:', error);
        setCidadesFiltro([]);
      }
    };
    fetchCidadesFiltro();
  }, [filtroEstado]);

  // Buscar cidades do IBGE quando o estado mudar
  useEffect(() => {
    const fetchCidadesIBGE = async () => {
      if (!corridaFormData.estado) {
        setCidadesIBGE([]);
        return;
      }
      setLoadingCidadesIBGE(true);
      try {
        const response = await axios.get(
          `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${corridaFormData.estado}/municipios`
        );
        const cidadesOrdenadas = response.data
          .map(cidade => cidade.nome)
          .sort((a, b) => a.localeCompare(b));
        setCidadesIBGE(cidadesOrdenadas);
      } catch (error) {
        console.error('Erro ao buscar cidades do IBGE:', error);
        setCidadesIBGE([]);
        toast.error('Erro ao buscar cidades. Tente novamente.');
      } finally {
        setLoadingCidadesIBGE(false);
      }
    };

    fetchCidadesIBGE();
  }, [corridaFormData.estado]);

  // ==================== FUNÇÕES DE SCRAPING ====================
  
  const handleScraping = async () => {
    if (!scrapingUrl.trim()) {
      toast.error('Digite uma URL válida');
      return;
    }

    setLoadingScraping(true);
    setScrapingResultado(null);

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('url', scrapingUrl);

      const response = await axios.post(`${API}/corridas-eventos/scraping`, formData, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      setScrapingResultado(response.data);
      
      if (response.data.success && response.data.total_encontradas > 0) {
        toast.success(`${response.data.total_encontradas} corridas encontradas!`);
        setShowScrapingModal(true);
      } else {
        toast.warning(response.data.mensagem || 'Nenhuma corrida encontrada');
      }
    } catch (error) {
      console.error('Erro no scraping:', error);
      toast.error(error.response?.data?.detail || 'Erro ao fazer varredura');
    } finally {
      setLoadingScraping(false);
    }
  };

  const handleExportarScraping = async (formato) => {
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('url', scrapingUrl);
      formData.append('formato', formato);

      const response = await axios.post(`${API}/corridas-eventos/scraping/exportar`, formData, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        responseType: 'blob'
      });

      // Criar download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = formato === 'excel' ? 'corridas_scraping.xlsx' : 'corridas_scraping.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success(`Arquivo ${formato.toUpperCase()} baixado com sucesso!`);
    } catch (error) {
      console.error('Erro ao exportar:', error);
      toast.error('Erro ao exportar arquivo');
    }
  };

  // ==================== FUNÇÕES DE IMPORTAÇÃO ====================

  const handleImportar = async () => {
    if (!importFile) {
      toast.error('Selecione um arquivo');
      return;
    }

    setLoadingImport(true);

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('arquivo', importFile);

      const response = await axios.post(`${API}/corridas-eventos/importar`, formData, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        toast.success(response.data.mensagem);
        setShowImportModal(false);
        setImportFile(null);
        if (onRefresh) onRefresh();
      }
    } catch (error) {
      console.error('Erro na importação:', error);
      toast.error(error.response?.data?.detail || 'Erro ao importar arquivo');
    } finally {
      setLoadingImport(false);
    }
  };

  const handleDownloadTemplate = async (formato) => {
    try {
      const response = await axios.get(`${API}/corridas-eventos/template?formato=${formato}`, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = formato === 'excel' ? 'template_corridas.xlsx' : 'template_corridas.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success('Template baixado!');
    } catch (error) {
      console.error('Erro ao baixar template:', error);
      toast.error('Erro ao baixar template');
    }
  };

  // ==================== SELEÇÃO E EXCLUSÃO EM LOTE ====================

  const handleSelectCorrida = (corridaId) => {
    setSelectedCorridas(prev => {
      if (prev.includes(corridaId)) {
        return prev.filter(id => id !== corridaId);
      } else {
        return [...prev, corridaId];
      }
    });
  };

  const handleSelectAll = () => {
    const corridasFiltradas = getCorridasFiltradas();
    if (selectedCorridas.length === corridasFiltradas.length) {
      setSelectedCorridas([]);
    } else {
      setSelectedCorridas(corridasFiltradas.map(c => c.id));
    }
  };

  const handleExcluirLote = async () => {
    if (selectedCorridas.length === 0) {
      toast.error('Selecione ao menos uma corrida');
      return;
    }

    if (!window.confirm(`Deseja excluir ${selectedCorridas.length} corrida(s)?`)) {
      return;
    }

    setLoadingExcluirLote(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('ids', selectedCorridas.join(','));

      const response = await axios.post(`${API}/corridas-eventos/excluir-lote`, formData, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success(response.data.message);
      setSelectedCorridas([]);
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Erro ao excluir:', error);
      toast.error(error.response?.data?.detail || 'Erro ao excluir corridas');
    } finally {
      setLoadingExcluirLote(false);
    }
  };

  // ==================== FILTROS E ORDENAÇÃO ====================

  const getCorridasFiltradas = () => {
    let resultado = corridasEventos || [];

    // Filtrar por estado
    if (filtroEstado) {
      resultado = resultado.filter(c => c.estado === filtroEstado);
    }

    // Filtrar por cidade
    if (filtroCidade) {
      resultado = resultado.filter(c => c.cidade?.toLowerCase().includes(filtroCidade.toLowerCase()));
    }

    // Filtrar por período/data
    if (filtroPeriodo) {
      const hoje = new Date();
      hoje.setHours(0, 0, 0, 0);

      if (filtroPeriodo === 'proximos30') {
        const limite = new Date(hoje);
        limite.setDate(limite.getDate() + 30);
        resultado = resultado.filter(c => {
          if (!c.data_corrida) return false;
          const dataCorrida = new Date(c.data_corrida);
          return dataCorrida >= hoje && dataCorrida <= limite;
        });
      } else if (filtroPeriodo === 'proximos90') {
        const limite = new Date(hoje);
        limite.setDate(limite.getDate() + 90);
        resultado = resultado.filter(c => {
          if (!c.data_corrida) return false;
          const dataCorrida = new Date(c.data_corrida);
          return dataCorrida >= hoje && dataCorrida <= limite;
        });
      } else if (filtroPeriodo === 'passados30') {
        const limite = new Date(hoje);
        limite.setDate(limite.getDate() - 30);
        resultado = resultado.filter(c => {
          if (!c.data_corrida) return false;
          const dataCorrida = new Date(c.data_corrida);
          return dataCorrida >= limite && dataCorrida < hoje;
        });
      } else if (filtroPeriodo === 'passados90') {
        const limite = new Date(hoje);
        limite.setDate(limite.getDate() - 90);
        resultado = resultado.filter(c => {
          if (!c.data_corrida) return false;
          const dataCorrida = new Date(c.data_corrida);
          return dataCorrida >= limite && dataCorrida < hoje;
        });
      } else if (filtroPeriodo === 'custom' && (dataInicio || dataFim)) {
        resultado = resultado.filter(c => {
          if (!c.data_corrida) return false;
          const dataCorrida = new Date(c.data_corrida);
          if (dataInicio && dataCorrida < new Date(dataInicio)) return false;
          if (dataFim && dataCorrida > new Date(dataFim)) return false;
          return true;
        });
      }
    }

    // Ordenar
    if (ordenacao === 'asc') {
      resultado = [...resultado].sort((a, b) => (a.nome_corrida || '').localeCompare(b.nome_corrida || ''));
    } else if (ordenacao === 'desc') {
      resultado = [...resultado].sort((a, b) => (b.nome_corrida || '').localeCompare(a.nome_corrida || ''));
    }

    return resultado;
  };

  const limparFiltros = () => {
    setFiltroEstado('');
    setFiltroCidade('');
    setFiltroPeriodo('');
    setDataInicio('');
    setDataFim('');
    setOrdenacao('');
    setSelectedCorridas([]);
  };

  const corridasFiltradas = getCorridasFiltradas();

  // Dados do dashboard
  const stats = rankingCorridasDashboard || {};
  const distribuicaoNotas = stats.distribuicao_notas || [];
  const topCorridas = stats.top_corridas || [];
  const corridasPorEstado = stats.corridas_por_estado || [];

  // Handlers para modal
  const handleOpenAdd = () => {
    setCorridaEditando(null);
    setCidadesIBGE([]);
    setCorridaFormData({
      nome_corrida: '',
      organizador: '',
      cidade: '',
      estado: '',
      data_corrida: '',
      pagina_link: '',
      status: 'ativa'
    });
    setShowCorridaModal(true);
  };

  const handleOpenEdit = (corrida) => {
    setCorridaEditando(corrida);
    setCorridaFormData({
      nome_corrida: corrida.nome_corrida || '',
      organizador: corrida.organizador || '',
      cidade: corrida.cidade || '',
      estado: corrida.estado || '',
      data_corrida: corrida.data_corrida || '',
      pagina_link: corrida.pagina_link || '',
      status: corrida.status || 'ativa'
    });
    setShowCorridaModal(true);
  };

  // Handler para mudança de estado - limpa a cidade
  const handleEstadoChange = (novoEstado) => {
    setCorridaFormData({
      ...corridaFormData,
      estado: novoEstado,
      cidade: '' // Limpar cidade ao mudar estado
    });
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Total Corridas</p>
                <p className="text-3xl font-bold">{stats.total_corridas || 0}</p>
              </div>
              <Trophy className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-500 to-orange-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-amber-100 text-sm">Total Avaliações</p>
                <p className="text-3xl font-bold">{stats.total_avaliacoes || 0}</p>
              </div>
              <Star className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Média Geral</p>
                <p className="text-3xl font-bold">{(stats.media_geral || 0).toFixed(1)}</p>
              </div>
              <TrendingUp className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Melhor Avaliada</p>
                <p className="text-lg font-bold truncate" title={stats.melhor_avaliada?.nome}>
                  {stats.melhor_avaliada?.nome?.substring(0, 15) || 'N/A'}
                </p>
              </div>
              <Award className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sistema de Selos */}
      <Card className="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 border-amber-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-500" />
            Sistema de Selos - Certificações
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-4 bg-white dark:bg-slate-800 rounded-lg">
              <span className="text-2xl">⭐</span>
              <div>
                <p className="font-semibold">Selo 5 Estrelas</p>
                <p className="text-sm text-slate-500">Média ≥ 4.5 + 50 avaliações</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-white dark:bg-slate-800 rounded-lg">
              <span className="text-2xl">🏆</span>
              <div>
                <p className="font-semibold">Top 10 Brasil</p>
                <p className="text-sm text-slate-500">10 melhores nacional</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-white dark:bg-slate-800 rounded-lg">
              <span className="text-2xl">📍</span>
              <div>
                <p className="font-semibold">Top 10 Estado</p>
                <p className="text-sm text-slate-500">10 melhores por UF</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribuição de Notas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              Distribuição de Notas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distribuicaoNotas}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="nota" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="quantidade" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Top 10 Melhores Corridas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500" />
              Top 10 - Melhores Corridas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {topCorridas.length === 0 ? (
                <p className="text-center text-slate-500 py-8">Nenhuma corrida avaliada</p>
              ) : (
                topCorridas.map((corrida, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                        idx < 3 ? 'bg-amber-100 text-amber-800' : 'bg-slate-200 text-slate-600'
                      }`}>
                        {idx + 1}
                      </span>
                      <span className="text-sm font-medium truncate max-w-[200px]">{corrida.nome}</span>
                    </div>
                    <Badge className="bg-green-100 text-green-800">
                      {(corrida.media || 0).toFixed(1)} ⭐
                    </Badge>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabela de Gerenciamento */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-500" />
              Gerenciar Corridas/Eventos
              <Badge variant="secondary">{corridasEventos?.length || 0} eventos</Badge>
            </CardTitle>
            <div className="flex gap-2">
              <Button onClick={() => setShowImportModal(true)} size="sm" variant="outline" className="border-green-500 text-green-600 hover:bg-green-50">
                <Upload className="w-4 h-4 mr-2" />
                Importar
              </Button>
              <Button onClick={handleOpenAdd} size="sm" className="bg-blue-500 hover:bg-blue-600">
                <Plus className="w-4 h-4 mr-2" />
                Nova Corrida
              </Button>
            </div>
          </div>
          
          {/* Barra de Scraping */}
          <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <div className="flex items-center gap-2 mb-3">
              <Globe className="w-5 h-5 text-purple-600" />
              <span className="font-semibold text-purple-700 dark:text-purple-300">Varredura Automática de Corridas</span>
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Cole a URL do site de corridas (Ticket Sports, Minhas Inscrições, etc.)"
                value={scrapingUrl}
                onChange={(e) => setScrapingUrl(e.target.value)}
                className="flex-1"
                data-testid="input-scraping-url"
              />
              <Button 
                onClick={handleScraping} 
                disabled={loadingScraping || !scrapingUrl.trim()}
                className="bg-purple-600 hover:bg-purple-700"
                data-testid="btn-scraping"
              >
                {loadingScraping ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Search className="w-4 h-4 mr-2" />
                )}
                {loadingScraping ? 'Buscando...' : 'Buscar Corridas'}
              </Button>
            </div>
            
            {/* Resultado do Scraping inline */}
            {scrapingResultado && (
              <div className="mt-4 p-4 bg-white dark:bg-slate-800 rounded-lg border">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      Fonte: {scrapingResultado.fonte}
                    </p>
                    <p className={`font-semibold ${scrapingResultado.total_encontradas > 0 ? 'text-green-600' : 'text-amber-600'}`}>
                      {scrapingResultado.total_encontradas > 0 
                        ? `${scrapingResultado.total_encontradas} corridas encontradas!`
                        : 'Nenhuma corrida encontrada neste site'}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {scrapingResultado.total_encontradas > 0 ? (
                      <>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleExportarScraping('csv')}
                          className="border-green-500 text-green-600 hover:bg-green-50"
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Baixar CSV
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleExportarScraping('excel')}
                          className="border-blue-500 text-blue-600 hover:bg-blue-50"
                        >
                          <FileSpreadsheet className="w-4 h-4 mr-2" />
                          Baixar Excel
                        </Button>
                        <Button 
                          size="sm"
                          onClick={() => setShowScrapingModal(true)}
                          className="bg-purple-600 hover:bg-purple-700"
                        >
                          Ver Detalhes
                        </Button>
                      </>
                    ) : (
                      <div className="flex gap-2 items-center">
                        <span className="text-sm text-slate-500">Use a importação manual:</span>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDownloadTemplate('csv')}
                          className="border-green-500 text-green-600"
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Template CSV
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDownloadTemplate('excel')}
                          className="border-blue-500 text-blue-600"
                        >
                          <FileSpreadsheet className="w-4 h-4 mr-2" />
                          Template Excel
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Preview das corridas encontradas */}
                {scrapingResultado.total_encontradas > 0 && (
                  <div className="border rounded-lg overflow-hidden max-h-60 overflow-y-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-100 dark:bg-slate-700 sticky top-0">
                        <tr>
                          <th className="text-left p-2 font-semibold">Nome</th>
                          <th className="text-left p-2 font-semibold">Cidade/UF</th>
                          <th className="text-left p-2 font-semibold">Data</th>
                        </tr>
                      </thead>
                      <tbody>
                        {scrapingResultado.corridas?.slice(0, 10).map((corrida, idx) => (
                          <tr key={idx} className="border-t hover:bg-slate-50 dark:hover:bg-slate-800/50">
                            <td className="p-2">{corrida.nome_corrida?.substring(0, 40)}</td>
                            <td className="p-2">{corrida.cidade}/{corrida.estado}</td>
                            <td className="p-2">{corrida.data_corrida || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {scrapingResultado.corridas?.length > 10 && (
                      <div className="p-2 bg-slate-50 text-center text-xs text-slate-500">
                        + {scrapingResultado.corridas.length - 10} corridas. Clique em "Ver Detalhes" para ver todas.
                      </div>
                    )}
                  </div>
                )}
                
                {/* Dica quando não encontra */}
                {scrapingResultado.total_encontradas === 0 && (
                  <div className="mt-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-sm">
                    <p className="font-semibold text-amber-700 mb-1">💡 Dica:</p>
                    <p className="text-amber-600">
                      Muitos sites modernos carregam conteúdo via JavaScript, dificultando a varredura automática.
                      Use a <strong>importação manual</strong>: baixe o template, preencha com as corridas e faça o upload.
                    </p>
                  </div>
                )}
              </div>
            )}
            
            <p className="text-xs text-purple-600 dark:text-purple-400 mt-2">
              <AlertCircle className="w-3 h-3 inline mr-1" />
              Sites suportados: Ticket Sports, Minhas Inscrições, Webrun, Sympla e outros sites de eventos esportivos
            </p>
          </div>
        </CardHeader>
        <CardContent>
          {loadingRankingCorridas ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : !corridasEventos || corridasEventos.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Trophy className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>Nenhuma corrida cadastrada</p>
            </div>
          ) : (
            <>
              {/* Barra de Filtros e Ações em Lote */}
              <div className="mb-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <div className="flex flex-wrap items-center gap-4">
                  {/* Filtro por Estado */}
                  <div className="flex items-center gap-2">
                    <Filter className="w-4 h-4 text-slate-500" />
                    <Select value={filtroEstado || "__all__"} onValueChange={(v) => { setFiltroEstado(v === "__all__" ? "" : v); setFiltroCidade(''); }}>
                      <SelectTrigger className="w-[120px]">
                        <SelectValue placeholder="Estado" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__all__">Todos</SelectItem>
                        {ESTADOS_BR.map(uf => (
                          <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Filtro por Cidade */}
                  <div>
                    <Select 
                      value={filtroCidade || "__all__"} 
                      onValueChange={(v) => setFiltroCidade(v === "__all__" ? "" : v)}
                      disabled={!filtroEstado}
                    >
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder={filtroEstado ? "Cidade" : "Selecione UF"} />
                      </SelectTrigger>
                      <SelectContent className="max-h-60">
                        <SelectItem value="__all__">Todas</SelectItem>
                        {cidadesFiltro.map(cidade => (
                          <SelectItem key={cidade} value={cidade}>{cidade}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Filtro por Período/Data */}
                  <div className="flex items-center gap-2">
                    <CalendarDays className="w-4 h-4 text-slate-500" />
                    <Select value={filtroPeriodo || "__all__"} onValueChange={(v) => { 
                      setFiltroPeriodo(v === "__all__" ? "" : v);
                      if (v !== "custom") {
                        setDataInicio('');
                        setDataFim('');
                      }
                    }}>
                      <SelectTrigger className="w-[160px]">
                        <SelectValue placeholder="Período" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__all__">Todas as datas</SelectItem>
                        <SelectItem value="proximos30">Próximos 30 dias</SelectItem>
                        <SelectItem value="proximos90">Próximos 90 dias</SelectItem>
                        <SelectItem value="passados30">Últimos 30 dias</SelectItem>
                        <SelectItem value="passados90">Últimos 90 dias</SelectItem>
                        <SelectItem value="custom">Período personalizado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Campos de Data Personalizada */}
                  {filtroPeriodo === 'custom' && (
                    <div className="flex items-center gap-2">
                      <Input
                        type="date"
                        value={dataInicio}
                        onChange={(e) => setDataInicio(e.target.value)}
                        className="w-[140px]"
                        placeholder="Data início"
                        data-testid="input-data-inicio"
                      />
                      <span className="text-slate-400">até</span>
                      <Input
                        type="date"
                        value={dataFim}
                        onChange={(e) => setDataFim(e.target.value)}
                        className="w-[140px]"
                        placeholder="Data fim"
                        data-testid="input-data-fim"
                      />
                    </div>
                  )}

                  {/* Ordenação */}
                  <div className="flex items-center gap-1">
                    <Button
                      variant={ordenacao === 'asc' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setOrdenacao(ordenacao === 'asc' ? '' : 'asc')}
                      className={ordenacao === 'asc' ? 'bg-blue-500' : ''}
                    >
                      <ArrowUpAZ className="w-4 h-4" />
                    </Button>
                    <Button
                      variant={ordenacao === 'desc' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setOrdenacao(ordenacao === 'desc' ? '' : 'desc')}
                      className={ordenacao === 'desc' ? 'bg-blue-500' : ''}
                    >
                      <ArrowDownAZ className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Limpar Filtros */}
                  {(filtroEstado || filtroCidade || filtroPeriodo || ordenacao) && (
                    <Button variant="ghost" size="sm" onClick={limparFiltros}>
                      <X className="w-4 h-4 mr-1" />
                      Limpar
                    </Button>
                  )}

                  {/* Contador de selecionados e botão excluir */}
                  <div className="flex-1 flex justify-end items-center gap-3">
                    {selectedCorridas.length > 0 && (
                      <>
                        <Badge variant="secondary" className="px-3 py-1">
                          {selectedCorridas.length} selecionada(s)
                        </Badge>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={handleExcluirLote}
                          disabled={loadingExcluirLote}
                        >
                          {loadingExcluirLote ? (
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                          ) : (
                            <Trash2 className="w-4 h-4 mr-2" />
                          )}
                          Excluir Selecionadas
                        </Button>
                      </>
                    )}
                  </div>
                </div>

                {/* Info de resultados */}
                <div className="mt-2 text-xs text-slate-500">
                  Mostrando {corridasFiltradas.length} de {corridasEventos.length} corridas
                </div>
              </div>

              {/* Tabela */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-slate-50 dark:bg-slate-800">
                      <th className="py-3 px-2 w-10">
                        <Checkbox
                          checked={corridasFiltradas.length > 0 && selectedCorridas.length === corridasFiltradas.length}
                          onCheckedChange={handleSelectAll}
                          data-testid="checkbox-select-all"
                        />
                      </th>
                      <th className="text-left py-3 px-4 font-semibold">Corrida</th>
                      <th className="text-left py-3 px-4 font-semibold">Organizador</th>
                      <th className="text-left py-3 px-4 font-semibold">Local</th>
                      <th className="text-center py-3 px-4 font-semibold">Avaliações</th>
                      <th className="text-center py-3 px-4 font-semibold">Média</th>
                      <th className="text-center py-3 px-4 font-semibold">Status</th>
                      <th className="text-center py-3 px-4 font-semibold">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {corridasFiltradas.map((corrida) => (
                      <tr 
                        key={corrida.id} 
                        className={`border-b hover:bg-slate-50 dark:hover:bg-slate-800 ${selectedCorridas.includes(corrida.id) ? 'bg-blue-50 dark:bg-blue-900/20' : ''}`}
                      >
                        <td className="py-3 px-2">
                          <Checkbox
                            checked={selectedCorridas.includes(corrida.id)}
                            onCheckedChange={() => handleSelectCorrida(corrida.id)}
                            data-testid={`checkbox-corrida-${corrida.id}`}
                          />
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{corrida.nome_corrida}</span>
                            {corrida.pagina_link && (
                              <a href={corrida.pagina_link} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="w-3 h-3 text-slate-400" />
                              </a>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">{corrida.organizador}</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-1">
                            <MapPin className="w-3 h-3 text-slate-400" />
                            {corrida.cidade}/{corrida.estado}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center">{corrida.total_avaliacoes || 0}</td>
                        <td className="py-3 px-4 text-center">
                          <Badge className="bg-amber-100 text-amber-800">
                            {(corrida.media_geral || 0).toFixed(1)} ⭐
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <Badge className={corrida.status === 'ativa' ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-800'}>
                            {corrida.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <Button variant="ghost" size="sm" onClick={() => handleOpenEdit(corrida)}>
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => onDeleteCorrida(corrida.id)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Modal de Cadastro/Edição */}
      <Dialog open={showCorridaModal} onOpenChange={setShowCorridaModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {corridaEditando ? 'Editar Corrida' : 'Nova Corrida'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nome da Corrida *</Label>
              <Input
                value={corridaFormData.nome_corrida}
                onChange={(e) => setCorridaFormData({...corridaFormData, nome_corrida: e.target.value})}
                placeholder="Ex: Maratona de São Paulo 2026"
              />
            </div>
            <div>
              <Label>Organizador</Label>
              <Input
                value={corridaFormData.organizador}
                onChange={(e) => setCorridaFormData({...corridaFormData, organizador: e.target.value})}
                placeholder="Nome do organizador"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Estado *</Label>
                <Select 
                  value={corridaFormData.estado} 
                  onValueChange={handleEstadoChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o UF" />
                  </SelectTrigger>
                  <SelectContent>
                    {ESTADOS_BR.map(uf => (
                      <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Cidade *</Label>
                <Select 
                  value={corridaFormData.cidade} 
                  onValueChange={(v) => setCorridaFormData({...corridaFormData, cidade: v})}
                  disabled={!corridaFormData.estado || loadingCidadesIBGE}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={loadingCidadesIBGE ? "Carregando..." : "Selecione a cidade"} />
                  </SelectTrigger>
                  <SelectContent className="max-h-60">
                    {cidadesIBGE.map(cidade => (
                      <SelectItem key={cidade} value={cidade}>{cidade}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {!corridaFormData.estado && (
                  <p className="text-xs text-slate-500 mt-1">Selecione o estado primeiro</p>
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Data da Corrida</Label>
                <Input
                  type="date"
                  value={corridaFormData.data_corrida}
                  onChange={(e) => setCorridaFormData({...corridaFormData, data_corrida: e.target.value})}
                />
              </div>
              <div>
                <Label>Status</Label>
                <Select 
                  value={corridaFormData.status} 
                  onValueChange={(v) => setCorridaFormData({...corridaFormData, status: v})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ativa">Ativa</SelectItem>
                    <SelectItem value="encerrada">Encerrada</SelectItem>
                    <SelectItem value="cancelada">Cancelada</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Link da Página</Label>
              <Input
                value={corridaFormData.pagina_link}
                onChange={(e) => setCorridaFormData({...corridaFormData, pagina_link: e.target.value})}
                placeholder="https://..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCorridaModal(false)}>
              Cancelar
            </Button>
            <Button onClick={onSaveCorrida} className="bg-blue-500 hover:bg-blue-600">
              {corridaEditando ? 'Salvar' : 'Cadastrar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Resultado do Scraping */}
      <Dialog open={showScrapingModal} onOpenChange={setShowScrapingModal}>
        <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-purple-600 flex items-center gap-2">
              <Globe className="w-6 h-6" />
              Resultado da Varredura
            </DialogTitle>
          </DialogHeader>
          
          {scrapingResultado && (
            <div className="space-y-4">
              {/* Info do scraping */}
              <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">Fonte: {scrapingResultado.fonte}</p>
                    <p className="font-semibold text-purple-700 dark:text-purple-300">
                      {scrapingResultado.total_encontradas} corridas encontradas
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleExportarScraping('csv')}
                      className="border-green-500 text-green-600"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      CSV
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleExportarScraping('excel')}
                      className="border-blue-500 text-blue-600"
                    >
                      <FileSpreadsheet className="w-4 h-4 mr-2" />
                      Excel
                    </Button>
                  </div>
                </div>
              </div>

              {/* Lista de corridas encontradas */}
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-slate-100 dark:bg-slate-800">
                    <tr>
                      <th className="text-left p-3 font-semibold">Nome da Corrida</th>
                      <th className="text-left p-3 font-semibold">Organizador</th>
                      <th className="text-left p-3 font-semibold">Cidade/UF</th>
                      <th className="text-left p-3 font-semibold">Data</th>
                      <th className="text-left p-3 font-semibold">Link</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scrapingResultado.corridas?.slice(0, 20).map((corrida, idx) => (
                      <tr key={idx} className="border-t hover:bg-slate-50 dark:hover:bg-slate-800/50">
                        <td className="p-3 font-medium">{corrida.nome_corrida}</td>
                        <td className="p-3 text-slate-600">{corrida.organizador}</td>
                        <td className="p-3">
                          <Badge variant="outline">{corrida.cidade}/{corrida.estado}</Badge>
                        </td>
                        <td className="p-3 text-slate-600">{corrida.data_corrida || '-'}</td>
                        <td className="p-3">
                          {corrida.pagina_link && (
                            <a 
                              href={corrida.pagina_link} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-blue-500 hover:underline flex items-center gap-1"
                            >
                              <ExternalLink className="w-3 h-3" />
                              Ver
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {scrapingResultado.corridas?.length > 20 && (
                  <div className="p-3 bg-slate-50 text-center text-sm text-slate-500">
                    Mostrando 20 de {scrapingResultado.corridas.length} corridas. Exporte para ver todas.
                  </div>
                )}
              </div>

              <p className="text-sm text-slate-500">
                💡 Exporte os dados e depois importe na plataforma usando o botão "Importar" para adicionar as corridas ao banco de dados.
              </p>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowScrapingModal(false)}>
              Fechar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Importação em Lote */}
      <Dialog open={showImportModal} onOpenChange={setShowImportModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-green-600 flex items-center gap-2">
              <Upload className="w-6 h-6" />
              Importar Corridas em Lote
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <h4 className="font-semibold text-green-700 mb-2">Formato do arquivo:</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                Colunas esperadas: Nome da Corrida, Organizador, Cidade, Estado, Link da Página, Data do Evento, Status
              </p>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleDownloadTemplate('csv')}
                  className="border-green-500 text-green-600"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Template CSV
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleDownloadTemplate('excel')}
                  className="border-blue-500 text-blue-600"
                >
                  <FileSpreadsheet className="w-4 h-4 mr-2" />
                  Template Excel
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Selecione o arquivo (CSV ou Excel):</Label>
              <Input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={(e) => setImportFile(e.target.files[0])}
                ref={fileInputRef}
                data-testid="input-import-file"
              />
              {importFile && (
                <p className="text-sm text-slate-500">
                  📄 Arquivo selecionado: {importFile.name}
                </p>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowImportModal(false);
              setImportFile(null);
            }}>
              Cancelar
            </Button>
            <Button 
              onClick={handleImportar} 
              disabled={!importFile || loadingImport}
              className="bg-green-600 hover:bg-green-700"
            >
              {loadingImport ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Upload className="w-4 h-4 mr-2" />
              )}
              {loadingImport ? 'Importando...' : 'Importar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardCorridas;
