import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Trophy, Users, Star, Shield, ChevronDown, ChevronUp, Crown, Medal, Award } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

const MEDAL_COLORS = ['text-amber-400', 'text-gray-300', 'text-orange-500', 'text-gray-500', 'text-gray-500'];
const MEDAL_BG = ['bg-amber-400/10', 'bg-gray-300/10', 'bg-orange-500/10', 'bg-gray-500/5', 'bg-gray-500/5'];

function PodiumRow({ item, index, nameField, pointsField, subField, suffix = ' pts' }) {
  const isTop3 = index < 3;
  return (
    <div className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${isTop3 ? 'bg-gray-800/80' : 'bg-gray-800/40'}`}>
      <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${isTop3 ? MEDAL_COLORS[index] : 'text-gray-500'} bg-gray-900`}>
        {index + 1}
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-sm truncate ${isTop3 ? 'text-white font-bold' : 'text-gray-200 font-medium'}`}>
          {item[nameField] || 'N/A'}
        </p>
        {subField && item[subField] && item[subField] !== 'Individual' && (
          <p className="text-[10px] text-gray-400 truncate">{item[subField]}</p>
        )}
      </div>
      <span className={`text-xs font-bold tabular-nums ${isTop3 ? 'text-emerald-300' : 'text-emerald-400/70'}`}>
        {typeof item[pointsField] === 'number'
          ? (pointsField === 'media_geral' ? item[pointsField].toFixed(2) : item[pointsField].toLocaleString('pt-BR'))
          : item[pointsField]}{suffix}
      </span>
    </div>
  );
}

function RankingCard({ icon: Icon, title, items, nameField, pointsField, subField, suffix = ' pts', color = 'emerald' }) {
  if (!items || items.length === 0) return null;

  const colorMap = {
    emerald: { border: 'border-emerald-500/20', iconBg: 'bg-emerald-500/10', iconColor: 'text-emerald-400', titleColor: 'text-emerald-400' },
    amber: { border: 'border-amber-500/20', iconBg: 'bg-amber-500/10', iconColor: 'text-amber-400', titleColor: 'text-amber-400' },
    blue: { border: 'border-blue-500/20', iconBg: 'bg-blue-500/10', iconColor: 'text-blue-400', titleColor: 'text-blue-400' },
    purple: { border: 'border-purple-500/20', iconBg: 'bg-purple-500/10', iconColor: 'text-purple-400', titleColor: 'text-purple-400' },
    rose: { border: 'border-rose-500/20', iconBg: 'bg-rose-500/10', iconColor: 'text-rose-400', titleColor: 'text-rose-400' },
    orange: { border: 'border-orange-500/20', iconBg: 'bg-orange-500/10', iconColor: 'text-orange-400', titleColor: 'text-orange-400' },
  };

  const c = colorMap[color] || colorMap.emerald;

  return (
    <div className={`bg-gray-900 border ${c.border} rounded-xl p-4`}>
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-7 h-7 rounded-lg ${c.iconBg} flex items-center justify-center`}>
          <Icon className={`w-3.5 h-3.5 ${c.iconColor}`} />
        </div>
        <h4 className={`text-xs font-bold uppercase tracking-wider ${c.titleColor}`}>{title}</h4>
      </div>
      <div className="space-y-0.5">
        {items.map((item, i) => (
          <PodiumRow key={i} item={item} index={i} nameField={nameField} pointsField={pointsField} subField={subField} suffix={suffix} />
        ))}
      </div>
    </div>
  );
}

