const MedalIcon = ({ position }) => {
  const medals = {
    1: { emoji: '🥇', color: 'text-yellow-500', label: '1º Lugar' },
    2: { emoji: '🥈', color: 'text-gray-400', label: '2º Lugar' },
    3: { emoji: '🥉', color: 'text-amber-600', label: '3º Lugar' },
  };

  const medal = medals[position];

  if (!medal) return null;

  return (
    <div className="flex items-center justify-center" data-testid={`medal-${position}`}>
      <span className="text-2xl" role="img" aria-label={medal.label}>
        {medal.emoji}
      </span>
    </div>
  );
};

export default MedalIcon;