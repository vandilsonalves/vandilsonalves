import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  ArrowLeft, Save, User, Mail, MapPin, Users, Trophy, 
  Facebook, Instagram, Phone, FileText, Camera, Check, Loader2,
  Share2, Award, ExternalLink, Download, Calendar, Lock, Eye, EyeOff, Crop, Zap
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import SelosAtleta from '@/components/SelosAtleta';
import ReputacaoAvaliador from '@/components/ReputacaoAvaliador';
import IndicarAmigos from '@/components/IndicarAmigos';
import CriarAssessoria from '@/components/CriarAssessoria';
import ImageCropModal from '@/components/ImageCropModal';
import StravaIntegration from '@/components/StravaIntegration';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Links de redes sociais com URLs funcionais
const SocialLinks = [
  { 
    name: 'Strava', 
    icon: '🏃', 
    url: 'https://www.strava.com/dashboard', 
    color: 'bg-orange-500 hover:bg-orange-600' 
  },
  { 
    name: 'WhatsApp', 
    icon: '💬', 
    url: 'https://wa.me/', 
    color: 'bg-green-500 hover:bg-green-600' 
  },
  { 
    name: 'TikTok', 
    icon: '🎵', 
    url: 'https://www.tiktok.com/explore', 
    color: 'bg-slate-800 hover:bg-slate-700' 
  },
  { 
    name: 'YouTube', 
    icon: '▶️', 
    url: 'https://www.youtube.com', 
    color: 'bg-red-600 hover:bg-red-700' 
  },
];

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

const PerfilAtletaPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [exportingData, setExportingData] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  // Dados do atleta
  const [atleta, setAtleta] = useState(null);
  const [conquistas, setConquistas] = useState([]);
  const [assessoriaPendente, setAssessoriaPendente] = useState(false);
  const [isDono, setIsDono] = useState(false);
  
  // Campos editáveis
  const [nome, setNome] = useState('');
  const [cidade, setCidade] = useState('');
  const [estado, setEstado] = useState('');
  const [dataNascimento, setDataNascimento] = useState('');
  const [equipe, setEquipe] = useState('');
  const [facebookUrl, setFacebookUrl] = useState('');
  const [instagramUrl, setInstagramUrl] = useState('');
  const [telefone, setTelefone] = useState('');
  const [bio, setBio] = useState('');
  const [etnia, setEtnia] = useState('');
  const [apelido, setApelido] = useState('');
  const [whatsappLink, setWhatsappLink] = useState(''); // Campo para dono de assessoria
  
  // Estados para alteração de senha
  const [showAlterarSenha, setShowAlterarSenha] = useState(false);
  const [senhaAtual, setSenhaAtual] = useState('');
  const [novaSenha, setNovaSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');
  const [savingSenha, setSavingSenha] = useState(false);
  const [showSenhaAtual, setShowSenhaAtual] = useState(false);
  const [showNovaSenha, setShowNovaSenha] = useState(false);

  // Estados para troca de equipe
  const [showTrocarEquipe, setShowTrocarEquipe] = useState(false);
  const [statusTrocaEquipe, setStatusTrocaEquipe] = useState(null);
  const [novaEquipe, setNovaEquipe] = useState('');
  const [equipesDisponiveis, setEquipesDisponiveis] = useState([]);
  const [savingEquipe, setSavingEquipe] = useState(false);

  // Estados para crop de imagem
  const [showCropModal, setShowCropModal] = useState(false);
  const [imageToCrop, setImageToCrop] = useState(null);

  const ETNIAS = ['Branco', 'Negro', 'Indígena', 'Pardo', 'Amarelo', 'Mulato'];

  useEffect(() => {
    if (!user || !token) {
      navigate('/login');
      return;
    }
    fetchAtletaData();
    fetchConquistas();
    fetchStatusTrocaEquipe();
    fetchEquipesDisponiveis();
  }, [user, token]);

  const fetchAtletaData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/atletas/meu-perfil`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const data = response.data;
      setAtleta({
        id: data.id,
        nome: data.nome,
        cidade: data.cidade,
        estado: data.estado,
        genero: data.genero,
        categoria: data.categoria,
        faixa_etaria: data.faixa_etaria,
        foto_url: data.foto_url,
        equipe: data.equipe,
        data_nascimento: data.data_nascimento,
        pontos_carreira: data.pontos_carreira || 0,
        total_corridas: data.total_corridas || 0,
        role: data.role,
        is_dono_assessoria: data.is_dono_assessoria
      });
      
      // Verificar se é dono de assessoria com assessoria pendente
      setIsDono(data.role === 'dono_assessoria' || data.is_dono_assessoria);
      setAssessoriaPendente(data.assessoria_pendente === true);
      
      // Preencher campos editáveis
      setNome(data.nome || '');
      setCidade(data.cidade || '');
      setEstado(data.estado || '');
      setDataNascimento(data.data_nascimento || '');
      setEquipe(data.equipe || '');
      setFacebookUrl(data.facebook_url || '');
      setInstagramUrl(data.instagram_url || '');
      setTelefone(data.telefone || '');
      setBio(data.bio || '');
      setEtnia(data.etnia || '');
      setApelido(data.apelido || '');
      setWhatsappLink(data.whatsapp_link || '');
      
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
      setError('Erro ao carregar dados do perfil');
    } finally {
      setLoading(false);
    }
  };

  const fetchConquistas = async () => {
    try {
      const response = await axios.get(`${API}/conquistas`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConquistas(response.data.conquistas || []);
    } catch (error) {
      console.error('Erro ao buscar conquistas:', error);
    }
  };

  const fetchStatusTrocaEquipe = async () => {
    try {
      const response = await axios.get(`${API}/atletas/status-troca-equipe`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatusTrocaEquipe(response.data);
    } catch (error) {
      console.error('Erro ao buscar status troca equipe:', error);
    }
  };

  const fetchEquipesDisponiveis = async () => {
    try {
      const response = await axios.get(`${API}/assessorias/lista`);
      setEquipesDisponiveis(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar equipes:', error);
    }
  };

  const handleTrocarEquipe = async () => {
    if (!novaEquipe) {
      toast.error('Selecione uma equipe');
      return;
    }
    
    setSavingEquipe(true);
    try {
      const response = await axios.post(`${API}/atletas/trocar-equipe`, 
        { nova_equipe: novaEquipe },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success(response.data.message);
      setShowTrocarEquipe(false);
      setNovaEquipe('');
      
      // Atualizar dados
      fetchAtletaData();
      fetchStatusTrocaEquipe();
      
    } catch (error) {
      const detail = error.response?.data?.detail;
      if (typeof detail === 'object') {
        toast.error(detail.message);
      } else {
        toast.error(detail || 'Erro ao trocar de equipe');
      }
    } finally {
      setSavingEquipe(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    
    try {
      const dadosAtualizar = {
        nome,
        cidade,
        estado,
        data_nascimento: dataNascimento,
        equipe,
        facebook_url: facebookUrl,
        instagram_url: instagramUrl,
        telefone,
        bio,
        etnia,
        apelido
      };
      
      // Adicionar whatsapp_link apenas para donos de assessoria
      if (isDono) {
        dadosAtualizar.whatsapp_link = whatsappLink;
      }
      
      await axios.patch(`${API}/atletas/perfil`, dadosAtualizar, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSuccess('Ação Concluída - Perfil atualizado com sucesso!');
      toast.success('Ação Concluída', { description: 'Perfil atualizado com sucesso!' });
      setAtleta(prev => ({ ...prev, nome, cidade, estado, equipe }));
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (error) {
      console.error('Erro ao salvar:', error);
      setError(error.response?.data?.detail || 'Erro ao salvar alterações');
      toast.error('Erro', { description: error.response?.data?.detail || 'Erro ao salvar alterações' });
    } finally {
      setSaving(false);
    }
  };

  const handleAlterarSenha = async () => {
    if (!senhaAtual || !novaSenha || !confirmarSenha) {
      setError('Preencha todos os campos de senha');
      toast.error('Erro', { description: 'Preencha todos os campos de senha' });
      return;
    }
    
    if (novaSenha !== confirmarSenha) {
      setError('A nova senha e confirmação não conferem');
      toast.error('Erro', { description: 'A nova senha e confirmação não conferem' });
      return;
    }
    
    if (novaSenha.length < 6) {
      setError('A nova senha deve ter pelo menos 6 caracteres');
      toast.error('Erro', { description: 'A nova senha deve ter pelo menos 6 caracteres' });
      return;
    }
    
    setSavingSenha(true);
    setError('');
    
    try {
      await axios.post(`${API}/atletas/alterar-senha`, {
        senha_atual: senhaAtual,
        nova_senha: novaSenha,
        confirmar_senha: confirmarSenha
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSuccess('Ação Concluída - Senha alterada com sucesso!');
      toast.success('Ação Concluída', { description: 'Senha alterada com sucesso!' });
      
      // Limpar campos
      setSenhaAtual('');
      setNovaSenha('');
      setConfirmarSenha('');
      setShowAlterarSenha(false);
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Erro ao alterar senha:', error);
      const msg = error.response?.data?.detail || 'Erro ao alterar senha';
      setError(msg);
      toast.error('Erro', { description: msg });
    } finally {
      setSavingSenha(false);
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      setError('Por favor, selecione uma imagem válida');
      toast.error('Erro', { description: 'Por favor, selecione uma imagem válida' });
      return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
      setError('A imagem deve ter no máximo 5MB');
      toast.error('Erro', { description: 'A imagem deve ter no máximo 5MB' });
      return;
    }
    
    // Abrir modal de crop ao invés de enviar direto
    const reader = new FileReader();
    reader.onload = () => {
      setImageToCrop(reader.result);
      setShowCropModal(true);
    };
    reader.readAsDataURL(file);
    
    // Limpar o input para permitir selecionar a mesma imagem novamente
    e.target.value = '';
  };

  const handleCroppedPhoto = async (croppedFile) => {
    setShowCropModal(false);
    setUploadingPhoto(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('foto', croppedFile);
      
      const response = await axios.post(`${API}/atletas/foto`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Atualizar foto local com URL completa e timestamp para forçar reload
      const fotoUrl = response.data.foto_url.startsWith('http') 
        ? response.data.foto_url 
        : `${BACKEND_URL}${response.data.foto_url}?t=${Date.now()}`;
      
      setAtleta(prev => ({ ...prev, foto_url: fotoUrl }));
      setSuccess('Ação Concluída - Foto atualizada com sucesso!');
      toast.success('Ação Concluída', { description: 'Foto atualizada com sucesso!' });
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (error) {
      console.error('Erro ao enviar foto:', error);
      setError('Erro ao enviar foto');
      toast.error('Erro', { description: 'Erro ao enviar foto' });
    } finally {
      setUploadingPhoto(false);
    }
  };

  const handleExportData = async () => {
    setExportingData(true);
    try {
      const response = await axios.get(`${API}/atletas/meu-ranking/export`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `meu_ranking_${atleta?.nome?.replace(/\s+/g, '_')}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setSuccess('Ação Concluída - Dados exportados com sucesso!');
      toast.success('Ação Concluída', { description: 'Dados exportados com sucesso!' });
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Erro ao exportar:', error);
      setError('Erro ao exportar dados');
      toast.error('Erro', { description: 'Erro ao exportar dados' });
    } finally {
      setExportingData(false);
    }
  };

  const handleShare = async (platform) => {
    try {
      const response = await axios.get(`${API}/atletas/${user.id}/compartilhar`);
      const data = response.data;
      
      const texto = encodeURIComponent(data.texto_whatsapp);
      const url = encodeURIComponent(data.url_compartilhar);
      
      let shareUrl = '';
      
      switch (platform) {
        case 'whatsapp':
          shareUrl = `https://api.whatsapp.com/send?text=${texto}`;
          break;
        case 'instagram':
          // Instagram não tem API de compartilhamento direto, copiar texto
          await navigator.clipboard.writeText(data.texto_whatsapp);
          setSuccess('Texto copiado! Cole no seu Instagram.');
          setTimeout(() => setSuccess(''), 3000);
          return;
        case 'facebook':
          shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${texto}`;
          break;
        default:
          break;
      }
      
      if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400');
      }
    } catch (error) {
      console.error('Erro ao compartilhar:', error);
      setError('Erro ao gerar link de compartilhamento');
    }
  };

  const handleSocialLink = (link) => {
    window.open(link.url, '_blank');
  };

  const formatCategoria = (categoria) => {
    const map = {
      'normal': 'Normal',
      'pcd': 'PCD',
      'cadeirante': 'Cadeirante'
    };
    return map[categoria] || categoria;
  };

  const formatGenero = (genero) => {
    return genero === 'M' ? 'Masculino' : 'Feminino';
  };

  // Construir URL da foto corretamente
  const getFotoUrl = () => {
    if (!atleta?.foto_url) return null;
    if (atleta.foto_url.startsWith('http')) return atleta.foto_url;
    return `${BACKEND_URL}${atleta.foto_url}`;
  };

  if (!user) return null;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-500 mx-auto mb-4" />
          <p className="text-slate-400">Carregando perfil...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-6 px-4">
      <div className="container mx-auto max-w-5xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1" data-testid="perfil-title">
              Meu Perfil
            </h1>
            <p className="text-slate-400">Gerencie suas informações de atleta</p>
          </div>
          <div className="flex gap-2">
            <Button 
              onClick={handleExportData} 
              disabled={exportingData}
              variant="outline" 
              className="border-emerald-600 text-emerald-400 hover:bg-emerald-600/20"
            >
              {exportingData ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Download className="w-4 h-4 mr-2" />
              )}
              Exportar Meus Dados
            </Button>
            <Button onClick={() => navigate('/')} variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar
            </Button>
          </div>
        </div>

        {/* Links Rápidos para Redes Sociais */}
        <Card className="mb-6 bg-slate-800/50 border-slate-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <ExternalLink className="w-5 h-5 text-emerald-400" />
              Acesso Rápido
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {SocialLinks.map((link) => (
                <Button
                  key={link.name}
                  className={`${link.color} text-white border-0`}
                  onClick={() => handleSocialLink(link)}
                >
                  <span className="mr-2">{link.icon}</span>
                  {link.name}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Alertas */}
        {success && (
          <Alert className="mb-6 bg-emerald-500/10 border-emerald-500/30">
            <Check className="h-4 w-4 text-emerald-400" />
            <AlertDescription className="text-emerald-300 ml-2">{success}</AlertDescription>
          </Alert>
        )}
        
        {error && (
          <Alert className="mb-6 bg-red-500/10 border-red-500/30">
            <AlertDescription className="text-red-300">{error}</AlertDescription>
          </Alert>
        )}

        {/* Modal Obrigatório para Criar Assessoria (Dono Pendente) */}
        {isDono && assessoriaPendente && (
          <CriarAssessoria 
            token={token}
            isModal={true}
            forceOpen={true}
            onSuccess={() => {
              setAssessoriaPendente(false);
              fetchAtletaData();
              toast.success('Sua assessoria foi criada! Acesse "Minha Assessoria" no menu.');
            }} 
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Card de Foto e Informações Básicas */}
          <Card className="bg-slate-800/50 border-slate-700 lg:col-span-1">
            <CardHeader className="text-center">
              <div className="relative inline-block mx-auto">
                <Avatar className="h-32 w-32 border-4 border-emerald-500/30">
                  <AvatarImage src={getFotoUrl()} alt={atleta?.nome} />
                  <AvatarFallback className="bg-emerald-600 text-white text-3xl">
                    {atleta?.nome?.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                
                <label className="absolute bottom-0 right-0 cursor-pointer">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoUpload}
                    className="hidden"
                    disabled={uploadingPhoto}
                  />
                  <div className="h-10 w-10 rounded-full bg-emerald-600 hover:bg-emerald-500 flex items-center justify-center transition-colors">
                    {uploadingPhoto ? (
                      <Loader2 className="h-5 w-5 text-white animate-spin" />
                    ) : (
                      <Camera className="h-5 w-5 text-white" />
                    )}
                  </div>
                </label>
              </div>
              
              <CardTitle className="text-xl text-white mt-4">{atleta?.nome}</CardTitle>
              <CardDescription className="text-slate-400">{user?.email}</CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-3 text-slate-300">
                  <MapPin className="w-4 h-4 text-emerald-400" />
                  <span>{atleta?.cidade}/{atleta?.estado}</span>
                </div>
                
                <div className="flex items-center gap-3 text-slate-300">
                  <User className="w-4 h-4 text-emerald-400" />
                  <span>{formatGenero(atleta?.genero)} • {formatCategoria(atleta?.categoria)}</span>
                </div>
                
                <div className="flex items-center gap-3 text-slate-300">
                  <Trophy className="w-4 h-4 text-amber-400" />
                  <span>Faixa: {atleta?.faixa_etaria}</span>
                </div>
              </div>

              {/* Estatísticas */}
              <div className="pt-4 border-t border-slate-700">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-emerald-400">{atleta?.pontos_carreira || 0}</p>
                    <p className="text-xs text-slate-400">Pontos</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-400">{atleta?.total_corridas || 0}</p>
                    <p className="text-xs text-slate-400">Corridas</p>
                  </div>
                </div>
              </div>

              {/* Botão RAIO-X */}
              <div className="pt-4 border-t border-slate-700">
                <Button
                  onClick={() => navigate('/raio-x')}
                  className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-medium"
                  data-testid="raio-x-btn"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  RAIO-X do Atleta
                  <span className="ml-2 text-xs bg-white/20 px-2 py-0.5 rounded">Novo!</span>
                </Button>
                <p className="text-xs text-slate-500 text-center mt-2">
                  Veja sua evolução, records e previsões
                </p>
              </div>

              {/* Selos e Conquistas - Novo Componente */}
              <div className="pt-4 border-t border-slate-700">
                <SelosAtleta atletaId={atleta?.id} compact={true} />
              </div>

              {/* Reputação de Avaliador */}
              <div className="pt-4 border-t border-slate-700">
                <p className="text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-400" />
                  Reputação de Avaliador
                </p>
                <ReputacaoAvaliador atletaId={atleta?.id} compact={true} />
              </div>

              {/* Compartilhar */}
              <div className="pt-4 border-t border-slate-700">
                <p className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
                  <Share2 className="w-4 h-4 text-emerald-400" />
                  Compartilhar minha posição
                </p>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    className="flex-1 bg-green-600 hover:bg-green-500"
                    onClick={() => handleShare('whatsapp')}
                  >
                    WhatsApp
                  </Button>
                  <Button
                    size="sm"
                    className="flex-1 bg-pink-600 hover:bg-pink-500"
                    onClick={() => handleShare('instagram')}
                  >
                    Instagram
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Formulário de Edição */}
          <Card className="bg-slate-800/50 border-slate-700 lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-emerald-400" />
                Informações Editáveis
              </CardTitle>
              <CardDescription className="text-slate-400">
                Atualize suas informações de perfil. O email não pode ser alterado.
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Nome */}
              <div className="space-y-2">
                <Label htmlFor="nome" className="text-slate-300 flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Nome Completo
                </Label>
                <Input
                  id="nome"
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  placeholder="Seu nome completo"
                  className="bg-slate-900 border-slate-600 text-white"
                  data-testid="input-nome"
                />
              </div>

              {/* Cidade e Estado */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="cidade" className="text-slate-300 flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    Cidade
                  </Label>
                  <Input
                    id="cidade"
                    value={cidade}
                    onChange={(e) => setCidade(e.target.value)}
                    placeholder="Sua cidade"
                    className="bg-slate-900 border-slate-600 text-white"
                    data-testid="input-cidade"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="estado" className="text-slate-300 flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    UF
                  </Label>
                  <Select value={estado} onValueChange={setEstado}>
                    <SelectTrigger className="bg-slate-900 border-slate-600 text-white" data-testid="input-estado">
                      <SelectValue placeholder="Selecione o estado" />
                    </SelectTrigger>
                    <SelectContent>
                      {ESTADOS_BR.map((uf) => (
                        <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Data de Nascimento */}
              <div className="space-y-2">
                <Label htmlFor="data_nascimento" className="text-slate-300 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Data de Nascimento
                </Label>
                <Input
                  id="data_nascimento"
                  type="date"
                  value={dataNascimento}
                  onChange={(e) => setDataNascimento(e.target.value)}
                  className="bg-slate-900 border-slate-600 text-white"
                  data-testid="input-data-nascimento"
                />
              </div>

              {/* Equipe */}
              <div className="space-y-2">
                <Label htmlFor="equipe" className="text-slate-300 flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Equipe / Assessoria
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="equipe"
                    value={equipe || 'INDIVIDUAL'}
                    disabled
                    className="bg-slate-900 border-slate-600 text-white flex-1"
                    data-testid="input-equipe"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowTrocarEquipe(true)}
                    disabled={user?.role === 'dono_assessoria'}
                    className="border-amber-500 text-amber-400 hover:bg-amber-500/10"
                    data-testid="btn-trocar-equipe"
                  >
                    Trocar Equipe
                  </Button>
                </div>
                {user?.role === 'dono_assessoria' && (
                  <p className="text-xs text-amber-400">
                    Donos de assessoria não podem trocar de equipe.
                  </p>
                )}
                {statusTrocaEquipe && !statusTrocaEquipe.pode_trocar && statusTrocaEquipe.motivo === 'periodo_espera' && (
                  <p className="text-xs text-slate-400">
                    Próxima troca disponível em: <span className="text-amber-400">{statusTrocaEquipe.proxima_troca}</span>
                    ({statusTrocaEquipe.dias_restantes} dias restantes)
                  </p>
                )}
              </div>

              {/* Modal Trocar Equipe */}
              {showTrocarEquipe && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
                  <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md mx-4 border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                      <Users className="w-5 h-5 text-amber-500" />
                      Trocar de Equipe
                    </h3>
                    
                    {statusTrocaEquipe && !statusTrocaEquipe.pode_trocar ? (
                      <div className="space-y-4">
                        <Alert className="border-amber-500/50 bg-amber-500/10">
                          <AlertDescription className="text-amber-200">
                            {statusTrocaEquipe.mensagem}
                            {statusTrocaEquipe.proxima_troca && (
                              <span className="block mt-2">
                                Próxima troca: <strong>{statusTrocaEquipe.proxima_troca}</strong>
                              </span>
                            )}
                          </AlertDescription>
                        </Alert>
                        <Button 
                          onClick={() => setShowTrocarEquipe(false)}
                          className="w-full"
                        >
                          Fechar
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div>
                          <Label className="text-slate-300 mb-2 block">Equipe Atual</Label>
                          <Badge variant="outline" className="text-lg px-4 py-2">
                            {equipe || 'INDIVIDUAL'}
                          </Badge>
                        </div>
                        
                        <div>
                          <Label className="text-slate-300 mb-2 block">Nova Equipe</Label>
                          <Select value={novaEquipe} onValueChange={setNovaEquipe}>
                            <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                              <SelectValue placeholder="Selecione uma equipe..." />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="INDIVIDUAL">INDIVIDUAL (Sem equipe)</SelectItem>
                              {equipesDisponiveis.map((eq) => (
                                <SelectItem key={eq.id} value={eq.nome}>
                                  {eq.nome}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <Alert className="border-slate-600 bg-slate-700/50">
                          <AlertDescription className="text-slate-300 text-sm">
                            Você só pode trocar de equipe a cada <strong>15 dias</strong>.
                          </AlertDescription>
                        </Alert>

                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            onClick={() => {
                              setShowTrocarEquipe(false);
                              setNovaEquipe('');
                            }}
                            className="flex-1"
                          >
                            Cancelar
                          </Button>
                          <Button 
                            onClick={handleTrocarEquipe}
                            disabled={savingEquipe || !novaEquipe}
                            className="flex-1 bg-amber-500 hover:bg-amber-600"
                          >
                            {savingEquipe ? (
                              <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Salvando...
                              </>
                            ) : (
                              'Confirmar Troca'
                            )}
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Redes Sociais */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="facebook" className="text-slate-300 flex items-center gap-2">
                    <Facebook className="w-4 h-4" />
                    Facebook
                  </Label>
                  <Input
                    id="facebook"
                    value={facebookUrl}
                    onChange={(e) => setFacebookUrl(e.target.value)}
                    placeholder="https://facebook.com/seu.perfil"
                    className="bg-slate-900 border-slate-600 text-white"
                    data-testid="input-facebook"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="instagram" className="text-slate-300 flex items-center gap-2">
                    <Instagram className="w-4 h-4" />
                    Instagram
                  </Label>
                  <Input
                    id="instagram"
                    value={instagramUrl}
                    onChange={(e) => setInstagramUrl(e.target.value)}
                    placeholder="https://instagram.com/seu.perfil"
                    className="bg-slate-900 border-slate-600 text-white"
                    data-testid="input-instagram"
                  />
                </div>
              </div>

              {/* Telefone */}
              <div className="space-y-2">
                <Label htmlFor="telefone" className="text-slate-300 flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  Telefone / WhatsApp
                </Label>
                <Input
                  id="telefone"
                  value={telefone}
                  onChange={(e) => setTelefone(e.target.value)}
                  placeholder="(11) 99999-9999"
                  className="bg-slate-900 border-slate-600 text-white"
                  data-testid="input-telefone"
                />
              </div>

              {/* Link WhatsApp para Dono de Assessoria */}
              {isDono && (
                <div className="space-y-2 p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
                  <Label htmlFor="whatsapp_link" className="text-green-400 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                    </svg>
                    Link de Mensagem WhatsApp (Assessoria)
                  </Label>
                  <Input
                    id="whatsapp_link"
                    value={whatsappLink}
                    onChange={(e) => setWhatsappLink(e.target.value)}
                    placeholder="https://wa.me/5511999999999"
                    className="bg-slate-900 border-green-500/50 text-white focus:border-green-400"
                    data-testid="input-whatsapp-link"
                  />
                  <p className="text-xs text-slate-400">
                    Cole o link do seu WhatsApp para que corredores interessados possam entrar em contato. 
                    Ex: https://wa.me/5511999999999
                  </p>
                </div>
              )}

              {/* Bio */}
              <div className="space-y-2">
                <Label htmlFor="bio" className="text-slate-300 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Bio do Atleta
                </Label>
                <Textarea
                  id="bio"
                  value={bio}
                  onChange={(e) => setBio(e.target.value.slice(0, 150))}
                  placeholder="Conte sua história em poucas palavras, como a bio do Instagram..."
                  rows={3}
                  maxLength={150}
                  className="bg-slate-900 border-slate-600 text-white resize-none"
                  data-testid="input-bio"
                />
                <p className={`text-xs ${bio.length >= 140 ? 'text-orange-400' : 'text-slate-500'}`}>{bio.length}/150 caracteres</p>
              </div>

              {/* Etnia */}
              <div className="space-y-2">
                <Label htmlFor="etnia" className="text-slate-300 flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Etnia
                </Label>
                <Select value={etnia} onValueChange={setEtnia}>
                  <SelectTrigger className="bg-slate-900 border-slate-600 text-white" data-testid="select-etnia">
                    <SelectValue placeholder="Selecione sua etnia" />
                  </SelectTrigger>
                  <SelectContent>
                    {ETNIAS.map((e) => (
                      <SelectItem key={e} value={e}>{e}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Apelido */}
              <div className="space-y-2">
                <Label htmlFor="apelido" className="text-slate-300 flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Apelido
                </Label>
                <Input
                  id="apelido"
                  value={apelido}
                  onChange={(e) => setApelido(e.target.value)}
                  placeholder="Como você quer ser chamado"
                  className="bg-slate-900 border-slate-600 text-white"
                  data-testid="input-apelido"
                />
              </div>

              {/* Seção Alterar Senha */}
              <div className="pt-4 border-t border-slate-700">
                <div 
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setShowAlterarSenha(!showAlterarSenha)}
                  data-testid="toggle-alterar-senha"
                >
                  <Label className="text-slate-300 flex items-center gap-2 cursor-pointer">
                    <Lock className="w-4 h-4" />
                    Alterar Senha
                  </Label>
                  <span className="text-xs text-slate-500">
                    {showAlterarSenha ? 'Fechar ▲' : 'Expandir ▼'}
                  </span>
                </div>
                
                {showAlterarSenha && (
                  <div className="mt-4 space-y-4 p-4 bg-slate-900/50 rounded-lg">
                    <div className="space-y-2">
                      <Label className="text-slate-400 text-sm">Senha Atual</Label>
                      <div className="relative">
                        <Input
                          type={showSenhaAtual ? "text" : "password"}
                          value={senhaAtual}
                          onChange={(e) => setSenhaAtual(e.target.value)}
                          placeholder="Digite sua senha atual"
                          className="bg-slate-900 border-slate-600 text-white pr-10"
                          data-testid="input-senha-atual"
                        />
                        <button
                          type="button"
                          onClick={() => setShowSenhaAtual(!showSenhaAtual)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                        >
                          {showSenhaAtual ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label className="text-slate-400 text-sm">Nova Senha</Label>
                      <div className="relative">
                        <Input
                          type={showNovaSenha ? "text" : "password"}
                          value={novaSenha}
                          onChange={(e) => setNovaSenha(e.target.value)}
                          placeholder="Mínimo 6 caracteres"
                          className="bg-slate-900 border-slate-600 text-white pr-10"
                          data-testid="input-nova-senha"
                        />
                        <button
                          type="button"
                          onClick={() => setShowNovaSenha(!showNovaSenha)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                        >
                          {showNovaSenha ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label className="text-slate-400 text-sm">Confirmar Nova Senha</Label>
                      <Input
                        type="password"
                        value={confirmarSenha}
                        onChange={(e) => setConfirmarSenha(e.target.value)}
                        placeholder="Repita a nova senha"
                        className="bg-slate-900 border-slate-600 text-white"
                        data-testid="input-confirmar-senha"
                      />
                    </div>
                    
                    <Button
                      onClick={handleAlterarSenha}
                      disabled={savingSenha}
                      className="w-full bg-amber-600 hover:bg-amber-500"
                      data-testid="btn-alterar-senha"
                    >
                      {savingSenha ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Alterando...
                        </>
                      ) : (
                        <>
                          <Lock className="w-4 h-4 mr-2" />
                          Alterar Senha
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>

              {/* Botão Salvar */}
              <div className="flex justify-end pt-4 border-t border-slate-700">
                <Button
                  onClick={handleSave}
                  disabled={saving}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-8"
                  data-testid="btn-salvar"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Salvando...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Salvar Alterações
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Informação adicional */}
        <Card className="mt-6 bg-slate-800/30 border-slate-700/50">
          <CardContent className="pt-6">
            <p className="text-sm text-slate-400 text-center">
              <Mail className="w-4 h-4 inline mr-2" />
              Para alterar seu email ou categoria, entre em contato com o suporte.
            </p>
          </CardContent>
        </Card>
        
        {/* Integração Strava */}
        <div className="mt-6">
          <StravaIntegration token={token} />
        </div>
        
        {/* Indicar Amigos */}
        <div className="mt-6">
          <IndicarAmigos />
        </div>
      </div>
      
      {/* Modal de Crop de Imagem */}
      <ImageCropModal
        isOpen={showCropModal}
        onClose={() => setShowCropModal(false)}
        imageSrc={imageToCrop}
        onCropComplete={handleCroppedPhoto}
        aspectRatio={1}
      />
    </div>
  );
};

export default PerfilAtletaPage;
