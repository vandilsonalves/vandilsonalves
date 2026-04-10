import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Trophy, Check, Loader2, ExternalLink, Lock, Medal } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MEDAL_COLORS = ['from-amber-400 to-yellow-500', 'from-slate-300 to-slate-400', 'from-orange-600 to-orange-700'];

const VotacaoPage = () => {
  const { token, user } = useAuth();
  const [status, setStatus] = useState(null);
  const [categorias, setCategorias] = useState([]);
  const [meusVotos, setMeusVotos] = useState({});
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState(null);
  const [resultados, setResultados] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, catsRes] = await Promise.all([
        axios.get(`${API}/premiacao/status`),
        axios.get(`${API}/premiacao/categorias`)
      ]);
      setStatus(statusRes.data);
      setCategorias(catsRes.data);

      if (token) {
        const votosRes = await axios.get(`${API}/premiacao/meus-votos`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const votosMap = {};
        const formMap = {};
        votosRes.data.forEach(v => {
          votosMap[v.categoria_id] = v;
          formMap[v.categoria_id] = { nome: v.nome_indicado, link: v.link_indicado || '' };
        });
        setMeusVotos(votosMap);
        setFormData(formMap);
      }

      // Try to get results if voting is closed
      if (!statusRes.data.votacao_aberta) {
        try {
          const resRes = await axios.get(`${API}/premiacao/resultados-publicos`);
          setResultados(resRes.data);
        } catch {
          setResultados(null);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleVote = async (catId) => {
    const data = formData[catId];
    if (!data?.nome?.trim()) return toast.error('Preencha o nome do indicado');

    setVoting(catId);
    try {
      const res = await axios.post(`${API}/premiacao/votar`, {
        categoria_id: catId,
        nome_indicado: data.nome.trim(),
        link_indicado: data.link?.trim() || ''
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      toast.success(res.data.message);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro ao votar');
    } finally {
      setVoting(null);
    }
  };

  const updateForm = (catId, field, value) => {
    setFormData(prev => ({
      ...prev,
      [catId]: { ...(prev[catId] || {}), [field]: value }
    }));
  };

  const votedCount = Object.keys(meusVotos).length;
  const totalCats = categorias.length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-amber-500" />
      </div>
    );
  }

  // Results view (voting closed)
  if (resultados && !status?.votacao_aberta) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 p-4 sm:p-8" data-testid="resultados-premiacao">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <Trophy className="w-16 h-16 text-amber-500 mx-auto mb-3" />
            <h1 className="text-2xl sm:text-3xl font-bold text-amber-400">{resultados.titulo}</h1>
            <p className="text-slate-400">{resultados.subtitulo} - {resultados.ano}</p>
            <Badge className="bg-red-500/20 text-red-400 mt-2">Votação Encerrada</Badge>
          </div>

          <div className="space-y-6">
            {resultados.resultados?.map((res) => (
              <Card key={res.categoria.id} className="bg-slate-800/80 border-slate-700 overflow-hidden">
                <div className="bg-amber-500/10 px-4 py-3 border-b border-slate-700">
                  <h3 className="font-bold text-amber-400 text-sm sm:text-base">{res.categoria.nome}</h3>
                  <p className="text-xs text-slate-500">{res.total_votos} votos totais</p>
                </div>
                <CardContent className="p-4 space-y-3">
                  {res.top3?.map((ind) => (
                    <div key={ind.posicao} className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${MEDAL_COLORS[ind.posicao - 1] || 'from-slate-500 to-slate-600'} flex items-center justify-center shrink-0`}>
                        <span className="text-white font-bold text-sm">{ind.posicao}°</span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-white font-semibold truncate">{ind.nome}</p>
                        {ind.link && (
                          <a href={ind.link.startsWith('http') ? ind.link : `https://instagram.com/${ind.link.replace('@','')}`} 
                             target="_blank" rel="noopener noreferrer"
                             className="text-xs text-blue-400 hover:underline flex items-center gap-1">
                            <ExternalLink className="w-3 h-3" />{ind.link}
                          </a>
                        )}
                      </div>
                      <Badge className="bg-amber-500/20 text-amber-400 shrink-0">{ind.votos} votos</Badge>
                    </div>
                  ))}
                  {(!res.top3 || res.top3.length === 0) && (
                    <p className="text-slate-500 text-sm text-center">Nenhum voto registrado</p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Voting closed, no results yet
  if (!status?.votacao_aberta) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 flex items-center justify-center p-4" data-testid="votacao-fechada">
        <Card className="bg-slate-800/80 border-slate-700 max-w-md w-full text-center p-8">
          <Lock className="w-16 h-16 text-slate-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Votação Não Disponível</h2>
          <p className="text-slate-400 text-sm">A votação do Prêmio Nacional Ranking Run ainda não foi aberta ou já foi encerrada. Aguarde a próxima edição!</p>
        </Card>
      </div>
    );
  }

  // Voting open
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 p-4 sm:p-8" data-testid="votacao-aberta">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <Trophy className="w-14 h-14 text-amber-500 mx-auto mb-3" />
          <h1 className="text-2xl sm:text-3xl font-bold text-amber-400">{status.titulo}</h1>
          <p className="text-slate-400 text-sm sm:text-base">{status.subtitulo} - {status.ano}</p>
          <Badge className="bg-emerald-500/20 text-emerald-400 mt-3">Votação Aberta</Badge>
        </div>

        {/* Progress */}
        {token && totalCats > 0 && (
          <div className="mb-6 bg-slate-800/50 rounded-lg p-3 border border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-slate-400">Seu progresso</span>
              <span className="text-xs text-amber-400 font-medium">{votedCount}/{totalCats} categorias</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-amber-500 to-amber-400 h-2 rounded-full transition-all duration-500"
                style={{ width: `${totalCats > 0 ? (votedCount / totalCats * 100) : 0}%` }}
              />
            </div>
          </div>
        )}

        {/* Categories */}
        <div className="space-y-4">
          {categorias.map((cat, i) => {
            const jaVotou = !!meusVotos[cat.id];
            const form = formData[cat.id] || { nome: '', link: '' };

            return (
              <Card key={cat.id} className={`border transition-all ${jaVotou ? 'bg-emerald-900/20 border-emerald-700/50' : 'bg-slate-800/80 border-slate-700'}`}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="w-8 h-8 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-sm font-bold shrink-0">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-semibold text-sm sm:text-base truncate">{cat.nome}</h3>
                      {cat.descricao && <p className="text-slate-400 text-xs">{cat.descricao}</p>}
                    </div>
                    {jaVotou && <Check className="w-5 h-5 text-emerald-400 shrink-0" />}
                  </div>

                  {!token ? (
                    <p className="text-slate-500 text-sm text-center py-2">Faça login para votar</p>
                  ) : (
                    <div className="space-y-2">
                      <Input
                        placeholder="Nome do indicado"
                        value={form.nome}
                        onChange={e => updateForm(cat.id, 'nome', e.target.value)}
                        className="bg-slate-700/50 border-slate-600 text-white text-sm"
                        data-testid={`input-nome-${cat.id}`}
                      />
                      <Input
                        placeholder="Instagram ou site (opcional)"
                        value={form.link}
                        onChange={e => updateForm(cat.id, 'link', e.target.value)}
                        className="bg-slate-700/50 border-slate-600 text-white text-sm"
                        data-testid={`input-link-${cat.id}`}
                      />
                      <Button 
                        onClick={() => handleVote(cat.id)} 
                        disabled={voting === cat.id || !form.nome?.trim()}
                        className={`w-full text-sm ${jaVotou ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-amber-500 hover:bg-amber-600'}`}
                        data-testid={`btn-votar-${cat.id}`}
                      >
                        {voting === cat.id ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : 
                         jaVotou ? <Check className="w-4 h-4 mr-2" /> : <Medal className="w-4 h-4 mr-2" />}
                        {jaVotou ? 'Alterar Indicação' : 'Indicar e Votar'}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {categorias.length === 0 && (
          <Card className="bg-slate-800/50 border-slate-700 p-8 text-center">
            <Trophy className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">As categorias de votação serão publicadas em breve!</p>
          </Card>
        )}
      </div>
    </div>
  );
};

export default VotacaoPage;
