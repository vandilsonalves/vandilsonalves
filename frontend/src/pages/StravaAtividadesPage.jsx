// /app/frontend/src/pages/StravaAtividadesPage.jsx
// Página de atividades do Strava - Similar ao Clube do Strava

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Loader2, Trophy, Activity, Timer, Mountain, TrendingUp,
  ChevronLeft, Users, Calendar, ArrowUpDown, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Ícone do Strava
const StravaIcon = ({ className = "w-6 h-6" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.598h4.172L10.463 0l-7 13.828h4.169"/>
  </svg>
);

// Componente de medalha para os líderes
const MedalIcon = ({ position }) => {
  const colors = {
    1: 'text-yellow-400',
    2: 'text-gray-400',
    3: 'text-amber-600'
  };
  return (
    <Trophy className={`w-5 h-5 ${colors[position] || 'text-gray-500'}`} />
  );
};

// Card de líder da semana
const LiderCard = ({ titulo, icone: Icone, lideres }) => (
  <Card className="bg-slate-800 border-slate-700">
    <CardHeader className="pb-2">
      <CardTitle className="text-sm font-medium text-slate-300 flex items-center gap-2">
        <Icone className="w-4 h-4 text-orange-400" />
        {titulo}
      </CardTitle>
    </CardHeader>
    <CardContent className="space-y-2">
      {lideres?.length > 0 ? (
        lideres.map((lider, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <MedalIcon position={lider.posicao} />
            <img 
              src={lider.foto || '/default-avatar.png'} 
              alt={lider.nome}
              className="w-7 h-7 rounded-full object-cover"
            />
            <span className="text-sm text-white flex-1 truncate">{lider.nome}</span>
            <span className="text-sm font-bold text-orange-400">{lider.valor}</span>
          </div>
        ))
      ) : (
        <p className="text-sm text-slate-500 text-center py-2">Sem dados</p>
      )}
    </CardContent>
  </Card>
);

// Linha da tabela de classificação
const ClassificacaoRow = ({ atleta, index }) => (
  <tr className={`border-b border-slate-700 hover:bg-slate-700/50 transition-colors ${index < 3 ? 'bg-slate-700/30' : ''}`}>
    <td className="py-3 px-2 text-center">
      <span className={`font-bold ${index === 0 ? 'text-yellow-400' : index === 1 ? 'text-gray-400' : index === 2 ? 'text-amber-600' : 'text-slate-400'}`}>
        {atleta.posicao}
      </span>
    </td>
    <td className="py-3 px-2">
      <div className="flex items-center gap-3">
        <img 
          src={atleta.foto || '/default-avatar.png'} 
          alt={atleta.nome}
          className="w-10 h-10 rounded-full object-cover border-2 border-slate-600"
        />
        <div>
          <p className="font-medium text-white">{atleta.nome}</p>
          {atleta.strava_username && (
            <p className="text-xs text-slate-500">@{atleta.strava_username}</p>
          )}
        </div>
      </div>
    </td>
    <td className="py-3 px-2 text-right">
      <span className="font-bold text-orange-400">{atleta.total_distancia_km}</span>
      <span className="text-xs text-slate-400 ml-1">km</span>
    </td>
    <td className="py-3 px-2 text-center text-white">{atleta.total_corridas}</td>
    <td className="py-3 px-2 text-right">
      <span className="text-white">{atleta.maior_corrida_km}</span>
      <span className="text-xs text-slate-400 ml-1">km</span>
    </td>
    <td className="py-3 px-2 text-center text-emerald-400">{atleta.ritmo_medio}<span className="text-xs text-slate-400">/km</span></td>
    <td className="py-3 px-2 text-right">
      <span className="text-white">{atleta.total_elevacao_m}</span>
      <span className="text-xs text-slate-400 ml-1">m</span>
    </td>
  </tr>
);

const StravaAtividadesPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [periodo, setPeriodo] = useState('esta_semana');
  const [ordenarPor, setOrdenarPor] = useState('distancia');
  const [classificacao, setClassificacao] = useState([]);
  const [lideres, setLideres] = useState(null);
  const [periodoInfo, setPeriodoInfo] = useState(null);
  const [totalMembros, setTotalMembros] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);

  useEffect(() => {
    fetchData();
    fetchSyncStatus();
  }, [periodo, ordenarPor]);

  const fetchSyncStatus = async () => {
    try {
      const response = await axios.get(`${API}/strava/sync-status`);
      setSyncStatus(response.data);
    } catch (error) {
      console.error('Erro ao buscar status sync:', error);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [classRes, lideresRes, membrosRes] = await Promise.all([
        axios.get(`${API}/strava-atividades/classificacao?periodo=${periodo}&ordenar_por=${ordenarPor}`),
        axios.get(`${API}/strava-atividades/lideres?periodo=${periodo === 'esta_semana' ? 'semana_passada' : periodo}`),
        axios.get(`${API}/strava-atividades/membros`)
      ]);
      
      setClassificacao(classRes.data.classificacao || []);
      setPeriodoInfo(classRes.data.periodo);
      setLideres(lideresRes.data);
      setTotalMembros(membrosRes.data.total || 0);
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
      toast.error('Erro ao carregar atividades');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
    toast.success('Dados atualizados!');
  };

  const ordenacaoOptions = [
    { value: 'distancia', label: 'Distância', icon: TrendingUp },
    { value: 'corridas', label: 'Corridas', icon: Activity },
    { value: 'maior_corrida', label: 'Mais longa', icon: TrendingUp },
    { value: 'ritmo', label: 'Ritmo médio', icon: Timer },
    { value: 'elevacao', label: 'Ganho de elev.', icon: Mountain },
  ];

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-600 to-orange-500 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="icon"
                onClick={() => navigate('/')}
                className="text-white hover:bg-white/20"
              >
                <ChevronLeft className="w-6 h-6" />
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                  <StravaIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">Atividades Strava</h1>
                  <p className="text-white/80 text-sm">Ranking Run - Clube</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-white/20 rounded-lg px-3 py-2">
                <Users className="w-4 h-4" />
                <span className="font-medium">{totalMembros} membros</span>
              </div>
              
              {/* Indicador de Sync Automático */}
              {syncStatus?.running && (
                <div className="hidden sm:flex items-center gap-2 bg-green-500/20 border border-green-400/30 rounded-lg px-3 py-2 text-sm">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span>Sync automático ativo</span>
                </div>
              )}
              
              <Button 
                variant="ghost" 
                size="icon"
                onClick={handleRefresh}
                disabled={refreshing}
                className="text-white hover:bg-white/20"
                title="Atualizar dados"
              >
                <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      <div className="container mx-auto px-4 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
          </div>
        ) : (
          <>
            {/* Líderes da semana passada */}
            {lideres && (
              <div className="mb-8">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-yellow-400" />
                  Líderes da semana passada
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <LiderCard 
                    titulo="Distância" 
                    icone={TrendingUp} 
                    lideres={lideres.distancia} 
                  />
                  <LiderCard 
                    titulo="Tempo total da corrida" 
                    icone={Timer} 
                    lideres={lideres.tempo_total} 
                  />
                  <LiderCard 
                    titulo="Subida" 
                    icone={Mountain} 
                    lideres={lideres.elevacao} 
                  />
                </div>
              </div>
            )}

            {/* Classificação desta semana */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <CardTitle className="text-white flex items-center gap-2">
                    <Activity className="w-5 h-5 text-orange-400" />
                    Classificação {periodo === 'esta_semana' ? 'desta semana' : 'da semana passada'}
                  </CardTitle>
                  
                  {/* Tabs de período */}
                  <div className="flex items-center gap-2">
                    <Button
                      variant={periodo === 'semana_passada' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setPeriodo('semana_passada')}
                      className={periodo === 'semana_passada' ? 'bg-orange-500 hover:bg-orange-600' : 'border-slate-600'}
                    >
                      Semana passada
                    </Button>
                    <Button
                      variant={periodo === 'esta_semana' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setPeriodo('esta_semana')}
                      className={periodo === 'esta_semana' ? 'bg-orange-500 hover:bg-orange-600' : 'border-slate-600'}
                    >
                      Esta semana
                    </Button>
                  </div>
                </div>
                
                {/* Info do período */}
                {periodoInfo && (
                  <p className="text-sm text-slate-400 flex items-center gap-2 mt-2">
                    <Calendar className="w-4 h-4" />
                    Período: {periodoInfo.inicio} a {periodoInfo.fim}
                  </p>
                )}
              </CardHeader>
              
              <CardContent>
                {classificacao.length === 0 ? (
                  <div className="text-center py-12">
                    <StravaIcon className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-400 mb-2">
                      Nenhuma atividade registrada
                    </h3>
                    <p className="text-slate-500 text-sm mb-4">
                      Conecte seu Strava e sincronize suas corridas para aparecer aqui!
                    </p>
                    <Button 
                      onClick={() => navigate('/perfil')}
                      className="bg-orange-500 hover:bg-orange-600"
                    >
                      <StravaIcon className="w-4 h-4 mr-2" />
                      Conectar Strava
                    </Button>
                  </div>
                ) : (
                  <>
                    {/* Botões de ordenação */}
                    <div className="flex flex-wrap gap-2 mb-4 pb-4 border-b border-slate-700">
                      {ordenacaoOptions.map((opt) => (
                        <Button
                          key={opt.value}
                          variant={ordenarPor === opt.value ? 'default' : 'ghost'}
                          size="sm"
                          onClick={() => setOrdenarPor(opt.value)}
                          className={ordenarPor === opt.value 
                            ? 'bg-orange-500/20 text-orange-400 border border-orange-500/50' 
                            : 'text-slate-400 hover:text-white'}
                        >
                          <opt.icon className="w-3 h-3 mr-1" />
                          {opt.label}
                          {ordenarPor === opt.value && <ArrowUpDown className="w-3 h-3 ml-1" />}
                        </Button>
                      ))}
                    </div>
                    
                    {/* Tabela de classificação */}
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="text-slate-400 text-sm border-b border-slate-700">
                            <th className="py-3 px-2 text-center w-12">Pos.</th>
                            <th className="py-3 px-2 text-left">Atleta</th>
                            <th className="py-3 px-2 text-right">Distância</th>
                            <th className="py-3 px-2 text-center">Corridas</th>
                            <th className="py-3 px-2 text-right">Mais longa</th>
                            <th className="py-3 px-2 text-center">Ritmo médio</th>
                            <th className="py-3 px-2 text-right">Ganho de elev.</th>
                          </tr>
                        </thead>
                        <tbody>
                          {classificacao.map((atleta, idx) => (
                            <ClassificacaoRow key={atleta.usuario_id} atleta={atleta} index={idx} />
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default StravaAtividadesPage;
