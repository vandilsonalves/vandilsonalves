import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Trophy, Check, Loader2, ExternalLink, Lock, Medal, Clock, ArrowLeft, AlertTriangle, PartyPopper, ScrollText, Play } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const resolveUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `${BACKEND_URL}${url}`;
};

const VotacaoPage = () => {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [premiacoes, setPremiacoes] = useState([]);
  const [selectedPrem, setSelectedPrem] = useState(null);
  const [categorias, setCategorias] = useState([]);
  const [meusVotos, setMeusVotos] = useState({});
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [showWarning, setShowWarning] = useState(false);
  const [showParabens, setShowParabens] = useState(false);
  const [parabensVotos, setParabensVotos] = useState([]);
  const [votoFinalizado, setVotoFinalizado] = useState(false);
  const [finalizando, setFinalizando] = useState(false);
  const [showRegulamento, setShowRegulamento] = useState(false);
  const [regulamento, setRegulamento] = useState('');
  const [warningAccepted, setWarningAccepted] = useState(false);
  const [resultadosPublicos, setResultadosPublicos] = useState(null);

  const fetchPremiacoes = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/premiacao/todas`);
      setPremiacoes(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPremiacao = useCallback(async (premId) => {
    setLoading(true);
    try {
      const [premRes, catsRes] = await Promise.all([
        axios.get(`${API}/premiacao/p/${premId}`),
        axios.get(`${API}/premiacao/p/${premId}/categorias`)
      ]);
      setSelectedPrem(premRes.data);
      setCategorias(catsRes.data);
      setResultadosPublicos(null);

      // Se encerrada, buscar resultados públicos
      if (!premRes.data.votacao_aberta && premRes.data.data_encerramento) {
        try {
          const resPublicos = await axios.get(`${API}/premiacao/p/${premId}/resultados-publicos`);
          setResultadosPublicos(resPublicos.data);
        } catch { /* resultados não disponíveis */ }
      }

      if (token) {
        const [votosRes, finRes] = await Promise.all([
          axios.get(`${API}/premiacao/p/${premId}/meus-votos`, { headers: { Authorization: `Bearer ${token}` } }),
          axios.get(`${API}/premiacao/p/${premId}/voto-finalizado`, { headers: { Authorization: `Bearer ${token}` } })
        ]);
        const votosMap = {};
        const formMap = {};
        votosRes.data.forEach(v => {
          votosMap[v.categoria_id] = v;
          formMap[v.categoria_id] = { nome: v.nome_indicado, link: v.link_indicado || '' };
        });
        setMeusVotos(votosMap);
        setFormData(formMap);
        setVotoFinalizado(finRes.data.finalizado);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchPremiacoes(); }, [fetchPremiacoes]);

  // Countdown
  useEffect(() => {
    if (!selectedPrem?.data_limite || !selectedPrem?.votacao_aberta) { setCountdown(null); return; }
    const target = new Date(selectedPrem.data_limite).getTime();
    const tick = () => {
      const diff = target - Date.now();
      if (diff <= 0) { setCountdown({ dias: 0, horas: 0, minutos: 0, segundos: 0, expirado: true }); return; }
      setCountdown({
        dias: Math.floor(diff / 86400000),
        horas: Math.floor((diff % 86400000) / 3600000),
        minutos: Math.floor((diff % 3600000) / 60000),
        segundos: Math.floor((diff % 60000) / 1000),
        expirado: false
      });
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [selectedPrem?.data_limite, selectedPrem?.votacao_aberta]);

  const handleVote = async (catId) => {
    const data = formData[catId];
    if (!data?.nome?.trim()) return toast.error('Preencha o nome do indicado');
    if (selectedPrem?.modo_votacao === 'indicar' && !data?.link?.trim()) return toast.error('Preencha o Link do Site Oficial ou Instagram');

    // Se for o primeiro voto e ainda não aceitou o aviso
    if (!warningAccepted && Object.keys(meusVotos).length === 0) {
      setShowWarning(true);
      return;
    }

    setVoting(catId);
    try {
      await axios.post(`${API}/premiacao/p/${selectedPrem.id}/votar`, {
        premiacao_id: selectedPrem.id,
        categoria_id: catId,
        nome_indicado: data.nome.trim(),
        link_indicado: data.link?.trim() || ''
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Voto registrado!');
      fetchPremiacao(selectedPrem.id);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro ao votar');
    } finally {
      setVoting(null);
    }
  };

  const handleFinalizar = async () => {
    setFinalizando(true);
    try {
      const res = await axios.post(`${API}/premiacao/p/${selectedPrem.id}/finalizar`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setParabensVotos(res.data.votos || []);
      setShowParabens(true);
      setVotoFinalizado(true);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro ao finalizar');
    } finally {
      setFinalizando(false);
    }
  };

  const fetchRegulamento = async () => {
    try {
      const res = await axios.get(`${API}/premiacao/p/${selectedPrem.id}/regulamento`);
      setRegulamento(res.data.regulamento || 'Regulamento não disponível.');
      setShowRegulamento(true);
    } catch {
      toast.error('Erro ao carregar regulamento');
    }
  };

  const updateForm = (catId, field, value) => {
    setFormData(prev => ({ ...prev, [catId]: { ...(prev[catId] || {}), [field]: value } }));
  };

  const votedCount = Object.keys(meusVotos).length;
  const totalCats = categorias.length;
  const allVoted = totalCats > 0 && votedCount >= totalCats;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-amber-500" />
      </div>
    );
  }

  // ==================== LISTAGEM DE PREMIAÇÕES ====================
  if (!selectedPrem) {
    const ativas = premiacoes.filter(p => p.votacao_aberta);
    const encerradas = premiacoes.filter(p => !p.votacao_aberta && p.data_encerramento);

    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 p-4 sm:p-8" data-testid="premiacoes-lista">
        <div className="max-w-3xl mx-auto">
          <div className="mb-4">
            <Button onClick={() => navigate('/')} variant="ghost" className="text-slate-400 hover:text-white" data-testid="btn-voltar">
              <ArrowLeft className="w-4 h-4 mr-2" /> Voltar
            </Button>
          </div>

          <div className="text-center mb-8">
            <Trophy className="w-14 h-14 text-amber-500 mx-auto mb-3" />
            <h1 className="text-2xl sm:text-3xl font-bold text-amber-400">Premiações</h1>
            <p className="text-slate-400 text-sm">Vote e participe das premiações da plataforma</p>
          </div>

          {ativas.length > 0 && (
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-emerald-400 mb-3 flex items-center gap-2">
                <Play className="w-4 h-4" /> Votação Aberta
              </h2>
              <div className="space-y-3">
                {ativas.map(p => (
                  <Card key={p.id} className="bg-slate-800/80 border-emerald-700/50 hover:border-emerald-500/50 cursor-pointer transition-all" onClick={() => fetchPremiacao(p.id)} data-testid={`prem-card-${p.id}`}>
                    <CardContent className="p-4 flex items-center gap-4">
                      {p.foto_url ? <img src={resolveUrl(p.foto_url)} alt="" className="w-14 h-14 rounded-xl object-cover shrink-0" /> : (
                        <div className="w-14 h-14 rounded-xl bg-amber-500/10 flex items-center justify-center shrink-0"><Trophy className="w-6 h-6 text-amber-500" /></div>
                      )}
                      <div className="min-w-0 flex-1">
                        <h3 className="text-white font-semibold truncate">{p.titulo}</h3>
                        <p className="text-slate-400 text-xs">{p.subtitulo}</p>
                        <Badge className="bg-emerald-500/20 text-emerald-400 mt-1">Aberta</Badge>
                      </div>
                      <Medal className="w-5 h-5 text-amber-500 shrink-0" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {encerradas.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-slate-400 mb-3 flex items-center gap-2">
                <Lock className="w-4 h-4" /> Encerradas
              </h2>
              <div className="space-y-3">
                {encerradas.map(p => (
                  <Card key={p.id} className="bg-slate-800/50 border-slate-700 hover:border-slate-600 cursor-pointer transition-all opacity-70" onClick={() => fetchPremiacao(p.id)} data-testid={`prem-encerrada-${p.id}`}>
                    <CardContent className="p-4 flex items-center gap-4">
                      {p.foto_url ? <img src={resolveUrl(p.foto_url)} alt="" className="w-12 h-12 rounded-lg object-cover shrink-0" /> : (
                        <div className="w-12 h-12 rounded-lg bg-slate-700 flex items-center justify-center shrink-0"><Trophy className="w-5 h-5 text-slate-500" /></div>
                      )}
                      <div className="min-w-0">
                        <h3 className="text-slate-300 font-medium truncate">{p.titulo}</h3>
                        <p className="text-slate-500 text-xs">{p.subtitulo}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {premiacoes.length === 0 && (
            <Card className="bg-slate-800/50 border-slate-700 p-8 text-center">
              <Trophy className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">Nenhuma premiação disponível no momento.</p>
            </Card>
          )}
        </div>
      </div>
    );
  }

  // ==================== DETALHE DA PREMIAÇÃO (VOTAÇÃO) ====================

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 p-4 sm:p-8" data-testid="votacao-aberta">
      <div className="max-w-2xl mx-auto">
        <div className="mb-4 flex items-center justify-between">
          <Button onClick={() => { setSelectedPrem(null); setWarningAccepted(false); }} variant="ghost" className="text-slate-400 hover:text-white" data-testid="btn-voltar">
            <ArrowLeft className="w-4 h-4 mr-2" /> Voltar
          </Button>
          {selectedPrem?.regulamento && (
            <Button onClick={fetchRegulamento} variant="ghost" className="text-blue-400 hover:text-blue-300" data-testid="btn-ver-regulamento">
              <ScrollText className="w-4 h-4 mr-2" /> Regulamento
            </Button>
          )}
        </div>

        {/* Header */}
        <div className="text-center mb-8">
          {selectedPrem?.foto_url && (
            <img src={resolveUrl(selectedPrem.foto_url)} alt="" className="w-24 h-24 rounded-2xl object-cover mx-auto mb-4 border-2 border-amber-500/50" />
          )}
          <Trophy className="w-14 h-14 text-amber-500 mx-auto mb-3" />
          <h1 className="text-2xl sm:text-3xl font-bold text-amber-400">{selectedPrem?.titulo}</h1>
          <p className="text-slate-400 text-sm sm:text-base">{selectedPrem?.subtitulo}</p>

          {selectedPrem?.votacao_aberta ? (
            <Badge className="bg-emerald-500/20 text-emerald-400 mt-3">Votação Aberta</Badge>
          ) : (
            <Badge className="bg-red-500/20 text-red-400 mt-3">Votação Encerrada</Badge>
          )}

          {votoFinalizado && (
            <div className="mt-3">
              <Badge className="bg-blue-500/20 text-blue-400">Sua votação foi finalizada</Badge>
            </div>
          )}

          {/* Countdown */}
          {countdown && !countdown.expirado && selectedPrem?.votacao_aberta && (
            <div className="mt-5 inline-flex items-center gap-2 bg-slate-800/80 border border-amber-500/30 rounded-xl px-5 py-3" data-testid="countdown-timer">
              <Clock className="w-4 h-4 text-amber-400" />
              <span className="text-xs text-slate-400 mr-1">Encerra em:</span>
              {[{ val: countdown.dias, label: 'd' }, { val: countdown.horas, label: 'h' }, { val: countdown.minutos, label: 'm' }, { val: countdown.segundos, label: 's' }].map((u, i) => (
                <span key={i} className="flex items-baseline gap-0.5">
                  <span className="text-xl font-bold text-white tabular-nums">{String(u.val).padStart(2, '0')}</span>
                  <span className="text-xs text-amber-400">{u.label}</span>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Not open - show results if available */}
        {!selectedPrem?.votacao_aberta && (
          resultadosPublicos ? (
            <div className="space-y-6" data-testid="resultados-historico">
              <div className="text-center mb-4">
                <Badge className="bg-slate-600/50 text-slate-300">Resultados Finais</Badge>
              </div>
              {resultadosPublicos.resultados?.map((res) => (
                <Card key={res.categoria.id} className="bg-slate-800/80 border-slate-700 overflow-hidden">
                  <div className="bg-amber-500/10 px-4 py-3 border-b border-slate-700">
                    <div className="flex items-center gap-3">
                      {res.categoria.foto_url && <img src={resolveUrl(res.categoria.foto_url)} alt="" className="w-8 h-8 rounded-lg object-cover" />}
                      <div>
                        <h3 className="font-bold text-amber-400 text-sm sm:text-base">{res.categoria.nome}</h3>
                        <p className="text-xs text-slate-500">{res.total_votos} votos</p>
                      </div>
                    </div>
                  </div>
                  <CardContent className="p-4">
                    {res.top3?.length > 0 ? (
                      <div className="space-y-3">
                        {res.top3.map((ind) => {
                          const medalColors = ['from-amber-400 to-yellow-500', 'from-slate-300 to-slate-400', 'from-orange-600 to-orange-700'];
                          return (
                            <div key={ind.posicao} className="flex items-center gap-3">
                              <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${medalColors[ind.posicao - 1] || 'from-slate-500 to-slate-600'} flex items-center justify-center shrink-0 ${ind.posicao === 1 ? 'ring-2 ring-amber-400/50 ring-offset-2 ring-offset-slate-800' : ''}`}>
                                <span className="text-white font-bold text-sm">{ind.posicao}°</span>
                              </div>
                              <div className="min-w-0 flex-1">
                                <p className={`font-semibold truncate ${ind.posicao === 1 ? 'text-amber-400 text-base' : 'text-white text-sm'}`}>{ind.nome}</p>
                                {ind.link && (
                                  <a href={ind.link.startsWith('http') ? ind.link : `https://instagram.com/${ind.link.replace('@','')}`}
                                     target="_blank" rel="noopener noreferrer"
                                     className="text-xs text-blue-400 hover:underline flex items-center gap-1">
                                    <ExternalLink className="w-3 h-3" />{ind.link}
                                  </a>
                                )}
                              </div>
                              <Badge className={`shrink-0 ${ind.posicao === 1 ? 'bg-amber-500 text-white' : 'bg-amber-500/20 text-amber-400'}`}>{ind.votos} votos</Badge>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-slate-500 text-sm text-center">Nenhum voto registrado</p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="bg-slate-800/80 border-slate-700 text-center p-8">
              <Lock className="w-16 h-16 text-slate-500 mx-auto mb-4" />
              <p className="text-slate-400">Esta votação foi encerrada ou ainda não foi aberta.</p>
            </Card>
          )
        )}

        {/* Voting open */}
        {selectedPrem?.votacao_aberta && (
          <>
            {/* Progress */}
            {token && totalCats > 0 && (
              <div className="mb-6 bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-slate-400">Seu progresso</span>
                  <span className="text-xs text-amber-400 font-medium">{votedCount}/{totalCats}</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-amber-500 to-amber-400 h-2 rounded-full transition-all duration-500" style={{ width: `${totalCats > 0 ? (votedCount / totalCats * 100) : 0}%` }} />
                </div>
              </div>
            )}

            {/* Categories */}
            <div className="space-y-4">
              {categorias.map((cat, i) => {
                const jaVotou = !!meusVotos[cat.id];
                const form = formData[cat.id] || { nome: '', link: '' };
                const isIndicar = selectedPrem?.modo_votacao === 'indicar';
                const disabled = votoFinalizado;

                return (
                  <Card key={cat.id} className={`border transition-all ${jaVotou ? 'bg-emerald-900/20 border-emerald-700/50' : 'bg-slate-800/80 border-slate-700'}`}>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3 mb-3">
                        {cat.foto_url ? (
                          <img src={resolveUrl(cat.foto_url)} alt="" className="w-10 h-10 rounded-lg object-cover shrink-0" />
                        ) : (
                          <span className="w-8 h-8 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-sm font-bold shrink-0">{i+1}</span>
                        )}
                        <div className="flex-1 min-w-0">
                          <h3 className="text-white font-semibold text-sm sm:text-base truncate">{cat.nome}</h3>
                          {cat.descricao && <p className="text-slate-400 text-xs">{cat.descricao}</p>}
                        </div>
                        {jaVotou && <Check className="w-5 h-5 text-emerald-400 shrink-0" />}
                      </div>

                      {!token ? (
                        <p className="text-slate-500 text-sm text-center py-2">Faça login para votar</p>
                      ) : disabled ? (
                        <div className="text-center py-2">
                          <p className="text-slate-400 text-sm">
                            {jaVotou ? `Seu voto: ${meusVotos[cat.id]?.nome_indicado}` : 'Não votado'}
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          {/* Modo INDICAR: campos de texto */}
                          {isIndicar && (
                            <>
                              <Input
                                placeholder="Nome do indicado *"
                                value={form.nome}
                                onChange={e => updateForm(cat.id, 'nome', e.target.value)}
                                className="bg-slate-700/50 border-slate-600 text-white text-sm"
                                data-testid={`input-nome-${cat.id}`}
                              />
                              <Input
                                placeholder="Link do Site Oficial ou Instagram *"
                                value={form.link}
                                onChange={e => updateForm(cat.id, 'link', e.target.value)}
                                className="bg-slate-700/50 border-slate-600 text-white text-sm"
                                data-testid={`input-link-${cat.id}`}
                              />
                              <Button
                                onClick={() => handleVote(cat.id)}
                                disabled={voting === cat.id || !form.nome?.trim() || !form.link?.trim()}
                                className={`w-full text-sm ${jaVotou ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-amber-500 hover:bg-amber-600'}`}
                                data-testid={`btn-votar-${cat.id}`}
                              >
                                {voting === cat.id ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : jaVotou ? <Check className="w-4 h-4 mr-2" /> : <Medal className="w-4 h-4 mr-2" />}
                                {jaVotou ? 'Alterar Indicação' : 'Indicar e Votar'}
                              </Button>
                            </>
                          )}

                          {/* Modo VOTAR: opções para clicar */}
                          {!isIndicar && cat.opcoes?.length > 0 && (
                            <div className="space-y-2">
                              {cat.opcoes.map((opcao, idx) => {
                                const opcaoTexto = typeof opcao === 'string' ? opcao : opcao.texto;
                                const opcaoFoto = typeof opcao === 'object' ? opcao.foto_url : null;
                                const selecionada = form.nome === opcaoTexto;
                                return (
                                  <button
                                    key={idx}
                                    onClick={() => updateForm(cat.id, 'nome', opcaoTexto)}
                                    className={`w-full flex items-center gap-3 p-3 rounded-lg border text-left transition-all ${
                                      selecionada
                                        ? 'border-amber-500 bg-amber-500/10 text-white'
                                        : 'border-slate-600 bg-slate-700/30 text-slate-300 hover:border-slate-500 hover:bg-slate-700/50'
                                    }`}
                                    data-testid={`opcao-${cat.id}-${idx}`}
                                  >
                                    {opcaoFoto ? (
                                      <img src={resolveUrl(opcaoFoto)} alt="" className="w-10 h-10 rounded-lg object-cover shrink-0 border border-slate-600" />
                                    ) : (
                                      <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                                        selecionada ? 'bg-amber-500 text-white' : 'bg-slate-600 text-slate-300'
                                      }`}>
                                        {String.fromCharCode(65 + idx)}
                                      </span>
                                    )}
                                    <span className="text-sm font-medium">{opcaoTexto}</span>
                                    {selecionada && <Check className="w-4 h-4 text-amber-400 ml-auto shrink-0" />}
                                  </button>
                                );
                              })}
                              <Button
                                onClick={() => handleVote(cat.id)}
                                disabled={voting === cat.id || !form.nome?.trim()}
                                className={`w-full text-sm mt-1 ${jaVotou ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-amber-500 hover:bg-amber-600'}`}
                                data-testid={`btn-votar-${cat.id}`}
                              >
                                {voting === cat.id ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : jaVotou ? <Check className="w-4 h-4 mr-2" /> : <Medal className="w-4 h-4 mr-2" />}
                                {jaVotou ? 'Alterar Voto' : 'Confirmar Voto'}
                              </Button>
                            </div>
                          )}

                          {/* Modo VOTAR sem opções */}
                          {!isIndicar && (!cat.opcoes || cat.opcoes.length === 0) && (
                            <>
                              <Input
                                placeholder="Nome do indicado *"
                                value={form.nome}
                                onChange={e => updateForm(cat.id, 'nome', e.target.value)}
                                className="bg-slate-700/50 border-slate-600 text-white text-sm"
                                data-testid={`input-nome-${cat.id}`}
                              />
                              <Button
                                onClick={() => handleVote(cat.id)}
                                disabled={voting === cat.id || !form.nome?.trim()}
                                className={`w-full text-sm ${jaVotou ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-amber-500 hover:bg-amber-600'}`}
                                data-testid={`btn-votar-${cat.id}`}
                              >
                                {voting === cat.id ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : jaVotou ? <Check className="w-4 h-4 mr-2" /> : <Medal className="w-4 h-4 mr-2" />}
                                {jaVotou ? 'Alterar Voto' : 'Votar'}
                              </Button>
                            </>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Finalizar Votação */}
            {token && allVoted && !votoFinalizado && (
              <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-center">
                <p className="text-amber-400 text-sm mb-3">
                  Você votou em todas as categorias! Clique abaixo para finalizar sua votação.
                </p>
                <p className="text-red-400 text-xs mb-4 font-medium">
                  Atenção: Após finalizar, você NÃO poderá mais alterar seus votos.
                </p>
                <Button onClick={handleFinalizar} disabled={finalizando} className="bg-amber-500 hover:bg-amber-600" data-testid="btn-finalizar-votacao">
                  {finalizando ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Check className="w-4 h-4 mr-2" />}
                  Finalizar Votação
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Modal Advertência (Splash Warning) */}
      <Dialog open={showWarning} onOpenChange={setShowWarning}>
        <DialogContent className="max-w-md w-[95vw] text-center" data-testid="splash-warning">
          <div className="py-4">
            <div className="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-amber-500" />
            </div>
            <h2 className="text-xl font-bold text-white mb-3">Atenção!</h2>
            <div className="space-y-3 text-sm text-slate-300">
              <p>Após indicar <strong>todas</strong> as categorias e clicar em "Finalizar Votação", <strong>não será mais possível editar</strong> seus votos.</p>
              <p>Você só pode votar <strong>uma única vez</strong> em cada premiação. Preste atenção nas suas escolhas!</p>
              <p className="text-amber-400 font-medium">Revise com cuidado antes de finalizar.</p>
            </div>
            <div className="flex gap-3 mt-6">
              <Button onClick={() => setShowWarning(false)} variant="outline" className="flex-1">Cancelar</Button>
              <Button onClick={() => { setWarningAccepted(true); setShowWarning(false); }} className="flex-1 bg-amber-500 hover:bg-amber-600" data-testid="btn-aceitar-aviso">
                Entendi, continuar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal Parabéns (Splash Animado) */}
      <Dialog open={showParabens} onOpenChange={setShowParabens}>
        <DialogContent className="max-w-lg w-[95vw] text-center overflow-y-auto max-h-[85vh]" data-testid="splash-parabens">
          <div className="py-4">
            <div className="w-20 h-20 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
              <PartyPopper className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-amber-400 mb-2">Parabéns!</h2>
            <p className="text-slate-300 text-sm mb-4">Sua votação foi registrada com sucesso! Confira o resumo abaixo:</p>
            <div className="space-y-2 text-left mb-4">
              {parabensVotos.map((v, i) => (
                <div key={i} className="flex items-center gap-2 p-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  <Medal className="w-4 h-4 text-amber-500 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-xs text-slate-500">{v.categoria}</p>
                    <p className="text-sm font-medium text-white truncate">{v.indicado}</p>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500 mb-4">Um email com o resumo da sua votação foi enviado para sua caixa de entrada. Verifique também suas notificações no app.</p>
            <Button onClick={() => { setShowParabens(false); navigate('/'); }} className="w-full bg-amber-500 hover:bg-amber-600" data-testid="btn-fechar-parabens">
              Fechar
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal Regulamento */}
      <Dialog open={showRegulamento} onOpenChange={setShowRegulamento}>
        <DialogContent className="max-w-2xl w-[95vw] max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-blue-500">
              <ScrollText className="w-5 h-5" /> Regulamento
            </DialogTitle>
          </DialogHeader>
          <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap text-sm text-slate-300">
            {regulamento || 'Regulamento não disponível.'}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default VotacaoPage;
