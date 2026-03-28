import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import RankingTable from '@/components/RankingTable';
import { Search, HelpCircle, Share2, Trophy, Flame, Users, Target, Award, CheckCircle, TrendingUp, Star, FileText, BadgeCheck, History, Activity, Zap, MapPin } from 'lucide-react';
import { RegulamentoButton } from '@/components/RegulamentoModal';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RankingGalera = () => {
  const navigate = useNavigate();
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
  const [periodoRankingPovao, setPeriodoRankingPovao] = useState('semanal');

  const [filtroNomePovao, setFiltroNomePovao] = useState('');
  const [filtroColocacaoPovao, setFiltroColocacaoPovao] = useState('');
  const [filtroUFPovao, setFiltroUFPovao] = useState('');
  const [filtroFaixaPovao, setFiltroFaixaPovao] = useState('');
  const [filtroEquipePovao, setFiltroEquipePovao] = useState('');
  const [filtroCidadePovao, setFiltroCidadePovao] = useState('');
  const [faixasDisponiveis, setFaixasDisponiveis] = useState([]);
  const [equipesDisponiveis, setEquipesDisponiveis] = useState([]);

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
    fetchRankingPovao();
    fetchPovaoDestaques();
  }, [generoPovao]);

  const rankingPovaoFiltrado = rankingPovao.filter(atleta => {
    const nomeMatch = atleta.nome.toLowerCase().includes(filtroNomePovao.toLowerCase());
    const colocacaoMatch = filtroColocacaoPovao === '' || atleta.colocacao === parseInt(filtroColocacaoPovao);
    const ufMatch = filtroUFPovao === '' || atleta.uf?.toUpperCase() === filtroUFPovao.toUpperCase();
    const faixaMatch = filtroFaixaPovao === '' || filtroFaixaPovao === 'all' || atleta.faixa_etaria === filtroFaixaPovao;
    const equipeMatch = filtroEquipePovao === '' || filtroEquipePovao === 'all' || atleta.equipe?.toLowerCase().includes(filtroEquipePovao.toLowerCase());
    const cidadeMatch = filtroCidadePovao === '' || atleta.cidade?.toLowerCase().includes(filtroCidadePovao.toLowerCase());
    return nomeMatch && colocacaoMatch && ufMatch && faixaMatch && equipeMatch && cidadeMatch;
  });

  const handleAtletaClick = (atletaId) => navigate(`/atleta/${atletaId}`);
  const limparFiltrosPovao = () => {
    setFiltroNomePovao(''); setFiltroColocacaoPovao(''); setFiltroUFPovao('');
    setFiltroFaixaPovao(''); setFiltroEquipePovao(''); setFiltroCidadePovao('');
  };

  return (
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
                      <SelectItem value="Até 17">Até 17</SelectItem>
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
  );
};

export default RankingGalera;
