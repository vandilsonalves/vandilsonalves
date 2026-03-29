import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Download, Send, Eye, UserX, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function getNomeDisplay(atleta) {
  const apelido = (atleta.apelido || '').trim();
  if (apelido) return apelido;
  const partes = (atleta.nome || '').split(' ');
  if (partes.length >= 2) return `${partes[0]} ${partes[1]}`;
  return atleta.nome || '';
}

export const AtletasTab = ({ atletas, onExportar, onEnviarMensagem, onVerPerfil, onDesvincular }) => (
  <div className="space-y-6">
    <div className="flex items-center justify-between flex-wrap gap-2">
      <h2 className="text-2xl font-bold text-white">Meus Atletas</h2>
      <div className="flex gap-2">
        <Button variant="outline" onClick={onExportar} size="sm">
          <Download className="w-4 h-4 mr-2" />
          Exportar Lista
        </Button>
        <Button onClick={onEnviarMensagem} className="bg-amber-500 hover:bg-amber-600" size="sm">
          <Send className="w-4 h-4 mr-2" />
          Enviar Mensagem
        </Button>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {atletas.map((atleta) => (
        <AtletaCard 
          key={atleta.id} 
          atleta={atleta} 
          onVerPerfil={() => onVerPerfil(atleta.id)} 
          onDesvincular={onDesvincular}
        />
      ))}
    </div>
  </div>
);

const AtletaCard = ({ atleta, onVerPerfil, onDesvincular }) => {
  const [showDesvincular, setShowDesvincular] = useState(false);
  const [motivo, setMotivo] = useState('');
  const [desvinculando, setDesvinculando] = useState(false);

  const handleDesvincular = async () => {
    setDesvinculando(true);
    try {
      await onDesvincular(atleta.id, motivo);
      setShowDesvincular(false);
      setMotivo('');
    } catch (e) {
      // error handled in parent
    } finally {
      setDesvinculando(false);
    }
  };

  return (
    <>
      <Card className="bg-slate-800 border-slate-700 hover:border-amber-500/50 transition-colors">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <Avatar className="w-14 h-14">
              {atleta.foto_url ? (
                <AvatarImage src={atleta.foto_url.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
              ) : null}
              <AvatarFallback className="bg-amber-500 text-white text-lg">
                {atleta.nome?.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-white truncate" data-testid={`atleta-nome-${atleta.id}`}>
                {getNomeDisplay(atleta)}
              </h3>
              {atleta.apelido && (
                <p className="text-xs text-slate-500 truncate">{atleta.nome}</p>
              )}
              <div className="flex gap-2 mt-1">
                <Badge variant="outline" className="text-xs text-slate-400 border-slate-600">
                  {atleta.categoria?.toUpperCase() || 'NORMAL'}
                </Badge>
                <Badge variant="outline" className="text-xs text-slate-400 border-slate-600">
                  {atleta.genero === 'M' ? 'Masc' : 'Fem'}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-amber-500">{atleta.pontos || 0}</p>
              <p className="text-xs text-slate-400">pontos</p>
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <Button 
              size="sm" 
              variant="outline" 
              className="flex-1 border-slate-600 text-slate-300"
              onClick={onVerPerfil}
            >
              <Eye className="w-4 h-4 mr-1" />
              Ver Perfil
            </Button>
            {onDesvincular && (
              <Button 
                size="sm" 
                variant="outline" 
                className="border-red-800/50 text-red-400 hover:bg-red-900/20 hover:text-red-300"
                onClick={() => setShowDesvincular(true)}
                data-testid={`btn-desvincular-${atleta.id}`}
              >
                <UserX className="w-4 h-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Dialog open={showDesvincular} onOpenChange={setShowDesvincular}>
        <DialogContent className="bg-slate-800 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">Desvincular Atleta</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <p className="text-sm text-slate-300">
              Tem certeza que deseja desvincular <strong className="text-amber-400">{getNomeDisplay(atleta)}</strong> da sua assessoria?
            </p>
            <p className="text-xs text-slate-500">O atleta voltará a ser "Individual" e será notificado.</p>
            <Textarea
              value={motivo}
              onChange={e => setMotivo(e.target.value)}
              placeholder="Motivo da desvinculação (opcional)..."
              className="bg-slate-900 border-slate-700 text-white min-h-20"
              data-testid="input-motivo-desvincular"
            />
          </div>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setShowDesvincular(false)}>Cancelar</Button>
            <Button 
              variant="destructive" 
              onClick={handleDesvincular}
              disabled={desvinculando}
              data-testid="btn-confirmar-desvincular"
            >
              {desvinculando ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <UserX className="w-4 h-4 mr-1" />}
              Desvincular
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
