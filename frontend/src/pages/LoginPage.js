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
const WHATSAPP_SUPORTE = '5577998626875';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Modal de recuperação
  const [showRecuperarModal, setShowRecuperarModal] = useState(false);
  const [metodoRecuperacao, setMetodoRecuperacao] = useState(null);
  const [emailRecuperar, setEmailRecuperar] = useState('');
  const [recuperarLoading, setRecuperarLoading] = useState(false);
  const [recuperarSucesso, setRecuperarSucesso] = useState(false);

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
      toast.error('Digite um email valido');
      return;
    }
    setRecuperarLoading(true);
    try {
      await axios.post(`${API}/auth/recuperar-senha`, { email: emailRecuperar });
      setRecuperarSucesso(true);
    } catch {
      toast.error('Erro ao processar. Tente novamente.');
    } finally {
      setRecuperarLoading(false);
    }
  };

  const handleRecuperarWhatsApp = () => {
    const emailMsg = emailRecuperar || email || '[seu email aqui]';
    const mensagem = encodeURIComponent(
      `Ola! Esqueci minha senha do Ranking Run.\n\nMeu email cadastrado e: ${emailMsg}\n\nPoderia me ajudar a recuperar?`
    );
    window.open(`https://wa.me/${WHATSAPP_SUPORTE}?text=${mensagem}`, '_blank');
  };

  const fecharModal = () => {
    setShowRecuperarModal(false);
    setMetodoRecuperacao(null);
    setEmailRecuperar('');
    setRecuperarSucesso(false);
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
                Como voce prefere recuperar sua senha?
              </DialogDescription>
            )}
          </DialogHeader>

          {/* Sucesso (email) */}
          {recuperarSucesso && (
            <div className="py-4 text-center space-y-3" data-testid="recuperar-sucesso">
              <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto" />
              <p className="text-base font-semibold text-emerald-700">Nova senha enviada!</p>
              <p className="text-sm text-slate-500">
                Verifique seu email <strong>{emailRecuperar}</strong>.
              </p>
              <Button onClick={fecharModal} className="mt-2 bg-emerald-600 hover:bg-emerald-700">
                Voltar ao Login
              </Button>
            </div>
          )}

          {/* Escolha do método */}
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
                onClick={handleRecuperarWhatsApp}
                className="w-full flex items-center gap-4 p-4 rounded-xl border-2 border-slate-200 hover:border-green-400 hover:bg-green-50 transition-all group"
                data-testid="btn-recuperar-whatsapp"
              >
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center group-hover:bg-green-200 transition-colors">
                  <Phone className="w-6 h-6 text-green-600" />
                </div>
                <div className="text-left">
                  <p className="font-semibold text-slate-800">Recuperar via WhatsApp</p>
                  <p className="text-xs text-slate-500">Fale com o suporte pelo WhatsApp</p>
                </div>
              </button>
            </div>
          )}

          {/* Formulário Email */}
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
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LoginPage;
