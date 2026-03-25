// /app/frontend/src/pages/FeedPage.jsx
// Feed Social da Plataforma com Reações, Comentários e Posts Automáticos de Conquistas

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Send, Loader2, ArrowLeft, MoreHorizontal,
  TrendingUp, Clock, Trash2, Users, Smile, MessageCircle,
  Trophy, Medal, PartyPopper, Star, Zap, Shield, Camera, X, Image as ImageIcon, Heart
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
  trofeu: { emoji: "🏆", nome: "Campeão" },
  parabens: { emoji: "🎊", nome: "Parabéns" }
};

// Tipos de posts automáticos
const TIPOS_POST = {
  texto: { label: "Texto", cor: "bg-slate-600" },
  foto: { label: "Foto", cor: "bg-teal-600", icone: Camera },
  conquista: { label: "Conquista", cor: "bg-purple-600", icone: Trophy },
  corrida_aprovada: { label: "Resultado", cor: "bg-green-600", icone: Medal },
  resultado: { label: "Resultado", cor: "bg-blue-600", icone: Zap }
};

const FeedPage = () => {
  const navigate = useNavigate();
  const { user, token, isAdmin } = useAuth();
  const [loading, setLoading] = useState(true);
  const [posts, setPosts] = useState([]);
  const [trending, setTrending] = useState([]);
  const [pagina, setPagina] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  
  // Novo post
  const [novoPost, setNovoPost] = useState('');
  const [enviandoPost, setEnviandoPost] = useState(false);
  
  // Foto do post
  const [fotoSelecionada, setFotoSelecionada] = useState(null);
  const [fotoPreview, setFotoPreview] = useState(null);
  const [fotosRestantes, setFotosRestantes] = useState(2);
  
  // Comentários
  const [comentarioTexto, setComentarioTexto] = useState({});
  const [enviandoComentario, setEnviandoComentario] = useState(null);
  const [showComentarios, setShowComentarios] = useState({});
  
  // Parabéns
  const [enviandoParabens, setEnviandoParabens] = useState(null);

  // Double-tap like
  const [heartAnimation, setHeartAnimation] = useState({});
  const lastTapRef = React.useRef({});

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchFeed();
    fetchTrending();
    fetchFotosRestantes();
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

  const fetchFotosRestantes = async () => {
    try {
      const response = await axios.get(`${API}/feed/fotos-restantes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFotosRestantes(response.data.restantes);
    } catch (error) {
      console.error('Erro ao buscar fotos restantes:', error);
    }
  };

  const handleSelecionarFoto = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['jpg','jpeg','png','webp','heic','heif'].includes(ext)) {
      toast.error('Formato não suportado. Use JPG, PNG ou WebP.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Imagem muito grande. Máximo: 5MB');
      return;
    }

    setFotoSelecionada(file);
    const reader = new FileReader();
    reader.onload = (ev) => setFotoPreview(ev.target.result);
    reader.readAsDataURL(file);
  };

  const handleRemoverFoto = () => {
    setFotoSelecionada(null);
    setFotoPreview(null);
  };

  const handleCriarPost = async () => {
    if (!novoPost.trim() && !fotoSelecionada) return;
    
    setEnviandoPost(true);
    try {
      if (fotoSelecionada) {
        // Post com foto
        const formData = new FormData();
        formData.append('foto', fotoSelecionada);
        formData.append('texto', novoPost);
        
        const response = await axios.post(
          `${API}/feed/posts/com-foto`,
          formData,
          { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' } }
        );
        
        toast.success('Foto publicada!');
        setFotosRestantes(response.data.fotos_restantes_hoje);
      } else {
        // Post só texto
        await axios.post(
          `${API}/feed/posts`,
          { texto: novoPost, tipo: 'texto' },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Post publicado!');
      }
      
      setNovoPost('');
      handleRemoverFoto();
      fetchFeed();
    } catch (error) {
      const errorData = error.response?.data?.detail;
      
      if (error.response?.status === 429) {
        toast.error(typeof errorData === 'string' ? errorData : 'Limite de fotos diário atingido!');
      } else if (errorData && typeof errorData === 'object' && errorData.message) {
        const { message, nivel, educativo } = errorData;
        if (nivel === 'grave') {
          toast.error(message, { duration: 8000 });
          if (educativo) toast.warning(educativo, { duration: 10000 });
        } else if (nivel === 'medio') {
          toast.warning(message, { duration: 6000 });
          if (educativo) toast.info(educativo, { duration: 8000 });
        } else {
          toast.info(message, { duration: 5000 });
        }
      } else {
        toast.error(typeof errorData === 'string' ? errorData : 'Erro ao publicar');
      }
    } finally {
      setEnviandoPost(false);
    }
  };

  const handleDoubleTap = (postId) => {
    const now = Date.now();
    const lastTap = lastTapRef.current[postId] || 0;

    if (now - lastTap < 350) {
      // Double tap detected
      setHeartAnimation(prev => ({ ...prev, [postId]: true }));
      handleReagir(postId, 'coracao');
      setTimeout(() => {
        setHeartAnimation(prev => ({ ...prev, [postId]: false }));
      }, 1000);
      lastTapRef.current[postId] = 0;
    } else {
      lastTapRef.current[postId] = now;
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
      const response = await axios.post(
        `${API}/feed/posts/${postId}/comentarios`,
        { texto },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setComentarioTexto({ ...comentarioTexto, [postId]: '' });
      toast.success('Comentário adicionado!');
      
      // Mostrar selo se ganhou
      if (response.data?.selo_respeitoso) {
        toast.success('🏅 Parabéns! Você ganhou o Selo de Atleta Respeitoso!', {
          duration: 5000
        });
      }
      
      // Recarregar feed para atualizar comentários
      fetchFeed();
    } catch (error) {
      console.log('Erro de moderação (debug):', error.response?.data);
      const errorData = error.response?.data?.detail;
      
      // Verificar se é erro de moderação (objeto com detalhes)
      if (errorData && typeof errorData === 'object' && errorData.message) {
        const { message, nivel, educativo } = errorData;
        
        // Mostrar mensagem baseada no nível
        if (nivel === 'grave') {
          toast.error(`🚫 ${message}`, { duration: 8000 });
          if (educativo) {
            setTimeout(() => {
              toast.warning(`💡 ${educativo}`, { duration: 10000 });
            }, 500);
          }
        } else if (nivel === 'medio') {
          toast.warning(`⚠️ ${message}`, { duration: 6000 });
          if (educativo) {
            setTimeout(() => {
              toast.info(`💡 ${educativo}`, { duration: 8000 });
            }, 500);
          }
        } else {
          toast.info(`ℹ️ ${message || 'Seu comentário precisa de revisão.'}`, { duration: 5000 });
        }
      } else {
        // Erro comum (string)
        toast.error(typeof errorData === 'string' ? errorData : 'Erro ao comentar');
      }
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

  const handleParabens = async (postId) => {
    setEnviandoParabens(postId);
    try {
      await axios.post(
        `${API}/feed/posts/${postId}/parabens`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('🎊 Parabéns enviado!');
      
      // Atualizar o post localmente para mostrar a reação
      setPosts(prev => prev.map(post => {
        if (post.id === postId) {
          const novasReacoes = { ...post.reacoes };
          if (!novasReacoes.parabens) {
            novasReacoes.parabens = {
              count: 0,
              emoji: "🎊",
              nome: "Parabéns"
            };
          }
          novasReacoes.parabens.count += 1;
          
          return {
            ...post,
            reacoes: novasReacoes,
            minha_reacao: "parabens",
            total_reacoes: (post.total_reacoes || 0) + 1
          };
        }
        return post;
      }));
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao enviar parabéns');
    } finally {
      setEnviandoParabens(null);
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

  // Funções de Admin para gerenciar comentários
  const handleFixarComentario = async (comentarioId) => {
    try {
      const response = await axios.post(
        `${API}/feed/admin/comentarios/${comentarioId}/fixar`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success(response.data.message);
      fetchFeed(); // Recarregar posts para atualizar UI
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao fixar comentário');
    }
  };

  const handleExcluirComentario = async (comentarioId, postId) => {
    if (!confirm('Tem certeza que deseja excluir este comentário?')) return;
    
    try {
      await axios.delete(
        `${API}/feed/admin/comentarios/${comentarioId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Comentário excluído');
      
      // Atualizar localmente
      setPosts(prev => prev.map(post => {
        if (post.id === postId) {
          return {
            ...post,
            comentarios_preview: post.comentarios_preview?.filter(c => c.id !== comentarioId),
            total_comentarios: Math.max(0, (post.total_comentarios || 0) - 1)
          };
        }
        return post;
      }));
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao excluir comentário');
    }
  };

  const handleBloquearUsuario = async (usuarioId, usuarioNome) => {
    const motivo = prompt(`Motivo para bloquear ${usuarioNome}:`, 'Violação das regras do feed');
    if (!motivo) return;
    
    try {
      await axios.post(
        `${API}/feed/admin/usuarios/bloquear`,
        { usuario_id: usuarioId, motivo },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success(`${usuarioNome} foi bloqueado de comentar no feed`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao bloquear usuário');
    }
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
              <span className="text-lg mr-1">{REACOES[minhaReacao]?.emoji || "👏"}</span>
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

  // Componente para exibir conteúdo especial de posts automáticos
  const PostConteudoEspecial = ({ post }) => {
    const tipo = post.tipo;
    const isAutoGerado = post.auto_gerado;
    
    // Post de conquista/insígnia
    if (tipo === 'conquista' && post.conquista_dados) {
      const { nome, descricao, emoji } = post.conquista_dados;
      return (
        <div className="bg-gradient-to-r from-purple-900/50 to-indigo-900/50 rounded-xl p-4 border border-purple-500/30">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/30">
              <span className="text-2xl">{emoji || "🏆"}</span>
            </div>
            <div>
              <Badge className="bg-purple-600 text-white mb-1">Nova Conquista!</Badge>
              <h4 className="font-bold text-white text-lg">{nome}</h4>
            </div>
          </div>
          {descricao && (
            <p className="text-purple-200 text-sm ml-15">{descricao}</p>
          )}
        </div>
      );
    }
    
    // Post de corrida aprovada
    if (tipo === 'corrida_aprovada' && post.resultado_dados) {
      const { nome_corrida, colocacao, pontos, distancia, tempo } = post.resultado_dados;
      const medalhas = { 1: "🥇", 2: "🥈", 3: "🥉" };
      const medalha = medalhas[colocacao] || "🏃";
      
      return (
        <div className="bg-gradient-to-r from-green-900/50 to-emerald-900/50 rounded-xl p-4 border border-green-500/30">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center shadow-lg shadow-green-500/30">
              <span className="text-2xl">{medalha}</span>
            </div>
            <div>
              <Badge className="bg-green-600 text-white mb-1">Resultado Aprovado!</Badge>
              <h4 className="font-bold text-white text-lg">{nome_corrida}</h4>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 ml-15">
            {colocacao > 0 && (
              <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                <p className="text-xs text-slate-400">Colocação</p>
                <p className="text-lg font-bold text-white">{colocacao}º</p>
              </div>
            )}
            <div className="bg-slate-800/50 rounded-lg p-2 text-center">
              <p className="text-xs text-slate-400">Pontos</p>
              <p className="text-lg font-bold text-amber-400">+{pontos}</p>
            </div>
            {distancia && (
              <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                <p className="text-xs text-slate-400">Distância</p>
                <p className="text-lg font-bold text-white">{distancia}</p>
              </div>
            )}
            {tempo && (
              <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                <p className="text-xs text-slate-400">Tempo</p>
                <p className="text-lg font-bold text-white">{tempo}</p>
              </div>
            )}
          </div>
        </div>
      );
    }
    
    return null;
  };

  // Componente botão de Parabéns para posts especiais
  const BotaoParabens = ({ post }) => {
    const isConquistaOuResultado = post.tipo === 'conquista' || post.tipo === 'corrida_aprovada';
    const jaParabenizou = post.minha_reacao === 'parabens';
    
    if (!isConquistaOuResultado) return null;
    
    return (
      <Button
        variant={jaParabenizou ? "default" : "outline"}
        size="sm"
        onClick={() => handleParabens(post.id)}
        disabled={enviandoParabens === post.id || jaParabenizou}
        className={`${jaParabenizou 
          ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white border-0' 
          : 'border-purple-500/50 text-purple-400 hover:bg-purple-500/20'
        }`}
        data-testid={`parabens-btn-${post.id}`}
      >
        {enviandoParabens === post.id ? (
          <Loader2 className="w-4 h-4 animate-spin mr-1" />
        ) : (
          <PartyPopper className="w-4 h-4 mr-1" />
        )}
        {jaParabenizou ? 'Parabenizado!' : 'Parabéns!'}
      </Button>
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
      <style>{`
        @keyframes heartBurst {
          0% { transform: scale(0); opacity: 0; }
          15% { transform: scale(1.3); opacity: 1; }
          30% { transform: scale(0.95); opacity: 1; }
          45% { transform: scale(1.1); opacity: 1; }
          80% { transform: scale(1); opacity: 0.8; }
          100% { transform: scale(1); opacity: 0; }
        }
      `}</style>
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
                      placeholder={fotoSelecionada ? "Adicione uma legenda..." : "O que você quer compartilhar?"}
                      value={novoPost}
                      onChange={(e) => setNovoPost(e.target.value)}
                      className="bg-slate-700 border-slate-600 min-h-[80px] resize-none text-white font-semibold placeholder:text-slate-400 placeholder:font-normal"
                      maxLength={1000}
                      data-testid="new-post-input"
                    />

                    {/* Preview da foto selecionada */}
                    {fotoPreview && (
                      <div className="relative inline-block">
                        <img
                          src={fotoPreview}
                          alt="Preview"
                          className="rounded-lg max-h-60 object-cover border border-slate-600"
                          data-testid="foto-preview"
                        />
                        <Button
                          variant="ghost"
                          size="icon"
                          className="absolute top-2 right-2 bg-black/60 hover:bg-black/80 text-white h-7 w-7 rounded-full"
                          onClick={handleRemoverFoto}
                          data-testid="remover-foto-btn"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {/* Botão de foto */}
                        <input
                          type="file"
                          id="foto-input"
                          accept="image/jpeg,image/png,image/webp,image/heic,image/heif"
                          className="hidden"
                          onChange={handleSelecionarFoto}
                          data-testid="foto-file-input"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          className={`text-slate-400 hover:text-green-400 hover:bg-slate-700/50 ${fotosRestantes === 0 ? 'opacity-40 cursor-not-allowed' : ''}`}
                          onClick={() => fotosRestantes > 0 && document.getElementById('foto-input').click()}
                          disabled={fotosRestantes === 0 || !!fotoSelecionada}
                          data-testid="add-foto-btn"
                        >
                          <Camera className="w-5 h-5 mr-1" />
                          Foto
                        </Button>
                        <span className="text-xs text-slate-500">
                          {fotoSelecionada
                            ? `${fotosRestantes} foto${fotosRestantes !== 1 ? 's' : ''} restante${fotosRestantes !== 1 ? 's' : ''} hoje`
                            : `${fotosRestantes}/${2} fotos hoje`
                          }
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-400">
                          {novoPost.length}/1000
                        </span>
                        <Button
                          onClick={handleCriarPost}
                          disabled={(!novoPost.trim() && !fotoSelecionada) || enviandoPost}
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
                          <div className="flex items-center gap-2">
                            <p className="font-semibold text-white">{post.autor?.nome}</p>
                            {/* Badge de tipo de post automático */}
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
                              <>
                                <DropdownMenuItem 
                                  className="text-amber-400 cursor-pointer"
                                  onClick={() => setShowComentarios({ ...showComentarios, [post.id]: true })}
                                >
                                  <MessageCircle className="w-4 h-4 mr-2" />
                                  Gerenciar Comentários ({post.total_comentarios})
                                </DropdownMenuItem>
                              </>
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
                          className="rounded-xl max-h-[500px] w-full object-cover border border-slate-700"
                          data-testid={`post-image-${post.id}`}
                          loading="lazy"
                          draggable={false}
                        />
                        {/* Animação de coração no duplo-toque */}
                        {heartAnimation[post.id] && (
                          <div className="absolute inset-0 flex items-center justify-center pointer-events-none" data-testid={`heart-animation-${post.id}`}>
                            <Heart
                              className="w-24 h-24 text-red-500 fill-red-500 drop-shadow-lg"
                              style={{
                                animation: 'heartBurst 1s ease-out forwards',
                              }}
                            />
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Reações Display */}
                    <ReacoesDisplay post={post} />
                    
                    {/* Ações - Reações, Comentários e Parabéns */}
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
                      
                      {/* Botão de Parabéns para posts de conquistas/resultados */}
                      <BotaoParabens post={post} />
                    </div>
                    
                    {/* Seção de Comentários */}
                    {showComentarios[post.id] && (
                      <div className="space-y-3 pt-3 border-t border-slate-700">
                        {/* Preview de comentários */}
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
                                {/* Selo de Atleta Respeitoso */}
                                {com.autor?.selo_respeitoso && (
                                  <span title="Atleta Respeitoso - Sem infrações" className="text-lg">🏅</span>
                                )}
                                {com.fixado && (
                                  <Badge className="bg-amber-500/20 text-amber-400 text-xs py-0">Fixado</Badge>
                                )}
                              </div>
                              <p className="text-sm text-slate-300 break-all">{com.texto}</p>
                            </div>
                            {/* Menu de Admin para comentários - sempre visível para admins */}
                            {isAdmin && (
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    className="text-amber-400 hover:text-amber-300 hover:bg-amber-500/20 h-8 w-8"
                                    data-testid={`admin-comment-menu-${com.id}`}
                                  >
                                    <MoreHorizontal className="w-4 h-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="bg-slate-800 border-slate-700">
                                  <DropdownMenuItem 
                                    className="text-amber-400 cursor-pointer"
                                    onClick={() => handleFixarComentario(com.id)}
                                    data-testid={`fixar-comment-${com.id}`}
                                  >
                                    <Star className="w-4 h-4 mr-2" />
                                    {com.fixado ? 'Desfixar' : 'Fixar'}
                                  </DropdownMenuItem>
                                  <DropdownMenuItem 
                                    className="text-red-400 cursor-pointer"
                                    onClick={() => handleExcluirComentario(com.id, post.id)}
                                    data-testid={`excluir-comment-${com.id}`}
                                  >
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Excluir
                                  </DropdownMenuItem>
                                  <DropdownMenuItem 
                                    className="text-orange-400 cursor-pointer"
                                    onClick={() => handleBloquearUsuario(com.autor_id, com.autor?.nome)}
                                    data-testid={`bloquear-user-${com.id}`}
                                  >
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

          {/* Sidebar - Apenas Admin */}
          <div className="space-y-4">
            {/* Painel de Admin - Gerenciar Comentários */}
            {isAdmin && (
              <Card className="bg-gradient-to-br from-amber-900/30 to-orange-900/30 border-amber-500/30 sticky top-20">
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2 text-amber-400">
                    <Shield className="w-5 h-5" />
                    <h3 className="font-semibold">Admin - Comentários</h3>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-xs text-slate-400">
                    Gerencie posts e comentários do feed.
                  </p>
                  
                  {/* Botão Limpar Posts */}
                  <Button 
                    variant="outline" 
                    size="sm"
                    className="w-full border-red-500/50 text-red-400 hover:bg-red-500/20"
                    onClick={async () => {
                      if (confirm('⚠️ ATENÇÃO: Limpar TODOS os posts do feed? Esta ação não pode ser desfeita!')) {
                        try {
                          const response = await axios.delete(`${API}/feed/admin/posts/limpar-todos`, {
                            headers: { Authorization: `Bearer ${token}` }
                          });
                          toast.success(response.data.message || 'Posts limpos com sucesso!');
                          fetchFeed();
                        } catch (error) {
                          toast.error(error.response?.data?.detail || 'Erro ao limpar posts');
                        }
                      }
                    }}
                    data-testid="btn-limpar-posts"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Limpar Todos Posts
                  </Button>
                  
                  {/* Botão Limpar Comentários */}
                  <Button 
                    variant="outline" 
                    size="sm"
                    className="w-full border-amber-500/50 text-amber-400 hover:bg-amber-500/20"
                    onClick={async () => {
                      if (confirm('Limpar TODOS os comentários não fixados? Esta ação não pode ser desfeita.')) {
                        try {
                          await axios.delete(`${API}/feed/admin/comentarios/limpar-todos`, {
                            headers: { Authorization: `Bearer ${token}` }
                          });
                          toast.success('Comentários limpos com sucesso!');
                          fetchFeed();
                        } catch (error) {
                          toast.error(error.response?.data?.detail || 'Erro ao limpar comentários');
                        }
                      }
                    }}
                    data-testid="btn-limpar-comentarios"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Limpar Todos Comentários
                  </Button>
                  <p className="text-[10px] text-slate-500 text-center">
                    Comentários fixados serão preservados
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeedPage;
