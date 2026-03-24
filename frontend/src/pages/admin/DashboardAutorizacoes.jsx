import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import {
  CheckCircle, XCircle, Shield, Search, RefreshCw, Loader2, Award, Trophy, Download
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getStatusColor = (status) => {
  switch (status) {
    case 'em_teste': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
    case 'autorizado': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
    case 'expirado': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
    default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
  }
};

const getStatusLabel = (status) => {
  switch (status) {
    case 'em_teste': return 'Em Teste';
    case 'autorizado': return 'Autorizado';
    case 'expirado': return 'Expirado';
    default: return 'Desconhecido';
  }
};

const DashboardAutorizacoes = ({ token }) => {
  const [atletasPeriodoTeste, setAtletasPeriodoTeste] = useState([]);
  const [loadingAutorizacoes, setLoadingAutorizacoes] = useState(false);
  const [showAutorizacaoModal, setShowAutorizacaoModal] = useState(false);
  const [atletaAutorizando, setAtletaAutorizando] = useState(null);
  const [tipoAutorizacao, setTipoAutorizacao] = useState('6_meses');
  const [observacaoAutorizacao, setObservacaoAutorizacao] = useState('');
  const [savingAutorizacao, setSavingAutorizacao] = useState(false);
  const [filtroStatusAutorizacao, setFiltroStatusAutorizacao] = useState('todos');
  const [showCarteirinhaModal, setShowCarteirinhaModal] = useState(false);
  const [carteirinhaData, setCarteirinhaData] = useState(null);
  const [buscaAutorizacao, setBuscaAutorizacao] = useState('');
  const [atletasSelecionados, setAtletasSelecionados] = useState([]);
  const [aprovandoEmMassa, setAprovandoEmMassa] = useState(false);

  useEffect(() => { fetchAtletasPeriodoTeste(); }, []);

  const fetchAtletasPeriodoTeste = async () => {
    setLoadingAutorizacoes(true);
    try {
      const response = await axios.get(`${API}/admin/atletas-periodo-teste`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAtletasPeriodoTeste(response.data);
    } catch (error) {
      console.error('Erro ao buscar atletas:', error);
      toast.error('Erro ao carregar lista de atletas');
    } finally {
      setLoadingAutorizacoes(false);
    }
  };

  const filteredAtletasAutorizacao = atletasPeriodoTeste
    .filter(atleta => {
      if (filtroStatusAutorizacao !== 'todos' && atleta.status_periodo !== filtroStatusAutorizacao) return false;
      if (buscaAutorizacao.trim()) {
        const termo = buscaAutorizacao.toLowerCase();
        return atleta.nome?.toLowerCase().includes(termo) || atleta.email?.toLowerCase().includes(termo) || atleta.equipe?.toLowerCase().includes(termo);
      }
      return true;
    })
    .sort((a, b) => (a.nome || '').localeCompare(b.nome || '', 'pt-BR'));

  const handleToggleSelectAtleta = (atletaId) => {
    setAtletasSelecionados(prev => prev.includes(atletaId) ? prev.filter(id => id !== atletaId) : [...prev, atletaId]);
  };

  const handleSelectAll = () => {
    const atletasNaoAutorizados = filteredAtletasAutorizacao.filter(a => a.status_periodo !== 'autorizado').map(a => a.id);
    setAtletasSelecionados(prev => prev.length === atletasNaoAutorizados.length ? [] : atletasNaoAutorizados);
  };

  const handleAprovarEmMassa = async () => {
    if (atletasSelecionados.length === 0) { toast.error('Selecione pelo menos um atleta'); return; }
    if (!confirm(`Deseja autorizar ${atletasSelecionados.length} atleta(s) selecionado(s)?`)) return;
    setAprovandoEmMassa(true);
    let aprovados = 0, erros = 0;
    for (const atletaId of atletasSelecionados) {
      try {
        const formData = new FormData();
        formData.append('atleta_id', atletaId);
        formData.append('tipo_autorizacao', tipoAutorizacao);
        formData.append('observacao', 'Aprovação em massa');
        await axios.post(`${API}/admin/autorizacoes`, formData, { headers: { Authorization: `Bearer ${token}` } });
        aprovados++;
      } catch { erros++; }
    }
    if (aprovados > 0) toast.success(`${aprovados} atleta(s) autorizado(s) com sucesso!`);
    if (erros > 0) toast.error(`${erros} atleta(s) não puderam ser autorizados`);
    setAtletasSelecionados([]);
    setAprovandoEmMassa(false);
    fetchAtletasPeriodoTeste();
  };

  const handleCriarAutorizacao = async () => {
    if (!atletaAutorizando) return;
    setSavingAutorizacao(true);
    try {
      const formData = new FormData();
      formData.append('atleta_id', atletaAutorizando.id);
      formData.append('tipo_autorizacao', tipoAutorizacao);
      formData.append('observacao', observacaoAutorizacao);
      const response = await axios.post(`${API}/admin/autorizacoes`, formData, { headers: { Authorization: `Bearer ${token}` } });
      toast.success(response.data.message);
      setShowAutorizacaoModal(false);
      setAtletaAutorizando(null);
      setTipoAutorizacao('6_meses');
      setObservacaoAutorizacao('');
      fetchAtletasPeriodoTeste();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao criar autorização');
    } finally { setSavingAutorizacao(false); }
  };

  const handleRevogarAutorizacao = async (autorizacaoId) => {
    if (!confirm('Tem certeza que deseja revogar esta autorização?')) return;
    try {
      await axios.delete(`${API}/admin/autorizacoes/${autorizacaoId}`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Autorização revogada com sucesso');
      fetchAtletasPeriodoTeste();
    } catch { toast.error('Erro ao revogar autorização'); }
  };

  const handleGerarCarteirinha = async (atletaId) => {
    try {
      const response = await axios.get(`${API}/admin/carteirinha/${atletaId}`, { headers: { Authorization: `Bearer ${token}` } });
      setCarteirinhaData(response.data);
      setShowCarteirinhaModal(true);
    } catch (error) { toast.error(error.response?.data?.detail || 'Erro ao gerar carteirinha'); }
  };

  return (
    <div className="space-y-6" data-testid="dashboard-autorizacoes">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="p-4">
            <p className="text-sm opacity-80">Em Teste</p>
            <p className="text-3xl font-bold">{atletasPeriodoTeste.filter(a => a.status_periodo === 'em_teste').length}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="p-4">
            <p className="text-sm opacity-80">Autorizados</p>
            <p className="text-3xl font-bold">{atletasPeriodoTeste.filter(a => a.status_periodo === 'autorizado').length}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardContent className="p-4">
            <p className="text-sm opacity-80">Expirados</p>
            <p className="text-3xl font-bold">{atletasPeriodoTeste.filter(a => a.status_periodo === 'expirado').length}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="p-4">
            <p className="text-sm opacity-80">Total Atletas</p>
            <p className="text-3xl font-bold">{atletasPeriodoTeste.length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Lista */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
        <CardHeader className="border-b dark:border-slate-700">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <CardTitle className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-emerald-500" /> Gerenciar Autorizações de Acesso
            </CardTitle>
            <div className="flex items-center gap-2">
              {atletasSelecionados.length > 0 && (
                <Button onClick={handleAprovarEmMassa} disabled={aprovandoEmMassa} className="bg-emerald-500 hover:bg-emerald-600 text-white">
                  {aprovandoEmMassa ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <CheckCircle className="w-4 h-4 mr-2" />}
                  Aprovar {atletasSelecionados.length} selecionado(s)
                </Button>
              )}
              <Select value={filtroStatusAutorizacao} onValueChange={setFiltroStatusAutorizacao}>
                <SelectTrigger className="w-40"><SelectValue placeholder="Status" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos</SelectItem>
                  <SelectItem value="em_teste">Em Teste</SelectItem>
                  <SelectItem value="autorizado">Autorizados</SelectItem>
                  <SelectItem value="expirado">Expirados</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" onClick={fetchAtletasPeriodoTeste} disabled={loadingAutorizacoes}>
                <RefreshCw className={`w-4 h-4 ${loadingAutorizacoes ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="p-4 border-b dark:border-slate-700">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input type="text" placeholder="Buscar por nome, email ou equipe..." value={buscaAutorizacao} onChange={(e) => setBuscaAutorizacao(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500" />
              {buscaAutorizacao && <button onClick={() => setBuscaAutorizacao('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">&#10005;</button>}
            </div>
            <p className="text-xs text-slate-500 mt-2">Mostrando {filteredAtletasAutorizacao.length} atleta(s) em ordem alfabética</p>
          </div>

          {loadingAutorizacoes ? (
            <div className="flex items-center justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-emerald-500" /></div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 dark:bg-slate-900/50">
                  <tr>
                    <th className="px-4 py-3 text-center w-12">
                      <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                        checked={filteredAtletasAutorizacao.filter(a => a.status_periodo !== 'autorizado').length > 0 && atletasSelecionados.length === filteredAtletasAutorizacao.filter(a => a.status_periodo !== 'autorizado').length}
                        onChange={handleSelectAll} title="Selecionar todos" />
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Atleta</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Equipe</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Dias Restantes</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                  {filteredAtletasAutorizacao.map((atleta) => (
                    <tr key={atleta.id} className={`hover:bg-slate-50 dark:hover:bg-slate-700/50 ${atletasSelecionados.includes(atleta.id) ? 'bg-emerald-50 dark:bg-emerald-900/20' : ''}`}>
                      <td className="px-4 py-3 text-center">
                        {atleta.status_periodo !== 'autorizado' && (
                          <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                            checked={atletasSelecionados.includes(atleta.id)} onChange={() => handleToggleSelectAtleta(atleta.id)} />
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div><p className="font-medium text-slate-900 dark:text-white">{atleta.nome}</p><p className="text-xs text-slate-500">{atleta.email}</p></div>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-400">{atleta.equipe || 'Individual'}</td>
                      <td className="px-4 py-3 text-center"><Badge className={getStatusColor(atleta.status_periodo)}>{getStatusLabel(atleta.status_periodo)}</Badge></td>
                      <td className="px-4 py-3 text-center">
                        <span className={`font-semibold ${atleta.dias_restantes > 10 ? 'text-green-600' : atleta.dias_restantes > 0 ? 'text-yellow-600' : 'text-red-600'}`}>
                          {atleta.dias_restantes !== null ? atleta.dias_restantes : '-'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-2">
                          {atleta.status_periodo !== 'autorizado' ? (
                            <Button size="sm" onClick={() => { setAtletaAutorizando(atleta); setShowAutorizacaoModal(true); }} className="bg-emerald-500 hover:bg-emerald-600 text-white">
                              <CheckCircle className="w-4 h-4 mr-1" /> Autorizar
                            </Button>
                          ) : (
                            <>
                              <Button size="sm" variant="outline" onClick={() => handleGerarCarteirinha(atleta.id)} className="text-blue-600 border-blue-300">
                                <Award className="w-4 h-4 mr-1" /> Carteirinha
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => handleRevogarAutorizacao(atleta.autorizacao?.id)} className="text-red-600 border-red-300">
                                <XCircle className="w-4 h-4" />
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredAtletasAutorizacao.length === 0 && <div className="text-center py-12 text-slate-500">Nenhum atleta encontrado com o filtro selecionado</div>}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal de Autorização */}
      <Dialog open={showAutorizacaoModal} onOpenChange={setShowAutorizacaoModal}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Shield className="w-5 h-5 text-emerald-500" /> Autorizar Acesso</DialogTitle></DialogHeader>
          {atletaAutorizando && (
            <div className="space-y-4">
              <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-lg">
                <p className="font-medium text-lg">{atletaAutorizando.nome}</p>
                <p className="text-sm text-slate-500">{atletaAutorizando.email}</p>
                <p className="text-sm text-slate-500">Equipe: {atletaAutorizando.equipe || 'Individual'}</p>
              </div>
              <div className="space-y-2">
                <Label>Tipo de Autorização</Label>
                <Select value={tipoAutorizacao} onValueChange={setTipoAutorizacao}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="6_meses">6 Meses</SelectItem>
                    <SelectItem value="1_ano">1 Ano</SelectItem>
                    <SelectItem value="ate_fim_ano">Até o Final do Ano</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Observação (opcional)</Label>
                <Textarea value={observacaoAutorizacao} onChange={(e) => setObservacaoAutorizacao(e.target.value)} placeholder="Ex: Pagamento via PIX em 09/03/2026" rows={2} />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAutorizacaoModal(false)}>Cancelar</Button>
            <Button onClick={handleCriarAutorizacao} disabled={savingAutorizacao} className="bg-emerald-600 hover:bg-emerald-700">
              {savingAutorizacao ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CheckCircle className="w-4 h-4 mr-2" />}
              Confirmar Autorização
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Carteirinha */}
      <Dialog open={showCarteirinhaModal} onOpenChange={setShowCarteirinhaModal}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Award className="w-5 h-5 text-amber-500" /> Carteirinha de Membro</DialogTitle></DialogHeader>
          {carteirinhaData && (
            <div className="space-y-4">
              <div className="bg-gradient-to-br from-emerald-600 to-emerald-800 p-6 rounded-xl text-white relative overflow-hidden">
                <div className="absolute inset-0 opacity-10"><div className="absolute top-2 right-2 text-6xl font-bold">RRP</div></div>
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-4">
                    <div><p className="text-xs uppercase opacity-70">Ranking Run Pró</p><p className="text-lg font-bold">Carteirinha de Membro</p></div>
                    <Trophy className="w-8 h-8" />
                  </div>
                  <div className="space-y-2">
                    <p className="text-xl font-bold">{carteirinhaData.atleta.nome}</p>
                    <p className="text-sm opacity-80">{carteirinhaData.atleta.equipe || 'Individual'}</p>
                    <p className="text-xs opacity-70">{carteirinhaData.atleta.email}</p>
                  </div>
                  <div className="mt-4 pt-4 border-t border-white/20 flex justify-between items-end">
                    <div><p className="text-xs opacity-70">Nº Carteirinha</p><p className="font-mono text-sm">{carteirinhaData.numero_carteirinha}</p></div>
                    <div className="text-right"><p className="text-xs opacity-70">Válido até</p><p className="font-semibold">{new Date(carteirinhaData.valido_ate).toLocaleDateString('pt-BR')}</p></div>
                  </div>
                </div>
              </div>
              <Alert className="bg-blue-50 dark:bg-blue-900/20 border-blue-200">
                <AlertDescription className="text-blue-700 dark:text-blue-300 text-sm">Esta carteirinha comprova que o atleta está autorizado a participar do Ranking Run Pró.</AlertDescription>
              </Alert>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCarteirinhaModal(false)}>Fechar</Button>
            <Button onClick={() => window.print()} className="bg-emerald-600 hover:bg-emerald-700"><Download className="w-4 h-4 mr-2" /> Imprimir</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardAutorizacoes;
