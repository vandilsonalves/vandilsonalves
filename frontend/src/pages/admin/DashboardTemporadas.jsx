import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import {
  Calendar, Lock, Unlock, Trophy, Users, BarChart3, Loader2, AlertTriangle,
  ChevronDown, ChevronUp, Shield, Star, Award
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function DashboardTemporadas() {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [senhaInput, setSenhaInput] = useState('');
  const [encerando, setEncerando] = useState(false);
  const [expandedSeason, setExpandedSeason] = useState(null);
  const [rankingFinal, setRankingFinal] = useState(null);
  const [loadingRanking, setLoadingRanking] = useState(false);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/temporadas`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setData(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRankingFinal = async (seasonId) => {
    if (expandedSeason === seasonId) {
      setExpandedSeason(null);
      return;
    }
    setExpandedSeason(seasonId);
    setLoadingRanking(true);
    try {
      const res = await fetch(`${API}/temporadas/${seasonId}/ranking-final`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setRankingFinal(await res.json());
      } else {
        setRankingFinal(null);
      }
    } catch {
      setRankingFinal(null);
    } finally {
      setLoadingRanking(false);
    }
  };

  const handleEncerrar = async () => {
    if (!data?.temporada_ativa) return;
    const seasonId = data.temporada_ativa.season_id;
    const esperado = `ENCERRAR ${seasonId}`;

    if (confirmText.trim().toUpperCase() !== esperado) {
      toast.error(`Digite exatamente: ${esperado}`);
      return;
    }
    if (!senhaInput) {
      toast.error('Digite a senha master');
      return;
    }

    setEncerando(true);
    try {
      const res = await fetch(`${API}/admin/temporadas/encerrar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          confirmacao: confirmText,
          senha_master: senhaInput,
        }),
      });
      const result = await res.json();
      if (res.ok) {
        toast.success(result.message);
        setShowModal(false);
        setConfirmText('');
        setSenhaInput('');
        fetchData();
      } else {
        toast.error(result.detail || 'Erro ao encerrar temporada');
      }
    } catch {
      toast.error('Erro de conexao');
    } finally {
      setEncerando(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
        <span className="ml-2 text-gray-400">Carregando temporadas...</span>
      </div>
    );
  }

  if (!data) return null;

  const { temporadas, temporada_ativa, pode_encerrar } = data;
  const seasonId = temporada_ativa?.season_id || new Date().getFullYear();

  return (
    <div className="space-y-6" data-testid="dashboard-temporadas">
      {/* Temporada Ativa */}
      <Card className="bg-gradient-to-r from-emerald-900/40 to-teal-900/30 border-emerald-500/30 p-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-emerald-500/20 rounded-2xl flex items-center justify-center">
              <Trophy className="w-7 h-7 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white" data-testid="temporada-ativa-titulo">
                Temporada {seasonId}
              </h2>
              <p className="text-emerald-300/70 text-sm">
                {temporada_ativa?.data_inicio} a {temporada_ativa?.data_fim}
              </p>
              <Badge className="mt-1 bg-emerald-500/20 text-emerald-300 border-emerald-500/30">
                ATIVA
              </Badge>
            </div>
          </div>

          <div>
            <Button
              onClick={() => setShowModal(true)}
              disabled={!pode_encerrar}
              className={`${pode_encerrar
                ? 'bg-red-600 hover:bg-red-500 text-white'
                : 'bg-gray-700 text-gray-400 cursor-not-allowed'
              }`}
              data-testid="btn-encerrar-temporada"
            >
              {pode_encerrar ? <Unlock className="w-4 h-4 mr-2" /> : <Lock className="w-4 h-4 mr-2" />}
              Encerrar Temporada {seasonId}
            </Button>
            {!pode_encerrar && (
              <p className="text-[11px] text-gray-500 mt-1.5 text-center">
                Disponivel apenas de 01 a 02 de janeiro
              </p>
            )}
          </div>
        </div>
      </Card>

      {/* Historico de Temporadas */}
      <Card className="bg-gray-900 border-gray-800 p-5">
        <div className="flex items-center gap-2 mb-5">
          <Calendar className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-semibold text-white">Historico de Temporadas</h3>
        </div>

        {temporadas.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Nenhuma temporada registrada</p>
        ) : (
          <div className="space-y-3">
            {temporadas.map((t) => (
              <div key={t.season_id} className="border border-gray-800 rounded-lg overflow-hidden" data-testid={`temporada-${t.season_id}`}>
                <div
                  className={`flex items-center justify-between p-4 cursor-pointer transition-colors ${
                    t.status === 'ativa' ? 'bg-emerald-500/5 hover:bg-emerald-500/10' : 'bg-gray-800/30 hover:bg-gray-800/50'
                  }`}
                  onClick={() => t.status === 'finalizada' && fetchRankingFinal(t.season_id)}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      t.status === 'ativa' ? 'bg-emerald-500/20' : 'bg-gray-700'
                    }`}>
                      <span className="text-lg font-bold text-white">{t.season_id}</span>
                    </div>
                    <div>
                      <p className="text-white font-medium">Temporada {t.season_id}</p>
                      <p className="text-xs text-gray-500">
                        {t.data_inicio} a {t.data_fim}
                        {t.encerrado_por && ` | Encerrado por ${t.encerrado_por}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={t.status === 'ativa'
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                      : 'bg-gray-700 text-gray-300 border-gray-600'
                    }>
                      {t.status === 'ativa' ? 'ATIVA' : 'FINALIZADA'}
                    </Badge>
                    {t.status === 'finalizada' && (
                      expandedSeason === t.season_id
                        ? <ChevronUp className="w-4 h-4 text-gray-400" />
                        : <ChevronDown className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                </div>

                {/* Ranking Final Expandido */}
                {expandedSeason === t.season_id && (
                  <div className="p-4 border-t border-gray-800 bg-gray-900/50">
                    {loadingRanking ? (
                      <div className="flex items-center justify-center py-6">
                        <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
                      </div>
                    ) : rankingFinal ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          <StatCard label="Total Atletas" value={rankingFinal.estatisticas?.total_atletas || 0} icon={Users} />
                          <StatCard label="Resultados" value={rankingFinal.estatisticas?.total_resultados || 0} icon={BarChart3} />
                          <StatCard label="Avaliacoes" value={rankingFinal.estatisticas?.total_avaliacoes || 0} icon={Star} />
                          <StatCard label="Assessorias" value={rankingFinal.ranking_assessorias?.length || 0} icon={Shield} />
                        </div>

                        {/* Top 5 Pro */}
                        {rankingFinal.ranking_profissional?.map((cat) => (
                          <MiniRanking
                            key={cat.genero}
                            title={`Top 5 Profissional ${cat.genero === 'M' ? 'Masculino' : 'Feminino'}`}
                            items={cat.atletas?.slice(0, 5) || []}
                            fieldNome="nome"
                            fieldPontos="pontos_total"
                          />
                        ))}

                        {/* Top 5 Assessorias */}
                        <MiniRanking
                          title="Top 5 Assessorias"
                          items={rankingFinal.ranking_assessorias?.slice(0, 5) || []}
                          fieldNome="nome"
                          fieldPontos="pontos"
                        />

                        {/* Top 5 Corridas */}
                        <MiniRanking
                          title="Top 5 Corridas Avaliadas"
                          items={rankingFinal.ranking_corridas?.slice(0, 5) || []}
                          fieldNome="nome_corrida"
                          fieldPontos="media_geral"
                          suffix=""
                        />
                      </div>
                    ) : (
                      <p className="text-gray-500 text-center py-4">Ranking final nao disponivel</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Modal de Encerramento */}
      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="bg-gray-900 border-gray-700 max-w-md">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              Encerrar Temporada {seasonId}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
              <p className="text-sm text-red-300">
                Esta acao ira encerrar a temporada {seasonId}, salvar o ranking final,
                zerar as pontuacoes e criar a temporada {seasonId + 1}.
                Esta acao NAO pode ser desfeita.
              </p>
            </div>

            <div>
              <label className="text-xs text-gray-400 mb-1 block">
                Digite <span className="text-red-400 font-bold">ENCERRAR {seasonId}</span> para confirmar
              </label>
              <input
                type="text"
                value={confirmText}
                onChange={e => setConfirmText(e.target.value)}
                placeholder={`ENCERRAR ${seasonId}`}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:ring-2 focus:ring-red-500 outline-none"
                data-testid="input-confirmacao-encerrar"
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 mb-1 block">Senha Master</label>
              <input
                type="password"
                value={senhaInput}
                onChange={e => setSenhaInput(e.target.value)}
                placeholder="Digite a senha master"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:ring-2 focus:ring-red-500 outline-none"
                data-testid="input-senha-master"
              />
            </div>
          </div>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setShowModal(false)} className="border-gray-700">
              Cancelar
            </Button>
            <Button
              onClick={handleEncerrar}
              disabled={encerando || confirmText.trim().toUpperCase() !== `ENCERRAR ${seasonId}`}
              className="bg-red-600 hover:bg-red-500 text-white"
              data-testid="btn-confirmar-encerrar"
            >
              {encerando ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Encerrar Temporada
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function StatCard({ label, value, icon: Icon }) {
  return (
    <div className="bg-gray-800/50 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-1">
        <Icon className="w-3.5 h-3.5 text-gray-500" />
        <p className="text-[11px] text-gray-500 uppercase tracking-wider">{label}</p>
      </div>
      <p className="text-lg font-bold text-white">{typeof value === 'number' ? value.toLocaleString('pt-BR') : value}</p>
    </div>
  );
}

function MiniRanking({ title, items, fieldNome, fieldPontos, suffix = ' pts' }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <p className="text-xs text-gray-400 font-medium mb-2">{title}</p>
      <div className="space-y-1">
        {items.map((item, i) => (
          <div key={i} className="flex items-center justify-between bg-gray-800/30 rounded px-3 py-1.5">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-bold ${i === 0 ? 'text-amber-400' : i === 1 ? 'text-gray-300' : i === 2 ? 'text-orange-400' : 'text-gray-500'}`}>
                {i + 1}
              </span>
              <span className="text-sm text-gray-200">{item[fieldNome] || 'N/A'}</span>
            </div>
            <span className="text-xs text-emerald-400 font-medium">
              {typeof item[fieldPontos] === 'number' ? item[fieldPontos].toFixed(fieldPontos === 'media_geral' ? 2 : 0) : item[fieldPontos]}{suffix}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
