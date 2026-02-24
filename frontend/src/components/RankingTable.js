import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import MedalIcon from '@/components/MedalIcon';
import UFBadge from '@/components/UFBadge';
import PendingBadge from '@/components/PendingBadge';

const RankingTable = ({ data, onAtletaClick }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-slate-600 dark:text-slate-400">
        Nenhum atleta encontrado.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full" data-testid="ranking-table">
        <thead>
          <tr className="border-b-2 border-slate-200 dark:border-slate-700">
            <th className="text-center py-3 px-2 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              Colocação
            </th>
            <th className="text-center py-3 px-2 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              UF
            </th>
            <th className="text-left py-3 px-4 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              Nome
            </th>
            <th className="text-left py-3 px-2 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              Cidade
            </th>
            <th className="text-center py-3 px-2 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              Faixa
            </th>
            <th className="text-center py-3 px-2 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              Nº Provas
            </th>
            <th className="text-right py-3 px-2 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              PTS
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((atleta, index) => (
            <tr
              key={index}
              onClick={() => onAtletaClick && onAtletaClick(atleta.id)}
              className="border-b border-slate-100 dark:border-slate-800 hover:bg-emerald-50 dark:hover:bg-emerald-900/10 transition-colors cursor-pointer"
              data-testid={`atleta-row-${index}`}
            >
              {/* Colocação */}
              <td className="py-4 px-2">
                <div className="flex items-center justify-center">
                  {atleta.colocacao <= 3 ? (
                    <MedalIcon position={atleta.colocacao} />
                  ) : (
                    <span className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                      {atleta.colocacao}
                    </span>
                  )}
                </div>
              </td>

              {/* UF Badge */}
              <td className="py-4 px-2">
                <div className="flex justify-center">
                  <UFBadge uf={atleta.uf} />
                </div>
              </td>

              {/* Foto + Nome + Equipe */}
              <td className="py-4 px-4">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Avatar
                      className={`h-12 w-12 ${
                        atleta.is_elite
                          ? 'ring-2 ring-amber-500 ring-offset-2 ring-offset-white dark:ring-offset-slate-900'
                          : ''
                      }`}
                    >
                      <AvatarImage src={atleta.foto_url} alt={atleta.nome} />
                      <AvatarFallback className="bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300 font-semibold">
                        {atleta.nome.split(' ').map(n => n[0]).join('').substring(0, 2)}
                      </AvatarFallback>
                    </Avatar>
                    {atleta.is_pendente && (
                      <div className="absolute -bottom-1 -right-1">
                        <PendingBadge />
                      </div>
                    )}
                  </div>
                  <div>
                    <div className="font-bold text-slate-900 dark:text-white text-sm">
                      {atleta.nome}
                      {atleta.is_elite && (
                        <Badge variant="secondary" className="ml-2 text-xs bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">
                          Elite
                        </Badge>
                      )}
                    </div>
                    <div className="text-xs text-slate-600 dark:text-slate-400">
                      {atleta.equipe}
                    </div>
                  </div>
                </div>
              </td>

              {/* Cidade */}
              <td className="py-4 px-2 text-sm text-slate-700 dark:text-slate-300">
                {atleta.cidade}
              </td>

              {/* Faixa Etária */}
              <td className="py-4 px-2 text-center">
                <Badge variant="outline" className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold">
                  {atleta.faixa_etaria}
                </Badge>
              </td>

              {/* Número de Provas com Badge Colorido */}
              <td className="py-4 px-2 text-center">
                <div className="flex items-center justify-center">
                  <Badge className={`h-8 w-8 rounded-full flex items-center justify-center font-bold text-white ${
                    atleta.total_corridas >= 12 ? 'bg-emerald-500' :
                    atleta.total_corridas >= 8 ? 'bg-blue-500' :
                    atleta.total_corridas >= 5 ? 'bg-orange-500' :
                    'bg-red-500'
                  }`}>
                    {atleta.total_corridas}
                  </Badge>
                </div>
              </td>

              {/* Pontos */}
              <td className="py-4 px-2 text-right">
                <span className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                  {atleta.pontos}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RankingTable;