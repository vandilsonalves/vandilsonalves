import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import useCidadesIBGE from '@/hooks/useCidadesIBGE';
import CidadeCombobox from '@/components/CidadeCombobox';
import {
  Users, Shield, Clock, AlertTriangle, Send, Calendar,
  Search, Filter, Paperclip, ImageIcon, X, Loader2,
  CheckCircle2, XCircle, Zap, ChevronDown, FileText, Mail
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const ESTADOS_BR = [
  'AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA',
  'PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'
];

const CATEGORIAS_GENERO = [
  { id: 'M', label: 'Masculino' },
  { id: 'F', label: 'Feminino' },
  { id: 'pcd_m', label: 'PCD Masculino' },
  { id: 'pcd_f', label: 'PCD Feminino' },
  { id: 'cadeirante_m', label: 'Cadeirante Masculino' },
  { id: 'cadeirante_f', label: 'Cadeirante Feminino' }
];

const MODALIDADES = [
  { id: 'corrida_rua', label: 'Corrida de Rua' },
  { id: 'trail', label: 'Trail Run' },
  { id: 'meia_maratona', label: 'Meia Maratona' },
  { id: 'maratona', label: 'Maratona' },
  { id: 'ultra', label: 'Ultra Maratona' }
];

const DashboardAutorizacoes = () => {
  const { token } = useAuth();
  const headers = { Authorization: `Bearer ${token}` };

  // Dados de atletas
  const [atletas, setAtletas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busca, setBusca] = useState('');

  // Filtros
  const [filtroStatus, setFiltroStatus] = useState('todos');
  const [filtroEstado, setFiltroEstado] = useState('');
  const [filtroCidade, setFiltroCidade] = useState('');
  const [filtroGeneros, setFiltroGeneros] = useState([]);
  const [filtroModalidades, setFiltroModalidades] = useState([]);
  const [filtroEspecial, setFiltroEspecial] = useState([]);
  const { cidades: cidadesIBGE, loading: loadingCidades } = useCidadesIBGE(filtroEstado);

  // Mensagem
  const [titulo, setTitulo] = useState('');
  const [mensagem, setMensagem] = useState('');
  const [link, setLink] = useState('');
  const [splash, setSplash] = useState(false);
  const [anexos, setAnexos] = useState([]);
  const [uploadingAnexo, setUploadingAnexo] = useState(false);
  const [enviando, setEnviando] = useState(false);

  // Agendamento
  const [modoAgendar, setModoAgendar] = useState(false);
  const [dataAgendamento, setDataAgendamento] = useState('');

  // Histórico
  const [historico, setHistorico] = useState([]);

  // Seleção de atletas
  const [selecionados, setSelecionados] = useState(new Set());

  // ---- Data fetching ----
  const fetchAtletas = async () => {
    try {
      const res = await axios.get(`${API}/admin/autorizacoes/atletas-completo`, { headers });
      setAtletas(res.data.atletas || []);
    } catch (err) {
      toast.error('Erro ao carregar atletas');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistorico = async () => {
    try {
      const res = await axios.get(`${API}/admin/autorizacoes/mensagens/historico`, { headers });
      setHistorico(res.data.mensagens || []);
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
    }
  };

  useEffect(() => {
    fetchAtletas();
    fetchHistorico();
  }, []);

  // ---- Stats ----
  const stats = useMemo(() => {
    const s = { em_teste: 0, autorizado: 0, expirado: 0, total: atletas.length };
    atletas.forEach(a => { if (s[a.status_periodo] !== undefined) s[a.status_periodo]++; });
    return s;
  }, [atletas]);

  // ---- Filtros ----
  const atletasFiltrados = useMemo(() => {
    return atletas.filter(a => {
      if (filtroStatus !== 'todos' && a.status_periodo !== filtroStatus) return false;
      if (filtroEstado && a.estado !== filtroEstado) return false;
      if (filtroCidade && a.cidade !== filtroCidade) return false;
      if (filtroGeneros.length > 0) {
        const g = a.genero || a.sexo || '';
        const cat = a.categoria || 'normal';
        const match = filtroGeneros.some(fg => {
          if (fg === 'M') return g === 'M' && cat === 'normal';
          if (fg === 'F') return g === 'F' && cat === 'normal';
          if (fg === 'pcd_m') return g === 'M' && cat === 'pcd';
          if (fg === 'pcd_f') return g === 'F' && cat === 'pcd';
          if (fg === 'cadeirante_m') return g === 'M' && cat === 'cadeirante';
          if (fg === 'cadeirante_f') return g === 'F' && cat === 'cadeirante';
          return false;
        });
        if (!match) return false;
      }
      if (busca) {
        const b = busca.toLowerCase();
        if (!a.nome?.toLowerCase().includes(b) && !a.email?.toLowerCase().includes(b)) return false;
      }
      return true;
    });
  }, [atletas, filtroStatus, filtroEstado, filtroCidade, filtroGeneros, busca]);

  // ---- Upload de anexo ----
  const handleUploadAnexo = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Arquivo muito grande (max 10MB)');
      return;
    }
    setUploadingAnexo(true);
    try {
      const formData = new FormData();
      formData.append('arquivo', file);
      const res = await axios.post(`${API}/admin/autorizacoes/mensagens/upload`, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' }
      });
      setAnexos(prev => [...prev, res.data]);
      toast.success('Arquivo anexado!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro no upload');
    } finally {
      setUploadingAnexo(false);
      e.target.value = '';
    }
  };

  const removerAnexo = (idx) => setAnexos(prev => prev.filter((_, i) => i !== idx));

  // ---- Enviar mensagem ----
  const handleEnviar = async () => {
    if (!mensagem.trim() && !link.trim()) {
      toast.error('Escreva uma mensagem ou adicione um link');
      return;
    }
    setEnviando(true);
    try {
      const formData = new FormData();
      formData.append('titulo', titulo);
      formData.append('mensagem', mensagem);
      formData.append('link', link);
      formData.append('anexos', JSON.stringify(anexos));
      formData.append('status_filtro', filtroStatus);
      formData.append('filtro_estados', JSON.stringify(filtroEstado ? [filtroEstado] : []));
      formData.append('filtro_cidades', JSON.stringify(filtroCidade ? [filtroCidade] : []));
      formData.append('filtro_modalidades', JSON.stringify(filtroModalidades));
      formData.append('filtro_generos', JSON.stringify(filtroGeneros));
      formData.append('filtro_especial', JSON.stringify(filtroEspecial));
      formData.append('splash', splash.toString());
      if (modoAgendar && dataAgendamento) {
        formData.append('agendar_para', dataAgendamento);
      }

      const res = await axios.post(`${API}/admin/autorizacoes/mensagens/enviar`, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' }
      });

      toast.success(res.data.message);
      setTitulo(''); setMensagem(''); setLink(''); setAnexos([]); setSplash(false);
      setModoAgendar(false); setDataAgendamento('');
      fetchHistorico();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro ao enviar');
    } finally {
      setEnviando(false);
    }
  };

  // ---- Autorizar atleta ----
  const handleAutorizar = async (atletaId, tipoPlano = 'ate_fim_ano') => {
    try {
      const res = await axios.post(`${API}/admin/autorizacoes/autorizar`, {
        atleta_id: atletaId,
        tipo_plano: tipoPlano,
      }, { headers });
      toast.success(res.data.message || 'Atleta autorizado!');
      fetchAtletas();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro ao autorizar');
    }
  };

  const handleRevogar = async (atletaId) => {
    if (!window.confirm('Tem certeza que deseja revogar o acesso deste atleta?')) return;
    try {
      const res = await axios.post(`${API}/admin/autorizacoes/revogar`, { atleta_id: atletaId }, { headers });
      toast.success(res.data.message || 'Autorização revogada');
      fetchAtletas();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erro ao revogar');
    }
  };

  const limparFiltros = () => {
    setFiltroStatus('todos'); setFiltroEstado(''); setFiltroCidade('');
    setFiltroGeneros([]); setFiltroModalidades([]); setFiltroEspecial([]);
    setBusca('');
  };

  const toggleGenero = (id) => {
    setFiltroGeneros(prev => prev.includes(id) ? prev.filter(g => g !== id) : [...prev, id]);
  };

  const statusColor = (s) => {
    if (s === 'em_teste') return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    if (s === 'autorizado') return 'bg-green-500/20 text-green-400 border-green-500/30';
    return 'bg-red-500/20 text-red-400 border-red-500/30';
  };

  const statusLabel = (s) => {
    if (s === 'em_teste') return 'Em Teste';
    if (s === 'autorizado') return 'Autorizado';
    return 'Expirado';
  };

  if (loading) return (
    <div className="flex items-center justify-center py-20">
      <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
    </div>
  );

  return (
    <div className="space-y-6" data-testid="dashboard-autorizacoes">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-blue-500/10 border-blue-500/20 cursor-pointer hover:bg-blue-500/20 transition-colors" onClick={() => setFiltroStatus('em_teste')}>
          <CardContent className="p-4 text-center">
            <Clock className="w-6 h-6 text-blue-400 mx-auto mb-1" />
            <p className="text-2xl font-bold text-blue-400">{stats.em_teste}</p>
            <p className="text-xs text-blue-300">Em Teste</p>
          </CardContent>
        </Card>
        <Card className="bg-green-500/10 border-green-500/20 cursor-pointer hover:bg-green-500/20 transition-colors" onClick={() => setFiltroStatus('autorizado')}>
          <CardContent className="p-4 text-center">
            <Shield className="w-6 h-6 text-green-400 mx-auto mb-1" />
            <p className="text-2xl font-bold text-green-400">{stats.autorizado}</p>
            <p className="text-xs text-green-300">Autorizados</p>
          </CardContent>
        </Card>
        <Card className="bg-red-500/10 border-red-500/20 cursor-pointer hover:bg-red-500/20 transition-colors" onClick={() => setFiltroStatus('expirado')}>
          <CardContent className="p-4 text-center">
            <AlertTriangle className="w-6 h-6 text-red-400 mx-auto mb-1" />
            <p className="text-2xl font-bold text-red-400">{stats.expirado}</p>
            <p className="text-xs text-red-300">Expirados</p>
          </CardContent>
        </Card>
        <Card className="bg-slate-500/10 border-slate-500/20 cursor-pointer hover:bg-slate-500/20 transition-colors" onClick={() => setFiltroStatus('todos')}>
          <CardContent className="p-4 text-center">
            <Users className="w-6 h-6 text-slate-400 mx-auto mb-1" />
            <p className="text-2xl font-bold text-slate-300">{stats.total}</p>
            <p className="text-xs text-slate-400">Total</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="mensagem" className="space-y-4">
        <TabsList className="bg-slate-800 border border-slate-700">
          <TabsTrigger value="mensagem" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black">
            <Mail className="w-4 h-4 mr-1" /> Enviar Mensagem
          </TabsTrigger>
          <TabsTrigger value="atletas" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black">
            <Users className="w-4 h-4 mr-1" /> Atletas ({atletasFiltrados.length})
          </TabsTrigger>
          <TabsTrigger value="historico" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black">
            <FileText className="w-4 h-4 mr-1" /> Histórico
          </TabsTrigger>
        </TabsList>

        {/* =========== ABA MENSAGEM =========== */}
        <TabsContent value="mensagem">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Send className="w-5 h-5 text-amber-500" /> Nova Mensagem
              </CardTitle>
              <CardDescription className="text-slate-400">
                Envie mensagens segmentadas por status de acesso e filtros geográficos
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Filtro de Status */}
              <div>
                <Label className="text-slate-300 text-xs uppercase tracking-wider mb-2 block">Destinatários por Status</Label>
                <div className="flex flex-wrap gap-2">
                  {[
                    { id: 'todos', label: 'Todos', count: stats.total },
                    { id: 'em_teste', label: 'Em Teste', count: stats.em_teste },
                    { id: 'autorizado', label: 'Autorizados', count: stats.autorizado },
                    { id: 'expirado', label: 'Expirados', count: stats.expirado },
                  ].map(s => (
                    <Button
                      key={s.id}
                      variant={filtroStatus === s.id ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFiltroStatus(s.id)}
                      className={filtroStatus === s.id ? 'bg-amber-500 text-black hover:bg-amber-600' : 'border-slate-600 text-slate-300'}
                      data-testid={`filtro-status-${s.id}`}
                    >
                      {s.label} <Badge variant="secondary" className="ml-1 text-[10px]">{s.count}</Badge>
                    </Button>
                  ))}
                </div>
              </div>

              {/* Filtros Geográficos e Demográficos */}
              <div>
                <Label className="text-slate-300 text-xs uppercase tracking-wider mb-2 block">Filtros Avançados</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {/* Estado */}
                  <div>
                    <Label className="text-xs text-slate-400">Estado</Label>
                    <Select value={filtroEstado || "__none__"} onValueChange={v => { setFiltroEstado(v === "__none__" ? "" : v); setFiltroCidade(""); }}>
                      <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                        <SelectValue placeholder="Todos" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__none__">Todos os Estados</SelectItem>
                        {ESTADOS_BR.map(uf => <SelectItem key={uf} value={uf}>{uf}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Cidade */}
                  <div>
                    <Label className="text-xs text-slate-400">Cidade</Label>
                    <CidadeCombobox
                      cidades={cidadesIBGE}
                      value={filtroCidade}
                      onValueChange={setFiltroCidade}
                      loading={loadingCidades}
                      disabled={!filtroEstado}
                      placeholder={filtroEstado ? 'Buscar cidade...' : 'Selecione estado'}
                      data-testid="filtro-cidade-aut"
                    />
                  </div>

                  {/* Gênero */}
                  <div>
                    <Label className="text-xs text-slate-400">Gênero</Label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {CATEGORIAS_GENERO.map(g => (
                        <Badge
                          key={g.id}
                          variant="outline"
                          className={`cursor-pointer text-[10px] ${filtroGeneros.includes(g.id) ? 'bg-amber-500/20 border-amber-500 text-amber-400' : 'border-slate-600 text-slate-400 hover:border-slate-400'}`}
                          onClick={() => toggleGenero(g.id)}
                        >
                          {g.label}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
                {(filtroEstado || filtroCidade || filtroGeneros.length > 0) && (
                  <div className="flex justify-end mt-2">
                    <Button variant="ghost" size="sm" onClick={limparFiltros} className="text-slate-400 text-xs">
                      <X className="w-3 h-3 mr-1" /> Limpar Filtros
                    </Button>
                  </div>
                )}
                <p className="text-xs text-slate-500 mt-1">{atletasFiltrados.length} atleta(s) correspondem aos filtros</p>
              </div>

              {/* Formulário de mensagem */}
              <div className="space-y-3 border-t border-slate-700 pt-4">
                <div>
                  <Label className="text-slate-300">Título</Label>
                  <Input
                    value={titulo}
                    onChange={e => setTitulo(e.target.value)}
                    placeholder="Título da mensagem"
                    className="bg-slate-700 border-slate-600 text-white"
                    maxLength={100}
                    data-testid="msg-titulo"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Mensagem *</Label>
                  <Textarea
                    value={mensagem}
                    onChange={e => setMensagem(e.target.value)}
                    placeholder="Escreva sua mensagem..."
                    className="bg-slate-700 border-slate-600 text-white min-h-[120px]"
                    maxLength={2000}
                    data-testid="msg-texto"
                  />
                  <p className="text-xs text-slate-500 text-right">{mensagem.length}/2000</p>
                </div>
                <div>
                  <Label className="text-slate-300">Link (opcional)</Label>
                  <Input
                    value={link}
                    onChange={e => setLink(e.target.value)}
                    placeholder="https://..."
                    className="bg-slate-700 border-slate-600 text-white"
                    data-testid="msg-link"
                  />
                </div>

                {/* Anexos */}
                <div>
                  <Label className="text-slate-300">Anexar Arquivo ou Imagem</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <input type="file" id="anexo-aut" className="hidden" onChange={handleUploadAnexo} data-testid="anexo-input" />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => document.getElementById('anexo-aut').click()}
                      disabled={uploadingAnexo}
                      className="border-slate-600 text-slate-300"
                    >
                      {uploadingAnexo ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Paperclip className="w-4 h-4 mr-1" />}
                      Arquivo
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const inp = document.getElementById('anexo-aut');
                        inp.accept = 'image/*';
                        inp.click();
                        setTimeout(() => { inp.accept = ''; }, 1000);
                      }}
                      disabled={uploadingAnexo}
                      className="border-slate-600 text-slate-300"
                    >
                      <ImageIcon className="w-4 h-4 mr-1" /> Imagem
                    </Button>
                  </div>
                  {anexos.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {anexos.map((a, i) => (
                        <Badge key={i} variant="secondary" className="bg-slate-700 text-slate-300 gap-1">
                          {a.tipo === 'imagem' ? <ImageIcon className="w-3 h-3" /> : <FileText className="w-3 h-3" />}
                          {a.original_name}
                          <X className="w-3 h-3 cursor-pointer hover:text-red-400" onClick={() => removerAnexo(i)} />
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                {/* Splash + Agendar */}
                <div className="flex flex-wrap items-center gap-6 border-t border-slate-700 pt-3">
                  <div className="flex items-center gap-2">
                    <Switch checked={splash} onCheckedChange={setSplash} data-testid="splash-switch" />
                    <Label className="text-slate-300 flex items-center gap-1">
                      <Zap className="w-4 h-4 text-yellow-500" /> Envio Splash
                    </Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch checked={modoAgendar} onCheckedChange={setModoAgendar} data-testid="agendar-switch" />
                    <Label className="text-slate-300 flex items-center gap-1">
                      <Calendar className="w-4 h-4 text-blue-400" /> Agendar
                    </Label>
                  </div>
                  {modoAgendar && (
                    <Input
                      type="datetime-local"
                      value={dataAgendamento}
                      onChange={e => setDataAgendamento(e.target.value)}
                      className="bg-slate-700 border-slate-600 text-white w-auto"
                      data-testid="data-agendamento"
                    />
                  )}
                </div>

                {/* Botões de Envio */}
                <div className="flex gap-3 pt-2">
                  <Button
                    onClick={handleEnviar}
                    disabled={enviando || (!mensagem.trim() && !link.trim())}
                    className="bg-amber-500 hover:bg-amber-600 text-black flex-1"
                    data-testid="btn-enviar-msg"
                  >
                    {enviando ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Send className="w-4 h-4 mr-1" />}
                    {modoAgendar ? 'Agendar Envio' : 'Enviar Agora'}
                    <Badge variant="secondary" className="ml-2 text-[10px]">{atletasFiltrados.length} atletas</Badge>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* =========== ABA ATLETAS =========== */}
        <TabsContent value="atletas">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <CardTitle className="text-lg text-white">Atletas</CardTitle>
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
                  <Input
                    placeholder="Buscar por nome ou email..."
                    value={busca}
                    onChange={e => setBusca(e.target.value)}
                    className="pl-8 bg-slate-700 border-slate-600 text-white w-full sm:w-64"
                    data-testid="busca-atleta"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto max-h-[500px]">
                <table className="w-full text-sm min-w-[600px]">
                  <thead className="sticky top-0 bg-slate-800 border-b border-slate-700">
                    <tr className="text-slate-400 text-left">
                      <th className="py-2 px-3">Nome</th>
                      <th className="py-2 px-3">Email</th>
                      <th className="py-2 px-3">UF/Cidade</th>
                      <th className="py-2 px-3">Status</th>
                      <th className="py-2 px-3">Dias</th>
                      <th className="py-2 px-3">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {atletasFiltrados.slice(0, 100).map(a => (
                      <tr key={a.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                        <td className="py-2 px-3 text-white font-medium">{a.nome}</td>
                        <td className="py-2 px-3 text-slate-400 text-xs">{a.email}</td>
                        <td className="py-2 px-3 text-slate-400 text-xs">{a.estado || '-'}/{a.cidade || '-'}</td>
                        <td className="py-2 px-3">
                          <Badge className={`${statusColor(a.status_periodo)} text-[10px]`}>
                            {statusLabel(a.status_periodo)}
                          </Badge>
                        </td>
                        <td className="py-2 px-3 text-slate-300 text-xs">{a.dias_restantes}d</td>
                        <td className="py-2 px-3">
                          {a.status_periodo !== 'autorizado' ? (
                            <div className="flex items-center gap-1">
                              <Button size="sm" variant="outline" className="text-xs border-green-600 text-green-400 hover:bg-green-600/20 h-7"
                                onClick={() => handleAutorizar(a.id, 'ate_fim_ano')} data-testid={`autorizar-${a.id}`}>
                                <CheckCircle2 className="w-3 h-3 mr-1" /> Ate 31/12/2026
                              </Button>
                              <Button size="sm" variant="outline" className="text-xs border-blue-600 text-blue-400 hover:bg-blue-600/20 h-7"
                                onClick={() => handleAutorizar(a.id, 'plano_anual')} data-testid={`autorizar-anual-${a.id}`}>
                                <CheckCircle2 className="w-3 h-3 mr-1" /> Anual
                              </Button>
                            </div>
                          ) : (
                            <Button size="sm" variant="outline" className="text-xs border-red-600 text-red-400 hover:bg-red-600/20 h-7"
                              onClick={() => handleRevogar(a.id)} data-testid={`revogar-${a.id}`}>
                              <XCircle className="w-3 h-3 mr-1" /> Revogar
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {atletasFiltrados.length > 100 && (
                  <p className="text-xs text-slate-500 text-center py-2">Mostrando 100 de {atletasFiltrados.length} atletas</p>
                )}
                {atletasFiltrados.length === 0 && (
                  <p className="text-center text-slate-500 py-8">Nenhum atleta encontrado com os filtros selecionados</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* =========== ABA HISTÓRICO =========== */}
        <TabsContent value="historico">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white">Histórico de Mensagens</CardTitle>
            </CardHeader>
            <CardContent>
              {historico.length === 0 ? (
                <p className="text-slate-500 text-center py-8">Nenhuma mensagem enviada ainda</p>
              ) : (
                <div className="space-y-3">
                  {historico.map(m => (
                    <Card key={m.id} className="bg-slate-700/50 border-slate-600">
                      <CardContent className="p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <p className="text-white font-medium text-sm">{m.titulo}</p>
                              {m.splash && <Badge className="bg-yellow-500/20 text-yellow-400 text-[10px]"><Zap className="w-3 h-3 mr-0.5" /> Splash</Badge>}
                              {m.status === 'agendada' && <Badge className="bg-blue-500/20 text-blue-400 text-[10px]"><Calendar className="w-3 h-3 mr-0.5" /> Agendada</Badge>}
                              <Badge variant="outline" className="border-slate-500 text-slate-400 text-[10px]">{m.status_filtro}</Badge>
                            </div>
                            <p className="text-slate-400 text-xs mt-1 line-clamp-2">{m.mensagem}</p>
                          </div>
                          <div className="text-right ml-3 flex-shrink-0">
                            <p className="text-amber-400 font-bold text-sm">{m.total_enviados}</p>
                            <p className="text-slate-500 text-[10px]">enviados</p>
                            <p className="text-slate-500 text-[10px] mt-1">
                              {new Date(m.data_criacao).toLocaleDateString('pt-BR')}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DashboardAutorizacoes;
