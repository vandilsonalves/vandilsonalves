import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Users, UserX, TrendingDown, AlertTriangle, Search, Bell,
  ArrowUpDown, Filter, RefreshCw, Loader2, ChevronDown, ChevronUp
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const StatCard = ({ title, value, subtitle, icon: Icon, color }) => (
  <div data-testid={`retencao-stat-${title.toLowerCase().replace(/\s+/g, '-')}`} className="bg-gray-800 rounded-xl p-5 border border-gray-700">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-400 text-sm">{title}</p>
        <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
        {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      </div>
      <div className="p-3 rounded-lg bg-gray-700/50">
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
    </div>
  </div>
);

const DashboardRetencao = () => {
  const { token } = useAuth();
  const [dados, setDados] = useState(null);
  const [loading, setLoading] = useState(true);
  const [periodo, setPeriodo] = useState('30');
  const [busca, setBusca] = useState('');
  const [filtroEquipe, setFiltroEquipe] = useState('all');
  const [ordenacao, setOrdenacao] = useState('dias_inativo');
  const [ordemAsc, setOrdemAsc] = useState(false);
  const [expandedEquipes, setExpandedEquipes] = useState(false);
  const [alertandoEquipe, setAlertandoEquipe] = useState(null);

  const fetchDados = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/admin/retencao/inativos`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { dias: periodo }
      });
      setDados(response.data);
    } catch (error) {
      toast.error('Erro ao carregar dados de retenção');
    } finally {
      setLoading(false);
    }
  }, [token, periodo]);

  useEffect(() => { fetchDados(); }, [fetchDados]);

  const handleAlertarAssessoria = async (equipe) => {
    setAlertandoEquipe(equipe);
    try {
      const response = await axios.post(`${API}/admin/retencao/alertar-assessoria`,
        { equipe },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.data.enviado) {
        toast.success(`Alerta enviado para ${response.data.dono} (${equipe})`);
      } else {
        toast.error(response.data.detail || 'Erro ao enviar alerta');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao enviar alerta');
    } finally {
      setAlertandoEquipe(null);
    }
  };

  // Filtrar atletas
  const atletasFiltrados = (dados?.atletas_inativos || []).filter(a => {
    const matchBusca = !busca ||
      a.nome.toLowerCase().includes(busca.toLowerCase()) ||
      a.email.toLowerCase().includes(busca.toLowerCase());
    const matchEquipe = filtroEquipe === 'all' || a.equipe === filtroEquipe;
    return matchBusca && matchEquipe;
  });

  // Ordenar
  const atletasOrdenados = [...atletasFiltrados].sort((a, b) => {
    let valA, valB;
    if (ordenacao === 'dias_inativo') {
      valA = a.dias_inativo ?? 9999;
      valB = b.dias_inativo ?? 9999;
    } else if (ordenacao === 'nome') {
      valA = a.nome;
      valB = b.nome;
      return ordemAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
    } else if (ordenacao === 'total_corridas') {
      valA = a.total_corridas || 0;
      valB = b.total_corridas || 0;
    }
    return ordemAsc ? valA - valB : valB - valA;
  });

  // Equipes únicas para filtro
  const equipes = [...new Set((dados?.atletas_inativos || []).map(a => a.equipe))].sort();

  const toggleOrdenacao = (campo) => {
    if (ordenacao === campo) {
      setOrdemAsc(!ordemAsc);
    } else {
      setOrdenacao(campo);
      setOrdemAsc(false);
    }
  };

  const resumo = dados?.resumo || {};

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
        <span className="ml-3 text-gray-400">Analisando retenção...</span>
      </div>
    );
  }

  return (
    <div data-testid="dashboard-retencao" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-emerald-500">Dashboard de Retenção</h2>
          <p className="text-gray-400 text-sm mt-1">
            Acompanhe atletas inativos e engaje as assessorias
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <Select value={periodo} onValueChange={setPeriodo}>
            <SelectTrigger data-testid="retencao-periodo-select" className="w-36 sm:w-[160px] bg-gray-800 border-gray-700 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Últimos 7 dias</SelectItem>
              <SelectItem value="15">Últimos 15 dias</SelectItem>
              <SelectItem value="30">Últimos 30 dias</SelectItem>
              <SelectItem value="60">Últimos 60 dias</SelectItem>
              <SelectItem value="90">Últimos 90 dias</SelectItem>
            </SelectContent>
          </Select>
          <Button data-testid="retencao-refresh-btn" variant="outline" size="sm" onClick={fetchDados} className="border-gray-700 text-gray-300 hover:bg-gray-800">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Taxa de Retenção"
          value={`${resumo.taxa_retencao || 0}%`}
          subtitle={`${resumo.total_ativos || 0} ativos de ${resumo.total_atletas || 0}`}
          icon={TrendingDown}
          color={resumo.taxa_retencao > 50 ? 'text-emerald-400' : 'text-red-400'}
        />
        <StatCard
          title="Atletas Inativos"
          value={resumo.total_inativos || 0}
          subtitle={`Nos últimos ${resumo.periodo_dias || 30} dias`}
          icon={UserX}
          color="text-orange-400"
        />
        <StatCard
          title="Pararam de Competir"
          value={resumo.pararam_de_competir || 0}
          subtitle="Tinham atividade anterior"
          icon={AlertTriangle}
          color="text-red-400"
        />
        <StatCard
          title="Nunca Submeteram"
          value={resumo.nunca_submeteram || 0}
          subtitle="Cadastrados mas sem resultado"
          icon={Users}
          color="text-gray-400"
        />
      </div>

      {/* Equipes com mais inativos */}
      <Card className="bg-gray-800 border-gray-700 p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            Equipes com Mais Inativos
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpandedEquipes(!expandedEquipes)}
            className="text-gray-400"
          >
            {expandedEquipes ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            {expandedEquipes ? 'Menos' : 'Mais'}
          </Button>
        </div>
        <div className="space-y-2">
          {(dados?.equipes_com_inativos || [])
            .slice(0, expandedEquipes ? 15 : 5)
            .map((eq, i) => (
              <div key={eq.equipe} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 bg-gray-700/40 rounded-lg hover:bg-gray-700/60 transition-colors">
                <div className="flex items-center gap-3 min-w-0">
                  <span className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold shrink-0 ${
                    i === 0 ? 'bg-red-500 text-white' :
                    i === 1 ? 'bg-orange-500 text-white' :
                    i === 2 ? 'bg-yellow-500 text-black' :
                    'bg-gray-600 text-white'
                  }`}>
                    {i + 1}
                  </span>
                  <span className="text-white text-sm font-medium truncate">{eq.equipe}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-9 sm:ml-0">
                  <Badge variant="secondary" className="bg-red-500/20 text-red-300 text-xs">
                    {eq.inativos} inativos
                  </Badge>
                  {eq.equipe !== 'Individual' && (
                    <Button
                      data-testid={`alertar-equipe-${i}`}
                      size="sm"
                      variant="ghost"
                      className="text-orange-400 hover:text-orange-300 hover:bg-orange-500/10 h-7 text-xs"
                      onClick={() => handleAlertarAssessoria(eq.equipe)}
                      disabled={alertandoEquipe === eq.equipe}
                    >
                      {alertandoEquipe === eq.equipe ? (
                        <Loader2 className="w-3 h-3 animate-spin mr-1" />
                      ) : (
                        <Bell className="w-3 h-3 mr-1" />
                      )}
                      Alertar Dono
                    </Button>
                  )}
                </div>
              </div>
            ))}
        </div>
      </Card>

      {/* Lista de Atletas Inativos */}
      <Card className="bg-gray-800 border-gray-700 p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">
            Atletas Inativos ({atletasOrdenados.length})
          </h3>
        </div>

        {/* Filtros */}
        <div className="flex flex-wrap gap-3 mb-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <Input
              data-testid="retencao-busca"
              placeholder="Buscar por nome ou email..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="pl-10 bg-gray-700 border-gray-600 text-white placeholder:text-gray-500"
            />
          </div>
          <Select value={filtroEquipe} onValueChange={setFiltroEquipe}>
            <SelectTrigger data-testid="retencao-filtro-equipe" className="w-[200px] bg-gray-700 border-gray-600 text-white">
              <Filter className="w-4 h-4 mr-2 text-gray-400" />
              <SelectValue placeholder="Todas equipes" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas equipes</SelectItem>
              {equipes.map(eq => (
                <SelectItem key={eq} value={eq}>{eq}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Tabela */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-3 text-gray-400 font-medium">
                  <button onClick={() => toggleOrdenacao('nome')} className="flex items-center gap-1 hover:text-white transition-colors">
                    Atleta <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-left py-3 px-3 text-gray-400 font-medium">Equipe</th>
                <th className="text-left py-3 px-3 text-gray-400 font-medium">Local</th>
                <th className="text-center py-3 px-3 text-gray-400 font-medium">
                  <button onClick={() => toggleOrdenacao('total_corridas')} className="flex items-center gap-1 hover:text-white transition-colors">
                    Corridas <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-center py-3 px-3 text-gray-400 font-medium">
                  <button onClick={() => toggleOrdenacao('dias_inativo')} className="flex items-center gap-1 hover:text-white transition-colors">
                    Dias Inativo <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-center py-3 px-3 text-gray-400 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {atletasOrdenados.slice(0, 50).map((atleta) => (
                <tr key={atleta.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors">
                  <td className="py-3 px-3">
                    <div>
                      <p className="text-white font-medium text-sm">{atleta.nome}</p>
                      <p className="text-gray-500 text-xs">{atleta.email}</p>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <span className="text-gray-300 text-xs">{atleta.equipe}</span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="text-gray-400 text-xs">
                      {[atleta.cidade, atleta.estado].filter(Boolean).join(' - ') || '-'}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-center">
                    <span className="text-gray-300">{atleta.total_corridas || 0}</span>
                  </td>
                  <td className="py-3 px-3 text-center">
                    {atleta.dias_inativo != null ? (
                      <span className={`font-medium ${
                        atleta.dias_inativo > 60 ? 'text-red-400' :
                        atleta.dias_inativo > 30 ? 'text-orange-400' :
                        'text-yellow-400'
                      }`}>
                        {atleta.dias_inativo}d
                      </span>
                    ) : (
                      <span className="text-gray-500">-</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-center">
                    {atleta.nunca_submeteu ? (
                      <Badge className="bg-gray-600/50 text-gray-400 text-[10px]">Nunca competiu</Badge>
                    ) : (
                      <Badge className="bg-orange-500/20 text-orange-300 text-[10px]">Parou</Badge>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {atletasOrdenados.length > 50 && (
            <p className="text-center text-gray-500 text-sm mt-3">
              Mostrando 50 de {atletasOrdenados.length} atletas inativos
            </p>
          )}
          {atletasOrdenados.length === 0 && (
            <div className="text-center py-10">
              <Users className="w-12 h-12 text-emerald-500 mx-auto mb-3 opacity-50" />
              <p className="text-gray-400">Nenhum atleta inativo encontrado com esses filtros</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default DashboardRetencao;
