import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import {
  AlertCircle, Edit, Plus, X, Send,
  ArrowRightLeft, RefreshCw, Loader2,
  Crown, MessageSquare
} from 'lucide-react';
import CidadeCombobox from '@/components/CidadeCombobox';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

const AdminModals = ({
  // Editar Atleta
  showAtletaModal, setShowAtletaModal,
  atletaEditando, setAtletaEditando,
  cidadesEditAtleta, loadingCidadesEdit,
  onSaveAtleta, actionLoading,
  // Adicionar Atleta
  showAddAtletaModal, setShowAddAtletaModal,
  novoAtleta, setNovoAtleta,
  cidadesNovoAtleta, loadingCidadesNovo,
  onAddAtleta,
  // Foto Modal
  showFotoModal, setShowFotoModal, fotoModalUrl,
  // Transferir Modalidade
  showTransferModal, setShowTransferModal,
  atletaTransferindo, setAtletaTransferindo,
  onTransferirModalidade, transferLoading,
  // Corrida Modal
  showCorridaModal, setShowCorridaModal,
  corridaEditando, setCorridaEditando,
  corridaFormData, setCorridaFormData,
  onSaveCorrida,
  // Promover Dono
  showPromoverModal, setShowPromoverModal,
  atletaAcao,
  onPromoverDonoAssessoria, promoverLoading,
  // Mensagem Individual
  showMensagemModal, setShowMensagemModal,
  mensagemAdmin, setMensagemAdmin,
  onEnviarMensagemIndividual, sendingMensagem,
}) => {
  return (
    <>
      {/* Modal Editar Atleta */}
      <Dialog open={showAtletaModal} onOpenChange={setShowAtletaModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Editar Atleta</DialogTitle>
          </DialogHeader>
          {atletaEditando && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Nome</Label>
                <Input value={atletaEditando.nome} onChange={(e) => setAtletaEditando({...atletaEditando, nome: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input value={atletaEditando.email} onChange={(e) => setAtletaEditando({...atletaEditando, email: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>Equipe</Label>
                <Input value={atletaEditando.equipe} onChange={(e) => setAtletaEditando({...atletaEditando, equipe: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>UF</Label>
                <Select value={atletaEditando.estado} onValueChange={(v) => setAtletaEditando({...atletaEditando, estado: v, cidade: ''})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {ESTADOS_BR.map((uf) => <SelectItem key={uf} value={uf}>{uf}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Cidade</Label>
                {atletaEditando.estado ? (
                  <CidadeCombobox
                    cidades={cidadesEditAtleta}
                    value={atletaEditando.cidade}
                    onValueChange={(v) => setAtletaEditando({...atletaEditando, cidade: v})}
                    loading={loadingCidadesEdit}
                    data-testid="edit-select-cidade"
                  />
                ) : (
                  <Input disabled placeholder="Selecione o estado primeiro" className="bg-slate-100" />
                )}
              </div>
              <div className="space-y-2">
                <Label>Categoria</Label>
                <Select value={atletaEditando.categoria} onValueChange={(v) => setAtletaEditando({...atletaEditando, categoria: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="pcd">PCD</SelectItem>
                    <SelectItem value="cadeirante">Cadeirante</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Gênero</Label>
                <Select value={atletaEditando.genero} onValueChange={(v) => setAtletaEditando({...atletaEditando, genero: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="M">Masculino</SelectItem>
                    <SelectItem value="F">Feminino</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Data de Nascimento</Label>
                <Input type="date" value={atletaEditando.data_nascimento} onChange={(e) => setAtletaEditando({...atletaEditando, data_nascimento: e.target.value})} />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAtletaModal(false)}>Cancelar</Button>
            <Button onClick={onSaveAtleta} disabled={actionLoading} className="bg-emerald-600">Salvar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Adicionar Atleta */}
      <Dialog open={showAddAtletaModal} onOpenChange={setShowAddAtletaModal}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Cadastrar Novo Atleta</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Nome *</Label>
              <Input value={novoAtleta.nome} onChange={(e) => setNovoAtleta({...novoAtleta, nome: e.target.value})} />
            </div>
            <div className="space-y-2">
              <Label>Email *</Label>
              <Input value={novoAtleta.email} onChange={(e) => setNovoAtleta({...novoAtleta, email: e.target.value})} />
            </div>
            <div className="space-y-2">
              <Label>Equipe</Label>
              <Input value={novoAtleta.equipe} onChange={(e) => setNovoAtleta({...novoAtleta, equipe: e.target.value})} />
            </div>
            <div className="space-y-2">
              <Label>UF</Label>
              <Select value={novoAtleta.estado} onValueChange={(v) => setNovoAtleta({...novoAtleta, estado: v, cidade: ''})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {ESTADOS_BR.map((uf) => <SelectItem key={uf} value={uf}>{uf}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Cidade *</Label>
              {novoAtleta.estado ? (
                <CidadeCombobox
                  cidades={cidadesNovoAtleta}
                  value={novoAtleta.cidade}
                  onValueChange={(v) => setNovoAtleta({...novoAtleta, cidade: v})}
                  loading={loadingCidadesNovo}
                  data-testid="admin-select-cidade"
                />
              ) : (
                <Input disabled placeholder="Selecione o estado primeiro" className="bg-slate-100" />
              )}
            </div>
            <div className="space-y-2">
              <Label>Categoria</Label>
              <Select value={novoAtleta.categoria} onValueChange={(v) => setNovoAtleta({...novoAtleta, categoria: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="normal">Normal</SelectItem>
                  <SelectItem value="pcd">PCD</SelectItem>
                  <SelectItem value="cadeirante">Cadeirante</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Gênero</Label>
              <Select value={novoAtleta.genero} onValueChange={(v) => setNovoAtleta({...novoAtleta, genero: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="M">Masculino</SelectItem>
                  <SelectItem value="F">Feminino</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Data de Nascimento *</Label>
              <Input type="date" value={novoAtleta.data_nascimento} onChange={(e) => setNovoAtleta({...novoAtleta, data_nascimento: e.target.value})} />
            </div>
            <div className="space-y-2">
              <Label>Telefone *</Label>
              <Input value={novoAtleta.telefone} onChange={(e) => setNovoAtleta({...novoAtleta, telefone: e.target.value})} placeholder="(00) 00000-0000" data-testid="admin-input-telefone" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Tipo de Corredor *</Label>
                <Select value={novoAtleta.tipo_corredor} onValueChange={(v) => setNovoAtleta({...novoAtleta, tipo_corredor: v})}>
                  <SelectTrigger data-testid="admin-select-tipo-corredor">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="velocista"><span><strong className="uppercase">VELOCISTA</strong> <span className="text-xs text-slate-500">- até 5km</span></span></SelectItem>
                    <SelectItem value="resistencia"><span><strong className="uppercase">RESISTÊNCIA</strong> <span className="text-xs text-slate-500">- até 21km</span></span></SelectItem>
                    <SelectItem value="endurance"><span><strong className="uppercase">ENDURANCE</strong> <span className="text-xs text-slate-500">- acima de 42km</span></span></SelectItem>
                    <SelectItem value="pace_leve"><span><strong className="uppercase">PACE LEVE</strong> <span className="text-xs text-slate-500">- Diversão</span></span></SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Terreno Preferido *</Label>
                <Select value={novoAtleta.terreno_preferido} onValueChange={(v) => setNovoAtleta({...novoAtleta, terreno_preferido: v})}>
                  <SelectTrigger data-testid="admin-select-terreno">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rua_asfalto">Rua - Asfalto</SelectItem>
                    <SelectItem value="trilha">Trilha</SelectItem>
                    <SelectItem value="esteira">Esteira</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Modalidade de Participação */}
          <div className="pt-3 border-t">
            <Label className="text-sm font-semibold">Modalidade de Participação *</Label>
            <div className="grid grid-cols-2 gap-3 mt-2">
              <div
                onClick={() => setNovoAtleta({...novoAtleta, modalidade_usuario: 'profissional_amador'})}
                className={`p-2.5 rounded-lg border-2 cursor-pointer transition-all ${
                  novoAtleta.modalidade_usuario === 'profissional_amador'
                    ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                    : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                }`}
                data-testid="admin-modalidade-profissional"
              >
                <p className="font-bold text-sm">Profissional / Amador</p>
                <p className="text-xs text-slate-500">Pontuação por colocação</p>
              </div>
              <div
                onClick={() => setNovoAtleta({...novoAtleta, modalidade_usuario: 'povao_pace_livre'})}
                className={`p-2.5 rounded-lg border-2 cursor-pointer transition-all ${
                  novoAtleta.modalidade_usuario === 'povao_pace_livre'
                    ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                    : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                }`}
                data-testid="admin-modalidade-galera"
              >
                <p className="font-bold text-sm">Ranking da Galera</p>
                <p className="text-xs text-slate-500">Pontuação por distância</p>
              </div>
            </div>
          </div>

          <p className="text-sm text-slate-500">Senha padrão: atleta123</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddAtletaModal(false)}>Cancelar</Button>
            <Button onClick={onAddAtleta} disabled={actionLoading} className="bg-emerald-600">Cadastrar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Visualização da Foto do Pódio */}
      <Dialog open={showFotoModal} onOpenChange={setShowFotoModal}>
        <DialogContent className="max-w-4xl p-0 bg-black/90">
          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 z-10 bg-black/50 hover:bg-black/70 text-white"
              onClick={() => setShowFotoModal(false)}
            >
              <X className="w-6 h-6" />
            </Button>
            {fotoModalUrl && (
              <img 
                src={fotoModalUrl}
                alt="Foto do Pódio - Ampliada"
                className="w-full h-auto max-h-[85vh] object-contain rounded-lg"
                data-testid="foto-podio-modal"
              />
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal de Transferência de Modalidade */}
      <Dialog open={showTransferModal} onOpenChange={setShowTransferModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-xl flex items-center gap-2">
              <ArrowRightLeft className="w-5 h-5 text-purple-500" />
              Transferir Modalidade
            </DialogTitle>
          </DialogHeader>
          
          {atletaTransferindo && (
            <div className="space-y-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={atletaTransferindo.foto_url?.startsWith('http') ? atletaTransferindo.foto_url : `${BACKEND_URL}${atletaTransferindo.foto_url}`} />
                    <AvatarFallback className="bg-emerald-600 text-white">
                      {atletaTransferindo.nome?.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="font-semibold">{atletaTransferindo.nome}</h3>
                    <p className="text-sm text-slate-500">{atletaTransferindo.equipe || 'Sem equipe'}</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-center gap-4 py-2">
                <div className={`px-4 py-2 rounded-lg text-center ${
                  atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                    ? 'bg-purple-100 text-purple-700'
                    : 'bg-emerald-100 text-emerald-700'
                }`}>
                  <p className="text-xs font-medium">Atual</p>
                  <p className="font-semibold">
                    {atletaTransferindo.modalidade_usuario === 'povao_pace_livre' ? 'Ranking da Galera' : 'Profissional/Amador'}
                  </p>
                </div>
                
                <ArrowRightLeft className="w-6 h-6 text-slate-400" />
                
                <div className={`px-4 py-2 rounded-lg text-center ${
                  atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-purple-100 text-purple-700'
                }`}>
                  <p className="text-xs font-medium">Nova</p>
                  <p className="font-semibold">
                    {atletaTransferindo.modalidade_usuario === 'povao_pace_livre' ? 'Profissional/Amador' : 'Ranking da Galera'}
                  </p>
                </div>
              </div>

              <Alert className={`${
                atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                  ? 'bg-emerald-50 border-emerald-200'
                  : 'bg-purple-50 border-purple-200'
              }`}>
                <AlertCircle className={`w-4 h-4 ${
                  atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                    ? 'text-emerald-600'
                    : 'text-purple-600'
                }`} />
                <AlertDescription className={`${
                  atletaTransferindo.modalidade_usuario === 'povao_pace_livre'
                    ? 'text-emerald-800'
                    : 'text-purple-800'
                }`}>
                  {atletaTransferindo.modalidade_usuario === 'povao_pace_livre' ? (
                    <>
                      <strong>Galera &rarr; Profissional/Amador:</strong><br />
                      Os pontos serão recalculados baseados na <strong>colocação</strong> de cada corrida.
                      Se a colocação original não pontuava (acima de 10º lugar), a corrida terá 0 pontos.
                    </>
                  ) : (
                    <>
                      <strong>Profissional/Amador &rarr; Galera:</strong><br />
                      Os pontos serão recalculados baseados na <strong>distância</strong> de cada corrida:
                      <ul className="list-disc list-inside mt-1 text-sm">
                        <li>5km a 9km = 5 pontos</li>
                        <li>10km a 20km = 7 pontos</li>
                        <li>21km ou mais = 9 pontos</li>
                      </ul>
                    </>
                  )}
                </AlertDescription>
              </Alert>

              <div className="p-3 bg-amber-50 dark:bg-amber-900/30 rounded-lg border border-amber-200">
                <p className="text-sm text-amber-800 dark:text-amber-200">
                  <strong>Atenção:</strong> Esta ação irá remover o atleta do ranking atual e 
                  recalcular todos os pontos baseado na nova modalidade. O atleta receberá uma 
                  notificação sobre a transferência.
                </p>
              </div>
            </div>
          )}

          <DialogFooter className="gap-2">
            <Button 
              variant="outline" 
              onClick={() => { setShowTransferModal(false); setAtletaTransferindo(null); }}
              disabled={transferLoading}
            >
              Cancelar
            </Button>
            <Button 
              onClick={onTransferirModalidade}
              disabled={transferLoading}
              className={`${
                atletaTransferindo?.modalidade_usuario === 'povao_pace_livre'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : 'bg-purple-600 hover:bg-purple-700'
              }`}
            >
              {transferLoading ? (
                <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Transferindo...</>
              ) : (
                <><ArrowRightLeft className="w-4 h-4 mr-2" />Confirmar Transferência</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Cadastrar/Editar Corrida */}
      <Dialog open={showCorridaModal} onOpenChange={setShowCorridaModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {corridaEditando ? <Edit className="w-5 h-5 text-blue-500" /> : <Plus className="w-5 h-5 text-emerald-500" />}
              {corridaEditando ? 'Editar Corrida' : 'Cadastrar Nova Corrida'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nome da Corrida *</Label>
              <Input
                value={corridaFormData.nome_corrida}
                onChange={(e) => setCorridaFormData({...corridaFormData, nome_corrida: e.target.value})}
                placeholder="Ex: Maratona de São Paulo"
              />
            </div>
            <div>
              <Label>Organizador / Empresa *</Label>
              <Input
                value={corridaFormData.organizador}
                onChange={(e) => setCorridaFormData({...corridaFormData, organizador: e.target.value})}
                placeholder="Ex: Yescom"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Estado *</Label>
                <Select value={corridaFormData.estado} onValueChange={(v) => setCorridaFormData({...corridaFormData, estado: v})}>
                  <SelectTrigger><SelectValue placeholder="UF" /></SelectTrigger>
                  <SelectContent>
                    {ESTADOS_BR.map(uf => (
                      <SelectItem key={uf} value={uf}>{uf}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Cidade *</Label>
                <Input
                  value={corridaFormData.cidade}
                  onChange={(e) => setCorridaFormData({...corridaFormData, cidade: e.target.value})}
                  placeholder="Cidade"
                />
              </div>
            </div>
            <div>
              <Label>Data da Corrida *</Label>
              <Input
                type="date"
                value={corridaFormData.data_corrida}
                onChange={(e) => setCorridaFormData({...corridaFormData, data_corrida: e.target.value})}
              />
            </div>
            <div>
              <Label>Link da Página (Instagram ou Site)</Label>
              <Input
                value={corridaFormData.pagina_link}
                onChange={(e) => setCorridaFormData({...corridaFormData, pagina_link: e.target.value})}
                placeholder="https://..."
              />
            </div>
            <div>
              <Label>Status</Label>
              <Select value={corridaFormData.status} onValueChange={(v) => setCorridaFormData({...corridaFormData, status: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="ativa">Ativa</SelectItem>
                  <SelectItem value="encerrada">Encerrada</SelectItem>
                  <SelectItem value="cancelada">Cancelada</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowCorridaModal(false); setCorridaEditando(null); }}>
              Cancelar
            </Button>
            <Button onClick={onSaveCorrida} className="bg-emerald-500 hover:bg-emerald-600">
              {corridaEditando ? 'Salvar Alterações' : 'Cadastrar Corrida'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Promover a Dono de Assessoria */}
      <Dialog open={showPromoverModal} onOpenChange={setShowPromoverModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Crown className="w-5 h-5 text-amber-500" />
              Promover a Dono de Assessoria
            </DialogTitle>
          </DialogHeader>
          {atletaAcao && (
            <div className="space-y-4">
              <p className="text-slate-300">
                Deseja promover <span className="font-semibold text-white">{atletaAcao.nome}</span> a Dono de Assessoria?
              </p>
              <div className="p-3 bg-slate-800 rounded-lg">
                <p className="text-sm text-slate-400">Assessoria: <span className="text-white">{atletaAcao.equipe}</span></p>
                <p className="text-sm text-slate-400 mt-1">Email: <span className="text-white">{atletaAcao.email}</span></p>
              </div>
              <p className="text-xs text-amber-400">
                Ao promover, este atleta terá acesso ao painel de gerenciamento da assessoria.
              </p>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPromoverModal(false)}>Cancelar</Button>
            <Button 
              onClick={onPromoverDonoAssessoria} 
              disabled={promoverLoading}
              className="bg-amber-500 hover:bg-amber-600"
            >
              {promoverLoading ? (
                <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Promovendo...</>
              ) : (
                <><Crown className="w-4 h-4 mr-2" /> Promover</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Enviar Mensagem Individual */}
      <Dialog open={showMensagemModal} onOpenChange={setShowMensagemModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-blue-500" />
              Enviar Mensagem
            </DialogTitle>
          </DialogHeader>
          {atletaAcao && (
            <div className="space-y-4">
              <p className="text-slate-300">
                Enviar mensagem para <span className="font-semibold text-white">{atletaAcao.nome}</span>
              </p>
              <Textarea
                value={mensagemAdmin}
                onChange={(e) => setMensagemAdmin(e.target.value)}
                placeholder="Digite sua mensagem..."
                rows={4}
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowMensagemModal(false)}>Cancelar</Button>
            <Button 
              onClick={onEnviarMensagemIndividual}
              disabled={sendingMensagem || !mensagemAdmin.trim()}
              className="bg-blue-500 hover:bg-blue-600"
            >
              {sendingMensagem ? (
                <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Enviando...</>
              ) : (
                <><Send className="w-4 h-4 mr-2" /> Enviar</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default AdminModals;
