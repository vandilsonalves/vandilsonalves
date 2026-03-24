import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Trophy, Users, Target, Clock, Medal, Star, 
  ArrowLeft, CheckCircle, Info, Award, Flame
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RegrasPage = () => {
  const [regras, setRegras] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('profissional');

  useEffect(() => {
    const fetchRegras = async () => {
      try {
        const response = await axios.get(`${API}/configuracoes/regras`);
        setRegras(response.data);
      } catch (error) {
        console.error('Erro ao carregar regras:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchRegras();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-8 px-4" data-testid="regras-page">
      <div className="container mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-8">
          <Link to="/">
            <Button variant="outline" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar ao Ranking
            </Button>
          </Link>
          
          <div className="text-center">
            <h1 className="text-4xl font-bold text-slate-800 mb-2">
              Regras do Sistema
            </h1>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Entenda como funciona a pontuação em cada modalidade do Ranking Run
            </p>
          </div>
        </div>

        {/* Tabs de Modalidades */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="profissional" className="flex items-center gap-2" data-testid="tab-profissional">
              <Trophy className="w-4 h-4" />
              <span className="hidden sm:inline">Profissional/Amador</span>
              <span className="sm:hidden">Pro/Amador</span>
            </TabsTrigger>
            <TabsTrigger value="povao" className="flex items-center gap-2" data-testid="tab-povao">
              <Users className="w-4 h-4" />
              <span className="hidden sm:inline">Ranking da Galera</span>
              <span className="sm:hidden">Galera</span>
            </TabsTrigger>
            <TabsTrigger value="equipes" className="flex items-center gap-2" data-testid="tab-equipes">
              <Target className="w-4 h-4" />
              <span className="hidden sm:inline">Ranking das Equipes</span>
              <span className="sm:hidden">Equipes</span>
            </TabsTrigger>
          </TabsList>

          {/* Tab Profissional/Amador */}
          <TabsContent value="profissional">
            <div className="space-y-6">
              <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3 text-emerald-700">
                    <Trophy className="w-6 h-6" />
                    {regras?.ranking_profissional?.titulo || 'RANKING PROFISSIONAL/AMADOR'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-600 mb-6">
                    {regras?.ranking_profissional?.descricao}
                  </p>

                  {/* Tabela de Pontuação Normal */}
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                        <Medal className="w-5 h-5 text-amber-500" />
                        Categoria Normal
                      </h3>
                      <div className="bg-white rounded-lg border overflow-hidden">
                        <table className="w-full">
                          <thead className="bg-emerald-600 text-white">
                            <tr>
                              <th className="py-2 px-4 text-left">Colocação</th>
                              <th className="py-2 px-4 text-center">Pontos</th>
                            </tr>
                          </thead>
                          <tbody>
                            {regras?.ranking_profissional?.pontuacao_normal?.map((item, idx) => (
                              <tr key={idx} className={idx % 2 === 0 ? 'bg-slate-50' : 'bg-white'}>
                                <td className="py-2 px-4">{item.posicao}</td>
                                <td className="py-2 px-4 text-center font-bold text-emerald-600">
                                  {item.pontos} pts
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                        <Award className="w-5 h-5 text-purple-500" />
                        PCD / Cadeirante
                      </h3>
                      <div className="bg-white rounded-lg border overflow-hidden">
                        <table className="w-full">
                          <thead className="bg-purple-600 text-white">
                            <tr>
                              <th className="py-2 px-4 text-left">Colocação</th>
                              <th className="py-2 px-4 text-center">Pontos</th>
                            </tr>
                          </thead>
                          <tbody>
                            {regras?.ranking_profissional?.pontuacao_pcd?.map((item, idx) => (
                              <tr key={idx} className={idx % 2 === 0 ? 'bg-slate-50' : 'bg-white'}>
                                <td className="py-2 px-4">{item.posicao}</td>
                                <td className="py-2 px-4 text-center font-bold text-purple-600">
                                  {item.pontos} pts
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  {/* Informações Adicionais */}
                  <div className="mt-6 grid md:grid-cols-3 gap-4">
                    <Card className="bg-amber-50 border-amber-200">
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Info className="w-5 h-5 text-amber-600" />
                          <span className="font-semibold text-amber-700">Selo "P" (Pendente)</span>
                        </div>
                        <p className="text-sm text-amber-700">
                          Mínimo de <strong>{regras?.ranking_profissional?.minimo_provas_normal || 12}</strong> provas (Normal) ou{' '}
                          <strong>{regras?.ranking_profissional?.minimo_provas_pcd || 8}</strong> provas (PCD/Cadeirante)
                        </p>
                      </CardContent>
                    </Card>

                    <Card className="bg-emerald-50 border-emerald-200">
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Star className="w-5 h-5 text-emerald-600" />
                          <span className="font-semibold text-emerald-700">Status Elite</span>
                        </div>
                        <p className="text-sm text-emerald-700">
                          Atletas com <strong>{regras?.ranking_profissional?.pontos_elite || 100}</strong> pontos ou mais
                          recebem o status Elite
                        </p>
                      </CardContent>
                    </Card>

                    <Card className="bg-blue-50 border-blue-200">
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Clock className="w-5 h-5 text-blue-600" />
                          <span className="font-semibold text-blue-700">Prazo de Envio</span>
                        </div>
                        <p className="text-sm text-blue-700">
                          Você tem até <strong>{regras?.configuracoes_gerais?.prazo_submissao_dias || 30}</strong> dias após 
                          a corrida para submeter o resultado
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Tab Galera */}
          <TabsContent value="povao">
            <div className="space-y-6">
              <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3 text-purple-700">
                    <Users className="w-6 h-6" />
                    {regras?.ranking_povao?.titulo || 'RANKING DA GALERA'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-600 mb-6">
                    {regras?.ranking_povao?.descricao}
                  </p>

                  {/* Tabela de Pontuação por Distância */}
                  <div className="max-w-md mx-auto">
                    <h3 className="font-semibold text-slate-700 mb-3 text-center flex items-center justify-center gap-2">
                      <Flame className="w-5 h-5 text-orange-500" />
                      Pontuação por Distância
                    </h3>
                    <div className="bg-white rounded-lg border overflow-hidden">
                      <table className="w-full">
                        <thead className="bg-purple-600 text-white">
                          <tr>
                            <th className="py-3 px-4 text-left">Distância</th>
                            <th className="py-3 px-4 text-center">Pontos</th>
                          </tr>
                        </thead>
                        <tbody>
                          {regras?.ranking_povao?.faixas?.map((item, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-slate-50' : 'bg-white'}>
                              <td className="py-3 px-4 font-medium">{item.distancia}</td>
                              <td className="py-3 px-4 text-center">
                                <Badge className="bg-purple-100 text-purple-700 text-lg px-4 py-1">
                                  {item.pontos} pts
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Destaque */}
                  <div className="mt-6 bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-6 text-center">
                    <CheckCircle className="w-12 h-12 mx-auto mb-3 text-purple-600" />
                    <h3 className="text-xl font-bold text-purple-700 mb-2">
                      Todos Ganham Pontos!
                    </h3>
                    <p className="text-purple-600">
                      No Ranking da Galera, não importa sua colocação. 
                      O importante é participar e completar a prova!
                    </p>
                  </div>

                  {/* Critérios de Desempate */}
                  <div className="mt-6">
                    <h3 className="font-semibold text-slate-700 mb-3">Critérios de Desempate</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="flex items-center gap-3 bg-white p-4 rounded-lg border">
                        <span className="flex items-center justify-center w-8 h-8 bg-purple-100 text-purple-700 rounded-full font-bold">1</span>
                        <span className="text-slate-600">Pontos totais</span>
                      </div>
                      <div className="flex items-center gap-3 bg-white p-4 rounded-lg border">
                        <span className="flex items-center justify-center w-8 h-8 bg-purple-100 text-purple-700 rounded-full font-bold">2</span>
                        <span className="text-slate-600">Número de provas</span>
                      </div>
                      <div className="flex items-center gap-3 bg-white p-4 rounded-lg border">
                        <span className="flex items-center justify-center w-8 h-8 bg-purple-100 text-purple-700 rounded-full font-bold">3</span>
                        <span className="text-slate-600">Distância acumulada</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Tab Equipes */}
          <TabsContent value="equipes">
            <div className="space-y-6">
              <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3 text-amber-700">
                    <Target className="w-6 h-6" />
                    {regras?.ranking_equipes?.titulo || 'RANKING DAS EQUIPES'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-600 mb-6">
                    {regras?.ranking_equipes?.descricao}
                  </p>

                  {/* Tabela de Pontuação de Equipes */}
                  <div className="max-w-lg mx-auto">
                    <h3 className="font-semibold text-slate-700 mb-3 text-center">
                      Sistema de Pontuação
                    </h3>
                    <div className="bg-white rounded-lg border overflow-hidden">
                      <table className="w-full">
                        <thead className="bg-amber-500 text-white">
                          <tr>
                            <th className="py-3 px-4 text-left">Critério</th>
                            <th className="py-3 px-4 text-center">Pontos</th>
                          </tr>
                        </thead>
                        <tbody>
                          {regras?.ranking_equipes?.pontuacao?.map((item, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-slate-50' : 'bg-white'}>
                              <td className="py-3 px-4">{item.criterio}</td>
                              <td className="py-3 px-4 text-center font-bold text-amber-600">
                                {item.pontos}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Fórmula */}
                  <div className="mt-6 bg-gradient-to-r from-amber-100 to-orange-100 rounded-lg p-6 text-center">
                    <h3 className="text-lg font-bold text-amber-700 mb-3">
                      Fórmula de Cálculo
                    </h3>
                    <code className="bg-white px-4 py-2 rounded-lg text-amber-800 font-mono">
                      Pontuação Total = (Atletas × 0,5) + (Resultados × 1,0) + Bônus de Pódio
                    </code>
                  </div>

                  {/* Níveis de Classificação */}
                  <div className="mt-6">
                    <h3 className="font-semibold text-slate-700 mb-3">Níveis de Classificação</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      <Card className="bg-amber-50 border-amber-300">
                        <CardContent className="pt-4 text-center">
                          <Trophy className="w-8 h-8 mx-auto mb-2 text-amber-500" />
                          <h4 className="font-bold text-amber-700">Nacional</h4>
                          <p className="text-sm text-amber-600">
                            Ranking geral de todas as assessorias do Brasil
                          </p>
                        </CardContent>
                      </Card>
                      <Card className="bg-slate-50 border-slate-300">
                        <CardContent className="pt-4 text-center">
                          <Medal className="w-8 h-8 mx-auto mb-2 text-slate-500" />
                          <h4 className="font-bold text-slate-700">Estadual</h4>
                          <p className="text-sm text-slate-600">
                            Ranking por estado (UF)
                          </p>
                        </CardContent>
                      </Card>
                      <Card className="bg-orange-50 border-orange-300">
                        <CardContent className="pt-4 text-center">
                          <Award className="w-8 h-8 mx-auto mb-2 text-orange-500" />
                          <h4 className="font-bold text-orange-700">Cidade</h4>
                          <p className="text-sm text-orange-600">
                            Ranking por município
                          </p>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        {regras?.ultima_atualizacao && (
          <div className="mt-8 text-center text-sm text-slate-500">
            Última atualização: {new Date(regras.ultima_atualizacao).toLocaleDateString('pt-BR')}
            {regras.atualizado_por && ` por ${regras.atualizado_por}`}
          </div>
        )}
      </div>
    </div>
  );
};

export default RegrasPage;
