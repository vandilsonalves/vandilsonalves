// /app/frontend/src/components/BadgesDisplay.jsx
// Componente de exibição de badges visuais

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { 
  Star, Medal, Trophy, Award, Zap, Play, Shield, Target, Crown, 
  Calendar, Users, Eye, Sparkles, Share2, Download, Check, Lock, HelpCircle
} from 'lucide-react';
import { toast } from 'sonner';

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
  sparkles: Sparkles
};

// Definição completa de todas as insígnias do sistema com explicações
const TODAS_INSIGNIAS = [
  {
    id: 'primeiro_lugar',
    nome: 'Campeão',
    emoji: '🥇',
    cor: '#FFD700',
    descricao: 'Conquistou o 1º lugar em uma corrida oficial',
    como_conquistar: 'Fique em 1º lugar na sua categoria em qualquer corrida aprovada',
    pontos_bonus: 5
  },
  {
    id: 'podio',
    nome: 'Pódio',
    emoji: '🏆',
    cor: '#F59E0B',
    descricao: 'Subiu ao pódio (top 3) em uma corrida',
    como_conquistar: 'Fique entre os 3 primeiros lugares na sua categoria',
    pontos_bonus: 2
  },
  {
    id: '10_corridas',
    nome: 'Veterano',
    emoji: '🏃',
    cor: '#10B981',
    descricao: 'Completou 10 corridas',
    como_conquistar: 'Participe e complete 10 corridas registradas no ranking',
    pontos_bonus: 10
  },
  {
    id: '12_resultados',
    nome: 'Atleta Bronze',
    emoji: '🥉',
    cor: '#CD7F32',
    descricao: 'Lançou 12 resultados no ranking',
    como_conquistar: 'Registre 12 resultados de corridas aprovados no sistema',
    pontos_bonus: 12
  },
  {
    id: '20_resultados',
    nome: 'Atleta Prata',
    emoji: '🥈',
    cor: '#C0C0C0',
    descricao: 'Lançou 20 resultados no ranking',
    como_conquistar: 'Registre 20 resultados de corridas aprovados no sistema',
    pontos_bonus: 20
  },
  {
    id: '30_resultados',
    nome: 'Atleta Ouro',
    emoji: '🥇',
    cor: '#FFD700',
    descricao: 'Lançou 30 resultados no ranking',
    como_conquistar: 'Registre 30 resultados de corridas aprovados no sistema',
    pontos_bonus: 30
  },
  {
    id: 'elite',
    nome: 'Atleta Elite',
    emoji: '⭐',
    cor: '#FFD700',
    descricao: 'Alcançou 100 pontos no ranking',
    como_conquistar: 'Acumule 100 pontos ou mais no ranking geral',
    pontos_bonus: 20
  },
  {
    id: 'maratonista',
    nome: 'Maratonista',
    emoji: '🎯',
    cor: '#8B5CF6',
    descricao: 'Completou uma maratona (42KM)',
    como_conquistar: 'Complete uma corrida de 42KM ou mais',
    pontos_bonus: 15
  },
  {
    id: 'consistente',
    nome: 'Consistente',
    emoji: '📅',
    cor: '#3B82F6',
    descricao: 'Completou corridas em 6 meses diferentes',
    como_conquistar: 'Participe de pelo menos uma corrida em 6 meses distintos',
    pontos_bonus: 10
  },
  {
    id: 'embaixador',
    nome: 'Embaixador Run',
    emoji: '🎖️',
    cor: '#EC4899',
    descricao: 'Embaixador oficial do Ranking Run',
    como_conquistar: 'Seja selecionado como embaixador oficial da plataforma',
    pontos_bonus: 25
  }
];

