import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, BadgeCheck, ShieldCheck, CheckCircle, Target } from 'lucide-react';

const DonoVerificacaoCard = ({ assessoria }) => {
  const isVerificada = assessoria.responsavel_nome && 
                       assessoria.total_atletas >= 10 && 
                       assessoria.total_resultados >= 5;
  const atletasProgress = Math.min((assessoria.total_atletas / 10) * 100, 100);
  const resultadosProgress = Math.min((assessoria.total_resultados / 5) * 100, 100);
  const donoProgress = assessoria.responsavel_nome ? 100 : 0;
  const progressoTotal = Math.round((atletasProgress + resultadosProgress + donoProgress) / 3);

  return (
    <Card className={`border-2 ${isVerificada ? 'bg-gradient-to-br from-blue-900/50 to-indigo-900/50 border-blue-500' : 'bg-slate-800/50 border-slate-600'}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white flex items-center gap-2">
            <ShieldCheck className={`w-5 h-5 ${isVerificada ? 'text-blue-400' : 'text-slate-400'}`} />
            Progresso para Verificação
          </CardTitle>
          {isVerificada ? (
            <Badge className="bg-blue-500 text-white flex items-center gap-1">
              <BadgeCheck className="w-4 h-4" />
              Verificada
            </Badge>
          ) : (
            <Badge variant="outline" className="text-slate-400 border-slate-500">
              {progressoTotal}% completo
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {isVerificada ? (
          <div className="text-center py-4">
            <div className="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-3">
              <BadgeCheck className="w-10 h-10 text-blue-400" />
            </div>
            <p className="text-blue-300 font-medium">Parabéns! Sua assessoria é verificada!</p>
            <p className="text-slate-400 text-sm mt-1">
              O selo de verificação aparece em toda a plataforma.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-slate-400 text-sm mb-4">
              Complete os critérios abaixo para obter o selo de verificação da sua assessoria.
            </p>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2">
                  <Users className={`w-4 h-4 ${assessoria.total_atletas >= 10 ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span className="text-sm text-slate-300">10+ Atletas</span>
                </div>
                <span className={`text-sm font-medium ${assessoria.total_atletas >= 10 ? 'text-emerald-400' : 'text-slate-400'}`}>
                  {assessoria.total_atletas}/10
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-emerald-500 h-2 rounded-full transition-all" style={{ width: `${atletasProgress}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2">
                  <Target className={`w-4 h-4 ${assessoria.total_resultados >= 5 ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span className="text-sm text-slate-300">5+ Resultados</span>
                </div>
                <span className={`text-sm font-medium ${assessoria.total_resultados >= 5 ? 'text-emerald-400' : 'text-slate-400'}`}>
                  {assessoria.total_resultados}/5
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-emerald-500 h-2 rounded-full transition-all" style={{ width: `${resultadosProgress}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2">
                  <CheckCircle className={`w-4 h-4 ${assessoria.responsavel_nome ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span className="text-sm text-slate-300">Responsável Definido</span>
                </div>
                <span className={`text-sm font-medium ${assessoria.responsavel_nome ? 'text-emerald-400' : 'text-slate-400'}`}>
                  {assessoria.responsavel_nome ? 'Sim' : 'Não'}
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-emerald-500 h-2 rounded-full transition-all" style={{ width: `${donoProgress}%` }} />
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DonoVerificacaoCard;
