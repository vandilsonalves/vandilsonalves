// /app/frontend/src/components/StravaIntegration.jsx
// Componente para integração com Strava

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, ExternalLink, RefreshCw, Unlink, CheckCircle2, 
  Activity, Timer, Mountain, TrendingUp
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Ícone do Strava (SVG inline)
const StravaIcon = ({ className = "w-6 h-6" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.598h4.172L10.463 0l-7 13.828h4.169"/>
  </svg>
);

const StravaIntegration = ({ token }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [status, setStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    // Verificar parâmetros de callback do Strava
    const stravaSuccess = searchParams.get('strava_success');
    const stravaError = searchParams.get('strava_error');

    if (stravaSuccess === 'true') {
      toast.success('Strava conectado com sucesso!');
      // Limpar parâmetros da URL
      searchParams.delete('strava_success');
      setSearchParams(searchParams);
    }

    if (stravaError) {
      const errorMessages = {
        'access_denied': 'Acesso negado. Você precisa autorizar o app.',
        'state_missing': 'Erro de segurança. Tente novamente.',
        'invalid_state': 'Sessão expirada. Tente novamente.',
        'token_exchange_failed': 'Erro ao conectar. Tente novamente.'
      };
      toast.error(errorMessages[stravaError] || 'Erro ao conectar com Strava');
      searchParams.delete('strava_error');
      setSearchParams(searchParams);
    }

    fetchStravaStatus();
  }, []);

  const fetchStravaStatus = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/strava/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatus(response.data);

      // Se conectado, buscar estatísticas e atividades
      if (response.data.conectado) {
        await Promise.all([fetchStats(), fetchActivities()]);
      }
    } catch (error) {
      console.error('Erro ao buscar status Strava:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/strava/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
    }
  };

  const fetchActivities = async () => {
    try {
      const response = await axios.get(`${API}/strava/activities?limit=5`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActivities(response.data.activities || []);
    } catch (error) {
      console.error('Erro ao buscar atividades:', error);
    }
  };

  const handleConnect = async () => {
    try {
      const response = await axios.get(`${API}/strava/authorize`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Redirecionar para autorização do Strava
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error('Erro ao iniciar conexão com Strava');
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const response = await axios.post(`${API}/strava/sync?max_activities=50`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(response.data.message);
      
      // Atualizar dados
      await Promise.all([fetchStats(), fetchActivities()]);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao sincronizar');
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Deseja realmente desconectar o Strava?')) return;
    
    setDisconnecting(true);
    try {
      await axios.delete(`${API}/strava/disconnect`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Strava desconectado');
      setStatus({ conectado: false });
      setStats(null);
      setActivities([]);
    } catch (error) {
      toast.error('Erro ao desconectar');
    } finally {
      setDisconnecting(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', { 
      day: '2-digit', 
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-6 flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-orange-500" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-800 border-slate-700" data-testid="strava-integration">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
              <StravaIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-lg text-white">Strava</CardTitle>
              <CardDescription className="text-slate-400">
                Importe suas corridas automaticamente
              </CardDescription>
            </div>
          </div>
          {status?.conectado && (
            <Badge className="bg-green-600">Conectado</Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {!status?.conectado ? (
          // Estado: Não conectado
          <div className="text-center py-4">
            <p className="text-slate-400 mb-4">
              Conecte sua conta do Strava para importar suas corridas e acompanhar seu progresso.
            </p>
            <Button 
              onClick={handleConnect}
              className="bg-orange-500 hover:bg-orange-600 text-white"
              data-testid="connect-strava-btn"
            >
              <StravaIcon className="w-5 h-5 mr-2" />
              Conectar com Strava
            </Button>
          </div>
        ) : (
          // Estado: Conectado
          <>
            {/* Info do perfil Strava */}
            <div className="flex items-center gap-3 p-3 bg-slate-700/50 rounded-lg">
              {status.foto && (
                <img 
                  src={status.foto} 
                  alt="Strava Profile" 
                  className="w-10 h-10 rounded-full"
                />
              )}
              <div className="flex-1">
                <p className="text-white font-medium">{status.nome}</p>
                <p className="text-sm text-slate-400">@{status.username}</p>
              </div>
              <a 
                href={`https://www.strava.com/athletes/${status.athlete_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-400 hover:text-orange-300"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            {/* Estatísticas */}
            {stats && stats.total_atividades > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                  <Activity className="w-5 h-5 mx-auto mb-1 text-orange-400" />
                  <p className="text-lg font-bold text-white">{stats.total_atividades}</p>
                  <p className="text-xs text-slate-400">Corridas</p>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                  <TrendingUp className="w-5 h-5 mx-auto mb-1 text-green-400" />
                  <p className="text-lg font-bold text-white">{stats.total_distancia_km} km</p>
                  <p className="text-xs text-slate-400">Distância</p>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                  <Timer className="w-5 h-5 mx-auto mb-1 text-blue-400" />
                  <p className="text-lg font-bold text-white">{stats.total_tempo_horas}h</p>
                  <p className="text-xs text-slate-400">Tempo</p>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                  <Mountain className="w-5 h-5 mx-auto mb-1 text-purple-400" />
                  <p className="text-lg font-bold text-white">{stats.total_elevacao_m}m</p>
                  <p className="text-xs text-slate-400">Elevação</p>
                </div>
              </div>
            )}

            {/* Últimas atividades */}
            {activities.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-slate-300 mb-2">Últimas corridas importadas</h4>
                <div className="space-y-2">
                  {activities.slice(0, 3).map((activity, idx) => (
                    <div 
                      key={idx}
                      className="flex items-center justify-between p-2 bg-slate-700/30 rounded-lg text-sm"
                    >
                      <div>
                        <p className="text-white font-medium">{activity.nome}</p>
                        <p className="text-xs text-slate-400">{formatDate(activity.data_inicio_local)}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-orange-400 font-medium">{activity.distancia_km} km</p>
                        <p className="text-xs text-slate-400">{activity.pace} /km</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Última sincronização */}
            {status.ultima_sincronizacao && (
              <p className="text-xs text-slate-500 text-center">
                Última sincronização: {formatDate(status.ultima_sincronizacao)}
              </p>
            )}

            {/* Botões de ação */}
            <div className="flex gap-2">
              <Button 
                onClick={handleSync}
                disabled={syncing}
                className="flex-1 bg-orange-500 hover:bg-orange-600"
                data-testid="sync-strava-btn"
              >
                {syncing ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <RefreshCw className="w-4 h-4 mr-2" />
                )}
                Sincronizar
              </Button>
              <Button 
                onClick={handleDisconnect}
                disabled={disconnecting}
                variant="outline"
                className="border-red-500/50 text-red-400 hover:bg-red-500/20"
                data-testid="disconnect-strava-btn"
              >
                {disconnecting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Unlink className="w-4 h-4" />
                )}
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default StravaIntegration;
