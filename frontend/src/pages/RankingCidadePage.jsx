// /app/frontend/src/pages/RankingCidadePage.jsx
// Ranking por Cidade/Bairro - Visualização local do ranking

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { 
  ArrowLeft, MapPin, Trophy, Users, Medal, 
  Search, Loader2, Building2, Map
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;
const BACKEND_URL = API;

const RankingCidadePage = () => {
  const navigate = useNavigate();
  
  // Estados para filtros
  const [estados, setEstados] = useState([]);
  const [cidades, setCidades] = useState([]);
  const [selectedEstado, setSelectedEstado] = useState('');
  const [selectedCidade, setSelectedCidade] = useState('');
  const [modalidade, setModalidade] = useState('profissional');
  const [genero, setGenero] = useState('M');
  const [searchCidade, setSearchCidade] = useState('');
  
  // Estados para dados
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingCidades, setLoadingCidades] = useState(false);
  const [stats, setStats] = useState({ total: 0, cidade: '', estado: '' });

  // Carregar estados ao montar
  useEffect(() => {
    fetchEstados();
  }, []);

  // Carregar cidades quando estado mudar
  useEffect(() => {
    if (selectedEstado) {
      fetchCidades(selectedEstado);
      setSelectedCidade('');
      setRanking([]);
    }
  }, [selectedEstado]);

  // Carregar ranking quando cidade mudar
  useEffect(() => {
    if (selectedEstado && selectedCidade) {
      fetchRanking();
    }
  }, [selectedCidade, modalidade, genero]);

  const fetchEstados = async () => {
    try {
      const response = await axios.get(`${API}/api/ranking/estados`);
      setEstados(response.data.estados || []);
    } catch (error) {
      console.error('Erro ao buscar estados:', error);
      toast.error('Erro ao carregar estados');
    }
  };

  const fetchCidades = async (estado) => {
    setLoadingCidades(true);
    try {
      const response = await axios.get(`${API}/api/ranking/cidades?estado=${estado}`);
      setCidades(response.data.cidades || []);
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
      toast.error('Erro ao carregar cidades');
    } finally {
      setLoadingCidades(false);
    }
  };

  const fetchRanking = async () => {
    if (!selectedEstado || !selectedCidade) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams({
        modalidade,
        genero,
        ano: new Date().getFullYear()
      });
      
      const response = await axios.get(
        `${API}/api/ranking/por-cidade/${encodeURIComponent(selectedEstado)}/${encodeURIComponent(selectedCidade)}?${params}`
      );
      
      setRanking(response.data.ranking || []);
      setStats({
        total: response.data.total || 0,
        cidade: response.data.cidade || selectedCidade,
        estado: response.data.estado || selectedEstado
      });
    } catch (error) {
      console.error('Erro ao buscar ranking:', error);
      toast.error('Erro ao carregar ranking da cidade');
    } finally {
      setLoading(false);
    }
  };

  // Filtrar cidades pela busca
  const cidadesFiltradas = cidades.filter(c => 
    c.nome.toLowerCase().includes(searchCidade.toLowerCase())
  );

  // Medalhas por posição
  const getMedalha = (posicao) => {
    if (posicao === 1) return <span className="text-2xl">🥇</span>;
    if (posicao === 2) return <span className="text-2xl">🥈</span>;
    if (posicao === 3) return <span className="text-2xl">🥉</span>;
    return <span className="text-lg font-bold text-slate-400">{posicao}º</span>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-green-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => navigate('/')}
              className="text-white hover:bg-white/20"
              data-testid="btn-voltar"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <MapPin className="h-6 w-6" />
                Ranking por Cidade
              </h1>
              <p className="text-emerald-100 text-sm">
                Veja a classificação dos atletas da sua região
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        {/* Filtros */}
        <Card className="bg-slate-800/50 border-slate-700 mb-6">
          <CardHeader className="pb-4">
            <CardTitle className="text-white flex items-center gap-2">
              <Map className="h-5 w-5 text-emerald-400" />
              Selecione a Localização
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Seletor de Estado */}
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Estado</label>
                <Select value={selectedEstado} onValueChange={setSelectedEstado}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="select-estado">
                    <SelectValue placeholder="Selecione o estado" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    {estados.map((estado) => (
                      <SelectItem key={estado} value={estado} className="text-white hover:bg-slate-700">
                        {estado}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Seletor de Cidade */}
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Cidade</label>
                <Select 
                  value={selectedCidade} 
                  onValueChange={setSelectedCidade}
                  disabled={!selectedEstado || loadingCidades}
                >
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="select-cidade">
                    {loadingCidades ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Carregando...
                      </div>
                    ) : (
                      <SelectValue placeholder={selectedEstado ? "Selecione a cidade" : "Selecione um estado primeiro"} />
                    )}
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700 max-h-60">
                    <div className="p-2 sticky top-0 bg-slate-800">
                      <Input
                        placeholder="Buscar cidade..."
                        value={searchCidade}
                        onChange={(e) => setSearchCidade(e.target.value)}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>
                    {cidadesFiltradas.map((cidade) => (
                      <SelectItem 
                        key={cidade.nome} 
                        value={cidade.nome} 
                        className="text-white hover:bg-slate-700"
                      >
                        <div className="flex items-center justify-between w-full">
                          <span>{cidade.nome}</span>
                          <Badge variant="outline" className="ml-2 text-xs">
                            {cidade.atletas} atletas
                          </Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Modalidade */}
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Modalidade</label>
                <Select value={modalidade} onValueChange={setModalidade}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="select-modalidade">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    <SelectItem value="profissional" className="text-white hover:bg-slate-700">
                      <div className="flex items-center gap-2">
                        <Trophy className="h-4 w-4 text-amber-400" />
                        Profissional/Amador
                      </div>
                    </SelectItem>
                    <SelectItem value="povao" className="text-white hover:bg-slate-700">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-green-400" />
                        Galera
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Gênero (apenas para profissional) */}
              {modalidade === 'profissional' && (
                <div>
                  <label className="text-sm text-slate-400 mb-2 block">Gênero</label>
                  <Select value={genero} onValueChange={setGenero}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="select-genero">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      <SelectItem value="M" className="text-white hover:bg-slate-700">Masculino</SelectItem>
                      <SelectItem value="F" className="text-white hover:bg-slate-700">Feminino</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Estatísticas da cidade */}
        {stats.total > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card className="bg-gradient-to-br from-emerald-600/20 to-green-600/20 border-emerald-500/30">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center">
                  <Building2 className="h-6 w-6 text-emerald-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Cidade</p>
                  <p className="text-xl font-bold text-white">{stats.cidade}</p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border-blue-500/30">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
                  <Map className="h-6 w-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Estado</p>
                  <p className="text-xl font-bold text-white">{stats.estado}</p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-amber-600/20 to-orange-600/20 border-amber-500/30">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center">
                  <Users className="h-6 w-6 text-amber-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Total de Atletas</p>
                  <p className="text-xl font-bold text-white">{stats.total}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Lista do Ranking */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
            <span className="ml-3 text-slate-400">Carregando ranking...</span>
          </div>
        ) : ranking.length > 0 ? (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Trophy className="h-5 w-5 text-amber-400" />
                Ranking de {stats.cidade} - {modalidade === 'povao' ? 'Galera' : 'Profissional/Amador'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {ranking.map((atleta, index) => (
                  <div 
                    key={atleta.id}
                    className={`flex items-center gap-4 p-4 rounded-lg transition-colors ${
                      index < 3 
                        ? 'bg-gradient-to-r from-amber-900/30 to-transparent border border-amber-500/30' 
                        : 'bg-slate-700/50 hover:bg-slate-700'
                    }`}
                    data-testid={`ranking-item-${atleta.id}`}
                  >
                    {/* Posição */}
                    <div className="w-12 flex justify-center">
                      {getMedalha(atleta.colocacao)}
                    </div>
                    
                    {/* Avatar */}
                    <Avatar className="h-12 w-12">
                      {atleta.foto_url ? (
                        <AvatarImage src={`${BACKEND_URL}${atleta.foto_url}`} />
                      ) : null}
                      <AvatarFallback className="bg-emerald-600 text-white">
                        {atleta.nome?.charAt(0) || '?'}
                      </AvatarFallback>
                    </Avatar>
                    
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-white truncate">{atleta.nome}</p>
                      <div className="flex items-center gap-2 text-sm text-slate-400">
                        {atleta.equipe && (
                          <span className="text-emerald-400">{atleta.equipe}</span>
                        )}
                        {atleta.faixa_etaria && (
                          <>
                            <span>•</span>
                            <span>{atleta.faixa_etaria}</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {/* Estatísticas */}
                    <div className="text-right">
                      <p className="text-lg font-bold text-amber-400">{atleta.pontos} pts</p>
                      <p className="text-xs text-slate-400">{atleta.total_corridas} corridas</p>
                    </div>
                    
                    {/* Badge Elite */}
                    {atleta.is_elite && (
                      <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                        Elite
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : selectedCidade ? (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="py-20 text-center">
              <MapPin className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Nenhum atleta encontrado</h3>
              <p className="text-slate-400">
                Não há atletas cadastrados em {selectedCidade} - {selectedEstado} para esta modalidade.
              </p>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="py-20 text-center">
              <Search className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Selecione uma localização</h3>
              <p className="text-slate-400">
                Escolha um estado e uma cidade para ver o ranking local.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default RankingCidadePage;
