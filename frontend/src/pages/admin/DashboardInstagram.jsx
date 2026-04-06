// /app/frontend/src/pages/admin/DashboardInstagram.jsx
// Ranking Run Inside - Análise de Perfis Instagram (estilo Social Blade)

import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import {
  Instagram, Search, Loader2, Activity, TrendingUp, TrendingDown, Users,
  Heart, MessageCircle, BarChart3, Eye, Trash2, Download, Plus, Award, Target, ArrowUp, ArrowDown
} from 'lucide-react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar as RechartsRadar,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell
} from 'recharts';

const API = process.env.REACT_APP_BACKEND_URL + '/api';
const COLORS_PIE = ['#EC4899', '#8B5CF6', '#3B82F6', '#10B981'];

const NOTA_COLORS = {
  'A++': 'bg-emerald-500', 'A+': 'bg-emerald-400', 'A': 'bg-green-500', 'A-': 'bg-green-400',
  'B+': 'bg-blue-500', 'B': 'bg-blue-400', 'B-': 'bg-sky-400',
  'C+': 'bg-yellow-500', 'C': 'bg-yellow-400', 'C-': 'bg-amber-400',
  'D+': 'bg-orange-500', 'D': 'bg-orange-400', 'D-': 'bg-red-400', 'F': 'bg-red-600'
};

