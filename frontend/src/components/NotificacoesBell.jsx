import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Bell, Check, CheckCheck, Trophy, XCircle, Award } from 'lucide-react';

const NotificacoesBell = () => {
  const { notificacoes, naoLidas, marcarLida, marcarTodasLidas } = useAuth();
  const [open, setOpen] = useState(false);

  const getIcon = (tipo) => {
    switch (tipo) {
      case 'aprovacao':
        return <Check className="w-4 h-4 text-emerald-500" />;
      case 'reprovacao':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'conquista':
        return <Award className="w-4 h-4 text-amber-500" />;
      default:
        return <Bell className="w-4 h-4 text-blue-500" />;
    }
  };

  const handleNotificacaoClick = async (notificacao) => {
    if (!notificacao.lida) {
      await marcarLida(notificacao.id);
    }
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative" data-testid="btn-notificacoes">
          <Bell className="h-5 w-5" />
          {naoLidas > 0 && (
            <Badge 
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-red-500 text-white text-xs"
            >
              {naoLidas > 9 ? '9+' : naoLidas}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80 max-h-96 overflow-y-auto">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span>Notificações</span>
          {naoLidas > 0 && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={marcarTodasLidas}
              className="text-xs h-7"
            >
              <CheckCheck className="w-3 h-3 mr-1" />
              Marcar todas
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {notificacoes.length === 0 ? (
          <div className="p-4 text-center text-sm text-slate-500">
            Nenhuma notificação
          </div>
        ) : (
          notificacoes.slice(0, 10).map((notificacao) => (
            <DropdownMenuItem 
              key={notificacao.id}
              className={`flex items-start gap-3 p-3 cursor-pointer ${!notificacao.lida ? 'bg-slate-50 dark:bg-slate-800/50' : ''}`}
              onClick={() => handleNotificacaoClick(notificacao)}
            >
              <div className="flex-shrink-0 mt-0.5">
                {notificacao.dados_extras?.icone ? (
                  <span className="text-lg">{notificacao.dados_extras.icone}</span>
                ) : (
                  getIcon(notificacao.tipo)
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${!notificacao.lida ? 'text-slate-900 dark:text-white' : 'text-slate-600 dark:text-slate-400'}`}>
                  {notificacao.titulo}
                </p>
                <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">
                  {notificacao.mensagem}
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  {new Date(notificacao.data_criacao).toLocaleDateString('pt-BR', {
                    day: '2-digit',
                    month: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
              {!notificacao.lida && (
                <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0 mt-2" />
              )}
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default NotificacoesBell;
