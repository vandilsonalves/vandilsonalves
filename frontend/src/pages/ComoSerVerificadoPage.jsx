import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  BadgeCheck, ArrowLeft, Trophy, Star, Zap, Shield, 
  BarChart3, Activity, Eye, Crown, ChevronRight
} from 'lucide-react';

const ComoSerVerificadoPage = () => {
  const navigate = useNavigate();

  const beneficios = [
    {
      icone: BadgeCheck,
      titulo: 'Selo de Verificado',
      descricao: 'Destaque-se no ranking com o selo azul de atleta premium ao lado do seu nome e avatar.',
      cor: 'text-blue-400',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20'
    },
    {
      icone: BarChart3,
      titulo: 'Raio-X Completo',
      descricao: 'Acesso ao Raio-X com estatísticas detalhadas, gráficos de evolução e insígnias exclusivas.',
      cor: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20'
    },
    {
      icone: Activity,
      titulo: 'Integração Strava',
      descricao: 'Conecte sua conta do Strava e importe suas corridas automaticamente para o ranking.',
      cor: 'text-orange-400',
      bg: 'bg-orange-500/10',
      border: 'border-orange-500/20'
    },
    {
      icone: Eye,
      titulo: 'Feed Social',
      descricao: 'Participe do feed social da sua equipe, compartilhe conquistas e interaja com outros atletas.',
      cor: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20'
    },
    {
      icone: Trophy,
      titulo: 'Ranking Exclusivo',
      descricao: 'Submeta seus resultados e concorra no ranking nacional e estadual com atletas de todo o Brasil.',
      cor: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20'
    },
    {
      icone: Shield,
      titulo: 'Suporte Prioritário',
      descricao: 'Atendimento prioritário pela equipe Ranking Run para qualquer dúvida ou problema.',
      cor: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
      border: 'border-cyan-500/20'
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950" data-testid="como-ser-verificado-page">
      {/* Header */}
      <div className="bg-gradient-to-b from-blue-600/20 to-transparent">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <Button 
            onClick={() => navigate(-1)} 
            variant="ghost" 
            size="sm" 
            className="text-slate-400 hover:text-white mb-6"
            data-testid="btn-voltar-verificado"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </Button>

          {/* Hero */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-500/20 border-2 border-blue-500/30 mb-6">
              <BadgeCheck className="w-10 h-10 text-blue-400" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
              Seja um Atleta <span className="text-blue-400">Verificado</span>
            </h1>
            <p className="text-slate-400 max-w-xl mx-auto text-base">
              Assine o Ranking Run e ganhe o selo de verificado, acesso completo 
              à plataforma e muito mais para sua jornada esportiva.
            </p>
          </div>

          {/* Preview do selo */}
          <Card className="bg-slate-800/50 border-slate-700/50 mb-12 max-w-md mx-auto">
            <CardContent className="pt-6">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-4 text-center font-medium">
                Como aparece no ranking
              </p>
              <div className="flex items-center gap-3 bg-slate-900/50 rounded-lg p-4">
                <div className="relative">
                  <Avatar className="h-12 w-12 ring-2 ring-blue-500 ring-offset-2 ring-offset-slate-800">
                    <AvatarFallback className="bg-emerald-600 text-white font-bold">VC</AvatarFallback>
                  </Avatar>
                  <div className="absolute -bottom-1 -right-1">
                    <BadgeCheck className="w-5 h-5 text-blue-500 fill-blue-500 stroke-white drop-shadow" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm">Seu Nome</span>
                    <Badge className="bg-amber-500/20 text-amber-400 text-[10px]">Elite</Badge>
                  </div>
                  <span className="text-xs text-slate-500">Sua Equipe</span>
                </div>
                <span className="text-2xl font-bold text-amber-400">98</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Benefícios */}
      <div className="container mx-auto px-4 max-w-4xl pb-12">
        <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
          <Star className="w-5 h-5 text-amber-400" />
          Benefícios do Plano Premium
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-12">
          {beneficios.map((b, i) => (
            <Card key={i} className={`${b.bg} border ${b.border} hover:scale-[1.02] transition-transform`}>
              <CardContent className="pt-5 pb-5 flex items-start gap-4">
                <div className={`w-10 h-10 rounded-lg ${b.bg} border ${b.border} flex items-center justify-center flex-shrink-0`}>
                  <b.icone className={`w-5 h-5 ${b.cor}`} />
                </div>
                <div>
                  <h3 className="font-bold text-white text-sm mb-1">{b.titulo}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{b.descricao}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Como funciona */}
        <Card className="bg-slate-800/30 border-slate-700/50 mb-12">
          <CardContent className="pt-6">
            <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              Como funciona?
            </h2>
            <div className="space-y-4">
              {[
                { num: '1', texto: 'Escolha seu plano e realize o pagamento via Pix ou Cartão de Crédito.' },
                { num: '2', texto: 'Sua conta é ativada instantaneamente com todos os recursos premium.' },
                { num: '3', texto: 'O selo de verificado aparece automaticamente no seu avatar em toda a plataforma.' }
              ].map((step) => (
                <div key={step.num} className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-blue-400">{step.num}</span>
                  </div>
                  <p className="text-sm text-slate-300 pt-1">{step.texto}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* CTA */}
        <Card className="bg-gradient-to-r from-blue-600 to-blue-700 border-0 overflow-hidden relative">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDUpIi8+PC9zdmc+')] opacity-50" />
          <CardContent className="pt-8 pb-8 text-center relative">
            <Crown className="w-10 h-10 text-amber-300 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">
              Torne-se Premium hoje!
            </h2>
            <p className="text-blue-100 mb-6 max-w-md mx-auto text-sm">
              Assine o Ranking Run e desbloqueie todos os recursos da plataforma 
              com o selo de atleta verificado.
            </p>
            <Button 
              onClick={() => navigate('/pagamento')} 
              className="bg-white text-blue-700 hover:bg-blue-50 font-bold px-8 py-3 text-base"
              data-testid="btn-assinar-premium"
            >
              Assinar agora
              <ChevronRight className="w-5 h-5 ml-1" />
            </Button>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-slate-600 mt-6">
          Dúvidas? Entre em contato com o suporte pelo e-mail suporte@rankingrun.com.br
        </p>
      </div>
    </div>
  );
};

export default ComoSerVerificadoPage;
