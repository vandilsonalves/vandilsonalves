import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Trophy, Star, Flame, Medal, Calendar, TrendingUp, Award, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RankingDestaques = ({ categoria = 'masculino' }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('semanal');
  const [rankingSemanal, setRankingSemanal] = useState(null);
  const [rankingMensal, setRankingMensal] = useState(null);
  const [destaqueMes, setDestaqueMes] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mapeia a tab de categoria para os params do backend
  const getBackendParams = (cat) => {
    const map = {
      'masculino':     { genero: 'M', categoria: 'normal' },
      'feminino':      { genero: 'F', categoria: 'normal' },
      'pcd-m':         { genero: 'M', categoria: 'pcd' },
      'pcd-f':         { genero: 'F', categoria: 'pcd' },
      'cadeirante-m':  { genero: 'M', categoria: 'cadeirante' },
      'cadeirante-f':  { genero: 'F', categoria: 'cadeirante' },
    };
    return map[cat] || { genero: 'M', categoria: 'normal' };
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const { genero, categoria: cat } = getBackendParams(categoria);
        const params = `genero=${genero}&categoria=${cat}`;
        const [semanalRes, mensalRes, destaqueRes] = await Promise.all([
          axios.get(`${API}/ranking/semanal?${params}`),
          axios.get(`${API}/ranking/mensal?${params}`),
          axios.get(`${API}/ranking/destaque-mes?${params}`)
        ]);
        
        setRankingSemanal(semanalRes.data);
        setRankingMensal(mensalRes.data);
        setDestaqueMes(destaqueRes.data);
      } catch (error) {
        console.error('Erro ao buscar destaques:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [categoria]);

  const getMedalColor = (posicao) => {
    switch (posicao) {
      case 1: return 'text-yellow-500';
      case 2: return 'text-slate-400';
      case 3: return 'text-amber-600';
      default: return 'text-slate-600';
    }
  };

  const getMedalBg = (posicao) => {
    switch (posicao) {
      case 1: return 'bg-gradient-to-r from-yellow-100 to-yellow-50 border-yellow-300';
      case 2: return 'bg-gradient-to-r from-slate-100 to-slate-50 border-slate-300';
      case 3: return 'bg-gradient-to-r from-amber-100 to-amber-50 border-amber-300';
      default: return 'bg-white border-slate-200';
    }
  };

  const renderAtletaCard = (atleta, index, tipo = 'semanal') => {
    const pontos = tipo === 'semanal' ? atleta.pontos_semana : atleta.pontos_mes;
    const corridas = tipo === 'semanal' ? atleta.corridas_semana : atleta.corridas_mes;
    
    return (
      <div
        key={atleta.atleta_id}
        className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all hover:scale-[1.02] hover:shadow-lg ${getMedalBg(atleta.posicao)}`}
        onClick={() => navigate(`/atleta/${atleta.atleta_id}`)}
        data-testid={`destaque-${tipo}-${index}`}
      >
        {/* Posição */}
        <div className={`flex items-center justify-center w-10 h-10 rounded-full ${atleta.posicao <= 3 ? 'bg-white shadow-md' : ''}`}>
          {atleta.posicao <= 3 ? (
            <Medal className={`w-6 h-6 ${getMedalColor(atleta.posicao)}`} />
          ) : (
            <span className="text-lg font-bold text-slate-600">{atleta.posicao}</span>
          )}
        </div>
        
        {/* Avatar */}
        <Avatar className="h-12 w-12 border-2 border-white shadow">
          <AvatarImage src={atleta.foto_url?.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
          <AvatarFallback className="bg-emerald-600 text-white font-bold">
            {atleta.nome?.charAt(0)}
          </AvatarFallback>
        </Avatar>
        
        {/* Info */}
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-slate-800 truncate">{atleta.nome}</h4>
          <p className="text-sm text-slate-500 truncate">{atleta.equipe}</p>
        </div>
        
        {/* Pontos */}
        <div className="text-right">
          <div className="flex items-center gap-1 justify-end">
            <Star className="w-4 h-4 text-emerald-500" />
            <span className="text-xl font-bold text-emerald-600">{pontos}</span>
          </div>
          <p className="text-xs text-slate-500">{corridas} corrida(s)</p>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <Card className="border-slate-200 dark:border-slate-800 shadow-lg">
        <CardContent className="py-12 text-center text-slate-500">
          Carregando destaques...
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Destaque do Mês */}
      {destaqueMes && (
        <Card className="border-0 shadow-xl bg-gradient-to-br from-emerald-500 to-emerald-700 text-white overflow-hidden" data-testid="destaque-mes-card">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-xl">
              <Award className="w-6 h-6 text-yellow-300" />
              Destaque de {destaqueMes.mes} {destaqueMes.ano} - {categoria.replace('-', ' / ').toUpperCase()}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-white/10 rounded-xl">
              <div className="text-center">
                <div className="text-3xl font-bold">{destaqueMes.total_corridas_mes}</div>
                <div className="text-sm opacity-80">Corridas no mês</div>
              </div>
              <div className="text-center border-l border-white/20">
                <div className="text-3xl font-bold">{Object.values(destaqueMes.destaques_categoria).flat().length}</div>
                <div className="text-sm opacity-80">Atletas no pódio</div>
              </div>
            </div>
            
            {/* Mais Ativo e Mais Pontos */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {destaqueMes.mais_ativo_mes && (
                <div 
                  className="flex items-center gap-3 p-4 bg-white/10 rounded-xl cursor-pointer hover:bg-white/20 transition-colors"
                  onClick={() => navigate(`/atleta/${destaqueMes.mais_ativo_mes.atleta_id}`)}
                >
                  <div className="p-2 bg-orange-400 rounded-full">
                    <Flame className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs opacity-80">Mais Ativo</p>
                    <p className="font-semibold">{destaqueMes.mais_ativo_mes.nome}</p>
                    <p className="text-sm opacity-80">{destaqueMes.mais_ativo_mes.total_corridas} corridas</p>
                  </div>
                  <Avatar className="h-10 w-10 border-2 border-white/50">
                    <AvatarImage src={destaqueMes.mais_ativo_mes.foto_url?.startsWith('http') ? destaqueMes.mais_ativo_mes.foto_url : `${BACKEND_URL}${destaqueMes.mais_ativo_mes.foto_url}`} />
                    <AvatarFallback className="bg-orange-500 text-white">{destaqueMes.mais_ativo_mes.nome?.charAt(0)}</AvatarFallback>
                  </Avatar>
                </div>
              )}
              
              {destaqueMes.mais_pontos_mes && (
                <div 
                  className="flex items-center gap-3 p-4 bg-white/10 rounded-xl cursor-pointer hover:bg-white/20 transition-colors"
                  onClick={() => navigate(`/atleta/${destaqueMes.mais_pontos_mes.atleta_id}`)}
                >
                  <div className="p-2 bg-yellow-400 rounded-full">
                    <Trophy className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs opacity-80">Mais Pontos</p>
                    <p className="font-semibold">{destaqueMes.mais_pontos_mes.nome}</p>
                    <p className="text-sm opacity-80">{destaqueMes.mais_pontos_mes.total_pontos} pontos</p>
                  </div>
                  <Avatar className="h-10 w-10 border-2 border-white/50">
                    <AvatarImage src={destaqueMes.mais_pontos_mes.foto_url?.startsWith('http') ? destaqueMes.mais_pontos_mes.foto_url : `${BACKEND_URL}${destaqueMes.mais_pontos_mes.foto_url}`} />
                    <AvatarFallback className="bg-yellow-500 text-white">{destaqueMes.mais_pontos_mes.nome?.charAt(0)}</AvatarFallback>
                  </Avatar>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Rankings Semanal e Mensal */}
      <Card className="border-slate-200 dark:border-slate-800 shadow-lg" data-testid="ranking-periodo-card">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-500" />
            Rankings por Periodo - {categoria.replace('-', ' / ').toUpperCase()}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-4">
              <TabsTrigger value="semanal" className="flex items-center gap-2" data-testid="tab-semanal">
                <Calendar className="w-4 h-4" />
                Semanal
              </TabsTrigger>
              <TabsTrigger value="mensal" className="flex items-center gap-2" data-testid="tab-mensal">
                <Calendar className="w-4 h-4" />
                Mensal
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="semanal" className="space-y-3">
              {rankingSemanal && (
                <>
                  <p className="text-sm text-slate-500 mb-4">
                    Período: {rankingSemanal.periodo}
                  </p>
                  {rankingSemanal.ranking.length > 0 ? (
                    rankingSemanal.ranking.map((atleta, index) => renderAtletaCard(atleta, index, 'semanal'))
                  ) : (
                    <div className="text-center py-8 text-slate-500">
                      <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Nenhuma corrida registrada esta semana</p>
                    </div>
                  )}
                </>
              )}
            </TabsContent>
            
            <TabsContent value="mensal" className="space-y-3">
              {rankingMensal && (
                <>
                  <p className="text-sm text-slate-500 mb-4">
                    {rankingMensal.mes} de {rankingMensal.ano}
                  </p>
                  {rankingMensal.ranking.length > 0 ? (
                    rankingMensal.ranking.map((atleta, index) => renderAtletaCard(atleta, index, 'mensal'))
                  ) : (
                    <div className="text-center py-8 text-slate-500">
                      <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Nenhuma corrida registrada este mês</p>
                    </div>
                  )}
                </>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default RankingDestaques;
