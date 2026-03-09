// /app/frontend/src/pages/admin/DashboardRBAC.jsx
// Sistema de Gerenciamento de Administradores (RBAC)

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Users, Shield, Activity, AlertTriangle, Plus, Edit, Trash2, 
  Lock, Unlock, Eye, Clock, Globe, Monitor, RefreshCw, Loader2,
  UserCog, Key, FileText, CheckCircle, XCircle, Crown, AlertCircle, MapPin
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'];

const DashboardRBAC = () => {
  const { token } = useAuth();
  
  // Estados
  const [activeTab, setActiveTab] = useState('admins');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  
  // Administradores
  const [admins, setAdmins] = useState([]);
  const [roles, setRoles] = useState([]);
  const [permissoes, setPermissoes] = useState([]);
  
  // Logs
  const [logs, setLogs] = useState([]);
  const [loginHistory, setLoginHistory] = useState([]);
  const [alertas, setAlertas] = useState([]);
  
  // Modais
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedAdmin, setSelectedAdmin] = useState(null);
  
  // Form
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    password: '',
    role_id: ''
  });
  
  // Carregar dados iniciais
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      
      const [statsRes, adminsRes, rolesRes, logsRes, alertasRes] = await Promise.all([
        axios.get(`${API}/rbac/stats`, { headers }),
        axios.get(`${API}/rbac/admins`, { headers }),
        axios.get(`${API}/rbac/roles`, { headers }),
        axios.get(`${API}/rbac/logs?limite=50`, { headers }),
        axios.get(`${API}/rbac/alertas`, { headers })
      ]);
      
      setStats(statsRes.data);
      setAdmins(adminsRes.data.administradores || []);
      setRoles(rolesRes.data.roles || []);
      setLogs(logsRes.data.logs || []);
      setAlertas(alertasRes.data.alertas || []);
      
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      if (error.response?.status === 403) {
        toast.error('Você não tem permissão para acessar esta seção');
      } else {
        toast.error('Erro ao carregar dados do sistema RBAC');
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddAdmin = async () => {
    if (!formData.nome || !formData.email || !formData.password || !formData.role_id) {
      toast.error('Preencha todos os campos');
      return;
    }
    
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(`${API}/rbac/admins`, formData, { headers });
      toast.success('Administrador criado com sucesso!');
      setShowAddModal(false);
      setFormData({ nome: '', email: '', password: '', role_id: '' });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao criar administrador');
    }
  };
  
  const handleEditAdmin = async () => {
    if (!selectedAdmin) return;
    
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.put(`${API}/rbac/admins/${selectedAdmin.id}`, {
        nome: formData.nome,
        email: formData.email,
        status: formData.status,
        role_id: formData.role_id
      }, { headers });
      toast.success('Administrador atualizado!');
      setShowEditModal(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar administrador');
    }
  };
  
  const handleDeleteAdmin = async () => {
    if (!selectedAdmin) return;
    
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.delete(`${API}/rbac/admins/${selectedAdmin.id}`, { headers });
      toast.success('Administrador excluído!');
      setShowDeleteModal(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao excluir administrador');
    }
  };
  
  const handleBlockAdmin = async (adminId, adminNome) => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(`${API}/rbac/admins/${adminId}/bloquear`, {}, { headers });
      toast.success(`${adminNome} foi bloqueado!`);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao bloquear administrador');
    }
  };
  
  const resolverAlerta = async (alertaId) => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(`${API}/rbac/alertas/${alertaId}/resolver`, {}, { headers });
      toast.success('Alerta resolvido!');
      loadData();
    } catch (error) {
      toast.error('Erro ao resolver alerta');
    }
  };
  
  const openEditModal = (admin) => {
    setSelectedAdmin(admin);
    setFormData({
      nome: admin.nome,
      email: admin.email,
      status: admin.status,
      role_id: admin.role_id
    });
    setShowEditModal(true);
  };
  
  const formatDate = (isoString) => {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleDateString('pt-BR', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
        <span className="ml-2">Carregando sistema RBAC...</span>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gerenciamento de Administradores</h1>
          <p className="text-gray-500">Sistema RBAC - Controle de Acesso Baseado em Papéis</p>
        </div>
        <Button onClick={() => setShowAddModal(true)} className="bg-emerald-600 hover:bg-emerald-700">
          <Plus className="w-4 h-4 mr-2" /> Novo Administrador
        </Button>
      </div>
      
      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-emerald-100 text-sm">Total Admins</p>
                <p className="text-3xl font-bold">{stats?.total_administradores || 0}</p>
              </div>
              <Users className="w-10 h-10 text-emerald-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Ativos</p>
                <p className="text-3xl font-bold">{stats?.administradores_ativos || 0}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-blue-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-100 text-sm">Bloqueados</p>
                <p className="text-3xl font-bold">{stats?.administradores_bloqueados || 0}</p>
              </div>
              <Lock className="w-10 h-10 text-red-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Ações Hoje</p>
                <p className="text-3xl font-bold">{stats?.logs_hoje || 0}</p>
              </div>
              <Activity className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card className={`bg-gradient-to-br ${(stats?.alertas_pendentes || 0) > 0 ? 'from-yellow-500 to-orange-500' : 'from-gray-500 to-gray-600'} text-white`}>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-100 text-sm">Alertas</p>
                <p className="text-3xl font-bold">{stats?.alertas_pendentes || 0}</p>
              </div>
              <AlertTriangle className="w-10 h-10 text-yellow-200" />
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Alertas de Segurança Pendentes */}
      {alertas.length > 0 && (
        <Alert className="bg-red-50 border-red-200">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>Atenção!</strong> Existem {alertas.length} alerta(s) de segurança pendente(s).
          </AlertDescription>
        </Alert>
      )}
      
      {/* Aviso de Email não configurado */}
      {stats && !stats.email_configurado && (
        <Alert className="bg-amber-50 border-amber-200">
          <AlertCircle className="w-5 h-5 text-amber-600" />
          <AlertDescription className="text-amber-800">
            <strong>Serviço de Email:</strong> RESEND_API_KEY não configurada. Os códigos 2FA e alertas de segurança não serão enviados por email até que a API key seja adicionada.
          </AlertDescription>
        </Alert>
      )}
      
      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-gray-100">
          <TabsTrigger value="admins" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            <Users className="w-4 h-4 mr-2" /> Administradores
          </TabsTrigger>
          <TabsTrigger value="roles" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            <Shield className="w-4 h-4 mr-2" /> Funções
          </TabsTrigger>
          <TabsTrigger value="logs" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            <FileText className="w-4 h-4 mr-2" /> Logs de Auditoria
          </TabsTrigger>
          <TabsTrigger value="alertas" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            <AlertTriangle className="w-4 h-4 mr-2" /> Alertas
            {alertas.length > 0 && (
              <Badge className="ml-2 bg-red-500">{alertas.length}</Badge>
            )}
          </TabsTrigger>
        </TabsList>
        
        {/* Tab: Administradores */}
        <TabsContent value="admins" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCog className="w-5 h-5" /> Lista de Administradores
              </CardTitle>
              <CardDescription>
                Gerencie os administradores do sistema e suas permissões
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {admins.map((admin) => (
                  <div 
                    key={admin.id} 
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <Avatar className="w-12 h-12">
                        <AvatarImage src={admin.foto_url} />
                        <AvatarFallback className="bg-emerald-100 text-emerald-700">
                          {admin.nome?.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-semibold text-gray-900">{admin.nome}</p>
                          {admin.is_super_admin && (
                            <Crown className="w-4 h-4 text-yellow-500" title="Super Admin" />
                          )}
                        </div>
                        <p className="text-sm text-gray-500">{admin.email}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className={
                            admin.role_nome === 'Super Admin' 
                              ? 'bg-purple-100 text-purple-700' 
                              : 'bg-blue-100 text-blue-700'
                          }>
                            {admin.role_nome}
                          </Badge>
                          <Badge className={
                            admin.status === 'ativo' 
                              ? 'bg-green-100 text-green-700' 
                              : admin.status === 'bloqueado'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-gray-100 text-gray-700'
                          }>
                            {admin.status}
                          </Badge>
                          {admin.dois_fatores_ativo && (
                            <Badge className="bg-emerald-100 text-emerald-700">
                              <Key className="w-3 h-3 mr-1" /> 2FA
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {admin.ultimo_login && (
                        <span className="text-xs text-gray-400 mr-4">
                          Último login: {formatDate(admin.ultimo_login)}
                        </span>
                      )}
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => openEditModal(admin)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      {admin.status === 'ativo' && !admin.is_super_admin && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          className="text-orange-600 hover:bg-orange-50"
                          onClick={() => handleBlockAdmin(admin.id, admin.nome)}
                        >
                          <Lock className="w-4 h-4" />
                        </Button>
                      )}
                      {!admin.is_super_admin && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          className="text-red-600 hover:bg-red-50"
                          onClick={() => {
                            setSelectedAdmin(admin);
                            setShowDeleteModal(true);
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
                
                {admins.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    Nenhum administrador encontrado.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Tab: Funções */}
        <TabsContent value="roles" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {roles.map((role) => (
              <Card key={role.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Shield className={
                      role.codigo === 'super_admin' ? 'text-purple-600' : 'text-blue-600'
                    } />
                    {role.nome}
                  </CardTitle>
                  <CardDescription>{role.descricao}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <p className="text-sm font-medium text-gray-700">Permissões:</p>
                    <div className="flex flex-wrap gap-2">
                      {role.permissoes?.slice(0, 8).map((perm) => (
                        <Badge key={perm} variant="outline" className="text-xs">
                          {perm.replace(/_/g, ' ')}
                        </Badge>
                      ))}
                      {role.permissoes?.length > 8 && (
                        <Badge variant="outline" className="text-xs bg-gray-100">
                          +{role.permissoes.length - 8} mais
                        </Badge>
                      )}
                    </div>
                    <div className="pt-2 border-t">
                      <p className="text-xs text-gray-400">
                        Nível: {role.nivel} | Total permissões: {role.permissoes?.length || 0}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        
        {/* Tab: Logs */}
        <TabsContent value="logs" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" /> Logs de Ações Administrativas
                  </CardTitle>
                  <CardDescription>
                    Registro de todas as ações realizadas por administradores
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={loadData}>
                  <RefreshCw className="w-4 h-4 mr-2" /> Atualizar
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px]">
                <div className="space-y-3">
                  {logs.map((log) => (
                    <div 
                      key={log.id} 
                      className="p-4 bg-gray-50 rounded-lg border-l-4 border-emerald-500"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Badge className="bg-emerald-100 text-emerald-700">
                              {log.tipo_acao}
                            </Badge>
                            <span className="text-sm font-medium text-gray-900">
                              {log.admin_nome}
                            </span>
                            <span className="text-xs text-gray-400">
                              ({log.admin_role})
                            </span>
                          </div>
                          <p className="mt-1 text-sm text-gray-600">{log.descricao}</p>
                          {log.entidade_nome && (
                            <p className="text-xs text-gray-400 mt-1">
                              Entidade: {log.entidade_tipo} - {log.entidade_nome}
                            </p>
                          )}
                        </div>
                        <div className="text-right text-xs text-gray-400">
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatDate(log.data_hora)}
                          </div>
                          <div className="flex items-center gap-1 mt-1">
                            <Globe className="w-3 h-3" />
                            {log.ip_address}
                          </div>
                          <div className="flex items-center gap-1 mt-1">
                            <MapPin className="w-3 h-3 text-blue-500" />
                            <span className="text-blue-600 font-medium">
                              {log.localizacao_aproximada || log.geo_cidade || 'Desconhecido'}
                            </span>
                          </div>
                          <div className="flex items-center gap-1 mt-1">
                            <Monitor className="w-3 h-3" />
                            {log.dispositivo || 'Desconhecido'}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {logs.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      Nenhum log encontrado.
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Tab: Alertas */}
        <TabsContent value="alertas" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" /> Alertas de Segurança
              </CardTitle>
              <CardDescription>
                Alertas críticos do sistema que requerem atenção
              </CardDescription>
            </CardHeader>
            <CardContent>
              {alertas.length > 0 ? (
                <div className="space-y-4">
                  {alertas.map((alerta) => (
                    <div 
                      key={alerta.id} 
                      className={`p-4 rounded-lg border-l-4 ${
                        alerta.tipo === 'admin_emergencia_usado'
                          ? 'bg-red-50 border-red-500'
                          : 'bg-yellow-50 border-yellow-500'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-semibold text-gray-900">{alerta.titulo}</h4>
                          <p className="text-sm text-gray-600 mt-1">{alerta.descricao}</p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span><Clock className="w-3 h-3 inline mr-1" />{formatDate(alerta.data_hora)}</span>
                            <span><Globe className="w-3 h-3 inline mr-1" />{alerta.ip_address}</span>
                            {alerta.admin_nome && (
                              <span><Users className="w-3 h-3 inline mr-1" />{alerta.admin_nome}</span>
                            )}
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => resolverAlerta(alerta.id)}
                          className="text-green-600 hover:bg-green-50"
                        >
                          <CheckCircle className="w-4 h-4 mr-1" /> Resolver
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-300" />
                  <p>Nenhum alerta de segurança pendente!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      {/* Modal: Adicionar Admin */}
      <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="w-5 h-5 text-emerald-600" /> Novo Administrador
            </DialogTitle>
            <DialogDescription>
              Crie uma nova conta de administrador para o sistema
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="nome">Nome Completo</Label>
              <Input 
                id="nome"
                value={formData.nome}
                onChange={(e) => setFormData({...formData, nome: e.target.value})}
                placeholder="Digite o nome completo"
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                placeholder="email@rankingrun.com"
              />
            </div>
            <div>
              <Label htmlFor="password">Senha</Label>
              <Input 
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                placeholder="Mínimo 6 caracteres"
              />
            </div>
            <div>
              <Label htmlFor="role">Função</Label>
              <Select 
                value={formData.role_id} 
                onValueChange={(v) => setFormData({...formData, role_id: v})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione a função" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((role) => (
                    <SelectItem key={role.id} value={role.id}>
                      {role.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleAddAdmin} className="bg-emerald-600 hover:bg-emerald-700">
              Criar Administrador
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Modal: Editar Admin */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Edit className="w-5 h-5 text-blue-600" /> Editar Administrador
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="edit-nome">Nome Completo</Label>
              <Input 
                id="edit-nome"
                value={formData.nome}
                onChange={(e) => setFormData({...formData, nome: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="edit-email">Email</Label>
              <Input 
                id="edit-email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="edit-status">Status</Label>
              <Select 
                value={formData.status} 
                onValueChange={(v) => setFormData({...formData, status: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ativo">Ativo</SelectItem>
                  <SelectItem value="inativo">Inativo</SelectItem>
                  <SelectItem value="bloqueado">Bloqueado</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit-role">Função</Label>
              <Select 
                value={formData.role_id} 
                onValueChange={(v) => setFormData({...formData, role_id: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((role) => (
                    <SelectItem key={role.id} value={role.id}>
                      {role.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleEditAdmin} className="bg-blue-600 hover:bg-blue-700">
              Salvar Alterações
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Modal: Confirmar Exclusão */}
      <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <Trash2 className="w-5 h-5" /> Confirmar Exclusão
            </DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-gray-600">
              Tem certeza que deseja excluir o administrador{' '}
              <strong>{selectedAdmin?.nome}</strong>?
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Esta ação não pode ser desfeita.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteModal(false)}>
              Cancelar
            </Button>
            <Button 
              onClick={handleDeleteAdmin} 
              className="bg-red-600 hover:bg-red-700"
            >
              Excluir Administrador
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardRBAC;
