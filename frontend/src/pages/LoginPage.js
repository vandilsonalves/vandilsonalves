import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { LogIn, KeyRound, Loader2, CheckCircle2 } from 'lucide-react';
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

  // Estados do modal de recuperação de senha
  const [showRecuperarModal, setShowRecuperarModal] = useState(false);
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

  const handleRecuperarSenha = async () => {
    if (!emailRecuperar || !emailRecuperar.includes('@')) {
      toast.error('Digite um email válido');
      return;
    }

    setRecuperarLoading(true);
    try {
      await axios.post(`${API}/auth/recuperar-senha`, { email: emailRecuperar });
      setRecuperarSucesso(true);
    } catch (err) {
      toast.error('Erro ao processar solicitação. Tente novamente.');
    } finally {
      setRecuperarLoading(false);
    }
  };

  const fecharModalRecuperar = () => {
    setShowRecuperarModal(false);
    setEmailRecuperar('');
    setRecuperarSucesso(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950 dark:to-green-950 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
            Ranking Run Pró
          </CardTitle>
          <p className="text-slate-600 dark:text-slate-400 mt-2">Faça login para continuar</p>
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
                placeholder="••••••••"
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
                Não tem conta?{' '}
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
      <Dialog open={showRecuperarModal} onOpenChange={fecharModalRecuperar}>
        <DialogContent className="max-w-sm" data-testid="modal-recuperar-senha">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <KeyRound className="w-5 h-5 text-emerald-600" />
              Recuperar Senha
            </DialogTitle>
            <DialogDescription>
              Informe seu email cadastrado. Enviaremos uma nova senha para você.
            </DialogDescription>
          </DialogHeader>

          {!recuperarSucesso ? (
            <div className="space-y-4 py-2">
              <div>
                <Label htmlFor="email-recuperar">Email</Label>
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
                <Button variant="outline" onClick={fecharModalRecuperar}>
                  Cancelar
                </Button>
                <Button
                  onClick={handleRecuperarSenha}
                  disabled={recuperarLoading}
                  className="bg-emerald-600 hover:bg-emerald-700"
                  data-testid="btn-enviar-recuperar"
                >
                  {recuperarLoading ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <KeyRound className="w-4 h-4 mr-2" />
                  )}
                  {recuperarLoading ? 'Enviando...' : 'Enviar Nova Senha'}
                </Button>
              </DialogFooter>
            </div>
          ) : (
            <div className="py-4 text-center space-y-3" data-testid="recuperar-sucesso">
              <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto" />
              <p className="text-base font-semibold text-emerald-700">
                Nova senha enviada!
              </p>
              <p className="text-sm text-slate-500">
                Verifique seu email <strong>{emailRecuperar}</strong>. 
                A nova senha foi enviada para você.
              </p>
              <Button
                onClick={fecharModalRecuperar}
                className="mt-2 bg-emerald-600 hover:bg-emerald-700"
              >
                Voltar ao Login
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LoginPage;
