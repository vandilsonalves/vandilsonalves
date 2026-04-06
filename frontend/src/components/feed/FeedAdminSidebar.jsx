import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Shield, Trash2 } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FeedAdminSidebar = ({ isAdmin, token, fetchFeed }) => {
  if (!isAdmin) return null;

  return (
    <Card className="bg-gradient-to-br from-amber-900/30 to-orange-900/30 border-amber-500/30 sticky top-20">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2 text-amber-400">
          <Shield className="w-5 h-5" />
          <h3 className="font-semibold">Admin - Comentários</h3>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-xs text-slate-400">
          Gerencie posts e comentários do feed.
        </p>
        
        <Button 
          variant="outline" 
          size="sm"
          className="w-full border-red-500/50 text-red-400 hover:bg-red-500/20"
          onClick={async () => {
            if (confirm('ATENÇÃO: Limpar TODOS os posts do feed? Esta ação não pode ser desfeita!')) {
              try {
                const response = await axios.delete(`${API}/feed/admin/posts/limpar-todos`, {
                  headers: { Authorization: `Bearer ${token}` }
                });
                toast.success(response.data.message || 'Posts limpos com sucesso!');
                fetchFeed();
              } catch (error) {
                toast.error(error.response?.data?.detail || 'Erro ao limpar posts');
              }
            }
          }}
          data-testid="btn-limpar-posts"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Limpar Todos Posts
        </Button>
        
        <Button 
          variant="outline" 
          size="sm"
          className="w-full border-amber-500/50 text-amber-400 hover:bg-amber-500/20"
          onClick={async () => {
            if (confirm('Limpar TODOS os comentários não fixados? Esta ação não pode ser desfeita.')) {
              try {
                await axios.delete(`${API}/feed/admin/comentarios/limpar-todos`, {
                  headers: { Authorization: `Bearer ${token}` }
                });
                toast.success('Comentários limpos com sucesso!');
                fetchFeed();
              } catch (error) {
                toast.error(error.response?.data?.detail || 'Erro ao limpar comentários');
              }
            }
          }}
          data-testid="btn-limpar-comentarios"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Limpar Todos Comentários
        </Button>
        <p className="text-[10px] text-slate-500 text-center">
          Comentários fixados serão preservados
        </p>
      </CardContent>
    </Card>
  );
};

export default FeedAdminSidebar;
