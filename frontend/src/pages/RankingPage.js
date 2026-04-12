import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import NotificacoesBell from '@/components/NotificacoesBell';
import MobileNav from '@/components/MobileNav';
import { LogIn, Upload, Shield, LogOut, User, Trophy, Flame, Users, MessageSquare, HelpCircle, Award, Star, Activity, History, MapPin, RefreshCw, Zap, CreditCard, UsersRound, Handshake, Medal } from 'lucide-react';
import { RegulamentoButton } from '@/components/RegulamentoModal';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useFeedNaoLidos } from '@/hooks/useFeedNaoLidos';
import RankingProfissional from '@/components/ranking/RankingProfissional';
import RankingGalera from '@/components/ranking/RankingGalera';
import RankingEquipes from '@/components/ranking/RankingEquipes';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const RankingPage = () => {
  const navigate = useNavigate();
  const { user, token, isAdmin, logout } = useAuth();
  const [tipoRanking, setTipoRanking] = useState('profissional');
  const hasEquipe = user?.equipe && !['Individual', 'individual', 'SEM EQUIPE', ''].includes(user.equipe);
  const { naoLidos } = useFeedNaoLidos(token, user?.equipe);
  const [votacaoAberta, setVotacaoAberta] = useState(false);
  const [votacaoTitulo, setVotacaoTitulo] = useState('');

  useEffect(() => {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    axios.get(`${BACKEND_URL}/api/premiacao/status`, { headers })
      .then(res => {
        const aberta = res.data?.votacao_aberta || false;
        const jaFinalizou = res.data?.todas_finalizadas || false;
        setVotacaoAberta(aberta && !jaFinalizou);
        setVotacaoTitulo(res.data?.titulo || '');
      })
      .catch(() => {});
  }, [token]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 overflow-x-hidden">
      {/* Header Mobile - fundo verde, compacto */}
      <div className="md:hidden bg-emerald-600 px-4 py-3 flex items-center justify-between sticky top-0 z-50">
        {user && <MobileNav />}
        <h1 className="text-lg font-bold text-white tracking-tight">Ranking Run Pro</h1>
        <div className="flex items-center gap-1">
          {user ? (
            <>
              <NotificacoesBell />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => window.location.reload()}
                className="text-white hover:bg-white/10 h-9 w-9"
              >
                <RefreshCw className="w-4 h-4" />
              </Button>
            </>
          ) : (
            <Button onClick={() => navigate('/login')} size="sm" className="bg-white text-emerald-700 hover:bg-emerald-50 h-8 text-xs font-semibold">
              <LogIn className="w-3.5 h-3.5 mr-1" />
              Entrar
            </Button>
          )}
        </div>
      </div>

      <div className="container mx-auto px-4 py-4 md:py-8">
        {/* Header Desktop */}
        <div className="hidden md:block mb-6">
          {/* Top row: Logo + User Actions */}
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-4xl font-bold text-emerald-600 dark:text-emerald-400 tracking-tight">
              Ranking Run Pro
            </h1>
            <div className="flex items-center gap-2">
              {user ? (
                <>
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/30 rounded-full">
                    <User className="w-4 h-4 text-emerald-600" />
                    <span className="text-sm font-medium text-emerald-700 dark:text-emerald-300" data-testid="user-name">
                      {user.nome}
                    </span>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => window.location.reload()} title="Atualizar" data-testid="btn-refresh" className="text-slate-600 hover:text-emerald-600 hover:bg-emerald-50">
                    <RefreshCw className="w-5 h-5" />
                  </Button>
                  <NotificacoesBell />
                  <Button onClick={() => navigate('/submeter-resultado')} className="bg-emerald-600" size="sm" data-testid="btn-submeter-desktop">
                    <Upload className="w-4 h-4 mr-1" />
                    Submeter
                  </Button>
                  <Button onClick={logout} variant="outline" size="sm" data-testid="btn-sair-desktop">
                    <LogOut className="w-4 h-4 mr-1" />
                    Sair
                  </Button>
                </>
              ) : (
                <>
                  <Button onClick={() => navigate('/cadastro')} variant="outline">Cadastrar</Button>
                  <Button onClick={() => navigate('/login')} className="bg-emerald-600">
                    <LogIn className="w-4 h-4 mr-2" />
                    Entrar
                  </Button>
                </>
              )}
            </div>
          </div>
          {/* Bottom row: Navigation */}
          {user && (
            <div className="flex items-center gap-1 overflow-x-auto pb-2 pt-1 scrollbar-thin -mx-1 px-1" data-testid="nav-bar-desktop" style={{WebkitOverflowScrolling: 'touch'}}>
              {isAdmin && (
                <Button onClick={() => navigate('/admin')} variant="outline" size="sm" className="shrink-0">
                  <Shield className="w-4 h-4 mr-1" />
                  Admin
                </Button>
              )}
              {user?.role === 'dono_assessoria' && (
                <Button onClick={() => navigate('/minha-assessoria')} variant="outline" size="sm" className="shrink-0 border-amber-500 text-amber-600 hover:bg-amber-50">
                  <Award className="w-4 h-4 mr-1" />
                  Minha Assessoria
                </Button>
              )}
              <Button onClick={() => navigate('/feed')} variant="ghost" size="sm" className="shrink-0 text-blue-500 hover:text-blue-600" data-testid="btn-feed">
                <MessageSquare className="w-4 h-4 mr-1" />
                Feed
              </Button>
              {hasEquipe && (
                <Button onClick={() => navigate('/feed-equipe')} variant="ghost" size="sm" className="shrink-0 text-amber-500 hover:text-amber-600 relative" data-testid="btn-feed-equipe">
                  <UsersRound className="w-4 h-4 mr-1" />
                  Feed da Equipe
                  {naoLidos > 0 && (
                    <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center px-1" data-testid="badge-feed-nao-lidos">
                      {naoLidos > 99 ? '99+' : naoLidos}
                    </span>
                  )}
                </Button>
              )}
              <Button onClick={() => navigate('/regras')} variant="ghost" size="sm" className="shrink-0 text-slate-500 hover:text-slate-700" data-testid="btn-regras">
                <HelpCircle className="w-4 h-4 mr-1" />
                Regras
              </Button>
              <Button onClick={() => navigate('/historico')} variant="ghost" size="sm" className="shrink-0 text-purple-500 hover:text-purple-700" data-testid="btn-historico">
                <History className="w-4 h-4 mr-1" />
                Historico
              </Button>
              <Button onClick={() => navigate('/ranking-cidade')} variant="ghost" size="sm" className="shrink-0 text-emerald-500 hover:text-emerald-700" data-testid="btn-ranking-cidade">
                <MapPin className="w-4 h-4 mr-1" />
                Por Cidade
              </Button>
              <Button onClick={() => navigate('/strava-clube')} variant="ghost" size="sm" className="shrink-0 text-orange-500 hover:text-orange-600" data-testid="btn-strava-clube">
                <Activity className="w-4 h-4 mr-1" />
                Strava
              </Button>
              <Button onClick={() => navigate('/corridas-parceiras')} variant="ghost" size="sm" className="shrink-0 text-emerald-500 hover:text-emerald-600" data-testid="btn-corridas-parceiras">
                <Trophy className="w-4 h-4 mr-1" />
                Corridas Parceiras
              </Button>
              <Button onClick={() => navigate('/parceiros')} variant="ghost" size="sm" className="shrink-0 text-blue-500 hover:text-blue-600" data-testid="btn-parceiros">
                <Handshake className="w-4 h-4 mr-1" />
                Parceiros
              </Button>
              <Button onClick={() => navigate('/votacao')} variant="ghost" size="sm" className="shrink-0 text-amber-500 hover:text-amber-600" data-testid="btn-votacao">
                <Medal className="w-4 h-4 mr-1" />
                Votação
              </Button>
              <Button onClick={() => navigate('/raio-x')} variant="ghost" size="sm" className="shrink-0 text-purple-500 hover:text-purple-600" data-testid="btn-raio-x">
                <Zap className="w-4 h-4 mr-1" />
                RAIO-X
              </Button>
              <Button onClick={() => navigate('/pagamento')} variant="ghost" size="sm" className="shrink-0 text-amber-500 hover:text-amber-600" data-testid="btn-premium-desktop">
                <CreditCard className="w-4 h-4 mr-1" />
                Atleta Premium
              </Button>
              <Button onClick={() => navigate('/perfil')} variant="outline" size="sm" className="shrink-0" data-testid="btn-perfil">
                <User className="w-4 h-4 mr-1" />
                Meu Perfil
              </Button>
            </div>
          )}
          {/* Visitor nav */}
          {!user && (
            <div className="flex items-center gap-2">
              <Button onClick={() => navigate('/regras')} variant="ghost" size="sm" className="text-slate-500 hover:text-slate-700" data-testid="btn-regras-visitor">
                <HelpCircle className="w-4 h-4 mr-1" />
                Regras
              </Button>
            </div>
          )}
        </div>

        {/* Visitante mobile - botões compactos */}
        {!user && (
          <div className="md:hidden flex gap-2 mb-4">
            <Button onClick={() => navigate('/regras')} variant="outline" size="sm" className="flex-1 text-xs">
              <HelpCircle className="w-3.5 h-3.5 mr-1" />
              Regras
            </Button>
            <Button onClick={() => navigate('/cadastro')} variant="outline" size="sm" className="flex-1 text-xs">
              Cadastrar
            </Button>
            <Button onClick={() => navigate('/login')} className="bg-emerald-600 flex-1 text-xs" size="sm">
              <LogIn className="w-3.5 h-3.5 mr-1" />
              Entrar
            </Button>
          </div>
        )}

        {/* Banner Votação Aberta */}
        {votacaoAberta && (
          <button
            onClick={() => navigate('/votacao')}
            className="w-full mb-4 relative overflow-hidden rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-yellow-500 p-[2px] group cursor-pointer"
            data-testid="banner-votacao"
          >
            <div className="flex items-center justify-between gap-3 rounded-[10px] bg-gradient-to-r from-amber-600 via-amber-500 to-yellow-500 px-4 py-3 sm:px-6 sm:py-4">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/20 flex items-center justify-center shrink-0 animate-pulse">
                  <Trophy className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
                <div className="min-w-0">
                  <p className="text-white font-bold text-sm sm:text-base truncate">{votacaoTitulo || 'PREMIAÇÃO'}</p>
                  <p className="text-amber-100 text-xs sm:text-sm truncate">Votação aberta! Clique para votar no seu destaque</p>
                </div>
              </div>
              <div className="shrink-0 bg-white/20 group-hover:bg-white/30 transition-colors rounded-lg px-3 py-1.5 sm:px-4 sm:py-2">
                <span className="text-white font-semibold text-xs sm:text-sm whitespace-nowrap">Votar Agora</span>
              </div>
            </div>
            {/* Animated shimmer */}
            <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent pointer-events-none" />
          </button>
        )}

        {/* Seletor de Tipo de Ranking - Fixo no topo ao rolar */}
        <Card className="mb-6 border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden sticky top-0 md:top-0 z-40 bg-white dark:bg-slate-900">
          <CardContent className="p-0">
            <div className="grid grid-cols-2 md:grid-cols-4">
              {/* Opcao Profissional/Amador */}
              <button 
                className={`py-3 md:py-4 px-3 md:px-4 flex items-center justify-center gap-1.5 md:gap-2 transition-all ${
                  tipoRanking === 'profissional' 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('profissional')}
                data-testid="tipo-ranking-profissional"
              >
                <Trophy className="w-4 h-4 md:w-5 md:h-5 flex-shrink-0" />
                <div className="text-left min-w-0">
                  <p className="font-semibold text-xs md:text-sm truncate">Profissional</p>
                  <p className={`text-xs hidden md:block ${tipoRanking === 'profissional' ? 'text-emerald-100' : 'text-slate-400'}`}>
                    Por colocacao
                  </p>
                </div>
              </button>
              
              {/* Opcao Galera */}
              <button 
                className={`py-3 md:py-4 px-3 md:px-4 flex items-center justify-center gap-1.5 md:gap-2 transition-all ${
                  tipoRanking === 'povao' 
                    ? 'bg-purple-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('povao')}
                data-testid="tipo-ranking-povao"
              >
                <Users className="w-4 h-4 md:w-5 md:h-5 flex-shrink-0" />
                <div className="text-left min-w-0">
                  <p className="font-semibold text-xs md:text-sm truncate">Galera</p>
                  <p className={`text-xs hidden md:block ${tipoRanking === 'povao' ? 'text-purple-100' : 'text-slate-400'}`}>
                    Por distancia
                  </p>
                </div>
              </button>

              {/* Opcao Equipes/Assessorias */}
              <button 
                className={`py-3 md:py-4 px-3 md:px-4 flex items-center justify-center gap-1.5 md:gap-2 transition-all ${
                  tipoRanking === 'equipes' 
                    ? 'bg-amber-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('equipes')}
                data-testid="tipo-ranking-equipes"
              >
                <Award className="w-4 h-4 md:w-5 md:h-5 flex-shrink-0" />
                <div className="text-left min-w-0">
                  <p className="font-semibold text-xs md:text-sm truncate">Equipes</p>
                  <p className={`text-xs hidden md:block ${tipoRanking === 'equipes' ? 'text-amber-100' : 'text-slate-400'}`}>
                    Liga de Assessorias
                  </p>
                </div>
              </button>

              {/* Opcao Ranking das Corridas */}
              <button 
                className="py-3 md:py-4 px-3 md:px-4 flex items-center justify-center gap-1.5 md:gap-2 transition-all bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-yellow-50 hover:text-yellow-700 border-l border-slate-200"
                onClick={() => navigate('/ranking-corridas')}
                data-testid="tipo-ranking-corridas"
              >
                <Star className="w-4 h-4 md:w-5 md:h-5 flex-shrink-0" />
                <div className="text-left min-w-0">
                  <p className="font-semibold text-xs md:text-sm truncate">Corridas</p>
                  <p className="text-xs text-slate-400 hidden md:block">
                    Avalie eventos
                  </p>
                </div>
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Ranking Profissional/Amador */}
        {tipoRanking === 'profissional' && <RankingProfissional />}


        {/* Ranking da Galera */}
        {tipoRanking === 'povao' && <RankingGalera />}


        {/* RANKING DE EQUIPES - LIGA NACIONAL DE ASSESSORIAS */}
        {tipoRanking === 'equipes' && <RankingEquipes />}

        {/* Footer */}
        <div className="mt-8 py-4 border-t border-slate-200 dark:border-slate-800 text-center">
          <button
            onClick={() => navigate('/politica-de-privacidade')}
            className="text-xs text-slate-400 hover:text-emerald-600 transition-colors inline-flex items-center gap-1"
            data-testid="link-politica-privacidade"
          >
            <Shield className="w-3 h-3" />
            Política de Privacidade
          </button>
          <span className="text-xs text-slate-300 dark:text-slate-600 mx-2">|</span>
          <span className="text-xs text-slate-400">Ranking Run Pro 2026</span>
        </div>

      </div>
    </div>
  );
};

export default RankingPage;
