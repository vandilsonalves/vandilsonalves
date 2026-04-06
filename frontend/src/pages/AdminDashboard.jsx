import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Trophy, Users, AlertCircle, BarChart3, Shield,
  Activity, Home, Settings, FileText,
  Download, Plus,
  Cake, Send, Loader2,
  Crown, MessageSquare, CreditCard, TrendingDown
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

import { downloadFile } from '@/utils/downloadHelper';
import { Instagram, Star, HardDrive, Handshake } from 'lucide-react';

// Componentes extraídos
import AdminSidebar from './admin/AdminSidebar';
import AdminModals from './admin/AdminModals';

// Dashboards modulares
import { 
  DashboardGeral, 
  DashboardAtletas, 
  DashboardAssessorias, 
  DashboardCorridas, 
  DashboardResultados,
  DashboardRBAC,
  DashboardSubmeter,
  DashboardRegulamento,
  DashboardAutorizacoes,
  DashboardAniversariantes,
  DashboardInstagram
} from './admin';
import DashboardMonitoramento from './admin/dashboards/DashboardMonitoramento';
import DashboardMensagens from './admin/DashboardMensagens';
import DashboardResumoSemanal from './admin/DashboardResumoSemanal';
import DashboardEngajamento from './admin/DashboardEngajamento';
import DashboardFinanceiro from './admin/DashboardFinanceiro';
import DashboardRetencao from './admin/DashboardRetencao';
import DashboardBackup from './admin/DashboardBackup';
import DashboardCorridasParceiras from './admin/DashboardCorridasParceiras';
import ConfiguracoesSistemaTab from '@/components/admin/ConfiguracoesSistemaTab';
import useCidadesIBGE from '@/hooks/useCidadesIBGE';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Definição dos itens do menu organizados em seções
const menuSections = [
  {
    title: null,
    items: [
      { id: 'dashboard', label: 'Dashboard Geral', icon: Home, permissoes: [] },
      { id: 'estrategico', label: 'Dashboard Estratégico', icon: BarChart3, permissoes: [], superAdminOnly: true },
    ]
  },
  {
    title: 'Gestão',
    items: [
      { id: 'atletas', label: 'Atletas', icon: Users, permissoes: ['visualizar_atletas'] },
      { id: 'assessorias', label: 'Assessorias', icon: Trophy, permissoes: ['visualizar_assessorias'] },
      { id: 'ranking-corridas', label: 'Corridas', icon: Star, permissoes: ['aprovar_corridas'] },
      { id: 'corridas-parceiras', label: 'Corridas Parceiras', icon: Handshake, permissoes: [] },
      { id: 'pendentes', label: 'Aprovações', icon: AlertCircle, permissoes: ['aprovar_corridas', 'aprovar_resultados'] },
      { id: 'financeiro', label: 'Financeiro', icon: CreditCard, permissoes: [] },
      { id: 'mensagens', label: 'Mensagens', icon: MessageSquare, permissoes: [] },
      { id: 'engajamento', label: 'Engajamento', icon: BarChart3, permissoes: [] },
      { id: 'retencao', label: 'Retenção', icon: TrendingDown, permissoes: [] },
    ]
  },
  {
    title: 'Sistema',
    superAdminOnly: true,
    items: [
      { id: 'configuracoes', label: 'Configurações', icon: Settings, permissoes: ['configuracoes_sistema'], superAdminOnly: true },
      { id: 'autorizacoes', label: 'Autorizações', icon: Shield, permissoes: ['configuracoes_sistema'], superAdminOnly: true },
      { id: 'administradores', label: 'Administradores', icon: Crown, permissoes: ['criar_admins'], superAdminOnly: true },
      { id: 'regulamento', label: 'Regulamento', icon: FileText, permissoes: ['configuracoes_sistema'], superAdminOnly: true },
      { id: 'backup', label: 'Backup', icon: HardDrive, permissoes: ['configuracoes_sistema'], superAdminOnly: true },
    ]
  },
  {
    title: 'Ferramentas',
    items: [
      { id: 'submeter', label: 'Submeter Resultado', icon: Plus, permissoes: ['aprovar_resultados'] },
      { id: 'resumo-semanal', label: 'Resumo Semanal', icon: Send, permissoes: [] },
      { id: 'ranking', label: 'Exportar Ranking', icon: FileText, permissoes: ['exportar_dados'], superAdminOnly: true },
      { id: 'aniversariantes', label: 'Aniversariantes', icon: Cake, permissoes: [] },
    ]
  },
  {
    title: 'Avançado',
    superAdminOnly: true,
    items: [
      { id: 'monitoramento', label: 'Monitoramento', icon: Activity, permissoes: ['configuracoes_sistema'], superAdminOnly: true },
      { id: 'instagram', label: 'Ranking Run Inside', icon: Instagram, permissoes: [], superAdminOnly: true },
    ]
  }
];

