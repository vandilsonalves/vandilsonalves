import { useState, useRef, useEffect, useCallback } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export function MentionInput({ value, onChange, onKeyDown, placeholder, className, token, testId, onMention }) {
  const [membros, setMembros] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [filtro, setFiltro] = useState('');
  const [cursorPos, setCursorPos] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!token) return;
    const fetchMembros = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/equipe/membros`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setMembros(data.membros || []);
      } catch { /* silent */ }
    };
    fetchMembros();
  }, [token]);

  const handleChange = (e) => {
    const val = e.target.value;
    const pos = e.target.selectionStart;
    onChange(e);
    setCursorPos(pos);

    // Check if we're typing after @
    const textBefore = val.substring(0, pos);
    const atMatch = textBefore.match(/@(\w*)$/);
    if (atMatch) {
      setFiltro(atMatch[1].toLowerCase());
      setShowDropdown(true);
    } else {
      setShowDropdown(false);
    }
  };

  const insertMention = (membro) => {
    const textBefore = value.substring(0, cursorPos);
    const textAfter = value.substring(cursorPos);
    const atIdx = textBefore.lastIndexOf('@');
    const newText = textBefore.substring(0, atIdx) + `@${membro.nome_display} ` + textAfter;
    onChange({ target: { value: newText } });
    setShowDropdown(false);
    if (onMention) onMention(membro.id);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const filtered = membros.filter(m =>
    m.nome_display.toLowerCase().includes(filtro) || m.nome.toLowerCase().includes(filtro)
  ).slice(0, 6);

  return (
    <div className="relative flex-1">
      <input
        ref={inputRef}
        value={value}
        onChange={handleChange}
        onKeyDown={(e) => {
          if (showDropdown && e.key === 'Escape') {
            setShowDropdown(false);
            return;
          }
          if (onKeyDown) onKeyDown(e);
        }}
        placeholder={placeholder}
        className={className}
        data-testid={testId}
      />
      {showDropdown && filtered.length > 0 && (
        <div className="absolute bottom-full mb-1 left-0 w-full max-h-48 overflow-y-auto bg-slate-800 border border-slate-600 rounded-lg shadow-xl z-50" data-testid="mention-dropdown">
          {filtered.map(m => (
            <button
              key={m.id}
              onClick={() => insertMention(m)}
              className="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-700 text-left transition-colors"
              data-testid={`mention-${m.id}`}
            >
              <div className="w-6 h-6 rounded-full bg-amber-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
                {m.nome_display.charAt(0)}
              </div>
              <span className="text-sm text-white truncate">{m.nome_display}</span>
              {m.nome_display !== m.nome && (
                <span className="text-xs text-slate-500 truncate">({m.nome.split(' ')[0]})</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Utility to render text with highlighted mentions
export function renderWithMentions(text) {
  if (!text) return null;
  const parts = text.split(/(@\w[\w\s]*?)(?=\s@|\s*$|[.,!?]|\s)/g);
  return parts.map((part, i) => {
    if (part.startsWith('@')) {
      return (
        <span key={i} className="text-amber-400 font-semibold">{part}</span>
      );
    }
    return part;
  });
}
