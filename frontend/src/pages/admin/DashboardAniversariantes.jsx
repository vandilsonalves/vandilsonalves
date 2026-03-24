import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import {
  Clock, Cake, Send, Gift, Settings, ChevronLeft, ChevronRight
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

const getDiasNoMes = (mes, ano) => new Date(ano, mes, 0).getDate();
const getPrimeiroDiaSemana = (mes, ano) => new Date(ano, mes - 1, 1).getDay();

const DashboardAniversariantes = ({ token }) => {
  const [aniversariantesMes, setAniversariantesMes] = useState(null);
  const [mesCalendario, setMesCalendario] = useState(new Date().getMonth() + 1);
  const [anoCalendario, setAnoCalendario] = useState(new Date().getFullYear());
  const [diaSelecionado, setDiaSelecionado] = useState(null);
  const [mensagemPadrao, setMensagemPadrao] = useState('Feliz Aniversário! Que este novo ciclo traga muitas conquistas nas pistas. O Ranking Run Pró deseja a você muita saúde e velocidade!');
  const [atletasSelecionar, setAtletasSelecionar] = useState([]);
  const [loadingAniversariantes, setLoadingAniversariantes] = useState(false);
  const [envioAutomatico, setEnvioAutomatico] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);

  useEffect(() => {
    fetchAniversariantes();
    fetchConfigAniversario();
  }, [mesCalendario, anoCalendario]);

  const fetchAniversariantes = async () => {
    setLoadingAniversariantes(true);
    try {
      const response = await axios.get(`${API}/admin/aniversariantes`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { mes: mesCalendario, ano: anoCalendario }
      });
      setAniversariantesMes(response.data);
    } catch (error) {
      console.error('Erro ao buscar aniversariantes:', error);
    } finally {
      setLoadingAniversariantes(false);
    }
  };

  const fetchConfigAniversario = async () => {
    try {
      const response = await axios.get(`${API}/admin/aniversariantes/configuracao`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensagemPadrao(response.data.mensagem_padrao || '');
      setEnvioAutomatico(response.data.envio_automatico || false);
    } catch (error) {
      console.error('Erro ao buscar configuração:', error);
    }
  };

  const handleSalvarConfigAniversario = async () => {
    try {
      await axios.put(`${API}/admin/aniversariantes/configuracao`, {
        mensagem_padrao: mensagemPadrao, envio_automatico: envioAutomatico
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success(`Configurações salvas! Envio automático ${envioAutomatico ? 'ATIVADO' : 'DESATIVADO'}`);
      setShowConfigModal(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao salvar configuração');
    }
  };

  const handleEnviarAniversariosAgora = async () => {
    try {
      const response = await axios.post(`${API}/admin/aniversariantes/enviar-agora`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = response.data;
      toast.success(`${data.mensagens_enviadas} mensagem(s) enviada(s). ${data.ja_enviadas_anteriormente} já enviada(s) anteriormente.`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao enviar mensagens');
    }
  };

  const handleEnviarMensagemAniversario = async () => {
    if (atletasSelecionar.length === 0) { toast.error('Selecione pelo menos um atleta'); return; }
    try {
      await axios.post(`${API}/admin/aniversariantes/enviar-mensagem`, {
        atleta_ids: atletasSelecionar, mensagem: mensagemPadrao
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success(`Mensagem enviada para ${atletasSelecionar.length} atleta(s)!`);
      setAtletasSelecionar([]);
      setDiaSelecionado(null);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao enviar mensagem');
    }
  };

  const toggleAtletaSelecao = (atletaId) => {
    setAtletasSelecionar(prev => prev.includes(atletaId) ? prev.filter(id => id !== atletaId) : [...prev, atletaId]);
  };

  return (
    <div className="space-y-6" data-testid="dashboard-aniversariantes">
      {/* Config Card */}
      <Card className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/30 dark:to-purple-900/30 shadow-lg border-0">
        <CardContent className="py-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${envioAutomatico ? 'bg-emerald-100 dark:bg-emerald-900' : 'bg-slate-100 dark:bg-slate-800'}`}>
                <Clock className={`w-5 h-5 ${envioAutomatico ? 'text-emerald-600' : 'text-slate-500'}`} />
              </div>
              <div>
                <p className="font-medium">Envio Automático às 00:00</p>
                <p className={`text-sm ${envioAutomatico ? 'text-emerald-600' : 'text-slate-500'}`}>
                  {envioAutomatico ? 'Ativado - Mensagens são enviadas automaticamente' : 'Desativado'}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setShowConfigModal(true)} className="bg-white dark:bg-slate-800">
                <Settings className="w-4 h-4 mr-2" /> Configurar
              </Button>
              <Button onClick={handleEnviarAniversariosAgora} className="bg-pink-500 hover:bg-pink-600">
                <Send className="w-4 h-4 mr-2" /> Enviar Agora (Hoje)
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Calendar */}
      <Card className="bg-white dark:bg-slate-800 shadow-lg border-0">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Cake className="w-5 h-5 text-pink-500" /> Aniversariantes - {MESES[mesCalendario - 1]} {anoCalendario}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={() => { if (mesCalendario === 1) { setMesCalendario(12); setAnoCalendario(p => p - 1); } else setMesCalendario(p => p - 1); }}>
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="font-medium px-4">{MESES[mesCalendario - 1]} {anoCalendario}</span>
            <Button size="sm" variant="outline" onClick={() => { if (mesCalendario === 12) { setMesCalendario(1); setAnoCalendario(p => p + 1); } else setMesCalendario(p => p + 1); }}>
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loadingAniversariantes ? (
            <div className="text-center py-12">Carregando...</div>
          ) : aniversariantesMes && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-pink-50 dark:bg-pink-900/30 rounded-lg p-4 text-center">
                  <Gift className="w-8 h-8 mx-auto mb-2 text-pink-500" />
                  <div className="text-2xl font-bold text-pink-600">{aniversariantesMes.total_aniversariantes}</div>
                  <div className="text-sm text-slate-500">Aniversariantes</div>
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900 rounded-xl p-4">
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(dia => (
                    <div key={dia} className="text-center text-xs font-medium text-slate-500 py-2">{dia}</div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {Array.from({ length: getPrimeiroDiaSemana(mesCalendario, anoCalendario) }).map((_, i) => <div key={`empty-${i}`} className="aspect-square" />)}
                  {Array.from({ length: getDiasNoMes(mesCalendario, anoCalendario) }).map((_, i) => {
                    const dia = i + 1;
                    const aniversariantes = aniversariantesMes.calendario[dia] || [];
                    const hasAniversariantes = aniversariantes.length > 0;
                    const isHoje = new Date().getDate() === dia && new Date().getMonth() + 1 === mesCalendario && new Date().getFullYear() === anoCalendario;
                    return (
                      <div key={dia} className={`aspect-square rounded-lg flex flex-col items-center justify-center cursor-pointer transition-all
                        ${hasAniversariantes ? 'bg-pink-100 dark:bg-pink-900/50 hover:bg-pink-200 dark:hover:bg-pink-900' : 'hover:bg-slate-100 dark:hover:bg-slate-800'}
                        ${isHoje ? 'ring-2 ring-emerald-500' : ''} ${diaSelecionado === dia ? 'ring-2 ring-pink-500 bg-pink-200 dark:bg-pink-800' : ''}`}
                        onClick={() => hasAniversariantes && setDiaSelecionado(dia)} data-testid={`dia-${dia}`}>
                        <span className={`text-sm font-medium ${hasAniversariantes ? 'text-pink-600 dark:text-pink-300' : ''}`}>{dia}</span>
                        {hasAniversariantes && (
                          <div className="flex -space-x-1 mt-1">
                            {aniversariantes.slice(0, 3).map((a, idx) => (
                              <Avatar key={idx} className="w-5 h-5 border border-white">
                                <AvatarImage src={a.foto_url?.startsWith('http') ? a.foto_url : `${BACKEND_URL}${a.foto_url}`} />
                                <AvatarFallback className="bg-pink-500 text-white text-[8px]">{a.nome?.charAt(0)}</AvatarFallback>
                              </Avatar>
                            ))}
                            {aniversariantes.length > 3 && <div className="w-5 h-5 rounded-full bg-pink-500 text-white text-[8px] flex items-center justify-center border border-white">+{aniversariantes.length - 3}</div>}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {diaSelecionado && aniversariantesMes.calendario[diaSelecionado]?.length > 0 && (
                <div className="mt-6 p-4 bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/30 dark:to-purple-900/30 rounded-xl">
                  <h4 className="font-semibold mb-4 flex items-center gap-2">
                    <Cake className="w-5 h-5 text-pink-500" /> Aniversariantes do dia {diaSelecionado}
                  </h4>
                  <div className="space-y-3 mb-4">
                    {aniversariantesMes.calendario[diaSelecionado].map((atleta) => (
                      <div key={atleta.id} className={`flex items-center gap-3 p-3 bg-white dark:bg-slate-800 rounded-lg cursor-pointer transition-all ${atletasSelecionar.includes(atleta.id) ? 'ring-2 ring-pink-500' : ''}`}
                        onClick={() => toggleAtletaSelecao(atleta.id)}>
                        <input type="checkbox" checked={atletasSelecionar.includes(atleta.id)} onChange={() => {}} className="rounded border-pink-300" />
                        <Avatar className="w-10 h-10">
                          <AvatarImage src={atleta.foto_url?.startsWith('http') ? atleta.foto_url : `${BACKEND_URL}${atleta.foto_url}`} />
                          <AvatarFallback className="bg-pink-500 text-white">{atleta.nome?.charAt(0)}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <p className="font-medium">{atleta.nome}</p>
                          <p className="text-sm text-slate-500">{atleta.equipe} - {atleta.idade} anos</p>
                        </div>
                        <Badge className="bg-pink-100 text-pink-700 border-0">{atleta.apelido || 'Atleta'}</Badge>
                      </div>
                    ))}
                  </div>
                  <div className="space-y-3">
                    <Label>Mensagem de Felicitação</Label>
                    <Textarea value={mensagemPadrao} onChange={(e) => setMensagemPadrao(e.target.value)} placeholder="Escreva sua mensagem de aniversário..." rows={3} className="bg-white dark:bg-slate-800" />
                    <div className="flex gap-2">
                      <Button onClick={handleEnviarMensagemAniversario} className="bg-pink-500 hover:bg-pink-600" disabled={atletasSelecionar.length === 0}>
                        <Send className="w-4 h-4 mr-2" /> Enviar para {atletasSelecionar.length} atleta(s)
                      </Button>
                      <Button variant="outline" onClick={() => setAtletasSelecionar(aniversariantesMes.calendario[diaSelecionado].map(a => a.id))}>
                        Selecionar Todos
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Config Modal */}
      <Dialog open={showConfigModal} onOpenChange={setShowConfigModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Settings className="w-5 h-5 text-pink-500" /> Configurações de Aniversário</DialogTitle>
          </DialogHeader>
          <div className="space-y-6">
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
              <div>
                <p className="font-medium">Envio Automático às 00:00</p>
                <p className="text-sm text-slate-500">Quando ativado, mensagens são enviadas automaticamente à meia-noite para os aniversariantes do dia.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked={envioAutomatico} onChange={(e) => setEnvioAutomatico(e.target.checked)} className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 dark:peer-focus:ring-pink-800 rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-pink-500"></div>
              </label>
            </div>
            <div className="space-y-2">
              <Label>Mensagem Padrão de Felicitação</Label>
              <Textarea value={mensagemPadrao} onChange={(e) => setMensagemPadrao(e.target.value)} placeholder="Escreva a mensagem padrão de aniversário..." rows={4} className="bg-slate-50 dark:bg-slate-900" />
              <p className="text-xs text-slate-500">Esta mensagem será usada tanto no envio automático quanto no envio manual.</p>
            </div>
            <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg text-sm text-blue-700 dark:text-blue-300">
              <p className="font-medium mb-1">Como funciona:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>O sistema verifica diariamente os aniversariantes às 00:00</li>
                <li>Cada atleta recebe apenas 1 mensagem por ano</li>
                <li>O atleta vê a mensagem em formato de popup ao abrir o app</li>
                <li>Após visualizar, a mensagem não aparece novamente</li>
              </ul>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfigModal(false)}>Cancelar</Button>
            <Button onClick={handleSalvarConfigAniversario} className="bg-pink-500 hover:bg-pink-600">Salvar Configurações</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardAniversariantes;