// Componente de Modal de Ajuda das Insígnias
const InsigniasHelpModal = ({ open, onOpenChange }) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Trophy className="w-6 h-6 text-amber-500" />
            Guia de Insígnias & Conquistas
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4 mt-4">
          <p className="text-slate-600 dark:text-slate-400 text-sm">
            As insígnias são conquistas especiais que você pode ganhar ao participar de corridas e atingir marcos importantes. 
            Cada insígnia concede pontos bônus ao ser conquistada!
          </p>
          
          <div className="grid gap-3">
            {TODAS_INSIGNIAS.map((insignia) => (
              <div 
                key={insignia.id}
                className="flex items-start gap-4 p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
              >
                {/* Badge visual */}
                <div 
                  className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg"
                  style={{ background: `linear-gradient(135deg, ${insignia.cor}, ${insignia.cor}dd)` }}
                >
                  <span className="text-2xl">{insignia.emoji}</span>
                </div>
                
                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-bold text-slate-800 dark:text-white">{insignia.nome}</h3>
                    <Badge className="text-xs" style={{ backgroundColor: `${insignia.cor}20`, color: insignia.cor }}>
                      +{insignia.pontos_bonus} pts
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{insignia.descricao}</p>
                  <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-2 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    <strong>Como conquistar:</strong> {insignia.como_conquistar}
                  </p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl border border-emerald-200 dark:border-emerald-800">
            <h4 className="font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
              <Star className="w-4 h-4" />
              Dica
            </h4>
            <p className="text-sm text-emerald-600 dark:text-emerald-300 mt-1">
              Continue participando de corridas e registrando seus resultados para desbloquear mais insígnias. 
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

// Componente de Card de Compartilhamento
const ShareCard = ({ atletaId, atleta, stats, badges, onClose }) => {
  const [copying, setCopying] = useState(false);
  
  const handleCopyText = async () => {
    const texto = `🏆 Minhas Insígnias no Ranking Run Pró!\n\n👤 ${atleta.nome}\n🎯 ${badges.length} insígnias conquistadas\n⭐ ${stats.pontos} pontos | ${stats.total_corridas} corridas\n\n🏅 Insígnias:\n${badges.slice(0, 5).map(b => `• ${b.nome}`).join('\n')}\n\n#RankingRunPro #Corrida #Running`;
    
    try {
      await navigator.clipboard.writeText(texto);
      setCopying(true);
      toast.success('Texto copiado!');
      setTimeout(() => setCopying(false), 2000);
    } catch {
      toast.error('Erro ao copiar');
    }
  };
  
  const handleShareWhatsApp = () => {
    const texto = encodeURIComponent(`🏆 Confira minhas insígnias no Ranking Run Pró!\n\n👤 ${atleta.nome}\n🎯 ${badges.length} insígnias\n⭐ ${stats.pontos} pontos\n\nhttps://geo-filtered-admin.preview.emergentagent.com/atleta/${atletaId}`);
    window.open(`https://wa.me/?text=${texto}`, '_blank');
  };
  
  const handleShareTwitter = () => {
    const texto = encodeURIComponent(`🏆 Conquistei ${badges.length} insígnias no @RankingRunPro! ${stats.pontos} pontos e ${stats.total_corridas} corridas! #RankingRunPro #Corrida`);
    window.open(`https://twitter.com/intent/tweet?text=${texto}`, '_blank');
  };
  
  return (
    <div className="space-y-4">
      {/* Card Visual */}
      <div 
        className="relative rounded-2xl overflow-hidden p-6"
        style={{
          background: 'linear-gradient(135deg, #10B981 0%, #059669 50%, #047857 100%)'
        }}
      >
        {/* Padrão decorativo */}
        <div className="absolute top-0 right-0 w-64 h-64 opacity-10">
          <div className="absolute inset-0" style={{
            background: 'radial-gradient(circle at center, white 1px, transparent 1px)',
            backgroundSize: '20px 20px'
          }} />
        </div>
        
        {/* Conteúdo */}
        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
              <span className="text-2xl font-bold text-white">
                {atleta.nome?.charAt(0)}
              </span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">{atleta.nome}</h3>
              <p className="text-emerald-100 text-sm">{atleta.equipe}</p>
            </div>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center bg-white/10 rounded-xl p-3">
              <p className="text-2xl font-bold text-white">{stats.pontos}</p>
              <p className="text-xs text-emerald-100">Pontos</p>
            </div>
            <div className="text-center bg-white/10 rounded-xl p-3">
              <p className="text-2xl font-bold text-white">{stats.total_corridas}</p>
              <p className="text-xs text-emerald-100">Corridas</p>
            </div>
            <div className="text-center bg-white/10 rounded-xl p-3">
              <p className="text-2xl font-bold text-white">{badges.length}</p>
              <p className="text-xs text-emerald-100">Insígnias</p>
            </div>
          </div>
          
          {/* Badges */}
          <div className="flex flex-wrap gap-2 justify-center">
            {badges.slice(0, 6).map(badge => (
              <BadgeItem key={badge.id} badge={badge} size="sm" showTooltip={false} />
            ))}
          </div>
          
          {/* Footer */}
          <div className="mt-4 text-center">
            <p className="text-emerald-100 text-xs">rankingrunpro.com.br</p>
          </div>
        </div>
      </div>
      
      {/* Botões de compartilhamento */}
      <div className="flex flex-wrap gap-2 justify-center">
        <Button onClick={handleShareWhatsApp} className="bg-green-600 hover:bg-green-700">
          <Share2 className="w-4 h-4 mr-2" />
          WhatsApp
        </Button>
        <Button onClick={handleShareTwitter} variant="outline" className="border-blue-500 text-blue-500">
          <Share2 className="w-4 h-4 mr-2" />
          Twitter
        </Button>
        <Button onClick={handleCopyText} variant="outline">
          {copying ? <Check className="w-4 h-4 mr-2" /> : <Download className="w-4 h-4 mr-2" />}
          {copying ? 'Copiado!' : 'Copiar Texto'}
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
