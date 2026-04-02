import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ExternalLink, Camera, Trophy, Loader2 } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const CorridasParceirasPage = () => {
  const { token } = useAuth();
  const [corridas, setCorridas] = useState([]);
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      try {
        const [corridasRes, configRes] = await Promise.all([
          axios.get(`${API}/corridas-parceiras`),
          axios.get(`${API}/corridas-parceiras/config`)
        ]);
        setCorridas(corridasRes.data);
        setConfig(configRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  const registrarClick = async (corridaId, tipo, link) => {
    if (!link) return;
    try {
      if (token) {
        axios.post(`${API}/corridas-parceiras/${corridaId}/click?tipo=${tipo}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        }).catch(() => {});
      }
    } catch {}
    window.open(link, '_blank');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-8" data-testid="corridas-parceiras-page">
      {/* Banner "Gostaria de Divulgar Seu Evento Aqui?" */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-8 text-center shadow-lg border border-slate-700">
        <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">
          Gostaria de Divulgar Seu Evento Aqui?
        </h2>
        <Button
          onClick={() => config.link_whatsapp && window.open(config.link_whatsapp, '_blank')}
          className="bg-emerald-500 hover:bg-emerald-600 text-white font-bold px-8 py-3 text-base rounded-lg shadow-md"
          data-testid="btn-click-aqui"
        >
          CLICK AQUI
        </Button>
      </div>

      {/* Cupom */}
      <div className="text-center py-3">
        <p className="text-base sm:text-lg font-bold text-emerald-600">
          {config.cupom_descricao || 'Use Nosso Cupom e Pague Menos'}
        </p>
        <span className="inline-block mt-1 px-6 py-2 bg-red-500 text-white font-black text-xl sm:text-2xl rounded-lg tracking-wider shadow-md">
          {config.cupom_nome || 'RANKINGRUN10'}
        </span>
      </div>

      {/* Grid de corridas */}
      {corridas.length === 0 ? (
        <Card className="p-8 text-center text-slate-500">
          Nenhuma corrida parceira disponivel no momento.
        </Card>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {corridas.map(corrida => (
            <CorridaCard
              key={corrida.id}
              corrida={corrida}
              onClickBtn={registrarClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const CorridaCard = ({ corrida, onClickBtn }) => {
  const c = corrida;

  // Calcular dias restantes
  const calcularDiasRestantes = (dataStr) => {
    if (!dataStr) return null;
    const partes = dataStr.split('/');
    if (partes.length !== 3) return null;
    const dataEvento = new Date(partes[2], partes[1] - 1, partes[0]);
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    const diff = Math.ceil((dataEvento - hoje) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const diasRestantes = calcularDiasRestantes(c.data_evento);

  const BotaoAcao = ({ tipo, label, link, icone: Icon }) => {
    if (!link) return null;
    return (
      <button
        onClick={() => onClickBtn(c.id, tipo, link)}
        className="w-full flex items-center gap-1.5 px-2 py-1.5 bg-orange-500 hover:bg-orange-600 text-white text-xs font-bold rounded transition"
        data-testid={`btn-${tipo}-${c.id}`}
      >
        <Icon className="w-3 h-3 flex-shrink-0" />
        <span className="truncate">{label}</span>
      </button>
    );
  };

  return (
    <Card className="overflow-hidden bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md transition" data-testid={`corrida-atleta-${c.id}`}>
      {/* Imagem 1:1 */}
      <div className="aspect-square w-full overflow-hidden bg-slate-100 dark:bg-slate-900">
        {c.imagem_url ? (
          <img
            src={`${BACKEND_URL}${c.imagem_url}`}
            alt={c.nome_evento}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-300">
            <Trophy className="w-12 h-12" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3 space-y-1.5">
        <div className="flex items-center justify-between">
          <p className="text-xs text-slate-500">Data: {c.data_evento}</p>
          {diasRestantes !== null && diasRestantes >= 0 && (
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              diasRestantes <= 7 ? 'bg-red-100 text-red-600' :
              diasRestantes <= 30 ? 'bg-orange-100 text-orange-600' :
              'bg-emerald-100 text-emerald-600'
            }`}>
              {diasRestantes === 0 ? 'HOJE!' :
               diasRestantes === 1 ? 'Amanha!' :
               `Faltam ${diasRestantes} dias!`}
            </span>
          )}
          {diasRestantes !== null && diasRestantes < 0 && (
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
              Encerrada
            </span>
          )}
        </div>
        <h3 className="text-sm font-bold text-slate-800 dark:text-white leading-tight line-clamp-2">
          {c.nome_evento}
        </h3>
        <p className="text-xs text-slate-500">{c.cidade}/{c.estado}</p>
        <p className="text-sm font-bold text-emerald-600">{c.valor_inscricao}</p>

        {/* Botões de ação */}
        <div className="space-y-1.5 pt-2">
          <BotaoAcao tipo="inscricao" label="INSCREVA-SE" link={c.link_inscricao} icone={ExternalLink} />
          <BotaoAcao tipo="resultado" label="RESULTADO" link={c.link_resultado} icone={Trophy} />
          <BotaoAcao tipo="fotos" label="FOTOS" link={c.link_fotos} icone={Camera} />
          <BotaoAcao tipo="instagram" label="INSTAGRAM" link={c.link_instagram} icone={ExternalLink} />
        </div>
      </div>
    </Card>
  );
};

export default CorridasParceirasPage;
