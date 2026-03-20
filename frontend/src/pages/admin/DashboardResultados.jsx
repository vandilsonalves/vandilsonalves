import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { 
  CheckCircle, XCircle, ExternalLink, Calendar, MapPin, Trophy, Clock, 
  AlertCircle, Eye, Image, X, Loader2, Users, Zap
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const DashboardResultados = ({ 
  pendentes, 
  loadingPendentes, 
  onAprovar, 
  onReprovar,
  onDeleteFoto,
  onViewFoto,
  actionLoading,
  showFotoModal,
  setShowFotoModal,
  fotoModalUrl
}) => {
  const [showReprovarModal, setShowReprovarModal] = useState(false);
  const [selectedResultado, setSelectedResultado] = useState(null);
  const [motivoReprovacao, setMotivoReprovacao] = useState('');

  const handleOpenReprovar = (resultado) => {
    setSelectedResultado(resultado);
    setMotivoReprovacao('');
    setShowReprovarModal(true);
  };

  const handleConfirmReprovar = async () => {
    if (!motivoReprovacao.trim()) {
      toast.error('Informe o motivo da reprovação');
      return;
    }
    await onReprovar(selectedResultado.id, motivoReprovacao);
    setShowReprovarModal(false);
    setSelectedResultado(null);
    setMotivoReprovacao('');
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-amber-200">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-8 h-8 text-amber-500" />
              <div>
                <h2 className="text-xl font-bold text-amber-800 dark:text-amber-200">
                  Aprovações Pendentes
                </h2>
                <p className="text-sm text-amber-600 dark:text-amber-300">
                  Resultados aguardando análise e aprovação
                </p>
              </div>
            </div>
            <Badge className="text-lg px-4 py-2 bg-amber-500 text-white">
              {pendentes?.length || 0} pendentes
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Pendentes */}
      {loadingPendentes ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
        </div>
      ) : !pendentes || pendentes.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-slate-500">
              <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500 opacity-50" />
              <p className="text-lg font-medium">Nenhum resultado pendente!</p>
              <p className="text-sm">Todos os resultados foram processados</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {pendentes.map((resultado) => (
            <Card key={resultado.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {/* Header do Card */}
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-bold text-lg">{resultado.atleta_nome}</h3>
                        {/* Badge de Modalidade */}
                        {resultado.modalidade_usuario === 'povao_pace_livre' ? (
                          <Badge className="bg-purple-500 text-white text-xs flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            Galera
                          </Badge>
                        ) : (
                          <Badge className="bg-emerald-500 text-white text-xs flex items-center gap-1">
                            <Zap className="w-3 h-3" />
                            Pro/Amador
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-slate-500">{resultado.atleta_email}</p>
                    </div>
                    <Badge className="bg-amber-100 text-amber-800">
                      Pendente
                    </Badge>
                  </div>

                  {/* Informações da Corrida */}
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Trophy className="w-4 h-4 text-amber-500" />
                      <span className="font-medium">{resultado.nome_competicao}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-slate-400" />
                      <span>{resultado.cidade_competicao}/{resultado.estado_competicao}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-slate-400" />
                      <span>{formatDate(resultado.data_competicao)}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        🏅 <strong>{resultado.colocacao}º lugar</strong>
                      </span>
                      <span className="flex items-center gap-1">
                        📏 {resultado.distancia}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {resultado.tempo}
                      </span>
                    </div>
                    {resultado.link_resultado && (
                      <a 
                        href={resultado.link_resultado} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-blue-500 hover:underline"
                      >
                        <ExternalLink className="w-3 h-3" /> Ver resultado oficial
                      </a>
                    )}
                  </div>

                  {/* Foto do Pódio */}
                  {resultado.foto_podio && (
                    <div className="relative">
                      <div className="flex items-center gap-2 mb-2">
                        <Image className="w-4 h-4 text-slate-400" />
                        <span className="text-sm font-medium">Foto do Pódio</span>
                      </div>
                      <div className="relative group">
                        <img
                          src={resultado.foto_podio.startsWith('http') 
                            ? resultado.foto_podio 
                            : `${BACKEND_URL}${resultado.foto_podio}`}
                          alt="Foto do Pódio"
                          className="w-full h-32 object-cover rounded-lg cursor-pointer hover:opacity-90"
                          onClick={() => onViewFoto(resultado.foto_podio)}
                        />
                        <Button
                          variant="destructive"
                          size="sm"
                          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteFoto(resultado.id);
                          }}
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Botões de Ação */}
                  <div className="flex items-center gap-2 pt-2 border-t">
                    <Button
                      onClick={() => onAprovar(resultado.id)}
                      disabled={actionLoading}
                      className="flex-1 bg-green-500 hover:bg-green-600"
                    >
                      {actionLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      ) : (
                        <CheckCircle className="w-4 h-4 mr-2" />
                      )}
                      Aprovar
                    </Button>
                    <Button
                      onClick={() => handleOpenReprovar(resultado)}
                      disabled={actionLoading}
                      variant="destructive"
                      className="flex-1"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Reprovar
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modal de Reprovação */}
      <Dialog open={showReprovarModal} onOpenChange={setShowReprovarModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <XCircle className="w-5 h-5" />
              Reprovar Resultado
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-500 mb-2">
                Atleta: <strong>{selectedResultado?.atleta_nome}</strong>
              </p>
              <p className="text-sm text-slate-500 mb-4">
                Competição: <strong>{selectedResultado?.nome_competicao}</strong>
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Motivo da Reprovação *
              </label>
              <Textarea
                value={motivoReprovacao}
                onChange={(e) => setMotivoReprovacao(e.target.value)}
                placeholder="Informe o motivo da reprovação..."
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReprovarModal(false)}>
              Cancelar
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleConfirmReprovar}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : null}
              Confirmar Reprovação
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Visualização de Foto */}
      <Dialog open={showFotoModal} onOpenChange={setShowFotoModal}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Foto do Pódio</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center">
            <img
              src={fotoModalUrl}
              alt="Foto do Pódio"
              className="max-w-full max-h-[70vh] object-contain rounded-lg"
            />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardResultados;
