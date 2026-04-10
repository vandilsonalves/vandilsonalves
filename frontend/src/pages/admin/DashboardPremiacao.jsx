import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Trophy, Plus, Trash2, Edit2, Play, Square, BarChart3, 
  Loader2, Users, Medal, Eye, Merge, ExternalLink, RefreshCw, Calendar, Save
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ICONE_MAP = {
  trophy: Trophy,
  medal: Medal,
  users: Users,
  star: Trophy
};

const DashboardPremiacao = ({ token }) => {
  const [config, setConfig] = useState(null);
  const [categorias, setCategorias] = useState([]);
  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddCat, setShowAddCat] = useState(false);
  const [showResultados, setShowResultados] = useState(false);
  const [showConsolidar, setShowConsolidar] = useState(null);
  const [novaCat, setNovaCat] = useState({ nome: '', descricao: '' });
  const [consolidarNome, setConsolidarNome] = useState('');
  const [consolidarVariantes, setConsolidarVariantes] = useState('');
  const [dataLimite, setDataLimite] = useState('');
  const [savingConfig, setSavingConfig] = useState(false);
  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [configRes, catsRes] = await Promise.all([
        axios.get(`${API}/premiacao/admin/config`, { headers }),
        axios.get(`${API}/premiacao/admin/categorias`, { headers })
      ]);
      setConfig(configRes.data);
      setCategorias(catsRes.data);
      if (configRes.data?.data_limite) {
        setDataLimite(configRes.data.data_limite.slice(0, 16));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const saveDataLimite = async () => {
    if (!dataLimite) return toast.error('Selecione uma data limite');
    setSavingConfig(true);
    try {
      await axios.put(`${API}/premiacao/admin/config`, { data_limite: new Date(dataLimite).toISOString() }, { headers });
      toast.success('Data limite salva!');
      fetchData();
    } catch (err) {
      toast.error('Erro ao salvar data');
    } finally {
      setSavingConfig(false);
    }
  };

  const toggleVotacao = async () => {
    try {
      const endpoint = config?.votacao_aberta ? 'fechar' : 'abrir';
      await axios.post(`${API}/premiacao/admin/${endpoint}`, {}, { headers });
      toast.success(config?.votacao_aberta ? 'Votação encerrada!' : 'Votação aberta!');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro');
    }
  };

  const addCategoria = async () => {
    if (!novaCat.nome.trim()) return toast.error('Nome da categoria obrigatório');
    try {
      await axios.post(`${API}/premiacao/admin/categorias`, novaCat, { headers });
      toast.success('Categoria criada!');
      setShowAddCat(false);
      setNovaCat({ nome: '', descricao: '' });
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro');
    }
  };

  const deleteCategoria = async (id) => {
    if (!window.confirm('Excluir categoria e todos os votos?')) return;
    try {
      await axios.delete(`${API}/premiacao/admin/categorias/${id}`, { headers });
      toast.success('Categoria excluída');
      fetchData();
    } catch (err) {
      toast.error('Erro ao excluir');
    }
  };

  const fetchResultados = async () => {
    try {
      const res = await axios.get(`${API}/premiacao/admin/resultados`, { headers });
      setResultados(res.data);
      setShowResultados(true);
    } catch (err) {
      toast.error('Erro ao buscar resultados');
    }
  };

  const handleConsolidar = async (catId) => {
    if (!consolidarNome.trim() || !consolidarVariantes.trim()) return toast.error('Preencha todos os campos');
    const variantes = consolidarVariantes.split(',').map(v => v.trim()).filter(Boolean);
    try {
      const res = await axios.post(`${API}/premiacao/admin/consolidar/${catId}`, {
        nome_principal: consolidarNome.trim(),
        nomes_variantes: variantes
      }, { headers });
      toast.success(res.data.message);
      setShowConsolidar(null);
      setConsolidarNome('');
      setConsolidarVariantes('');
      fetchResultados();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro');
    }
  };

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-amber-500" /></div>;

  return (
    <div className="space-y-6" data-testid="dashboard-premiacao">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-amber-500">{config?.titulo || 'Premiação'}</h2>
          <p className="text-slate-400 text-sm">{config?.subtitulo} - {config?.ano}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={toggleVotacao}
            className={config?.votacao_aberta 
              ? 'bg-red-600 hover:bg-red-700' 
              : 'bg-emerald-600 hover:bg-emerald-700'
            }
            data-testid="btn-toggle-votacao"
          >
            {config?.votacao_aberta ? <Square className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
            {config?.votacao_aberta ? 'Encerrar Votação' : 'Abrir Votação'}
          </Button>
          <Button onClick={fetchResultados} variant="outline" className="border-amber-500 text-amber-500 hover:bg-amber-500/10">
            <BarChart3 className="w-4 h-4 mr-2" /> Resultados
          </Button>
          <Button onClick={() => fetchData()} variant="ghost" size="icon"><RefreshCw className="w-4 h-4" /></Button>
        </div>
      </div>

      {/* Status */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4 flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <Badge className={`${config?.votacao_aberta ? 'bg-emerald-500' : 'bg-red-500'} text-white px-3 py-1`}>
            {config?.votacao_aberta ? 'VOTAÇÃO ABERTA' : 'VOTAÇÃO FECHADA'}
          </Badge>
          {config?.data_abertura && (
            <span className="text-xs text-slate-400">
              Aberta em: {new Date(config.data_abertura).toLocaleString('pt-BR')}
            </span>
          )}
          {config?.data_encerramento && !config?.votacao_aberta && (
            <span className="text-xs text-slate-400">
              Encerrada em: {new Date(config.data_encerramento).toLocaleString('pt-BR')}
            </span>
          )}
        </CardContent>
      </Card>

      {/* Data Limite */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row sm:items-end gap-3">
            <div className="flex-1">
              <Label className="text-slate-300 flex items-center gap-2 mb-2">
                <Calendar className="w-4 h-4 text-amber-500" /> Data Limite da Votação
              </Label>
              <Input
                type="datetime-local"
                value={dataLimite}
                onChange={e => setDataLimite(e.target.value)}
                className="bg-slate-700/50 border-slate-600 text-white max-w-xs"
                data-testid="input-data-limite"
              />
            </div>
            <Button
              onClick={saveDataLimite}
              disabled={savingConfig}
              className="bg-amber-500 hover:bg-amber-600 shrink-0"
              data-testid="btn-salvar-data-limite"
            >
              {savingConfig ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
              Salvar Data Limite
            </Button>
          </div>
          {config?.data_limite && (
            <p className="text-xs text-slate-400 mt-2">
              Encerramento programado: {new Date(config.data_limite).toLocaleString('pt-BR')}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Categorias */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <CardTitle className="text-white flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500" /> Categorias de Votação
            </CardTitle>
            <Button onClick={() => setShowAddCat(true)} size="sm" className="bg-amber-500 hover:bg-amber-600 w-full sm:w-auto">
              <Plus className="w-4 h-4 mr-2" /> Nova Categoria
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {categorias.length === 0 ? (
            <p className="text-slate-400 text-center py-6">Nenhuma categoria criada. Clique em "Nova Categoria" para começar.</p>
          ) : categorias.map((cat, i) => (
            <div key={cat.id} className="flex items-center justify-between gap-3 p-3 bg-slate-700/50 rounded-lg">
              <div className="flex items-center gap-3 min-w-0">
                <span className="w-8 h-8 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-sm font-bold shrink-0">
                  {i + 1}
                </span>
                <div className="min-w-0">
                  <p className="text-white font-medium truncate">{cat.nome}</p>
                  {cat.descricao && <p className="text-slate-400 text-xs truncate">{cat.descricao}</p>}
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Badge variant="secondary" className="text-xs">{cat.total_votos || 0} votos</Badge>
                <Button onClick={() => deleteCategoria(cat.id)} size="icon" variant="ghost" className="text-red-400 hover:text-red-300 h-8 w-8">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Modal Nova Categoria */}
      <Dialog open={showAddCat} onOpenChange={setShowAddCat}>
        <DialogContent className="max-w-md w-[95vw]">
          <DialogHeader>
            <DialogTitle>Nova Categoria de Votação</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nome da Categoria</Label>
              <Input 
                value={novaCat.nome} 
                onChange={e => setNovaCat({...novaCat, nome: e.target.value})}
                placeholder="Ex: Treinador do Ano"
                data-testid="input-cat-nome"
              />
            </div>
            <div>
              <Label>Descrição (opcional)</Label>
              <Input 
                value={novaCat.descricao} 
                onChange={e => setNovaCat({...novaCat, descricao: e.target.value})}
                placeholder="Ex: Vote no melhor treinador de corrida de rua"
              />
            </div>
            <Button onClick={addCategoria} className="w-full bg-amber-500 hover:bg-amber-600" data-testid="btn-salvar-categoria">
              Criar Categoria
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal Resultados */}
      <Dialog open={showResultados} onOpenChange={setShowResultados}>
        <DialogContent className="max-w-3xl w-[95vw] max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-amber-500">
              <BarChart3 className="w-5 h-5" /> Resultados da Votação
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-6">
            {resultados.map((res) => (
              <Card key={res.categoria.id} className="bg-slate-50 dark:bg-slate-800 border-0">
                <CardHeader className="pb-2">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <CardTitle className="text-base text-amber-600">{res.categoria.nome}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge>{res.total_votos} votos</Badge>
                      <Button 
                        size="sm" variant="ghost" 
                        onClick={() => { setShowConsolidar(res.categoria.id); setConsolidarNome(''); setConsolidarVariantes(''); }}
                        title="Consolidar nomes"
                      >
                        <Merge className="w-3 h-3 mr-1" /> Consolidar
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {res.indicados.length === 0 ? (
                    <p className="text-slate-400 text-sm">Nenhum voto ainda</p>
                  ) : (
                    <div className="space-y-2">
                      {res.indicados.map((ind, idx) => (
                        <div key={idx} className="flex items-center justify-between gap-2 p-2 bg-white dark:bg-slate-700 rounded-lg">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                              idx === 0 ? 'bg-amber-500 text-white' :
                              idx === 1 ? 'bg-slate-300 text-slate-700' :
                              idx === 2 ? 'bg-orange-700 text-white' :
                              'bg-slate-200 text-slate-600'
                            }`}>{idx + 1}</span>
                            <div className="min-w-0">
                              <p className="font-medium text-sm truncate">{ind.nome}</p>
                              {ind.link && (
                                <a href={ind.link.startsWith('http') ? ind.link : `https://instagram.com/${ind.link.replace('@','')}`} 
                                   target="_blank" rel="noopener noreferrer" 
                                   className="text-xs text-blue-500 hover:underline flex items-center gap-1">
                                  <ExternalLink className="w-3 h-3" />{ind.link}
                                </a>
                              )}
                            </div>
                          </div>
                          <Badge className="bg-amber-500/20 text-amber-600 shrink-0">{ind.votos} votos</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal Consolidar */}
      <Dialog open={!!showConsolidar} onOpenChange={() => setShowConsolidar(null)}>
        <DialogContent className="max-w-md w-[95vw]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Merge className="w-5 h-5 text-amber-500" /> Consolidar Indicações
            </DialogTitle>
          </DialogHeader>
          <p className="text-sm text-slate-500">
            Junte variações do mesmo nome. Ex: "João Silva", "joao silva", "João S." → "João Silva"
          </p>
          <div className="space-y-4">
            <div>
              <Label>Nome principal (correto)</Label>
              <Input 
                value={consolidarNome} 
                onChange={e => setConsolidarNome(e.target.value)}
                placeholder="Ex: João Silva"
              />
            </div>
            <div>
              <Label>Variantes (separadas por vírgula)</Label>
              <Input 
                value={consolidarVariantes} 
                onChange={e => setConsolidarVariantes(e.target.value)}
                placeholder="Ex: joao silva, João S., J. Silva"
              />
            </div>
            <Button onClick={() => handleConsolidar(showConsolidar)} className="w-full bg-amber-500 hover:bg-amber-600">
              Consolidar Votos
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardPremiacao;
