// /app/frontend/src/components/PWAInstallPrompt.jsx
// Componente para sugerir instalação do PWA

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Download, X, Smartphone } from 'lucide-react';

const PWAInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Verificar se já está instalado como PWA
    const standalone = window.matchMedia('(display-mode: standalone)').matches 
      || window.navigator.standalone 
      || document.referrer.includes('android-app://');
    
    setIsStandalone(standalone);

    // Verificar se é iOS
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    setIsIOS(iOS);

    // Verificar se já foi fechado antes
    const dismissed = localStorage.getItem('pwa-prompt-dismissed');
    const dismissedTime = dismissed ? parseInt(dismissed) : 0;
    const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);

    // Capturar evento de instalação (Android/Desktop)
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      
      // Mostrar prompt após 5 segundos se não foi dispensado recentemente
      if (daysSinceDismissed > 7) {
        setTimeout(() => setShowPrompt(true), 5000);
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);

    // Para iOS, mostrar instruções manuais
    if (iOS && !standalone && daysSinceDismissed > 7) {
      setTimeout(() => setShowPrompt(true), 5000);
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
    };
  }, []);

  const handleInstall = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('PWA instalado!');
      }
      
      setDeferredPrompt(null);
      setShowPrompt(false);
    }
  };

  const handleDismiss = () => {
    localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
    setShowPrompt(false);
  };

  // Não mostrar se já está instalado ou não deve mostrar
  if (isStandalone || !showPrompt) {
    return null;
  }

  return (
    <div className="fixed bottom-20 left-4 right-4 z-50 md:left-auto md:right-4 md:w-96 animate-in slide-in-from-bottom duration-300">
      <Card className="bg-gradient-to-r from-emerald-600 to-green-600 border-0 shadow-2xl">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center shrink-0">
              <Smartphone className="w-6 h-6 text-white" />
            </div>
            
            <div className="flex-1 min-w-0">
              <h3 className="font-bold text-white mb-1">
                Instale o App!
              </h3>
              
              {isIOS ? (
                <p className="text-sm text-emerald-100 mb-3">
                  Toque em <span className="font-semibold">Compartilhar</span> e depois em{' '}
                  <span className="font-semibold">"Adicionar à Tela Inicial"</span>
                </p>
              ) : (
                <p className="text-sm text-emerald-100 mb-3">
                  Tenha acesso rápido ao ranking direto do seu celular!
                </p>
              )}
              
              <div className="flex gap-2">
                {!isIOS && deferredPrompt && (
                  <Button 
                    onClick={handleInstall}
                    size="sm"
                    className="bg-white text-emerald-600 hover:bg-emerald-50"
                    data-testid="pwa-install-btn"
                  >
                    <Download className="w-4 h-4 mr-1" />
                    Instalar
                  </Button>
                )}
                
                <Button 
                  onClick={handleDismiss}
                  size="sm"
                  variant="ghost"
                  className="text-white hover:bg-white/20"
                  data-testid="pwa-dismiss-btn"
                >
                  Agora não
                </Button>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDismiss}
              className="text-white/70 hover:text-white hover:bg-white/20 shrink-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PWAInstallPrompt;
