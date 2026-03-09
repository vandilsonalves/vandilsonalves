import { useState, useEffect } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { FileText, Loader2, Calendar, User } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RegulamentoModal = ({ open, onOpenChange }) => {
  const [loading, setLoading] = useState(true);
  const [regulamento, setRegulamento] = useState(null);

  useEffect(() => {
    if (open) {
      fetchRegulamento();
    }
  }, [open]);

  const fetchRegulamento = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/regulamento`);
      setRegulamento(response.data);
    } catch (error) {
      console.error('Erro ao buscar regulamento:', error);
    } finally {
      setLoading(false);
    }
  };

  // Função para renderizar markdown básico
  const renderMarkdown = (text) => {
    if (!text) return null;
    
    return text.split('\n').map((line, index) => {
      // Headers
      if (line.startsWith('### ')) {
        return <h3 key={index} className="text-lg font-semibold text-emerald-400 mt-4 mb-2">{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={index} className="text-xl font-bold text-emerald-500 mt-6 mb-3">{line.replace('## ', '')}</h2>;
      }
      if (line.startsWith('# ')) {
        return <h1 key={index} className="text-2xl font-bold text-emerald-600 mt-6 mb-4">{line.replace('# ', '')}</h1>;
      }
      // Horizontal rule
      if (line.startsWith('---')) {
        return <hr key={index} className="my-4 border-slate-600" />;
      }
      // List items
      if (line.startsWith('- **')) {
        const match = line.match(/- \*\*(.+?)\*\*:?\s*(.*)/);
        if (match) {
          return (
            <div key={index} className="flex gap-2 ml-4 my-1">
              <span className="text-emerald-500">•</span>
              <span><strong className="text-white">{match[1]}</strong>{match[2] ? `: ${match[2]}` : ''}</span>
            </div>
          );
        }
      }
      if (line.startsWith('- ')) {
        return (
          <div key={index} className="flex gap-2 ml-4 my-1">
            <span className="text-emerald-500">•</span>
            <span>{line.replace('- ', '')}</span>
          </div>
        );
      }
      // Bold text
      if (line.includes('**')) {
        const parts = line.split(/\*\*(.+?)\*\*/g);
        return (
          <p key={index} className="my-1">
            {parts.map((part, i) => 
              i % 2 === 1 ? <strong key={i} className="text-white">{part}</strong> : part
            )}
          </p>
        );
      }
      // Italic text (for notes)
      if (line.startsWith('*') && line.endsWith('*')) {
        return <p key={index} className="my-2 text-slate-400 italic text-sm">{line.replace(/\*/g, '')}</p>;
      }
      // Empty lines
      if (line.trim() === '') {
        return <div key={index} className="h-2"></div>;
      }
      // Regular paragraph
      return <p key={index} className="my-1">{line}</p>;
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[85vh] bg-slate-900 border-slate-700">
        <DialogHeader className="border-b border-slate-700 pb-4">
          <DialogTitle className="flex items-center gap-3 text-white">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <FileText className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <span className="text-xl">{regulamento?.titulo || 'Regulamento'}</span>
              {regulamento?.ultima_atualizacao && (
                <div className="flex items-center gap-4 text-xs text-slate-400 font-normal mt-1">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    Atualizado em: {new Date(regulamento.ultima_atualizacao).toLocaleDateString('pt-BR')}
                  </span>
                  {regulamento.atualizado_por && (
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      Por: {regulamento.atualizado_por}
                    </span>
                  )}
                </div>
              )}
            </div>
          </DialogTitle>
        </DialogHeader>
        
        <ScrollArea className="h-[60vh] pr-4">
          {loading ? (
            <div className="flex items-center justify-center h-40">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : (
            <div className="text-slate-300 leading-relaxed py-4">
              {renderMarkdown(regulamento?.conteudo)}
            </div>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

// Botão reutilizável para abrir o regulamento
export const RegulamentoButton = ({ className = "", variant = "outline", size = "sm" }) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button 
        variant={variant} 
        size={size}
        onClick={() => setOpen(true)}
        className={`border-emerald-500/50 text-emerald-600 hover:bg-emerald-500/10 ${className}`}
        data-testid="btn-regulamento"
      >
        <FileText className="w-4 h-4 mr-2" />
        Regulamento
      </Button>
      <RegulamentoModal open={open} onOpenChange={setOpen} />
    </>
  );
};

export default RegulamentoModal;
