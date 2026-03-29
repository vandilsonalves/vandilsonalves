import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Trophy, Award, TrendingUp, Users, Eye, Star, HelpCircle, FileText, MapPin, Target, Send, RefreshCw, Loader2, Activity, BadgeCheck, CheckCircle } from 'lucide-react';
import { RegulamentoButton } from '@/components/RegulamentoModal';
import { useAuth } from '@/context/AuthContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, LineChart, Line, Legend } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RankingEquipes = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [ligaRanking, setLigaRanking] = useState([]);
  const [ligaStats, setLigaStats] = useState(null);
  const [ligaTipo, setLigaTipo] = useState('nacional');
  const [ligaEstado, setLigaEstado] = useState('');
  const [ligaCidade, setLigaCidade] = useState('');
  const [ligaMes, setLigaMes] = useState('');
  const [loadingLiga, setLoadingLiga] = useState(false);
  const [estadosComAssessorias, setEstadosComAssessorias] = useState([]);
  const [cidadesComAssessorias, setCidadesComAssessorias] = useState([]);
  const [assessoriaDetalhe, setAssessoriaDetalhe] = useState(null);
  const [showAssessoriaModal, setShowAssessoriaModal] = useState(false);
  const [evolucaoMensal, setEvolucaoMensal] = useState(null);
  const [showEvolucaoChart, setShowEvolucaoChart] = useState(true);
  const [showComoFuncionaEquipes, setShowComoFuncionaEquipes] = useState(false);
  const [showRegulamentoEquipes, setShowRegulamentoEquipes] = useState(false);
  const [displayCount, setDisplayCount] = useState(20);

  const getMesesDisponiveis = () => {
    const mesAtual = new Date().getMonth() + 1;
    const meses = [
      { value: '1', label: 'Janeiro' }, { value: '2', label: 'Fevereiro' },
      { value: '3', label: 'Março' }, { value: '4', label: 'Abril' },
      { value: '5', label: 'Maio' }, { value: '6', label: 'Junho' },
      { value: '7', label: 'Julho' }, { value: '8', label: 'Agosto' },
      { value: '9', label: 'Setembro' }, { value: '10', label: 'Outubro' },
      { value: '11', label: 'Novembro' }, { value: '12', label: 'Dezembro' }
    ];
    return meses.filter(m => parseInt(m.value) <= mesAtual);
  };

  useEffect(() => {
    setDisplayCount(20);
    fetchLigaRanking();
    fetchLigaStats();
    fetchEstadosComAssessorias();
    fetchEvolucaoMensal();
  }, [ligaTipo, ligaEstado, ligaCidade, ligaMes]);

  const fetchLigaRanking = async () => {
    setLoadingLiga(true);
    try {
      let url = `${API}/liga-assessorias/ranking?tipo=${ligaTipo}`;
      if (ligaTipo === 'estadual' && ligaEstado) url += `&estado=${ligaEstado}`;
      if (ligaTipo === 'cidade' && ligaCidade) url += `&cidade=${encodeURIComponent(ligaCidade)}`;
      if (ligaMes) url += `&mes=${ligaMes}`;
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(url, { headers });
      setLigaRanking(response.data.ranking || []);
    } catch (error) {
      console.error('Erro ao buscar ranking liga:', error);
      setLigaRanking([]);
    } finally { setLoadingLiga(false); }
  };

  const fetchLigaStats = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/stats`, { headers });
      setLigaStats(response.data);
    } catch (error) { console.error('Erro ao buscar stats liga:', error); }
  };

  const fetchEvolucaoMensal = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/evolucao-mensal?top=5`, { headers });
      setEvolucaoMensal(response.data);
    } catch (error) { console.error('Erro ao buscar evolução mensal:', error); }
  };

  const fetchEstadosComAssessorias = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/estados`, { headers });
      setEstadosComAssessorias(response.data || []);
    } catch (error) { console.error('Erro ao buscar estados:', error); }
  };

  const fetchCidadesComAssessorias = async (estado) => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/cidades?estado=${estado}`, { headers });
      setCidadesComAssessorias(response.data || []);
    } catch (error) { console.error('Erro ao buscar cidades:', error); }
  };

  const fetchAssessoriaDetalhe = async (nome) => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`${API}/liga-assessorias/assessoria/${encodeURIComponent(nome)}`, { headers });
      setAssessoriaDetalhe(response.data);
      setShowAssessoriaModal(true);
    } catch (error) { console.error('Erro ao buscar detalhes:', error); }
  };

  const getSeloIcon = (selo) => {
    switch(selo) { case 'ouro': return '🥇'; case 'prata': return '🥈'; case 'bronze': return '🥉'; default: return '🏅'; }
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
    <>
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

                  {/* NOVA SEÇÃO: Mudança de Equipe */}
                  <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg border border-amber-300">
                    <h3 className="font-semibold text-lg mb-2 text-amber-800 dark:text-amber-300 flex items-center gap-2">
                      <span>⚠️</span> Regra de Transferência de Atletas
                    </h3>
                    <p className="text-sm text-amber-700 dark:text-amber-400 mb-3">
                      Os pontos ficam vinculados à assessoria onde foram conquistados, <strong>não acompanham o atleta</strong> em caso de mudança de equipe.
                    </p>
                    <div className="bg-white dark:bg-slate-800 p-3 rounded-md space-y-2 text-sm">
                      <p><strong>Exemplo:</strong></p>
                      <ul className="list-disc list-inside space-y-1 text-slate-600 dark:text-slate-400">
                        <li>Atleta João está na <strong>Equipe A</strong> e conquista 6 resultados = 6 pontos para Equipe A</li>
                        <li>João muda para <strong>Equipe B</strong></li>
                        <li>Os 6 pontos <strong>permanecem na Equipe A</strong></li>
                        <li>João conquista mais 3 resultados na Equipe B = 3 pontos para Equipe B</li>
                        <li>Atletas que mudaram de equipe são identificados com o ícone <span className="text-amber-600">🔄</span></li>
                      </ul>
                    </div>
                    <p className="text-xs text-amber-600 mt-2">
                      Esta regra garante justiça e transparência no ranking de equipes.
                    </p>
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

                  {/* NOVA SEÇÃO: Regra de Transferência */}
                  <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border-l-4 border-red-500">
                    <h3 className="font-semibold text-base mb-2 text-red-800 dark:text-red-300">5.1. Regra de Transferência de Atletas</h3>
                    <p className="mb-2 text-sm">
                      <strong>IMPORTANTE:</strong> Os pontos conquistados por um atleta pertencem à assessoria onde foram obtidos, não ao atleta.
                    </p>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      <li>Ao mudar de equipe, os pontos NÃO acompanham o atleta</li>
                      <li>Pontos conquistados na equipe anterior permanecem nela</li>
                      <li>Na nova equipe, o atleta começa a pontuar do zero</li>
                      <li>Atletas que mudaram de equipe recebem identificação visual (🔄)</li>
                      <li>Esta regra evita transferências oportunistas e garante justiça</li>
                    </ul>
                    <p className="mt-2 text-xs text-red-600 dark:text-red-400">
                      <strong>Motivo:</strong> Garantir que o esforço coletivo de uma assessoria não seja prejudicado pela saída de atletas.
                    </p>
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
                        {ligaRanking.slice(0, displayCount).map((equipe, idx) => (
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
                {ligaRanking.length > displayCount && (
                  <div className="flex justify-center mt-4">
                    <Button
                      onClick={() => setDisplayCount(prev => prev + 20)}
                      variant="outline"
                      className="w-full md:w-auto"
                      data-testid="btn-carregar-mais-equipes"
                    >
                      Carregar mais ({Math.min(displayCount, ligaRanking.length)} de {ligaRanking.length})
                    </Button>
                  </div>
                )}
                {ligaRanking.length > 0 && ligaRanking.length <= displayCount && (
                  <p className="text-center text-sm text-slate-400 mt-3">
                    Mostrando todas as {ligaRanking.length} assessorias
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

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
    </>
  );
};

export default RankingEquipes;
