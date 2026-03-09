import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { 
  Trophy, Users, MapPin, Award, CheckCircle, TrendingUp, ArrowLeft, Download, 
  Send, Mail, Phone, Loader2, Zap, BarChart3, User, Star, Target, Medal,
  Calendar, Flag, ExternalLink, Crown, Share2, Camera, X
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import html2canvas from 'html2canvas';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AssessoriaPage = () => {
  const { nome } = useParams();
  const navigate = useNavigate();
  const [assessoria, setAssessoria] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingCertificado, setDownloadingCertificado] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [showFotoModal, setShowFotoModal] = useState(false);
  const [fotoModalUrl, setFotoModalUrl] = useState('');
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
      toast.success('Selo baixado com sucesso!');
    } catch (error) {
      console.error('Erro ao gerar certificado:', error);
      toast.error('Erro ao gerar o selo');
    } finally {
      setDownloadingCertificado(false);
    }
  };

  const handleVerPerfilDono = () => {
    if (assessoria.responsavel_id) {
      navigate(`/atleta/${assessoria.responsavel_id}`);
    } else {
      toast.info('Perfil do responsável não disponível');
    }
  };

  const handleCompartilhar = async () => {
    setSharing(true);
    try {
      const url = window.location.href;
      if (navigator.share) {
        await navigator.share({
          title: `${assessoria.nome} - Liga Nacional de Assessorias`,
          text: `Confira a assessoria ${assessoria.nome} no Ranking Run!`,
          url: url
        });
      } else {
        await navigator.clipboard.writeText(url);
        toast.success('Link copiado para a área de transferência!');
      }
    } catch (error) {
      console.error('Erro ao compartilhar:', error);
    } finally {
      setSharing(false);
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
        {/* Header Melhorado */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Button onClick={() => navigate('/')} variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar ao Ranking
            </Button>
            <Button onClick={handleCompartilhar} variant="outline" size="sm" disabled={sharing}>
              <Share2 className="w-4 h-4 mr-2" />
              Compartilhar
            </Button>
          </div>
          
          {/* Hero Section */}
          <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 rounded-2xl p-6 md:p-8 text-white shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              {/* Logo/Avatar da Assessoria */}
              <div className="flex-shrink-0">
                <div className={`w-24 h-24 md:w-32 md:h-32 rounded-2xl ${getSeloColor(assessoria.selo)} flex items-center justify-center text-6xl shadow-lg border-4 border-white/30`}>
                  {getSeloIcon(assessoria.selo)}
                </div>
              </div>
              
              {/* Informações */}
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-3 mb-2">
                  <h1 className="text-2xl md:text-4xl font-bold">{assessoria.nome}</h1>
                  <Badge className="bg-white/20 text-white border-white/30 text-sm px-3 py-1">
                    SELO {assessoria.selo?.toUpperCase()}
                  </Badge>
                </div>
                
                <p className="text-amber-100 flex items-center gap-2 mb-3">
                  <MapPin className="w-5 h-5" />
                  <span className="text-lg">{assessoria.cidade}, {assessoria.estado}</span>
                </p>
                
                {/* Responsável com link */}
                {assessoria.responsavel_nome && (
                  <div 
                    className="flex items-center gap-2 bg-white/10 rounded-lg px-4 py-2 w-fit cursor-pointer hover:bg-white/20 transition-colors"
                    onClick={handleVerPerfilDono}
                  >
                    <Crown className="w-5 h-5 text-yellow-300" />
                    <span className="font-medium">Responsável:</span>
                    <span className="underline underline-offset-2">{assessoria.responsavel_nome}</span>
                    <ExternalLink className="w-4 h-4 ml-1" />
                  </div>
                )}
                
                {/* Bio */}
                {assessoria.mensagem_bio && (
                  <div className="mt-3 bg-white/10 rounded-lg px-4 py-3 max-w-2xl">
                    <p className="text-amber-50 italic">"{assessoria.mensagem_bio}"</p>
                  </div>
                )}
              </div>
              
              {/* Posição Destaque */}
              <div className="flex-shrink-0 text-center bg-white/10 rounded-xl p-4 md:p-6">
                <Trophy className="w-10 h-10 mx-auto text-yellow-300 mb-2" />
                <p className="text-4xl md:text-5xl font-bold">{assessoria.posicao_nacional || '-'}º</p>
                <p className="text-sm text-amber-100">Ranking Nacional</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Coluna Principal */}
          <div className="lg:col-span-2 space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/30 dark:to-amber-800/20 border-amber-200 hover:shadow-lg transition-shadow">
                <CardContent className="p-4 text-center">
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-amber-500/20 flex items-center justify-center">
                    <Trophy className="w-6 h-6 text-amber-600" />
                  </div>
                  <p className="text-3xl font-bold text-amber-600">{assessoria.posicao_estadual || '-'}º</p>
                  <p className="text-xs text-slate-500 font-medium">Ranking Estadual</p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/30 dark:to-emerald-800/20 border-emerald-200 hover:shadow-lg transition-shadow">
                <CardContent className="p-4 text-center">
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Users className="w-6 h-6 text-emerald-600" />
                  </div>
                  <p className="text-3xl font-bold text-emerald-600">{assessoria.total_atletas}</p>
                  <p className="text-xs text-slate-500 font-medium">Atletas Ativos</p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/20 border-blue-200 hover:shadow-lg transition-shadow">
                <CardContent className="p-4 text-center">
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-blue-500/20 flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-blue-600" />
                  </div>
                  <p className="text-3xl font-bold text-blue-600">{assessoria.total_resultados}</p>
                  <p className="text-xs text-slate-500 font-medium">Resultados Aprovados</p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/20 border-purple-200 hover:shadow-lg transition-shadow">
                <CardContent className="p-4 text-center">
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-purple-500/20 flex items-center justify-center">
                    <Star className="w-6 h-6 text-purple-600" />
                  </div>
                  <p className="text-3xl font-bold text-purple-600">{assessoria.pontos_total}</p>
                  <p className="text-xs text-slate-500 font-medium">Pontos ROE-RR</p>
                </CardContent>
              </Card>
            </div>

            {/* Conquistas e Destaques */}
            <Card className="border-amber-200 overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20">
                <CardTitle className="flex items-center gap-2 text-lg text-amber-700 dark:text-amber-400">
                  <Medal className="w-5 h-5" />
                  Conquistas e Destaques
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="text-center p-4 bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 rounded-xl border border-yellow-200">
                    <span className="text-3xl">🥇</span>
                    <p className="text-2xl font-bold text-yellow-600 mt-1">{assessoria.total_primeiros}</p>
                    <p className="text-xs text-slate-500">1º Lugares</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-slate-50 to-gray-50 dark:from-slate-800 dark:to-gray-800 rounded-xl border border-slate-200">
                    <span className="text-3xl">🏅</span>
                    <p className="text-2xl font-bold text-slate-600 mt-1">{assessoria.total_podios}</p>
                    <p className="text-xs text-slate-500">Pódios (2º-5º)</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20 rounded-xl border border-emerald-200">
                    <span className="text-3xl">👥</span>
                    <p className="text-2xl font-bold text-emerald-600 mt-1">{assessoria.pontos_cadastro}</p>
                    <p className="text-xs text-slate-500">Pts de Cadastro</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200">
                    <span className="text-3xl">✅</span>
                    <p className="text-2xl font-bold text-blue-600 mt-1">{assessoria.pontos_resultados}</p>
                    <p className="text-xs text-slate-500">Pts de Resultados</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Galeria de Fotos de Pódio */}
            {assessoria.fotos_podio && assessoria.fotos_podio.length > 0 && (
              <Card className="border-purple-200 overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20">
                  <CardTitle className="flex items-center gap-2 text-lg text-purple-700 dark:text-purple-400">
                    <Camera className="w-5 h-5" />
                    Galeria de Pódios ({assessoria.fotos_podio.length} fotos)
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {assessoria.fotos_podio.map((foto, index) => (
                      <div 
                        key={index}
                        className="group relative aspect-square rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all cursor-pointer"
                        onClick={() => {
                          setFotoModalUrl(foto.foto_url.startsWith('http') ? foto.foto_url : `${BACKEND_URL}${foto.foto_url}`);
                          setShowFotoModal(true);
                        }}
                      >
                        <img 
                          src={foto.foto_url.startsWith('http') ? foto.foto_url : `${BACKEND_URL}${foto.foto_url}`}
                          alt={`Pódio - ${foto.atleta_nome}`}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                          <div className="absolute bottom-0 left-0 right-0 p-3 text-white">
                            <p className="font-semibold text-sm truncate">{foto.atleta_nome}</p>
                            <p className="text-xs opacity-90 truncate">{foto.competicao}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge className="bg-amber-500 text-xs">{foto.colocacao}º lugar</Badge>
                            </div>
                          </div>
                        </div>
                        {/* Badge de posição no canto */}
                        <div className={`absolute top-2 right-2 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg ${
                          foto.colocacao === 1 ? 'bg-yellow-500' :
                          foto.colocacao === 2 ? 'bg-slate-400' :
                          foto.colocacao === 3 ? 'bg-amber-700' : 'bg-purple-500'
                        }`}>
                          {foto.colocacao}º
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

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
            {/* Card do Responsável */}
            {assessoria.responsavel_nome && (
              <Card className="overflow-hidden border-emerald-200">
                <CardHeader className="bg-gradient-to-r from-emerald-500 to-green-500 text-white pb-4">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Crown className="w-5 h-5 text-yellow-300" />
                    Responsável da Assessoria
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="flex items-center gap-4 mb-4">
                    <Avatar className="w-16 h-16 border-2 border-emerald-200">
                      <AvatarFallback className="bg-emerald-100 text-emerald-700 text-xl">
                        {assessoria.responsavel_nome?.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-bold text-lg">{assessoria.responsavel_nome}</p>
                      <p className="text-sm text-slate-500">Dono da Assessoria</p>
                    </div>
                  </div>
                  <Button 
                    className="w-full bg-emerald-500 hover:bg-emerald-600" 
                    onClick={handleVerPerfilDono}
                    data-testid="btn-ver-perfil-dono"
                  >
                    <User className="w-4 h-4 mr-2" />
                    Ver Perfil Completo
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Selo Digital Oficial */}
            <Card className="overflow-hidden border-amber-200">
              <CardHeader className="bg-gradient-to-r from-amber-500 to-yellow-500 text-white">
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5" />
                  Selo Digital Oficial 2026
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {/* Certificado para Download */}
                <div 
                  ref={certificadoRef}
                  className={`${getSeloColor(assessoria.selo)} text-white p-6 rounded-xl text-center mb-4 shadow-lg`}
                >
                  <div className="text-6xl mb-3">{getSeloIcon(assessoria.selo)}</div>
                  <h3 className="text-xl font-bold mb-1">{getSeloTitle(assessoria.selo)}</h3>
                  <p className="text-lg font-semibold">{assessoria.nome}</p>
                  <p className="text-sm opacity-80 mt-1">{assessoria.cidade}/{assessoria.estado}</p>
                  <div className="border-t border-white/30 mt-4 pt-4">
                    <p className="text-sm opacity-90">Liga Nacional de Assessorias</p>
                    <p className="text-sm font-bold">RANKING RUN</p>
                    <p className="text-xs opacity-75 mt-2">Certificação Oficial ROE-RR – 2026</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <Button 
                    className="w-full bg-amber-500 hover:bg-amber-600" 
                    onClick={downloadCertificado}
                    disabled={downloadingCertificado}
                    data-testid="btn-baixar-selo"
                  >
                    {downloadingCertificado ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Gerando Selo...
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4 mr-2" />
                        Baixar Selo Oficial
                      </>
                    )}
                  </Button>
                  
                  {assessoria.responsavel_id && (
                    <Button 
                      variant="outline"
                      className="w-full border-amber-300 text-amber-700 hover:bg-amber-50" 
                      onClick={handleVerPerfilDono}
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Ver Perfil do Responsável
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Botão de Contato */}
            <Card className="border-emerald-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Target className="w-5 h-5 text-emerald-500" />
                  Quer Treinar com Esta Equipe?
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-600">
                  Entre em contato com a assessoria para conhecer os planos de treino, 
                  metodologia e comece sua jornada de evolução!
                </p>
                <Button className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 shadow-md">
                  <Send className="w-4 h-4 mr-2" />
                  Quero Treinar com Essa Assessoria
                </Button>
              </CardContent>
            </Card>

            {/* Sistema de Pontuação */}
            <Card className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900 border-slate-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-amber-500" />
                  Sistema de Pontuação ROE-RR
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-2 p-2 bg-white dark:bg-slate-700 rounded-lg">
                    <span className="text-emerald-500">+0,5</span>
                    <span className="text-slate-600 dark:text-slate-300">Atleta cadastrado</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 bg-white dark:bg-slate-700 rounded-lg">
                    <span className="text-blue-500">+1,0</span>
                    <span className="text-slate-600 dark:text-slate-300">Resultado aprovado</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 bg-white dark:bg-slate-700 rounded-lg">
                    <span className="text-amber-500">+0,5</span>
                    <span className="text-slate-600 dark:text-slate-300">2º a 5º lugar</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 bg-white dark:bg-slate-700 rounded-lg">
                    <span className="text-yellow-500">+1,0</span>
                    <span className="text-slate-600 dark:text-slate-300">1º lugar</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Modal de Visualização de Foto */}
      <Dialog open={showFotoModal} onOpenChange={setShowFotoModal}>
        <DialogContent className="max-w-4xl bg-black/95 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">Foto do Pódio</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center p-4">
            <img
              src={fotoModalUrl}
              alt="Foto do Pódio"
              className="max-w-full max-h-[70vh] object-contain rounded-lg shadow-xl"
            />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AssessoriaPage;
