const PendingBadge = () => {
  return (
    <div 
      className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shadow-lg"
      title="Pendente - Menos de 12 provas no ano"
      data-testid="pending-badge"
    >
      P
    </div>
  );
};

export default PendingBadge;