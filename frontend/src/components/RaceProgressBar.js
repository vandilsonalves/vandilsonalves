import { Progress } from '@/components/ui/progress';

const RaceProgressBar = ({ current, total }) => {
  const percentage = Math.min((current / total) * 100, 100);
  
  return (
    <div className="w-full" data-testid="race-progress-bar">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          Progresso de Provas
        </span>
        <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
          {current} / {total}
        </span>
      </div>
      <Progress value={percentage} className="h-3" />
      {current < total && (
        <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">
          Faltam <strong>{total - current} provas</strong> para completar o requisito anual
        </p>
      )}
      {current >= total && (
        <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-2 font-semibold">
          ✅ Requisito anual completo!
        </p>
      )}
    </div>
  );
};

export default RaceProgressBar;