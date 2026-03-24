import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import {
  Activity, Search, Eye, Trash2, Download, FileText, RefreshCw, Loader2,
  TrendingUp, BarChart3, PieChart, AlertCircle
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart as RechartsPie, Pie, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar as RechartsRadar
} from 'recharts';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getClassificacaoColor = (classificacao) => {
  const colors = {
    'Elite Platinum': 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white',
    'Elite Gold': 'bg-gradient-to-r from-yellow-500 to-amber-500 text-white',
    'Premium': 'bg-gradient-to-r from-purple-500 to-violet-500 text-white',
    'Profissional': 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white',
    'Regular': 'bg-gradient-to-r from-slate-500 to-gray-500 text-white',
    'Alto Risco': 'bg-gradient-to-r from-red-500 to-rose-500 text-white'
  };
  return colors[classificacao] || 'bg-slate-500 text-white';
};

const DashboardInstagram = ({ token }) => {
  const [instagramAnalises, setInstagramAnalises] = useState([]);
  const [loadingInstagram, setLoadingInstagram] = useState(false);
  const [showInstagramForm, setShowInstagramForm] = useState(false);
  const [instagramResult, setInstagramResult] = useState(null);
  const [instagramSearchUsername, setInstagramSearchUsername] = useState('');
  const [instagramSearchLoading, setInstagramSearchLoading] = useState(false);
  const [instagramSearchError, setInstagramSearchError] = useState('');
  const [instagramFormData, setInstagramFormData] = useState({
    username: '', nome_completo: '', nicho: 'corrida',
    seguidores: '', seguindo: '', total_posts: '', bio: ''
  });

  useEffect(() => { fetchInstagramAnalises(); }, []);

  const fetchInstagramAnalises = async () => {
    setLoadingInstagram(true);
    try {
      const response = await axios.get(`${API}/admin/instagram/analises`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInstagramAnalises(response.data);
    } catch (error) {
      console.error('Erro ao buscar análises Instagram:', error);
    } finally {
      setLoadingInstagram(false);
    }
  };

  const handleInstagramSearch = async () => {
    if (!instagramSearchUsername.trim()) { toast.error('Digite o @username do perfil'); return; }
    setInstagramSearchLoading(true);
    setInstagramSearchError('');
    try {
      const cleanUsername = instagramSearchUsername.trim().replace('@', '');
      const response = await axios.post(
        `${API}/admin/instagram/analisar-automatico/${cleanUsername}?nicho=${instagramFormData.nicho}`,
        {}, { headers: { Authorization: `Bearer ${token}` } }
      );
      setInstagramResult(response.data);
      setInstagramSearchUsername('');
      fetchInstagramAnalises();
      toast.success(`@${cleanUsername}: Score ${response.data.analysis.score_final}/100 - ${response.data.analysis.classificacao}`);
    } catch (error) {
      const errorMsg = typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail : 'Não foi possível analisar o perfil.';
      setInstagramSearchError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setInstagramSearchLoading(false);
    }
  };

  const handleInstagramAnalyze = async () => {
    const required = ['username', 'seguidores', 'seguindo', 'total_posts'];
    if (required.some(f => !instagramFormData[f])) {
      toast.error('Preencha: Username, Seguidores, Seguindo e Total de Posts');
      return;
    }
    setLoadingInstagram(true);
    try {
      const payload = {
        username: instagramFormData.username, nome_completo: instagramFormData.nome_completo || '',
        nicho: instagramFormData.nicho || 'corrida',
        seguidores: parseInt(instagramFormData.seguidores) || 0,
        seguindo: parseInt(instagramFormData.seguindo) || 0,
        total_posts: parseInt(instagramFormData.total_posts) || 0,
        bio: instagramFormData.bio || ''
      };
      const response = await axios.post(`${API}/admin/instagram/analisar-simplificado`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInstagramResult(response.data);
      setShowInstagramForm(false);
      fetchInstagramAnalises();
      toast.success(`Score: ${response.data.analysis.score_final}/100 - ${response.data.analysis.classificacao}`);
    } catch (error) {
      let errorMsg = 'Erro ao analisar perfil';
      if (typeof error.response?.data?.detail === 'string') errorMsg = error.response.data.detail;
      toast.error(errorMsg);
    } finally {
      setLoadingInstagram(false);
    }
  };

  const handleDeleteInstagramAnalysis = async (analysisId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta análise?')) return;
    try {
      await axios.delete(`${API}/admin/instagram/analises/${analysisId}`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Análise excluída!');
      fetchInstagramAnalises();
      if (instagramResult?.analysis?.id === analysisId) setInstagramResult(null);
    } catch { toast.error('Erro ao excluir análise'); }
  };

  const handleExportInstagram = (analysisId, format) => {
    const endpoint = format === 'xlsx'
      ? `${API}/admin/instagram/export/${analysisId}`
      : `${API}/admin/instagram/export-csv/${analysisId}`;
    window.open(endpoint + `?token=${token}`, '_blank');
  };

  const resetInstagramForm = () => {
    setInstagramFormData({ username: '', nome_completo: '', nicho: 'corrida', seguidores: '', seguindo: '', total_posts: '', bio: '' });
    setInstagramResult(null);
  };

  return (
    <div className="space-y-6" data-testid="dashboard-instagram">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Activity className="w-6 h-6 text-pink-500" /> Ranking Run Inside
          </h2>
          <p className="text-slate-500">Análise de Perfis Instagram - Sistema de Score de Influenciadores</p>
        </div>
      </div>

      {/* Search Bar */}
      {!instagramResult && !showInstagramForm && (
        <Card className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20 border-pink-200 dark:border-pink-800">
          <CardContent className="p-6">
            <div className="text-center mb-6">
              <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-2">Analisar Perfil do Instagram</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">Digite o @username para análise automática completa</p>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 max-w-xl mx-auto">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <Input placeholder="@username (ex: rankingrun)" value={instagramSearchUsername}
                  onChange={(e) => setInstagramSearchUsername(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleInstagramSearch()}
                  className="pl-10 h-12 text-lg" disabled={instagramSearchLoading} />
              </div>
              <select value={instagramFormData.nicho} onChange={(e) => setInstagramFormData({...instagramFormData, nicho: e.target.value})}
                className="h-12 px-4 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800">
                <option value="corrida">Corrida</option><option value="fitness">Fitness</option>
                <option value="lifestyle">Lifestyle</option><option value="moda">Moda</option>
                <option value="gastronomia">Gastronomia</option><option value="viagem">Viagem</option>
                <option value="tech">Tecnologia</option><option value="outros">Outros</option>
              </select>
              <Button onClick={handleInstagramSearch} disabled={instagramSearchLoading || !instagramSearchUsername.trim()}
                className="h-12 px-6 bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600">
                {instagramSearchLoading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Analisando...</> : <><Activity className="w-4 h-4 mr-2" />Analisar</>}
              </Button>
            </div>
            {instagramSearchError && (
              <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/30 rounded-lg text-center">
                <p className="text-red-700 dark:text-red-300 text-sm">{instagramSearchError}</p>
              </div>
            )}
            <div className="mt-6 text-center text-sm text-slate-500">
              <p>O sistema busca automaticamente: seguidores, posts, engajamento, crescimento, análise da bio e indicadores anti-fake.</p>
              <button onClick={() => { resetInstagramForm(); setShowInstagramForm(true); }}
                className="mt-2 text-pink-600 dark:text-pink-400 hover:underline font-medium">
                Ou inserir dados manualmente
              </button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Result */}
      {instagramResult && (
        <div className="space-y-6">
          <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white border-0 shadow-2xl overflow-hidden">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="text-center lg:text-left">
                  <div className="flex items-center justify-center lg:justify-start gap-4 mb-4">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-2xl font-bold">@</div>
                    <div>
                      <h3 className="text-2xl font-bold">@{instagramResult.analysis.username}</h3>
                      <p className="text-slate-400">{instagramResult.analysis.nome_completo || 'Influenciador'}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 justify-center lg:justify-start">
                    <Badge className="bg-slate-700 text-slate-200">{instagramResult.analysis.nicho}</Badge>
                    <Badge className={getClassificacaoColor(instagramResult.analysis.classificacao)}>{instagramResult.analysis.classificacao}</Badge>
                  </div>
                </div>
                <div className="text-center">
                  <div className="relative w-40 h-40 mx-auto">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="80" cy="80" r="70" stroke="#334155" strokeWidth="12" fill="none" />
                      <circle cx="80" cy="80" r="70"
                        stroke={instagramResult.analysis.score_final >= 80 ? '#10B981' : instagramResult.analysis.score_final >= 60 ? '#F59E0B' : '#EF4444'}
                        strokeWidth="12" fill="none"
                        strokeDasharray={`${(instagramResult.analysis.score_final / 100) * 440} 440`}
                        strokeLinecap="round" />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-4xl font-bold">{instagramResult.analysis.score_final}</span>
                      <span className="text-sm text-slate-400">/100</span>
                    </div>
                  </div>
                  <p className="mt-2 text-lg font-semibold">Score de Influência</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-700/50 p-4 rounded-xl text-center">
                    <div className="text-2xl font-bold text-pink-400">{instagramResult.analysis.seguidores.toLocaleString()}</div>
                    <div className="text-sm text-slate-400">Seguidores</div>
                  </div>
                  <div className="bg-slate-700/50 p-4 rounded-xl text-center">
                    <div className="text-2xl font-bold text-blue-400">{instagramResult.analysis.engagement_rate}%</div>
                    <div className="text-sm text-slate-400">Engajamento</div>
                  </div>
                  <div className="bg-slate-700/50 p-4 rounded-xl text-center">
                    <div className="text-2xl font-bold text-green-400">{instagramResult.analysis.total_posts}</div>
                    <div className="text-sm text-slate-400">Posts</div>
                  </div>
                  <div className="bg-slate-700/50 p-4 rounded-xl text-center">
                    <div className="text-2xl font-bold text-amber-400">{((instagramResult.graficos_data?.metricas?.indice_anomalia || 0)).toFixed(1)}%</div>
                    <div className="text-sm text-slate-400">Índice Anomalia</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader><CardTitle className="flex items-center gap-2"><Activity className="w-5 h-5 text-purple-500" /> Análise Radar (8 Métricas)</CardTitle></CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={instagramResult.graficos_data.radar.labels.map((label, i) => ({ metric: label, value: instagramResult.graficos_data.radar.values[i], fullMark: 10 }))}>
                      <PolarGrid stroke="#E5E7EB" /><PolarAngleAxis dataKey="metric" tick={{ fill: '#6B7280', fontSize: 11 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: '#9CA3AF', fontSize: 10 }} />
                      <RechartsRadar name="Perfil" dataKey="value" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.5} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-blue-500" /> Notas Individuais (0-10)</CardTitle></CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={instagramResult.graficos_data.radar.labels.map((label, i) => ({ name: label, nota: instagramResult.graficos_data.radar.values[i] }))} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis type="number" domain={[0, 10]} stroke="#9CA3AF" />
                      <YAxis dataKey="name" type="category" stroke="#9CA3AF" width={90} tick={{ fontSize: 11 }} />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                      <Bar dataKey="nota" radius={[0, 4, 4, 0]}>
                        {instagramResult.graficos_data.radar.values.map((value, index) => (
                          <Cell key={`cell-${index}`} fill={value >= 7 ? '#10B981' : value >= 5 ? '#F59E0B' : '#EF4444'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader><CardTitle className="flex items-center gap-2"><PieChart className="w-5 h-5 text-pink-500" /> Distribuição de Formatos</CardTitle></CardHeader>
              <CardContent>
                <div className="h-[280px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPie>
                      <Pie data={instagramResult.graficos_data.formatos.labels.map((label, i) => ({ name: label, value: instagramResult.graficos_data.formatos.values[i] }))}
                        cx="50%" cy="50%" innerRadius={50} outerRadius={90} paddingAngle={5} dataKey="value"
                        label={({ name, value }) => `${name}: ${value}%`}>
                        <Cell fill="#EC4899" /><Cell fill="#8B5CF6" /><Cell fill="#3B82F6" />
                      </Pie>
                      <Tooltip /><Legend />
                    </RechartsPie>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
              <CardHeader><CardTitle className="flex items-center gap-2"><TrendingUp className="w-5 h-5 text-emerald-500" /> Comparativo vs Média do Nicho</CardTitle></CardHeader>
              <CardContent>
                <div className="h-[280px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={instagramResult.graficos_data.comparativo.labels.map((label, i) => ({
                      name: label, perfil: instagramResult.graficos_data.comparativo.perfil[i], media: instagramResult.graficos_data.comparativo.media_nicho[i]
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis dataKey="name" stroke="#9CA3AF" /><YAxis stroke="#9CA3AF" />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                      <Legend />
                      <Bar dataKey="perfil" name="Perfil Analisado" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="media" name="Média do Nicho" fill="#94A3B8" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border-0">
            <CardHeader><CardTitle className="flex items-center gap-2"><AlertCircle className="w-5 h-5 text-blue-500" /> Recomendações Personalizadas</CardTitle></CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {instagramResult.recomendacoes.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-slate-700 dark:text-slate-300">
                    <span className="mt-1 w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />{rec}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Action buttons */}
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => handleExportInstagram(instagramResult.analysis.id, 'xlsx')} className="bg-emerald-600 hover:bg-emerald-700">
              <Download className="w-4 h-4 mr-2" /> Exportar XLSX
            </Button>
            <Button onClick={() => handleExportInstagram(instagramResult.analysis.id, 'csv')} variant="outline">
              <Download className="w-4 h-4 mr-2" /> Exportar CSV
            </Button>
            <Button onClick={() => setInstagramResult(null)} variant="outline">Fechar Resultado</Button>
          </div>
        </div>
      )}

      {/* History */}
      {!instagramResult && (
        <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
          <CardHeader><CardTitle className="flex items-center gap-2"><FileText className="w-5 h-5 text-slate-500" /> Histórico de Análises</CardTitle></CardHeader>
          <CardContent>
            {loadingInstagram ? (
              <div className="text-center py-12 text-slate-500">Carregando análises...</div>
            ) : instagramAnalises.length === 0 ? (
              <div className="text-center py-12">
                <Activity className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <p className="text-slate-500">Nenhuma análise realizada ainda.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {instagramAnalises.map((analysis) => (
                  <div key={analysis.id} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-white font-bold">@</div>
                      <div>
                        <h4 className="font-semibold">@{analysis.username}</h4>
                        <p className="text-sm text-slate-500">{analysis.seguidores?.toLocaleString()} seguidores - {analysis.nicho}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">{analysis.score_final}</div>
                        <Badge className={getClassificacaoColor(analysis.classificacao)}>{analysis.classificacao}</Badge>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={async () => {
                          const response = await axios.get(`${API}/admin/instagram/analises/${analysis.id}`, { headers: { Authorization: `Bearer ${token}` } });
                          setInstagramResult(response.data);
                        }}><Eye className="w-4 h-4" /></Button>
                        <Button size="sm" variant="destructive" onClick={() => handleDeleteInstagramAnalysis(analysis.id)}><Trash2 className="w-4 h-4" /></Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Manual Form Modal */}
      <Dialog open={showInstagramForm} onOpenChange={setShowInstagramForm}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Activity className="w-5 h-5 text-pink-500" /> Nova Análise de Perfil</DialogTitle>
          </DialogHeader>
          <div className="space-y-6 py-4">
            <p className="text-sm text-slate-500 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
              Preencha apenas os dados básicos. O sistema calculará automaticamente: média de likes, comentários, engagement rate, crescimento, análise da bio e indicadores anti-fake.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2"><Label>@Username *</Label><Input value={instagramFormData.username} onChange={(e) => setInstagramFormData({...instagramFormData, username: e.target.value.replace('@', '')})} placeholder="usuario" /></div>
              <div className="space-y-2"><Label>Nome Completo</Label><Input value={instagramFormData.nome_completo} onChange={(e) => setInstagramFormData({...instagramFormData, nome_completo: e.target.value})} placeholder="João Silva" /></div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-2"><Label>Seguidores *</Label><Input type="number" value={instagramFormData.seguidores} onChange={(e) => setInstagramFormData({...instagramFormData, seguidores: e.target.value})} placeholder="10000" /></div>
              <div className="space-y-2"><Label>Seguindo *</Label><Input type="number" value={instagramFormData.seguindo} onChange={(e) => setInstagramFormData({...instagramFormData, seguindo: e.target.value})} placeholder="500" /></div>
              <div className="space-y-2"><Label>Total de Posts *</Label><Input type="number" value={instagramFormData.total_posts} onChange={(e) => setInstagramFormData({...instagramFormData, total_posts: e.target.value})} placeholder="150" /></div>
              <div className="space-y-2">
                <Label>Nicho</Label>
                <select value={instagramFormData.nicho} onChange={(e) => setInstagramFormData({...instagramFormData, nicho: e.target.value})}
                  className="w-full h-10 px-3 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800">
                  <option value="corrida">Corrida</option><option value="fitness">Fitness</option>
                  <option value="lifestyle">Lifestyle</option><option value="moda">Moda</option>
                  <option value="gastronomia">Gastronomia</option><option value="viagem">Viagem</option>
                  <option value="tech">Tecnologia</option><option value="outros">Outros</option>
                </select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Bio do Perfil (opcional)</Label>
              <textarea value={instagramFormData.bio} onChange={(e) => setInstagramFormData({...instagramFormData, bio: e.target.value})}
                placeholder="Cole aqui a bio do perfil para análise automática de keywords, CTA, etc."
                className="w-full h-20 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 resize-none" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowInstagramForm(false)}>Cancelar</Button>
            <Button onClick={handleInstagramAnalyze} disabled={loadingInstagram} className="bg-gradient-to-r from-pink-500 to-purple-500">
              {loadingInstagram ? <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Analisando...</> : <><Activity className="w-4 h-4 mr-2" />Analisar Perfil</>}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardInstagram;
