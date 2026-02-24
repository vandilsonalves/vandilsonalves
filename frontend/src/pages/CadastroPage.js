import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { UserPlus } from 'lucide-react';

const CadastroPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    password: '',
    equipe: '',
    cidade: '',
    estado: '',
    genero: '',
    categoria: '',
    data_nascimento: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(formData);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao cadastrar');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950 dark:to-green-950 py-8 px-4">
      <div className="container mx-auto max-w-2xl">
        <Card className="shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
              Cadastro de Atleta
            </CardTitle>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              Preencha seus dados para começar a pontuar
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Nome Completo *</Label>
                  <Input
                    value={formData.nome}
                    onChange={(e) => handleChange('nome', e.target.value)}
                    placeholder="João Silva"
                    required
                  />
                </div>

                <div>
                  <Label>Email *</Label>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    placeholder="seu@email.com"
                    required
                  />
                </div>

                <div>
                  <Label>Senha *</Label>
                  <Input
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    placeholder="Mínimo 6 caracteres"
                    minLength={6}
                    required
                  />
                </div>

                <div>
                  <Label>Equipe</Label>
                  <Input
                    value={formData.equipe}
                    onChange={(e) => handleChange('equipe', e.target.value)}
                    placeholder="Sem equipe"
                  />
                </div>

                <div>
                  <Label>Cidade *</Label>
                  <Input
                    value={formData.cidade}
                    onChange={(e) => handleChange('cidade', e.target.value)}
                    placeholder="São Paulo"
                    required
                  />
                </div>

                <div>
                  <Label>Estado (UF) *</Label>
                  <Input
                    value={formData.estado}
                    onChange={(e) => handleChange('estado', e.target.value.toUpperCase())}
                    placeholder="SP"
                    maxLength={2}
                    required
                  />
                </div>

                <div>
                  <Label>Gênero *</Label>
                  <Select value={formData.genero} onValueChange={(value) => handleChange('genero', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="M">Masculino</SelectItem>
                      <SelectItem value="F">Feminino</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Categoria *</Label>
                  <Select value={formData.categoria} onValueChange={(value) => handleChange('categoria', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="pcd">PCD</SelectItem>
                      <SelectItem value="cadeirante">Cadeirante</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Data de Nascimento *</Label>
                  <Input
                    type="date"
                    value={formData.data_nascimento}
                    onChange={(e) => handleChange('data_nascimento', e.target.value)}
                    required
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-emerald-600 hover:bg-emerald-700"
                disabled={loading}
              >
                <UserPlus className="w-4 h-4 mr-2" />
                {loading ? 'Cadastrando...' : 'Cadastrar'}
              </Button>

              <div className="text-center mt-4">
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Já tem conta?{' '}
                  <Link to="/login" className="text-emerald-600 hover:underline font-semibold">
                    Faça login
                  </Link>
                </p>
              </div>

              <div className="text-center mt-2">
                <Link to="/" className="text-sm text-slate-500 hover:underline">
                  ← Voltar para o ranking
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CadastroPage;