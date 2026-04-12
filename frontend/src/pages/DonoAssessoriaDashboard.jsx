import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { 
  Trophy, Users, MapPin, Award, CheckCircle, TrendingUp, Home, Bell, 
  Download, Send, Settings, LogOut, Plus, Eye, BarChart3, Loader2, 
  MessageSquare, Calendar, Target, Medal, ArrowUpRight, ArrowDownRight, Minus, PieChart,
  BadgeCheck, Crown, X, ShieldCheck, UserPlus, UserCheck, UserX, Clock, Upload, Camera, Trash2, Image,
  FileSpreadsheet, FileText, Menu
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell, Legend, RadarChart, PolarGrid, PolarAngleAxis, Radar } from 'recharts';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import { downloadFile, downloadCSVContent } from '@/utils/downloadHelper';
import html2canvas from 'html2canvas';
import RelatoriosAssessoria from '@/components/RelatoriosAssessoria';

// Subcomponentes refatorados
import { RankingCards, MetricasCards } from '@/components/dono-assessoria/DashboardStats';
import { ExportacaoCard } from '@/components/dono-assessoria/ExportacaoCard';
import { SolicitacoesTab } from '@/components/dono-assessoria/SolicitacoesTab';
import { AtletasTab } from '@/components/dono-assessoria/AtletasTab';
import { FotoEquipeTab } from '@/components/dono-assessoria/FotoEquipeTab';
import { ChatAssessoria } from '@/components/dono-assessoria/ChatAssessoria';
import { FeedEquipe } from '@/components/dono-assessoria/FeedEquipe';

