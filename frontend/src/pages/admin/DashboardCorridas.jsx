import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { 
  Star, Trophy, MapPin, Plus, Edit, Trash2, Loader2, 
  Calendar, ExternalLink, BarChart3, Award, TrendingUp
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { toast } from 'sonner';

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

const DashboardCorridas = ({ 
  rankingCorridasDashboard,
  corridasEventos,
  loadingRankingCorridas,
  corridaFormData,
  setCorridaFormData,
  showCorridaModal,
  setShowCorridaModal,
  corridaEditando,
  setCorridaEditando,
  onSaveCorrida,
  onDeleteCorrida,
  onRefresh
}) => {
  // Estados para cidades do IBGE
  const [cidadesIBGE, setCidadesIBGE] = useState([]);
  const [loadingCidadesIBGE, setLoadingCidadesIBGE] = useState(false);

  // Buscar cidades do IBGE quando o estado mudar
  useEffect(() => {
    const fetchCidadesIBGE = async () => {
      if (!corridaFormData.estado) {
        setCidadesIBGE([]);
        return;
      }
      setLoadingCidadesIBGE(true);
      try {
        const response = await axios.get(
          `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${corridaFormData.estado}/municipios`
        );
        const cidadesOrdenadas = response.data
          .map(cidade => cidade.nome)
          .sort((a, b) => a.localeCompare(b));
        setCidadesIBGE(cidadesOrdenadas);
      } catch (error) {
        console.error('Erro ao buscar cidades do IBGE:', error);
        setCidadesIBGE([]);
        toast.error('Erro ao buscar cidades. Tente novamente.');
      } finally {
        setLoadingCidadesIBGE(false);
      }
    };

    fetchCidadesIBGE();
  }, [corridaFormData.estado]);

  // Dados do dashboard
  const stats = rankingCorridasDashboard || {};
  const distribuicaoNotas = stats.distribuicao_notas || [];
  const topCorridas = stats.top_corridas || [];
  const corridasPorEstado = stats.corridas_por_estado || [];

  // Handlers para modal
  const handleOpenAdd = () => {
    setCorridaEditando(null);
    setCidadesIBGE([]);
    setCorridaFormData({
      nome_corrida: '',
      organizador: '',
      cidade: '',
      estado: '',
      data_corrida: '',
      pagina_link: '',
      status: 'ativa'
    });
    setShowCorridaModal(true);
  };

  const handleOpenEdit = (corrida) => {
    setCorridaEditando(corrida);
    setCorridaFormData({
      nome_corrida: corrida.nome_corrida || '',
      organizador: corrida.organizador || '',
      cidade: corrida.cidade || '',
      estado: corrida.estado || '',
      data_corrida: corrida.data_corrida || '',
      pagina_link: corrida.pagina_link || '',
      status: corrida.status || 'ativa'
    });
    setShowCorridaModal(true);
  };

  // Handler para mudança de estado - limpa a cidade
  const handleEstadoChange = (novoEstado) => {
    setCorridaFormData({
      ...corridaFormData,
      estado: novoEstado,
      cidade: '' // Limpar cidade ao mudar estado
    });
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Total Corridas</p>
                <p className="text-3xl font-bold">{stats.total_corridas || 0}</p>
              </div>
              <Trophy className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-500 to-orange-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-amber-100 text-sm">Total Avaliações</p>
                <p className="text-3xl font-bold">{stats.total_avaliacoes || 0}</p>
              </div>
              <Star className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Média Geral</p>
                <p className="text-3xl font-bold">{(stats.media_geral || 0).toFixed(1)}</p>
              </div>
              <TrendingUp className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Melhor Avaliada</p>
                <p className="text-lg font-bold truncate" title={stats.melhor_avaliada?.nome}>
                  {stats.melhor_avaliada?.nome?.substring(0, 15) || 'N/A'}
                </p>
              </div>
              <Award className="w-10 h-10 opacity-80" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sistema de Selos */}
      <Card className="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 border-amber-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-500" />
            Sistema de Selos - Certificações
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-4 bg-white dark:bg-slate-800 rounded-lg">
              <span className="text-2xl">⭐</span>
              <div>
                <p className="font-semibold">Selo 5 Estrelas</p>
                <p className="text-sm text-slate-500">Média ≥ 4.5 + 50 avaliações</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-white dark:bg-slate-800 rounded-lg">
              <span className="text-2xl">🏆</span>
              <div>
                <p className="font-semibold">Top 10 Brasil</p>
                <p className="text-sm text-slate-500">10 melhores nacional</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-white dark:bg-slate-800 rounded-lg">
              <span className="text-2xl">📍</span>
              <div>
                <p className="font-semibold">Top 10 Estado</p>
                <p className="text-sm text-slate-500">10 melhores por UF</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribuição de Notas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              Distribuição de Notas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distribuicaoNotas}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="nota" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="quantidade" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Top 10 Melhores Corridas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500" />
              Top 10 - Melhores Corridas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {topCorridas.length === 0 ? (
                <p className="text-center text-slate-500 py-8">Nenhuma corrida avaliada</p>
              ) : (
                topCorridas.map((corrida, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                        idx < 3 ? 'bg-amber-100 text-amber-800' : 'bg-slate-200 text-slate-600'
                      }`}>
                        {idx + 1}
                      </span>
                      <span className="text-sm font-medium truncate max-w-[200px]">{corrida.nome}</span>
                    </div>
                    <Badge className="bg-green-100 text-green-800">
                      {(corrida.media || 0).toFixed(1)} ⭐
                    </Badge>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabela de Gerenciamento */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-500" />
              Gerenciar Corridas/Eventos
              <Badge variant="secondary">{corridasEventos?.length || 0} eventos</Badge>
            </CardTitle>
            <Button onClick={handleOpenAdd} size="sm" className="bg-blue-500 hover:bg-blue-600">
              <Plus className="w-4 h-4 mr-2" />
              Nova Corrida
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loadingRankingCorridas ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : !corridasEventos || corridasEventos.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Trophy className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>Nenhuma corrida cadastrada</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-slate-50 dark:bg-slate-800">
                    <th className="text-left py-3 px-4 font-semibold">Corrida</th>
                    <th className="text-left py-3 px-4 font-semibold">Organizador</th>
                    <th className="text-left py-3 px-4 font-semibold">Local</th>
                    <th className="text-center py-3 px-4 font-semibold">Avaliações</th>
                    <th className="text-center py-3 px-4 font-semibold">Média</th>
                    <th className="text-center py-3 px-4 font-semibold">Status</th>
                    <th className="text-center py-3 px-4 font-semibold">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {corridasEventos.map((corrida) => (
                    <tr key={corrida.id} className="border-b hover:bg-slate-50 dark:hover:bg-slate-800">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{corrida.nome_corrida}</span>
                          {corrida.pagina_link && (
                            <a href={corrida.pagina_link} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="w-3 h-3 text-slate-400" />
                            </a>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">{corrida.organizador}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          {corrida.cidade}/{corrida.estado}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-center">{corrida.total_avaliacoes || 0}</td>
                      <td className="py-3 px-4 text-center">
                        <Badge className="bg-amber-100 text-amber-800">
                          {(corrida.media_geral || 0).toFixed(1)} ⭐
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge className={corrida.status === 'ativa' ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-800'}>
                          {corrida.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <Button variant="ghost" size="sm" onClick={() => handleOpenEdit(corrida)}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => onDeleteCorrida(corrida.id)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal de Cadastro/Edição */}
      <Dialog open={showCorridaModal} onOpenChange={setShowCorridaModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {corridaEditando ? 'Editar Corrida' : 'Nova Corrida'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nome da Corrida *</Label>
              <Input
                value={corridaFormData.nome_corrida}
                onChange={(e) => setCorridaFormData({...corridaFormData, nome_corrida: e.target.value})}
                placeholder="Ex: Maratona de São Paulo 2026"
              />
            </div>
            <div>
              <Label>Organizador</Label>
              <Input
                value={corridaFormData.organizador}
                onChange={(e) => setCorridaFormData({...corridaFormData, organizador: e.target.value})}
                placeholder="Nome do organizador"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Estado *</Label>
                <Select 
                  value={corridaFormData.estado} 
                  onValueChange={handleEstadoChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o UF" />
                  </SelectTrigger>
                  <SelectContent>
                    {ESTADOS_BR.map(uf => (
                      <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Cidade *</Label>
                <Select 
                  value={corridaFormData.cidade} 
                  onValueChange={(v) => setCorridaFormData({...corridaFormData, cidade: v})}
                  disabled={!corridaFormData.estado || loadingCidadesIBGE}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={loadingCidadesIBGE ? "Carregando..." : "Selecione a cidade"} />
                  </SelectTrigger>
                  <SelectContent className="max-h-60">
                    {cidadesIBGE.map(cidade => (
                      <SelectItem key={cidade} value={cidade}>{cidade}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {!corridaFormData.estado && (
                  <p className="text-xs text-slate-500 mt-1">Selecione o estado primeiro</p>
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Data da Corrida</Label>
                <Input
                  type="date"
                  value={corridaFormData.data_corrida}
                  onChange={(e) => setCorridaFormData({...corridaFormData, data_corrida: e.target.value})}
                />
              </div>
              <div>
                <Label>Status</Label>
                <Select 
                  value={corridaFormData.status} 
                  onValueChange={(v) => setCorridaFormData({...corridaFormData, status: v})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ativa">Ativa</SelectItem>
                    <SelectItem value="encerrada">Encerrada</SelectItem>
                    <SelectItem value="cancelada">Cancelada</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Link da Página</Label>
              <Input
                value={corridaFormData.pagina_link}
                onChange={(e) => setCorridaFormData({...corridaFormData, pagina_link: e.target.value})}
                placeholder="https://..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCorridaModal(false)}>
              Cancelar
            </Button>
            <Button onClick={onSaveCorrida} className="bg-blue-500 hover:bg-blue-600">
              {corridaEditando ? 'Salvar' : 'Cadastrar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardCorridas;
