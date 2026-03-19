// /app/frontend/src/pages/RivaisPage.jsx
// Página do Sistema de Rivais

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { 
  Swords, Trophy, Users, MapPin, TrendingUp, TrendingDown, Minus,
  UserPlus, Check, X, Loader2, Target, Medal, ArrowLeft, Sparkles, Search
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RivaisPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [rivais, setRivais] = useState([]);
  const [pendentes, setPendentes] = useState({ recebidas: [], enviadas: [] });
  const [sugestoes, setSugestoes] = useState([]);
  const [duelos, setDuelos] = useState([]);
  const [activeTab, setActiveTab] = useState('rivais');
  
  // Modal de solicitar rival
  const [showSolicitarModal, setShowSolicitarModal] = useState(false);
  const [atletaSelecionado, setAtletaSelecionado] = useState(null);
  const [mensagemRival, setMensagemRival] = useState('');
  const [enviando, setEnviando] = useState(false);
  
  // Busca de atletas
  const [busca, setBusca] = useState('');
  const [resultadosBusca, setResultadosBusca] = useState([]);
  const [buscando, setBuscando] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchDados();
  }, [user]);

  const fetchDados = async () => {
    setLoading(true);
    try {
      const [rivaisRes, pendentesRes, sugestoesRes, duelosRes] = await Promise.all([
        axios.get(`${API}/rivais/meus`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/rivais/pendentes`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/rivais/sugestoes`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/rivais/ranking-duelos`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      setRivais(rivaisRes.data.rivais || []);
      setPendentes(pendentesRes.data || { recebidas: [], enviadas: [] });
      setSugestoes(sugestoesRes.data.sugestoes || []);
      setDuelos(duelosRes.data.duelos || []);
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
      toast.error('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const buscarAtletas = async () => {
    if (!busca.trim() || busca.length < 3) return;
    
    setBuscando(true);
    try {
      const response = await axios.get(`${API}/atletas/buscar?nome=${encodeURIComponent(busca)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResultadosBusca(response.data.atletas || []);
    } catch (error) {
      console.error('Erro na busca:', error);
    } finally {
      setBuscando(false);
    }
  };

  const handleSolicitarRival = async () => {
    if (!atletaSelecionado) return;
    
    setEnviando(true);
    try {
      await axios.post(
        `${API}/rivais/solicitar`,
        { atleta_id: atletaSelecionado.id, mensagem: mensagemRival },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success(`Solicitação de rivalidade enviada para ${atletaSelecionado.nome}!`);
      setShowSolicitarModal(false);
      setAtletaSelecionado(null);
      setMensagemRival('');
      fetchDados();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao enviar solicitação');
    } finally {
      setEnviando(false);
    }
  };

  const handleAceitarRival = async (rivalidadeId) => {
    try {
      await axios.post(
        `${API}/rivais/aceitar/${rivalidadeId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Rivalidade aceita! A competição começou!');
      fetchDados();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao aceitar rivalidade');
    }
  };

  const handleRecusarRival = async (rivalidadeId) => {
    try {
      await axios.post(
        `${API}/rivais/recusar/${rivalidadeId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Solicitação recusada');
      fetchDados();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao recusar');
    }
  };

  const abrirModalSolicitar = (atleta) => {
    setAtletaSelecionado(atleta);
    setShowSolicitarModal(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button variant="ghost" onClick={() => navigate(-1)} className="text-slate-400">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center">
              <Swords className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Sistema de Rivais</h1>
              <p className="text-slate-400 text-sm">Desafie outros atletas e acompanhe sua performance</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-slate-800 border border-slate-700">
            <TabsTrigger value="rivais" className="data-[state=active]:bg-amber-500">
              <Swords className="w-4 h-4 mr-2" />
              Meus Rivais ({rivais.length})
            </TabsTrigger>
            <TabsTrigger value="pendentes" className="data-[state=active]:bg-amber-500">
              <UserPlus className="w-4 h-4 mr-2" />
              Pendentes ({pendentes.recebidas.length})
            </TabsTrigger>
            <TabsTrigger value="duelos" className="data-[state=active]:bg-amber-500">
              <Trophy className="w-4 h-4 mr-2" />
              Histórico de Duelos
            </TabsTrigger>
            <TabsTrigger value="buscar" className="data-[state=active]:bg-amber-500">
              <Search className="w-4 h-4 mr-2" />
              Buscar Rival
            </TabsTrigger>
          </TabsList>

          {/* Meus Rivais */}
          <TabsContent value="rivais" className="space-y-4">
            {rivais.length === 0 ? (
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-12 text-center">
                  <Swords className="w-16 h-16 mx-auto text-slate-600 mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Sem rivais ainda</h3>
                  <p className="text-slate-400 mb-4">
                    Desafie outros atletas e acompanhe quem está na frente na competição!
                  </p>
                  <Button onClick={() => setActiveTab('buscar')} className="bg-amber-500 hover:bg-amber-600">
                    <UserPlus className="w-4 h-4 mr-2" />
                    Buscar Rival
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {rivais.map((item) => (
                  <Card key={item.id} className="bg-slate-800 border-slate-700 hover:border-amber-500/50 transition-colors">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <Avatar className="w-16 h-16">
                          {item.rival.foto_url ? (
                            <AvatarImage src={item.rival.foto_url.startsWith('http') ? item.rival.foto_url : `${BACKEND_URL}${item.rival.foto_url}`} />
                          ) : null}
                          <AvatarFallback className="bg-amber-500 text-white text-xl">
                            {item.rival.nome?.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-white">{item.rival.nome}</h3>
                          <p className="text-sm text-slate-400 flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {item.rival.cidade}, {item.rival.estado}
                          </p>
                          {item.rival.equipe && (
                            <p className="text-sm text-amber-400">{item.rival.equipe}</p>
                          )}
                        </div>
                        
                        <div className="text-right">
                          <div className={`flex items-center gap-1 text-lg font-bold ${
                            item.status === 'ganhando' ? 'text-emerald-400' :
                            item.status === 'perdendo' ? 'text-red-400' : 'text-slate-400'
                          }`}>
                            {item.status === 'ganhando' ? <TrendingUp className="w-5 h-5" /> :
                             item.status === 'perdendo' ? <TrendingDown className="w-5 h-5" /> :
                             <Minus className="w-5 h-5" />}
                            {item.vantagem_pontos > 0 ? '+' : ''}{item.vantagem_pontos} pts
                          </div>
                          <Badge variant="outline" className={`mt-1 ${
                            item.status === 'ganhando' ? 'border-emerald-500 text-emerald-400' :
                            item.status === 'perdendo' ? 'border-red-500 text-red-400' :
                            'border-slate-500 text-slate-400'
                          }`}>
                            {item.status === 'ganhando' ? 'Você lidera!' :
                             item.status === 'perdendo' ? 'Atrás' : 'Empatados'}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {/* Sugestões */}
            {sugestoes.length > 0 && (
              <Card className="bg-slate-800 border-slate-700 mt-6">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-amber-500" />
                    Atletas com pontuação similar
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4 overflow-x-auto pb-2">
                    {sugestoes.map((atleta) => (
                      <div key={atleta.id} className="flex-shrink-0 bg-slate-700 rounded-lg p-4 w-48 text-center">
                        <Avatar className="w-12 h-12 mx-auto mb-2">
                          <AvatarFallback className="bg-amber-500 text-white">
                            {atleta.nome?.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <p className="text-white font-medium text-sm truncate">{atleta.nome}</p>
                        <p className="text-xs text-slate-400">{atleta.pontos_geral || 0} pts</p>
                        <Button 
                          size="sm" 
                          className="mt-2 w-full bg-amber-500 hover:bg-amber-600"
                          onClick={() => abrirModalSolicitar(atleta)}
                        >
                          <Swords className="w-3 h-3 mr-1" />
                          Desafiar
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Pendentes */}
          <TabsContent value="pendentes" className="space-y-6">
            {/* Recebidas */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Solicitações Recebidas</CardTitle>
              </CardHeader>
              <CardContent>
                {pendentes.recebidas.length === 0 ? (
                  <p className="text-slate-400 text-center py-8">Nenhuma solicitação pendente</p>
                ) : (
                  <div className="space-y-4">
                    {pendentes.recebidas.map((sol) => (
                      <div key={sol.id} className="flex items-center justify-between bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback className="bg-amber-500 text-white">
                              {sol.solicitante?.nome?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-white font-medium">{sol.solicitante?.nome}</p>
                            <p className="text-sm text-slate-400">{sol.mensagem || 'Quer ser seu rival!'}</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700" onClick={() => handleAceitarRival(sol.id)}>
                            <Check className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="outline" className="border-red-500 text-red-400" onClick={() => handleRecusarRival(sol.id)}>
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Enviadas */}
            {pendentes.enviadas.length > 0 && (
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Solicitações Enviadas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {pendentes.enviadas.map((sol) => (
                      <div key={sol.id} className="flex items-center justify-between bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback className="bg-slate-500 text-white">
                              {sol.destinatario?.nome?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-white font-medium">{sol.destinatario?.nome}</p>
                            <p className="text-sm text-slate-400">Aguardando resposta...</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="border-amber-500 text-amber-400">
                          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                          Pendente
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Histórico de Duelos */}
          <TabsContent value="duelos">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-amber-500" />
                  Confrontos Diretos
                </CardTitle>
              </CardHeader>
              <CardContent>
                {duelos.length === 0 ? (
                  <p className="text-slate-400 text-center py-8">
                    Você ainda não participou de corridas com seus rivais
                  </p>
                ) : (
                  <div className="space-y-4">
                    {duelos.map((duelo, index) => (
                      <div key={index} className="flex items-center justify-between bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback className="bg-amber-500 text-white">
                              {duelo.rival?.nome?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-white font-medium">{duelo.rival?.nome}</p>
                            <p className="text-sm text-slate-400">
                              {duelo.corridas_em_comum} corridas em comum
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-center">
                          <div>
                            <p className="text-2xl font-bold text-emerald-400">{duelo.vitorias}</p>
                            <p className="text-xs text-slate-400">Vitórias</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-slate-400">{duelo.empates}</p>
                            <p className="text-xs text-slate-400">Empates</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-red-400">{duelo.derrotas}</p>
                            <p className="text-xs text-slate-400">Derrotas</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Buscar Rival */}
          <TabsContent value="buscar">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Buscar Atleta para Desafiar</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Digite o nome do atleta..."
                    value={busca}
                    onChange={(e) => setBusca(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && buscarAtletas()}
                    className="bg-slate-700 border-slate-600"
                  />
                  <Button onClick={buscarAtletas} disabled={buscando || busca.length < 3}>
                    {buscando ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                  </Button>
                </div>

                {resultadosBusca.length > 0 && (
                  <div className="space-y-2">
                    {resultadosBusca.map((atleta) => (
                      <div key={atleta.id} className="flex items-center justify-between bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback className="bg-amber-500 text-white">
                              {atleta.nome?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-white font-medium">{atleta.nome}</p>
                            <p className="text-sm text-slate-400">
                              {atleta.cidade}, {atleta.estado} • {atleta.pontos_geral || 0} pts
                            </p>
                          </div>
                        </div>
                        <Button 
                          size="sm" 
                          className="bg-amber-500 hover:bg-amber-600"
                          onClick={() => abrirModalSolicitar(atleta)}
                        >
                          <Swords className="w-4 h-4 mr-1" />
                          Desafiar
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Modal de Solicitar Rival */}
      <Dialog open={showSolicitarModal} onOpenChange={setShowSolicitarModal}>
        <DialogContent className="bg-slate-800 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Swords className="w-5 h-5 text-amber-500" />
              Desafiar {atletaSelecionado?.nome}
            </DialogTitle>
            <DialogDescription className="text-slate-400">
              Envie uma mensagem de desafio para seu futuro rival!
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <Textarea
              placeholder="Ex: Vamos ver quem é o melhor nas próximas corridas!"
              value={mensagemRival}
              onChange={(e) => setMensagemRival(e.target.value)}
              rows={3}
              className="bg-slate-700 border-slate-600"
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSolicitarModal(false)}>
              Cancelar
            </Button>
            <Button 
              onClick={handleSolicitarRival} 
              disabled={enviando}
              className="bg-amber-500 hover:bg-amber-600"
            >
              {enviando ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Swords className="w-4 h-4 mr-2" />}
              Enviar Desafio
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RivaisPage;
