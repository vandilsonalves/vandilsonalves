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
  Users, AlertCircle, TrendingUp, BarChart3, PieChart,
  Activity, Home, Settings, FileText, Bell, ChevronRight, Award, Database,
  UserPlus, Edit, Trash2, Eye, Download, Plus, Minus, Search, Image, X,
  Cake, Send, Gift, ChevronLeft
} from 'lucide-react';
import { toast } from 'sonner';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPie, Pie, Cell, LineChart, Line, AreaChart, Area } from 'recharts';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

// Menu items para sidebar
const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Home },
  { id: 'pendentes', label: 'Aprovações', icon: AlertCircle },
  { id: 'atletas', label: 'Atletas', icon: Users },
  { id: 'submeter', label: '+ Submeter Resultado', icon: Plus },
  { id: 'graficos', label: 'Gráficos', icon: BarChart3 },
  { id: 'ranking', label: 'Ranking', icon: Trophy },
  { id: 'aniversariantes', label: 'Aniversariantes', icon: Cake },
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
  
  // Stats Avançados
  const [statsEquipes, setStatsEquipes] = useState([]);
  const [statsPovao, setStatsPovao] = useState(null);
  const [statsModalidade, setStatsModalidade] = useState({ profissional: 0, povao: 0 });
  
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
  const [searchQuery, setSearchQuery] = useState('');
  const [showAtletaModal, setShowAtletaModal] = useState(false);
  const [atletaEditando, setAtletaEditando] = useState(null);
  const [showAddAtletaModal, setShowAddAtletaModal] = useState(false);
  
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

  const MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

  useEffect(() => {
    if (!isAdmin) {
      navigate('/');
      return;
    }
    fetchAllData();
  }, [isAdmin]);

  useEffect(() => {
    if (activeMenu === 'atletas') {
      fetchAtletas();
    }
    if (activeMenu === 'aniversariantes') {
      fetchAniversariantes();
      fetchConfigAniversario();
    }
  }, [activeMenu, filtroCategoria, mesCalendario, anoCalendario]);

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
    await Promise.all([
      fetchStats(),
      fetchPendentes()
    ]);
  };

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      const [statsRes, estadosRes, categoriasRes, faixaRes, corridasRes, povaoRes] = await Promise.all([
        axios.get(`${API}/admin/stats`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/estados`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/categorias`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/faixa-etaria`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/stats/corridas-por-mes`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/ranking/povao/stats`)
      ]);
      
      setStats(statsRes.data);
      setStatsEstados(estadosRes.data);
      setStatsCategorias(categoriasRes.data);
      setStatsFaixa(faixaRes.data);
      setCorridasPorMes(corridasRes.data);
      setStatsPovao(povaoRes.data);
      
      // Calcular estatísticas de equipes a partir dos atletas
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
        params: { categoria: filtroCategoria !== 'all' ? filtroCategoria : undefined }
      });
      setAtletas(response.data);
    } catch (error) {
      console.error('Erro ao buscar atletas:', error);
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

  const handleExportAtletas = async () => {
    try {
      const response = await axios.get(`${API}/admin/atletas/export`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { categoria: filtroCategoria },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `atletas_${filtroCategoria}.xlsx`);
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

  if (!isAdmin) return null;

  return (
    <div className="min-h-screen flex bg-slate-100 dark:bg-slate-950">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-slate-800 to-slate-900 text-white fixed h-full shadow-xl">
        <div className="p-6 border-b border-slate-700/50">
          <h1 className="text-xl font-bold text-emerald-400">Ranking Run Pró</h1>
          <p className="text-xs text-slate-400 mt-1">Painel Administrativo</p>
        </div>

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
              </button>
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

        {/* Dashboard View */}
        {activeMenu === 'dashboard' && (
          <div className="space-y-6">
            {loadingStats ? (
              <div className="text-center py-12">Carregando...</div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                          <CardTitle className="text-lg">{resultado.nome_competicao}</CardTitle>
                          <p className="text-sm text-slate-500 mt-1">
                            <strong>Atleta:</strong> {resultado.atleta_nome}
                          </p>
                          <Badge variant="outline" className="mt-2">
                            {resultado.atleta_categoria?.toUpperCase()}
                          </Badge>
                        </div>
                        <Badge className="bg-amber-100 text-amber-700 border-0">Pendente</Badge>
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

                      {/* Foto do Pódio */}
                      {resultado.foto_podio_url && (
                        <div className="pt-3 border-t">
                          <p className="text-sm font-medium mb-2 flex items-center gap-2">
                            <Image className="w-4 h-4 text-blue-500" />
                            Foto do Pódio
                            <span className="text-xs text-blue-500 font-normal">(clique para ampliar)</span>
                          </p>
                          <div className="relative inline-block group">
                            <img 
                              src={resultado.foto_podio_url.startsWith('http') ? resultado.foto_podio_url : `${BACKEND_URL}${resultado.foto_podio_url}`}
                              alt="Foto do Pódio"
                              className="max-h-48 rounded-lg border border-slate-200 object-cover cursor-pointer transition-all hover:ring-4 hover:ring-blue-300"
                              onClick={() => handleViewFoto(resultado.foto_podio_url)}
                              data-testid={`foto-podio-${resultado.id}`}
                            />
                            <div 
                              className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center cursor-pointer"
                              onClick={() => handleViewFoto(resultado.foto_podio_url)}
                            >
                              <Eye className="w-8 h-8 text-white" />
                            </div>
                            <Button
                              size="sm"
                              variant="destructive"
                              className="absolute top-2 right-2 z-10"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteFotoPodio(resultado.id);
                              }}
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                          <p className="text-xs text-slate-500 mt-1">
                            A foto será auto-excluída em 24h após aprovação/reprovação
                          </p>
                        </div>
                      )}

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

        {/* Atletas View */}
        {activeMenu === 'atletas' && (
          <div className="space-y-6">
            {/* Toolbar */}
            <div className="flex flex-wrap gap-4 items-center justify-between">
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={filtroCategoria === 'all' ? 'default' : 'outline'}
                  onClick={() => setFiltroCategoria('all')}
                  size="sm"
                >
                  Todos
                </Button>
                <Button
                  variant={filtroCategoria === 'normal-m' ? 'default' : 'outline'}
                  onClick={() => setFiltroCategoria('normal-m')}
                  size="sm"
                >
                  Atletas M
                </Button>
                <Button
                  variant={filtroCategoria === 'normal-f' ? 'default' : 'outline'}
                  onClick={() => setFiltroCategoria('normal-f')}
                  size="sm"
                >
                  Atletas F
                </Button>
                <Button
                  variant={filtroCategoria === 'pcd' ? 'default' : 'outline'}
                  onClick={() => setFiltroCategoria('pcd')}
                  size="sm"
                >
                  PCD M/F
                </Button>
                <Button
                  variant={filtroCategoria === 'cadeirante' ? 'default' : 'outline'}
                  onClick={() => setFiltroCategoria('cadeirante')}
                  size="sm"
                >
                  Cadeirante M/F
                </Button>
              </div>
              
              <div className="flex gap-2">
                <Button onClick={() => setShowAddAtletaModal(true)} className="bg-emerald-600">
                  <UserPlus className="w-4 h-4 mr-2" />
                  + Adicionar
                </Button>
                <Button onClick={handleExportAtletas} variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Exportar Dados
                </Button>
              </div>
            </div>

            {/* Filtro por Modalidade */}
            <div className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Modalidade:</span>
              <div className="flex gap-2">
                <Button
                  variant={filtroModalidade === 'all' ? 'default' : 'outline'}
                  onClick={() => setFiltroModalidade('all')}
                  size="sm"
                  className={filtroModalidade === 'all' ? 'bg-slate-700' : ''}
                >
                  Todas
                </Button>
                <Button
                  variant={filtroModalidade === 'profissional_amador' ? 'default' : 'outline'}
                  onClick={() => setFiltroModalidade('profissional_amador')}
                  size="sm"
                  className={filtroModalidade === 'profissional_amador' ? 'bg-emerald-600' : ''}
                >
                  Profissional/Amador
                </Button>
                <Button
                  variant={filtroModalidade === 'povao_pace_livre' ? 'default' : 'outline'}
                  onClick={() => setFiltroModalidade('povao_pace_livre')}
                  size="sm"
                  className={filtroModalidade === 'povao_pace_livre' ? 'bg-purple-600' : ''}
                >
                  Ranking do Povão
                </Button>
              </div>
            </div>

            {/* Barra de Pesquisa */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <Input
                placeholder="Pesquisar atleta por nome, equipe ou cidade..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-white dark:bg-slate-800"
                data-testid="search-atletas"
              />
            </div>

            {/* Lista de Atletas */}
            {loadingAtletas ? (
              <div className="text-center py-12">Carregando...</div>
            ) : (
              <>
                <p className="text-sm text-slate-500">
                  {filteredAtletas.length} atleta(s) encontrado(s) • Ordenado de A a Z
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredAtletas.map((atleta) => (
                    <Card key={atleta.id} className="bg-white dark:bg-slate-800 shadow border-0">
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-4">
                          <Avatar className="h-12 w-12">
                            <AvatarImage src={atleta.foto_url?.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                            <AvatarFallback className="bg-emerald-600 text-white">
                              {atleta.nome?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold truncate">{atleta.nome}</h3>
                            <p className="text-sm text-slate-500">{atleta.equipe}</p>
                            <div className="flex flex-wrap gap-2 mt-1">
                              <Badge variant="outline" className="text-xs">
                                {atleta.categoria?.toUpperCase()}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {atleta.genero === 'M' ? 'Masc' : 'Fem'}
                              </Badge>
                              {/* Badge de Modalidade */}
                              <Badge 
                                className={`text-xs ${
                                  atleta.modalidade_usuario === 'povao_pace_livre' 
                                    ? 'bg-purple-100 text-purple-700 border-purple-300' 
                                    : 'bg-emerald-100 text-emerald-700 border-emerald-300'
                                }`}
                              >
                                {atleta.modalidade_usuario === 'povao_pace_livre' ? 'Povão' : 'Pro/Amador'}
                              </Badge>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex gap-2 mt-4 pt-4 border-t">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => navigate(`/atleta/${atleta.id}`)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setAtletaEditando(atleta);
                              setShowAtletaModal(true);
                            }}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteAtleta(atleta.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </>
            )}
          </div>
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

        {/* Gráficos View */}
        {activeMenu === 'graficos' && (
          <div className="space-y-6">
            {loadingStats ? (
              <div className="text-center py-12">Carregando...</div>
            ) : (
              <>
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

        {/* Modal de Reprovação */}
        <Dialog open={showReprovarModal} onOpenChange={setShowReprovarModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Reprovar Resultado</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <p className="text-sm text-slate-600">
                O atleta receberá uma notificação com o motivo da reprovação.
              </p>
              <Textarea
                value={motivoReprovacao}
                onChange={(e) => setMotivoReprovacao(e.target.value)}
                placeholder="Ex: Resultado não encontrado no link fornecido..."
                rows={4}
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowReprovarModal(false)}>Cancelar</Button>
              <Button variant="destructive" onClick={handleReprovar} disabled={actionLoading}>Reprovar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

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
      </div>
    </div>
  );
};

export default AdminDashboard;
