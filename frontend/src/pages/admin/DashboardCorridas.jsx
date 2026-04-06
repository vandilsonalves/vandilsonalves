import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { downloadFile, downloadCSVContent } from '@/utils/downloadHelper';
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
  ArrowUpAZ, ArrowDownAZ, Filter, X, CheckSquare, Square, FileText,
  RefreshCw, Bookmark, Clock, Link2, ShieldCheck, AlertOctagon,
  Check, XCircle, User, ChevronDown
} from 'lucide-react';
import CidadeCombobox from '@/components/CidadeCombobox';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import { toast } from 'sonner';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

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

  // Estados para Scraping Avançado
  const [scrapingUrl, setScrapingUrl] = useState('');
  const [loadingScraping, setLoadingScraping] = useState(false);
  const [scrapingResultado, setScrapingResultado] = useState(null);
  const [showScrapingModal, setShowScrapingModal] = useState(false);
  const [fontesMonitoradas, setFontesMonitoradas] = useState([]);
  const [loadingFontes, setLoadingFontes] = useState(false);
  const [showFontes, setShowFontes] = useState(false);
  const [loadingAtualizarTodas, setLoadingAtualizarTodas] = useState(false);

  // Estados para Importação
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [loadingImport, setLoadingImport] = useState(false);
  const fileInputRef = useRef(null);
  const reportRef = useRef(null);

  // Estados para seleção múltipla e exclusão em lote
  const [selectedCorridas, setSelectedCorridas] = useState([]);
  const [loadingExcluirLote, setLoadingExcluirLote] = useState(false);

  // Estados para filtros
  const [filtroEstado, setFiltroEstado] = useState('');
  const [filtroCidade, setFiltroCidade] = useState('');
  const [cidadesFiltro, setCidadesFiltro] = useState([]);
  const [filtroStatus, setFiltroStatus] = useState(''); // '', 'ativa', 'encerrada', 'cancelada'

  // Estados para filtro de data
  const [filtroPeriodo, setFiltroPeriodo] = useState(''); // '', 'proximos30', 'proximos90', 'passados30', 'passados90', 'custom'
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');

  // Estado para ordenação
  const [ordenacao, setOrdenacao] = useState(''); // '', 'asc', 'desc'

  // Estado para modal de relatório
  const [showReportModal, setShowReportModal] = useState(false);
  const [generatingPDF, setGeneratingPDF] = useState(false);

  // ==================== APROVAÇÃO DE CORRIDAS PENDENTES ====================
  const [corridasPendentes, setCorridasPendentes] = useState([]);
  const [loadingPendentes, setLoadingPendentes] = useState(false);
  const [loadingAprovacao, setLoadingAprovacao] = useState({});
  const [motivoRejeicao, setMotivoRejeicao] = useState('');
  const [showRejeicaoModal, setShowRejeicaoModal] = useState(false);
  const [corridaRejeitar, setCorridaRejeitar] = useState(null);

  const fetchCorridasPendentes = async () => {
    setLoadingPendentes(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/corridas-eventos/pendentes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setCorridasPendentes(response.data.corridas || []);
    } catch (error) {
      console.error('Erro ao buscar corridas pendentes:', error);
    } finally {
      setLoadingPendentes(false);
    }
  };

  useEffect(() => {
    fetchCorridasPendentes();
  }, []);

  const handleAprovarCorrida = async (corridaId) => {
    setLoadingAprovacao(prev => ({ ...prev, [corridaId]: 'aprovando' }));
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/corridas-eventos/${corridaId}/aprovar`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      toast.success('Corrida aprovada com sucesso!');
      setCorridasPendentes(prev => prev.filter(c => c.id !== corridaId));
      if (onRefresh) onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao aprovar corrida');
    } finally {
      setLoadingAprovacao(prev => ({ ...prev, [corridaId]: null }));
    }
  };

  const handleRejeitarCorrida = async () => {
    if (!corridaRejeitar) return;
    setLoadingAprovacao(prev => ({ ...prev, [corridaRejeitar.id]: 'rejeitando' }));
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/corridas-eventos/${corridaRejeitar.id}/rejeitar`, 
        { motivo: motivoRejeicao },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      toast.success('Corrida rejeitada.');
      setCorridasPendentes(prev => prev.filter(c => c.id !== corridaRejeitar.id));
      setShowRejeicaoModal(false);
      setMotivoRejeicao('');
      setCorridaRejeitar(null);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao rejeitar corrida');
    } finally {
      setLoadingAprovacao(prev => ({ ...prev, [corridaRejeitar?.id]: null }));
    }
  };

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
  
  // Carregar fontes monitoradas
  const fetchFontes = async () => {
    setLoadingFontes(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API}/scraping/fontes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFontesMonitoradas(res.data);
    } catch (e) { console.error('Erro ao buscar fontes:', e); }
    finally { setLoadingFontes(false); }
  };

  useEffect(() => { fetchFontes(); }, []);

  const handleScraping = async () => {
    if (!scrapingUrl.trim()) {
      toast.error('Cole uma URL válida');
      return;
    }
    setLoadingScraping(true);
    setScrapingResultado(null);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/scraping/buscar`, {
        url: scrapingUrl,
        usar_playwright: false,
        cadastrar_automaticamente: false
      }, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 120000
      });
      setScrapingResultado(response.data);
      if (response.data.success && response.data.total_encontradas > 0) {
        const novas = response.data.novas || 0;
        const dups = response.data.duplicatas || 0;
        if (novas > 0) {
          toast.success(`${novas} corridas novas encontradas! (${dups} duplicatas). Exporte o Excel e importe via "Importar Dados".`);
        } else {
          toast.info(`${response.data.total_encontradas} corridas encontradas, mas todas já existem no banco.`);
        }
      } else {
        toast.warning(response.data.mensagem || 'Nenhuma corrida encontrada');
      }
    } catch (error) {
      console.error('Scraping error:', error);
      toast.error(error.response?.data?.detail || 'Erro ao fazer varredura. Tente novamente.');
    } finally {
      setLoadingScraping(false);
    }
  };

  const handleSalvarFonte = async () => {
    if (!scrapingUrl.trim()) return;
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/scraping/fontes`, {
        url: scrapingUrl,
        nome: '',
        ativa: true
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Fonte salva para monitoramento automático!');
      fetchFontes();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Erro ao salvar fonte');
    }
  };

  const handleRemoverFonte = async (fonteId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/scraping/fontes/${fonteId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Fonte removida');
      fetchFontes();
    } catch (e) {
      toast.error('Erro ao remover fonte');
    }
  };

  const handleAtualizarTodas = async () => {
    setLoadingAtualizarTodas(true);
    try {
      downloadFile('/api/scraping/atualizar-todas');
      toast.success('Varredura iniciada! O arquivo Excel será baixado automaticamente.');
      fetchFontes();
    } catch (e) {
      toast.error('Erro na atualização geral');
    } finally {
      setLoadingAtualizarTodas(false);
    }
  };

  const handleExportarScraping = async (formato) => {
    try {
      // Usar os dados já em memória do scraping
      const corridas = scrapingResultado?.corridas_novas || scrapingResultado?.corridas || [];
      if (corridas.length === 0) {
        toast.error('Nenhuma corrida para exportar');
        return;
      }
      
      // Gerar CSV no frontend e enviar para download via backend
      const header = ['Nome da Corrida', 'Organizador', 'Cidade', 'Estado', 'Link da Página', 'Data do Evento', 'Status'];
      const rows = corridas.map(c => [
        c.nome_corrida || '',
        c.organizador || '',
        c.cidade || '',
        c.estado || '',
        c.pagina_link || '',
        c.data_corrida || '',
        c.status || 'ativa'
      ].join(';'));
      
      const csvContent = '\ufeff' + [header.join(';'), ...rows].join('\n');
      downloadCSVContent(csvContent, formato === 'excel' ? 'corridas_scraping.csv' : 'corridas_scraping.csv');
      
      toast.success(`Arquivo exportado com sucesso!`);
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
      downloadFile(`/api/corridas-eventos/template`, { formato });
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
    const paginadas = corridasFiltradas.slice(
      (paginaAtual - 1) * itensPorPagina,
      paginaAtual * itensPorPagina
    );
    const idsPage = paginadas.map(c => c.id);
    const allSelected = idsPage.every(id => selectedCorridas.includes(id));
    if (allSelected) {
      setSelectedCorridas(prev => prev.filter(id => !idsPage.includes(id)));
    } else {
      setSelectedCorridas(prev => [...new Set([...prev, ...idsPage])]);
    }
  };

  const handleExcluirLote = async () => {
    if (selectedCorridas.length === 0) {
      toast.error('Selecione ao menos uma corrida');
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

    // Filtrar por status
    if (filtroStatus) {
      resultado = resultado.filter(c => c.status === filtroStatus);
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
    setFiltroStatus('');
    setFiltroPeriodo('');
    setDataInicio('');
    setDataFim('');
    setOrdenacao('');
    setSelectedCorridas([]);
  };

  const corridasFiltradas = getCorridasFiltradas();

  // Paginação frontend
  const [paginaAtual, setPaginaAtual] = useState(1);
  const itensPorPagina = 50;
  const totalPaginas = Math.ceil(corridasFiltradas.length / itensPorPagina);
  const corridasPaginadas = corridasFiltradas.slice(
    (paginaAtual - 1) * itensPorPagina,
    paginaAtual * itensPorPagina
  );

  // ==================== EXPORTAÇÃO DE DADOS ====================

  const exportarDados = (tipoExport) => {
    // Usar o novo endpoint backend com filtros
    const params = {};
    if (filtroEstado) params.estado = filtroEstado;
    if (filtroCidade) params.cidade = filtroCidade;
    if (filtroStatus) params.status_corrida = filtroStatus;
    params.ordenar_por = tipoExport === 'estado' ? 'estado' : 'data';
    
    downloadFile('/api/corridas-eventos/exportar/csv', params);
    toast.success(`Exportando ${corridasFiltradas.length} corridas...`);
  };

  // Dados para gráficos do relatório
  const getReportData = () => {
    const dados = corridasFiltradas;
    
    // Distribuição por estado
    const porEstado = {};
    dados.forEach(c => {
      const estado = c.estado || 'N/A';
      porEstado[estado] = (porEstado[estado] || 0) + 1;
    });
    const distribuicaoEstado = Object.entries(porEstado)
      .map(([estado, total]) => ({ estado, total }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 10);

    // Distribuição por status
    const porStatus = { ativa: 0, encerrada: 0, cancelada: 0 };
    dados.forEach(c => {
      const status = c.status || 'ativa';
      porStatus[status] = (porStatus[status] || 0) + 1;
    });
    const distribuicaoStatus = [
      { name: 'Ativas', value: porStatus.ativa, fill: '#10B981' },
      { name: 'Encerradas', value: porStatus.encerrada, fill: '#F59E0B' },
      { name: 'Canceladas', value: porStatus.cancelada, fill: '#EF4444' }
    ].filter(s => s.value > 0);

    // Evolução mensal (últimos 12 meses)
    const evolucaoMensal = {};
    dados.forEach(c => {
      if (c.data_corrida) {
        const mes = c.data_corrida.substring(0, 7); // YYYY-MM
        evolucaoMensal[mes] = (evolucaoMensal[mes] || 0) + 1;
      }
    });
    const evolucao = Object.entries(evolucaoMensal)
      .map(([mes, total]) => ({ mes: mes.split('-').reverse().join('/'), total }))
      .sort((a, b) => a.mes.localeCompare(b.mes))
      .slice(-12);

    // Média de avaliações
    const avaliacoes = dados.filter(c => c.media_nota);
    const mediaGeral = avaliacoes.length > 0 
      ? (avaliacoes.reduce((acc, c) => acc + (c.media_nota || 0), 0) / avaliacoes.length).toFixed(1)
      : '0.0';

    return {
      total: dados.length,
      distribuicaoEstado,
      distribuicaoStatus,
      evolucao,
      mediaGeral,
      totalAvaliacoes: dados.reduce((acc, c) => acc + (c.total_avaliacoes || 0), 0)
    };
  };

  // Gerar PDF do relatório
  const gerarRelatorioPDF = async () => {
    setGeneratingPDF(true);
    toast.info('Gerando relatório PDF...');

    try {
      await new Promise(resolve => setTimeout(resolve, 500)); // Aguardar renderização

      const element = reportRef.current;
      if (!element) {
        toast.error('Erro ao gerar relatório');
        return;
      }

      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
      const imgX = (pdfWidth - imgWidth * ratio) / 2;
      const imgY = 10;

      pdf.addImage(imgData, 'PNG', imgX, imgY, imgWidth * ratio, imgHeight * ratio);
      pdf.save(`relatorio_corridas_${new Date().toISOString().slice(0,10)}.pdf`);

      toast.success('Relatório PDF gerado com sucesso!');
      setShowReportModal(false);
    } catch (error) {
      console.error('Erro ao gerar PDF:', error);
      toast.error('Erro ao gerar relatório PDF');
    } finally {
      setGeneratingPDF(false);
    }
  };

  const reportData = getReportData();

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

      {/* ==================== CORRIDAS PENDENTES DE APROVAÇÃO ==================== */}
      {corridasPendentes.length > 0 && (
        <Card className="border-amber-300 bg-amber-50/50 dark:bg-amber-900/10" data-testid="corridas-pendentes-section">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-amber-700">
                <AlertCircle className="w-5 h-5" />
                Corridas Pendentes de Aprovação
                <Badge className="bg-amber-500 text-white ml-2">{corridasPendentes.length}</Badge>
              </div>
              <Button variant="ghost" size="sm" onClick={fetchCorridasPendentes} disabled={loadingPendentes}>
                <RefreshCw className={`w-4 h-4 ${loadingPendentes ? 'animate-spin' : ''}`} />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {corridasPendentes.map(corrida => (
                <div key={corrida.id} className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-amber-200 flex flex-col md:flex-row md:items-center justify-between gap-3" data-testid={`corrida-pendente-${corrida.id}`}>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="font-semibold text-slate-800 dark:text-white">{corrida.nome_corrida}</h4>
                      <Badge variant="outline" className={corrida.status === 'ativa' ? 'border-green-400 text-green-600' : 'border-slate-400 text-slate-600'}>
                        {corrida.status === 'ativa' ? 'Ativa' : 'Encerrada'}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-sm text-slate-500">
                      <span className="flex items-center gap-1"><User className="w-3 h-3" />{corrida.criado_por_nome || 'Desconhecido'} ({corrida.criado_por_role === 'dono_assessoria' ? 'Assessoria' : 'Atleta'})</span>
                      <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{corrida.cidade}/{corrida.estado}</span>
                      <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{corrida.data_corrida}</span>
                      {corrida.organizador && <span>Org: {corrida.organizador}</span>}
                      {corrida.pagina_link && (
                        <a href={corrida.pagina_link} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline flex items-center gap-1">
                          <ExternalLink className="w-3 h-3" />Link
                        </a>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <Button
                      size="sm"
                      className="bg-green-500 hover:bg-green-600 text-white"
                      disabled={!!loadingAprovacao[corrida.id]}
                      onClick={() => handleAprovarCorrida(corrida.id)}
                      data-testid={`aprovar-corrida-${corrida.id}`}
                    >
                      {loadingAprovacao[corrida.id] === 'aprovando' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4 mr-1" />}
                      Aprovar
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      disabled={!!loadingAprovacao[corrida.id]}
                      onClick={() => { setCorridaRejeitar(corrida); setShowRejeicaoModal(true); }}
                      data-testid={`rejeitar-corrida-${corrida.id}`}
                    >
                      {loadingAprovacao[corrida.id] === 'rejeitando' ? <Loader2 className="w-4 h-4 animate-spin" /> : <XCircle className="w-4 h-4 mr-1" />}
                      Rejeitar
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modal de Rejeição */}
      <Dialog open={showRejeicaoModal} onOpenChange={setShowRejeicaoModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <XCircle className="w-5 h-5" />
              Rejeitar Corrida
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-slate-600">
              Corrida: <strong>{corridaRejeitar?.nome_corrida}</strong>
            </p>
            <div>
              <Label>Motivo da Rejeição (opcional)</Label>
              <Input
                value={motivoRejeicao}
                onChange={(e) => setMotivoRejeicao(e.target.value)}
                placeholder="Ex: Corrida duplicada, dados incorretos..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowRejeicaoModal(false); setMotivoRejeicao(''); setCorridaRejeitar(null); }}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleRejeitarCorrida} disabled={!!loadingAprovacao[corridaRejeitar?.id]}>
              {loadingAprovacao[corridaRejeitar?.id] === 'rejeitando' ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <XCircle className="w-4 h-4 mr-2" />}
              Confirmar Rejeição
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
          
          {/* Barra de Scraping Avançado */}
          <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-purple-600" />
                <span className="font-semibold text-purple-700 dark:text-purple-300">Busca e Varredura Manual de Corridas</span>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFontes(!showFontes)}
                  className="border-purple-400 text-purple-600 hover:bg-purple-50 text-xs"
                  data-testid="btn-toggle-fontes"
                >
                  <Bookmark className="w-3 h-3 mr-1" />
                  Fontes ({fontesMonitoradas.length})
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAtualizarTodas}
                  disabled={loadingAtualizarTodas || fontesMonitoradas.length === 0}
                  className="border-green-500 text-green-600 hover:bg-green-50 text-xs"
                  data-testid="btn-atualizar-todas"
                >
                  {loadingAtualizarTodas ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <RefreshCw className="w-3 h-3 mr-1" />}
                  Atualizar e Baixar Excel
                </Button>
              </div>
            </div>
            
            {/* Search bar */}
            <div className="flex gap-2">
              <Input
                placeholder="Cole a URL do site de corridas (Ticket Sports, Sympla, Central das Inscrições, etc.)"
                value={scrapingUrl}
                onChange={(e) => setScrapingUrl(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleScraping()}
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
              <Button
                variant="outline"
                onClick={handleSalvarFonte}
                disabled={!scrapingUrl.trim()}
                className="border-orange-400 text-orange-600 hover:bg-orange-50"
                title="Salvar URL para monitoramento automático (12h)"
                data-testid="btn-salvar-fonte"
              >
                <Bookmark className="w-4 h-4" />
              </Button>
            </div>

            {/* Fontes Monitoradas (collapsible) */}
            {showFontes && (
              <div className="mt-3 p-3 bg-white dark:bg-slate-800 rounded-lg border max-h-48 overflow-y-auto">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    Fontes Salvas
                  </span>
                </div>
                {fontesMonitoradas.length === 0 ? (
                  <p className="text-sm text-slate-400">Nenhuma fonte salva. Cole uma URL e clique no ícone de marcador.</p>
                ) : (
                  <div className="space-y-1">
                    {fontesMonitoradas.map(f => (
                      <div key={f.id} className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-700/50 rounded text-xs group hover:bg-slate-100 dark:hover:bg-slate-700">
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          <Link2 className="w-3 h-3 text-purple-500 flex-shrink-0" />
                          <span 
                            className="truncate text-slate-700 dark:text-slate-300 cursor-pointer hover:text-purple-600"
                            onClick={() => { setScrapingUrl(f.url); }}
                            title={f.url}
                          >
                            {f.nome || f.url}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                          {f.ultima_varredura && (
                            <span className="text-[10px] text-slate-400">
                              {new Date(f.ultima_varredura).toLocaleDateString('pt-BR')} - {f.total_novas_ultima || 0} novas
                            </span>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100"
                            onClick={() => handleRemoverFonte(f.id)}
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* Resultado do Scraping inline */}
            {scrapingResultado && (
              <div className="mt-4 p-4 bg-white dark:bg-slate-800 rounded-lg border">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Fonte: {scrapingResultado.fonte} | Método: {scrapingResultado.metodo || 'auto'}
                    </p>
                    <p className={`font-semibold ${scrapingResultado.total_encontradas > 0 ? 'text-green-600' : 'text-amber-600'}`}>
                      {scrapingResultado.total_encontradas > 0 
                        ? `${scrapingResultado.total_encontradas} corridas encontradas`
                        : 'Nenhuma corrida encontrada neste site'}
                    </p>
                    {scrapingResultado.total_encontradas > 0 && (
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-xs flex items-center gap-1 text-green-600">
                          <ShieldCheck className="w-3 h-3" />
                          {scrapingResultado.novas || 0} novas
                        </span>
                        <span className="text-xs flex items-center gap-1 text-orange-500">
                          <AlertOctagon className="w-3 h-3" />
                          {scrapingResultado.duplicatas || 0} já existentes
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {scrapingResultado.total_encontradas > 0 && (
                      <>
                        <Button variant="outline" size="sm" onClick={() => handleExportarScraping('csv')} className="border-green-500 text-green-600 hover:bg-green-50">
                          <Download className="w-4 h-4 mr-1" /> CSV
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleExportarScraping('excel')} className="border-blue-500 text-blue-600 hover:bg-blue-50">
                          <FileSpreadsheet className="w-4 h-4 mr-1" /> Excel
                        </Button>
                      </>
                    )}
                  </div>
                </div>
                
                {/* Preview table */}
                {scrapingResultado.total_encontradas > 0 && (
                  <div className="border rounded-lg overflow-hidden max-h-60 overflow-y-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-100 dark:bg-slate-700 sticky top-0">
                        <tr>
                          <th className="text-left p-2 font-semibold text-xs">Status</th>
                          <th className="text-left p-2 font-semibold text-xs">Nome</th>
                          <th className="text-left p-2 font-semibold text-xs">Organizador</th>
                          <th className="text-left p-2 font-semibold text-xs">Cidade/UF</th>
                          <th className="text-left p-2 font-semibold text-xs">Data</th>
                          <th className="text-left p-2 font-semibold text-xs">Situação</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(scrapingResultado.corridas_novas || scrapingResultado.corridas || []).slice(0, 15).map((corrida, idx) => (
                          <tr key={idx} className="border-t hover:bg-slate-50 dark:hover:bg-slate-800/50 text-xs">
                            <td className="p-2">
                              <Badge className="bg-green-100 text-green-700 text-[10px]">Nova</Badge>
                            </td>
                            <td className="p-2 max-w-[200px] truncate">{corrida.nome_corrida}</td>
                            <td className="p-2 text-slate-500">{corrida.organizador || '-'}</td>
                            <td className="p-2">{[corrida.cidade, corrida.estado].filter(Boolean).join('/') || '-'}</td>
                            <td className="p-2">{corrida.data_corrida || '-'}</td>
                            <td className="p-2">
                              <Badge className={corrida.status === 'ativa' ? 'bg-blue-100 text-blue-700 text-[10px]' : 'bg-gray-100 text-gray-600 text-[10px]'}>
                                {corrida.status || 'ativa'}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                        {(scrapingResultado.corridas_duplicatas || []).slice(0, 5).map((corrida, idx) => (
                          <tr key={`dup-${idx}`} className="border-t bg-orange-50/50 dark:bg-orange-900/10 text-xs opacity-60">
                            <td className="p-2">
                              <Badge className="bg-orange-100 text-orange-700 text-[10px]">Duplicata</Badge>
                            </td>
                            <td className="p-2 max-w-[200px] truncate">{corrida.nome_corrida}</td>
                            <td className="p-2 text-slate-500">{corrida.organizador || '-'}</td>
                            <td className="p-2">{[corrida.cidade, corrida.estado].filter(Boolean).join('/') || '-'}</td>
                            <td className="p-2">{corrida.data_corrida || '-'}</td>
                            <td className="p-2">
                              <Badge className="bg-gray-100 text-gray-600 text-[10px]">já existe</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {(scrapingResultado.total_encontradas) > 15 && (
                      <div className="p-2 bg-slate-50 text-center text-xs text-slate-500">
                        + {scrapingResultado.total_encontradas - 15} corridas no total
                      </div>
                    )}
                  </div>
                )}
                
                {scrapingResultado.total_encontradas === 0 && (
                  <div className="mt-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-sm">
                    <p className="font-semibold text-amber-700 mb-1">Dica:</p>
                    <p className="text-amber-600 text-xs">
                      O sistema tentará automaticamente o modo Playwright (navegador headless) para sites com JavaScript.
                      Se persistir sem resultados, o site pode ter proteção anti-bot avançada. Use a importação manual.
                    </p>
                  </div>
                )}
              </div>
            )}
            
            <p className="text-xs text-purple-600 dark:text-purple-400 mt-2">
              <AlertCircle className="w-3 h-3 inline mr-1" />
              Varredura manual: busque corridas, exporte o Excel e importe via "Importar Dados". Anti-duplicidade ativa.
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
                    <CidadeCombobox
                      cidades={cidadesFiltro}
                      value={filtroCidade || "__all__"}
                      onValueChange={(v) => setFiltroCidade(v === "__all__" ? "" : v)}
                      disabled={!filtroEstado}
                      placeholder={filtroEstado ? "Cidade" : "Selecione UF"}
                      allOption={{ value: "__all__", label: "Todas" }}
                      triggerClassName="w-[180px]"
                    />
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

                  {/* Filtro por Status */}
                  <div className="flex items-center gap-2">
                    <Select value={filtroStatus || "__all__"} onValueChange={(v) => setFiltroStatus(v === "__all__" ? "" : v)}>
                      <SelectTrigger className="w-[130px]">
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__all__">Todos Status</SelectItem>
                        <SelectItem value="ativa">
                          <span className="flex items-center gap-2">
                            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                            Ativas
                          </span>
                        </SelectItem>
                        <SelectItem value="encerrada">
                          <span className="flex items-center gap-2">
                            <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                            Encerradas
                          </span>
                        </SelectItem>
                        <SelectItem value="cancelada">
                          <span className="flex items-center gap-2">
                            <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                            Canceladas
                          </span>
                        </SelectItem>
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
                  {(filtroEstado || filtroCidade || filtroPeriodo || filtroStatus || ordenacao) && (
                    <Button variant="ghost" size="sm" onClick={limparFiltros}>
                      <X className="w-4 h-4 mr-1" />
                      Limpar
                    </Button>
                  )}

                  {/* Contador de selecionados e botão excluir */}
                  <div className="flex-1 flex justify-end items-center gap-3">
                    {/* Botão de Exportar CSV */}
                    <Select onValueChange={(v) => exportarDados(v)}>
                      <SelectTrigger className="w-[160px]" data-testid="btn-exportar-corridas">
                        <Download className="w-4 h-4 mr-2" />
                        <SelectValue placeholder="Exportar CSV" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="estado">Por Estado</SelectItem>
                        <SelectItem value="data">Por Data</SelectItem>
                      </SelectContent>
                    </Select>

                    {/* Botão de Relatório PDF */}
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => setShowReportModal(true)}
                      data-testid="btn-relatorio-pdf-corridas"
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      Relatório PDF
                    </Button>

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
                  Mostrando {(paginaAtual - 1) * itensPorPagina + 1}-{Math.min(paginaAtual * itensPorPagina, corridasFiltradas.length)} de {corridasFiltradas.length} corridas (total: {corridasEventos.length})
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
                    {corridasPaginadas.map((corrida) => (
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

              {/* Paginação */}
              {totalPaginas > 1 && (
                <div className="flex items-center justify-between mt-4 px-2">
                  <span className="text-sm text-slate-500">
                    Página {paginaAtual} de {totalPaginas}
                  </span>
                  <div className="flex gap-1">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={paginaAtual === 1}
                      onClick={() => setPaginaAtual(1)}
                      className="text-xs h-8"
                    >
                      Primeira
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={paginaAtual === 1}
                      onClick={() => setPaginaAtual(p => Math.max(1, p - 1))}
                      className="text-xs h-8"
                    >
                      Anterior
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={paginaAtual === totalPaginas}
                      onClick={() => setPaginaAtual(p => Math.min(totalPaginas, p + 1))}
                      className="text-xs h-8"
                    >
                      Próxima
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={paginaAtual === totalPaginas}
                      onClick={() => setPaginaAtual(totalPaginas)}
                      className="text-xs h-8"
                    >
                      Última
                    </Button>
                  </div>
                </div>
              )}
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
                <CidadeCombobox
                  cidades={cidadesIBGE}
                  value={corridaFormData.cidade}
                  onValueChange={(v) => setCorridaFormData({...corridaFormData, cidade: v})}
                  loading={loadingCidadesIBGE}
                  disabled={!corridaFormData.estado}
                />
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

      {/* Modal de Relatório Visual */}
      <Dialog open={showReportModal} onOpenChange={setShowReportModal}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-emerald-500" />
              Relatório Visual - Corridas
            </DialogTitle>
          </DialogHeader>

          <div ref={reportRef} className="bg-white p-6 space-y-6">
            {/* Cabeçalho do Relatório */}
            <div className="text-center border-b pb-4">
              <h1 className="text-2xl font-bold text-slate-800">Ranking Run Pró</h1>
              <h2 className="text-lg text-slate-600">Relatório de Corridas e Eventos</h2>
              <p className="text-sm text-slate-500">
                Gerado em {new Date().toLocaleDateString('pt-BR')} às {new Date().toLocaleTimeString('pt-BR')}
              </p>
            </div>

            {/* Cards de Resumo */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-emerald-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-emerald-600">{reportData.total}</div>
                <div className="text-sm text-slate-600">Total de Corridas</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-blue-600">{reportData.distribuicaoStatus.find(s => s.name === 'Ativas')?.value || 0}</div>
                <div className="text-sm text-slate-600">Corridas Ativas</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-amber-600">{reportData.mediaGeral}</div>
                <div className="text-sm text-slate-600">Média de Avaliação</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-purple-600">{reportData.totalAvaliacoes}</div>
                <div className="text-sm text-slate-600">Total de Avaliações</div>
              </div>
            </div>

            {/* Gráficos */}
            <div className="grid grid-cols-2 gap-6">
              {/* Distribuição por Estado */}
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold text-slate-700 mb-3">Top 10 Estados</h3>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={reportData.distribuicaoEstado} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="estado" type="category" width={40} tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Bar dataKey="total" fill="#10B981" radius={[0, 4, 4, 0]} name="Corridas" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Distribuição por Status */}
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold text-slate-700 mb-3">Status das Corridas</h3>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={reportData.distribuicaoStatus}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={70}
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}`}
                      >
                        {reportData.distribuicaoStatus.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Evolução Temporal */}
            {reportData.evolucao.length > 0 && (
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold text-slate-700 mb-3">Evolução Mensal de Corridas</h3>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={reportData.evolucao}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="mes" tick={{ fontSize: 10 }} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="total" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Corridas" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Tabela Resumida */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-slate-700 mb-3">Resumo por Estado</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-slate-50">
                    <th className="text-left py-2 px-3">Estado</th>
                    <th className="text-center py-2 px-3">Corridas</th>
                    <th className="text-center py-2 px-3">% do Total</th>
                  </tr>
                </thead>
                <tbody>
                  {reportData.distribuicaoEstado.slice(0, 8).map((item, idx) => (
                    <tr key={idx} className="border-b">
                      <td className="py-2 px-3">{item.estado}</td>
                      <td className="text-center py-2 px-3">{item.total}</td>
                      <td className="text-center py-2 px-3">
                        {((item.total / reportData.total) * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Rodapé */}
            <div className="text-center text-xs text-slate-400 pt-4 border-t">
              Ranking Run Pró - Sistema de Gestão de Corridas
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReportModal(false)}>
              Fechar
            </Button>
            <Button 
              onClick={gerarRelatorioPDF} 
              disabled={generatingPDF}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              {generatingPDF ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Download className="w-4 h-4 mr-2" />
              )}
              {generatingPDF ? 'Gerando...' : 'Baixar PDF'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardCorridas;
