import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { FeedEquipe } from '@/components/dono-assessoria/FeedEquipe';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function FeedEquipePage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();

  if (!user || !token) {
    navigate('/login');
    return null;
  }

  const equipe = user.equipe || '';
  const isDono = user.role === 'dono_assessoria';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 px-4 py-6 md:px-8">
      <div className="max-w-2xl mx-auto">
        <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="text-slate-400 mb-4">
          <ArrowLeft className="w-4 h-4 mr-1" /> Voltar
        </Button>
        <FeedEquipe
          token={token}
          userId={user.id}
          equipe={equipe}
          isDonoAssessoria={isDono}
        />
      </div>
    </div>
  );
}
