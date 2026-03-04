import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Trophy, Users, MapPin, Award, CheckCircle, TrendingUp, ArrowLeft, Download, Send, Mail, Phone, Loader2 } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import html2canvas from 'html2canvas';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AssessoriaPage = () => {
  const { nome } = useParams();
  const navigate = useNavigate();
  const [assessoria, setAssessoria] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingCertificado, setDownloadingCertificado] = useState(false);
  const certificadoRef = useRef(null);

  useEffect(() => {
    const fetchAssessoria = async () => {
      try {
        const response = await axios.get(`${API}/liga-assessorias/assessoria/${encodeURIComponent(nome)}`);
        setAssessoria(response.data);
      } catch (error) {
        console.error('Erro ao buscar assessoria:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAssessoria();
  }, [nome]);

  const getSeloIcon = (selo) => {
    switch(selo) {
      case 'ouro': return '🥇';
      case 'prata': return '🥈';
      case 'bronze': return '🥉';
      default: return '🏅';
    }
  };

  const getSeloColor = (selo) => {
    switch(selo) {
      case 'ouro': return 'bg-gradient-to-r from-yellow-500 to-amber-600';
      case 'prata': return 'bg-gradient-to-r from-slate-400 to-slate-500';
      case 'bronze': return 'bg-gradient-to-r from-amber-700 to-orange-800';
      default: return 'bg-slate-600';
    }
  };

  const getSeloTitle = (selo) => {
    switch(selo) {
      case 'ouro': return 'TOP 20 NACIONAL';
      case 'prata': return 'TOP 10 ESTADUAL';
      case 'bronze': return 'ASSESSORIA INTEGRANTE';
      default: return 'PARTICIPANTE';
    }
  };

  const downloadCertificado = async () => {
    if (!certificadoRef.current) return;
    
    setDownloadingCertificado(true);
    try {
      const canvas = await html2canvas(certificadoRef.current, {
        scale: 2,
        backgroundColor: null,
        useCORS: true
      });
      
      const link = document.createElement('a');
      link.download = `selo_${assessoria.nome.replace(/\s+/g, '_')}_ROE-RR_2026.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (error) {
      console.error('Erro ao gerar certificado:', error);
    } finally {
      setDownloadingCertificado(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
      </div>
    );
  }

  if (!assessoria) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 flex flex-col items-center justify-center">
        <Award className="w-16 h-16 text-slate-300 mb-4" />
        <h2 className="text-xl font-semibold text-slate-600">Assessoria não encontrada</h2>
        <Button onClick={() => navigate('/')} className="mt-4" variant="outline">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Voltar ao Ranking
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button onClick={() => navigate('/')} variant="outline" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl md:text-3xl font-bold text-amber-600 flex items-center gap-3">
              {getSeloIcon(assessoria.selo)} {assessoria.nome}
              <Badge className={`${getSeloColor(assessoria.selo)} text-white`}>
                SELO {assessoria.selo?.toUpperCase()}
              </Badge>
            </h1>
            <p className="text-slate-500 flex items-center gap-2 mt-1">
              <MapPin className="w-4 h-4" />
              {assessoria.cidade}/{assessoria.estado}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Coluna Principal */}
          <div className="lg:col-span-2 space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-amber-50 dark:bg-amber-900/20 border-amber-200">
                <CardContent className="p-4 text-center">
                  <Trophy className="w-8 h-8 mx-auto text-amber-500 mb-2" />
                  <p className="text-3xl font-bold text-amber-600">{assessoria.posicao_nacional || '-'}º</p>
                  <p className="text-xs text-slate-500">Posição Nacional</p>
                </CardContent>
              </Card>
              <Card className="bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200">
                <CardContent className="p-4 text-center">
                  <Users className="w-8 h-8 mx-auto text-emerald-500 mb-2" />
                  <p className="text-3xl font-bold text-emerald-600">{assessoria.total_atletas}</p>
                  <p className="text-xs text-slate-500">Atletas Ativos</p>
                </CardContent>
              </Card>
              <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200">
                <CardContent className="p-4 text-center">
                  <CheckCircle className="w-8 h-8 mx-auto text-blue-500 mb-2" />
                  <p className="text-3xl font-bold text-blue-600">{assessoria.total_resultados}</p>
                  <p className="text-xs text-slate-500">Resultados</p>
                </CardContent>
              </Card>
              <Card className="bg-purple-50 dark:bg-purple-900/20 border-purple-200">
                <CardContent className="p-4 text-center">
                  <Award className="w-8 h-8 mx-auto text-purple-500 mb-2" />
                  <p className="text-3xl font-bold text-purple-600">{assessoria.pontos_total}</p>
                  <p className="text-xs text-slate-500">Pontos Total</p>
                </CardContent>
              </Card>
            </div>

            {/* Conquistas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Trophy className="w-5 h-5 text-yellow-500" />
                  Conquistas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-3">
                  <Badge variant="outline" className="bg-yellow-50 border-yellow-300 text-yellow-700 py-2 px-4">
                    🥇 {assessoria.total_primeiros} Primeiros Lugares
                  </Badge>
                  <Badge variant="outline" className="bg-slate-50 border-slate-300 text-slate-700 py-2 px-4">
                    🏅 {assessoria.total_podios} Pódios (2º-5º)
                  </Badge>
                  <Badge variant="outline" className="bg-emerald-50 border-emerald-300 text-emerald-700 py-2 px-4">
                    📊 {assessoria.pontos_cadastro} pts de Cadastro
                  </Badge>
                  <Badge variant="outline" className="bg-blue-50 border-blue-300 text-blue-700 py-2 px-4">
                    ✅ {assessoria.pontos_resultados} pts de Resultados
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Atletas da Equipe */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Users className="w-5 h-5 text-emerald-500" />
                  Atletas da Equipe ({assessoria.atletas?.length || 0})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {assessoria.atletas?.map((atleta) => (
                    <div 
                      key={atleta.id}
                      className="flex flex-col items-center p-3 bg-slate-50 dark:bg-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 cursor-pointer transition-colors"
                      onClick={() => navigate(`/atleta/${atleta.id}`)}
                    >
                      <Avatar className="w-14 h-14 mb-2">
                        {atleta.foto_url ? (
                          <AvatarImage src={atleta.foto_url.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                        ) : null}
                        <AvatarFallback className="bg-emerald-100 text-emerald-700 text-lg">
                          {atleta.nome?.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <p className="font-medium text-sm text-center truncate w-full">{atleta.nome?.split(' ')[0]}</p>
                      <p className="text-xs text-slate-500">{atleta.pontos || 0} pts</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Evolução Mensal */}
            {assessoria.evolucao_mensal && assessoria.evolucao_mensal.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <TrendingUp className="w-5 h-5 text-blue-500" />
                    Evolução Mensal
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={assessoria.evolucao_mensal}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis dataKey="mes" stroke="#9CA3AF" tick={{ fontSize: 12 }} />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip />
                      <Area type="monotone" dataKey="resultados" fill="#F59E0B" stroke="#D97706" fillOpacity={0.3} name="Resultados" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Coluna Lateral - Selo e Ações */}
          <div className="space-y-6">
            {/* Selo Digital Oficial */}
            <Card className="overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-amber-500 to-yellow-500 text-white">
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5" />
                  Selo Digital Oficial
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {/* Certificado para Download */}
                <div 
                  ref={certificadoRef}
                  className={`${getSeloColor(assessoria.selo)} text-white p-6 rounded-lg text-center mb-4`}
                >
                  <div className="text-5xl mb-3">{getSeloIcon(assessoria.selo)}</div>
                  <h3 className="text-xl font-bold mb-1">{getSeloTitle(assessoria.selo)}</h3>
                  <p className="text-lg font-semibold">{assessoria.nome}</p>
                  <div className="border-t border-white/30 mt-4 pt-4">
                    <p className="text-sm opacity-90">Liga Nacional de Assessorias</p>
                    <p className="text-sm font-semibold">Ranking Run</p>
                    <p className="text-xs opacity-75 mt-2">Classificação Oficial ROE-RR – 2026</p>
                  </div>
                </div>

                <Button 
                  className="w-full bg-amber-500 hover:bg-amber-600" 
                  onClick={downloadCertificado}
                  disabled={downloadingCertificado}
                >
                  {downloadingCertificado ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Gerando...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Baixar Selo Oficial
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Botão de Contato */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quer treinar com esta equipe?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-600">
                  Entre em contato com a assessoria para conhecer os planos de treino e começar sua jornada!
                </p>
                <Button className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700">
                  <Send className="w-4 h-4 mr-2" />
                  Quero Treinar com Essa Assessoria
                </Button>
              </CardContent>
            </Card>

            {/* Informações */}
            <Card className="bg-slate-50 dark:bg-slate-800">
              <CardContent className="p-4">
                <h4 className="font-semibold text-sm mb-3 text-slate-700 dark:text-slate-300">
                  Sistema de Pontuação ROE-RR
                </h4>
                <div className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
                  <p>• Atleta cadastrado = +0,5 pts</p>
                  <p>• Resultado aprovado = +1,0 pts</p>
                  <p>• 2º a 5º lugar = +0,5 pts extra</p>
                  <p>• 1º lugar = +1,0 pts extra</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssessoriaPage;
