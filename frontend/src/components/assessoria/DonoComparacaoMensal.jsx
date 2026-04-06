import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUpRight, ArrowDownRight, Minus, TrendingUp } from 'lucide-react';

const ComparacaoItem = ({ label, atual, anterior, variacao, color = 'text-white', suffix = '' }) => (
  <div className="bg-slate-800 rounded-lg p-4">
    <div className="flex items-center justify-between mb-2">
      <span className="text-slate-400 text-sm">{label}</span>
      <span className={`flex items-center text-xs font-medium ${
        variacao > 0 ? 'text-green-400' : variacao < 0 ? 'text-red-400' : 'text-slate-400'
      }`}>
        {variacao > 0 ? <ArrowUpRight className="w-3 h-3" /> :
         variacao < 0 ? <ArrowDownRight className="w-3 h-3" /> :
         <Minus className="w-3 h-3" />}
        {Math.abs(variacao)}{suffix || '%'}
      </span>
    </div>
    <div className="flex items-baseline gap-2">
      <span className={`text-2xl font-bold ${color}`}>{atual}{suffix === ' pos' ? 'º' : ''}</span>
      <span className="text-sm text-slate-500">vs {anterior}{suffix === ' pos' ? 'º' : ''}</span>
    </div>
  </div>
);

const DonoComparacaoMensal = ({ comparacaoMensal }) => {
  if (!comparacaoMensal) return null;

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-500" />
          Comparação Mensal
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <ComparacaoItem
            label="Resultados"
            atual={comparacaoMensal.mes_atual.resultados}
            anterior={comparacaoMensal.mes_anterior.resultados}
            variacao={comparacaoMensal.variacoes.resultados}
          />
          <ComparacaoItem
            label="Pontos Conquistados"
            atual={comparacaoMensal.mes_atual.pontos}
            anterior={comparacaoMensal.mes_anterior.pontos}
            variacao={comparacaoMensal.variacoes.pontos}
            color="text-amber-500"
          />
          <ComparacaoItem
            label="Novos Atletas"
            atual={comparacaoMensal.mes_atual.novos_atletas}
            anterior={comparacaoMensal.mes_anterior.novos_atletas}
            variacao={comparacaoMensal.variacoes.novos_atletas}
            color="text-blue-400"
          />
          <ComparacaoItem
            label="Posição Ranking"
            atual={comparacaoMensal.mes_atual.posicao_ranking || '-'}
            anterior={comparacaoMensal.mes_anterior.posicao_ranking || '-'}
            variacao={comparacaoMensal.variacoes.posicao}
            color="text-purple-400"
            suffix=" pos"
          />
        </div>

        <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20">
          <p className="text-amber-200 text-sm">
            {comparacaoMensal.variacoes.pontos > 0 
              ? `Parabéns! Sua assessoria cresceu ${comparacaoMensal.variacoes.pontos}% em pontos este mês.`
              : comparacaoMensal.variacoes.pontos < 0
              ? `Atenção: Queda de ${Math.abs(comparacaoMensal.variacoes.pontos)}% nos pontos. Incentive seus atletas a participar de mais corridas!`
              : `Desempenho estável. Continue motivando seus atletas!`
            }
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default DonoComparacaoMensal;
