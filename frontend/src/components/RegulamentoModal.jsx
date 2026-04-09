import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { FileText, Loader2, Calendar, User, List, ChevronDown, ChevronUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const slugify = (text) => text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

const TOC_ICONS = {
  'ranking-das-corridas': '1',
  'ranking-profissional-amador': '2',
  'ranking-da-galera': '3',
  'ranking-das-assessorias-equipes': '4',
  'carta-de-princ': '5',
  'pol-tica-de-integridade': '6',
  'estatuto-institucional': '7',
  'considera-o-final': '8',
};

const getTocNumber = (slug) => {
  for (const [key, val] of Object.entries(TOC_ICONS)) {
    if (slug.includes(key)) return val;
  }
  return null;
};

const RegulamentoModal = ({ open, onOpenChange }) => {
  const [loading, setLoading] = useState(true);
  const [regulamento, setRegulamento] = useState(null);
  const [tocOpen, setTocOpen] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (open) {
      fetchRegulamento();
      setTocOpen(false);
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

  // Extract TOC from ## headers
  const tocItems = useMemo(() => {
    if (!regulamento?.conteudo) return [];
    const items = [];
    const lines = regulamento.conteudo.split('\n');
    for (const line of lines) {
      if (line.startsWith('## ') && !line.startsWith('### ')) {
        const title = line.replace('## ', '').trim();
        if (title.length > 2) {
          items.push({ title, slug: slugify(title) });
        }
      }
    }
    return items;
  }, [regulamento?.conteudo]);

  const scrollToSection = useCallback((slug) => {
    const el = document.getElementById(`sec-${slug}`);
    if (el) {
      const viewport = scrollRef.current?.querySelector('[data-radix-scroll-area-viewport]');
      if (viewport) {
        const offset = el.offsetTop - 10;
        viewport.scrollTo({ top: offset, behavior: 'smooth' });
      }
    }
    setTocOpen(false);
  }, []);

  const renderInlineBold = (text) => {
    if (!text.includes('**')) return text;
    const parts = text.split(/\*\*(.+?)\*\*/g);
    return parts.map((part, i) =>
      i % 2 === 1 ? <strong key={i} className="text-white">{part}</strong> : part
    );
  };

  const renderMarkdown = (text) => {
    if (!text) return null;

    const lines = text.split('\n');
    const elements = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      // Table detection
      if (line.trim().startsWith('|') && line.trim().endsWith('|') && line.split('|').length >= 3) {
        const tableLines = [];
        while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
          tableLines.push(lines[i]);
          i++;
        }
        const headerCells = tableLines[0].split('|').filter(c => c.trim() !== '').map(c => c.trim());
        const dataRows = tableLines.slice(2).map(row =>
          row.split('|').filter(c => c.trim() !== '').map(c => c.trim())
        );
        elements.push(
          <div key={`table-${i}`} className="overflow-x-auto my-3">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-600">
                  {headerCells.map((cell, ci) => (
                    <th key={ci} className="px-3 py-2 text-left text-emerald-400 font-semibold">{renderInlineBold(cell)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dataRows.map((row, ri) => (
                  <tr key={ri} className="border-b border-slate-700/50">
                    {row.map((cell, ci) => (
                      <td key={ci} className="px-3 py-1.5 text-slate-300">{renderInlineBold(cell)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        continue;
      }

      // Headers with anchor IDs
      if (line.startsWith('### ')) {
        elements.push(<h3 key={i} className="text-base sm:text-lg font-semibold text-emerald-400 mt-4 mb-2 break-words">{line.replace('### ', '')}</h3>);
        i++; continue;
      }
      if (line.startsWith('## ')) {
        const title = line.replace('## ', '').trim();
        const slug = slugify(title);
        elements.push(<h2 key={i} id={`sec-${slug}`} className="text-lg sm:text-xl font-bold text-emerald-500 mt-6 mb-3 break-words scroll-mt-2">{title}</h2>);
        i++; continue;
      }
      if (line.startsWith('# ')) {
        elements.push(<h1 key={i} className="text-xl sm:text-2xl font-bold text-emerald-600 mt-6 mb-4 break-words">{line.replace('# ', '')}</h1>);
        i++; continue;
      }
      // Horizontal rule
      if (line.startsWith('---') || line.startsWith('____')) {
        elements.push(<hr key={i} className="my-4 border-slate-600" />);
        i++; continue;
      }
      // Tab-indented bullet items
      if (line.trimStart().startsWith('•')) {
        const txt = line.replace(/^[\s]*•[\s\t]*/, '');
        elements.push(
          <div key={i} className="flex gap-2 ml-2 sm:ml-4 my-1">
            <span className="text-emerald-500 shrink-0">•</span>
            <span className="break-words min-w-0">{renderInlineBold(txt)}</span>
          </div>
        );
        i++; continue;
      }
      // List items with bold
      if (line.startsWith('- **')) {
        const match = line.match(/- \*\*(.+?)\*\*:?\s*(.*)/);
        if (match) {
          elements.push(
            <div key={i} className="flex gap-2 ml-2 sm:ml-4 my-1">
              <span className="text-emerald-500 shrink-0">•</span>
              <span className="break-words min-w-0"><strong className="text-white">{match[1]}</strong>{match[2] ? `: ${match[2]}` : ''}</span>
            </div>
          );
          i++; continue;
        }
      }
      if (line.startsWith('- ')) {
        elements.push(
          <div key={i} className="flex gap-2 ml-2 sm:ml-4 my-1">
            <span className="text-emerald-500 shrink-0">•</span>
            <span className="break-words min-w-0">{renderInlineBold(line.replace('- ', ''))}</span>
          </div>
        );
        i++; continue;
      }
      // Bold text
      if (line.includes('**')) {
        elements.push(<p key={i} className="my-1 break-words">{renderInlineBold(line)}</p>);
        i++; continue;
      }
      // Italic text
      if (line.startsWith('*') && line.endsWith('*')) {
        elements.push(<p key={i} className="my-2 text-slate-400 italic text-sm break-words">{line.replace(/\*/g, '')}</p>);
        i++; continue;
      }
      // Empty lines
      if (line.trim() === '') {
        elements.push(<div key={i} className="h-2"></div>);
        i++; continue;
      }
      // Regular paragraph
      elements.push(<p key={i} className="my-1 break-words">{line}</p>);
      i++;
    }

    return elements;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent 
        className="max-h-[92vh] sm:max-h-[85vh] bg-slate-900 border-slate-700 p-3 sm:p-6 rounded-lg" 
        style={{ width: 'min(95vw, 48rem)', maxWidth: 'min(95vw, 48rem)' }}
        data-testid="regulamento-modal"
      >
        <DialogHeader className="border-b border-slate-700 pb-3 sm:pb-4">
          <DialogTitle className="flex items-center gap-2 sm:gap-3 text-white">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center shrink-0">
              <FileText className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-500" />
            </div>
            <div className="min-w-0 flex-1">
              <span className="text-base sm:text-xl">{regulamento?.titulo || 'Regulamento'}</span>
              {regulamento?.ultima_atualizacao && (
                <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs text-slate-400 font-normal mt-1">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(regulamento.ultima_atualizacao).toLocaleDateString('pt-BR')}
                  </span>
                  {regulamento.atualizado_por && (
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      {regulamento.atualizado_por}
                    </span>
                  )}
                </div>
              )}
            </div>
            {!loading && tocItems.length > 0 && (
              <button
                onClick={() => setTocOpen(!tocOpen)}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium hover:bg-emerald-500/20 transition-colors shrink-0"
                data-testid="toc-toggle-btn"
              >
                <List className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Sumário</span>
                {tocOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            )}
          </DialogTitle>
        </DialogHeader>

        {/* TOC Panel */}
        {tocOpen && tocItems.length > 0 && (
          <div className="border border-emerald-500/20 rounded-lg bg-slate-800/80 p-3 max-h-[30vh] overflow-y-auto" data-testid="toc-panel">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-2 font-semibold">Navegação Rápida</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
              {tocItems.map((item, idx) => {
                const num = getTocNumber(item.slug);
                return (
                  <button
                    key={idx}
                    onClick={() => scrollToSection(item.slug)}
                    className="flex items-center gap-2 px-2 py-1.5 rounded text-left text-xs sm:text-sm text-slate-300 hover:bg-emerald-500/10 hover:text-emerald-400 transition-colors group"
                    data-testid={`toc-item-${idx}`}
                  >
                    {num && (
                      <span className="w-5 h-5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold flex items-center justify-center shrink-0 group-hover:bg-emerald-500/30">
                        {num}
                      </span>
                    )}
                    <span className="truncate">{item.title}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
        
        <ScrollArea className="h-[65vh] sm:h-[60vh] pr-4 sm:pr-4" ref={scrollRef}>
          {loading ? (
            <div className="flex items-center justify-center h-40">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : (
            <div className="text-slate-300 leading-relaxed py-2 sm:py-4 text-sm sm:text-base" style={{ overflowWrap: 'break-word', wordBreak: 'break-word' }}>
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
