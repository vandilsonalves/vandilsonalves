// /app/frontend/src/components/BadgesDisplay.jsx
// Componente de exibição de badges visuais

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { 
  Star, Medal, Trophy, Award, Zap, Play, Shield, Target, Crown, 
  Calendar, Users, Eye, Sparkles, Share2, Download, Check, Lock, HelpCircle, Gem
} from 'lucide-react';
import { toast } from 'sonner';
import html2canvas from 'html2canvas';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mapeamento de ícones
const ICON_MAP = {
  star: Star,
  medal: Medal,
  trophy: Trophy,
  award: Award,
  zap: Zap,
  play: Play,
  shield: Shield,
  target: Target,
  crown: Crown,
  calendar: Calendar,
  users: Users,
  eye: Eye,
  sparkles: Sparkles,
  gem: Gem
};

// Definição completa de todas as insígnias do sistema com explicações (sincronizado com backend)
const TODAS_INSIGNIAS = [
  // === Performance ===
  {
    id: 'atleta_elite',
    nome: 'Atleta Elite',
    icone: 'star',
    cor_primaria: '#FFD700',
    cor_secundaria: '#FFA500',
    categoria: 'performance',
    descricao: 'Conquistou 100+ pontos no ranking',
    como_conquistar: 'Acumule 100 pontos ou mais no ranking geral'
  },
  {
    id: 'corredor_maratona',
    nome: 'Corredor de Maratona',
    icone: 'medal',
    cor_primaria: '#8B5CF6',
    cor_secundaria: '#6D28D9',
    categoria: 'performance',
    descricao: 'Completou uma prova de 42km',
    como_conquistar: 'Registre uma corrida de 42km ou mais no sistema'
  },
  {
    id: 'top_10_mes',
    nome: 'Top 10 do Mes',
    icone: 'trophy',
    cor_primaria: '#10B981',
    cor_secundaria: '#059669',
    categoria: 'performance',
    descricao: 'Ficou entre os 10 melhores do mes na sua modalidade',
    como_conquistar: 'Fique entre os 10 primeiros do ranking mensal da sua modalidade'
  },
  {
    id: 'podio',
    nome: 'Podio',
    icone: 'award',
    cor_primaria: '#F59E0B',
    cor_secundaria: '#D97706',
    categoria: 'performance',
    descricao: 'Conquistou 1, 2 ou 3 lugar em uma corrida',
    como_conquistar: 'Fique entre os 3 primeiros na sua categoria em qualquer corrida aprovada'
  },
  {
    id: 'rei_velocidade',
    nome: 'Rei da Velocidade',
    icone: 'zap',
    cor_primaria: '#EF4444',
    cor_secundaria: '#DC2626',
    categoria: 'performance',
    descricao: 'Maior pontuacao semanal na sua modalidade',
    como_conquistar: 'Tenha a maior pontuacao na semana dentro da sua modalidade'
  },
  // === Participacao ===
  {
    id: 'iniciante',
    nome: 'Iniciante',
    icone: 'play',
    cor_primaria: '#06B6D4',
    cor_secundaria: '#0891B2',
    categoria: 'participacao',
    descricao: 'Primeira corrida registrada',
    como_conquistar: 'Registre sua primeira corrida na plataforma'
  },
  {
    id: 'veterano',
    nome: 'Veterano',
    icone: 'shield',
    cor_primaria: '#3B82F6',
    cor_secundaria: '#2563EB',
    categoria: 'participacao',
    descricao: 'Completou 10+ corridas',
    como_conquistar: 'Participe e complete 10 corridas registradas no ranking'
  },
  {
    id: 'maratonista',
    nome: 'Maratonista',
    icone: 'target',
    cor_primaria: '#8B5CF6',
    cor_secundaria: '#7C3AED',
    categoria: 'participacao',
    descricao: 'Completou 20+ corridas',
    como_conquistar: 'Participe e complete 20 corridas registradas no ranking'
  },
  {
    id: 'lenda',
    nome: 'Lenda',
    icone: 'crown',
    cor_primaria: '#FFD700',
    cor_secundaria: '#FFC000',
    categoria: 'participacao',
    descricao: 'Completou 50+ corridas',
    como_conquistar: 'Participe e complete 50 corridas registradas no ranking'
  },
  {
    id: 'consistente',
    nome: 'Consistente',
    icone: 'calendar',
    cor_primaria: '#14B8A6',
    cor_secundaria: '#0D9488',
    categoria: 'participacao',
    descricao: 'Participou de corridas em 6 meses consecutivos',
    como_conquistar: 'Participe de pelo menos uma corrida em 6 meses distintos'
  },
  // === Especiais ===
  {
    id: 'embaixador_run',
    nome: 'Embaixador Run',
    icone: 'users',
    cor_primaria: '#EC4899',
    cor_secundaria: '#DB2777',
    categoria: 'especial',
    descricao: 'Indicou 5+ atletas para a plataforma',
    como_conquistar: 'Indique 5 atletas que se cadastrem na plataforma'
  },
  {
    id: 'indicador_bronze',
    nome: 'Indicador Bronze',
    icone: 'award',
    cor_primaria: '#CD7F32',
    cor_secundaria: '#B87333',
    categoria: 'especial',
    descricao: 'Indicou 10+ atletas para a plataforma',
    como_conquistar: 'Indique 10 atletas que se cadastrem na plataforma'
  },
  {
    id: 'indicador_prata',
    nome: 'Indicador Prata',
    icone: 'medal',
    cor_primaria: '#C0C0C0',
    cor_secundaria: '#A8A8A8',
    categoria: 'especial',
    descricao: 'Indicou 20+ atletas para a plataforma',
    como_conquistar: 'Indique 20 atletas que se cadastrem na plataforma'
  },
  {
    id: 'indicador_ouro',
    nome: 'Indicador Ouro',
    icone: 'trophy',
    cor_primaria: '#FFD700',
    cor_secundaria: '#FFC000',
    categoria: 'especial',
    descricao: 'Indicou 30+ atletas para a plataforma',
    como_conquistar: 'Indique 30 atletas que se cadastrem na plataforma'
  },
  {
    id: 'indicador_diamante',
    nome: 'Indicador Diamante',
    icone: 'sparkles',
    cor_primaria: '#B9F2FF',
    cor_secundaria: '#00CED1',
    categoria: 'especial',
    descricao: 'Indicou 50+ atletas para a plataforma',
    como_conquistar: 'Indique 50 atletas que se cadastrem na plataforma'
  },
  {
    id: 'influencer',
    nome: 'Influencer',
    icone: 'eye',
    cor_primaria: '#F472B6',
    cor_secundaria: '#EC4899',
    categoria: 'especial',
    descricao: 'Perfil mais visualizado do mes',
    como_conquistar: 'Tenha o perfil mais visualizado do mes na plataforma'
  },
  {
    id: 'estrela_assessoria',
    nome: 'Estrela da Assessoria',
    icone: 'sparkles',
    cor_primaria: '#FBBF24',
    cor_secundaria: '#F59E0B',
    categoria: 'especial',
    descricao: 'Maior pontuacao da equipe',
    como_conquistar: 'Seja o atleta com maior pontuacao dentro da sua assessoria'
  }
];

