import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { ArrowLeft, MapPin, Trophy, Medal, Award, Share2, Download, Copy, Check, Link2, Instagram, Facebook } from 'lucide-react';
import PendingBadge from '@/components/PendingBadge';
import RaceProgressBar from '@/components/RaceProgressBar';
import ConquistasTable from '@/components/ConquistasTable';
import GraficoEvolucao from '@/components/GraficoEvolucao';
import SelosAtleta from '@/components/SelosAtleta';
import { BadgesDisplay } from '@/components/BadgesDisplay';
import MinhasIndicacoes from '@/components/MinhasIndicacoes';
import { useAuth } from '@/context/AuthContext';
import html2canvas from 'html2canvas';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Cores por modalidade
const getModalidadeColors = (modalidade) => {
  if (modalidade === 'povao_pace_livre') {
    return {
      ring: 'ring-purple-500',
      bg: '#8B5CF6',
      bgClass: 'bg-purple-500',
      text: 'text-purple-700 dark:text-purple-300',
      bgLight: 'bg-purple-100 dark:bg-purple-900'
    };
  }
  // Profissional/Amador (default)
  return {
    ring: 'ring-emerald-500',
    bg: '#10B981',
    bgClass: 'bg-emerald-500',
    text: 'text-emerald-700 dark:text-emerald-300',
    bgLight: 'bg-emerald-100 dark:bg-emerald-900'
  };
};

