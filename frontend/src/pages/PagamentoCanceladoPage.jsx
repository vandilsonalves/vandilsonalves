import { useNavigate } from 'react-router-dom';
import { XCircle, ArrowLeft, CreditCard } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function PagamentoCanceladoPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-4" data-testid="pagamento-cancelado-page">
      <div className="max-w-md w-full text-center">
        <div className="w-20 h-20 bg-amber-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
          <XCircle className="w-10 h-10 text-amber-400" />
        </div>
        <h2 className="text-2xl font-bold mb-3">Pagamento Cancelado</h2>
        <p className="text-gray-400 mb-8">
          O pagamento foi cancelado. Nenhum valor foi cobrado. Voce pode tentar novamente a qualquer momento.
        </p>
        <div className="flex flex-col gap-3">
          <Button
            onClick={() => navigate('/pagamento')}
            className="bg-emerald-600 hover:bg-emerald-500 text-white"
            data-testid="btn-tentar-novamente"
          >
            <CreditCard className="w-4 h-4 mr-2" /> Tentar Novamente
          </Button>
          <Button
            onClick={() => navigate('/')}
            variant="outline"
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            data-testid="btn-voltar"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Voltar ao Ranking
          </Button>
        </div>
      </div>
    </div>
  );
}
