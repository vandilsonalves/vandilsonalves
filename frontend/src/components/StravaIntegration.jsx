import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Loader2, ExternalLink, RefreshCw, Unlink, CheckCircle2, 
  Activity, Timer, Mountain, TrendingUp, Shield, ScrollText,
  ChevronDown, ChevronUp, X
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StravaIcon = ({ className = "w-6 h-6" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.598h4.172L10.463 0l-7 13.828h4.169"/>
  </svg>
);

const POLITICA_PRIVACIDADE = `POLÍTICA DE PRIVACIDADE – RANKING RUN

Última atualização: 2026

A presente Política de Privacidade descreve como o Ranking Run coleta, utiliza, armazena e protege os dados dos usuários, especialmente no contexto da integração com a API do Strava.

Ao utilizar nossa plataforma, você concorda com os termos aqui descritos.

1. SOBRE O RANKING RUN

O Ranking Run é uma plataforma digital voltada para atletas de corrida de rua, com o objetivo de centralizar informações, promover engajamento e facilitar a visualização de dados esportivos provenientes de integrações autorizadas pelo usuário.

2. INTEGRAÇÃO COM O STRAVA

O Ranking Run utiliza a API oficial do Strava para permitir que os usuários conectem suas contas e visualizem suas próprias atividades dentro da plataforma.

Ao conectar sua conta Strava, o usuário autoriza o Ranking Run a acessar dados básicos de atividades, incluindo:

• Distância percorrida
• Tempo de atividade
• Tipo de atividade
• Data da atividade
• Informações públicas associadas ao perfil

Esses dados são acessados exclusivamente mediante autorização do usuário, através do fluxo oficial de autenticação do Strava (OAuth).

3. FINALIDADE DO USO DOS DADOS

Os dados obtidos via Strava são utilizados exclusivamente para:

• Exibição das atividades do usuário dentro da plataforma
• Visualização de dados já disponíveis no clube do Strava vinculado
• Geração de painéis informativos e estatísticos
• Melhoria da experiência do usuário

O Ranking Run NÃO utiliza os dados para:

• Venda ou comercialização
• Compartilhamento com terceiros
• Publicidade direcionada baseada em dados do Strava

4. DADOS DE CLUBES DO STRAVA

O Ranking Run pode exibir informações provenientes de clubes do Strava dos quais o usuário já faz parte, como o clube:

https://www.strava.com/clubs/rankingrun

Essas informações são exibidas dentro da plataforma apenas para facilitar o acesso e visualização, sem alteração ou redistribuição indevida.

5. CONTROLE DO USUÁRIO

O usuário possui total controle sobre seus dados e pode, a qualquer momento:

• Desconectar sua conta Strava
• Revogar permissões diretamente no Strava
• Solicitar a exclusão de seus dados

Após a desconexão, o Ranking Run interrompe imediatamente a sincronização de dados.

6. ARMAZENAMENTO E SEGURANÇA

Os dados são armazenados de forma segura, utilizando boas práticas de proteção da informação, incluindo:

• Criptografia de dados sensíveis
• Controle de acesso restrito
• Monitoramento de segurança

7. CONFORMIDADE COM A LGPD

O Ranking Run está em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), garantindo:

• Transparência no uso de dados
• Consentimento do usuário
• Direito de acesso, correção e exclusão
• Segurança e proteção das informações

8. COMPARTILHAMENTO DE DADOS

O Ranking Run não compartilha dados pessoais com terceiros, exceto quando:

• Necessário para cumprimento legal
• Exigido por autoridades competentes

9. RELAÇÃO COM O STRAVA

O Ranking Run utiliza a API do Strava de acordo com os termos estabelecidos pelo próprio Strava, disponíveis em:

https://www.strava.com/legal/api

O Ranking Run não é afiliado oficialmente ao Strava, mas utiliza seus serviços de forma autorizada via API.

10. ALTERAÇÕES NA POLÍTICA

Esta política pode ser atualizada a qualquer momento para garantir conformidade legal e melhorias no serviço.

11. CONTATO

Em caso de dúvidas ou solicitações relacionadas a dados, entre em contato:

suporte@rankingrun.com.br`;

// Tela de consentimento/autorização antes de conectar o Strava
const StravaConsentScreen = ({ onConnect, onCancel }) => {
  const [accepted, setAccepted] = useState(false);
  const [showPolicy, setShowPolicy] = useState(false);
  const [connecting, setConnecting] = useState(false);

  const handleConnect = async () => {
    if (!accepted) return;
    setConnecting(true);
    await onConnect();
    setConnecting(false);
  };

  return (
    <div className="space-y-5">
      {/* Header com ícone */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-orange-500/15 border border-orange-500/30 mb-4">
          <StravaIcon className="w-9 h-9 text-orange-400" />
        </div>
        <h3 className="text-lg font-bold text-white mb-1">
          Conectar com Strava
        </h3>
        <p className="text-sm text-slate-400">
          Autorize o acesso aos seus dados de atividades
        </p>
      </div>

      {/* Explicação */}
      <div className="bg-slate-700/40 rounded-lg p-4 space-y-3">
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-slate-300 leading-relaxed">
              Ao conectar sua conta Strava ao Ranking Run, você autoriza o acesso 
              aos seus dados de atividades (como distância, tempo e informações 
              básicas de treino) para exibição dentro da plataforma.
            </p>
          </div>
        </div>

        <div className="border-t border-slate-600/50 pt-3 space-y-2">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Esses dados serão utilizados exclusivamente para:
          </p>
          <ul className="space-y-1.5">
            {[
              'Exibir suas atividades dentro do ambiente do Ranking Run',
              'Mostrar informações já disponíveis no seu clube do Strava',
              'Melhorar sua experiência dentro da plataforma'
            ].map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div className="border-t border-slate-600/50 pt-3 space-y-1">
          <p className="text-xs text-slate-400 flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            O Ranking Run <strong className="text-emerald-400">não vende, compartilha ou comercializa</strong> seus dados.
          </p>
          <p className="text-xs text-slate-400 flex items-center gap-1.5">
            <Unlink className="w-3.5 h-3.5 text-blue-400" />
            Você pode <strong className="text-blue-400">desconectar sua conta a qualquer momento</strong>.
          </p>
        </div>
      </div>

      {/* Política de Privacidade (expansível) */}
      <div className="border border-slate-700 rounded-lg overflow-hidden">
        <button
          onClick={() => setShowPolicy(!showPolicy)}
          className="w-full flex items-center justify-between px-4 py-3 text-sm text-slate-300 hover:bg-slate-700/30 transition-colors"
          data-testid="toggle-privacy-policy"
        >
          <span className="flex items-center gap-2">
            <ScrollText className="w-4 h-4 text-slate-400" />
            Política de Privacidade
          </span>
          {showPolicy ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </button>
        {showPolicy && (
          <div className="px-4 pb-4 max-h-64 overflow-y-auto border-t border-slate-700">
            <pre className="text-xs text-slate-400 whitespace-pre-wrap font-sans leading-relaxed pt-3">
              {POLITICA_PRIVACIDADE}
            </pre>
          </div>
        )}
      </div>

      {/* Checkbox obrigatório */}
      <div className="flex items-start gap-3 p-3 bg-slate-700/30 rounded-lg border border-slate-700">
        <Checkbox
          id="consent-checkbox"
          checked={accepted}
          onCheckedChange={(checked) => setAccepted(checked === true)}
          className="mt-0.5 border-slate-500 data-[state=checked]:bg-orange-500 data-[state=checked]:border-orange-500"
          data-testid="strava-consent-checkbox"
        />
        <label htmlFor="consent-checkbox" className="text-sm text-slate-300 cursor-pointer leading-relaxed">
          Eu autorizo o uso dos meus dados conforme descrito na Política de Privacidade acima
        </label>
      </div>

      {/* Botões */}
      <div className="flex gap-3">
        <Button
          onClick={handleConnect}
          disabled={!accepted || connecting}
          className="flex-1 bg-orange-500 hover:bg-orange-600 text-white disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="strava-consent-connect-btn"
        >
          {connecting ? (
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <StravaIcon className="w-5 h-5 mr-2" />
          )}
          Conectar com Strava
        </Button>
        <Button
          onClick={onCancel}
          variant="outline"
          className="border-slate-600 text-slate-300 hover:bg-slate-700"
          data-testid="strava-consent-cancel-btn"
        >
          <X className="w-4 h-4 mr-1" />
          Cancelar
        </Button>
      </div>
    </div>
  );
};

const StravaIntegration = ({ token }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [status, setStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [showConsentScreen, setShowConsentScreen] = useState(false);

  useEffect(() => {
    const stravaSuccess = searchParams.get('strava_success');
    const stravaError = searchParams.get('strava_error');

    if (stravaSuccess === 'true') {
      toast.success('Strava conectado com sucesso!');
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
      setShowConsentScreen(false);
    } catch (error) {
      toast.error('Erro ao desconectar');
    } finally {
      setDisconnecting(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
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
          showConsentScreen ? (
            <StravaConsentScreen 
              onConnect={handleConnect}
              onCancel={() => setShowConsentScreen(false)}
            />
          ) : (
            <div className="text-center py-4">
              <p className="text-slate-400 mb-4">
                Conecte sua conta do Strava para importar suas corridas e acompanhar seu progresso.
              </p>
              <Button 
                onClick={() => setShowConsentScreen(true)}
                className="bg-orange-500 hover:bg-orange-600 text-white"
                data-testid="connect-strava-btn"
              >
                <StravaIcon className="w-5 h-5 mr-2" />
                Conectar com Strava
              </Button>
            </div>
          )
        ) : (
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
                Desconectar
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default StravaIntegration;
