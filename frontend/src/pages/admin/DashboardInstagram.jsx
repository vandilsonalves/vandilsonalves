// /app/frontend/src/pages/admin/DashboardInstagram.jsx
// Ranking Run Inside - Análise Manual de Perfis Instagram (Social Blade)

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
  Instagram, Loader2, Activity, TrendingUp, TrendingDown, Users,
  Heart, MessageCircle, BarChart3, Eye, Trash2, Download, Plus, Target,
  ArrowUp, ArrowDown, Camera, Calendar, Star, Zap, Film
} from 'lucide-react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar as RechartsRadar,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, LineChart, Line, RadialBarChart, RadialBar
} from 'recharts';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const NOTA_COLORS = {
  'A++': '#059669', 'A+': '#10B981', 'A': '#22C55E',
  'B+': '#3B82F6', 'B': '#60A5FA',
  'C+': '#F59E0B', 'C': '#FBBF24',
  'D': '#F97316', 'E': '#EF4444', 'F': '#DC2626'
};

const NOTA_BG = {
  'A++': 'bg-emerald-600', 'A+': 'bg-emerald-500', 'A': 'bg-green-500',
  'B+': 'bg-blue-500', 'B': 'bg-blue-400',
  'C+': 'bg-yellow-500', 'C': 'bg-yellow-400',
  'D': 'bg-orange-500', 'E': 'bg-red-500', 'F': 'bg-red-700'
};

const METRICA_COLORS = {
  'Excelente': 'text-emerald-400', 'Ótimo': 'text-green-400',
  'Bom': 'text-blue-400', 'Regular': 'text-yellow-400', 'Péssimo': 'text-red-400'
};

