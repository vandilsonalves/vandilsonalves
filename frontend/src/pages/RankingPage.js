import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import RankingTable from '@/components/RankingTable';
import { Search, HelpCircle, LogIn, Upload, FileDown, Shield, LogOut, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RankingPage = () => {
  const navigate = useNavigate();
  const { user, isAdmin, logout } = useAuth();
  const [categoriaAtual, setCategoriaAtual] = useState('masculino');
  const [rankingData, setRankingData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Filtros
  const [filtroNome, setFiltroNome] = useState('');
  const [filtroColocacao, setFiltroColocacao] = useState('');
  const [filtroUF, setFiltroUF] = useState('');

  // Buscar ranking
  useEffect(() => {
    const fetchRanking = async () => {
      setLoading(true);
      try {
        const url = `${API}/ranking/categoria/${categoriaAtual}/M?ano=2025`;
        const response = await axios.get(url);
        setRankingData(response.data);
      } catch (error) {
        console.error('Erro ao buscar ranking:', error);
        setRankingData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRanking();
  }, [categoriaAtual]);

  // Aplicar filtros
  const rankingFiltrado = rankingData.filter(atleta => {
    const nomeMatch = atleta.nome.toLowerCase().includes(filtroNome.toLowerCase());
    const colocacaoMatch = filtroColocacao === '' || atleta.colocacao === parseInt(filtroColocacao);
    const ufMatch = atleta.uf.toLowerCase().includes(filtroUF.toLowerCase());
    
    return nomeMatch && colocacaoMatch && ufMatch;
  });

  const handleAtletaClick = (atletaId) => {
    navigate(`/atleta/${atletaId}`);
  };

  const handleExport = (format) => {
    const url = `${API}/ranking/export/${format}?categoria=${categoriaAtual}`;
    window.open(url, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header com Login/Logout */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-emerald-600 dark:text-emerald-400 mb-2 tracking-tight">
              Ranking Run Pró
            </h1>
          </div>
          <div className="flex gap-2">
            {user ? (
              <>
                {isAdmin && (
                  <Button onClick={() => navigate('/admin')} variant="outline">
                    <Shield className="w-4 h-4 mr-2" />
                    Admin
                  </Button>
                )}
                <Button onClick={() => navigate('/submeter-resultado')} className="bg-emerald-600">
                  <Upload className="w-4 h-4 mr-2" />
                  Submeter Resultado
                </Button>
                <Button onClick={logout} variant="outline">
                  <LogOut className="w-4 h-4 mr-2" />
                  Sair
                </Button>
              </>
            ) : (
              <>
                <Button onClick={() => navigate('/cadastro')} variant="outline">
                  Cadastrar
                </Button>
                <Button onClick={() => navigate('/login')} className="bg-emerald-600">
                  <LogIn className="w-4 h-4 mr-2" />
                  Entrar
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Tabs de Categorias */}
        <Card className="mb-6 border-slate-200 dark:border-slate-800 shadow-lg">
          <CardContent className="pt-6">
            <Tabs value={categoriaAtual} onValueChange={setCategoriaAtual} className="w-full">
              <TabsList className="grid w-full grid-cols-2 lg:grid-cols-6 h-auto gap-1">
                <TabsTrigger value="masculino" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-masculino">
                  MASCULINO
                </TabsTrigger>
                <TabsTrigger value="feminino" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-feminino">
                  FEMININO
                </TabsTrigger>
                <TabsTrigger value="pcd-m" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-pcd-m">
                  PCD / M
                </TabsTrigger>
                <TabsTrigger value="pcd-f" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-pcd-f">
                  PCD / F
                </TabsTrigger>
                <TabsTrigger value="cadeirante-m" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-cadeirante-m">
                  CADEIRANTE / M
                </TabsTrigger>
                <TabsTrigger value="cadeirante-f" className="font-semibold py-3 text-xs lg:text-sm" data-testid="tab-cadeirante-f">
                  CADEIRANTE / F
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </CardContent>
        </Card>

        {/* Layout: Filtros + Tabela */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar de Filtros */}
          <Card className="lg:col-span-1 h-fit border-slate-200 dark:border-slate-800 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Search className="w-5 h-5" />
                Opções de filtro
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filtro Nome */}
              <div>
                <Label htmlFor="filtro-nome" className="text-sm font-medium mb-2 block">
                  Nome
                </Label>
                <Input
                  id="filtro-nome"
                  placeholder="Buscar por nome"
                  value={filtroNome}
                  onChange={(e) => setFiltroNome(e.target.value)}
                  data-testid="filtro-nome"
                />
              </div>

              {/* Filtro Colocação */}
              <div>
                <Label htmlFor="filtro-colocacao" className="text-sm font-medium mb-2 block">
                  Colocação
                </Label>
                <Input
                  id="filtro-colocacao"
                  type="number"
                  placeholder="Ex: 1"
                  value={filtroColocacao}
                  onChange={(e) => setFiltroColocacao(e.target.value)}
                  data-testid="filtro-colocacao"
                />
              </div>

              {/* Filtro UF */}
              <div>
                <Label htmlFor="filtro-uf" className="text-sm font-medium mb-2 block">
                  UF
                </Label>
                <Input
                  id="filtro-uf"
                  placeholder="Ex: SP"
                  value={filtroUF}
                  onChange={(e) => setFiltroUF(e.target.value.toUpperCase())}
                  maxLength={2}
                  data-testid="filtro-uf"
                />
              </div>

              {/* Botão Filtrar */}
              <Button 
                className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-semibold"
                data-testid="btn-filtrar"
              >
                Filtrar
              </Button>

              {/* Botão Como funciona? */}
              <Dialog>
                <DialogTrigger asChild>
                  <Button 
                    variant="outline"
                    className="w-full bg-yellow-400 hover:bg-yellow-500 text-slate-900 font-semibold border-0"
                    data-testid="btn-como-funciona"
                  >
                    <HelpCircle className="w-4 h-4 mr-2" />
                    Como funciona?
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle className="text-2xl font-bold text-emerald-600">Como funciona o Ranking?</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 text-slate-700 dark:text-slate-300">
                    <div>
                      <h3 className="font-semibold text-lg mb-2">🏆 Sistema de Pontuação</h3>
                      <p>Os atletas acumulam pontos ao participar de corridas oficiais. A pontuação varia de acordo com a colocação e distância da prova.</p>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-2">📊 Categorias</h3>
                      <ul className="list-disc list-inside space-y-1">
                        <li><strong>Masculino/Feminino:</strong> Atletas sem restrições</li>
                        <li><strong>PCD:</strong> Pessoas com Deficiência</li>
                        <li><strong>Cadeirante:</strong> Atletas em cadeiras de rodas</li>
                      </ul>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-2">🅿️ Selo "P" (Pendente)</h3>
                      <p>O selo laranja "P" indica que o atleta ainda não completou <strong>12 provas no ano</strong>. Após atingir esse número, o selo desaparece e o atleta está elegível para premiação anual.</p>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-2">⭐ Status Elite</h3>
                      <p>Atletas com <strong>100 pontos ou mais</strong> recebem o status Elite, identificado por uma borda dourada no avatar e badge especial.</p>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-2">📅 Período</h3>
                      <p>O ranking é calculado anualmente, de janeiro a dezembro de 2025.</p>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>

          {/* Tabela de Ranking */}
          <div className="lg:col-span-3">
            <Card className="border-slate-200 dark:border-slate-800 shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-xl">
                  Ranking {categoriaAtual.replace('-', ' ').toUpperCase()}
                  <span className="ml-2 text-sm font-normal text-slate-600 dark:text-slate-400">
                    ({rankingFiltrado.length} atletas)
                  </span>
                </CardTitle>
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleExport('csv')}
                    variant="outline"
                    size="sm"
                    className="text-emerald-600"
                  >
                    <FileDown className="w-4 h-4 mr-2" />
                    CSV
                  </Button>
                  <Button
                    onClick={() => handleExport('excel')}
                    variant="outline"
                    size="sm"
                    className="text-emerald-600"
                  >
                    <FileDown className="w-4 h-4 mr-2" />
                    Excel
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-12 text-slate-600 dark:text-slate-400">
                    Carregando ranking...
                  </div>
                ) : (
                  <RankingTable data={rankingFiltrado} onAtletaClick={handleAtletaClick} />
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RankingPage;