import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Send, Loader2, MoreHorizontal, Clock, Trash2, Users, 
  MessageCircle, Trophy, Medal, Star, Image as ImageIcon, Heart
} from 'lucide-react';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const FeedPostCard = ({
  post, user, isAdmin, token,
  ReacoesDisplay, ReacaoButton, PostConteudoEspecial, BotaoParabens,
  handleDeletarPost, handleDoubleTap, handleComentar,
  handleFixarComentario, handleExcluirComentario, handleBloquearUsuario,
  heartAnimation, showComentarios, setShowComentarios,
  comentarioTexto, setComentarioTexto, enviandoComentario,
  formatarData
}) => {
  return (
    <Card className="bg-slate-800 border-slate-700" data-testid={`post-${post.id}`}>
      <CardContent className="p-4 space-y-3">
        {/* Header do Post */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Avatar className="w-10 h-10">
              {post.autor?.foto_url ? (
                <AvatarImage src={`${BACKEND_URL}${post.autor.foto_url}`} />
              ) : null}
              <AvatarFallback className="bg-amber-500 text-white">
                {post.autor?.nome?.charAt(0) || '?'}
              </AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-2">
                <p className="font-semibold text-white">{post.autor?.nome}</p>
                {post.auto_gerado && post.tipo === 'conquista' && (
                  <Badge className="bg-purple-600/80 text-xs py-0">
                    <Trophy className="w-3 h-3 mr-1" />
                    Conquista
                  </Badge>
                )}
                {post.auto_gerado && post.tipo === 'corrida_aprovada' && (
                  <Badge className="bg-green-600/80 text-xs py-0">
                    <Medal className="w-3 h-3 mr-1" />
                    Resultado
                  </Badge>
                )}
                {post.tipo === 'foto' && (
                  <Badge className="bg-teal-600/80 text-xs py-0">
                    <ImageIcon className="w-3 h-3 mr-1" />
                    Foto
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Clock className="w-3 h-3" />
                {formatarData(post.data_criacao)}
                {post.autor?.equipe && (
                  <>
                    <span>•</span>
                    <span className="text-amber-400">{post.autor.equipe}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          
          {(post.autor_id === user?.id || isAdmin) && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="text-slate-400">
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-slate-800 border-slate-700">
                <DropdownMenuItem 
                  className="text-red-400 cursor-pointer"
                  onClick={() => handleDeletarPost(post.id)}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Deletar Post
                </DropdownMenuItem>
                {isAdmin && post.total_comentarios > 0 && (
                  <DropdownMenuItem 
                    className="text-amber-400 cursor-pointer"
                    onClick={() => setShowComentarios({ ...showComentarios, [post.id]: true })}
                  >
                    <MessageCircle className="w-4 h-4 mr-2" />
                    Gerenciar Comentários ({post.total_comentarios})
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
        
        {/* Conteúdo especial para posts automáticos */}
        <PostConteudoEspecial post={post} />
        
        {/* Texto do post */}
        {post.texto && !post.auto_gerado && (
          <p className="text-slate-200 whitespace-pre-wrap">{post.texto}</p>
        )}
        
        {/* Imagem do post com duplo-toque para curtir */}
        {post.imagem_url && (
          <div
            className="relative cursor-pointer select-none"
            onClick={() => handleDoubleTap(post.id)}
            data-testid={`post-image-wrapper-${post.id}`}
          >
            <img 
              src={`${BACKEND_URL}/api${post.imagem_url}`} 
              alt="Post" 
              className="rounded-xl max-h-[350px] w-full object-contain bg-slate-900/50 border border-slate-700"
              data-testid={`post-image-${post.id}`}
              loading="lazy"
              draggable={false}
            />
            {heartAnimation[post.id] && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none" data-testid={`heart-animation-${post.id}`}>
                <Heart
                  className="w-24 h-24 text-red-500 fill-red-500 drop-shadow-lg"
                  style={{ animation: 'heartBurst 1s ease-out forwards' }}
                />
              </div>
            )}
          </div>
        )}
        
        {/* Reações Display */}
        <ReacoesDisplay post={post} />
        
        {/* Ações */}
        <div className="flex items-center gap-4 pt-2 border-t border-slate-700">
          <ReacaoButton post={post} />
          
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-slate-400 hover:text-blue-400"
            onClick={() => setShowComentarios({ ...showComentarios, [post.id]: !showComentarios[post.id] })}
            data-testid={`comment-btn-${post.id}`}
          >
            <MessageCircle className="w-4 h-4 mr-1" />
            {post.total_comentarios || 0}
          </Button>
          
          <BotaoParabens post={post} />
        </div>
        
        {/* Seção de Comentários */}
        {showComentarios[post.id] && (
          <div className="space-y-3 pt-3 border-t border-slate-700">
            {post.comentarios_preview?.map((com) => (
              <div key={com.id} className="flex gap-2 group">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="bg-slate-600 text-white text-xs">
                    {com.autor?.nome?.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div className={`rounded-lg px-3 py-2 flex-1 ${com.fixado ? 'bg-amber-900/30 border border-amber-500/30' : 'bg-slate-700'}`}>
                  <div className="flex items-center gap-2">
                    <p className="text-sm text-white font-medium">{com.autor?.nome}</p>
                    {com.autor?.selo_respeitoso && (
                      <span title="Atleta Respeitoso - Sem infrações" className="text-lg">🏅</span>
                    )}
                    {com.fixado && (
                      <Badge className="bg-amber-500/20 text-amber-400 text-xs py-0">Fixado</Badge>
                    )}
                  </div>
                  <p className="text-sm text-slate-300 break-all">{com.texto}</p>
                </div>
                {isAdmin && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button 
                        variant="ghost" size="icon" 
                        className="text-amber-400 hover:text-amber-300 hover:bg-amber-500/20 h-8 w-8"
                        data-testid={`admin-comment-menu-${com.id}`}
                      >
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="bg-slate-800 border-slate-700">
                      <DropdownMenuItem className="text-amber-400 cursor-pointer" onClick={() => handleFixarComentario(com.id)} data-testid={`fixar-comment-${com.id}`}>
                        <Star className="w-4 h-4 mr-2" />
                        {com.fixado ? 'Desfixar' : 'Fixar'}
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-red-400 cursor-pointer" onClick={() => handleExcluirComentario(com.id, post.id)} data-testid={`excluir-comment-${com.id}`}>
                        <Trash2 className="w-4 h-4 mr-2" />
                        Excluir
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-orange-400 cursor-pointer" onClick={() => handleBloquearUsuario(com.autor_id, com.autor?.nome)} data-testid={`bloquear-user-${com.id}`}>
                        <Users className="w-4 h-4 mr-2" />
                        Bloquear Usuário
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
            ))}
            
            {/* Input de novo comentário */}
            <div className="flex gap-2">
              <Avatar className="w-8 h-8">
                <AvatarFallback className="bg-amber-500 text-white text-xs">
                  {user?.nome?.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex gap-2">
                  <Input
                    placeholder="Escreva um comentário..."
                    value={comentarioTexto[post.id] || ''}
                    onChange={(e) => setComentarioTexto({ ...comentarioTexto, [post.id]: e.target.value })}
                    onKeyDown={(e) => e.key === 'Enter' && handleComentar(post.id)}
                    className="bg-slate-700 border-slate-600 text-sm"
                    maxLength={200}
                    data-testid={`comment-input-${post.id}`}
                  />
                  <Button 
                    size="sm"
                    onClick={() => handleComentar(post.id)}
                    disabled={!comentarioTexto[post.id]?.trim() || enviandoComentario === post.id}
                    data-testid={`send-comment-${post.id}`}
                  >
                    {enviandoComentario === post.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
                <p className="text-xs text-slate-500 mt-1 text-right">
                  {(comentarioTexto[post.id] || '').length}/200
                </p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FeedPostCard;
