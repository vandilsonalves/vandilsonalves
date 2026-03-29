import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Send, Loader2, Clock, Users, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DashboardResumoSemanal = ({ token }) => {
  const [disparando, setDisparando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [historico, setHistorico] = useState([]);
  const [loadingHist, setLoadingHist] = useState(true);

  useEffect(() => {
    fetchHistorico();
  }, []);

  const fetchHistorico = async () => {
    setLoadingHist(true);
    try {
      const res = await axios.get(`${API}/admin/resumo-semanal/historico`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setHistorico(res.data.historico || []);
    } catch {
      setHistorico([]);
    } finally {
      setLoadingHist(false);
    }
  };

  const handleDisparar = async () => {
    setDisparando(true);
    setResultado(null);
    try {
      const res = await axios.post(`${API}/admin/resumo-semanal/disparar`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResultado(res.data.resultado);
      toast.success(`Resumo enviado para ${res.data.resultado.enviados} atletas!`);
      fetchHistorico();
    } catch (err) {
      toast.error('Erro ao disparar resumo semanal');
    } finally {
      setDisparando(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="dashboard-resumo-semanal">
      {/* Header */}
      <Card className="bg-gradient-to-r from-emerald-600 to-teal-600 border-0 text-white">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">Resumo Semanal para Atletas</h2>
              <p className="text-emerald-100 mt-1 text-sm">
                Envia uma notificacao personalizada para cada atleta com destaques da semana: corridas, pontos e posicao no ranking.
              </p>
              <div className="flex items-center gap-2 mt-3">
                <Clock className="w-4 h-4 text-emerald-200" />
                <span className="text-emerald-100 text-xs">Envio automatico: toda segunda-feira as 08:00</span>
              </div>
            </div>
            <Button
              onClick={handleDisparar}
              disabled={disparando}
              className="bg-white text-emerald-700 hover:bg-emerald-50 font-semibold px-6"
              data-testid="btn-disparar-resumo"
            >
              {disparando ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Enviando...</>
              ) : (
                <><Send className="w-4 h-4 mr-2" /> Disparar Agora</>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Resultado do disparo */}
      {resultado && (
        <Card className="bg-slate-800 border-emerald-500/30 border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <span className="text-white font-medium">Disparo concluido!</span>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-3">
              <div className="bg-slate-700 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-emerald-400">{resultado.enviados}</div>
                <div className="text-xs text-slate-400">Enviados</div>
              </div>
              <div className="bg-slate-700 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-white">{resultado.total}</div>
                <div className="text-xs text-slate-400">Total Atletas</div>
              </div>
              <div className="bg-slate-700 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-red-400">{resultado.erros}</div>
                <div className="text-xs text-slate-400">Erros</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Preview da notificacao */}
      <Card className="bg-slate-800 border-0">
        <CardHeader>
          <CardTitle className="text-white text-base">Preview da Notificacao</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
            <div className="flex items-center gap-2 mb-3">
              <Badge className="bg-emerald-600 text-white text-xs">Resumo Semanal</Badge>
            </div>
            <p className="text-white font-medium mb-2">Seu Resumo Semanal</p>
            <div className="text-slate-300 text-sm space-y-1 whitespace-pre-line">
              <p>Ola, [Nome]! Aqui esta seu resumo da semana:</p>
              <p></p>
              <p>Corridas na semana: X corridas</p>
              <p>Pontos ganhos: +Y</p>
              <p>Total de corridas: Z</p>
              <p>Pontos acumulados: W</p>
              <p>Posicao no ranking: #N</p>
              <p></p>
              <p>Continue firme! Cada corrida conta.</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Historico */}
      <Card className="bg-slate-800 border-0">
        <CardHeader>
          <CardTitle className="text-white text-base flex items-center gap-2">
            <Clock className="w-4 h-4" /> Historico de Disparos
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingHist ? (
            <div className="flex justify-center py-6">
              <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            </div>
          ) : historico.length === 0 ? (
            <p className="text-slate-500 text-center py-4 text-sm">Nenhum disparo registrado ainda.</p>
          ) : (
            <div className="space-y-2">
              {historico.map((h, i) => (
                <div key={i} className="flex items-center justify-between bg-slate-700/50 rounded-lg p-3">
                  <div className="flex items-center gap-3">
                    <Users className="w-4 h-4 text-slate-400" />
                    <div>
                      <span className="text-white text-sm">{h.enviados}/{h.total_atletas} atletas</span>
                      {h.erros > 0 && (
                        <span className="text-red-400 text-xs ml-2">({h.erros} erros)</span>
                      )}
                    </div>
                  </div>
                  <span className="text-slate-400 text-xs">
                    {new Date(h.data).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardResumoSemanal;
