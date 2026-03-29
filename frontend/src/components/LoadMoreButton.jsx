import { useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';

const LoadMoreButton = ({ current, total, loading, onClick, testId, color = 'emerald' }) => {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
  const sentinelRef = useRef(null);
  const hasTriggered = useRef(false);

  const colorMap = {
    emerald: { bar: 'bg-emerald-500', track: 'bg-emerald-100', text: 'text-emerald-600', spinner: 'border-emerald-500' },
    purple: { bar: 'bg-purple-500', track: 'bg-purple-100', text: 'text-purple-600', spinner: 'border-purple-500' },
    amber: { bar: 'bg-amber-500', track: 'bg-amber-100', text: 'text-amber-600', spinner: 'border-amber-500' },
  };
  const c = colorMap[color] || colorMap.emerald;

  const stableOnClick = useCallback(() => {
    if (!loading && !hasTriggered.current) {
      hasTriggered.current = true;
      onClick();
    }
  }, [loading, onClick]);

  useEffect(() => {
    hasTriggered.current = false;
  }, [current]);

  useEffect(() => {
    const el = sentinelRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !loading && !hasTriggered.current) {
          stableOnClick();
        }
      },
      { rootMargin: '200px' }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [loading, stableOnClick]);

  return (
    <div ref={sentinelRef} className="flex flex-col items-center gap-2 mt-4 py-2" data-testid={testId}>
      {loading ? (
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <div className={`w-4 h-4 border-2 ${c.spinner} border-t-transparent rounded-full animate-spin`} />
          Carregando...
        </div>
      ) : (
        <Button
          onClick={onClick}
          variant="ghost"
          size="sm"
          className="text-xs text-slate-400 hover:text-slate-600"
          data-testid={`${testId}-manual`}
        >
          Carregar mais
        </Button>
      )}
      <div className="w-48 flex items-center gap-2">
        <div className={`flex-1 h-1 ${c.track} rounded-full overflow-hidden`}>
          <div
            className={`h-full ${c.bar} rounded-full transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className={`text-xs ${c.text} min-w-[56px] text-right`}>{current}/{total}</span>
      </div>
    </div>
  );
};

export default LoadMoreButton;