// Componente de Modal de Ajuda das Insígnias - com badges 3D
const InsigniasHelpModal = ({ open, onOpenChange }) => {
  const categorias = [
    { key: 'performance', label: 'Performance', cor: '#10B981' },
    { key: 'participacao', label: 'Participacao', cor: '#3B82F6' },
    { key: 'especial', label: 'Especiais', cor: '#EC4899' }
  ];
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Trophy className="w-6 h-6 text-amber-500" />
            Guia de Insignias & Conquistas
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6 mt-4">
          <p className="text-slate-600 dark:text-slate-400 text-sm">
            As insignias sao conquistas especiais que voce pode ganhar ao participar de corridas e atingir marcos importantes.
            Cada insignia representa uma conquista unica na sua jornada como atleta!
          </p>
          
          {categorias.map(cat => {
            const insigniasCat = TODAS_INSIGNIAS.filter(i => i.categoria === cat.key);
            return (
              <div key={cat.key}>
                <h3 className="font-bold text-base mb-3 flex items-center gap-2" style={{ color: cat.cor }}>
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: cat.cor }} />
                  {cat.label} ({insigniasCat.length})
                </h3>
                <div className="grid gap-3">
                  {insigniasCat.map((insignia) => {
                    const IconComp = ICON_MAP[insignia.icone] || Star;
                    return (
                      <div 
                        key={insignia.id}
                        className="flex items-start gap-4 p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                      >
                        {/* Badge 3D */}
                        <div className="relative flex-shrink-0">
                          <div 
                            className="w-14 h-14 rounded-full flex items-center justify-center shadow-lg"
                            style={{
                              background: `linear-gradient(135deg, ${insignia.cor_primaria}, ${insignia.cor_secundaria})`
                            }}
                          >
                            {/* Anel externo */}
                            <div 
                              className="absolute inset-0 rounded-full"
                              style={{
                                border: `2px solid ${insignia.cor_primaria}40`,
                                transform: 'scale(1.15)'
                              }}
                            />
                            {/* Brilho */}
                            <div 
                              className="absolute top-1 left-1/4 w-1/3 h-1/4 rounded-full opacity-40"
                              style={{ background: 'linear-gradient(to bottom, white, transparent)' }}
                            />
                            <IconComp className="w-7 h-7 text-white" strokeWidth={2} />
                          </div>
                        </div>
                        
                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <h4 className="font-bold text-slate-800 dark:text-white">{insignia.nome}</h4>
                          </div>
                          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{insignia.descricao}</p>
                          <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-2 flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            <strong>Como conquistar:</strong> {insignia.como_conquistar}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
          
          <div className="mt-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl border border-emerald-200 dark:border-emerald-800">
            <h4 className="font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
              <Star className="w-4 h-4" />
              Dica
            </h4>
            <p className="text-sm text-emerald-600 dark:text-emerald-300 mt-1">
              Continue participando de corridas e registrando seus resultados para desbloquear mais insignias. 
              Cada conquista te aproxima do status de Atleta Elite!
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Componente individual de badge
const BadgeItem = ({ badge, size = 'md', showTooltip = true }) => {
  const IconComponent = ICON_MAP[badge.icone] || Star;
  
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-14 h-14',
    lg: 'w-20 h-20'
  };
  
  const iconSizes = {
    sm: 'w-5 h-5',
    md: 'w-7 h-7',
    lg: 'w-10 h-10'
  };
  
  const badgeContent = (
    <div 
      className={`relative ${sizeClasses[size]} rounded-full flex items-center justify-center transition-all duration-300 ${
        badge.conquistado 
          ? 'cursor-pointer hover:scale-110 shadow-lg hover:shadow-xl' 
          : 'opacity-40 grayscale cursor-not-allowed'
      }`}
      style={{
        background: badge.conquistado 
          ? `linear-gradient(135deg, ${badge.cor_primaria}, ${badge.cor_secundaria})` 
          : '#94a3b8'
      }}
    >
      {/* Anel externo decorativo */}
      <div 
        className="absolute inset-0 rounded-full"
        style={{
          border: badge.conquistado ? `2px solid ${badge.cor_primaria}40` : '2px solid #94a3b840',
          transform: 'scale(1.15)'
        }}
      />
      
      {/* Brilho interno */}
      {badge.conquistado && (
        <div 
          className="absolute top-1 left-1/4 w-1/3 h-1/4 rounded-full opacity-40"
          style={{ background: 'linear-gradient(to bottom, white, transparent)' }}
        />
      )}
      
      {/* Ícone */}
      <IconComponent 
        className={`${iconSizes[size]} ${badge.conquistado ? 'text-white' : 'text-slate-400'}`}
        strokeWidth={2}
      />
      
      {/* Indicador de não conquistado */}
      {!badge.conquistado && (
        <div className="absolute -bottom-1 -right-1 bg-slate-500 rounded-full p-0.5">
          <Lock className="w-3 h-3 text-white" />
        </div>
      )}
      
      {/* Indicador de conquistado */}
      {badge.conquistado && (
        <div 
          className="absolute -bottom-1 -right-1 rounded-full p-0.5"
          style={{ background: badge.cor_primaria }}
        >
          <Check className="w-3 h-3 text-white" />
        </div>
      )}
    </div>
  );
  
  if (!showTooltip) return badgeContent;
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          {badgeContent}
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs">
          <div className="text-center">
            <p className="font-bold">{badge.nome}</p>
            <p className="text-xs text-slate-400">{badge.descricao}</p>
            {badge.data_conquista && (
              <p className="text-xs text-emerald-400 mt-1">
                Conquistado em {new Date(badge.data_conquista).toLocaleDateString('pt-BR')}
              </p>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// Componente de Card de Compartilhamento - Formato 9:16 (Stories)
const ShareCard = ({ atletaId, atleta, stats, badges, fotoUrl, onClose }) => {
  const [shareImageUrl, setShareImageUrl] = useState(null);
  const [generatingImage, setGeneratingImage] = useState(false);
  const [fotoError, setFotoError] = useState(false);
  const shareCardRef = useRef(null);
  
  // Gerar imagem ao abrir
  useEffect(() => {
    const timer = setTimeout(() => generateShareImage(), 300);
    return () => clearTimeout(timer);
  }, []);
  
  const generateShareImage = async () => {
    setGeneratingImage(true);
    try {
      const element = shareCardRef.current;
      if (!element) return;
      
      // Pre-carregar foto
      if (fotoUrl) {
        try {
          const img = new window.Image();
          img.crossOrigin = 'anonymous';
          img.src = fotoUrl;
          await new Promise((resolve) => {
            img.onload = resolve;
            img.onerror = resolve;
            setTimeout(resolve, 3000);
          });
        } catch {}
      }
      
      const canvas = await html2canvas(element, {
        scale: 3,
        backgroundColor: '#0f172a',
        useCORS: true,
        allowTaint: true,
        logging: false
      });
      
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      const url = URL.createObjectURL(blob);
      setShareImageUrl(url);
    } catch (err) {
      console.error('Erro ao gerar imagem:', err);
    } finally {
      setGeneratingImage(false);
    }
  };
  
  const downloadImage = () => {
    if (!shareImageUrl) return;
    const link = document.createElement('a');
    link.href = shareImageUrl;
    link.download = `insignias-${atleta.nome?.replace(/\s+/g, '-')}.png`;
    link.click();
    toast.success('Imagem baixada!');
  };
  
  const shareToWhatsApp = () => {
    const texto = encodeURIComponent(`Confira minhas insignias no Ranking Run Pro!\n\n${atleta.nome}\n${badges.length} insignias | ${stats.pontos} pontos | ${stats.total_corridas} corridas\n\nhttps://geo-filtered-admin.preview.emergentagent.com/atleta/${atletaId}`);
    window.open(`https://wa.me/?text=${texto}`, '_blank');
  };
  
  const shareToInstagram = () => {
    if (shareImageUrl) {
      downloadImage();
      toast.success('Imagem baixada! Abra o Instagram e poste nos Stories');
    }
  };
  
  const shareToFacebook = () => {
    const url = encodeURIComponent(`https://geo-filtered-admin.preview.emergentagent.com/atleta/${atletaId}`);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
  };
  
  return (
    <div className="space-y-4">
      {/* Preview da imagem */}
      <div className="relative">
        {generatingImage && (
          <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center rounded-lg z-10">
            <p className="text-white">Gerando imagem...</p>
          </div>
        )}
        
        {/* Card 9:16 para gerar imagem */}
        <div 
          ref={shareCardRef}
          className="bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 rounded-lg p-6 text-white"
          style={{ aspectRatio: '9/16', maxHeight: '420px' }}
          data-testid="share-insignias-card"
        >
          <div className="h-full flex flex-col justify-between">
            {/* Header */}
            <div className="text-center">
              <p className="text-emerald-400 text-sm font-semibold mb-1">RANKING RUN PRO 2026</p>
              <div className="w-16 h-1 bg-emerald-500 mx-auto rounded-full" />
            </div>
            
            {/* Atleta Info */}
            <div className="text-center flex-1 flex flex-col justify-center">
              {/* Foto do Atleta */}
              <div className="w-20 h-20 mx-auto mb-3 rounded-full ring-4 ring-amber-500 overflow-hidden bg-amber-600 flex items-center justify-center">
                {fotoUrl && !fotoError ? (
                  <img
                    src={fotoUrl}
                    alt={atleta.nome}
                    crossOrigin="anonymous"
                    className="w-full h-full object-cover"
                    onError={() => setFotoError(true)}
                  />
                ) : (
                  <span className="text-white text-xl font-bold flex items-center justify-center w-full h-full">
                    {atleta.nome?.charAt(0)}
                  </span>
                )}
              </div>
              
              <h2 className="text-lg font-bold mb-0.5">{atleta.nome}</h2>
              <p className="text-emerald-300 text-xs mb-3">{atleta.equipe}</p>
              
              {/* Stats */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="bg-slate-800/50 rounded-lg p-2">
                  <p className="text-xl font-bold text-amber-400">{stats.pontos}</p>
                  <p className="text-[10px] text-slate-400">Pontos</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-2">
                  <p className="text-xl font-bold text-blue-400">{stats.total_corridas}</p>
                  <p className="text-[10px] text-slate-400">Corridas</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-2">
                  <p className="text-xl font-bold text-emerald-400">{badges.length}</p>
                  <p className="text-[10px] text-slate-400">Insignias</p>
                </div>
              </div>
              
              {/* Titulo Insignias */}
              <div className="flex items-center justify-center gap-1 mb-2">
                <Trophy className="w-4 h-4 text-amber-400" />
                <p className="text-amber-400 text-xs font-semibold">MINHAS INSIGNIAS</p>
              </div>
              
              {/* Badges Grid */}
              <div className="flex flex-wrap gap-2 justify-center">
                {badges.slice(0, 8).map(badge => (
                  <BadgeItem key={badge.id} badge={badge} size="sm" showTooltip={false} />
                ))}
              </div>
              {badges.length > 8 && (
                <p className="text-slate-400 text-[10px] mt-1">+{badges.length - 8} mais</p>
              )}
            </div>
            
            {/* Footer */}
            <div className="text-center">
              <p className="text-xs text-slate-400">ranking-run-pro.com</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Botoes de Compartilhamento */}
      <div className="grid grid-cols-2 gap-3">
        <Button
          onClick={shareToWhatsApp}
          className="bg-green-600 hover:bg-green-700"
          data-testid="share-insignias-whatsapp"
        >
          <Share2 className="w-4 h-4 mr-2" />
          WhatsApp
        </Button>
        <Button
          onClick={shareToInstagram}
          className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          data-testid="share-insignias-instagram"
        >
          <Share2 className="w-4 h-4 mr-2" />
          Instagram
        </Button>
        <Button
          onClick={shareToFacebook}
          className="bg-blue-600 hover:bg-blue-700"
          data-testid="share-insignias-facebook"
        >
          <Share2 className="w-4 h-4 mr-2" />
          Facebook
        </Button>
        <Button
          onClick={downloadImage}
          disabled={!shareImageUrl}
          variant="outline"
          data-testid="share-insignias-download"
        >
          <Download className="w-4 h-4 mr-2" />
          Baixar
        </Button>
      </div>
    </div>
  );
};

// Componente principal
export const BadgesDisplay = ({ atletaId, showTitle = true, compact = false }) => {
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [atletaData, setAtletaData] = useState(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  
  useEffect(() => {
    if (atletaId) {
      fetchBadges();
    }
  }, [atletaId]);
  
  const fetchBadges = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/badges/atleta/${atletaId}`);
      setBadges(response.data.badges || []);
      setAtletaData({
        nome: response.data.atleta_nome,
        equipe: response.data.equipe || '',
        foto_url: response.data.foto_url || '',
        pontos: response.data.pontos_totais,
        total_corridas: response.data.total_corridas || 0,
        total_badges: response.data.badges_conquistados
      });
    } catch (error) {
      console.error('Erro ao buscar badges:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const badgesConquistados = badges.filter(b => b.conquistado);
  const badgesNaoConquistados = badges.filter(b => !b.conquistado);
  
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500" />
      </div>
    );
  }
  
  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {badgesConquistados.slice(0, 5).map(badge => (
          <BadgeItem key={badge.id} badge={badge} size="sm" />
        ))}
        {badgesConquistados.length > 5 && (
          <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">
            +{badgesConquistados.length - 5}
          </div>
        )}
      </div>
    );
  }
  
  return (
    <Card className="border-slate-200 dark:border-slate-800 shadow-lg">
      {showTitle && (
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500" />
              Insígnias & Conquistas
              <Badge variant="outline" className="ml-2">
                {badgesConquistados.length}/{badges.length}
              </Badge>
              {/* Botão de Ajuda */}
              <Button 
                variant="ghost" 
                size="sm" 
                className="ml-1 p-1 h-7 w-7 rounded-full hover:bg-amber-100 dark:hover:bg-amber-900/30"
                onClick={() => setShowHelpModal(true)}
              >
                <HelpCircle className="w-4 h-4 text-amber-500" />
              </Button>
            </CardTitle>
            
            {badgesConquistados.length > 0 && (
              <Dialog open={showShareModal} onOpenChange={setShowShareModal}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Share2 className="w-4 h-4 mr-2" />
                    Compartilhar
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Compartilhar Insígnias</DialogTitle>
                  </DialogHeader>
                  <ShareCard 
                    atletaId={atletaId}
                    atleta={{ nome: atletaData?.nome, equipe: atletaData?.equipe || '' }}
                    stats={{ pontos: atletaData?.pontos || 0, total_corridas: atletaData?.total_corridas || 0 }}
                    badges={badgesConquistados}
                    fotoUrl={atletaData?.foto_url || ''}
                    onClose={() => setShowShareModal(false)}
                  />
                </DialogContent>
              </Dialog>
            )}
          </div>
        </CardHeader>
      )}
      
      {/* Modal de Ajuda */}
      <InsigniasHelpModal open={showHelpModal} onOpenChange={setShowHelpModal} />
      
      <CardContent className="space-y-4">
        {/* Badges Conquistados */}
        {badgesConquistados.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-600 dark:text-slate-400 mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-500" />
              Conquistados ({badgesConquistados.length})
            </h4>
            <div className="flex flex-wrap gap-3">
              {badgesConquistados.map(badge => (
                <BadgeItem key={badge.id} badge={badge} size="md" />
              ))}
            </div>
          </div>
        )}
        
        {/* Badges Não Conquistados */}
        {badgesNaoConquistados.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-400 mb-3 flex items-center gap-2">
              <Lock className="w-4 h-4" />
              A Conquistar ({badgesNaoConquistados.length})
            </h4>
            <div className="flex flex-wrap gap-3">
              {badgesNaoConquistados.map(badge => (
                <BadgeItem key={badge.id} badge={badge} size="md" />
              ))}
            </div>
          </div>
        )}
        
        {/* Mensagem se não há badges */}
        {badges.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            <Trophy className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p>Nenhum badge disponível ainda.</p>
            <p className="text-sm">Continue participando para conquistar badges!</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Componente mini para exibir badges no ranking/tabela
export const BadgesMini = ({ atletaId }) => {
  const [badges, setBadges] = useState([]);
  
  useEffect(() => {
    const fetchBadges = async () => {
      try {
        const response = await axios.get(`${API}/badges/atleta/${atletaId}`);
        setBadges((response.data.badges || []).filter(b => b.conquistado).slice(0, 3));
      } catch (error) {
        console.error('Erro ao buscar badges:', error);
      }
    };
    
    if (atletaId) {
      fetchBadges();
    }
  }, [atletaId]);
  
  if (badges.length === 0) return null;
  
  return (
    <div className="flex gap-1">
      {badges.map(badge => {
        const IconComponent = ICON_MAP[badge.icone] || Star;
        return (
          <TooltipProvider key={badge.id}>
            <Tooltip>
              <TooltipTrigger asChild>
                <div 
                  className="w-5 h-5 rounded-full flex items-center justify-center"
                  style={{ background: `linear-gradient(135deg, ${badge.cor_primaria}, ${badge.cor_secundaria})` }}
                >
                  <IconComponent className="w-3 h-3 text-white" />
                </div>
              </TooltipTrigger>
              <TooltipContent side="top">
                <p className="text-xs font-medium">{badge.nome}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        );
      })}
    </div>
  );
};

export default BadgesDisplay;
