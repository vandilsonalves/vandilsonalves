import { useState, useEffect } from 'react';

const useCidadesIBGE = (uf) => {
  const [cidades, setCidades] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!uf) {
      setCidades([]);
      return;
    }
    setLoading(true);
    fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios?orderBy=nome`)
      .then(res => res.json())
      .then(data => {
        setCidades(data.map(m => m.nome));
      })
      .catch(() => setCidades([]))
      .finally(() => setLoading(false));
  }, [uf]);

  return { cidades, loading };
};

export default useCidadesIBGE;
