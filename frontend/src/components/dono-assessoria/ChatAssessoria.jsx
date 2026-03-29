import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { 
  Send, Paperclip, FileText, Image as ImageIcon, X, Download, Loader2, Check, CheckCheck
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getNomeDisplay(atleta) {
  const apelido = (atleta.apelido || '').trim();
  if (apelido) return apelido;
  const partes = (atleta.nome || '').split(' ');
  if (partes.length >= 2) return `${partes[0]} ${partes[1]}`;
  return atleta.nome || '';
}

export const ChatAssessoria = ({ atletas, token, userId }) => {
  const [mensagens, setMensagens] = useState([]);
  const [texto, setTexto] = useState('');
  const [arquivo, setArquivo] = useState(null);
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selecionados, setSelecionados] = useState([]);
  const [showDestinatarios, setShowDestinatarios] = useState(false);
  const scrollRef = useRef(null);
  const fileInputRef = useRef(null);
  const pollingRef = useRef(null);

  const fetchMensagens = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/assessoria/chat/historico?limit=50`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensagens(res.data.mensagens || []);
    } catch (e) {
      // silent
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchMensagens();
    pollingRef.current = setInterval(fetchMensagens, 8000);
    return () => clearInterval(pollingRef.current);
  }, [fetchMensagens]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [mensagens]);

  const enviar = async () => {
    if (!texto.trim() && !arquivo) return;
    setSending(true);
    try {
      const formData = new FormData();
      formData.append('mensagem', texto);
      formData.append('destinatarios', selecionados.join(','));
      if (arquivo) formData.append('arquivo', arquivo);

      await axios.post(`${API}/assessoria/chat/enviar`, formData, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
      });
      setTexto('');
      setArquivo(null);
      setSelecionados([]);
      setShowDestinatarios(false);
      await fetchMensagens();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Erro ao enviar');
    } finally {
      setSending(false);
    }
  };

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 10 * 1024 * 1024) {
      toast.error('Arquivo muito grande (máx 10MB)');
      return;
    }
    setArquivo(f);
  };

  const toggleDestinatario = (id) => {
    setSelecionados(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const fileIcon = (ext) => {
    if (['.png','.jpg','.jpeg','.gif','.webp'].includes(ext)) return <ImageIcon className="w-4 h-4" />;
    return <FileText className="w-4 h-4" />;
  };

  return (
    <div className="space-y-4" data-testid="chat-assessoria">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Chat da Assessoria</h2>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => setShowDestinatarios(!showDestinatarios)}
          className="text-slate-300 border-slate-600"
          data-testid="btn-toggle-destinatarios"
        >
          {selecionados.length > 0 
            ? `${selecionados.length} selecionado(s)` 
            : 'Todos os atletas'}
        </Button>
      </div>

      {showDestinatarios && (
        <Card className="bg-slate-800/80 border-slate-700">
          <CardContent className="p-3">
            <p className="text-xs text-slate-400 mb-2">Selecione destinatários (vazio = todos):</p>
            <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto">
              {atletas.filter(a => a.id !== userId).map(a => (
                <button
                  key={a.id}
                  onClick={() => toggleDestinatario(a.id)}
                  className={`px-2.5 py-1 rounded-full text-xs transition-colors ${
                    selecionados.includes(a.id)
                      ? 'bg-amber-500 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                  data-testid={`dest-${a.id}`}
                >
                  {getNomeDisplay(a)}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-0 flex flex-col" style={{ height: '60vh' }}>
          {/* Messages area */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3" data-testid="chat-messages">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-6 h-6 animate-spin text-amber-500" />
              </div>
            ) : mensagens.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-slate-500">
                <Send className="w-10 h-10 mb-2 opacity-50" />
                <p className="text-sm">Nenhuma mensagem ainda</p>
                <p className="text-xs">Envie a primeira mensagem!</p>
              </div>
            ) : (
              mensagens.map(msg => {
                const isOwn = msg.remetente_id === userId;
                return (
                  <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
                    <div className={`flex gap-2 max-w-[80%] ${isOwn ? 'flex-row-reverse' : ''}`}>
                      <Avatar className="w-8 h-8 shrink-0">
                        <AvatarImage src={msg.remetente_foto?.startsWith('http') ? msg.remetente_foto : `${BACKEND_URL}${msg.remetente_foto}`} />
                        <AvatarFallback className="bg-amber-500 text-white text-xs">
                          {msg.remetente_nome?.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div className={`rounded-2xl px-3.5 py-2 ${
                        isOwn 
                          ? 'bg-amber-500 text-white rounded-tr-sm' 
                          : 'bg-slate-700 text-slate-100 rounded-tl-sm'
                      }`}>
                        {!isOwn && (
                          <p className="text-xs font-semibold mb-0.5 text-amber-400">{msg.remetente_nome}</p>
                        )}
                        {msg.mensagem && <p className="text-sm whitespace-pre-wrap">{msg.mensagem}</p>}
                        {msg.arquivo && (
                          <div className="mt-1.5">
                            {msg.arquivo.tipo === 'imagem' ? (
                              <img 
                                src={`${BACKEND_URL}${msg.arquivo.caminho}`} 
                                alt={msg.arquivo.nome_original}
                                className="rounded-lg max-w-full max-h-48 cursor-pointer"
                                onClick={() => window.open(`${BACKEND_URL}${msg.arquivo.caminho}`, '_blank')}
                              />
                            ) : (
                              <a 
                                href={`${BACKEND_URL}${msg.arquivo.caminho}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs ${
                                  isOwn ? 'bg-amber-600/50' : 'bg-slate-600/50'
                                }`}
                              >
                                {fileIcon(msg.arquivo.extensao)}
                                <span className="truncate max-w-[140px]">{msg.arquivo.nome_original}</span>
                                <Download className="w-3.5 h-3.5 shrink-0" />
                              </a>
                            )}
                          </div>
                        )}
                        <div className={`flex items-center gap-1 mt-1 ${isOwn ? 'justify-end' : ''}`}>
                          <span className="text-[10px] opacity-60">
                            {new Date(msg.data_envio).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                          </span>
                          {isOwn && <CheckCheck className="w-3 h-3 opacity-60" />}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* File preview */}
          {arquivo && (
            <div className="mx-4 mb-2 px-3 py-2 bg-slate-700 rounded-lg flex items-center gap-2 text-sm text-slate-300">
              {fileIcon(`.${arquivo.name.split('.').pop()}`)}
              <span className="truncate flex-1">{arquivo.name}</span>
              <span className="text-xs text-slate-500">{(arquivo.size / 1024).toFixed(0)}KB</span>
              <button onClick={() => setArquivo(null)} className="p-0.5 hover:text-red-400">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Input area */}
          <div className="border-t border-slate-700 p-3 flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg,.gif,.webp"
              className="hidden"
              onChange={handleFile}
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              className="text-slate-400 hover:text-amber-400 shrink-0"
              data-testid="btn-anexar"
            >
              <Paperclip className="w-5 h-5" />
            </Button>
            <Input
              value={texto}
              onChange={e => setTexto(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && enviar()}
              placeholder="Digite sua mensagem..."
              className="bg-slate-900 border-slate-700 text-white flex-1"
              data-testid="input-chat"
            />
            <Button
              onClick={enviar}
              disabled={sending || (!texto.trim() && !arquivo)}
              className="bg-amber-500 hover:bg-amber-600 shrink-0"
              size="icon"
              data-testid="btn-enviar-chat"
            >
              {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChatAssessoria;
