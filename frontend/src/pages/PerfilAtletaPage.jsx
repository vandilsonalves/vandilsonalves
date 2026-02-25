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
  Share2, Award, ExternalLink, Download, Calendar
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

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

  const ETNIAS = ['Branco', 'Negro', 'Indígena', 'Pardo', 'Amarelo'];

  useEffect(() => {
    if (!user || !token) {
      navigate('/login');
      return;
    }
    fetchAtletaData();
    fetchConquistas();
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
        total_corridas: data.total_corridas || 0
      });
      
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

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    
    try {
      await axios.patch(`${API}/atletas/perfil`, {
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
      }, {
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
    
    setUploadingPhoto(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('foto', file);
      
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

              {/* Conquistas */}
              {conquistas.length > 0 && (
                <div className="pt-4 border-t border-slate-700">
                  <p className="text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
                    <Award className="w-4 h-4 text-amber-400" />
                    Conquistas
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {conquistas.map((c) => (
                      <Badge key={c.codigo} variant="outline" className="border-amber-500/30 text-amber-300">
                        {c.icone} {c.nome}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

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
                <Input
                  id="equipe"
                  value={equipe}
                  onChange={(e) => setEquipe(e.target.value)}
                  placeholder="Ex: Runners BR, Team Run, etc."
                  className="bg-slate-900 border-slate-600 text-white"
                  data-testid="input-equipe"
                />
              </div>

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

              {/* Bio */}
              <div className="space-y-2">
                <Label htmlFor="bio" className="text-slate-300 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Sobre você
                </Label>
                <Textarea
                  id="bio"
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Conte um pouco sobre sua história no esporte, conquistas, motivações..."
                  rows={4}
                  className="bg-slate-900 border-slate-600 text-white resize-none"
                  data-testid="input-bio"
                />
                <p className="text-xs text-slate-500">{bio.length}/500 caracteres</p>
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
      </div>
    </div>
  );
};

export default PerfilAtletaPage;
