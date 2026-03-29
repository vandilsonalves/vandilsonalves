import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { 
  Send, Paperclip, Heart, Trash2, FileText, X, Download, Loader2, MessageSquare, Users, MessageCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { MentionInput, renderWithMentions } from '@/components/MentionInput';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const FeedEquipe = ({ token, userId, equipe, isDonoAssessoria = false }) => {
  const [posts, setPosts] = useState([]);
  const [texto, setTexto] = useState('');
  const [arquivo, setArquivo] = useState(null);
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [threadOpen, setThreadOpen] = useState(null);
  const [mencionadosPost, setMencionadosPost] = useState([]);
  const fileInputRef = useRef(null);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchPosts = useCallback(async (pg = 1, append = false) => {
    try {
      const res = await axios.get(`${API}/equipe/feed?page=${pg}&limit=20`, { headers });
      if (append) {
        setPosts(prev => [...prev, ...res.data.posts]);
      } else {
        setPosts(res.data.posts);
      }
      setHasMore(res.data.has_more);
      setPage(pg);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchPosts(); }, [fetchPosts]);

  const enviar = async () => {
    if (!texto.trim() && !arquivo) return;
    setSending(true);
    try {
      const formData = new FormData();
      formData.append('mensagem', texto);
      formData.append('mencionados', mencionadosPost.join(','));
      if (arquivo) formData.append('arquivo', arquivo);
      await axios.post(`${API}/equipe/feed/enviar`, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' }
      });
      setTexto('');
      setArquivo(null);
      setMencionadosPost([]);
      await fetchPosts(1);
      toast.success('Publicado!');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Erro ao publicar');
    } finally { setSending(false); }
  };

  const curtir = async (postId) => {
    try {
      const res = await axios.post(`${API}/equipe/feed/${postId}/curtir`, {}, { headers });
      setPosts(prev => prev.map(p => {
        if (p.id !== postId) return p;
        const curtidas = [...(p.curtidas || [])];
        if (res.data.curtiu) curtidas.push(userId);
        else { const idx = curtidas.indexOf(userId); if (idx > -1) curtidas.splice(idx, 1); }
        return { ...p, curtidas };
      }));
    } catch { toast.error('Erro ao curtir'); }
  };

  const deletar = async (postId) => {
    if (!window.confirm('Remover este post?')) return;
    try {
      await axios.delete(`${API}/equipe/feed/${postId}`, { headers });
      setPosts(prev => prev.filter(p => p.id !== postId));
      toast.success('Post removido');
    } catch { toast.error('Erro ao remover'); }
  };

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 10 * 1024 * 1024) { toast.error('Máx 10MB'); return; }
    setArquivo(f);
  };

  if (!equipe || equipe.toUpperCase() === 'INDIVIDUAL' || equipe.toUpperCase() === 'SEM EQUIPE') {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-500">
        <Users className="w-12 h-12 mb-3 opacity-40" />
        <p className="font-medium">Você não pertence a nenhuma equipe</p>
        <p className="text-sm">Entre em uma assessoria para acessar o Feed.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="feed-equipe">
      <div className="flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-amber-500" />
        <h2 className="text-xl font-bold text-white">Feed da Equipe</h2>
        <Badge variant="outline" className="text-amber-400 border-amber-500/40 ml-auto">{equipe}</Badge>
      </div>

      {/* Compose */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4 space-y-3">
          <Textarea
            value={texto}
            onChange={e => setTexto(e.target.value)}
            placeholder="O que está acontecendo na equipe? (use @ para mencionar)"
            className="bg-slate-900 border-slate-700 text-white min-h-20 resize-none"
            data-testid="feed-input"
          />
          {arquivo && (
            <div className="flex items-center gap-2 text-sm text-slate-300 bg-slate-700 rounded-lg px-3 py-2">
              <FileText className="w-4 h-4" />
              <span className="truncate flex-1">{arquivo.name}</span>
              <button onClick={() => setArquivo(null)} className="hover:text-red-400"><X className="w-4 h-4" /></button>
            </div>
          )}
          <div className="flex items-center gap-2">
            <input ref={fileInputRef} type="file" accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg,.gif,.webp" className="hidden" onChange={handleFile} />
            <Button variant="ghost" size="sm" onClick={() => fileInputRef.current?.click()} className="text-slate-400" data-testid="feed-btn-anexar">
              <Paperclip className="w-4 h-4 mr-1" /> Anexar
            </Button>
            <div className="flex-1" />
            <Button onClick={enviar} disabled={sending || (!texto.trim() && !arquivo)} className="bg-amber-500 hover:bg-amber-600" size="sm" data-testid="feed-btn-publicar">
              {sending ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Send className="w-4 h-4 mr-1" />}
              Publicar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Posts */}
      {loading ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-amber-500" /></div>
      ) : posts.length === 0 ? (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-8 text-center text-slate-500">
            <MessageSquare className="w-10 h-10 mx-auto mb-2 opacity-40" />
            <p>Nenhuma publicação ainda.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {posts.map(post => (
            <PostCard
              key={post.id}
              post={post}
              userId={userId}
              isDonoAssessoria={isDonoAssessoria}
              onCurtir={curtir}
              onDeletar={deletar}
              threadOpen={threadOpen === post.id}
              onToggleThread={() => setThreadOpen(threadOpen === post.id ? null : post.id)}
              token={token}
              headers={headers}
            />
          ))}
          {hasMore && (
            <Button variant="outline" className="w-full" onClick={() => fetchPosts(page + 1, true)} data-testid="feed-btn-mais">
              Carregar mais
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

const PostCard = ({ post, userId, isDonoAssessoria, onCurtir, onDeletar, threadOpen, onToggleThread, token, headers }) => {
  const isOwn = post.autor_id === userId;
  const curtiu = (post.curtidas || []).includes(userId);

  return (
    <Card className="bg-slate-800 border-slate-700" data-testid={`feed-post-${post.id}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <Avatar className="w-10 h-10 shrink-0">
            <AvatarImage src={post.autor_foto?.startsWith('http') ? post.autor_foto : `${BACKEND_URL}${post.autor_foto}`} />
            <AvatarFallback className="bg-amber-500 text-white">{post.autor_nome?.charAt(0)}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-white text-sm">{post.autor_nome}</span>
              <span className="text-xs text-slate-500">
                {new Date(post.data_envio).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })}
                {' '}
                {new Date(post.data_envio).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
              </span>
              {(isOwn || isDonoAssessoria) && (
                <button onClick={() => onDeletar(post.id)} className="ml-auto p-1 text-slate-500 hover:text-red-400">
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
            {post.mensagem && <p className="text-sm text-slate-200 mt-1 whitespace-pre-wrap">{renderWithMentions(post.mensagem)}</p>}
            {post.arquivo && <ArquivoDisplay arquivo={post.arquivo} />}
            <div className="flex items-center gap-4 mt-2">
              <button
                onClick={() => onCurtir(post.id)}
                className={`flex items-center gap-1 text-xs transition-colors ${curtiu ? 'text-red-400' : 'text-slate-500 hover:text-red-400'}`}
                data-testid={`btn-curtir-${post.id}`}
              >
                <Heart className={`w-4 h-4 ${curtiu ? 'fill-current' : ''}`} />
                {(post.curtidas || []).length > 0 && <span>{post.curtidas.length}</span>}
              </button>
              <button
                onClick={onToggleThread}
                className={`flex items-center gap-1 text-xs transition-colors ${threadOpen ? 'text-amber-400' : 'text-slate-500 hover:text-amber-400'}`}
                data-testid={`btn-responder-${post.id}`}
              >
                <MessageCircle className="w-4 h-4" />
                <span>{post.respostas_count > 0 ? `${post.respostas_count} resposta${post.respostas_count > 1 ? 's' : ''}` : 'Responder'}</span>
              </button>
            </div>
          </div>
        </div>
        {threadOpen && (
          <ThreadSection postId={post.id} token={token} headers={headers} userId={userId} />
        )}
      </CardContent>
    </Card>
  );
};

const ThreadSection = ({ postId, token, headers, userId }) => {
  const [respostas, setRespostas] = useState([]);
  const [texto, setTexto] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [mencionados, setMencionados] = useState([]);

  const fetchRespostas = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/equipe/feed/${postId}/respostas`, { headers });
      setRespostas(res.data.respostas || []);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, [postId, token]);

  useEffect(() => { fetchRespostas(); }, [fetchRespostas]);

  const enviar = async () => {
    if (!texto.trim()) return;
    setSending(true);
    try {
      const formData = new FormData();
      formData.append('mensagem', texto);
      formData.append('mencionados', mencionados.join(','));
      await axios.post(`${API}/equipe/feed/${postId}/responder`, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' }
      });
      setTexto('');
      setMencionados([]);
      await fetchRespostas();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Erro ao responder');
    } finally { setSending(false); }
  };

  return (
    <div className="mt-3 ml-12 border-l-2 border-amber-500/30 pl-4 space-y-3" data-testid={`thread-${postId}`}>
      {loading ? (
        <div className="flex justify-center py-2"><Loader2 className="w-4 h-4 animate-spin text-amber-500" /></div>
      ) : respostas.length > 0 ? (
        respostas.map(r => (
          <div key={r.id} className="flex gap-2">
            <Avatar className="w-7 h-7 shrink-0">
              <AvatarImage src={r.autor_foto?.startsWith('http') ? r.autor_foto : `${BACKEND_URL}${r.autor_foto}`} />
              <AvatarFallback className="bg-slate-600 text-white text-xs">{r.autor_nome?.charAt(0)}</AvatarFallback>
            </Avatar>
            <div className="bg-slate-700/50 rounded-lg px-3 py-1.5 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-amber-400">{r.autor_nome}</span>
                <span className="text-[10px] text-slate-500">
                  {new Date(r.data_envio).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <p className="text-sm text-slate-200 whitespace-pre-wrap">{renderWithMentions(r.mensagem)}</p>
              {r.arquivo && <ArquivoDisplay arquivo={r.arquivo} small />}
            </div>
          </div>
        ))
      ) : null}
      <div className="flex gap-2">
        <MentionInput
          value={texto}
          onChange={e => setTexto(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && enviar()}
          placeholder="Escreva uma resposta... (use @ para mencionar)"
          className="w-full bg-slate-900 border border-slate-700 text-white text-sm h-8 rounded-md px-3 flex-1"
          token={token}
          testId={`thread-input-${postId}`}
          onMention={(id) => setMencionados(prev => prev.includes(id) ? prev : [...prev, id])}
        />
        <Button onClick={enviar} disabled={sending || !texto.trim()} size="sm" className="bg-amber-500 hover:bg-amber-600 h-8 px-3" data-testid={`thread-send-${postId}`}>
          {sending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
        </Button>
      </div>
    </div>
  );
};

const ArquivoDisplay = ({ arquivo, small = false }) => (
  <div className={`${small ? 'mt-1' : 'mt-2'}`}>
    {arquivo.tipo === 'imagem' ? (
      <img
        src={`${BACKEND_URL}${arquivo.caminho}`}
        alt={arquivo.nome_original}
        className={`rounded-lg max-w-full cursor-pointer ${small ? 'max-h-32' : 'max-h-64'}`}
        onClick={() => window.open(`${BACKEND_URL}${arquivo.caminho}`, '_blank')}
      />
    ) : (
      <a href={`${BACKEND_URL}${arquivo.caminho}`} target="_blank" rel="noopener noreferrer"
        className="flex items-center gap-2 px-3 py-2 bg-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-600 w-fit">
        <FileText className="w-4 h-4" />
        <span className="truncate max-w-[200px]">{arquivo.nome_original}</span>
        <Download className="w-4 h-4 shrink-0" />
      </a>
    )}
  </div>
);

export default FeedEquipe;
