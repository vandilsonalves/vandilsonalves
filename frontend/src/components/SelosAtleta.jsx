import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Award, Medal, Trophy, Star, Target, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SelosAtleta = ({ atletaId, compact = false, showAll = false }) => {
  const [loading, setLoading] = useState(true);
  const [dados, setDados] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (atletaId) {
      fetchSelos();
    }
  }, [atletaId]);

  const fetchSelos = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/selos-atleta/${atletaId}`);
      setDados(response.data);
    } catch (error) {
      console.error('Erro ao buscar selos:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4">
        <Loader2 className="w-5 h-5 animate-spin text-amber-500" />
      </div>
    );
  }

  if (!dados) {
    return null;
  }

  const { selos_resultados, todas_conquistas, atleta, total_conquistas } = dados;

  // Versão compacta - apenas mostrar badges das conquistas
  if (compact) {
    const conquistados = selos_resultados.filter(s => s.conquistado);
    
    if (conquistados.length === 0 && todas_conquistas.length === 0) {
      return null;
    }

    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-slate-300 flex items-center gap-2">
            <Award className="w-4 h-4 text-amber-400" />
            Conquistas ({total_conquistas})
          </p>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setShowModal(true)}
            className="text-xs text-amber-400 hover:text-amber-300"
          >
            Ver todos
          </Button>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {/* Selos de resultados conquistados */}
          {conquistados.map((selo) => (
            <Badge 
              key={selo.codigo} 
              className="text-white border-0"
              style={{ backgroundColor: selo.cor }}
            >
              {selo.icone} {selo.nome}
            </Badge>
          ))}
          
          {/* Outras conquistas */}
          {todas_conquistas.filter(c => !['12_resultados', '20_resultados', '30_resultados'].includes(c.codigo)).map((c) => (
            <Badge key={c.codigo} variant="outline" className="border-amber-500/30 text-amber-300">
              {c.icone} {c.nome}
            </Badge>
          ))}
        </div>

        {/* Modal com detalhes */}
        <Dialog open={showModal} onOpenChange={setShowModal}>
          <DialogContent className="max-w-lg bg-slate-900 border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-500" />
                Selos e Conquistas de {atleta.nome}
              </DialogTitle>
            </DialogHeader>
            <SelosCompleto dados={dados} />
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  // Versão completa
  return <SelosCompleto dados={dados} />;
};

// Componente interno para exibição completa
const SelosCompleto = ({ dados }) => {
  const { selos_resultados, todas_conquistas, atleta } = dados;

  return (
    <div className="space-y-6">
      {/* Info do atleta */}
      <div className="text-center py-2">
        <p className="text-slate-400 text-sm">
          Total de resultados: <span className="text-amber-500 font-bold">{atleta.total_resultados}</span>
        </p>
      </div>

      {/* Selos de Resultados com Progresso */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <Medal className="w-4 h-4 text-amber-400" />
          Selos por Número de Resultados
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {selos_resultados.map((selo) => (
            <div 
              key={selo.codigo}
              className={`relative p-4 rounded-xl border-2 transition-all ${
                selo.conquistado 
                  ? 'border-amber-500 bg-gradient-to-br from-amber-500/20 to-amber-500/5'
                  : 'border-slate-300 bg-white dark:bg-slate-100'
              }`}
            >
              {selo.conquistado && (
                <div className="absolute -top-2 -right-2 bg-emerald-500 text-white text-xs px-2 py-0.5 rounded-full">
                  ✓
                </div>
              )}
              
              <div className="text-center mb-3">
                <span className="text-4xl">{selo.icone}</span>
                <p 
                  className="font-bold mt-1 text-lg"
                  style={{ color: selo.cor }}
                >
                  {selo.nome}
                </p>
                <p className="text-sm text-slate-600 dark:text-slate-700 font-medium">{selo.meta} resultados</p>
              </div>
              
              {!selo.conquistado && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm font-semibold text-slate-700">
                    <span>{selo.atual}/{selo.meta}</span>
                    <span>{Math.round(selo.progresso)}%</span>
                  </div>
                  <Progress value={selo.progresso} className="h-3 bg-slate-200" />
                  <p className="text-sm text-center text-slate-600 mt-1 font-medium">
                    Faltam {selo.meta - selo.atual} resultados
                  </p>
                </div>
              )}
              
              {selo.conquistado && (
                <p className="text-sm text-center text-emerald-600 font-bold">
                  Conquistado!
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Outras Conquistas */}
      {todas_conquistas.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <Star className="w-4 h-4 text-amber-400" />
            Outras Conquistas
          </h3>
          
          <div className="grid grid-cols-2 gap-2">
            {todas_conquistas
              .filter(c => !['12_resultados', '20_resultados', '30_resultados'].includes(c.codigo))
              .map((conquista) => (
                <div 
                  key={conquista.codigo}
                  className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700"
                >
                  <span className="text-2xl">{conquista.icone}</span>
                  <div>
                    <p className="text-white font-medium text-sm">{conquista.nome}</p>
                    <p className="text-xs text-slate-400">{conquista.descricao}</p>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Conquistas Disponíveis (não conquistadas) */}
      <div className="pt-4 border-t border-slate-700">
        <h3 className="text-sm font-semibold text-slate-400 mb-2 flex items-center gap-2">
          <Target className="w-4 h-4" />
          Próximas Conquistas
        </h3>
        <p className="text-xs text-slate-500">
          Continue participando de corridas para desbloquear mais conquistas!
        </p>
      </div>
    </div>
  );
};

export default SelosAtleta;
