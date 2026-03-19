// /app/frontend/src/components/dono-assessoria/ExportacaoCard.jsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, FileSpreadsheet, FileText, BarChart3 } from 'lucide-react';

export const ExportacaoCard = ({ onExportarDados, onExportarGraficos }) => (
  <Card className="bg-slate-800 border-slate-700">
    <CardHeader>
      <CardTitle className="text-white flex items-center gap-2">
        <Download className="w-5 h-5 text-blue-500" />
        Exportar Dados
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Button
          variant="outline"
          className="border-green-500 text-green-400 hover:bg-green-500/20"
          onClick={() => onExportarDados('csv')}
          data-testid="export-csv-btn"
        >
          <Download className="w-4 h-4 mr-2" />
          CSV
        </Button>
        <Button
          variant="outline"
          className="border-blue-500 text-blue-400 hover:bg-blue-500/20"
          onClick={() => onExportarDados('json')}
          data-testid="export-json-btn"
        >
          <Download className="w-4 h-4 mr-2" />
          JSON
        </Button>
        <Button
          variant="outline"
          className="border-emerald-500 text-emerald-400 hover:bg-emerald-500/20"
          onClick={() => onExportarDados('xlsx')}
          data-testid="export-xlsx-btn"
        >
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Excel
        </Button>
        <Button
          variant="outline"
          className="border-red-500 text-red-400 hover:bg-red-500/20"
          onClick={() => onExportarDados('pdf')}
          data-testid="export-pdf-btn"
        >
          <FileText className="w-4 h-4 mr-2" />
          PDF
        </Button>
        <Button
          variant="outline"
          className="border-purple-500 text-purple-400 hover:bg-purple-500/20"
          onClick={() => onExportarGraficos()}
          data-testid="export-graficos-btn"
        >
          <BarChart3 className="w-4 h-4 mr-2" />
          Gráficos
        </Button>
      </div>
      <p className="text-xs text-slate-400 mt-3">
        CSV: Planilha simples • JSON: Dados estruturados • Excel: Planilha formatada • PDF: Relatório visual • Gráficos: Dados para visualização
      </p>
    </CardContent>
  </Card>
);
