import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import RankingTable from '@/components/RankingTable';
import RankingDestaques from '@/components/RankingDestaques';
import NotificacoesBell from '@/components/NotificacoesBell';
import { Search, HelpCircle, LogIn, Upload, FileDown, Shield, LogOut, User, Share2, Trophy, Flame, Users, MapPin, Target, Award, CheckCircle, TrendingUp, RefreshCw, Eye, Send, Loader2, Star, FileText, BadgeCheck, MessageSquare, History } from 'lucide-react';
import { RegulamentoButton } from '@/components/RegulamentoModal';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, LineChart, Line, Legend } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RankingPage = () => {
  const navigate = useNavigate();
  const { user, token, isAdmin, logout } = useAuth();
  const [categoriaAtual, setCategoriaAtual] = useState('masculino');
  const [rankingData, setRankingData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDestaques, setShowDestaques] = useState(true);
  
  // Ranking da Galera
  const [tipoRanking, setTipoRanking] = useState('profissional'); // 'profissional', 'povao' ou 'equipes'
  const [generoPovao, setGeneroPovao] = useState('M');
  const [rankingPovao, setRankingPovao] = useState([]);
  const [povaoStats, setPovaoStats] = useState(null);
  const [loadingPovao, setLoadingPovao] = useState(false);
  const [showDestaquePovao, setShowDestaquePovao] = useState(true);
  const [showComoFuncionaPovao, setShowComoFuncionaPovao] = useState(false);
  const [showRegulamentoPovao, setShowRegulamentoPovao] = useState(false);
  const [povaoRankingSemanal, setPovaoRankingSemanal] = useState([]);
  const [povaoRankingMensal, setPovaoRankingMensal] = useState([]);
  const [povaoDestaqueMes, setPovaoDestaqueMes] = useState(null);
  const [periodoRankingPovao, setPeriodoRankingPovao] = useState('semanal'); // 'semanal' ou 'mensal'
  
  // Liga de Assessorias (Equipes)
  const [ligaRanking, setLigaRanking] = useState([]);
  const [ligaStats, setLigaStats] = useState(null);
  const [ligaTipo, setLigaTipo] = useState('nacional');
  const [ligaEstado, setLigaEstado] = useState('');
  const [ligaCidade, setLigaCidade] = useState('');
  const [ligaMes, setLigaMes] = useState(''); // Novo: filtro por mês
  const [loadingLiga, setLoadingLiga] = useState(false);
  const [estadosComAssessorias, setEstadosComAssessorias] = useState([]);
  const [cidadesComAssessorias, setCidadesComAssessorias] = useState([]);
  const [assessoriaDetalhe, setAssessoriaDetalhe] = useState(null);
  const [showAssessoriaModal, setShowAssessoriaModal] = useState(false);
  const [evolucaoMensal, setEvolucaoMensal] = useState(null); // Dados do gráfico de evolução
  const [showEvolucaoChart, setShowEvolucaoChart] = useState(true); // Toggle para mostrar/ocultar gráfico
  const [showComoFuncionaEquipes, setShowComoFuncionaEquipes] = useState(false);
  const [showRegulamentoEquipes, setShowRegulamentoEquipes] = useState(false);
  
  // Meses disponíveis para filtro (apenas meses passados ou atual)
  const getMesesDisponiveis = () => {
    const mesAtual = new Date().getMonth() + 1; // 1-12
    const meses = [
      { value: '1', label: 'Janeiro' },
      { value: '2', label: 'Fevereiro' },
      { value: '3', label: 'Março' },
      { value: '4', label: 'Abril' },
      { value: '5', label: 'Maio' },
      { value: '6', label: 'Junho' },
      { value: '7', label: 'Julho' },
      { value: '8', label: 'Agosto' },
      { value: '9', label: 'Setembro' },
      { value: '10', label: 'Outubro' },
      { value: '11', label: 'Novembro' },
      { value: '12', label: 'Dezembro' }
    ];
    return meses.filter(m => parseInt(m.value) <= mesAtual);
  };
  
  // Filtros
  const [filtroNome, setFiltroNome] = useState('');
  const [filtroColocacao, setFiltroColocacao] = useState('');
  const [filtroUF, setFiltroUF] = useState('');
  const [filtroFaixa, setFiltroFaixa] = useState('');
  const [filtroEquipe, setFiltroEquipe] = useState('');
  const [filtroCidade, setFiltroCidade] = useState('');
  
  // Filtros da Galera
  const [filtroNomePovao, setFiltroNomePovao] = useState('');
  const [filtroColocacaoPovao, setFiltroColocacaoPovao] = useState('');
  const [filtroUFPovao, setFiltroUFPovao] = useState('');
  const [filtroFaixaPovao, setFiltroFaixaPovao] = useState('');
  const [filtroEquipePovao, setFiltroEquipePovao] = useState('');
  const [filtroCidadePovao, setFiltroCidadePovao] = useState('');
  
  // Dados auxiliares
  const [faixasDisponiveis, setFaixasDisponiveis] = useState([]);
  const [equipesDisponiveis, setEquipesDisponiveis] = useState([]);

  // Buscar dados auxiliares
  useEffect(() => {
    const fetchAuxData = async () => {
      try {
        const [faixasRes, equipesRes] = await Promise.all([
          axios.get(`${API}/ranking/faixas-etarias`),
          axios.get(`${API}/ranking/equipes`)
        ]);
        setFaixasDisponiveis(faixasRes.data.faixas || []);
        setEquipesDisponiveis(equipesRes.data.equipes || []);
      } catch (error) {
        console.error('Erro ao buscar dados auxiliares:', error);
      }
    };
    fetchAuxData();
  }, []);

  // Buscar ranking
  useEffect(() => {
    const fetchRanking = async () => {
      setLoading(true);
      try {
        let url = `${API}/ranking/categoria/${categoriaAtual}/M?ano=2025`;
        
        // Adicionar filtros à URL
        if (filtroFaixa) url += `&faixa=${filtroFaixa}`;
        if (filtroEquipe) url += `&equipe=${encodeURIComponent(filtroEquipe)}`;
        if (filtroCidade) url += `&cidade=${encodeURIComponent(filtroCidade)}`;
        
        const response = await axios.get(url);
        setRankingData(response.data);
      } catch (error) {
        console.error('Erro ao buscar ranking:', error);
        setRankingData([]);
      } finally {
        setLoading(false);
      }
    };

    if (tipoRanking === 'profissional') {
      fetchRanking();
    }
  }, [categoriaAtual, filtroFaixa, filtroEquipe, filtroCidade, tipoRanking]);

  // Buscar ranking da Galera
  useEffect(() => {
    const fetchRankingPovao = async () => {
      setLoadingPovao(true);
      try {
        const [rankingRes, statsRes] = await Promise.all([
          axios.get(`${API}/ranking/povao?genero=${generoPovao}`),
          axios.get(`${API}/ranking/povao/stats`)
        ]);
        setRankingPovao(rankingRes.data.ranking || []);
        setPovaoStats(statsRes.data);
      } catch (error) {
        console.error('Erro ao buscar ranking Galera:', error);
        setRankingPovao([]);
      } finally {
        setLoadingPovao(false);
      }
    };

    if (tipoRanking === 'povao') {
      fetchRankingPovao();
      fetchPovaoDestaques();
    }
  }, [tipoRanking, generoPovao]);

  // Buscar destaques da Galera (semanal, mensal, destaque do mês)
  const fetchPovaoDestaques = async () => {
    try {
      const [semanalRes, mensalRes, destaqueRes] = await Promise.all([
        axios.get(`${API}/ranking/povao/semanal?genero=${generoPovao}`),
        axios.get(`${API}/ranking/povao/mensal?genero=${generoPovao}`),
        axios.get(`${API}/ranking/povao/destaque-mes`)
      ]);
      setPovaoRankingSemanal(semanalRes.data);
      setPovaoRankingMensal(mensalRes.data);
      setPovaoDestaqueMes(destaqueRes.data);
    } catch (error) {
      console.error('Erro ao buscar destaques da Galera:', error);
    }
  };

  // Aplicar filtros locais
  const rankingFiltrado = rankingData.filter(atleta => {
    const nomeMatch = atleta.nome.toLowerCase().includes(filtroNome.toLowerCase());
    const colocacaoMatch = filtroColocacao === '' || atleta.colocacao === parseInt(filtroColocacao);
    const ufMatch = atleta.uf.toLowerCase().includes(filtroUF.toLowerCase());
    
    return nomeMatch && colocacaoMatch && ufMatch;
  });

  // Aplicar filtros locais para a Galera
  const rankingPovaoFiltrado = rankingPovao.filter(atleta => {
    const nomeMatch = atleta.nome.toLowerCase().includes(filtroNomePovao.toLowerCase());
    const colocacaoMatch = filtroColocacaoPovao === '' || atleta.colocacao === parseInt(filtroColocacaoPovao);
    const ufMatch = filtroUFPovao === '' || atleta.uf?.toUpperCase() === filtroUFPovao.toUpperCase();
    const faixaMatch = filtroFaixaPovao === '' || filtroFaixaPovao === 'all' || atleta.faixa_etaria === filtroFaixaPovao;
    const equipeMatch = filtroEquipePovao === '' || filtroEquipePovao === 'all' || atleta.equipe?.toLowerCase().includes(filtroEquipePovao.toLowerCase());
    const cidadeMatch = filtroCidadePovao === '' || atleta.cidade?.toLowerCase().includes(filtroCidadePovao.toLowerCase());
    
    return nomeMatch && colocacaoMatch && ufMatch && faixaMatch && equipeMatch && cidadeMatch;
  });

  const handleAtletaClick = (atletaId) => {
    navigate(`/atleta/${atletaId}`);
  };

  const handleExport = (format) => {
    const url = `${API}/ranking/export/${format}?categoria=${categoriaAtual}`;
    window.open(url, '_blank');
  };

  const limparFiltros = () => {
    setFiltroNome('');
    setFiltroColocacao('');
    setFiltroUF('');
    setFiltroFaixa('');
    setFiltroEquipe('');
    setFiltroCidade('');
  };

  const limparFiltrosPovao = () => {
    setFiltroNomePovao('');
    setFiltroColocacaoPovao('');
    setFiltroUFPovao('');
    setFiltroFaixaPovao('');
    setFiltroEquipePovao('');
    setFiltroCidadePovao('');
  };

  // ============ LIGA DE ASSESSORIAS - ROE-RR ============
  useEffect(() => {
    if (tipoRanking === 'equipes') {
      fetchLigaRanking();
      fetchLigaStats();
      fetchEstadosComAssessorias();
      fetchEvolucaoMensal();
    }
  }, [tipoRanking, ligaTipo, ligaEstado, ligaCidade, ligaMes]);

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
      // Adicionar filtro de mês se selecionado
      if (ligaMes) {
        url += `&mes=${ligaMes}`;
      }
      
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(url, { headers });
      setLigaRanking(response.data.ranking || []);
    } catch (error) {
      console.error('Erro ao buscar ranking liga:', error);
      setLigaRanking([]);
    } finally {
      setLoadingLiga(false);
    }
  };

  const fetchLigaStats = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/stats`, { headers });
      setLigaStats(response.data);
    } catch (error) {
      console.error('Erro ao buscar stats liga:', error);
    }
  };

  const fetchEvolucaoMensal = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/evolucao-mensal?top=5`, { headers });
      setEvolucaoMensal(response.data);
    } catch (error) {
      console.error('Erro ao buscar evolução mensal:', error);
    }
  };

  const fetchEstadosComAssessorias = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/estados`, { headers });
      setEstadosComAssessorias(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar estados:', error);
    }
  };

  const fetchCidadesComAssessorias = async (estado) => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/cidades?estado=${estado}`, { headers });
      setCidadesComAssessorias(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
    }
  };

  const fetchAssessoriaDetalhe = async (nome) => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/assessoria/${encodeURIComponent(nome)}`, { headers });
      setAssessoriaDetalhe(response.data);
      setShowAssessoriaModal(true);
    } catch (error) {
      console.error('Erro ao buscar detalhes:', error);
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
      case 'ouro': return 'bg-gradient-to-r from-yellow-500 to-amber-600 text-white';
      case 'prata': return 'bg-gradient-to-r from-slate-400 to-slate-500 text-white';
      case 'bronze': return 'bg-gradient-to-r from-amber-700 to-orange-800 text-white';
      default: return 'bg-slate-600 text-white';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header com Login/Logout e Nome do Usuário */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-emerald-600 dark:text-emerald-400 mb-2 tracking-tight">
              Ranking Run Pró
            </h1>
          </div>
          <div className="flex items-center gap-2">
            {user ? (
              <>
                {/* Nome do usuário */}
                <div className="hidden md:flex items-center gap-2 mr-4 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/30 rounded-full">
                  <User className="w-4 h-4 text-emerald-600" />
                  <span className="text-sm font-medium text-emerald-700 dark:text-emerald-300" data-testid="user-name">
                    {user.nome}
                  </span>
                </div>
                
                {/* Botão Atualizar Página */}
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => window.location.reload()} 
                  title="Atualizar página"
                  data-testid="btn-refresh"
                  className="text-slate-600 hover:text-emerald-600 hover:bg-emerald-50"
                >
                  <RefreshCw className="w-5 h-5" />
                </Button>
                
                {/* Notificações */}
                <NotificacoesBell />
                
                {isAdmin && (
                  <Button onClick={() => navigate('/admin')} variant="outline" size="sm">
                    <Shield className="w-4 h-4 mr-2" />
                    Admin
                  </Button>
                )}
                {user?.role === 'dono_assessoria' && (
                  <Button onClick={() => navigate('/minha-assessoria')} variant="outline" size="sm" className="border-amber-500 text-amber-600 hover:bg-amber-50">
                    <Award className="w-4 h-4 mr-2" />
                    Minha Assessoria
                  </Button>
                )}
                
                {/* Link para Feed */}
                <Button onClick={() => navigate('/feed')} variant="ghost" size="sm" className="text-blue-500 hover:text-blue-600" data-testid="btn-feed">
                  <MessageSquare className="w-4 h-4 mr-1" />
                  Feed
                </Button>
                
                {/* Link para Regras */}
                <Button onClick={() => navigate('/regras')} variant="ghost" size="sm" className="text-slate-500 hover:text-slate-700" data-testid="btn-regras">
                  <HelpCircle className="w-4 h-4 mr-1" />
                  Regras
                </Button>
                
                {/* Link para Histórico de Submissões */}
                <Button onClick={() => navigate('/historico')} variant="ghost" size="sm" className="text-purple-500 hover:text-purple-700" data-testid="btn-historico">
                  <History className="w-4 h-4 mr-1" />
                  Histórico
                </Button>
                
                {/* Link para Ranking por Cidade */}
                <Button onClick={() => navigate('/ranking-cidade')} variant="ghost" size="sm" className="text-emerald-500 hover:text-emerald-700" data-testid="btn-ranking-cidade">
                  <MapPin className="w-4 h-4 mr-1" />
                  Por Cidade
                </Button>
                
                {!isAdmin && (
                  <Button onClick={() => navigate('/perfil')} variant="outline" size="sm" data-testid="btn-perfil">
                    <User className="w-4 h-4 mr-2" />
                    Meu Perfil
                  </Button>
                )}
                <Button onClick={() => navigate('/submeter-resultado')} className="bg-emerald-600" size="sm">
                  <Upload className="w-4 h-4 mr-2" />
                  Submeter
                </Button>
                <Button onClick={logout} variant="outline" size="sm">
                  <LogOut className="w-4 h-4 mr-2" />
                  Sair
                </Button>
              </>
            ) : (
              <>
                {/* Link para Regras (visitantes) */}
                <Button onClick={() => navigate('/regras')} variant="ghost" size="sm" className="text-slate-500 hover:text-slate-700" data-testid="btn-regras-visitor">
                  <HelpCircle className="w-4 h-4 mr-1" />
                  Regras
                </Button>
                <Button onClick={() => navigate('/cadastro')} variant="outline">
                  Cadastrar
                </Button>
                <Button onClick={() => navigate('/login')} className="bg-emerald-600">
                  <LogIn className="w-4 h-4 mr-2" />
                  Entrar
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Seletor de Tipo de Ranking */}
        <Card className="mb-6 border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden">
          <CardContent className="p-0">
            <div className="grid grid-cols-2 md:grid-cols-4">
              {/* Opção Profissional/Amador */}
              <button 
                className={`py-4 px-4 flex items-center justify-center gap-2 transition-all ${
                  tipoRanking === 'profissional' 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('profissional')}
                data-testid="tipo-ranking-profissional"
              >
                <Trophy className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold text-sm">Ranking Profissional/Amador</p>
                  <p className={`text-xs ${tipoRanking === 'profissional' ? 'text-emerald-100' : 'text-slate-400'}`}>
                    Pontuação por colocação
                  </p>
                </div>
              </button>
              
              {/* Opção Galera */}
              <button 
                className={`py-4 px-4 flex items-center justify-center gap-2 transition-all ${
                  tipoRanking === 'povao' 
                    ? 'bg-purple-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('povao')}
                data-testid="tipo-ranking-povao"
              >
                <Users className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold text-sm">Ranking da Galera</p>
                  <p className={`text-xs ${tipoRanking === 'povao' ? 'text-purple-100' : 'text-slate-400'}`}>
                    Pace Livre - Pontuação por distância
                  </p>
                </div>
              </button>

              {/* Opção Equipes/Assessorias */}
              <button 
                className={`py-4 px-4 flex items-center justify-center gap-2 transition-all ${
                  tipoRanking === 'equipes' 
                    ? 'bg-amber-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('equipes')}
                data-testid="tipo-ranking-equipes"
              >
                <Award className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold text-sm">Ranking de Equipes</p>
                  <p className={`text-xs ${tipoRanking === 'equipes' ? 'text-amber-100' : 'text-slate-400'}`}>
                    Liga Nacional de Assessorias
                  </p>
                </div>
              </button>

              {/* Opção Ranking das Corridas */}
              <button 
                className="py-4 px-4 flex items-center justify-center gap-2 transition-all bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-yellow-50 hover:text-yellow-700 border-l border-slate-200"
                onClick={() => navigate('/ranking-corridas')}
                data-testid="tipo-ranking-corridas"
              >
                <Star className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold text-sm">Ranking das Corridas</p>
                  <p className="text-xs text-slate-400">
                    Avalie eventos de corrida
                  </p>
                </div>
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Ranking Profissional/Amador */}
        {tipoRanking === 'profissional' && (
          <>
            {/* Tabs de Categorias */}
            <Card className="mb-6 border-slate-200 dark:border-slate-800 shadow-lg">
              <CardContent className="pt-6">
                <Tabs value={categoriaAtual} onValueChange={setCategoriaAtual} className="w-full">
                  <TabsList className="grid w-full grid-cols-2 lg:grid-cols-6 h-auto gap-1">
                    <TabsTrigger value="masculino" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-masculino">
                      MASCULINO
                    </TabsTrigger>
                    <TabsTrigger value="feminino" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-feminino">
                      FEMININO
                    </TabsTrigger>
                    <TabsTrigger value="pcd-m" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-pcd-m">
                      PCD / M
                    </TabsTrigger>
                    <TabsTrigger value="pcd-f" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-pcd-f">
                      PCD / F
                    </TabsTrigger>
                    <TabsTrigger value="cadeirante-m" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-cadeirante-m">
                      CADEIRANTE / M
                    </TabsTrigger>
                    <TabsTrigger value="cadeirante-f" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-cadeirante-f">
                      CADEIRANTE / F
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </CardContent>
            </Card>

            {/* Layout: Filtros + Tabela */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Sidebar de Filtros */}
              <Card className="lg:col-span-1 h-fit border-slate-200 dark:border-slate-800 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Search className="w-5 h-5" />
                    Opções de filtro
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
              {/* Filtro Nome */}
              <div>
                <Label htmlFor="filtro-nome" className="text-sm font-medium mb-2 block">
                  Nome
                </Label>
                <Input
                  id="filtro-nome"
                  placeholder="Buscar por nome"
                  value={filtroNome}
                  onChange={(e) => setFiltroNome(e.target.value)}
                  data-testid="filtro-nome"
                />
              </div>

              {/* Filtro Colocação */}
              <div>
                <Label htmlFor="filtro-colocacao" className="text-sm font-medium mb-2 block">
                  Colocação
                </Label>
                <Input
                  id="filtro-colocacao"
                  type="number"
                  placeholder="Ex: 1"
                  value={filtroColocacao}
                  onChange={(e) => setFiltroColocacao(e.target.value)}
                  data-testid="filtro-colocacao"
                />
              </div>

              {/* Filtro UF */}
              <div>
                <Label htmlFor="filtro-uf" className="text-sm font-medium mb-2 block">
                  UF
                </Label>
                <Input
                  id="filtro-uf"
                  placeholder="Ex: SP"
                  value={filtroUF}
                  onChange={(e) => setFiltroUF(e.target.value.toUpperCase())}
                  maxLength={2}
                  data-testid="filtro-uf"
                />
              </div>

              {/* Filtro Faixa Etária */}
              <div>
                <Label htmlFor="filtro-faixa" className="text-sm font-medium mb-2 block">
                  Faixa Etária
                </Label>
                <Select value={filtroFaixa || "all"} onValueChange={(v) => setFiltroFaixa(v === "all" ? "" : v)}>
                  <SelectTrigger data-testid="filtro-faixa">
                    <SelectValue placeholder="Todas as faixas" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas as faixas</SelectItem>
                    {faixasDisponiveis.map((faixa) => (
                      <SelectItem key={faixa} value={faixa}>{faixa}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Filtro Equipe */}
              <div>
                <Label htmlFor="filtro-equipe" className="text-sm font-medium mb-2 block">
                  Equipe
                </Label>
                <Select value={filtroEquipe || "all"} onValueChange={(v) => setFiltroEquipe(v === "all" ? "" : v)}>
                  <SelectTrigger data-testid="filtro-equipe">
                    <SelectValue placeholder="Todas as equipes" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas as equipes</SelectItem>
                    {equipesDisponiveis.map((equipe) => (
                      <SelectItem key={equipe.nome} value={equipe.nome}>{equipe.nome}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Filtro Cidade */}
              <div>
                <Label htmlFor="filtro-cidade" className="text-sm font-medium mb-2 block">
                  Cidade
                </Label>
                <Input
                  id="filtro-cidade"
                  placeholder="Ex: São Paulo"
                  value={filtroCidade}
                  onChange={(e) => setFiltroCidade(e.target.value)}
                  data-testid="filtro-cidade"
                />
              </div>

              {/* Botões */}
              <div className="space-y-2 pt-2">
                <Button 
                  className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-semibold"
                  data-testid="btn-filtrar"
                >
                  Filtrar
                </Button>
                <Button 
                  variant="outline"
                  className="w-full"
                  onClick={limparFiltros}
                  data-testid="btn-limpar"
                >
                  Limpar Filtros
                </Button>
              </div>

              {/* Botão Mostrar/Ocultar Destaques */}
              <Button 
                variant="outline"
                className={`w-full ${showDestaques ? 'bg-emerald-50 border-emerald-300' : ''}`}
                onClick={() => setShowDestaques(!showDestaques)}
                data-testid="btn-toggle-destaques"
              >
                <Flame className="w-4 h-4 mr-2" />
                {showDestaques ? 'Ocultar Destaques' : 'Ver Destaques'}
              </Button>

              {/* Botão Como funciona? */}
              <Dialog>
                <DialogTrigger asChild>
                  <Button 
                    variant="outline"
                    className="w-full bg-yellow-400 hover:bg-yellow-500 text-slate-900 font-semibold border-0"
                    data-testid="btn-como-funciona"
                  >
                    <HelpCircle className="w-4 h-4 mr-2" />
                    Como funciona?
                  </Button>
                </DialogTrigger>

              {/* Botão Regulamento */}
              <RegulamentoButton 
                className="w-full bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 font-semibold border-emerald-500/30"
                variant="outline"
                size="default"
              />
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle className="text-2xl font-bold text-emerald-600">Como funciona o Ranking?</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 text-slate-700 dark:text-slate-300">
                    <div>
                      <h3 className="font-semibold text-lg mb-2">Sistema de Pontuação</h3>
                      <p>Os atletas acumulam pontos ao participar de corridas oficiais. A pontuação varia de acordo com a colocação.</p>
                      <ul className="list-disc list-inside mt-2 text-sm">
                        <li><strong>Normal:</strong> 1º lugar = 10pts, 2º = 9pts, ... até 10º = 1pt</li>
                        <li><strong>PCD/Cadeirante:</strong> 1º = 10pts, 2º = 9pts, 3º = 8pts</li>
                      </ul>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-2">Selo "P" (Pendente)</h3>
                      <p>O selo laranja "P" indica que o atleta ainda não completou o mínimo de provas:</p>
                      <ul className="list-disc list-inside mt-2 text-sm">
                        <li><strong>Normal:</strong> 12 provas</li>
                        <li><strong>PCD/Cadeirante:</strong> 8 provas</li>
                      </ul>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-2">Status Elite</h3>
                      <p>Atletas com <strong>100 pontos ou mais</strong> recebem o status Elite.</p>
                    </div>

                    <div>
                      <h3 className="font-semibold text-lg mb-2">Rankings por Período</h3>
                      <p>Além do ranking anual, temos:</p>
                      <ul className="list-disc list-inside mt-2 text-sm">
                        <li><strong>Ranking Semanal:</strong> Top 10 da última semana</li>
                        <li><strong>Ranking Mensal:</strong> Top 10 do mês atual</li>
                        <li><strong>Destaque do Mês:</strong> Atletas mais ativos e com mais pontos</li>
                      </ul>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>

          {/* Conteúdo Principal */}
          <div className="lg:col-span-3 space-y-6">
            {/* Seção de Destaques */}
            {showDestaques && (
              <RankingDestaques categoria={categoriaAtual} />
            )}

            {/* Tabela de Ranking */}
            <Card className="border-slate-200 dark:border-slate-800 shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-xl flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-emerald-500" />
                  Ranking Anual {categoriaAtual.replace('-', ' ').toUpperCase()}
                  <span className="ml-2 text-sm font-normal text-slate-600 dark:text-slate-400">
                    ({rankingFiltrado.length} atletas)
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-12 text-slate-600 dark:text-slate-400">
                    Carregando ranking...
                  </div>
                ) : (
                  <RankingTable data={rankingFiltrado} onAtletaClick={handleAtletaClick} modalidade="profissional" />
                )}
              </CardContent>
            </Card>
          </div>
        </div>
          </>
        )}

        {/* Ranking da Galera */}
        {tipoRanking === 'povao' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar de Filtros - Galera */}
            <Card className="lg:col-span-1 h-fit border-purple-200 dark:border-purple-800 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2 text-purple-700">
                  <Search className="w-5 h-5" />
                  Opções de filtro
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Filtro de Gênero */}
                <div>
                  <Label className="text-purple-700">Gênero</Label>
                  <div className="flex gap-2 mt-2">
                    <Button
                      variant={generoPovao === 'M' ? 'default' : 'outline'}
                      onClick={() => setGeneroPovao('M')}
                      className={`flex-1 ${generoPovao === 'M' ? 'bg-purple-600 hover:bg-purple-700' : ''}`}
                      size="sm"
                      data-testid="povao-masculino"
                    >
                      Masculino
                    </Button>
                    <Button
                      variant={generoPovao === 'F' ? 'default' : 'outline'}
                      onClick={() => setGeneroPovao('F')}
                      className={`flex-1 ${generoPovao === 'F' ? 'bg-purple-600 hover:bg-purple-700' : ''}`}
                      size="sm"
                      data-testid="povao-feminino"
                    >
                      Feminino
                    </Button>
                  </div>
                </div>

                {/* Nome */}
                <div>
                  <Label>Nome</Label>
                  <Input
                    placeholder="Buscar por nome"
                    value={filtroNomePovao}
                    onChange={(e) => setFiltroNomePovao(e.target.value)}
                    data-testid="filtro-nome-povao"
                  />
                </div>

                {/* Colocação */}
                <div>
                  <Label>Colocação</Label>
                  <Input
                    type="number"
                    placeholder="Ex: 1"
                    value={filtroColocacaoPovao}
                    onChange={(e) => setFiltroColocacaoPovao(e.target.value)}
                    data-testid="filtro-colocacao-povao"
                  />
                </div>

                {/* UF */}
                <div>
                  <Label>UF</Label>
                  <Input
                    placeholder="Ex: SP"
                    value={filtroUFPovao}
                    onChange={(e) => setFiltroUFPovao(e.target.value.toUpperCase())}
                    maxLength={2}
                    data-testid="filtro-uf-povao"
                  />
                </div>

                {/* Faixa Etária */}
                <div>
                  <Label>Faixa Etária</Label>
                  <Select value={filtroFaixaPovao} onValueChange={setFiltroFaixaPovao}>
                    <SelectTrigger data-testid="filtro-faixa-povao">
                      <SelectValue placeholder="Todas as faixas" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todas as faixas</SelectItem>
                      <SelectItem value="18-29">18-29</SelectItem>
                      <SelectItem value="30-39">30-39</SelectItem>
                      <SelectItem value="40-49">40-49</SelectItem>
                      <SelectItem value="50-59">50-59</SelectItem>
                      <SelectItem value="60+">60+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Equipe */}
                <div>
                  <Label>Equipe</Label>
                  <Select value={filtroEquipePovao} onValueChange={setFiltroEquipePovao}>
                    <SelectTrigger data-testid="filtro-equipe-povao">
                      <SelectValue placeholder="Todas as equipes" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todas as equipes</SelectItem>
                      {equipesDisponiveis.map(eq => (
                        <SelectItem key={eq.nome} value={eq.nome}>{eq.nome}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Cidade */}
                <div>
                  <Label>Cidade</Label>
                  <Input
                    placeholder="Ex: São Paulo"
                    value={filtroCidadePovao}
                    onChange={(e) => setFiltroCidadePovao(e.target.value)}
                    data-testid="filtro-cidade-povao"
                  />
                </div>

                {/* Botões */}
                <div className="space-y-2 pt-2">
                  <Button 
                    className="w-full bg-purple-500 hover:bg-purple-600 text-white font-semibold"
                    data-testid="btn-filtrar-povao"
                  >
                    Filtrar
                  </Button>
                  <Button 
                    variant="outline"
                    className="w-full"
                    onClick={limparFiltrosPovao}
                    data-testid="btn-limpar-povao"
                  >
                    Limpar Filtros
                  </Button>
                </div>

                {/* Separador */}
                <div className="border-t border-purple-200 pt-4 mt-4">
                  <p className="text-xs text-purple-600 font-medium mb-3">DESTAQUES & INFO</p>
                  
                  {/* Botão Mostrar/Ocultar Destaques */}
                  <Button 
                    variant="outline"
                    className={`w-full mb-2 ${showDestaquePovao ? 'bg-purple-50 border-purple-300' : ''}`}
                    onClick={() => setShowDestaquePovao(!showDestaquePovao)}
                    data-testid="btn-toggle-destaque-povao"
                  >
                    <Flame className="w-4 h-4 mr-2" />
                    {showDestaquePovao ? 'Ocultar Destaques' : 'Ver Destaques'}
                  </Button>

                  {/* Botão Como funciona? */}
                  <Button 
                    variant="outline"
                    className="w-full mb-2 bg-yellow-400 hover:bg-yellow-500 text-slate-900 font-semibold border-0"
                    onClick={() => setShowComoFuncionaPovao(true)}
                    data-testid="btn-como-funciona-povao"
                  >
                    <HelpCircle className="w-4 h-4 mr-2" />
                    Como funciona?
                  </Button>

                  {/* Botão Regulamento */}
                  <Button 
                    variant="outline"
                    className="w-full bg-purple-500/10 hover:bg-purple-500/20 text-purple-600 font-semibold border-purple-500/30"
                    onClick={() => setShowRegulamentoPovao(true)}
                    data-testid="btn-regulamento-povao"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Regulamento
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Modal Como Funciona - Galera */}
            <Dialog open={showComoFuncionaPovao} onOpenChange={setShowComoFuncionaPovao}>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle className="text-2xl font-bold text-purple-600 flex items-center gap-2">
                    <HelpCircle className="w-6 h-6" />
                    Como funciona o Ranking da Galera?
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4 text-slate-700 dark:text-slate-300">
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                    <h3 className="font-semibold text-lg mb-2 text-purple-700">O que é o Ranking da Galera?</h3>
                    <p>O Ranking da Galera é uma modalidade especial que valoriza a <strong>participação</strong> acima da colocação. Aqui, todos ganham pontos por correr, independente de onde chegaram!</p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Sistema de Pontuação</h3>
                    <p className="mb-2">A pontuação é baseada <strong>apenas na distância percorrida</strong>:</p>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="bg-purple-100 p-3 rounded-lg text-center">
                        <div className="text-2xl font-bold text-purple-700">5 pts</div>
                        <div className="text-sm text-purple-600">5km a 9km</div>
                      </div>
                      <div className="bg-purple-200 p-3 rounded-lg text-center">
                        <div className="text-2xl font-bold text-purple-800">7 pts</div>
                        <div className="text-sm text-purple-700">10km a 20km</div>
                      </div>
                      <div className="bg-purple-300 p-3 rounded-lg text-center">
                        <div className="text-2xl font-bold text-purple-900">9 pts</div>
                        <div className="text-sm text-purple-800">21km+</div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Critérios de Desempate</h3>
                    <ol className="list-decimal list-inside space-y-1 text-sm">
                      <li><strong>Pontos totais</strong> - Quem tem mais pontos</li>
                      <li><strong>Número de provas</strong> - Quem participou de mais corridas</li>
                      <li><strong>Distância acumulada</strong> - Quem correu mais km no total</li>
                    </ol>
                  </div>

                  <div>
                    <h3 className="font-semibold text-lg mb-2">Rankings por Período</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      <li><strong>Ranking Semanal:</strong> Top 10 da última semana</li>
                      <li><strong>Ranking Mensal:</strong> Top 10 do mês atual</li>
                      <li><strong>Destaque do Mês:</strong> Atletas mais ativos e com mais pontos</li>
                    </ul>
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={() => setShowComoFuncionaPovao(false)} className="bg-purple-600 hover:bg-purple-700">
                    Entendi!
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Modal Regulamento - Galera */}
            <Dialog open={showRegulamentoPovao} onOpenChange={setShowRegulamentoPovao}>
              <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-2xl font-bold text-purple-600 flex items-center gap-2">
                    <FileText className="w-6 h-6" />
                    Regulamento do Ranking da Galera
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4 text-slate-700 dark:text-slate-300 text-sm">
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                    <h3 className="font-semibold text-base mb-2">1. Objetivo</h3>
                    <p>O Ranking da Galera tem como objetivo incentivar a prática da corrida de rua, valorizando a participação e a constância dos atletas amadores.</p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">2. Elegibilidade</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Qualquer pessoa cadastrada na plataforma pode participar</li>
                      <li>Não há restrição de idade ou nível de experiência</li>
                      <li>É necessário submeter resultados de corridas oficiais</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">3. Pontuação</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li>5km a 9km: <strong>5 pontos</strong></li>
                      <li>10km a 20km: <strong>7 pontos</strong></li>
                      <li>21km ou mais: <strong>9 pontos</strong></li>
                    </ul>
                    <p className="mt-2 text-xs text-slate-500">* A colocação na prova não influencia a pontuação</p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">4. Submissão de Resultados</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Os resultados devem ser submetidos em até 30 dias após a prova</li>
                      <li>É obrigatório anexar comprovante (foto do certificado ou print do resultado)</li>
                      <li>Resultados são verificados pela equipe antes da aprovação</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">5. Desclassificação</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Submissão de resultados falsos ou adulterados</li>
                      <li>Múltiplas submissões da mesma prova</li>
                      <li>Comportamento antidesportivo</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">6. Premiação</h3>
                    <p>Os destaques mensais e anuais recebem reconhecimento na plataforma. Premiações físicas podem ser oferecidas em parcerias com eventos e patrocinadores.</p>
                  </div>
                  
                  <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg">
                    <h3 className="font-semibold text-base mb-2">7. Disposições Gerais</h3>
                    <p>A organização reserva-se o direito de alterar este regulamento a qualquer momento, mediante aviso prévio aos participantes.</p>
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={() => setShowRegulamentoPovao(false)} className="bg-purple-600 hover:bg-purple-700">
                    Fechar
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Conteúdo Principal - Galera */}
            <div className="lg:col-span-3 space-y-6">
              {/* Stats da Galera */}
              {povaoStats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30 border-0 shadow-lg">
                    <CardContent className="pt-6 text-center">
                      <Users className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                      <div className="text-3xl font-bold text-purple-700">{povaoStats.total_atletas || 0}</div>
                      <div className="text-sm text-purple-600">Atletas Galera</div>
                    </CardContent>
                  </Card>
                  <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 border-0 shadow-lg">
                    <CardContent className="pt-6 text-center">
                      <Target className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                      <div className="text-3xl font-bold text-blue-700">{povaoStats.total_atletas_masculino || 0}</div>
                      <div className="text-sm text-blue-600">Masculino</div>
                    </CardContent>
                  </Card>
                  <Card className="bg-gradient-to-br from-pink-50 to-pink-100 dark:from-pink-900/30 dark:to-pink-800/30 border-0 shadow-lg">
                    <CardContent className="pt-6 text-center">
                      <Target className="w-8 h-8 mx-auto mb-2 text-pink-600" />
                      <div className="text-3xl font-bold text-pink-700">{povaoStats.total_atletas_feminino || 0}</div>
                      <div className="text-sm text-pink-600">Feminino</div>
                    </CardContent>
                  </Card>
                  <Card className="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/30 dark:to-amber-800/30 border-0 shadow-lg">
                    <CardContent className="pt-6 text-center">
                      <Trophy className="w-8 h-8 mx-auto mb-2 text-amber-600" />
                      <div className="text-3xl font-bold text-amber-700">{povaoStats.total_provas || 0}</div>
                      <div className="text-sm text-amber-600">Provas Registradas</div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Seção de Destaques da Galera */}
              {showDestaquePovao && (
                <div className="space-y-4">
                  {/* Seletor de Período */}
                  <Card className="border-purple-200 dark:border-purple-800">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between flex-wrap gap-4">
                        <div className="flex items-center gap-2">
                          <Flame className="w-5 h-5 text-purple-600" />
                          <span className="font-semibold text-purple-700">Destaques da Galera</span>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant={periodoRankingPovao === 'semanal' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setPeriodoRankingPovao('semanal')}
                            className={periodoRankingPovao === 'semanal' ? 'bg-purple-600 hover:bg-purple-700' : ''}
                            data-testid="btn-periodo-semanal"
                          >
                            Semanal
                          </Button>
                          <Button
                            variant={periodoRankingPovao === 'mensal' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setPeriodoRankingPovao('mensal')}
                            className={periodoRankingPovao === 'mensal' ? 'bg-purple-600 hover:bg-purple-700' : ''}
                            data-testid="btn-periodo-mensal"
                          >
                            Mensal
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Grid de Destaques */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* Ranking Semanal ou Mensal */}
                    <Card className="border-purple-200 dark:border-purple-800 shadow-lg">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-lg flex items-center gap-2 text-purple-700">
                          <Trophy className="w-5 h-5" />
                          Top 10 - {periodoRankingPovao === 'semanal' ? 'Semanal' : 'Mensal'}
                        </CardTitle>
                        <p className="text-xs text-slate-500">
                          {periodoRankingPovao === 'semanal' 
                            ? povaoRankingSemanal?.periodo 
                            : povaoRankingMensal?.periodo}
                        </p>
                      </CardHeader>
                      <CardContent>
                        {(periodoRankingPovao === 'semanal' ? povaoRankingSemanal?.ranking : povaoRankingMensal?.ranking)?.length > 0 ? (
                          <div className="space-y-2">
                            {(periodoRankingPovao === 'semanal' ? povaoRankingSemanal.ranking : povaoRankingMensal.ranking).slice(0, 10).map((atleta, idx) => (
                              <div 
                                key={atleta.atleta_id} 
                                className="flex items-center gap-3 p-2 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 cursor-pointer transition-colors"
                                onClick={() => handleAtletaClick(atleta.atleta_id)}
                              >
                                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold ${
                                  idx === 0 ? 'bg-yellow-500 text-white' :
                                  idx === 1 ? 'bg-slate-400 text-white' :
                                  idx === 2 ? 'bg-amber-600 text-white' :
                                  'bg-slate-200 text-slate-700'
                                }`}>
                                  {idx + 1}
                                </div>
                                <Avatar className="h-8 w-8">
                                  <AvatarImage src={atleta.foto_url?.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                                  <AvatarFallback className="bg-purple-500 text-white text-xs">
                                    {atleta.nome?.charAt(0)}
                                  </AvatarFallback>
                                </Avatar>
                                <div className="flex-1 min-w-0">
                                  <p className="font-medium text-sm truncate">{atleta.nome}</p>
                                  <p className="text-xs text-slate-500">{atleta.total_corridas} provas</p>
                                </div>
                                <Badge className="bg-purple-100 text-purple-700 border-0">
                                  {atleta.pontos} pts
                                </Badge>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-8 text-slate-500">
                            <Users className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                            <p className="text-sm">Nenhum resultado encontrado para este período</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Destaque do Mês */}
                    <Card className="border-purple-200 dark:border-purple-800 shadow-lg bg-gradient-to-br from-purple-50 to-white dark:from-purple-900/20 dark:to-slate-900">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-lg flex items-center gap-2 text-purple-700">
                          <Star className="w-5 h-5" />
                          Destaque do Mês
                        </CardTitle>
                        <p className="text-xs text-slate-500">{povaoDestaqueMes?.mes}</p>
                      </CardHeader>
                      <CardContent>
                        {povaoDestaqueMes ? (
                          <div className="space-y-4">
                            {/* Stats do mês */}
                            <div className="grid grid-cols-2 gap-2">
                              <div className="bg-white dark:bg-slate-800 p-3 rounded-lg text-center shadow-sm">
                                <div className="text-2xl font-bold text-purple-600">{povaoDestaqueMes.total_corridas || 0}</div>
                                <div className="text-xs text-slate-500">Corridas no mês</div>
                              </div>
                              <div className="bg-white dark:bg-slate-800 p-3 rounded-lg text-center shadow-sm">
                                <div className="text-2xl font-bold text-purple-600">{povaoDestaqueMes.atletas_participantes || 0}</div>
                                <div className="text-xs text-slate-500">Atletas ativos</div>
                              </div>
                            </div>

                            {/* Mais Ativo */}
                            {povaoDestaqueMes.mais_ativo && (
                              <div 
                                className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm cursor-pointer hover:shadow-md transition-shadow"
                                onClick={() => handleAtletaClick(povaoDestaqueMes.mais_ativo.atleta_id)}
                              >
                                <div className="flex items-center gap-2 mb-2">
                                  <Flame className="w-4 h-4 text-orange-500" />
                                  <span className="text-xs font-semibold text-orange-600">MAIS ATIVO</span>
                                </div>
                                <div className="flex items-center gap-3">
                                  <Avatar className="h-12 w-12 ring-2 ring-orange-500">
                                    <AvatarImage src={povaoDestaqueMes.mais_ativo.foto_url?.startsWith('http') ? povaoDestaqueMes.mais_ativo.foto_url : `${BACKEND_URL}${povaoDestaqueMes.mais_ativo.foto_url}`} />
                                    <AvatarFallback className="bg-orange-500 text-white">
                                      {povaoDestaqueMes.mais_ativo.nome?.charAt(0)}
                                    </AvatarFallback>
                                  </Avatar>
                                  <div>
                                    <p className="font-semibold">{povaoDestaqueMes.mais_ativo.nome}</p>
                                    <p className="text-sm text-slate-500">{povaoDestaqueMes.mais_ativo.total_corridas} corridas</p>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Mais Pontos */}
                            {povaoDestaqueMes.mais_pontos && (
                              <div 
                                className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm cursor-pointer hover:shadow-md transition-shadow"
                                onClick={() => handleAtletaClick(povaoDestaqueMes.mais_pontos.atleta_id)}
                              >
                                <div className="flex items-center gap-2 mb-2">
                                  <Trophy className="w-4 h-4 text-amber-500" />
                                  <span className="text-xs font-semibold text-amber-600">MAIS PONTOS</span>
                                </div>
                                <div className="flex items-center gap-3">
                                  <Avatar className="h-12 w-12 ring-2 ring-amber-500">
                                    <AvatarImage src={povaoDestaqueMes.mais_pontos.foto_url?.startsWith('http') ? povaoDestaqueMes.mais_pontos.foto_url : `${BACKEND_URL}${povaoDestaqueMes.mais_pontos.foto_url}`} />
                                    <AvatarFallback className="bg-amber-500 text-white">
                                      {povaoDestaqueMes.mais_pontos.nome?.charAt(0)}
                                    </AvatarFallback>
                                  </Avatar>
                                  <div>
                                    <p className="font-semibold">{povaoDestaqueMes.mais_pontos.nome}</p>
                                    <p className="text-sm text-slate-500">{povaoDestaqueMes.mais_pontos.total_pontos} pontos</p>
                                  </div>
                                </div>
                              </div>
                            )}

                            {!povaoDestaqueMes.mais_ativo && !povaoDestaqueMes.mais_pontos && (
                              <div className="text-center py-4 text-slate-500">
                                <p className="text-sm">Ainda não há destaques para este mês</p>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-center py-8 text-slate-500">
                            <Star className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                            <p className="text-sm">Carregando destaques...</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}

              {/* Info sobre o sistema de pontuação */}
              <Card className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
                <CardContent className="pt-4">
                  <div className="flex items-start gap-3">
                    <HelpCircle className="w-5 h-5 text-purple-600 mt-0.5" />
                    <div className="text-sm text-purple-800 dark:text-purple-200">
                      <p className="font-semibold mb-1">Sistema de Pontuação da Galera</p>
                      <p>A pontuação é baseada apenas na distância percorrida, não importa a colocação:</p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        <Badge className="bg-purple-200 text-purple-800 border-0">5km a 9km = 5 pontos</Badge>
                        <Badge className="bg-purple-300 text-purple-800 border-0">10km a 20km = 7 pontos</Badge>
                        <Badge className="bg-purple-400 text-purple-900 border-0">21km ou mais = 9 pontos</Badge>
                      </div>
                      <p className="mt-2 text-xs text-purple-600">Critérios de desempate: 1º Pontos, 2º Número de Provas, 3º Distância Acumulada</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Tabela do Ranking Galera */}
              <Card className="border-purple-200 dark:border-purple-800 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl flex items-center gap-2">
                    <Users className="w-5 h-5 text-purple-500" />
                    Ranking da Galera - {generoPovao === 'M' ? 'Masculino' : 'Feminino'}
                    <span className="ml-2 text-sm font-normal text-slate-600 dark:text-slate-400">
                      ({rankingPovaoFiltrado.length} atletas)
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                {loadingPovao ? (
                  <div className="text-center py-12 text-slate-600 dark:text-slate-400">
                    Carregando ranking da Galera...
                  </div>
                ) : rankingPovaoFiltrado.length === 0 ? (
                  <div className="text-center py-12 text-slate-500">
                    <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                    <p>Nenhum atleta encontrado com os filtros aplicados.</p>
                    <p className="text-sm mt-2">Tente limpar os filtros ou buscar por outros critérios.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-purple-50 dark:bg-purple-900/30">
                        <tr className="text-left">
                          <th className="px-4 py-3 font-semibold text-purple-800 dark:text-purple-200">#</th>
                          <th className="px-4 py-3 font-semibold text-purple-800 dark:text-purple-200">Atleta</th>
                          <th className="px-4 py-3 font-semibold text-purple-800 dark:text-purple-200">Cidade/UF</th>
                          <th className="px-4 py-3 font-semibold text-purple-800 dark:text-purple-200 text-center">Provas</th>
                          <th className="px-4 py-3 font-semibold text-purple-800 dark:text-purple-200 text-center">Distância (km)</th>
                          <th className="px-4 py-3 font-semibold text-purple-800 dark:text-purple-200 text-center">Pontos</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rankingPovaoFiltrado.map((atleta, index) => (
                          <tr 
                            key={atleta.atleta_id} 
                            className="border-b border-purple-100 dark:border-purple-800 hover:bg-purple-50 dark:hover:bg-purple-900/20 cursor-pointer transition-colors"
                            onClick={() => handleAtletaClick(atleta.atleta_id)}
                          >
                            <td className="px-4 py-3">
                              {atleta.colocacao <= 3 ? (
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                                  atleta.colocacao === 1 ? 'bg-yellow-500' :
                                  atleta.colocacao === 2 ? 'bg-slate-400' :
                                  'bg-amber-600'
                                }`}>
                                  {atleta.colocacao}
                                </div>
                              ) : (
                                <span className="font-semibold text-slate-600">{atleta.colocacao}º</span>
                              )}
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-3">
                                <Avatar className="h-10 w-10 ring-2 ring-purple-500 ring-offset-2 ring-offset-white dark:ring-offset-slate-900">
                                  <AvatarImage src={atleta.foto_url?.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                                  <AvatarFallback 
                                    className="text-white font-semibold"
                                    style={{ backgroundColor: '#8B5CF6' }}
                                  >
                                    {atleta.nome?.charAt(0)}
                                  </AvatarFallback>
                                </Avatar>
                                <div>
                                  <p className="font-semibold text-slate-800 dark:text-slate-200">{atleta.nome}</p>
                                  <p className="text-sm text-slate-500">{atleta.equipe || 'Sem equipe'}</p>
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-1 text-sm text-slate-600 dark:text-slate-400">
                                <MapPin className="w-4 h-4" />
                                {atleta.cidade}/{atleta.uf}
                              </div>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <Badge variant="outline" className="border-purple-300 text-purple-700">
                                {atleta.total_corridas} provas
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className="font-semibold text-purple-600">{atleta.distancia_acumulada?.toFixed(1) || 0}</span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/50">
                                <span className="font-bold text-lg text-purple-700 dark:text-purple-300">{atleta.pontos}</span>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
            </div>
          </div>
        )}

        {/* RANKING DE EQUIPES - LIGA NACIONAL DE ASSESSORIAS */}
        {tipoRanking === 'equipes' && (
          <div className="space-y-6">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-500 to-yellow-500 text-white rounded-full text-sm font-medium mb-4">
                <Trophy className="w-4 h-4" />
                Classificação Oficial ROE-RR
              </div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-amber-600 to-yellow-600 bg-clip-text text-transparent">
                Liga Nacional de Assessorias Ranking Run
              </h2>
              <p className="text-slate-500 mt-2 max-w-2xl mx-auto">
                Sistema técnico de pontuação que avalia assessorias esportivas de corrida de rua no Brasil
              </p>
            </div>

            {/* Stats Cards */}
            {ligaStats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <Card className="bg-gradient-to-br from-amber-500 to-yellow-600 text-white">
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-amber-100 text-xs md:text-sm">Total Assessorias</p>
                        <p className="text-2xl md:text-3xl font-bold">{ligaStats.total_assessorias}</p>
                      </div>
                      <Award className="w-8 h-8 md:w-10 md:h-10 text-amber-200" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-emerald-500 to-green-600 text-white">
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-emerald-100 text-xs md:text-sm">Atletas Vinculados</p>
                        <p className="text-2xl md:text-3xl font-bold">{ligaStats.total_atletas_vinculados}</p>
                      </div>
                      <Users className="w-8 h-8 md:w-10 md:h-10 text-emerald-200" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-blue-100 text-xs md:text-sm">Resultados Aprovados</p>
                        <p className="text-2xl md:text-3xl font-bold">{ligaStats.total_resultados_aprovados}</p>
                      </div>
                      <CheckCircle className="w-8 h-8 md:w-10 md:h-10 text-blue-200" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-purple-500 to-pink-600 text-white">
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-purple-100 text-xs md:text-sm">Estados Ativos</p>
                        <p className="text-2xl md:text-3xl font-bold">{ligaStats.distribuicao_estados?.length || 0}</p>
                      </div>
                      <MapPin className="w-8 h-8 md:w-10 md:h-10 text-purple-200" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Sistema de Pontuação Info */}
            <Card className="bg-slate-50 dark:bg-slate-800/50 border-dashed">
              <CardContent className="p-4">
                <div className="flex flex-wrap items-center justify-center gap-2 md:gap-4 text-xs md:text-sm">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">Sistema de Pontuação:</span>
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
                {/* Botões Como funciona e Regulamento */}
                <div className="flex justify-center gap-3 mt-4">
                  <Button 
                    variant="outline"
                    className="bg-yellow-400 hover:bg-yellow-500 text-slate-900 font-semibold border-0"
                    onClick={() => setShowComoFuncionaEquipes(true)}
                    data-testid="btn-como-funciona-equipes"
                  >
                    <HelpCircle className="w-4 h-4 mr-2" />
                    Como funciona?
                  </Button>
                  <Button 
                    variant="outline"
                    className="bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 font-semibold border-amber-500/30"
                    onClick={() => setShowRegulamentoEquipes(true)}
                    data-testid="btn-regulamento-equipes"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Regulamento
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Modal Como Funciona - Equipes */}
            <Dialog open={showComoFuncionaEquipes} onOpenChange={setShowComoFuncionaEquipes}>
              <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-2xl font-bold text-amber-600 flex items-center gap-2">
                    <HelpCircle className="w-6 h-6" />
                    Como funciona a Liga Nacional de Assessorias?
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4 text-slate-700 dark:text-slate-300">
                  <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg">
                    <h3 className="font-semibold text-lg mb-2 text-amber-700">O que é a Liga?</h3>
                    <p>A Liga Nacional de Assessorias é o sistema oficial de <strong>classificação de equipes</strong> do Ranking Run. Ela avalia assessorias esportivas de corrida de rua em todo o Brasil com base em critérios técnicos e desempenho dos atletas vinculados.</p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Sistema de Pontuação</h3>
                    <p className="mb-3">A pontuação de cada assessoria é calculada com base em múltiplos fatores:</p>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-emerald-100 dark:bg-emerald-900/30 p-3 rounded-lg text-center">
                        <div className="text-2xl font-bold text-emerald-700">+0,5</div>
                        <div className="text-sm text-emerald-600">Por atleta vinculado</div>
                      </div>
                      <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg text-center">
                        <div className="text-2xl font-bold text-blue-700">+1,0</div>
                        <div className="text-sm text-blue-600">Por resultado aprovado</div>
                      </div>
                      <div className="bg-amber-100 dark:bg-amber-900/30 p-3 rounded-lg text-center">
                        <div className="text-2xl font-bold text-amber-700">+0,5</div>
                        <div className="text-sm text-amber-600">2º ao 5º lugar</div>
                      </div>
                      <div className="bg-yellow-100 dark:bg-yellow-900/30 p-3 rounded-lg text-center">
                        <div className="text-2xl font-bold text-yellow-700">+1,0</div>
                        <div className="text-sm text-yellow-600">1º lugar (vitória)</div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Fórmula de Cálculo</h3>
                    <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-lg font-mono text-sm">
                      <p><strong>Pontuação Total</strong> = (Atletas × 0,5) + (Resultados × 1,0) + Bônus de Pódio</p>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-lg mb-2">Níveis de Classificação</h3>
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                        <strong>Nacional:</strong> Ranking geral de todas as assessorias do Brasil
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                        <strong>Estadual:</strong> Ranking por estado (UF)
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-green-500"></span>
                        <strong>Cidade:</strong> Ranking por município
                      </li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="font-semibold text-lg mb-2">Como Subir no Ranking?</h3>
                    <ol className="list-decimal list-inside space-y-1 text-sm">
                      <li>Vincule mais atletas à sua assessoria</li>
                      <li>Incentive seus atletas a participarem de corridas</li>
                      <li>Submeta os resultados das provas para aprovação</li>
                      <li>Busque pódios para ganhar bônus extras</li>
                    </ol>
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={() => setShowComoFuncionaEquipes(false)} className="bg-amber-600 hover:bg-amber-700">
                    Entendi!
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Modal Regulamento - Equipes */}
            <Dialog open={showRegulamentoEquipes} onOpenChange={setShowRegulamentoEquipes}>
              <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-2xl font-bold text-amber-600 flex items-center gap-2">
                    <FileText className="w-6 h-6" />
                    Regulamento da Liga Nacional de Assessorias
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4 text-slate-700 dark:text-slate-300 text-sm">
                  <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg">
                    <h3 className="font-semibold text-base mb-2">1. Objetivo</h3>
                    <p>A Liga Nacional de Assessorias Ranking Run tem como objetivo reconhecer e classificar as melhores assessorias esportivas de corrida de rua do Brasil, incentivando o profissionalismo e o desenvolvimento do esporte.</p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">2. Elegibilidade</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Assessorias devem estar cadastradas na plataforma Ranking Run</li>
                      <li>É necessário ter pelo menos 1 atleta vinculado</li>
                      <li>A assessoria deve ter um responsável (dono) definido</li>
                      <li>Atletas só podem estar vinculados a uma assessoria por vez</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">3. Sistema de Pontuação</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li><strong>Atleta vinculado:</strong> +0,5 pontos por atleta ativo</li>
                      <li><strong>Resultado aprovado:</strong> +1,0 ponto por resultado de prova</li>
                      <li><strong>Pódio (2º ao 5º lugar):</strong> +0,5 pontos adicionais</li>
                      <li><strong>Vitória (1º lugar):</strong> +1,0 ponto adicional</li>
                    </ul>
                    <p className="mt-2 text-xs text-slate-500">* Apenas resultados aprovados pela administração são contabilizados</p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">4. Critérios de Desempate</h3>
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Maior número de vitórias (1º lugar)</li>
                      <li>Maior número de pódios totais</li>
                      <li>Maior número de resultados aprovados</li>
                      <li>Maior número de atletas vinculados</li>
                      <li>Data de cadastro mais antiga</li>
                    </ol>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">5. Vinculação de Atletas</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li>O atleta solicita vinculação através da plataforma</li>
                      <li>O dono da assessoria aprova ou rejeita a solicitação</li>
                      <li>Atletas podem solicitar desvinculação a qualquer momento</li>
                      <li>Resultados anteriores permanecem contabilizados para a assessoria</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">6. Verificação de Assessorias</h3>
                    <p className="mb-2">Assessorias podem receber o selo de verificação ao cumprir os critérios:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Mínimo de 10 atletas vinculados</li>
                      <li>Mínimo de 5 resultados aprovados</li>
                      <li>Dono da assessoria definido</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-base mb-2">7. Penalidades</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Submissão de resultados falsos: exclusão permanente</li>
                      <li>Comportamento antidesportivo: advertência ou suspensão</li>
                      <li>Uso de atletas fictícios: desconto de pontos e suspensão</li>
                    </ul>
                  </div>
                  
                  <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg">
                    <h3 className="font-semibold text-base mb-2">8. Disposições Gerais</h3>
                    <p>A organização reserva-se o direito de alterar este regulamento a qualquer momento, mediante comunicação prévia às assessorias participantes. Casos omissos serão analisados pela administração.</p>
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={() => setShowRegulamentoEquipes(false)} className="bg-amber-600 hover:bg-amber-700">
                    Fechar
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Tabs de Período - Nacional / Estadual / Cidade / Histórico */}
            <Card className="overflow-hidden">
              <CardContent className="p-0">
                <div className="grid grid-cols-4">
                  <button 
                    className={`py-3 px-4 flex items-center justify-center gap-2 transition-all border-b-2 ${
                      ligaTipo === 'nacional' 
                        ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-500 text-amber-700 dark:text-amber-300' 
                        : 'bg-white dark:bg-slate-800 border-transparent text-slate-600 hover:bg-slate-50'
                    }`}
                    onClick={() => { setLigaTipo('nacional'); setLigaEstado(''); setLigaCidade(''); setLigaMes(''); }}
                  >
                    <span className="text-lg">🌍</span>
                    <span className="font-semibold text-sm">Nacional</span>
                  </button>
                  <button 
                    className={`py-3 px-4 flex items-center justify-center gap-2 transition-all border-b-2 ${
                      ligaTipo === 'estadual' 
                        ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-500 text-amber-700 dark:text-amber-300' 
                        : 'bg-white dark:bg-slate-800 border-transparent text-slate-600 hover:bg-slate-50'
                    }`}
                    onClick={() => { setLigaTipo('estadual'); setLigaCidade(''); setLigaMes(''); }}
                  >
                    <span className="text-lg">🗺️</span>
                    <span className="font-semibold text-sm">Estadual</span>
                  </button>
                  <button 
                    className={`py-3 px-4 flex items-center justify-center gap-2 transition-all border-b-2 ${
                      ligaTipo === 'cidade' 
                        ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-500 text-amber-700 dark:text-amber-300' 
                        : 'bg-white dark:bg-slate-800 border-transparent text-slate-600 hover:bg-slate-50'
                    }`}
                    onClick={() => { setLigaTipo('cidade'); setLigaMes(''); }}
                  >
                    <span className="text-lg">🏙️</span>
                    <span className="font-semibold text-sm">Cidade</span>
                  </button>
                  <button 
                    className={`py-3 px-4 flex items-center justify-center gap-2 transition-all border-b-2 ${
                      ligaTipo === 'historico' 
                        ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-500 text-amber-700 dark:text-amber-300' 
                        : 'bg-white dark:bg-slate-800 border-transparent text-slate-600 hover:bg-slate-50'
                    }`}
                    onClick={() => { setLigaTipo('historico'); setLigaEstado(''); setLigaCidade(''); setLigaMes(''); }}
                  >
                    <span className="text-lg">📊</span>
                    <span className="font-semibold text-sm">Histórico</span>
                  </button>
                </div>
              </CardContent>
            </Card>

            {/* Filtros */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Label className="text-sm font-medium">Tipo de Ranking:</Label>
                    <Select value={ligaTipo} onValueChange={(v) => {
                      setLigaTipo(v);
                      setLigaEstado('');
                      setLigaCidade('');
                      if (v !== 'nacional' && v !== 'estadual' && v !== 'cidade' && v !== 'historico') {
                        setLigaMes('');
                      }
                    }}>
                      <SelectTrigger className="w-36 md:w-40">
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

                  {/* Filtro de Mês - Mostra apenas meses passados ou atual (não exibe no histórico) */}
                  {ligaTipo !== 'historico' && (
                    <div className="flex items-center gap-2">
                      <Label className="text-sm">📅 Mês:</Label>
                      <Select value={ligaMes || "todos"} onValueChange={(v) => setLigaMes(v === "todos" ? "" : v)}>
                        <SelectTrigger className="w-32 md:w-36">
                          <SelectValue placeholder="Todos" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="todos">Todos os meses</SelectItem>
                          {getMesesDisponiveis().map(mes => (
                            <SelectItem key={mes.value} value={mes.value}>
                              {mes.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  {ligaTipo === 'estadual' && (
                    <div className="flex items-center gap-2">
                      <Label className="text-sm">Estado:</Label>
                      <Select value={ligaEstado} onValueChange={(v) => {
                        setLigaEstado(v);
                        fetchCidadesComAssessorias(v);
                      }}>
                        <SelectTrigger className="w-28 md:w-32">
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
                          fetchCidadesComAssessorias(v);
                        }}>
                          <SelectTrigger className="w-24 md:w-32">
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
                            <SelectTrigger className="w-32 md:w-40">
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

                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={fetchLigaRanking}
                    disabled={loadingLiga}
                  >
                    <RefreshCw className={`w-4 h-4 mr-2 ${loadingLiga ? 'animate-spin' : ''}`} />
                    Atualizar
                  </Button>

                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setShowEvolucaoChart(!showEvolucaoChart)}
                    className="ml-auto"
                  >
                    <TrendingUp className="w-4 h-4 mr-2" />
                    {showEvolucaoChart ? 'Ocultar' : 'Ver'} Evolução
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Gráfico de Evolução Mensal das Equipes */}
            {showEvolucaoChart && evolucaoMensal && evolucaoMensal.evolucao && evolucaoMensal.evolucao.length > 0 && (
              <Card className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-slate-800 dark:to-slate-900">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <TrendingUp className="w-5 h-5 text-amber-600" />
                    📈 Evolução Mensal - Top 5 Equipes ({evolucaoMensal.ano})
                  </CardTitle>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    Acompanhe o crescimento das melhores assessorias ao longo do ano
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={evolucaoMensal.evolucao} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis 
                          dataKey="mes" 
                          tick={{ fontSize: 12, fill: '#6b7280' }}
                          tickLine={{ stroke: '#d1d5db' }}
                        />
                        <YAxis 
                          tick={{ fontSize: 12, fill: '#6b7280' }}
                          tickLine={{ stroke: '#d1d5db' }}
                          label={{ value: 'Pontos', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#6b7280' } }}
                        />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                            borderRadius: '8px',
                            border: '1px solid #e5e7eb',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                          }}
                          formatter={(value, name) => {
                            const equipe = evolucaoMensal.equipes.find(e => e.key === name);
                            return [value + ' pts', equipe?.nome || name];
                          }}
                        />
                        <Legend 
                          wrapperStyle={{ paddingTop: '20px' }}
                          formatter={(value) => {
                            const equipe = evolucaoMensal.equipes.find(e => e.key === value);
                            return equipe?.nome || value;
                          }}
                        />
                        {evolucaoMensal.equipes.map((equipe, index) => (
                          <Line 
                            key={equipe.key}
                            type="monotone" 
                            dataKey={equipe.key} 
                            stroke={['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'][index % 5]}
                            strokeWidth={2}
                            dot={{ r: 4, strokeWidth: 2, fill: 'white' }}
                            activeDot={{ r: 6, strokeWidth: 2 }}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2 justify-center">
                    {evolucaoMensal.equipes.map((equipe, index) => (
                      <Badge 
                        key={equipe.key} 
                        variant="outline" 
                        className="flex items-center gap-1"
                        style={{ borderColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'][index % 5] }}
                      >
                        <span 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'][index % 5] }}
                        />
                        {equipe.nome}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Tabela de Ranking */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-amber-500" />
                  🏆 Ranking das Assessorias
                  <Badge variant="secondary" className="ml-2">
                    {ligaRanking.length} assessorias
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingLiga ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
                  </div>
                ) : ligaRanking.length === 0 ? (
                  <div className="text-center py-12 text-slate-500">
                    <Award className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p>Nenhuma assessoria encontrada</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-slate-700 bg-amber-50 dark:bg-amber-900/20">
                          <th className="text-left py-3 px-2 md:px-4 font-semibold text-amber-800 dark:text-amber-200">Pos</th>
                          <th className="text-left py-3 px-2 md:px-4 font-semibold text-amber-800 dark:text-amber-200">UF</th>
                          <th className="text-left py-3 px-2 md:px-4 font-semibold text-amber-800 dark:text-amber-200">Assessoria</th>
                          <th className="text-left py-3 px-2 md:px-4 font-semibold text-amber-800 dark:text-amber-200 hidden md:table-cell">Cidade</th>
                          <th className="text-center py-3 px-2 md:px-4 font-semibold text-amber-800 dark:text-amber-200">Atletas</th>
                          <th className="text-right py-3 px-2 md:px-4 font-semibold text-amber-800 dark:text-amber-200">Pontos</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ligaRanking.map((equipe, idx) => (
                          <tr 
                            key={equipe.nome} 
                            className={`border-b border-slate-100 dark:border-slate-800 hover:bg-amber-50 dark:hover:bg-amber-900/10 transition-colors cursor-pointer ${
                              idx < 3 ? 'bg-amber-50/50 dark:bg-amber-900/10' : ''
                            }`}
                            onClick={() => navigate(`/assessoria/${encodeURIComponent(equipe.nome)}`)}
                          >
                            <td className="py-3 px-2 md:px-4">
                              <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                                idx === 0 ? 'bg-yellow-400 text-yellow-900' :
                                idx === 1 ? 'bg-slate-300 text-slate-700' :
                                idx === 2 ? 'bg-amber-600 text-white' :
                                'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                              }`}>
                                {equipe.posicao}
                              </span>
                            </td>
                            <td className="py-3 px-2 md:px-4">
                              <Badge variant="outline">{equipe.estado}</Badge>
                            </td>
                            <td className="py-3 px-2 md:px-4">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">{getSeloIcon(equipe.selo)}</span>
                                <span className="font-medium text-amber-700 dark:text-amber-300 hover:underline">
                                  {equipe.nome}
                                </span>
                                {equipe.verificada && (
                                  <BadgeCheck className="w-5 h-5 text-blue-500" title="Assessoria Verificada" />
                                )}
                              </div>
                            </td>
                            <td className="py-3 px-2 md:px-4 text-slate-600 dark:text-slate-400 hidden md:table-cell">
                              {equipe.cidade}
                            </td>
                            <td className="py-3 px-2 md:px-4 text-center">
                              <span className="font-semibold text-emerald-600">{equipe.total_atletas}</span>
                            </td>
                            <td className="py-3 px-2 md:px-4 text-right">
                              <span className="text-xl font-bold text-amber-600">{equipe.pontos_total}</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Modal Detalhes da Assessoria */}
        <Dialog open={showAssessoriaModal} onOpenChange={setShowAssessoriaModal}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <Award className="w-6 h-6 text-amber-500" />
                {assessoriaDetalhe?.nome}
                {assessoriaDetalhe?.verificada && (
                  <Badge className="bg-blue-500 text-white flex items-center gap-1">
                    <BadgeCheck className="w-4 h-4" />
                    Verificada
                  </Badge>
                )}
                {assessoriaDetalhe?.selo && (
                  <Badge className={getSeloColor(assessoriaDetalhe.selo)}>
                    {getSeloIcon(assessoriaDetalhe.selo)} SELO {assessoriaDetalhe.selo.toUpperCase()}
                  </Badge>
                )}
              </DialogTitle>
            </DialogHeader>

            {assessoriaDetalhe && (
              <div className="space-y-6">
                {/* Info Principal */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-amber-50 dark:bg-amber-900/20">
                    <CardContent className="p-4 text-center">
                      <Trophy className="w-6 h-6 mx-auto text-amber-500 mb-2" />
                      <p className="text-2xl font-bold text-amber-600">{assessoriaDetalhe.posicao_nacional || '-'}º</p>
                      <p className="text-xs text-slate-500">Posição Nacional</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-emerald-50 dark:bg-emerald-900/20">
                    <CardContent className="p-4 text-center">
                      <Users className="w-6 h-6 mx-auto text-emerald-500 mb-2" />
                      <p className="text-2xl font-bold text-emerald-600">{assessoriaDetalhe.total_atletas}</p>
                      <p className="text-xs text-slate-500">Atletas Ativos</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-blue-50 dark:bg-blue-900/20">
                    <CardContent className="p-4 text-center">
                      <CheckCircle className="w-6 h-6 mx-auto text-blue-500 mb-2" />
                      <p className="text-2xl font-bold text-blue-600">{assessoriaDetalhe.total_resultados}</p>
                      <p className="text-xs text-slate-500">Resultados</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-purple-50 dark:bg-purple-900/20">
                    <CardContent className="p-4 text-center">
                      <Award className="w-6 h-6 mx-auto text-purple-500 mb-2" />
                      <p className="text-2xl font-bold text-purple-600">{assessoriaDetalhe.pontos_total}</p>
                      <p className="text-xs text-slate-500">Pontos Total</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Localização e Pódios */}
                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                    <MapPin className="w-4 h-4" />
                    {assessoriaDetalhe.cidade}/{assessoriaDetalhe.estado}
                  </div>
                  <Badge variant="outline" className="bg-yellow-50">
                    🥇 {assessoriaDetalhe.total_primeiros} primeiros lugares
                  </Badge>
                  <Badge variant="outline" className="bg-slate-50">
                    🏅 {assessoriaDetalhe.total_podios} pódios (2º-5º)
                  </Badge>
                </div>

                {/* Atletas */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      Atletas da Equipe ({assessoriaDetalhe.atletas?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {assessoriaDetalhe.atletas?.slice(0, 20).map((atleta) => (
                        <div 
                          key={atleta.id}
                          className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 cursor-pointer transition-colors"
                          title={`${atleta.nome} - ${atleta.pontos || 0} pontos`}
                          onClick={() => {
                            setShowAssessoriaModal(false);
                            navigate(`/atleta/${atleta.id}`);
                          }}
                        >
                          <Avatar className="w-8 h-8">
                            {atleta.foto_url ? (
                              <AvatarImage src={atleta.foto_url.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                            ) : null}
                            <AvatarFallback className="text-xs bg-emerald-100 text-emerald-700">
                              {atleta.nome?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div className="text-xs">
                            <p className="font-medium truncate max-w-[100px]">{atleta.nome?.split(' ')[0]}</p>
                            <p className="text-slate-500">{atleta.pontos || 0} pts</p>
                          </div>
                        </div>
                      ))}
                      {assessoriaDetalhe.atletas?.length > 20 && (
                        <div className="flex items-center justify-center w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-lg text-xs text-slate-500">
                          +{assessoriaDetalhe.atletas.length - 20} mais
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Evolução Mensal */}
                {assessoriaDetalhe.evolucao_mensal && assessoriaDetalhe.evolucao_mensal.length > 0 && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <TrendingUp className="w-4 h-4" />
                        Evolução Mensal
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={200}>
                        <AreaChart data={assessoriaDetalhe.evolucao_mensal}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                          <XAxis dataKey="mes" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
                          <YAxis stroke="#9CA3AF" />
                          <Tooltip />
                          <Area type="monotone" dataKey="resultados" fill="#F59E0B" stroke="#D97706" fillOpacity={0.3} name="Resultados" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                )}

                {/* Selo Digital Oficial */}
                <Card className={`${getSeloColor(assessoriaDetalhe.selo)} border-0`}>
                  <CardContent className="p-6 text-center">
                    <div className="text-4xl mb-2">{getSeloIcon(assessoriaDetalhe.selo)}</div>
                    <h3 className="text-lg font-bold">SELO {assessoriaDetalhe.selo?.toUpperCase()}</h3>
                    <p className="text-sm opacity-90">Liga Nacional de Assessorias Ranking Run</p>
                    <p className="text-xs opacity-75 mt-1">Classificação Oficial ROE-RR – 2026</p>
                  </CardContent>
                </Card>

                {/* Botão de Contato */}
                <Button className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700">
                  <Send className="w-4 h-4 mr-2" />
                  Quero treinar com essa assessoria
                </Button>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default RankingPage;