const AtletaDetalhes = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [atleta, setAtleta] = useState(null);
  const [corridas, setCorridas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareImageUrl, setShareImageUrl] = useState(null);
  const [generatingImage, setGeneratingImage] = useState(false);
  const [copied, setCopied] = useState(false);
  const shareCardRef = useRef(null);
  
  // Verificar se é o dono do perfil
  const isOwner = user?.id === id;

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

  // Gerar imagem para compartilhamento
  const generateShareImage = async () => {
    setGeneratingImage(true);
    try {
      const element = shareCardRef.current;
      if (!element) return;

      const canvas = await html2canvas(element, {
        scale: 2,
        backgroundColor: '#0f172a',
        useCORS: true,
        logging: false
      });

      const imageUrl = canvas.toDataURL('image/png');
      setShareImageUrl(imageUrl);
    } catch (error) {
      console.error('Erro ao gerar imagem:', error);
    } finally {
      setGeneratingImage(false);
    }
  };

  const downloadImage = () => {
    if (!shareImageUrl) return;
    const link = document.createElement('a');
    link.download = `ranking_${atleta.nome.replace(/\s+/g, '_')}.png`;
    link.href = shareImageUrl;
    link.click();
  };

  const copyLink = async () => {
    const link = `${window.location.origin}/atleta/${id}`;
    await navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const shareToWhatsApp = () => {
    const texto = encodeURIComponent(
      `🏆 Confira meu ranking no Ranking Run Pró!\n\n` +
      `👤 ${atleta.nome}\n` +
      `⭐ ${atleta.pontos_carreira} pontos\n` +
      `🏃 ${atleta.total_corridas} corridas\n\n` +
      `${window.location.href}`
    );
    window.open(`https://api.whatsapp.com/send?text=${texto}`, '_blank');
  };

  const shareToFacebook = () => {
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=600,height=400');
  };

  const shareToInstagram = async () => {
    // Para Instagram, fazer download da imagem
    if (shareImageUrl) {
      downloadImage();
      alert('Imagem baixada! Abra o Instagram e compartilhe a imagem no seu Story ou Feed.');
    } else {
      await generateShareImage();
      setTimeout(() => {
        downloadImage();
        alert('Imagem baixada! Abra o Instagram e compartilhe a imagem no seu Story ou Feed.');
      }, 500);
    }
  };

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

  // Construir URL da foto
  const getFotoUrl = () => {
    if (!atleta?.foto_url) return null;
    if (atleta.foto_url.startsWith('http')) return atleta.foto_url;
    return `${BACKEND_URL}${atleta.foto_url}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header com botões */}
        <div className="flex items-center justify-between mb-6">
          <Button
            onClick={() => navigate('/')}
            variant="outline"
            data-testid="btn-voltar"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar ao Ranking
          </Button>

          {/* Botão de Compartilhamento */}
          <Dialog open={showShareModal} onOpenChange={(open) => {
            setShowShareModal(open);
            if (open && !shareImageUrl) {
              setTimeout(generateShareImage, 100);
            }
          }}>
            <DialogTrigger asChild>
              <Button className="bg-emerald-600 hover:bg-emerald-700" data-testid="btn-compartilhar">
                <Share2 className="w-4 h-4 mr-2" />
                Compartilhar
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-xl">Compartilhar Ranking</DialogTitle>
              </DialogHeader>
              
              <div className="space-y-4">
                {/* Preview da imagem */}
                <div className="relative">
                  {generatingImage && (
                    <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center rounded-lg z-10">
                      <p className="text-white">Gerando imagem...</p>
                    </div>
                  )}
                  
                  {/* Card para gerar imagem (9:16 aspect ratio) */}
                  <div 
                    ref={shareCardRef}
                    className="bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 rounded-lg p-6 text-white"
                    style={{ aspectRatio: '9/16', maxHeight: '400px' }}
                  >
                    <div className="h-full flex flex-col justify-between">
                      {/* Header */}
                      <div className="text-center">
                        <p className="text-emerald-400 text-sm font-semibold mb-1">RANKING RUN PRÓ 2025</p>
                        <div className="w-16 h-1 bg-emerald-500 mx-auto rounded-full" />
                      </div>

                      {/* Atleta Info */}
                      <div className="text-center flex-1 flex flex-col justify-center">
                        <Avatar className="h-20 w-20 mx-auto mb-3 ring-4 ring-emerald-500">
                          <AvatarImage src={getFotoUrl()} alt={atleta.nome} />
                          <AvatarFallback className="bg-emerald-600 text-white text-xl">
                            {atleta.nome.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <h2 className="text-xl font-bold mb-1">{atleta.nome}</h2>
                        <p className="text-emerald-300 text-sm mb-4">{atleta.equipe}</p>
                        
                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-2 mb-4">
                          <div className="bg-slate-800/50 rounded-lg p-2">
                            <p className="text-2xl font-bold text-amber-400">{atleta.pontos_carreira}</p>
                            <p className="text-xs text-slate-400">Pontos</p>
                          </div>
                          <div className="bg-slate-800/50 rounded-lg p-2">
                            <p className="text-2xl font-bold text-blue-400">{atleta.total_corridas}</p>
                            <p className="text-xs text-slate-400">Corridas</p>
                          </div>
                          <div className="bg-slate-800/50 rounded-lg p-2">
                            <p className="text-2xl font-bold text-emerald-400">{atleta.melhor_colocacao}º</p>
                            <p className="text-xs text-slate-400">Melhor</p>
                          </div>
                        </div>
                      </div>

                      {/* Footer */}
                      <div className="text-center">
                        <p className="text-xs text-slate-400">ranking-run-pro.com</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Botões de Compartilhamento */}
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    onClick={shareToWhatsApp}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    💬 WhatsApp
                  </Button>
                  <Button
                    onClick={shareToInstagram}
                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                  >
                    📷 Instagram
                  </Button>
                  <Button
                    onClick={shareToFacebook}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    📘 Facebook
                  </Button>
                  <Button
                    onClick={downloadImage}
                    disabled={!shareImageUrl}
                    variant="outline"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Baixar
                  </Button>
                </div>

                {/* Copiar Link */}
                <div className="flex gap-2">
                  <Button
                    onClick={copyLink}
                    variant="outline"
                    className="flex-1"
                  >
                    {copied ? (
                      <>
                        <Check className="w-4 h-4 mr-2 text-emerald-500" />
                        Copiado!
                      </>
                    ) : (
                      <>
                        <Link2 className="w-4 h-4 mr-2" />
                        Copiar Link
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Header do Atleta */}
        <Card className="mb-6 border-slate-200 dark:border-slate-800 shadow-lg">
          <CardContent className="pt-6">
            {(() => {
              const colors = getModalidadeColors(atleta.modalidade_usuario);
              return (
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              {/* Foto com Selo P */}
              <div className="relative">
                <Avatar className={`h-32 w-32 ring-4 ${colors.ring} ring-offset-4 ring-offset-white dark:ring-offset-slate-900`}>
                  <AvatarImage src={getFotoUrl()} alt={atleta.nome} />
                  <AvatarFallback 
                    className="text-white text-3xl font-bold"
                    style={{ backgroundColor: colors.bg }}
                  >
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
                <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 mb-2">
                  <h1 className={`text-3xl font-bold ${atleta.modalidade_usuario === 'povao_pace_livre' ? 'text-purple-600 dark:text-purple-400' : 'text-emerald-600 dark:text-emerald-400'}`}>
                    {atleta.nome}
                  </h1>
                  {/* Badge de Dono de Assessoria */}
                  {(atleta.role === 'dono_assessoria' || atleta.is_dono_assessoria) && (
                    <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-3 py-1 text-sm font-semibold shadow-md">
                      <Trophy className="w-4 h-4 mr-1" />
                      Dono de Assessoria
                    </Badge>
                  )}
                </div>
                <div className="flex items-center justify-center md:justify-start gap-2 text-slate-600 dark:text-slate-400 mb-3">
                  <MapPin className="w-4 h-4" />
                  <span>{atleta.cidade}, {atleta.estado}, Brasil</span>
                </div>
                <div className="text-slate-600 dark:text-slate-400 mb-3">
                  <strong>Equipe:</strong> {atleta.equipe}
                </div>

                {/* Redes Sociais com Apelido/Nome */}
                <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 mb-3">
                  {atleta.instagram_url && (
                    <a 
                      href={atleta.instagram_url.startsWith('http') ? atleta.instagram_url : `https://instagram.com/${atleta.instagram_url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-pink-600 hover:text-pink-700 transition-colors"
                      data-testid="link-instagram"
                    >
                      <Instagram className="w-5 h-5" />
                      <span className="font-medium">@{atleta.apelido || atleta.nome.split(' ')[0]}</span>
                    </a>
                  )}
                  {atleta.facebook_url && (
                    <a 
                      href={atleta.facebook_url.startsWith('http') ? atleta.facebook_url : `https://facebook.com/${atleta.facebook_url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors"
                      data-testid="link-facebook"
                    >
                      <Facebook className="w-5 h-5" />
                      <span className="font-medium">{atleta.nome.split(' ')[0]}</span>
                    </a>
                  )}
                </div>

                {/* Bio do Atleta */}
                {atleta.bio && (
                  <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-3 mb-3">
                    <p className="text-sm text-slate-700 dark:text-slate-300 italic">
                      "{atleta.bio}"
                    </p>
                  </div>
                )}

                <div className="text-lg font-semibold text-slate-700 dark:text-slate-300">
                  Pontos de carreira: <span className="text-amber-600 dark:text-amber-400">{atleta.pontos_carreira}</span>
                </div>

                {/* Barra de Progresso */}
                <div className="mt-4">
                  <RaceProgressBar current={atleta.total_corridas} total={12} />
                </div>
              </div>
            </div>
              );
            })()}
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

        {/* Quadro de Indicações - Visível apenas para o próprio atleta */}
        {isOwner && (
          <div className="mb-6">
            <MinhasIndicacoes atletaId={id} isOwner={true} />
          </div>
        )}

        {/* Badges Visuais - Nova Seção */}
        <BadgesDisplay atletaId={id} showTitle={true} />

        {/* Selos e Conquistas */}
        <Card className="border-slate-200 dark:border-slate-800 shadow-lg">
          <CardContent className="pt-6">
            <h2 className="text-2xl font-bold text-amber-600 dark:text-amber-400 mb-4 flex items-center gap-2">
              <Medal className="w-6 h-6" />
              Selos e Conquistas
            </h2>
            <SelosAtleta atletaId={id} compact={false} />
          </CardContent>
        </Card>

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
