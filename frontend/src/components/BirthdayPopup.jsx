import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { X, Cake, PartyPopper, Star } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BirthdayPopup = () => {
  const { user, token } = useAuth();
  const [mensagem, setMensagem] = useState(null);
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (user && token && user.role !== 'admin') {
      checkBirthdayMessage();
    }
  }, [user, token]);

  const checkBirthdayMessage = async () => {
    try {
      const response = await axios.get(`${API}/atletas/mensagem-aniversario`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.mensagem) {
        setMensagem(response.data.mensagem);
        setShow(true);
      }
    } catch (error) {
      console.error('Erro ao verificar mensagem de aniversário:', error);
    }
  };

  const handleClose = async () => {
    setShow(false);
    
    // Marcar como visualizada
    try {
      await axios.post(`${API}/atletas/mensagem-aniversario/visualizar`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Erro ao marcar mensagem como visualizada:', error);
    }
  };

  if (!mensagem || !show) return null;

  return (
    <Dialog open={show} onOpenChange={setShow}>
      <DialogContent className="max-w-md p-0 overflow-hidden bg-transparent border-0">
        <div className="relative bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 rounded-2xl p-1">
          <div className="bg-white dark:bg-slate-900 rounded-xl p-6 relative">
            {/* Botão fechar */}
            <Button
              size="sm"
              variant="ghost"
              className="absolute top-2 right-2 rounded-full h-8 w-8 p-0"
              onClick={handleClose}
            >
              <X className="w-4 h-4" />
            </Button>

            {/* Confetes decorativos */}
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden">
              <div className="absolute top-4 left-4 animate-bounce">
                <Star className="w-6 h-6 text-yellow-400" />
              </div>
              <div className="absolute top-8 right-8 animate-bounce delay-100">
                <PartyPopper className="w-6 h-6 text-pink-400" />
              </div>
              <div className="absolute bottom-16 left-8 animate-bounce delay-200">
                <Star className="w-4 h-4 text-purple-400" />
              </div>
              <div className="absolute bottom-20 right-12 animate-bounce delay-300">
                <Star className="w-5 h-5 text-blue-400" />
              </div>
            </div>

            {/* Conteúdo */}
            <div className="text-center relative z-10">
              {/* Bolo animado */}
              <div className="mb-4">
                <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-pink-100 to-purple-100 dark:from-pink-900 dark:to-purple-900 rounded-full">
                  <Cake className="w-12 h-12 text-pink-500 animate-pulse" />
                </div>
              </div>

              {/* Título */}
              <h2 className="text-2xl font-bold bg-gradient-to-r from-pink-500 to-purple-500 bg-clip-text text-transparent mb-2">
                Feliz Aniversário! 🎉
              </h2>

              {/* Nome do usuário */}
              <p className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-4">
                {user?.nome?.split(' ')[0]}
              </p>

              {/* Mensagem */}
              <div className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/30 dark:to-purple-900/30 rounded-xl p-4 mb-4">
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  {mensagem.mensagem}
                </p>
              </div>

              {/* Assinatura */}
              <p className="text-sm text-slate-500 mb-4">
                — Equipe Ranking Run Pró
              </p>

              {/* Botão fechar */}
              <Button
                onClick={handleClose}
                className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white"
              >
                Obrigado! 🎂
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BirthdayPopup;
