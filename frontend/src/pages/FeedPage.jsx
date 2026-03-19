// /app/frontend/src/pages/FeedPage.jsx
// Feed Social da Plataforma com Reações e Comentários (sem upload de imagem)

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { 
  Send, Loader2, ArrowLeft, MoreHorizontal,
  TrendingUp, Clock, Trash2, Users, Smile, MessageCircle
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Reações disponíveis
const REACOES = {
  aplausos: { emoji: "👏", nome: "Aplausos" },
  corrida: { emoji: "🏃", nome: "Correndo" },
  forca: { emoji: "💪", nome: "Força" },
  fogo: { emoji: "🔥", nome: "Em chamas" },
  coracao: { emoji: "❤️", nome: "Amei" },
  festa: { emoji: "🎉", nome: "Celebrando" },
  trofeu: { emoji: "🏆", nome: "Campeão" }
};

const FeedPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [posts, setPosts] = useState([]);
  const [trending, setTrending] = useState([]);
  const [pagina, setPagina] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  
  // Novo post
  const [novoPost, setNovoPost] = useState('');
  const [enviandoPost, setEnviandoPost] = useState(false);
  
  // Comentários
  const [comentarioTexto, setComentarioTexto] = useState({});
  const [enviandoComentario, setEnviandoComentario] = useState(null);
  const [showComentarios, setShowComentarios] = useState({});

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchFeed();
    fetchTrending();
  }, [user]);

  const fetchFeed = async (pag = 1, append = false) => {
    if (pag === 1) setLoading(true);
    else setLoadingMore(true);
    
    try {
      const response = await axios.get(`${API}/feed?pagina=${pag}&limite=10`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (append) {
        setPosts(prev => [...prev, ...response.data.posts]);
      } else {
        setPosts(response.data.posts || []);
      }
      
      setHasMore(pag < response.data.total_paginas);
      setPagina(pag);
    } catch (error) {
      console.error('Erro ao buscar feed:', error);
      toast.error('Erro ao carregar feed');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const fetchTrending = async () => {
    try {
      const response = await axios.get(`${API}/feed/trending?limite=5`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTrending(response.data.trending || []);
    } catch (error) {
      console.error('Erro ao buscar trending:', error);
    }
  };

  const handleCriarPost = async () => {
    if (!novoPost.trim()) return;
    
    setEnviandoPost(true);
    try {
      await axios.post(
        `${API}/feed/posts`,
        { texto: novoPost, tipo: 'texto' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('Post publicado!');
      setNovoPost('');
      fetchFeed();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao publicar post');
    } finally {
      setEnviandoPost(false);
    }
  };

  const handleReagir = async (postId, tipoReacao) => {
    try {
      const response = await axios.post(
        `${API}/feed/posts/${postId}/reagir`,
        { tipo_reacao: tipoReacao },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Atualizar o post localmente
      setPosts(prev => prev.map(post => {
        if (post.id === postId) {
          const novasReacoes = { ...post.reacoes };
          const minhaReacaoAnterior = post.minha_reacao;
          
          // Remover contagem da reação anterior se houver
          if (minhaReacaoAnterior && novasReacoes[minhaReacaoAnterior]) {
            novasReacoes[minhaReacaoAnterior] = {
              ...novasReacoes[minhaReacaoAnterior],
              count: novasReacoes[minhaReacaoAnterior].count - 1
            };
            if (novasReacoes[minhaReacaoAnterior].count <= 0) {
              delete novasReacoes[minhaReacaoAnterior];
            }
          }
          
          // Se removeu a reação
          if (response.data.removida) {
            return {
              ...post,
              reacoes: novasReacoes,
              minha_reacao: null,
              total_reacoes: Math.max(0, (post.total_reacoes || 1) - 1)
            };
          }
          
          // Adicionar nova reação
          if (!novasReacoes[tipoReacao]) {
            novasReacoes[tipoReacao] = {
              count: 0,
              emoji: REACOES[tipoReacao].emoji,
              nome: REACOES[tipoReacao].nome
            };
          }
          novasReacoes[tipoReacao] = {
            ...novasReacoes[tipoReacao],
            count: novasReacoes[tipoReacao].count + 1
          };
          
          const totalAnterior = post.total_reacoes || 0;
          const novoTotal = minhaReacaoAnterior ? totalAnterior : totalAnterior + 1;
          
          return {
            ...post,
            reacoes: novasReacoes,
            minha_reacao: tipoReacao,
            total_reacoes: novoTotal
          };
        }
        return post;
      }));
      
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao reagir');
    }
  };

  const handleComentar = async (postId) => {
    const texto = comentarioTexto[postId];
    if (!texto?.trim()) return;
    
    setEnviandoComentario(postId);
    try {
      await axios.post(
        `${API}/feed/posts/${postId}/comentarios`,
        { texto },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setComentarioTexto({ ...comentarioTexto, [postId]: '' });
      toast.success('Comentário adicionado!');
      
      // Recarregar feed para atualizar comentários
      fetchFeed();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao comentar');
    } finally {
      setEnviandoComentario(null);
    }
  };

  const handleDeletarPost = async (postId) => {
    try {
      await axios.delete(`${API}/feed/posts/${postId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPosts(prev => prev.filter(p => p.id !== postId));
      toast.success('Post deletado');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao deletar post');
    }
  };

  const formatarData = (dataStr) => {
    if (!dataStr) return '';
    const data = new Date(dataStr);
    const agora = new Date();
    const diff = agora - data;
    
    const minutos = Math.floor(diff / 60000);
    const horas = Math.floor(diff / 3600000);
    const dias = Math.floor(diff / 86400000);
    
    if (minutos < 1) return 'Agora mesmo';
    if (minutos < 60) return `${minutos}m`;
    if (horas < 24) return `${horas}h`;
    if (dias < 7) return `${dias}d`;
    
    return data.toLocaleDateString('pt-BR');
  };

  // Componente para exibir as reações de um post
  const ReacoesDisplay = ({ post }) => {
    const reacoes = post.reacoes || {};
    const reacoesArray = Object.entries(reacoes).filter(([_, r]) => r.count > 0);
    
    if (reacoesArray.length === 0) return null;
    
    return (
      <div className="flex items-center gap-1 flex-wrap">
        {reacoesArray.map(([tipo, reacao]) => (
          <span 
            key={tipo} 
            className="flex items-center gap-0.5 bg-slate-700/50 rounded-full px-2 py-0.5 text-xs"
            title={`${reacao.count} ${reacao.nome}`}
          >
            <span className="text-sm">{reacao.emoji}</span>
            <span className="text-slate-300">{reacao.count}</span>
          </span>
        ))}
      </div>
    );
  };

  // Componente botão de reação
  const ReacaoButton = ({ post }) => {
    const [open, setOpen] = useState(false);
    const minhaReacao = post.minha_reacao;
    
    return (
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button 
            variant="ghost" 
            size="sm" 
            className={`${minhaReacao ? 'text-amber-400' : 'text-slate-400'} hover:text-amber-400 hover:bg-slate-700/50`}
            data-testid={`reaction-btn-${post.id}`}
          >
            {minhaReacao ? (
              <span className="text-lg mr-1">{REACOES[minhaReacao].emoji}</span>
            ) : (
              <Smile className="w-4 h-4 mr-1" />
            )}
            {post.total_reacoes || 0}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-2 bg-slate-800 border-slate-700" align="start">
          <div className="flex gap-1">
            {Object.entries(REACOES).map(([tipo, { emoji, nome }]) => (
              <Button
                key={tipo}
                variant="ghost"
                size="sm"
                className={`text-2xl hover:bg-slate-700 p-2 h-auto transition-transform hover:scale-125 ${minhaReacao === tipo ? 'bg-slate-700 ring-2 ring-amber-500' : ''}`}
                onClick={() => {
                  handleReagir(post.id, tipo);
                  setOpen(false);
                }}
                title={nome}
                data-testid={`reaction-${tipo}-${post.id}`}
              >
                {emoji}
              </Button>
            ))}
          </div>
        </PopoverContent>
      </Popover>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white" data-testid="feed-page">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Feed Social</h1>
                <p className="text-xs text-slate-400">Compartilhe suas conquistas</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Feed Principal */}
          <div className="lg:col-span-2 space-y-4">
            {/* Criar Post */}
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-4">
                <div className="flex gap-3">
                  <Avatar className="w-10 h-10">
                    <AvatarFallback className="bg-amber-500 text-white">
                      {user?.nome?.charAt(0) || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-3">
                    <Textarea
                      placeholder="O que você quer compartilhar?"
                      value={novoPost}
                      onChange={(e) => setNovoPost(e.target.value)}
                      className="bg-slate-700 border-slate-600 min-h-[80px] resize-none"
                      maxLength={1000}
                      data-testid="new-post-input"
                    />
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400">
                        {novoPost.length}/1000
                      </span>
                      <Button
                        onClick={handleCriarPost}
                        disabled={!novoPost.trim() || enviandoPost}
                        className="bg-amber-500 hover:bg-amber-600 text-black"
                        data-testid="publish-post-btn"
                      >
                        {enviandoPost ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <Send className="w-4 h-4 mr-1" />
                            Publicar
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Lista de Posts */}
            {posts.length === 0 ? (
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-12 text-center">
                  <Users className="w-16 h-16 mx-auto text-slate-600 mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Feed vazio</h3>
                  <p className="text-slate-400">Seja o primeiro a compartilhar algo!</p>
                </CardContent>
              </Card>
            ) : (
              posts.map((post) => (
                <Card key={post.id} className="bg-slate-800 border-slate-700" data-testid={`post-${post.id}`}>
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
                          <p className="font-semibold text-white">{post.autor?.nome}</p>
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
                      
                      {(post.autor_id === user?.id || user?.role === 'admin') && (
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
                              Deletar
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                    </div>
                    
                    {/* Conteúdo do Post */}
                    <p className="text-slate-200 whitespace-pre-wrap">{post.texto}</p>
                    
                    {/* Imagens existentes ainda são exibidas */}
                    {post.imagem_url && (
                      <img 
                        src={`${BACKEND_URL}${post.imagem_url}`} 
                        alt="Post" 
                        className="rounded-lg max-h-96 w-full object-cover"
                      />
                    )}
                    
                    {/* Reações Display */}
                    <ReacoesDisplay post={post} />
                    
                    {/* Ações - Reações e Comentários */}
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
                    </div>
                    
                    {/* Seção de Comentários */}
                    {showComentarios[post.id] && (
                      <div className="space-y-3 pt-3 border-t border-slate-700">
                        {/* Preview de comentários */}
                        {post.comentarios_preview?.map((com) => (
                          <div key={com.id} className="flex gap-2">
                            <Avatar className="w-8 h-8">
                              <AvatarFallback className="bg-slate-600 text-white text-xs">
                                {com.autor?.nome?.charAt(0)}
                              </AvatarFallback>
                            </Avatar>
                            <div className="bg-slate-700 rounded-lg px-3 py-2 flex-1">
                              <p className="text-sm text-white font-medium">{com.autor?.nome}</p>
                              <p className="text-sm text-slate-300">{com.texto}</p>
                            </div>
                          </div>
                        ))}
                        
                        {/* Input de novo comentário */}
                        <div className="flex gap-2">
                          <Avatar className="w-8 h-8">
                            <AvatarFallback className="bg-amber-500 text-white text-xs">
                              {user?.nome?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 flex gap-2">
                            <Input
                              placeholder="Escreva um comentário..."
                              value={comentarioTexto[post.id] || ''}
                              onChange={(e) => setComentarioTexto({ ...comentarioTexto, [post.id]: e.target.value })}
                              onKeyDown={(e) => e.key === 'Enter' && handleComentar(post.id)}
                              className="bg-slate-700 border-slate-600 text-sm"
                              maxLength={500}
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
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
            
            {/* Carregar Mais */}
            {hasMore && (
              <div className="text-center py-4">
                <Button
                  variant="outline"
                  onClick={() => fetchFeed(pagina + 1, true)}
                  disabled={loadingMore}
                  className="border-slate-600"
                >
                  {loadingMore ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : null}
                  Carregar mais
                </Button>
              </div>
            )}
          </div>

          {/* Sidebar - Trending */}
          <div className="space-y-4">
            <Card className="bg-slate-800 border-slate-700 sticky top-20">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2 text-amber-400">
                  <TrendingUp className="w-5 h-5" />
                  <h3 className="font-semibold">Em Alta</h3>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {trending.length === 0 ? (
                  <p className="text-slate-400 text-sm">Nenhum post em alta</p>
                ) : (
                  trending.map((post) => (
                    <div key={post.id} className="flex gap-3 p-2 rounded-lg hover:bg-slate-700/50 transition-colors cursor-pointer">
                      <Avatar className="w-8 h-8">
                        <AvatarFallback className="bg-amber-500 text-white text-xs">
                          {post.autor?.nome?.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white font-medium truncate">{post.autor?.nome}</p>
                        <p className="text-xs text-slate-400 truncate">{post.texto}</p>
                        <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                          {post.reacoes && Object.entries(post.reacoes)
                            .sort((a, b) => b[1].count - a[1].count)
                            .slice(0, 3)
                            .map(([tipo, r]) => (
                              <span key={tipo} className="flex items-center gap-0.5">
                                <span>{r.emoji}</span>
                                <span>{r.count}</span>
                              </span>
                            ))
                          }
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
            
            {/* Reações Disponíveis */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2 text-purple-400">
                  <Smile className="w-5 h-5" />
                  <h3 className="font-semibold">Reações</h3>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-2">
                  {Object.entries(REACOES).map(([tipo, { emoji, nome }]) => (
                    <div 
                      key={tipo} 
                      className="flex flex-col items-center p-2 rounded-lg hover:bg-slate-700/50 transition-colors"
                      title={nome}
                    >
                      <span className="text-2xl">{emoji}</span>
                      <span className="text-[10px] text-slate-400 mt-1">{nome}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeedPage;
