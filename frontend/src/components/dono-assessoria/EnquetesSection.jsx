import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { BarChart3, Plus, X, Loader2, Check, Lock } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const EnquetesSection = ({ token, userId, isDonoAssessoria }) => {
  const [enquetes, setEnquetes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchEnquetes = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/equipe/enquetes`, { headers });
      setEnquetes(res.data.enquetes || []);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchEnquetes(); }, [fetchEnquetes]);

  const votar = async (enqueteId, opcaoIdx) => {
    try {
      const res = await axios.post(`${API}/equipe/enquete/${enqueteId}/votar?opcao_idx=${opcaoIdx}`, {}, { headers });
      setEnquetes(prev => prev.map(e => e.id === enqueteId ? res.data.enquete : e));
    } catch (e) { toast.error(e.response?.data?.detail || 'Erro ao votar'); }
  };

  const encerrar = async (enqueteId) => {
    try {
      await axios.post(`${API}/equipe/enquete/${enqueteId}/encerrar`, {}, { headers });
      setEnquetes(prev => prev.map(e => e.id === enqueteId ? { ...e, ativa: false } : e));
      toast.success('Enquete encerrada');
    } catch (e) { toast.error('Erro ao encerrar'); }
  };

  if (loading) return null;
  if (enquetes.length === 0 && !isDonoAssessoria) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-violet-400" />
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Enquetes</h3>
        {isDonoAssessoria && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowForm(!showForm)}
            className="ml-auto text-violet-400 hover:text-violet-300 text-xs"
            data-testid="btn-nova-enquete"
          >
            <Plus className="w-3.5 h-3.5 mr-1" /> Nova Enquete
          </Button>
        )}
      </div>

      {showForm && <EnqueteForm token={token} headers={headers} onCreated={() => { setShowForm(false); fetchEnquetes(); }} onCancel={() => setShowForm(false)} />}

      {enquetes.map(enquete => (
        <EnqueteCard
          key={enquete.id}
          enquete={enquete}
          userId={userId}
          isDonoAssessoria={isDonoAssessoria}
          onVotar={votar}
          onEncerrar={encerrar}
        />
      ))}
    </div>
  );
};

const EnqueteForm = ({ token, headers, onCreated, onCancel }) => {
  const [pergunta, setPergunta] = useState('');
  const [opcoes, setOpcoes] = useState(['', '']);
  const [sending, setSending] = useState(false);

  const addOpcao = () => { if (opcoes.length < 6) setOpcoes([...opcoes, '']); };
  const removeOpcao = (i) => { if (opcoes.length > 2) setOpcoes(opcoes.filter((_, idx) => idx !== i)); };
  const updateOpcao = (i, val) => { const n = [...opcoes]; n[i] = val; setOpcoes(n); };

  const criar = async () => {
    if (!pergunta.trim() || opcoes.filter(o => o.trim()).length < 2) {
      toast.error('Preencha a pergunta e ao menos 2 opções');
      return;
    }
    setSending(true);
    try {
      await axios.post(`${API}/equipe/enquete/criar`, {
        pergunta: pergunta.trim(),
        opcoes: opcoes.filter(o => o.trim())
      }, { headers: { ...headers, 'Content-Type': 'application/json' } });
      toast.success('Enquete criada!');
      onCreated();
    } catch (e) { toast.error(e.response?.data?.detail || 'Erro'); }
    finally { setSending(false); }
  };

  return (
    <Card className="bg-violet-900/20 border-violet-500/30">
      <CardContent className="p-4 space-y-3">
        <Input
          value={pergunta}
          onChange={e => setPergunta(e.target.value)}
          placeholder="Qual a sua pergunta?"
          className="bg-slate-900 border-slate-700 text-white"
          data-testid="enquete-pergunta"
        />
        {opcoes.map((op, i) => (
          <div key={i} className="flex gap-2">
            <Input
              value={op}
              onChange={e => updateOpcao(i, e.target.value)}
              placeholder={`Opção ${i + 1}`}
              className="bg-slate-900 border-slate-700 text-white text-sm"
              data-testid={`enquete-opcao-${i}`}
            />
            {opcoes.length > 2 && (
              <Button variant="ghost" size="icon" onClick={() => removeOpcao(i)} className="text-red-400 shrink-0 h-10 w-10">
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        ))}
        <div className="flex gap-2">
          {opcoes.length < 6 && (
            <Button variant="outline" size="sm" onClick={addOpcao} className="text-xs border-violet-500 text-violet-300 bg-violet-600/20 hover:bg-violet-600/40 hover:text-white font-semibold" data-testid="btn-adicionar-opcao">
              <Plus className="w-3.5 h-3.5 mr-1" /> Adicionar opção
            </Button>
          )}
          <div className="flex-1" />
          <Button variant="outline" size="sm" onClick={onCancel} className="border-red-500/50 text-red-400 hover:bg-red-500/20 hover:text-red-300 font-semibold" data-testid="btn-cancelar-enquete">Cancelar</Button>
          <Button size="sm" onClick={criar} disabled={sending} className="bg-violet-600 hover:bg-violet-700" data-testid="btn-criar-enquete">
            {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Criar Enquete'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

const EnqueteCard = ({ enquete, userId, isDonoAssessoria, onVotar, onEncerrar }) => {
  const total = enquete.total_votos || 0;
  const votouEm = enquete.opcoes.findIndex(op => (op.votos || []).includes(userId));

  return (
    <Card className="bg-slate-800 border-slate-700" data-testid={`enquete-${enquete.id}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3 mb-3">
          <Avatar className="w-8 h-8 shrink-0">
            <AvatarImage src={enquete.autor_foto?.startsWith('http') ? enquete.autor_foto : `${BACKEND_URL}${enquete.autor_foto}`} />
            <AvatarFallback className="bg-violet-500 text-white text-xs">{enquete.autor_nome?.charAt(0)}</AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-white">{enquete.autor_nome}</span>
              <Badge variant="outline" className="text-violet-400 border-violet-500/40 text-[10px]">Enquete</Badge>
              {!enquete.ativa && <Badge className="bg-slate-600 text-[10px]">Encerrada</Badge>}
            </div>
            <p className="text-base font-medium text-white mt-1">{enquete.pergunta}</p>
          </div>
        </div>

        <div className="space-y-2">
          {enquete.opcoes.map((op, idx) => {
            const votos = (op.votos || []).length;
            const pct = total > 0 ? Math.round((votos / total) * 100) : 0;
            const isVoted = votouEm === idx;
            const hasVoted = votouEm >= 0;

            return (
              <button
                key={idx}
                onClick={() => enquete.ativa && onVotar(enquete.id, idx)}
                disabled={!enquete.ativa}
                className={`w-full relative overflow-hidden rounded-lg border transition-all text-left ${
                  isVoted
                    ? 'border-violet-500 bg-violet-900/30'
                    : 'border-slate-600 hover:border-slate-500 bg-slate-700/30'
                } ${!enquete.ativa ? 'cursor-default' : 'cursor-pointer'}`}
                data-testid={`enquete-opcao-btn-${enquete.id}-${idx}`}
              >
                {(hasVoted || !enquete.ativa) && (
                  <div
                    className={`absolute inset-y-0 left-0 transition-all duration-500 ${isVoted ? 'bg-violet-500/20' : 'bg-slate-600/20'}`}
                    style={{ width: `${pct}%` }}
                  />
                )}
                <div className="relative flex items-center justify-between px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    {isVoted && <Check className="w-4 h-4 text-violet-400" />}
                    <span className={`text-sm ${isVoted ? 'text-violet-300 font-semibold' : 'text-slate-200'}`}>
                      {op.texto}
                    </span>
                  </div>
                  {(hasVoted || !enquete.ativa) && (
                    <span className="text-xs text-slate-400 font-medium">{pct}%</span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-slate-500">{total} voto{total !== 1 ? 's' : ''}</span>
          {isDonoAssessoria && enquete.ativa && (
            <Button variant="ghost" size="sm" onClick={() => onEncerrar(enquete.id)} className="text-xs text-slate-500 hover:text-red-400" data-testid={`btn-encerrar-${enquete.id}`}>
              <Lock className="w-3 h-3 mr-1" /> Encerrar
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default EnquetesSection;
