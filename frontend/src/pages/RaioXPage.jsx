// /app/frontend/src/pages/RaioXPage.jsx
// Página RAIO-X do Atleta - Análise completa de performance

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ComposedChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, RadialBarChart, RadialBar
} from 'recharts';
import {
  Loader2, ChevronLeft, Download, TrendingUp, TrendingDown, Trophy,
  Target, Zap, Calendar, Clock, Activity, Award, Flame, Star,
  ArrowUpRight, ArrowDownRight, Minus, BarChart3, PieChart as PieIcon, FileText, FileSpreadsheet
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Cores para gráficos
const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
const GRADIENT_COLORS = {
  green: ['#10b981', '#059669'],
  blue: ['#3b82f6', '#2563eb'],
  orange: ['#f59e0b', '#d97706'],
  purple: ['#8b5cf6', '#7c3aed']
};

// Componente de KPI Widget
const KPIWidget = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = "emerald" }) => {
  const colorClasses = {
    emerald: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    blue: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    orange: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    purple: "bg-purple-500/10 text-purple-500 border-purple-500/20"
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-slate-400">{title}</p>
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
            {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
          </div>
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
        {trend !== undefined && (
          <div className="flex items-center gap-1 mt-2">
            {trend > 0 ? (
              <ArrowUpRight className="w-4 h-4 text-emerald-400" />
            ) : trend < 0 ? (
              <ArrowDownRight className="w-4 h-4 text-red-400" />
            ) : (
              <Minus className="w-4 h-4 text-slate-400" />
            )}
            <span className={`text-xs ${trend > 0 ? 'text-emerald-400' : trend < 0 ? 'text-red-400' : 'text-slate-400'}`}>
              {trend > 0 ? '+' : ''}{trendValue || trend}%
            </span>
            <span className="text-xs text-slate-500">vs mês anterior</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Componente de Record Card
const RecordCard = ({ title, value, subtitle, date, icon: Icon, highlight }) => (
  <div className={`p-4 rounded-lg border ${highlight ? 'bg-yellow-500/10 border-yellow-500/30' : 'bg-slate-700/50 border-slate-600'}`}>
    <div className="flex items-center gap-2 mb-2">
      <Icon className={`w-4 h-4 ${highlight ? 'text-yellow-400' : 'text-slate-400'}`} />
      <span className="text-sm text-slate-400">{title}</span>
    </div>
    <p className={`text-xl font-bold ${highlight ? 'text-yellow-400' : 'text-white'}`}>{value}</p>
    {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
    {date && <p className="text-xs text-slate-500 mt-1">{date}</p>}
  </div>
);

const RaioXPage = () => {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('visao-geral');

  useEffect(() => {
    if (token) {
      fetchRaioX();
    }
  }, [token]);

  const fetchRaioX = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/raio-x/completo`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setData(response.data);
    } catch (error) {
      console.error('Erro ao carregar RAIO-X:', error);
      toast.error('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = async () => {
    const loadingToast = toast.loading('Gerando PDF...');
    try {
      // Captura a div principal do conteúdo
      const contentElement = document.getElementById('raio-x-content');
      if (!contentElement) {
        toast.dismiss(loadingToast);
        toast.error('Erro ao capturar conteúdo');
        return;
      }

      // Configura html2canvas para capturar o conteúdo
      const canvas = await html2canvas(contentElement, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#0f172a' // slate-900
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      
      // Cabeçalho
      pdf.setFillColor(16, 185, 129); // emerald-500
      pdf.rect(0, 0, pdfWidth, 25, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(18);
      pdf.text('RAIO-X do Atleta', 15, 15);
      pdf.setFontSize(10);
      pdf.text(`${atleta?.nome || 'Atleta'} - Gerado em ${new Date().toLocaleDateString('pt-BR')}`, 15, 21);

      // Resumo de métricas
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(12);
      let yPos = 35;
      
      pdf.setFontSize(14);
      pdf.setFont(undefined, 'bold');
      pdf.text('Resumo de Performance', 15, yPos);
      yPos += 10;
      
      pdf.setFontSize(10);
      pdf.setFont(undefined, 'normal');
      
      const metricas = [
        ['Score de Consistência:', `${score.score_mes_atual}% - ${score.classificacao}`],
        ['Distância Total:', `${evolucao.totais?.distancia_total_km || 0} km`],
        ['Tempo Total:', `${evolucao.totais?.tempo_total_horas || 0} horas`],
        ['Total de Provas:', `${evolucao.totais?.total_provas || 0}`],
        ['Melhor Pace:', records.records?.melhor_pace?.valor_formatado || '-'],
        ['Média 6 Meses:', `${score.media_6_meses}%`],
      ];
      
      metricas.forEach(([label, value]) => {
        pdf.text(label, 15, yPos);
        pdf.text(value, 70, yPos);
        yPos += 6;
      });

      // Records por categoria
      yPos += 8;
      pdf.setFontSize(14);
      pdf.setFont(undefined, 'bold');
      pdf.text('Records Pessoais (RP)', 15, yPos);
      yPos += 8;
      
      pdf.setFontSize(10);
      pdf.setFont(undefined, 'normal');
      ['5km', '10km', '21km', '42km'].forEach((cat) => {
        const rp = records.records?.por_categoria?.[cat];
        pdf.text(`${cat}:`, 15, yPos);
        if (rp) {
          pdf.text(`${rp.tempo} (Pace: ${rp.pace})`, 35, yPos);
          pdf.text(rp.corrida || '', 90, yPos);
        } else {
          pdf.text('Sem registro', 35, yPos);
        }
        yPos += 6;
      });

      // Evolução mensal
      yPos += 8;
      pdf.setFontSize(14);
      pdf.setFont(undefined, 'bold');
      pdf.text('Evolução Mensal', 15, yPos);
      yPos += 8;
      
      pdf.setFontSize(9);
      pdf.setFont(undefined, 'normal');
      
      // Cabeçalho da tabela
      pdf.setFillColor(226, 232, 240);
      pdf.rect(15, yPos - 4, 180, 6, 'F');
      pdf.text('Mês', 17, yPos);
      pdf.text('Provas', 50, yPos);
      pdf.text('Distância', 75, yPos);
      pdf.text('Tempo', 105, yPos);
      pdf.text('Pace Médio', 135, yPos);
      yPos += 6;
      
      const ultimosMeses = evolucao.evolucao_mensal?.slice(-6) || [];
      ultimosMeses.forEach((mes) => {
        if (yPos > pdfHeight - 20) {
          pdf.addPage();
          yPos = 20;
        }
        pdf.text(mes.mes_formatado || '', 17, yPos);
        pdf.text(String(mes.num_provas || 0), 50, yPos);
        pdf.text(`${mes.distancia_total_km || 0} km`, 75, yPos);
        pdf.text(`${mes.tempo_total_horas || 0}h`, 105, yPos);
        pdf.text(mes.pace_medio || '-', 135, yPos);
        yPos += 5;
      });

      // Adiciona imagem dos gráficos na página 2
      pdf.addPage();
      pdf.setFillColor(16, 185, 129);
      pdf.rect(0, 0, pdfWidth, 15, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(12);
      pdf.text('Visualização dos Gráficos', 15, 10);
      
      const imgWidth = pdfWidth - 20;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 10, 20, imgWidth, Math.min(imgHeight, pdfHeight - 30));

      pdf.save(`RAIO-X_${atleta?.nome?.replace(/\s+/g, '_') || 'Atleta'}_${new Date().toISOString().split('T')[0]}.pdf`);
      
      toast.dismiss(loadingToast);
      toast.success('PDF gerado com sucesso!');
    } catch (error) {
      console.error('Erro ao gerar PDF:', error);
      toast.dismiss(loadingToast);
      toast.error('Erro ao gerar PDF');
    }
  };

  const exportToExcel = () => {
    const loadingToast = toast.loading('Gerando Excel...');
    try {
      const workbook = XLSX.utils.book_new();

      // Aba 1: Resumo
      const resumoData = [
        ['RAIO-X do Atleta - Resumo'],
        [''],
        ['Atleta:', atleta?.nome || 'N/A'],
        ['Data de Geração:', new Date().toLocaleDateString('pt-BR')],
        [''],
        ['MÉTRICAS GERAIS'],
        ['Score de Consistência', `${score.score_mes_atual}%`],
        ['Classificação', score.classificacao],
        ['Distância Total (km)', evolucao.totais?.distancia_total_km || 0],
        ['Tempo Total (horas)', evolucao.totais?.tempo_total_horas || 0],
        ['Total de Provas', evolucao.totais?.total_provas || 0],
        ['Melhor Pace', records.records?.melhor_pace?.valor_formatado || '-'],
        ['Média 6 Meses', `${score.media_6_meses}%`],
        ['Corridas Este Mês', score.corridas_mes_atual],
      ];
      const wsResumo = XLSX.utils.aoa_to_sheet(resumoData);
      wsResumo['!cols'] = [{ wch: 25 }, { wch: 30 }];
      XLSX.utils.book_append_sheet(workbook, wsResumo, 'Resumo');

      // Aba 2: Records Pessoais
      const recordsData = [
        ['RECORDS PESSOAIS (RP)'],
        [''],
        ['Distância', 'Tempo', 'Pace', 'Corrida', 'Data'],
      ];
      ['5km', '10km', '21km', '42km'].forEach((cat) => {
        const rp = records.records?.por_categoria?.[cat];
        recordsData.push([
          cat,
          rp?.tempo || '-',
          rp?.pace || '-',
          rp?.corrida || '-',
          rp?.data ? new Date(rp.data).toLocaleDateString('pt-BR') : '-'
        ]);
      });
      recordsData.push(['']);
      recordsData.push(['DESTAQUES']);
      recordsData.push(['Melhor Pace Geral', records.records?.melhor_pace?.valor_formatado || '-']);
      recordsData.push(['Maior Distância', `${records.records?.maior_distancia?.valor || '-'} km`]);
      
      const wsRecords = XLSX.utils.aoa_to_sheet(recordsData);
      wsRecords['!cols'] = [{ wch: 15 }, { wch: 15 }, { wch: 15 }, { wch: 30 }, { wch: 15 }];
      XLSX.utils.book_append_sheet(workbook, wsRecords, 'Records');

      // Aba 3: Evolução Mensal
      const evolucaoData = [
        ['EVOLUÇÃO MENSAL'],
        [''],
        ['Mês', 'Nº Provas', 'Distância (km)', 'Tempo (h)', 'Pace Médio'],
      ];
      (evolucao.evolucao_mensal || []).forEach((mes) => {
        evolucaoData.push([
          mes.mes_formatado || '',
          mes.num_provas || 0,
          mes.distancia_total_km || 0,
          mes.tempo_total_horas || 0,
          mes.pace_medio || '-'
        ]);
      });
      const wsEvolucao = XLSX.utils.aoa_to_sheet(evolucaoData);
      wsEvolucao['!cols'] = [{ wch: 15 }, { wch: 12 }, { wch: 15 }, { wch: 12 }, { wch: 15 }];
      XLSX.utils.book_append_sheet(workbook, wsEvolucao, 'Evolução Mensal');

      // Aba 4: Comparativo
      const comparativoData = [
        ['COMPARATIVO MENSAL'],
        [''],
        ['Métrica', 'Este Mês', 'Mês Anterior', 'Variação (%)'],
        ['Distância (km)', 
          comparativo.mes_atual?.metricas?.distancia_total_km || 0,
          comparativo.mes_anterior?.metricas?.distancia_total_km || 0,
          `${comparativo.variacoes?.distancia || 0}%`
        ],
        ['Nº de Provas',
          comparativo.mes_atual?.metricas?.num_provas || 0,
          comparativo.mes_anterior?.metricas?.num_provas || 0,
          `${comparativo.variacoes?.provas || 0}%`
        ],
        ['Pace Médio',
          comparativo.mes_atual?.metricas?.pace_medio || '-',
          comparativo.mes_anterior?.metricas?.pace_medio || '-',
          `${comparativo.variacoes?.pace || 0}%`
        ],
      ];
      if (comparativo.melhor_performance_mes) {
        comparativoData.push(['']);
        comparativoData.push(['MELHOR PERFORMANCE DO MÊS']);
        comparativoData.push(['Corrida', comparativo.melhor_performance_mes.corrida]);
        comparativoData.push(['Data', new Date(comparativo.melhor_performance_mes.data).toLocaleDateString('pt-BR')]);
        comparativoData.push(['Distância', `${comparativo.melhor_performance_mes.distancia} km`]);
        comparativoData.push(['Tempo', comparativo.melhor_performance_mes.tempo]);
        comparativoData.push(['Pace', comparativo.melhor_performance_mes.pace]);
      }
      const wsComparativo = XLSX.utils.aoa_to_sheet(comparativoData);
      wsComparativo['!cols'] = [{ wch: 20 }, { wch: 15 }, { wch: 15 }, { wch: 15 }];
      XLSX.utils.book_append_sheet(workbook, wsComparativo, 'Comparativo');

      // Aba 5: Heatmap (Dias da Semana)
      const heatmapData = [
        ['DIAS FAVORITOS PARA CORRER'],
        [''],
        ['Dia', 'Quantidade de Corridas'],
      ];
      Object.entries(heatmap.dias_semana || {}).forEach(([dia, count]) => {
        heatmapData.push([dia, count]);
      });
      heatmapData.push(['']);
      heatmapData.push(['Dia Favorito:', heatmap.dia_favorito || '-']);
      const wsHeatmap = XLSX.utils.aoa_to_sheet(heatmapData);
      wsHeatmap['!cols'] = [{ wch: 20 }, { wch: 25 }];
      XLSX.utils.book_append_sheet(workbook, wsHeatmap, 'Dias da Semana');

      // Aba 6: Histórico de Consistência
      const historicoData = [
        ['HISTÓRICO DE CONSISTÊNCIA'],
        [''],
        ['Mês', 'Score (%)'],
      ];
      (score.historico || []).forEach((item) => {
        historicoData.push([item.mes_formatado || '', item.score || 0]);
      });
      const wsHistorico = XLSX.utils.aoa_to_sheet(historicoData);
      wsHistorico['!cols'] = [{ wch: 15 }, { wch: 15 }];
      XLSX.utils.book_append_sheet(workbook, wsHistorico, 'Histórico Consistência');

      // Aba 7: Previsões
      if (previsoes.tem_dados) {
        const previsoesData = [
          ['PREVISÕES INTELIGENTES'],
          [''],
          ['Pace Base Atual:', previsoes.pace_base],
          ['Corridas Analisadas:', previsoes.corridas_analisadas],
          [''],
          ['PREVISÕES POR DISTÂNCIA'],
          ['Distância', 'Tempo Previsto', 'Pace Previsto', 'Confiança'],
        ];
        Object.entries(previsoes.previsoes || {}).forEach(([, prev]) => {
          previsoesData.push([
            prev.distancia,
            prev.tempo_previsto,
            prev.pace_previsto,
            prev.confianca
          ]);
        });
        previsoesData.push(['']);
        previsoesData.push(['Probabilidade RP próxima corrida:', previsoes.probabilidade_rp_proxima]);
        previsoesData.push(['Dica:', previsoes.dica]);
        
        const wsPrevisoes = XLSX.utils.aoa_to_sheet(previsoesData);
        wsPrevisoes['!cols'] = [{ wch: 30 }, { wch: 20 }, { wch: 20 }, { wch: 15 }];
        XLSX.utils.book_append_sheet(workbook, wsPrevisoes, 'Previsões IA');
      }

      // Gera o arquivo
      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      saveAs(blob, `RAIO-X_${atleta?.nome?.replace(/\s+/g, '_') || 'Atleta'}_${new Date().toISOString().split('T')[0]}.xlsx`);

      toast.dismiss(loadingToast);
      toast.success('Excel gerado com sucesso!');
    } catch (error) {
      console.error('Erro ao gerar Excel:', error);
      toast.dismiss(loadingToast);
      toast.error('Erro ao gerar Excel');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-emerald-500 mx-auto" />
          <p className="text-slate-400 mt-4">Analisando seus dados...</p>
        </div>
      </div>
    );
  }

  if (!data || !data.evolucao?.tem_dados) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Card className="bg-slate-800 border-slate-700 max-w-md">
          <CardContent className="p-8 text-center">
            <Activity className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Sem dados suficientes</h2>
            <p className="text-slate-400 mb-4">
              Você precisa ter corridas registradas para ver seu RAIO-X.
              Comece registrando suas corridas!
            </p>
            <Button onClick={() => navigate('/submeter-resultado')} className="bg-emerald-500 hover:bg-emerald-600">
              Registrar Corrida
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { evolucao, records, comparativo, previsoes, score, heatmap, atleta } = data;

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/perfil')}
                className="text-white hover:bg-white/20"
              >
                <ChevronLeft className="w-6 h-6" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Zap className="w-7 h-7" />
                  RAIO-X do Atleta
                </h1>
                <p className="text-white/80">Análise completa de performance - {atleta?.nome}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={exportToPDF} className="border-white/30 text-white hover:bg-white/20">
                <Download className="w-4 h-4 mr-2" />
                PDF
              </Button>
              <Button variant="outline" size="sm" onClick={exportToExcel} className="border-white/30 text-white hover:bg-white/20">
                <Download className="w-4 h-4 mr-2" />
                Excel
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Score de Consistência - Destaque */}
      <div className="container mx-auto px-4 -mt-4">
        <Card className="bg-gradient-to-r from-slate-800 to-slate-700 border-slate-600">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="relative w-32 h-32">
                <ResponsiveContainer>
                  <RadialBarChart
                    innerRadius="70%"
                    outerRadius="100%"
                    data={[{ value: score.score_mes_atual, fill: '#10b981' }]}
                    startAngle={90}
                    endAngle={-270}
                  >
                    <RadialBar dataKey="value" cornerRadius={10} background={{ fill: '#334155' }} />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-white">{score.score_mes_atual}%</span>
                  <span className="text-xs text-slate-400">Consistência</span>
                </div>
              </div>
              <div className="flex-1 text-center md:text-left">
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span className="text-2xl">{score.emoji}</span>
                  <h3 className="text-xl font-bold text-white">{score.classificacao}</h3>
                </div>
                <p className="text-slate-400 mt-1">{score.dica}</p>
                <div className="flex items-center gap-4 mt-3 justify-center md:justify-start">
                  <div className="text-center">
                    <p className="text-lg font-bold text-emerald-400">{score.corridas_mes_atual}</p>
                    <p className="text-xs text-slate-500">Corridas este mês</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-blue-400">{score.media_6_meses}%</p>
                    <p className="text-xs text-slate-500">Média 6 meses</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-orange-400">{evolucao.totais?.total_provas || 0}</p>
                    <p className="text-xs text-slate-500">Total de provas</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Conteúdo Principal */}
      <div id="raio-x-content" className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-slate-800 border-slate-700 mb-6">
            <TabsTrigger value="visao-geral">Visão Geral</TabsTrigger>
            <TabsTrigger value="evolucao">Evolução</TabsTrigger>
            <TabsTrigger value="records">Records (RP)</TabsTrigger>
            <TabsTrigger value="comparativo">Comparativo</TabsTrigger>
            <TabsTrigger value="previsoes">Previsões IA</TabsTrigger>
          </TabsList>

          {/* Aba: Visão Geral */}
          <TabsContent value="visao-geral">
            {/* KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <KPIWidget
                title="Distância Total"
                value={`${evolucao.totais?.distancia_total_km || 0} km`}
                icon={TrendingUp}
                trend={comparativo.variacoes?.distancia}
                color="emerald"
              />
              <KPIWidget
                title="Tempo Total"
                value={`${evolucao.totais?.tempo_total_horas || 0}h`}
                icon={Clock}
                color="blue"
              />
              <KPIWidget
                title="Total de Provas"
                value={evolucao.totais?.total_provas || 0}
                icon={Trophy}
                trend={comparativo.variacoes?.provas}
                color="orange"
              />
              <KPIWidget
                title="Melhor Pace"
                value={records.records?.melhor_pace?.valor_formatado || '-'}
                subtitle="/km"
                icon={Zap}
                color="purple"
              />
            </div>

            {/* Gráfico de Evolução + Heatmap */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              {/* Gráfico de Área - Evolução de Distância */}
              <Card className="bg-slate-800 border-slate-700 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-emerald-400" />
                    Evolução de Distância
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={evolucao.evolucao_mensal}>
                      <defs>
                        <linearGradient id="colorDist" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                        labelStyle={{ color: '#fff' }}
                      />
                      <Area
                        type="monotone"
                        dataKey="distancia_total_km"
                        stroke="#10b981"
                        fillOpacity={1}
                        fill="url(#colorDist)"
                        name="Distância (km)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Heatmap - Dias da Semana */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-blue-400" />
                    Dias Favoritos
                  </CardTitle>
                  <CardDescription className="text-slate-400">
                    Dia favorito: <span className="text-blue-400 font-medium">{heatmap.dia_favorito}</span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(heatmap.dias_semana).map(([dia, count]) => {
                      const max = Math.max(...Object.values(heatmap.dias_semana));
                      const percent = max > 0 ? (count / max) * 100 : 0;
                      return (
                        <div key={dia} className="flex items-center gap-2">
                          <span className="text-sm text-slate-400 w-8">{dia}</span>
                          <div className="flex-1 bg-slate-700 rounded-full h-4 overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all"
                              style={{ width: `${percent}%` }}
                            />
                          </div>
                          <span className="text-sm text-white w-6 text-right">{count}</span>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Records por Categoria + Radar */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Records por Categoria */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-yellow-400" />
                    Records Pessoais (RP)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {['5km', '10km', '21km', '42km'].map((cat) => {
                      const rp = records.records?.por_categoria?.[cat];
                      return (
                        <RecordCard
                          key={cat}
                          title={cat}
                          value={rp?.tempo || '-'}
                          subtitle={rp ? `Pace: ${rp.pace}` : 'Sem registro'}
                          date={rp?.data ? new Date(rp.data).toLocaleDateString('pt-BR') : null}
                          icon={Trophy}
                          highlight={!!rp}
                        />
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Gráfico Radar - Performance */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <PieIcon className="w-5 h-5 text-purple-400" />
                    Perfil de Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <RadarChart
                      data={[
                        { subject: 'Consistência', value: score.score_mes_atual, fullMark: 100 },
                        { subject: 'Volume', value: Math.min((evolucao.totais?.total_provas || 0) * 10, 100), fullMark: 100 },
                        { subject: 'Velocidade', value: records.records?.melhor_pace ? Math.max(100 - (records.records.melhor_pace.valor * 10), 20) : 30, fullMark: 100 },
                        { subject: 'Distância', value: Math.min((evolucao.totais?.distancia_total_km || 0) / 5, 100), fullMark: 100 },
                        { subject: 'Regularidade', value: score.media_6_meses, fullMark: 100 }
                      ]}
                    >
                      <PolarGrid stroke="#334155" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar
                        name="Performance"
                        dataKey="value"
                        stroke="#8b5cf6"
                        fill="#8b5cf6"
                        fillOpacity={0.3}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Aba: Evolução */}
          <TabsContent value="evolucao">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Gráfico de Linha - Evolução do Pace */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Evolução do Pace Médio</CardTitle>
                  <CardDescription className="text-slate-400">Menor pace = melhor performance</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={evolucao.evolucao_mensal.filter(e => e.pace_medio_valor)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} domain={['auto', 'auto']} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                        formatter={(value) => [`${value.toFixed(2)} min/km`, 'Pace']}
                      />
                      <Line
                        type="monotone"
                        dataKey="pace_medio_valor"
                        stroke="#f59e0b"
                        strokeWidth={3}
                        dot={{ fill: '#f59e0b', strokeWidth: 2 }}
                        name="Pace médio"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Gráfico de Barras - Número de Provas */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Provas por Mês</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={evolucao.evolucao_mensal}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                      <Bar dataKey="num_provas" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Provas" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Gráfico Composto - Distância x Tempo */}
              <Card className="bg-slate-800 border-slate-700 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white">Distância vs Tempo Total</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <ComposedChart data={evolucao.evolucao_mensal}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis yAxisId="left" stroke="#10b981" fontSize={12} />
                      <YAxis yAxisId="right" orientation="right" stroke="#8b5cf6" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                      <Legend />
                      <Bar yAxisId="left" dataKey="distancia_total_km" fill="#10b981" name="Distância (km)" radius={[4, 4, 0, 0]} />
                      <Line yAxisId="right" type="monotone" dataKey="tempo_total_horas" stroke="#8b5cf6" strokeWidth={2} name="Tempo (h)" />
                    </ComposedChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Aba: Records */}
          <TabsContent value="records">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Melhor Pace */}
              <Card className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border-yellow-500/30">
                <CardContent className="p-6 text-center">
                  <Trophy className="w-12 h-12 text-yellow-400 mx-auto mb-3" />
                  <h3 className="text-lg text-slate-300">Melhor Pace</h3>
                  <p className="text-4xl font-bold text-yellow-400 my-2">
                    {records.records?.melhor_pace?.valor_formatado || '-'}
                  </p>
                  <p className="text-slate-400">/km</p>
                  {records.records?.melhor_pace && (
                    <>
                      <p className="text-sm text-slate-400 mt-2">{records.records.melhor_pace.corrida}</p>
                      <p className="text-xs text-slate-500">{records.records.melhor_pace.distancia} km</p>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Maior Distância */}
              <Card className="bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border-emerald-500/30">
                <CardContent className="p-6 text-center">
                  <TrendingUp className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                  <h3 className="text-lg text-slate-300">Maior Distância</h3>
                  <p className="text-4xl font-bold text-emerald-400 my-2">
                    {records.records?.maior_distancia?.valor || '-'}
                  </p>
                  <p className="text-slate-400">km</p>
                  {records.records?.maior_distancia && (
                    <p className="text-sm text-slate-400 mt-2">{records.records.maior_distancia.corrida}</p>
                  )}
                </CardContent>
              </Card>

              {/* Score de Consistência */}
              <Card className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-purple-500/30">
                <CardContent className="p-6 text-center">
                  <Flame className="w-12 h-12 text-purple-400 mx-auto mb-3" />
                  <h3 className="text-lg text-slate-300">Consistência</h3>
                  <p className="text-4xl font-bold text-purple-400 my-2">{score.media_6_meses}%</p>
                  <p className="text-slate-400">Média 6 meses</p>
                  <Badge className="mt-2 bg-purple-500/30 text-purple-300">{score.classificacao}</Badge>
                </CardContent>
              </Card>
            </div>

            {/* Tabela de Records por Categoria */}
            <Card className="bg-slate-800 border-slate-700 mt-6">
              <CardHeader>
                <CardTitle className="text-white">Records por Distância</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="py-3 px-4 text-left text-slate-400">Distância</th>
                        <th className="py-3 px-4 text-center text-slate-400">Melhor Tempo</th>
                        <th className="py-3 px-4 text-center text-slate-400">Pace</th>
                        <th className="py-3 px-4 text-left text-slate-400">Corrida</th>
                        <th className="py-3 px-4 text-center text-slate-400">Data</th>
                      </tr>
                    </thead>
                    <tbody>
                      {['5km', '10km', '21km', '42km'].map((cat) => {
                        const rp = records.records?.por_categoria?.[cat];
                        return (
                          <tr key={cat} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                            <td className="py-3 px-4">
                              <span className="font-medium text-white">{cat}</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              {rp ? (
                                <span className="text-emerald-400 font-bold">{rp.tempo}</span>
                              ) : (
                                <span className="text-slate-500">-</span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-center text-slate-300">{rp?.pace || '-'}</td>
                            <td className="py-3 px-4 text-slate-300">{rp?.corrida || '-'}</td>
                            <td className="py-3 px-4 text-center text-slate-400">
                              {rp?.data ? new Date(rp.data).toLocaleDateString('pt-BR') : '-'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Aba: Comparativo */}
          <TabsContent value="comparativo">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Comparativo Este Mês vs Mês Anterior */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Este Mês vs Mês Anterior</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Distância */}
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-slate-400">Distância Total</span>
                        <div className="flex items-center gap-2">
                          {comparativo.variacoes?.distancia > 0 ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                          ) : comparativo.variacoes?.distancia < 0 ? (
                            <ArrowDownRight className="w-4 h-4 text-red-400" />
                          ) : null}
                          <span className={comparativo.variacoes?.distancia > 0 ? 'text-emerald-400' : comparativo.variacoes?.distancia < 0 ? 'text-red-400' : 'text-slate-400'}>
                            {comparativo.variacoes?.distancia > 0 ? '+' : ''}{comparativo.variacoes?.distancia || 0}%
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-white">{comparativo.mes_atual?.metricas?.distancia_total_km || 0}</p>
                          <p className="text-xs text-slate-400">km este mês</p>
                        </div>
                        <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-slate-400">{comparativo.mes_anterior?.metricas?.distancia_total_km || 0}</p>
                          <p className="text-xs text-slate-500">km mês passado</p>
                        </div>
                      </div>
                    </div>

                    {/* Provas */}
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-slate-400">Número de Provas</span>
                        <div className="flex items-center gap-2">
                          {comparativo.variacoes?.provas > 0 ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                          ) : comparativo.variacoes?.provas < 0 ? (
                            <ArrowDownRight className="w-4 h-4 text-red-400" />
                          ) : null}
                          <span className={comparativo.variacoes?.provas > 0 ? 'text-emerald-400' : comparativo.variacoes?.provas < 0 ? 'text-red-400' : 'text-slate-400'}>
                            {comparativo.variacoes?.provas > 0 ? '+' : ''}{comparativo.variacoes?.provas || 0}%
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-white">{comparativo.mes_atual?.metricas?.num_provas || 0}</p>
                          <p className="text-xs text-slate-400">este mês</p>
                        </div>
                        <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-slate-400">{comparativo.mes_anterior?.metricas?.num_provas || 0}</p>
                          <p className="text-xs text-slate-500">mês passado</p>
                        </div>
                      </div>
                    </div>

                    {/* Pace */}
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-slate-400">Pace Médio</span>
                        <div className="flex items-center gap-2">
                          {comparativo.variacoes?.pace > 0 ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                          ) : comparativo.variacoes?.pace < 0 ? (
                            <ArrowDownRight className="w-4 h-4 text-red-400" />
                          ) : null}
                          <span className={comparativo.variacoes?.pace > 0 ? 'text-emerald-400' : comparativo.variacoes?.pace < 0 ? 'text-red-400' : 'text-slate-400'}>
                            {comparativo.variacoes?.pace > 0 ? '+' : ''}{comparativo.variacoes?.pace || 0}%
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-white">{comparativo.mes_atual?.metricas?.pace_medio || '-'}</p>
                          <p className="text-xs text-slate-400">/km este mês</p>
                        </div>
                        <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                          <p className="text-2xl font-bold text-slate-400">{comparativo.mes_anterior?.metricas?.pace_medio || '-'}</p>
                          <p className="text-xs text-slate-500">/km mês passado</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Melhor Performance do Mês */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Star className="w-5 h-5 text-yellow-400" />
                    Melhor Performance do Mês
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {comparativo.melhor_performance_mes ? (
                    <div className="text-center py-4">
                      <Award className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
                      <h3 className="text-xl font-bold text-white">{comparativo.melhor_performance_mes.corrida}</h3>
                      <p className="text-slate-400 mt-2">{new Date(comparativo.melhor_performance_mes.data).toLocaleDateString('pt-BR')}</p>
                      <div className="flex justify-center gap-6 mt-4">
                        <div>
                          <p className="text-2xl font-bold text-emerald-400">{comparativo.melhor_performance_mes.distancia} km</p>
                          <p className="text-xs text-slate-500">Distância</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-blue-400">{comparativo.melhor_performance_mes.tempo}</p>
                          <p className="text-xs text-slate-500">Tempo</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-orange-400">{comparativo.melhor_performance_mes.pace}</p>
                          <p className="text-xs text-slate-500">Pace</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Activity className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                      <p className="text-slate-400">Nenhuma corrida registrada este mês</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Gráfico de Comparação Histórica */}
              <Card className="bg-slate-800 border-slate-700 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white">Histórico de Consistência</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={score.historico}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="mes_formatado" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                      <Bar dataKey="score" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Score (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Aba: Previsões IA */}
          <TabsContent value="previsoes">
            <Card className="bg-slate-800 border-slate-700 mb-6">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  Previsões Inteligentes
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Baseado nas suas últimas {previsoes.corridas_analisadas || 0} corridas
                </CardDescription>
              </CardHeader>
              <CardContent>
                {previsoes.tem_dados ? (
                  <>
                    <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
                      <p className="text-slate-400">Seu pace base atual:</p>
                      <p className="text-3xl font-bold text-emerald-400">{previsoes.pace_base} /km</p>
                      <p className="text-sm text-slate-500 mt-1">{previsoes.dica}</p>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(previsoes.previsoes || {}).map(([dist, prev]) => (
                        <Card key={dist} className="bg-slate-700 border-slate-600">
                          <CardContent className="p-4 text-center">
                            <p className="text-lg font-bold text-white">{prev.distancia}</p>
                            <p className="text-2xl font-bold text-blue-400 my-2">{prev.tempo_previsto}</p>
                            <p className="text-sm text-slate-400">Pace: {prev.pace_previsto}</p>
                            <Badge className="mt-2" variant={prev.confianca === 'Alta' ? 'default' : 'secondary'}>
                              {prev.confianca}
                            </Badge>
                          </CardContent>
                        </Card>
                      ))}
                    </div>

                    <div className="mt-6 p-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg border border-purple-500/30">
                      <div className="flex items-center gap-3">
                        <Target className="w-8 h-8 text-purple-400" />
                        <div>
                          <p className="text-white font-medium">Probabilidade de bater RP na próxima corrida</p>
                          <p className="text-2xl font-bold text-purple-400">{previsoes.probabilidade_rp_proxima}</p>
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <Activity className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400">{previsoes.mensagem}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default RaioXPage;
