import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { LogIn, KeyRound, Loader2, CheckCircle2, Phone, Mail, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Modal de recuperação
  const [showRecuperarModal, setShowRecuperarModal] = useState(false);
  const [metodoRecuperacao, setMetodoRecuperacao] = useState(null); // 'email' | 'whatsapp' | null
  const [emailRecuperar, setEmailRecuperar] = useState('');
  const [telefoneRecuperar, setTelefoneRecuperar] = useState('');
  const [recuperarLoading, setRecuperarLoading] = useState(false);
  const [recuperarSucesso, setRecuperarSucesso] = useState(false);
  const [recuperarMensagem, setRecuperarMensagem] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const userData = await login(email, password);
      if (userData.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  const handleRecuperarEmail = async () => {
    if (!emailRecuperar || !emailRecuperar.includes('@')) {
      toast.error('Digite um email válido');
      return;
    }
    setRecuperarLoading(true);
    try {
      const res = await axios.post(`${API}/auth/recuperar-senha`, { email: emailRecuperar });
      setRecuperarSucesso(true);
      setRecuperarMensagem(res.data.message);
    } catch {
      toast.error('Erro ao processar. Tente novamente.');
    } finally {
      setRecuperarLoading(false);
    }
  };

  const handleRecuperarWhatsApp = async () => {
    const nums = telefoneRecuperar.replace(/\D/g, '');
    if (nums.length < 10) {
      toast.error('Digite um telefone válido com DDD');
      return;
    }
    setRecuperarLoading(true);
    try {
      const res = await axios.post(`${API}/auth/recuperar-senha-whatsapp`, { telefone: telefoneRecuperar });
      if (res.data.success) {
        setRecuperarSucesso(true);
        setRecuperarMensagem(res.data.message);
      } else {
        toast.error(res.data.message || 'Erro ao enviar via WhatsApp. Tente por email.');
      }
    } catch {
      toast.error('Erro ao processar. Tente por email.');
    } finally {
      setRecuperarLoading(false);
    }
  };

  const fecharModal = () => {
    setShowRecuperarModal(false);
    setMetodoRecuperacao(null);
    setEmailRecuperar('');
    setTelefoneRecuperar('');
    setRecuperarSucesso(false);
    setRecuperarMensagem('');
  };

  const formatarTelefone = (value) => {
    const nums = value.replace(/\D/g, '');
    if (nums.length <= 2) return `(${nums}`;
    if (nums.length <= 7) return `(${nums.slice(0, 2)}) ${nums.slice(2)}`;
    return `(${nums.slice(0, 2)}) ${nums.slice(2, 7)}-${nums.slice(7, 11)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950 dark:to-green-950 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
            Ranking Run Pro
          </CardTitle>
          <p className="text-slate-600 dark:text-slate-400 mt-2">Faca login para continuar</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="input-email"
              />
            </div>

            <div>
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                placeholder="........"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                data-testid="input-password"
              />
            </div>

            <div className="text-right">
              <button
                type="button"
                onClick={() => {
                  setEmailRecuperar(email);
                  setShowRecuperarModal(true);
                }}
                className="text-sm text-emerald-600 hover:text-emerald-700 hover:underline font-medium"
                data-testid="btn-esqueci-senha"
              >
                Esqueci minha senha
              </button>
            </div>

            <Button
              type="submit"
              className="w-full bg-emerald-600 hover:bg-emerald-700"
              disabled={loading}
              data-testid="btn-login"
            >
              <LogIn className="w-4 h-4 mr-2" />
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>

            <div className="text-center mt-4">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Nao tem conta?{' '}
                <Link to="/cadastro" className="text-emerald-600 hover:underline font-semibold">
                  Cadastre-se aqui
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

      {/* Modal Recuperar Senha */}
      <Dialog open={showRecuperarModal} onOpenChange={fecharModal}>
        <DialogContent className="max-w-sm" data-testid="modal-recuperar-senha">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <KeyRound className="w-5 h-5 text-emerald-600" />
              Recuperar Senha
            </DialogTitle>
            {!metodoRecuperacao && !recuperarSucesso && (
              <DialogDescription>
                Como voce prefere receber sua nova senha?
              </DialogDescription>
            )}
          </DialogHeader>

          {/* Estado: Sucesso */}
          {recuperarSucesso && (
            <div className="py-4 text-center space-y-3" data-testid="recuperar-sucesso">
              <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto" />
              <p className="text-base font-semibold text-emerald-700">Nova senha enviada!</p>
              <p className="text-sm text-slate-500">
                {metodoRecuperacao === 'email'
                  ? <>Verifique seu email <strong>{emailRecuperar}</strong>.</>
                  : <>Verifique seu WhatsApp <strong>{telefoneRecuperar}</strong>.</>
                }
              </p>
              <Button onClick={fecharModal} className="mt-2 bg-emerald-600 hover:bg-emerald-700">
                Voltar ao Login
              </Button>
            </div>
          )}

          {/* Estado: Escolha do método */}
          {!metodoRecuperacao && !recuperarSucesso && (
            <div className="space-y-3 py-2">
              <button
                onClick={() => setMetodoRecuperacao('email')}
                className="w-full flex items-center gap-4 p-4 rounded-xl border-2 border-slate-200 hover:border-emerald-400 hover:bg-emerald-50 transition-all group"
                data-testid="btn-recuperar-email"
              >
                <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center group-hover:bg-emerald-200 transition-colors">
                  <Mail className="w-6 h-6 text-emerald-600" />
                </div>
                <div className="text-left">
                  <p className="font-semibold text-slate-800">Recuperar por Email</p>
                  <p className="text-xs text-slate-500">Receba a nova senha no seu email cadastrado</p>
                </div>
              </button>

              <button
                onClick={() => setMetodoRecuperacao('whatsapp')}
                className="w-full flex items-center gap-4 p-4 rounded-xl border-2 border-slate-200 hover:border-green-400 hover:bg-green-50 transition-all group"
                data-testid="btn-recuperar-whatsapp"
              >
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center group-hover:bg-green-200 transition-colors">
                  <Phone className="w-6 h-6 text-green-600" />
                </div>
                <div className="text-left">
                  <p className="font-semibold text-slate-800">Recuperar via WhatsApp</p>
                  <p className="text-xs text-slate-500">Receba a nova senha direto no seu WhatsApp</p>
                </div>
              </button>
            </div>
          )}

          {/* Estado: Formulário Email */}
          {metodoRecuperacao === 'email' && !recuperarSucesso && (
            <div className="space-y-4 py-2">
              <button
                onClick={() => setMetodoRecuperacao(null)}
                className="text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1"
              >
                <ArrowLeft className="w-3 h-3" /> Voltar
              </button>
              <div>
                <Label htmlFor="email-recuperar">Email cadastrado</Label>
                <Input
                  id="email-recuperar"
                  type="email"
                  placeholder="seu@email.com"
                  value={emailRecuperar}
                  onChange={(e) => setEmailRecuperar(e.target.value)}
                  data-testid="input-email-recuperar"
                />
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={fecharModal}>Cancelar</Button>
                <Button
                  onClick={handleRecuperarEmail}
                  disabled={recuperarLoading}
                  className="bg-emerald-600 hover:bg-emerald-700"
                  data-testid="btn-enviar-recuperar-email"
                >
                  {recuperarLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Mail className="w-4 h-4 mr-2" />}
                  {recuperarLoading ? 'Enviando...' : 'Enviar por Email'}
                </Button>
              </DialogFooter>
            </div>
          )}

          {/* Estado: Formulário WhatsApp */}
          {metodoRecuperacao === 'whatsapp' && !recuperarSucesso && (
            <div className="space-y-4 py-2">
              <button
                onClick={() => setMetodoRecuperacao(null)}
                className="text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1"
              >
                <ArrowLeft className="w-3 h-3" /> Voltar
              </button>
              <div>
                <Label htmlFor="telefone-recuperar">Telefone com DDD</Label>
                <Input
                  id="telefone-recuperar"
                  type="tel"
                  placeholder="(11) 99999-9999"
                  value={telefoneRecuperar}
                  onChange={(e) => setTelefoneRecuperar(formatarTelefone(e.target.value))}
                  maxLength={15}
                  data-testid="input-telefone-recuperar"
                />
                <p className="text-xs text-slate-400 mt-1">Informe o telefone cadastrado na sua conta</p>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={fecharModal}>Cancelar</Button>
                <Button
                  onClick={handleRecuperarWhatsApp}
                  disabled={recuperarLoading}
                  className="bg-green-600 hover:bg-green-700"
                  data-testid="btn-enviar-recuperar-whatsapp"
                >
                  {recuperarLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Phone className="w-4 h-4 mr-2" />}
                  {recuperarLoading ? 'Enviando...' : 'Enviar via WhatsApp'}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LoginPage;
