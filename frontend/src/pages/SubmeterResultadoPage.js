import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, CheckCircle, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SubmeterResultadoPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  
  // Verificar se usuário é da modalidade Povão
  const isPovao = user?.modalidade_usuario === 'povao_pace_livre';
  
  const [formData, setFormData] = useState({
    nome_competicao: '',
    colocacao: isPovao ? '0' : '',
    cidade_competicao: '',
    estado_competicao: '',
    data_competicao: '',
    link_resultado: '',
    tempo: isPovao ? '00:00:00' : '',
    distancia: ''
  });
  
  const [fotoPodio, setFotoPodio] = useState(null);

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="mb-4">Você precisa estar logado para submeter resultados.</p>
            <Link to="/login">
              <Button>Fazer Login</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formDataToSend = new FormData();
      Object.keys(formData).forEach(key => {
        formDataToSend.append(key, formData[key]);
      });
      
      if (fotoPodio) {
        formDataToSend.append('foto_podio', fotoPodio);
      }

      await axios.post(`${API}/resultados/submeter`, formDataToSend, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success('Ação Concluída', { description: 'Resultado submetido com sucesso!' });
      setSuccess(true);
      setTimeout(() => navigate('/'), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao submeter resultado');
      toast.error('Erro', { description: err.response?.data?.detail || 'Erro ao submeter resultado' });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-50 flex items-center justify-center p-4">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <CheckCircle className="w-16 h-16 mx-auto mb-4 text-emerald-600" />
            <h2 className="text-2xl font-bold text-emerald-600 mb-2">
              Resultado Enviado!
            </h2>
            <p className="text-slate-600 mb-4">
              Seu resultado foi submetido com sucesso e está aguardando aprovação do administrador.
            </p>
            <Button onClick={() => navigate('/')}>
              Voltar ao Ranking
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-50 py-8 px-4">
      <div className="container mx-auto max-w-3xl">
        <Button
          onClick={() => navigate('/')}
          variant="outline"
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Voltar
        </Button>

        <Card className="shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className={`text-3xl font-bold ${isPovao ? 'text-purple-600' : 'text-emerald-600'}`}>
              Submeter Resultado
            </CardTitle>
            <p className="text-slate-600 mt-2">
              {isPovao 
                ? 'Ranking do Povão - Pace Livre (Pontuação por distância)'
                : 'Preencha os dados da sua corrida (Prazo: 6 dias após o evento)'
              }
            </p>
            {isPovao && (
              <div className="mt-3 inline-flex items-center px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
                <span className="font-semibold">Modalidade: Pace Livre</span>
              </div>
            )}
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Alerta específico para cada modalidade */}
              {isPovao ? (
                <Alert className="bg-purple-50 border-purple-200">
                  <AlertDescription>
                    <strong>Ranking do Povão - Pace Livre</strong><br />
                    Você compete pela distância percorrida, não pela colocação!<br />
                    <strong>Pontuação:</strong> 5-9km = 5pts | 10-20km = 7pts | 21km+ = 9pts
                  </AlertDescription>
                </Alert>
              ) : (
                <Alert className="bg-amber-50 border-amber-200">
                  <AlertDescription>
                    <strong>Atenção:</strong> Você tem 6 dias úteis após a competição para enviar o resultado.
                    <br />
                    <strong>Colocações válidas:</strong> {user?.categoria === 'pcd' || user?.categoria === 'cadeirante' 
                      ? '1º a 3º lugar (PCD/Cadeirante)' 
                      : '1º a 10º lugar (Normal)'}
                  </AlertDescription>
                </Alert>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <Label>Nome da Competição *</Label>
                  <Input
                    value={formData.nome_competicao}
                    onChange={(e) => handleChange('nome_competicao', e.target.value)}
                    placeholder="Ex: Corrida de São Silvestre"
                    required
                  />
                </div>

                {/* Campo de Colocação - oculto para Povão */}
                {!isPovao && (
                  <div>
                    <Label>Sua Colocação *</Label>
                    <Input
                      type="number"
                      min="1"
                      max={user?.categoria === 'pcd' || user?.categoria === 'cadeirante' ? 3 : 10}
                      value={formData.colocacao}
                      onChange={(e) => handleChange('colocacao', e.target.value)}
                      placeholder={user?.categoria === 'pcd' || user?.categoria === 'cadeirante' ? "1 a 3" : "1 a 10"}
                      required
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      {user?.categoria === 'pcd' || user?.categoria === 'cadeirante' 
                        ? 'PCD/Cadeirante: Apenas 1º a 3º lugar pontuam'
                        : 'Normal: Apenas 1º a 10º lugar pontuam'}
                    </p>
                  </div>
                )}

                <div>
                  <Label>Distância *</Label>
                  <Select value={formData.distancia} onValueChange={(value) => handleChange('distancia', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5KM">5 KM</SelectItem>
                      <SelectItem value="10KM">10 KM</SelectItem>
                      <SelectItem value="21KM">21 KM (Meia Maratona)</SelectItem>
                      <SelectItem value="42KM">42 KM (Maratona)</SelectItem>
                      <SelectItem value="OUTRA">Outra</SelectItem>
                    </SelectContent>
                  </Select>
                  {isPovao && (
                    <p className="text-xs text-purple-600 mt-1">
                      {formData.distancia === '5KM' && '5 pontos'}
                      {formData.distancia === '10KM' && '7 pontos'}
                      {formData.distancia === '21KM' && '9 pontos'}
                      {formData.distancia === '42KM' && '9 pontos'}
                      {formData.distancia === 'OUTRA' && 'Pontuação depende da distância'}
                    </p>
                  )}
                </div>

                <div>
                  <Label>Cidade da Competição *</Label>
                  <Input
                    value={formData.cidade_competicao}
                    onChange={(e) => handleChange('cidade_competicao', e.target.value)}
                    placeholder="Ex: São Paulo"
                    required
                  />
                </div>

                <div>
                  <Label>Estado (UF) *</Label>
                  <Input
                    value={formData.estado_competicao}
                    onChange={(e) => handleChange('estado_competicao', e.target.value.toUpperCase())}
                    placeholder="SP"
                    maxLength={2}
                    required
                  />
                </div>

                <div>
                  <Label>Data da Competição *</Label>
                  <Input
                    type="date"
                    value={formData.data_competicao}
                    onChange={(e) => handleChange('data_competicao', e.target.value)}
                    required
                  />
                </div>

                {/* Campo de Tempo - oculto para Povão */}
                {!isPovao && (
                  <div>
                    <Label>Seu Tempo (HH:MM:SS) *</Label>
                    <Input
                      type="time"
                      step="1"
                      value={formData.tempo}
                      onChange={(e) => handleChange('tempo', e.target.value)}
                      required
                    />
                  </div>
                )}

                <div className="md:col-span-2">
                  <Label>Link do Resultado (Site de Cronometragem) *</Label>
                  <Input
                    type="url"
                    value={formData.link_resultado}
                    onChange={(e) => handleChange('link_resultado', e.target.value)}
                    placeholder="https://..."
                    required
                  />
                </div>

                <div className="md:col-span-2">
                  <Label className="flex items-center gap-2 mb-2">
                    <Upload className="w-4 h-4" />
                    Foto do Pódio ou sua no Evento (opcional)
                  </Label>
                  <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-emerald-400 transition-colors">
                    {fotoPodio ? (
                      <div>
                        <p className="text-sm text-emerald-600 mb-2">✓ {fotoPodio.name}</p>
                        <div className="flex gap-2 justify-center">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => setFotoPodio(null)}
                          >
                            Remover
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <Upload className="w-12 h-12 mx-auto mb-3 text-slate-400" />
                        <label className="cursor-pointer">
                          <Button
                            type="button"
                            variant="outline"
                            className="mb-2 border-emerald-500 text-emerald-600 hover:bg-emerald-50"
                            onClick={() => document.getElementById('foto-podio-input').click()}
                          >
                            Adicionar uma Foto do Pódio ou sua no Evento
                          </Button>
                          <Input
                            id="foto-podio-input"
                            type="file"
                            accept="image/*"
                            onChange={(e) => setFotoPodio(e.target.files[0])}
                            className="hidden"
                          />
                        </label>
                        <p className="text-xs text-slate-500">
                          Formatos aceitos: JPG, PNG, GIF (máx. 5MB)
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-emerald-600 hover:bg-emerald-700"
                disabled={loading}
                size="lg"
              >
                {loading ? 'Enviando...' : 'Submeter Resultado'}
              </Button>

              <p className="text-xs text-slate-500 text-center">
                Art.20-22: Resultados serão validados pela administração antes de contabilizar pontos.
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SubmeterResultadoPage;
