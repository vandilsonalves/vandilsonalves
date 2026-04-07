import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Instagram, Globe, Handshake } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

export default function ParceirosPage() {
  const navigate = useNavigate();
  const [parceiros, setParceiros] = useState([]);

  useEffect(() => {
    axios.get(`${API}/parceiros`)
      .then(r => setParceiros(r.data || []))
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-white" data-testid="parceiros-page">
      {/* Header */}
      <div className="max-w-6xl mx-auto px-4 pt-6 pb-2">
        <Button variant="ghost" onClick={() => navigate(-1)} className="text-slate-500 hover:text-slate-800 mb-3" data-testid="btn-voltar-parceiros">
          <ArrowLeft className="w-4 h-4 mr-2" />Voltar
        </Button>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-800" data-testid="titulo-parceiros">Parceiros</h1>
      </div>

      {/* Banner */}
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="bg-gradient-to-r from-slate-700 to-slate-800 rounded-2xl p-5 text-center text-white shadow-lg">
          <h2 className="text-lg sm:text-xl font-bold">Seja Nosso Parceiro - Veja Os Benefícios Aqui</h2>
          <a
            href="https://wa.me/5577998626875?text=Olá! Gostaria de saber mais sobre parcerias com o Ranking Run."
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 mt-3 px-5 py-2 bg-emerald-500 hover:bg-emerald-600 rounded-full text-white text-sm font-semibold transition-colors shadow"
            data-testid="btn-seja-parceiro"
          >
            <Handshake className="w-4 h-4" />Click Aqui
          </a>
        </div>
      </div>

      {/* Grid de Parceiros */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        {parceiros.length === 0 ? (
          <div className="text-center py-16 text-slate-400">
            <Handshake className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p className="text-lg">Em breve nossos parceiros estarão aqui.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {parceiros.map(p => (
              <div key={p.id} className="flex flex-col items-center text-center" data-testid={`parceiro-card-${p.id}`}>
                {/* Imagem */}
                <div className="w-full aspect-square bg-white flex items-center justify-center p-2 mb-2">
                  {p.imagem_url ? (
                    <img
                      src={`${process.env.REACT_APP_BACKEND_URL}${p.imagem_url}`}
                      alt={p.nome || 'Parceiro'}
                      className="max-w-full max-h-full object-contain"
                    />
                  ) : (
                    <div className="w-full h-full bg-slate-50 rounded-lg flex items-center justify-center">
                      <Handshake className="w-12 h-12 text-slate-200" />
                    </div>
                  )}
                </div>

                {/* Links */}
                <div className="flex items-center gap-3 mt-1">
                  {p.instagram && (
                    <a
                      href={p.instagram}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-purple-600 hover:text-purple-800 transition-colors uppercase tracking-wide"
                      data-testid={`link-instagram-${p.id}`}
                    >
                      <Instagram className="w-3.5 h-3.5" />
                      <span>Rede Social</span>
                    </a>
                  )}
                  {p.site && (
                    <a
                      href={p.site}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors uppercase tracking-wide"
                      data-testid={`link-site-${p.id}`}
                    >
                      <Globe className="w-3.5 h-3.5" />
                      <span>Site</span>
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
