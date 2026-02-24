import { Badge } from '@/components/ui/badge';
import { MapPin, Calendar, Timer } from 'lucide-react';

const ConquistasTable = ({ corridas }) => {
  if (!corridas || corridas.length === 0) {
    return (
      <div className="text-center py-8 text-slate-600 dark:text-slate-400">
        Nenhuma corrida registrada.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full" data-testid="conquistas-table">
        <thead>
          <tr className="border-b-2 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
            <th className="text-left py-3 px-4 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Corrida
            </th>
            <th className="text-center py-3 px-2 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Colocação
            </th>
            <th className="text-center py-3 px-2 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Tempo
            </th>
            <th className="text-center py-3 px-2 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Pontos
            </th>
            <th className="text-left py-3 px-3 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Local
            </th>
            <th className="text-center py-3 px-2 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Prova
            </th>
            <th className="text-center py-3 px-2 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Data
            </th>
          </tr>
        </thead>
        <tbody>
          {corridas.map((corrida, index) => (
            <tr
              key={corrida.id}
              className={`border-b border-slate-100 dark:border-slate-800 ${
                index % 2 === 0 ? 'bg-white dark:bg-slate-950' : 'bg-slate-50 dark:bg-slate-900'
              } hover:bg-emerald-50 dark:hover:bg-emerald-900/10 transition-colors`}
              data-testid={`corrida-row-${index}`}
            >
              {/* Nome da Corrida */}
              <td className="py-4 px-4 font-semibold text-slate-900 dark:text-white">
                {corrida.nome}
              </td>

              {/* Colocação */}
              <td className="py-4 px-2 text-center">
                <Badge 
                  variant="outline"
                  className={`font-bold ${
                    corrida.colocacao === 1 ? 'bg-yellow-100 text-yellow-800 border-yellow-300' :
                    corrida.colocacao <= 3 ? 'bg-slate-100 text-slate-800 border-slate-300' :
                    'bg-slate-50 text-slate-600 border-slate-200'
                  }`}
                >
                  {corrida.colocacao}º
                </Badge>
              </td>

              {/* Tempo */}
              <td className="py-4 px-2 text-center text-sm font-mono text-slate-700 dark:text-slate-300">
                <div className="flex items-center justify-center gap-1">
                  <Timer className="w-3 h-3" />
                  {corrida.tempo}
                </div>
              </td>

              {/* Pontos */}
              <td className="py-4 px-2 text-center">
                <Badge className="bg-orange-500 hover:bg-orange-600 text-white font-bold">
                  +{corrida.pontos}
                </Badge>
              </td>

              {/* Local */}
              <td className="py-4 px-3 text-sm text-slate-700 dark:text-slate-300">
                <div className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {corrida.local}
                </div>
              </td>

              {/* Distância */}
              <td className="py-4 px-2 text-center">
                <Badge variant="outline" className="font-semibold">
                  {corrida.distancia}
                </Badge>
              </td>

              {/* Data */}
              <td className="py-4 px-2 text-center text-sm text-slate-600 dark:text-slate-400">
                <div className="flex items-center justify-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {new Date(corrida.data).toLocaleDateString('pt-BR')}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ConquistasTable;