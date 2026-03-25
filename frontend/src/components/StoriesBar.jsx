import React, { useState, useEffect, useCallback } from 'react';
import { X, ChevronLeft, ChevronRight, Camera, Plus, Heart, Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { toast } from 'sonner';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const REACOES_STORY = [
  { tipo: 'coracao', emoji: '❤️' },
  { tipo: 'fogo', emoji: '🔥' },
  { tipo: 'aplausos', emoji: '👏' },
  { tipo: 'trofeu', emoji: '🏆' },
  { tipo: 'forca', emoji: '💪' },
];

// ============================================================
// StoryViewer - Visualizador fullscreen de stories
// ============================================================
const StoryViewer = ({ autores, startIndex, token, userId, onClose }) => {
  const [autorIdx, setAutorIdx] = useState(startIndex);
  const [storyIdx, setStoryIdx] = useState(0);
  const [progress, setProgress] = useState(0);
  const [enviandoReacao, setEnviandoReacao] = useState(false);
  const [reacaoVisivel, setReacaoVisivel] = useState(null);

  const autor = autores[autorIdx];
  const story = autor?.stories[storyIdx];
  const DURACAO = 10000; // 10 segundos por story

  // Marcar como visualizado
  useEffect(() => {
    if (!story || story.visto) return;
    axios.post(`${API}/feed/stories/${story.id}/visualizar`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    }).catch(() => {});
  }, [story?.id, token]);

  // Progresso automático
  useEffect(() => {
    if (!story) return;
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          handleNext();
          return 100;
        }
        return prev + (100 / (DURACAO / 50));
      });
    }, 50);
    return () => clearInterval(interval);
  }, [autorIdx, storyIdx]);

  const handleNext = useCallback(() => {
    if (storyIdx < autor.stories.length - 1) {
      setStoryIdx(s => s + 1);
    } else if (autorIdx < autores.length - 1) {
      setAutorIdx(a => a + 1);
      setStoryIdx(0);
    } else {
      onClose();
    }
  }, [storyIdx, autorIdx, autor, autores, onClose]);

  const handlePrev = useCallback(() => {
    if (storyIdx > 0) {
      setStoryIdx(s => s - 1);
    } else if (autorIdx > 0) {
      setAutorIdx(a => a - 1);
      setStoryIdx(0);
    }
  }, [storyIdx, autorIdx]);

  const handleReagir = async (tipo, emoji) => {
    if (enviandoReacao) return;
    setEnviandoReacao(true);
    setReacaoVisivel(emoji);
    try {
      await axios.post(`${API}/feed/stories/${story.id}/reagir`,
        { tipo_reacao: tipo },
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch {
      // silently fail
    } finally {
      setEnviandoReacao(false);
      setTimeout(() => setReacaoVisivel(null), 1200);
    }
  };

  if (!story) return null;

  const tempoAtras = () => {
    const diff = Date.now() - new Date(story.data_criacao).getTime();
    const h = Math.floor(diff / 3600000);
    if (h < 1) return `${Math.floor(diff / 60000)}min`;
    return `${h}h`;
  };

  return (
    <div className="fixed inset-0 z-[100] bg-black flex items-center justify-center" data-testid="story-viewer">
      {/* Overlay para fechar */}
      <div className="absolute inset-0" onClick={onClose} />

      {/* Container do story */}
      <div className="relative w-full max-w-[420px] h-full max-h-[90vh] mx-auto flex flex-col">
        {/* Barra de progresso */}
        <div className="flex gap-1 px-3 pt-3 z-10" data-testid="story-progress">
          {autor.stories.map((_, i) => (
            <div key={i} className="flex-1 h-[3px] bg-white/30 rounded-full overflow-hidden">
              <div
                className="h-full bg-white rounded-full transition-all duration-100"
                style={{
                  width: i < storyIdx ? '100%' : i === storyIdx ? `${progress}%` : '0%'
                }}
              />
            </div>
          ))}
        </div>

        {/* Header */}
        <div className="flex items-center gap-3 px-3 py-2 z-10">
          <Avatar className="w-8 h-8 border-2 border-white">
            <AvatarFallback className="bg-amber-500 text-white text-xs">
              {autor.autor_nome?.charAt(0) || '?'}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-semibold truncate">{autor.autor_nome}</p>
            <p className="text-white/60 text-xs">{tempoAtras()}</p>
          </div>
          <Button variant="ghost" size="icon" className="text-white hover:bg-white/10" onClick={onClose} data-testid="story-close-btn">
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Imagem */}
        <div className="flex-1 relative overflow-hidden rounded-xl mx-2">
          <img
            src={`${API.replace('/api', '')}/api${story.imagem_url}`}
            alt="Story"
            className="w-full h-full object-contain"
            data-testid="story-image"
          />

          {/* Áreas de toque para nav */}
          <div className="absolute inset-0 flex">
            <div className="w-1/3 h-full cursor-pointer" onClick={(e) => { e.stopPropagation(); handlePrev(); }} />
            <div className="w-1/3 h-full" />
            <div className="w-1/3 h-full cursor-pointer" onClick={(e) => { e.stopPropagation(); handleNext(); }} />
          </div>

          {/* Texto overlay */}
          {story.texto && (
            <div className="absolute bottom-16 left-0 right-0 px-4">
              <p className="text-white text-base font-medium drop-shadow-lg bg-black/40 backdrop-blur-sm rounded-lg px-3 py-2">
                {story.texto}
              </p>
            </div>
          )}

          {/* Animação de reação */}
          {reacaoVisivel && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <span className="text-7xl" style={{ animation: 'heartBurst 1.2s ease-out forwards' }}>
                {reacaoVisivel}
              </span>
            </div>
          )}

          {/* Setas de navegação */}
          {(autorIdx > 0 || storyIdx > 0) && (
            <button className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full p-1" onClick={(e) => { e.stopPropagation(); handlePrev(); }}>
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
          {(autorIdx < autores.length - 1 || storyIdx < autor.stories.length - 1) && (
            <button className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full p-1" onClick={(e) => { e.stopPropagation(); handleNext(); }}>
              <ChevronRight className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Reações rápidas */}
        <div className="flex items-center justify-center gap-4 py-3 z-10" data-testid="story-reactions">
          {REACOES_STORY.map(r => (
            <button
              key={r.tipo}
              className="text-2xl hover:scale-125 transition-transform active:scale-90"
              onClick={() => handleReagir(r.tipo, r.emoji)}
              data-testid={`story-react-${r.tipo}`}
            >
              {r.emoji}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};


// ============================================================
// StoriesBar - Barra de stories no topo do Feed
// ============================================================
const StoriesBar = ({ token, userId }) => {
  const [autores, setAutores] = useState([]);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [viewerStart, setViewerStart] = useState(0);
  const [podePostar, setPodePostar] = useState(true);
  const [uploading, setUploading] = useState(false);

  const fetchStories = async () => {
    try {
      const res = await axios.get(`${API}/feed/stories`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAutores(res.data.autores || []);
    } catch {}
  };

  const fetchRestantes = async () => {
    try {
      const res = await axios.get(`${API}/feed/stories/restantes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPodePostar(res.data.restantes > 0);
    } catch {}
  };

  useEffect(() => {
    if (token) {
      fetchStories();
    }
  }, [token]);

  const handleUploadStory = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['jpg','jpeg','png','webp','heic','heif'].includes(ext)) {
      toast.error('Formato não suportado.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Imagem muito grande. Máximo: 5MB');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('foto', file);
      await axios.post(`${API}/feed/stories`, formData, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Story publicado!');
      fetchStories();
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Erro ao publicar story');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const openViewer = (index) => {
    setViewerStart(index);
    setViewerOpen(true);
  };

  const closeViewer = () => {
    setViewerOpen(false);
    fetchStories(); // Refresh vistos
  };

  return (
    <>
      <div className="flex items-center gap-3 px-1 py-3 overflow-x-auto scrollbar-hide" data-testid="stories-bar">
        {/* Botão Adicionar Story */}
        <div className="flex flex-col items-center gap-1 flex-shrink-0">
          <input
            type="file"
            id="story-upload"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handleUploadStory}
            data-testid="story-file-input"
          />
          <button
            className={`w-16 h-16 rounded-full flex items-center justify-center border-2 border-dashed transition-colors ${
              podePostar && !uploading
                ? 'border-amber-500 text-amber-500 hover:bg-amber-500/10'
                : 'border-slate-600 text-slate-600 cursor-not-allowed'
            }`}
            onClick={() => podePostar && !uploading && document.getElementById('story-upload').click()}
            disabled={!podePostar || uploading}
            data-testid="add-story-btn"
          >
            {uploading ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : (
              <Plus className="w-6 h-6" />
            )}
          </button>
          <span className="text-[10px] text-slate-400 truncate max-w-[64px]">Seu Story</span>
        </div>

        {/* Stories dos autores */}
        {autores.map((autor, idx) => (
          <button
            key={autor.autor_id}
            className="flex flex-col items-center gap-1 flex-shrink-0"
            onClick={() => openViewer(idx)}
            data-testid={`story-avatar-${autor.autor_id}`}
          >
            <div className={`w-16 h-16 rounded-full p-[3px] ${
              autor.tem_nao_visto
                ? 'bg-gradient-to-tr from-amber-500 via-red-500 to-purple-500'
                : 'bg-slate-600'
            }`}>
              <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center overflow-hidden">
                <Avatar className="w-full h-full">
                  <AvatarFallback className="bg-slate-700 text-white text-lg">
                    {autor.autor_nome?.charAt(0) || '?'}
                  </AvatarFallback>
                </Avatar>
              </div>
            </div>
            <span className="text-[10px] text-slate-300 truncate max-w-[64px]">
              {autor.autor_nome?.split(' ')[0]}
            </span>
          </button>
        ))}

        {autores.length === 0 && !uploading && (
          <p className="text-xs text-slate-500 ml-2">Nenhum story ativo</p>
        )}
      </div>

      {/* Viewer fullscreen */}
      {viewerOpen && autores.length > 0 && (
        <StoryViewer
          autores={autores}
          startIndex={viewerStart}
          token={token}
          userId={userId}
          onClose={closeViewer}
        />
      )}
    </>
  );
};

export default StoriesBar;
