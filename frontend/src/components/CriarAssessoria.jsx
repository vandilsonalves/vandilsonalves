// /app/frontend/src/components/CriarAssessoria.jsx
// Componente para donos de assessoria criarem sua equipe
// Usando Portal isolado para evitar problemas de foco

import React, { useState, useEffect, useRef, memo } from 'react';
import { createPortal } from 'react-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { 
  Building2, MapPin, Users, Save, Loader2, Trophy, Sparkles, CheckCircle, AlertCircle, X
} from 'lucide-react';
import { toast } from 'sonner';
import CidadeCombobox from '@/components/CidadeCombobox';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ESTADOS_BR = [
  { sigla: 'AC', nome: 'Acre' },
  { sigla: 'AL', nome: 'Alagoas' },
  { sigla: 'AP', nome: 'Amapá' },
  { sigla: 'AM', nome: 'Amazonas' },
  { sigla: 'BA', nome: 'Bahia' },
  { sigla: 'CE', nome: 'Ceará' },
  { sigla: 'DF', nome: 'Distrito Federal' },
  { sigla: 'ES', nome: 'Espírito Santo' },
  { sigla: 'GO', nome: 'Goiás' },
  { sigla: 'MA', nome: 'Maranhão' },
  { sigla: 'MT', nome: 'Mato Grosso' },
  { sigla: 'MS', nome: 'Mato Grosso do Sul' },
  { sigla: 'MG', nome: 'Minas Gerais' },
  { sigla: 'PA', nome: 'Pará' },
  { sigla: 'PB', nome: 'Paraíba' },
  { sigla: 'PR', nome: 'Paraná' },
  { sigla: 'PE', nome: 'Pernambuco' },
  { sigla: 'PI', nome: 'Piauí' },
  { sigla: 'RJ', nome: 'Rio de Janeiro' },
  { sigla: 'RN', nome: 'Rio Grande do Norte' },
  { sigla: 'RS', nome: 'Rio Grande do Sul' },
  { sigla: 'RO', nome: 'Rondônia' },
  { sigla: 'RR', nome: 'Roraima' },
  { sigla: 'SC', nome: 'Santa Catarina' },
  { sigla: 'SP', nome: 'São Paulo' },
  { sigla: 'SE', nome: 'Sergipe' },
  { sigla: 'TO', nome: 'Tocantins' }
];

