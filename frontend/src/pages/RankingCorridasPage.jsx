import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Trophy, Star, MapPin, Calendar, ExternalLink, Users, Award, 
  RefreshCw, Loader2, Plus, ArrowLeft, Home, LogOut, Filter,
  BarChart3, TrendingUp, Medal, ClipboardCheck, CheckCircle2, FileText,
  HelpCircle
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import { RegulamentoButton } from '@/components/RegulamentoModal';
import { RankingAvaliadores } from '@/components/ReputacaoAvaliador';
import CidadeCombobox from '@/components/CidadeCombobox';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RankingCorridasPage = () => {
  const navigate = useNavigate();
  const { user, token, isAdmin, logout } = useAuth();
  
  const [ranking, setRanking] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tipo, setTipo] = useState('nacional');
  const [estado, setEstado] = useState('');
  const [cidade, setCidade] = useState('');
  const [estados, setEstados] = useState([]);
  const [cidades, setCidades] = useState([]);
  
  // Modal de cadastro de corrida
  const [showCadastroModal, setShowCadastroModal] = useState(false);
  const [cadastroLoading, setCadastroLoading] = useState(false);
  const [formData, setFormData] = useState({
    nome_corrida: '',
    organizador: '',
    cidade: '',
    estado: '',
    data_corrida: '',
    pagina_link: '',
    status: 'ativa'
  });

  // Modal de avaliação
  const [showAvaliacaoModal, setShowAvaliacaoModal] = useState(false);
  const [corridaSelecionada, setCorridaSelecionada] = useState(null);
  const [avaliacaoLoading, setAvaliacaoLoading] = useState(false);
  const [termoTexto, setTermoTexto] = useState(null);
  const [showRankingAvaliadores, setShowRankingAvaliadores] = useState(false);
  const [showComoFunciona, setShowComoFunciona] = useState(false);
  const [showRegulamento, setShowRegulamento] = useState(false);
  const [avaliacaoData, setAvaliacaoData] = useState({
    organizacao: 0,
    percurso: 0,
    kit_atleta: 0,
    hidratacao: 0,
    pos_prova: 0,
    premiacao: 0,
    participei: false,
    aceito_termo: false
  });

  // Estados para o formulário de cadastro - cidades do IBGE
  const [cidadesIBGE, setCidadesIBGE] = useState([]);
  const [loadingCidadesIBGE, setLoadingCidadesIBGE] = useState(false);

  useEffect(() => {
    fetchRanking();
    fetchStats();
    fetchEstados();
  }, [tipo, estado, cidade]);

  const fetchRanking = async () => {
    setLoading(true);
    try {
      let url = `${API}/ranking-corridas?tipo=${tipo}`;
      if (tipo === 'estadual' && estado) {
        url += `&estado=${estado}`;
      }
      if (tipo === 'cidade') {
        // Sempre enviar o estado quando estiver na aba cidade
        if (estado) {
          url += `&estado=${estado}`;
        }
        if (cidade) {
          url += `&cidade=${encodeURIComponent(cidade)}`;
        }
      }
      
      const response = await axios.get(url);
      setRanking(response.data.ranking || []);
    } catch (error) {
      console.error('Erro ao buscar ranking:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/ranking-corridas/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Erro ao buscar stats:', error);
    }
  };

  const fetchEstados = async () => {
    try {
      const response = await axios.get(`${API}/ranking-corridas/estados`);
      // A API retorna {estados: [...]} então precisamos acessar response.data.estados
      const data = response.data;
      setEstados(Array.isArray(data) ? data : (data.estados || []));
    } catch (error) {
      console.error('Erro ao buscar estados:', error);
      setEstados([]);
    }
  };

  const fetchCidades = async (uf) => {
    try {
      const response = await axios.get(`${API}/ranking-corridas/cidades?estado=${uf}`);
      // A API pode retornar {cidades: [...]} ou apenas [...]
      const data = response.data;
      setCidades(Array.isArray(data) ? data : (data.cidades || []));
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
      setCidades([]);
    }
  };

  // Buscar cidades do IBGE para o formulário de cadastro
  const fetchCidadesIBGE = async (uf) => {
    if (!uf) return;
    setLoadingCidadesIBGE(true);
    try {
      const response = await axios.get(
        `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios`
      );
      const cidadesOrdenadas = response.data
        .map(cidade => cidade.nome)
        .sort((a, b) => a.localeCompare(b));
      setCidadesIBGE(cidadesOrdenadas);
    } catch (error) {
      console.error('Erro ao buscar cidades do IBGE:', error);
      setCidadesIBGE([]);
      toast.error('Erro ao buscar cidades. Tente novamente.');
    } finally {
      setLoadingCidadesIBGE(false);
    }
  };

  // Quando o estado do formulário mudar, buscar cidades do IBGE
  useEffect(() => {
    if (formData.estado) {
      fetchCidadesIBGE(formData.estado);
      setFormData(prev => ({ ...prev, cidade: '' })); // Limpar cidade ao mudar estado
    }
  }, [formData.estado]);

  const handleCadastrarCorrida = async () => {
    if (!formData.nome_corrida || !formData.organizador || !formData.cidade || !formData.estado || !formData.data_corrida) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setCadastroLoading(true);
    try {
      const form = new FormData();
      Object.keys(formData).forEach(key => {
        form.append(key, formData[key]);
      });

      await axios.post(`${API}/corridas-eventos`, form, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success('Corrida cadastrada com sucesso!');
      setShowCadastroModal(false);
      setFormData({
        nome_corrida: '',
        organizador: '',
        cidade: '',
        estado: '',
        data_corrida: '',
        pagina_link: '',
        status: 'ativa'
      });
      fetchRanking();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao cadastrar corrida');
    } finally {
      setCadastroLoading(false);
    }
  };

  // Abrir modal de avaliação
  const handleAbrirAvaliacao = async (corrida) => {
    if (!user) {
      toast.error('Faça login para avaliar corridas');
      navigate('/login');
      return;
    }
    
    // Verificar se corrida já ocorreu
    const hoje = new Date();
    const dataCorrida = new Date(corrida.data_corrida);
    if (dataCorrida > hoje) {
      toast.error('Avaliações disponíveis apenas após a realização da corrida');
      return;
    }
    
    // Verificar se já avaliou
    try {
      const response = await axios.get(`${API}/verificar-avaliacao/${corrida.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.ja_avaliou) {
        toast.error('Você já avaliou esta corrida');
        return;
      }
    } catch (error) {
      console.error('Erro ao verificar avaliação:', error);
    }
    
    setCorridaSelecionada(corrida);
    setAvaliacaoData({
      organizacao: 0,
      percurso: 0,
      kit_atleta: 0,
      hidratacao: 0,
      pos_prova: 0,
      premiacao: 0,
      participei: false,
      aceito_termo: false
    });
    
    // Buscar texto do termo
    try {
      const termoResponse = await axios.get(`${API}/admin/avaliacoes/termo`);
      setTermoTexto(termoResponse.data);
    } catch (error) {
      console.error('Erro ao buscar termo:', error);
    }
    
    setShowAvaliacaoModal(true);
  };

  // Enviar avaliação
  const handleEnviarAvaliacao = async () => {
    // Validar se todos os critérios foram avaliados
    if (avaliacaoData.organizacao === 0 || avaliacaoData.percurso === 0 || 
        avaliacaoData.kit_atleta === 0 || avaliacaoData.hidratacao === 0 || 
        avaliacaoData.pos_prova === 0 || avaliacaoData.premiacao === 0) {
      toast.error('Avalie todos os 6 critérios antes de enviar');
      return;
    }
    
    if (!avaliacaoData.participei) {
      toast.error('Você precisa confirmar que participou desta corrida');
      return;
    }
    
    if (!avaliacaoData.aceito_termo) {
      toast.error('Você precisa aceitar o termo de responsabilidade');
      return;
    }

    setAvaliacaoLoading(true);
    try {
      const form = new FormData();
      form.append('corrida_id', corridaSelecionada.id);
      form.append('organizacao', avaliacaoData.organizacao);
      form.append('percurso', avaliacaoData.percurso);
      form.append('kit_atleta', avaliacaoData.kit_atleta);
      form.append('hidratacao', avaliacaoData.hidratacao);
      form.append('pos_prova', avaliacaoData.pos_prova);
      form.append('premiacao', avaliacaoData.premiacao);
      form.append('participei', avaliacaoData.participei);
      form.append('aceito_termo', avaliacaoData.aceito_termo);

      const response = await axios.post(
        `${API}/avaliar-corrida`,
        form,
        {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      toast.success(`Avaliação registrada! Nota final: ${response.data.nota_corrida}`);
      setShowAvaliacaoModal(false);
      setCorridaSelecionada(null);
      fetchRanking();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao enviar avaliação');
    } finally {
      setAvaliacaoLoading(false);
    }
  };

  // Componente de avaliação por estrelas interativo
  const StarRating = ({ value, onChange, label, description }) => {
    const [hoverValue, setHoverValue] = useState(0);
    
    return (
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium">{label}</Label>
          <span className="text-xs text-slate-500">{description}</span>
        </div>
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className="p-1 transition-transform hover:scale-110"
              onMouseEnter={() => setHoverValue(star)}
              onMouseLeave={() => setHoverValue(0)}
              onClick={() => onChange(star)}
            >
              <Star
                className={`w-7 h-7 transition-colors ${
                  star <= (hoverValue || value)
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-slate-300 hover:text-yellow-200'
                }`}
              />
            </button>
          ))}
          <span className="ml-2 text-sm font-medium text-slate-600">
            {value > 0 ? getRatingLabel(value) : '-'}
          </span>
        </div>
      </div>
    );
  };

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />);
      } else if (i === fullStars && hasHalfStar) {
        stars.push(<Star key={i} className="w-4 h-4 fill-yellow-400/50 text-yellow-400" />);
      } else {
        stars.push(<Star key={i} className="w-4 h-4 text-slate-300" />);
      }
    }
    return stars;
  };

  const getRatingLabel = (rating) => {
    if (rating >= 4.5) return 'Excelente';
    if (rating >= 3.5) return 'Ótima';
    if (rating >= 2.5) return 'Boa';
    if (rating >= 1.5) return 'Regular';
    return 'Péssima';
  };

  const canCadastrar = user && (user.role === 'admin' || user.role === 'dono_assessoria');

  const ESTADOS_BR = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
    "RS", "RO", "RR", "SC", "SP", "SE", "TO"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button onClick={() => navigate('/')} variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar
            </Button>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-slate-800 dark:text-white flex items-center gap-3">
                <Trophy className="w-8 h-8 text-yellow-500" />
                Ranking das Corridas
              </h1>
              <p className="text-slate-500 text-sm mt-1">
                Avaliações de corridas de rua por atletas
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              onClick={() => setShowRankingAvaliadores(!showRankingAvaliadores)}
              variant={showRankingAvaliadores ? "default" : "outline"}
              size="default"
              className={showRankingAvaliadores ? "bg-amber-500 hover:bg-amber-600" : "text-amber-600 border-amber-500/30"}
            >
              <Award className="w-4 h-4 mr-2" />
              Top Avaliadores
            </Button>
            <RegulamentoButton 
              className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 border-emerald-500/30"
              variant="outline"
              size="default"
            />
            {canCadastrar && (
              <Button onClick={() => setShowCadastroModal(true)} className="bg-emerald-500 hover:bg-emerald-600">
                <Plus className="w-4 h-4 mr-2" />
                Cadastrar Corrida
              </Button>
            )}
          </div>
        </div>

        {/* Legenda de Avaliação */}
        <Card className="mb-6 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200">
          <CardContent className="p-4">
            <div className="flex flex-wrap items-center justify-center gap-4 text-sm">
              <span className="font-semibold text-yellow-800 dark:text-yellow-200">Legenda:</span>
              <span className="flex items-center gap-1"><Star className="w-4 h-4 fill-yellow-400 text-yellow-400" /> Péssima</span>
              <span className="flex items-center gap-1">{renderStars(2)} Regular</span>
              <span className="flex items-center gap-1">{renderStars(3)} Boa</span>
              <span className="flex items-center gap-1">{renderStars(4)} Ótima</span>
              <span className="flex items-center gap-1">{renderStars(5)} Excelente</span>
            </div>
            {/* Botões Como funciona e Regulamento */}
            <div className="flex justify-center gap-3 mt-4">
              <Button 
                variant="outline"
                className="bg-yellow-400 hover:bg-yellow-500 text-slate-900 font-semibold border-0"
                onClick={() => setShowComoFunciona(true)}
                data-testid="btn-como-funciona-corridas"
              >
                <HelpCircle className="w-4 h-4 mr-2" />
                Como funciona?
              </Button>
              <Button 
                variant="outline"
                className="bg-blue-500/10 hover:bg-blue-500/20 text-blue-700 font-semibold border-blue-500/30"
                onClick={() => setShowRegulamento(true)}
                data-testid="btn-regulamento-corridas"
              >
                <FileText className="w-4 h-4 mr-2" />
                Regulamento
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Modal Como Funciona - Ranking de Corridas */}
        <Dialog open={showComoFunciona} onOpenChange={setShowComoFunciona}>
          <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold text-blue-600 flex items-center gap-2">
                <HelpCircle className="w-6 h-6" />
                Como funciona o Ranking das Corridas?
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4 text-slate-700 dark:text-slate-300">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <h3 className="font-semibold text-lg mb-2 text-blue-700">O que é o Ranking das Corridas?</h3>
                <p>O Ranking das Corridas é um sistema de <strong>avaliação colaborativa</strong> onde atletas avaliam as corridas de rua que participaram. As notas determinam a posição de cada evento no ranking.</p>
              </div>
              
              <div>
                <h3 className="font-semibold text-lg mb-2">Sistema de Avaliação</h3>
                <p className="mb-3">Cada corrida é avaliada em <strong>6 critérios</strong>, com notas de 1 a 5 estrelas:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">🏢</span>
                      <span className="font-semibold">Organização</span>
                    </div>
                    <p className="text-xs text-slate-500">Estrutura, pontualidade, comunicação</p>
                  </div>
                  <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">🛣️</span>
                      <span className="font-semibold">Percurso</span>
                    </div>
                    <p className="text-xs text-slate-500">Sinalização, segurança, qualidade</p>
                  </div>
                  <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">🎁</span>
                      <span className="font-semibold">Kit do Atleta</span>
                    </div>
                    <p className="text-xs text-slate-500">Camiseta, medalha, brindes</p>
                  </div>
                  <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">💧</span>
                      <span className="font-semibold">Hidratação</span>
                    </div>
                    <p className="text-xs text-slate-500">Postos, disponibilidade, variedade</p>
                  </div>
                  <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">🎉</span>
                      <span className="font-semibold">Pós-Prova</span>
                    </div>
                    <p className="text-xs text-slate-500">Alimentação, área de recuperação</p>
                  </div>
                  <div className="bg-amber-100 dark:bg-amber-900/30 p-3 rounded-lg border-2 border-amber-400">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">🏆</span>
                      <span className="font-semibold text-amber-700 dark:text-amber-300">Premiação</span>
                    </div>
                    <p className="text-xs text-amber-600 dark:text-amber-400">Dinheiro, brindes, qualidade dos prêmios</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold text-lg mb-2">Cálculo da Nota Final</h3>
                <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-lg font-mono text-sm">
                  <p><strong>Nota Média</strong> = (Organização + Percurso + Kit + Hidratação + Pós-Prova + Premiação) ÷ 6</p>
                </div>
                <p className="text-sm mt-2 text-slate-500">A nota final é a média de todas as avaliações recebidas pela corrida.</p>
              </div>

              <div>
                <h3 className="font-semibold text-lg mb-2">Escala de Classificação</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between bg-yellow-100 dark:bg-yellow-900/30 p-2 rounded">
                    <span className="flex items-center gap-2"><Star className="w-4 h-4 fill-yellow-400 text-yellow-400" /> 4.5 - 5.0</span>
                    <Badge className="bg-yellow-500">Excelente</Badge>
                  </div>
                  <div className="flex items-center justify-between bg-emerald-100 dark:bg-emerald-900/30 p-2 rounded">
                    <span className="flex items-center gap-2"><Star className="w-4 h-4 fill-emerald-400 text-emerald-400" /> 3.5 - 4.4</span>
                    <Badge className="bg-emerald-500">Ótima</Badge>
                  </div>
                  <div className="flex items-center justify-between bg-blue-100 dark:bg-blue-900/30 p-2 rounded">
                    <span className="flex items-center gap-2"><Star className="w-4 h-4 fill-blue-400 text-blue-400" /> 2.5 - 3.4</span>
                    <Badge className="bg-blue-500">Boa</Badge>
                  </div>
                  <div className="flex items-center justify-between bg-orange-100 dark:bg-orange-900/30 p-2 rounded">
                    <span className="flex items-center gap-2"><Star className="w-4 h-4 fill-orange-400 text-orange-400" /> 1.5 - 2.4</span>
                    <Badge className="bg-orange-500">Regular</Badge>
                  </div>
                  <div className="flex items-center justify-between bg-red-100 dark:bg-red-900/30 p-2 rounded">
                    <span className="flex items-center gap-2"><Star className="w-4 h-4 fill-red-400 text-red-400" /> 1.0 - 1.4</span>
                    <Badge className="bg-red-500">Péssima</Badge>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-lg mb-2">Quem pode avaliar?</h3>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Qualquer atleta cadastrado na plataforma</li>
                  <li>É necessário marcar "Participei desta corrida"</li>
                  <li>Cada atleta pode avaliar uma corrida apenas uma vez</li>
                  <li>Avaliações são públicas e contribuem para o ranking</li>
                </ul>
              </div>
            </div>
            <DialogFooter>
              <Button onClick={() => setShowComoFunciona(false)} className="bg-blue-600 hover:bg-blue-700">
                Entendi!
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal Regulamento - Ranking de Corridas */}
        <Dialog open={showRegulamento} onOpenChange={setShowRegulamento}>
          <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold text-blue-600 flex items-center gap-2">
                <FileText className="w-6 h-6" />
                Regulamento do Ranking das Corridas
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4 text-slate-700 dark:text-slate-300 text-sm">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <h3 className="font-semibold text-base mb-2">1. Objetivo</h3>
                <p>O Ranking das Corridas tem como objetivo criar um sistema transparente de avaliação de eventos de corrida de rua, ajudando atletas a escolherem as melhores provas e incentivando organizadores a melhorarem seus eventos.</p>
              </div>
              
              <div>
                <h3 className="font-semibold text-base mb-2">2. Elegibilidade para Avaliação</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>O avaliador deve estar cadastrado na plataforma Ranking Run</li>
                  <li>O avaliador deve declarar que participou da corrida</li>
                  <li>É permitida apenas uma avaliação por atleta por corrida</li>
                  <li>A avaliação deve ser feita de forma honesta e imparcial</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold text-base mb-2">3. Critérios de Avaliação</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li><strong>Organização (1-5):</strong> Estrutura do evento, pontualidade, comunicação, atendimento</li>
                  <li><strong>Percurso (1-5):</strong> Sinalização, segurança, qualidade do piso, paisagem</li>
                  <li><strong>Kit do Atleta (1-5):</strong> Qualidade da camiseta, medalha, sacola, brindes</li>
                  <li><strong>Hidratação (1-5):</strong> Quantidade de postos, disponibilidade, variedade de bebidas</li>
                  <li><strong>Pós-Prova (1-5):</strong> Alimentação, área de descanso, massagem</li>
                  <li><strong>Premiação (1-5):</strong> Prêmios em dinheiro, qualidade dos brindes, troféus, sorteios</li>
                </ul>
                <p className="mt-2 text-xs text-slate-500">* A nota final é a média aritmética dos 6 critérios</p>
              </div>
              
              <div>
                <h3 className="font-semibold text-base mb-2">4. Cadastro de Corridas</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>Corridas podem ser cadastradas por administradores ou donos de assessoria</li>
                  <li>Informações obrigatórias: nome, cidade, estado, data</li>
                  <li>Corridas duplicadas serão removidas</li>
                  <li>Informações falsas resultarão em exclusão da corrida</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold text-base mb-2">5. Classificação no Ranking</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li><strong>Nacional:</strong> Todas as corridas do Brasil ordenadas por nota média</li>
                  <li><strong>Estadual:</strong> Corridas filtradas por estado (UF)</li>
                  <li><strong>Cidade:</strong> Corridas filtradas por município</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold text-base mb-2">6. Critérios de Desempate</h3>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Maior nota média</li>
                  <li>Maior número de avaliações</li>
                  <li>Data mais recente do evento</li>
                </ol>
              </div>
              
              <div>
                <h3 className="font-semibold text-base mb-2">7. Conduta dos Avaliadores</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>Avaliações devem refletir a experiência real do atleta</li>
                  <li>Comentários ofensivos ou difamatórios serão removidos</li>
                  <li>Avaliações fraudulentas resultarão em banimento</li>
                  <li>Conflitos de interesse devem ser declarados</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold text-base mb-2">8. Direitos dos Organizadores</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>Organizadores podem visualizar as avaliações de seus eventos</li>
                  <li>É possível responder às avaliações de forma educada</li>
                  <li>Organizadores podem solicitar remoção de avaliações falsas</li>
                </ul>
              </div>
              
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <h3 className="font-semibold text-base mb-2">9. Disposições Gerais</h3>
                <p>A organização reserva-se o direito de remover avaliações ou corridas que violem este regulamento. Casos omissos serão analisados pela equipe do Ranking Run.</p>
              </div>
            </div>
            <DialogFooter>
              <Button onClick={() => setShowRegulamento(false)} className="bg-blue-600 hover:bg-blue-700">
                Fechar
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-xs">Total Corridas</p>
                    <p className="text-2xl font-bold">{stats.total_corridas}</p>
                  </div>
                  <Trophy className="w-8 h-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-emerald-100 text-xs">Total Avaliações</p>
                    <p className="text-2xl font-bold">{stats.total_avaliacoes}</p>
                  </div>
                  <Star className="w-8 h-8 text-emerald-200" />
                </div>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-yellow-500 to-amber-600 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-yellow-100 text-xs">Média Geral</p>
                    <p className="text-2xl font-bold">{stats.media_geral || '-'}</p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-yellow-200" />
                </div>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-xs">Melhor Avaliada</p>
                    <p className="text-sm font-bold truncate">{stats.corrida_melhor_avaliada?.nome_corrida || '-'}</p>
                  </div>
                  <Medal className="w-8 h-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Ranking de Avaliadores (toggle) */}
        {showRankingAvaliadores && (
          <div className="mb-6">
            <RankingAvaliadores />
          </div>
        )}

        {/* Tabs de Período */}
        <Card className="mb-6 overflow-hidden">
          <CardContent className="p-0">
            <div className="grid grid-cols-3 md:grid-cols-6">
              {[
                { id: 'nacional', label: '🌍 Nacional' },
                { id: 'estadual', label: '🗺️ Estadual' },
                { id: 'cidade', label: '🏙️ Cidade' },
                { id: 'mensal', label: '📅 Mensal' },
                { id: 'anual', label: '📆 Anual' },
                { id: 'historico', label: '📊 Histórico' }
              ].map(tab => (
                <button
                  key={tab.id}
                  className={`py-3 px-2 text-center transition-all border-b-2 text-sm ${
                    tipo === tab.id
                      ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500 text-yellow-700 dark:text-yellow-300 font-semibold'
                      : 'bg-white dark:bg-slate-800 border-transparent text-slate-600 hover:bg-slate-50'
                  }`}
                  onClick={() => { setTipo(tab.id); setEstado(''); setCidade(''); }}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Filtros Adicionais */}
        {(tipo === 'estadual' || tipo === 'cidade') && (
          <Card className="mb-6">
            <CardContent className="p-4">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                  <Label className="text-sm">Estado:</Label>
                  <Select value={estado} onValueChange={(v) => {
                    setEstado(v);
                    setCidade('');
                    if (tipo === 'cidade') fetchCidades(v);
                  }}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      {Array.isArray(estados) && estados.map(uf => (
                        <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {tipo === 'cidade' && estado && (
                  <div className="flex items-center gap-2">
                    <Label className="text-sm">Cidade:</Label>
                    <Select value={cidade} onValueChange={setCidade}>
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="Selecione" />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.isArray(cidades) && cidades.map(c => (
                          <SelectItem key={c} value={c}>{c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <Button variant="outline" size="sm" onClick={fetchRanking}>
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Atualizar
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Tabela de Ranking */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-500" />
                🏆 Ranking das Corridas
              </span>
              <Badge variant="secondary">
                {ranking.filter(c => c.no_ranking).length} no ranking
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-yellow-500" />
              </div>
            ) : ranking.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Trophy className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>Nenhuma corrida encontrada</p>
                {canCadastrar && (
                  <Button onClick={() => setShowCadastroModal(true)} className="mt-4" variant="outline">
                    <Plus className="w-4 h-4 mr-2" />
                    Cadastrar Primeira Corrida
                  </Button>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-slate-700 bg-yellow-50 dark:bg-yellow-900/20">
                      <th className="text-left py-3 px-2 font-semibold text-yellow-800 dark:text-yellow-200">Pos</th>
                      <th className="text-left py-3 px-2 font-semibold text-yellow-800 dark:text-yellow-200">Corrida</th>
                      <th className="text-left py-3 px-2 font-semibold text-yellow-800 dark:text-yellow-200 hidden md:table-cell">Organização</th>
                      <th className="text-left py-3 px-2 font-semibold text-yellow-800 dark:text-yellow-200">Cidade/UF</th>
                      <th className="text-center py-3 px-2 font-semibold text-yellow-800 dark:text-yellow-200 hidden md:table-cell">Página</th>
                      <th className="text-center py-3 px-2 font-semibold text-yellow-800 dark:text-yellow-200">Ação</th>
                      <th className="text-right py-3 px-2 font-semibold text-yellow-800 dark:text-yellow-200">Pontos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ranking.map((corrida, idx) => (
                      <tr
                        key={corrida.id}
                        className={`border-b border-slate-100 dark:border-slate-800 hover:bg-yellow-50 dark:hover:bg-yellow-900/10 transition-colors ${
                          idx < 3 && corrida.no_ranking ? 'bg-yellow-50/50 dark:bg-yellow-900/10' : ''
                        } ${!corrida.no_ranking ? 'opacity-60' : ''}`}
                      >
                        <td className="py-3 px-2">
                          {corrida.no_ranking ? (
                            <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                              corrida.posicao === 1 ? 'bg-yellow-400 text-yellow-900' :
                              corrida.posicao === 2 ? 'bg-slate-300 text-slate-700' :
                              corrida.posicao === 3 ? 'bg-amber-600 text-white' :
                              'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                            }`}>
                              {corrida.posicao}
                            </span>
                          ) : (
                            <span className="text-xs text-slate-400">-</span>
                          )}
                        </td>
                        <td className="py-3 px-2">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-slate-800 dark:text-white">
                                {corrida.nome_corrida}
                              </span>
                              {corrida.selo === '5_estrelas' && (
                                <Badge className="bg-yellow-500 text-white text-xs">⭐ 5 Estrelas</Badge>
                              )}
                              {corrida.selo_top10 && (
                                <Badge className="bg-blue-500 text-white text-xs">🏆 Top 10</Badge>
                              )}
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                              {renderStars(corrida.media_geral)}
                              <span className="text-xs text-slate-500 ml-1">
                                {corrida.media_geral} ({corrida.total_avaliacoes} aval.)
                              </span>
                            </div>
                            {!corrida.no_ranking && corrida.total_avaliacoes < 10 && (
                              <p className="text-xs text-amber-600 mt-1">
                                Aguardando {10 - corrida.total_avaliacoes} avaliações para entrar no ranking
                              </p>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-2 text-slate-600 dark:text-slate-400 hidden md:table-cell">
                          {corrida.organizador}
                        </td>
                        <td className="py-3 px-2">
                          <div className="flex items-center gap-1 text-slate-600 dark:text-slate-400">
                            <MapPin className="w-3 h-3" />
                            <span className="text-sm">{corrida.cidade}/{corrida.estado}</span>
                          </div>
                        </td>
                        <td className="py-3 px-2 text-center hidden md:table-cell">
                          {corrida.pagina_link ? (
                            <a 
                              href={corrida.pagina_link} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-blue-500 hover:text-blue-700"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          ) : (
                            <span className="text-slate-300">-</span>
                          )}
                        </td>
                        <td className="py-3 px-2 text-center">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAbrirAvaliacao(corrida)}
                            className="text-xs bg-emerald-50 border-emerald-300 text-emerald-700 hover:bg-emerald-100"
                            data-testid={`avaliar-corrida-${corrida.id}`}
                          >
                            <ClipboardCheck className="w-3 h-3 mr-1" />
                            Avaliar
                          </Button>
                        </td>
                        <td className="py-3 px-2 text-right">
                          <span className="text-xl font-bold text-yellow-600">
                            {corrida.pontuacao_ranking}
                          </span>
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

      {/* Modal Cadastro de Corrida */}
      <Dialog open={showCadastroModal} onOpenChange={setShowCadastroModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="w-5 h-5 text-emerald-500" />
              Cadastrar Nova Corrida
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nome da Corrida *</Label>
              <Input
                value={formData.nome_corrida}
                onChange={(e) => setFormData({...formData, nome_corrida: e.target.value})}
                placeholder="Ex: Maratona de São Paulo"
              />
            </div>
            <div>
              <Label>Organizador / Empresa *</Label>
              <Input
                value={formData.organizador}
                onChange={(e) => setFormData({...formData, organizador: e.target.value})}
                placeholder="Ex: Yescom"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Estado *</Label>
                <Select value={formData.estado} onValueChange={(v) => setFormData({...formData, estado: v, cidade: ''})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o UF" />
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
                <CidadeCombobox
                  cidades={cidadesIBGE}
                  value={formData.cidade}
                  onValueChange={(v) => setFormData({...formData, cidade: v})}
                  loading={loadingCidadesIBGE}
                  disabled={!formData.estado}
                />
                {!formData.estado && (
                  <p className="text-xs text-slate-500 mt-1">Selecione o estado primeiro</p>
                )}
              </div>
            </div>
            <div>
              <Label>Data da Corrida *</Label>
              <Input
                type="date"
                value={formData.data_corrida}
                onChange={(e) => setFormData({...formData, data_corrida: e.target.value})}
              />
            </div>
            <div>
              <Label>Link da Página (Instagram ou Site)</Label>
              <Input
                value={formData.pagina_link}
                onChange={(e) => setFormData({...formData, pagina_link: e.target.value})}
                placeholder="https://..."
              />
            </div>
            <div>
              <Label>Status</Label>
              <Select value={formData.status} onValueChange={(v) => setFormData({...formData, status: v})}>
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
            <Button variant="outline" onClick={() => setShowCadastroModal(false)}>
              Cancelar
            </Button>
            <Button 
              onClick={handleCadastrarCorrida} 
              disabled={cadastroLoading}
              className="bg-emerald-500 hover:bg-emerald-600"
            >
              {cadastroLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Cadastrando...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4 mr-2" />
                  Cadastrar
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Avaliação de Corrida */}
      <Dialog open={showAvaliacaoModal} onOpenChange={setShowAvaliacaoModal}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              Avaliar Corrida
            </DialogTitle>
            <DialogDescription>
              {corridaSelecionada && (
                <div className="mt-2 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <p className="font-semibold text-slate-800 dark:text-white">
                    {corridaSelecionada.nome_corrida}
                  </p>
                  <p className="text-sm text-slate-500 flex items-center gap-1 mt-1">
                    <MapPin className="w-3 h-3" />
                    {corridaSelecionada.cidade}/{corridaSelecionada.estado}
                    <span className="mx-2">•</span>
                    <Calendar className="w-3 h-3" />
                    {corridaSelecionada.data_corrida}
                  </p>
                </div>
              )}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-5 py-4">
            {/* Legenda IQC */}
            <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg border border-yellow-200">
              <p className="text-xs font-semibold text-yellow-800 dark:text-yellow-200 mb-1">
                Índice de Qualidade da Corrida (IQC)
              </p>
              <p className="text-xs text-yellow-700 dark:text-yellow-300">
                Avalie de 1 a 5 estrelas cada critério baseado na sua experiência
              </p>
            </div>
            
            {/* 6 Critérios de Avaliação */}
            <div className="space-y-4">
              <StarRating
                value={avaliacaoData.organizacao}
                onChange={(v) => setAvaliacaoData({...avaliacaoData, organizacao: v})}
                label="1. Organização"
                description="Estrutura, sinalização, apoio"
              />
              
              <StarRating
                value={avaliacaoData.percurso}
                onChange={(v) => setAvaliacaoData({...avaliacaoData, percurso: v})}
                label="2. Percurso"
                description="Trajeto, segurança, paisagem"
              />
              
              <StarRating
                value={avaliacaoData.kit_atleta}
                onChange={(v) => setAvaliacaoData({...avaliacaoData, kit_atleta: v})}
                label="3. Kit do Atleta"
                description="Camiseta, medalha, brindes"
              />
              
              <StarRating
                value={avaliacaoData.hidratacao}
                onChange={(v) => setAvaliacaoData({...avaliacaoData, hidratacao: v})}
                label="4. Hidratação"
                description="Postos, água, isotônico"
              />
              
              <StarRating
                value={avaliacaoData.pos_prova}
                onChange={(v) => setAvaliacaoData({...avaliacaoData, pos_prova: v})}
                label="5. Pós-Prova"
                description="Frutas, massagem, estrutura"
              />
              
              <div className="bg-amber-50 dark:bg-amber-900/20 p-3 rounded-lg border border-amber-300">
                <StarRating
                  value={avaliacaoData.premiacao}
                  onChange={(v) => setAvaliacaoData({...avaliacaoData, premiacao: v})}
                  label="6. Premiação"
                  description="Dinheiro, brindes, troféus, sorteios"
                />
              </div>
            </div>
            
            {/* Média calculada */}
            {avaliacaoData.organizacao > 0 && avaliacaoData.percurso > 0 && 
             avaliacaoData.kit_atleta > 0 && avaliacaoData.hidratacao > 0 && 
             avaliacaoData.pos_prova > 0 && avaliacaoData.premiacao > 0 && (
              <div className="p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-emerald-800 dark:text-emerald-200">
                    Sua nota final:
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-emerald-600">
                      {((avaliacaoData.organizacao + avaliacaoData.percurso + 
                         avaliacaoData.kit_atleta + avaliacaoData.hidratacao + 
                         avaliacaoData.pos_prova + avaliacaoData.premiacao) / 6).toFixed(1)}
                    </span>
                    <span className="text-sm text-emerald-600">/ 5.0</span>
                  </div>
                </div>
              </div>
            )}
            
            {/* Checkbox de participação */}
            <div className="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border">
              <Checkbox
                id="participei"
                checked={avaliacaoData.participei}
                onCheckedChange={(checked) => setAvaliacaoData({...avaliacaoData, participei: checked})}
                className="mt-0.5"
              />
              <div className="grid gap-1.5 leading-none">
                <label
                  htmlFor="participei"
                  className="text-sm font-medium cursor-pointer leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Confirmo que participei desta corrida
                </label>
                <p className="text-xs text-slate-500">
                  Apenas atletas que participaram podem avaliar
                </p>
              </div>
            </div>

            {/* Termo de Responsabilidade */}
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
              <h4 className="font-semibold text-red-800 dark:text-red-200 mb-2 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                {termoTexto?.titulo || "Termo de Responsabilidade"}
              </h4>
              <div className="max-h-32 overflow-y-auto text-xs text-red-700 dark:text-red-300 mb-3 space-y-1 pr-2">
                {(termoTexto?.texto || "Carregando...").split('\n').map((line, i) => {
                  if (line.startsWith('**') && line.endsWith('**')) {
                    return <p key={i} className="font-semibold">{line.replace(/\*\*/g, '')}</p>;
                  }
                  if (line.match(/^\d+\./)) {
                    return <p key={i} className="ml-2">{line}</p>;
                  }
                  return <p key={i}>{line}</p>;
                })}
              </div>
              
              <div className="flex items-start space-x-3 p-2 bg-white dark:bg-slate-900 rounded border border-red-300">
                <Checkbox
                  id="aceito_termo"
                  checked={avaliacaoData.aceito_termo}
                  onCheckedChange={(checked) => setAvaliacaoData({...avaliacaoData, aceito_termo: checked})}
                  className="mt-0.5 border-red-500 data-[state=checked]:bg-red-600"
                />
                <div className="grid gap-1 leading-none">
                  <label
                    htmlFor="aceito_termo"
                    className="text-sm font-medium cursor-pointer leading-none text-red-800 dark:text-red-200"
                  >
                    Li e aceito o termo de responsabilidade
                  </label>
                  <p className="text-xs text-red-600 dark:text-red-400">
                    Seu IP será registrado para fins de auditoria
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAvaliacaoModal(false)}>
              Cancelar
            </Button>
            <Button 
              onClick={handleEnviarAvaliacao} 
              disabled={avaliacaoLoading || !avaliacaoData.participei || !avaliacaoData.aceito_termo}
              className="bg-yellow-500 hover:bg-yellow-600 text-white"
              data-testid="enviar-avaliacao-btn"
            >
              {avaliacaoLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Enviando...
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  Enviar Avaliação
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RankingCorridasPage;
