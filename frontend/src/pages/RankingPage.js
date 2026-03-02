import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import RankingTable from '@/components/RankingTable';
import RankingDestaques from '@/components/RankingDestaques';
import NotificacoesBell from '@/components/NotificacoesBell';
import { Search, HelpCircle, LogIn, Upload, FileDown, Shield, LogOut, User, Share2, Trophy, Flame, Users, MapPin, Target } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RankingPage = () => {
  const navigate = useNavigate();
  const { user, isAdmin, logout } = useAuth();
  const [categoriaAtual, setCategoriaAtual] = useState('masculino');
  const [rankingData, setRankingData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDestaques, setShowDestaques] = useState(true);
  
  // Ranking do Povão
  const [tipoRanking, setTipoRanking] = useState('profissional'); // 'profissional' ou 'povao'
  const [generoPovao, setGeneroPovao] = useState('M');
  const [rankingPovao, setRankingPovao] = useState([]);
  const [povaoStats, setPovaoStats] = useState(null);
  const [loadingPovao, setLoadingPovao] = useState(false);
  
  // Filtros
  const [filtroNome, setFiltroNome] = useState('');
  const [filtroColocacao, setFiltroColocacao] = useState('');
  const [filtroUF, setFiltroUF] = useState('');
  const [filtroFaixa, setFiltroFaixa] = useState('');
  const [filtroEquipe, setFiltroEquipe] = useState('');
  const [filtroCidade, setFiltroCidade] = useState('');
  
  // Filtros do Povão
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

  // Buscar ranking do Povão
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
        console.error('Erro ao buscar ranking Povão:', error);
        setRankingPovao([]);
      } finally {
        setLoadingPovao(false);
      }
    };

    if (tipoRanking === 'povao') {
      fetchRankingPovao();
    }
  }, [tipoRanking, generoPovao]);

  // Aplicar filtros locais
  const rankingFiltrado = rankingData.filter(atleta => {
    const nomeMatch = atleta.nome.toLowerCase().includes(filtroNome.toLowerCase());
    const colocacaoMatch = filtroColocacao === '' || atleta.colocacao === parseInt(filtroColocacao);
    const ufMatch = atleta.uf.toLowerCase().includes(filtroUF.toLowerCase());
    
    return nomeMatch && colocacaoMatch && ufMatch;
  });

  // Aplicar filtros locais para o Povão
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
                
                {/* Notificações */}
                <NotificacoesBell />
                
                {isAdmin && (
                  <Button onClick={() => navigate('/admin')} variant="outline" size="sm">
                    <Shield className="w-4 h-4 mr-2" />
                    Admin
                  </Button>
                )}
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
            <div className="grid grid-cols-2">
              {/* Opção Profissional/Amador */}
              <button 
                className={`py-4 px-6 flex items-center justify-center gap-3 transition-all ${
                  tipoRanking === 'profissional' 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('profissional')}
                data-testid="tipo-ranking-profissional"
              >
                <Trophy className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold">Ranking Profissional/Amador</p>
                  <p className={`text-xs ${tipoRanking === 'profissional' ? 'text-emerald-100' : 'text-slate-400'}`}>
                    Pontuação por colocação
                  </p>
                </div>
              </button>
              
              {/* Opção Povão */}
              <button 
                className={`py-4 px-6 flex items-center justify-center gap-3 transition-all ${
                  tipoRanking === 'povao' 
                    ? 'bg-purple-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('povao')}
                data-testid="tipo-ranking-povao"
              >
                <Users className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold">Ranking do Povão</p>
                  <p className={`text-xs ${tipoRanking === 'povao' ? 'text-purple-100' : 'text-slate-400'}`}>
                    Pace Livre - Pontuação por distância
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
                      <SelectItem key={equipe} value={equipe}>{equipe}</SelectItem>
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
                  <RankingTable data={rankingFiltrado} onAtletaClick={handleAtletaClick} />
                )}
              </CardContent>
            </Card>
          </div>
        </div>
          </>
        )}

        {/* Ranking do Povão */}
        {tipoRanking === 'povao' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar de Filtros - Povão */}
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
                        <SelectItem key={eq} value={eq}>{eq}</SelectItem>
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
              </CardContent>
            </Card>

            {/* Conteúdo Principal - Povão */}
            <div className="lg:col-span-3 space-y-6">
              {/* Stats do Povão */}
              {povaoStats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30 border-0 shadow-lg">
                    <CardContent className="pt-6 text-center">
                      <Users className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                      <div className="text-3xl font-bold text-purple-700">{povaoStats.total_atletas || 0}</div>
                      <div className="text-sm text-purple-600">Atletas Povão</div>
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

              {/* Info sobre o sistema de pontuação */}
              <Card className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
                <CardContent className="pt-4">
                  <div className="flex items-start gap-3">
                    <HelpCircle className="w-5 h-5 text-purple-600 mt-0.5" />
                    <div className="text-sm text-purple-800 dark:text-purple-200">
                      <p className="font-semibold mb-1">Sistema de Pontuação do Povão</p>
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

              {/* Tabela do Ranking Povão */}
              <Card className="border-purple-200 dark:border-purple-800 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl flex items-center gap-2">
                    <Users className="w-5 h-5 text-purple-500" />
                    Ranking do Povão - {generoPovao === 'M' ? 'Masculino' : 'Feminino'}
                    <span className="ml-2 text-sm font-normal text-slate-600 dark:text-slate-400">
                      ({rankingPovaoFiltrado.length} atletas)
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                {loadingPovao ? (
                  <div className="text-center py-12 text-slate-600 dark:text-slate-400">
                    Carregando ranking do Povão...
                  </div>
                ) : rankingPovao.length === 0 ? (
                  <div className="text-center py-12 text-slate-500">
                    <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                    <p>Nenhum atleta cadastrado nesta modalidade ainda.</p>
                    <p className="text-sm mt-2">Seja o primeiro a participar do Ranking do Povão!</p>
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
                        {rankingPovao.map((atleta, index) => (
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
                                <Avatar className="h-10 w-10">
                                  <AvatarImage src={atleta.foto_url?.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                                  <AvatarFallback className="bg-purple-600 text-white">
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
        )}
      </div>
    </div>
  );
};

export default RankingPage;
