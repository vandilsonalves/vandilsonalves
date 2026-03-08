import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { 
  Trophy, Star, MapPin, Calendar, ExternalLink, Users, Award, 
  RefreshCw, Loader2, Plus, ArrowLeft, Home, LogOut, Filter,
  BarChart3, TrendingUp, Medal
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';

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
      if (tipo === 'cidade' && cidade) {
        url += `&cidade=${encodeURIComponent(cidade)}`;
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
      setEstados(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar estados:', error);
    }
  };

  const fetchCidades = async (uf) => {
    try {
      const response = await axios.get(`${API}/ranking-corridas/cidades?estado=${uf}`);
      setCidades(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
    }
  };

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
          </CardContent>
        </Card>

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
                      {estados.map(uf => (
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
                        {cidades.map(c => (
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
                <Select value={formData.estado} onValueChange={(v) => setFormData({...formData, estado: v})}>
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
                  value={formData.cidade}
                  onChange={(e) => setFormData({...formData, cidade: e.target.value})}
                  placeholder="Cidade"
                />
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
    </div>
  );
};

export default RankingCorridasPage;