// Formulário isolado com memo para evitar re-renders
const AssessoriaForm = memo(({ token, onSuccess }) => {
  const [nome, setNome] = useState('');
  const [cidade, setCidade] = useState('');
  const [estado, setEstado] = useState('');
  const [mensagemBio, setMensagemBio] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [cidades, setCidades] = useState([]);
  const [loadingCidades, setLoadingCidades] = useState(false);
  
  const nomeInputRef = useRef(null);

  // Buscar cidades quando estado muda
  useEffect(() => {
    if (estado) {
      fetchCidades(estado);
    } else {
      setCidades([]);
      setCidade('');
    }
  }, [estado]);

  const fetchCidades = async (uf) => {
    setLoadingCidades(true);
    setCidade('');
    try {
      const response = await axios.get(
        `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios`
      );
      const cidadesOrdenadas = response.data
        .map(c => c.nome)
        .sort((a, b) => a.localeCompare(b, 'pt-BR'));
      setCidades(cidadesOrdenadas);
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
      setCidades([]);
      toast.error('Erro ao carregar cidades. Tente novamente.');
    } finally {
      setLoadingCidades(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!nome.trim()) {
      setError('O nome da assessoria é obrigatório');
      return;
    }
    if (!cidade.trim()) {
      setError('A cidade é obrigatória');
      return;
    }
    if (!estado) {
      setError('O estado é obrigatório');
      return;
    }
    
    setSaving(true);
    try {
      const response = await axios.post(
        `${API}/atletas/criar-assessoria`,
        {
          nome: nome.trim(),
          cidade: cidade.trim(),
          estado,
          mensagem_bio: mensagemBio.trim()
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('Assessoria criada com sucesso!', {
        description: 'Sua assessoria começa com 0,5 pontos. Agora você pode convidar atletas para sua equipe.'
      });
      
      if (onSuccess) {
        onSuccess(response.data.assessoria);
      }
    } catch (err) {
      const message = err.response?.data?.detail || 'Erro ao criar assessoria';
      setError(message);
      toast.error('Erro', { description: message });
    } finally {
      setSaving(false);
    }
  };

  // Evitar que eventos de teclado vazem para fora
  const handleKeyDown = (e) => {
    e.stopPropagation();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5" onKeyDown={handleKeyDown}>
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="w-4 h-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Nome da Assessoria */}
      <div className="space-y-2">
        <Label htmlFor="nome-assessoria" className="flex items-center gap-2 text-base font-semibold">
          <Building2 className="w-5 h-5 text-amber-600" />
          Nome da Assessoria/Equipe *
        </Label>
        <input
          ref={nomeInputRef}
          id="nome-assessoria"
          type="text"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          onFocus={(e) => e.target.select()}
          placeholder="Ex: Team Running Pro, Assessoria XYZ"
          className="flex h-10 w-full rounded-md border-2 border-slate-200 bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          data-testid="input-nome-assessoria"
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck="false"
        />
        <p className="text-xs text-slate-500">
          Este será o nome oficial da sua equipe nos rankings
        </p>
      </div>

      {/* Estado */}
      <div className="space-y-2">
        <Label htmlFor="estado" className="flex items-center gap-2 font-semibold">
          <MapPin className="w-4 h-4 text-amber-600" />
          Estado *
        </Label>
        <select
          id="estado"
          value={estado}
          onChange={(e) => setEstado(e.target.value)}
          className="flex h-10 w-full rounded-md border-2 border-slate-200 bg-white px-3 py-2 text-sm focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2"
          data-testid="select-estado-assessoria"
        >
          <option value="">Selecione o estado</option>
          {ESTADOS_BR.map(e => (
            <option key={e.sigla} value={e.sigla}>{e.sigla} - {e.nome}</option>
          ))}
        </select>
      </div>

      {/* Cidade */}
      <div className="space-y-2">
        <Label htmlFor="cidade" className="flex items-center gap-2 font-semibold">
          <MapPin className="w-4 h-4 text-amber-600" />
          Cidade *
        </Label>
        
        {loadingCidades ? (
          <div className="flex items-center gap-2 p-3 bg-slate-100 rounded-md">
            <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
            <span className="text-sm text-slate-600">Carregando cidades...</span>
          </div>
        ) : cidades.length > 0 ? (
          <>
            <CidadeCombobox
              cidades={cidades}
              value={cidade}
              onValueChange={setCidade}
              disabled={!estado}
              placeholder={estado ? "Selecione a cidade" : "Selecione o estado primeiro"}
              data-testid="select-cidade-assessoria"
            />
            <p className="text-xs text-slate-500">
              {cidades.length} cidades disponíveis
            </p>
          </>
        ) : estado ? (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-md">
            <p className="text-sm text-amber-700">
              Erro ao carregar cidades. Tente selecionar o estado novamente.
            </p>
            <Button 
              type="button" 
              variant="outline" 
              size="sm" 
              className="mt-2"
              onClick={() => fetchCidades(estado)}
            >
              <Loader2 className="w-3 h-3 mr-1" />
              Tentar novamente
            </Button>
          </div>
        ) : (
          <div className="p-3 bg-slate-100 rounded-md">
            <p className="text-sm text-slate-500">Selecione o estado primeiro</p>
          </div>
        )}
      </div>

      {/* Bio/Mensagem */}
      <div className="space-y-2">
        <Label htmlFor="bio-assessoria" className="flex items-center gap-2 font-semibold">
          <Users className="w-4 h-4 text-amber-600" />
          Mensagem/Bio (opcional)
        </Label>
        <textarea
          id="bio-assessoria"
          value={mensagemBio}
          onChange={(e) => setMensagemBio(e.target.value)}
          onFocus={(e) => e.target.select()}
          placeholder="Escreva uma mensagem de apresentação da sua assessoria..."
          rows={3}
          className="flex min-h-[80px] w-full rounded-md border-2 border-slate-200 bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          data-testid="input-bio-assessoria"
          autoComplete="off"
          autoCorrect="off"
          spellCheck="false"
        />
      </div>

      {/* Info de Pontuação Inicial */}
      <Alert className="bg-amber-50 border-amber-200">
        <Trophy className="w-4 h-4 text-amber-600" />
        <AlertDescription className="text-amber-800">
          Sua assessoria começará com <strong>0,5 pontos</strong> no ranking!
        </AlertDescription>
      </Alert>

      {/* Botão Criar */}
      <Button
        type="submit"
        disabled={saving}
        className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-bold py-3 text-lg"
        data-testid="btn-criar-assessoria"
      >
        {saving ? (
          <>
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            Criando sua assessoria...
          </>
        ) : (
          <>
            <CheckCircle className="w-5 h-5 mr-2" />
            Criar Minha Assessoria
          </>
        )}
      </Button>

      <p className="text-center text-xs text-slate-500">
        Após criar, você terá acesso ao painel "Minha Assessoria"
      </p>
    </form>
  );
});

AssessoriaForm.displayName = 'AssessoriaForm';

// Modal usando Portal para isolamento completo
const CriarAssessoria = ({ token, onSuccess, isModal = false, forceOpen = false }) => {
  
  // Modal usando Portal
  if (isModal && forceOpen) {
    return createPortal(
      <div 
        className="fixed inset-0 z-[9999] flex items-center justify-center"
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div 
          className="relative bg-white rounded-lg shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 p-6 text-white rounded-t-lg">
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-white/20 rounded-full p-3">
                <Trophy className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Parabéns!</h2>
                <p className="text-amber-100">Você foi promovido a Dono de Assessoria!</p>
              </div>
            </div>
            <Badge className="bg-white/20 text-white mt-2">
              <Sparkles className="w-4 h-4 mr-1" />
              Complete seu cadastro para ativar sua equipe
            </Badge>
          </div>
          
          {/* Content */}
          <div className="p-6">
            <Alert className="mb-4 bg-blue-50 border-blue-200">
              <AlertCircle className="w-4 h-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                Este cadastro é obrigatório. Você precisa criar sua assessoria para continuar usando a plataforma como Dono de Assessoria.
              </AlertDescription>
            </Alert>
            
            <AssessoriaForm token={token} onSuccess={onSuccess} />
          </div>
        </div>
      </div>,
      document.body
    );
  }

  // Renderizar como Card normal
  return (
    <Card className="border-2 border-amber-400 shadow-lg overflow-hidden" data-testid="criar-assessoria">
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-white/20 rounded-full p-3">
            <Trophy className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">Parabéns!</h2>
            <p className="text-amber-100">Você foi promovido a Dono de Assessoria!</p>
          </div>
        </div>
        <Badge className="bg-white/20 text-white mt-2">
          <Sparkles className="w-4 h-4 mr-1" />
          Complete seu cadastro para ativar sua equipe
        </Badge>
      </div>

      <CardContent className="p-6">
        <AssessoriaForm token={token} onSuccess={onSuccess} />
      </CardContent>
    </Card>
  );
};

export default memo(CriarAssessoria);
