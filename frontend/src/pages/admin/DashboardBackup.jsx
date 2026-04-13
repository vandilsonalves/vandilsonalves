import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  HardDrive, Download, Trash2, RefreshCw, Loader2,
  Shield, Clock, Database, FolderArchive, Calendar, AlertCircle, CheckCircle2, Upload, AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { downloadFile } from '@/utils/downloadHelper';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DashboardBackup = () => {
  const { token } = useAuth();
  const [backups, setBackups] = useState([]);
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [criandoBackup, setCriandoBackup] = useState(false);
  const [excluindoId, setExcluindoId] = useState(null);
  const [restaurando, setRestaurando] = useState(false);
  const [arquivoRestore, setArquivoRestore] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [histRes, infoRes] = await Promise.allSettled([
        axios.get(`${API}/admin/backup/historico`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/admin/backup/info`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      if (histRes.status === 'fulfilled') setBackups(histRes.value.data);
      if (infoRes.status === 'fulfilled') setInfo(infoRes.value.data);
    } catch (err) {
      console.error('Erro ao carregar backups:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCriarBackup = async () => {
    setCriandoBackup(true);
    try {
      const res = await axios.post(`${API}/admin/backup/criar`, {}, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 300000
      });
      toast.success('Backup criado com sucesso!', {
        description: `${res.data.backup.total_collections} collections, ${res.data.backup.total_documentos} documentos (${res.data.backup.tamanho_mb} MB)`
      });
      fetchData();
    } catch (error) {
      toast.error('Erro ao criar backup', {
        description: error.response?.data?.detail || 'Tente novamente'
      });
    } finally {
      setCriandoBackup(false);
    }
  };

  const handleDownload = (backupId) => {
    downloadFile(`/api/admin/backup/download/${backupId}`);
    toast.success('Download do backup iniciado!');
  };

  const handleExcluir = async (backupId) => {
    if (!window.confirm('Tem certeza que deseja excluir este backup?')) return;
    setExcluindoId(backupId);
    try {
      await axios.delete(`${API}/admin/backup/${backupId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Backup excluído');
      fetchData();
    } catch (error) {
      toast.error('Erro ao excluir backup');
    } finally {
      setExcluindoId(null);
    }
  };

  const handleRestaurar = async () => {
    if (!arquivoRestore) return;
    if (!window.confirm('ATENCAO: Isso ira SUBSTITUIR todos os dados atuais pelos dados do backup. Deseja continuar?')) return;
    setRestaurando(true);
    try {
      const formData = new FormData();
      formData.append('arquivo', arquivoRestore);
      const res = await axios.post(`${API}/admin/backup/restaurar-upload`, formData, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' },
        timeout: 600000,
      });
      toast.success(res.data.mensagem || 'Backup restaurado com sucesso!');
      setArquivoRestore(null);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao restaurar backup');
    } finally {
      setRestaurando(false);
    }
  };

  const formatarData = (iso) => {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="dashboard-backup">
      {/* Header com info geral */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-5 border-0">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-xs font-medium">Total de Backups</p>
              <p className="text-3xl font-bold mt-1">{info?.total_backups || 0}</p>
            </div>
            <FolderArchive className="w-10 h-10 text-blue-300/50" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-600 to-emerald-700 text-white p-5 border-0">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-emerald-200 text-xs font-medium">Collections</p>
              <p className="text-3xl font-bold mt-1">{info?.total_collections || 0}</p>
            </div>
            <Database className="w-10 h-10 text-emerald-300/50" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-600 to-purple-700 text-white p-5 border-0">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-200 text-xs font-medium">Documentos</p>
              <p className="text-3xl font-bold mt-1">{(info?.total_documentos || 0).toLocaleString()}</p>
            </div>
            <HardDrive className="w-10 h-10 text-purple-300/50" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-amber-600 to-amber-700 text-white p-5 border-0">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-amber-200 text-xs font-medium">Uploads</p>
              <p className="text-3xl font-bold mt-1">{info?.tamanho_uploads_mb || 0} MB</p>
            </div>
            <FolderArchive className="w-10 h-10 text-amber-300/50" />
          </div>
        </Card>
      </div>

      {/* Ações */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 p-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
              <Shield className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800 dark:text-white">Sistema de Backup</h3>
              <p className="text-sm text-slate-500">
                Backup completo: MongoDB + Arquivos de Upload
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <Calendar className="w-3.5 h-3.5" />
                <span>Automático: quartas, 02:30h</span>
              </div>
              {info?.ultimo_backup && (
                <p className="text-xs text-slate-400 mt-0.5">
                  Último: {formatarData(info.ultimo_backup.data_criacao)}
                </p>
              )}
            </div>

            <Button
              onClick={handleCriarBackup}
              disabled={criandoBackup}
              className="bg-blue-600 hover:bg-blue-700 text-white"
              data-testid="btn-criar-backup"
            >
              {criandoBackup ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Criando Backup...</>
              ) : (
                <><HardDrive className="w-4 h-4 mr-2" />Fazer Backup</>
              )}
            </Button>

            <Button
              onClick={fetchData}
              variant="outline"
              size="icon"
              data-testid="btn-atualizar-backups"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>

      {/* Restaurar Backup */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
            <Upload className="w-5 h-5 text-amber-500" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-800 dark:text-white">Restaurar Backup</h3>
            <p className="text-xs text-slate-500">Envie o arquivo .zip do ultimo backup para restaurar o sistema</p>
          </div>
        </div>

        <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-3 mb-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-amber-300">
              Esta operacao ira <strong>substituir</strong> todos os dados atuais pelos dados do backup enviado. Certifique-se de que o arquivo foi gerado pelo sistema de backup da plataforma.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <input
            type="file"
            id="restore-file"
            accept=".zip"
            className="hidden"
            onChange={(e) => setArquivoRestore(e.target.files?.[0] || null)}
            data-testid="restore-file-input"
          />
          <Button
            variant="outline"
            onClick={() => document.getElementById('restore-file').click()}
            className="border-amber-500/50 text-amber-400 hover:bg-amber-500/10"
            disabled={restaurando}
            data-testid="btn-selecionar-backup"
          >
            <FolderArchive className="w-4 h-4 mr-2" />
            {arquivoRestore ? arquivoRestore.name : 'Selecionar arquivo .zip'}
          </Button>

          {arquivoRestore && (
            <>
              <span className="text-xs text-slate-400">
                {(arquivoRestore.size / 1024 / 1024).toFixed(1)} MB
              </span>
              <Button
                onClick={handleRestaurar}
                disabled={restaurando}
                className="bg-amber-600 hover:bg-amber-500 text-white"
                data-testid="btn-restaurar-backup"
              >
                {restaurando ? (
                  <><Loader2 className="w-4 h-4 animate-spin mr-2" />Restaurando...</>
                ) : (
                  <><Upload className="w-4 h-4 mr-2" />Restaurar Sistema</>
                )}
              </Button>
            </>
          )}
        </div>
      </Card>

      {/* Histórico de Backups */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0 overflow-hidden">
        <div className="p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 className="font-semibold text-slate-800 dark:text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-slate-500" />
            Histórico de Backups
          </h3>
        </div>

        {backups.length === 0 ? (
          <div className="p-12 text-center">
            <FolderArchive className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 font-medium">Nenhum backup realizado ainda</p>
            <p className="text-sm text-slate-400 mt-1">Clique em "Fazer Backup" para criar o primeiro</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {backups.map((backup) => (
              <div key={backup.id} className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors" data-testid={`backup-item-${backup.id}`}>
                <div className="flex items-center justify-between flex-wrap gap-3">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      backup.tipo === 'automatico' 
                        ? 'bg-purple-100 dark:bg-purple-900/30' 
                        : 'bg-blue-100 dark:bg-blue-900/30'
                    }`}>
                      {backup.tipo === 'automatico' 
                        ? <Calendar className="w-5 h-5 text-purple-600" />
                        : <HardDrive className="w-5 h-5 text-blue-600" />
                      }
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-medium text-sm text-slate-800 dark:text-white truncate">
                          {backup.nome_arquivo}
                        </p>
                        <Badge className={`text-[10px] ${
                          backup.tipo === 'automatico'
                            ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
                            : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                        }`}>
                          {backup.tipo === 'automatico' ? 'Automático' : 'Manual'}
                        </Badge>
                        {backup.status === 'concluido' && (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                        )}
                      </div>
                      <div className="flex items-center gap-3 mt-0.5 text-xs text-slate-500">
                        <span>{formatarData(backup.data_criacao)}</span>
                        <span>{backup.tamanho_mb} MB</span>
                        <span>{backup.total_collections} collections</span>
                        <span>{(backup.total_documentos || 0).toLocaleString()} docs</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {backup.arquivo_disponivel ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownload(backup.id)}
                        className="text-blue-600 hover:text-blue-700 border-blue-200 hover:border-blue-300"
                        data-testid={`btn-download-${backup.id}`}
                      >
                        <Download className="w-4 h-4 mr-1.5" />
                        Baixar
                      </Button>
                    ) : (
                      <Badge variant="outline" className="text-xs text-slate-400 border-slate-300">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        Indisponível
                      </Badge>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleExcluir(backup.id)}
                      disabled={excluindoId === backup.id}
                      className="text-red-500 hover:text-red-600 hover:bg-red-50"
                      data-testid={`btn-excluir-${backup.id}`}
                    >
                      {excluindoId === backup.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Nota informativa */}
      <Card className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-700 p-4">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-amber-800 dark:text-amber-200">
            <p className="font-semibold mb-1">Informações sobre o Backup</p>
            <ul className="list-disc list-inside space-y-0.5 text-xs text-amber-700 dark:text-amber-300">
              <li>O backup inclui todas as collections do banco de dados e todos os arquivos de upload</li>
              <li>O backup automático é executado toda <strong>quarta-feira às 02:30h</strong></li>
              <li>Os arquivos de backup são armazenados fora do banco de dados para não sobrecarregar o sistema</li>
              <li>Para restaurar, descompacte o .zip e importe os JSONs no MongoDB</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Seção Strava - Limpeza de Tokens */}
      <StravaCleanup token={token} />
    </div>
  );
};

// ==================== Componente de Limpeza Strava ====================
const StravaCleanup = ({ token }) => {
  const [limpando, setLimpando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [confirmar, setConfirmar] = useState(false);

  const handleLimparStrava = async () => {
    if (!confirmar) {
      setConfirmar(true);
      return;
    }
    setLimpando(true);
    setConfirmar(false);
    try {
      const res = await axios.delete(`${API}/strava/admin/limpar-todos`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResultado(res.data);
      toast.success(`${res.data.usuarios_desconectados} conexões Strava removidas!`);
    } catch (err) {
      toast.error('Erro ao limpar tokens Strava');
      console.error(err);
    } finally {
      setLimpando(false);
    }
  };

  return (
    <Card className="bg-orange-50 dark:bg-orange-900/20 border-orange-300 dark:border-orange-700 p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex gap-3">
          <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center flex-shrink-0">
            <RefreshCw className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <h3 className="font-semibold text-orange-800 dark:text-orange-200">Limpar Conexões Strava</h3>
            <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              Remove TODOS os tokens de acesso ao Strava de todos os atletas.
              Use quando atingir o limite de 100 usuários conectados.
            </p>
            {resultado && (
              <div className="mt-2 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span className="text-xs text-green-700 font-medium">
                  {resultado.usuarios_desconectados} usuários desconectados ({resultado.documentos_atualizados} registros atualizados)
                </span>
              </div>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <Button
            onClick={handleLimparStrava}
            disabled={limpando}
            variant={confirmar ? "destructive" : "outline"}
            size="sm"
            className={confirmar ? '' : 'border-orange-400 text-orange-700 hover:bg-orange-100'}
            data-testid="btn-limpar-strava"
          >
            {limpando ? (
              <><Loader2 className="w-4 h-4 mr-1 animate-spin" /> Limpando...</>
            ) : confirmar ? (
              'Confirmar Limpeza'
            ) : (
              'Limpar Tokens'
            )}
          </Button>
          {confirmar && (
            <button
              onClick={() => setConfirmar(false)}
              className="text-xs text-slate-500 hover:text-slate-700"
            >
              Cancelar
            </button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default DashboardBackup;
