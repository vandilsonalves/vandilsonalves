import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Trophy, Plus, Trash2, Play, Square, BarChart3, 
  Loader2, Medal, Merge, ExternalLink, RefreshCw, 
  Calendar, Save, Download, Upload, Image as ImageIcon,
  ArrowLeft, ScrollText, Settings, Eye
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DashboardPremiacao = ({ token }) => {
  const [premiacoes, setPremiacoes] = useState([]);
  const [selected, setSelected] = useState(null); // premiacao selecionada
  const [categorias, setCategorias] = useState([]);
  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showAddCat, setShowAddCat] = useState(false);
  const [showResultados, setShowResultados] = useState(false);
  const [showConsolidar, setShowConsolidar] = useState(null);
  const [showRegulamento, setShowRegulamento] = useState(false);
  const [novaPrem, setNovaPrem] = useState({ titulo: '', subtitulo: '', modo_votacao: 'indicar', regulamento: '' });
  const [novaCat, setNovaCat] = useState({ nome: '', descricao: '', opcoes: [''] });
  const [consolidarNome, setConsolidarNome] = useState('');
  const [consolidarVariantes, setConsolidarVariantes] = useState('');
  const [editTitulo, setEditTitulo] = useState('');
  const [editSubtitulo, setEditSubtitulo] = useState('');
  const [editModo, setEditModo] = useState('indicar');
  const [editRegulamento, setEditRegulamento] = useState('');
  const [dataAbertura, setDataAbertura] = useState('');
  const [dataEncerramento, setDataEncerramento] = useState('');
  const [saving, setSaving] = useState(false);
  const [exportingExcel, setExportingExcel] = useState(false);
  const headers = { Authorization: `Bearer ${token}` };

  const fetchPremiacoes = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/premiacao/admin/premiacoes`, { headers });
      setPremiacoes(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchPremiacao = useCallback(async (premId) => {
    try {
      const [premRes, catsRes] = await Promise.all([
        axios.get(`${API}/premiacao/admin/premiacoes/${premId}`, { headers }),
        axios.get(`${API}/premiacao/admin/premiacoes/${premId}/categorias`, { headers })
      ]);
      setSelected(premRes.data);
      setCategorias(catsRes.data);
      setEditTitulo(premRes.data.titulo || '');
      setEditSubtitulo(premRes.data.subtitulo || '');
      setEditModo(premRes.data.modo_votacao || 'indicar');
      setEditRegulamento(premRes.data.regulamento || '');
      setDataAbertura(premRes.data.data_abertura_programada?.slice(0, 16) || '');
      setDataEncerramento(premRes.data.data_encerramento_programada?.slice(0, 16) || '');
    } catch (err) {
      toast.error('Erro ao carregar premiação');
    }
  }, [token]);

  useEffect(() => { fetchPremiacoes(); }, [fetchPremiacoes]);

  const createPremiacao = async () => {
    if (!novaPrem.titulo.trim()) return toast.error('Título é obrigatório');
    try {
      const res = await axios.post(`${API}/premiacao/admin/premiacoes`, novaPrem, { headers });
      toast.success('Premiação criada!');
      setShowCreate(false);
      setNovaPrem({ titulo: '', subtitulo: '', modo_votacao: 'indicar', regulamento: '' });
      fetchPremiacoes();
      fetchPremiacao(res.data.id);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro');
    }
  };

  const saveConfig = async () => {
    setSaving(true);
    try {
      const payload = {
        titulo: editTitulo,
        subtitulo: editSubtitulo,
        modo_votacao: editModo,
        regulamento: editRegulamento
      };
      if (dataAbertura) payload.data_abertura_programada = new Date(dataAbertura).toISOString();
      if (dataEncerramento) {
        payload.data_encerramento_programada = new Date(dataEncerramento).toISOString();
        payload.data_limite = new Date(dataEncerramento).toISOString();
      }
      await axios.put(`${API}/premiacao/admin/premiacoes/${selected.id}`, payload, { headers });
      toast.success('Configurações salvas!');
      fetchPremiacao(selected.id);
      fetchPremiacoes();
    } catch (err) {
      toast.error('Erro ao salvar');
    } finally {
      setSaving(false);
    }
  };

  const handleUploadFoto = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append('foto', file);
      await axios.post(`${API}/premiacao/admin/premiacoes/${selected.id}/foto`, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Foto atualizada!');
      fetchPremiacao(selected.id);
    } catch (err) {
      toast.error('Erro no upload');
    }
    e.target.value = '';
  };

  const handleUploadFotoCat = async (catId, e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append('foto', file);
      await axios.post(`${API}/premiacao/admin/premiacoes/${selected.id}/categorias/${catId}/foto`, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Foto da categoria atualizada!');
      fetchPremiacao(selected.id);
    } catch (err) {
      toast.error('Erro no upload');
    }
    e.target.value = '';
  };

  const toggleVotacao = async () => {
    try {
      const endpoint = selected?.votacao_aberta ? 'fechar' : 'abrir';
      await axios.post(`${API}/premiacao/admin/premiacoes/${selected.id}/${endpoint}`, {}, { headers });
      toast.success(selected?.votacao_aberta ? 'Votação encerrada!' : 'Votação aberta!');
      fetchPremiacao(selected.id);
      fetchPremiacoes();
    } catch (err) {
      toast.error('Erro');
    }
  };

  const addCategoria = async () => {
    if (!novaCat.nome.trim()) return toast.error('Nome obrigatório');
    const payload = { nome: novaCat.nome, descricao: novaCat.descricao };
    if (editModo === 'votar') {
      const opcoesFiltradas = (novaCat.opcoes || []).map(o => o.trim()).filter(Boolean);
      if (opcoesFiltradas.length < 2) return toast.error('Adicione pelo menos 2 opções para o modo "Votar"');
      payload.opcoes = opcoesFiltradas;
    }
    try {
      await axios.post(`${API}/premiacao/admin/premiacoes/${selected.id}/categorias`, payload, { headers });
      toast.success('Categoria criada!');
      setShowAddCat(false);
      setNovaCat({ nome: '', descricao: '', opcoes: [''] });
      fetchPremiacao(selected.id);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro');
    }
  };

  const deleteCategoria = async (catId) => {
    if (!window.confirm('Excluir categoria e todos os votos?')) return;
    try {
      await axios.delete(`${API}/premiacao/admin/premiacoes/${selected.id}/categorias/${catId}`, { headers });
      toast.success('Categoria excluída');
      fetchPremiacao(selected.id);
    } catch (err) {
      toast.error('Erro');
    }
  };

  const deletePremiacao = async (premId) => {
    if (!window.confirm('Excluir esta premiação e TODOS os votos? Esta ação não pode ser desfeita.')) return;
    try {
      await axios.delete(`${API}/premiacao/admin/premiacoes/${premId}`, { headers });
      toast.success('Premiação excluída');
      setSelected(null);
      fetchPremiacoes();
    } catch (err) {
      toast.error('Erro');
    }
  };

  const fetchResultados = async () => {
    try {
      const res = await axios.get(`${API}/premiacao/admin/premiacoes/${selected.id}/resultados`, { headers });
      setResultados(res.data);
      setShowResultados(true);
    } catch (err) {
      toast.error('Erro');
    }
  };

  const handleConsolidar = async (catId) => {
    if (!consolidarNome.trim() || !consolidarVariantes.trim()) return toast.error('Preencha todos os campos');
    try {
      const res = await axios.post(`${API}/premiacao/admin/premiacoes/${selected.id}/consolidar/${catId}`, {
        nome_principal: consolidarNome.trim(),
        nomes_variantes: consolidarVariantes.split(',').map(v => v.trim()).filter(Boolean)
      }, { headers });
      toast.success(res.data.message);
      setShowConsolidar(null);
      fetchResultados();
    } catch (err) {
      toast.error('Erro');
    }
  };

  const handleExportExcel = async () => {
    setExportingExcel(true);
    try {
      const res = await axios.get(`${API}/premiacao/admin/premiacoes/${selected.id}/exportar-excel`, {
        headers, responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `votos_${selected.titulo?.replace(/\s+/g,'_')}_${new Date().toISOString().slice(0,10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Excel exportado!');
    } catch (err) {
      toast.error('Erro ao exportar');
    } finally {
      setExportingExcel(false);
    }
  };

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-amber-500" /></div>;

  // ==================== LISTAGEM DE PREMIAÇÕES ====================
  if (!selected) {
    return (
      <div className="space-y-6" data-testid="dashboard-premiacao">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 className="text-xl sm:text-2xl font-bold text-amber-500 flex items-center gap-2">
            <Trophy className="w-6 h-6" /> Premiações
          </h2>
          <Button onClick={() => setShowCreate(true)} className="bg-amber-500 hover:bg-amber-600" data-testid="btn-nova-premiacao">
            <Plus className="w-4 h-4 mr-2" /> Nova Premiação
          </Button>
        </div>

        {premiacoes.length === 0 ? (
          <Card className="bg-slate-800 border-slate-700 p-12 text-center">
            <Trophy className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-lg text-slate-300 mb-2">Nenhuma premiação criada</h3>
            <p className="text-slate-500 text-sm mb-4">Crie sua primeira premiação para que os atletas possam votar</p>
            <Button onClick={() => setShowCreate(true)} className="bg-amber-500 hover:bg-amber-600">
              <Plus className="w-4 h-4 mr-2" /> Criar Premiação
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {premiacoes.map(p => (
              <Card key={p.id}
                className="bg-slate-800 border-slate-700 hover:border-amber-500/50 transition-all cursor-pointer group"
                onClick={() => fetchPremiacao(p.id)}
                data-testid={`premiacao-card-${p.id}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    {p.foto_url ? (
                      <img src={p.foto_url} alt="" className="w-14 h-14 rounded-lg object-cover shrink-0 border border-slate-600" />
                    ) : (
                      <div className="w-14 h-14 rounded-lg bg-amber-500/10 flex items-center justify-center shrink-0">
                        <Trophy className="w-6 h-6 text-amber-500" />
                      </div>
                    )}
                    <div className="min-w-0 flex-1">
                      <h3 className="text-white font-semibold truncate group-hover:text-amber-400 transition-colors">{p.titulo}</h3>
                      <p className="text-slate-400 text-xs truncate">{p.subtitulo}</p>
                      <div className="flex flex-wrap items-center gap-2 mt-2">
                        <Badge className={p.votacao_aberta ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-600/50 text-slate-400'}>
                          {p.votacao_aberta ? 'Aberta' : 'Fechada'}
                        </Badge>
                        <span className="text-xs text-slate-500">{p.total_categorias} categorias</span>
                        <span className="text-xs text-slate-500">{p.total_votos} votos</span>
                        <Badge variant="secondary" className="text-xs capitalize">{p.modo_votacao || 'indicar'}</Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Modal Criar Premiação */}
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogContent className="max-w-lg w-[95vw]">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-amber-500">
                <Trophy className="w-5 h-5" /> Nova Premiação
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Título da Premiação *</Label>
                <Input value={novaPrem.titulo} onChange={e => setNovaPrem({...novaPrem, titulo: e.target.value})} placeholder="Ex: PRÊMIO NACIONAL RANKING RUN" data-testid="input-prem-titulo" />
              </div>
              <div>
                <Label>Subtítulo</Label>
                <Input value={novaPrem.subtitulo} onChange={e => setNovaPrem({...novaPrem, subtitulo: e.target.value})} placeholder="Ex: Troféu Destaque Internet" />
              </div>
              <div>
                <Label>Modo de Votação</Label>
                <Select value={novaPrem.modo_votacao} onValueChange={v => setNovaPrem({...novaPrem, modo_votacao: v})}>
                  <SelectTrigger data-testid="select-modo-votacao">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="indicar">Indicar (texto livre — atleta escreve)</SelectItem>
                    <SelectItem value="votar">Votar (atleta escolhe uma opção)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={createPremiacao} className="w-full bg-amber-500 hover:bg-amber-600" data-testid="btn-criar-premiacao">Criar Premiação</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  // ==================== DETALHE DA PREMIAÇÃO ====================
  const totalVotos = categorias.reduce((s, c) => s + (c.total_votos || 0), 0);

  return (
    <div className="space-y-5" data-testid="premiacao-detalhe">
      {/* Voltar */}
      <Button onClick={() => { setSelected(null); fetchPremiacoes(); }} variant="ghost" className="text-slate-400 hover:text-white -ml-2" data-testid="btn-voltar-premiacoes">
        <ArrowLeft className="w-4 h-4 mr-2" /> Voltar às Premiações
      </Button>

      {/* Header editável */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Foto */}
            <div className="relative group shrink-0 self-start">
              {selected?.foto_url ? (
                <img src={selected.foto_url} alt="" className="w-20 h-20 rounded-xl object-cover border-2 border-amber-500/50" data-testid="foto-premiacao" />
              ) : (
                <div className="w-20 h-20 rounded-xl bg-slate-700 border-2 border-dashed border-slate-500 flex items-center justify-center">
                  <ImageIcon className="w-6 h-6 text-slate-500" />
                </div>
              )}
              <label className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                <Upload className="w-5 h-5 text-white" />
                <input type="file" accept="image/*" className="hidden" onChange={handleUploadFoto} data-testid="input-foto-premiacao" />
              </label>
            </div>

            <div className="flex-1 space-y-3 min-w-0">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs text-slate-400">Título</Label>
                  <Input value={editTitulo} onChange={e => setEditTitulo(e.target.value)} className="bg-slate-700/50 border-slate-600 text-white font-semibold" data-testid="input-edit-titulo" />
                </div>
                <div>
                  <Label className="text-xs text-slate-400">Subtítulo</Label>
                  <Input value={editSubtitulo} onChange={e => setEditSubtitulo(e.target.value)} className="bg-slate-700/50 border-slate-600 text-white" data-testid="input-edit-subtitulo" />
                </div>
              </div>
              <div>
                <Label className="text-xs text-slate-400">Modo de Votação</Label>
                <Select value={editModo} onValueChange={setEditModo}>
                  <SelectTrigger className="bg-slate-700/50 border-slate-600 text-white max-w-xs" data-testid="select-edit-modo">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="indicar">Indicar (texto livre)</SelectItem>
                    <SelectItem value="votar">Votar (escolher opção)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Ações */}
          <div className="flex flex-wrap gap-2 mt-4">
            <Button onClick={saveConfig} disabled={saving} className="bg-amber-500 hover:bg-amber-600" data-testid="btn-salvar-config">
              {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />} Salvar
            </Button>
            <Button onClick={toggleVotacao} className={selected?.votacao_aberta ? 'bg-red-600 hover:bg-red-700' : 'bg-emerald-600 hover:bg-emerald-700'} data-testid="btn-toggle-votacao">
              {selected?.votacao_aberta ? <Square className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
              {selected?.votacao_aberta ? 'Encerrar' : 'Abrir Votação'}
            </Button>
            <Button onClick={fetchResultados} variant="outline" className="border-amber-500 text-amber-500 hover:bg-amber-500/10">
              <BarChart3 className="w-4 h-4 mr-2" /> Resultados
            </Button>
            <Button onClick={handleExportExcel} disabled={exportingExcel} variant="outline" className="border-emerald-500 text-emerald-500 hover:bg-emerald-500/10" data-testid="btn-exportar-excel">
              {exportingExcel ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Download className="w-4 h-4 mr-2" />} Excel
            </Button>
            <Button onClick={() => setShowRegulamento(true)} variant="outline" className="border-blue-500 text-blue-500 hover:bg-blue-500/10" data-testid="btn-regulamento">
              <ScrollText className="w-4 h-4 mr-2" /> Regulamento
            </Button>
            <Button onClick={() => deletePremiacao(selected.id)} variant="ghost" className="text-red-400 hover:text-red-300 ml-auto">
              <Trash2 className="w-4 h-4 mr-2" /> Excluir
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Status + Datas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <Badge className={selected?.votacao_aberta ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'}>
                {selected?.votacao_aberta ? 'ABERTA' : 'FECHADA'}
              </Badge>
              <Badge variant="secondary">{totalVotos} votos</Badge>
              <Badge variant="secondary" className="capitalize">{selected?.modo_votacao || 'indicar'}</Badge>
            </div>
            {selected?.data_abertura && <p className="text-xs text-slate-400">Aberta: {new Date(selected.data_abertura).toLocaleString('pt-BR')}</p>}
            {selected?.data_encerramento && <p className="text-xs text-slate-400">Encerrada: {new Date(selected.data_encerramento).toLocaleString('pt-BR')}</p>}
          </CardContent>
        </Card>
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <Label className="text-slate-300 flex items-center gap-2 mb-3"><Calendar className="w-4 h-4 text-amber-500" /> Datas Programadas</Label>
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div>
                <Label className="text-xs text-slate-400">Abertura</Label>
                <Input type="datetime-local" value={dataAbertura} onChange={e => setDataAbertura(e.target.value)} className="bg-slate-700/50 border-slate-600 text-white text-xs" data-testid="input-data-abertura" />
              </div>
              <div>
                <Label className="text-xs text-slate-400">Encerramento</Label>
                <Input type="datetime-local" value={dataEncerramento} onChange={e => setDataEncerramento(e.target.value)} className="bg-slate-700/50 border-slate-600 text-white text-xs" data-testid="input-data-encerramento" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Categorias */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <CardTitle className="text-white flex items-center gap-2"><Trophy className="w-5 h-5 text-amber-500" /> Categorias</CardTitle>
            <Button onClick={() => setShowAddCat(true)} size="sm" className="bg-amber-500 hover:bg-amber-600 w-full sm:w-auto" data-testid="btn-nova-categoria">
              <Plus className="w-4 h-4 mr-2" /> Nova Categoria
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {categorias.length === 0 ? (
            <p className="text-slate-400 text-center py-6">Nenhuma categoria. Clique em "Nova Categoria" para começar.</p>
          ) : categorias.map((cat, i) => (
            <div key={cat.id} className="flex items-center gap-3 p-3 bg-slate-700/50 rounded-lg">
              {/* Foto da categoria */}
              <div className="relative group shrink-0">
                {cat.foto_url ? (
                  <img src={cat.foto_url} alt="" className="w-10 h-10 rounded-lg object-cover border border-slate-600" />
                ) : (
                  <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
                    <Medal className="w-5 h-5" />
                  </div>
                )}
                <label className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                  <Upload className="w-3 h-3 text-white" />
                  <input type="file" accept="image/*" className="hidden" onChange={e => handleUploadFotoCat(cat.id, e)} />
                </label>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium text-sm truncate">{cat.nome}</p>
                {cat.descricao && <p className="text-slate-400 text-xs truncate">{cat.descricao}</p>}
                {cat.opcoes?.length > 0 && (
                  <p className="text-amber-400/70 text-xs mt-0.5 truncate">
                    Opções: {cat.opcoes.map((o, i) => `${String.fromCharCode(65 + i)}) ${o}`).join(' · ')}
                  </p>
                )}
              </div>
              <Badge variant="secondary" className="text-xs shrink-0">{cat.total_votos || 0}</Badge>
              <Button onClick={() => deleteCategoria(cat.id)} size="icon" variant="ghost" className="text-red-400 hover:text-red-300 h-8 w-8 shrink-0">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Modal Nova Categoria */}
      <Dialog open={showAddCat} onOpenChange={setShowAddCat}>
        <DialogContent className="max-w-md w-[95vw] max-h-[85vh] overflow-y-auto">
          <DialogHeader><DialogTitle>Nova Categoria</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nome da Categoria *</Label>
              <Input value={novaCat.nome} onChange={e => setNovaCat({...novaCat, nome: e.target.value})} placeholder="Ex: Cor da Camisa" data-testid="input-cat-nome" />
            </div>
            <div>
              <Label>Descrição (opcional)</Label>
              <Input value={novaCat.descricao} onChange={e => setNovaCat({...novaCat, descricao: e.target.value})} placeholder="Ex: Escolha a cor da próxima corrida" />
            </div>

            {/* Opções para modo "Votar" */}
            {editModo === 'votar' && (
              <div>
                <Label className="mb-2 block">Opções de Votação</Label>
                <div className="space-y-2">
                  {(novaCat.opcoes || ['']).map((opcao, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <span className="w-7 h-7 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold shrink-0">
                        {String.fromCharCode(65 + idx)}
                      </span>
                      <Input
                        value={opcao}
                        onChange={e => {
                          const novas = [...(novaCat.opcoes || [''])];
                          novas[idx] = e.target.value;
                          setNovaCat({...novaCat, opcoes: novas});
                        }}
                        placeholder={`Opção ${String.fromCharCode(65 + idx)}`}
                        className="flex-1 bg-slate-50 dark:bg-slate-800 text-sm"
                        data-testid={`input-opcao-${idx}`}
                      />
                      {(novaCat.opcoes || []).length > 1 && (
                        <Button
                          type="button" size="icon" variant="ghost"
                          className="text-red-400 hover:text-red-300 h-7 w-7 shrink-0"
                          onClick={() => {
                            const novas = (novaCat.opcoes || []).filter((_, i) => i !== idx);
                            setNovaCat({...novaCat, opcoes: novas});
                          }}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
                <Button
                  type="button" variant="outline" size="sm"
                  className="mt-2 w-full border-dashed border-slate-600 text-slate-400"
                  onClick={() => setNovaCat({...novaCat, opcoes: [...(novaCat.opcoes || []), '']})}
                  data-testid="btn-add-opcao"
                >
                  <Plus className="w-3 h-3 mr-1" /> Adicionar Opção
                </Button>
              </div>
            )}

            <p className="text-xs text-slate-500">Após criar, passe o mouse sobre o ícone da categoria para carregar uma foto.</p>
            <Button onClick={addCategoria} className="w-full bg-amber-500 hover:bg-amber-600" data-testid="btn-salvar-categoria">Criar Categoria</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal Regulamento */}
      <Dialog open={showRegulamento} onOpenChange={setShowRegulamento}>
        <DialogContent className="max-w-2xl w-[95vw] max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-blue-500">
              <ScrollText className="w-5 h-5" /> Regulamento da Premiação
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Textarea
              value={editRegulamento}
              onChange={e => setEditRegulamento(e.target.value)}
              placeholder="Insira aqui o regulamento completo desta premiação. Este texto será exibido aos atletas..."
              className="min-h-[300px] bg-slate-50 dark:bg-slate-800 text-sm"
              data-testid="textarea-regulamento"
            />
            <Button onClick={() => { saveConfig(); setShowRegulamento(false); }} className="w-full bg-blue-500 hover:bg-blue-600">
              <Save className="w-4 h-4 mr-2" /> Salvar Regulamento
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal Resultados */}
      <Dialog open={showResultados} onOpenChange={setShowResultados}>
        <DialogContent className="max-w-3xl w-[95vw] max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-amber-500">
              <BarChart3 className="w-5 h-5" /> Resultados — {selected?.titulo}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-6">
            {resultados.map(res => (
              <Card key={res.categoria.id} className="bg-slate-50 dark:bg-slate-800 border-0">
                <CardHeader className="pb-2">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <CardTitle className="text-base text-amber-600">{res.categoria.nome}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge>{res.total_votos} votos</Badge>
                      <Button size="sm" variant="ghost" onClick={() => { setShowConsolidar(res.categoria.id); setConsolidarNome(''); setConsolidarVariantes(''); }}>
                        <Merge className="w-3 h-3 mr-1" /> Consolidar
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {res.indicados.length === 0 ? <p className="text-slate-400 text-sm">Nenhum voto</p> : (
                    <div className="space-y-2">
                      {res.indicados.map((ind, idx) => (
                        <div key={idx} className="flex items-center justify-between gap-2 p-2 bg-white dark:bg-slate-700 rounded-lg">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${idx === 0 ? 'bg-amber-500 text-white' : idx === 1 ? 'bg-slate-300 text-slate-700' : idx === 2 ? 'bg-orange-700 text-white' : 'bg-slate-200 text-slate-600'}`}>{idx+1}</span>
                            <div className="min-w-0">
                              <p className="font-medium text-sm truncate">{ind.nome}</p>
                              {ind.link && <a href={ind.link.startsWith('http') ? ind.link : `https://instagram.com/${ind.link.replace('@','')}`} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline flex items-center gap-1"><ExternalLink className="w-3 h-3" />{ind.link}</a>}
                            </div>
                          </div>
                          <Badge className="bg-amber-500/20 text-amber-600 shrink-0">{ind.votos}</Badge>
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
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Merge className="w-5 h-5 text-amber-500" /> Consolidar</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nome principal</Label>
              <Input value={consolidarNome} onChange={e => setConsolidarNome(e.target.value)} placeholder="Nome correto" />
            </div>
            <div>
              <Label>Variantes (vírgula)</Label>
              <Input value={consolidarVariantes} onChange={e => setConsolidarVariantes(e.target.value)} placeholder="var1, var2, var3" />
            </div>
            <Button onClick={() => handleConsolidar(showConsolidar)} className="w-full bg-amber-500 hover:bg-amber-600">Consolidar</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardPremiacao;
