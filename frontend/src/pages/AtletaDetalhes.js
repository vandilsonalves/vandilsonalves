import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, MapPin, Trophy, Medal, Award } from 'lucide-react';
import PendingBadge from '@/components/PendingBadge';
import RaceProgressBar from '@/components/RaceProgressBar';
import ConquistasTable from '@/components/ConquistasTable';
import GraficoEvolucao from '@/components/GraficoEvolucao';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AtletaDetalhes = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [atleta, setAtleta] = useState(null);
  const [corridas, setCorridas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAtleta = async () => {
      try {
        const [atletaRes, corridasRes] = await Promise.all([
          axios.get(`${API}/atletas/${id}`),
          axios.get(`${API}/atletas/${id}/corridas`)
        ]);
        
        setAtleta(atletaRes.data);
        setCorridas(corridasRes.data);
      } catch (error) {
        console.error('Erro ao buscar dados do atleta:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAtleta();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-xl text-slate-600 dark:text-slate-400">Carregando...</div>
      </div>
    );
  }

  if (!atleta) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-xl text-slate-600 dark:text-slate-400">Atleta não encontrado</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Botão Voltar */}
        <Button
          onClick={() => navigate('/')}
          variant="outline"
          className="mb-6"
          data-testid="btn-voltar"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Voltar ao Ranking
        </Button>

        {/* Header do Atleta */}
        <Card className="mb-6 border-slate-200 dark:border-slate-800 shadow-lg">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              {/* Foto com Selo P */}
              <div className="relative">
                <Avatar className="h-32 w-32 ring-4 ring-emerald-500 ring-offset-4 ring-offset-white dark:ring-offset-slate-900">
                  <AvatarImage src={atleta.foto_url} alt={atleta.nome} />
                  <AvatarFallback className="bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300 text-3xl font-bold">
                    {atleta.nome.split(' ').map(n => n[0]).join('').substring(0, 2)}
                  </AvatarFallback>
                </Avatar>
                {atleta.is_pendente && (
                  <div className="absolute -top-2 -right-2">
                    <div className="bg-orange-500 text-white rounded-full w-10 h-10 flex items-center justify-center text-lg font-bold shadow-lg">
                      P
                    </div>
                  </div>
                )}
              </div>

              {/* Informações */}
              <div className="flex-1 text-center md:text-left">
                <h1 className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mb-2">
                  {atleta.nome}
                </h1>
                <div className="flex items-center justify-center md:justify-start gap-2 text-slate-600 dark:text-slate-400 mb-3">
                  <MapPin className="w-4 h-4" />
                  <span>{atleta.cidade}, {atleta.estado}, Brasil</span>
                </div>
                <div className="text-slate-600 dark:text-slate-400 mb-3">
                  <strong>Equipe:</strong> {atleta.equipe}
                </div>
                <div className="text-lg font-semibold text-slate-700 dark:text-slate-300">
                  Pontos de carreira: <span className="text-amber-600 dark:text-amber-400">{atleta.pontos_carreira}</span>
                </div>

                {/* Barra de Progresso */}
                <div className="mt-4">
                  <RaceProgressBar current={atleta.total_corridas} total={12} />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Cards de Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Card Pontos */}
          <Card className="border-slate-200 dark:border-slate-800 shadow-md bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950 dark:to-orange-950">
            <CardContent className="pt-6 text-center">
              <Trophy className="w-12 h-12 mx-auto mb-3 text-amber-600 dark:text-amber-400" />
              <div className="text-4xl font-bold text-amber-600 dark:text-amber-400 mb-1">
                {atleta.pontos_carreira}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400 font-medium">
                Pontos
              </div>
            </CardContent>
          </Card>

          {/* Card Corridas */}
          <Card className="border-slate-200 dark:border-slate-800 shadow-md bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950 dark:to-cyan-950">
            <CardContent className="pt-6 text-center">
              <Medal className="w-12 h-12 mx-auto mb-3 text-blue-600 dark:text-blue-400" />
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                {atleta.total_corridas}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400 font-medium">
                Corridas
              </div>
            </CardContent>
          </Card>

          {/* Card Melhor Colocação */}
          <Card className="border-slate-200 dark:border-slate-800 shadow-md bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950 dark:to-green-950">
            <CardContent className="pt-6 text-center">
              <Award className="w-12 h-12 mx-auto mb-3 text-emerald-600 dark:text-emerald-400" />
              <div className="text-4xl font-bold text-emerald-600 dark:text-emerald-400 mb-1">
                {atleta.melhor_colocacao}º
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400 font-medium">
                Lugar
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Gráfico de Evolução */}
        <GraficoEvolucao atletaId={id} />

        {/* Tabela de Últimas Conquistas */}
        <Card className="border-slate-200 dark:border-slate-800 shadow-lg">
          <CardContent className="pt-6">
            <h2 className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mb-4">
              Últimas Conquistas
            </h2>
            <ConquistasTable corridas={corridas} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AtletaDetalhes;