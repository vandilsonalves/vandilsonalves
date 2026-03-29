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

### Sessão Atual (29/03/2026)
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
- Testes: Backend 17/17 PASSED, Frontend 100% (iteration_91)

## Backlog Priorizado

### P2
- Exportar como PDF no Raio-X do atleta (usar canvasShareGenerator.js)

### P3
- Limpeza de código morto: pasta tasks/, celery_app.py, rotas antigas Stripe
- Limpeza de states obsoletos no AdminDashboard.jsx

## Credenciais de Teste
- Dono Assessoria: gustavo_gomes_2@email.com / teste123 (equipe: Assessoria CAFAV)
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

## Collections MongoDB Novas
- `chat_assessoria`: Mensagens do chat da assessoria (texto + arquivos)
- `feed_equipe`: Posts do feed da equipe (texto + arquivos + curtidas)
