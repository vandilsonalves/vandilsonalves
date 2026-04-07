import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import ImageCropModal from '@/components/ImageCropModal';
import { Handshake, Plus, Trash2, Edit, Download, Loader2, Instagram, Globe, ImageIcon } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const DashboardParceiros = ({ token }) => {
  const [parceiros, setParceiros] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [nome, setNome] = useState('');
  const [instagram, setInstagram] = useState('');
  const [site, setSite] = useState('');
  const [imagemUrl, setImagemUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [cropModal, setCropModal] = useState(false);
  const [cropSrc, setCropSrc] = useState(null);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchParceiros = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/admin/parceiros`, { headers });
      setParceiros(r.data || []);
    } catch { /* silent */ }
  }, [token]);

  useEffect(() => { fetchParceiros(); }, [fetchParceiros]);

  const resetForm = () => {
    setNome(''); setInstagram(''); setSite(''); setImagemUrl(''); setEditId(null);
  };

  const openNew = () => { resetForm(); setShowForm(true); };

  const openEdit = (p) => {
    setEditId(p.id);
    setNome(p.nome || '');
    setInstagram(p.instagram || '');
    setSite(p.site || '');
    setImagemUrl(p.imagem_url || '');
    setShowForm(true);
  };

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => { setCropSrc(reader.result); setCropModal(true); };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const handleCropComplete = async (croppedFile) => {
    setCropModal(false);
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('imagem', croppedFile);
      const r = await axios.post(`${API}/admin/parceiros/upload-imagem`, fd, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' }
      });
      setImagemUrl(r.data.imagem_url);
      toast.success('Imagem enviada!');
    } catch { toast.error('Erro no upload'); }
    finally { setUploading(false); }
  };

  const handleSubmit = async () => {
    if (!nome.trim()) { toast.error('Preencha o nome do parceiro'); return; }
    setSubmitting(true);
    try {
      const fd = new FormData();
      fd.append('nome', nome);
      fd.append('instagram', instagram);
      fd.append('site', site);

      // Se temos imagem previamente carregada via crop, buscar e anexar ao form
      if (imagemUrl) {
        const imgResp = await fetch(`${process.env.REACT_APP_BACKEND_URL}${imagemUrl}`);
        const blob = await imgResp.blob();
        fd.append('imagem', blob, 'imagem.png');
      }

      const url = editId ? `${API}/admin/parceiros/${editId}` : `${API}/admin/parceiros`;
      const method = editId ? 'put' : 'post';

      await axios[method](url, fd, { headers: { ...headers, 'Content-Type': 'multipart/form-data' } });

      toast.success(editId ? 'Parceiro atualizado!' : 'Parceiro adicionado!');
      setShowForm(false);
      resetForm();
      fetchParceiros();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Erro ao salvar');
    } finally { setSubmitting(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remover este parceiro?')) return;
    try {
      await axios.delete(`${API}/admin/parceiros/${id}`, { headers });
      toast.success('Parceiro removido');
      fetchParceiros();
    } catch { toast.error('Erro ao remover'); }
  };

  return (
    <div className="space-y-6" data-testid="dashboard-parceiros">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
            <Handshake className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Parceiros</h2>
            <p className="text-slate-500 text-sm">Gerenciar parceiros e patrocinadores</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => window.open(`${API}/admin/parceiros/export-excel?token=${token}`, '_blank')} variant="outline" className="text-emerald-600 border-emerald-300" data-testid="btn-export-parceiros">
            <Download className="w-4 h-4 mr-2" />Exportar Excel
          </Button>
          <Button onClick={openNew} className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600" data-testid="btn-novo-parceiro">
            <Plus className="w-4 h-4 mr-2" />Novo Parceiro
          </Button>
        </div>
      </div>

      {/* Lista */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Handshake className="w-5 h-5 text-blue-500" />Parceiros Cadastrados ({parceiros.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {parceiros.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Handshake className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>Nenhum parceiro cadastrado.</p>
              <Button onClick={openNew} className="mt-4" variant="outline"><Plus className="w-4 h-4 mr-2" />Adicionar primeiro parceiro</Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {parceiros.map(p => (
                <div key={p.id} className="bg-white border rounded-xl p-4 flex flex-col items-center text-center shadow-sm hover:shadow-md transition-shadow" data-testid={`parceiro-${p.id}`}>
                  {p.imagem_url ? (
                    <img src={`${process.env.REACT_APP_BACKEND_URL}${p.imagem_url}`} alt={p.nome} className="w-28 h-28 object-contain mb-3" />
                  ) : (
                    <div className="w-28 h-28 bg-slate-100 rounded-lg flex items-center justify-center mb-3">
                      <ImageIcon className="w-10 h-10 text-slate-300" />
                    </div>
                  )}
                  <h4 className="font-semibold text-slate-800 text-sm mb-2">{p.nome || 'Sem nome'}</h4>
                  <div className="flex gap-3 text-xs mb-3">
                    {p.instagram && (
                      <a href={p.instagram} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-pink-500 hover:text-pink-600">
                        <Instagram className="w-3 h-3" />Rede Social
                      </a>
                    )}
                    {p.site && (
                      <a href={p.site} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-blue-500 hover:text-blue-600">
                        <Globe className="w-3 h-3" />Site
                      </a>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" onClick={() => openEdit(p)} data-testid={`edit-${p.id}`}><Edit className="w-4 h-4" /></Button>
                    <Button size="sm" variant="ghost" className="text-red-500" onClick={() => handleDelete(p.id)} data-testid={`delete-${p.id}`}><Trash2 className="w-4 h-4" /></Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal Form */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Handshake className="w-5 h-5 text-blue-500" />{editId ? 'Editar' : 'Novo'} Parceiro
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nome da Empresa/Marca</Label>
              <Input placeholder="Ex: Nike" value={nome} onChange={e => setNome(e.target.value)} data-testid="input-nome-parceiro" />
            </div>
            <div>
              <Label>Rede Social (Instagram)</Label>
              <div className="flex items-center gap-2">
                <Instagram className="w-4 h-4 text-pink-500 shrink-0" />
                <Input placeholder="https://instagram.com/marca" value={instagram} onChange={e => setInstagram(e.target.value)} data-testid="input-instagram-parceiro" />
              </div>
            </div>
            <div>
              <Label>Site</Label>
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-blue-500 shrink-0" />
                <Input placeholder="https://www.marca.com.br" value={site} onChange={e => setSite(e.target.value)} data-testid="input-site-parceiro" />
              </div>
            </div>
            <div>
              <Label>Imagem da Empresa (PNG, formato 1:1)</Label>
              <div className="flex items-center gap-3 mt-1">
                <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg text-blue-600 hover:bg-blue-100 transition text-sm font-medium" data-testid="btn-upload-imagem-parceiro">
                  {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ImageIcon className="w-4 h-4" />}
                  {uploading ? 'Enviando...' : 'Escolher Imagem'}
                  <input type="file" accept="image/*" className="hidden" onChange={handleImageSelect} disabled={uploading} />
                </label>
                {imagemUrl && (
                  <img src={`${process.env.REACT_APP_BACKEND_URL}${imagemUrl}`} alt="Preview" className="w-16 h-16 object-contain border rounded-lg bg-white" />
                )}
              </div>
            </div>
          </div>
          <DialogFooter className="mt-4 gap-2">
            <Button variant="outline" onClick={() => setShowForm(false)}>Cancelar</Button>
            <Button onClick={handleSubmit} disabled={submitting} className="bg-gradient-to-r from-blue-500 to-indigo-500" data-testid="btn-salvar-parceiro">
              {submitting ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Salvando...</> : editId ? 'Atualizar' : 'Adicionar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Crop Modal (1:1 quadrado) */}
      <ImageCropModal
        isOpen={cropModal}
        onClose={() => setCropModal(false)}
        imageSrc={cropSrc}
        onCropComplete={handleCropComplete}
        aspectRatio={1}
      />
    </div>
  );
};

export default DashboardParceiros;
