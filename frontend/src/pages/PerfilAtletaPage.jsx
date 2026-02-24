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
import { 
  ArrowLeft, Save, User, Mail, MapPin, Users, Trophy, 
  Facebook, Instagram, Phone, FileText, Camera, Check, Loader2
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PerfilAtletaPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  // Dados do atleta
  const [atleta, setAtleta] = useState(null);
  
  // Campos editáveis
  const [equipe, setEquipe] = useState('');
  const [facebookUrl, setFacebookUrl] = useState('');
  const [instagramUrl, setInstagramUrl] = useState('');
  const [telefone, setTelefone] = useState('');
  const [bio, setBio] = useState('');

  useEffect(() => {
    if (!user || !token) {
      navigate('/login');
      return;
    }
    fetchAtletaData();
  }, [user, token]);

  const fetchAtletaData = async () => {
    setLoading(true);
    try {
      // Buscar perfil completo do atleta logado
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
        pontos_carreira: data.pontos_carreira || 0,
        total_corridas: data.total_corridas || 0
      });
      
      // Preencher campos editáveis
      setEquipe(data.equipe || '');
      setFacebookUrl(data.facebook_url || '');
      setInstagramUrl(data.instagram_url || '');
      setTelefone(data.telefone || '');
      setBio(data.bio || '');
      
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
      setError('Erro ao carregar dados do perfil');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    
    try {
      await axios.patch(`${API}/atletas/perfil`, {
        equipe,
        facebook_url: facebookUrl,
        instagram_url: instagramUrl,
        telefone,
        bio
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSuccess('Perfil atualizado com sucesso!');
      
      // Atualizar dados locais
      setAtleta(prev => ({ ...prev, equipe }));
      
      // Limpar mensagem após 3 segundos
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (error) {
      console.error('Erro ao salvar:', error);
      setError(error.response?.data?.detail || 'Erro ao salvar alterações');
    } finally {
      setSaving(false);
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Validar tipo
    if (!file.type.startsWith('image/')) {
      setError('Por favor, selecione uma imagem válida');
      return;
    }
    
    // Validar tamanho (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('A imagem deve ter no máximo 5MB');
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
      
      // Atualizar foto local
      setAtleta(prev => ({ ...prev, foto_url: response.data.foto_url }));
      setSuccess('Foto atualizada com sucesso!');
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (error) {
      console.error('Erro ao enviar foto:', error);
      setError('Erro ao enviar foto');
    } finally {
      setUploadingPhoto(false);
    }
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
      <div className="container mx-auto max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1" data-testid="perfil-title">
              Meu Perfil
            </h1>
            <p className="text-slate-400">Gerencie suas informações de atleta</p>
          </div>
          <Button onClick={() => navigate('/')} variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </Button>
        </div>

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
                  <AvatarImage src={atleta?.foto_url} alt={atleta?.nome} />
                  <AvatarFallback className="bg-emerald-600 text-white text-3xl">
                    {atleta?.nome?.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                
                {/* Botão de upload de foto */}
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
              {/* Informações não editáveis */}
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
              Para alterar seu email ou outras informações pessoais, entre em contato com o suporte.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PerfilAtletaPage;
