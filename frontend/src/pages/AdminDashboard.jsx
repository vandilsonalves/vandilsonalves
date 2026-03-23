import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { 
  CheckCircle, XCircle, ExternalLink, Calendar, MapPin, Trophy, Clock, 
  Users, AlertCircle, TrendingUp, BarChart3, PieChart, Shield,
  Activity, Home, Settings, FileText, Bell, ChevronRight, Award, Database,
  UserPlus, Edit, Trash2, Eye, Download, Plus, Minus, Search, Image, X,
  Cake, Send, Gift, ChevronLeft, ArrowRightLeft, RefreshCw, Loader2,
  Crown, MessageSquare
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  PieChart as RechartsPie, Pie, Cell, LineChart, Line, AreaChart, Area,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar as RechartsRadar
} from 'recharts';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

// Menu items para sidebar com permissões necessárias
import { Instagram, Radar, Star } from 'lucide-react';

// Import dos novos dashboards modulares
import { 
  DashboardGeral, 
  DashboardAtletas, 
  DashboardAssessorias, 
  DashboardCorridas, 
  DashboardResultados,
  DashboardRBAC
} from './admin';
import DashboardMonitoramento from './admin/dashboards/DashboardMonitoramento';
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
  
  // Submeter Resultado (Admin) - Novo formato completo
  const [atletaSelecionado, setAtletaSelecionado] = useState('');
  const [tipoOperacao, setTipoOperacao] = useState('adicionar');
  const [corridasAtleta, setCorridasAtleta] = useState([]);
  const [corridaSelecionada, setCorridaSelecionada] = useState(null);
  const [showEditCorridaModal, setShowEditCorridaModal] = useState(false);
  
  // Form para nova corrida (admin)
  const [novaCorridaAdmin, setNovaCorridaAdmin] = useState({
    nome_competicao: '',
    colocacao: '',
    distancia: '',
    cidade_competicao: '',
    estado_competicao: '',
    data_competicao: '',
    tempo: '',
    link_resultado: ''
  });
  
  // Modal
  const [showReprovarModal, setShowReprovarModal] = useState(false);
  const [selectedResultado, setSelectedResultado] = useState(null);
  const [motivoReprovacao, setMotivoReprovacao] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  // Form para novo atleta
  const [novoAtleta, setNovoAtleta] = useState({
    nome: '', email: '', password: 'atleta123', equipe: '',
    cidade: '', estado: 'SP', genero: 'M', categoria: 'normal',
    data_nascimento: '', etnia: '', apelido: ''
  });

  // Aniversariantes
  const [aniversariantesMes, setAniversariantesMes] = useState(null);
  const [mesCalendario, setMesCalendario] = useState(new Date().getMonth() + 1);
  const [anoCalendario, setAnoCalendario] = useState(new Date().getFullYear());
  const [diaSelecionado, setDiaSelecionado] = useState(null);
  const [mensagemPadrao, setMensagemPadrao] = useState('Feliz Aniversário! 🎂 Que este novo ciclo traga muitas conquistas nas pistas. O Ranking Run Pró deseja a você muita saúde e velocidade! 🏃‍♂️');
  const [atletasSelecionar, setAtletasSelecionar] = useState([]);
  const [loadingAniversariantes, setLoadingAniversariantes] = useState(false);
  const [envioAutomatico, setEnvioAutomatico] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);

  // Instagram Analytics (Ranking Run Inside)
  const [instagramAnalises, setInstagramAnalises] = useState([]);
  const [loadingInstagram, setLoadingInstagram] = useState(false);
  const [showInstagramForm, setShowInstagramForm] = useState(false);
  const [instagramResult, setInstagramResult] = useState(null);
  const [instagramSearchUsername, setInstagramSearchUsername] = useState('');
  const [instagramSearchLoading, setInstagramSearchLoading] = useState(false);
  const [instagramSearchError, setInstagramSearchError] = useState('');
  const [instagramFormData, setInstagramFormData] = useState({
    username: '',
    nome_completo: '',
    nicho: 'corrida',
    seguidores: '',
    seguindo: '',
    total_posts: '',
    bio: ''
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

  // Regulamento
  const [regulamento, setRegulamento] = useState({ titulo: '', conteudo: '' });
  const [loadingRegulamento, setLoadingRegulamento] = useState(false);
  const [savingRegulamento, setSavingRegulamento] = useState(false);

  // Autorizações
  const [atletasPeriodoTeste, setAtletasPeriodoTeste] = useState([]);
  const [loadingAutorizacoes, setLoadingAutorizacoes] = useState(false);
  const [showAutorizacaoModal, setShowAutorizacaoModal] = useState(false);
  const [atletaAutorizando, setAtletaAutorizando] = useState(null);
  const [tipoAutorizacao, setTipoAutorizacao] = useState('6_meses');
  const [observacaoAutorizacao, setObservacaoAutorizacao] = useState('');
  const [savingAutorizacao, setSavingAutorizacao] = useState(false);
  const [filtroStatusAutorizacao, setFiltroStatusAutorizacao] = useState('todos');
  const [showCarteirinhaModal, setShowCarteirinhaModal] = useState(false);
  const [carteirinhaData, setCarteirinhaData] = useState(null);
  
  // Seleção múltipla de autorizações
  const [atletasSelecionados, setAtletasSelecionados] = useState([]);
  const [aprovandoEmMassa, setAprovandoEmMassa] = useState(false);

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

  const MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

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
    if (activeMenu === 'aniversariantes') {
      fetchAniversariantes();
      fetchConfigAniversario();
    }
    if (activeMenu === 'instagram') {
      fetchInstagramAnalises();
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
    if (activeMenu === 'regulamento') {
      fetchRegulamento();
    }
    if (activeMenu === 'autorizacoes') {
      fetchAtletasPeriodoTeste();
    }
  }, [activeMenu, filtroCategoria, filtroEquipe, mesCalendario, anoCalendario, ligaTipo, ligaEstado, ligaCidade]);

  // Buscar corridas do atleta quando selecionar para remover
  useEffect(() => {
    if (atletaSelecionado && tipoOperacao === 'remover') {
      fetchCorridasAtleta(atletaSelecionado);
    }
  }, [atletaSelecionado, tipoOperacao]);

  const fetchCorridasAtleta = async (atletaId) => {
    try {
      const response = await axios.get(`${API}/atletas/${atletaId}/corridas`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCorridasAtleta(response.data);
    } catch (error) {
      console.error('Erro ao buscar corridas:', error);
    }
  };

  const fetchAllData = async () => {
    // Executar de forma independente para não bloquear um ao outro
    fetchStats();
    fetchPendentes();
  };

  // Funções de Regulamento
  const fetchRegulamento = async () => {
    setLoadingRegulamento(true);
    try {
      const response = await axios.get(`${API}/admin/regulamento`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRegulamento(response.data);
    } catch (error) {
      console.error('Erro ao buscar regulamento:', error);
      toast.error('Erro ao carregar regulamento');
    } finally {
      setLoadingRegulamento(false);
    }
  };

  const handleSaveRegulamento = async () => {
    if (!regulamento.titulo.trim() || !regulamento.conteudo.trim()) {
      toast.error('Preencha o título e o conteúdo do regulamento');
      return;
    }
    
    setSavingRegulamento(true);
    try {
      const formData = new FormData();
      formData.append('titulo', regulamento.titulo);
      formData.append('conteudo', regulamento.conteudo);
      
      await axios.put(`${API}/admin/regulamento`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Regulamento salvo com sucesso!');
      fetchRegulamento(); // Recarregar para atualizar a data
    } catch (error) {
      console.error('Erro ao salvar regulamento:', error);
      toast.error('Erro ao salvar regulamento');
    } finally {
      setSavingRegulamento(false);
    }
  };

  // Funções de Autorizações
  const fetchAtletasPeriodoTeste = async () => {
    setLoadingAutorizacoes(true);
    try {
      const response = await axios.get(`${API}/admin/atletas-periodo-teste`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAtletasPeriodoTeste(response.data);
    } catch (error) {
      console.error('Erro ao buscar atletas:', error);
      toast.error('Erro ao carregar lista de atletas');
    } finally {
      setLoadingAutorizacoes(false);
    }
  };

  const handleCriarAutorizacao = async () => {
    if (!atletaAutorizando) return;
    
    setSavingAutorizacao(true);
    try {
      const formData = new FormData();
      formData.append('atleta_id', atletaAutorizando.id);
      formData.append('tipo_autorizacao', tipoAutorizacao);
      formData.append('observacao', observacaoAutorizacao);
      
      const response = await axios.post(`${API}/admin/autorizacoes`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(response.data.message);
      setShowAutorizacaoModal(false);
      setAtletaAutorizando(null);
      setTipoAutorizacao('6_meses');
      setObservacaoAutorizacao('');
      fetchAtletasPeriodoTeste();
    } catch (error) {
      console.error('Erro ao criar autorização:', error);
      toast.error(error.response?.data?.detail || 'Erro ao criar autorização');
    } finally {
      setSavingAutorizacao(false);
    }
  };

  const handleRevogarAutorizacao = async (autorizacaoId) => {
    if (!confirm('Tem certeza que deseja revogar esta autorização?')) return;
    
    try {
      await axios.delete(`${API}/admin/autorizacoes/${autorizacaoId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Autorização revogada com sucesso');
      fetchAtletasPeriodoTeste();
    } catch (error) {
      console.error('Erro ao revogar autorização:', error);
      toast.error('Erro ao revogar autorização');
    }
  };

  const handleGerarCarteirinha = async (atletaId) => {
    try {
      const response = await axios.get(`${API}/admin/carteirinha/${atletaId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCarteirinhaData(response.data);
      setShowCarteirinhaModal(true);
    } catch (error) {
      console.error('Erro ao gerar carteirinha:', error);
      toast.error(error.response?.data?.detail || 'Erro ao gerar carteirinha');
    }
  };

  // Funções de seleção múltipla para autorizações
  const handleToggleSelectAtleta = (atletaId) => {
    setAtletasSelecionados(prev => 
      prev.includes(atletaId) 
        ? prev.filter(id => id !== atletaId)
        : [...prev, atletaId]
    );
  };

  const handleSelectAll = () => {
    // Selecionar apenas os que não estão autorizados
    const atletasNaoAutorizados = filteredAtletasAutorizacao
      .filter(a => a.status_periodo !== 'autorizado')
      .map(a => a.id);
    
    if (atletasSelecionados.length === atletasNaoAutorizados.length) {
      setAtletasSelecionados([]);
    } else {
      setAtletasSelecionados(atletasNaoAutorizados);
    }
  };

  const handleAprovarEmMassa = async () => {
    if (atletasSelecionados.length === 0) {
      toast.error('Selecione pelo menos um atleta');
      return;
    }

    if (!confirm(`Deseja autorizar ${atletasSelecionados.length} atleta(s) selecionado(s)?`)) return;

    setAprovandoEmMassa(true);
    let aprovados = 0;
    let erros = 0;

    for (const atletaId of atletasSelecionados) {
      try {
        const formData = new FormData();
        formData.append('atleta_id', atletaId);
        formData.append('tipo_autorizacao', tipoAutorizacao);
        formData.append('observacao', 'Aprovação em massa');

        await axios.post(`${API}/admin/autorizacoes`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        aprovados++;
      } catch (error) {
        console.error(`Erro ao autorizar atleta ${atletaId}:`, error);
        erros++;
      }
    }

    if (aprovados > 0) {
      toast.success(`${aprovados} atleta(s) autorizado(s) com sucesso!`);
    }
    if (erros > 0) {
      toast.error(`${erros} atleta(s) não puderam ser autorizados`);
    }

    setAtletasSelecionados([]);
    setAprovandoEmMassa(false);
    fetchAtletasPeriodoTeste();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'em_teste': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'autorizado': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'expirado': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'em_teste': return 'Em Teste';
      case 'autorizado': return 'Autorizado';
      case 'expirado': return 'Expirado';
      default: return 'Desconhecido';
    }
  };

  const filteredAtletasAutorizacao = atletasPeriodoTeste.filter(atleta => {
    if (filtroStatusAutorizacao === 'todos') return true;
    return atleta.status_periodo === filtroStatusAutorizacao;
  });

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      // Usar Promise.allSettled para não bloquear se uma requisição falhar
      const results = await Promise.allSettled([
        axios.get(`${API}/admin/stats`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/estados`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/categorias`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/faixa-etaria`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/corridas-por-mes`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/ranking/povao/stats`),
        axios.get(`${API}/admin/stats/etnia`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/equipes-por-estado`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/donos-por-estado`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/assessorias-verificadas`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/insignias`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      // Extrair dados apenas de requisições bem-sucedidas
      const [statsRes, estadosRes, categoriasRes, faixaRes, corridasRes, povaoRes, etniaRes, equipesPorEstadoRes, donosEstadoRes, assessoriasVerificadasRes, insigniasRes] = results;
      
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (estadosRes.status === 'fulfilled') setStatsEstados(estadosRes.value.data);
      if (categoriasRes.status === 'fulfilled') setStatsCategorias(categoriasRes.value.data);
      if (faixaRes.status === 'fulfilled') setStatsFaixa(faixaRes.value.data);
      if (corridasRes.status === 'fulfilled') setCorridasPorMes(corridasRes.value.data);
      if (povaoRes.status === 'fulfilled') setStatsPovao(povaoRes.value.data);
      if (etniaRes.status === 'fulfilled') setStatsEtnia(etniaRes.value.data);
      if (equipesPorEstadoRes.status === 'fulfilled') setStatsEquipesPorEstado(equipesPorEstadoRes.value.data);
      if (donosEstadoRes.status === 'fulfilled') setStatsDonosPorEstado(donosEstadoRes.value.data);
      if (assessoriasVerificadasRes.status === 'fulfilled') setStatsAssessoriasVerificadas(assessoriasVerificadasRes.value.data);
      if (insigniasRes.status === 'fulfilled') setStatsInsignias(insigniasRes.value.data);
      
      // Calcular estatísticas de equipes a partir dos atletas
      try {
        const atletasRes = await axios.get(`${API}/admin/atletas`, { headers: { Authorization: `Bearer ${token}` } });
        const atletas = atletasRes.data;
        
        // Contar por equipe
        const equipesCount = {};
        let profissionalCount = 0;
        let povaoCount = 0;
        
        atletas.forEach(a => {
          const equipe = a.equipe || 'Sem equipe';
          equipesCount[equipe] = (equipesCount[equipe] || 0) + 1;
          
          // Contar modalidades
          if (a.modalidade_usuario === 'povao_pace_livre') {
            povaoCount++;
          } else {
            profissionalCount++;
          }
        });
        
        // Converter para array e ordenar por quantidade
        const equipesArray = Object.entries(equipesCount)
          .map(([equipe, total]) => ({ equipe, total }))
          .sort((a, b) => b.total - a.total)
          .slice(0, 10); // Top 10 equipes
        
        setStatsEquipes(equipesArray);
        setStatsModalidade({ profissional: profissionalCount, povao: povaoCount });
      } catch (err) {
        console.error('Erro ao processar atletas:', err);
      }
      
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

  const fetchAniversariantes = async () => {
    setLoadingAniversariantes(true);
    try {
      const response = await axios.get(`${API}/admin/aniversariantes`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { mes: mesCalendario, ano: anoCalendario }
      });
      setAniversariantesMes(response.data);
    } catch (error) {
      console.error('Erro ao buscar aniversariantes:', error);
    } finally {
      setLoadingAniversariantes(false);
    }
  };

  const handleEnviarMensagemAniversario = async () => {
    if (atletasSelecionar.length === 0) {
      toast.error('Erro', { description: 'Selecione pelo menos um atleta' });
      return;
    }

    try {
      await axios.post(`${API}/admin/aniversariantes/enviar-mensagem`, {
        atleta_ids: atletasSelecionar,
        mensagem: mensagemPadrao
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Ação Concluída', { description: `Mensagem enviada para ${atletasSelecionar.length} atleta(s)!` });
      setAtletasSelecionar([]);
      setDiaSelecionado(null);
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao enviar mensagem' });
    }
  };

  const toggleAtletaSelecao = (atletaId) => {
    setAtletasSelecionar(prev => 
      prev.includes(atletaId) 
        ? prev.filter(id => id !== atletaId)
        : [...prev, atletaId]
    );
  };

  const getDiasNoMes = (mes, ano) => {
    return new Date(ano, mes, 0).getDate();
  };

  const getPrimeiroDiaSemana = (mes, ano) => {
    return new Date(ano, mes - 1, 1).getDay();
  };

  const fetchConfigAniversario = async () => {
    try {
      const response = await axios.get(`${API}/admin/aniversariantes/configuracao`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensagemPadrao(response.data.mensagem_padrao || '');
      setEnvioAutomatico(response.data.envio_automatico || false);
    } catch (error) {
      console.error('Erro ao buscar configuração:', error);
    }
  };

  const handleSalvarConfigAniversario = async () => {
    try {
      await axios.put(`${API}/admin/aniversariantes/configuracao`, {
        mensagem_padrao: mensagemPadrao,
        envio_automatico: envioAutomatico
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Ação Concluída', { 
        description: `Configurações salvas! Envio automático ${envioAutomatico ? 'ATIVADO' : 'DESATIVADO'}` 
      });
      setShowConfigModal(false);
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao salvar configuração' });
    }
  };

  const handleEnviarAniversariosAgora = async () => {
    try {
      const response = await axios.post(`${API}/admin/aniversariantes/enviar-agora`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = response.data;
      toast.success('Ação Concluída', { 
        description: `${data.mensagens_enviadas} mensagem(s) enviada(s). ${data.ja_enviadas_anteriormente} já enviada(s) anteriormente.` 
      });
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao enviar mensagens' });
    }
  };

  // ===== INSTAGRAM ANALYTICS (RANKING RUN INSIDE) =====
  const fetchInstagramAnalises = async () => {
    setLoadingInstagram(true);
    try {
      const response = await axios.get(`${API}/admin/instagram/analises`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInstagramAnalises(response.data);
    } catch (error) {
      console.error('Erro ao buscar análises Instagram:', error);
    } finally {
      setLoadingInstagram(false);
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

  const renderStarsAdmin = (rating) => {
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        <Star key={i} className={`w-4 h-4 ${i < Math.floor(rating) ? 'fill-yellow-400 text-yellow-400' : 'text-slate-300'}`} />
      );
    }
    return <div className="flex">{stars}</div>;
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

  // Função para buscar e analisar automaticamente do Instagram
  const handleInstagramSearch = async () => {
    if (!instagramSearchUsername.trim()) {
      toast.error('Username obrigatório', { description: 'Digite o @username do perfil' });
      return;
    }

    setInstagramSearchLoading(true);
    setInstagramSearchError('');

    try {
      const cleanUsername = instagramSearchUsername.trim().replace('@', '');
      
      // Chamar o endpoint de análise automática
      const response = await axios.post(
        `${API}/admin/instagram/analisar-automatico/${cleanUsername}?nicho=${instagramFormData.nicho}`, 
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Mostrar resultado direto
      setInstagramResult(response.data);
      setInstagramSearchUsername('');
      fetchInstagramAnalises();
      toast.success('Análise Completa!', { 
        description: `@${cleanUsername}: Score ${response.data.analysis.score_final}/100 - ${response.data.analysis.classificacao}` 
      });

    } catch (error) {
      const errorMsg = typeof error.response?.data?.detail === 'string' 
        ? error.response?.data?.detail 
        : 'Não foi possível analisar o perfil. Verifique se o username está correto.';
      setInstagramSearchError(errorMsg);
      toast.error('Erro na Análise', { description: errorMsg });
    } finally {
      setInstagramSearchLoading(false);
    }
  };

  // Função para análise com dados básicos (Sistema Híbrido)
  const handleInstagramAnalyze = async () => {
    // Validar apenas campos essenciais
    const required = ['username', 'seguidores', 'seguindo', 'total_posts'];
    const missing = required.filter(field => !instagramFormData[field]);
    
    if (missing.length > 0) {
      toast.error('Campos obrigatórios', { description: 'Preencha: Username, Seguidores, Seguindo e Total de Posts' });
      return;
    }

    setLoadingInstagram(true);
    try {
      const payload = {
        username: instagramFormData.username,
        nome_completo: instagramFormData.nome_completo || '',
        nicho: instagramFormData.nicho || 'corrida',
        seguidores: parseInt(instagramFormData.seguidores) || 0,
        seguindo: parseInt(instagramFormData.seguindo) || 0,
        total_posts: parseInt(instagramFormData.total_posts) || 0,
        bio: instagramFormData.bio || ''
      };

      const response = await axios.post(`${API}/admin/instagram/analisar-simplificado`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setInstagramResult(response.data);
      setShowInstagramForm(false);
      setInstagramSearchUsername('');
      fetchInstagramAnalises();
      toast.success('Análise Concluída!', { 
        description: `Score: ${response.data.analysis.score_final}/100 - ${response.data.analysis.classificacao}` 
      });
    } catch (error) {
      let errorMsg = 'Erro ao analisar perfil';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMsg = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMsg = error.response.data.detail.map(e => e.msg || e.message || 'Erro de validação').join(', ');
        }
      }
      toast.error('Erro na Análise', { description: errorMsg });
    } finally {
      setLoadingInstagram(false);
    }
  };

  const handleDeleteInstagramAnalysis = async (analysisId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta análise?')) return;
    
    try {
      await axios.delete(`${API}/admin/instagram/analises/${analysisId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Ação Concluída', { description: 'Análise excluída!' });
      fetchInstagramAnalises();
      if (instagramResult?.analysis?.id === analysisId) {
        setInstagramResult(null);
      }
    } catch (error) {
      toast.error('Erro', { description: 'Erro ao excluir análise' });
    }
  };

  const handleExportInstagram = async (analysisId, format) => {
    const endpoint = format === 'xlsx' 
      ? `${API}/admin/instagram/export/${analysisId}`
      : `${API}/admin/instagram/export-csv/${analysisId}`;
    
    window.open(endpoint + `?token=${token}`, '_blank');
  };

  const getClassificacaoColor = (classificacao) => {
    const colors = {
      'Elite Platinum': 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white',
      'Elite Gold': 'bg-gradient-to-r from-yellow-500 to-amber-500 text-white',
      'Premium': 'bg-gradient-to-r from-purple-500 to-violet-500 text-white',
      'Profissional': 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white',
      'Regular': 'bg-gradient-to-r from-slate-500 to-gray-500 text-white',
      'Alto Risco': 'bg-gradient-to-r from-red-500 to-rose-500 text-white'
    };
    return colors[classificacao] || 'bg-slate-500 text-white';
  };

  const resetInstagramForm = () => {
    setInstagramFormData({
      username: '',
      nome_completo: '',
      nicho: 'corrida',
      seguidores: '',
      seguindo: '',
      total_posts: '',
      bio: ''
    });
    setInstagramResult(null);
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
        data_nascimento: ''
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

  const handleSubmeterResultadoAdmin = async () => {
    if (!atletaSelecionado) {
      toast.error('Erro', { description: 'Selecione um atleta' });
      return;
    }

    if (tipoOperacao === 'adicionar') {
      // Validar campos obrigatórios
      if (!novaCorridaAdmin.nome_competicao || !novaCorridaAdmin.colocacao || !novaCorridaAdmin.distancia ||
          !novaCorridaAdmin.cidade_competicao || !novaCorridaAdmin.estado_competicao || 
          !novaCorridaAdmin.data_competicao || !novaCorridaAdmin.tempo) {
        toast.error('Erro', { description: 'Preencha todos os campos obrigatórios' });
        return;
      }

      setActionLoading(true);
      try {
        await axios.post(`${API}/admin/adicionar-corrida`, {
          atleta_id: atletaSelecionado,
          ...novaCorridaAdmin
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        toast.success('Ação Concluída', { description: 'Corrida adicionada com sucesso!' });
        setAtletaSelecionado('');
        setNovaCorridaAdmin({
          nome_competicao: '',
          colocacao: '',
          distancia: '',
          cidade_competicao: '',
          estado_competicao: '',
          data_competicao: '',
          tempo: '',
          link_resultado: ''
        });
        fetchStats();
      } catch (error) {
        toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao adicionar corrida' });
      } finally {
        setActionLoading(false);
      }
    }
  };

  const handleDeleteCorrida = async (corridaId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta corrida?')) return;
    
    try {
      await axios.delete(`${API}/admin/corridas/${corridaId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Ação Concluída', { description: 'Corrida excluída com sucesso!' });
      fetchCorridasAtleta(atletaSelecionado);
      fetchStats();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao excluir corrida' });
    }
  };

  const handleEditCorrida = async () => {
    if (!corridaSelecionada) return;
    
    setActionLoading(true);
    try {
      await axios.put(`${API}/admin/corridas/${corridaSelecionada.id}`, corridaSelecionada, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Ação Concluída', { description: 'Corrida atualizada com sucesso!' });
      setShowEditCorridaModal(false);
      setCorridaSelecionada(null);
      fetchCorridasAtleta(atletaSelecionado);
      fetchStats();
    } catch (error) {
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao atualizar corrida' });
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

  // Filtrar atletas por busca, modalidade e ordenar A-Z
  const filteredAtletas = atletas
    .filter(a => {
      const matchSearch = a.nome.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.equipe?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.cidade?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchModalidade = filtroModalidade === 'all' || 
        a.modalidade_usuario === filtroModalidade ||
        (filtroModalidade === 'profissional_amador' && !a.modalidade_usuario); // Default é profissional
      
      return matchSearch && matchModalidade;
    })
    .sort((a, b) => a.nome.localeCompare(b.nome));

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



        {/* Submeter Resultado View */}
        {activeMenu === 'submeter' && (
          <div className="max-w-4xl">
            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader>
                <CardTitle>Gerenciar Resultados do Atleta</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Selecionar Atleta</Label>
                  <Select value={atletaSelecionado} onValueChange={(v) => {
                    setAtletaSelecionado(v);
                    setCorridasAtleta([]);
                  }}>
                    <SelectTrigger>
                      <SelectValue placeholder="Buscar atleta..." />
                    </SelectTrigger>
                    <SelectContent>
                      {atletas.sort((a, b) => a.nome.localeCompare(b.nome)).map((a) => (
                        <SelectItem key={a.id} value={a.id}>{a.nome} - {a.equipe}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Tipo de Operação</Label>
                  <div className="flex gap-4">
                    <Button
                      variant={tipoOperacao === 'adicionar' ? 'default' : 'outline'}
                      onClick={() => setTipoOperacao('adicionar')}
                      className={tipoOperacao === 'adicionar' ? 'bg-emerald-600' : ''}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Adicionar Pontos
                    </Button>
                    <Button
                      variant={tipoOperacao === 'remover' ? 'default' : 'outline'}
                      onClick={() => setTipoOperacao('remover')}
                      className={tipoOperacao === 'remover' ? 'bg-red-600' : ''}
                    >
                      <Minus className="w-4 h-4 mr-2" />
                      Remover Pontos
                    </Button>
                  </div>
                </div>

                {/* Formulário para Adicionar Pontos */}
                {tipoOperacao === 'adicionar' && atletaSelecionado && (
                  <div className="border rounded-lg p-6 bg-slate-50 dark:bg-slate-900 space-y-4">
                    <h3 className="font-semibold text-lg flex items-center gap-2">
                      <Plus className="w-5 h-5 text-emerald-500" />
                      Adicionar Nova Corrida
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="md:col-span-2 space-y-2">
                        <Label>Nome da Competição *</Label>
                        <Input
                          value={novaCorridaAdmin.nome_competicao}
                          onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, nome_competicao: e.target.value})}
                          placeholder="Ex: Maratona de São Paulo"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Colocação *</Label>
                        <Input
                          type="number"
                          min="1"
                          max="10"
                          value={novaCorridaAdmin.colocacao}
                          onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, colocacao: e.target.value})}
                          placeholder="1 a 10"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Distância *</Label>
                        <Select 
                          value={novaCorridaAdmin.distancia} 
                          onValueChange={(v) => setNovaCorridaAdmin({...novaCorridaAdmin, distancia: v})}
                        >
                          <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="5KM">5 KM</SelectItem>
                            <SelectItem value="10KM">10 KM</SelectItem>
                            <SelectItem value="21KM">21 KM (Meia Maratona)</SelectItem>
                            <SelectItem value="42KM">42 KM (Maratona)</SelectItem>
                            <SelectItem value="OUTRA">Outra</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Cidade da Competição *</Label>
                        <Input
                          value={novaCorridaAdmin.cidade_competicao}
                          onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, cidade_competicao: e.target.value})}
                          placeholder="Ex: São Paulo"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Estado (UF) *</Label>
                        <Select 
                          value={novaCorridaAdmin.estado_competicao} 
                          onValueChange={(v) => setNovaCorridaAdmin({...novaCorridaAdmin, estado_competicao: v})}
                        >
                          <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
                          <SelectContent>
                            {ESTADOS_BR.map((uf) => <SelectItem key={uf} value={uf}>{uf}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Data da Competição *</Label>
                        <Input
                          type="date"
                          value={novaCorridaAdmin.data_competicao}
                          onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, data_competicao: e.target.value})}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Tempo (HH:MM:SS) *</Label>
                        <Input
                          type="time"
                          step="1"
                          value={novaCorridaAdmin.tempo}
                          onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, tempo: e.target.value})}
                        />
                      </div>
                      
                      <div className="md:col-span-2 space-y-2">
                        <Label>Link do Resultado (opcional)</Label>
                        <Input
                          type="url"
                          value={novaCorridaAdmin.link_resultado}
                          onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, link_resultado: e.target.value})}
                          placeholder="https://..."
                        />
                      </div>
                    </div>

                    <Button
                      onClick={handleSubmeterResultadoAdmin}
                      disabled={actionLoading}
                      className="w-full bg-emerald-600 mt-4"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Adicionar Corrida e Pontos
                    </Button>
                  </div>
                )}

                {/* Lista de Corridas para Remover */}
                {tipoOperacao === 'remover' && atletaSelecionado && (
                  <div className="border rounded-lg p-6 bg-slate-50 dark:bg-slate-900 space-y-4">
                    <h3 className="font-semibold text-lg flex items-center gap-2">
                      <Minus className="w-5 h-5 text-red-500" />
                      Corridas do Atleta (selecione para editar ou excluir)
                    </h3>
                    
                    {corridasAtleta.length === 0 ? (
                      <p className="text-slate-500 text-center py-4">Nenhuma corrida encontrada para este atleta.</p>
                    ) : (
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {corridasAtleta.map((corrida) => (
                          <div key={corrida.id} className="flex items-center justify-between p-4 bg-white dark:bg-slate-800 rounded-lg border">
                            <div className="flex-1">
                              <p className="font-medium">{corrida.nome}</p>
                              <div className="flex gap-4 text-sm text-slate-500 mt-1">
                                <span>{corrida.data}</span>
                                <span>{corrida.colocacao}º lugar</span>
                                <span>{corrida.distancia}</span>
                                <span className="font-semibold text-emerald-600">{corrida.pontos} pts</span>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setCorridaSelecionada(corrida);
                                  setShowEditCorridaModal(true);
                                }}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => handleDeleteCorrida(corrida.id)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Autorizações View */}
        {activeMenu === 'autorizacoes' && (
          <div className="space-y-6">
            {/* Header e Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                <CardContent className="p-4">
                  <p className="text-sm opacity-80">Em Teste</p>
                  <p className="text-3xl font-bold">
                    {atletasPeriodoTeste.filter(a => a.status_periodo === 'em_teste').length}
                  </p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
                <CardContent className="p-4">
                  <p className="text-sm opacity-80">Autorizados</p>
                  <p className="text-3xl font-bold">
                    {atletasPeriodoTeste.filter(a => a.status_periodo === 'autorizado').length}
                  </p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
                <CardContent className="p-4">
                  <p className="text-sm opacity-80">Expirados</p>
                  <p className="text-3xl font-bold">
                    {atletasPeriodoTeste.filter(a => a.status_periodo === 'expirado').length}
                  </p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                <CardContent className="p-4">
                  <p className="text-sm opacity-80">Total Atletas</p>
                  <p className="text-3xl font-bold">{atletasPeriodoTeste.length}</p>
                </CardContent>
              </Card>
            </div>

            {/* Filtros e Lista */}
            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader className="border-b dark:border-slate-700">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <CardTitle className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-emerald-500" />
                    Gerenciar Autorizações de Acesso
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    {/* Botão Aprovar Selecionados */}
                    {atletasSelecionados.length > 0 && (
                      <Button
                        onClick={handleAprovarEmMassa}
                        disabled={aprovandoEmMassa}
                        className="bg-emerald-500 hover:bg-emerald-600 text-white"
                      >
                        {aprovandoEmMassa ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <CheckCircle className="w-4 h-4 mr-2" />
                        )}
                        Aprovar {atletasSelecionados.length} selecionado(s)
                      </Button>
                    )}
                    <Select value={filtroStatusAutorizacao} onValueChange={setFiltroStatusAutorizacao}>
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="todos">Todos</SelectItem>
                        <SelectItem value="em_teste">Em Teste</SelectItem>
                        <SelectItem value="autorizado">Autorizados</SelectItem>
                        <SelectItem value="expirado">Expirados</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button variant="outline" onClick={fetchAtletasPeriodoTeste} disabled={loadingAutorizacoes}>
                      <RefreshCw className={`w-4 h-4 ${loadingAutorizacoes ? 'animate-spin' : ''}`} />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                {loadingAutorizacoes ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-50 dark:bg-slate-900/50">
                        <tr>
                          <th className="px-4 py-3 text-center w-12">
                            <input
                              type="checkbox"
                              className="w-4 h-4 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                              checked={
                                filteredAtletasAutorizacao.filter(a => a.status_periodo !== 'autorizado').length > 0 &&
                                atletasSelecionados.length === filteredAtletasAutorizacao.filter(a => a.status_periodo !== 'autorizado').length
                              }
                              onChange={handleSelectAll}
                              title="Selecionar todos"
                            />
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Atleta</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Equipe</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Status</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Dias Restantes</th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Ações</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                        {filteredAtletasAutorizacao.map((atleta) => (
                          <tr 
                            key={atleta.id} 
                            className={`hover:bg-slate-50 dark:hover:bg-slate-700/50 ${
                              atletasSelecionados.includes(atleta.id) ? 'bg-emerald-50 dark:bg-emerald-900/20' : ''
                            }`}
                          >
                            <td className="px-4 py-3 text-center">
                              {atleta.status_periodo !== 'autorizado' && (
                                <input
                                  type="checkbox"
                                  className="w-4 h-4 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                                  checked={atletasSelecionados.includes(atleta.id)}
                                  onChange={() => handleToggleSelectAtleta(atleta.id)}
                                />
                              )}
                            </td>
                            <td className="px-4 py-3">
                              <div>
                                <p className="font-medium text-slate-900 dark:text-white">{atleta.nome}</p>
                                <p className="text-xs text-slate-500">{atleta.email}</p>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-400">
                              {atleta.equipe || 'Individual'}
                            </td>
                            <td className="px-4 py-3 text-center">
                              <Badge className={getStatusColor(atleta.status_periodo)}>
                                {getStatusLabel(atleta.status_periodo)}
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className={`font-semibold ${
                                atleta.dias_restantes > 10 ? 'text-green-600' :
                                atleta.dias_restantes > 0 ? 'text-yellow-600' : 'text-red-600'
                              }`}>
                                {atleta.dias_restantes !== null ? atleta.dias_restantes : '-'}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <div className="flex items-center justify-center gap-2">
                                {atleta.status_periodo !== 'autorizado' ? (
                                  <Button
                                    size="sm"
                                    onClick={() => {
                                      setAtletaAutorizando(atleta);
                                      setShowAutorizacaoModal(true);
                                    }}
                                    className="bg-emerald-500 hover:bg-emerald-600 text-white"
                                  >
                                    <CheckCircle className="w-4 h-4 mr-1" />
                                    Autorizar
                                  </Button>
                                ) : (
                                  <>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      onClick={() => handleGerarCarteirinha(atleta.id)}
                                      className="text-blue-600 border-blue-300"
                                    >
                                      <Award className="w-4 h-4 mr-1" />
                                      Carteirinha
                                    </Button>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      onClick={() => handleRevogarAutorizacao(atleta.autorizacao?.id)}
                                      className="text-red-600 border-red-300"
                                    >
                                      <XCircle className="w-4 h-4" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {filteredAtletasAutorizacao.length === 0 && (
                      <div className="text-center py-12 text-slate-500">
                        Nenhum atleta encontrado com o filtro selecionado
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Modal de Autorização */}
            <Dialog open={showAutorizacaoModal} onOpenChange={setShowAutorizacaoModal}>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-emerald-500" />
                    Autorizar Acesso
                  </DialogTitle>
                </DialogHeader>
                {atletaAutorizando && (
                  <div className="space-y-4">
                    <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-lg">
                      <p className="font-medium text-lg">{atletaAutorizando.nome}</p>
                      <p className="text-sm text-slate-500">{atletaAutorizando.email}</p>
                      <p className="text-sm text-slate-500">Equipe: {atletaAutorizando.equipe || 'Individual'}</p>
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Tipo de Autorização</Label>
                      <Select value={tipoAutorizacao} onValueChange={setTipoAutorizacao}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="6_meses">6 Meses</SelectItem>
                          <SelectItem value="1_ano">1 Ano</SelectItem>
                          <SelectItem value="ate_fim_ano">Até o Final do Ano</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Observação (opcional)</Label>
                      <Textarea
                        value={observacaoAutorizacao}
                        onChange={(e) => setObservacaoAutorizacao(e.target.value)}
                        placeholder="Ex: Pagamento via PIX em 09/03/2026"
                        rows={2}
                      />
                    </div>
                  </div>
                )}
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowAutorizacaoModal(false)}>
                    Cancelar
                  </Button>
                  <Button 
                    onClick={handleCriarAutorizacao}
                    disabled={savingAutorizacao}
                    className="bg-emerald-600 hover:bg-emerald-700"
                  >
                    {savingAutorizacao ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CheckCircle className="w-4 h-4 mr-2" />}
                    Confirmar Autorização
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Modal de Carteirinha */}
            <Dialog open={showCarteirinhaModal} onOpenChange={setShowCarteirinhaModal}>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-amber-500" />
                    Carteirinha de Membro
                  </DialogTitle>
                </DialogHeader>
                {carteirinhaData && (
                  <div className="space-y-4">
                    <div className="bg-gradient-to-br from-emerald-600 to-emerald-800 p-6 rounded-xl text-white relative overflow-hidden">
                      {/* Background pattern */}
                      <div className="absolute inset-0 opacity-10">
                        <div className="absolute top-2 right-2 text-6xl font-bold">RRP</div>
                      </div>
                      
                      <div className="relative z-10">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <p className="text-xs uppercase opacity-70">Ranking Run Pró</p>
                            <p className="text-lg font-bold">Carteirinha de Membro</p>
                          </div>
                          <Trophy className="w-8 h-8" />
                        </div>
                        
                        <div className="space-y-2">
                          <p className="text-xl font-bold">{carteirinhaData.atleta.nome}</p>
                          <p className="text-sm opacity-80">{carteirinhaData.atleta.equipe || 'Individual'}</p>
                          <p className="text-xs opacity-70">{carteirinhaData.atleta.email}</p>
                        </div>
                        
                        <div className="mt-4 pt-4 border-t border-white/20 flex justify-between items-end">
                          <div>
                            <p className="text-xs opacity-70">Nº Carteirinha</p>
                            <p className="font-mono text-sm">{carteirinhaData.numero_carteirinha}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs opacity-70">Válido até</p>
                            <p className="font-semibold">
                              {new Date(carteirinhaData.valido_ate).toLocaleDateString('pt-BR')}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <Alert className="bg-blue-50 dark:bg-blue-900/20 border-blue-200">
                      <AlertDescription className="text-blue-700 dark:text-blue-300 text-sm">
                        Esta carteirinha comprova que o atleta está autorizado a participar do Ranking Run Pró.
                      </AlertDescription>
                    </Alert>
                  </div>
                )}
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowCarteirinhaModal(false)}>
                    Fechar
                  </Button>
                  <Button 
                    onClick={() => {
                      // Implementar download/impressão
                      window.print();
                    }}
                    className="bg-emerald-600 hover:bg-emerald-700"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Imprimir
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        )}

        {/* Administradores View (RBAC) */}
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
        {activeMenu === 'regulamento' && (
          <div className="space-y-6">
            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader className="border-b dark:border-slate-700">
                <CardTitle className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-emerald-500" />
                  </div>
                  <div>
                    <span>Gerenciar Regulamento</span>
                    {regulamento.ultima_atualizacao && (
                      <p className="text-xs text-slate-400 font-normal mt-1">
                        Última atualização: {new Date(regulamento.ultima_atualizacao).toLocaleString('pt-BR')} 
                        {regulamento.atualizado_por && ` por ${regulamento.atualizado_por}`}
                      </p>
                    )}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                {loadingRegulamento ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Instruções */}
                    <Alert className="bg-blue-50 dark:bg-blue-900/20 border-blue-200">
                      <AlertDescription className="text-blue-700 dark:text-blue-300">
                        <strong>Dica:</strong> Use formatação Markdown para estruturar o regulamento:
                        <ul className="list-disc list-inside mt-2 text-sm">
                          <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">## Título</code> para títulos de seção</li>
                          <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">### Subtítulo</code> para subtítulos</li>
                          <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">- Item</code> para listas</li>
                          <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">**texto**</code> para negrito</li>
                          <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">---</code> para linha horizontal</li>
                        </ul>
                      </AlertDescription>
                    </Alert>

                    {/* Título */}
                    <div className="space-y-2">
                      <Label htmlFor="reg-titulo" className="text-slate-700 dark:text-slate-300">
                        Título do Regulamento
                      </Label>
                      <Input
                        id="reg-titulo"
                        value={regulamento.titulo}
                        onChange={(e) => setRegulamento({ ...regulamento, titulo: e.target.value })}
                        placeholder="Ex: Regulamento Oficial do Ranking Run Pró"
                        className="bg-slate-50 dark:bg-slate-900"
                      />
                    </div>

                    {/* Conteúdo */}
                    <div className="space-y-2">
                      <Label htmlFor="reg-conteudo" className="text-slate-700 dark:text-slate-300">
                        Conteúdo do Regulamento
                      </Label>
                      <Textarea
                        id="reg-conteudo"
                        value={regulamento.conteudo}
                        onChange={(e) => setRegulamento({ ...regulamento, conteudo: e.target.value })}
                        placeholder="Digite o conteúdo do regulamento aqui..."
                        className="bg-slate-50 dark:bg-slate-900 min-h-[400px] font-mono text-sm"
                      />
                    </div>

                    {/* Botões */}
                    <div className="flex justify-end gap-3">
                      <Button 
                        variant="outline" 
                        onClick={fetchRegulamento}
                        disabled={loadingRegulamento}
                      >
                        <RefreshCw className={`w-4 h-4 mr-2 ${loadingRegulamento ? 'animate-spin' : ''}`} />
                        Recarregar
                      </Button>
                      <Button 
                        onClick={handleSaveRegulamento}
                        disabled={savingRegulamento}
                        className="bg-emerald-600 hover:bg-emerald-700"
                      >
                        {savingRegulamento ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <CheckCircle className="w-4 h-4 mr-2" />
                        )}
                        Salvar Regulamento
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Preview */}
            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader className="border-b dark:border-slate-700">
                <CardTitle className="text-base flex items-center gap-2">
                  <Eye className="w-4 h-4 text-slate-400" />
                  Pré-visualização
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-6 max-h-[400px] overflow-y-auto">
                  <h2 className="text-xl font-bold text-emerald-600 mb-4">{regulamento.titulo || 'Título do Regulamento'}</h2>
                  <div className="text-slate-700 dark:text-slate-300 space-y-2 whitespace-pre-wrap">
                    {regulamento.conteudo ? (
                      regulamento.conteudo.split('\n').map((line, i) => {
                        if (line.startsWith('### ')) return <h3 key={i} className="text-lg font-semibold text-emerald-500 mt-4 mb-2">{line.replace('### ', '')}</h3>;
                        if (line.startsWith('## ')) return <h2 key={i} className="text-xl font-bold text-emerald-600 mt-6 mb-3">{line.replace('## ', '')}</h2>;
                        if (line.startsWith('---')) return <hr key={i} className="my-4 border-slate-300 dark:border-slate-600" />;
                        if (line.startsWith('- ')) return <div key={i} className="flex gap-2 ml-4"><span className="text-emerald-500">•</span>{line.replace('- ', '')}</div>;
                        if (line.trim() === '') return <div key={i} className="h-2"></div>;
                        return <p key={i}>{line}</p>;
                      })
                    ) : (
                      <p className="text-slate-400 italic">O conteúdo do regulamento aparecerá aqui...</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Ranking View */}
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
        {activeMenu === 'aniversariantes' && (
          <div className="space-y-6">
            {/* Card de Configuração */}
            <Card className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/30 dark:to-purple-900/30 shadow-lg border-0">
              <CardContent className="py-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full ${envioAutomatico ? 'bg-emerald-100 dark:bg-emerald-900' : 'bg-slate-100 dark:bg-slate-800'}`}>
                      <Clock className={`w-5 h-5 ${envioAutomatico ? 'text-emerald-600' : 'text-slate-500'}`} />
                    </div>
                    <div>
                      <p className="font-medium">Envio Automático às 00:00</p>
                      <p className={`text-sm ${envioAutomatico ? 'text-emerald-600' : 'text-slate-500'}`}>
                        {envioAutomatico ? '✅ Ativado - Mensagens são enviadas automaticamente' : '⏸️ Desativado'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      onClick={() => setShowConfigModal(true)}
                      className="bg-white dark:bg-slate-800"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Configurar
                    </Button>
                    <Button 
                      onClick={handleEnviarAniversariosAgora}
                      className="bg-pink-500 hover:bg-pink-600"
                    >
                      <Send className="w-4 h-4 mr-2" />
                      Enviar Agora (Hoje)
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Cake className="w-5 h-5 text-pink-500" />
                  Aniversariantes - {MESES[mesCalendario - 1]} {anoCalendario}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => {
                      if (mesCalendario === 1) {
                        setMesCalendario(12);
                        setAnoCalendario(prev => prev - 1);
                      } else {
                        setMesCalendario(prev => prev - 1);
                      }
                    }}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="font-medium px-4">{MESES[mesCalendario - 1]} {anoCalendario}</span>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => {
                      if (mesCalendario === 12) {
                        setMesCalendario(1);
                        setAnoCalendario(prev => prev + 1);
                      } else {
                        setMesCalendario(prev => prev + 1);
                      }
                    }}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {loadingAniversariantes ? (
                  <div className="text-center py-12">Carregando...</div>
                ) : aniversariantesMes && (
                  <>
                    {/* Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-pink-50 dark:bg-pink-900/30 rounded-lg p-4 text-center">
                        <Gift className="w-8 h-8 mx-auto mb-2 text-pink-500" />
                        <div className="text-2xl font-bold text-pink-600">{aniversariantesMes.total_aniversariantes}</div>
                        <div className="text-sm text-slate-500">Aniversariantes</div>
                      </div>
                    </div>

                    {/* Calendário */}
                    <div className="bg-slate-50 dark:bg-slate-900 rounded-xl p-4">
                      <div className="grid grid-cols-7 gap-1 mb-2">
                        {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(dia => (
                          <div key={dia} className="text-center text-xs font-medium text-slate-500 py-2">
                            {dia}
                          </div>
                        ))}
                      </div>
                      <div className="grid grid-cols-7 gap-1">
                        {/* Dias vazios no início */}
                        {Array.from({ length: getPrimeiroDiaSemana(mesCalendario, anoCalendario) }).map((_, i) => (
                          <div key={`empty-${i}`} className="aspect-square" />
                        ))}
                        {/* Dias do mês */}
                        {Array.from({ length: getDiasNoMes(mesCalendario, anoCalendario) }).map((_, i) => {
                          const dia = i + 1;
                          const aniversariantes = aniversariantesMes.calendario[dia] || [];
                          const hasAniversariantes = aniversariantes.length > 0;
                          const isHoje = new Date().getDate() === dia && 
                                         new Date().getMonth() + 1 === mesCalendario &&
                                         new Date().getFullYear() === anoCalendario;
                          
                          return (
                            <div 
                              key={dia}
                              className={`aspect-square rounded-lg flex flex-col items-center justify-center cursor-pointer transition-all
                                ${hasAniversariantes ? 'bg-pink-100 dark:bg-pink-900/50 hover:bg-pink-200 dark:hover:bg-pink-900' : 'hover:bg-slate-100 dark:hover:bg-slate-800'}
                                ${isHoje ? 'ring-2 ring-emerald-500' : ''}
                                ${diaSelecionado === dia ? 'ring-2 ring-pink-500 bg-pink-200 dark:bg-pink-800' : ''}
                              `}
                              onClick={() => hasAniversariantes && setDiaSelecionado(dia)}
                              data-testid={`dia-${dia}`}
                            >
                              <span className={`text-sm font-medium ${hasAniversariantes ? 'text-pink-600 dark:text-pink-300' : ''}`}>
                                {dia}
                              </span>
                              {hasAniversariantes && (
                                <div className="flex -space-x-1 mt-1">
                                  {aniversariantes.slice(0, 3).map((a, idx) => (
                                    <Avatar key={idx} className="w-5 h-5 border border-white">
                                      <AvatarImage src={a.foto_url?.startsWith('http') ? a.foto_url : `${BACKEND_URL}${a.foto_url}`} />
                                      <AvatarFallback className="bg-pink-500 text-white text-[8px]">{a.nome?.charAt(0)}</AvatarFallback>
                                    </Avatar>
                                  ))}
                                  {aniversariantes.length > 3 && (
                                    <div className="w-5 h-5 rounded-full bg-pink-500 text-white text-[8px] flex items-center justify-center border border-white">
                                      +{aniversariantes.length - 3}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Painel lateral - Aniversariantes do dia selecionado */}
                    {diaSelecionado && aniversariantesMes.calendario[diaSelecionado]?.length > 0 && (
                      <div className="mt-6 p-4 bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/30 dark:to-purple-900/30 rounded-xl">
                        <h4 className="font-semibold mb-4 flex items-center gap-2">
                          <Cake className="w-5 h-5 text-pink-500" />
                          Aniversariantes do dia {diaSelecionado}
                        </h4>
                        
                        <div className="space-y-3 mb-4">
                          {aniversariantesMes.calendario[diaSelecionado].map((atleta) => (
                            <div 
                              key={atleta.id}
                              className={`flex items-center gap-3 p-3 bg-white dark:bg-slate-800 rounded-lg cursor-pointer transition-all
                                ${atletasSelecionar.includes(atleta.id) ? 'ring-2 ring-pink-500' : ''}`}
                              onClick={() => toggleAtletaSelecao(atleta.id)}
                            >
                              <input 
                                type="checkbox" 
                                checked={atletasSelecionar.includes(atleta.id)}
                                onChange={() => {}}
                                className="rounded border-pink-300"
                              />
                              <Avatar className="w-10 h-10">
                                <AvatarImage src={atleta.foto_url?.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                                <AvatarFallback className="bg-pink-500 text-white">{atleta.nome?.charAt(0)}</AvatarFallback>
                              </Avatar>
                              <div className="flex-1">
                                <p className="font-medium">{atleta.nome}</p>
                                <p className="text-sm text-slate-500">{atleta.equipe} • {atleta.idade} anos</p>
                              </div>
                              <Badge className="bg-pink-100 text-pink-700 border-0">
                                {atleta.apelido || 'Atleta'}
                              </Badge>
                            </div>
                          ))}
                        </div>

                        {/* Mensagem de aniversário */}
                        <div className="space-y-3">
                          <Label>Mensagem de Felicitação</Label>
                          <Textarea
                            value={mensagemPadrao}
                            onChange={(e) => setMensagemPadrao(e.target.value)}
                            placeholder="Escreva sua mensagem de aniversário..."
                            rows={3}
                            className="bg-white dark:bg-slate-800"
                          />
                          <div className="flex gap-2">
                            <Button
                              onClick={handleEnviarMensagemAniversario}
                              className="bg-pink-500 hover:bg-pink-600"
                              disabled={atletasSelecionar.length === 0}
                            >
                              <Send className="w-4 h-4 mr-2" />
                              Enviar para {atletasSelecionar.length} atleta(s)
                            </Button>
                            <Button
                              variant="outline"
                              onClick={() => {
                                const todosIds = aniversariantesMes.calendario[diaSelecionado].map(a => a.id);
                                setAtletasSelecionar(todosIds);
                              }}
                            >
                              Selecionar Todos
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        )}



        {/* RANKING RUN INSIDE - INSTAGRAM ANALYTICS */}
        {activeMenu === 'instagram' && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <Activity className="w-6 h-6 text-pink-500" />
                  Ranking Run Inside
                </h2>
                <p className="text-slate-500">Análise de Perfis Instagram - Sistema de Score de Influenciadores</p>
              </div>
            </div>

            {/* Barra de Pesquisa */}
            {!instagramResult && !showInstagramForm && (
              <Card className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20 border-pink-200 dark:border-pink-800">
                <CardContent className="p-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-2">
                      Analisar Perfil do Instagram
                    </h3>
                    <p className="text-slate-600 dark:text-slate-400 text-sm">
                      Digite o @username para análise automática completa
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3 max-w-xl mx-auto">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                      <Input
                        placeholder="@username (ex: rankingrun)"
                        value={instagramSearchUsername}
                        onChange={(e) => setInstagramSearchUsername(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleInstagramSearch()}
                        className="pl-10 h-12 text-lg"
                        disabled={instagramSearchLoading}
                      />
                    </div>
                    <select
                      value={instagramFormData.nicho}
                      onChange={(e) => setInstagramFormData({...instagramFormData, nicho: e.target.value})}
                      className="h-12 px-4 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800"
                    >
                      <option value="corrida">Corrida</option>
                      <option value="fitness">Fitness</option>
                      <option value="lifestyle">Lifestyle</option>
                      <option value="moda">Moda</option>
                      <option value="gastronomia">Gastronomia</option>
                      <option value="viagem">Viagem</option>
                      <option value="tech">Tecnologia</option>
                      <option value="outros">Outros</option>
                    </select>
                    <Button
                      onClick={handleInstagramSearch}
                      disabled={instagramSearchLoading || !instagramSearchUsername.trim()}
                      className="h-12 px-6 bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600"
                    >
                      {instagramSearchLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Analisando...
                        </>
                      ) : (
                        <>
                          <Activity className="w-4 h-4 mr-2" />
                          Analisar
                        </>
                      )}
                    </Button>
                  </div>

                  {instagramSearchError && (
                    <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/30 rounded-lg text-center">
                      <p className="text-red-700 dark:text-red-300 text-sm">
                        {instagramSearchError}
                      </p>
                    </div>
                  )}

                  <div className="mt-6 text-center text-sm text-slate-500">
                    <p>O sistema busca automaticamente: seguidores, posts, engajamento, crescimento, análise da bio e indicadores anti-fake.</p>
                    <button
                      onClick={() => { resetInstagramForm(); setShowInstagramForm(true); }}
                      className="mt-2 text-pink-600 dark:text-pink-400 hover:underline font-medium"
                    >
                      Ou inserir dados manualmente →
                    </button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Resultado da Análise */}
            {instagramResult && (
              <div className="space-y-6">
                {/* Card Principal do Score */}
                <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white border-0 shadow-2xl overflow-hidden">
                  <CardContent className="p-6">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      {/* Perfil */}
                      <div className="text-center lg:text-left">
                        <div className="flex items-center justify-center lg:justify-start gap-4 mb-4">
                          <div className="w-16 h-16 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-2xl font-bold">
                            @
                          </div>
                          <div>
                            <h3 className="text-2xl font-bold">@{instagramResult.analysis.username}</h3>
                            <p className="text-slate-400">{instagramResult.analysis.nome_completo || 'Influenciador'}</p>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2 justify-center lg:justify-start">
                          <Badge className="bg-slate-700 text-slate-200">{instagramResult.analysis.nicho}</Badge>
                          <Badge className={getClassificacaoColor(instagramResult.analysis.classificacao)}>
                            {instagramResult.analysis.classificacao}
                          </Badge>
                        </div>
                      </div>

                      {/* Score Gauge */}
                      <div className="text-center">
                        <div className="relative w-40 h-40 mx-auto">
                          <svg className="w-full h-full transform -rotate-90">
                            <circle
                              cx="80" cy="80" r="70"
                              stroke="#334155"
                              strokeWidth="12"
                              fill="none"
                            />
                            <circle
                              cx="80" cy="80" r="70"
                              stroke={instagramResult.analysis.score_final >= 80 ? '#10B981' : 
                                      instagramResult.analysis.score_final >= 60 ? '#F59E0B' : '#EF4444'}
                              strokeWidth="12"
                              fill="none"
                              strokeDasharray={`${(instagramResult.analysis.score_final / 100) * 440} 440`}
                              strokeLinecap="round"
                            />
                          </svg>
                          <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-4xl font-bold">{instagramResult.analysis.score_final}</span>
                            <span className="text-sm text-slate-400">/100</span>
                          </div>
                        </div>
                        <p className="mt-2 text-lg font-semibold">Score de Influência</p>
                        
                        {/* Barra de Score Visual */}
                        <div className="mt-4 w-full max-w-xs mx-auto">
                          <div className="relative h-3 rounded-full overflow-hidden bg-slate-700">
                            <div className="absolute inset-0 flex">
                              <div className="w-[20%] bg-red-600" title="Péssimo (0-40)"></div>
                              <div className="w-[20%] bg-orange-500" title="Ruim (40-60)"></div>
                              <div className="w-[10%] bg-amber-400" title="Regular (60-70)"></div>
                              <div className="w-[10%] bg-blue-500" title="Bom (70-80)"></div>
                              <div className="w-[10%] bg-purple-500" title="Ótimo (80-90)"></div>
                              <div className="w-[30%] bg-green-500" title="Excelente (90-100)"></div>
                            </div>
                            {/* Indicador de posição */}
                            <div 
                              className="absolute top-0 w-1 h-3 bg-white shadow-lg transition-all"
                              style={{ left: `${instagramResult.analysis.score_final}%` }}
                            ></div>
                          </div>
                          <div className="flex justify-between mt-1 text-[10px] text-slate-500">
                            <span>Péssimo</span>
                            <span>Ruim</span>
                            <span>Regular</span>
                            <span>Bom</span>
                            <span>Ótimo</span>
                            <span>Excelente</span>
                          </div>
                        </div>
                      </div>

                      {/* Métricas Rápidas */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-slate-700/50 p-4 rounded-xl text-center">
                          <div className="text-2xl font-bold text-pink-400">
                            {instagramResult.analysis.seguidores.toLocaleString()}
                          </div>
                          <div className="text-sm text-slate-400">Seguidores</div>
                        </div>
                        <div className="bg-slate-700/50 p-4 rounded-xl text-center">
                          <div className="text-2xl font-bold text-blue-400">
                            {instagramResult.analysis.engagement_rate}%
                          </div>
                          <div className="text-sm text-slate-400">Engajamento</div>
                        </div>
                        <div className="bg-slate-700/50 p-4 rounded-xl text-center">
                          <div className="text-2xl font-bold text-green-400">
                            {instagramResult.analysis.total_posts}
                          </div>
                          <div className="text-sm text-slate-400">Posts</div>
                        </div>
                        <div className="bg-slate-700/50 p-4 rounded-xl text-center">
                          <div className="text-2xl font-bold text-amber-400">
                            {((instagramResult.graficos_data?.metricas?.indice_anomalia || 0)).toFixed(1)}%
                          </div>
                          <div className="text-sm text-slate-400">Índice Anomalia</div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Gráficos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Radar Chart - 8 Métricas */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Activity className="w-5 h-5 text-purple-500" />
                        Análise Radar (8 Métricas)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart data={instagramResult.graficos_data.radar.labels.map((label, i) => ({
                            metric: label,
                            value: instagramResult.graficos_data.radar.values[i],
                            fullMark: 10
                          }))}>
                            <PolarGrid stroke="#E5E7EB" />
                            <PolarAngleAxis dataKey="metric" tick={{ fill: '#6B7280', fontSize: 11 }} />
                            <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: '#9CA3AF', fontSize: 10 }} />
                            <RechartsRadar name="Perfil" dataKey="value" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.5} />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Notas Individuais */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-blue-500" />
                        Notas Individuais (0-10)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart 
                            data={instagramResult.graficos_data.radar.labels.map((label, i) => ({
                              name: label,
                              nota: instagramResult.graficos_data.radar.values[i]
                            }))}
                            layout="vertical"
                          >
                            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                            <XAxis type="number" domain={[0, 10]} stroke="#9CA3AF" />
                            <YAxis dataKey="name" type="category" stroke="#9CA3AF" width={90} tick={{ fontSize: 11 }} />
                            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                            <Bar dataKey="nota" radius={[0, 4, 4, 0]}>
                              {instagramResult.graficos_data.radar.values.map((value, index) => (
                                <Cell key={`cell-${index}`} fill={value >= 7 ? '#10B981' : value >= 5 ? '#F59E0B' : '#EF4444'} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Distribuição de Formatos */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <PieChart className="w-5 h-5 text-pink-500" />
                        Distribuição de Formatos
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <RechartsPie>
                            <Pie
                              data={instagramResult.graficos_data.formatos.labels.map((label, i) => ({
                                name: label,
                                value: instagramResult.graficos_data.formatos.values[i]
                              }))}
                              cx="50%"
                              cy="50%"
                              innerRadius={50}
                              outerRadius={90}
                              paddingAngle={5}
                              dataKey="value"
                              label={({ name, value }) => `${name}: ${value}%`}
                            >
                              <Cell fill="#EC4899" />
                              <Cell fill="#8B5CF6" />
                              <Cell fill="#3B82F6" />
                            </Pie>
                            <Tooltip />
                            <Legend />
                          </RechartsPie>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Comparativo com Média do Nicho */}
                  <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-emerald-500" />
                        Comparativo vs Média do Nicho
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={instagramResult.graficos_data.comparativo.labels.map((label, i) => ({
                            name: label,
                            perfil: instagramResult.graficos_data.comparativo.perfil[i],
                            media: instagramResult.graficos_data.comparativo.media_nicho[i]
                          }))}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                            <XAxis dataKey="name" stroke="#9CA3AF" />
                            <YAxis stroke="#9CA3AF" />
                            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                            <Legend />
                            <Bar dataKey="perfil" name="Perfil Analisado" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="media" name="Média do Nicho" fill="#94A3B8" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Recomendações */}
                <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border-0">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-blue-500" />
                      Recomendações Personalizadas
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {instagramResult.recomendacoes.map((rec, i) => (
                        <li key={i} className="flex items-start gap-2 text-slate-700 dark:text-slate-300">
                          <span className="mt-1 w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {/* Botões de Ação */}
                <div className="flex flex-wrap gap-3">
                  <Button 
                    onClick={() => handleExportInstagram(instagramResult.analysis.id, 'xlsx')}
                    className="bg-emerald-600 hover:bg-emerald-700"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Exportar XLSX
                  </Button>
                  <Button 
                    onClick={() => handleExportInstagram(instagramResult.analysis.id, 'csv')}
                    variant="outline"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Exportar CSV
                  </Button>
                  <Button 
                    onClick={() => setInstagramResult(null)}
                    variant="outline"
                  >
                    Fechar Resultado
                  </Button>
                </div>
              </div>
            )}

            {/* Histórico de Análises */}
            {!instagramResult && (
              <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-slate-500" />
                    Histórico de Análises
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {loadingInstagram ? (
                    <div className="text-center py-12 text-slate-500">Carregando análises...</div>
                  ) : instagramAnalises.length === 0 ? (
                    <div className="text-center py-12">
                      <Activity className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                      <p className="text-slate-500">Nenhuma análise realizada ainda.</p>
                      <p className="text-sm text-slate-400 mt-1">Use a barra de pesquisa acima para começar.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {instagramAnalises.map((analysis) => (
                        <div 
                          key={analysis.id}
                          className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        >
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-white font-bold">
                              @
                            </div>
                            <div>
                              <h4 className="font-semibold">@{analysis.username}</h4>
                              <p className="text-sm text-slate-500">
                                {analysis.seguidores?.toLocaleString()} seguidores • {analysis.nicho}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-purple-600">{analysis.score_final}</div>
                              <Badge className={getClassificacaoColor(analysis.classificacao)}>
                                {analysis.classificacao}
                              </Badge>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={async () => {
                                  const response = await axios.get(`${API}/admin/instagram/analises/${analysis.id}`, {
                                    headers: { Authorization: `Bearer ${token}` }
                                  });
                                  setInstagramResult(response.data);
                                }}
                              >
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => handleDeleteInstagramAnalysis(analysis.id)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Modal Nova Análise */}
            <Dialog open={showInstagramForm} onOpenChange={setShowInstagramForm}>
              <DialogContent className="max-w-xl">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-pink-500" />
                    Nova Análise de Perfil
                  </DialogTitle>
                </DialogHeader>

                <div className="space-y-6 py-4">
                  <p className="text-sm text-slate-500 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                    💡 Preencha apenas os dados básicos. O sistema calculará automaticamente: 
                    média de likes, comentários, engagement rate, crescimento, análise da bio e indicadores anti-fake.
                  </p>

                  {/* Dados Básicos */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>@Username *</Label>
                      <Input
                        value={instagramFormData.username}
                        onChange={(e) => setInstagramFormData({...instagramFormData, username: e.target.value.replace('@', '')})}
                        placeholder="usuario"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Nome Completo</Label>
                      <Input
                        value={instagramFormData.nome_completo}
                        onChange={(e) => setInstagramFormData({...instagramFormData, nome_completo: e.target.value})}
                        placeholder="João Silva"
                      />
                    </div>
                  </div>

                  {/* Métricas */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="space-y-2">
                      <Label>Seguidores *</Label>
                      <Input
                        type="number"
                        value={instagramFormData.seguidores}
                        onChange={(e) => setInstagramFormData({...instagramFormData, seguidores: e.target.value})}
                        placeholder="10000"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Seguindo *</Label>
                      <Input
                        type="number"
                        value={instagramFormData.seguindo}
                        onChange={(e) => setInstagramFormData({...instagramFormData, seguindo: e.target.value})}
                        placeholder="500"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Total de Posts *</Label>
                      <Input
                        type="number"
                        value={instagramFormData.total_posts}
                        onChange={(e) => setInstagramFormData({...instagramFormData, total_posts: e.target.value})}
                        placeholder="150"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Nicho</Label>
                      <select
                        value={instagramFormData.nicho}
                        onChange={(e) => setInstagramFormData({...instagramFormData, nicho: e.target.value})}
                        className="w-full h-10 px-3 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800"
                      >
                        <option value="corrida">Corrida</option>
                        <option value="fitness">Fitness</option>
                        <option value="lifestyle">Lifestyle</option>
                        <option value="moda">Moda</option>
                        <option value="gastronomia">Gastronomia</option>
                        <option value="viagem">Viagem</option>
                        <option value="tech">Tecnologia</option>
                        <option value="outros">Outros</option>
                      </select>
                    </div>
                  </div>

                  {/* Bio (opcional) */}
                  <div className="space-y-2">
                    <Label>Bio do Perfil (opcional - para análise de qualidade)</Label>
                    <textarea
                      value={instagramFormData.bio}
                      onChange={(e) => setInstagramFormData({...instagramFormData, bio: e.target.value})}
                      placeholder="Cole aqui a bio do perfil para análise automática de keywords, CTA, etc."
                      className="w-full h-20 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 resize-none"
                    />
                  </div>
                </div>

                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowInstagramForm(false)}>
                    Cancelar
                  </Button>
                  <Button 
                    onClick={handleInstagramAnalyze}
                    disabled={loadingInstagram}
                    className="bg-gradient-to-r from-pink-500 to-purple-500"
                  >
                    {loadingInstagram ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Analisando...
                      </>
                    ) : (
                      <>
                        <Activity className="w-4 h-4 mr-2" />
                        Analisar Perfil
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
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
            </div>
            <p className="text-sm text-slate-500">Senha padrão: atleta123</p>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowAddAtletaModal(false)}>Cancelar</Button>
              <Button onClick={handleAddAtleta} disabled={actionLoading} className="bg-emerald-600">Cadastrar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal Editar Corrida */}
        <Dialog open={showEditCorridaModal} onOpenChange={setShowEditCorridaModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Editar Corrida</DialogTitle>
            </DialogHeader>
            {corridaSelecionada && (
              <div className="grid grid-cols-2 gap-4">
                <div className="md:col-span-2 space-y-2">
                  <Label>Nome da Competição</Label>
                  <Input 
                    value={corridaSelecionada.nome} 
                    onChange={(e) => setCorridaSelecionada({...corridaSelecionada, nome: e.target.value})} 
                  />
                </div>
                <div className="space-y-2">
                  <Label>Colocação</Label>
                  <Input 
                    type="number"
                    min="1"
                    max="10"
                    value={corridaSelecionada.colocacao} 
                    onChange={(e) => setCorridaSelecionada({...corridaSelecionada, colocacao: parseInt(e.target.value)})} 
                  />
                </div>
                <div className="space-y-2">
                  <Label>Distância</Label>
                  <Select 
                    value={corridaSelecionada.distancia} 
                    onValueChange={(v) => setCorridaSelecionada({...corridaSelecionada, distancia: v})}
                  >
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5KM">5 KM</SelectItem>
                      <SelectItem value="10KM">10 KM</SelectItem>
                      <SelectItem value="21KM">21 KM</SelectItem>
                      <SelectItem value="42KM">42 KM</SelectItem>
                      <SelectItem value="OUTRA">Outra</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Data</Label>
                  <Input 
                    type="date"
                    value={corridaSelecionada.data} 
                    onChange={(e) => setCorridaSelecionada({...corridaSelecionada, data: e.target.value})} 
                  />
                </div>
                <div className="space-y-2">
                  <Label>Tempo</Label>
                  <Input 
                    type="time"
                    step="1"
                    value={corridaSelecionada.tempo} 
                    onChange={(e) => setCorridaSelecionada({...corridaSelecionada, tempo: e.target.value})} 
                  />
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowEditCorridaModal(false)}>Cancelar</Button>
              <Button onClick={handleEditCorrida} disabled={actionLoading} className="bg-emerald-600">Salvar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal Configuração de Aniversário */}
        <Dialog open={showConfigModal} onOpenChange={setShowConfigModal}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-pink-500" />
                Configurações de Aniversário
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-6">
              {/* Toggle Envio Automático */}
              <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
                <div>
                  <p className="font-medium">Envio Automático às 00:00</p>
                  <p className="text-sm text-slate-500">
                    Quando ativado, mensagens são enviadas automaticamente à meia-noite para os aniversariantes do dia.
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={envioAutomatico}
                    onChange={(e) => setEnvioAutomatico(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 dark:peer-focus:ring-pink-800 rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-pink-500"></div>
                </label>
              </div>

              {/* Mensagem Padrão */}
              <div className="space-y-2">
                <Label>Mensagem Padrão de Felicitação</Label>
                <Textarea
                  value={mensagemPadrao}
                  onChange={(e) => setMensagemPadrao(e.target.value)}
                  placeholder="Escreva a mensagem padrão de aniversário..."
                  rows={4}
                  className="bg-slate-50 dark:bg-slate-900"
                />
                <p className="text-xs text-slate-500">
                  Esta mensagem será usada tanto no envio automático quanto no envio manual.
                </p>
              </div>

              {/* Info */}
              <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg text-sm text-blue-700 dark:text-blue-300">
                <p className="font-medium mb-1">Como funciona:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>O sistema verifica diariamente os aniversariantes às 00:00</li>
                  <li>Cada atleta recebe apenas 1 mensagem por ano</li>
                  <li>O atleta vê a mensagem em formato de popup ao abrir o app</li>
                  <li>Após visualizar, a mensagem não aparece novamente</li>
                </ul>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowConfigModal(false)}>Cancelar</Button>
              <Button onClick={handleSalvarConfigAniversario} className="bg-pink-500 hover:bg-pink-600">
                Salvar Configurações
              </Button>
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