export default function HallDaFama() {
  const navigate = useNavigate();
  const [temporadas, setTemporadas] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [rankingData, setRankingData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTemporadas();
  }, []);

  const fetchTemporadas = async () => {
    try {
      const res = await fetch(`${API}/api/temporadas/historico`);
      if (res.ok) {
        const data = await res.json();
        const finalizadas = (data.temporadas || []).filter(t => t.status === 'finalizada');
        setTemporadas(finalizadas);
        if (finalizadas.length > 0) {
          loadRanking(finalizadas[0].season_id);
          setExpanded(finalizadas[0].season_id);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadRanking = async (seasonId) => {
    if (rankingData[seasonId]) return;
    try {
      const res = await fetch(`${API}/api/temporadas/${seasonId}/ranking-final`);
      if (res.ok) {
        const data = await res.json();
        setRankingData(prev => ({ ...prev, [seasonId]: data }));
      }
    } catch {}
  };

  const toggleSeason = (seasonId) => {
    if (expanded === seasonId) {
      setExpanded(null);
    } else {
      setExpanded(seasonId);
      loadRanking(seasonId);
    }
  };

  if (loading || temporadas.length === 0) return null;

  return (
    <div className="mt-8" data-testid="hall-da-fama">
      {/* Header */}
      <div className="text-center mb-6">
        <div className="inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-full px-4 py-1.5 mb-3">
          <Crown className="w-4 h-4 text-amber-400" />
          <span className="text-sm text-amber-400 font-semibold tracking-wide">HALL DA FAMA</span>
        </div>
        <h2 className="text-xl md:text-2xl font-bold text-white">
          Campeoes das Temporadas
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Os melhores atletas, assessorias e corridas de cada temporada
        </p>
      </div>

      {temporadas.map((temp) => {
        const data = rankingData[temp.season_id];
        const isExpanded = expanded === temp.season_id;

        return (
          <div key={temp.season_id} className="mb-4" data-testid={`hall-season-${temp.season_id}`}>
            {/* Season header */}
            <button
              onClick={() => toggleSeason(temp.season_id)}
              className="w-full flex items-center justify-between bg-gradient-to-r from-amber-600/20 to-orange-600/10 border border-amber-500/20 rounded-xl px-5 py-3.5 hover:from-amber-600/30 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-amber-500/20 rounded-xl flex items-center justify-center">
                  <Trophy className="w-5 h-5 text-amber-400" />
                </div>
                <div className="text-left">
                  <p className="font-bold text-white text-base">Temporada {temp.season_id}</p>
                  <p className="text-xs text-amber-300/60">Ranking Final Oficial</p>
                </div>
              </div>
              {isExpanded ? <ChevronUp className="w-5 h-5 text-amber-400" /> : <ChevronDown className="w-5 h-5 text-amber-400" />}
            </button>

            {/* Expanded ranking */}
            {isExpanded && (
              <div className="mt-3 space-y-6 animate-in fade-in duration-300">
                {!data ? (
                  <div className="text-center py-8 text-gray-500 text-sm">Carregando ranking final...</div>
                ) : (
                  <>
                    {/* PROFISSIONAL/AMADOR */}
                    {data.ranking_profissional && data.ranking_profissional.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <Medal className="w-4 h-4 text-emerald-400" />
                          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Profissional / Amador</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                          {data.ranking_profissional.map((cat) => {
                            const genLabel = cat.genero === 'M' ? 'Masculino' : 'Feminino';
                            const atletas = cat.atletas || [];
                            const normais = atletas.filter(a => !a.categoria || a.categoria.toUpperCase() === 'NORMAL').slice(0, 5);
                            const pcd = atletas.filter(a => a.categoria?.toUpperCase() === 'PCD').slice(0, 5);
                            const cad = atletas.filter(a => a.categoria?.toUpperCase() === 'CADEIRANTE').slice(0, 5);

                            return [
                              normais.length > 0 && (
                                <RankingCard
                                  key={`pro-${cat.genero}`}
                                  icon={Trophy}
                                  title={genLabel}
                                  items={normais}
                                  nameField="nome"
                                  pointsField="pontos_total"
                                  subField="equipe"
                                  color={cat.genero === 'M' ? 'emerald' : 'rose'}
                                />
                              ),
                              pcd.length > 0 && (
                                <RankingCard
                                  key={`pcd-${cat.genero}`}
                                  icon={Award}
                                  title={`PCD ${genLabel}`}
                                  items={pcd}
                                  nameField="nome"
                                  pointsField="pontos_total"
                                  subField="equipe"
                                  color="purple"
                                />
                              ),
                              cad.length > 0 && (
                                <RankingCard
                                  key={`cad-${cat.genero}`}
                                  icon={Award}
                                  title={`Cadeirante ${genLabel}`}
                                  items={cad}
                                  nameField="nome"
                                  pointsField="pontos_total"
                                  subField="equipe"
                                  color="blue"
                                />
                              ),
                            ];
                          })}
                        </div>
                      </div>
                    )}

                    {/* GALERA - PACE LIVRE */}
                    {data.ranking_galera && data.ranking_galera.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <Users className="w-4 h-4 text-amber-400" />
                          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Galera - Pace Livre</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {data.ranking_galera.map((cat) => (
                            <RankingCard
                              key={`galera-${cat.genero}`}
                              icon={Users}
                              title={cat.genero === 'M' ? 'Masculino' : 'Feminino'}
                              items={(cat.atletas || []).slice(0, 5)}
                              nameField="nome"
                              pointsField="pontos_povao"
                              subField="equipe"
                              color={cat.genero === 'M' ? 'amber' : 'orange'}
                            />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* ASSESSORIAS */}
                    {data.ranking_assessorias && data.ranking_assessorias.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <Shield className="w-4 h-4 text-blue-400" />
                          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Assessorias / Equipes</h3>
                        </div>
                        <div className="grid grid-cols-1 gap-3">
                          <RankingCard
                            icon={Shield}
                            title="Top 10 Assessorias"
                            items={(data.ranking_assessorias || []).slice(0, 10)}
                            nameField="nome"
                            pointsField="pontos"
                            subField="estado"
                            color="blue"
                          />
                        </div>
                      </div>
                    )}

                    {/* CORRIDAS AVALIADAS */}
                    {data.ranking_corridas && data.ranking_corridas.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <Star className="w-4 h-4 text-purple-400" />
                          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Corridas Avaliadas</h3>
                        </div>
                        <div className="grid grid-cols-1 gap-3">
                          <RankingCard
                            icon={Star}
                            title="Top 10 Corridas"
                            items={(data.ranking_corridas || []).slice(0, 10)}
                            nameField="nome_corrida"
                            pointsField="media_geral"
                            subField="estado"
                            suffix=""
                            color="purple"
                          />
                        </div>
                      </div>
                    )}

                    {/* Link to full history */}
                    <div className="text-center pt-2">
                      <button
                        onClick={() => navigate('/historico-temporadas')}
                        className="text-xs text-amber-400/70 hover:text-amber-400 transition-colors"
                        data-testid="link-historico-completo"
                      >
                        Ver historico completo de todas as temporadas
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