const allMenuItems = menuSections.flatMap(section => section.items);

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, token, loading, isAdmin, tipoAdmin, isSuperAdmin, adminPermissoes } = useAuth();
  const [activeMenu, setActiveMenu] = useState('dashboard');
  
  // Stats
  const [stats, setStats] = useState(null);
  const [statsEstados, setStatsEstados] = useState([]);
  const [statsCategorias, setStatsCategorias] = useState(null);
  const [statsFaixa, setStatsFaixa] = useState([]);
  const [corridasPorMes, setCorridasPorMes] = useState([]);
  const [loadingStats, setLoadingStats] = useState(true);
  const [statsEquipes, setStatsEquipes] = useState([]);
  const [statsPovao, setStatsPovao] = useState(null);
  const [statsModalidade, setStatsModalidade] = useState({ profissional: 0, povao: 0 });
  const [statsDonosPorEstado, setStatsDonosPorEstado] = useState([]);
  const [statsAssessoriasVerificadas, setStatsAssessoriasVerificadas] = useState(null);
  const [statsInsignias, setStatsInsignias] = useState([]);
  
  // Pendentes
  const [pendentes, setPendentes] = useState([]);
  const [loadingPendentes, setLoadingPendentes] = useState(true);
  
  // Atletas
  const [atletas, setAtletas] = useState([]);
  const [loadingAtletas, setLoadingAtletas] = useState(false);
  const [filtroCategoria, setFiltroCategoria] = useState('all');
  const [filtroModalidade, setFiltroModalidade] = useState('all');
  const [filtroEquipe, setFiltroEquipe] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAtletaModal, setShowAtletaModal] = useState(false);
  const [atletaEditando, setAtletaEditando] = useState(null);
  const [showAddAtletaModal, setShowAddAtletaModal] = useState(false);
  
  // Transferência de Modalidade
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [atletaTransferindo, setAtletaTransferindo] = useState(null);
  const [transferLoading, setTransferLoading] = useState(false);

  // Ações gerais
  const [actionLoading, setActionLoading] = useState(false);

  // Form para novo atleta
  const [novoAtleta, setNovoAtleta] = useState({
    nome: '', email: '', password: 'atleta123', equipe: '',
    cidade: '', estado: 'SP', genero: 'M', categoria: 'normal',
    data_nascimento: '', telefone: '', tipo_corredor: '', terreno_preferido: '',
    modalidade_usuario: 'profissional_amador'
  });

  // Cidades via IBGE para modais de atleta
  const { cidades: cidadesNovoAtleta, loading: loadingCidadesNovo } = useCidadesIBGE(novoAtleta.estado);
  const { cidades: cidadesEditAtleta, loading: loadingCidadesEdit } = useCidadesIBGE(atletaEditando?.estado);

  // Liga de Assessorias
  const [ligaRanking, setLigaRanking] = useState([]);
  const [ligaStats, setLigaStats] = useState(null);
  const [ligaTipo, setLigaTipo] = useState('nacional');
  const [ligaEstado, setLigaEstado] = useState('');
  const [ligaCidade, setLigaCidade] = useState('');
  const [loadingLiga, setLoadingLiga] = useState(false);
  const [estadosComAssessorias, setEstadosComAssessorias] = useState([]);
  const [cidadesComAssessorias, setCidadesComAssessorias] = useState([]);

  // Promover Dono de Assessoria
  const [showPromoverModal, setShowPromoverModal] = useState(false);
  const [atletaPromover, setAtletaPromover] = useState(null);
  const [promoverLoading, setPromoverLoading] = useState(false);

  // Enviar Mensagem Individual
  const [showMensagemModal, setShowMensagemModal] = useState(false);
  const [mensagemAdmin, setMensagemAdmin] = useState('');
  const [sendingMensagem, setSendingMensagem] = useState(false);
  const [atletaAcao, setAtletaAcao] = useState(null);

  // Foto modal
  const [showFotoModal, setShowFotoModal] = useState(false);
  const [fotoModalUrl, setFotoModalUrl] = useState('');

  // Dashboard Ranking das Corridas
  const [rankingCorridasDashboard, setRankingCorridasDashboard] = useState(null);
  const [loadingRankingCorridas, setLoadingRankingCorridas] = useState(false);
  const [corridasEventos, setCorridasEventos] = useState([]);
  const [showCorridaModal, setShowCorridaModal] = useState(false);
  const [corridaEditando, setCorridaEditando] = useState(null);
  const [corridaFormData, setCorridaFormData] = useState({
    nome_corrida: '', organizador: '', cidade: '', estado: '',
    data_corrida: '', pagina_link: '', status: 'ativa'
  });

  // ==================== EFFECTS ====================

  useEffect(() => {
    if (loading) return;
    if (!token || !isAdmin) { navigate('/'); return; }
    
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
    fetchStats();
    fetchPendentes();
  }, [isAdmin, token, loading, navigate]);

  useEffect(() => {
    if (activeMenu === 'atletas') fetchAtletas();
    if (activeMenu === 'assessorias') { fetchLigaRanking(); fetchLigaStats(); fetchEstadosComAssessorias(); }
    if (activeMenu === 'ranking-corridas') { fetchRankingCorridasDashboard(); fetchCorridasEventos(); }
    if (activeMenu === 'geral' && !statsCategorias) { fetchExtraStats(); fetchEquipesStats(); }
  }, [activeMenu, filtroCategoria, filtroEquipe, ligaTipo, ligaEstado, ligaCidade]);

  // ==================== FETCHERS ====================

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      const results = await Promise.allSettled([
        axios.get(`${API}/admin/stats`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/estados`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/ranking/povao/stats`)
      ]);
      const [statsRes, estadosRes, povaoRes] = results;
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (estadosRes.status === 'fulfilled') setStatsEstados(estadosRes.value.data);
      if (povaoRes.status === 'fulfilled') setStatsPovao(povaoRes.value.data);
    } catch (err) {
      console.error('Erro ao buscar stats:', err);
    } finally {
      setLoadingStats(false);
    }
  };

  const fetchExtraStats = async () => {
    try {
      const results = await Promise.allSettled([
        axios.get(`${API}/admin/stats/categorias`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/faixa-etaria`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/corridas-por-mes`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/donos-por-estado`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/assessorias-verificadas`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/insignias`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      const [categoriasRes, faixaRes, corridasRes, donosEstadoRes, assessoriasVerificadasRes, insigniasRes] = results;
      if (categoriasRes.status === 'fulfilled') setStatsCategorias(categoriasRes.value.data);
      if (faixaRes.status === 'fulfilled') setStatsFaixa(faixaRes.value.data);
      if (corridasRes.status === 'fulfilled') setCorridasPorMes(corridasRes.value.data);
      if (donosEstadoRes.status === 'fulfilled') setStatsDonosPorEstado(donosEstadoRes.value.data);
      if (assessoriasVerificadasRes.status === 'fulfilled') setStatsAssessoriasVerificadas(assessoriasVerificadasRes.value.data);
      if (insigniasRes.status === 'fulfilled') setStatsInsignias(insigniasRes.value.data);
    } catch (error) {
      console.error('Erro ao buscar stats extras:', error);
    }
  };

  const fetchPendentes = async () => {
    setLoadingPendentes(true);
    try {
      const response = await axios.get(`${API}/admin/pendentes`, { headers: { Authorization: `Bearer ${token}` } });
      setPendentes(response.data);
    } catch (error) {
      console.error('Erro ao buscar pendentes:', error);
    } finally {
      setLoadingPendentes(false);
    }
  };

  const fetchEquipesStats = async () => {
    try {
      const atletasRes = await axios.get(`${API}/admin/atletas?limit=1000`, { headers: { Authorization: `Bearer ${token}` } });
      const raw = atletasRes.data;
      const atletasList = Array.isArray(raw) ? raw : Array.isArray(raw?.atletas) ? raw.atletas : [];
      const equipesCount = {};
      let profissionalCount = 0;
      let povaoCount = 0;
      atletasList.forEach(a => {
        const equipe = a.equipe || 'Sem equipe';
        equipesCount[equipe] = (equipesCount[equipe] || 0) + 1;
        if (a.modalidade_usuario === 'povao_pace_livre') { povaoCount++; } else { profissionalCount++; }
      });
      setStatsEquipes(Object.entries(equipesCount).map(([equipe, total]) => ({ equipe, total })).sort((a, b) => b.total - a.total).slice(0, 10));
      setStatsModalidade({ profissional: profissionalCount, povao: povaoCount });
    } catch (err) {
      console.error('Erro ao processar equipes:', err);
    }
  };

  const fetchAtletas = async () => {
    setLoadingAtletas(true);
    try {
      const response = await axios.get(`${API}/admin/atletas`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { 
          categoria: filtroCategoria !== 'all' ? filtroCategoria : undefined,
          modalidade: filtroModalidade !== 'all' ? filtroModalidade : undefined,
          equipe: filtroEquipe !== 'all' ? filtroEquipe : undefined,
          limit: 1000
        }
      });
      setAtletas(response.data.atletas || response.data || []);
    } catch (error) {
      console.error('Erro ao buscar atletas:', error);
      setAtletas([]);
    } finally {
      setLoadingAtletas(false);
    }
  };

  const fetchLigaRanking = async () => {
    setLoadingLiga(true);
    try {
      let url = `${API}/liga-assessorias/ranking?tipo=${ligaTipo}`;
      if (ligaTipo === 'estadual' && ligaEstado) url += `&estado=${ligaEstado}`;
      if (ligaTipo === 'cidade' && ligaCidade) url += `&cidade=${encodeURIComponent(ligaCidade)}`;
      const response = await axios.get(url, { headers: { Authorization: `Bearer ${token}` } });
      setLigaRanking(response.data.ranking || []);
    } catch (error) {
      console.error('Erro ao buscar ranking liga:', error);
      toast.error('Erro ao carregar ranking');
    } finally {
      setLoadingLiga(false);
    }
  };

  const fetchLigaStats = async () => {
    try {
      const response = await axios.get(`${API}/liga-assessorias/stats`, { headers: { Authorization: `Bearer ${token}` } });
      setLigaStats(response.data);
    } catch (error) {
      console.error('Erro ao buscar stats liga:', error);
    }
  };

  const fetchEstadosComAssessorias = async () => {
    try {
      const response = await axios.get(`${API}/liga-assessorias/estados`, { headers: { Authorization: `Bearer ${token}` } });
      setEstadosComAssessorias(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar estados:', error);
    }
  };

  const fetchCidadesComAssessorias = async (estado) => {
    try {
      const response = await axios.get(`${API}/liga-assessorias/cidades?estado=${estado}`, { headers: { Authorization: `Bearer ${token}` } });
      setCidadesComAssessorias(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
    }
  };

  const fetchRankingCorridasDashboard = async () => {
    setLoadingRankingCorridas(true);
    try {
      const response = await axios.get(`${API}/admin/ranking-corridas/dashboard`, { headers: { Authorization: `Bearer ${token}` } });
      setRankingCorridasDashboard(response.data);
    } catch (error) {
      console.error('Erro ao buscar dashboard:', error);
    } finally {
      setLoadingRankingCorridas(false);
    }
  };

  const fetchCorridasEventos = async () => {
    try {
      const response = await axios.get(`${API}/corridas-eventos`);
      setCorridasEventos(Array.isArray(response.data) ? response.data : (response.data?.corridas || []));
    } catch (error) {
      console.error('Erro ao buscar corridas:', error);
    }
  };

  // ==================== HANDLERS ====================

  const handleSalvarCorrida = async () => {
    if (!corridaFormData.nome_corrida || !corridaFormData.organizador || !corridaFormData.cidade || 
        !corridaFormData.estado || !corridaFormData.data_corrida) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }
    try {
      if (corridaEditando) {
        await axios.put(`${API}/corridas-eventos/${corridaEditando.id}`, corridaFormData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Corrida atualizada!');
      } else {
        const form = new FormData();
        Object.keys(corridaFormData).forEach(key => form.append(key, corridaFormData[key]));
        await axios.post(`${API}/corridas-eventos`, form, {
          headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
        });
        toast.success('Corrida cadastrada!');
      }
      setShowCorridaModal(false);
      setCorridaEditando(null);
      setCorridaFormData({ nome_corrida: '', organizador: '', cidade: '', estado: '', data_corrida: '', pagina_link: '', status: 'ativa' });
      fetchCorridasEventos();
      fetchRankingCorridasDashboard();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao salvar corrida');
    }
  };

  const handleExcluirCorrida = async (corridaId) => {
    try {
      await axios.delete(`${API}/corridas-eventos/${corridaId}`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Corrida excluída!');
      fetchCorridasEventos();
      fetchRankingCorridasDashboard();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao excluir');
    }
  };

  const handleAprovar = async (resultadoId) => {
    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/aprovar/${resultadoId}`, {}, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Ação Concluída', { description: 'Resultado aprovado com sucesso!' });
      fetchPendentes();
      fetchStats();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao aprovar' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReprovar = async (resultadoId, motivo) => {
    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/reprovar/${resultadoId}`, { motivo }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Ação Concluída', { description: 'Resultado reprovado com sucesso!' });
      fetchPendentes();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao reprovar' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteAtleta = async (atletaId) => {
    if (!window.confirm('Tem certeza que deseja excluir este atleta?')) return;
    try {
      await axios.delete(`${API}/admin/atletas/${atletaId}`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Ação Concluída', { description: 'Atleta excluído com sucesso!' });
      fetchAtletas();
      fetchStats();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao excluir' });
    }
  };

  const handlePromoverDonoAssessoria = async () => {
    if (!atletaPromover) return;
    setPromoverLoading(true);
    try {
      await axios.post(`${API}/admin/atletas/${atletaPromover.id}/promover-dono-assessoria`, {}, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Promoção Concluída', { description: `${atletaPromover.nome} agora é Dono de Assessoria!` });
      setShowPromoverModal(false);
      setAtletaPromover(null);
      setAtletaAcao(null);
      fetchAtletas();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao promover' });
    } finally {
      setPromoverLoading(false);
    }
  };

  const handleEnviarMensagemIndividual = async () => {
    if (!atletaAcao || !mensagemAdmin.trim()) return;
    setSendingMensagem(true);
    try {
      await axios.post(`${API}/notificacoes/enviar`, {
        destinatarios: [atletaAcao.id],
        mensagem: mensagemAdmin,
        tipo: 'mensagem_admin',
        titulo: 'Mensagem do Administrador'
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Mensagem Enviada', { description: `Mensagem enviada para ${atletaAcao.nome}` });
      setShowMensagemModal(false);
      setMensagemAdmin('');
      setAtletaAcao(null);
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao enviar mensagem' });
    } finally {
      setSendingMensagem(false);
    }
  };

  const handleSaveAtleta = async () => {
    setActionLoading(true);
    try {
      await axios.put(`${API}/admin/atletas/${atletaEditando.id}`, atletaEditando, { headers: { Authorization: `Bearer ${token}` } });
      setShowAtletaModal(false);
      setAtletaEditando(null);
      toast.success('Ação Concluída', { description: 'Atleta atualizado com sucesso!' });
      fetchAtletas();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao salvar' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddAtleta = async () => {
    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/atletas`, novoAtleta, { headers: { Authorization: `Bearer ${token}` } });
      setShowAddAtletaModal(false);
      setNovoAtleta({
        nome: '', email: '', password: 'atleta123', equipe: '',
        cidade: '', estado: 'SP', genero: 'M', categoria: 'normal',
        data_nascimento: '', telefone: '', tipo_corredor: '', terreno_preferido: '',
        modalidade_usuario: 'profissional_amador'
      });
      toast.success('Ação Concluída', { description: 'Atleta cadastrado com sucesso!' });
      fetchAtletas();
      fetchStats();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao cadastrar' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteFotoPodio = async (resultadoId) => {
    if (!window.confirm('Tem certeza que deseja excluir a foto do pódio?')) return;
    try {
      await axios.delete(`${API}/admin/pendentes/${resultadoId}/foto`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Ação Concluída', { description: 'Foto excluída com sucesso!' });
      fetchPendentes();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao excluir foto' });
    }
  };

  const handleViewFoto = (fotoUrl) => {
    const fullUrl = fotoUrl.startsWith('http') ? fotoUrl : `${BACKEND_URL}${fotoUrl}`;
    setFotoModalUrl(fullUrl);
    setShowFotoModal(true);
  };

  const handleTransferirModalidade = async () => {
    if (!atletaTransferindo) return;
    setTransferLoading(true);
    try {
      const response = await axios.post(
        `${API}/admin/atletas/${atletaTransferindo.id}/transferir-modalidade`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const { stats } = response.data;
      const modalidadeNova = stats.modalidade_nova === 'povao_pace_livre' ? 'Ranking da Galera' : 'Ranking Profissional/Amador';
      toast.success('Transferência Concluída!', {
        description: `${atletaTransferindo.nome} transferido para ${modalidadeNova}. Pontos: ${stats.pontos_antigos} → ${stats.pontos_novos}`
      });
      setShowTransferModal(false);
      setAtletaTransferindo(null);
      fetchAtletas();
      fetchStats();
    } catch (error) {
      toast.error('Erro na Transferência', { description: error.response?.data?.detail || 'Erro ao transferir atleta' });
    } finally {
      setTransferLoading(false);
    }
  };

  const handleExportAtletas = async () => {
    try {
      const params = {};
      if (filtroCategoria !== 'all') params.categoria = filtroCategoria;
      if (filtroModalidade !== 'all') params.modalidade = filtroModalidade;
      if (filtroEquipe !== 'all') params.equipe = filtroEquipe;
      downloadFile('/api/admin/atletas/export', params);
      toast.success('Download iniciado!');
    } catch (error) {
      toast.error('Erro ao exportar dados');
    }
  };

  const handleExportRanking = async (format) => {
    try {
      downloadFile(`/api/ranking/export/${format}`, { todas_modalidades: true });
      toast.success('Download iniciado!');
    } catch (error) {
      toast.error('Erro ao exportar ranking');
    }
  };

  // ==================== RENDER ====================

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100 dark:bg-slate-950">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-emerald-500 mx-auto mb-4" />
          <p className="text-slate-500">Carregando painel...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) return null;

  const menuItems = allMenuItems.filter(item => {
    if (isSuperAdmin) return true;
    if (item.superAdminOnly) return false;
    if (!item.permissoes || item.permissoes.length === 0) return true;
    return item.permissoes.some(perm => adminPermissoes.includes(perm));
  });

  return (
    <div className="min-h-screen flex bg-slate-100 dark:bg-slate-950">
      {/* Sidebar extraído */}
      <AdminSidebar
        menuSections={menuSections}
        activeMenu={activeMenu}
        setActiveMenu={setActiveMenu}
        isSuperAdmin={isSuperAdmin}
        adminPermissoes={adminPermissoes}
        tipoAdmin={tipoAdmin}
        pendentes={pendentes}
        onNavigateHome={() => navigate('/')}
      />

      {/* Main Content */}
      <div className="ml-64 flex-1 p-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white">
            {menuItems.find(m => m.id === activeMenu)?.label || 'Dashboard'}
          </h2>
          <p className="text-slate-500">Bem-vindo, {user?.nome}</p>
        </div>

        {activeMenu === 'dashboard' && (
          <DashboardGeral
            stats={stats} statsEstados={statsEstados} statsCategorias={statsCategorias}
            statsFaixa={statsFaixa} corridasPorMes={corridasPorMes} statsModalidade={statsModalidade}
            statsPovao={statsPovao} statsEquipes={statsEquipes} statsDonosPorEstado={statsDonosPorEstado}
            statsAssessoriasVerificadas={statsAssessoriasVerificadas} statsInsignias={statsInsignias}
            loadingStats={loadingStats} token={token}
          />
        )}

        {activeMenu === 'estrategico' && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Dashboard Estratégico</h2>
              <p className="text-slate-400 max-w-md">
                Acesse o painel completo com 31 gráficos e indicadores estratégicos da plataforma.
              </p>
            </div>
            <Button onClick={() => navigate('/admin/estrategico')} className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-3 text-lg">
              <BarChart3 className="w-5 h-5 mr-2" />
              Abrir Dashboard Estratégico
            </Button>
          </div>
        )}

        {activeMenu === 'pendentes' && (
          <DashboardResultados
            pendentes={pendentes} loadingPendentes={loadingPendentes}
            onAprovar={handleAprovar} onReprovar={handleReprovar}
            onDeleteFoto={handleDeleteFotoPodio} onViewFoto={handleViewFoto}
            actionLoading={actionLoading} showFotoModal={showFotoModal}
            setShowFotoModal={setShowFotoModal} fotoModalUrl={fotoModalUrl}
          />
        )}

        {activeMenu === 'atletas' && (
          <DashboardAtletas
            atletas={atletas} loadingAtletas={loadingAtletas}
            filtroCategoria={filtroCategoria} setFiltroCategoria={setFiltroCategoria}
            filtroModalidade={filtroModalidade} setFiltroModalidade={setFiltroModalidade}
            filtroEquipe={filtroEquipe} setFiltroEquipe={setFiltroEquipe}
            searchQuery={searchQuery} setSearchQuery={setSearchQuery}
            token={token} onRefresh={fetchAtletas}
            onEditAtleta={(atleta) => {
              if (atleta) { setAtletaEditando(atleta); setShowAtletaModal(true); }
              else { setShowAddAtletaModal(true); }
            }}
            onDeleteAtleta={handleDeleteAtleta}
            onTransferirModalidade={(atleta) => { setAtletaTransferindo(atleta); setShowTransferModal(true); }}
            onPromoverDono={(atleta) => { setAtletaPromover(atleta); setAtletaAcao(atleta); setShowPromoverModal(true); }}
            onExportAtletas={handleExportAtletas}
            onViewAtleta={(atleta) => navigate(`/atleta/${atleta.id}`)}
            onEnviarMensagem={(atleta) => { setAtletaAcao(atleta); setMensagemAdmin(''); setShowMensagemModal(true); }}
          />
        )}

        {activeMenu === 'assessorias' && (
          <DashboardAssessorias
            ligaRanking={ligaRanking} ligaStats={ligaStats}
            ligaTipo={ligaTipo} setLigaTipo={setLigaTipo}
            ligaEstado={ligaEstado} setLigaEstado={setLigaEstado}
            ligaCidade={ligaCidade} setLigaCidade={setLigaCidade}
            estadosComAssessorias={estadosComAssessorias} cidadesComAssessorias={cidadesComAssessorias}
            loadingLiga={loadingLiga} onRefresh={fetchLigaRanking}
            fetchCidades={fetchCidadesComAssessorias} token={token}
          />
        )}

        {activeMenu === 'mensagens' && <DashboardMensagens />}
        {activeMenu === 'engajamento' && <DashboardEngajamento />}
        {activeMenu === 'financeiro' && <DashboardFinanceiro />}

        {activeMenu === 'ranking-corridas' && (
          <DashboardCorridas
            rankingCorridasDashboard={rankingCorridasDashboard} corridasEventos={corridasEventos}
            loadingRankingCorridas={loadingRankingCorridas}
            corridaFormData={corridaFormData} setCorridaFormData={setCorridaFormData}
            showCorridaModal={showCorridaModal} setShowCorridaModal={setShowCorridaModal}
            corridaEditando={corridaEditando} setCorridaEditando={setCorridaEditando}
            onSaveCorrida={handleSalvarCorrida} onDeleteCorrida={handleExcluirCorrida}
            onRefresh={() => { fetchRankingCorridasDashboard(); fetchCorridasEventos(); }}
          />
        )}

        {activeMenu === 'submeter' && <DashboardSubmeter token={token} atletas={atletas} onStatsRefresh={fetchStats} />}
        {activeMenu === 'autorizacoes' && <DashboardAutorizacoes token={token} />}
        {activeMenu === 'administradores' && <DashboardRBAC />}
        {activeMenu === 'monitoramento' && <DashboardMonitoramento />}
        {activeMenu === 'configuracoes' && <ConfiguracoesSistemaTab token={token} />}
        {activeMenu === 'regulamento' && <DashboardRegulamento token={token} />}

        {activeMenu === 'ranking' && (
          <div className="space-y-6">
            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 p-6">
              <h3 className="text-lg font-semibold mb-4">Exportar Ranking Completo</h3>
              <p className="text-slate-500 mb-4">
                Exporta todas as modalidades em um único arquivo: Masculino, Feminino, PCD Masculino, PCD Feminino, Cadeirante Masculino, Cadeirante Feminino.
              </p>
              <div className="flex gap-4">
                <Button onClick={() => handleExportRanking('csv')} variant="outline">
                  <Download className="w-4 h-4 mr-2" />Exportar CSV
                </Button>
                <Button onClick={() => handleExportRanking('excel')} variant="outline">
                  <Download className="w-4 h-4 mr-2" />Exportar Excel
                </Button>
              </div>
            </Card>

            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 p-6">
              <h3 className="text-lg font-semibold mb-4">Exportar Dados do Sistema</h3>
              <p className="text-slate-500 mb-6">
                Exporte dados detalhados de cada módulo do sistema em formato Excel.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {[
                  { label: 'Atletas Profissional/Amador', path: '/api/admin/exportar/atletas-profissional', icon: Users },
                  { label: 'Atletas da Galera', path: '/api/admin/exportar/atletas-galera', icon: Users },
                  { label: 'Donos de Assessoria', path: '/api/admin/exportar/donos-assessoria', icon: Crown },
                  { label: 'Assessorias', path: '/api/admin/exportar/assessorias', icon: Shield },
                  { label: 'Corridas Parceiras', path: '/api/admin/exportar/corridas-parceiras', icon: Handshake },
                  { label: 'Corridas Avaliadas', path: '/api/admin/exportar/corridas-avaliadas', icon: Star },
                  { label: 'Média das Avaliações', path: '/api/admin/exportar/media-avaliacoes', icon: BarChart3 },
                  { label: 'Engajamento', path: '/api/admin/exportar/engajamento', icon: Activity },
                  { label: 'Retenção', path: '/api/admin/exportar/retencao', icon: TrendingDown },
                  { label: 'Aprovações com Logs', path: '/api/admin/exportar/aprovacoes-logs', icon: AlertCircle },
                  { label: 'Autorizações', path: '/api/admin/exportar/autorizacoes', icon: Shield },
                  { label: 'Financeiro', path: '/api/admin/exportar/financeiro', icon: CreditCard },
                  { label: 'Mensagens Enviadas', path: '/api/admin/exportar/mensagens', icon: MessageSquare },
                  { label: 'Logs Administrativos', path: '/api/admin/exportar/logs-admin', icon: FileText },
                ].map(({ label, path, icon: Icon }) => (
                  <Button
                    key={path}
                    variant="outline"
                    className="justify-start h-auto py-3 px-4 text-left"
                    onClick={() => { downloadFile(path); toast.success(`Exportando ${label}...`); }}
                    data-testid={`export-btn-${path.split('/').pop()}`}
                  >
                    <Icon className="w-4 h-4 mr-2 shrink-0 text-emerald-600" />
                    <span className="text-sm">{label}</span>
                  </Button>
                ))}
              </div>
            </Card>

            <div className="text-center py-12">
              <Trophy className="h-16 w-16 text-emerald-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Gerenciar Ranking</h3>
              <p className="text-slate-500 mb-4">Acesse a página principal para visualizar os rankings completos.</p>
              <Button onClick={() => navigate('/')} className="bg-emerald-600">Ir para Ranking</Button>
            </div>
          </div>
        )}

        {activeMenu === 'aniversariantes' && <DashboardAniversariantes token={token} />}
        {activeMenu === 'instagram' && <DashboardInstagram token={token} />}
        {activeMenu === 'resumo-semanal' && <DashboardResumoSemanal token={token} />}
        {activeMenu === 'retencao' && <DashboardRetencao />}
        {activeMenu === 'backup' && <DashboardBackup />}
        {activeMenu === 'corridas-parceiras' && <DashboardCorridasParceiras token={token} />}

        {/* Modais extraídos */}
        <AdminModals
          showAtletaModal={showAtletaModal} setShowAtletaModal={setShowAtletaModal}
          atletaEditando={atletaEditando} setAtletaEditando={setAtletaEditando}
          cidadesEditAtleta={cidadesEditAtleta} loadingCidadesEdit={loadingCidadesEdit}
          onSaveAtleta={handleSaveAtleta} actionLoading={actionLoading}
          showAddAtletaModal={showAddAtletaModal} setShowAddAtletaModal={setShowAddAtletaModal}
          novoAtleta={novoAtleta} setNovoAtleta={setNovoAtleta}
          cidadesNovoAtleta={cidadesNovoAtleta} loadingCidadesNovo={loadingCidadesNovo}
          onAddAtleta={handleAddAtleta}
          showFotoModal={showFotoModal} setShowFotoModal={setShowFotoModal} fotoModalUrl={fotoModalUrl}
          showTransferModal={showTransferModal} setShowTransferModal={setShowTransferModal}
          atletaTransferindo={atletaTransferindo} setAtletaTransferindo={setAtletaTransferindo}
          onTransferirModalidade={handleTransferirModalidade} transferLoading={transferLoading}
          showCorridaModal={showCorridaModal} setShowCorridaModal={setShowCorridaModal}
          corridaEditando={corridaEditando} setCorridaEditando={setCorridaEditando}
          corridaFormData={corridaFormData} setCorridaFormData={setCorridaFormData}
          onSaveCorrida={handleSalvarCorrida}
          showPromoverModal={showPromoverModal} setShowPromoverModal={setShowPromoverModal}
          atletaAcao={atletaAcao}
          onPromoverDonoAssessoria={handlePromoverDonoAssessoria} promoverLoading={promoverLoading}
          showMensagemModal={showMensagemModal} setShowMensagemModal={setShowMensagemModal}
          mensagemAdmin={mensagemAdmin} setMensagemAdmin={setMensagemAdmin}
          onEnviarMensagemIndividual={handleEnviarMensagemIndividual} sendingMensagem={sendingMensagem}
        />
      </div>
    </div>
  );
};

export default AdminDashboard;
