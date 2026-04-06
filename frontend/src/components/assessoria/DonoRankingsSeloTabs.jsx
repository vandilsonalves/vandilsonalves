import { useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Trophy, MapPin, Calendar, Target, Download, Loader2 } from 'lucide-react';
import html2canvas from 'html2canvas';

const DonoRankingsTab = ({ assessoria, rankingNacional, rankingEstadual, rankingMensal, rankingAnual }) => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-white">Posição nos Rankings</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {[
        { icon: Trophy, label: 'Ranking Nacional', sub: 'de todas as assessorias do Brasil', value: rankingNacional, color: 'text-amber-500' },
        { icon: MapPin, label: `Ranking Estadual (${assessoria.estado})`, sub: `no estado de ${assessoria.estado}`, value: rankingEstadual, color: 'text-blue-500' },
        { icon: Calendar, label: 'Ranking Mensal', sub: 'neste mês', value: rankingMensal, color: 'text-emerald-500' },
        { icon: Target, label: 'Ranking Anual', sub: 'no ano de 2026', value: rankingAnual, color: 'text-purple-500' },
      ].map((item) => (
        <Card key={item.label} className="bg-slate-800 border-slate-700">
          <CardHeader className="border-b border-slate-700">
            <CardTitle className="text-white flex items-center gap-2">
              <item.icon className={`w-5 h-5 ${item.color}`} />
              {item.label}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 text-center">
            <p className={`text-6xl font-bold ${item.color} mb-2`}>{item.value || '-'}º</p>
            <p className="text-slate-400">{item.sub}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  </div>
);

const DonoSeloTab = ({ assessoria, getSeloColor, getSeloIcon, getSeloTitle }) => {
  const certificadoRef = useRef(null);
  const [downloadingCertificado, setDownloadingCertificado] = useState(false);

  const downloadCertificado = async () => {
    if (!certificadoRef.current) return;
    setDownloadingCertificado(true);
    try {
      const canvas = await html2canvas(certificadoRef.current, { scale: 2, backgroundColor: null, useCORS: true });
      const link = document.createElement('a');
      link.download = `selo_${assessoria.nome.replace(/\s+/g, '_')}_ROE-RR_2026.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (error) {
      console.error('Erro ao gerar certificado:', error);
    } finally {
      setDownloadingCertificado(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Selo Oficial ROE-RR</h2>
      <div className="max-w-md mx-auto">
        <div ref={certificadoRef} className={`${getSeloColor(assessoria.selo)} text-white p-8 rounded-xl text-center shadow-2xl`}>
          <div className="text-6xl mb-4">{getSeloIcon(assessoria.selo)}</div>
          <h3 className="text-2xl font-bold mb-2">{getSeloTitle(assessoria.selo)}</h3>
          <p className="text-xl font-semibold mb-4">{assessoria.nome}</p>
          <div className="border-t border-white/30 pt-4">
            <p className="text-sm opacity-90">Liga Nacional de Assessorias</p>
            <p className="text-lg font-semibold">Ranking Run</p>
            <p className="text-xs opacity-75 mt-2">Classificação Oficial ROE-RR – 2026</p>
          </div>
        </div>
        <Button className="w-full mt-6 bg-amber-500 hover:bg-amber-600" onClick={downloadCertificado} disabled={downloadingCertificado}>
          {downloadingCertificado ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Gerando...</> : <><Download className="w-4 h-4 mr-2" />Baixar Selo Oficial</>}
        </Button>
      </div>
    </div>
  );
};

export { DonoRankingsTab, DonoSeloTab };
