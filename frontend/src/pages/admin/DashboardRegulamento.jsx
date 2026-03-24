import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText, RefreshCw, CheckCircle, Eye, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardRegulamento = ({ token }) => {
  const [regulamento, setRegulamento] = useState({ titulo: '', conteudo: '' });
  const [loadingRegulamento, setLoadingRegulamento] = useState(false);
  const [savingRegulamento, setSavingRegulamento] = useState(false);

  useEffect(() => { fetchRegulamento(); }, []);

  const fetchRegulamento = async () => {
    setLoadingRegulamento(true);
    try {
      const response = await axios.get(`${API}/admin/regulamento`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRegulamento(response.data);
    } catch (error) {
      console.error('Erro ao buscar regulamento:', error);
      toast.error('Erro ao carregar regulamento');
    } finally {
      setLoadingRegulamento(false);
    }
  };

  const handleSaveRegulamento = async () => {
    if (!regulamento.titulo.trim() || !regulamento.conteudo.trim()) {
      toast.error('Preencha o título e o conteúdo do regulamento');
      return;
    }
    setSavingRegulamento(true);
    try {
      const formData = new FormData();
      formData.append('titulo', regulamento.titulo);
      formData.append('conteudo', regulamento.conteudo);
      await axios.put(`${API}/admin/regulamento/form`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Regulamento salvo com sucesso!');
      fetchRegulamento();
    } catch (error) {
      console.error('Erro ao salvar regulamento:', error);
      toast.error('Erro ao salvar regulamento');
    } finally {
      setSavingRegulamento(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="dashboard-regulamento">
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
        <CardHeader className="border-b dark:border-slate-700">
          <CardTitle className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <FileText className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <span>Gerenciar Regulamento</span>
              {regulamento.ultima_atualizacao && (
                <p className="text-xs text-slate-400 font-normal mt-1">
                  Última atualização: {new Date(regulamento.ultima_atualizacao).toLocaleString('pt-BR')}
                  {regulamento.atualizado_por && ` por ${regulamento.atualizado_por}`}
                </p>
              )}
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {loadingRegulamento ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : (
            <div className="space-y-6">
              <Alert className="bg-blue-50 dark:bg-blue-900/20 border-blue-200">
                <AlertDescription className="text-blue-700 dark:text-blue-300">
                  <strong>Dica:</strong> Use formatação Markdown para estruturar o regulamento:
                  <ul className="list-disc list-inside mt-2 text-sm">
                    <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">## Título</code> para títulos de seção</li>
                    <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">### Subtítulo</code> para subtítulos</li>
                    <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">- Item</code> para listas</li>
                    <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">**texto**</code> para negrito</li>
                    <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">---</code> para linha horizontal</li>
                  </ul>
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label htmlFor="reg-titulo" className="text-slate-700 dark:text-slate-300">Título do Regulamento</Label>
                <Input id="reg-titulo" value={regulamento.titulo} onChange={(e) => setRegulamento({ ...regulamento, titulo: e.target.value })} placeholder="Ex: Regulamento Oficial do Ranking Run Pró" className="bg-slate-50 dark:bg-slate-900" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="reg-conteudo" className="text-slate-700 dark:text-slate-300">Conteúdo do Regulamento</Label>
                <Textarea id="reg-conteudo" value={regulamento.conteudo} onChange={(e) => setRegulamento({ ...regulamento, conteudo: e.target.value })} placeholder="Digite o conteúdo do regulamento aqui..." className="bg-slate-50 dark:bg-slate-900 min-h-[400px] font-mono text-sm" />
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={fetchRegulamento} disabled={loadingRegulamento}>
                  <RefreshCw className={`w-4 h-4 mr-2 ${loadingRegulamento ? 'animate-spin' : ''}`} /> Recarregar
                </Button>
                <Button onClick={handleSaveRegulamento} disabled={savingRegulamento} className="bg-emerald-600 hover:bg-emerald-700">
                  {savingRegulamento ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <CheckCircle className="w-4 h-4 mr-2" />}
                  Salvar Regulamento
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Preview */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
        <CardHeader className="border-b dark:border-slate-700">
          <CardTitle className="text-base flex items-center gap-2">
            <Eye className="w-4 h-4 text-slate-400" /> Pré-visualização
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-6 max-h-[400px] overflow-y-auto">
            <h2 className="text-xl font-bold text-emerald-600 mb-4">{regulamento.titulo || 'Título do Regulamento'}</h2>
            <div className="text-slate-700 dark:text-slate-300 space-y-2 whitespace-pre-wrap">
              {regulamento.conteudo ? (
                regulamento.conteudo.split('\n').map((line, i) => {
                  if (line.startsWith('### ')) return <h3 key={i} className="text-lg font-semibold text-emerald-500 mt-4 mb-2">{line.replace('### ', '')}</h3>;
                  if (line.startsWith('## ')) return <h2 key={i} className="text-xl font-bold text-emerald-600 mt-6 mb-3">{line.replace('## ', '')}</h2>;
                  if (line.startsWith('---')) return <hr key={i} className="my-4 border-slate-300 dark:border-slate-600" />;
                  if (line.startsWith('- ')) return <div key={i} className="flex gap-2 ml-4"><span className="text-emerald-500">•</span>{line.replace('- ', '')}</div>;
                  if (line.trim() === '') return <div key={i} className="h-2"></div>;
                  return <p key={i}>{line}</p>;
                })
              ) : (
                <p className="text-slate-400 italic">O conteúdo do regulamento aparecerá aqui...</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardRegulamento;
