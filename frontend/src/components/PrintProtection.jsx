import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Shield } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * PrintProtection - Previne print/screenshot para usuarios expirados.
 * Aplica:
 * - CSS @media print que oculta todo o conteudo
 * - Deteccao de atalhos de teclado (PrintScreen, Ctrl+P, Ctrl+Shift+S, etc.)
 * - Blur no conteudo quando detecta tentativa de captura
 * - user-select: none para impedir copia de texto
 */
export default function PrintProtection({ children }) {
  const { user, token } = useAuth();
  const [isExpired, setIsExpired] = useState(false);
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (!token || !user) return;
    if (user.role === 'admin' || user.role === 'super_admin') return;

    const checkStatus = async () => {
      try {
        const res = await fetch(`${API}/api/pagamentos/meu-plano`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setIsExpired(data.status === 'expirado');
      } catch {
        // Em caso de erro, nao bloqueia
      }
    };
    checkStatus();
  }, [token, user]);

  const handleBlock = useCallback((e) => {
    if (!isExpired) return;

    // Bloquear PrintScreen
    if (e.key === 'PrintScreen') {
      e.preventDefault();
      setShowWarning(true);
      setTimeout(() => setShowWarning(false), 3000);
      return;
    }

    // Bloquear Ctrl+P (print)
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
      e.preventDefault();
      setShowWarning(true);
      setTimeout(() => setShowWarning(false), 3000);
      return;
    }

    // Bloquear Ctrl+Shift+S (screenshot tools)
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 's' || e.key === 'S')) {
      e.preventDefault();
      setShowWarning(true);
      setTimeout(() => setShowWarning(false), 3000);
      return;
    }

    // Bloquear Ctrl+Shift+I (DevTools)
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'i' || e.key === 'I')) {
      e.preventDefault();
      return;
    }
  }, [isExpired]);

  useEffect(() => {
    if (!isExpired) return;

    document.addEventListener('keydown', handleBlock, true);

    // Injetar CSS anti-print
    const styleId = 'print-protection-style';
    if (!document.getElementById(styleId)) {
      const style = document.createElement('style');
      style.id = styleId;
      style.textContent = `
        @media print {
          body * { visibility: hidden !important; }
          body::after {
            content: 'Conteudo protegido. Assine o plano Atleta Premium para acessar.';
            visibility: visible !important;
            display: flex;
            align-items: center;
            justify-content: center;
            position: fixed;
            inset: 0;
            font-size: 24px;
            color: #666;
            text-align: center;
          }
        }
        .print-protected {
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;
        }
      `;
      document.head.appendChild(style);
    }

    return () => {
      document.removeEventListener('keydown', handleBlock, true);
    };
  }, [isExpired, handleBlock]);

  if (!isExpired) return children;

  return (
    <div className="print-protected relative">
      {children}

      {/* Warning overlay quando tenta print */}
      {showWarning && (
        <div
          className="fixed inset-0 z-[9999] bg-gray-950/95 flex items-center justify-center"
          data-testid="print-warning-overlay"
        >
          <div className="text-center max-w-md px-6">
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-red-400" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Conteudo Protegido</h3>
            <p className="text-gray-400 text-sm">
              Capturas de tela e impressao estao desabilitadas. Assine o plano Atleta Premium para acesso completo.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
