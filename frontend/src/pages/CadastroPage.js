import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { UserPlus, Search } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Lista de estados brasileiros
const ESTADOS_BR = [
  { uf: 'AC', nome: 'Acre' },
  { uf: 'AL', nome: 'Alagoas' },
  { uf: 'AP', nome: 'Amapá' },
  { uf: 'AM', nome: 'Amazonas' },
  { uf: 'BA', nome: 'Bahia' },
  { uf: 'CE', nome: 'Ceará' },
  { uf: 'DF', nome: 'Distrito Federal' },
  { uf: 'ES', nome: 'Espírito Santo' },
  { uf: 'GO', nome: 'Goiás' },
  { uf: 'MA', nome: 'Maranhão' },
  { uf: 'MT', nome: 'Mato Grosso' },
  { uf: 'MS', nome: 'Mato Grosso do Sul' },
  { uf: 'MG', nome: 'Minas Gerais' },
  { uf: 'PA', nome: 'Pará' },
  { uf: 'PB', nome: 'Paraíba' },
  { uf: 'PR', nome: 'Paraná' },
  { uf: 'PE', nome: 'Pernambuco' },
  { uf: 'PI', nome: 'Piauí' },
  { uf: 'RJ', nome: 'Rio de Janeiro' },
  { uf: 'RN', nome: 'Rio Grande do Norte' },
  { uf: 'RS', nome: 'Rio Grande do Sul' },
  { uf: 'RO', nome: 'Rondônia' },
  { uf: 'RR', nome: 'Roraima' },
  { uf: 'SC', nome: 'Santa Catarina' },
  { uf: 'SP', nome: 'São Paulo' },
  { uf: 'SE', nome: 'Sergipe' },
  { uf: 'TO', nome: 'Tocantins' }
];

const ETNIAS = ['Branco', 'Negro', 'Pardo', 'Indígena', 'Amarelo', 'Mulato'];

const CadastroPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Listas dinâmicas
  const [cidades, setCidades] = useState([]);
  const [loadingCidades, setLoadingCidades] = useState(false);
  const [equipesCadastradas, setEquipesCadastradas] = useState([]);
  const [equipeSearchTerm, setEquipeSearchTerm] = useState('');
  const [showEquipeDropdown, setShowEquipeDropdown] = useState(false);
  
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    password: '',
    equipe: '',
    cidade: '',
    estado: '',
    genero: '',
    categoria: '',
    data_nascimento: '',
    etnia: '',
    apelido: '',
    modalidade_usuario: 'profissional_amador'
  });

  // Buscar equipes cadastradas ao carregar a página
  useEffect(() => {
    const fetchEquipes = async () => {
      try {
        const response = await axios.get(`${API}/ranking/equipes`);
        setEquipesCadastradas(response.data || []);
      } catch (err) {
        console.error('Erro ao buscar equipes:', err);
      }
    };
    fetchEquipes();
  }, []);

  // Buscar cidades quando o estado mudar
  useEffect(() => {
    const fetchCidades = async () => {
      if (!formData.estado || formData.estado.length !== 2) {
        setCidades([]);
        return;
      }
      
      setLoadingCidades(true);
      try {
        // API do IBGE para buscar cidades por UF
        const response = await axios.get(
          `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${formData.estado}/municipios`
        );
        const cidadesOrdenadas = response.data
          .map(c => c.nome)
          .sort((a, b) => a.localeCompare(b));
        setCidades(cidadesOrdenadas);
        
        // Limpar cidade se mudou de estado
        if (formData.cidade && !cidadesOrdenadas.includes(formData.cidade)) {
          setFormData(prev => ({ ...prev, cidade: '' }));
        }
      } catch (err) {
        console.error('Erro ao buscar cidades:', err);
        setCidades([]);
      } finally {
        setLoadingCidades(false);
      }
    };
    
    fetchCidades();
  }, [formData.estado]);
  
  // Verificar se pode usar modalidade Povão (PCD e Cadeirante não podem)
  const podeSelecionarPovao = formData.categoria === 'normal' || formData.categoria === '';

  // Filtrar equipes pela busca
  const equipesFiltradas = equipesCadastradas.filter(equipe => 
    equipe.toLowerCase().includes(equipeSearchTerm.toLowerCase())
  );

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
    setFormData(prev => {
      const newData = { ...prev, [field]: value };
      
      // Se categoria mudou para PCD ou Cadeirante, forçar modalidade profissional
      if (field === 'categoria' && (value === 'pcd' || value === 'cadeirante')) {
        newData.modalidade_usuario = 'profissional_amador';
      }
      
      return newData;
    });
  };

  const handleEquipeSelect = (equipe) => {
    setFormData(prev => ({ ...prev, equipe }));
    setEquipeSearchTerm(equipe);
    setShowEquipeDropdown(false);
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

                {/* Campo Equipe/Assessoria com autocomplete */}
                <div className="relative">
                  <Label>Equipe / Assessoria</Label>
                  <div className="relative">
                    <Input
                      value={equipeSearchTerm}
                      onChange={(e) => {
                        setEquipeSearchTerm(e.target.value);
                        setShowEquipeDropdown(true);
                        handleChange('equipe', e.target.value);
                      }}
                      onFocus={() => setShowEquipeDropdown(true)}
                      placeholder="Digite ou selecione..."
                      data-testid="input-equipe"
                    />
                    <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  </div>
                  
                  {/* Dropdown de equipes */}
                  {showEquipeDropdown && (
                    <div className="absolute z-50 w-full mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                      <div
                        className="px-3 py-2 hover:bg-emerald-50 dark:hover:bg-emerald-900/30 cursor-pointer border-b border-slate-100 dark:border-slate-700"
                        onClick={() => handleEquipeSelect('Sem equipe')}
                      >
                        <span className="text-slate-500">Sem equipe</span>
                      </div>
                      {equipesFiltradas.length > 0 ? (
                        equipesFiltradas.slice(0, 10).map((equipe, idx) => (
                          <div
                            key={idx}
                            className="px-3 py-2 hover:bg-emerald-50 dark:hover:bg-emerald-900/30 cursor-pointer"
                            onClick={() => handleEquipeSelect(equipe)}
                          >
                            {equipe}
                          </div>
                        ))
                      ) : equipeSearchTerm.length > 0 ? (
                        <div className="px-3 py-2 text-slate-500 text-sm">
                          Equipe não encontrada. Será cadastrada como nova.
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>

                {/* Estado (UF) */}
                <div>
                  <Label>Estado (UF) *</Label>
                  <Select 
                    value={formData.estado} 
                    onValueChange={(value) => handleChange('estado', value)}
                  >
                    <SelectTrigger data-testid="select-estado">
                      <SelectValue placeholder="Selecione o estado" />
                    </SelectTrigger>
                    <SelectContent>
                      {ESTADOS_BR.map((estado) => (
                        <SelectItem key={estado.uf} value={estado.uf}>
                          {estado.uf} - {estado.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Cidade */}
                <div>
                  <Label>Cidade *</Label>
                  {formData.estado ? (
                    <Select 
                      value={formData.cidade} 
                      onValueChange={(value) => handleChange('cidade', value)}
                      disabled={loadingCidades || cidades.length === 0}
                    >
                      <SelectTrigger data-testid="select-cidade">
                        <SelectValue placeholder={loadingCidades ? "Carregando..." : "Selecione a cidade"} />
                      </SelectTrigger>
                      <SelectContent className="max-h-[200px]">
                        {cidades.map((cidade) => (
                          <SelectItem key={cidade} value={cidade}>
                            {cidade}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      disabled
                      placeholder="Selecione o estado primeiro"
                      className="bg-slate-100"
                    />
                  )}
                </div>

                <div>
                  <Label>Gênero *</Label>
                  <Select value={formData.genero} onValueChange={(value) => handleChange('genero', value)}>
                    <SelectTrigger data-testid="select-genero">
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
                    <SelectTrigger data-testid="select-categoria">
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
                    data-testid="input-data-nascimento"
                  />
                </div>

                <div>
                  <Label>Etnia *</Label>
                  <Select value={formData.etnia} onValueChange={(value) => handleChange('etnia', value)}>
                    <SelectTrigger data-testid="select-etnia">
                      <SelectValue placeholder="Selecione sua etnia" />
                    </SelectTrigger>
                    <SelectContent>
                      {ETNIAS.map((etnia) => (
                        <SelectItem key={etnia} value={etnia}>{etnia}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Apelido</Label>
                  <Input
                    value={formData.apelido}
                    onChange={(e) => handleChange('apelido', e.target.value)}
                    placeholder="Como você quer ser chamado"
                    data-testid="input-apelido"
                  />
                </div>

                {/* Seleção de Modalidade */}
                <div className="md:col-span-2">
                  <Label className="text-base font-semibold">Modalidade de Participação *</Label>
                  <p className="text-sm text-slate-500 mb-3">
                    Escolha como você deseja competir no Ranking Run Pró
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Opção Profissional/Amador */}
                    <div 
                      className={`relative border-2 rounded-xl p-4 cursor-pointer transition-all ${
                        formData.modalidade_usuario === 'profissional_amador' 
                          ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30' 
                          : 'border-slate-200 hover:border-emerald-300'
                      }`}
                      onClick={() => handleChange('modalidade_usuario', 'profissional_amador')}
                      data-testid="modalidade-profissional"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5 ${
                          formData.modalidade_usuario === 'profissional_amador' 
                            ? 'border-emerald-500 bg-emerald-500' 
                            : 'border-slate-300'
                        }`}>
                          {formData.modalidade_usuario === 'profissional_amador' && (
                            <div className="w-2 h-2 rounded-full bg-white" />
                          )}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-slate-800 dark:text-slate-200">
                            Atleta Profissional / Amador
                          </h4>
                          <p className="text-sm text-slate-500 mt-1">
                            Pontuação baseada em colocação (1º a 10º lugar)
                          </p>
                          <div className="mt-2 text-xs text-slate-400">
                            <span className="inline-block bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded mr-1">1º = 10pts</span>
                            <span className="inline-block bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded mr-1">2º = 9pts</span>
                            <span className="inline-block bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">...</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Opção Povão - Pace Livre */}
                    <div 
                      className={`relative border-2 rounded-xl p-4 transition-all ${
                        !podeSelecionarPovao 
                          ? 'opacity-50 cursor-not-allowed border-slate-200' 
                          : formData.modalidade_usuario === 'povao_pace_livre'
                            ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/30 cursor-pointer'
                            : 'border-slate-200 hover:border-purple-300 cursor-pointer'
                      }`}
                      onClick={() => podeSelecionarPovao && handleChange('modalidade_usuario', 'povao_pace_livre')}
                      data-testid="modalidade-povao"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5 ${
                          formData.modalidade_usuario === 'povao_pace_livre' 
                            ? 'border-purple-500 bg-purple-500' 
                            : 'border-slate-300'
                        }`}>
                          {formData.modalidade_usuario === 'povao_pace_livre' && (
                            <div className="w-2 h-2 rounded-full bg-white" />
                          )}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-slate-800 dark:text-slate-200">
                            Ranking do Povão - Pace Livre
                          </h4>
                          <p className="text-sm text-slate-500 mt-1">
                            Pontuação baseada apenas na distância percorrida
                          </p>
                          <div className="mt-2 text-xs text-slate-400">
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded mr-1">5-9km = 5pts</span>
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded mr-1">10-20km = 7pts</span>
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded">21km+ = 9pts</span>
                          </div>
                          {!podeSelecionarPovao && (
                            <p className="text-xs text-red-500 mt-2">
                              Não disponível para PCD/Cadeirante
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
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
      
      {/* Click outside to close dropdown */}
      {showEquipeDropdown && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowEquipeDropdown(false)}
        />
      )}
    </div>
  );
};

export default CadastroPage;
