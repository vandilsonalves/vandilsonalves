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
- **Scraping agora é MANUAL**: Removido job automático, admin baixa Excel manualmente

### Sessão Componentização AdminDashboard (31/03/2026)
- **AdminDashboard.jsx**: 1628 → 789 linhas (redução de 52%)
- **AdminSidebar.jsx** e **AdminModals.jsx** (NOVOS)
- Fix Gráficos 8 e 30, Fix Funil de Conversão

### Sessão Sistema de Backup (31/03/2026)
- Backup completo MongoDB + uploads com retenção automática de 4 backups
- APScheduler: toda quarta-feira às 02:30h

### Sessão 5 Features UI/UX (31/03/2026)
- **Feature 1 - Stories Profile Photo**: Foto de perfil do atleta agora aparece nos Stories do Feed Social
  - Backend: campo `autor_foto` adicionado ao criar e listar stories (feed_routes.py)
  - Frontend: `AvatarImage` renderiza a foto no `StoriesBar.jsx` (viewer + barra)
- **Feature 2 - Botões Enquetes Visíveis**: Botões "Adicionar Opção" (violeta) e "Cancelar" (vermelho) com cores fortes em `EnquetesSection.jsx`
- **Feature 3 - "SOU DONO DE UMA ASSESSORIA" no Cadastro**: Nova opção no dropdown de Equipe/Assessoria
  - Ao selecionar, campos de cadastro de assessoria (nome, UF, cidade, foto, bio) aparecem automaticamente
  - Opção separada de "INDIVIDUAL" para melhor UX
- **Feature 4 - "Esqueci minha Senha"**: Link no Login + modal de recuperação
  - Backend: `POST /api/auth/recuperar-senha` gera nova senha aleatória, salva hash, envia em texto plano via Resend
  - Frontend: Modal com campo de email, feedback visual de sucesso
- **Feature 5 - Fix Strava**: Removido `require_premium_access` do `/strava/authorize` (agora usa `get_current_user`)
  - FRONTEND_URL fallback melhorado para ler REACT_APP_BACKEND_URL do env
- Testado: Backend 100% (5/5), Frontend 100% (iteration_99)

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
- Resend (Emails) - Usado para recuperação de senha, relatórios, alertas
- Strava (Atividades) - OAuth2 com callback

## Notas Importantes
- NÃO iniciar Redis ou Celery (removidos da arquitetura)
- NÃO usar Blob/createObjectURL para downloads (bloqueado por iframe)
- Usar window.open(url?token=...) para todos os downloads
- Pagamentos em PRODUÇÃO REAL (não testar com dados falsos)
- App.js usa imports diretos (sem React.lazy)
- Acesso 90% via celular - performance é prioridade
- Scraping é MANUAL - não insere automaticamente no banco

- `autorizacoes`: Gerencia assinaturas premium (campo `atleta_id`, `status: ativa`, `data_expiracao`)

## Collections MongoDB Relevantes
- `mensagens_assessoria`: Chat + Feed posts (diferenciados por campo `tipo`)
- `feed_enquetes`: Enquetes do feed da equipe
- `notificacoes`: Notificações push
- `corridas_eventos`: Central de corridas e avaliações
- `scraping_fontes`: URLs monitoradas para varredura manual
- `stories`: Stories do feed social (inclui `autor_foto` desde 31/03/2026)
- `corridas_parceiras`: Corridas parceiras cadastradas pelo admin (CRUD completo)
- `clicks_corridas_parceiras`: Tracking de clicks por corrida, tipo, região
- `config_corridas_parceiras`: Link WhatsApp, cupom editável

### Sessão Selo Premium Verificado (04/04/2026)
- Selo de verificado (BadgeCheck azul) exibido no avatar de atletas premium na RankingTable
- Backend: `is_premium: bool` adicionado ao `RankingResponse` (models/__init__.py)
- Backend: Endpoints de ranking (`server.py`, `ranking_routes.py`) cruzam `autorizacoes` com status='ativa' para determinar premium
- Frontend: `RankingTable.js` renderiza ícone `BadgeCheck` (lucide-react) azul no avatar + anel `ring-blue-500`
- Quando atleta é premium E pendente: verified badge em `-bottom-1 -right-1`, PendingBadge em `-top-1 -right-1`
- Testado com testing agent: 100% de sucesso (iteração 100)

## API Endpoints Relevantes (Novos)
- `POST /api/auth/recuperar-senha` - Gera nova senha e envia por email
- `GET /api/feed/stories` - Retorna `autor_foto` para cada autor
- `GET /api/strava/authorize` - Usa `get_current_user` (sem premium required)
- `DELETE /api/strava/admin/limpar-todos` - Remove todos os tokens Strava (admin)
- WhatsApp recovery: usa link `wa.me/5577998626875` com mensagem pre-preenchida (sem API)
- `GET /api/corridas-parceiras` - Lista corridas parceiras (público, ordenadas por data)
- `GET /api/corridas-parceiras/config` - Config pública (link WhatsApp, cupom)
- `POST /api/admin/corridas-parceiras` - Cria corrida (admin, multipart/form-data)
- `PUT /api/admin/corridas-parceiras/{id}` - Edita corrida (admin)
- `DELETE /api/admin/corridas-parceiras/{id}` - Exclui corrida (admin)
- `POST /api/corridas-parceiras/{id}/click?tipo=X` - Registra click (autenticado)
- `GET /api/admin/corridas-parceiras/stats` - Dashboard de métricas de clicks (admin)
- `PUT /api/admin/corridas-parceiras/config` - Atualiza config (admin)