const SELO_CONFIG = {
  'Elite': { color: 'bg-gradient-to-r from-amber-400 to-yellow-300 text-black', icon: '🔥' },
  'Destaque': { color: 'bg-gradient-to-r from-purple-500 to-pink-500 text-white', icon: '🚀' },
  'Forte': { color: 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white', icon: '⭐' },
  'Em crescimento': { color: 'bg-gradient-to-r from-green-500 to-emerald-500 text-white', icon: '📈' },
  'Baixo desempenho': { color: 'bg-slate-500 text-white', icon: '⚠️' }
};

const LABEL_COLORS = {
  'Excelente': 'text-emerald-500', 'Muito bom': 'text-green-500', 'Ótima': 'text-green-500',
  'Bom': 'text-green-400', 'Boa': 'text-green-400', 'Ok': 'text-yellow-500',
  'Normal': 'text-yellow-500', 'Ruim': 'text-orange-500', 'Fraco': 'text-orange-500',
  'Péssimo': 'text-red-500', 'Péssima': 'text-red-500'
};

const DashboardInstagram = ({ token }) => {
  const [analises, setAnalises] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    username: '', nome_completo: '', nicho: 'corrida', bio: '',
    seguidores: '', seguindo: '', total_posts: '',
    curtidas_30d: '', comentarios_30d: '',
    ganho_seguidores_30d: '', perda_seguidores_30d: '', posts_30d: ''
  });

  const fetchAnalises = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/admin/instagram/analises`, { headers: { Authorization: `Bearer ${token}` } });
      setAnalises(r.data || []);
    } catch { /* silent */ }
  }, [token]);

  useEffect(() => { fetchAnalises(); }, [fetchAnalises]);

  const handleSubmit = async () => {
    if (!formData.username.trim()) { toast.error('Preencha o @username'); return; }
    if (!formData.seguidores) { toast.error('Preencha a quantidade de seguidores'); return; }
    setSubmitting(true);
    try {
      const payload = { ...formData };
      Object.keys(payload).forEach(k => {
        if (['seguidores','seguindo','total_posts','curtidas_30d','comentarios_30d','ganho_seguidores_30d','perda_seguidores_30d','posts_30d'].includes(k)) {
          payload[k] = parseInt(payload[k]) || 0;
        }
      });
      const r = await axios.post(`${API}/admin/instagram/analisar-simplificado`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResult(r.data);
      setShowForm(false);
      fetchAnalises();
      toast.success(`Análise de @${formData.username} concluída! Nota: ${r.data.analysis.nota}`);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Erro ao analisar');
    } finally { setSubmitting(false); }
  };

  const handleView = async (id) => {
    try {
      const r = await axios.get(`${API}/admin/instagram/analises/${id}`, { headers: { Authorization: `Bearer ${token}` } });
      setResult(r.data);
    } catch { toast.error('Erro ao carregar análise'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Excluir esta análise?')) return;
    try {
      await axios.delete(`${API}/admin/instagram/analises/${id}`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Análise excluída');
      fetchAnalises();
      if (result?.analysis?.id === id) setResult(null);
    } catch { toast.error('Erro ao excluir'); }
  };

  const handleExport = (id, fmt) => {
    window.open(`${API}/admin/instagram/exportar/${id}/${fmt}?token=${token}`, '_blank');
  };

  const resetForm = () => setFormData({
    username: '', nome_completo: '', nicho: 'corrida', bio: '',
    seguidores: '', seguindo: '', total_posts: '',
    curtidas_30d: '', comentarios_30d: '',
    ganho_seguidores_30d: '', perda_seguidores_30d: '', posts_30d: ''
  });

  const F = (k, v) => setFormData(p => ({ ...p, [k]: v }));

  const a = result?.analysis || {};
  const gd = result?.graficos_data || {};

  return (
    <div className="space-y-6" data-testid="dashboard-instagram">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-br from-pink-500 to-purple-600 rounded-xl">
            <Instagram className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Ranking Run Inside</h2>
            <p className="text-slate-500 text-sm">Análise de perfis estilo Social Blade</p>
          </div>
        </div>
        <Button onClick={() => { resetForm(); setShowForm(true); }} className="bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600" data-testid="btn-nova-analise">
          <Plus className="w-4 h-4 mr-2" /> Nova Análise
        </Button>
      </div>

      {/* ==================== RESULTADO DA ANÁLISE ==================== */}
      {result && (
        <div className="space-y-6">
          {/* Card Principal - Header escuro */}
          <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white border-0 shadow-2xl overflow-hidden">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 flex-wrap">
                    <h3 className="text-2xl font-bold">@{a.username}</h3>
                    {a.nome_completo && <span className="text-slate-400">({a.nome_completo})</span>}
                    <Badge className={`text-lg px-3 py-1 ${NOTA_COLORS[a.nota] || 'bg-slate-500'} text-white`}>{a.nota}</Badge>
                    {a.selo && (() => { const s = SELO_CONFIG[a.selo] || {}; return <Badge className={`${s.color} px-3 py-1`}>{s.icon} {a.selo}</Badge>; })()}
                  </div>
                  <div className="flex gap-4 mt-2 text-sm text-slate-400">
                    <span>SB: {a.classificacao_sb}</span>
                    <span>Score: {a.score_sb}</span>
                    <span>Nicho: {a.nicho}</span>
                  </div>
                </div>
                {/* Gauge circular */}
                <div className="relative w-32 h-32 shrink-0">
                  <svg viewBox="0 0 160 160" className="w-full h-full -rotate-90">
                    <circle cx="80" cy="80" r="70" stroke="#334155" strokeWidth="12" fill="none" />
                    <circle cx="80" cy="80" r="70" stroke={a.score_sb >= 70 ? '#10B981' : a.score_sb >= 40 ? '#F59E0B' : '#EF4444'}
                      strokeWidth="12" fill="none" strokeDasharray={`${(Math.min(a.score_sb, 100) / 100) * 440} 440`}
                      strokeLinecap="round" />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold">{a.score_sb}</span>
                    <span className="text-xs text-slate-400">SCORE</span>
                  </div>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 mt-6">
                <StatCard icon={Users} label="Seguidores" value={(a.seguidores || 0).toLocaleString()} color="text-pink-400" />
                <StatCard icon={Heart} label="Engajamento" value={`${a.engajamento_pct || 0}%`} color="text-red-400" />
                <StatCard icon={Heart} label="Taxa Curtidas" value={`${a.taxa_curtidas_pct || 0}%`} sub={a.curtidas_label} subColor={LABEL_COLORS[a.curtidas_label]} color="text-rose-400" />
                <StatCard icon={TrendingUp} label="Crescimento" value={`${a.crescimento_pct || 0}%`} sub={a.crescimento_label} subColor={LABEL_COLORS[a.crescimento_label]} color="text-green-400" />
                <StatCard icon={Heart} label="Curtidas/Post" value={a.curtidas_medias || 0} color="text-amber-400" />
                <StatCard icon={MessageCircle} label="Coment./Post" value={a.comentarios_medios || 0} color="text-blue-400" />
              </div>

              {/* Métricas de Crescimento */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 mt-3">
                <StatCard icon={ArrowUp} label="Ganho 30d" value={`+${(a.ganho_seguidores_30d || 0).toLocaleString()}`} color="text-emerald-400" />
                <StatCard icon={ArrowDown} label="Perda 30d" value={`-${(a.perda_seguidores_30d || 0).toLocaleString()}`} color="text-red-400" />
                <StatCard icon={ArrowUp} label="Ganho/Sem." value={`+${a.ganho_semanal || 0}`} color="text-emerald-300" />
                <StatCard icon={ArrowDown} label="Perda/Sem." value={`-${a.perda_semanal || 0}`} color="text-red-300" />
                <StatCard icon={BarChart3} label="Posts 30d" value={a.posts_30d || 0} color="text-indigo-400" />
                <StatCard icon={BarChart3} label="Posts/Sem." value={a.posts_semanais || 0} color="text-violet-400" />
              </div>

              {/* Classificações */}
              <div className="flex flex-wrap gap-3 mt-4">
                <ClassifBadge label="Seguidores" value={a.classificacao_seguidores} />
                <ClassifBadge label="Curtidas" value={a.curtidas_label} />
                <ClassifBadge label="Crescimento" value={a.crescimento_label} />
                <ClassifBadge label="Seguindo/Seguidores" value={a.ratio_seguindo_seguidores ? `${(a.ratio_seguindo_seguidores * 100).toFixed(1)}%` : '0%'} />
              </div>
            </CardContent>
          </Card>

          {/* Gráficos */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Radar */}
            {gd.radar && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><Target className="w-5 h-5 text-purple-500" />Radar de Métricas</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={gd.radar.labels.map((l, i) => ({ metric: l, value: gd.radar.values[i], fullMark: 10 }))}>
                      <PolarGrid stroke="#E5E7EB" /><PolarAngleAxis dataKey="metric" tick={{ fill: '#6B7280', fontSize: 11 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: '#9CA3AF', fontSize: 10 }} />
                      <RechartsRadar name="Perfil" dataKey="value" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.4} />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {/* Barras - Métricas Principais */}
            {gd.barras_metricas && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-blue-500" />Métricas Principais</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={gd.barras_metricas.labels.map((l, i) => ({ name: l, valor: gd.barras_metricas.values[i] }))} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" /><XAxis type="number" /><YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 12 }} />
                      <Tooltip /><Bar dataKey="valor" fill="#3B82F6" radius={[0, 6, 6, 0]}>
                        {gd.barras_metricas.values.map((v, i) => <Cell key={i} fill={['#EC4899', '#8B5CF6', '#10B981', '#F59E0B'][i]} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {/* Pizza - Distribuição Curtidas vs Comentários */}
            {gd.pizza_distribuicao && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><Heart className="w-5 h-5 text-pink-500" />Interações (30 dias)</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie data={gd.pizza_distribuicao.labels.map((l, i) => ({ name: l, value: gd.pizza_distribuicao.values[i] }))}
                        cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value"
                        label={({ name, value }) => `${name}: ${value.toLocaleString()}`}>
                        {gd.pizza_distribuicao.labels.map((_, i) => <Cell key={i} fill={COLORS_PIE[i]} />)}
                      </Pie>
                      <Tooltip /><Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {/* Barras Agrupadas - Crescimento Semanal */}
            {gd.crescimento_semanal && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><TrendingUp className="w-5 h-5 text-green-500" />Crescimento Semanal</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={gd.crescimento_semanal.labels.map((l, i) => ({
                      name: l, ganho: gd.crescimento_semanal.ganho[i], perda: gd.crescimento_semanal.perda[i]
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Legend />
                      <Bar dataKey="ganho" name="Ganho" fill="#10B981" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="perda" name="Perda" fill="#EF4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Ações */}
          <div className="flex gap-3 justify-center flex-wrap">
            <Button onClick={() => handleExport(a.id, 'xlsx')} className="bg-emerald-600 hover:bg-emerald-700"><Download className="w-4 h-4 mr-2" />Exportar XLSX</Button>
            <Button onClick={() => handleExport(a.id, 'csv')} variant="outline"><Download className="w-4 h-4 mr-2" />Exportar CSV</Button>
            <Button onClick={() => setResult(null)} variant="outline">Fechar</Button>
          </div>
        </div>
      )}

      {/* ==================== LISTA DE ANÁLISES ==================== */}
      {!result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Activity className="w-5 h-5 text-pink-500" />Análises Realizadas ({analises.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {analises.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Instagram className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>Nenhuma análise realizada ainda.</p>
                <Button onClick={() => { resetForm(); setShowForm(true); }} className="mt-4" variant="outline">
                  <Plus className="w-4 h-4 mr-2" />Criar primeira análise
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {analises.map(item => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                    <div className="flex items-center gap-3">
                      <Badge className={`${NOTA_COLORS[item.nota] || 'bg-slate-400'} text-white text-xs`}>{item.nota || item.classificacao || '-'}</Badge>
                      <div>
                        <span className="font-semibold text-slate-800 dark:text-white">@{item.username}</span>
                        <div className="text-xs text-slate-500 flex gap-3">
                          <span>{(item.seguidores || 0).toLocaleString()} seg.</span>
                          {item.engajamento_pct != null && <span>Eng: {item.engajamento_pct}%</span>}
                          {item.classificacao_sb && <span>SB: {item.classificacao_sb}</span>}
                          <span>{item.data_analise?.substring(0, 10)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="ghost" onClick={() => handleView(item.id)} data-testid={`view-${item.id}`}><Eye className="w-4 h-4" /></Button>
                      <Button size="sm" variant="ghost" className="text-red-500" onClick={() => handleDelete(item.id)}><Trash2 className="w-4 h-4" /></Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ==================== FORMULÁRIO MODAL ==================== */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Instagram className="w-5 h-5 text-pink-500" />Nova Análise - Dados Manuais (Social Blade)
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-5">
            {/* Identificação */}
            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg space-y-3">
              <h4 className="font-semibold text-sm text-slate-600 dark:text-slate-300 uppercase tracking-wider">Identificação</h4>
              <div className="grid grid-cols-2 gap-3">
                <div><Label>@Username *</Label><Input placeholder="cafvaassessoria" value={formData.username} onChange={e => F('username', e.target.value)} data-testid="input-username" /></div>
                <div><Label>Nome Completo</Label><Input placeholder="CAFVA Assessoria" value={formData.nome_completo} onChange={e => F('nome_completo', e.target.value)} /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><Label>Nicho</Label>
                  <select className="w-full h-10 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm" value={formData.nicho} onChange={e => F('nicho', e.target.value)}>
                    <option value="corrida">Corrida</option><option value="fitness">Fitness</option><option value="lifestyle">Lifestyle</option>
                  </select>
                </div>
                <div><Label>Bio</Label><Input placeholder="Corredor | Maratonista" value={formData.bio} onChange={e => F('bio', e.target.value)} /></div>
              </div>
            </div>

            {/* Dados Gerais */}
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg space-y-3">
              <h4 className="font-semibold text-sm text-blue-600 dark:text-blue-300 uppercase tracking-wider">Dados Gerais do Perfil</h4>
              <div className="grid grid-cols-3 gap-3">
                <div><Label>Seguidores *</Label><Input type="number" placeholder="10000" value={formData.seguidores} onChange={e => F('seguidores', e.target.value)} data-testid="input-seguidores" /></div>
                <div><Label>Seguindo</Label><Input type="number" placeholder="500" value={formData.seguindo} onChange={e => F('seguindo', e.target.value)} /></div>
                <div><Label>Total de Posts</Label><Input type="number" placeholder="350" value={formData.total_posts} onChange={e => F('total_posts', e.target.value)} /></div>
              </div>
            </div>

            {/* Interações 30 dias */}
            <div className="p-4 bg-pink-50 dark:bg-pink-900/20 rounded-lg space-y-3">
              <h4 className="font-semibold text-sm text-pink-600 dark:text-pink-300 uppercase tracking-wider">Interações (Últimos 30 dias)</h4>
              <div className="grid grid-cols-3 gap-3">
                <div><Label>Curtidas (30d)</Label><Input type="number" placeholder="3000" value={formData.curtidas_30d} onChange={e => F('curtidas_30d', e.target.value)} /></div>
                <div><Label>Comentários (30d)</Label><Input type="number" placeholder="200" value={formData.comentarios_30d} onChange={e => F('comentarios_30d', e.target.value)} /></div>
                <div><Label>Posts (30d)</Label><Input type="number" placeholder="20" value={formData.posts_30d} onChange={e => F('posts_30d', e.target.value)} /></div>
              </div>
            </div>

            {/* Crescimento */}
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg space-y-3">
              <h4 className="font-semibold text-sm text-green-600 dark:text-green-300 uppercase tracking-wider">Crescimento de Seguidores (30 dias)</h4>
              <div className="grid grid-cols-2 gap-3">
                <div><Label>Seguidores Ganhos</Label><Input type="number" placeholder="800" value={formData.ganho_seguidores_30d} onChange={e => F('ganho_seguidores_30d', e.target.value)} /></div>
                <div><Label>Seguidores Perdidos</Label><Input type="number" placeholder="100" value={formData.perda_seguidores_30d} onChange={e => F('perda_seguidores_30d', e.target.value)} /></div>
              </div>
            </div>
          </div>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setShowForm(false)}>Cancelar</Button>
            <Button onClick={handleSubmit} disabled={submitting} className="bg-gradient-to-r from-pink-500 to-purple-500">
              {submitting ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Analisando...</> : <><Activity className="w-4 h-4 mr-2" />Analisar Perfil</>}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Sub-componentes
const StatCard = ({ icon: Icon, label, value, sub, subColor, color }) => (
  <div className="bg-slate-700/50 p-3 rounded-xl text-center">
    <Icon className={`w-4 h-4 mx-auto mb-1 ${color}`} />
    <div className={`text-lg font-bold ${color}`}>{value}</div>
    <div className="text-xs text-slate-400">{label}</div>
    {sub && <div className={`text-xs font-semibold mt-0.5 ${subColor || 'text-slate-300'}`}>{sub}</div>}
  </div>
);

const ClassifBadge = ({ label, value }) => {
  const color = LABEL_COLORS[value] || 'text-slate-400';
  return (
    <div className="bg-slate-700/30 px-3 py-1.5 rounded-full text-sm">
      <span className="text-slate-400">{label}: </span>
      <span className={`font-semibold ${color}`}>{value || '-'}</span>
    </div>
  );
};

export default DashboardInstagram;
