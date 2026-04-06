import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Award, Calendar, MapPin, UserPlus, TrendingUp, BarChart3 } from 'lucide-react';
import { Trophy, Medal } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell,
  AreaChart, Area
} from 'recharts';

const DonoGraficosAvancados = ({ graficosAvancados, atletas, assessoria }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Distribuição por Cidade */}
      {atletas.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <MapPin className="w-5 h-5 text-emerald-500" />
              Distribuição por Cidade
            </CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              const cidadeCount = atletas.reduce((acc, atleta) => {
                const cidade = atleta.cidade || 'Não informada';
                acc[cidade] = (acc[cidade] || 0) + 1;
                return acc;
              }, {});
              const cidadeData = Object.entries(cidadeCount)
                .map(([cidade, count]) => ({ cidade: cidade.substring(0, 15), total: count }))
                .sort((a, b) => b.total - a.total)
                .slice(0, 6);
              
              return (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={cidadeData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" stroke="#9CA3AF" />
                    <YAxis dataKey="cidade" type="category" stroke="#9CA3AF" width={100} tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                    <Bar dataKey="total" fill="#10B981" radius={[0, 4, 4, 0]} name="Atletas" />
                  </BarChart>
                </ResponsiveContainer>
              );
            })()}
          </CardContent>
        </Card>
      )}

      {/* Top Atletas */}
      {atletas.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Medal className="w-5 h-5 text-amber-500" />
              Top 5 Atletas - Mais Pontos
            </CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              const topAtletas = [...atletas]
                .sort((a, b) => (b.pontos_total || 0) - (a.pontos_total || 0))
                .slice(0, 5)
                .map(a => ({
                  nome: a.nome?.split(' ').slice(0, 2).join(' ') || 'Atleta',
                  pontos: a.pontos_total || 0
                }));
              
              return (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={topAtletas}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="nome" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                    <Bar dataKey="pontos" fill="#F59E0B" radius={[4, 4, 0, 0]} name="Pontos" />
                  </BarChart>
                </ResponsiveContainer>
              );
            })()}
          </CardContent>
        </Card>
      )}

      {/* Conquistas da Equipe */}
      {assessoria && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-500" />
              Conquistas da Equipe
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-gradient-to-br from-yellow-500/20 to-amber-500/20 rounded-lg p-4">
                <div className="text-3xl mb-1">1</div>
                <p className="text-2xl font-bold text-yellow-400">{assessoria.total_primeiros || 0}</p>
                <p className="text-xs text-slate-400">Primeiros Lugares</p>
              </div>
              <div className="bg-gradient-to-br from-slate-400/20 to-slate-500/20 rounded-lg p-4">
                <div className="text-3xl mb-1">2</div>
                <p className="text-2xl font-bold text-slate-300">
                  {Math.floor((assessoria.total_podios || 0) * 0.4)}
                </p>
                <p className="text-xs text-slate-400">Segundos Lugares</p>
              </div>
              <div className="bg-gradient-to-br from-amber-700/20 to-orange-700/20 rounded-lg p-4">
                <div className="text-3xl mb-1">3</div>
                <p className="text-2xl font-bold text-amber-600">
                  {(assessoria.total_podios || 0) - (assessoria.total_primeiros || 0) - Math.floor((assessoria.total_podios || 0) * 0.4)}
                </p>
                <p className="text-xs text-slate-400">Terceiros Lugares</p>
              </div>
            </div>
            <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Total de Pódios</span>
                <span className="text-xl font-bold text-white">{assessoria.total_podios || 0}</span>
              </div>
              <div className="flex justify-between items-center mt-2">
                <span className="text-slate-400">Total de Resultados</span>
                <span className="text-xl font-bold text-white">{assessoria.total_resultados || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Distribuição por Gênero */}
      {graficosAvancados?.grafico_genero && graficosAvancados.grafico_genero.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Users className="w-5 h-5 text-pink-500" />
              Distribuição por Gênero
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <RechartsPieChart>
                <Pie
                  data={graficosAvancados.grafico_genero}
                  cx="50%" cy="50%" innerRadius={50} outerRadius={80}
                  paddingAngle={5} dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {graficosAvancados.grafico_genero.map((entry, index) => (
                    <Cell key={`cell-g-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Distribuição por Categoria */}
      {graficosAvancados?.grafico_categoria && graficosAvancados.grafico_categoria.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-green-500" />
              Distribuição por Categoria
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <RechartsPieChart>
                <Pie
                  data={graficosAvancados.grafico_categoria}
                  cx="50%" cy="50%" outerRadius={80} dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {graficosAvancados.grafico_categoria.map((entry, index) => (
                    <Cell key={`cell-c-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Faixa Etária */}
      {graficosAvancados?.grafico_faixa_etaria && graficosAvancados.grafico_faixa_etaria.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-purple-500" />
              Distribuição por Faixa Etária
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={graficosAvancados.grafico_faixa_etaria}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="faixa" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
                <YAxis stroke="#9CA3AF" />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                <Bar dataKey="atletas" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="Atletas" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Resultados por Mês */}
      {graficosAvancados?.resultados_por_mes && graficosAvancados.resultados_por_mes.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-cyan-500" />
              Resultados por Mês (Últimos 6 meses)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={graficosAvancados.resultados_por_mes}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                <Area type="monotone" dataKey="resultados" stroke="#06B6D4" fill="#06B6D4" fillOpacity={0.3} name="Resultados" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Distâncias Mais Corridas */}
      {graficosAvancados?.grafico_distancias && graficosAvancados.grafico_distancias.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <MapPin className="w-5 h-5 text-red-500" />
              Distâncias Mais Corridas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={graficosAvancados.grafico_distancias.slice(0, 6)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9CA3AF" />
                <YAxis dataKey="distancia" type="category" stroke="#9CA3AF" width={60} tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                <Bar dataKey="corridas" fill="#EF4444" radius={[0, 4, 4, 0]} name="Corridas" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Novos Atletas por Mês */}
      {graficosAvancados?.evolucao_atletas && graficosAvancados.evolucao_atletas.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <UserPlus className="w-5 h-5 text-emerald-500" />
              Novos Atletas por Mês
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={graficosAvancados.evolucao_atletas}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="mes" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                <Bar dataKey="novos_atletas" fill="#10B981" radius={[4, 4, 0, 0]} name="Novos Atletas" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Indicadores de Performance */}
      {graficosAvancados?.estatisticas && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-500" />
              Indicadores de Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-white">{graficosAvancados.estatisticas.media_pontos_atleta}</p>
                <p className="text-xs text-slate-400">Média Pontos/Atleta</p>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-white">{graficosAvancados.estatisticas.media_corridas_atleta}</p>
                <p className="text-xs text-slate-400">Média Corridas/Atleta</p>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-amber-400">{graficosAvancados.estatisticas.total_vitorias}</p>
                <p className="text-xs text-slate-400">Total Vitórias</p>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-green-400">{graficosAvancados.estatisticas.taxa_podio}%</p>
                <p className="text-xs text-slate-400">Taxa de Pódio</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DonoGraficosAvancados;
