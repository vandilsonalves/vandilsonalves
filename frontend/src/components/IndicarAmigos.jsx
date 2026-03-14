// /app/frontend/src/components/IndicarAmigos.jsx
// Componente para indicar amigos e ganhar a insígnia Embaixador

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Users, Copy, Check, Share2, Gift, Trophy, UserPlus, 
  MessageCircle, Link2, Sparkles
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const IndicarAmigos = () => {
  const [dadosIndicacao, setDadosIndicacao] = useState(null);
  const [indicacoes, setIndicacoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copiado, setCopiado] = useState(false);
  const [showIndicacoes, setShowIndicacoes] = useState(false);
  
  useEffect(() => {
    fetchDadosIndicacao();
  }, []);
  
  const fetchDadosIndicacao = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const [codigoRes, indicacoesRes] = await Promise.all([
        axios.get(`${API}/indicacao/meu-codigo`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/indicacao/minhas-indicacoes`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setDadosIndicacao(codigoRes.data);
      setIndicacoes(indicacoesRes.data.indicacoes || []);
    } catch (error) {
      console.error('Erro ao buscar dados de indicação:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const copiarCodigo = async () => {
    if (!dadosIndicacao?.codigo) return;
    
    try {
      await navigator.clipboard.writeText(dadosIndicacao.codigo);
      setCopiado(true);
      toast.success('Código copiado!');
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      toast.error('Erro ao copiar');
    }
  };
  
  const copiarLink = async () => {
    if (!dadosIndicacao?.link) return;
    
    try {
      await navigator.clipboard.writeText(dadosIndicacao.link);
      toast.success('Link copiado!');
    } catch {
      toast.error('Erro ao copiar');
    }
  };
  
  const compartilharWhatsApp = () => {
    if (!dadosIndicacao?.link) return;
    
    const texto = encodeURIComponent(
      `🏃 Vem correr comigo no Ranking Run Pró!\n\n` +
      `Use meu código de indicação: ${dadosIndicacao.codigo}\n\n` +
      `Cadastre-se aqui: ${dadosIndicacao.link}\n\n` +
      `#RankingRunPro #Corrida`
    );
    
    window.open(`https://wa.me/?text=${texto}`, '_blank');
  };
  
  const compartilharTelegram = () => {
    if (!dadosIndicacao?.link) return;
    
    const texto = encodeURIComponent(
      `🏃 Vem correr comigo no Ranking Run Pró! Use meu código: ${dadosIndicacao.codigo}`
    );
    
    window.open(`https://t.me/share/url?url=${encodeURIComponent(dadosIndicacao.link)}&text=${texto}`, '_blank');
  };
  
  if (loading) {
    return (
      <Card className="border-slate-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500" />
          </div>
        </CardContent>
      </Card>
    );
  }
  
  if (!dadosIndicacao) return null;
  
  const progresso = (dadosIndicacao.total_indicacoes / 5) * 100;
  
  return (
    <Card className="border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden">
      {/* Header com gradiente */}
      <div className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-4 text-white">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 rounded-full p-2">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg">Indicar Amigos</h3>
            <p className="text-sm text-white/80">Ganhe a insígnia Embaixador!</p>
          </div>
          {dadosIndicacao.is_embaixador && (
            <Badge className="ml-auto bg-amber-400 text-amber-900">
              <Trophy className="w-3 h-3 mr-1" />
              Embaixador
            </Badge>
          )}
        </div>
      </div>
      
      <CardContent className="p-4 space-y-4">
        {/* Código de Indicação */}
        <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
          <p className="text-sm text-slate-500 mb-2">Seu código de indicação:</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-white dark:bg-slate-900 border-2 border-dashed border-emerald-500 rounded-lg px-4 py-3 font-mono font-bold text-lg text-emerald-600 dark:text-emerald-400 text-center">
              {dadosIndicacao.codigo}
            </div>
            <Button 
              variant="outline" 
              size="icon"
              onClick={copiarCodigo}
              className="shrink-0"
            >
              {copiado ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
            </Button>
          </div>
        </div>
        
        {/* Progresso para Embaixador */}
        {!dadosIndicacao.is_embaixador && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-600 dark:text-slate-400">
                Progresso para Embaixador
              </span>
              <span className="font-bold text-purple-600">
                {dadosIndicacao.total_indicacoes}/5 indicações
              </span>
            </div>
            <Progress value={progresso} className="h-3" />
            <p className="text-xs text-center text-slate-500">
              {dadosIndicacao.indicacoes_para_embaixador > 0 
                ? `Faltam ${dadosIndicacao.indicacoes_para_embaixador} indicações para a insígnia!`
                : '🎉 Você já é um Embaixador!'}
            </p>
          </div>
        )}
        
        {/* Recompensa */}
        <div className="flex items-center gap-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3 border border-amber-200 dark:border-amber-800">
          <div className="bg-amber-500 rounded-full p-2">
            <Gift className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-amber-800 dark:text-amber-300 text-sm">
              Indique 5 amigos e ganhe:
            </p>
            <p className="text-xs text-amber-600 dark:text-amber-400">
              🏅 Insígnia exclusiva "Embaixador"
            </p>
          </div>
        </div>
        
        {/* Botões de Compartilhar */}
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Compartilhar convite:
          </p>
          <div className="grid grid-cols-2 gap-2">
            <Button 
              onClick={compartilharWhatsApp}
              className="bg-green-500 hover:bg-green-600 text-white"
            >
              <MessageCircle className="w-4 h-4 mr-2" />
              WhatsApp
            </Button>
            <Button 
              onClick={copiarLink}
              variant="outline"
            >
              <Link2 className="w-4 h-4 mr-2" />
              Copiar Link
            </Button>
          </div>
        </div>
        
        {/* Indicações Feitas */}
        {indicacoes.length > 0 && (
          <Dialog open={showIndicacoes} onOpenChange={setShowIndicacoes}>
            <DialogTrigger asChild>
              <Button variant="ghost" className="w-full">
                <UserPlus className="w-4 h-4 mr-2" />
                Ver minhas indicações ({indicacoes.length})
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-500" />
                  Suas Indicações
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {indicacoes.map((ind, i) => (
                  <div 
                    key={ind.id || i}
                    className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  >
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={ind.foto_url} />
                      <AvatarFallback className="bg-purple-500 text-white">
                        {ind.nome?.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <p className="font-medium">{ind.nome}</p>
                      <p className="text-xs text-slate-500">
                        {new Date(ind.data_cadastro).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-emerald-600 border-emerald-500">
                      <Check className="w-3 h-3 mr-1" />
                      Confirmada
                    </Badge>
                  </div>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        )}
      </CardContent>
    </Card>
  );
};

export default IndicarAmigos;
