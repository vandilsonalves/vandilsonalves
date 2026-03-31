# Ranking Run Pro - PRD

## Problema Original
Plataforma de ranking de corridas de rua no Brasil. Sistema full-stack (React/FastAPI/MongoDB) com rankings profissionais, amadores ("Galera"), equipes (Liga de Assessorias) e corridas. Inclui sistema de insígnias, compartilhamento via Canvas, pagamentos via Efí Bank e painel administrativo completo.

## Arquitetura
- **Frontend**: React + Shadcn/UI + Recharts
- **Backend**: FastAPI + MongoDB (Motor async)
- **Cache**: cachetools (in-memory) - Redis/Celery foram removidos
- **Agendamento**: APScheduler (nativo Python)
- **Pagamentos**: Efí Bank (PRODUÇÃO REAL)
- **Compressão**: GZip Middleware
- **Downloads**: window.open(url?token=...) — NÃO usa Blob/createObjectURL (bloqueado por iframe)

## O que foi implementado

### Sessões Anteriores (Refatoração/Features)
- Refatoração de AdminDashboard.jsx, RankingPage.js, RaioXPage.jsx
- Filtros geográficos no Admin Mensagens, Splash Screen, leitura de mensagens
- Remoção Redis/Celery, faixa "Até 17 anos", rankings por modalidade
- Insígnias 3D, compartilhamento 9:16, GZip, índices MongoDB

### Sessão Redes Sociais no Perfil (29/03/2026)
- 8 botões de redes sociais no "Acesso Rápido" do Meu Perfil
- Paginação "Carregar Mais" em todos os 4 rankings
- Chat da Assessoria com upload de PDF/Excel/Imagens
- Feed da Equipe com curtidas, anexos, threads, menções, enquetes
- Badge de posts não lidos com polling 15s
- Header reestruturado em 2 linhas

### Sessão Resumo Semanal + Instagram Fix (29/03/2026)
- Link Instagram corrigido, Resumo Semanal automático via APScheduler

### Sessão Admin Dashboard Fixes (30/03/2026)
- Fix: Gráficos sobrepostos, Mapa coroplético SVG, Busca por email
- Tipo de Corredor + Terreno Preferido no perfil

### Sessão Refatoração + Dashboard Retenção (30/03/2026)
- Dashboard de Retenção no Admin (Taxa, Inativos, Equipes com mais inativos)
- triggerDownload extraído para downloadHelper.js (DRY)

### Sessão Scraping Avançado de Corridas (30/03/2026)
- Sistema de Busca e Varredura com fallback: API → HTML → Playwright
- Parsers específicos: Ticket Sports (API JSON), Central das Inscrições (HTML), Genérico
- Anti-duplicidade, Status automático (ativa/encerrada)

### Sessão Fix Downloads + Scraping Manual (31/03/2026)
- **FIX P0**: Todos os botões de exportação (PDF, CSV, Excel) agora fazem download real
  - Auth modificada para aceitar token via query parameter (?token=...)
  - Frontend usa window.open(url?token=...) em vez de Blob/createObjectURL
  - Funciona corretamente dentro de iframes (ambiente preview)
  - Todos os componentes atualizados: AdminDashboard, DashboardFinanceiro, DashboardCorridas, PerfilAtletaPage, DonoAssessoriaDashboard, DashboardAssessorias
- **Scraping agora é MANUAL**: 
  - Removido job automático a cada 12h do APScheduler
  - /scraping/buscar NÃO insere corridas no banco (cadastradas=0)
  - /scraping/atualizar-todas retorna Excel para download manual
  - Admin baixa o Excel e importa via "Importar Dados"
  - UI atualizada: "Busca e Varredura Manual de Corridas"
- **Novo endpoint**: GET /api/corridas-eventos/exportar/{formato} (CSV/Excel com filtros)
- **Novo endpoint**: POST /api/admin/download-csv (proxy para CSVs gerados no frontend)
- Testado: Backend 15/15 PASSED, Frontend 100% (iteration_96)

### Sessão Componentização AdminDashboard (31/03/2026)
- **AdminDashboard.jsx**: 1628 → 789 linhas (redução de 52%)
- **AdminSidebar.jsx** (NOVO): 94 linhas — Sidebar de navegação extraída
- **AdminModals.jsx** (NOVO): 593 linhas — 7 modais extraídos (EditAtleta, AddAtleta, FotoPodio, TransferModalidade, Corrida, PromoverDono, Mensagem)
- **Fix**: Guard duplo `Array.isArray` no `fetchEquipesStats` para prevenir `atletas.forEach` error
- Testado: Frontend 100% (iteration_97), nenhuma regressão

### Sessão Sistema de Backup (31/03/2026)
- **Nova aba "Backup"** no painel Admin (Super Admin only, seção Sistema)
- Backup completo: MongoDB (todas as 50+ collections como JSON) + arquivos de upload (~65MB)
- Botão "Fazer Backup" para backup manual sob demanda
- Backup automático agendado via APScheduler: toda **quarta-feira às 02:30h**
- Histórico de backups com download (.zip) e exclusão
- Arquivos armazenados no disco (/app/backups/), NÃO no banco de dados
- Segurança: apenas Super Admin pode acessar (verificação role + tipo_admin)
- **Retenção automática**: mantém apenas os últimos 4 backups, excluindo os mais antigos automaticamente (disco + banco)
- Testado: Backend 11/11 PASSED, Frontend 100% (iteration_98)

## Backlog Priorizado

### P2
- Exportar Raio-X como PDF (validar que funciona com nova abordagem de download)

### P3
- Scraping Sympla continua BLOQUEADO (Cloudflare 403 — limitação de IP datacenter)

## Credenciais de Teste
- Dono Assessoria: marcos_martins_3@email.com / marcos123 (equipe: Victory Run PE)
- Atleta c/ Equipe: leonardo_souza_136@email.com / leonardo123
- Admin: admin@runpro.com / admin

## Integrações
- Efí Bank (Pagamentos) - PRODUÇÃO REAL
- Resend (Emails)
- Strava (Atividades)

## Notas Importantes
- NÃO iniciar Redis ou Celery (removidos da arquitetura)
- NÃO usar Blob/createObjectURL para downloads (bloqueado por iframe)
- Usar window.open(url?token=...) para todos os downloads
- Pagamentos em PRODUÇÃO REAL (não testar com dados falsos)
- App.js usa imports diretos (sem React.lazy)
- Acesso 90% via celular - performance é prioridade
- Scraping é MANUAL - não insere automaticamente no banco

## Collections MongoDB Relevantes
- `mensagens_assessoria`: Chat + Feed posts (diferenciados por campo `tipo`)
- `feed_enquetes`: Enquetes do feed da equipe
- `notificacoes`: Notificações push
- `corridas_eventos`: Central de corridas e avaliações
- `scraping_fontes`: URLs monitoradas para varredura manual
