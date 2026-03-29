import { Button } from '@/components/ui/button';

const LoadMoreButton = ({ current, total, loading, onClick, testId, color = 'emerald' }) => {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  const colorMap = {
    emerald: { bar: 'bg-emerald-500', track: 'bg-emerald-100', text: 'text-emerald-600', spinner: 'border-emerald-500' },
    purple: { bar: 'bg-purple-500', track: 'bg-purple-100', text: 'text-purple-600', spinner: 'border-purple-500' },
    amber: { bar: 'bg-amber-500', track: 'bg-amber-100', text: 'text-amber-600', spinner: 'border-amber-500' },
  };
  const c = colorMap[color] || colorMap.emerald;

  return (
    <div className="flex justify-center mt-4">
      <Button
        onClick={onClick}
        disabled={loading}
        variant="outline"
        className="w-full md:w-auto flex flex-col items-center gap-1.5 py-3 px-6"
        data-testid={testId}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <div className={`w-4 h-4 border-2 ${c.spinner} border-t-transparent rounded-full animate-spin`} />
            Carregando...
          </span>
        ) : (
          <>
            <span>Carregar mais ({current} de {total})</span>
            <div className="w-full flex items-center gap-2">
              <div className={`flex-1 h-1.5 ${c.track} rounded-full overflow-hidden`}>
                <div
                  className={`h-full ${c.bar} rounded-full transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <span className={`text-xs font-semibold ${c.text} min-w-[32px] text-right`}>{percentage}%</span>
            </div>
          </>
        )}
      </Button>
    </div>
  );
};

export default LoadMoreButton;
