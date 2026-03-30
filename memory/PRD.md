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

## O que foi implementado

### Sessões Anteriores (Refatoração/Features)
- Refatoração de AdminDashboard.jsx, RankingPage.js, RaioXPage.jsx
- Filtros geográficos no Admin Mensagens, Splash Screen, leitura de mensagens
- Remoção Redis/Celery, faixa "Até 17 anos", rankings por modalidade
- Insígnias 3D, compartilhamento 9:16, GZip, índices MongoDB

### Sessão Redes Sociais no Perfil (29/03/2026)
- **8 botões de redes sociais** no "Acesso Rápido" do Meu Perfil: Instagram, Club Strava, Facebook, Grupo WhatsApp, TikTok, YouTube, Canal WhatsApp, Telegram ✅
- Todos com links oficiais do Ranking Run e ícones lucide-react (sem emojis) ✅
- Botão Instagram removido de "Compartilhar minha posição" (só WhatsApp permanece) ✅
- Paginação "Carregar Mais" em todos os 4 rankings (Profissional, Galera, Equipes, Corridas) ✅
- Scroll infinito automático via IntersectionObserver ✅
- Componente reutilizável LoadMoreButton.jsx com barra de progresso ✅
- **Chat da Assessoria** com upload de PDF/Excel/Imagens ✅
- **Feed da Equipe** (grupo fechado tipo WhatsApp) com curtidas e anexos ✅
- **Botão "Desvincular Atleta"** com motivo e notificação ✅
- **Nomes com apelido** (prioriza apelido, senão primeiro+segundo nome) ✅
- Feed acessível tanto no painel do dono quanto no perfil do atleta ✅
- **Botão "Feed da Equipe"** no header e mobile nav (só para atletas com equipe) ✅
- **Página dedicada /feed-equipe** fora do AccessGate (sempre acessível) ✅
- **Badge de posts não lidos** (vermelho) no botão Feed da Equipe com polling 15s ✅
- **Auto marca como lido** ao entrar no feed, badge desaparece ✅
- **Threads de resposta** nos posts do Feed (respostas indentadas com borda lateral) ✅
- **Menções @nome** com autocomplete dropdown e notificação push ao mencionado ✅
- **Header reestruturado** em 2 linhas: top (logo+user+ações) + bottom (navegação com scroll) ✅
- **Enquetes (Polls) no Feed da Equipe** ✅ — Criar enquetes, votar, ver %, encerrar (testado 29/03)
- Testes: Backend 17/17 PASSED, Frontend 100% (iteration_91)

### Sessão Resumo Semanal + Instagram Fix (29/03/2026)
- **Link Instagram corrigido** no Meu Perfil (trailing slash adicionado) ✅
- **Resumo Semanal automático para atletas** via notificação push ✅
  - Agendado: toda segunda-feira às 08:00 (APScheduler CronTrigger)
  - Conteúdo: corridas da semana, pontos ganhos, posição no ranking, total acumulado
  - Endpoint admin: `POST /api/admin/resumo-semanal/disparar` (disparo manual)
  - Endpoint admin: `GET /api/admin/resumo-semanal/historico` (historico de disparos)
  - Painel Admin: Menu "Resumo Semanal" em Ferramentas com botao "Disparar Agora", preview e historico ✅
  - Testado: 392/392 atletas notificados, 0 erros

### Regra de Notificações (29/03/2026)
- Atletas recebem notificações APENAS de Admin e Dono de Assessoria ✅
- Removidas: notificações de reação, comentário, parabéns, conquista de colega (feed_routes.py)
- Condicionadas: menções no Feed da Equipe só notificam se remetente for dono/admin (equipe_chat_routes.py)
- Chat da Assessoria já era restrito a dono/admin (sem alteração)
- Testado: 3/3 cenários validados via curl


### Tipo de Corredor + Terreno Preferido (29/03/2026)
- Novos campos no "Meu Perfil": **Tipo de Corredor** (Velocista/Resistencia/Endurance/Pace Leve) e **Seu Terreno Preferido** (Rua-Asfalto/Trilha/Esteira) ✅
- Backend: Model `PerfilUpdate` atualizado + endpoints de atualização ✅
- Admin Dashboard: Gráficos **31. Tipo de Corredor** e **32. Terreno Preferido** em pizza no Dashboard Estratégico ✅
- Header: Fix do overflow na barra de navegação (badges não cortam mais) ✅

### Sessão Admin Dashboard Fixes (30/03/2026)
- Fix: Gráficos sobrepostos no Dashboard Estratégico — ChartCard com `overflowY: auto` ✅
- Fix: Mapa coroplético do Brasil com SVG (27 estados, escala de cores, legenda) no seção 8 ✅
- Fix: Busca por e-mail no Admin Atletas ✅
- Fix: `KeyError: 'faixa_etaria'` e `KeyError: 'seguindo'` nos exports/análises do Instagram ✅
- Feature: Helper unificado `triggerDownload(blob, filename)` para forçar download de arquivos via Blob ✅
- Fix: Exportações (Excel/CSV/PDF) no Admin — todas funcionando via Blob download ✅
- Feature: Gráficos 31 (Tipo de Corredor) e 32 (Terreno Preferido) em pizza no Dashboard Estratégico ✅
- Testado: Backend 12/12 PASSED, Frontend 100% (iteration_92)

## Backlog Priorizado

### P2
- Exportar Raio-X como PDF (usar canvasShareGenerator.js)
- Corrigir `atletas.forEach` error residual no fetchStats
- Mover helper `triggerDownload` de AdminDashboard.jsx para `src/utils/downloadHelper.js`

### P3
- ~~Limpeza de código morto: pasta tasks/, celery_app.py, rotas antigas Stripe~~ ✅ (Removido em 29/03)
- ~~Limpeza de states obsoletos no AdminDashboard.jsx~~ ✅ (Removido em 29/03)
- Continuar quebra do AdminDashboard.jsx (+1600 linhas) em componentes menores

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
- Pagamentos em PRODUÇÃO REAL (não testar com dados falsos)
- App.js usa imports diretos (sem React.lazy)
- Acesso 90% via celular - performance é prioridade

## Collections MongoDB Relevantes
- `mensagens_assessoria`: Chat + Feed posts (diferenciados por campo `tipo`)
- `feed_enquetes`: Enquetes do feed da equipe (pergunta, opções, votos, ativa)
- `notificacoes`: Notificações push (menções, desvinculação, splash, etc.)
