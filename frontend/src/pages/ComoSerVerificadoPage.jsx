import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BadgeCheck, Users, CheckCircle, Crown, ArrowLeft, Trophy, 
  Target, Star, Zap, Shield, Award, TrendingUp, UserPlus, Medal
} from 'lucide-react';

const ComoSerVerificadoPage = () => {
  const navigate = useNavigate();

  const criterios = [
    {
      id: 1,
      titulo: '10+ Atletas Cadastrados',
      descricao: 'Tenha pelo menos 10 atletas vinculados à sua assessoria',
      icone: Users,
      cor: 'text-blue-500',
      bgCor: 'bg-blue-50',
      borderCor: 'border-blue-200',
      dica: 'Convide atletas da sua equipe para se cadastrarem na plataforma e selecionarem sua assessoria durante o cadastro.'
    },
    {
      id: 2,
      titulo: '5+ Resultados Aprovados',
      descricao: 'Seus atletas devem ter pelo menos 5 resultados aprovados',
      icone: CheckCircle,
      cor: 'text-green-500',
      bgCor: 'bg-green-50',
      borderCor: 'border-green-200',
      dica: 'Incentive seus atletas a submeterem seus resultados de corridas. Cada resultado aprovado conta para a verificação.'
    },
    {
      id: 3,
      titulo: 'Dono de Assessoria Definido',
      descricao: 'A assessoria deve ter um responsável oficial cadastrado',
      icone: Crown,
      cor: 'text-amber-500',
      bgCor: 'bg-amber-50',
      borderCor: 'border-amber-200',
      dica: 'Entre em contato com a administração para ser promovido a Dono de Assessoria, ou aguarde ser identificado automaticamente.'
    }
  ];

  const beneficios = [
    {
      titulo: 'Credibilidade',
      descricao: 'Selo de verificação visível em toda a plataforma',
      icone: Shield
    },
    {
      titulo: 'Destaque',
      descricao: 'Maior visibilidade no ranking de assessorias',
      icone: Star
    },
    {
      titulo: 'Confiança',
      descricao: 'Atletas preferem equipes verificadas',
      icone: Award
    },
    {
      titulo: 'Reconhecimento',
      descricao: 'Prova de compromisso com o esporte',
      icone: Medal
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="mb-8">
          <Button onClick={() => navigate(-1)} variant="outline" size="sm" className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </Button>
          
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-100 mb-4">
              <BadgeCheck className="w-12 h-12 text-blue-500" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-slate-800 dark:text-white mb-3">
              Como ser uma Assessoria Verificada
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              O selo de verificação é um reconhecimento para assessorias que demonstram 
              compromisso, organização e engajamento na plataforma Ranking Run.
            </p>
          </div>
        </div>

        {/* O que é o Selo */}
        <Card className="mb-8 border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="flex-shrink-0">
                <div className="w-24 h-24 rounded-2xl bg-blue-500 flex items-center justify-center shadow-lg">
                  <BadgeCheck className="w-14 h-14 text-white" />
                </div>
              </div>
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-2xl font-bold text-slate-800 mb-2 flex items-center justify-center md:justify-start gap-2">
                  <span>Selo de Verificação</span>
                  <Badge className="bg-blue-500 text-white">Oficial</Badge>
                </h2>
                <p className="text-slate-600">
                  O selo de verificação aparece ao lado do nome da sua assessoria em toda a plataforma: 
                  na lista de rankings, na página da assessoria e no painel administrativo. 
                  É a forma de mostrar que sua equipe é séria e comprometida com o esporte.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Critérios */}
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6 flex items-center gap-2">
          <Target className="w-6 h-6 text-blue-500" />
          Critérios para Verificação
        </h2>
        
        <div className="grid gap-6 mb-10">
          {criterios.map((criterio, idx) => (
            <Card key={criterio.id} className={`${criterio.bgCor} ${criterio.borderCor} border-2`}>
              <CardContent className="pt-6">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-shrink-0 flex items-start gap-4">
                    <div className={`w-12 h-12 rounded-xl ${criterio.bgCor} border-2 ${criterio.borderCor} flex items-center justify-center`}>
                      <criterio.icone className={`w-6 h-6 ${criterio.cor}`} />
                    </div>
                    <div className="w-8 h-8 rounded-full bg-white border-2 border-slate-200 flex items-center justify-center font-bold text-slate-600">
                      {idx + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-slate-800 mb-1">{criterio.titulo}</h3>
                    <p className="text-slate-600 mb-3">{criterio.descricao}</p>
                    <div className="bg-white/70 rounded-lg p-3 border border-slate-200">
                      <p className="text-sm text-slate-500 flex items-start gap-2">
                        <Zap className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                        <span><strong>Dica:</strong> {criterio.dica}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Exemplo Visual */}
        <Card className="mb-10 overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
            <CardTitle className="flex items-center gap-2">
              <Trophy className="w-5 h-5" />
              Como aparece o Selo
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {/* Exemplo na Lista */}
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-500 mb-2">Na lista de assessorias:</p>
                <div className="flex items-center gap-3 bg-white p-3 rounded-lg border">
                  <span className="w-8 h-8 rounded-full bg-amber-400 text-amber-900 flex items-center justify-center font-bold">1</span>
                  <span className="text-lg">🥇</span>
                  <span className="font-semibold text-amber-700">Sua Assessoria</span>
                  <BadgeCheck className="w-5 h-5 text-blue-500" />
                  <span className="text-slate-400">|</span>
                  <span className="text-slate-600">São Paulo, SP</span>
                </div>
              </div>

              {/* Exemplo na Página */}
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-500 mb-2">Na página da assessoria:</p>
                <div className="bg-gradient-to-r from-amber-500 to-orange-500 p-4 rounded-lg text-white">
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-bold">Sua Assessoria</h3>
                    <Badge className="bg-blue-500 text-white flex items-center gap-1">
                      <BadgeCheck className="w-4 h-4" />
                      Verificada
                    </Badge>
                    <Badge className="bg-white/20">SELO OURO</Badge>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Benefícios */}
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6 flex items-center gap-2">
          <Star className="w-6 h-6 text-amber-500" />
          Benefícios de ser Verificada
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          {beneficios.map((beneficio, idx) => (
            <Card key={idx} className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <beneficio.icone className="w-10 h-10 mx-auto text-blue-500 mb-3" />
                <h3 className="font-bold text-slate-800 mb-1">{beneficio.titulo}</h3>
                <p className="text-sm text-slate-500">{beneficio.descricao}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Progresso Example */}
        <Card className="mb-10 border-2 border-emerald-200 bg-emerald-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-emerald-700">
              <TrendingUp className="w-5 h-5" />
              Acompanhe seu Progresso
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600 mb-4">
              Se você é dono de uma assessoria, pode acompanhar o progresso dos critérios 
              no painel administrativo. Veja um exemplo:
            </p>
            <div className="space-y-4 bg-white p-4 rounded-lg">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">Atletas (8/10)</span>
                  <span className="text-blue-600 font-medium">80%</span>
                </div>
                <Progress value={80} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">Resultados (5/5)</span>
                  <span className="text-green-600 font-medium">100% ✓</span>
                </div>
                <Progress value={100} className="h-2 bg-green-100" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">Dono Definido</span>
                  <span className="text-green-600 font-medium">✓ Completo</span>
                </div>
                <Progress value={100} className="h-2 bg-green-100" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* CTA */}
        <Card className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
          <CardContent className="pt-6 text-center">
            <h2 className="text-2xl font-bold mb-3">Pronto para começar?</h2>
            <p className="text-blue-100 mb-6 max-w-xl mx-auto">
              Convide seus atletas, incentive a submissão de resultados e conquiste 
              o selo de verificação para sua assessoria!
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button 
                onClick={() => navigate('/cadastro')} 
                className="bg-white text-blue-600 hover:bg-blue-50"
              >
                <UserPlus className="w-4 h-4 mr-2" />
                Cadastrar Atleta
              </Button>
              <Button 
                onClick={() => navigate('/')} 
                variant="outline"
                className="border-white text-white hover:bg-white/10"
              >
                <Trophy className="w-4 h-4 mr-2" />
                Ver Ranking de Equipes
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-slate-500">
          <p>
            Dúvidas? Entre em contato com a administração do Ranking Run.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ComoSerVerificadoPage;
