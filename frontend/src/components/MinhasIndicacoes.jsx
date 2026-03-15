// /app/frontend/src/components/MinhasIndicacoes.jsx
// Componente que exibe as indicações do atleta no perfil público

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { 
  Users, Trophy, UserPlus, Gift, Copy, Check,
  Share2, MessageCircle, ChevronDown, ChevronUp, Sparkles
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MinhasIndicacoes = ({ atletaId, isOwner = false }) => {
  const [dadosIndicacao, setDadosIndicacao] = useState(null);
  const [indicacoes, setIndicacoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copiado, setCopiado] = useState(false);
  const [expandido, setExpandido] = useState(false);

  useEffect(() => {
    fetchDados();
  }, [atletaId, isOwner]);

  const fetchDados = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      if (isOwner && token) {
        // Se é o dono do perfil, buscar dados completos
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
      } else {
        // Se é visitante, buscar apenas dados públicos do atleta
        const res = await axios.get(`${API}/indicacao/atleta/${atletaId}/publico`);
        setDadosIndicacao(res.data);
        setIndicacoes(res.data.indicacoes || []);
      }
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

  if (loading) {
    return (
      <Card className="border-slate-200 dark:border-slate-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!dadosIndicacao) return null;

  const totalIndicacoes = dadosIndicacao.total_indicacoes || indicacoes.length || 0;
  const isEmbaixador = dadosIndicacao.is_embaixador || totalIndicacoes >= 5;
  const indicacoesParaMostrar = expandido ? indicacoes : indicacoes.slice(0, 3);

  return (
    <Card className="border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden" data-testid="minhas-indicacoes">
      {/* Header com gradiente */}
      <div className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-4 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 rounded-full p-2">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-lg">
                {isOwner ? 'Minhas Indicações' : 'Indicações'}
              </h3>
              <p className="text-sm text-white/80">
                {totalIndicacoes} {totalIndicacoes === 1 ? 'amigo indicado' : 'amigos indicados'}
              </p>
            </div>
          </div>
          
          {isEmbaixador && (
            <Badge className="bg-amber-400 text-amber-900 shadow-lg">
              <Trophy className="w-3 h-3 mr-1" />
              Embaixador
            </Badge>
          )}
        </div>
      </div>

      <CardContent className="p-4 space-y-4">
        {/* Estatísticas */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gradient-to-br from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-pink-600 dark:text-pink-400">
              {totalIndicacoes}
            </div>
            <div className="text-xs text-slate-600 dark:text-slate-400">
              Pessoas Indicadas
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-amber-600 dark:text-amber-400">
              {isEmbaixador ? '✓' : `${5 - totalIndicacoes}`}
            </div>
            <div className="text-xs text-slate-600 dark:text-slate-400">
              {isEmbaixador ? 'Embaixador' : 'Faltam p/ Badge'}
            </div>
          </div>
        </div>

        {/* Código e Compartilhamento (apenas para o dono) */}
        {isOwner && dadosIndicacao.codigo && (
          <div className="space-y-3">
            <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-3">
              <p className="text-xs text-slate-500 mb-2">Seu código de indicação:</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-white dark:bg-slate-900 border-2 border-dashed border-pink-500 rounded-lg px-3 py-2 font-mono font-bold text-pink-600 dark:text-pink-400 text-center">
                  {dadosIndicacao.codigo}
                </div>
                <Button 
                  variant="outline" 
                  size="icon"
                  onClick={copiarCodigo}
                  className="shrink-0"
                  data-testid="btn-copiar-codigo"
                >
                  {copiado ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                </Button>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={compartilharWhatsApp}
                className="flex-1 bg-green-500 hover:bg-green-600 text-white"
                size="sm"
              >
                <MessageCircle className="w-4 h-4 mr-2" />
                Convidar via WhatsApp
              </Button>
            </div>
          </div>
        )}

        {/* Lista de Indicados */}
        {indicacoes.length > 0 ? (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2">
                <UserPlus className="w-4 h-4 text-pink-500" />
                Quem entrou com {isOwner ? 'seu' : 'o'} código:
              </p>
            </div>
            
            <div className="space-y-2">
              {indicacoesParaMostrar.map((ind, i) => (
                <div 
                  key={ind.id || i}
                  className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                  data-testid={`indicado-${i}`}
                >
                  <Avatar className="h-10 w-10 ring-2 ring-pink-200 dark:ring-pink-800">
                    <AvatarImage src={ind.foto_url} />
                    <AvatarFallback className="bg-gradient-to-br from-pink-500 to-purple-500 text-white font-bold">
                      {ind.nome?.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-800 dark:text-slate-200 truncate">
                      {ind.nome}
                    </p>
                    <p className="text-xs text-slate-500">
                      Entrou em {new Date(ind.data_cadastro).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                  <Badge variant="outline" className="text-emerald-600 border-emerald-400 shrink-0">
                    <Check className="w-3 h-3 mr-1" />
                    OK
                  </Badge>
                </div>
              ))}
            </div>
            
            {/* Botão Ver Mais/Menos */}
            {indicacoes.length > 3 && (
              <Button 
                variant="ghost" 
                className="w-full text-pink-600 hover:text-pink-700 hover:bg-pink-50"
                onClick={() => setExpandido(!expandido)}
                data-testid="btn-ver-mais-indicacoes"
              >
                {expandido ? (
                  <>
                    <ChevronUp className="w-4 h-4 mr-2" />
                    Ver Menos
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4 mr-2" />
                    Ver Todos ({indicacoes.length})
                  </>
                )}
              </Button>
            )}
          </div>
        ) : (
          <div className="text-center py-6">
            <div className="bg-slate-100 dark:bg-slate-800 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
              <UserPlus className="w-8 h-8 text-slate-400" />
            </div>
            <p className="text-slate-500 text-sm">
              {isOwner 
                ? 'Você ainda não indicou ninguém. Compartilhe seu código!'
                : 'Nenhuma indicação registrada ainda.'}
            </p>
          </div>
        )}

        {/* Recompensa (apenas para o dono e se não for embaixador) */}
        {isOwner && !isEmbaixador && (
          <div className="flex items-center gap-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3 border border-amber-200 dark:border-amber-800">
            <div className="bg-amber-500 rounded-full p-2 shrink-0">
              <Gift className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-amber-800 dark:text-amber-300 text-sm">
                Indique {5 - totalIndicacoes} {5 - totalIndicacoes === 1 ? 'amigo' : 'amigos'} e ganhe:
              </p>
              <p className="text-xs text-amber-600 dark:text-amber-400">
                🏅 Insígnia exclusiva "Embaixador"
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default MinhasIndicacoes;
