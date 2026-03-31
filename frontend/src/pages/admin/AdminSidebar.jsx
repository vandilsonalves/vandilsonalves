import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Home } from 'lucide-react';

const AdminSidebar = ({
  menuSections,
  activeMenu,
  setActiveMenu,
  isSuperAdmin,
  adminPermissoes,
  tipoAdmin,
  pendentes,
  onNavigateHome
}) => {
  return (
    <div className="w-64 bg-gradient-to-b from-slate-800 to-slate-900 text-white fixed h-full shadow-xl">
      <div className="p-6 border-b border-slate-700/50">
        <h1 className="text-xl font-bold text-emerald-400">Ranking Run Pró</h1>
        <p className="text-xs text-slate-400 mt-1">Painel Administrativo</p>
        <div className="mt-3">
          <Badge className={`text-xs ${
            isSuperAdmin 
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' 
              : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
          }`}>
            {tipoAdmin || 'Admin'}
          </Badge>
        </div>
      </div>

      <nav className="p-4 space-y-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        {menuSections.map((section, sectionIdx) => {
          const sectionItems = section.items.filter(item => {
            if (isSuperAdmin) return true;
            if (item.superAdminOnly) return false;
            if (!item.permissoes || item.permissoes.length === 0) return true;
            return item.permissoes.some(perm => adminPermissoes.includes(perm));
          });
          
          if (section.superAdminOnly && !isSuperAdmin) return null;
          if (sectionItems.length === 0) return null;
          
          return (
            <div key={sectionIdx} className={section.title ? 'pt-4' : ''}>
              {section.title && (
                <p className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  {section.title}
                </p>
              )}
              <div className="space-y-1">
                {sectionItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveMenu(item.id)}
                      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all text-sm ${
                        activeMenu === item.id 
                          ? 'bg-emerald-500/20 text-emerald-400 border-l-4 border-emerald-400' 
                          : 'text-slate-400 hover:bg-slate-700/50 hover:text-white'
                      }`}
                      data-testid={`menu-${item.id}`}
                    >
                      <Icon className="w-4 h-4" />
                      <span className="font-medium">{item.label}</span>
                      {item.id === 'pendentes' && pendentes.length > 0 && (
                        <Badge className="ml-auto bg-red-500 text-white text-xs px-1.5 py-0.5 min-w-[20px]">
                          {pendentes.length}
                        </Badge>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700/50">
        <Button 
          onClick={onNavigateHome} 
          variant="ghost" 
          className="w-full justify-start text-slate-400 hover:text-white"
        >
          <Home className="w-4 h-4 mr-2" />
          Voltar ao Site
        </Button>
      </div>
    </div>
  );
};

export default AdminSidebar;
