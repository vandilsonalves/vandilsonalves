// /app/frontend/src/components/dono-assessoria/AtletasTab.jsx
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Download, Send, Eye } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const AtletasTab = ({ atletas, onExportar, onEnviarMensagem, onVerPerfil }) => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <h2 className="text-2xl font-bold text-white">Meus Atletas</h2>
      <div className="flex gap-2">
        <Button variant="outline" onClick={onExportar}>
          <Download className="w-4 h-4 mr-2" />
          Exportar Lista
        </Button>
        <Button onClick={onEnviarMensagem} className="bg-amber-500 hover:bg-amber-600">
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
        />
      ))}
    </div>
  </div>
);

const AtletaCard = ({ atleta, onVerPerfil }) => (
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
        <div className="flex-1">
          <h3 className="font-semibold text-white">{atleta.nome}</h3>
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
      </div>
    </CardContent>
  </Card>
);
