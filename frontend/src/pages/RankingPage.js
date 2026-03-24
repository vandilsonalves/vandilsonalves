import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import NotificacoesBell from '@/components/NotificacoesBell';
import { LogIn, Upload, Shield, LogOut, User, Trophy, Flame, Users, MessageSquare, HelpCircle, Award, Star, Activity, History, MapPin, RefreshCw, Zap } from 'lucide-react';
import { RegulamentoButton } from '@/components/RegulamentoModal';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import RankingProfissional from '@/components/ranking/RankingProfissional';
import RankingGalera from '@/components/ranking/RankingGalera';
import RankingEquipes from '@/components/ranking/RankingEquipes';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const RankingPage = () => {
  const navigate = useNavigate();
  const { user, token, isAdmin, logout } = useAuth();
  const [tipoRanking, setTipoRanking] = useState('profissional');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header com Login/Logout e Nome do Usuário */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-emerald-600 dark:text-emerald-400 mb-2 tracking-tight">
              Ranking Run Pró
            </h1>
          </div>
          <div className="flex items-center gap-2">
            {user ? (
              <>
                {/* Nome do usuário */}
                <div className="hidden md:flex items-center gap-2 mr-4 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/30 rounded-full">
                  <User className="w-4 h-4 text-emerald-600" />
                  <span className="text-sm font-medium text-emerald-700 dark:text-emerald-300" data-testid="user-name">
                    {user.nome}
                  </span>
                </div>
                
                {/* Botão Atualizar Página */}
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => window.location.reload()} 
                  title="Atualizar página"
                  data-testid="btn-refresh"
                  className="text-slate-600 hover:text-emerald-600 hover:bg-emerald-50"
                >
                  <RefreshCw className="w-5 h-5" />
                </Button>
                
                {/* Notificações */}
                <NotificacoesBell />
                
                {isAdmin && (
                  <Button onClick={() => navigate('/admin')} variant="outline" size="sm">
                    <Shield className="w-4 h-4 mr-2" />
                    Admin
                  </Button>
                )}
                {user?.role === 'dono_assessoria' && (
                  <Button onClick={() => navigate('/minha-assessoria')} variant="outline" size="sm" className="border-amber-500 text-amber-600 hover:bg-amber-50">
                    <Award className="w-4 h-4 mr-2" />
                    Minha Assessoria
                  </Button>
                )}
                
                {/* Link para Feed */}
                <Button onClick={() => navigate('/feed')} variant="ghost" size="sm" className="text-blue-500 hover:text-blue-600" data-testid="btn-feed">
                  <MessageSquare className="w-4 h-4 mr-1" />
                  Feed
                </Button>
                
                {/* Link para Regras */}
                <Button onClick={() => navigate('/regras')} variant="ghost" size="sm" className="text-slate-500 hover:text-slate-700" data-testid="btn-regras">
                  <HelpCircle className="w-4 h-4 mr-1" />
                  Regras
                </Button>
                
                {/* Link para Histórico de Submissões */}
                <Button onClick={() => navigate('/historico')} variant="ghost" size="sm" className="text-purple-500 hover:text-purple-700" data-testid="btn-historico">
                  <History className="w-4 h-4 mr-1" />
                  Histórico
                </Button>
                
                {/* Link para Ranking por Cidade */}
                <Button onClick={() => navigate('/ranking-cidade')} variant="ghost" size="sm" className="text-emerald-500 hover:text-emerald-700" data-testid="btn-ranking-cidade">
                  <MapPin className="w-4 h-4 mr-1" />
                  Por Cidade
                </Button>
                
                {/* Link para Strava Clube */}
                <Button onClick={() => navigate('/strava-clube')} variant="ghost" size="sm" className="text-orange-500 hover:text-orange-600" data-testid="btn-strava-clube">
                  <Activity className="w-4 h-4 mr-1" />
                  Strava
                </Button>
                
                {/* Link para RAIO-X */}
                <Button onClick={() => navigate('/raio-x')} variant="ghost" size="sm" className="text-purple-500 hover:text-purple-600" data-testid="btn-raio-x">
                  <Zap className="w-4 h-4 mr-1" />
                  RAIO-X
                </Button>
                
                <Button onClick={() => navigate('/perfil')} variant="outline" size="sm" data-testid="btn-perfil">
                  <User className="w-4 h-4 mr-2" />
                  Meu Perfil
                </Button>
                <Button onClick={() => navigate('/submeter-resultado')} className="bg-emerald-600" size="sm">
                  <Upload className="w-4 h-4 mr-2" />
                  Submeter
                </Button>
                <Button onClick={logout} variant="outline" size="sm">
                  <LogOut className="w-4 h-4 mr-2" />
                  Sair
                </Button>
              </>
            ) : (
              <>
                {/* Link para Regras (visitantes) */}
                <Button onClick={() => navigate('/regras')} variant="ghost" size="sm" className="text-slate-500 hover:text-slate-700" data-testid="btn-regras-visitor">
                  <HelpCircle className="w-4 h-4 mr-1" />
                  Regras
                </Button>
                <Button onClick={() => navigate('/cadastro')} variant="outline">
                  Cadastrar
                </Button>
                <Button onClick={() => navigate('/login')} className="bg-emerald-600">
                  <LogIn className="w-4 h-4 mr-2" />
                  Entrar
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Seletor de Tipo de Ranking - Fixo no topo ao rolar */}
        <Card className="mb-6 border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden sticky top-0 z-50 bg-white dark:bg-slate-900">
          <CardContent className="p-0">
            <div className="grid grid-cols-2 md:grid-cols-4">
              {/* Opção Profissional/Amador */}
              <button 
                className={`py-4 px-4 flex items-center justify-center gap-2 transition-all ${
                  tipoRanking === 'profissional' 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('profissional')}
                data-testid="tipo-ranking-profissional"
              >
                <Trophy className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold text-sm">Ranking Profissional/Amador</p>
                  <p className={`text-xs ${tipoRanking === 'profissional' ? 'text-emerald-100' : 'text-slate-400'}`}>
                    Pontuação por colocação
                  </p>
                </div>
              </button>
              
              {/* Opção Galera */}
              <button 
                className={`py-4 px-4 flex items-center justify-center gap-2 transition-all ${
                  tipoRanking === 'povao' 
                    ? 'bg-purple-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('povao')}
                data-testid="tipo-ranking-povao"
              >
                <Users className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold text-sm">Ranking da Galera</p>
                  <p className={`text-xs ${tipoRanking === 'povao' ? 'text-purple-100' : 'text-slate-400'}`}>
                    Pontuação por distância
                  </p>
                </div>
              </button>

              {/* Opção Equipes/Assessorias */}
              <button 
                className={`py-4 px-4 flex items-center justify-center gap-2 transition-all ${
                  tipoRanking === 'equipes' 
                    ? 'bg-amber-500 text-white' 
                    : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                }`}
                onClick={() => setTipoRanking('equipes')}
                data-testid="tipo-ranking-equipes"
              >
                <Award className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold text-sm">Ranking de Equipes</p>
                  <p className={`text-xs ${tipoRanking === 'equipes' ? 'text-amber-100' : 'text-slate-400'}`}>
                    Liga Nacional de Assessorias
                  </p>
                </div>
              </button>

              {/* Opção Ranking das Corridas */}
              <button 
                className="py-4 px-4 flex items-center justify-center gap-2 transition-all bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-yellow-50 hover:text-yellow-700 border-l border-slate-200"
                onClick={() => navigate('/ranking-corridas')}
                data-testid="tipo-ranking-corridas"
              >
                <Star className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold text-sm">Ranking das Corridas</p>
                  <p className="text-xs text-slate-400">
                    Avalie eventos de corrida
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

      </div>
    </div>
  );
};

export default RankingPage;
