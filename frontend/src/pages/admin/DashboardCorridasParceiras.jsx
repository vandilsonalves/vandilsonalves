import { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Pencil, Trash2, Save, Link2, Image, BarChart3, MapPin, MousePointer, Loader2, Settings, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ESTADOS_BR = [
  'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA',
  'PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'
];

const DashboardCorridasParceiras = ({ token }) => {
  const [corridas, setCorridas] = useState([]);
  const [stats, setStats] = useState(null);
  const [config, setConfig] = useState({ link_whatsapp: '', cupom_nome: '', cupom_descricao: '' });
  const [loading, setLoading] = useState(true);
  const [modalAberto, setModalAberto] = useState(false);
  const [editando, setEditando] = useState(null);
  const [salvando, setSalvando] = useState(false);
  const [abaAtiva, setAbaAtiva] = useState('corridas'); // corridas | config | metricas

  const [form, setForm] = useState({
    nome_evento: '', data_evento: '', cidade: '', estado: '',
    valor_inscricao: '', link_inscricao: '', link_resultado: '',
    link_fotos: '', link_instagram: '', imagem: null
  });

  const headers = { Authorization: `Bearer ${token}` };

  const carregarDados = useCallback(async () => {
    try {
      const [corridasRes, statsRes, configRes] = await Promise.all([
        axios.get(`${API}/admin/corridas-parceiras`, { headers }),
        axios.get(`${API}/admin/corridas-parceiras/stats`, { headers }),
        axios.get(`${API}/corridas-parceiras/config`)
      ]);
      setCorridas(corridasRes.data);
      setStats(statsRes.data);
      setConfig(configRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { carregarDados(); }, [carregarDados]);

  const resetForm = () => {
    setForm({
      nome_evento: '', data_evento: '', cidade: '', estado: '',
      valor_inscricao: '', link_inscricao: '', link_resultado: '',
      link_fotos: '', link_instagram: '', imagem: null
    });
    setEditando(null);
  };

  const abrirModal = (corrida = null) => {
    if (corrida) {
      setEditando(corrida.id);
      setForm({
        nome_evento: corrida.nome_evento || '',
        data_evento: corrida.data_evento || '',
        cidade: corrida.cidade || '',
        estado: corrida.estado || '',
        valor_inscricao: corrida.valor_inscricao || '',
        link_inscricao: corrida.link_inscricao || '',
        link_resultado: corrida.link_resultado || '',
        link_fotos: corrida.link_fotos || '',
        link_instagram: corrida.link_instagram || '',
        imagem: null
      });
    } else {
      resetForm();
    }
    setModalAberto(true);
  };

  const salvarCorrida = async () => {
    if (!form.nome_evento || !form.data_evento || !form.cidade || !form.estado) {
      toast.error('Preencha os campos obrigatórios');
      return;
    }
    setSalvando(true);
    try {
      const formData = new FormData();
      Object.entries(form).forEach(([key, val]) => {
        if (key === 'imagem' && val) formData.append('imagem', val);
        else if (key !== 'imagem') formData.append(key, val || '');
      });

      if (editando) {
        await axios.put(`${API}/admin/corridas-parceiras/${editando}`, formData, {
          headers: { ...headers, 'Content-Type': 'multipart/form-data' }
        });
        toast.success('Corrida atualizada!');
      } else {
        await axios.post(`${API}/admin/corridas-parceiras`, formData, {
          headers: { ...headers, 'Content-Type': 'multipart/form-data' }
        });
        toast.success('Corrida criada!');
      }
      setModalAberto(false);
      resetForm();
      carregarDados();
    } catch (err) {
      toast.error('Erro ao salvar');
    } finally {
      setSalvando(false);
    }
  };

  const excluirCorrida = async (id) => {
    if (!window.confirm('Excluir esta corrida?')) return;
    try {
      await axios.delete(`${API}/admin/corridas-parceiras/${id}`, { headers });
      toast.success('Corrida excluída');
      carregarDados();
    } catch {
      toast.error('Erro ao excluir');
    }
  };

  const salvarConfig = async () => {
    try {
      const formData = new FormData();
      formData.append('link_whatsapp', config.link_whatsapp);
      formData.append('cupom_nome', config.cupom_nome);
      formData.append('cupom_descricao', config.cupom_descricao);
      await axios.put(`${API}/admin/corridas-parceiras/config`, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Configurações salvas!');
    } catch {
      toast.error('Erro ao salvar configurações');
    }
  };

  const totalClicksCorrida = (c) => {
    const cl = c.clicks || {};
    return (cl.inscricao || 0) + (cl.resultado || 0) + (cl.fotos || 0) + (cl.instagram || 0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="dashboard-corridas-parceiras">
      {/* Abas */}
      <div className="flex gap-2 border-b border-slate-700 pb-2">
        {[
          { id: 'corridas', label: 'Corridas', icon: MapPin },
          { id: 'config', label: 'Configuracoes', icon: Settings },
          { id: 'metricas', label: 'Metricas', icon: BarChart3 }
        ].map(aba => (
          <button
            key={aba.id}
            onClick={() => setAbaAtiva(aba.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg text-sm font-medium transition ${
              abaAtiva === aba.id
                ? 'bg-emerald-600 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-700'
            }`}
            data-testid={`tab-${aba.id}`}
          >
            <aba.icon className="w-4 h-4" />
            {aba.label}
          </button>
        ))}
      </div>

      {/* === ABA CORRIDAS === */}
      {abaAtiva === 'corridas' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white">Corridas Parceiras ({corridas.length})</h3>
            <Button onClick={() => abrirModal()} className="bg-emerald-600 hover:bg-emerald-700" data-testid="btn-nova-corrida">
              <Plus className="w-4 h-4 mr-2" /> Nova Corrida
            </Button>
          </div>

          {corridas.length === 0 ? (
            <Card className="p-8 text-center text-slate-400 bg-slate-800/50">
              Nenhuma corrida cadastrada. Clique em "Nova Corrida" para adicionar.
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {corridas.map(c => (
                <Card key={c.id} className="bg-slate-800/50 border-slate-700 overflow-hidden" data-testid={`corrida-card-${c.id}`}>
                  {c.imagem_url && (
                    <div className="aspect-square w-full overflow-hidden bg-slate-900">
                      <img
                        src={`${BACKEND_URL}${c.imagem_url}`}
                        alt={c.nome_evento}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div className="p-4 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-xs text-slate-400">Data: {c.data_evento}</p>
                        <h4 className="font-bold text-white text-sm">{c.nome_evento}</h4>
                        <p className="text-xs text-slate-400">{c.cidade}/{c.estado}</p>
                      </div>
                      <span className="text-emerald-400 font-bold text-sm whitespace-nowrap">{c.valor_inscricao}</span>
                    </div>

                    <div className="flex items-center gap-1 text-xs text-slate-500">
                      <MousePointer className="w-3 h-3" />
                      {totalClicksCorrida(c)} clicks totais
                    </div>

                    <div className="flex gap-2 pt-2 border-t border-slate-700">
                      <Button size="sm" variant="outline" onClick={() => abrirModal(c)} className="flex-1 text-xs border-slate-600">
                        <Pencil className="w-3 h-3 mr-1" /> Editar
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => excluirCorrida(c.id)} className="text-xs border-red-800 text-red-400 hover:bg-red-900/30">
                        <Trash2 className="w-3 h-3 mr-1" /> Excluir
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* === ABA CONFIGURAÇÕES === */}
      {abaAtiva === 'config' && (
        <div className="space-y-4 max-w-lg">
          <h3 className="text-lg font-bold text-white">Configuracoes da Pagina</h3>

          <Card className="bg-slate-800/50 border-slate-700 p-4 space-y-4">
            <div>
              <Label className="text-slate-300">Link WhatsApp (botao "CLICK AQUI")</Label>
              <Input
                value={config.link_whatsapp}
                onChange={e => setConfig({ ...config, link_whatsapp: e.target.value })}
                placeholder="https://wa.me/5577998626875"
                className="bg-slate-900 border-slate-600"
                data-testid="input-link-whatsapp"
              />
              <p className="text-xs text-slate-500 mt-1">Formato: https://wa.me/NUMERO</p>
            </div>

            <div>
              <Label className="text-slate-300">Nome do Cupom</Label>
              <Input
                value={config.cupom_nome}
                onChange={e => setConfig({ ...config, cupom_nome: e.target.value })}
                placeholder="RANKINGRUN10"
                className="bg-slate-900 border-slate-600 font-bold"
                data-testid="input-cupom-nome"
              />
            </div>

            <div>
              <Label className="text-slate-300">Descricao do Cupom</Label>
              <Input
                value={config.cupom_descricao}
                onChange={e => setConfig({ ...config, cupom_descricao: e.target.value })}
                placeholder="Use Nosso Cupom e Pague Menos"
                className="bg-slate-900 border-slate-600"
                data-testid="input-cupom-descricao"
              />
            </div>

            <Button onClick={salvarConfig} className="bg-emerald-600 hover:bg-emerald-700 w-full" data-testid="btn-salvar-config">
              <Save className="w-4 h-4 mr-2" /> Salvar Configuracoes
            </Button>
          </Card>
        </div>
      )}

      {/* === ABA MÉTRICAS === */}
      {abaAtiva === 'metricas' && stats && (
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-white">Metricas de Clicks</h3>

          {/* Cards resumo */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Card className="bg-slate-800/50 border-slate-700 p-4 text-center">
              <p className="text-2xl font-bold text-emerald-400">{stats.total_corridas}</p>
              <p className="text-xs text-slate-400">Corridas</p>
            </Card>
            <Card className="bg-slate-800/50 border-slate-700 p-4 text-center">
              <p className="text-2xl font-bold text-blue-400">{stats.total_clicks}</p>
              <p className="text-xs text-slate-400">Clicks Totais</p>
            </Card>
            <Card className="bg-slate-800/50 border-slate-700 p-4 text-center">
              <p className="text-2xl font-bold text-orange-400">{stats.clicks_por_tipo?.inscricao || 0}</p>
              <p className="text-xs text-slate-400">Inscricoes</p>
            </Card>
            <Card className="bg-slate-800/50 border-slate-700 p-4 text-center">
              <p className="text-2xl font-bold text-pink-400">{stats.clicks_por_tipo?.instagram || 0}</p>
              <p className="text-xs text-slate-400">Instagram</p>
            </Card>
          </div>

          {/* Top corridas */}
          <Card className="bg-slate-800/50 border-slate-700 p-4">
            <h4 className="font-semibold text-white mb-3">Top Corridas por Clicks</h4>
            {stats.top_corridas?.length > 0 ? (
              <div className="space-y-2">
                {stats.top_corridas.map((c, i) => {
                  const total = Object.values(c.clicks || {}).reduce((a, b) => a + b, 0);
                  return (
                    <div key={c.id} className="flex items-center justify-between p-2 rounded bg-slate-900/50">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-500 w-5">#{i + 1}</span>
                        <span className="text-sm text-white">{c.nome_evento}</span>
                      </div>
                      <span className="text-sm font-bold text-emerald-400">{total} clicks</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-slate-500">Nenhum click registrado ainda.</p>
            )}
          </Card>

          {/* Clicks por região */}
          <Card className="bg-slate-800/50 border-slate-700 p-4">
            <h4 className="font-semibold text-white mb-3">Clicks por Regiao</h4>
            {stats.clicks_por_regiao?.length > 0 ? (
              <div className="space-y-2">
                {stats.clicks_por_regiao.map((r, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-slate-900/50">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      <span className="text-sm text-white">{r.cidade || '?'}/{r.estado || '?'}</span>
                    </div>
                    <span className="text-sm font-bold text-blue-400">{r.total}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">Nenhum click por regiao registrado.</p>
            )}
          </Card>
        </div>
      )}

      {/* === MODAL CRIAR/EDITAR === */}
      <Dialog open={modalAberto} onOpenChange={setModalAberto}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto" data-testid="modal-corrida">
          <DialogHeader>
            <DialogTitle>{editando ? 'Editar Corrida' : 'Nova Corrida Parceira'}</DialogTitle>
          </DialogHeader>

          <div className="space-y-3">
            <div>
              <Label>Imagem do Evento (1:1)</Label>
              <label className="flex items-center justify-center gap-2 p-6 border-2 border-dashed border-slate-300 rounded-lg cursor-pointer hover:bg-slate-50 transition">
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={e => setForm({ ...form, imagem: e.target.files[0] })}
                />
                {form.imagem ? (
                  <span className="text-sm text-emerald-600 flex items-center gap-2">
                    <Image className="w-4 h-4" /> {form.imagem.name}
                  </span>
                ) : (
                  <span className="text-sm text-slate-500 flex items-center gap-2">
                    <Image className="w-4 h-4" /> Selecionar imagem
                  </span>
                )}
              </label>
            </div>

            <div>
              <Label>Nome do Evento *</Label>
              <Input
                value={form.nome_evento}
                onChange={e => setForm({ ...form, nome_evento: e.target.value })}
                placeholder="Ex: Corrida dos Ventos"
                data-testid="input-nome-evento"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Data do Evento *</Label>
                <Input
                  value={form.data_evento}
                  onChange={e => setForm({ ...form, data_evento: e.target.value })}
                  placeholder="26/06/2026"
                  data-testid="input-data-evento"
                />
              </div>
              <div>
                <Label>Valor da Inscricao</Label>
                <Input
                  value={form.valor_inscricao}
                  onChange={e => setForm({ ...form, valor_inscricao: e.target.value })}
                  placeholder="R$ 90,00"
                  data-testid="input-valor-inscricao"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Cidade *</Label>
                <Input
                  value={form.cidade}
                  onChange={e => setForm({ ...form, cidade: e.target.value })}
                  placeholder="Caetite"
                  data-testid="input-cidade-evento"
                />
              </div>
              <div>
                <Label>Estado *</Label>
                <Select value={form.estado} onValueChange={v => setForm({ ...form, estado: v })}>
                  <SelectTrigger data-testid="select-estado-evento"><SelectValue placeholder="UF" /></SelectTrigger>
                  <SelectContent>
                    {ESTADOS_BR.map(uf => <SelectItem key={uf} value={uf}>{uf}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label className="flex items-center gap-1"><Link2 className="w-3 h-3" /> Link Inscricao</Label>
              <Input
                value={form.link_inscricao}
                onChange={e => setForm({ ...form, link_inscricao: e.target.value })}
                placeholder="https://..."
              />
            </div>
            <div>
              <Label className="flex items-center gap-1"><Link2 className="w-3 h-3" /> Link Resultado</Label>
              <Input
                value={form.link_resultado}
                onChange={e => setForm({ ...form, link_resultado: e.target.value })}
                placeholder="https://..."
              />
            </div>
            <div>
              <Label className="flex items-center gap-1"><Link2 className="w-3 h-3" /> Link Fotos</Label>
              <Input
                value={form.link_fotos}
                onChange={e => setForm({ ...form, link_fotos: e.target.value })}
                placeholder="https://..."
              />
            </div>
            <div>
              <Label className="flex items-center gap-1"><Link2 className="w-3 h-3" /> Link Instagram</Label>
              <Input
                value={form.link_instagram}
                onChange={e => setForm({ ...form, link_instagram: e.target.value })}
                placeholder="https://instagram.com/..."
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setModalAberto(false)}>Cancelar</Button>
            <Button onClick={salvarCorrida} disabled={salvando} className="bg-emerald-600 hover:bg-emerald-700" data-testid="btn-salvar-corrida">
              {salvando ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
              {salvando ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardCorridasParceiras;
