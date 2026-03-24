// /app/frontend/src/pages/RaioXPage.jsx
// Página RAIO-X do Atleta - Análise completa de performance

import { useState, useEffect } from 'react';
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
  Loader2, ChevronLeft, ChevronRight, Download, TrendingUp, TrendingDown, Trophy,
  Target, Zap, Calendar, Clock, Activity, Award, Flame, Star,
  ArrowUpRight, ArrowDownRight, Minus, BarChart3, PieChart as PieIcon, FileText, FileSpreadsheet,
  Share2, Copy, Check, X, Lock, Sparkles, Medal, Shield, Play, Crown, Users, Eye, HelpCircle, ArrowLeftRight
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { Tooltip as TooltipUI, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

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

// Mapeamento de ícones para badges
const ICON_MAP = {
  star: Star,
  medal: Medal,
  trophy: Trophy,
  award: Award,
  zap: Zap,
  play: Play,
  shield: Shield,
  target: Target,
  crown: Crown,
  calendar: Calendar,
  users: Users,
  eye: Eye,
  sparkles: Sparkles,
  flame: Flame
};

// Definição das insígnias para o guia de ajuda
const TODAS_INSIGNIAS = [
  { id: 'primeiro_lugar', nome: 'Campeão', emoji: '🥇', cor: '#FFD700', descricao: 'Conquistou o 1º lugar em uma corrida oficial', como_conquistar: 'Fique em 1º lugar na sua categoria em qualquer corrida aprovada', pontos_bonus: 5 },
  { id: 'podio', nome: 'Pódio', emoji: '🏆', cor: '#F59E0B', descricao: 'Subiu ao pódio (top 3) em uma corrida', como_conquistar: 'Fique entre os 3 primeiros lugares na sua categoria', pontos_bonus: 2 },
  { id: '10_corridas', nome: 'Veterano', emoji: '🏃', cor: '#10B981', descricao: 'Completou 10 corridas', como_conquistar: 'Participe e complete 10 corridas registradas no ranking', pontos_bonus: 10 },
  { id: '12_resultados', nome: 'Atleta Bronze', emoji: '🥉', cor: '#CD7F32', descricao: 'Lançou 12 resultados no ranking', como_conquistar: 'Registre 12 resultados de corridas aprovados no sistema', pontos_bonus: 12 },
  { id: '20_resultados', nome: 'Atleta Prata', emoji: '🥈', cor: '#C0C0C0', descricao: 'Lançou 20 resultados no ranking', como_conquistar: 'Registre 20 resultados de corridas aprovados no sistema', pontos_bonus: 20 },
  { id: '30_resultados', nome: 'Atleta Ouro', emoji: '🥇', cor: '#FFD700', descricao: 'Lançou 30 resultados no ranking', como_conquistar: 'Registre 30 resultados de corridas aprovados no sistema', pontos_bonus: 30 },
  { id: 'elite', nome: 'Atleta Elite', emoji: '⭐', cor: '#FFD700', descricao: 'Alcançou 100 pontos no ranking', como_conquistar: 'Acumule 100 pontos ou mais no ranking geral', pontos_bonus: 20 },
  { id: 'maratonista', nome: 'Maratonista', emoji: '🎯', cor: '#8B5CF6', descricao: 'Completou uma maratona (42KM)', como_conquistar: 'Complete uma corrida de 42KM ou mais', pontos_bonus: 15 },
  { id: 'consistente', nome: 'Consistente', emoji: '📅', cor: '#3B82F6', descricao: 'Completou corridas em 6 meses diferentes', como_conquistar: 'Participe de pelo menos uma corrida em 6 meses distintos', pontos_bonus: 10 },
  { id: 'embaixador', nome: 'Embaixador Run', emoji: '🎖️', cor: '#EC4899', descricao: 'Embaixador oficial do Ranking Run', como_conquistar: 'Seja selecionado como embaixador oficial da plataforma', pontos_bonus: 25 }
];

// Componente de Badge Individual
const BadgeItem = ({ badge, size = 'md' }) => {
  const IconComponent = ICON_MAP[badge.icone] || Star;
  
  const sizeClasses = {
    sm: 'w-12 h-12',
    md: 'w-16 h-16',
    lg: 'w-20 h-20'
  };
  
  const iconSizes = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10'
  };
  
  return (
    <TooltipProvider>
      <TooltipUI>
        <TooltipTrigger asChild>
          <div 
            className={`relative ${sizeClasses[size]} rounded-full flex items-center justify-center transition-all duration-300 ${
              badge.conquistado 
                ? 'cursor-pointer hover:scale-110 shadow-lg hover:shadow-xl' 
                : 'opacity-40 grayscale cursor-not-allowed'
            }`}
            style={{
              background: badge.conquistado 
                ? `linear-gradient(135deg, ${badge.cor_primaria}, ${badge.cor_secundaria})` 
                : '#475569'
            }}
          >
            {/* Anel externo */}
            <div 
              className="absolute inset-0 rounded-full"
              style={{
                border: badge.conquistado ? `3px solid ${badge.cor_primaria}40` : '3px solid #47556940',
                transform: 'scale(1.12)'
              }}
            />
            
            {/* Brilho interno */}
            {badge.conquistado && (
              <div 
                className="absolute top-1 left-1/4 w-1/3 h-1/4 rounded-full opacity-40"
                style={{ background: 'linear-gradient(to bottom, white, transparent)' }}
              />
            )}
            
            {/* Ícone */}
            <IconComponent 
              className={`${iconSizes[size]} ${badge.conquistado ? 'text-white' : 'text-slate-400'}`}
              strokeWidth={2}
            />
            
            {/* Indicador */}
            {badge.conquistado ? (
              <div 
                className="absolute -bottom-1 -right-1 rounded-full p-1"
                style={{ background: badge.cor_primaria }}
              >
                <Check className="w-3 h-3 text-white" />
              </div>
            ) : (
              <div className="absolute -bottom-1 -right-1 bg-slate-600 rounded-full p-1">
                <Lock className="w-3 h-3 text-white" />
              </div>
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs bg-slate-800 border-slate-700">
          <div className="text-center p-1">
            <p className="font-bold text-white">{badge.nome}</p>
            <p className="text-xs text-slate-400">{badge.descricao}</p>
            {badge.data_conquista && (
              <p className="text-xs text-emerald-400 mt-1">
                Conquistado em {new Date(badge.data_conquista).toLocaleDateString('pt-BR')}
              </p>
            )}
          </div>
        </TooltipContent>
      </TooltipUI>
    </TooltipProvider>
  );
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
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareImageUrl, setShareImageUrl] = useState(null);
  const [generatingShare, setGeneratingShare] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);
  const [badges, setBadges] = useState([]);
  const [badgesLoading, setBadgesLoading] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  
  // Estados para comparativo personalizado
  const anoAtual = new Date().getFullYear();
  const mesAtualNum = new Date().getMonth();
  const [mesSelecionado1, setMesSelecionado1] = useState(mesAtualNum);
  const [mesSelecionado2, setMesSelecionado2] = useState(mesAtualNum > 0 ? mesAtualNum - 1 : 11);
  const [comparativoPersonalizado, setComparativoPersonalizado] = useState(null);
  const [loadingComparativo, setLoadingComparativo] = useState(false);
  
  const mesesDoAno = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ];

  useEffect(() => {
    if (token) {
      fetchRaioX();
    }
  }, [token]);

  useEffect(() => {
    if (user?.id) {
      fetchBadges();
    }
  }, [user?.id]);

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

  const fetchBadges = async () => {
    setBadgesLoading(true);
    try {
      const response = await axios.get(`${API}/badges/atleta/${user.id}`);
      setBadges(response.data.badges || []);
    } catch (error) {
      console.error('Erro ao carregar badges:', error);
    } finally {
      setBadgesLoading(false);
    }
  };

  // Busca comparativo personalizado
  const fetchComparativoPersonalizado = async () => {
    setLoadingComparativo(true);
    try {
      const mes1 = `${anoAtual}-${String(mesSelecionado1 + 1).padStart(2, '0')}`;
      const mes2 = `${anoAtual}-${String(mesSelecionado2 + 1).padStart(2, '0')}`;
      
      const response = await axios.get(`${API}/raio-x/comparativo-meses`, {
        params: { mes1, mes2 },
        headers: { Authorization: `Bearer ${token}` }
      });
      setComparativoPersonalizado(response.data);
    } catch (error) {
      console.error('Erro ao carregar comparativo:', error);
      toast.error('Erro ao carregar comparativo');
    } finally {
      setLoadingComparativo(false);
    }
  };

  // Buscar comparativo quando meses mudam
  useEffect(() => {
    if (token && activeTab === 'comparativo') {
      fetchComparativoPersonalizado();
    }
  }, [mesSelecionado1, mesSelecionado2, activeTab, token]);

  const exportToPDF = async () => {
    const loadingToast = toast.loading('Gerando PDF completo...');
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      
      // ========== PÁGINA 1: VISÃO GERAL ==========
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
      let yPos = 35;
      
      pdf.setFontSize(14);
      pdf.setFont(undefined, 'bold');
      pdf.text('1. Resumo de Performance', 15, yPos);
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
        ['Corridas Este Mês:', `${score.corridas_mes_atual || 0}`],
      ];
      
      metricas.forEach(([label, value]) => {
        pdf.text(label, 15, yPos);
        pdf.text(String(value), 70, yPos);
        yPos += 6;
      });

      // Records por categoria
      yPos += 10;
      pdf.setFontSize(14);
      pdf.setFont(undefined, 'bold');
      pdf.text('2. Records Pessoais (RP)', 15, yPos);
      yPos += 8;
      
      pdf.setFontSize(10);
      pdf.setFont(undefined, 'normal');
      ['5km', '10km', '21km', '42km'].forEach((cat) => {
        const rp = records.records?.por_categoria?.[cat];
        pdf.text(`${cat}:`, 15, yPos);
        if (rp) {
          pdf.text(`${rp.tempo} (Pace: ${rp.pace})`, 35, yPos);
          pdf.text(String(rp.corrida || ''), 100, yPos);
        } else {
          pdf.text('Sem registro', 35, yPos);
        }
        yPos += 6;
      });

      // Destaques
      yPos += 5;
      pdf.setFillColor(240, 253, 244); // green-50
      pdf.rect(15, yPos - 3, 180, 18, 'F');
      pdf.setTextColor(22, 163, 74); // green-600
      pdf.text('Destaques:', 20, yPos + 2);
      pdf.setTextColor(0, 0, 0);
      pdf.text(`Melhor Pace Geral: ${records.records?.melhor_pace?.valor_formatado || '-'}/km`, 20, yPos + 8);
      pdf.text(`Maior Distância: ${records.records?.maior_distancia?.valor || '-'} km`, 20, yPos + 14);
      yPos += 25;

      // ========== PÁGINA 2: EVOLUÇÃO ==========
      pdf.addPage();
      pdf.setFillColor(59, 130, 246); // blue-500
      pdf.rect(0, 0, pdfWidth, 15, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(14);
      pdf.text('3. Evolução Mensal', 15, 10);
      
      yPos = 25;
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(9);
      
      // Cabeçalho da tabela
      pdf.setFillColor(226, 232, 240);
      pdf.rect(15, yPos - 4, 180, 7, 'F');
      pdf.setFont(undefined, 'bold');
      pdf.text('Mês', 17, yPos);
      pdf.text('Provas', 55, yPos);
      pdf.text('Distância (km)', 80, yPos);
      pdf.text('Tempo (h)', 115, yPos);
      pdf.text('Pace Médio', 145, yPos);
      yPos += 8;
      
      pdf.setFont(undefined, 'normal');
      const todosMeses = evolucao.evolucao_mensal || [];
      todosMeses.forEach((mes) => {
        if (yPos > pdfHeight - 20) {
          pdf.addPage();
          yPos = 20;
        }
        pdf.text(mes.mes_formatado || '', 17, yPos);
        pdf.text(String(mes.num_provas || 0), 55, yPos);
        pdf.text(String(mes.distancia_total_km || 0), 80, yPos);
        pdf.text(String(mes.tempo_total_horas || 0), 115, yPos);
        pdf.text(mes.pace_medio || '-', 145, yPos);
        yPos += 6;
      });

      // Totais
      yPos += 5;
      pdf.setFillColor(226, 232, 240);
      pdf.rect(15, yPos - 4, 180, 7, 'F');
      pdf.setFont(undefined, 'bold');
      pdf.text('TOTAL:', 17, yPos);
      pdf.text(String(evolucao.totais?.total_provas || 0), 55, yPos);
      pdf.text(String(evolucao.totais?.distancia_total_km || 0), 80, yPos);
      pdf.text(String(evolucao.totais?.tempo_total_horas || 0), 115, yPos);

      // ========== PÁGINA 3: COMPARATIVO ==========
      pdf.addPage();
      pdf.setFillColor(249, 115, 22); // orange-500
      pdf.rect(0, 0, pdfWidth, 15, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(14);
      pdf.text('4. Comparativo Mensal', 15, 10);
      
      yPos = 25;
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'bold');
      pdf.text('Este Mês vs Mês Anterior', 15, yPos);
      yPos += 10;
      
      pdf.setFontSize(10);
      pdf.setFont(undefined, 'normal');
      
      const compData = [
        ['Distância (km):', comparativo.mes_atual?.metricas?.distancia_total_km || 0, comparativo.mes_anterior?.metricas?.distancia_total_km || 0, comparativo.variacoes?.distancia || 0],
        ['Nº de Provas:', comparativo.mes_atual?.metricas?.num_provas || 0, comparativo.mes_anterior?.metricas?.num_provas || 0, comparativo.variacoes?.provas || 0],
        ['Pace Médio:', comparativo.mes_atual?.metricas?.pace_medio || '-', comparativo.mes_anterior?.metricas?.pace_medio || '-', comparativo.variacoes?.pace || 0],
        ['Tempo Total:', comparativo.mes_atual?.metricas?.tempo_total_horas || 0, comparativo.mes_anterior?.metricas?.tempo_total_horas || 0, ''],
      ];
      
      // Cabeçalho
      pdf.setFillColor(226, 232, 240);
      pdf.rect(15, yPos - 4, 180, 7, 'F');
      pdf.setFont(undefined, 'bold');
      pdf.text('Métrica', 17, yPos);
      pdf.text('Este Mês', 70, yPos);
      pdf.text('Mês Anterior', 105, yPos);
      pdf.text('Variação (%)', 150, yPos);
      yPos += 8;
      
      pdf.setFont(undefined, 'normal');
      compData.forEach(([metrica, atual, anterior, variacao]) => {
        pdf.text(String(metrica), 17, yPos);
        pdf.text(String(atual), 70, yPos);
        pdf.text(String(anterior), 105, yPos);
        if (variacao !== '') {
          const varStr = `${variacao > 0 ? '+' : ''}${variacao}%`;
          pdf.setTextColor(variacao > 0 ? 22 : variacao < 0 ? 220 : 100, variacao > 0 ? 163 : variacao < 0 ? 38 : 100, variacao > 0 ? 74 : variacao < 0 ? 38 : 100);
          pdf.text(varStr, 150, yPos);
          pdf.setTextColor(0, 0, 0);
        }
        yPos += 6;
      });

      // Melhor performance do mês
      if (comparativo.melhor_performance_mes) {
        yPos += 10;
        pdf.setFillColor(240, 253, 244);
        pdf.rect(15, yPos - 4, 180, 25, 'F');
        pdf.setTextColor(22, 163, 74);
        pdf.setFont(undefined, 'bold');
        pdf.text('Melhor Performance do Mês', 20, yPos + 2);
        pdf.setTextColor(0, 0, 0);
        pdf.setFont(undefined, 'normal');
        pdf.text(`Corrida: ${comparativo.melhor_performance_mes.corrida}`, 20, yPos + 9);
        pdf.text(`Distância: ${comparativo.melhor_performance_mes.distancia} km | Tempo: ${comparativo.melhor_performance_mes.tempo} | Pace: ${comparativo.melhor_performance_mes.pace}`, 20, yPos + 16);
      }

      // ========== PÁGINA 4: PREVISÕES IA ==========
      if (previsoes.tem_dados) {
        pdf.addPage();
        pdf.setFillColor(139, 92, 246); // purple-500
        pdf.rect(0, 0, pdfWidth, 15, 'F');
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(14);
        pdf.text('5. Previsões Inteligentes (IA)', 15, 10);
        
        yPos = 25;
        pdf.setTextColor(0, 0, 0);
        pdf.setFontSize(10);
        
        pdf.text(`Pace Base Atual: ${previsoes.pace_base}`, 15, yPos);
        pdf.text(`Corridas Analisadas: ${previsoes.corridas_analisadas}`, 100, yPos);
        yPos += 10;
        
        pdf.setFont(undefined, 'bold');
        pdf.text('Previsões por Distância:', 15, yPos);
        yPos += 8;
        
        // Cabeçalho
        pdf.setFillColor(226, 232, 240);
        pdf.rect(15, yPos - 4, 180, 7, 'F');
        pdf.text('Distância', 17, yPos);
        pdf.text('Tempo Previsto', 55, yPos);
        pdf.text('Pace Previsto', 100, yPos);
        pdf.text('Confiança', 145, yPos);
        yPos += 8;
        
        pdf.setFont(undefined, 'normal');
        Object.values(previsoes.previsoes || {}).forEach((prev) => {
          pdf.text(String(prev.distancia), 17, yPos);
          pdf.text(String(prev.tempo_previsto), 55, yPos);
          pdf.text(String(prev.pace_previsto), 100, yPos);
          pdf.text(String(prev.confianca), 145, yPos);
          yPos += 6;
        });

        yPos += 10;
        pdf.setFillColor(243, 232, 255); // purple-100
        pdf.rect(15, yPos - 4, 180, 20, 'F');
        pdf.setTextColor(107, 33, 168); // purple-800
        pdf.setFont(undefined, 'bold');
        pdf.text(`Probabilidade de RP na próxima corrida: ${previsoes.probabilidade_rp_proxima}`, 20, yPos + 3);
        pdf.setFont(undefined, 'normal');
        pdf.setFontSize(9);
        const dica = previsoes.dica || '';
        const dicaLines = pdf.splitTextToSize(dica, 170);
        pdf.text(dicaLines, 20, yPos + 10);
      }

      // ========== PÁGINA 5: CONQUISTAS ==========
      const badgesConquistados = badges.filter(b => b.conquistado);
      if (badgesConquistados.length > 0) {
        pdf.addPage();
        pdf.setFillColor(234, 179, 8); // yellow-500
        pdf.rect(0, 0, pdfWidth, 15, 'F');
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(14);
        pdf.text('6. Conquistas & Insígnias', 15, 10);
        
        yPos = 25;
        pdf.setTextColor(0, 0, 0);
        pdf.setFontSize(10);
        pdf.text(`Total de insígnias conquistadas: ${badgesConquistados.length}/${badges.length}`, 15, yPos);
        yPos += 10;
        
        badgesConquistados.forEach((badge) => {
          if (yPos > pdfHeight - 20) {
            pdf.addPage();
            yPos = 20;
          }
          pdf.setFont(undefined, 'bold');
          pdf.text(`• ${badge.nome}`, 15, yPos);
          pdf.setFont(undefined, 'normal');
          pdf.text(badge.descricao || '', 50, yPos);
          if (badge.data_conquista) {
            pdf.text(`(${new Date(badge.data_conquista).toLocaleDateString('pt-BR')})`, 160, yPos);
          }
          yPos += 6;
        });
      }

      pdf.save(`RAIO-X_${atleta?.nome?.replace(/\s+/g, '_') || 'Atleta'}_${new Date().toISOString().split('T')[0]}.pdf`);
      
      toast.dismiss(loadingToast);
      toast.success('PDF completo gerado com sucesso!');
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

      // Aba 5: Histórico de Consistência
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

  // Gera imagem para compartilhamento usando Canvas API diretamente
  // Formato 9:16 (ideal para Stories do Instagram)
  const generateShareCard = async () => {
    setGeneratingShare(true);
    try {
      // Formato 9:16 para Stories (540x960)
      const width = 540;
      const height = 960;
      
      const canvas = document.createElement('canvas');
      canvas.width = width * 2; // Scale 2x para qualidade
      canvas.height = height * 2;
      const ctx = canvas.getContext('2d');
      
      // Scale para 2x
      ctx.scale(2, 2);
      
      // Background gradient
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, '#0f172a');
      gradient.addColorStop(0.3, '#1e293b');
      gradient.addColorStop(0.7, '#1e293b');
      gradient.addColorStop(1, '#0f172a');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);
      
      // Decorative elements
      ctx.fillStyle = 'rgba(16, 185, 129, 0.1)';
      ctx.beginPath();
      ctx.arc(-50, 100, 200, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(width + 50, height - 100, 200, 0, Math.PI * 2);
      ctx.fill();
      
      let yPos = 30;
      
      // Header - Logo area
      const logoGradient = ctx.createLinearGradient(20, yPos, 68, yPos + 48);
      logoGradient.addColorStop(0, '#10b981');
      logoGradient.addColorStop(1, '#14b8a6');
      ctx.fillStyle = logoGradient;
      ctx.beginPath();
      ctx.roundRect(20, yPos, 48, 48, 12);
      ctx.fill();
      
      // Logo icon
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 26px Arial';
      ctx.fillText('⚡', 30, yPos + 35);
      
      // Title
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 18px Arial';
      ctx.fillText('RAIO-X do Atleta', 78, yPos + 25);
      ctx.fillStyle = '#10b981';
      ctx.font = '12px Arial';
      ctx.fillText('Ranking Run', 78, yPos + 42);
      
      // Website
      ctx.fillStyle = '#64748b';
      ctx.font = '10px Arial';
      ctx.textAlign = 'right';
      ctx.fillText('rankingrun.com.br', width - 20, yPos + 35);
      ctx.textAlign = 'left';
      
      yPos += 80;
      
      // Nome do atleta
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 26px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(atleta?.nome || 'Atleta', width / 2, yPos);
      if (atleta?.assessoria) {
        ctx.fillStyle = '#94a3b8';
        ctx.font = '13px Arial';
        ctx.fillText(atleta.assessoria, width / 2, yPos + 22);
        yPos += 30;
      }
      ctx.textAlign = 'left';
      
      yPos += 30;
      
      // Score circle (maior)
      const scoreValue = score.score_mes_atual || 0;
      const scoreX = width / 2;
      const scoreRadius = 60;
      
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 14;
      ctx.beginPath();
      ctx.arc(scoreX, yPos + scoreRadius, scoreRadius, 0, Math.PI * 2);
      ctx.stroke();
      
      // Score progress
      const scoreGradient = ctx.createLinearGradient(scoreX - scoreRadius, yPos, scoreX + scoreRadius, yPos + scoreRadius * 2);
      scoreGradient.addColorStop(0, '#10b981');
      scoreGradient.addColorStop(1, '#06b6d4');
      ctx.strokeStyle = scoreGradient;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(scoreX, yPos + scoreRadius, scoreRadius, -Math.PI / 2, -Math.PI / 2 + (scoreValue / 100) * Math.PI * 2);
      ctx.stroke();
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 36px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(`${scoreValue}%`, scoreX, yPos + scoreRadius + 12);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px Arial';
      ctx.fillText('Consistência', scoreX, yPos + scoreRadius + 32);
      ctx.textAlign = 'left';
      
      yPos += scoreRadius * 2 + 50;
      
      // Métricas em 2x2 grid
      const cardWidth = 240;
      const cardHeight = 75;
      const cardGap = 15;
      const gridStartX = (width - cardWidth * 2 - cardGap) / 2;
      
      const metrics = [
        { icon: '🏆', value: evolucao.totais?.total_provas || 0, label: 'Provas' },
        { icon: '📏', value: `${evolucao.totais?.distancia_total_km || 0} km`, label: 'Distância' },
        { icon: '⏱️', value: `${evolucao.totais?.tempo_total_horas || 0}h`, label: 'Tempo Total' },
        { icon: '⚡', value: records.records?.melhor_pace?.valor_formatado || '-', label: 'Melhor Pace' }
      ];
      
      metrics.forEach((metric, i) => {
        const col = i % 2;
        const row = Math.floor(i / 2);
        const x = gridStartX + col * (cardWidth + cardGap);
        const y = yPos + row * (cardHeight + 10);
        
        // Card background
        ctx.fillStyle = 'rgba(71, 85, 105, 0.4)';
        ctx.beginPath();
        ctx.roundRect(x, y, cardWidth, cardHeight, 10);
        ctx.fill();
        
        // Icon
        ctx.font = '22px Arial';
        ctx.fillText(metric.icon, x + 15, y + 35);
        
        // Value
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 22px Arial';
        ctx.fillText(String(metric.value), x + 50, y + 35);
        
        // Label
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px Arial';
        ctx.fillText(metric.label, x + 50, y + 55);
      });
      
      yPos += cardHeight * 2 + 40;
      
      // Records section
      ctx.fillStyle = 'rgba(71, 85, 105, 0.3)';
      ctx.beginPath();
      ctx.roundRect(20, yPos, width - 40, 90, 10);
      ctx.fill();
      
      ctx.fillStyle = '#facc15';
      ctx.font = 'bold 14px Arial';
      ctx.fillText('🏅 Records Pessoais', 35, yPos + 25);
      
      const categories = ['5km', '10km', '21km', '42km'];
      const rpStartX = 35;
      const rpWidth = (width - 70) / 4;
      
      ctx.font = '11px Arial';
      categories.forEach((cat, i) => {
        const x = rpStartX + i * rpWidth;
        const rp = records.records?.por_categoria?.[cat];
        
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(cat, x, yPos + 50);
        
        ctx.fillStyle = rp ? '#10b981' : '#64748b';
        ctx.font = 'bold 14px Arial';
        ctx.fillText(rp?.tempo || '-', x, yPos + 70);
        ctx.font = '11px Arial';
      });
      
      yPos += 110;
      
      // ========== INSÍGNIAS CONQUISTADAS ==========
      const badgesConquistados = badges.filter(b => b.conquistado);
      
      // Função para desenhar ícone do badge no Canvas (simplificada)
      const drawBadgeIcon = (ctx, icon, cx, cy, size) => {
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        const s = size * 0.35;
        
        switch(icon) {
          case 'star':
            // Estrela de 5 pontas
            ctx.beginPath();
            for (let i = 0; i < 10; i++) {
              const angle = (i * Math.PI / 5) - Math.PI / 2;
              const r = i % 2 === 0 ? s : s * 0.5;
              const px = cx + r * Math.cos(angle);
              const py = cy + r * Math.sin(angle);
              if (i === 0) ctx.moveTo(px, py);
              else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'medal':
            // Medalha - círculo com fita
            ctx.beginPath();
            ctx.arc(cx, cy + s * 0.15, s * 0.65, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.35, cy - s * 0.5);
            ctx.lineTo(cx, cy - s * 0.1);
            ctx.lineTo(cx + s * 0.35, cy - s * 0.5);
            ctx.stroke();
            break;
            
          case 'trophy':
            // Troféu simplificado
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.4, cy - s * 0.4);
            ctx.lineTo(cx - s * 0.25, cy + s * 0.15);
            ctx.lineTo(cx + s * 0.25, cy + s * 0.15);
            ctx.lineTo(cx + s * 0.4, cy - s * 0.4);
            ctx.closePath();
            ctx.fill();
            ctx.fillRect(cx - s * 0.15, cy + s * 0.15, s * 0.3, s * 0.25);
            ctx.fillRect(cx - s * 0.3, cy + s * 0.4, s * 0.6, s * 0.12);
            break;
            
          case 'award':
            // Prêmio/Roseta
            ctx.beginPath();
            ctx.arc(cx, cy - s * 0.1, s * 0.45, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.25, cy + s * 0.25);
            ctx.lineTo(cx - s * 0.4, cy + s * 0.65);
            ctx.lineTo(cx, cy + s * 0.35);
            ctx.lineTo(cx + s * 0.4, cy + s * 0.65);
            ctx.lineTo(cx + s * 0.25, cy + s * 0.25);
            ctx.fill();
            break;
            
          case 'zap':
            // Raio
            ctx.beginPath();
            ctx.moveTo(cx + s * 0.1, cy - s * 0.55);
            ctx.lineTo(cx - s * 0.25, cy + s * 0.05);
            ctx.lineTo(cx + s * 0.05, cy + s * 0.05);
            ctx.lineTo(cx - s * 0.1, cy + s * 0.55);
            ctx.lineTo(cx + s * 0.25, cy - s * 0.05);
            ctx.lineTo(cx - s * 0.05, cy - s * 0.05);
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'play':
            // Triângulo play
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.25, cy - s * 0.4);
            ctx.lineTo(cx + s * 0.4, cy);
            ctx.lineTo(cx - s * 0.25, cy + s * 0.4);
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'shield':
            // Escudo
            ctx.beginPath();
            ctx.moveTo(cx, cy - s * 0.5);
            ctx.lineTo(cx + s * 0.45, cy - s * 0.25);
            ctx.lineTo(cx + s * 0.45, cy + s * 0.1);
            ctx.lineTo(cx, cy + s * 0.55);
            ctx.lineTo(cx - s * 0.45, cy + s * 0.1);
            ctx.lineTo(cx - s * 0.45, cy - s * 0.25);
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'target':
            // Alvo - círculos concêntricos
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(cx, cy, s * 0.5, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(cx, cy, s * 0.3, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(cx, cy, s * 0.12, 0, Math.PI * 2);
            ctx.fill();
            ctx.lineWidth = 2;
            break;
            
          case 'crown':
            // Coroa
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.45, cy + s * 0.25);
            ctx.lineTo(cx - s * 0.45, cy - s * 0.05);
            ctx.lineTo(cx - s * 0.2, cy + s * 0.1);
            ctx.lineTo(cx, cy - s * 0.4);
            ctx.lineTo(cx + s * 0.2, cy + s * 0.1);
            ctx.lineTo(cx + s * 0.45, cy - s * 0.05);
            ctx.lineTo(cx + s * 0.45, cy + s * 0.25);
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'calendar':
            // Calendário
            ctx.fillRect(cx - s * 0.4, cy - s * 0.3, s * 0.8, s * 0.7);
            ctx.fillStyle = '#000000';
            ctx.fillRect(cx - s * 0.3, cy - s * 0.1, s * 0.18, s * 0.18);
            ctx.fillRect(cx - s * 0.05, cy - s * 0.1, s * 0.18, s * 0.18);
            ctx.fillRect(cx + s * 0.12, cy - s * 0.1, s * 0.18, s * 0.18);
            ctx.fillRect(cx - s * 0.3, cy + s * 0.15, s * 0.18, s * 0.18);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(cx - s * 0.25, cy - s * 0.5, s * 0.08, s * 0.2);
            ctx.fillRect(cx + s * 0.17, cy - s * 0.5, s * 0.08, s * 0.2);
            break;
            
          case 'users':
            // Pessoas
            ctx.beginPath();
            ctx.arc(cx - s * 0.18, cy - s * 0.2, s * 0.22, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(cx + s * 0.22, cy - s * 0.15, s * 0.18, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(cx - s * 0.18, cy + s * 0.35, s * 0.3, Math.PI, 0);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(cx + s * 0.22, cy + s * 0.3, s * 0.25, Math.PI, 0);
            ctx.fill();
            break;
            
          case 'flame':
            // Chama
            ctx.beginPath();
            ctx.moveTo(cx, cy - s * 0.5);
            ctx.quadraticCurveTo(cx + s * 0.45, cy - s * 0.15, cx + s * 0.28, cy + s * 0.35);
            ctx.quadraticCurveTo(cx + s * 0.12, cy + s * 0.5, cx, cy + s * 0.42);
            ctx.quadraticCurveTo(cx - s * 0.12, cy + s * 0.5, cx - s * 0.28, cy + s * 0.35);
            ctx.quadraticCurveTo(cx - s * 0.45, cy - s * 0.15, cx, cy - s * 0.5);
            ctx.fill();
            break;
            
          case 'sparkles':
            // Brilhos - estrelas pequenas
            const drawStar = (sx, sy, ss) => {
              ctx.beginPath();
              ctx.moveTo(sx, sy - ss);
              ctx.lineTo(sx + ss * 0.25, sy - ss * 0.25);
              ctx.lineTo(sx + ss, sy);
              ctx.lineTo(sx + ss * 0.25, sy + ss * 0.25);
              ctx.lineTo(sx, sy + ss);
              ctx.lineTo(sx - ss * 0.25, sy + ss * 0.25);
              ctx.lineTo(sx - ss, sy);
              ctx.lineTo(sx - ss * 0.25, sy - ss * 0.25);
              ctx.closePath();
              ctx.fill();
            };
            drawStar(cx - s * 0.2, cy - s * 0.2, s * 0.25);
            drawStar(cx + s * 0.22, cy + s * 0.08, s * 0.22);
            drawStar(cx - s * 0.08, cy + s * 0.32, s * 0.18);
            break;
            
          case 'eye':
            // Olho
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.5, cy);
            ctx.quadraticCurveTo(cx, cy - s * 0.35, cx + s * 0.5, cy);
            ctx.quadraticCurveTo(cx, cy + s * 0.35, cx - s * 0.5, cy);
            ctx.fill();
            ctx.fillStyle = '#000000';
            ctx.beginPath();
            ctx.arc(cx, cy, s * 0.18, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(cx - s * 0.05, cy - s * 0.05, s * 0.07, 0, Math.PI * 2);
            ctx.fill();
            break;
            
          default:
            // Ícone padrão - estrela
            ctx.beginPath();
            for (let i = 0; i < 10; i++) {
              const angle = (i * Math.PI / 5) - Math.PI / 2;
              const r = i % 2 === 0 ? s : s * 0.5;
              const px = cx + r * Math.cos(angle);
              const py = cy + r * Math.sin(angle);
              if (i === 0) ctx.moveTo(px, py);
              else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.fill();
        }
      };
      
      if (badgesConquistados.length > 0) {
        // Calcular altura necessária
        const badgeSize = 52;
        const badgeGap = 10;
        const maxBadgesPerRow = 7;
        const numRows = Math.min(Math.ceil(badgesConquistados.length / maxBadgesPerRow), 2);
        const sectionHeight = 55 + numRows * (badgeSize + 12);
        
        // Fundo da seção
        ctx.fillStyle = 'rgba(234, 179, 8, 0.15)';
        ctx.beginPath();
        ctx.moveTo(30, yPos);
        ctx.lineTo(width - 30, yPos);
        ctx.lineTo(width - 20, yPos + 10);
        ctx.lineTo(width - 20, yPos + sectionHeight - 10);
        ctx.lineTo(width - 30, yPos + sectionHeight);
        ctx.lineTo(30, yPos + sectionHeight);
        ctx.lineTo(20, yPos + sectionHeight - 10);
        ctx.lineTo(20, yPos + 10);
        ctx.closePath();
        ctx.fill();
        
        ctx.fillStyle = '#facc15';
        ctx.font = 'bold 14px Arial';
        ctx.fillText(`🎖️ Insígnias Conquistadas (${badgesConquistados.length})`, 35, yPos + 25);
        
        // Desenhar insígnias
        const badgesToShow = badgesConquistados.slice(0, maxBadgesPerRow * 2);
        const badgesInFirstRow = Math.min(badgesToShow.length, maxBadgesPerRow);
        const totalBadgesWidth = badgesInFirstRow * (badgeSize + badgeGap) - badgeGap;
        const badgeStartX = (width - totalBadgesWidth) / 2;
        
        badgesToShow.forEach((badge, i) => {
          const row = Math.floor(i / maxBadgesPerRow);
          const col = i % maxBadgesPerRow;
          
          const badgesInThisRow = row === 0 ? badgesInFirstRow : Math.min(badgesToShow.length - maxBadgesPerRow, maxBadgesPerRow);
          const rowWidth = badgesInThisRow * (badgeSize + badgeGap) - badgeGap;
          const rowStartX = (width - rowWidth) / 2;
          
          const x = rowStartX + col * (badgeSize + badgeGap);
          const y = yPos + 40 + row * (badgeSize + 14);
          const cx = x + badgeSize / 2;
          const cy = y + badgeSize / 2;
          
          // Sombra
          ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
          ctx.beginPath();
          ctx.arc(cx + 2, cy + 3, badgeSize / 2.3, 0, Math.PI * 2);
          ctx.fill();
          
          // Badge circular com gradiente
          const corPrimaria = badge.cor_primaria || '#10b981';
          const corSecundaria = badge.cor_secundaria || '#059669';
          const badgeGradient = ctx.createRadialGradient(cx - 5, cy - 5, 0, cx, cy, badgeSize / 2);
          badgeGradient.addColorStop(0, corPrimaria);
          badgeGradient.addColorStop(1, corSecundaria);
          ctx.fillStyle = badgeGradient;
          
          ctx.beginPath();
          ctx.arc(cx, cy, badgeSize / 2 - 2, 0, Math.PI * 2);
          ctx.fill();
          
          // Borda brilhante
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
          ctx.lineWidth = 2;
          ctx.stroke();
          
          // Brilho no topo
          ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
          ctx.beginPath();
          ctx.arc(cx - 3, cy - badgeSize / 5, badgeSize / 5, 0, Math.PI * 2);
          ctx.fill();
          
          // Desenhar o ícone
          drawBadgeIcon(ctx, badge.icone, cx, cy, badgeSize);
        });
        
        yPos += sectionHeight + 15;
      }
      
      // Footer (posicionado no final)
      const footerY = Math.max(yPos, height - 50);
      
      // Linha decorativa
      const lineGradient = ctx.createLinearGradient(20, footerY, width - 20, footerY);
      lineGradient.addColorStop(0, '#10b981');
      lineGradient.addColorStop(0.5, '#06b6d4');
      lineGradient.addColorStop(1, '#10b981');
      ctx.strokeStyle = lineGradient;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(20, footerY);
      ctx.lineTo(width - 20, footerY);
      ctx.stroke();
      
      ctx.fillStyle = '#64748b';
      ctx.font = '11px Arial';
      ctx.fillText(`Gerado em ${new Date().toLocaleDateString('pt-BR')}`, 20, footerY + 25);
      ctx.textAlign = 'right';
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 12px Arial';
      ctx.fillText('Ranking Run', width - 20, footerY + 25);
      ctx.textAlign = 'left';

      const imageUrl = canvas.toDataURL('image/png');
      setShareImageUrl(imageUrl);
    } catch (error) {
      console.error('Erro ao gerar card:', error);
      toast.error('Erro ao gerar imagem. Tente novamente.');
    } finally {
      setGeneratingShare(false);
    }
  };

  // Abre modal de compartilhamento
  const handleOpenShare = async () => {
    setShowShareModal(true);
    await generateShareCard();
  };

  // Baixa a imagem do card
  const downloadShareImage = () => {
    if (!shareImageUrl) return;
    const link = document.createElement('a');
    link.download = `RAIO-X_${atleta?.nome?.replace(/\s+/g, '_') || 'Atleta'}_${new Date().toISOString().split('T')[0]}.png`;
    link.href = shareImageUrl;
    link.click();
    toast.success('Imagem baixada!');
  };

  // Gera URL de compartilhamento
  const getShareUrl = () => {
    return `${window.location.origin}/raio-x`;
  };

  // Gera texto de compartilhamento
  const getShareText = () => {
    const nome = atleta?.nome || 'Atleta';
    const scoreAtual = score?.score_mes_atual || 0;
    const totalProvas = evolucao?.totais?.total_provas || 0;
    const melhorPace = records?.records?.melhor_pace?.valor_formatado || '-';
    return `🏃 Meu RAIO-X no Ranking Run!\n\n📊 Score: ${scoreAtual}%\n🏆 ${totalProvas} provas\n⚡ Melhor pace: ${melhorPace}/km\n\nConfira seu desempenho também!`;
  };

  // Compartilha no WhatsApp
  const shareWhatsApp = () => {
    const text = encodeURIComponent(getShareText() + '\n\n' + getShareUrl());
    window.open(`https://wa.me/?text=${text}`, '_blank');
  };

  // Compartilha no Facebook
  const shareFacebook = () => {
    const url = encodeURIComponent(getShareUrl());
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
  };

  // Compartilha no Twitter/X
  const shareTwitter = () => {
    const text = encodeURIComponent(getShareText());
    const url = encodeURIComponent(getShareUrl());
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  };

  // Copia link
  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(getShareUrl());
      setLinkCopied(true);
      toast.success('Link copiado!');
      setTimeout(() => setLinkCopied(false), 2000);
    } catch (error) {
      toast.error('Erro ao copiar link');
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
              <Button variant="outline" size="sm" onClick={handleOpenShare} className="border-white/30 text-white hover:bg-white/20">
                <Share2 className="w-4 h-4 mr-2" />
                Compartilhar
              </Button>
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
          <TabsList className="bg-slate-800 border-slate-700 mb-6 flex-wrap">
            <TabsTrigger value="visao-geral">Visão Geral</TabsTrigger>
            <TabsTrigger value="evolucao">Evolução</TabsTrigger>
            <TabsTrigger value="records">Records (RP)</TabsTrigger>
            <TabsTrigger value="comparativo">Comparativo</TabsTrigger>
            <TabsTrigger value="conquistas">Conquistas</TabsTrigger>
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
            <div className="space-y-6">
              {/* Seletores de Mês */}
              <Card className="bg-gradient-to-r from-orange-500/10 to-amber-500/10 border-orange-500/30">
                <CardContent className="py-4">
                  <div className="flex flex-col md:flex-row items-center justify-center gap-4">
                    {/* Mês 1 */}
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setMesSelecionado1(prev => prev > 0 ? prev - 1 : 11)}
                        className="text-white hover:bg-slate-700"
                      >
                        <ChevronLeft className="w-5 h-5" />
                      </Button>
                      <div className="w-32 text-center">
                        <p className="text-xs text-slate-400">Comparar</p>
                        <p className="text-lg font-bold text-white">{mesesDoAno[mesSelecionado1]}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setMesSelecionado1(prev => prev < 11 ? prev + 1 : 0)}
                        className="text-white hover:bg-slate-700"
                      >
                        <ChevronRight className="w-5 h-5" />
                      </Button>
                    </div>
                    
                    {/* Ícone de comparação */}
                    <div className="flex items-center gap-2 px-4">
                      <ArrowLeftRight className="w-6 h-6 text-orange-400" />
                    </div>
                    
                    {/* Mês 2 */}
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setMesSelecionado2(prev => prev > 0 ? prev - 1 : 11)}
                        className="text-white hover:bg-slate-700"
                      >
                        <ChevronLeft className="w-5 h-5" />
                      </Button>
                      <div className="w-32 text-center">
                        <p className="text-xs text-slate-400">Com</p>
                        <p className="text-lg font-bold text-white">{mesesDoAno[mesSelecionado2]}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setMesSelecionado2(prev => prev < 11 ? prev + 1 : 0)}
                        className="text-white hover:bg-slate-700"
                      >
                        <ChevronRight className="w-5 h-5" />
                      </Button>
                    </div>
                  </div>
                  <p className="text-center text-xs text-slate-500 mt-2">Ano: {anoAtual}</p>
                </CardContent>
              </Card>

              {loadingComparativo ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Comparativo Personalizado */}
                  <Card className="bg-slate-800 border-slate-700">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-orange-400" />
                        {mesesDoAno[mesSelecionado1]} vs {mesesDoAno[mesSelecionado2]}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        {/* Distância */}
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-slate-400">Distância Total</span>
                            <div className="flex items-center gap-2">
                              {(comparativoPersonalizado?.variacoes?.distancia || 0) > 0 ? (
                                <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                              ) : (comparativoPersonalizado?.variacoes?.distancia || 0) < 0 ? (
                                <ArrowDownRight className="w-4 h-4 text-red-400" />
                              ) : null}
                              <span className={(comparativoPersonalizado?.variacoes?.distancia || 0) > 0 ? 'text-emerald-400' : (comparativoPersonalizado?.variacoes?.distancia || 0) < 0 ? 'text-red-400' : 'text-slate-400'}>
                                {(comparativoPersonalizado?.variacoes?.distancia || 0) > 0 ? '+' : ''}{comparativoPersonalizado?.variacoes?.distancia || 0}%
                              </span>
                            </div>
                          </div>
                          <div className="flex gap-4">
                            <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                              <p className="text-2xl font-bold text-white">{comparativoPersonalizado?.mes1?.metricas?.distancia_total_km || 0}</p>
                              <p className="text-xs text-slate-400">km em {mesesDoAno[mesSelecionado1]}</p>
                            </div>
                            <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                              <p className="text-2xl font-bold text-slate-400">{comparativoPersonalizado?.mes2?.metricas?.distancia_total_km || 0}</p>
                              <p className="text-xs text-slate-500">km em {mesesDoAno[mesSelecionado2]}</p>
                            </div>
                          </div>
                        </div>

                        {/* Provas */}
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-slate-400">Número de Provas</span>
                            <div className="flex items-center gap-2">
                              {(comparativoPersonalizado?.variacoes?.provas || 0) > 0 ? (
                                <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                              ) : (comparativoPersonalizado?.variacoes?.provas || 0) < 0 ? (
                                <ArrowDownRight className="w-4 h-4 text-red-400" />
                              ) : null}
                              <span className={(comparativoPersonalizado?.variacoes?.provas || 0) > 0 ? 'text-emerald-400' : (comparativoPersonalizado?.variacoes?.provas || 0) < 0 ? 'text-red-400' : 'text-slate-400'}>
                                {(comparativoPersonalizado?.variacoes?.provas || 0) > 0 ? '+' : ''}{comparativoPersonalizado?.variacoes?.provas || 0}%
                              </span>
                            </div>
                          </div>
                          <div className="flex gap-4">
                            <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                              <p className="text-2xl font-bold text-white">{comparativoPersonalizado?.mes1?.metricas?.num_provas || 0}</p>
                              <p className="text-xs text-slate-400">em {mesesDoAno[mesSelecionado1]}</p>
                            </div>
                            <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                              <p className="text-2xl font-bold text-slate-400">{comparativoPersonalizado?.mes2?.metricas?.num_provas || 0}</p>
                              <p className="text-xs text-slate-500">em {mesesDoAno[mesSelecionado2]}</p>
                            </div>
                          </div>
                        </div>

                        {/* Pace */}
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-slate-400">Pace Médio</span>
                            <div className="flex items-center gap-2">
                              {(comparativoPersonalizado?.variacoes?.pace || 0) > 0 ? (
                                <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                              ) : (comparativoPersonalizado?.variacoes?.pace || 0) < 0 ? (
                                <ArrowDownRight className="w-4 h-4 text-red-400" />
                              ) : null}
                              <span className={(comparativoPersonalizado?.variacoes?.pace || 0) > 0 ? 'text-emerald-400' : (comparativoPersonalizado?.variacoes?.pace || 0) < 0 ? 'text-red-400' : 'text-slate-400'}>
                                {(comparativoPersonalizado?.variacoes?.pace || 0) > 0 ? '+' : ''}{comparativoPersonalizado?.variacoes?.pace || 0}%
                              </span>
                            </div>
                          </div>
                          <div className="flex gap-4">
                            <div className="flex-1 bg-slate-700 rounded-lg p-3 text-center">
                              <p className="text-2xl font-bold text-white">{comparativoPersonalizado?.mes1?.metricas?.pace_medio || '-'}</p>
                              <p className="text-xs text-slate-400">/km em {mesesDoAno[mesSelecionado1]}</p>
                            </div>
                            <div className="flex-1 bg-slate-700/50 rounded-lg p-3 text-center">
                              <p className="text-2xl font-bold text-slate-400">{comparativoPersonalizado?.mes2?.metricas?.pace_medio || '-'}</p>
                              <p className="text-xs text-slate-500">/km em {mesesDoAno[mesSelecionado2]}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Melhor Performance do Mês Atual */}
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
                              <p className="text-2xl font-bold text-purple-400">{comparativo.melhor_performance_mes.pace}</p>
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
                </div>
              )}
            </div>
          </TabsContent>

          {/* Aba: Conquistas */}
          <TabsContent value="conquistas">
            <div className="space-y-6">
              {/* Header com botão de ajuda */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Trophy className="w-6 h-6 text-amber-500" />
                  <h2 className="text-xl font-bold text-white">Insígnias & Conquistas</h2>
                  {badges.length > 0 && (
                    <Badge variant="outline" className="border-amber-500/50 text-amber-400">
                      {badges.filter(b => b.conquistado).length}/{badges.length}
                    </Badge>
                  )}
                </div>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowHelpModal(true)}
                  className="border-slate-600 text-slate-300 hover:bg-slate-700"
                >
                  <HelpCircle className="w-4 h-4 mr-2" />
                  Como Conquistar
                </Button>
              </div>

              {badgesLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
                </div>
              ) : badges.length === 0 ? (
                <Card className="bg-slate-800 border-slate-700">
                  <CardContent className="py-12 text-center">
                    <Trophy className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-white mb-2">Nenhuma insígnia disponível</h3>
                    <p className="text-slate-400">Continue participando de corridas para desbloquear conquistas!</p>
                  </CardContent>
                </Card>
              ) : (
                <>
                  {/* Badges Conquistados */}
                  {badges.filter(b => b.conquistado).length > 0 && (
                    <Card className="bg-slate-800 border-slate-700">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg text-white flex items-center gap-2">
                          <Sparkles className="w-5 h-5 text-amber-400" />
                          Conquistados ({badges.filter(b => b.conquistado).length})
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-4">
                          {badges.filter(b => b.conquistado).map(badge => (
                            <BadgeItem key={badge.id} badge={badge} size="md" />
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Badges A Conquistar */}
                  {badges.filter(b => !b.conquistado).length > 0 && (
                    <Card className="bg-slate-800/50 border-slate-700">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg text-slate-400 flex items-center gap-2">
                          <Lock className="w-5 h-5" />
                          A Conquistar ({badges.filter(b => !b.conquistado).length})
                        </CardTitle>
                        <CardDescription className="text-slate-500">
                          Continue participando para desbloquear mais insígnias!
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-4">
                          {badges.filter(b => !b.conquistado).map(badge => (
                            <BadgeItem key={badge.id} badge={badge} size="md" />
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Dica */}
                  <div className="p-4 bg-emerald-500/10 rounded-xl border border-emerald-500/30">
                    <div className="flex items-start gap-3">
                      <Star className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-medium text-emerald-400">Dica</p>
                        <p className="text-sm text-emerald-300/80">
                          Cada insígnia conquistada garante pontos bônus no ranking! Continue participando de corridas e registrando seus resultados para desbloquear todas as conquistas.
                        </p>
                      </div>
                    </div>
                  </div>
                </>
              )}
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

      {/* Modal de Compartilhamento */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            {/* Header do Modal */}
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Share2 className="w-5 h-5 text-emerald-400" />
                Compartilhar RAIO-X
              </h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowShareModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Preview da Imagem */}
            <div className="p-4">
              <div className="bg-slate-900 rounded-lg p-2 mb-4">
                {generatingShare ? (
                  <div className="h-64 flex items-center justify-center">
                    <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
                  </div>
                ) : shareImageUrl ? (
                  <img
                    src={shareImageUrl}
                    alt="Preview do card"
                    className="w-full rounded-lg"
                  />
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400">
                    Gerando preview...
                  </div>
                )}
              </div>

              {/* Botões de Redes Sociais */}
              <div className="space-y-3">
                <p className="text-sm text-slate-400 text-center mb-2">Compartilhar via</p>
                
                <div className="grid grid-cols-2 gap-2">
                  {/* WhatsApp */}
                  <Button
                    onClick={shareWhatsApp}
                    className="bg-[#25D366] hover:bg-[#20BD5A] text-white"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                    </svg>
                    WhatsApp
                  </Button>

                  {/* Facebook */}
                  <Button
                    onClick={shareFacebook}
                    className="bg-[#1877F2] hover:bg-[#166FE5] text-white"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                    Facebook
                  </Button>

                  {/* Twitter/X */}
                  <Button
                    onClick={shareTwitter}
                    className="bg-black hover:bg-gray-900 text-white"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                    Twitter/X
                  </Button>

                  {/* Copiar Link */}
                  <Button
                    onClick={copyLink}
                    variant="outline"
                    className="border-slate-600 text-white hover:bg-slate-700"
                  >
                    {linkCopied ? (
                      <>
                        <Check className="w-5 h-5 mr-2 text-emerald-400" />
                        Copiado!
                      </>
                    ) : (
                      <>
                        <Copy className="w-5 h-5 mr-2" />
                        Copiar Link
                      </>
                    )}
                  </Button>
                </div>

                {/* Botão de Download da Imagem */}
                <Button
                  onClick={downloadShareImage}
                  disabled={!shareImageUrl}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white mt-2"
                >
                  <Download className="w-5 h-5 mr-2" />
                  Baixar Imagem para Instagram
                </Button>
                <p className="text-xs text-slate-500 text-center">
                  Baixe a imagem e compartilhe nos Stories do Instagram
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Ajuda - Como Conquistar Insígnias */}
      <Dialog open={showHelpModal} onOpenChange={setShowHelpModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto bg-slate-800 border-slate-700">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl text-white">
              <Trophy className="w-6 h-6 text-amber-500" />
              Guia de Insígnias & Conquistas
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 mt-4">
            <p className="text-slate-400 text-sm">
              As insígnias são conquistas especiais que você pode ganhar ao participar de corridas e atingir marcos importantes. 
              Cada insígnia concede pontos bônus ao ser conquistada!
            </p>
            
            <div className="grid gap-3">
              {TODAS_INSIGNIAS.map((insignia) => (
                <div 
                  key={insignia.id}
                  className="flex items-start gap-4 p-4 rounded-xl border border-slate-700 hover:bg-slate-700/50 transition-colors"
                >
                  {/* Badge visual */}
                  <div 
                    className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg"
                    style={{ background: `linear-gradient(135deg, ${insignia.cor}, ${insignia.cor}dd)` }}
                  >
                    <span className="text-2xl">{insignia.emoji}</span>
                  </div>
                  
                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-white">{insignia.nome}</h3>
                      <Badge className="text-xs" style={{ backgroundColor: `${insignia.cor}20`, color: insignia.cor }}>
                        +{insignia.pontos_bonus} pts
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-400 mt-1">{insignia.descricao}</p>
                    <p className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" />
                      <strong>Como conquistar:</strong> {insignia.como_conquistar}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 p-4 bg-emerald-500/10 rounded-xl border border-emerald-500/30">
              <h4 className="font-bold text-emerald-400 flex items-center gap-2">
                <Star className="w-4 h-4" />
                Dica
              </h4>
              <p className="text-sm text-emerald-300/80 mt-1">
                Continue participando de corridas e registrando seus resultados para desbloquear mais insígnias. 
                Cada conquista te aproxima do status de Atleta Elite!
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RaioXPage;
