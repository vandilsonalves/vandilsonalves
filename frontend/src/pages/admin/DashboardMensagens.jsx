import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Send, Paperclip, Link2, Image, X, Loader2, CheckCircle2,
  Users, Clock, FileText, Download, ChevronDown, ChevronUp,
  Calendar, XCircle, Timer, MapPin, Building2
} from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FILTRO_OPTIONS = {
  modalidades: [
    { id: 'profissional_amador', label: 'Profissional/Amador' },
    { id: 'povao_pace_livre', label: 'Galera' }
  ],
  generos: [
    { id: 'M', label: 'Masculino' },
    { id: 'F', label: 'Feminino' },
    { id: 'pcd_m', label: 'PCD Masculino' },
    { id: 'pcd_f', label: 'PCD Feminino' },
    { id: 'cadeirante_m', label: 'Cadeirante Masculino' },
    { id: 'cadeirante_f', label: 'Cadeirante Feminino' }
  ],
  especiais: [
    { id: 'donos_assessoria', label: 'Donos de Assessoria' },
    { id: 'individual_sem_assessoria', label: 'Atletas Individuais (sem assessoria)' }
  ]
};

const DashboardMensagens = () => {
  const [titulo, setTitulo] = useState('');
  const [mensagem, setMensagem] = useState('');
  const [link, setLink] = useState('');
  const [anexos, setAnexos] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [contagem, setContagem] = useState(null);
  const [historico, setHistorico] = useState([]);
  const [showHistorico, setShowHistorico] = useState(false);
  const [agendadas, setAgendadas] = useState([]);
  const [modoAgendar, setModoAgendar] = useState(false);
  const [dataAgendamento, setDataAgendamento] = useState('');
  const [horaAgendamento, setHoraAgendamento] = useState('09:00');

  const [filtroTipo, setFiltroTipo] = useState('todos');
  const [filtroModalidades, setFiltroModalidades] = useState([]);
  const [filtroGeneros, setFiltroGeneros] = useState([]);
  const [filtroEspecial, setFiltroEspecial] = useState([]);
  const [filtroEstados, setFiltroEstados] = useState([]);
  const [filtroCidades, setFiltroCidades] = useState([]);
  const [estadosDisponiveis, setEstadosDisponiveis] = useState([]);
  const [cidadesDisponiveis, setCidadesDisponiveis] = useState([]);

  const fileInputRef = useRef(null);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchContagem();
  }, [filtroTipo, filtroModalidades, filtroGeneros, filtroEspecial, filtroEstados, filtroCidades]);

  useEffect(() => {
    if (showHistorico) fetchHistorico();
  }, [showHistorico]);

  useEffect(() => {
    fetchAgendadas();
    fetchEstadosDisponiveis();
  }, []);

  useEffect(() => {
    if (filtroTipo === 'cidade' && filtroEstados.length > 0) {
      fetchCidadesDisponiveis(filtroEstados[0]);
    }
  }, [filtroEstados, filtroTipo]);

  const fetchContagem = async () => {
    try {
      const params = new URLSearchParams({
        filtro_tipo: filtroTipo,
        filtro_modalidades: JSON.stringify(filtroModalidades),
        filtro_generos: JSON.stringify(filtroGeneros),
        filtro_especial: JSON.stringify(filtroEspecial),
        filtro_estados: JSON.stringify(filtroEstados),
        filtro_cidades: JSON.stringify(filtroCidades)
      });
      const res = await fetch(`${API}/admin/mensagens/contagem-destinatarios?${params}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setContagem(data.total);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchEstadosDisponiveis = async () => {
    try {
      const res = await fetch(`${API}/admin/mensagens/estados-disponiveis`, { headers });
      if (res.ok) {
        const data = await res.json();
        setEstadosDisponiveis(data.estados || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchCidadesDisponiveis = async (estado) => {
    try {
      const params = estado ? `?estado=${estado}` : '';
      const res = await fetch(`${API}/admin/mensagens/cidades-disponiveis${params}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setCidadesDisponiveis(data.cidades || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchHistorico = async () => {
    try {
      const res = await fetch(`${API}/admin/mensagens/historico`, { headers });
      if (res.ok) {
        const data = await res.json();
        setHistorico(data.mensagens || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchAgendadas = async () => {
    try {
      const res = await fetch(`${API}/admin/mensagens/agendadas`, { headers });
      if (res.ok) {
        const data = await res.json();
        setAgendadas(data.agendadas || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const cancelarAgendada = async (id) => {
    if (!window.confirm('Cancelar esta mensagem agendada?')) return;
    try {
      const res = await fetch(`${API}/admin/mensagens/agendada/${id}`, {
        method: 'DELETE',
        headers
      });
      if (res.ok) {
        toast.success('Mensagem agendada cancelada');
        fetchAgendadas();
        if (showHistorico) fetchHistorico();
      } else {
        toast.error('Erro ao cancelar');
      }
    } catch (e) {
      toast.error('Erro de conexão');
    }
  };

  const handleUpload = async (e) => {
    const files = e.target.files;
    if (!files?.length) return;
    setUploading(true);

    for (const file of files) {
      const formData = new FormData();
      formData.append('arquivo', file);
      try {
        const res = await fetch(`${API}/admin/mensagens/upload`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData
        });
        if (res.ok) {
          const data = await res.json();
          setAnexos(prev => [...prev, data]);
        } else {
          toast.error(`Erro ao enviar ${file.name}`);
        }
      } catch (err) {
        toast.error(`Erro ao enviar ${file.name}`);
      }
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeAnexo = (idx) => {
    setAnexos(prev => prev.filter((_, i) => i !== idx));
  };

  const toggleFiltro = (list, setList, value) => {
    setList(prev => prev.includes(value) ? prev.filter(v => v !== value) : [...prev, value]);
  };

  const handleEnviar = async () => {
    if (!mensagem.trim() && !link.trim()) {
      toast.error('Escreva uma mensagem ou adicione um link');
      return;
    }
    if (contagem === 0) {
      toast.error('Nenhum destinatário com os filtros selecionados');
      return;
    }

    let agendarPara = '';
    if (modoAgendar) {
      if (!dataAgendamento) {
        toast.error('Selecione a data do agendamento');
        return;
      }
      agendarPara = `${dataAgendamento}T${horaAgendamento}:00`;
      const agendaDate = new Date(agendarPara);
      if (agendaDate <= new Date()) {
        toast.error('A data de agendamento deve ser no futuro');
        return;
      }
    }

    const actionText = modoAgendar
      ? `Agendar mensagem para ${dataAgendamento} às ${horaAgendamento}?`
      : `Enviar mensagem para ${contagem} atleta(s)?`;
    if (!window.confirm(actionText)) return;

    setEnviando(true);
    try {
      const formData = new FormData();
      formData.append('titulo', titulo);
      formData.append('mensagem', mensagem);
      formData.append('link', link);
      formData.append('anexos', JSON.stringify(anexos));
      formData.append('filtro_tipo', filtroTipo);
      formData.append('filtro_modalidades', JSON.stringify(filtroModalidades));
      formData.append('filtro_generos', JSON.stringify(filtroGeneros));
      formData.append('filtro_especial', JSON.stringify(filtroEspecial));
      formData.append('filtro_estados', JSON.stringify(filtroEstados));
      formData.append('filtro_cidades', JSON.stringify(filtroCidades));
      formData.append('agendar_para', agendarPara);

      const res = await fetch(`${API}/admin/mensagens/enviar`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        if (data.status === 'agendada') {
          toast.success(`Mensagem agendada para ${dataAgendamento} às ${horaAgendamento}`);
          fetchAgendadas();
        } else {
          toast.success(`Mensagem enviada para ${data.total_enviados} atleta(s)!`);
        }
        setTitulo('');
        setMensagem('');
        setLink('');
        setAnexos([]);
        setDataAgendamento('');
        setModoAgendar(false);
        if (showHistorico) fetchHistorico();
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || 'Erro ao enviar mensagem');
      }
    } catch (err) {
      toast.error('Erro de conexão');
    } finally {
      setEnviando(false);
    }
  };

  const getFiltroLabel = (tipo) => {
    if (tipo === 'todos') return 'Todos os Atletas';
    if (tipo === 'estado') return 'Por Estado';
    if (tipo === 'cidade') return 'Por Cidade';
    if (tipo === 'modalidade') return 'Por Modalidade';
    if (tipo === 'genero') return 'Por Gênero/Categoria';
    if (tipo === 'especial') return 'Grupos Especiais';
    return tipo;
  };

  const formatDate = (iso) => {
    if (!iso) return '';
    return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-4" data-testid="dashboard-mensagens">
      {/* Composer */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
        <CardHeader className="border-b dark:border-slate-700 pb-3">
          <CardTitle className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <Send className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <h3 className="font-bold">Nova Mensagem</h3>
              <p className="text-sm text-slate-500 font-normal">Envie mensagens, links e arquivos para os atletas</p>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
          {/* Destinatários */}
          <div className="space-y-3">
            <Label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Destinatários</Label>

            {/* Tipo de filtro */}
            <div className="flex flex-wrap gap-2">
              {[
                { id: 'todos', label: 'Todos', icon: <Users className="w-3.5 h-3.5 mr-1.5" /> },
                { id: 'estado', label: 'Por Estado', icon: <MapPin className="w-3.5 h-3.5 mr-1.5" /> },
                { id: 'cidade', label: 'Por Cidade', icon: <Building2 className="w-3.5 h-3.5 mr-1.5" /> },
                { id: 'modalidade', label: 'Por Modalidade' },
                { id: 'genero', label: 'Por Gênero' },
                { id: 'especial', label: 'Grupos Especiais' }
              ].map(opt => (
                <Button
                  key={opt.id}
                  variant={filtroTipo === opt.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => {
                    setFiltroTipo(opt.id);
                    setFiltroModalidades([]);
                    setFiltroGeneros([]);
                    setFiltroEspecial([]);
                    setFiltroEstados([]);
                    setFiltroCidades([]);
                  }}
                  className={filtroTipo === opt.id ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'dark:border-slate-600 dark:text-slate-300'}
                  data-testid={`filtro-tipo-${opt.id}`}
                >
                  {opt.icon || null}{opt.label}
                </Button>
              ))}
            </div>

            {/* Sub-filtros */}
            {filtroTipo === 'estado' && (
              <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg space-y-3" data-testid="filtro-estado-panel">
                <p className="text-xs text-slate-500 mb-2">Selecione os estados (UF):</p>
                <div className="flex flex-wrap gap-2">
                  {estadosDisponiveis.length === 0 ? (
                    <p className="text-sm text-slate-400">Nenhum estado encontrado</p>
                  ) : (
                    estadosDisponiveis.map(uf => (
                      <label key={uf} className="flex items-center gap-2 cursor-pointer bg-white dark:bg-slate-800 px-3 py-1.5 rounded-md border border-slate-200 dark:border-slate-600 hover:border-emerald-400 transition-colors">
                        <input
                          type="checkbox"
                          checked={filtroEstados.includes(uf)}
                          onChange={() => toggleFiltro(filtroEstados, setFiltroEstados, uf)}
                          className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                          data-testid={`filtro-estado-${uf}`}
                        />
                        <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{uf}</span>
                      </label>
                    ))
                  )}
                </div>
                {filtroEstados.length > 0 && (
                  <p className="text-xs text-emerald-600 font-medium">
                    <MapPin className="w-3 h-3 inline mr-1" />
                    {filtroEstados.length} estado(s) selecionado(s): {filtroEstados.join(', ')}
                  </p>
                )}
              </div>
            )}

            {filtroTipo === 'cidade' && (
              <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg space-y-3" data-testid="filtro-cidade-panel">
                <p className="text-xs text-slate-500 mb-2">Primeiro, selecione um estado para filtrar as cidades:</p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {estadosDisponiveis.map(uf => (
                    <Button
                      key={uf}
                      size="sm"
                      variant={filtroEstados.includes(uf) ? 'default' : 'outline'}
                      onClick={() => {
                        setFiltroEstados([uf]);
                        setFiltroCidades([]);
                      }}
                      className={filtroEstados.includes(uf) ? 'bg-emerald-600 hover:bg-emerald-700 text-white h-7 text-xs' : 'h-7 text-xs dark:border-slate-600 dark:text-slate-300'}
                      data-testid={`filtro-cidade-estado-${uf}`}
                    >
                      {uf}
                    </Button>
                  ))}
                </div>
                {filtroEstados.length > 0 && cidadesDisponiveis.length > 0 && (
                  <>
                    <p className="text-xs text-slate-500">Cidades em {filtroEstados[0]}:</p>
                    <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
                      {cidadesDisponiveis.map(cidade => (
                        <label key={cidade} className="flex items-center gap-2 cursor-pointer bg-white dark:bg-slate-800 px-3 py-1.5 rounded-md border border-slate-200 dark:border-slate-600 hover:border-emerald-400 transition-colors">
                          <input
                            type="checkbox"
                            checked={filtroCidades.includes(cidade)}
                            onChange={() => toggleFiltro(filtroCidades, setFiltroCidades, cidade)}
                            className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                            data-testid={`filtro-cidade-${cidade}`}
                          />
                          <span className="text-sm text-slate-700 dark:text-slate-300">{cidade}</span>
                        </label>
                      ))}
                    </div>
                  </>
                )}
                {filtroEstados.length > 0 && cidadesDisponiveis.length === 0 && (
                  <p className="text-sm text-slate-400">Nenhuma cidade encontrada para {filtroEstados[0]}</p>
                )}
                {filtroCidades.length > 0 && (
                  <p className="text-xs text-emerald-600 font-medium">
                    <Building2 className="w-3 h-3 inline mr-1" />
                    {filtroCidades.length} cidade(s) selecionada(s): {filtroCidades.join(', ')}
                  </p>
                )}
              </div>
            )}

            {filtroTipo === 'modalidade' && (
              <div className="flex flex-wrap gap-2 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                {FILTRO_OPTIONS.modalidades.map(opt => (
                  <label key={opt.id} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filtroModalidades.includes(opt.id)}
                      onChange={() => toggleFiltro(filtroModalidades, setFiltroModalidades, opt.id)}
                      className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                      data-testid={`filtro-mod-${opt.id}`}
                    />
                    <span className="text-sm text-slate-700 dark:text-slate-300">{opt.label}</span>
                  </label>
                ))}
              </div>
            )}

            {filtroTipo === 'genero' && (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                {FILTRO_OPTIONS.generos.map(opt => (
                  <label key={opt.id} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filtroGeneros.includes(opt.id)}
                      onChange={() => toggleFiltro(filtroGeneros, setFiltroGeneros, opt.id)}
                      className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                      data-testid={`filtro-gen-${opt.id}`}
                    />
                    <span className="text-sm text-slate-700 dark:text-slate-300">{opt.label}</span>
                  </label>
                ))}
              </div>
            )}

            {filtroTipo === 'especial' && (
              <div className="flex flex-wrap gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                {FILTRO_OPTIONS.especiais.map(opt => (
                  <label key={opt.id} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filtroEspecial.includes(opt.id)}
                      onChange={() => toggleFiltro(filtroEspecial, setFiltroEspecial, opt.id)}
                      className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                      data-testid={`filtro-esp-${opt.id}`}
                    />
                    <span className="text-sm text-slate-700 dark:text-slate-300">{opt.label}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Contagem */}
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-emerald-600" />
              <span className="text-sm text-slate-600 dark:text-slate-400">
                {contagem !== null ? (
                  <><strong className="text-emerald-600">{contagem}</strong> atleta(s) receberão esta mensagem</>
                ) : 'Calculando...'}
              </span>
            </div>
          </div>

          {/* Título */}
          <div>
            <Label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Título (opcional)</Label>
            <Input
              value={titulo}
              onChange={e => setTitulo(e.target.value)}
              placeholder="Assunto da mensagem"
              className="mt-1 dark:bg-slate-700 dark:border-slate-600"
              data-testid="input-titulo"
            />
          </div>

          {/* Mensagem */}
          <div>
            <Label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Mensagem</Label>
            <Textarea
              value={mensagem}
              onChange={e => setMensagem(e.target.value)}
              placeholder="Escreva sua mensagem aqui..."
              rows={5}
              className="mt-1 dark:bg-slate-700 dark:border-slate-600"
              data-testid="input-mensagem"
            />
          </div>

          {/* Link */}
          <div>
            <Label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Link (opcional)</Label>
            <div className="flex items-center gap-2 mt-1">
              <Link2 className="w-4 h-4 text-slate-400 flex-shrink-0" />
              <Input
                value={link}
                onChange={e => setLink(e.target.value)}
                placeholder="https://..."
                className="dark:bg-slate-700 dark:border-slate-600"
                data-testid="input-link"
              />
            </div>
          </div>

          {/* Anexos */}
          <div>
            <Label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Anexos</Label>
            <div className="flex items-center gap-2 mt-1">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.zip"
                onChange={handleUpload}
                className="hidden"
                data-testid="input-arquivo"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="dark:border-slate-600 dark:text-slate-300"
                data-testid="btn-anexar"
              >
                {uploading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Paperclip className="w-4 h-4 mr-2" />}
                Anexar Arquivo
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const input = document.createElement('input');
                  input.type = 'file';
                  input.accept = 'image/*';
                  input.onchange = (e) => handleUpload(e);
                  input.click();
                }}
                disabled={uploading}
                className="dark:border-slate-600 dark:text-slate-300"
                data-testid="btn-anexar-imagem"
              >
                <Image className="w-4 h-4 mr-2" />
                Imagem
              </Button>
            </div>

            {/* Lista de anexos */}
            {anexos.length > 0 && (
              <div className="mt-2 space-y-1">
                {anexos.map((a, idx) => (
                  <div key={idx} className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-700/50 rounded text-sm">
                    {a.tipo === 'imagem' ? (
                      <Image className="w-4 h-4 text-blue-500 flex-shrink-0" />
                    ) : (
                      <FileText className="w-4 h-4 text-amber-500 flex-shrink-0" />
                    )}
                    <span className="text-slate-700 dark:text-slate-300 truncate flex-1">{a.original_name}</span>
                    <span className="text-xs text-slate-400">{(a.tamanho / 1024).toFixed(0)}KB</span>
                    <button onClick={() => removeAnexo(idx)} className="text-red-400 hover:text-red-600">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Agendamento */}
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Button
                variant={!modoAgendar ? 'default' : 'outline'}
                size="sm"
                onClick={() => setModoAgendar(false)}
                className={!modoAgendar ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'dark:border-slate-600 dark:text-slate-300'}
                data-testid="btn-enviar-agora"
              >
                <Send className="w-4 h-4 mr-1" /> Enviar Agora
              </Button>
              <Button
                variant={modoAgendar ? 'default' : 'outline'}
                size="sm"
                onClick={() => setModoAgendar(true)}
                className={modoAgendar ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'dark:border-slate-600 dark:text-slate-300'}
                data-testid="btn-agendar"
              >
                <Calendar className="w-4 h-4 mr-1" /> Agendar
              </Button>
            </div>

            {modoAgendar && (
              <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <Calendar className="w-5 h-5 text-blue-600 flex-shrink-0" />
                <div className="flex items-center gap-2 flex-wrap">
                  <Input
                    type="date"
                    value={dataAgendamento}
                    onChange={e => setDataAgendamento(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-44 dark:bg-slate-700 dark:border-slate-600"
                    data-testid="input-data-agendamento"
                  />
                  <Input
                    type="time"
                    value={horaAgendamento}
                    onChange={e => setHoraAgendamento(e.target.value)}
                    className="w-32 dark:bg-slate-700 dark:border-slate-600"
                    data-testid="input-hora-agendamento"
                  />
                  <span className="text-sm text-blue-700 dark:text-blue-300">
                    A mensagem será enviada automaticamente neste horário
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Botão enviar */}
          <div className="flex items-center justify-between pt-2 border-t dark:border-slate-700">
            <span className="text-xs text-slate-400">
              {filtroTipo !== 'todos' && getFiltroLabel(filtroTipo)}
            </span>
            <Button
              onClick={handleEnviar}
              disabled={enviando || (!mensagem.trim() && !link.trim())}
              className={modoAgendar ? 'bg-blue-600 hover:bg-blue-700 text-white px-8' : 'bg-emerald-600 hover:bg-emerald-700 text-white px-8'}
              data-testid="btn-enviar-mensagem"
            >
              {enviando ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {modoAgendar ? 'Agendando...' : 'Enviando...'}</>
              ) : modoAgendar ? (
                <><Calendar className="w-4 h-4 mr-2" /> Agendar Mensagem</>
              ) : (
                <><Send className="w-4 h-4 mr-2" /> Enviar Mensagem</>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Mensagens Agendadas */}
      {agendadas.length > 0 && (
        <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 border-l-4 border-l-blue-500">
          <CardHeader className="border-b dark:border-slate-700 pb-3">
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Timer className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <h3 className="font-bold">Mensagens Agendadas</h3>
                <p className="text-sm text-slate-500 font-normal">{agendadas.length} mensagem(ns) aguardando envio</p>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-3">
              {agendadas.map((msg, idx) => (
                <div key={idx} className="p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start justify-between mb-1">
                    <div>
                      <h4 className="font-semibold text-sm text-slate-800 dark:text-white">{msg.titulo}</h4>
                      <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 mt-1">{msg.mensagem}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => cancelarAgendada(msg.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 flex-shrink-0"
                      data-testid={`btn-cancelar-agendada-${idx}`}
                    >
                      <XCircle className="w-4 h-4 mr-1" /> Cancelar
                    </Button>
                  </div>
                  <div className="flex items-center gap-3 mt-2">
                    <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                      <Calendar className="w-3 h-3 mr-1" />
                      {formatDate(msg.agendar_para)}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {msg.filtro_tipo === 'todos' ? 'Todos' : getFiltroLabel(msg.filtro_tipo)}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Histórico */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
        <CardHeader
          className="border-b dark:border-slate-700 cursor-pointer"
          onClick={() => setShowHistorico(!showHistorico)}
        >
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Clock className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <h3 className="font-bold">Histórico de Mensagens</h3>
                <p className="text-sm text-slate-500 font-normal">Mensagens enviadas anteriormente</p>
              </div>
            </div>
            {showHistorico ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </CardTitle>
        </CardHeader>
        {showHistorico && (
          <CardContent className="pt-4">
            {historico.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-6">Nenhuma mensagem enviada ainda</p>
            ) : (
              <div className="space-y-3">
                {historico.map((msg, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                    <div className="flex items-start justify-between mb-1">
                      <h4 className="font-semibold text-sm text-slate-800 dark:text-white">{msg.titulo}</h4>
                      <div className="flex items-center gap-2">
                        {msg.status === 'agendada' && (
                          <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 text-xs">
                            <Calendar className="w-3 h-3 mr-1" /> Agendada
                          </Badge>
                        )}
                        {msg.status === 'cancelada' && (
                          <Badge className="bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 text-xs">
                            <XCircle className="w-3 h-3 mr-1" /> Cancelada
                          </Badge>
                        )}
                        {(!msg.status || msg.status === 'enviada') && (
                          <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 text-xs">
                            <CheckCircle2 className="w-3 h-3 mr-1" /> Enviada
                          </Badge>
                        )}
                        <Badge variant="secondary" className="text-xs">
                          <Users className="w-3 h-3 mr-1" />
                          {msg.total_enviados}
                        </Badge>
                        <span className="text-xs text-slate-400">{formatDate(msg.data_envio || msg.data_criacao)}</span>
                      </div>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2">{msg.mensagem}</p>
                    {msg.link && (
                      <a href={msg.link} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline flex items-center gap-1 mt-1">
                        <Link2 className="w-3 h-3" /> {msg.link}
                      </a>
                    )}
                    {msg.anexos?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {msg.anexos.map((a, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            <Paperclip className="w-3 h-3 mr-1" /> {a.original_name}
                          </Badge>
                        ))}
                      </div>
                    )}
                    <div className="flex flex-wrap gap-1 mt-2">
                      <Badge variant="outline" className="text-xs bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                        {msg.filtro_tipo === 'todos' ? 'Todos' : getFiltroLabel(msg.filtro_tipo)}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  );
};

const getFiltroLabel = (tipo) => {
  if (tipo === 'todos') return 'Todos os Atletas';
  if (tipo === 'estado') return 'Por Estado';
  if (tipo === 'cidade') return 'Por Cidade';
  if (tipo === 'modalidade') return 'Por Modalidade';
  if (tipo === 'genero') return 'Por Gênero';
  if (tipo === 'especial') return 'Grupos Especiais';
  return tipo;
};

export default DashboardMensagens;
