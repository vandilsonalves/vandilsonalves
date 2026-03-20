import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Settings, Save, RotateCcw, Trophy, Users, Target, 
  Clock, CheckCircle, AlertTriangle, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ConfiguracoesSistemaTab = ({ token }) => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API}/admin/configuracoes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(response.data);
      setHasChanges(false);
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
      toast.error('Erro ao carregar configurações');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/admin/configuracoes`, config, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Configurações salvas com sucesso!');
      setHasChanges(false);
      fetchConfig();
    } catch (error) {
      console.error('Erro ao salvar:', error);
      toast.error('Erro ao salvar configurações');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Tem certeza que deseja resetar para os valores padrão?')) return;
    
    setSaving(true);
    try {
      await axios.post(`${API}/admin/configuracoes/resetar`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Configurações resetadas para os valores padrão!');
      fetchConfig();
    } catch (error) {
      console.error('Erro ao resetar:', error);
      toast.error('Erro ao resetar configurações');
    } finally {
      setSaving(false);
    }
  };

  const updateConfig = (path, value) => {
    setConfig(prev => {
      const newConfig = { ...prev };
      const keys = path.split('.');
      let current = newConfig;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] };
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newConfig;
    });
    setHasChanges(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="configuracoes-sistema-tab">
      {/* Header com botões de ação */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Settings className="w-6 h-6" />
            Configurações do Sistema
          </h2>
          <p className="text-slate-600 text-sm mt-1">
            Configure as regras de pontuação e parâmetros do sistema
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleReset}
            disabled={saving}
            className="text-amber-600 border-amber-300 hover:bg-amber-50"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Resetar Padrão
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving || !hasChanges}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {saving ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Salvar Alterações
          </Button>
        </div>
      </div>

      {hasChanges && (
        <Alert className="bg-amber-50 border-amber-200">
          <AlertTriangle className="w-4 h-4 text-amber-600" />
          <AlertDescription className="text-amber-700">
            Você tem alterações não salvas. Clique em "Salvar Alterações" para aplicar.
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="pontuacao" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="pontuacao">
            <Trophy className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">Pontuação</span>
          </TabsTrigger>
          <TabsTrigger value="povao">
            <Users className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">Galera</span>
          </TabsTrigger>
          <TabsTrigger value="equipes">
            <Target className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">Equipes</span>
          </TabsTrigger>
          <TabsTrigger value="gerais">
            <Clock className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">Gerais</span>
          </TabsTrigger>
        </TabsList>

        {/* Tab Pontuação Pro/Amador */}
        <TabsContent value="pontuacao" className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Normal */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Categoria Normal</CardTitle>
                <CardDescription>Pontuação por colocação (1º a 10º lugar)</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {['primeiro', 'segundo', 'terceiro', 'quarto', 'quinto', 
                  'sexto', 'setimo', 'oitavo', 'nono', 'decimo'].map((pos, idx) => (
                  <div key={pos} className="flex items-center gap-3">
                    <Label className="w-24">{idx + 1}º lugar:</Label>
                    <Input
                      type="number"
                      min="0"
                      value={config?.pontuacao_normal?.[pos] || 0}
                      onChange={(e) => updateConfig(`pontuacao_normal.${pos}`, parseInt(e.target.value) || 0)}
                      className="w-20"
                    />
                    <span className="text-slate-500">pts</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* PCD */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">PCD / Cadeirante</CardTitle>
                <CardDescription>Pontuação por colocação (1º a 3º lugar)</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {['primeiro', 'segundo', 'terceiro'].map((pos, idx) => (
                  <div key={pos} className="flex items-center gap-3">
                    <Label className="w-24">{idx + 1}º lugar:</Label>
                    <Input
                      type="number"
                      min="0"
                      value={config?.pontuacao_pcd?.[pos] || 0}
                      onChange={(e) => updateConfig(`pontuacao_pcd.${pos}`, parseInt(e.target.value) || 0)}
                      className="w-20"
                    />
                    <span className="text-slate-500">pts</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Textos */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Textos da Página de Regras</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Título da Seção</Label>
                <Input
                  value={config?.textos?.titulo_profissional || ''}
                  onChange={(e) => updateConfig('textos.titulo_profissional', e.target.value)}
                />
              </div>
              <div>
                <Label>Descrição</Label>
                <Textarea
                  value={config?.textos?.descricao_profissional || ''}
                  onChange={(e) => updateConfig('textos.descricao_profissional', e.target.value)}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Galera */}
        <TabsContent value="povao" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Pontuação por Distância</CardTitle>
              <CardDescription>Define os pontos para cada faixa de distância</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Label className="w-32">5km a 9km:</Label>
                <Input
                  type="number"
                  min="0"
                  value={config?.pontuacao_povao?.faixa_5_9km || 0}
                  onChange={(e) => updateConfig('pontuacao_povao.faixa_5_9km', parseInt(e.target.value) || 0)}
                  className="w-20"
                />
                <span className="text-slate-500">pts</span>
              </div>
              <div className="flex items-center gap-3">
                <Label className="w-32">10km a 20km:</Label>
                <Input
                  type="number"
                  min="0"
                  value={config?.pontuacao_povao?.faixa_10_20km || 0}
                  onChange={(e) => updateConfig('pontuacao_povao.faixa_10_20km', parseInt(e.target.value) || 0)}
                  className="w-20"
                />
                <span className="text-slate-500">pts</span>
              </div>
              <div className="flex items-center gap-3">
                <Label className="w-32">21km ou mais:</Label>
                <Input
                  type="number"
                  min="0"
                  value={config?.pontuacao_povao?.faixa_21km_mais || 0}
                  onChange={(e) => updateConfig('pontuacao_povao.faixa_21km_mais', parseInt(e.target.value) || 0)}
                  className="w-20"
                />
                <span className="text-slate-500">pts</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Textos da Página de Regras</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Título da Seção</Label>
                <Input
                  value={config?.textos?.titulo_povao || ''}
                  onChange={(e) => updateConfig('textos.titulo_povao', e.target.value)}
                />
              </div>
              <div>
                <Label>Descrição</Label>
                <Textarea
                  value={config?.textos?.descricao_povao || ''}
                  onChange={(e) => updateConfig('textos.descricao_povao', e.target.value)}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Equipes */}
        <TabsContent value="equipes" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Sistema de Pontuação das Equipes</CardTitle>
              <CardDescription>Configure os valores de pontuação para o ranking de assessorias</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Label className="w-48">Por atleta vinculado:</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.1"
                  value={config?.pontuacao_equipes?.por_atleta || 0}
                  onChange={(e) => updateConfig('pontuacao_equipes.por_atleta', parseFloat(e.target.value) || 0)}
                  className="w-20"
                />
                <span className="text-slate-500">pts</span>
              </div>
              <div className="flex items-center gap-3">
                <Label className="w-48">Por resultado aprovado:</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.1"
                  value={config?.pontuacao_equipes?.por_resultado || 0}
                  onChange={(e) => updateConfig('pontuacao_equipes.por_resultado', parseFloat(e.target.value) || 0)}
                  className="w-20"
                />
                <span className="text-slate-500">pts</span>
              </div>
              <div className="flex items-center gap-3">
                <Label className="w-48">Bônus 2º ao 5º lugar:</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.1"
                  value={config?.pontuacao_equipes?.bonus_2_a_5_lugar || 0}
                  onChange={(e) => updateConfig('pontuacao_equipes.bonus_2_a_5_lugar', parseFloat(e.target.value) || 0)}
                  className="w-20"
                />
                <span className="text-slate-500">pts</span>
              </div>
              <div className="flex items-center gap-3">
                <Label className="w-48">Bônus 1º lugar (vitória):</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.1"
                  value={config?.pontuacao_equipes?.bonus_1_lugar || 0}
                  onChange={(e) => updateConfig('pontuacao_equipes.bonus_1_lugar', parseFloat(e.target.value) || 0)}
                  className="w-20"
                />
                <span className="text-slate-500">pts</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Textos da Página de Regras</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Título da Seção</Label>
                <Input
                  value={config?.textos?.titulo_equipes || ''}
                  onChange={(e) => updateConfig('textos.titulo_equipes', e.target.value)}
                />
              </div>
              <div>
                <Label>Descrição</Label>
                <Textarea
                  value={config?.textos?.descricao_equipes || ''}
                  onChange={(e) => updateConfig('textos.descricao_equipes', e.target.value)}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Configurações Gerais */}
        <TabsContent value="gerais" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Configurações Gerais</CardTitle>
              <CardDescription>Parâmetros gerais do sistema</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Label className="w-56">Prazo de submissão (dias):</Label>
                <Input
                  type="number"
                  min="1"
                  value={config?.configuracoes_gerais?.prazo_submissao_dias || 30}
                  onChange={(e) => updateConfig('configuracoes_gerais.prazo_submissao_dias', parseInt(e.target.value) || 30)}
                  className="w-20"
                />
                <span className="text-slate-500">dias</span>
              </div>
              <div className="flex items-center gap-3">
                <Label className="w-56">Mínimo de provas (Normal):</Label>
                <Input
                  type="number"
                  min="1"
                  value={config?.configuracoes_gerais?.minimo_provas_normal || 12}
                  onChange={(e) => updateConfig('configuracoes_gerais.minimo_provas_normal', parseInt(e.target.value) || 12)}
                  className="w-20"
                />
                <span className="text-slate-500">provas</span>
              </div>
              <div className="flex items-center gap-3">
                <Label className="w-56">Mínimo de provas (PCD):</Label>
                <Input
                  type="number"
                  min="1"
                  value={config?.configuracoes_gerais?.minimo_provas_pcd || 8}
                  onChange={(e) => updateConfig('configuracoes_gerais.minimo_provas_pcd', parseInt(e.target.value) || 8)}
                  className="w-20"
                />
                <span className="text-slate-500">provas</span>
              </div>
              <div className="flex items-center gap-3">
                <Label className="w-56">Pontos para Status Elite:</Label>
                <Input
                  type="number"
                  min="1"
                  value={config?.configuracoes_gerais?.pontos_status_elite || 100}
                  onChange={(e) => updateConfig('configuracoes_gerais.pontos_status_elite', parseInt(e.target.value) || 100)}
                  className="w-20"
                />
                <span className="text-slate-500">pts</span>
              </div>
            </CardContent>
          </Card>

          {/* Info de última atualização */}
          {config?.ultima_atualizacao && (
            <Alert className="bg-slate-50 border-slate-200">
              <CheckCircle className="w-4 h-4 text-slate-600" />
              <AlertDescription className="text-slate-600">
                Última atualização: {new Date(config.ultima_atualizacao).toLocaleString('pt-BR')}
                {config.atualizado_por && ` por ${config.atualizado_por}`}
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ConfiguracoesSistemaTab;
