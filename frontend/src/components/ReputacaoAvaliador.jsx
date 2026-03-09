import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Award, Star, Trophy, Loader2, TrendingUp, Calendar, Target } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ReputacaoAvaliador = ({ atletaId, compact = false, showRanking = false }) => {
  const [loading, setLoading] = useState(true);
  const [dados, setDados] = useState(null);
  const [rankingData, setRankingData] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (atletaId) {
      fetchReputacao();
    }
  }, [atletaId]);

  useEffect(() => {
    if (showRanking) {
      fetchRanking();
    }
  }, [showRanking]);

  const fetchReputacao = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/reputacao-avaliador/${atletaId}`);
      setDados(response.data);
    } catch (error) {
      console.error('Erro ao buscar reputação:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRanking = async () => {
    try {
      const response = await axios.get(`${API}/ranking-avaliadores`);
      setRankingData(response.data);
    } catch (error) {
      console.error('Erro ao buscar ranking:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4">
        <Loader2 className="w-5 h-5 animate-spin text-amber-500" />
      </div>
    );
  }

  if (!dados) {
    return null;
  }

  const { nivel_atual, proximo_nivel, total_avaliacoes, progresso, faltam_para_proximo, estatisticas, todos_niveis } = dados;

  // Versão compacta - badge simples
  if (compact) {
    if (total_avaliacoes === 0) {
      return null;
    }

    return (
      <div className="flex items-center gap-2">
        <Badge 
          className="text-white border-0 cursor-pointer hover:opacity-80"
          style={{ backgroundColor: nivel_atual.cor }}
          onClick={() => setShowModal(true)}
        >
          {nivel_atual.icone} {nivel_atual.nome}
        </Badge>
        <span className="text-xs text-slate-400">({total_avaliacoes} avaliações)</span>

        {/* Modal com detalhes */}
        <Dialog open={showModal} onOpenChange={setShowModal}>
          <DialogContent className="max-w-md bg-slate-900 border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white flex items-center gap-2">
                <Award className="w-5 h-5 text-amber-500" />
                Reputação de Avaliador
              </DialogTitle>
            </DialogHeader>
            <ReputacaoCompleta dados={dados} />
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  // Versão completa
  return <ReputacaoCompleta dados={dados} rankingData={rankingData} />;
};

// Componente interno para exibição completa
const ReputacaoCompleta = ({ dados, rankingData }) => {
  const { nivel_atual, proximo_nivel, total_avaliacoes, progresso, faltam_para_proximo, estatisticas, todos_niveis, atleta } = dados;

  return (
    <div className="space-y-6">
      {/* Nível Atual */}
      <div className="text-center p-6 rounded-xl border-2" style={{ borderColor: nivel_atual.cor, backgroundColor: `${nivel_atual.cor}15` }}>
        <span className="text-5xl">{nivel_atual.icone}</span>
        <h3 className="text-xl font-bold mt-2" style={{ color: nivel_atual.cor }}>
          {nivel_atual.nome}
        </h3>
        <p className="text-sm text-slate-400 mt-1">{nivel_atual.descricao}</p>
        <p className="text-2xl font-bold text-white mt-3">
          {total_avaliacoes} <span className="text-sm font-normal text-slate-400">avaliações</span>
        </p>
      </div>

      {/* Progresso para próximo nível */}
      {proximo_nivel && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-400">Próximo: {proximo_nivel.nome}</span>
            <span className="text-sm text-slate-400">{Math.round(progresso)}%</span>
          </div>
          <Progress value={progresso} className="h-3" />
          <p className="text-xs text-center text-slate-500">
            Faltam <span className="text-amber-500 font-bold">{faltam_para_proximo}</span> avaliações para {proximo_nivel.icone} {proximo_nivel.nome}
          </p>
        </div>
      )}

      {/* Estatísticas */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 bg-slate-800/50 rounded-lg text-center">
          <Star className="w-5 h-5 mx-auto text-amber-400 mb-1" />
          <p className="text-lg font-bold text-white">{estatisticas.media_notas_dadas}</p>
          <p className="text-xs text-slate-400">Média das notas</p>
        </div>
        <div className="p-3 bg-slate-800/50 rounded-lg text-center">
          <Calendar className="w-5 h-5 mx-auto text-emerald-400 mb-1" />
          <p className="text-lg font-bold text-white">{estatisticas.meses_ativos}</p>
          <p className="text-xs text-slate-400">Meses ativos</p>
        </div>
      </div>

      {/* Todos os níveis */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <Target className="w-4 h-4 text-amber-400" />
          Níveis de Reputação
        </h4>
        <div className="space-y-2">
          {todos_niveis?.map((nivel) => (
            <div 
              key={nivel.codigo}
              className={`flex items-center justify-between p-3 rounded-lg border ${
                nivel.conquistado 
                  ? 'border-emerald-500/50 bg-emerald-500/10'
                  : 'border-slate-700 bg-slate-800/30'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{nivel.icone}</span>
                <div>
                  <p className={`font-medium ${nivel.conquistado ? 'text-white' : 'text-slate-400'}`}>
                    {nivel.nome}
                  </p>
                  <p className="text-xs text-slate-500">{nivel.min_avaliacoes}+ avaliações</p>
                </div>
              </div>
              {nivel.conquistado ? (
                <Badge className="bg-emerald-500 text-white">✓</Badge>
              ) : (
                <span className="text-xs text-slate-500">
                  {nivel.atual}/{nivel.min_avaliacoes}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Ranking (se disponível) */}
      {rankingData && (
        <div className="space-y-3 pt-4 border-t border-slate-700">
          <h4 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <Trophy className="w-4 h-4 text-amber-400" />
            Top Avaliadores
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {rankingData.ranking?.slice(0, 5).map((av) => (
              <div 
                key={av.atleta_id}
                className={`flex items-center justify-between p-2 rounded-lg ${
                  av.posicao <= 3 ? 'bg-amber-500/10 border border-amber-500/30' : 'bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    av.posicao === 1 ? 'bg-yellow-500 text-white' :
                    av.posicao === 2 ? 'bg-slate-400 text-white' :
                    av.posicao === 3 ? 'bg-amber-700 text-white' :
                    'bg-slate-700 text-slate-300'
                  }`}>
                    {av.posicao}
                  </span>
                  <span className="text-sm text-white">{av.nome}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs" style={{ color: av.nivel.cor }}>{av.nivel.icone}</span>
                  <span className="text-xs text-slate-400">{av.total_avaliacoes}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Componente para exibir o ranking completo
export const RankingAvaliadores = () => {
  const [loading, setLoading] = useState(true);
  const [dados, setDados] = useState(null);

  useEffect(() => {
    fetchRanking();
  }, []);

  const fetchRanking = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/ranking-avaliadores`);
      setDados(response.data);
    } catch (error) {
      console.error('Erro ao buscar ranking:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
      </div>
    );
  }

  if (!dados) {
    return <p className="text-slate-400 text-center">Nenhum dado disponível</p>;
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Trophy className="w-5 h-5 text-amber-500" />
          Ranking de Avaliadores
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Legenda de níveis */}
        <div className="flex flex-wrap gap-2 mb-4">
          {dados.niveis_disponiveis?.map((nivel) => (
            <Badge 
              key={nivel.codigo}
              variant="outline"
              className="border-slate-600"
              style={{ color: nivel.cor }}
            >
              {nivel.icone} {nivel.nome} ({nivel.min_avaliacoes}+)
            </Badge>
          ))}
        </div>

        {/* Tabela de ranking */}
        <div className="space-y-2">
          {dados.ranking?.map((av) => (
            <div 
              key={av.atleta_id}
              className={`flex items-center justify-between p-3 rounded-lg ${
                av.posicao === 1 ? 'bg-gradient-to-r from-yellow-500/20 to-transparent border border-yellow-500/30' :
                av.posicao === 2 ? 'bg-gradient-to-r from-slate-400/20 to-transparent border border-slate-400/30' :
                av.posicao === 3 ? 'bg-gradient-to-r from-amber-700/20 to-transparent border border-amber-700/30' :
                'bg-slate-900/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                  av.posicao === 1 ? 'bg-yellow-500 text-white' :
                  av.posicao === 2 ? 'bg-slate-400 text-white' :
                  av.posicao === 3 ? 'bg-amber-700 text-white' :
                  'bg-slate-700 text-slate-300'
                }`}>
                  {av.posicao}º
                </span>
                <div>
                  <p className="text-white font-medium">{av.nome}</p>
                  <p className="text-xs text-slate-400">
                    Média: {av.media_notas} ⭐
                  </p>
                </div>
              </div>
              <div className="text-right flex items-center gap-3">
                <Badge 
                  className="text-white border-0"
                  style={{ backgroundColor: av.nivel.cor }}
                >
                  {av.nivel.icone} {av.nivel.nome}
                </Badge>
                <div>
                  <p className="text-amber-500 font-bold">{av.total_avaliacoes}</p>
                  <p className="text-xs text-slate-500">avaliações</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default ReputacaoAvaliador;
