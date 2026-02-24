import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import RankingTable from '@/components/RankingTable';
import { Search } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RankingPage = () => {
  const [tipoRanking, setTipoRanking] = useState('nacional'); // 'nacional' ou 'estadual'
  const [ufSelecionada, setUfSelecionada] = useState('');
  const [estados, setEstados] = useState([]);
  const [rankingData, setRankingData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Filtros
  const [filtroNome, setFiltroNome] = useState('');
  const [filtroEquipe, setFiltroEquipe] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('');
  const [filtroCidade, setFiltroCidade] = useState('');

  // Buscar estados disponíveis
  useEffect(() => {
    const fetchEstados = async () => {
      try {
        const response = await axios.get(`${API}/ranking/estados?ano=2025`);
        setEstados(response.data.estados);
        if (response.data.estados.length > 0) {
          setUfSelecionada(response.data.estados[0]);
        }
      } catch (error) {
        console.error('Erro ao buscar estados:', error);
      }
    };
    fetchEstados();
  }, []);

  // Buscar ranking
  useEffect(() => {
    const fetchRanking = async () => {
      setLoading(true);
      try {
        let url = `${API}/ranking/nacional?ano=2025`;
        
        if (tipoRanking === 'estadual' && ufSelecionada) {
          url = `${API}/ranking/estadual/${ufSelecionada}?ano=2025`;
        }
        
        const response = await axios.get(url);
        setRankingData(response.data);
      } catch (error) {
        console.error('Erro ao buscar ranking:', error);
        setRankingData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRanking();
  }, [tipoRanking, ufSelecionada]);

  // Aplicar filtros
  const rankingFiltrado = rankingData.filter(atleta => {
    const nomeMatch = atleta.nome.toLowerCase().includes(filtroNome.toLowerCase());
    const equipeMatch = atleta.equipe.toLowerCase().includes(filtroEquipe.toLowerCase());
    const estadoMatch = atleta.uf.toLowerCase().includes(filtroEstado.toLowerCase());
    const cidadeMatch = atleta.cidade.toLowerCase().includes(filtroCidade.toLowerCase());
    
    return nomeMatch && equipeMatch && estadoMatch && cidadeMatch;
  });

  const handleTipoChange = (value) => {
    setTipoRanking(value);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight">
            Ranking Run Pró
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Sistema Nacional de Rankings de Corrida 2025
          </p>
        </div>

        {/* Toggle Nacional/Estadual */}
        <Card className="mb-6 border-slate-200 dark:border-slate-800 shadow-lg">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
              <div className="flex-1">
                <Label className="text-sm font-medium mb-2 block">Tipo de Ranking</Label>
                <Tabs value={tipoRanking} onValueChange={handleTipoChange} className="w-full md:w-auto">
                  <TabsList className="grid w-full md:w-[400px] grid-cols-2">
                    <TabsTrigger value="nacional" className="font-semibold" data-testid="toggle-nacional">
                      🇧🇷 Nacional
                    </TabsTrigger>
                    <TabsTrigger value="estadual" className="font-semibold" data-testid="toggle-estadual">
                      🏳 Estadual
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Dropdown UF (apenas para estadual) */}
              {tipoRanking === 'estadual' && (
                <div className="flex-1">
                  <Label className="text-sm font-medium mb-2 block">Selecionar Estado</Label>
                  <Select value={ufSelecionada} onValueChange={setUfSelecionada}>
                    <SelectTrigger className="w-full md:w-[200px]" data-testid="select-estado">
                      <SelectValue placeholder="Selecione o estado" />
                    </SelectTrigger>
                    <SelectContent>
                      {estados.map(uf => (
                        <SelectItem key={uf} value={uf} data-testid={`estado-${uf}`}>
                          {uf}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Layout Principal: Filtros + Tabela */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar de Filtros */}
          <Card className="lg:col-span-1 h-fit border-slate-200 dark:border-slate-800 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Search className="w-5 h-5" />
                Opções de filtro
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filtro Nome */}
              <div>
                <Label htmlFor="filtro-nome" className="text-sm font-medium mb-2 block">
                  Nome
                </Label>
                <Input
                  id="filtro-nome"
                  placeholder="Buscar por nome"
                  value={filtroNome}
                  onChange={(e) => setFiltroNome(e.target.value)}
                  data-testid="filtro-nome"
                />
              </div>

              {/* Filtro Equipe */}
              <div>
                <Label htmlFor="filtro-equipe" className="text-sm font-medium mb-2 block">
                  Equipe
                </Label>
                <Input
                  id="filtro-equipe"
                  placeholder="Todas as equipes"
                  value={filtroEquipe}
                  onChange={(e) => setFiltroEquipe(e.target.value)}
                  data-testid="filtro-equipe"
                />
              </div>

              {/* Filtro Estado */}
              <div>
                <Label htmlFor="filtro-estado" className="text-sm font-medium mb-2 block">
                  Estado
                </Label>
                <Input
                  id="filtro-estado"
                  placeholder="Todos os estados"
                  value={filtroEstado}
                  onChange={(e) => setFiltroEstado(e.target.value)}
                  data-testid="filtro-estado"
                />
              </div>

              {/* Filtro Cidade */}
              <div>
                <Label htmlFor="filtro-cidade" className="text-sm font-medium mb-2 block">
                  Cidade
                </Label>
                <Input
                  id="filtro-cidade"
                  placeholder="Todas cidades"
                  value={filtroCidade}
                  onChange={(e) => setFiltroCidade(e.target.value)}
                  data-testid="filtro-cidade"
                />
              </div>

              {/* Botão Limpar Filtros */}
              {(filtroNome || filtroEquipe || filtroEstado || filtroCidade) && (
                <button
                  onClick={() => {
                    setFiltroNome('');
                    setFiltroEquipe('');
                    setFiltroEstado('');
                    setFiltroCidade('');
                  }}
                  className="w-full text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white underline"
                  data-testid="limpar-filtros"
                >
                  Limpar filtros
                </button>
              )}
            </CardContent>
          </Card>

          {/* Tabela de Ranking */}
          <div className="lg:col-span-3">
            <Card className="border-slate-200 dark:border-slate-800 shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl">
                  {tipoRanking === 'nacional' ? 'Ranking Nacional' : `Ranking ${ufSelecionada}`}
                  <span className="ml-2 text-sm font-normal text-slate-600 dark:text-slate-400">
                    ({rankingFiltrado.length} atletas)
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-12 text-slate-600 dark:text-slate-400">
                    Carregando ranking...
                  </div>
                ) : (
                  <RankingTable data={rankingFiltrado} />
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RankingPage;