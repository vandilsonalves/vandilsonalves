import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import {
  Menu, X, MessageSquare, HelpCircle, History, MapPin, Activity,
  Zap, User, Upload, LogOut, Shield, Award, Home, CreditCard, UsersRound
} from 'lucide-react';

/**
 * MobileNav - Menu hamburger com drawer lateral para mobile.
 * Escondido em telas md+ (desktop mantém o header original).
 */
export default function MobileNav() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { user, isAdmin, logout } = useAuth();

  const go = (path) => {
    setOpen(false);
    navigate(path);
  };

  const hasEquipe = user?.equipe && !['Individual', 'individual', 'SEM EQUIPE', ''].includes(user.equipe);

  const menuItems = [
    { label: 'Ranking', icon: Home, path: '/', color: 'text-emerald-400' },
    { label: 'Feed', icon: MessageSquare, path: '/feed', color: 'text-blue-400' },
    ...(hasEquipe ? [{ label: 'Feed da Equipe', icon: UsersRound, path: '/feed-equipe', color: 'text-amber-400' }] : []),
    { label: 'Regras', icon: HelpCircle, path: '/regras', color: 'text-slate-400' },
    { label: 'Historico', icon: History, path: '/historico', color: 'text-purple-400' },
    { label: 'Por Cidade', icon: MapPin, path: '/ranking-cidade', color: 'text-teal-400' },
    { label: 'Strava', icon: Activity, path: '/strava-clube', color: 'text-orange-400' },
    { label: 'Raio-X', icon: Zap, path: '/raio-x', color: 'text-violet-400' },
    { label: 'Meu Perfil', icon: User, path: '/perfil', color: 'text-sky-400' },
    { label: 'Submeter Resultado', icon: Upload, path: '/submeter-resultado', color: 'text-emerald-400' },
    { label: 'Atleta Premium', icon: CreditCard, path: '/pagamento', color: 'text-amber-400' },
  ];

  return (
    <>
      {/* Botão hamburger - visível apenas no mobile */}
      <button
        onClick={() => setOpen(true)}
        className="md:hidden p-2 rounded-lg text-white hover:bg-white/10 transition"
        data-testid="btn-mobile-menu"
        aria-label="Abrir menu"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm md:hidden"
          onClick={() => setOpen(false)}
          data-testid="mobile-nav-overlay"
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed top-0 left-0 z-[101] h-full w-72 bg-gray-950 border-r border-gray-800 transform transition-transform duration-300 ease-out md:hidden ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
        data-testid="mobile-nav-drawer"
      >
        {/* Header do drawer */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-white leading-tight">Ranking Run Pro</p>
              {user && (
                <p className="text-xs text-gray-400 truncate max-w-[140px]">{user.nome}</p>
              )}
            </div>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition"
            data-testid="btn-close-menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Menu items */}
        <nav className="flex-1 overflow-y-auto py-3 px-3">
          {isAdmin && (
            <button
              onClick={() => go('/admin')}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-amber-400 hover:bg-amber-500/10 transition mb-1"
              data-testid="mobile-nav-admin"
            >
              <Shield className="w-5 h-5" />
              <span className="text-sm font-medium">Painel Admin</span>
            </button>
          )}

          {user?.role === 'dono_assessoria' && (
            <button
              onClick={() => go('/minha-assessoria')}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-amber-400 hover:bg-amber-500/10 transition mb-1"
              data-testid="mobile-nav-assessoria"
            >
              <Award className="w-5 h-5" />
              <span className="text-sm font-medium">Minha Assessoria</span>
            </button>
          )}

          <div className="h-px bg-gray-800 my-2" />

          {menuItems.map((item) => (
            <button
              key={item.path}
              onClick={() => go(item.path)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition mb-0.5"
              data-testid={`mobile-nav-${item.label.toLowerCase().replace(/\s/g, '-')}`}
            >
              <item.icon className={`w-5 h-5 ${item.color}`} />
              <span className="text-sm">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-gray-800 p-3">
          <button
            onClick={() => { logout(); setOpen(false); }}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-red-400 hover:bg-red-500/10 transition"
            data-testid="mobile-nav-sair"
          >
            <LogOut className="w-5 h-5" />
            <span className="text-sm font-medium">Sair</span>
          </button>
        </div>
      </div>
    </>
  );
}
