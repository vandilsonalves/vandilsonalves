import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GraficoEvolucao = ({ atletaId }) => {
  const [dados, setDados] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvolucao = async () => {
      try {
        const response = await axios.get(`${API}/atletas/${atletaId}/evolucao`);
        setDados(response.data);
      } catch (error) {
        console.error('Erro ao buscar evolução:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvolucao();
  }, [atletaId]);

  if (loading) return <div className="text-center py-4">Carregando gráfico...</div>;
  if (dados.length === 0) return null;

  return (
    <Card className="border-slate-200 dark:border-slate-800 shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl text-emerald-600 dark:text-emerald-400">
          Evolução Mensal 2025
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dados}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="mes" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="pontos" stroke="#10b981" strokeWidth={2} name="Pontos" />
            <Line type="monotone" dataKey="corridas" stroke="#3b82f6" strokeWidth={2} name="Corridas" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default GraficoEvolucao;
