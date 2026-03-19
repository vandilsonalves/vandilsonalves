// /app/frontend/src/pages/FeedPage.jsx
// Feed Social da Plataforma (apenas curtidas)

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { 
  Heart, Send, Image, Loader2, ArrowLeft, MoreHorizontal,
  TrendingUp, Clock, Trophy, Award, Trash2, X, Users
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
  const [imagemPost, setImagemPost] = useState(null);
  const imagemInputRef = useRef(null);

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
      const response = await axios.post(
        `${API}/feed/posts`,
        { texto: novoPost, tipo: 'texto' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Se tiver imagem, fazer upload
      if (imagemPost && response.data.post_id) {
        const formData = new FormData();
        formData.append('imagem', imagemPost);
        
        await axios.post(
          `${API}/feed/posts/${response.data.post_id}/imagem`,
          formData,
          { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' } }
        );
      }
      
      toast.success('Post publicado!');
      setNovoPost('');
      setImagemPost(null);
      fetchFeed();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao publicar post');
    } finally {
      setEnviandoPost(false);
    }
  };

  const handleCurtir = async (postId) => {
    try {
      const response = await axios.post(
        `${API}/feed/posts/${postId}/curtir`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Atualizar estado local
      setPosts(posts.map(post => {
        if (post.id === postId) {
          return {
            ...post,
            curtido: response.data.curtido,
            total_curtidas: post.total_curtidas + (response.data.curtido ? 1 : -1)
          };
        }
        return post;
      }));
    } catch (error) {
      toast.error('Erro ao curtir post');
    }
  };

  const handleDeletarPost = async (postId) => {
    if (!window.confirm('Tem certeza que deseja deletar este post?')) return;
    
    try {
      await axios.delete(`${API}/feed/posts/${postId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Post deletado');
      setPosts(posts.filter(p => p.id !== postId));
    } catch (error) {
      toast.error('Erro ao deletar post');
    }
  };

  const formatarData = (data) => {
    const d = new Date(data);
    const agora = new Date();
    const diffMs = agora - d;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHoras = Math.floor(diffMs / 3600000);
    const diffDias = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Agora';
    if (diffMins < 60) return `${diffMins}min`;
    if (diffHoras < 24) return `${diffHoras}h`;
    if (diffDias < 7) return `${diffDias}d`;
    return d.toLocaleDateString('pt-BR');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => navigate(-1)} className="text-slate-400">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Feed Social</h1>
              <p className="text-slate-400 text-sm">Compartilhe com a comunidade</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Feed Principal */}
          <div className="lg:col-span-2 space-y-4">
            {/* Criar Post */}
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-4">
                <div className="flex gap-3">
                  <Avatar className="w-10 h-10">
                    {user?.foto_url ? (
                      <AvatarImage src={user.foto_url.startsWith('http') ? user.foto_url : `${BACKEND_URL}${user.foto_url}`} />
                    ) : null}
                    <AvatarFallback className="bg-amber-500 text-white">
                      {user?.nome?.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 space-y-3">
                    <Textarea
                      placeholder="O que você quer compartilhar?"
                      value={novoPost}
                      onChange={(e) => setNovoPost(e.target.value)}
                      rows={3}
                      className="bg-slate-700 border-slate-600 resize-none"
                      maxLength={1000}
                    />
                    
                    {imagemPost && (
                      <div className="relative inline-block">
                        <img 
                          src={URL.createObjectURL(imagemPost)} 
                          alt="Preview" 
                          className="max-h-32 rounded-lg"
                        />
                        <Button
                          size="icon"
                          variant="destructive"
                          className="absolute -top-2 -right-2 w-6 h-6"
                          onClick={() => setImagemPost(null)}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <div className="flex gap-2">
                        <input
                          type="file"
                          ref={imagemInputRef}
                          onChange={(e) => setImagemPost(e.target.files?.[0])}
                          accept="image/*"
                          className="hidden"
                        />
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="text-slate-400"
                          onClick={() => imagemInputRef.current?.click()}
                        >
                          <Image className="w-4 h-4 mr-1" />
                          Foto
                        </Button>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">{novoPost.length}/1000</span>
                        <Button 
                          onClick={handleCriarPost}
                          disabled={!novoPost.trim() || enviandoPost}
                          className="bg-amber-500 hover:bg-amber-600"
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
                </div>
              </CardContent>
            </Card>

            {/* Posts */}
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
                <Card key={post.id} className="bg-slate-800 border-slate-700">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <Avatar className="w-10 h-10 cursor-pointer" onClick={() => navigate(`/atleta/${post.autor?.id}`)}>
                          {post.autor?.foto_url ? (
                            <AvatarImage src={post.autor.foto_url.startsWith('http') ? post.autor.foto_url : `${BACKEND_URL}${post.autor.foto_url}`} />
                          ) : null}
                          <AvatarFallback className="bg-amber-500 text-white">
                            {post.autor?.nome?.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="text-white font-medium hover:underline cursor-pointer" onClick={() => navigate(`/atleta/${post.autor?.id}`)}>
                            {post.autor?.nome}
                          </p>
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
                  </CardHeader>
                  
                  <CardContent className="pt-0 space-y-3">
                    {/* Texto do post */}
                    <p className="text-slate-200 whitespace-pre-wrap">{post.texto}</p>
                    
                    {/* Imagem */}
                    {post.imagem_url && (
                      <img 
                        src={post.imagem_url.startsWith('http') ? post.imagem_url : `${BACKEND_URL}${post.imagem_url}`}
                        alt="Post"
                        className="rounded-lg max-h-96 w-full object-cover"
                      />
                    )}
                    
                    {/* Dados de resultado */}
                    {post.tipo === 'resultado' && post.resultado_dados && (
                      <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-lg p-4 border border-amber-500/20">
                        <div className="flex items-center gap-2 mb-2">
                          <Trophy className="w-5 h-5 text-amber-500" />
                          <span className="text-white font-medium">{post.resultado_dados.corrida_nome}</span>
                        </div>
                        <div className="text-sm text-slate-300">
                          <p>Posição: {post.resultado_dados.posicao}º lugar</p>
                          <p>Tempo: {post.resultado_dados.tempo}</p>
                        </div>
                      </div>
                    )}
                    
                    {/* Dados de conquista */}
                    {post.tipo === 'conquista' && post.conquista_dados && (
                      <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg p-4 border border-purple-500/20">
                        <div className="flex items-center gap-2">
                          <Award className="w-5 h-5 text-purple-500" />
                          <span className="text-white font-medium">{post.conquista_dados.nome}</span>
                        </div>
                      </div>
                    )}
                    
                    {/* Ações - Apenas curtidas */}
                    <div className="flex items-center gap-4 pt-2 border-t border-slate-700">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className={`${post.curtido ? 'text-red-400' : 'text-slate-400'} hover:text-red-400`}
                        onClick={() => handleCurtir(post.id)}
                        data-testid={`like-btn-${post.id}`}
                      >
                        <Heart className={`w-4 h-4 mr-1 ${post.curtido ? 'fill-current' : ''}`} />
                        {post.total_curtidas} {post.total_curtidas === 1 ? 'curtida' : 'curtidas'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}

            {/* Load More */}
            {hasMore && (
              <div className="text-center">
                <Button 
                  variant="outline" 
                  onClick={() => fetchFeed(pagina + 1, true)}
                  disabled={loadingMore}
                  className="border-slate-600"
                >
                  {loadingMore ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : null}
                  Carregar mais
                </Button>
              </div>
            )}
          </div>

          {/* Sidebar - Trending */}
          <div className="space-y-4">
            <Card className="bg-slate-800 border-slate-700 sticky top-4">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-amber-500" />
                  <h3 className="font-semibold text-white">Em Alta</h3>
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
                          <span className="flex items-center gap-1">
                            <Heart className="w-3 h-3 text-red-400" /> {post.total_curtidas}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeedPage;
