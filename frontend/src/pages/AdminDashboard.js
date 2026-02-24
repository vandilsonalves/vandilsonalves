import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { CheckCircle, XCircle, ExternalLink, Calendar, MapPin, Trophy, Clock, ArrowLeft } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, token, isAdmin } = useAuth();
  const [pendentes, setPendentes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showReprovarModal, setShowReprovarModal] = useState(false);
  const [selectedResultado, setSelectedResultado] = useState(null);
  const [motivoReprovacao, setMotivoReprovacao] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (!isAdmin) {
      navigate('/');
      return;
    }
    fetchPendentes();
  }, [isAdmin]);

  const fetchPendentes = async () => {
    try {
      const response = await axios.get(`${API}/admin/pendentes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendentes(response.data);
    } catch (error) {
      console.error('Erro ao buscar pendentes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAprovar = async (resultadoId) => {
    if (!window.confirm('Confirma a aprovação deste resultado?')) return;

    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/aprovar/${resultadoId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Resultado aprovado com sucesso!');
      fetchPendentes();
    } catch (error) {
      alert(error.response?.data?.detail || 'Erro ao aprovar');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReprovar = async () => {
    setActionLoading(true);
    try {
      await axios.post(
        `${API}/admin/reprovar/${selectedResultado.id}`,
        { motivo: motivoReprovacao },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      alert('Resultado reprovado');
      setShowReprovarModal(false);
      setMotivoReprovacao('');
      setSelectedResultado(null);
      fetchPendentes();
    } catch (error) {
      alert(error.response?.data?.detail || 'Erro ao reprovar');
    } finally {
      setActionLoading(false);
    }
  };

  if (!isAdmin) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-8 px-4">
      <div className="container mx-auto max-w-7xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Dashboard Admin</h1>
            <p className="text-slate-600 mt-1">Gerenciar aprovações de resultados</p>
          </div>
          <Button onClick={() => navigate('/')} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar ao Ranking
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12">Carregando...</div>
        ) : pendentes.length === 0 ? (
          <Alert className="bg-emerald-50 border-emerald-200">
            <AlertDescription className="text-emerald-700">
              ✓ Não há resultados pendentes de aprovação.
            </AlertDescription>
          </Alert>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {pendentes.map((resultado) => (
              <Card key={resultado.id} className="shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-xl text-slate-900">
                        {resultado.nome_competicao}
                      </CardTitle>
                      <p className="text-sm text-slate-600 mt-1">
                        <strong>Atleta:</strong> {resultado.atleta_nome} ({resultado.atleta_equipe})
                      </p>
                      <Badge variant="outline" className="mt-2">
                        {resultado.atleta_categoria.toUpperCase()}
                      </Badge>
                    </div>
                    <Badge className="bg-amber-500">Pendente</Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-6 space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <Trophy className="w-4 h-4 text-amber-600" />
                      <span><strong>Colocação:</strong> {resultado.colocacao}º</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-blue-600" />
                      <span><strong>Tempo:</strong> {resultado.tempo}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-emerald-600" />
                      <span>{resultado.cidade_competicao}/{resultado.estado_competicao}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-slate-600" />
                      <span>{new Date(resultado.data_competicao).toLocaleDateString('pt-BR')}</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t">
                    <p className="text-sm"><strong>Distância:</strong> {resultado.distancia}</p>
                    <p className="text-sm mt-1">
                      <strong>Link:</strong>{' '}
                      <a
                        href={resultado.link_resultado}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline inline-flex items-center gap-1"
                      >
                        Ver resultado <ExternalLink className="w-3 h-3" />
                      </a>
                    </p>
                    {resultado.foto_podio_url && (
                      <div className="mt-3">
                        <p className="text-sm font-semibold mb-2">Foto do Pódio:</p>
                        <img
                          src={`${BACKEND_URL}${resultado.foto_podio_url}`}
                          alt="Pódio"
                          className="w-full h-48 object-cover rounded-lg border"
                        />
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2 pt-4">
                    <Button
                      onClick={() => handleAprovar(resultado.id)}
                      disabled={actionLoading}
                      className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Aprovar
                    </Button>
                    <Button
                      onClick={() => {
                        setSelectedResultado(resultado);
                        setShowReprovarModal(true);
                      }}
                      disabled={actionLoading}
                      variant="destructive"
                      className="flex-1"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Reprovar
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Modal de Reprovação */}
        <Dialog open={showReprovarModal} onOpenChange={setShowReprovarModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Reprovar Resultado</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <p className="text-sm text-slate-600">
                Informe o motivo da reprovação (será enviado ao atleta):
              </p>
              <Textarea
                value={motivoReprovacao}
                onChange={(e) => setMotivoReprovacao(e.target.value)}
                placeholder="Ex: Resultado não encontrado no link fornecido, foto ilegível, etc."
                rows={4}
              />
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setShowReprovarModal(false);
                  setMotivoReprovacao('');
                }}
              >
                Cancelar
              </Button>
              <Button
                variant="destructive"
                onClick={handleReprovar}
                disabled={actionLoading}
              >
                Reprovar
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default AdminDashboard;
