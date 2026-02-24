import { Badge } from '@/components/ui/badge';

const UFBadge = ({ uf }) => {
  return (
    <Badge
      variant="outline"
      className="font-semibold text-xs px-2 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-600"
      data-testid={`uf-badge-${uf}`}
    >
      {uf}
    </Badge>
  );
};

export default UFBadge;