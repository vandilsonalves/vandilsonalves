// Helper para download de arquivos via URL direta (contorna bloqueio de iframe)
// NÃO usa Blob/createObjectURL - usa window.open com token na URL

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Abre uma URL de download autenticada em nova aba.
 * O navegador gerencia o download nativamente via Content-Disposition.
 * @param {string} apiPath - Caminho da API (ex: "/api/admin/financeiro/exportar/excel")
 * @param {object} params - Query params adicionais (opcionais)
 */
export const downloadFile = (apiPath, params = {}) => {
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('Token não encontrado');
    return;
  }
  
  const url = new URL(`${API}${apiPath}`);
  url.searchParams.set('token', token);
  
  // Adicionar params extras
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value);
    }
  });
  
  window.open(url.toString(), '_blank');
};

/**
 * Download de dados gerados no frontend (CSV) via backend proxy.
 * Envia o conteúdo para um endpoint que retorna como arquivo.
 * @param {string} csvContent - Conteúdo CSV
 * @param {string} filename - Nome do arquivo
 */
export const downloadCSVContent = (csvContent, filename) => {
  const token = localStorage.getItem('token');
  if (!token) return;

  // Criar form e submeter para download direto
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = `${API}/api/admin/download-csv?token=${encodeURIComponent(token)}&filename=${encodeURIComponent(filename)}`;
  form.target = '_blank';

  const input = document.createElement('input');
  input.type = 'hidden';
  input.name = 'csv_content';
  input.value = csvContent;
  form.appendChild(input);

  document.body.appendChild(form);
  form.submit();
  document.body.removeChild(form);
};

// Mantém triggerDownload para compatibilidade (fallback)
export const triggerDownload = (blob, filename) => {
  console.warn('triggerDownload via Blob está obsoleto neste ambiente. Use downloadFile().');
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 500);
};