const CHART_COLORS = ['#EC4899', '#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

const INITIAL_FORM = {
  username: '', nome_completo: '', data_analise: new Date().toISOString().split('T')[0],
  seguidores: '', seguindo: '', total_posts: '',
  nota: 'C', classificacao_sb: '', classificacao_seguidores: '',
  ganho_seguidores_30d: '', perda_seguidores_30d: '',
  media_semanal_ganho: '', media_semanal_perda: '',
  posts_30d: '', media_semanal_posts: '',
  views_reels_6: '', curtidas_medias: '', comentarios_medios: '',
  foto_url: ''
};

const DashboardInstagram = ({ token }) => {
  const [analises, setAnalises] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({ ...INITIAL_FORM });

  const fetchAnalises = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/admin/instagram/analises`, { headers: { Authorization: `Bearer ${token}` } });
      setAnalises(r.data || []);
    } catch { /* silent */ }
  }, [token]);

  useEffect(() => { fetchAnalises(); }, [fetchAnalises]);

  const F = (k, v) => setFormData(p => ({ ...p, [k]: v }));

  // Upload foto
  const handleFotoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('foto', file);
      const r = await axios.post(`${API}/admin/instagram/upload-foto`, fd, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
      });
      F('foto_url', r.data.foto_url);
      toast.success('Foto enviada!');
    } catch { toast.error('Erro no upload da foto'); }
    finally { setUploading(false); }
  };

  // Submit análise
  const handleSubmit = async () => {
    if (!formData.username.trim()) { toast.error('Preencha o @username'); return; }
    if (!formData.seguidores) { toast.error('Preencha a quantidade de seguidores'); return; }
    setSubmitting(true);
    try {
      const payload = { ...formData };
      ['seguidores','seguindo','total_posts','ganho_seguidores_30d','perda_seguidores_30d','posts_30d','views_reels_6'].forEach(k => {
        payload[k] = parseInt(payload[k]) || 0;
      });
      ['media_semanal_ganho','media_semanal_perda','media_semanal_posts','curtidas_medias','comentarios_medios'].forEach(k => {
        payload[k] = parseFloat(payload[k]) || 0;
      });
      const r = await axios.post(`${API}/admin/instagram/analisar-simplificado`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResult(r.data);
      setShowForm(false);
      fetchAnalises();
      toast.success(`Análise de @${formData.username} concluída!`);
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

  const a = result?.analysis || {};
  const gd = result?.graficos_data || {};

  return (
    <div className="space-y-6" data-testid="dashboard-instagram">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-br from-pink-500 to-purple-600 rounded-xl">
            <Instagram className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Ranking Run Inside</h2>
            <p className="text-slate-500 text-sm">Análise manual de perfis (Social Blade)</p>
          </div>
        </div>
        <Button onClick={() => { setFormData({ ...INITIAL_FORM }); setShowForm(true); }} className="bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600" data-testid="btn-nova-analise">
          <Plus className="w-4 h-4 mr-2" /> Nova Análise
        </Button>
      </div>

      {/* ==================== RESULTADO DA ANÁLISE ==================== */}
      {result && <ResultadoAnalise a={a} gd={gd} token={token} onClose={() => setResult(null)} />}

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
                <Button onClick={() => { setFormData({ ...INITIAL_FORM }); setShowForm(true); }} className="mt-4" variant="outline">
                  <Plus className="w-4 h-4 mr-2" />Criar primeira análise
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {analises.map(item => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" data-testid={`analise-item-${item.id}`}>
                    <div className="flex items-center gap-3">
                      {item.foto_url && <img src={`${process.env.REACT_APP_BACKEND_URL}${item.foto_url}`} alt="" className="w-10 h-10 rounded-full object-cover border-2 border-pink-300" />}
                      <Badge className={`${NOTA_BG[item.nota] || NOTA_BG[item.nota_calc] || 'bg-slate-400'} text-white text-xs`}>{item.nota || item.nota_calc || '-'}</Badge>
                      <div>
                        <span className="font-semibold text-slate-800 dark:text-white">@{item.username}</span>
                        {item.nome_completo && <span className="text-slate-400 ml-1 text-sm">({item.nome_completo})</span>}
                        <div className="text-xs text-slate-500 flex gap-3 flex-wrap">
                          <span>{(item.seguidores || 0).toLocaleString()} seg.</span>
                          {item.engajamento_pct != null && <span>Eng: {item.engajamento_pct}%</span>}
                          {item.score_medio != null && <span>Score: {item.score_medio}/10</span>}
                          <span>{item.data_analise?.substring(0, 10)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button size="sm" variant="ghost" onClick={() => handleView(item.id)} data-testid={`view-${item.id}`}><Eye className="w-4 h-4" /></Button>
                      <Button size="sm" variant="ghost" className="text-red-500 hover:text-red-700" onClick={() => handleDelete(item.id)} data-testid={`delete-${item.id}`}><Trash2 className="w-4 h-4" /></Button>
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
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Instagram className="w-5 h-5 text-pink-500" />Nova Análise Manual (Social Blade)
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-5">
            {/* Seção 1: Identificação + Foto */}
            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg space-y-3">
              <h4 className="font-semibold text-sm text-slate-600 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2"><Camera className="w-4 h-4" />Identificação</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <Label>@Username *</Label>
                  <Input placeholder="cafvaassessoria" value={formData.username} onChange={e => F('username', e.target.value)} data-testid="input-username" />
                </div>
                <div>
                  <Label>Nome Completo</Label>
                  <Input placeholder="CAFVA Assessoria" value={formData.nome_completo} onChange={e => F('nome_completo', e.target.value)} data-testid="input-nome" />
                </div>
                <div>
                  <Label>Data da Análise</Label>
                  <Input type="date" value={formData.data_analise} onChange={e => F('data_analise', e.target.value)} data-testid="input-data" />
                </div>
              </div>
              {/* Upload Foto */}
              <div className="flex items-center gap-4">
                <div>
                  <Label>Foto de Perfil</Label>
                  <div className="flex items-center gap-3 mt-1">
                    <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 bg-pink-50 dark:bg-pink-900/30 border border-pink-200 dark:border-pink-800 rounded-lg text-pink-600 dark:text-pink-400 hover:bg-pink-100 transition text-sm font-medium" data-testid="btn-upload-foto">
                      {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Camera className="w-4 h-4" />}
                      {uploading ? 'Enviando...' : 'Escolher Foto'}
                      <input type="file" accept="image/*" className="hidden" onChange={handleFotoUpload} disabled={uploading} />
                    </label>
                    {formData.foto_url && (
                      <img src={`${process.env.REACT_APP_BACKEND_URL}${formData.foto_url}`} alt="Preview" className="w-12 h-12 rounded-full object-cover border-2 border-pink-400" />
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Seção 2: Dados Gerais do Perfil */}
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg space-y-3">
              <h4 className="font-semibold text-sm text-blue-600 dark:text-blue-300 uppercase tracking-wider flex items-center gap-2"><Users className="w-4 h-4" />Dados Gerais do Perfil</h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div><Label>Seguidores *</Label><Input type="number" placeholder="10000" value={formData.seguidores} onChange={e => F('seguidores', e.target.value)} data-testid="input-seguidores" /></div>
                <div><Label>Seguindo</Label><Input type="number" placeholder="500" value={formData.seguindo} onChange={e => F('seguindo', e.target.value)} data-testid="input-seguindo" /></div>
                <div><Label>Total de Posts</Label><Input type="number" placeholder="350" value={formData.total_posts} onChange={e => F('total_posts', e.target.value)} data-testid="input-posts" /></div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div>
                  <Label>Nota (A++ a F)</Label>
                  <select className="w-full h-10 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm" value={formData.nota} onChange={e => F('nota', e.target.value)} data-testid="select-nota">
                    {['A++','A+','A','B+','B','C+','C','D','E','F'].map(n => <option key={n} value={n}>{n}</option>)}
                  </select>
                </div>
                <div><Label>Classificação SB</Label><Input placeholder="Ex: B+" value={formData.classificacao_sb} onChange={e => F('classificacao_sb', e.target.value)} data-testid="input-classif-sb" /></div>
                <div><Label>Classif. Seguidores</Label><Input placeholder="Ex: Micro-influencer" value={formData.classificacao_seguidores} onChange={e => F('classificacao_seguidores', e.target.value)} data-testid="input-classif-seg" /></div>
              </div>
            </div>

            {/* Seção 3: Crescimento de Seguidores (30d) */}
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg space-y-3">
              <h4 className="font-semibold text-sm text-green-600 dark:text-green-300 uppercase tracking-wider flex items-center gap-2"><TrendingUp className="w-4 h-4" />Crescimento de Seguidores (30 dias)</h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div><Label>Ganho 30d</Label><Input type="number" placeholder="800" value={formData.ganho_seguidores_30d} onChange={e => F('ganho_seguidores_30d', e.target.value)} data-testid="input-ganho" /></div>
                <div><Label>Perda 30d</Label><Input type="number" placeholder="100" value={formData.perda_seguidores_30d} onChange={e => F('perda_seguidores_30d', e.target.value)} data-testid="input-perda" /></div>
                <div><Label>Média Semanal Ganho</Label><Input type="number" step="0.1" placeholder="200" value={formData.media_semanal_ganho} onChange={e => F('media_semanal_ganho', e.target.value)} data-testid="input-med-ganho" /></div>
                <div><Label>Média Semanal Perda</Label><Input type="number" step="0.1" placeholder="25" value={formData.media_semanal_perda} onChange={e => F('media_semanal_perda', e.target.value)} data-testid="input-med-perda" /></div>
              </div>
            </div>

            {/* Seção 4: Interações e Conteúdo (30d) */}
            <div className="p-4 bg-pink-50 dark:bg-pink-900/20 rounded-lg space-y-3">
              <h4 className="font-semibold text-sm text-pink-600 dark:text-pink-300 uppercase tracking-wider flex items-center gap-2"><Heart className="w-4 h-4" />Interações e Conteúdo (30 dias)</h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div><Label>Posts nos últimos 30d</Label><Input type="number" placeholder="20" value={formData.posts_30d} onChange={e => F('posts_30d', e.target.value)} data-testid="input-posts30" /></div>
                <div><Label>Média Semanal Posts</Label><Input type="number" step="0.1" placeholder="5" value={formData.media_semanal_posts} onChange={e => F('media_semanal_posts', e.target.value)} data-testid="input-med-posts" /></div>
                <div><Label>Views Reels (soma 6 últimos)</Label><Input type="number" placeholder="60000" value={formData.views_reels_6} onChange={e => F('views_reels_6', e.target.value)} data-testid="input-views-reels" /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><Label>Curtidas Médias / Post</Label><Input type="number" step="0.1" placeholder="350" value={formData.curtidas_medias} onChange={e => F('curtidas_medias', e.target.value)} data-testid="input-curtidas-med" /></div>
                <div><Label>Comentários Médios / Post</Label><Input type="number" step="0.1" placeholder="15" value={formData.comentarios_medios} onChange={e => F('comentarios_medios', e.target.value)} data-testid="input-coment-med" /></div>
              </div>
            </div>
          </div>

          <DialogFooter className="mt-4 gap-2">
            <Button variant="outline" onClick={() => setShowForm(false)}>Cancelar</Button>
            <Button onClick={handleSubmit} disabled={submitting} className="bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600" data-testid="btn-submit-analise">
              {submitting ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Analisando...</> : <><Activity className="w-4 h-4 mr-2" />Analisar Perfil</>}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ==================== COMPONENTE DE RESULTADO ====================
const ResultadoAnalise = ({ a, gd, token, onClose }) => {
  const scores = gd.scores || {};
  const fotoSrc = a.foto_url ? `${process.env.REACT_APP_BACKEND_URL}${a.foto_url}` : null;

  return (
    <div className="space-y-6" data-testid="resultado-analise">
      {/* Card Principal - Header escuro */}
      <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white border-0 shadow-2xl overflow-hidden">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              {fotoSrc && <img src={fotoSrc} alt={a.username} className="w-20 h-20 rounded-full object-cover border-4 border-pink-500 shadow-lg" data-testid="foto-perfil" />}
              <div>
                <div className="flex items-center gap-3 flex-wrap">
                  <h3 className="text-2xl font-bold" data-testid="username-result">@{a.username}</h3>
                  {a.nome_completo && <span className="text-slate-400">({a.nome_completo})</span>}
                  <Badge className={`text-lg px-3 py-1 ${NOTA_BG[a.nota] || NOTA_BG[a.nota_calc] || 'bg-slate-500'} text-white`} data-testid="nota-badge">{a.nota || a.nota_calc}</Badge>
                </div>
                <div className="flex gap-4 mt-1 text-sm text-slate-400 flex-wrap">
                  {a.classificacao_sb && <span>SB: {a.classificacao_sb}</span>}
                  {a.classificacao_seguidores && <span>Seg: {a.classificacao_seguidores}</span>}
                  {a.nota_nivel && <span>Nível: {a.nota_nivel}</span>}
                  <span>Data: {a.data_analise?.substring(0, 10)}</span>
                </div>
              </div>
            </div>

            {/* Gauge circular SVG - Score Médio */}
            <div className="relative w-32 h-32 shrink-0" data-testid="gauge-score">
              <svg viewBox="0 0 160 160" className="w-full h-full -rotate-90">
                <circle cx="80" cy="80" r="70" stroke="#334155" strokeWidth="12" fill="none" />
                <circle cx="80" cy="80" r="70"
                  stroke={scores.media >= 8 ? '#10B981' : scores.media >= 6 ? '#F59E0B' : '#EF4444'}
                  strokeWidth="12" fill="none"
                  strokeDasharray={`${(Math.min(scores.media || 0, 10) / 10) * 440} 440`}
                  strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">{scores.media || 0}</span>
                <span className="text-xs text-slate-400">SCORE</span>
              </div>
            </div>
          </div>

          {/* Grid de Métricas Rápidas */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-6">
            <MiniStat icon={Users} label="Seguidores" value={(a.seguidores || 0).toLocaleString()} color="text-pink-400" />
            <MiniStat icon={Zap} label="Engajamento" value={`${a.engajamento_pct || 0}%`} sub={gd.engajamento?.metrica} color="text-yellow-400" />
            <MiniStat icon={Heart} label="Taxa Curtidas" value={`${a.taxa_curtidas_pct || 0}%`} color="text-rose-400" />
            <MiniStat icon={TrendingUp} label="Crescimento" value={`${a.crescimento_pct || 0}%`} sub={gd.crescimento?.metrica} color="text-green-400" />
            <MiniStat icon={ArrowUp} label="Ganho 30d" value={`+${(a.ganho_seguidores_30d || 0).toLocaleString()}`} color="text-emerald-400" />
            <MiniStat icon={ArrowDown} label="Perda 30d" value={`-${(a.perda_seguidores_30d || 0).toLocaleString()}`} color="text-red-400" />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-3">
            <MiniStat icon={Heart} label="Curtidas/Post" value={a.curtidas_medias || 0} color="text-amber-400" />
            <MiniStat icon={MessageCircle} label="Coment./Post" value={a.comentarios_medios || 0} color="text-blue-400" />
            <MiniStat icon={Film} label="Views Reels" value={(a.media_views_reels || 0).toLocaleString()} color="text-purple-400" />
            <MiniStat icon={BarChart3} label="Posts 30d" value={a.posts_30d || 0} color="text-indigo-400" />
            <MiniStat icon={Activity} label="Posts/Semana" value={a.media_semanal_posts || 0} color="text-violet-400" />
            <MiniStat icon={Target} label="Saldo Seg." value={(a.saldo_seguidores || 0).toLocaleString()} color={a.saldo_seguidores >= 0 ? 'text-emerald-400' : 'text-red-400'} />
          </div>
        </CardContent>
      </Card>

      {/* ==================== 7 GRÁFICOS ==================== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* 1. CÍRCULO (Gauge/Donut) - NOTA / Taxa de Curtidas */}
        <GraficoNota gd={gd} a={a} />

        {/* 2. BARRAS HORIZONTAIS - Views de Reels */}
        <GraficoViewsReels gd={gd} />

        {/* 3. PIZZA - Engajamento */}
        <GraficoEngajamento gd={gd} />

        {/* 4. COLUNAS VERTICAIS - Curtidas Médias */}
        <GraficoCurtidas gd={gd} a={a} />

        {/* 5. LINHAS - Comentários Médios */}
        <GraficoComentarios gd={gd} a={a} />

        {/* 6. RADAR - Crescimento Mensal */}
        <GraficoCrescimento gd={gd} />

        {/* 7. HISTOGRAMA - Posts (30 dias) */}
        <GraficoPosts gd={gd} />
      </div>

      {/* Scores Consolidados */}
      {scores && (
        <Card className="border-2 border-purple-200 dark:border-purple-800">
          <CardHeader><CardTitle className="flex items-center gap-2"><Star className="w-5 h-5 text-purple-500" />Scores por Métrica</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              {[
                { label: 'Views Reels', val: scores.views, color: '#8B5CF6' },
                { label: 'Engajamento', val: scores.engajamento, color: '#EC4899' },
                { label: 'Curtidas', val: scores.curtidas, color: '#F59E0B' },
                { label: 'Comentários', val: scores.comentarios, color: '#3B82F6' },
                { label: 'Crescimento', val: scores.crescimento, color: '#10B981' },
                { label: 'Posts', val: scores.posts, color: '#EF4444' },
              ].map(s => (
                <div key={s.label} className="text-center p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
                  <div className="text-2xl font-bold" style={{ color: s.color }}>{s.val || 0}</div>
                  <div className="text-xs text-slate-500 mt-1">{s.label}</div>
                  <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 mt-2">
                    <div className="h-2 rounded-full transition-all" style={{ width: `${(s.val || 0) * 10}%`, backgroundColor: s.color }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="text-center mt-4 p-3 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl">
              <span className="text-sm text-slate-500">Score Médio Geral:</span>
              <span className="text-3xl font-bold ml-3" style={{ color: scores.media >= 8 ? '#10B981' : scores.media >= 6 ? '#F59E0B' : '#EF4444' }}>{scores.media || 0}/10</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Ações */}
      <div className="flex gap-3 justify-center flex-wrap">
        <Button onClick={() => window.open(`${API}/admin/instagram/export/${a.id}?token=${token}`, '_blank')} className="bg-emerald-600 hover:bg-emerald-700" data-testid="btn-export-xlsx">
          <Download className="w-4 h-4 mr-2" />Exportar XLSX
        </Button>
        <Button onClick={() => window.open(`${API}/admin/instagram/export-csv/${a.id}?token=${token}`, '_blank')} variant="outline" data-testid="btn-export-csv">
          <Download className="w-4 h-4 mr-2" />Exportar CSV
        </Button>
        <Button onClick={onClose} variant="outline" data-testid="btn-fechar-resultado">Fechar</Button>
      </div>
    </div>
  );
};

// ==================== SUB-COMPONENTES ====================

const MiniStat = ({ icon: Icon, label, value, sub, color }) => (
  <div className="bg-slate-700/50 p-3 rounded-xl text-center">
    <Icon className={`w-4 h-4 mx-auto mb-1 ${color}`} />
    <div className={`text-lg font-bold ${color}`}>{value}</div>
    <div className="text-xs text-slate-400">{label}</div>
    {sub && <div className={`text-xs font-semibold mt-0.5 ${METRICA_COLORS[sub] || 'text-slate-300'}`}>{sub}</div>}
  </div>
);

// 1. Gauge/Donut - NOTA
const GraficoNota = ({ gd, a }) => {
  const ng = gd.nota_gauge || {};
  const notaVal = ng.nota || a.nota || 'C';
  const cor = NOTA_COLORS[notaVal] || '#94A3B8';
  const notaNum = { 'A++': 100, 'A+': 90, 'A': 80, 'B+': 70, 'B': 60, 'C+': 50, 'C': 40, 'D': 30, 'E': 20, 'F': 10 };
  const pct = notaNum[notaVal] || 40;
  const data = [{ name: 'score', value: pct, fill: cor }, { name: 'rest', value: 100 - pct, fill: '#1E293B' }];

  return (
    <Card data-testid="grafico-nota">
      <CardHeader><CardTitle className="flex items-center gap-2"><Target className="w-5 h-5 text-amber-500" />1. Nota - Taxa de Curtidas (Donut)</CardTitle></CardHeader>
      <CardContent>
        <div className="flex items-center gap-6">
          <ResponsiveContainer width="60%" height={250}>
            <PieChart>
              <Pie data={data} cx="50%" cy="50%" innerRadius={65} outerRadius={95} startAngle={90} endAngle={-270} dataKey="value" stroke="none">
                {data.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Pie>
              <text x="50%" y="45%" textAnchor="middle" className="fill-current text-3xl font-bold" fill={cor}>{notaVal}</text>
              <text x="50%" y="60%" textAnchor="middle" className="fill-slate-400 text-xs" fill="#94A3B8">{ng.nivel || ''}</text>
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 text-sm">
            <div><span className="text-slate-500">Taxa Curtidas:</span> <span className="font-bold text-white">{ng.taxa_curtidas_pct || a.taxa_curtidas_pct || 0}%</span></div>
            <div><span className="text-slate-500">Nota Calc.:</span> <span className="font-bold" style={{ color: NOTA_COLORS[ng.nota_calc] || cor }}>{ng.nota_calc || '-'}</span></div>
            <div><span className="text-slate-500">Nota Manual:</span> <span className="font-bold" style={{ color: cor }}>{notaVal}</span></div>
            <div className="pt-2 border-t border-slate-700">
              <div className="text-xs text-slate-500">Escala: A++ (7%+) ... F (&lt;0.5%)</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// 2. Barras Horizontais - Views de Reels
const GraficoViewsReels = ({ gd }) => {
  const vr = gd.views_reels || {};
  const escala = vr.escala || [];
  const barData = escala.map(e => ({
    name: e.label,
    range: e.range,
    value: e.max - e.min,
    isActive: vr.taxa_views_pct >= e.min && vr.taxa_views_pct < (e.max === 200 ? Infinity : e.max)
  }));

  return (
    <Card data-testid="grafico-views-reels">
      <CardHeader><CardTitle className="flex items-center gap-2"><Film className="w-5 h-5 text-purple-500" />2. Views de Reels (Barras)</CardTitle></CardHeader>
      <CardContent>
        <div className="mb-4 flex items-center gap-4 flex-wrap">
          <div className="text-center"><span className="text-2xl font-bold text-purple-400">{(vr.media_views || 0).toLocaleString()}</span><div className="text-xs text-slate-500">Média Views</div></div>
          <div className="text-center"><span className="text-2xl font-bold text-purple-300">{vr.taxa_views_pct || 0}%</span><div className="text-xs text-slate-500">Taxa vs Seg.</div></div>
          <Badge className={`${METRICA_COLORS[vr.metrica] ? '' : 'bg-slate-500'} text-sm`} variant="outline">
            <span className={METRICA_COLORS[vr.metrica] || 'text-slate-400'}>{vr.metrica || '-'} ({vr.score || 0}/10)</span>
          </Badge>
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={barData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis type="number" tick={{ fill: '#94A3B8', fontSize: 11 }} />
            <YAxis dataKey="name" type="category" width={70} tick={{ fill: '#94A3B8', fontSize: 11 }} />
            <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8 }} />
            <Bar dataKey="value" radius={[0, 6, 6, 0]}>
              {barData.map((entry, i) => <Cell key={i} fill={entry.isActive ? '#8B5CF6' : '#475569'} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// 3. Pizza - Engajamento
const GraficoEngajamento = ({ gd }) => {
  const eng = gd.engajamento || {};
  const pieData = (eng.labels || []).map((l, i) => ({ name: l, value: eng.values?.[i] || 0 }));

  return (
    <Card data-testid="grafico-engajamento">
      <CardHeader><CardTitle className="flex items-center gap-2"><Heart className="w-5 h-5 text-pink-500" />3. Engajamento (Pizza)</CardTitle></CardHeader>
      <CardContent>
        <div className="mb-3 flex items-center gap-4 flex-wrap">
          <div><span className="text-2xl font-bold text-pink-400">{eng.taxa || 0}%</span><div className="text-xs text-slate-500">Taxa Engajamento</div></div>
          <Badge variant="outline"><span className={METRICA_COLORS[eng.metrica] || 'text-slate-400'}>{eng.metrica || '-'} ({eng.score || 0}/10)</span></Badge>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={90} paddingAngle={5} dataKey="value"
              label={({ name, value }) => `${name}: ${value.toLocaleString()}`}>
              {pieData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8 }} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// 4. Colunas Verticais - Curtidas Médias
const GraficoCurtidas = ({ gd, a }) => {
  const curt = gd.curtidas || {};
  const colData = [
    { name: 'Curtidas/Post', valor: curt.valor || a.curtidas_medias || 0 },
    { name: 'Taxa %', valor: curt.taxa || a.taxa_curtidas_pct || 0 },
  ];

  return (
    <Card data-testid="grafico-curtidas">
      <CardHeader><CardTitle className="flex items-center gap-2"><Heart className="w-5 h-5 text-amber-500" />4. Curtidas Médias (Colunas)</CardTitle></CardHeader>
      <CardContent>
        <div className="mb-3 flex items-center gap-4 flex-wrap">
          <div><span className="text-2xl font-bold text-amber-400">{(curt.valor || 0).toLocaleString()}</span><div className="text-xs text-slate-500">Curtidas/Post</div></div>
          <div><span className="text-2xl font-bold text-amber-300">{curt.taxa || 0}%</span><div className="text-xs text-slate-500">Taxa Curtidas</div></div>
          <Badge variant="outline"><span className={METRICA_COLORS[curt.metrica] || 'text-slate-400'}>{curt.metrica || '-'} ({curt.score || 0}/10)</span></Badge>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={colData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" tick={{ fill: '#94A3B8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} />
            <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8 }} />
            <Bar dataKey="valor" radius={[6, 6, 0, 0]}>
              <Cell fill="#F59E0B" />
              <Cell fill="#FB923C" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// 5. Linhas - Comentários Médios
const GraficoComentarios = ({ gd, a }) => {
  const coment = gd.comentarios || {};
  const taxa = coment.taxa || a.taxa_comentarios_pct || 0;
  const valor = coment.valor || a.comentarios_medios || 0;
  const lineData = [
    { name: 'Ref. Péssimo', taxa: 0.05, comentarios: valor * 0.2 },
    { name: 'Ref. Regular', taxa: 0.1, comentarios: valor * 0.5 },
    { name: 'Atual', taxa: taxa, comentarios: valor },
    { name: 'Ref. Bom', taxa: 0.3, comentarios: valor * 1.5 },
    { name: 'Ref. Excelente', taxa: 0.6, comentarios: valor * 3 },
  ];

  return (
    <Card data-testid="grafico-comentarios">
      <CardHeader><CardTitle className="flex items-center gap-2"><MessageCircle className="w-5 h-5 text-blue-500" />5. Comentários Médios (Linhas)</CardTitle></CardHeader>
      <CardContent>
        <div className="mb-3 flex items-center gap-4 flex-wrap">
          <div><span className="text-2xl font-bold text-blue-400">{valor}</span><div className="text-xs text-slate-500">Coment./Post</div></div>
          <div><span className="text-2xl font-bold text-blue-300">{taxa}%</span><div className="text-xs text-slate-500">Taxa</div></div>
          <Badge variant="outline"><span className={METRICA_COLORS[coment.metrica] || 'text-slate-400'}>{coment.metrica || '-'} ({coment.score || 0}/10)</span></Badge>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={lineData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" tick={{ fill: '#94A3B8', fontSize: 10 }} />
            <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} />
            <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8 }} />
            <Line type="monotone" dataKey="comentarios" stroke="#3B82F6" strokeWidth={3} dot={{ r: 5, fill: '#3B82F6' }} activeDot={{ r: 7 }} name="Comentários" />
            <Line type="monotone" dataKey="taxa" stroke="#60A5FA" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Taxa %" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// 6. Radar - Crescimento Mensal
const GraficoCrescimento = ({ gd }) => {
  const cresc = gd.crescimento || {};
  const radarData = (cresc.radar_labels || []).map((l, i) => ({
    metric: l, value: cresc.radar_values?.[i] || 0, fullMark: 10
  }));

  return (
    <Card data-testid="grafico-crescimento">
      <CardHeader><CardTitle className="flex items-center gap-2"><TrendingUp className="w-5 h-5 text-green-500" />6. Crescimento Mensal (Radar)</CardTitle></CardHeader>
      <CardContent>
        <div className="mb-3 flex items-center gap-4 flex-wrap">
          <div><span className="text-2xl font-bold text-green-400">{cresc.taxa || 0}%</span><div className="text-xs text-slate-500">Crescimento</div></div>
          <div><span className="text-lg font-bold" style={{ color: (cresc.saldo || 0) >= 0 ? '#10B981' : '#EF4444' }}>Saldo: {(cresc.saldo || 0) >= 0 ? '+' : ''}{(cresc.saldo || 0).toLocaleString()}</span></div>
          <Badge variant="outline"><span className={METRICA_COLORS[cresc.metrica] || 'text-slate-400'}>{cresc.metrica || '-'} ({cresc.score || 0}/10)</span></Badge>
        </div>
        {radarData.length > 0 && (
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: '#6B7280', fontSize: 10 }} />
              <RechartsRadar name="Métricas" dataKey="value" stroke="#10B981" fill="#10B981" fillOpacity={0.35} />
            </RadarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};

// 7. Histograma - Posts (30 dias)
const GraficoPosts = ({ gd }) => {
  const posts = gd.posts || {};
  const escala = posts.escala || [];
  const histData = escala.map(e => ({
    name: e.label,
    range: e.range,
    score: parseInt(e.score?.split('-')?.[1] || e.score, 10) || 0,
    isActive: (() => {
      const total = posts.total || 0;
      if (e.label === '30+') return total > 30;
      const [min, max] = e.label.split('-').map(Number);
      return total >= min && total <= max;
    })()
  }));

  return (
    <Card data-testid="grafico-posts">
      <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-red-500" />7. Posts nos últimos 30 dias (Histograma)</CardTitle></CardHeader>
      <CardContent>
        <div className="mb-3 flex items-center gap-4 flex-wrap">
          <div><span className="text-2xl font-bold text-red-400">{posts.total || 0}</span><div className="text-xs text-slate-500">Posts 30d</div></div>
          <div><span className="text-lg font-bold text-red-300">{posts.semanal || 0}/sem</span></div>
          <Badge variant="outline"><span className={METRICA_COLORS[posts.metrica] || 'text-slate-400'}>{posts.metrica || '-'} ({posts.score || 0}/10)</span></Badge>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={histData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" tick={{ fill: '#94A3B8', fontSize: 12 }} />
            <YAxis domain={[0, 10]} tick={{ fill: '#94A3B8', fontSize: 11 }} label={{ value: 'Score', angle: -90, position: 'insideLeft', fill: '#94A3B8', fontSize: 11 }} />
            <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8 }}
              formatter={(val, name, props) => [`Score: ${val}`, `Faixa: ${props.payload.range}`]} />
            <Bar dataKey="score" radius={[4, 4, 0, 0]}>
              {histData.map((entry, i) => <Cell key={i} fill={entry.isActive ? '#EF4444' : '#475569'} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default DashboardInstagram;
