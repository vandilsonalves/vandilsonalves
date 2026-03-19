// /app/frontend/src/components/dono-assessoria/SolicitacoesTab.jsx
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { UserPlus, UserCheck, UserX, Clock, MapPin, Eye, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const SolicitacoesTab = ({
  solicitacoesPendentes,
  totalPendentes,
  processandoSolicitacao,
  onAtualizar,
  onAprovar,
  onReprovar,
  onVerPerfil
}) => (
  <div className="space-y-6" data-testid="solicitacoes-tab">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <h2 className="text-2xl font-bold text-white">Solicitações de Entrada</h2>
        {totalPendentes > 0 && (
          <Badge className="bg-red-500 text-white px-3 py-1 animate-pulse" data-testid="total-pendentes">
            {totalPendentes} pendente{totalPendentes > 1 ? 's' : ''}
          </Badge>
        )}
      </div>
      <Button 
        variant="outline" 
        onClick={onAtualizar}
        className="border-slate-600"
      >
        <Clock className="w-4 h-4 mr-2" />
        Atualizar
      </Button>
    </div>

    {solicitacoesPendentes.length === 0 ? (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-12 text-center">
          <UserPlus className="w-16 h-16 mx-auto text-slate-600 mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Nenhuma solicitação pendente</h3>
          <p className="text-slate-400">
            Quando atletas solicitarem entrada na sua assessoria, eles aparecerão aqui para aprovação.
          </p>
        </CardContent>
      </Card>
    ) : (
      <div className="space-y-4">
        {solicitacoesPendentes.map((solicitacao) => (
          <SolicitacaoCard
            key={solicitacao.id}
            solicitacao={solicitacao}
            processando={processandoSolicitacao === solicitacao.id}
            onAprovar={() => onAprovar(solicitacao.id)}
            onReprovar={() => onReprovar(solicitacao.id)}
            onVerPerfil={() => onVerPerfil(solicitacao.atleta_id)}
          />
        ))}
      </div>
    )}
  </div>
);

const SolicitacaoCard = ({ solicitacao, processando, onAprovar, onReprovar, onVerPerfil }) => (
  <Card className="bg-slate-800 border-slate-700 hover:border-amber-500/50 transition-colors" data-testid={`solicitacao-${solicitacao.id}`}>
    <CardContent className="p-6">
      <div className="flex items-start gap-4">
        <Avatar className="w-16 h-16">
          {solicitacao.atleta_foto ? (
            <AvatarImage src={solicitacao.atleta_foto.startsWith('http') ? solicitacao.atleta_foto : `${BACKEND_URL}${solicitacao.atleta_foto}`} />
          ) : null}
          <AvatarFallback className="bg-amber-500 text-white text-xl">
            {solicitacao.atleta_nome?.charAt(0)}
          </AvatarFallback>
        </Avatar>
        
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-semibold text-white">{solicitacao.atleta_nome}</h3>
            <Badge variant="outline" className="text-xs text-amber-400 border-amber-400/50">
              Nova solicitação
            </Badge>
          </div>
          
          <div className="flex flex-wrap gap-3 text-sm text-slate-400 mb-3">
            <span className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              {solicitacao.atleta_cidade || 'Cidade não informada'}, {solicitacao.atleta_estado || 'UF'}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {new Date(solicitacao.data_solicitacao).toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </div>
          
          {solicitacao.mensagem && (
            <div className="bg-slate-700/50 rounded-lg p-3 mb-3">
              <p className="text-sm text-slate-300 italic">"{solicitacao.mensagem}"</p>
            </div>
          )}
          
          <div className="flex gap-2">
            <Button 
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
              onClick={onAprovar}
              disabled={processando}
              data-testid={`btn-aprovar-${solicitacao.id}`}
            >
              {processando ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <UserCheck className="w-4 h-4 mr-2" />
              )}
              Aprovar
            </Button>
            <Button 
              variant="outline"
              className="border-red-500/50 text-red-400 hover:bg-red-500/10"
              onClick={onReprovar}
              disabled={processando}
              data-testid={`btn-reprovar-${solicitacao.id}`}
            >
              <UserX className="w-4 h-4 mr-2" />
              Reprovar
            </Button>
            <Button 
              variant="ghost"
              className="text-slate-400 hover:text-white"
              onClick={onVerPerfil}
            >
              <Eye className="w-4 h-4 mr-2" />
              Ver Perfil
            </Button>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
);
