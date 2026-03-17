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
  BadgeCheck, Crown, X, ShieldCheck
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import html2canvas from 'html2canvas';
import RelatoriosAssessoria from '@/components/RelatoriosAssessoria';

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
  const [showMensagemModal, setShowMensagemModal] = useState(false);
  const [mensagem, setMensagem] = useState('');
  const [atletasSelecionados, setAtletasSelecionados] = useState([]);
  const [sendingMensagem, setSendingMensagem] = useState(false);
  const [downloadingCertificado, setDownloadingCertificado] = useState(false);
  const certificadoRef = useRef(null);

  useEffect(() => {
    if (!user || user.role !== 'dono_assessoria') {
      navigate('/');
      return;
    }
    fetchDados();
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
        axios.get(`${API}/liga-assessorias/ranking?tipo=estadual&estado=${user.estado}`),
        axios.get(`${API}/liga-assessorias/ranking?tipo=nacional&mes=${new Date().getMonth() + 1}`),
        axios.get(`${API}/liga-assessorias/ranking?tipo=historico`),
        axios.get(`${API}/liga-assessorias/comparacao-mensal/${encodeURIComponent(equipe)}`)
      ]);

      if (assessoriaRes.status === 'fulfilled') {
        setAssessoria(assessoriaRes.value.data);
        setAtletas(assessoriaRes.value.data.atletas || []);
      }
      
      // Encontrar posição nos rankings
      const findPosicao = (ranking, nome) => {
        const item = ranking.find(r => r.nome === nome);
        return item ? item.posicao : null;
      };

      if (nacionalRes.status === 'fulfilled') {
        setRankingNacional(findPosicao(nacionalRes.value.data.ranking, equipe));
      }
      if (estadualRes.status === 'fulfilled') {
        setRankingEstadual(findPosicao(estadualRes.value.data.ranking, equipe));
      }
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
    // Criar CSV dos atletas
    const headers = ['Nome', 'Categoria', 'Gênero', 'Pontos'];
    const rows = atletas.map(a => [a.nome, a.categoria || '', a.genero || '', a.pontos || 0]);
    
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `atletas_${user.equipe.replace(/\s+/g, '_')}.csv`;
    link.click();
    
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
    { id: 'atletas', label: 'Meus Atletas', icon: Users },
    { id: 'relatorios', label: 'Relatórios', icon: PieChart },
    { id: 'rankings', label: 'Rankings', icon: Trophy },
    { id: 'mensagens', label: 'Mensagens', icon: MessageSquare },
    { id: 'selo', label: 'Selo Oficial', icon: Award },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex">
      {/* Sidebar */}
      <div className="w-64 bg-slate-950 p-4 flex flex-col">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
            <Award className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white text-sm">Painel da Assessoria</h1>
            <p className="text-xs text-slate-400 truncate">{user?.equipe}</p>
          </div>
        </div>

        <nav className="flex-1 space-y-2">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === item.id
                  ? 'bg-amber-500 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
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
      <div className="flex-1 p-8 overflow-auto">
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

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-sm">Ranking Nacional</p>
                      <p className="text-3xl font-bold text-amber-500">{rankingNacional || '-'}º</p>
                    </div>
                    <Trophy className="w-10 h-10 text-amber-500/30" />
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-sm">Ranking Estadual</p>
                      <p className="text-3xl font-bold text-blue-500">{rankingEstadual || '-'}º</p>
                    </div>
                    <MapPin className="w-10 h-10 text-blue-500/30" />
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-sm">Ranking Mensal</p>
                      <p className="text-3xl font-bold text-emerald-500">{rankingMensal || '-'}º</p>
                    </div>
                    <Calendar className="w-10 h-10 text-emerald-500/30" />
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-sm">Ranking Anual</p>
                      <p className="text-3xl font-bold text-purple-500">{rankingAnual || '-'}º</p>
                    </div>
                    <Target className="w-10 h-10 text-purple-500/30" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Métricas */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-gradient-to-br from-emerald-600 to-emerald-700">
                <CardContent className="p-6 text-white">
                  <Users className="w-8 h-8 mb-2 opacity-80" />
                  <p className="text-3xl font-bold">{assessoria.total_atletas}</p>
                  <p className="text-sm opacity-80">Atletas</p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-blue-600 to-blue-700">
                <CardContent className="p-6 text-white">
                  <CheckCircle className="w-8 h-8 mb-2 opacity-80" />
                  <p className="text-3xl font-bold">{assessoria.total_resultados}</p>
                  <p className="text-sm opacity-80">Resultados</p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-yellow-600 to-yellow-700">
                <CardContent className="p-6 text-white">
                  <Medal className="w-8 h-8 mb-2 opacity-80" />
                  <p className="text-3xl font-bold">{assessoria.total_primeiros}</p>
                  <p className="text-sm opacity-80">1º Lugares</p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-amber-600 to-amber-700">
                <CardContent className="p-6 text-white">
                  <Award className="w-8 h-8 mb-2 opacity-80" />
                  <p className="text-3xl font-bold">{assessoria.pontos_total}</p>
                  <p className="text-sm opacity-80">Pontos Total</p>
                </CardContent>
              </Card>
            </div>

            {/* Card de Progresso para Verificação */}
            {(() => {
              const isVerificada = assessoria.responsavel_nome && 
                                   assessoria.total_atletas >= 10 && 
                                   assessoria.total_resultados >= 5;
              const atletasProgress = Math.min((assessoria.total_atletas / 10) * 100, 100);
              const resultadosProgress = Math.min((assessoria.total_resultados / 5) * 100, 100);
              const donoProgress = assessoria.responsavel_nome ? 100 : 0;
              const progressoTotal = Math.round((atletasProgress + resultadosProgress + donoProgress) / 3);
              
              return (
                <Card className={`border-2 ${isVerificada ? 'bg-gradient-to-br from-blue-900/50 to-indigo-900/50 border-blue-500' : 'bg-slate-800/50 border-slate-600'}`}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-white flex items-center gap-2">
                        <ShieldCheck className={`w-5 h-5 ${isVerificada ? 'text-blue-400' : 'text-slate-400'}`} />
                        Progresso para Verificação
                      </CardTitle>
                      {isVerificada ? (
                        <Badge className="bg-blue-500 text-white flex items-center gap-1">
                          <BadgeCheck className="w-4 h-4" />
                          Verificada
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-slate-400 border-slate-500">
                          {progressoTotal}% completo
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    {isVerificada ? (
                      <div className="text-center py-4">
                        <div className="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-3">
                          <BadgeCheck className="w-10 h-10 text-blue-400" />
                        </div>
                        <p className="text-blue-300 font-medium">Parabéns! Sua assessoria é verificada!</p>
                        <p className="text-slate-400 text-sm mt-1">
                          O selo de verificação aparece em toda a plataforma.
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <p className="text-slate-400 text-sm mb-4">
                          Complete os critérios abaixo para obter o selo de verificação da sua assessoria.
                        </p>
                        
                        {/* Critério 1: Atletas */}
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2">
                              <Users className={`w-4 h-4 ${assessoria.total_atletas >= 10 ? 'text-emerald-400' : 'text-slate-400'}`} />
                              <span className="text-sm text-slate-300">10+ Atletas</span>
                            </div>
                            <span className={`text-sm font-medium ${assessoria.total_atletas >= 10 ? 'text-emerald-400' : 'text-slate-400'}`}>
                              {assessoria.total_atletas}/10
                              {assessoria.total_atletas >= 10 && <CheckCircle className="w-4 h-4 inline ml-1" />}
                            </span>
                          </div>
                          <Progress value={atletasProgress} className="h-2" />
                          {assessoria.total_atletas < 10 && (
                            <p className="text-xs text-slate-500 mt-1">
                              Faltam {10 - assessoria.total_atletas} atletas para completar
                            </p>
                          )}
                        </div>
                        
                        {/* Critério 2: Resultados */}
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2">
                              <CheckCircle className={`w-4 h-4 ${assessoria.total_resultados >= 5 ? 'text-emerald-400' : 'text-slate-400'}`} />
                              <span className="text-sm text-slate-300">5+ Resultados</span>
                            </div>
                            <span className={`text-sm font-medium ${assessoria.total_resultados >= 5 ? 'text-emerald-400' : 'text-slate-400'}`}>
                              {assessoria.total_resultados}/5
                              {assessoria.total_resultados >= 5 && <CheckCircle className="w-4 h-4 inline ml-1" />}
                            </span>
                          </div>
                          <Progress value={resultadosProgress} className="h-2" />
                          {assessoria.total_resultados < 5 && (
                            <p className="text-xs text-slate-500 mt-1">
                              Faltam {5 - assessoria.total_resultados} resultados para completar
                            </p>
                          )}
                        </div>
                        
                        {/* Critério 3: Dono */}
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2">
                              <Crown className={`w-4 h-4 ${assessoria.responsavel_nome ? 'text-emerald-400' : 'text-slate-400'}`} />
                              <span className="text-sm text-slate-300">Dono Definido</span>
                            </div>
                            <span className={`text-sm font-medium ${assessoria.responsavel_nome ? 'text-emerald-400' : 'text-slate-400'}`}>
                              {assessoria.responsavel_nome ? (
                                <>Completo <CheckCircle className="w-4 h-4 inline ml-1" /></>
                              ) : (
                                'Pendente'
                              )}
                            </span>
                          </div>
                          <Progress value={donoProgress} className="h-2" />
                        </div>
                        
                        {/* Link para página de ajuda */}
                        <div className="pt-2 border-t border-slate-700">
                          <Button 
                            variant="link" 
                            className="text-blue-400 hover:text-blue-300 p-0 h-auto"
                            onClick={() => navigate('/como-ser-verificado')}
                          >
                            Saiba mais sobre como ser verificado →
                          </Button>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })()}

            {/* Comparação Mensal */}
            {comparacaoMensal && (
              <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-amber-500/30">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-amber-500" />
                    Comparação de Desempenho: {comparacaoMensal.mes_atual.nome} vs {comparacaoMensal.mes_anterior.nome}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {/* Resultados */}
                    <div className="bg-slate-800 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm">Resultados</span>
                        <span className={`flex items-center text-xs font-medium ${
                          comparacaoMensal.variacoes.resultados > 0 ? 'text-green-400' :
                          comparacaoMensal.variacoes.resultados < 0 ? 'text-red-400' : 'text-slate-400'
                        }`}>
                          {comparacaoMensal.variacoes.resultados > 0 ? <ArrowUpRight className="w-3 h-3" /> :
                           comparacaoMensal.variacoes.resultados < 0 ? <ArrowDownRight className="w-3 h-3" /> :
                           <Minus className="w-3 h-3" />}
                          {Math.abs(comparacaoMensal.variacoes.resultados)}%
                        </span>
                      </div>
                      <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-white">{comparacaoMensal.mes_atual.resultados}</span>
                        <span className="text-sm text-slate-500">vs {comparacaoMensal.mes_anterior.resultados}</span>
                      </div>
                    </div>

                    {/* Pontos */}
                    <div className="bg-slate-800 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm">Pontos Conquistados</span>
                        <span className={`flex items-center text-xs font-medium ${
                          comparacaoMensal.variacoes.pontos > 0 ? 'text-green-400' :
                          comparacaoMensal.variacoes.pontos < 0 ? 'text-red-400' : 'text-slate-400'
                        }`}>
                          {comparacaoMensal.variacoes.pontos > 0 ? <ArrowUpRight className="w-3 h-3" /> :
                           comparacaoMensal.variacoes.pontos < 0 ? <ArrowDownRight className="w-3 h-3" /> :
                           <Minus className="w-3 h-3" />}
                          {Math.abs(comparacaoMensal.variacoes.pontos)}%
                        </span>
                      </div>
                      <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-amber-500">{comparacaoMensal.mes_atual.pontos}</span>
                        <span className="text-sm text-slate-500">vs {comparacaoMensal.mes_anterior.pontos}</span>
                      </div>
                    </div>

                    {/* Novos Atletas */}
                    <div className="bg-slate-800 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm">Novos Atletas</span>
                        <span className={`flex items-center text-xs font-medium ${
                          comparacaoMensal.variacoes.novos_atletas > 0 ? 'text-green-400' :
                          comparacaoMensal.variacoes.novos_atletas < 0 ? 'text-red-400' : 'text-slate-400'
                        }`}>
                          {comparacaoMensal.variacoes.novos_atletas > 0 ? <ArrowUpRight className="w-3 h-3" /> :
                           comparacaoMensal.variacoes.novos_atletas < 0 ? <ArrowDownRight className="w-3 h-3" /> :
                           <Minus className="w-3 h-3" />}
                          {Math.abs(comparacaoMensal.variacoes.novos_atletas)}%
                        </span>
                      </div>
                      <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-blue-400">{comparacaoMensal.mes_atual.novos_atletas}</span>
                        <span className="text-sm text-slate-500">vs {comparacaoMensal.mes_anterior.novos_atletas}</span>
                      </div>
                    </div>

                    {/* Posição no Ranking */}
                    <div className="bg-slate-800 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm">Posição Ranking</span>
                        <span className={`flex items-center text-xs font-medium ${
                          comparacaoMensal.variacoes.posicao > 0 ? 'text-green-400' :
                          comparacaoMensal.variacoes.posicao < 0 ? 'text-red-400' : 'text-slate-400'
                        }`}>
                          {comparacaoMensal.variacoes.posicao > 0 ? <ArrowUpRight className="w-3 h-3" /> :
                           comparacaoMensal.variacoes.posicao < 0 ? <ArrowDownRight className="w-3 h-3" /> :
                           <Minus className="w-3 h-3" />}
                          {Math.abs(comparacaoMensal.variacoes.posicao)} pos
                        </span>
                      </div>
                      <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-purple-400">
                          {comparacaoMensal.mes_atual.posicao_ranking || '-'}º
                        </span>
                        <span className="text-sm text-slate-500">
                          vs {comparacaoMensal.mes_anterior.posicao_ranking || '-'}º
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Mensagem de Performance */}
                  <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20">
                    <p className="text-amber-200 text-sm">
                      {comparacaoMensal.variacoes.pontos > 0 
                        ? `Parabéns! Sua assessoria cresceu ${comparacaoMensal.variacoes.pontos}% em pontos este mês.`
                        : comparacaoMensal.variacoes.pontos < 0
                        ? `Atenção: Queda de ${Math.abs(comparacaoMensal.variacoes.pontos)}% nos pontos. Incentive seus atletas a participar de mais corridas!`
                        : `Desempenho estável. Continue motivando seus atletas!`
                      }
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Evolução */}
            {assessoria.evolucao_mensal && assessoria.evolucao_mensal.length > 0 && (
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-amber-500" />
                    Evolução Mensal
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={assessoria.evolucao_mensal}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="mes" stroke="#9CA3AF" tick={{ fontSize: 12 }} />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                      <Area type="monotone" dataKey="resultados" fill="#F59E0B" stroke="#D97706" fillOpacity={0.3} name="Resultados" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Atletas Tab */}
        {activeTab === 'atletas' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Meus Atletas</h2>
              <div className="flex gap-2">
                <Button variant="outline" onClick={exportarAtletas}>
                  <Download className="w-4 h-4 mr-2" />
                  Exportar Lista
                </Button>
                <Button onClick={() => setShowMensagemModal(true)} className="bg-amber-500 hover:bg-amber-600">
                  <Send className="w-4 h-4 mr-2" />
                  Enviar Mensagem
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {atletas.map((atleta) => (
                <Card key={atleta.id} className="bg-slate-800 border-slate-700 hover:border-amber-500/50 transition-colors">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <Avatar className="w-14 h-14">
                        {atleta.foto_url ? (
                          <AvatarImage src={atleta.foto_url.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                        ) : null}
                        <AvatarFallback className="bg-amber-500 text-white text-lg">
                          {atleta.nome?.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <h3 className="font-semibold text-white">{atleta.nome}</h3>
                        <div className="flex gap-2 mt-1">
                          <Badge variant="outline" className="text-xs text-slate-400 border-slate-600">
                            {atleta.categoria?.toUpperCase() || 'NORMAL'}
                          </Badge>
                          <Badge variant="outline" className="text-xs text-slate-400 border-slate-600">
                            {atleta.genero === 'M' ? 'Masc' : 'Fem'}
                          </Badge>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-amber-500">{atleta.pontos || 0}</p>
                        <p className="text-xs text-slate-400">pontos</p>
                      </div>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="flex-1 border-slate-600 text-slate-300"
                        onClick={() => navigate(`/atleta/${atleta.id}`)}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        Ver Perfil
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Relatórios Tab */}
        {activeTab === 'relatorios' && (
          <RelatoriosAssessoria equipe={user?.equipe} token={token} />
        )}

        {/* Rankings Tab */}
        {activeTab === 'rankings' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">Posição nos Rankings</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="border-b border-slate-700">
                  <CardTitle className="text-white flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-amber-500" />
                    Ranking Nacional
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 text-center">
                  <p className="text-6xl font-bold text-amber-500 mb-2">{rankingNacional || '-'}º</p>
                  <p className="text-slate-400">de todas as assessorias do Brasil</p>
                </CardContent>
              </Card>
              
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="border-b border-slate-700">
                  <CardTitle className="text-white flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-blue-500" />
                    Ranking Estadual ({assessoria.estado})
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 text-center">
                  <p className="text-6xl font-bold text-blue-500 mb-2">{rankingEstadual || '-'}º</p>
                  <p className="text-slate-400">no estado de {assessoria.estado}</p>
                </CardContent>
              </Card>
              
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="border-b border-slate-700">
                  <CardTitle className="text-white flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-emerald-500" />
                    Ranking Mensal
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 text-center">
                  <p className="text-6xl font-bold text-emerald-500 mb-2">{rankingMensal || '-'}º</p>
                  <p className="text-slate-400">neste mês</p>
                </CardContent>
              </Card>
              
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="border-b border-slate-700">
                  <CardTitle className="text-white flex items-center gap-2">
                    <Target className="w-5 h-5 text-purple-500" />
                    Ranking Anual
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 text-center">
                  <p className="text-6xl font-bold text-purple-500 mb-2">{rankingAnual || '-'}º</p>
                  <p className="text-slate-400">no ano de 2026</p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Mensagens Tab */}
        {activeTab === 'mensagens' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Enviar Mensagem</h2>
            </div>

            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-6 space-y-4">
                <div>
                  <Label className="text-slate-300">Selecionar Atletas</Label>
                  <p className="text-xs text-slate-500 mb-2">Deixe em branco para enviar para todos</p>
                  <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto p-2 bg-slate-900 rounded-lg">
                    {atletas.map((atleta) => (
                      <button
                        key={atleta.id}
                        onClick={() => {
                          if (atletasSelecionados.includes(atleta.id)) {
                            setAtletasSelecionados(atletasSelecionados.filter(id => id !== atleta.id));
                          } else {
                            setAtletasSelecionados([...atletasSelecionados, atleta.id]);
                          }
                        }}
                        className={`px-3 py-1 rounded-full text-sm transition-colors ${
                          atletasSelecionados.includes(atleta.id)
                            ? 'bg-amber-500 text-white'
                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        }`}
                      >
                        {atleta.nome?.split(' ')[0]}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <Label className="text-slate-300">Mensagem</Label>
                  <Textarea
                    value={mensagem}
                    onChange={(e) => setMensagem(e.target.value)}
                    placeholder="Digite sua mensagem para os atletas..."
                    className="bg-slate-900 border-slate-700 text-white min-h-32"
                  />
                </div>

                <Button 
                  className="w-full bg-amber-500 hover:bg-amber-600"
                  onClick={enviarMensagem}
                  disabled={sendingMensagem}
                >
                  {sendingMensagem ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Enviar Mensagem ({atletasSelecionados.length || atletas.length} atletas)
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Selo Tab */}
        {activeTab === 'selo' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">Selo Oficial ROE-RR</h2>

            <div className="max-w-md mx-auto">
              {/* Certificado */}
              <div 
                ref={certificadoRef}
                className={`${getSeloColor(assessoria.selo)} text-white p-8 rounded-xl text-center shadow-2xl`}
              >
                <div className="text-6xl mb-4">{getSeloIcon(assessoria.selo)}</div>
                <h3 className="text-2xl font-bold mb-2">{getSeloTitle(assessoria.selo)}</h3>
                <p className="text-xl font-semibold mb-4">{assessoria.nome}</p>
                <div className="border-t border-white/30 pt-4">
                  <p className="text-sm opacity-90">Liga Nacional de Assessorias</p>
                  <p className="text-lg font-semibold">Ranking Run</p>
                  <p className="text-xs opacity-75 mt-2">Classificação Oficial ROE-RR – 2026</p>
                </div>
              </div>

              <Button 
                className="w-full mt-6 bg-amber-500 hover:bg-amber-600" 
                onClick={downloadCertificado}
                disabled={downloadingCertificado}
              >
                {downloadingCertificado ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Gerando...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Baixar Selo Oficial
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </div>

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
  );
};

export default DonoAssessoriaDashboard;
