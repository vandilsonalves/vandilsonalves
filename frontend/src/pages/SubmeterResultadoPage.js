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
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SubmeterResultadoPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    nome_competicao: '',
    colocacao: '',
    cidade_competicao: '',
    estado_competicao: '',
    data_competicao: '',
    link_resultado: '',
    tempo: '',
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

      setSuccess(true);
      setTimeout(() => navigate('/'), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao submeter resultado');
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
            <CardTitle className="text-3xl font-bold text-emerald-600">
              Submeter Resultado
            </CardTitle>
            <p className="text-slate-600 mt-2">
              Preencha os dados da sua corrida (Prazo: 6 dias após o evento)
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Alert className="bg-amber-50 border-amber-200">
                <AlertDescription>
                  <strong>Atenção:</strong> Você tem 6 dias úteis após a competição para enviar o resultado.
                  <br />
                  <strong>Colocações válidas:</strong> {user.categoria === 'pcd' || user.categoria === 'cadeirante' 
                    ? '1º a 3º lugar (PCD/Cadeirante)' 
                    : '1º a 10º lugar (Normal)'}
                </AlertDescription>
              </Alert>

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

                <div>
                  <Label>Sua Colocação *</Label>
                  <Input
                    type="number"
                    min="1"
                    max={user.categoria === 'pcd' || user.categoria === 'cadeirante' ? 3 : 10}
                    value={formData.colocacao}
                    onChange={(e) => handleChange('colocacao', e.target.value)}
                    placeholder={user.categoria === 'pcd' || user.categoria === 'cadeirante' ? "1 a 3" : "1 a 10"}
                    required
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    {user.categoria === 'pcd' || user.categoria === 'cadeirante' 
                      ? '⚠️ PCD/Cadeirante: Apenas 1º a 3º lugar pontuam e podem ser enviados'
                      : '⚠️ Normal: Apenas 1º a 10º lugar pontuam e podem ser enviados'}
                  </p>
                </div>

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
                  <Label>Foto do Pódio *</Label>
                  <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center">
                    {fotoPodio ? (
                      <div>
                        <p className="text-sm text-emerald-600 mb-2">✓ {fotoPodio.name}</p>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => setFotoPodio(null)}
                        >
                          Remover
                        </Button>
                      </div>
                    ) : (
                      <div>
                        <Upload className="w-12 h-12 mx-auto mb-2 text-slate-400" />
                        <p className="text-sm text-slate-600 mb-2">
                          Clique para selecionar a foto do pódio
                        </p>
                        <Input
                          type="file"
                          accept="image/*"
                          onChange={(e) => setFotoPodio(e.target.files[0])}
                          required
                        />
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
