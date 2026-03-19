// /app/frontend/src/components/admin/InsigniasStatsCard.jsx
// Componente que mostra estatísticas de insígnias com visual de badges

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { 
  Star, Medal, Trophy, Award, Zap, Shield, Target, Crown, 
  Calendar, Users, Flame, Flag, Heart, Clock
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mapeamento de ícones por código de insígnia
const BADGE_ICONS = {
  elite: Star,
  maratonista: Target,
  primeiro_lugar: Trophy,
  podio: Medal,
  '10_corridas': Flame,
  '12_resultados': Award,
  '20_resultados': Award,
  '30_resultados': Crown,
  consistente: Calendar,
  embaixador: Flag,
  iniciante: Heart,
  veterano: Shield
};

// Cores para cada insígnia
const BADGE_COLORS = {
  elite: { primary: '#FFD700', secondary: '#FFA500' },
  maratonista: { primary: '#8B5CF6', secondary: '#6D28D9' },
  primeiro_lugar: { primary: '#FFD700', secondary: '#F59E0B' },
  podio: { primary: '#F59E0B', secondary: '#D97706' },
  '10_corridas': { primary: '#10B981', secondary: '#059669' },
  '12_resultados': { primary: '#CD7F32', secondary: '#A0522D' },
  '20_resultados': { primary: '#C0C0C0', secondary: '#A8A8A8' },
  '30_resultados': { primary: '#FFD700', secondary: '#DAA520' },
  consistente: { primary: '#3B82F6', secondary: '#2563EB' },
  embaixador: { primary: '#EC4899', secondary: '#DB2777' },
  iniciante: { primary: '#F472B6', secondary: '#EC4899' },
  veterano: { primary: '#10B981', secondary: '#047857' }
};

// Componente individual de badge com contador
const BadgeWithCount = ({ badge }) => {
  const IconComponent = BADGE_ICONS[badge.codigo] || Star;
  const colors = BADGE_COLORS[badge.codigo] || { primary: '#6B7280', secondary: '#4B5563' };
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex flex-col items-center gap-1 cursor-pointer group">
            {/* Badge visual */}
            <div 
              className="relative w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 hover:scale-110 shadow-lg hover:shadow-xl"
              style={{
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`
              }}
            >
              {/* Anel externo */}
              <div 
                className="absolute inset-0 rounded-full"
                style={{
                  border: `3px solid ${colors.primary}40`,
                  transform: 'scale(1.15)'
                }}
              />
              
              {/* Brilho interno */}
              <div 
                className="absolute top-1 left-1/4 w-1/3 h-1/4 rounded-full opacity-40"
                style={{ background: 'linear-gradient(to bottom, white, transparent)' }}
              />
              
              {/* Ícone */}
              <IconComponent className="w-8 h-8 text-white" strokeWidth={2} />
              
              {/* Contador no canto */}
              <div 
                className="absolute -bottom-1 -right-1 min-w-[24px] h-6 px-1 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-md"
                style={{ background: colors.secondary }}
              >
                {badge.total}
              </div>
            </div>
            
            {/* Nome da insígnia */}
            <span className="text-xs text-slate-600 dark:text-slate-400 text-center font-medium max-w-[70px] truncate group-hover:text-slate-800 dark:group-hover:text-slate-200">
              {badge.nome}
            </span>
          </div>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs">
          <div className="text-center">
            <p className="font-bold text-lg">{badge.icone} {badge.nome}</p>
            <p className="text-2xl font-bold text-emerald-500">{badge.total}</p>
            <p className="text-sm text-slate-400">atletas conquistaram</p>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// Componente principal
const InsigniasStatsCard = ({ token }) => {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/admin/stats/insignias`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(response.data);
      } catch (error) {
        console.error('Erro ao carregar estatísticas de insígnias:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (token) {
      fetchStats();
    }
  }, [token]);

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </CardContent>
      </Card>
    );
  }

  const totalConquistas = stats.reduce((acc, s) => acc + s.total, 0);
  const insigniasComAtletas = stats.filter(s => s.total > 0);
  const insigniasSemAtletas = stats.filter(s => s.total === 0);

  return (
    <Card className="border-purple-200 dark:border-purple-800">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Trophy className="w-5 h-5 text-purple-500" />
            Insígnias & Conquistas
            <Badge variant="outline" className="ml-2 bg-purple-50">
              {totalConquistas} conquistadas
            </Badge>
          </CardTitle>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Insígnias com atletas */}
        {insigniasComAtletas.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-purple-600 dark:text-purple-400 mb-4 flex items-center gap-2">
              <Star className="w-4 h-4" />
              Conquistadas ({insigniasComAtletas.length} tipos)
            </h4>
            <div className="flex flex-wrap gap-4 justify-start">
              {insigniasComAtletas.map(badge => (
                <BadgeWithCount key={badge.codigo} badge={badge} />
              ))}
            </div>
          </div>
        )}
        
        {/* Insígnias sem atletas */}
        {insigniasSemAtletas.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-400 mb-4 flex items-center gap-2">
              Sem atletas ainda ({insigniasSemAtletas.length})
            </h4>
            <div className="flex flex-wrap gap-4 justify-start opacity-50">
              {insigniasSemAtletas.map(badge => (
                <BadgeWithCount key={badge.codigo} badge={badge} />
              ))}
            </div>
          </div>
        )}

        {/* Resumo em números */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
          {stats.slice(0, 4).map((item, idx) => (
            <div key={idx} className="text-center p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <p className="text-2xl">{item.icone}</p>
              <p className="text-xl font-bold" style={{ color: BADGE_COLORS[item.codigo]?.primary || '#6B7280' }}>
                {item.total}
              </p>
              <p className="text-xs text-slate-500 truncate">{item.nome}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default InsigniasStatsCard;
