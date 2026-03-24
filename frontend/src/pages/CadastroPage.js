import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { UserPlus, Search, ScrollText, CheckCircle2, HelpCircle, Building2, Upload, FileImage, Users, Gift } from 'lucide-react';
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
  const [searchParams] = useSearchParams();
  const { register } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Estado para código de indicação
  const [codigoIndicacaoValido, setCodigoIndicacaoValido] = useState(null);
  const [nomeIndicador, setNomeIndicador] = useState('');
  
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
    modalidade_usuario: 'profissional_amador',
    codigo_indicacao: ''
  });

  // Estados do Termo de Aceite
  const [showTermoModal, setShowTermoModal] = useState(false);
  const [aceitouTermo, setAceitouTermo] = useState(false);
  const [scrolledToBottom, setScrolledToBottom] = useState(false);
  const termoRef = useRef(null);

  // Estados para Dono de Assessoria (3ª Tarefa)
  const [isDonoAssessoria, setIsDonoAssessoria] = useState(null); // null = não respondeu, true = SIM, false = NÃO
  const [assessoriaData, setAssessoriaData] = useState({
    nome_assessoria: '',
    estado_assessoria: '',
    cidade_assessoria: '',
    foto_assessoria: null,
    mensagem_bio: ''
  });
  const [cidadesAssessoria, setCidadesAssessoria] = useState([]);
  const [loadingCidadesAssessoria, setLoadingCidadesAssessoria] = useState(false);

  // Capturar código de indicação da URL
  useEffect(() => {
    const refCode = searchParams.get('ref');
    if (refCode) {
      setFormData(prev => ({ ...prev, codigo_indicacao: refCode.toUpperCase() }));
      verificarCodigoIndicacao(refCode.toUpperCase());
    }
  }, [searchParams]);

  // Verificar código de indicação
  const verificarCodigoIndicacao = async (codigo) => {
    if (!codigo || codigo.length < 5) {
      setCodigoIndicacaoValido(null);
      setNomeIndicador('');
      return;
    }
    
    try {
      const response = await axios.get(`${API}/indicacao/verificar-codigo/${codigo}`);
      if (response.data.valido) {
        setCodigoIndicacaoValido(true);
        setNomeIndicador(response.data.indicador?.nome || '');
      } else {
        setCodigoIndicacaoValido(false);
        setNomeIndicador('');
      }
    } catch (err) {
      setCodigoIndicacaoValido(false);
      setNomeIndicador('');
    }
  };

  // Buscar equipes cadastradas ao carregar a página
  useEffect(() => {
    const fetchEquipes = async () => {
      try {
        const response = await axios.get(`${API}/assessorias/lista`);
        // Formato: [{nome, cidade, estado}]
        setEquipesCadastradas(response.data || []);
      } catch (err) {
        console.error('Erro ao buscar equipes:', err);
        // Fallback para endpoint antigo
        try {
          const fallback = await axios.get(`${API}/ranking/equipes`);
          setEquipesCadastradas((fallback.data || []).map(nome => ({ nome, cidade: '', estado: '' })));
        } catch (e) {
          console.error('Fallback também falhou:', e);
        }
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

  // Buscar cidades da assessoria quando o estado da assessoria mudar
  useEffect(() => {
    const fetchCidadesAssessoria = async () => {
      if (!assessoriaData.estado_assessoria || assessoriaData.estado_assessoria.length !== 2) {
        setCidadesAssessoria([]);
        return;
      }
      
      setLoadingCidadesAssessoria(true);
      try {
        const response = await axios.get(
          `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${assessoriaData.estado_assessoria}/municipios`
        );
        const cidadesOrdenadas = response.data
          .map(c => c.nome)
          .sort((a, b) => a.localeCompare(b));
        setCidadesAssessoria(cidadesOrdenadas);
      } catch (err) {
        console.error('Erro ao buscar cidades da assessoria:', err);
        setCidadesAssessoria([]);
      } finally {
        setLoadingCidadesAssessoria(false);
      }
    };
    
    fetchCidadesAssessoria();
  }, [assessoriaData.estado_assessoria]);
  
  // Verificar se pode usar modalidade Galera (PCD e Cadeirante não podem)
  const podeSelecionarPovao = formData.categoria === 'normal' || formData.categoria === '';

  // Filtrar equipes pela busca (agora são objetos com nome, cidade, estado)
  const equipesFiltradas = equipesCadastradas.filter(equipe => 
    equipe.nome?.toLowerCase().includes(equipeSearchTerm.toLowerCase()) ||
    equipe.cidade?.toLowerCase().includes(equipeSearchTerm.toLowerCase()) ||
    equipe.estado?.toLowerCase().includes(equipeSearchTerm.toLowerCase())
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Verificar se aceitou o termo
    if (!aceitouTermo) {
      setShowTermoModal(true);
      return;
    }

    // Validar campos de assessoria se for dono
    if (isDonoAssessoria === true) {
      if (!assessoriaData.nome_assessoria || !assessoriaData.estado_assessoria || !assessoriaData.cidade_assessoria || !assessoriaData.mensagem_bio) {
        setError('Preencha todos os campos obrigatórios da assessoria');
        return;
      }
    }
    
    setLoading(true);

    try {
      // Preparar dados com informações de dono de assessoria
      const dadosCompletos = {
        ...formData,
        is_dono_assessoria: isDonoAssessoria === true,
        assessoria_data: isDonoAssessoria === true ? {
          nome: assessoriaData.nome_assessoria,
          estado: assessoriaData.estado_assessoria,
          cidade: assessoriaData.cidade_assessoria,
          mensagem_bio: assessoriaData.mensagem_bio
        } : null
      };

      // Se for dono de assessoria, definir a equipe como o nome da assessoria
      if (isDonoAssessoria === true) {
        dadosCompletos.equipe = assessoriaData.nome_assessoria;
      }

      await register(dadosCompletos);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao cadastrar');
    } finally {
      setLoading(false);
    }
  };

  // Detectar scroll no termo
  const handleTermoScroll = (e) => {
    const element = e.target;
    const isAtBottom = Math.abs(element.scrollHeight - element.scrollTop - element.clientHeight) < 10;
    if (isAtBottom) {
      setScrolledToBottom(true);
    }
  };

  // Aceitar termo
  const handleAceitarTermo = () => {
    setAceitouTermo(true);
    setShowTermoModal(false);
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

  // Função para limpar a seleção de equipe
  const handleLimparEquipe = () => {
    setFormData(prev => ({ ...prev, equipe: '' }));
    setEquipeSearchTerm('');
    setShowEquipeDropdown(true);
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

                {/* Campo Equipe/Assessoria com dropdown - APENAS equipes cadastradas */}
                <div className="relative">
                  <Label>Equipe / Assessoria *</Label>
                  <div className="relative">
                    <Input
                      value={equipeSearchTerm}
                      onChange={(e) => {
                        setEquipeSearchTerm(e.target.value);
                        setShowEquipeDropdown(true);
                        // Se estiver editando, limpa a seleção atual
                        if (formData.equipe) {
                          setFormData(prev => ({ ...prev, equipe: '' }));
                        }
                      }}
                      onFocus={() => setShowEquipeDropdown(true)}
                      placeholder="Selecione ou busque sua equipe..."
                      data-testid="input-equipe"
                    />
                    {formData.equipe ? (
                      <button
                        type="button"
                        onClick={handleLimparEquipe}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-red-500 transition-colors"
                        title="Limpar seleção"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                      </button>
                    ) : (
                      <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    )}
                  </div>
                  
                  {/* Dropdown de equipes - APENAS cadastradas + INDIVIDUAL */}
                  {showEquipeDropdown && (
                    <div className="absolute z-50 w-full mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {/* Opção INDIVIDUAL - sempre primeiro */}
                      <div
                        className="px-3 py-3 hover:bg-amber-50 dark:hover:bg-amber-900/30 cursor-pointer border-b-2 border-amber-200 bg-amber-50/50"
                        onClick={() => handleEquipeSelect('Individual')}
                        data-testid="option-individual"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-amber-700">INDIVIDUAL</span>
                          <span className="text-xs text-amber-600 bg-amber-100 px-2 py-0.5 rounded">Sem equipe</span>
                        </div>
                      </div>
                      
                      {/* Lista de equipes cadastradas */}
                      {equipesFiltradas.length > 0 ? (
                        equipesFiltradas.slice(0, 15).map((equipe, idx) => (
                          <div
                            key={idx}
                            className="px-3 py-2 hover:bg-emerald-50 dark:hover:bg-emerald-900/30 cursor-pointer border-b border-slate-100 dark:border-slate-700"
                            onClick={() => handleEquipeSelect(equipe.nome)}
                          >
                            <div className="font-medium">{equipe.nome}</div>
                            {(equipe.cidade || equipe.estado) && (
                              <div className="text-xs text-slate-500">
                                {equipe.cidade}{equipe.cidade && equipe.estado && '/'}{equipe.estado}
                              </div>
                            )}
                          </div>
                        ))
                      ) : equipeSearchTerm.length > 0 ? (
                        <div className="px-3 py-3 text-slate-500 text-sm bg-slate-50">
                          <p className="font-medium text-slate-600">Equipe não encontrada</p>
                          <p className="text-xs mt-1">Selecione "INDIVIDUAL" e peça ao dono da assessoria para cadastrá-la.</p>
                        </div>
                      ) : null}
                    </div>
                  )}

                  {/* Alerta quando selecionar INDIVIDUAL */}
                  {formData.equipe === 'Individual' && (
                    <div className="mt-2 p-3 bg-amber-50 dark:bg-amber-900/20 border-2 border-amber-300 rounded-lg">
                      <div className="flex items-start gap-2">
                        <span className="text-amber-600 text-lg">⚠️</span>
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-amber-800 dark:text-amber-200">
                            Não encontrou sua equipe? É normal!
                          </p>
                          <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
                            Fale com o <strong>Dono(a) da sua Assessoria/Equipe</strong> para fazer o cadastro. 
                            Assim que ele(a) fizer, você já poderá alterar no seu <strong>Perfil</strong>.
                          </p>
                          <button
                            type="button"
                            onClick={handleLimparEquipe}
                            className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
                          >
                            Clique aqui para selecionar outra equipe
                          </button>
                        </div>
                      </div>
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

                {/* Seção Dono de Assessoria - Aparece APENAS quando selecionou INDIVIDUAL */}
                {formData.equipe === 'Individual' && (
                  <div className="md:col-span-2 bg-orange-100 dark:bg-orange-900/30 border-2 border-orange-300 rounded-xl p-4 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Building2 className="w-5 h-5 text-orange-600" />
                        <Label className="text-base font-semibold text-orange-800 dark:text-orange-200">
                          Você é Dono de Uma Assessoria/Equipe?
                        </Label>
                        <div className="relative group">
                          <HelpCircle className="w-4 h-4 text-orange-500 cursor-help" />
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block bg-slate-800 text-white text-xs p-2 rounded-lg w-48 z-50">
                            Se "SIM", realize o cadastro agora mesmo
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Seleção SIM/NÃO */}
                    <div className="flex gap-3">
                      <Button
                        type="button"
                        variant={isDonoAssessoria === true ? "default" : "outline"}
                        className={`flex-1 ${isDonoAssessoria === true ? 'bg-orange-500 hover:bg-orange-600' : 'border-orange-300 hover:bg-orange-50'}`}
                        onClick={() => setIsDonoAssessoria(true)}
                        data-testid="btn-dono-sim"
                      >
                        SIM
                      </Button>
                      <Button
                        type="button"
                        variant={isDonoAssessoria === false ? "default" : "outline"}
                        className={`flex-1 ${isDonoAssessoria === false ? 'bg-slate-500 hover:bg-slate-600' : 'border-orange-300 hover:bg-orange-50'}`}
                        onClick={() => setIsDonoAssessoria(false)}
                        data-testid="btn-dono-nao"
                      >
                        NÃO
                      </Button>
                    </div>

                    {/* Campos da Assessoria - Aparecem apenas se SIM */}
                    {isDonoAssessoria === true && (
                      <div className="space-y-4 pt-4 border-t border-orange-300">
                        <div>
                          <Label className="text-orange-800">Nome da Assessoria/Equipe *</Label>
                          <Input
                            value={assessoriaData.nome_assessoria}
                            onChange={(e) => setAssessoriaData({...assessoriaData, nome_assessoria: e.target.value})}
                            placeholder="Ex: Team Running Brasil"
                            className="bg-white"
                            data-testid="input-nome-assessoria"
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label className="text-orange-800">Estado (UF) *</Label>
                            <Select 
                              value={assessoriaData.estado_assessoria} 
                              onValueChange={(v) => setAssessoriaData({...assessoriaData, estado_assessoria: v, cidade_assessoria: ''})}
                            >
                              <SelectTrigger className="bg-white">
                                <SelectValue placeholder="Selecione" />
                              </SelectTrigger>
                              <SelectContent>
                                {ESTADOS_BR.map((estado) => (
                                  <SelectItem key={estado.uf} value={estado.uf}>{estado.uf} - {estado.nome}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          <div>
                            <Label className="text-orange-800">Cidade *</Label>
                            <Select 
                              value={assessoriaData.cidade_assessoria} 
                              onValueChange={(v) => setAssessoriaData({...assessoriaData, cidade_assessoria: v})}
                              disabled={!assessoriaData.estado_assessoria || loadingCidadesAssessoria}
                            >
                              <SelectTrigger className="bg-white">
                                <SelectValue placeholder={loadingCidadesAssessoria ? "Carregando..." : "Selecione a cidade"} />
                              </SelectTrigger>
                              <SelectContent>
                                {cidadesAssessoria.map(cidade => (
                                  <SelectItem key={cidade} value={cidade}>{cidade}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>

                        <div>
                          <Label className="text-orange-800">Envie uma Foto da Sua Equipe/Assessoria</Label>
                          <div className="mt-1">
                            <label className="flex items-center justify-center gap-2 p-4 border-2 border-dashed border-orange-300 rounded-lg bg-white cursor-pointer hover:bg-orange-50 transition">
                              <input
                                type="file"
                                accept="image/*"
                                className="hidden"
                                onChange={(e) => setAssessoriaData({...assessoriaData, foto_assessoria: e.target.files[0]})}
                              />
                              {assessoriaData.foto_assessoria ? (
                                <div className="flex items-center gap-2 text-orange-700">
                                  <FileImage className="w-5 h-5" />
                                  <span className="text-sm">{assessoriaData.foto_assessoria.name}</span>
                                </div>
                              ) : (
                                <div className="flex items-center gap-2 text-orange-500">
                                  <Upload className="w-5 h-5" />
                                  <span className="text-sm">Imagem Retangular (opcional)</span>
                                </div>
                              )}
                            </label>
                          </div>
                        </div>

                        <div>
                          <Label className="text-orange-800">Mensagem da BIO *</Label>
                          <textarea
                            value={assessoriaData.mensagem_bio}
                            onChange={(e) => setAssessoriaData({...assessoriaData, mensagem_bio: e.target.value})}
                            placeholder="Ex: Ajudamos milhares de Atletas pelo Brasil, faça parte do nosso Time!"
                            className="w-full mt-1 p-3 border border-orange-300 rounded-lg bg-white resize-none h-20 focus:outline-none focus:ring-2 focus:ring-orange-400"
                            maxLength={200}
                            data-testid="input-bio-assessoria"
                          />
                          <p className="text-xs text-orange-600 mt-1">
                            {assessoriaData.mensagem_bio.length}/200 caracteres
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

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

                    {/* Opção Galera - Pace Livre */}
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
                            Ranking da Galera
                          </h4>
                          <p className="text-sm text-slate-500 mt-1">
                            Pontuação baseada apenas na distância percorrida
                          </p>
                          <div className="mt-2 text-xs text-slate-400">
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded mr-1">5-9km = 5pts</span>
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded mr-1">10-20km = 10pts</span>
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded">21km+ = distância em pts</span>
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

              {/* Código de Indicação de Amigo(a) */}
              <div className="border-2 border-pink-200 bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Users className="w-5 h-5 text-pink-500" />
                  <Label className="text-base font-semibold text-pink-700 dark:text-pink-300">
                    Código de Indicação de Amigo(a)
                  </Label>
                  <span className="text-xs text-slate-500">(opcional)</span>
                </div>
                
                <div className="space-y-2">
                  <Input
                    placeholder="Ex: REF-AB123XYZ"
                    value={formData.codigo_indicacao}
                    onChange={(e) => {
                      const codigo = e.target.value.toUpperCase();
                      handleChange('codigo_indicacao', codigo);
                      verificarCodigoIndicacao(codigo);
                    }}
                    className={`bg-white font-mono ${
                      codigoIndicacaoValido === true 
                        ? 'border-emerald-500 focus:ring-emerald-500' 
                        : codigoIndicacaoValido === false 
                          ? 'border-red-500 focus:ring-red-500'
                          : ''
                    }`}
                    data-testid="input-codigo-indicacao"
                  />
                  
                  {codigoIndicacaoValido === true && nomeIndicador && (
                    <div className="flex items-center gap-2 text-emerald-600 text-sm">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Indicado por: <strong>{nomeIndicador}</strong></span>
                    </div>
                  )}
                  
                  {codigoIndicacaoValido === false && formData.codigo_indicacao.length >= 5 && (
                    <p className="text-red-500 text-sm">Código de indicação inválido</p>
                  )}
                  
                  <p className="text-xs text-slate-500">
                    <Gift className="w-3 h-3 inline mr-1" />
                    Se um amigo te indicou, insira o código dele aqui!
                  </p>
                </div>
              </div>

              {/* Termo de Aceite */}
              <div className="border-2 border-amber-200 bg-amber-50 dark:bg-amber-900/20 rounded-xl p-4">
                <div className="flex items-start space-x-3">
                  <Checkbox
                    id="termo"
                    checked={aceitouTermo}
                    onCheckedChange={(checked) => {
                      if (!checked) {
                        setAceitouTermo(false);
                      } else {
                        setShowTermoModal(true);
                      }
                    }}
                    className="mt-1"
                  />
                  <div className="space-y-1">
                    <label
                      htmlFor="termo"
                      className="text-sm font-medium cursor-pointer leading-none"
                    >
                      Li e concordo com o Regulamento da Plataforma *
                    </label>
                    <p className="text-xs text-slate-500">
                      Clique para ler o regulamento completo antes de continuar
                    </p>
                    {aceitouTermo && (
                      <div className="flex items-center gap-1 text-emerald-600 text-xs font-medium">
                        <CheckCircle2 className="w-3 h-3" />
                        Termo aceito
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-emerald-600 hover:bg-emerald-700"
                disabled={loading || !aceitouTermo}
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

      {/* Modal do Termo de Aceite */}
      <Dialog open={showTermoModal} onOpenChange={setShowTermoModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ScrollText className="w-5 h-5 text-emerald-600" />
              Regulamento da Plataforma Ranking Run
            </DialogTitle>
            <DialogDescription>
              Leia atentamente o regulamento abaixo. Role até o final para habilitar o botão de aceite.
            </DialogDescription>
          </DialogHeader>
          
          <div 
            ref={termoRef}
            onScroll={handleTermoScroll}
            className="flex-1 overflow-y-auto border rounded-lg p-4 bg-slate-50 dark:bg-slate-900 text-xs leading-relaxed max-h-[50vh]"
          >
            <div className="space-y-4 text-slate-700 dark:text-slate-300">
              <h3 className="font-bold text-sm text-emerald-700">REGULAMENTO OFICIAL DA PLATAFORMA RANKING RUN</h3>
              
              <section>
                <h4 className="font-semibold text-emerald-600">1. DISPOSIÇÕES GERAIS</h4>
                <p>1.1. A Plataforma Ranking Run é um sistema de ranqueamento de atletas de corrida de rua, desenvolvido para promover a competição saudável e o reconhecimento dos participantes.</p>
                <p>1.2. Ao se cadastrar, o atleta declara ter lido, compreendido e aceito integralmente este regulamento.</p>
                <p>1.3. A Ranking Run reserva-se o direito de alterar este regulamento a qualquer momento, mediante comunicação prévia aos usuários.</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">2. CADASTRO E PARTICIPAÇÃO</h4>
                <p>2.1. O cadastro é gratuito e destinado a atletas maiores de 18 anos ou menores com autorização dos responsáveis legais.</p>
                <p>2.2. Os dados fornecidos devem ser verdadeiros e atualizados. Informações falsas podem resultar em exclusão da plataforma.</p>
                <p>2.3. Cada pessoa física pode ter apenas um cadastro ativo na plataforma.</p>
                <p>2.4. O atleta é responsável pela segurança de suas credenciais de acesso (e-mail e senha).</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">3. MODALIDADES DE PARTICIPAÇÃO</h4>
                <p>3.1. RANKING PROFISSIONAL/AMADOR: Pontuação baseada na colocação em provas oficiais (1º ao 10º lugar).</p>
                <p>3.2. RANKING DA GALERA: Pontuação baseada exclusivamente na distância percorrida, independente da colocação.</p>
                <p>3.3. RANKING DE EQUIPES/ASSESSORIAS: Pontuação coletiva baseada nos resultados dos atletas vinculados.</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">4. SISTEMA DE PONTUAÇÃO</h4>
                <p>4.1. PROFISSIONAL/AMADOR: 1º lugar = 10pts, 2º = 9pts, 3º = 8pts, até 10º = 1pt.</p>
                <p>4.2. GALERA: 5km a 9km = 5pts, 10km a 20km = 10pts, 21km ou mais = distância em pts.</p>
                <p>4.3. EQUIPES: Atleta cadastrado = +0,5pt, Resultado lançado = +1,0pt, Pódio (2º-5º) = +0,5pt, 1º lugar = +1,0pt.</p>
                <p>4.4. Os pontos são acumulados por período (mensal, anual e histórico).</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">5. SUBMISSÃO DE RESULTADOS</h4>
                <p>5.1. Os resultados devem ser submetidos com documentação comprobatória (foto do resultado oficial, print do chip time, etc.).</p>
                <p>5.2. Resultados fraudulentos ou adulterados resultarão em exclusão imediata e permanente da plataforma.</p>
                <p>5.3. A equipe de moderação da Ranking Run reserva-se o direito de solicitar documentação adicional.</p>
                <p>5.4. Resultados não aprovados não geram pontuação e não aparecem no ranking.</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">6. EQUIPES E ASSESSORIAS</h4>
                <p>6.1. Cada atleta pode estar vinculado a apenas uma equipe/assessoria por vez.</p>
                <p>6.2. A transferência de equipe só pode ser realizada a cada 15 dias.</p>
                <p>6.3. O responsável/dono da assessoria não pode transferir-se para outra equipe enquanto for responsável legal.</p>
                <p>6.4. A exclusão de uma assessoria remove automaticamente todos os pontos vinculados.</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">7. AVALIAÇÃO DE CORRIDAS</h4>
                <p>7.1. Apenas atletas que participaram efetivamente de uma corrida podem avaliá-la.</p>
                <p>7.2. Avaliações fraudulentas podem caracterizar falsidade ideológica e gerar responsabilização civil ou legal.</p>
                <p>7.3. Cada atleta pode avaliar cada corrida apenas uma vez.</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">8. PRIVACIDADE E DADOS</h4>
                <p>8.1. Os dados pessoais são tratados conforme a Lei Geral de Proteção de Dados (LGPD).</p>
                <p>8.2. Informações de ranking e desempenho podem ser exibidas publicamente na plataforma.</p>
                <p>8.3. O atleta pode solicitar a exclusão de seus dados a qualquer momento.</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">9. CONDUTAS PROIBIDAS</h4>
                <p>9.1. É proibido: fornecer informações falsas, utilizar múltiplas contas, manipular resultados, prejudicar outros atletas, utilizar linguagem ofensiva ou discriminatória.</p>
                <p>9.2. Violações podem resultar em suspensão temporária ou exclusão permanente da plataforma.</p>
              </section>

              <section>
                <h4 className="font-semibold text-emerald-600">10. DISPOSIÇÕES FINAIS</h4>
                <p>10.1. Casos omissos serão analisados pela administração da Ranking Run.</p>
                <p>10.2. Este regulamento entra em vigor na data de aceite pelo atleta.</p>
                <p>10.3. Dúvidas e sugestões podem ser enviadas através dos canais oficiais da plataforma.</p>
              </section>

              <div className="mt-6 p-3 bg-amber-100 dark:bg-amber-900/30 rounded-lg border border-amber-300">
                <p className="font-semibold text-amber-800 dark:text-amber-200 text-center">
                  Ao clicar em "EU CONCORDO", você declara ter lido e aceito integralmente este regulamento.
                </p>
              </div>
            </div>
          </div>

          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setShowTermoModal(false)}>
              Cancelar
            </Button>
            <Button 
              onClick={handleAceitarTermo}
              disabled={!scrolledToBottom}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <CheckCircle2 className="w-4 h-4 mr-2" />
              {scrolledToBottom ? 'EU CONCORDO' : 'Role até o final para aceitar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CadastroPage;
