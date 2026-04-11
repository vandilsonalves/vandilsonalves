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
import CidadeCombobox from '@/components/CidadeCombobox';
import CadastroTermoModal from '@/components/cadastro/CadastroTermoModal';
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
    codigo_indicacao: '',
    telefone: '',
    tipo_corredor: '',
    terreno_preferido: ''
  });

  // Estados do Termo de Aceite
  const [showTermoModal, setShowTermoModal] = useState(false);
  const [aceitouTermo, setAceitouTermo] = useState(false);

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

    // Validar equipe selecionada
    if (!formData.equipe) {
      setError('Selecione uma equipe ou a opção INDIVIDUAL');
      return;
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
                  
                  {/* Dropdown de equipes - INDIVIDUAL + SOU DONO + equipes cadastradas */}
                  {showEquipeDropdown && (
                    <div className="absolute z-50 w-full mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {/* Opção INDIVIDUAL - sempre primeiro */}
                      <div
                        className="px-3 py-3 hover:bg-amber-50 dark:hover:bg-amber-900/30 cursor-pointer border-b border-slate-200"
                        onClick={() => {
                          handleEquipeSelect('Individual');
                          setIsDonoAssessoria(false);
                        }}
                        data-testid="option-individual"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-amber-700">INDIVIDUAL</span>
                          <span className="text-xs text-amber-600 bg-amber-100 px-2 py-0.5 rounded">Sem equipe</span>
                        </div>
                      </div>

                      {/* Opção SOU DONO DE UMA ASSESSORIA */}
                      <div
                        className="px-3 py-3 hover:bg-orange-50 dark:hover:bg-orange-900/30 cursor-pointer border-b-2 border-orange-200 bg-orange-50/50"
                        onClick={() => {
                          handleEquipeSelect('Dono de Assessoria');
                          setIsDonoAssessoria(true);
                        }}
                        data-testid="option-dono-assessoria"
                      >
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-orange-600" />
                          <span className="font-semibold text-orange-700">SOU DONO DE UMA ASSESSORIA / EQUIPE</span>
                        </div>
                        <p className="text-xs text-orange-500 mt-1 ml-6">Cadastre sua assessoria agora mesmo</p>
                      </div>
                      
                      {/* Lista de equipes cadastradas */}
                      {equipesFiltradas.length > 0 ? (
                        equipesFiltradas.slice(0, 15).map((equipe, idx) => (
                          <div
                            key={idx}
                            className="px-3 py-2 hover:bg-emerald-50 dark:hover:bg-emerald-900/30 cursor-pointer border-b border-slate-100 dark:border-slate-700"
                            onClick={() => {
                              handleEquipeSelect(equipe.nome);
                              setIsDonoAssessoria(false);
                            }}
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
                          <p className="text-xs mt-1">Selecione "INDIVIDUAL" ou "SOU DONO DE UMA ASSESSORIA".</p>
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
                    <CidadeCombobox
                      cidades={cidades}
                      value={formData.cidade}
                      onValueChange={(value) => handleChange('cidade', value)}
                      loading={loadingCidades}
                      disabled={cidades.length === 0}
                      data-testid="select-cidade"
                    />
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

                <div>
                  <Label>Telefone *</Label>
                  <Input
                    value={formData.telefone}
                    onChange={(e) => handleChange('telefone', e.target.value)}
                    placeholder="(00) 00000-0000"
                    data-testid="input-telefone"
                  />
                </div>

                <div>
                  <Label>Tipo de Corredor *</Label>
                  <Select value={formData.tipo_corredor} onValueChange={(value) => handleChange('tipo_corredor', value)}>
                    <SelectTrigger data-testid="select-tipo-corredor">
                      <SelectValue placeholder="Selecione seu tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="velocista">
                        <span><strong className="uppercase">VELOCISTA</strong> <span className="text-xs text-slate-500">- provas curtas até 5km</span></span>
                      </SelectItem>
                      <SelectItem value="resistencia">
                        <span><strong className="uppercase">RESISTÊNCIA</strong> <span className="text-xs text-slate-500">- provas mais longas até 21km</span></span>
                      </SelectItem>
                      <SelectItem value="endurance">
                        <span><strong className="uppercase">ENDURANCE</strong> <span className="text-xs text-slate-500">- provas acima de 42km. Maratonista, Ironman, triatlo</span></span>
                      </SelectItem>
                      <SelectItem value="pace_leve">
                        <span><strong className="uppercase">PACE LEVE</strong> <span className="text-xs text-slate-500">- Corro por Diversão</span></span>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Seu Terreno Preferido *</Label>
                  <Select value={formData.terreno_preferido} onValueChange={(value) => handleChange('terreno_preferido', value)}>
                    <SelectTrigger data-testid="select-terreno-preferido">
                      <SelectValue placeholder="Selecione seu terreno" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="rua_asfalto">Rua - Asfalto</SelectItem>
                      <SelectItem value="trilha">Trilha</SelectItem>
                      <SelectItem value="esteira">Esteira</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Seção Dono de Assessoria - Aparece quando selecionou SOU DONO no dropdown */}
                {formData.equipe === 'Dono de Assessoria' && isDonoAssessoria === true && (
                  <div className="md:col-span-2 bg-orange-100 dark:bg-orange-900/30 border-2 border-orange-300 rounded-xl p-4 space-y-4">
                    <div className="flex items-center gap-2">
                      <Building2 className="w-5 h-5 text-orange-600" />
                      <Label className="text-base font-semibold text-orange-800 dark:text-orange-200">
                        Cadastro da Assessoria/Equipe
                      </Label>
                    </div>

                    <div className="space-y-4">
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
                          <CidadeCombobox
                            cidades={cidadesAssessoria}
                            value={assessoriaData.cidade_assessoria}
                            onValueChange={(v) => setAssessoriaData({...assessoriaData, cidade_assessoria: v})}
                            loading={loadingCidadesAssessoria}
                            disabled={!assessoriaData.estado_assessoria}
                            triggerClassName="bg-white"
                          />
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
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded mr-1">5-9km = 5 pts</span>
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded mr-1">10-20km = 7 pts</span>
                            <span className="inline-block bg-purple-100 dark:bg-purple-800 px-2 py-1 rounded">21km+ = 9 pts</span>
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

      {/* Modal do Termo de Aceite - Extraído */}
      <CadastroTermoModal 
        open={showTermoModal} 
        onOpenChange={setShowTermoModal} 
        onAccept={handleAceitarTermo}
      />
    </div>
  );
};

export default CadastroPage;