import DonoVerificacaoCard from '@/components/assessoria/DonoVerificacaoCard';
import DonoComparacaoMensal from '@/components/assessoria/DonoComparacaoMensal';
import DonoGraficosAvancados from '@/components/assessoria/DonoGraficosAvancados';
import DonoFotoTab from '@/components/assessoria/DonoFotoTab';
import { DonoRankingsTab, DonoSeloTab } from '@/components/assessoria/DonoRankingsSeloTabs';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DonoAssessoriaDashboard = () => {
  const navigate = useNavigate();
  const { user, token, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [assessoria, setAssessoria] = useState(null);
  const [atletas, setAtletas] = useState([]);
  const [rankingNacional, setRankingNacional] = useState(null);
  const [rankingEstadual, setRankingEstadual] = useState(null);
  const [rankingMensal, setRankingMensal] = useState(null);
  const [rankingAnual, setRankingAnual] = useState(null);
  const [comparacaoMensal, setComparacaoMensal] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);
  const [showMensagemModal, setShowMensagemModal] = useState(false);
  const [mensagem, setMensagem] = useState('');
  const [atletasSelecionados, setAtletasSelecionados] = useState([]);
  const [sendingMensagem, setSendingMensagem] = useState(false);
  const [downloadingCertificado, setDownloadingCertificado] = useState(false);
  const certificadoRef = useRef(null);
  
  // Estados para solicitações pendentes
  const [solicitacoesPendentes, setSolicitacoesPendentes] = useState([]);
  const [totalPendentes, setTotalPendentes] = useState(0);
  const [processandoSolicitacao, setProcessandoSolicitacao] = useState(null);
  
  // Estados para upload de foto
  const [uploadingFoto, setUploadingFoto] = useState(false);
  const fotoInputRef = useRef(null);
  
  // Estados para gráficos avançados
  const [graficosAvancados, setGraficosAvancados] = useState(null);

  useEffect(() => {
    if (!user) return;
    if (user.role !== 'dono_assessoria' && user.role !== 'admin' && user.role !== 'super_admin') {
      navigate('/');
      return;
    }
    if (!user.equipe) return; // Wait for full user data
    fetchDados();
    fetchSolicitacoesPendentes();
  }, [user]);

  const fetchDados = async () => {
    setLoading(true);
    try {
      // Buscar detalhes da assessoria do usuário
      const equipe = user.equipe;
      if (!equipe) {
        toast.error('Você não está vinculado a nenhuma equipe');
        navigate('/');
        return;
      }

      const [assessoriaRes, nacionalRes, estadualRes, mensalRes, anualRes, comparacaoRes] = await Promise.allSettled([
        axios.get(`${API}/liga-assessorias/assessoria/${encodeURIComponent(equipe)}`),
        axios.get(`${API}/liga-assessorias/ranking?tipo=nacional`),
        axios.get(`${API}/liga-assessorias/ranking?tipo=estadual&estado=${user.estado || ''}`),
        axios.get(`${API}/liga-assessorias/ranking?tipo=nacional&mes=${new Date().getMonth() + 1}`),
        axios.get(`${API}/liga-assessorias/ranking?tipo=historico`),
        axios.get(`${API}/liga-assessorias/comparacao-mensal/${encodeURIComponent(equipe)}`)
      ]);

      if (assessoriaRes.status === 'fulfilled') {
        const assessoriaData = assessoriaRes.value.data;
        setAssessoria(assessoriaData);
        setAtletas(assessoriaData.atletas || []);
        
        // Buscar gráficos avançados
        fetchGraficosAvancados(equipe);
        
        // Se temos o estado da assessoria, buscar ranking estadual correto
        if (assessoriaData.estado) {
          try {
            const estadualCorreto = await axios.get(`${API}/liga-assessorias/ranking?tipo=estadual&estado=${assessoriaData.estado}`);
            if (estadualCorreto.data?.ranking) {
              const posicao = estadualCorreto.data.ranking.find(r => r.nome === equipe);
              setRankingEstadual(posicao ? posicao.posicao : null);
            }
          } catch (e) {
            console.error('Erro ao buscar ranking estadual:', e);
          }
        }
      }
      
      // Encontrar posição nos rankings
      const findPosicao = (ranking, nome) => {
        const item = ranking.find(r => r.nome === nome);
        return item ? item.posicao : null;
      };

      if (nacionalRes.status === 'fulfilled') {
        setRankingNacional(findPosicao(nacionalRes.value.data.ranking, equipe));
      }
      // Ranking estadual já foi processado acima com o estado correto da assessoria
      if (mensalRes.status === 'fulfilled') {
        setRankingMensal(findPosicao(mensalRes.value.data.ranking, equipe));
      }
      if (anualRes.status === 'fulfilled') {
        setRankingAnual(findPosicao(anualRes.value.data.ranking, equipe));
      }
      if (comparacaoRes.status === 'fulfilled') {
        setComparacaoMensal(comparacaoRes.value.data);
      }
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
      toast.error('Erro ao carregar dados da assessoria');
    } finally {
      setLoading(false);
    }
  };

  const fetchGraficosAvancados = async (equipe) => {
    try {
      const response = await axios.get(
        `${API}/liga-assessorias/graficos-avancados/${encodeURIComponent(equipe)}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setGraficosAvancados(response.data);
    } catch (error) {
      console.error('Erro ao buscar gráficos avançados:', error);
    }
  };

  const fetchSolicitacoesPendentes = async () => {
    try {
      const response = await axios.get(`${API}/assessorias/solicitacoes-pendentes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSolicitacoesPendentes(response.data.solicitacoes || []);
      setTotalPendentes(response.data.total_pendentes || 0);
    } catch (error) {
      console.error('Erro ao buscar solicitações:', error);
    }
  };

  const handleAprovarSolicitacao = async (solicitacaoId) => {
    setProcessandoSolicitacao(solicitacaoId);
    try {
      const response = await axios.post(
        `${API}/assessorias/aprovar-solicitacao/${solicitacaoId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success(response.data.message);
      fetchSolicitacoesPendentes();
      fetchDados(); // Atualizar lista de atletas
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao aprovar solicitação');
    } finally {
      setProcessandoSolicitacao(null);
    }
  };

  const handleReprovarSolicitacao = async (solicitacaoId, motivo = 'Solicitação não aprovada') => {
    setProcessandoSolicitacao(solicitacaoId);
    try {
      const response = await axios.post(
        `${API}/assessorias/reprovar-solicitacao/${solicitacaoId}`,
        { motivo },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Solicitação reprovada');
      fetchSolicitacoesPendentes();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao reprovar solicitação');
    } finally {
      setProcessandoSolicitacao(null);
    }
  };

  // Funções de exportação de dados
  const handleExportarDados = async (formato) => {
    try {
      downloadFile(`/api/liga-assessorias/exportar-dados/${encodeURIComponent(user.equipe)}`, { formato });
      const nomeFormato = formato === 'xlsx' ? 'Excel' : formato.toUpperCase();
      toast.success(`Dados exportados em ${nomeFormato} com sucesso!`);
    } catch (error) {
      console.error('Erro ao exportar:', error);
      toast.error('Erro ao exportar dados');
    }
  };

  const handleExportarGraficos = async () => {
    try {
      downloadFile(`/api/liga-assessorias/exportar-graficos/${encodeURIComponent(user.equipe)}`);
      toast.success('Dados dos gráficos exportados com sucesso!');
    } catch (error) {
      console.error('Erro ao exportar gráficos:', error);
      toast.error('Erro ao exportar dados dos gráficos');
    }
  };

  // Funções de upload de foto
  const handleUploadFoto = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validar tamanho (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Arquivo muito grande. Máximo: 5MB');
      return;
    }

    // Validar tipo
    if (!['image/jpeg', 'image/png', 'image/webp', 'image/gif'].includes(file.type)) {
      toast.error('Tipo de arquivo não permitido. Use: JPEG, PNG, WebP ou GIF');
      return;
    }

    setUploadingFoto(true);
    try {
      const formData = new FormData();
      formData.append('foto', file);

      const response = await axios.post(
        `${API}/assessorias/upload-foto`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      toast.success(response.data.message);
      
      // Atualizar estado local
      setAssessoria(prev => ({
        ...prev,
        foto_url: response.data.foto_url
      }));
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao fazer upload da foto');
    } finally {
      setUploadingFoto(false);
      if (fotoInputRef.current) {
        fotoInputRef.current.value = '';
      }
    }
  };

  const handleRemoverFoto = async () => {
    if (!window.confirm('Tem certeza que deseja remover a foto da assessoria?')) return;

    setUploadingFoto(true);
    try {
      await axios.delete(`${API}/assessorias/remover-foto`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Foto removida com sucesso');
      setAssessoria(prev => ({
        ...prev,
        foto_url: ''
      }));
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao remover foto');
    } finally {
      setUploadingFoto(false);
    }
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
      case 'ouro': return 'bg-gradient-to-r from-yellow-500 to-amber-600';
      case 'prata': return 'bg-gradient-to-r from-slate-400 to-slate-500';
      case 'bronze': return 'bg-gradient-to-r from-amber-700 to-orange-800';
      default: return 'bg-slate-600';
    }
  };

  const getSeloTitle = (selo) => {
    switch(selo) {
      case 'ouro': return 'TOP 20 NACIONAL';
      case 'prata': return 'TOP 10 ESTADUAL';
      case 'bronze': return 'ASSESSORIA INTEGRANTE';
      default: return 'PARTICIPANTE';
    }
  };

  const enviarMensagem = async () => {
    if (!mensagem.trim()) {
      toast.error('Digite uma mensagem');
      return;
    }

    const destinatarios = atletasSelecionados.length > 0 
      ? atletasSelecionados 
      : atletas.map(a => a.id);

    if (destinatarios.length === 0) {
      toast.error('Selecione ao menos um atleta');
      return;
    }

    setSendingMensagem(true);
    try {
      await axios.post(`${API}/notificacoes/enviar`, {
        destinatarios,
        mensagem,
        tipo: 'mensagem_assessoria',
        titulo: `Mensagem de ${user.equipe}`
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(`Mensagem enviada para ${destinatarios.length} atleta(s)!`);
      setShowMensagemModal(false);
      setMensagem('');
      setAtletasSelecionados([]);
    } catch (error) {
      toast.error('Erro ao enviar mensagem');
    } finally {
      setSendingMensagem(false);
    }
  };

  const handleDesvincular = async (atletaId, motivo) => {
    try {
      await axios.post(`${API}/assessoria/desvincular-atleta`, {
        atleta_id: atletaId,
        motivo
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Atleta desvinculado com sucesso!');
      setAtletas(prev => prev.filter(a => a.id !== atletaId));
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao desvincular');
      throw error;
    }
  };

  const downloadCertificado = async () => {
    if (!certificadoRef.current) return;
    
    setDownloadingCertificado(true);
    try {
      const canvas = await html2canvas(certificadoRef.current, {
        scale: 2,
        backgroundColor: null,
        useCORS: true
      });
      
      const link = document.createElement('a');
      link.download = `selo_${assessoria.nome.replace(/\s+/g, '_')}_ROE-RR_2026.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (error) {
      console.error('Erro ao gerar certificado:', error);
    } finally {
      setDownloadingCertificado(false);
    }
  };

  const exportarAtletas = () => {
    const headers = ['Nome', 'Categoria', 'Gênero', 'Pontos'];
    const rows = atletas.map(a => [a.nome, a.categoria || '', a.genero || '', a.pontos || 0]);
    const csvContent = '\ufeff' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `atletas_${user.equipe.replace(/\s+/g, '_')}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Lista de atletas exportada!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
      </div>
    );
  }

  if (!assessoria) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex flex-col items-center justify-center">
        <Award className="w-16 h-16 text-slate-500 mb-4" />
        <h2 className="text-xl font-semibold text-white">Assessoria não encontrada</h2>
        <Button onClick={() => navigate('/')} className="mt-4" variant="outline">
          Voltar ao Ranking
        </Button>
      </div>
    );
  }

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'solicitacoes', label: 'Solicitacoes', icon: UserPlus, badge: totalPendentes },
    { id: 'atletas', label: 'Meus Atletas', icon: Users },
    { id: 'mensagens', label: 'Chat', icon: MessageSquare },
    { id: 'feed', label: 'Feed da Equipe', icon: Send },
    { id: 'foto', label: 'Foto da Equipe', icon: Camera },
    { id: 'relatorios', label: 'Relatorios', icon: PieChart },
    { id: 'rankings', label: 'Rankings', icon: Trophy },
    { id: 'selo', label: 'Selo Oficial', icon: Award },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex">
      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 bg-slate-950 border-b border-slate-800 px-4 py-3 flex items-center justify-between">
        <button
          onClick={() => setShowMobileSidebar(true)}
          className="p-2 rounded-lg text-white hover:bg-slate-800"
          data-testid="btn-sidebar-toggle"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h1 className="font-bold text-white text-sm truncate">{assessoria?.nome || 'Assessoria'}</h1>
        <div className="w-9" />
      </div>

      {/* Overlay mobile */}
      {showMobileSidebar && (
        <div
          className="fixed inset-0 z-[60] bg-black/60 backdrop-blur-sm md:hidden"
          onClick={() => setShowMobileSidebar(false)}
        />
      )}

      {/* Sidebar - hidden on mobile, drawer on mobile when open */}
      <div className={`
        fixed md:sticky top-0 left-0 z-[61] md:z-auto h-full w-64 bg-slate-950 p-4 flex flex-col
        transition-transform duration-300 ease-out
        ${showMobileSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-white text-sm">Painel da Assessoria</h1>
              <p className="text-xs text-slate-400 truncate">{user?.equipe}</p>
            </div>
          </div>
          <button
            onClick={() => setShowMobileSidebar(false)}
            className="md:hidden p-1 rounded-lg text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-2">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => { setActiveTab(item.id); setShowMobileSidebar(false); }}
              data-testid={`menu-${item.id}`}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === item.id
                  ? 'bg-amber-500 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-sm font-medium flex-1 text-left">{item.label}</span>
              {item.badge > 0 && (
                <Badge className="bg-red-500 text-white text-xs px-2 py-0.5 animate-pulse" data-testid="badge-pendentes">
                  {item.badge}
                </Badge>
              )}
            </button>
          ))}
        </nav>

        <div className="border-t border-slate-800 pt-4 space-y-2">
          <Button 
            variant="ghost" 
            className="w-full justify-start text-slate-400 hover:text-white"
            onClick={() => navigate('/')}
          >
            <Home className="w-4 h-4 mr-2" />
            Voltar ao Site
          </Button>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-slate-400 hover:text-white"
            onClick={logout}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sair
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-4 md:p-8 overflow-auto pt-16 md:pt-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                  {getSeloIcon(assessoria.selo)} {assessoria.nome}
                </h2>
                <p className="text-slate-400 flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  {assessoria.cidade}/{assessoria.estado}
                </p>
              </div>
              <Badge className={`${getSeloColor(assessoria.selo)} text-white px-4 py-2`}>
                {getSeloTitle(assessoria.selo)}
              </Badge>
            </div>

            {/* Stats Cards - Ranking */}
            <RankingCards 
              rankingNacional={rankingNacional}
              rankingEstadual={rankingEstadual}
              rankingMensal={rankingMensal}
              rankingAnual={rankingAnual}
            />

            {/* Métricas */}
            <MetricasCards assessoria={assessoria} />

            {/* Card de Progresso para Verificação - Extraído */}
            <DonoVerificacaoCard assessoria={assessoria} />
            {/* Comparação Mensal - Extraído */}
            <DonoComparacaoMensal comparacaoMensal={comparacaoMensal} />
            {/* Grid de Gráficos Adicionais - Extraído */}
            <DonoGraficosAvancados 
              graficosAvancados={graficosAvancados} 
              atletas={atletas} 
              assessoria={assessoria} 
            />

            {/* Botões de Exportação */}
            {assessoria && (
              <ExportacaoCard
                onExportarDados={handleExportarDados}
                onExportarGraficos={handleExportarGraficos}
              />
            )}

            {/* Posições nos Rankings */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Target className="w-5 h-5 text-blue-500" />
                  Posições nos Rankings
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-lg border border-amber-500/20">
                    <div className="flex items-center gap-3">
                      <Trophy className="w-6 h-6 text-amber-500" />
                      <div>
                        <p className="text-sm text-slate-400">Nacional</p>
                        <p className="text-white font-medium">Todas as Assessorias</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-amber-500">{rankingNacional || '-'}º</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-lg border border-blue-500/20">
                    <div className="flex items-center gap-3">
                      <MapPin className="w-6 h-6 text-blue-500" />
                      <div>
                        <p className="text-sm text-slate-400">Estadual ({assessoria.estado})</p>
                        <p className="text-white font-medium">No seu Estado</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-blue-500">{rankingEstadual || '-'}º</p>
                    </div>
                  </div>
                  
                  {rankingMensal && (
                    <div className="flex items-center justify-between p-3 bg-gradient-to-r from-emerald-500/10 to-green-500/10 rounded-lg border border-emerald-500/20">
                      <div className="flex items-center gap-3">
                        <Calendar className="w-6 h-6 text-emerald-500" />
                        <div>
                          <p className="text-sm text-slate-400">Mensal</p>
                          <p className="text-white font-medium">Este Mês</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-3xl font-bold text-emerald-500">{rankingMensal}º</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Solicitações Tab */}
        {activeTab === 'solicitacoes' && (
          <SolicitacoesTab
            solicitacoesPendentes={solicitacoesPendentes}
            totalPendentes={totalPendentes}
            processandoSolicitacao={processandoSolicitacao}
            onAtualizar={fetchSolicitacoesPendentes}
            onAprovar={handleAprovarSolicitacao}
            onReprovar={handleReprovarSolicitacao}
            onVerPerfil={(atletaId) => navigate(`/atleta/${atletaId}`)}
          />
        )}

        {/* Atletas Tab */}
        {activeTab === 'atletas' && (
          <AtletasTab
            atletas={atletas}
            onExportar={exportarAtletas}
            onEnviarMensagem={() => setActiveTab('mensagens')}
            onVerPerfil={(atletaId) => navigate(`/atleta/${atletaId}`)}
            onDesvincular={handleDesvincular}
          />
        )}

        {/* Foto da Equipe Tab */}
        {activeTab === 'foto' && (
          <DonoFotoTab 
            assessoria={assessoria}
            token={token}
            onFotoUpdated={fetchDados}
            getSeloColor={getSeloColor}
            getSeloIcon={getSeloIcon}
          />
        )}
        {/* Relatórios Tab */}
        {activeTab === 'relatorios' && (
          <RelatoriosAssessoria equipe={user?.equipe} token={token} />
        )}

        {/* Rankings Tab */}
        {activeTab === 'rankings' && (
          <DonoRankingsTab 
            assessoria={assessoria}
            rankingNacional={rankingNacional}
            rankingEstadual={rankingEstadual}
            rankingMensal={rankingMensal}
            rankingAnual={rankingAnual}
          />
        )}
        {/* Mensagens/Chat Tab */}
        {activeTab === 'mensagens' && (
          <ChatAssessoria 
            atletas={atletas}
            token={token}
            userId={user.id}
          />
        )}

        {/* Feed da Equipe Tab */}
        {activeTab === 'feed' && (
          <FeedEquipe
            token={token}
            userId={user.id}
            equipe={user.equipe}
            isDonoAssessoria={true}
          />
        )}

        {/* Selo Tab */}
        {activeTab === 'selo' && (
          <DonoSeloTab 
            assessoria={assessoria} 
            getSeloColor={getSeloColor} 
            getSeloIcon={getSeloIcon} 
            getSeloTitle={getSeloTitle} 
          />
        )}
      {/* Modal Mensagem */}
      <Dialog open={showMensagemModal} onOpenChange={setShowMensagemModal}>
        <DialogContent className="bg-slate-800 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">Enviar Mensagem</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Textarea
              value={mensagem}
              onChange={(e) => setMensagem(e.target.value)}
              placeholder="Digite sua mensagem..."
              className="bg-slate-900 border-slate-700 text-white"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowMensagemModal(false)}>
              Cancelar
            </Button>
            <Button onClick={enviarMensagem} disabled={sendingMensagem} className="bg-amber-500">
              Enviar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      </div>
    </div>
  );
};

export default DonoAssessoriaDashboard;
