import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import MedalIcon from '@/components/MedalIcon';
import UFBadge from '@/components/UFBadge';

const RankingTable = ({ data }) => {
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
          <tr className="border-b border-slate-200 dark:border-slate-700">
            <th className="text-left py-3 px-2 text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Colocação
            </th>
            <th className="text-left py-3 px-2 text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              UF
            </th>
            <th className="text-left py-3 px-2 text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Nome
            </th>
            <th className="text-left py-3 px-2 text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Cidade
            </th>
            <th className="text-left py-3 px-2 text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Equipe
            </th>
            <th className="text-center py-3 px-2 text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Nº
            </th>
            <th className="text-right py-3 px-2 text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Pts
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((atleta, index) => (
            <tr
              key={index}
              className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
              data-testid={`atleta-row-${index}`}
            >
              {/* Colocação */}
              <td className="py-4 px-2">
                <div className="flex items-center justify-center w-10">
                  {atleta.colocacao <= 3 ? (
                    <MedalIcon position={atleta.colocacao} />
                  ) : (
                    <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                      {atleta.colocacao}
                    </span>
                  )}
                </div>
              </td>

              {/* UF Badge */}
              <td className="py-4 px-2">
                <UFBadge uf={atleta.uf} />
              </td>

              {/* Foto + Nome + Equipe */}
              <td className="py-4 px-2">
                <div className="flex items-center gap-3">
                  <Avatar
                    className={`h-10 w-10 ${
                      atleta.is_elite
                        ? 'ring-2 ring-amber-500 ring-offset-2 ring-offset-white dark:ring-offset-slate-900'
                        : ''
                    }`}
                  >
                    <AvatarImage src={atleta.foto_url} alt={atleta.nome} />
                    <AvatarFallback className="bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                      {atleta.nome.split(' ').map(n => n[0]).join('').substring(0, 2)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="font-semibold text-slate-900 dark:text-white text-sm">
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

              {/* Equipe (coluna separada mobile) - hidden em desktop pois já aparece com nome */}
              <td className="py-4 px-2 text-sm text-slate-600 dark:text-slate-400 hidden xl:table-cell">
                {atleta.equipe}
              </td>

              {/* Número de Corridas */}
              <td className="py-4 px-2 text-center text-sm font-medium text-slate-700 dark:text-slate-300">
                {atleta.total_corridas}
              </td>

              {/* Pontos */}
              <td className="py-4 px-2 text-right">
                <span className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
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