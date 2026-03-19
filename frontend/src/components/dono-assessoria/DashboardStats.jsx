// /app/frontend/src/components/dono-assessoria/DashboardStats.jsx
import { Card, CardContent } from '@/components/ui/card';
import { Trophy, MapPin, Calendar, Target, Users, CheckCircle, Medal, Award } from 'lucide-react';

export const RankingCards = ({ rankingNacional, rankingEstadual, rankingMensal, rankingAnual }) => (
  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Ranking Nacional</p>
            <p className="text-3xl font-bold text-amber-500">{rankingNacional || '-'}º</p>
          </div>
          <Trophy className="w-10 h-10 text-amber-500/30" />
        </div>
      </CardContent>
    </Card>
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Ranking Estadual</p>
            <p className="text-3xl font-bold text-blue-500">{rankingEstadual || '-'}º</p>
          </div>
          <MapPin className="w-10 h-10 text-blue-500/30" />
        </div>
      </CardContent>
    </Card>
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Ranking Mensal</p>
            <p className="text-3xl font-bold text-emerald-500">{rankingMensal || '-'}º</p>
          </div>
          <Calendar className="w-10 h-10 text-emerald-500/30" />
        </div>
      </CardContent>
    </Card>
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Ranking Anual</p>
            <p className="text-3xl font-bold text-purple-500">{rankingAnual || '-'}º</p>
          </div>
          <Target className="w-10 h-10 text-purple-500/30" />
        </div>
      </CardContent>
    </Card>
  </div>
);

export const MetricasCards = ({ assessoria }) => (
  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
    <Card className="bg-gradient-to-br from-emerald-600 to-emerald-700">
      <CardContent className="p-6 text-white">
        <Users className="w-8 h-8 mb-2 opacity-80" />
        <p className="text-3xl font-bold">{assessoria.total_atletas}</p>
        <p className="text-sm opacity-80">Atletas</p>
      </CardContent>
    </Card>
    <Card className="bg-gradient-to-br from-blue-600 to-blue-700">
      <CardContent className="p-6 text-white">
        <CheckCircle className="w-8 h-8 mb-2 opacity-80" />
        <p className="text-3xl font-bold">{assessoria.total_resultados}</p>
        <p className="text-sm opacity-80">Resultados</p>
      </CardContent>
    </Card>
    <Card className="bg-gradient-to-br from-yellow-600 to-yellow-700">
      <CardContent className="p-6 text-white">
        <Medal className="w-8 h-8 mb-2 opacity-80" />
        <p className="text-3xl font-bold">{assessoria.total_primeiros}</p>
        <p className="text-sm opacity-80">1º Lugares</p>
      </CardContent>
    </Card>
    <Card className="bg-gradient-to-br from-amber-600 to-amber-700">
      <CardContent className="p-6 text-white">
        <Award className="w-8 h-8 mb-2 opacity-80" />
        <p className="text-3xl font-bold">{assessoria.pontos_total}</p>
        <p className="text-sm opacity-80">Pontos Total</p>
      </CardContent>
    </Card>
  </div>
);
