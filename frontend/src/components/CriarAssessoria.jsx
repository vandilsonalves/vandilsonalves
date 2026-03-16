// /app/frontend/src/components/CriarAssessoria.jsx
// Componente para donos de assessoria criarem sua equipe

import { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, MapPin, Users, Save, Loader2, Trophy, Sparkles, CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

const CriarAssessoria = ({ token, onSuccess }) => {
  const [nome, setNome] = useState('');
  const [cidade, setCidade] = useState('');
  const [estado, setEstado] = useState('');
  const [mensagemBio, setMensagemBio] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

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
        description: 'Agora você pode convidar atletas para sua equipe.'
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
        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Nome da Assessoria */}
          <div className="space-y-2">
            <Label htmlFor="nome" className="flex items-center gap-2 text-base font-semibold">
              <Building2 className="w-5 h-5 text-amber-600" />
              Nome da Assessoria/Equipe *
            </Label>
            <Input
              id="nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              placeholder="Ex: Team Running Pro, Assessoria XYZ"
              className="border-2 border-slate-200 focus:border-amber-500"
              data-testid="input-nome-assessoria"
            />
            <p className="text-xs text-slate-500">
              Este será o nome oficial da sua equipe nos rankings
            </p>
          </div>

          {/* Cidade e Estado */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="cidade" className="flex items-center gap-2 font-semibold">
                <MapPin className="w-4 h-4 text-amber-600" />
                Cidade *
              </Label>
              <Input
                id="cidade"
                value={cidade}
                onChange={(e) => setCidade(e.target.value)}
                placeholder="Sua cidade"
                className="border-2 border-slate-200 focus:border-amber-500"
                data-testid="input-cidade-assessoria"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="estado" className="font-semibold">UF *</Label>
              <Select value={estado} onValueChange={setEstado}>
                <SelectTrigger className="border-2 border-slate-200 focus:border-amber-500" data-testid="select-estado-assessoria">
                  <SelectValue placeholder="Selecione" />
                </SelectTrigger>
                <SelectContent>
                  {ESTADOS_BR.map(uf => (
                    <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Bio/Mensagem */}
          <div className="space-y-2">
            <Label htmlFor="bio" className="flex items-center gap-2 font-semibold">
              <Users className="w-4 h-4 text-amber-600" />
              Mensagem/Bio (opcional)
            </Label>
            <Textarea
              id="bio"
              value={mensagemBio}
              onChange={(e) => setMensagemBio(e.target.value)}
              placeholder="Escreva uma mensagem de apresentação da sua assessoria..."
              rows={3}
              className="border-2 border-slate-200 focus:border-amber-500"
              data-testid="input-bio-assessoria"
            />
          </div>

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
                Criando Assessoria...
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
      </CardContent>
    </Card>
  );
};

export default CriarAssessoria;
