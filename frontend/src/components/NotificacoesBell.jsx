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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Bell, Check, CheckCheck, Trophy, XCircle, Award, Trash2, ExternalLink, X, Image, Loader2 } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const NotificacoesBell = () => {
  const { notificacoes, naoLidas, marcarLida, marcarTodasLidas, token, fetchNotificacoes } = useAuth();
  const [open, setOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedNotificacao, setSelectedNotificacao] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [imageModalOpen, setImageModalOpen] = useState(false);

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

  // Função para renderizar mensagem com links clicáveis
  const renderMensagemComLinks = (mensagem) => {
    if (!mensagem) return null;
    
    // Regex para detectar URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const parts = mensagem.split(urlRegex);
    
    return parts.map((part, index) => {
      if (part.match(urlRegex)) {
        return (
          <a
            key={index}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 underline inline-flex items-center gap-1"
            onClick={(e) => e.stopPropagation()}
          >
            {part.length > 40 ? part.substring(0, 40) + '...' : part}
            <ExternalLink className="w-3 h-3" />
          </a>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  const handleNotificacaoClick = async (notificacao) => {
    if (!notificacao.lida) {
      await marcarLida(notificacao.id);
    }
    
    // Abrir modal com detalhes da notificação
    setSelectedNotificacao(notificacao);
    setModalOpen(true);
    setOpen(false);
  };

  const handleExcluirNotificacao = async () => {
    if (!selectedNotificacao) return;
    
    setDeleting(true);
    try {
      await axios.delete(`${API}/notificacoes/${selectedNotificacao.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Notificação excluída');
      setModalOpen(false);
      setSelectedNotificacao(null);
      
      // Recarregar notificações
      if (fetchNotificacoes) {
        await fetchNotificacoes();
      }
    } catch (error) {
      console.error('Erro ao excluir notificação:', error);
      toast.error('Erro ao excluir notificação');
    } finally {
      setDeleting(false);
    }
  };

  // Verificar se a notificação tem imagem
  const getImageUrl = (notificacao) => {
    if (!notificacao) return null;
    
    // Verificar em dados_extras
    const imageUrl = notificacao.dados_extras?.imagem_url || 
                     notificacao.dados_extras?.foto_url ||
                     notificacao.imagem_url ||
                     notificacao.foto_url;
    
    if (!imageUrl) return null;
    
    // Se for URL relativa, adicionar base
    if (imageUrl.startsWith('/')) {
      return `${BACKEND_URL}${imageUrl}`;
    }
    
    return imageUrl;
  };

  return (
    <>
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
                data-testid={`notificacao-item-${notificacao.id}`}
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
                  {/* Indicador de imagem */}
                  {getImageUrl(notificacao) && (
                    <div className="flex items-center gap-1 mt-1">
                      <Image className="w-3 h-3 text-blue-400" />
                      <span className="text-xs text-blue-400">Contém imagem</span>
                    </div>
                  )}
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

      {/* Modal de Detalhes da Notificação */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent className="sm:max-w-md bg-slate-900 border-slate-700">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-white">
              {selectedNotificacao?.dados_extras?.icone ? (
                <span className="text-xl">{selectedNotificacao.dados_extras.icone}</span>
              ) : (
                getIcon(selectedNotificacao?.tipo)
              )}
              {selectedNotificacao?.titulo}
            </DialogTitle>
            <DialogDescription className="text-slate-400">
              {new Date(selectedNotificacao?.data_criacao).toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Conteúdo da mensagem com links clicáveis */}
            <div className="text-slate-300 text-sm leading-relaxed">
              {renderMensagemComLinks(selectedNotificacao?.mensagem)}
            </div>
            
            {/* Imagem da notificação (se houver) */}
            {getImageUrl(selectedNotificacao) && (
              <div className="mt-4">
                <p className="text-xs text-slate-400 mb-2 flex items-center gap-1">
                  <Image className="w-3 h-3" />
                  Imagem anexada:
                </p>
                <div 
                  className="relative cursor-pointer group rounded-lg overflow-hidden border border-slate-700"
                  onClick={() => setImageModalOpen(true)}
                >
                  <img 
                    src={getImageUrl(selectedNotificacao)} 
                    alt="Imagem da notificação"
                    className="w-full max-h-64 object-contain bg-slate-800 group-hover:opacity-90 transition-opacity"
                  />
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/30">
                    <span className="text-white text-sm flex items-center gap-1">
                      <ExternalLink className="w-4 h-4" />
                      Ampliar
                    </span>
                  </div>
                </div>
              </div>
            )}
            
            {/* Dados extras (se houver) */}
            {selectedNotificacao?.dados_extras && Object.keys(selectedNotificacao.dados_extras).filter(k => !['icone', 'imagem_url', 'foto_url'].includes(k)).length > 0 && (
              <div className="mt-4 p-3 bg-slate-800 rounded-lg">
                <p className="text-xs text-slate-400 mb-2">Informações adicionais:</p>
                <div className="space-y-1">
                  {Object.entries(selectedNotificacao.dados_extras)
                    .filter(([key]) => !['icone', 'imagem_url', 'foto_url'].includes(key))
                    .map(([key, value]) => (
                      <div key={key} className="text-xs text-slate-300">
                        <span className="text-slate-500">{key.replace(/_/g, ' ')}:</span>{' '}
                        {typeof value === 'string' && value.match(/^https?:\/\//) ? (
                          <a 
                            href={value} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:underline"
                          >
                            {value.length > 30 ? value.substring(0, 30) + '...' : value}
                          </a>
                        ) : (
                          String(value)
                        )}
                      </div>
                    ))
                  }
                </div>
              </div>
            )}
          </div>

          <DialogFooter className="flex gap-2 sm:gap-2">
            <Button 
              variant="outline" 
              onClick={() => setModalOpen(false)}
              className="border-slate-600 text-slate-300"
            >
              Fechar
            </Button>
            <Button 
              variant="destructive"
              onClick={handleExcluirNotificacao}
              disabled={deleting}
              data-testid="btn-excluir-notificacao"
            >
              {deleting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Excluindo...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Excluir
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Imagem Ampliada */}
      <Dialog open={imageModalOpen} onOpenChange={setImageModalOpen}>
        <DialogContent className="sm:max-w-3xl bg-slate-900 border-slate-700 p-2">
          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 z-10 bg-black/50 hover:bg-black/70"
              onClick={() => setImageModalOpen(false)}
            >
              <X className="w-5 h-5 text-white" />
            </Button>
            {getImageUrl(selectedNotificacao) && (
              <img 
                src={getImageUrl(selectedNotificacao)} 
                alt="Imagem ampliada"
                className="w-full max-h-[80vh] object-contain rounded-lg"
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default NotificacoesBell;
