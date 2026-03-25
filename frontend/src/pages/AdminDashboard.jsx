import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { 
  Trophy, Users, AlertCircle, BarChart3, Shield,
  Activity, Home, Settings, FileText,
  Edit, Download, Plus, X,
  Cake, Send, ArrowRightLeft, RefreshCw, Loader2,
  Crown, MessageSquare
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

import { Instagram, Star } from 'lucide-react';

// Import dos novos dashboards modulares
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
import DashboardEngajamento from './admin/DashboardEngajamento';
import ConfiguracoesSistemaTab from '@/components/admin/ConfiguracoesSistemaTab';

// Definição dos itens do menu organizados em seções
const menuSections = [
  {
    title: null, // Seção principal sem título
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
      { id: 'pendentes', label: 'Aprovações', icon: AlertCircle, permissoes: ['aprovar_corridas', 'aprovar_resultados'] },
      { id: 'mensagens', label: 'Mensagens', icon: MessageSquare, permissoes: [] },
      { id: 'engajamento', label: 'Engajamento', icon: BarChart3, permissoes: [] },
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
    ]
  },
  {
    title: 'Ferramentas',
    items: [
      { id: 'submeter', label: 'Submeter Resultado', icon: Plus, permissoes: ['aprovar_resultados'] },
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

// Flatten para compatibilidade com código existente
const allMenuItems = menuSections.flatMap(section => section.items);

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, token, loading, isAdmin, tipoAdmin, isSuperAdmin, temPermissao, adminPermissoes } = useAuth();
  const [activeMenu, setActiveMenu] = useState('dashboard');
  
  // Filtrar itens do menu baseado nas permissões
  const menuItems = allMenuItems.filter(item => {
    // Se for Super Admin, mostrar tudo
    if (isSuperAdmin) return true;
    
    // Se o item requer Super Admin e o usuário não é, esconder
    if (item.superAdminOnly) return false;
    
    // Se não tem permissões definidas, mostrar para todos
    if (!item.permissoes || item.permissoes.length === 0) return true;
    
    // Verificar se tem pelo menos uma das permissões necessárias
    return item.permissoes.some(perm => adminPermissoes.includes(perm));
  });
  
  // Stats
  const [stats, setStats] = useState(null);
  const [statsEstados, setStatsEstados] = useState([]);
  const [statsCategorias, setStatsCategorias] = useState(null);
  const [statsFaixa, setStatsFaixa] = useState([]);
  const [corridasPorMes, setCorridasPorMes] = useState([]);
  const [loadingStats, setLoadingStats] = useState(true);
  
  // Stats Avançados
  const [statsEquipes, setStatsEquipes] = useState([]);
  const [statsPovao, setStatsPovao] = useState(null);
  const [statsModalidade, setStatsModalidade] = useState({ profissional: 0, povao: 0 });
  const [statsEtnia, setStatsEtnia] = useState([]);
  const [statsEquipesPorEstado, setStatsEquipesPorEstado] = useState([]);
  const [statsDonosPorEstado, setStatsDonosPorEstado] = useState([]);
  const [statsAssessoriasVerificadas, setStatsAssessoriasVerificadas] = useState(null);
  const [statsInsignias, setStatsInsignias] = useState([]);
  
  // Modal de visualização de foto do pódio
  const [showFotoModal, setShowFotoModal] = useState(false);
  const [fotoModalUrl, setFotoModalUrl] = useState('');
  
  // Pendentes
  const [pendentes, setPendentes] = useState([]);
  const [loadingPendentes, setLoadingPendentes] = useState(true);
  
  // Atletas
  const [atletas, setAtletas] = useState([]);
  const [loadingAtletas, setLoadingAtletas] = useState(false);
  const [filtroCategoria, setFiltroCategoria] = useState('all');
  const [filtroModalidade, setFiltroModalidade] = useState('all'); // all, profissional_amador, povao_pace_livre
  const [filtroEquipe, setFiltroEquipe] = useState('all'); // all, com_assessoria, individual
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

  // Liga de Assessorias (ROE-RR)
  const [ligaRanking, setLigaRanking] = useState([]);
  const [ligaStats, setLigaStats] = useState(null);
  const [ligaTipo, setLigaTipo] = useState('nacional');
  const [ligaEstado, setLigaEstado] = useState('');
  const [ligaCidade, setLigaCidade] = useState('');
  const [loadingLiga, setLoadingLiga] = useState(false);
  const [estadosComAssessorias, setEstadosComAssessorias] = useState([]);
  const [cidadesComAssessorias, setCidadesComAssessorias] = useState([]);
  const [assessoriaDetalhe, setAssessoriaDetalhe] = useState(null);
  const [showAssessoriaModal, setShowAssessoriaModal] = useState(false);

  // Regulamento / Autorizações: gerenciados pelos sub-componentes

  // Promover Dono de Assessoria
  const [showPromoverModal, setShowPromoverModal] = useState(false);
  const [atletaPromover, setAtletaPromover] = useState(null);
  const [promoverLoading, setPromoverLoading] = useState(false);

  // Enviar Mensagem Individual
  const [showMensagemModal, setShowMensagemModal] = useState(false);
  const [mensagemAdmin, setMensagemAdmin] = useState('');
  const [sendingMensagem, setSendingMensagem] = useState(false);

  // Atleta selecionado para ações (promover, mensagem)
  const [atletaAcao, setAtletaAcao] = useState(null);

  // Dashboard Ranking das Corridas (Fase 4)
  const [rankingCorridasDashboard, setRankingCorridasDashboard] = useState(null);
  const [loadingRankingCorridas, setLoadingRankingCorridas] = useState(false);
  const [corridasEventos, setCorridasEventos] = useState([]);
  const [showCorridaModal, setShowCorridaModal] = useState(false);
  const [corridaEditando, setCorridaEditando] = useState(null);
  const [corridaFormData, setCorridaFormData] = useState({
    nome_corrida: '',
    organizador: '',
    cidade: '',
    estado: '',
    data_corrida: '',
    pagina_link: '',
    status: 'ativa'
  });


  useEffect(() => {
    // Aguardar o carregamento do usuário antes de verificar permissões
    if (loading) return;
    
    if (!token) {
      navigate('/');
      return;
    }
    
    if (!isAdmin) {
      navigate('/');
      return;
    }
    
    fetchAllData();
  }, [isAdmin, token, loading, navigate]);

  useEffect(() => {
    if (activeMenu === 'atletas') {
      fetchAtletas();
    }
    if (activeMenu === 'assessorias') {
      fetchLigaRanking();
      fetchLigaStats();
      fetchEstadosComAssessorias();
    }
    if (activeMenu === 'ranking-corridas') {
      fetchRankingCorridasDashboard();
      fetchCorridasEventos();
    }
    if (activeMenu === 'geral' && !statsCategorias) {
      fetchExtraStats();
      fetchEquipesStats();
    }
  }, [activeMenu, filtroCategoria, filtroEquipe, ligaTipo, ligaEstado, ligaCidade]);



  const fetchAllData = async () => {
    // Carregar apenas stats essenciais no startup (visão geral)
    fetchStats();
    fetchPendentes();
  };

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      // Apenas 3 requests essenciais no startup (os outros carregam sob demanda)
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
        axios.get(`${API}/admin/stats/etnia`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/equipes-por-estado`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/donos-por-estado`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/assessorias-verificadas`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/insignias`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      const [categoriasRes, faixaRes, corridasRes, etniaRes, equipesPorEstadoRes, donosEstadoRes, assessoriasVerificadasRes, insigniasRes] = results;
      
      if (categoriasRes.status === 'fulfilled') setStatsCategorias(categoriasRes.value.data);
      if (faixaRes.status === 'fulfilled') setStatsFaixa(faixaRes.value.data);
      if (corridasRes.status === 'fulfilled') setCorridasPorMes(corridasRes.value.data);
      if (etniaRes.status === 'fulfilled') setStatsEtnia(etniaRes.value.data);
      if (equipesPorEstadoRes.status === 'fulfilled') setStatsEquipesPorEstado(equipesPorEstadoRes.value.data);
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

  const fetchEquipesStats = async () => {
    try {
      const atletasRes = await axios.get(`${API}/admin/atletas?limit=1000`, { headers: { Authorization: `Bearer ${token}` } });
      const atletasList = Array.isArray(atletasRes.data) ? atletasRes.data : (atletasRes.data.atletas || []);
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
          limit: 1000 // Buscar mais atletas para filtro local funcionar
        }
      });
      // O endpoint retorna {atletas: [], total: ..., page: ...}
      setAtletas(response.data.atletas || response.data || []);
    } catch (error) {
      console.error('Erro ao buscar atletas:', error);
      setAtletas([]);
    } finally {
      setLoadingAtletas(false);
    }
  };

  // ============ LIGA DE ASSESSORIAS - ROE-RR ============
  const fetchLigaRanking = async () => {
    setLoadingLiga(true);
    try {
      let url = `${API}/liga-assessorias/ranking?tipo=${ligaTipo}`;
      if (ligaTipo === 'estadual' && ligaEstado) {
        url += `&estado=${ligaEstado}`;
      }
      if (ligaTipo === 'cidade' && ligaCidade) {
        url += `&cidade=${encodeURIComponent(ligaCidade)}`;
      }
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
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
      const response = await axios.get(`${API}/liga-assessorias/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLigaStats(response.data);
    } catch (error) {
      console.error('Erro ao buscar stats liga:', error);
    }
  };

  const fetchEstadosComAssessorias = async () => {
    try {
      const response = await axios.get(`${API}/liga-assessorias/estados`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEstadosComAssessorias(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar estados:', error);
    }
  };

  const fetchCidadesComAssessorias = async (estado) => {
    try {
      const response = await axios.get(`${API}/liga-assessorias/cidades?estado=${estado}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCidadesComAssessorias(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
    }
  };

  const fetchAssessoriaDetalhe = async (nome) => {
    try {
      const response = await axios.get(`${API}/liga-assessorias/assessoria/${encodeURIComponent(nome)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAssessoriaDetalhe(response.data);
      setShowAssessoriaModal(true);
    } catch (error) {
      console.error('Erro ao buscar detalhes:', error);
      toast.error('Erro ao carregar detalhes da assessoria');
    }
  };

  // ======= Ranking das Corridas - Dashboard Admin (Fase 4) =======
  const fetchRankingCorridasDashboard = async () => {
    setLoadingRankingCorridas(true);
    try {
      const response = await axios.get(`${API}/admin/ranking-corridas/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRankingCorridasDashboard(response.data);
    } catch (error) {
      console.error('Erro ao buscar dashboard:', error);
    } finally {
      setLoadingRankingCorridas(false);
    }
  };

  const fetchCorridasEventos = async () => {
    try {
      const response = await axios.get(`${API}/ranking-corridas`);
      setCorridasEventos(response.data.ranking || []);
    } catch (error) {
      console.error('Erro ao buscar corridas:', error);
    }
  };

  const handleSalvarCorrida = async () => {
    if (!corridaFormData.nome_corrida || !corridaFormData.organizador || !corridaFormData.cidade || 
        !corridaFormData.estado || !corridaFormData.data_corrida) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    try {
      const form = new FormData();
      Object.keys(corridaFormData).forEach(key => {
        form.append(key, corridaFormData[key]);
      });

      if (corridaEditando) {
        await axios.put(`${API}/corridas-eventos/${corridaEditando.id}`, corridaFormData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Corrida atualizada!');
      } else {
        await axios.post(`${API}/corridas-eventos`, form, {
          headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
        });
        toast.success('Corrida cadastrada!');
      }

      setShowCorridaModal(false);
      setCorridaEditando(null);
      setCorridaFormData({
        nome_corrida: '', organizador: '', cidade: '', estado: '',
        data_corrida: '', pagina_link: '', status: 'ativa'
      });
      fetchCorridasEventos();
      fetchRankingCorridasDashboard();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao salvar corrida');
    }
  };

  const handleExcluirCorrida = async (corridaId) => {
    if (!confirm('Excluir esta corrida? Todas as avaliações serão perdidas.')) return;
    
    try {
      await axios.delete(`${API}/corridas-eventos/${corridaId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
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
      await axios.post(`${API}/admin/aprovar/${resultadoId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
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
      await axios.post(
        `${API}/admin/reprovar/${resultadoId}`,
        { motivo: motivo },
        { headers: { Authorization: `Bearer ${token}` }}
      );
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
      await axios.delete(`${API}/admin/atletas/${atletaId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Ação Concluída', { description: 'Atleta excluído com sucesso!' });
      fetchAtletas();
      fetchStats();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao excluir' });
    }
  };

  // Promover atleta a Dono de Assessoria
  const handlePromoverDonoAssessoria = async () => {
    if (!atletaPromover) return;
    
    setPromoverLoading(true);
    try {
      await axios.post(`${API}/admin/atletas/${atletaPromover.id}/promover-dono-assessoria`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Promoção Concluída', { 
        description: `${atletaPromover.nome} agora é Dono de Assessoria!` 
      });
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

  // Enviar mensagem individual para atleta
  const handleEnviarMensagemIndividual = async () => {
    if (!atletaAcao || !mensagemAdmin.trim()) return;
    
    setSendingMensagem(true);
    try {
      await axios.post(`${API}/notificacoes/enviar`, {
        destinatarios: [atletaAcao.id],
        mensagem: mensagemAdmin,
        tipo: 'mensagem_admin',
        titulo: 'Mensagem do Administrador'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Mensagem Enviada', { 
        description: `Mensagem enviada para ${atletaAcao.nome}` 
      });
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
      await axios.put(`${API}/admin/atletas/${atletaEditando.id}`, atletaEditando, {
        headers: { Authorization: `Bearer ${token}` }
      });
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
      await axios.post(`${API}/admin/atletas`, novoAtleta, {
        headers: { Authorization: `Bearer ${token}` }
      });
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
      await axios.delete(`${API}/admin/pendentes/${resultadoId}/foto`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Ação Concluída', { description: 'Foto excluída com sucesso!' });
      fetchPendentes();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao excluir foto' });
    }
  };

  // Função para abrir modal de visualização da foto
  const handleViewFoto = (fotoUrl) => {
    const fullUrl = fotoUrl.startsWith('http') ? fotoUrl : `${BACKEND_URL}${fotoUrl}`;
    setFotoModalUrl(fullUrl);
    setShowFotoModal(true);
  };

  // Função para transferir atleta entre modalidades
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
      toast.error('Erro na Transferência', {
        description: error.response?.data?.detail || 'Erro ao transferir atleta'
      });
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
      
      const response = await axios.get(`${API}/admin/atletas/export`, {
        headers: { Authorization: `Bearer ${token}` },
        params,
        responseType: 'blob'
      });
      
      // Gerar nome do arquivo com base nos filtros
      const filtros = [];
      if (filtroModalidade !== 'all') filtros.push(filtroModalidade);
      if (filtroEquipe !== 'all') filtros.push(filtroEquipe);
      const nomeArquivo = `atletas_${filtros.length ? filtros.join('_') : 'todos'}.xlsx`;
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', nomeArquivo);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Ação Concluída', { description: 'Dados exportados com sucesso!' });
    } catch (error) {
      toast.error('Erro', { description: 'Erro ao exportar dados' });
    }
  };

  const handleExportRanking = async (format) => {
    try {
      const response = await axios.get(`${API}/ranking/export/${format}`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { todas_modalidades: true },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ranking_todas_modalidades.${format === 'excel' ? 'xlsx' : 'csv'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Ação Concluída', { description: 'Ranking exportado com sucesso!' });
    } catch (error) {
      toast.error('Erro', { description: 'Erro ao exportar ranking' });
    }
  };

  // Mostrar loading enquanto carrega o usuário
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

  return (
    <div className="min-h-screen flex bg-slate-100 dark:bg-slate-950">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-slate-800 to-slate-900 text-white fixed h-full shadow-xl">
        <div className="p-6 border-b border-slate-700/50">
          <h1 className="text-xl font-bold text-emerald-400">Ranking Run Pró</h1>
          <p className="text-xs text-slate-400 mt-1">Painel Administrativo</p>
          {/* Badge do tipo de admin */}
          <div className="mt-3">
            <Badge className={`text-xs ${
              isSuperAdmin 
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' 
                : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
            }`}>
              {tipoAdmin || 'Admin'}
            </Badge>
          </div>
        </div>

        <nav className="p-4 space-y-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
          {menuSections.map((section, sectionIdx) => {
            // Filtrar itens da seção baseado nas permissões
            const sectionItems = section.items.filter(item => {
              if (isSuperAdmin) return true;
              if (item.superAdminOnly) return false;
              if (!item.permissoes || item.permissoes.length === 0) return true;
              return item.permissoes.some(perm => adminPermissoes.includes(perm));
            });
            
            // Se a seção é superAdminOnly e o usuário não é, pular
            if (section.superAdminOnly && !isSuperAdmin) return null;
            
            // Se não há itens visíveis na seção, pular
            if (sectionItems.length === 0) return null;
            
            return (
              <div key={sectionIdx} className={section.title ? 'pt-4' : ''}>
                {section.title && (
                  <p className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    {section.title}
                  </p>
                )}
                <div className="space-y-1">
                  {sectionItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.id}
                        onClick={() => setActiveMenu(item.id)}
                        className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all text-sm ${
                          activeMenu === item.id 
                            ? 'bg-emerald-500/20 text-emerald-400 border-l-4 border-emerald-400' 
                            : 'text-slate-400 hover:bg-slate-700/50 hover:text-white'
                        }`}
                        data-testid={`menu-${item.id}`}
                      >
                        <Icon className="w-4 h-4" />
                        <span className="font-medium">{item.label}</span>
                        {item.id === 'pendentes' && pendentes.length > 0 && (
                          <Badge className="ml-auto bg-red-500 text-white text-xs px-1.5 py-0.5 min-w-[20px]">
                            {pendentes.length}
                          </Badge>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </nav>

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
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white">
            {menuItems.find(m => m.id === activeMenu)?.label || 'Dashboard'}
          </h2>
          <p className="text-slate-500">Bem-vindo, {user?.nome}</p>
        </div>

        {/* Dashboard Geral View - Usando componente modular */}
        {activeMenu === 'dashboard' && (
          <DashboardGeral
            stats={stats}
            statsEstados={statsEstados}
            statsCategorias={statsCategorias}
            statsFaixa={statsFaixa}
            corridasPorMes={corridasPorMes}
            statsModalidade={statsModalidade}
            statsPovao={statsPovao}
            statsEquipes={statsEquipes}
            statsDonosPorEstado={statsDonosPorEstado}
            statsAssessoriasVerificadas={statsAssessoriasVerificadas}
            statsInsignias={statsInsignias}
            loadingStats={loadingStats}
            token={token}
          />
        )}

        {/* Dashboard Estratégico - Redireciona para página dedicada */}
        {activeMenu === 'estrategico' && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Dashboard Estratégico</h2>
              <p className="text-slate-400 max-w-md">
                Acesse o painel completo com 31 gráficos e indicadores estratégicos da plataforma.
              </p>
            </div>
            <Button 
              onClick={() => navigate('/admin/estrategico')}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-3 text-lg"
            >
              <BarChart3 className="w-5 h-5 mr-2" />
              Abrir Dashboard Estratégico
            </Button>
          </div>
        )}

        {/* Pendentes View - Usando componente modular */}
        {activeMenu === 'pendentes' && (
          <DashboardResultados
            pendentes={pendentes}
            loadingPendentes={loadingPendentes}
            onAprovar={handleAprovar}
            onReprovar={handleReprovar}
            onDeleteFoto={handleDeleteFotoPodio}
            onViewFoto={handleViewFoto}
            actionLoading={actionLoading}
            showFotoModal={showFotoModal}
            setShowFotoModal={setShowFotoModal}
            fotoModalUrl={fotoModalUrl}
          />
        )}

        {/* Atletas View - Usando componente modular */}
        {activeMenu === 'atletas' && (
          <DashboardAtletas
            atletas={atletas}
            loadingAtletas={loadingAtletas}
            filtroCategoria={filtroCategoria}
            setFiltroCategoria={setFiltroCategoria}
            filtroModalidade={filtroModalidade}
            setFiltroModalidade={setFiltroModalidade}
            filtroEquipe={filtroEquipe}
            setFiltroEquipe={setFiltroEquipe}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            token={token}
            onRefresh={fetchAtletas}
            onEditAtleta={(atleta) => {
              if (atleta) {
                setAtletaEditando(atleta);
                setShowAtletaModal(true);
              } else {
                setShowAddAtletaModal(true);
              }
            }}
            onDeleteAtleta={handleDeleteAtleta}
            onTransferirModalidade={(atleta) => {
              setAtletaTransferindo(atleta);
              setShowTransferModal(true);
            }}
            onPromoverDono={(atleta) => {
              setAtletaPromover(atleta);
              setAtletaAcao(atleta);
              setShowPromoverModal(true);
            }}
            onExportAtletas={handleExportAtletas}
            onViewAtleta={(atleta) => navigate(`/atleta/${atleta.id}`)}
            onEnviarMensagem={(atleta) => {
              setAtletaAcao(atleta);
              setMensagemAdmin('');
              setShowMensagemModal(true);
            }}
          />
        )}

        {/* Assessorias View - Usando componente modular */}
        {activeMenu === 'assessorias' && (
          <DashboardAssessorias
            ligaRanking={ligaRanking}
            ligaStats={ligaStats}
            ligaTipo={ligaTipo}
            setLigaTipo={setLigaTipo}
            ligaEstado={ligaEstado}
            setLigaEstado={setLigaEstado}
            ligaCidade={ligaCidade}
            setLigaCidade={setLigaCidade}
            estadosComAssessorias={estadosComAssessorias}
            cidadesComAssessorias={cidadesComAssessorias}
            loadingLiga={loadingLiga}
            onRefresh={fetchLigaRanking}
            onViewAssessoria={fetchAssessoriaDetalhe}
            fetchCidades={fetchCidadesComAssessorias}
            token={token}
          />
        )}

        {/* Mensagens View */}
        {activeMenu === 'mensagens' && (
          <DashboardMensagens />
        )}

        {/* Engajamento View */}
        {activeMenu === 'engajamento' && (
          <DashboardEngajamento />
        )}


        {/* Ranking Corridas View - Usando componente modular */}
        {activeMenu === 'ranking-corridas' && (
          <DashboardCorridas
            rankingCorridasDashboard={rankingCorridasDashboard}
            corridasEventos={corridasEventos}
            loadingRankingCorridas={loadingRankingCorridas}
            corridaFormData={corridaFormData}
            setCorridaFormData={setCorridaFormData}
            showCorridaModal={showCorridaModal}
            setShowCorridaModal={setShowCorridaModal}
            corridaEditando={corridaEditando}
            setCorridaEditando={setCorridaEditando}
            onSaveCorrida={handleSalvarCorrida}
            onDeleteCorrida={handleExcluirCorrida}
            onRefresh={fetchRankingCorridasDashboard}
          />
        )}



        {/* Submeter Resultado View - Componentizado */}
        {activeMenu === 'submeter' && (
          <DashboardSubmeter token={token} atletas={atletas} onStatsRefresh={() => { fetchStats(); }} />
        )}

        {/* Autorizacoes View - Componentizado */}
        {activeMenu === 'autorizacoes' && (
          <DashboardAutorizacoes token={token} />
        )}

        {activeMenu === 'administradores' && (
          <DashboardRBAC />
        )}

        {/* Monitoramento do Sistema */}
        {activeMenu === 'monitoramento' && (
          <DashboardMonitoramento />
        )}

        {/* Configurações do Sistema */}
        {activeMenu === 'configuracoes' && (
          <ConfiguracoesSistemaTab token={token} />
        )}

        {/* Regulamento View */}
        {/* Regulamento View - Componentizado */}
        {activeMenu === 'regulamento' && (
          <DashboardRegulamento token={token} />
        )}

        {activeMenu === 'ranking' && (
          <div className="space-y-6">
            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 p-6">
              <h3 className="text-lg font-semibold mb-4">Exportar Ranking Completo</h3>
              <p className="text-slate-500 mb-4">
                Exporta todas as modalidades em um único arquivo: Masculino, Feminino, PCD Masculino, PCD Feminino, Cadeirante Masculino, Cadeirante Feminino.
              </p>
              <div className="flex gap-4">
                <Button onClick={() => handleExportRanking('csv')} variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Exportar CSV
                </Button>
                <Button onClick={() => handleExportRanking('excel')} variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Exportar Excel
                </Button>
              </div>
            </Card>
            
            <div className="text-center py-12">
              <Trophy className="h-16 w-16 text-emerald-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Gerenciar Ranking</h3>
              <p className="text-slate-500 mb-4">Acesse a página principal para visualizar os rankings completos.</p>
              <Button onClick={() => navigate('/')} className="bg-emerald-600">
                Ir para Ranking
              </Button>
            </div>
          </div>
        )}

        {/* Aniversariantes View */}
        {/* Aniversariantes View - Componentizado */}
        {activeMenu === 'aniversariantes' && (
          <DashboardAniversariantes token={token} />
        )}

        {/* Instagram Analytics - Componentizado */}
        {activeMenu === 'instagram' && (
          <DashboardInstagram token={token} />
        )}

        {/* Modal Editar Atleta */}
        <Dialog open={showAtletaModal} onOpenChange={setShowAtletaModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Editar Atleta</DialogTitle>
            </DialogHeader>
            {atletaEditando && (
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Nome</Label>
                  <Input value={atletaEditando.nome} onChange={(e) => setAtletaEditando({...atletaEditando, nome: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input value={atletaEditando.email} onChange={(e) => setAtletaEditando({...atletaEditando, email: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label>Equipe</Label>
                  <Input value={atletaEditando.equipe} onChange={(e) => setAtletaEditando({...atletaEditando, equipe: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label>Cidade</Label>
                  <Input value={atletaEditando.cidade} onChange={(e) => setAtletaEditando({...atletaEditando, cidade: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label>UF</Label>
                  <Select value={atletaEditando.estado} onValueChange={(v) => setAtletaEditando({...atletaEditando, estado: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {ESTADOS_BR.map((uf) => <SelectItem key={uf} value={uf}>{uf}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Categoria</Label>
                  <Select value={atletaEditando.categoria} onValueChange={(v) => setAtletaEditando({...atletaEditando, categoria: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="pcd">PCD</SelectItem>
                      <SelectItem value="cadeirante">Cadeirante</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Gênero</Label>
                  <Select value={atletaEditando.genero} onValueChange={(v) => setAtletaEditando({...atletaEditando, genero: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="M">Masculino</SelectItem>
                      <SelectItem value="F">Feminino</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Data de Nascimento</Label>
                  <Input type="date" value={atletaEditando.data_nascimento} onChange={(e) => setAtletaEditando({...atletaEditando, data_nascimento: e.target.value})} />
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowAtletaModal(false)}>Cancelar</Button>
              <Button onClick={handleSaveAtleta} disabled={actionLoading} className="bg-emerald-600">Salvar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal Adicionar Atleta */}
        <Dialog open={showAddAtletaModal} onOpenChange={setShowAddAtletaModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Cadastrar Novo Atleta</DialogTitle>
            </DialogHeader>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Nome *</Label>
                <Input value={novoAtleta.nome} onChange={(e) => setNovoAtleta({...novoAtleta, nome: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>Email *</Label>
                <Input value={novoAtleta.email} onChange={(e) => setNovoAtleta({...novoAtleta, email: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>Equipe</Label>
                <Input value={novoAtleta.equipe} onChange={(e) => setNovoAtleta({...novoAtleta, equipe: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>Cidade *</Label>
                <Input value={novoAtleta.cidade} onChange={(e) => setNovoAtleta({...novoAtleta, cidade: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>UF</Label>
                <Select value={novoAtleta.estado} onValueChange={(v) => setNovoAtleta({...novoAtleta, estado: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {ESTADOS_BR.map((uf) => <SelectItem key={uf} value={uf}>{uf}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Categoria</Label>
                <Select value={novoAtleta.categoria} onValueChange={(v) => setNovoAtleta({...novoAtleta, categoria: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="pcd">PCD</SelectItem>
                    <SelectItem value="cadeirante">Cadeirante</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Gênero</Label>
                <Select value={novoAtleta.genero} onValueChange={(v) => setNovoAtleta({...novoAtleta, genero: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="M">Masculino</SelectItem>
                    <SelectItem value="F">Feminino</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Data de Nascimento *</Label>
                <Input type="date" value={novoAtleta.data_nascimento} onChange={(e) => setNovoAtleta({...novoAtleta, data_nascimento: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>Telefone *</Label>
                <Input value={novoAtleta.telefone} onChange={(e) => setNovoAtleta({...novoAtleta, telefone: e.target.value})} placeholder="(00) 00000-0000" data-testid="admin-input-telefone" />
              </div>
              <div className="space-y-2">
                <Label>Tipo de Corredor *</Label>
                <Select value={novoAtleta.tipo_corredor} onValueChange={(v) => setNovoAtleta({...novoAtleta, tipo_corredor: v})}>
                  <SelectTrigger data-testid="admin-select-tipo-corredor">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="velocista"><span><strong className="uppercase">VELOCISTA</strong> <span className="text-xs text-slate-500">- provas curtas até 5km</span></span></SelectItem>
                    <SelectItem value="resistencia"><span><strong className="uppercase">RESISTÊNCIA</strong> <span className="text-xs text-slate-500">- provas mais longas até 21km</span></span></SelectItem>
                    <SelectItem value="endurance"><span><strong className="uppercase">ENDURANCE</strong> <span className="text-xs text-slate-500">- provas acima de 42km</span></span></SelectItem>
                    <SelectItem value="pace_leve"><span><strong className="uppercase">PACE LEVE</strong> <span className="text-xs text-slate-500">- Corro por Diversão</span></span></SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Terreno Preferido *</Label>
                <Select value={novoAtleta.terreno_preferido} onValueChange={(v) => setNovoAtleta({...novoAtleta, terreno_preferido: v})}>
                  <SelectTrigger data-testid="admin-select-terreno">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rua_asfalto">Rua - Asfalto</SelectItem>
                    <SelectItem value="trilha">Trilha</SelectItem>
                    <SelectItem value="esteira">Esteira</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Modalidade de Participação */}
            <div className="pt-3 border-t">
              <Label className="text-base font-semibold">Modalidade de Participação *</Label>
              <p className="text-xs text-slate-500 mb-3">Escolha como o atleta irá competir no Ranking Run Pró</p>
              <div className="grid grid-cols-2 gap-3">
                <div
                  onClick={() => setNovoAtleta({...novoAtleta, modalidade_usuario: 'profissional_amador'})}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    novoAtleta.modalidade_usuario === 'profissional_amador'
                      ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                  data-testid="admin-modalidade-profissional"
                >
                  <p className="font-bold text-sm">Atleta Profissional / Amador</p>
                  <p className="text-xs text-slate-500 mt-1">Pontuação baseada em colocação (1° a 10° lugar)</p>
                </div>
                <div
                  onClick={() => setNovoAtleta({...novoAtleta, modalidade_usuario: 'povao_pace_livre'})}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    novoAtleta.modalidade_usuario === 'povao_pace_livre'
                      ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                  data-testid="admin-modalidade-galera"
                >
                  <p className="font-bold text-sm">Ranking da Galera</p>
                  <p className="text-xs text-slate-500 mt-1">Pontuação baseada apenas na distância percorrida</p>
                </div>
              </div>
            </div>

            <p className="text-sm text-slate-500">Senha padrão: atleta123</p>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowAddAtletaModal(false)}>Cancelar</Button>
              <Button onClick={handleAddAtleta} disabled={actionLoading} className="bg-emerald-600">Cadastrar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal de Visualização da Foto do Pódio */}
        <Dialog open={showFotoModal} onOpenChange={setShowFotoModal}>
          <DialogContent className="max-w-4xl p-0 bg-black/90">
            <div className="relative">
              <Button
                variant="ghost"
                size="icon"
                className="absolute top-2 right-2 z-10 bg-black/50 hover:bg-black/70 text-white"
                onClick={() => setShowFotoModal(false)}
              >
                <X className="w-6 h-6" />
              </Button>
              {fotoModalUrl && (
                <img 
                  src={fotoModalUrl}
                  alt="Foto do Pódio - Ampliada"
                  className="w-full h-auto max-h-[85vh] object-contain rounded-lg"
                  data-testid="foto-podio-modal"
                />
              )}
            </div>
          </DialogContent>
        </Dialog>

        {/* Modal de Transferência de Modalidade */}
        <Dialog open={showTransferModal} onOpenChange={setShowTransferModal}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="text-xl flex items-center gap-2">
                <ArrowRightLeft className="w-5 h-5 text-purple-500" />
                Transferir Modalidade
              </DialogTitle>
            </DialogHeader>
            
            {atletaTransferindo && (
              <div className="space-y-4">
                {/* Info do Atleta */}
                <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={atletaTransferindo.foto_url?.startsWith('http') ? atletaTransferindo.foto_url : `${BACKEND_URL}${atletaTransferindo.foto_url}`} />
                      <AvatarFallback className="bg-emerald-600 text-white">
                        {atletaTransferindo.nome?.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold">{atletaTransferindo.nome}</h3>
                      <p className="text-sm text-slate-500">{atletaTransferindo.equipe || 'Sem equipe'}</p>
                    </div>
                  </div>
                </div>

                {/* Seta de Transferência */}
                <div className="flex items-center justify-center gap-4 py-2">
                  <div className={`px-4 py-2 rounded-lg text-center ${
                    atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-emerald-100 text-emerald-700'
                  }`}>
                    <p className="text-xs font-medium">Atual</p>
                    <p className="font-semibold">
                      {atletaTransferindo.modalidade_usuario === 'povao_pace_livre' ? 'Ranking da Galera' : 'Profissional/Amador'}
                    </p>
                  </div>
                  
                  <ArrowRightLeft className="w-6 h-6 text-slate-400" />
                  
                  <div className={`px-4 py-2 rounded-lg text-center ${
                    atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                      ? 'bg-emerald-100 text-emerald-700'
                      : 'bg-purple-100 text-purple-700'
                  }`}>
                    <p className="text-xs font-medium">Nova</p>
                    <p className="font-semibold">
                      {atletaTransferindo.modalidade_usuario === 'povao_pace_livre' ? 'Profissional/Amador' : 'Ranking da Galera'}
                    </p>
                  </div>
                </div>

                {/* Aviso Importante */}
                <Alert className={`${
                  atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                    ? 'bg-emerald-50 border-emerald-200'
                    : 'bg-purple-50 border-purple-200'
                }`}>
                  <AlertCircle className={`w-4 h-4 ${
                    atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                      ? 'text-emerald-600'
                      : 'text-purple-600'
                  }`} />
                  <AlertDescription className={`${
                    atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                      ? 'text-emerald-800'
                      : 'text-purple-800'
                  }`}>
                    {atletaTransferindo.modalidade_usuario === 'povao_pace_livre' ? (
                      <>
                        <strong>Galera → Profissional/Amador:</strong><br />
                        Os pontos serão recalculados baseados na <strong>colocação</strong> de cada corrida.
                        Se a colocação original não pontuava (acima de 10º lugar), a corrida terá 0 pontos.
                      </>
                    ) : (
                      <>
                        <strong>Profissional/Amador → Galera:</strong><br />
                        Os pontos serão recalculados baseados na <strong>distância</strong> de cada corrida:
                        <ul className="list-disc list-inside mt-1 text-sm">
                          <li>5km a 9km = 5 pontos</li>
                          <li>10km a 20km = 7 pontos</li>
                          <li>21km ou mais = 9 pontos</li>
                        </ul>
                      </>
                    )}
                  </AlertDescription>
                </Alert>

                {/* Confirmação */}
                <div className="p-3 bg-amber-50 dark:bg-amber-900/30 rounded-lg border border-amber-200">
                  <p className="text-sm text-amber-800 dark:text-amber-200">
                    <strong>Atenção:</strong> Esta ação irá remover o atleta do ranking atual e 
                    recalcular todos os pontos baseado na nova modalidade. O atleta receberá uma 
                    notificação sobre a transferência.
                  </p>
                </div>
              </div>
            )}

            <DialogFooter className="gap-2">
              <Button 
                variant="outline" 
                onClick={() => {
                  setShowTransferModal(false);
                  setAtletaTransferindo(null);
                }}
                disabled={transferLoading}
              >
                Cancelar
              </Button>
              <Button 
                onClick={handleTransferirModalidade}
                disabled={transferLoading}
                className={`${
                  atletaTransferindo?.modalidade_usuario === 'povao_pace_livre'
                    ? 'bg-emerald-600 hover:bg-emerald-700'
                    : 'bg-purple-600 hover:bg-purple-700'
                }`}
              >
                {transferLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Transferindo...
                  </>
                ) : (
                  <>
                    <ArrowRightLeft className="w-4 h-4 mr-2" />
                    Confirmar Transferência
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal Cadastrar/Editar Corrida */}
        <Dialog open={showCorridaModal} onOpenChange={setShowCorridaModal}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                {corridaEditando ? <Edit className="w-5 h-5 text-blue-500" /> : <Plus className="w-5 h-5 text-emerald-500" />}
                {corridaEditando ? 'Editar Corrida' : 'Cadastrar Nova Corrida'}
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Nome da Corrida *</Label>
                <Input
                  value={corridaFormData.nome_corrida}
                  onChange={(e) => setCorridaFormData({...corridaFormData, nome_corrida: e.target.value})}
                  placeholder="Ex: Maratona de São Paulo"
                />
              </div>
              <div>
                <Label>Organizador / Empresa *</Label>
                <Input
                  value={corridaFormData.organizador}
                  onChange={(e) => setCorridaFormData({...corridaFormData, organizador: e.target.value})}
                  placeholder="Ex: Yescom"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Estado *</Label>
                  <Select value={corridaFormData.estado} onValueChange={(v) => setCorridaFormData({...corridaFormData, estado: v})}>
                    <SelectTrigger>
                      <SelectValue placeholder="UF" />
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
                  <Input
                    value={corridaFormData.cidade}
                    onChange={(e) => setCorridaFormData({...corridaFormData, cidade: e.target.value})}
                    placeholder="Cidade"
                  />
                </div>
              </div>
              <div>
                <Label>Data da Corrida *</Label>
                <Input
                  type="date"
                  value={corridaFormData.data_corrida}
                  onChange={(e) => setCorridaFormData({...corridaFormData, data_corrida: e.target.value})}
                />
              </div>
              <div>
                <Label>Link da Página (Instagram ou Site)</Label>
                <Input
                  value={corridaFormData.pagina_link}
                  onChange={(e) => setCorridaFormData({...corridaFormData, pagina_link: e.target.value})}
                  placeholder="https://..."
                />
              </div>
              <div>
                <Label>Status</Label>
                <Select value={corridaFormData.status} onValueChange={(v) => setCorridaFormData({...corridaFormData, status: v})}>
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
            <DialogFooter>
              <Button variant="outline" onClick={() => { setShowCorridaModal(false); setCorridaEditando(null); }}>
                Cancelar
              </Button>
              <Button onClick={handleSalvarCorrida} className="bg-emerald-500 hover:bg-emerald-600">
                {corridaEditando ? 'Salvar Alterações' : 'Cadastrar Corrida'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal de Promover a Dono de Assessoria */}
        <Dialog open={showPromoverModal} onOpenChange={setShowPromoverModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Crown className="w-5 h-5 text-amber-500" />
                Promover a Dono de Assessoria
              </DialogTitle>
            </DialogHeader>
            {atletaAcao && (
              <div className="space-y-4">
                <p className="text-slate-300">
                  Deseja promover <span className="font-semibold text-white">{atletaAcao.nome}</span> a Dono de Assessoria?
                </p>
                <div className="p-3 bg-slate-800 rounded-lg">
                  <p className="text-sm text-slate-400">Assessoria: <span className="text-white">{atletaAcao.equipe}</span></p>
                  <p className="text-sm text-slate-400 mt-1">Email: <span className="text-white">{atletaAcao.email}</span></p>
                </div>
                <p className="text-xs text-amber-400">
                  Ao promover, este atleta terá acesso ao painel de gerenciamento da assessoria.
                </p>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowPromoverModal(false)}>
                Cancelar
              </Button>
              <Button 
                onClick={handlePromoverDonoAssessoria} 
                disabled={promoverLoading}
                className="bg-amber-500 hover:bg-amber-600"
              >
                {promoverLoading ? (
                  <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Promovendo...</>
                ) : (
                  <><Crown className="w-4 h-4 mr-2" /> Promover</>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal de Enviar Mensagem Individual */}
        <Dialog open={showMensagemModal} onOpenChange={setShowMensagemModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-500" />
                Enviar Mensagem
              </DialogTitle>
            </DialogHeader>
            {atletaAcao && (
              <div className="space-y-4">
                <p className="text-slate-300">
                  Enviar mensagem para <span className="font-semibold text-white">{atletaAcao.nome}</span>
                </p>
                <Textarea
                  value={mensagemAdmin}
                  onChange={(e) => setMensagemAdmin(e.target.value)}
                  placeholder="Digite sua mensagem..."
                  rows={4}
                  className="bg-slate-900 border-slate-600 text-white"
                />
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowMensagemModal(false)}>
                Cancelar
              </Button>
              <Button 
                onClick={handleEnviarMensagemIndividual}
                disabled={sendingMensagem || !mensagemAdmin.trim()}
                className="bg-blue-500 hover:bg-blue-600"
              >
                {sendingMensagem ? (
                  <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Enviando...</>
                ) : (
                  <><Send className="w-4 h-4 mr-2" /> Enviar</>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default AdminDashboard;
