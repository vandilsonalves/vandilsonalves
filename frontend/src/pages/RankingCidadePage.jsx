// /app/frontend/src/pages/RankingCidadePage.jsx
// Ranking por Cidade/Bairro - Visualização local do ranking

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { 
  ArrowLeft, MapPin, Trophy, Users, Medal, 
  Search, Loader2, Building2, Map, Share2, Download,
  X, Check, Copy
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;
const BACKEND_URL = API;

const RankingCidadePage = () => {
  const navigate = useNavigate();
  
  // Estados para filtros
  const [estados, setEstados] = useState([]);
  const [cidades, setCidades] = useState([]);
  const [selectedEstado, setSelectedEstado] = useState('');
  const [selectedCidade, setSelectedCidade] = useState('');
  const [modalidade, setModalidade] = useState('profissional');
  const [genero, setGenero] = useState('M');
  const [searchCidade, setSearchCidade] = useState('');
  
  // Estados para dados
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingCidades, setLoadingCidades] = useState(false);
  const [stats, setStats] = useState({ total: 0, cidade: '', estado: '' });

  // Share states
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareImageUrl, setShareImageUrl] = useState(null);
  const [generatingShare, setGeneratingShare] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);

  // Carregar estados ao montar
  useEffect(() => {
    fetchEstados();
  }, []);

  // Carregar cidades quando estado mudar
  useEffect(() => {
    if (selectedEstado) {
      fetchCidades(selectedEstado);
      setSelectedCidade('');
      setRanking([]);
    }
  }, [selectedEstado]);

  // Carregar ranking quando cidade mudar
  useEffect(() => {
    if (selectedEstado && selectedCidade) {
      fetchRanking();
    }
  }, [selectedCidade, modalidade, genero]);

  const fetchEstados = async () => {
    try {
      const response = await axios.get(`${API}/api/ranking/estados`);
      setEstados(response.data.estados || []);
    } catch (error) {
      console.error('Erro ao buscar estados:', error);
      toast.error('Erro ao carregar estados');
    }
  };

  const fetchCidades = async (estado) => {
    setLoadingCidades(true);
    try {
      const response = await axios.get(`${API}/api/ranking/cidades?estado=${estado}`);
      setCidades(response.data.cidades || []);
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
      toast.error('Erro ao carregar cidades');
    } finally {
      setLoadingCidades(false);
    }
  };

  const fetchRanking = async () => {
    if (!selectedEstado || !selectedCidade) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams({
        modalidade,
        genero,
        ano: new Date().getFullYear()  // Ano atual dinâmico
      });
      
      const response = await axios.get(
        `${API}/api/ranking/por-cidade/${encodeURIComponent(selectedEstado)}/${encodeURIComponent(selectedCidade)}?${params}`
      );
      
      setRanking(response.data.ranking || []);
      setStats({
        total: response.data.total || 0,
        cidade: response.data.cidade || selectedCidade,
        estado: response.data.estado || selectedEstado
      });
    } catch (error) {
      console.error('Erro ao buscar ranking:', error);
      toast.error('Erro ao carregar ranking da cidade');
    } finally {
      setLoading(false);
    }
  };

  // Filtrar cidades pela busca
  const cidadesFiltradas = cidades.filter(c => 
    c.nome.toLowerCase().includes(searchCidade.toLowerCase())
  );

  // Helper: desenha retângulo arredondado sem usar roundRect
  const drawRoundedRect = (ctx, x, y, w, h, r) => {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.arc(x + w - r, y + r, r, -Math.PI / 2, 0);
    ctx.lineTo(x + w, y + h - r);
    ctx.arc(x + w - r, y + h - r, r, 0, Math.PI / 2);
    ctx.lineTo(x + r, y + h);
    ctx.arc(x + r, y + h - r, r, Math.PI / 2, Math.PI);
    ctx.lineTo(x, y + r);
    ctx.arc(x + r, y + r, r, Math.PI, -Math.PI / 2);
    ctx.closePath();
  };

  // Gera share card Canvas 9:16
  const generateShareCard = async () => {
    setGeneratingShare(true);
    try {
      const width = 540;
      const height = 960;
      const canvas = document.createElement('canvas');
      canvas.width = width * 2;
      canvas.height = height * 2;
      const ctx = canvas.getContext('2d');
      ctx.scale(2, 2);

      // Background
      const bg = ctx.createLinearGradient(0, 0, 0, height);
      bg.addColorStop(0, '#0f172a');
      bg.addColorStop(0.4, '#1e293b');
      bg.addColorStop(0.8, '#1e293b');
      bg.addColorStop(1, '#0f172a');
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, width, height);

      // Decorative circles
      ctx.fillStyle = 'rgba(16, 185, 129, 0.08)';
      ctx.beginPath();
      ctx.arc(-40, 120, 180, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(width + 40, height - 120, 180, 0, Math.PI * 2);
      ctx.fill();

      let yPos = 30;

      // Logo area
      const logoGrad = ctx.createLinearGradient(20, yPos, 68, yPos + 48);
      logoGrad.addColorStop(0, '#10b981');
      logoGrad.addColorStop(1, '#14b8a6');
      ctx.fillStyle = logoGrad;
      drawRoundedRect(ctx, 20, yPos, 48, 48, 12);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 24px Arial';
      ctx.textAlign = 'left';
      ctx.fillText('R', 35, yPos + 34);

      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 18px Arial';
      ctx.fillText('Ranking por Cidade', 78, yPos + 25);
      ctx.fillStyle = '#10b981';
      ctx.font = '12px Arial';
      ctx.fillText('Ranking Run', 78, yPos + 42);

      ctx.fillStyle = '#64748b';
      ctx.font = '10px Arial';
      ctx.textAlign = 'right';
      ctx.fillText('rankingrun.com.br', width - 20, yPos + 35);
      ctx.textAlign = 'left';
      yPos += 80;

      // City + State title
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 28px Arial';
      ctx.textAlign = 'center';
      const cityTitle = `${stats.cidade} - ${stats.estado}`;
      ctx.fillText(cityTitle, width / 2, yPos);
      yPos += 10;

      // Modalidade + Gênero subtitle
      const modLabel = modalidade === 'povao' ? 'Galera' : 'Profissional/Amador';
      const genLabel = genero === 'M' ? 'Masculino' : genero === 'F' ? 'Feminino' : genero === 'pcd' ? 'PCD' : 'Cadeirante';
      ctx.fillStyle = '#94a3b8';
      ctx.font = '14px Arial';
      ctx.fillText(`${modLabel} | ${genLabel}`, width / 2, yPos + 20);
      ctx.textAlign = 'left';
      yPos += 50;

      // Divider line
      const divGrad = ctx.createLinearGradient(40, yPos, width - 40, yPos);
      divGrad.addColorStop(0, 'rgba(16,185,129,0)');
      divGrad.addColorStop(0.5, 'rgba(16,185,129,0.5)');
      divGrad.addColorStop(1, 'rgba(16,185,129,0)');
      ctx.strokeStyle = divGrad;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(40, yPos);
      ctx.lineTo(width - 40, yPos);
      ctx.stroke();
      yPos += 20;

      // Stats bar
      ctx.fillStyle = 'rgba(16,185,129,0.1)';
      drawRoundedRect(ctx, 30, yPos, width - 60, 45, 10);
      ctx.fill();
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 14px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(`${stats.total} atletas classificados`, width / 2, yPos + 28);
      ctx.textAlign = 'left';
      yPos += 65;

      // Column headers
      ctx.fillStyle = '#64748b';
      ctx.font = 'bold 11px Arial';
      ctx.fillText('#', 35, yPos);
      ctx.fillText('ATLETA', 70, yPos);
      ctx.textAlign = 'right';
      ctx.fillText('PTS', width - 35, yPos);
      ctx.textAlign = 'left';
      yPos += 15;

      // Header line
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(30, yPos);
      ctx.lineTo(width - 30, yPos);
      ctx.stroke();
      yPos += 10;

      // Athlete rows (max 10)
      const topAtletas = ranking.slice(0, 10);
      const rowHeight = 58;

      topAtletas.forEach((atleta, idx) => {
        const rowY = yPos + idx * rowHeight;

        // Top 3 highlight background
        if (idx < 3) {
          ctx.fillStyle = idx === 0 ? 'rgba(234,179,8,0.08)' : idx === 1 ? 'rgba(148,163,184,0.06)' : 'rgba(180,83,9,0.06)';
          drawRoundedRect(ctx, 30, rowY - 5, width - 60, rowHeight - 6, 8);
          ctx.fill();
        }

        // Position number / medal
        ctx.textAlign = 'center';
        if (idx === 0) {
          ctx.font = '22px Arial';
          ctx.fillText('🥇', 48, rowY + 24);
        } else if (idx === 1) {
          ctx.font = '22px Arial';
          ctx.fillText('🥈', 48, rowY + 24);
        } else if (idx === 2) {
          ctx.font = '22px Arial';
          ctx.fillText('🥉', 48, rowY + 24);
        } else {
          ctx.fillStyle = '#64748b';
          ctx.font = 'bold 14px Arial';
          ctx.fillText(`${idx + 1}º`, 48, rowY + 22);
        }

        // Avatar circle
        const avatarX = 82;
        const avatarR = 16;
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc(avatarX, rowY + 18, avatarR, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 14px Arial';
        ctx.fillText((atleta.nome || '?')[0].toUpperCase(), avatarX, rowY + 23);
        ctx.textAlign = 'left';

        // Name
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 13px Arial';
        const nameMaxWidth = width - 180;
        let displayName = atleta.nome || '';
        if (ctx.measureText(displayName).width > nameMaxWidth) {
          while (ctx.measureText(displayName + '...').width > nameMaxWidth && displayName.length > 0) {
            displayName = displayName.slice(0, -1);
          }
          displayName += '...';
        }
        ctx.fillText(displayName, 106, rowY + 17);

        // Team
        if (atleta.equipe) {
          ctx.fillStyle = '#10b981';
          ctx.font = '10px Arial';
          let teamName = atleta.equipe;
          if (ctx.measureText(teamName).width > nameMaxWidth) {
            while (ctx.measureText(teamName + '...').width > nameMaxWidth && teamName.length > 0) {
              teamName = teamName.slice(0, -1);
            }
            teamName += '...';
          }
          ctx.fillText(teamName, 106, rowY + 32);
        }

        // Points
        ctx.textAlign = 'right';
        ctx.fillStyle = '#f59e0b';
        ctx.font = 'bold 14px Arial';
        ctx.fillText(`${atleta.pontos}`, width - 35, rowY + 17);
        ctx.fillStyle = '#64748b';
        ctx.font = '10px Arial';
        ctx.fillText(`${atleta.total_corridas || 0} corridas`, width - 35, rowY + 32);
        ctx.textAlign = 'left';

        // Row separator (except last)
        if (idx < topAtletas.length - 1) {
          ctx.strokeStyle = 'rgba(51,65,85,0.5)';
          ctx.lineWidth = 0.5;
          ctx.beginPath();
          ctx.moveTo(65, rowY + rowHeight - 5);
          ctx.lineTo(width - 35, rowY + rowHeight - 5);
          ctx.stroke();
        }
      });

      // Footer
      const footerY = height - 50;
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(20, footerY);
      ctx.lineTo(width - 20, footerY);
      ctx.stroke();

      ctx.fillStyle = '#64748b';
      ctx.font = '11px Arial';
      ctx.textAlign = 'left';
      ctx.fillText(`Gerado em ${new Date().toLocaleDateString('pt-BR')}`, 20, footerY + 25);
      ctx.textAlign = 'right';
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 12px Arial';
      ctx.fillText('Ranking Run', width - 20, footerY + 25);
      ctx.textAlign = 'left';

      const imageUrl = canvas.toDataURL('image/png');
      setShareImageUrl(imageUrl);
    } catch (error) {
      console.error('Erro ao gerar share card:', error);
      toast.error('Erro ao gerar imagem. Tente novamente.');
    } finally {
      setGeneratingShare(false);
    }
  };

  const handleOpenShare = async () => {
    setShowShareModal(true);
    setShareImageUrl(null);
    await generateShareCard();
  };

  const downloadShareImage = () => {
    if (!shareImageUrl) return;
    const link = document.createElement('a');
    link.download = `Ranking_${stats.cidade}_${stats.estado}_${new Date().toISOString().split('T')[0]}.png`;
    link.href = shareImageUrl;
    link.click();
    toast.success('Imagem baixada!');
  };

  const getShareText = () => {
    const modLabel = modalidade === 'povao' ? 'Galera' : 'Profissional/Amador';
    const genLabel = genero === 'M' ? 'Masculino' : genero === 'F' ? 'Feminino' : genero;
    return `🏃 Ranking de ${stats.cidade}/${stats.estado}!\n\n📊 ${stats.total} atletas classificados\n🏆 Modalidade: ${modLabel}\n👤 ${genLabel}\n\nConfira o ranking da sua cidade!`;
  };

  const getShareUrl = () => `${window.location.origin}/ranking-cidade`;

  const shareWhatsApp = () => {
    const text = encodeURIComponent(getShareText() + '\n\n' + getShareUrl());
    window.open(`https://wa.me/?text=${text}`, '_blank');
  };

  const shareFacebook = () => {
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(getShareUrl())}`, '_blank');
  };

  const shareTwitter = () => {
    const text = encodeURIComponent(getShareText());
    const url = encodeURIComponent(getShareUrl());
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  };

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

  // Medalhas por posição
  const getMedalha = (posicao) => {
    if (posicao === 1) return <span className="text-2xl">🥇</span>;
    if (posicao === 2) return <span className="text-2xl">🥈</span>;
    if (posicao === 3) return <span className="text-2xl">🥉</span>;
    return <span className="text-lg font-bold text-slate-400">{posicao}º</span>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-green-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => navigate('/')}
              className="text-white hover:bg-white/20"
              data-testid="btn-voltar"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <MapPin className="h-6 w-6" />
                Ranking por Cidade
              </h1>
              <p className="text-emerald-100 text-sm">
                Veja a classificação dos atletas da sua região
              </p>
            </div>
            {/* Share button */}
            {ranking.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleOpenShare}
                className="text-white hover:bg-white/20 ml-auto"
                data-testid="btn-compartilhar-ranking"
              >
                <Share2 className="h-4 w-4 mr-2" />
                Compartilhar
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        {/* Filtros */}
        <Card className="bg-slate-800/50 border-slate-700 mb-6">
          <CardHeader className="pb-4">
            <CardTitle className="text-white flex items-center gap-2">
              <Map className="h-5 w-5 text-emerald-400" />
              Selecione a Localização
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Seletor de Estado */}
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Estado</label>
                <Select value={selectedEstado} onValueChange={setSelectedEstado}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="select-estado">
                    <SelectValue placeholder="Selecione o estado" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    {estados.map((estado) => (
                      <SelectItem key={estado} value={estado} className="text-white hover:bg-slate-700">
                        {estado}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Seletor de Cidade */}
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Cidade</label>
                <Select 
                  value={selectedCidade} 
                  onValueChange={setSelectedCidade}
                  disabled={!selectedEstado || loadingCidades}
                >
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="select-cidade">
                    {loadingCidades ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Carregando...
                      </div>
                    ) : (
                      <SelectValue placeholder={selectedEstado ? "Selecione a cidade" : "Selecione um estado primeiro"} />
                    )}
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700 max-h-60">
                    <div className="p-2 sticky top-0 bg-slate-800">
                      <Input
                        placeholder="Buscar cidade..."
                        value={searchCidade}
                        onChange={(e) => setSearchCidade(e.target.value)}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>
                    {cidadesFiltradas.map((cidade) => (
                      <SelectItem 
                        key={cidade.nome} 
                        value={cidade.nome} 
                        className="text-white hover:bg-slate-700"
                      >
                        <div className="flex items-center justify-between w-full">
                          <span>{cidade.nome}</span>
                          <Badge variant="outline" className="ml-2 text-xs">
                            {cidade.atletas} atletas
                          </Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Modalidade */}
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Modalidade</label>
                <Select value={modalidade} onValueChange={setModalidade}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="select-modalidade">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    <SelectItem value="profissional" className="text-white hover:bg-slate-700">
                      <div className="flex items-center gap-2">
                        <Trophy className="h-4 w-4 text-amber-400" />
                        Profissional/Amador
                      </div>
                    </SelectItem>
                    <SelectItem value="povao" className="text-white hover:bg-slate-700">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-green-400" />
                        Galera
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Gênero */}
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Gênero</label>
                  <Select value={genero} onValueChange={setGenero}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="select-genero">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      <SelectItem value="M" className="text-white hover:bg-slate-700">Masculino</SelectItem>
                      <SelectItem value="F" className="text-white hover:bg-slate-700">Feminino</SelectItem>
                      <SelectItem value="pcd" className="text-white hover:bg-slate-700">PCD</SelectItem>
                      <SelectItem value="cadeirante" className="text-white hover:bg-slate-700">Cadeirante</SelectItem>
                    </SelectContent>
                  </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Estatísticas da cidade */}
        {stats.total > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card className="bg-gradient-to-br from-emerald-600/20 to-green-600/20 border-emerald-500/30">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center">
                  <Building2 className="h-6 w-6 text-emerald-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Cidade</p>
                  <p className="text-xl font-bold text-white">{stats.cidade}</p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border-blue-500/30">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
                  <Map className="h-6 w-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Estado</p>
                  <p className="text-xl font-bold text-white">{stats.estado}</p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-amber-600/20 to-orange-600/20 border-amber-500/30">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center">
                  <Users className="h-6 w-6 text-amber-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Total de Atletas</p>
                  <p className="text-xl font-bold text-white">{stats.total}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Lista do Ranking */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
            <span className="ml-3 text-slate-400">Carregando ranking...</span>
          </div>
        ) : ranking.length > 0 ? (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Trophy className="h-5 w-5 text-amber-400" />
                Ranking de {stats.cidade} - {modalidade === 'povao' ? 'Galera' : 'Profissional/Amador'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {ranking.map((atleta, index) => (
                  <div 
                    key={atleta.id}
                    className={`flex items-center gap-4 p-4 rounded-lg transition-colors ${
                      index < 3 
                        ? 'bg-gradient-to-r from-amber-900/30 to-transparent border border-amber-500/30' 
                        : 'bg-slate-700/50 hover:bg-slate-700'
                    }`}
                    data-testid={`ranking-item-${atleta.id}`}
                  >
                    {/* Posição */}
                    <div className="w-12 flex justify-center">
                      {getMedalha(atleta.colocacao)}
                    </div>
                    
                    {/* Avatar */}
                    <Avatar className="h-12 w-12">
                      {atleta.foto_url ? (
                        <AvatarImage src={`${BACKEND_URL}${atleta.foto_url}`} />
                      ) : null}
                      <AvatarFallback className="bg-emerald-600 text-white">
                        {atleta.nome?.charAt(0) || '?'}
                      </AvatarFallback>
                    </Avatar>
                    
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-white truncate">{atleta.nome}</p>
                      <div className="flex items-center gap-2 text-sm text-slate-400">
                        {atleta.equipe && (
                          <span className="text-emerald-400">{atleta.equipe}</span>
                        )}
                        {atleta.faixa_etaria && (
                          <>
                            <span>•</span>
                            <span>{atleta.faixa_etaria}</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {/* Estatísticas */}
                    <div className="text-right">
                      <p className="text-lg font-bold text-amber-400">{atleta.pontos} pts</p>
                      <p className="text-xs text-slate-400">{atleta.total_corridas} corridas</p>
                    </div>
                    
                    {/* Badge Elite */}
                    {atleta.is_elite && (
                      <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                        Elite
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : selectedCidade ? (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="py-20 text-center">
              <MapPin className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Nenhum atleta encontrado</h3>
              <p className="text-slate-400">
                Não há atletas cadastrados em {selectedCidade} - {selectedEstado} para esta modalidade.
              </p>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="py-20 text-center">
              <Search className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Selecione uma localização</h3>
              <p className="text-slate-400">
                Escolha um estado e uma cidade para ver o ranking local.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Share2 className="w-5 h-5 text-emerald-400" />
                Compartilhar Ranking
              </h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowShareModal(false)}
                className="text-slate-400 hover:text-white"
                data-testid="btn-fechar-share"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            <div className="p-4">
              <div className="bg-slate-900 rounded-lg p-2 mb-4">
                {generatingShare ? (
                  <div className="h-64 flex items-center justify-center">
                    <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
                  </div>
                ) : shareImageUrl ? (
                  <img
                    src={shareImageUrl}
                    alt="Preview do ranking"
                    className="w-full rounded-lg"
                    data-testid="share-image-preview"
                  />
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400">
                    Gerando preview...
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <p className="text-sm text-slate-400 text-center mb-2">Compartilhar via</p>
                
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    onClick={shareWhatsApp}
                    className="bg-[#25D366] hover:bg-[#20BD5A] text-white"
                    data-testid="btn-share-whatsapp"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                    </svg>
                    WhatsApp
                  </Button>

                  <Button
                    onClick={shareFacebook}
                    className="bg-[#1877F2] hover:bg-[#166FE5] text-white"
                    data-testid="btn-share-facebook"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                    Facebook
                  </Button>

                  <Button
                    onClick={shareTwitter}
                    className="bg-black hover:bg-gray-900 text-white"
                    data-testid="btn-share-twitter"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                    Twitter/X
                  </Button>

                  <Button
                    onClick={copyLink}
                    variant="outline"
                    className="border-slate-600 text-white hover:bg-slate-700"
                    data-testid="btn-share-copiar"
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

                <Button
                  onClick={downloadShareImage}
                  disabled={!shareImageUrl}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white mt-2"
                  data-testid="btn-download-image"
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
    </div>
  );
};

export default RankingCidadePage;
