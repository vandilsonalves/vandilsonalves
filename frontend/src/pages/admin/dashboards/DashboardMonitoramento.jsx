// /app/frontend/src/pages/admin/dashboards/DashboardMonitoramento.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { toast } from 'sonner';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar
} from 'recharts';
import {
  Activity, Cpu, HardDrive, MemoryStick, Clock, AlertTriangle,
  RefreshCw, Mail, Server, Zap, TrendingUp, AlertCircle, CheckCircle2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const DashboardMonitoramento = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/monitoring/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Erro ao buscar métricas:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    
    // Auto refresh a cada 30 segundos
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchData, 30000);
    }
    
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  const sendTestAlert = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/monitoring/test-alert`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const result = await response.json();
      if (response.ok) {
        toast.success(`Email de teste enviado para ${result.email}`);
      } else {
        toast.error(result.detail || 'Erro ao enviar email de teste');
      }
    } catch (error) {
      toast.error('Erro ao enviar email de teste');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'bg-emerald-500';
      case 'degraded': return 'bg-yellow-500';
      case 'unhealthy': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'healthy': return 'Saudável';
      case 'degraded': return 'Degradado';
      case 'unhealthy': return 'Crítico';
      default: return 'Desconhecido';
    }
  };

  const getUsageColor = (percent) => {
    if (percent >= 90) return 'text-red-500';
    if (percent >= 70) return 'text-yellow-500';
    return 'text-emerald-500';
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  if (!data) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Erro ao carregar dados de monitoramento</AlertDescription>
      </Alert>
    );
  }

  const { current, history_24h, thresholds } = data;
  const { system, requests, slowest_endpoints, active_alerts } = current;

  return (
    <div className="space-y-6" data-testid="monitoring-dashboard">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Monitoramento do Sistema</h2>
          <p className="text-gray-600">Métricas de saúde e performance do backend</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? 'border-emerald-500 text-emerald-600' : ''}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? 'Auto (30s)' : 'Manual'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={sendTestAlert}
          >
            <Mail className="w-4 h-4 mr-2" />
            Testar Alerta
          </Button>
          <Button
            size="sm"
            onClick={fetchData}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Status Badge */}
      <div className="flex items-center gap-4">
        <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${getStatusColor(current.status)} text-white`}>
          {current.status === 'healthy' ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <AlertTriangle className="w-5 h-5" />
          )}
          <span className="font-semibold">{getStatusText(current.status)}</span>
        </div>
        <span className="text-gray-500">
          Uptime: <strong>{requests.uptime_formatted}</strong>
        </span>
        <span className="text-gray-500">
          Última atualização: {formatTimestamp(current.timestamp)}
        </span>
      </div>

      {/* Active Alerts */}
      {active_alerts && active_alerts.length > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="font-semibold mb-2">{active_alerts.length} alerta(s) ativo(s):</div>
            <ul className="list-disc list-inside space-y-1">
              {active_alerts.map((alert, idx) => (
                <li key={idx}>{alert.message}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* System Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Cpu className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">CPU</p>
                  <p className={`text-2xl font-bold ${getUsageColor(system.cpu_percent)}`}>
                    {system.cpu_percent}%
                  </p>
                </div>
              </div>
              <div className="text-right text-xs text-gray-500">
                Limite: {thresholds.cpu_percent}%
              </div>
            </div>
            <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${system.cpu_percent >= 90 ? 'bg-red-500' : system.cpu_percent >= 70 ? 'bg-yellow-500' : 'bg-blue-500'}`}
                style={{ width: `${Math.min(system.cpu_percent, 100)}%` }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Memory */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <MemoryStick className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Memória</p>
                  <p className={`text-2xl font-bold ${getUsageColor(system.memory_percent)}`}>
                    {system.memory_percent}%
                  </p>
                </div>
              </div>
              <div className="text-right text-xs text-gray-500">
                {system.memory_used_gb}GB / {system.memory_total_gb}GB
              </div>
            </div>
            <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${system.memory_percent >= 85 ? 'bg-red-500' : system.memory_percent >= 70 ? 'bg-yellow-500' : 'bg-purple-500'}`}
                style={{ width: `${Math.min(system.memory_percent, 100)}%` }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Disk */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-orange-100 rounded-lg">
                  <HardDrive className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Disco</p>
                  <p className={`text-2xl font-bold ${getUsageColor(system.disk_percent)}`}>
                    {system.disk_percent}%
                  </p>
                </div>
              </div>
              <div className="text-right text-xs text-gray-500">
                {system.disk_used_gb}GB / {system.disk_total_gb}GB
              </div>
            </div>
            <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${system.disk_percent >= 90 ? 'bg-red-500' : system.disk_percent >= 70 ? 'bg-yellow-500' : 'bg-orange-500'}`}
                style={{ width: `${Math.min(system.disk_percent, 100)}%` }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Connections */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-emerald-100 rounded-lg">
                <Server className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Conexões de Rede</p>
                <p className="text-2xl font-bold text-emerald-600">
                  {system.network_connections}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Request Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-indigo-100 rounded-lg">
                <Activity className="w-6 h-6 text-indigo-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Requisições</p>
                <p className="text-2xl font-bold text-indigo-600">
                  {requests.total_requests.toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-cyan-100 rounded-lg">
                <Zap className="w-6 h-6 text-cyan-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Req/min</p>
                <p className="text-2xl font-bold text-cyan-600">
                  {requests.requests_per_minute}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-teal-100 rounded-lg">
                <Clock className="w-6 h-6 text-teal-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Tempo Médio</p>
                <p className={`text-2xl font-bold ${requests.avg_response_time_ms > 5000 ? 'text-red-500' : requests.avg_response_time_ms > 2000 ? 'text-yellow-500' : 'text-teal-600'}`}>
                  {requests.avg_response_time_ms}ms
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-lg ${requests.error_rate_percent > 5 ? 'bg-red-100' : 'bg-gray-100'}`}>
                <AlertCircle className={`w-6 h-6 ${requests.error_rate_percent > 5 ? 'text-red-600' : 'text-gray-600'}`} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Taxa de Erros</p>
                <p className={`text-2xl font-bold ${requests.error_rate_percent > 10 ? 'text-red-500' : requests.error_rate_percent > 5 ? 'text-yellow-500' : 'text-gray-600'}`}>
                  {requests.error_rate_percent}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Historical Metrics Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-600" />
              Histórico de Métricas (24h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {history_24h && history_24h.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={history_24h}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(val) => formatTimestamp(val)}
                    fontSize={12}
                  />
                  <YAxis fontSize={12} />
                  <Tooltip 
                    labelFormatter={(val) => new Date(val).toLocaleString('pt-BR')}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="cpu_percent" 
                    stackId="1"
                    stroke="#3b82f6" 
                    fill="#93c5fd" 
                    name="CPU %"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="memory_percent" 
                    stackId="2"
                    stroke="#8b5cf6" 
                    fill="#c4b5fd" 
                    name="Memória %"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                Aguardando dados históricos...
              </div>
            )}
          </CardContent>
        </Card>

        {/* Slowest Endpoints */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-orange-600" />
              Endpoints Mais Lentos
            </CardTitle>
          </CardHeader>
          <CardContent>
            {slowest_endpoints && slowest_endpoints.length > 0 ? (
              <div className="space-y-3">
                {slowest_endpoints.map((ep, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1 min-w-0">
                      <p className="font-mono text-sm truncate" title={ep.endpoint}>
                        {ep.endpoint}
                      </p>
                      <p className="text-xs text-gray-500">
                        {ep.request_count} requisições
                      </p>
                    </div>
                    <div className="text-right ml-4">
                      <p className={`font-bold ${ep.avg_time_ms > 2000 ? 'text-red-500' : ep.avg_time_ms > 500 ? 'text-yellow-500' : 'text-emerald-500'}`}>
                        {ep.avg_time_ms}ms
                      </p>
                      <p className="text-xs text-gray-500">
                        max: {ep.max_time_ms}ms
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                Nenhum endpoint registrado ainda
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Status Codes */}
      <Card>
        <CardHeader>
          <CardTitle>Distribuição de Status HTTP</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {Object.entries(requests.status_codes || {}).map(([code, count]) => {
              const codeNum = parseInt(code);
              let color = 'bg-gray-100 text-gray-800';
              if (codeNum >= 200 && codeNum < 300) color = 'bg-emerald-100 text-emerald-800';
              else if (codeNum >= 300 && codeNum < 400) color = 'bg-blue-100 text-blue-800';
              else if (codeNum >= 400 && codeNum < 500) color = 'bg-yellow-100 text-yellow-800';
              else if (codeNum >= 500) color = 'bg-red-100 text-red-800';
              
              return (
                <div key={code} className={`px-4 py-2 rounded-lg ${color}`}>
                  <span className="font-bold">{code}</span>
                  <span className="ml-2">{count}</span>
                </div>
              );
            })}
            {Object.keys(requests.status_codes || {}).length === 0 && (
              <p className="text-gray-500">Nenhuma requisição registrada</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Thresholds Info */}
      <Card>
        <CardHeader>
          <CardTitle>Limites de Alerta Configurados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">CPU</p>
              <p className="text-lg font-bold">{thresholds.cpu_percent}%</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Memória</p>
              <p className="text-lg font-bold">{thresholds.memory_percent}%</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Disco</p>
              <p className="text-lg font-bold">{thresholds.disk_percent}%</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Taxa Erros</p>
              <p className="text-lg font-bold">{thresholds.error_rate}%</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Resp. Máx</p>
              <p className="text-lg font-bold">{thresholds.response_time_avg}s</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sincronizar Rankings */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
        <CardHeader className="border-b dark:border-slate-700">
          <CardTitle className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <RefreshCw className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <h3 className="font-bold">Sincronizar Rankings</h3>
              <p className="text-sm text-slate-500 font-normal">Recalcula pontos e corridas a partir dos dados reais</p>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <SyncRankingsPanel />
        </CardContent>
      </Card>
    </div>
  );
};

const SyncRankingsPanel = () => {
  const [syncing, setSyncing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSync = async () => {
    setSyncing(true);
    setResult(null);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/admin/recalcular-rankings`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data.resultados);
        toast.success(`Rankings sincronizados! ${data.resultados.usuarios_divergentes} divergências corrigidas.`);
      } else {
        toast.error('Erro ao sincronizar rankings');
      }
    } catch (error) {
      toast.error('Erro de conexão');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
        <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
        <p className="text-sm text-amber-800 dark:text-amber-200">
          Recalcula <strong>pontos</strong> e <strong>total de corridas</strong> de todos os atletas a partir 
          das corridas registradas. Atualiza: usuarios, ranking_anual e ranking da galera.
        </p>
      </div>

      <Button
        onClick={handleSync}
        disabled={syncing}
        className="bg-amber-600 hover:bg-amber-700 text-white"
        data-testid="btn-recalcular-rankings"
      >
        {syncing ? (
          <>
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            Recalculando...
          </>
        ) : (
          <>
            <RefreshCw className="w-4 h-4 mr-2" />
            Recalcular Rankings
          </>
        )}
      </Button>

      {result && (
        <div className="space-y-3 mt-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-slate-50 dark:bg-slate-700 p-3 rounded-lg text-center">
              <p className="text-2xl font-bold text-slate-800 dark:text-white">{result.usuarios_atualizados}</p>
              <p className="text-xs text-slate-500">Atletas verificados</p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-700 p-3 rounded-lg text-center">
              <p className="text-2xl font-bold text-amber-600">{result.usuarios_divergentes}</p>
              <p className="text-xs text-slate-500">Divergências corrigidas</p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-700 p-3 rounded-lg text-center">
              <p className="text-2xl font-bold text-blue-600">{result.ranking_anual_atualizados}</p>
              <p className="text-xs text-slate-500">Ranking anual atualizados</p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-700 p-3 rounded-lg text-center">
              <p className="text-2xl font-bold text-purple-600">{result.ranking_povao_atualizados}</p>
              <p className="text-xs text-slate-500">Ranking galera atualizados</p>
            </div>
          </div>

          {result.detalhes_divergencias?.length > 0 && (
            <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-3">
              <h4 className="font-semibold text-sm mb-2 text-slate-700 dark:text-slate-300">Divergências encontradas:</h4>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {result.detalhes_divergencias.map((d, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs py-1 border-b border-slate-200 dark:border-slate-600 last:border-0">
                    <span className="font-medium text-slate-700 dark:text-slate-300">{d.nome}</span>
                    <span className="text-slate-500">
                      {d.antes.pontos}pts/{d.antes.corridas}corr → {d.depois.pontos}pts/{d.depois.corridas}corr
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.usuarios_divergentes === 0 && (
            <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <p className="text-sm text-green-700 dark:text-green-300">Todos os rankings estão sincronizados!</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DashboardMonitoramento;
