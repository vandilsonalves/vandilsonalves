import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Plus, Minus, Edit, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

const DashboardSubmeter = ({ token, atletas, onStatsRefresh }) => {
  const [atletaSelecionado, setAtletaSelecionado] = useState('');
  const [tipoOperacao, setTipoOperacao] = useState('adicionar');
  const [corridasAtleta, setCorridasAtleta] = useState([]);
  const [corridaSelecionada, setCorridaSelecionada] = useState(null);
  const [showEditCorridaModal, setShowEditCorridaModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [buscaAtleta, setBuscaAtleta] = useState('');
  const [showAtletaList, setShowAtletaList] = useState(false);

  const [novaCorridaAdmin, setNovaCorridaAdmin] = useState({
    nome_competicao: '', colocacao: '', distancia: '',
    cidade_competicao: '', estado_competicao: '',
    data_competicao: '', tempo: '', link_resultado: ''
  });

  useEffect(() => {
    if (atletaSelecionado && tipoOperacao === 'remover') {
      fetchCorridasAtleta(atletaSelecionado);
    }
  }, [atletaSelecionado, tipoOperacao]);

  const fetchCorridasAtleta = async (atletaId) => {
    try {
      const response = await axios.get(`${API}/atletas/${atletaId}/corridas`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCorridasAtleta(response.data);
    } catch (error) {
      console.error('Erro ao buscar corridas:', error);
    }
  };

  const handleSubmeterResultadoAdmin = async () => {
    if (!atletaSelecionado) {
      toast.error('Selecione um atleta');
      return;
    }
    if (tipoOperacao !== 'adicionar') return;

    if (!novaCorridaAdmin.nome_competicao || !novaCorridaAdmin.colocacao || !novaCorridaAdmin.distancia ||
        !novaCorridaAdmin.cidade_competicao || !novaCorridaAdmin.estado_competicao ||
        !novaCorridaAdmin.data_competicao || !novaCorridaAdmin.tempo) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/adicionar-corrida`, {
        atleta_id: atletaSelecionado, ...novaCorridaAdmin
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Corrida adicionada com sucesso!');
      setAtletaSelecionado('');
      setNovaCorridaAdmin({
        nome_competicao: '', colocacao: '', distancia: '',
        cidade_competicao: '', estado_competicao: '',
        data_competicao: '', tempo: '', link_resultado: ''
      });
      onStatsRefresh?.();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao adicionar corrida');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteCorrida = async (corridaId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta corrida?')) return;
    try {
      await axios.delete(`${API}/admin/corridas/${corridaId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Corrida excluída com sucesso!');
      fetchCorridasAtleta(atletaSelecionado);
      onStatsRefresh?.();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao excluir corrida');
    }
  };

  const handleEditCorrida = async () => {
    if (!corridaSelecionada) return;
    setActionLoading(true);
    try {
      await axios.put(`${API}/admin/corridas/${corridaSelecionada.id}`, corridaSelecionada, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Corrida atualizada com sucesso!');
      setShowEditCorridaModal(false);
      setCorridaSelecionada(null);
      fetchCorridasAtleta(atletaSelecionado);
      onStatsRefresh?.();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar corrida');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="max-w-4xl" data-testid="dashboard-submeter">
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
        <CardHeader>
          <CardTitle>Gerenciar Resultados do Atleta</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label>Selecionar Atleta</Label>
            <div className="relative">
              <Input
                placeholder="Buscar atleta pelo nome..."
                value={buscaAtleta}
                onChange={(e) => { setBuscaAtleta(e.target.value); setShowAtletaList(true); }}
                onFocus={() => setShowAtletaList(true)}
                data-testid="busca-atleta-input"
              />
              {atletaSelecionado && !buscaAtleta && (
                <div className="mt-1 px-3 py-2 bg-emerald-50 dark:bg-emerald-900/30 rounded-md text-sm text-emerald-700 dark:text-emerald-300 flex items-center justify-between">
                  <span>{atletas.find(a => a.id === atletaSelecionado)?.nome}</span>
                  <button onClick={() => { setAtletaSelecionado(''); setCorridasAtleta([]); }} className="text-xs text-red-500 hover:underline">Limpar</button>
                </div>
              )}
              {showAtletaList && buscaAtleta && (
                <div className="absolute z-50 w-full mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                  {[...atletas]
                    .filter(a => a.nome.toLowerCase().includes(buscaAtleta.toLowerCase()) || a.equipe?.toLowerCase().includes(buscaAtleta.toLowerCase()))
                    .sort((a, b) => a.nome.localeCompare(b.nome))
                    .slice(0, 20)
                    .map((a) => (
                      <button
                        key={a.id}
                        className="w-full text-left px-3 py-2 text-sm hover:bg-emerald-50 dark:hover:bg-slate-700 transition-colors border-b border-slate-100 dark:border-slate-700 last:border-0"
                        onClick={() => { setAtletaSelecionado(a.id); setBuscaAtleta(''); setShowAtletaList(false); setCorridasAtleta([]); }}
                        data-testid={`atleta-option-${a.id}`}
                      >
                        <span className="font-medium">{a.nome}</span>
                        <span className="text-slate-500 ml-1">- {a.equipe}</span>
                      </button>
                    ))
                  }
                  {[...atletas].filter(a => a.nome.toLowerCase().includes(buscaAtleta.toLowerCase()) || a.equipe?.toLowerCase().includes(buscaAtleta.toLowerCase())).length === 0 && (
                    <p className="px-3 py-2 text-sm text-slate-500">Nenhum atleta encontrado</p>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label>Tipo de Operação</Label>
            <div className="flex gap-4">
              <Button variant={tipoOperacao === 'adicionar' ? 'default' : 'outline'} onClick={() => setTipoOperacao('adicionar')} className={tipoOperacao === 'adicionar' ? 'bg-emerald-600' : ''}>
                <Plus className="w-4 h-4 mr-2" /> Adicionar Pontos
              </Button>
              <Button variant={tipoOperacao === 'remover' ? 'default' : 'outline'} onClick={() => setTipoOperacao('remover')} className={tipoOperacao === 'remover' ? 'bg-red-600' : ''}>
                <Minus className="w-4 h-4 mr-2" /> Remover Pontos
              </Button>
            </div>
          </div>

          {tipoOperacao === 'adicionar' && atletaSelecionado && (
            <div className="border rounded-lg p-6 bg-slate-50 dark:bg-slate-900 space-y-4">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Plus className="w-5 h-5 text-emerald-500" /> Adicionar Nova Corrida
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2 space-y-2">
                  <Label>Nome da Competição *</Label>
                  <Input value={novaCorridaAdmin.nome_competicao} onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, nome_competicao: e.target.value})} placeholder="Ex: Maratona de São Paulo" />
                </div>
                <div className="space-y-2">
                  <Label>Colocação *</Label>
                  <Input type="number" min="1" max="10" value={novaCorridaAdmin.colocacao} onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, colocacao: e.target.value})} placeholder="1 a 10" />
                </div>
                <div className="space-y-2">
                  <Label>Distância *</Label>
                  <Select value={novaCorridaAdmin.distancia} onValueChange={(v) => setNovaCorridaAdmin({...novaCorridaAdmin, distancia: v})}>
                    <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5KM">5 KM</SelectItem>
                      <SelectItem value="10KM">10 KM</SelectItem>
                      <SelectItem value="21KM">21 KM (Meia Maratona)</SelectItem>
                      <SelectItem value="42KM">42 KM (Maratona)</SelectItem>
                      <SelectItem value="OUTRA">Outra</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Cidade da Competição *</Label>
                  <Input value={novaCorridaAdmin.cidade_competicao} onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, cidade_competicao: e.target.value})} placeholder="Ex: São Paulo" />
                </div>
                <div className="space-y-2">
                  <Label>Estado (UF) *</Label>
                  <Select value={novaCorridaAdmin.estado_competicao} onValueChange={(v) => setNovaCorridaAdmin({...novaCorridaAdmin, estado_competicao: v})}>
                    <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
                    <SelectContent>
                      {ESTADOS_BR.map((uf) => <SelectItem key={uf} value={uf}>{uf}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Data da Competição *</Label>
                  <Input type="date" value={novaCorridaAdmin.data_competicao} onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, data_competicao: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label>Tempo (HH:MM:SS) *</Label>
                  <Input type="time" step="1" value={novaCorridaAdmin.tempo} onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, tempo: e.target.value})} />
                </div>
                <div className="md:col-span-2 space-y-2">
                  <Label>Link do Resultado (opcional)</Label>
                  <Input type="url" value={novaCorridaAdmin.link_resultado} onChange={(e) => setNovaCorridaAdmin({...novaCorridaAdmin, link_resultado: e.target.value})} placeholder="https://..." />
                </div>
              </div>
              <Button onClick={handleSubmeterResultadoAdmin} disabled={actionLoading} className="w-full bg-emerald-600 mt-4">
                <Plus className="w-4 h-4 mr-2" /> Adicionar Corrida e Pontos
              </Button>
            </div>
          )}

          {tipoOperacao === 'remover' && atletaSelecionado && (
            <div className="border rounded-lg p-6 bg-slate-50 dark:bg-slate-900 space-y-4">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Minus className="w-5 h-5 text-red-500" /> Corridas do Atleta (selecione para editar ou excluir)
              </h3>
              {corridasAtleta.length === 0 ? (
                <p className="text-slate-500 text-center py-4">Nenhuma corrida encontrada para este atleta.</p>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {corridasAtleta.map((corrida) => (
                    <div key={corrida.id} className="flex items-center justify-between p-4 bg-white dark:bg-slate-800 rounded-lg border">
                      <div className="flex-1">
                        <p className="font-medium">{corrida.nome}</p>
                        <div className="flex gap-4 text-sm text-slate-500 mt-1">
                          <span>{corrida.data}</span>
                          <span>{corrida.colocacao}º lugar</span>
                          <span>{corrida.distancia}</span>
                          <span className="font-semibold text-emerald-600">{corrida.pontos} pts</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => { setCorridaSelecionada(corrida); setShowEditCorridaModal(true); }}>
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="destructive" onClick={() => handleDeleteCorrida(corrida.id)}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal Editar Corrida */}
      <Dialog open={showEditCorridaModal} onOpenChange={setShowEditCorridaModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader><DialogTitle>Editar Corrida</DialogTitle></DialogHeader>
          {corridaSelecionada && (
            <div className="grid grid-cols-2 gap-4">
              <div className="md:col-span-2 space-y-2">
                <Label>Nome da Competição</Label>
                <Input value={corridaSelecionada.nome} onChange={(e) => setCorridaSelecionada({...corridaSelecionada, nome: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>Colocação</Label>
                <Input type="number" min="1" max="10" value={corridaSelecionada.colocacao} onChange={(e) => setCorridaSelecionada({...corridaSelecionada, colocacao: parseInt(e.target.value)})} />
              </div>
              <div className="space-y-2">
                <Label>Distância</Label>
                <Select value={corridaSelecionada.distancia} onValueChange={(v) => setCorridaSelecionada({...corridaSelecionada, distancia: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5KM">5 KM</SelectItem>
                    <SelectItem value="10KM">10 KM</SelectItem>
                    <SelectItem value="21KM">21 KM</SelectItem>
                    <SelectItem value="42KM">42 KM</SelectItem>
                    <SelectItem value="OUTRA">Outra</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Data</Label>
                <Input type="date" value={corridaSelecionada.data} onChange={(e) => setCorridaSelecionada({...corridaSelecionada, data: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>Tempo</Label>
                <Input type="time" step="1" value={corridaSelecionada.tempo} onChange={(e) => setCorridaSelecionada({...corridaSelecionada, tempo: e.target.value})} />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditCorridaModal(false)}>Cancelar</Button>
            <Button onClick={handleEditCorrida} disabled={actionLoading} className="bg-emerald-600">Salvar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardSubmeter;
