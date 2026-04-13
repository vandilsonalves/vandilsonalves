import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { Trophy, Calendar, Users, Star, ChevronDown, ChevronUp, Loader2, ArrowLeft, Shield, BarChart3 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function HistoricoTemporadasPage() {
  const navigate = useNavigate();
  const [temporadas, setTemporadas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);
  const [rankingData, setRankingData] = useState(null);
  const [loadingRanking, setLoadingRanking] = useState(false);

  useEffect(() => {
    fetchTemporadas();
  }, []);

  const fetchTemporadas = async () => {
    try {
      const res = await fetch(`${API}/api/temporadas/historico`);
      if (res.ok) {
        const data = await res.json();
        setTemporadas(data.temporadas || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = async (seasonId) => {
    if (expanded === seasonId) {
      setExpanded(null);
      return;
    }
    setExpanded(seasonId);
    setLoadingRanking(true);
    try {
      const res = await fetch(`${API}/api/temporadas/${seasonId}/ranking-final`);
      if (res.ok) {
        setRankingData(await res.json());
      } else {
        setRankingData(null);
      }
    } catch {
      setRankingData(null);
    } finally {
      setLoadingRanking(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
      </div>
    );
  }

  const finalizadas = temporadas.filter(t => t.status === 'finalizada');
  const ativa = temporadas.find(t => t.status === 'ativa');

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="historico-temporadas-page">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center gap-3 mb-8">
          <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="text-gray-400 hover:text-white">
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Calendar className="w-6 h-6 text-amber-400" />
              Historico de Temporadas
            </h1>
            <p className="text-gray-400 text-sm">Rankings oficiais de cada temporada do Ranking Run Pro</p>
          </div>
        </div>

        {/* Temporada Ativa */}
        {ativa && (
          <Card className="bg-emerald-500/5 border-emerald-500/20 p-5 mb-6" data-testid="temporada-ativa-card">
            <div className="flex items-center gap-3">
              <Trophy className="w-6 h-6 text-emerald-400" />
              <div>
                <p className="font-semibold text-white">Temporada {ativa.season_id}</p>
                <p className="text-xs text-emerald-300/60">Em andamento</p>
              </div>
              <Badge className="ml-auto bg-emerald-500/20 text-emerald-300 border-emerald-500/30">ATIVA</Badge>
            </div>
          </Card>
        )}

        {/* Temporadas Finalizadas */}
        {finalizadas.length === 0 ? (
          <Card className="bg-gray-900 border-gray-800 p-10 text-center">
            <Calendar className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">Nenhuma temporada encerrada ainda.</p>
            <p className="text-gray-500 text-sm mt-1">O historico aparecera aqui apos o encerramento de uma temporada.</p>
          </Card>
        ) : (
          <div className="space-y-4">
            {finalizadas.map((t) => (
              <Card key={t.season_id} className="bg-gray-900 border-gray-800 overflow-hidden" data-testid={`historico-${t.season_id}`}>
                <div
                  className="flex items-center justify-between p-5 cursor-pointer hover:bg-gray-800/50 transition-colors"
                  onClick={() => toggleExpand(t.season_id)}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center">
                      <span className="text-lg font-bold text-amber-400">{t.season_id}</span>
                    </div>
                    <div>
                      <p className="font-semibold text-white">Temporada {t.season_id}</p>
                      <p className="text-xs text-gray-500">
                        Encerrada em {t.data_encerramento ? new Date(t.data_encerramento).toLocaleDateString('pt-BR') : ''}
                        {t.encerrado_por && ` por ${t.encerrado_por}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className="bg-gray-700 text-gray-300">FINALIZADA</Badge>
                    {expanded === t.season_id ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                  </div>
                </div>

                {expanded === t.season_id && (
                  <div className="border-t border-gray-800 p-5">
                    {loadingRanking ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
                      </div>
                    ) : rankingData ? (
                      <div className="space-y-6">
                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-3">
                          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
                            <Users className="w-4 h-4 text-blue-400 mx-auto mb-1" />
                            <p className="text-lg font-bold text-white">{rankingData.estatisticas?.total_atletas || 0}</p>
                            <p className="text-[10px] text-gray-500">Atletas</p>
                          </div>
                          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
                            <BarChart3 className="w-4 h-4 text-emerald-400 mx-auto mb-1" />
                            <p className="text-lg font-bold text-white">{rankingData.estatisticas?.total_resultados || 0}</p>
                            <p className="text-[10px] text-gray-500">Resultados</p>
                          </div>
                          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
                            <Star className="w-4 h-4 text-amber-400 mx-auto mb-1" />
                            <p className="text-lg font-bold text-white">{rankingData.estatisticas?.total_avaliacoes || 0}</p>
                            <p className="text-[10px] text-gray-500">Avaliacoes</p>
                          </div>
                        </div>

                        {/* Podio Profissional */}
                        {rankingData.ranking_profissional?.map((cat) => (
                          <RankingSection
                            key={cat.genero}
                            title={`Profissional ${cat.genero === 'M' ? 'Masculino' : 'Feminino'}`}
                            items={cat.atletas?.slice(0, 10) || []}
                            nameField="nome"
                            pointsField="pontos_total"
                          />
                        ))}

                        {/* Assessorias */}
                        <RankingSection
                          title="Assessorias"
                          items={rankingData.ranking_assessorias?.slice(0, 10) || []}
                          nameField="nome"
                          pointsField="pontos"
                        />

                        {/* Corridas */}
                        <RankingSection
                          title="Corridas Melhor Avaliadas"
                          items={rankingData.ranking_corridas?.slice(0, 10) || []}
                          nameField="nome_corrida"
                          pointsField="media_geral"
                          suffix=""
                        />
                      </div>
                    ) : (
                      <p className="text-gray-500 text-center py-4">Ranking final nao disponivel</p>
                    )}
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function RankingSection({ title, items, nameField, pointsField, suffix = ' pts' }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
        <Trophy className="w-4 h-4 text-amber-400" />
        {title}
      </h4>
      <div className="space-y-1">
        {items.map((item, i) => (
          <div key={i} className="flex items-center justify-between bg-gray-800/40 rounded-lg px-3 py-2">
            <div className="flex items-center gap-3">
              <span className={`w-6 text-center text-sm font-bold ${
                i === 0 ? 'text-amber-400' : i === 1 ? 'text-gray-300' : i === 2 ? 'text-orange-400' : 'text-gray-500'
              }`}>{i + 1}</span>
              <span className="text-sm text-white">{item[nameField] || 'N/A'}</span>
              {item.equipe && item.equipe !== 'Individual' && (
                <span className="text-[10px] text-gray-500">{item.equipe}</span>
              )}
            </div>
            <span className="text-sm text-emerald-400 font-medium">
              {typeof item[pointsField] === 'number'
                ? (pointsField === 'media_geral' ? item[pointsField].toFixed(2) : item[pointsField])
                : item[pointsField]}{suffix}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
