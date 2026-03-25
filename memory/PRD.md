# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas completa com sistema de ranking profissional/amador, feed social, stories, sistema de mensagens admin, Raio-X do atleta, integracoes com Strava e sistema de monetizacao via Stripe.

## Arquitetura
- **Frontend**: React + TailwindCSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **Pagamentos**: Stripe (via emergentintegrations)
- **Messaging**: Celery + Redis (broker)
- **Integracoes**: Strava API, Resend (email)

## Funcionalidades Implementadas

### Core
- [x] Sistema de autenticacao JWT (login/registro)
- [x] RBAC (admin, super_admin, atleta, dono_assessoria)
- [x] Rankings: Nacional, Estadual, Cidade, Povao, Semanal, Mensal
- [x] Perfil do atleta com foto e bio
- [x] Submissao e aprovacao de resultados
- [x] Historico de corridas
- [x] Conquistas e badges

### Admin Dashboard
- [x] Gestao de atletas (CRUD)
- [x] Aprovacao/reprovacao de resultados
- [x] Sistema de mensagens em massa (com filtros geograficos/demograficos)
- [x] Mensagens com modo Splash Screen
- [x] Dashboard de autorizacoes (por status: em_teste, autorizado, expirado)
- [x] Estatisticas e metricas

### Feed Social
- [x] Posts de texto e fotos (limite 2 fotos/dia)
- [x] Stories (24h, fullscreen viewer)
- [x] Reacoes com emojis
- [x] Comentarios com moderacao
- [x] Double-tap to like (estilo Instagram)
- [x] Compressao automatica de imagens (Pillow)

### Integracao Strava
- [x] Autenticacao OAuth2
- [x] Sincronizacao de atividades
- [x] Stats do atleta

### Raio-X do Atleta
- [x] Evolucao de performance
- [x] Records pessoais
- [x] Comparativo mensal
- [x] Score de consistencia
- [x] Heatmap de corridas
- [x] Previsoes

### Sistema de Pagamento (NOVO - 25/03/2026)
- [x] Integracao Stripe via emergentintegrations
- [x] Plano Atleta Premium: R$97,00 (pagamento unico ate 31/12/2026)
- [x] Checkout session com redirect para Stripe
- [x] Webhook para confirmar pagamento
- [x] Polling de status no frontend
- [x] Pagina de pagamento com plano detalhado
- [x] Pagina de sucesso com polling
- [x] Pagina de cancelamento

### Bloqueio de Acesso para Expirados (NOVO - 25/03/2026)
- [x] Dependency `require_premium_access` no backend
- [x] Bloqueio no Raio-X (todas as rotas)
- [x] Bloqueio na edicao de perfil e upload de foto
- [x] Bloqueio no Strava (authorize)
- [x] Bloqueio no Feed (postar, reagir, comentar)
- [x] Bloqueio nos Stories (criar, reagir)
- [x] Componente AccessGate no frontend
- [x] Ranking publico continua acessivel
- [x] Login e navegacao basica liberados

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta (em teste): teste.dono@teste.com / 123456
- Atleta (expirado): expirado@teste.com / 123456

## Endpoints Chave
- POST /api/pagamentos/checkout - Cria sessao Stripe
- GET /api/pagamentos/status/{session_id} - Status do pagamento
- GET /api/pagamentos/meu-plano - Status do plano do usuario
- POST /api/webhook/stripe - Webhook Stripe

## Backlog Priorizado

### P1
- Preparar logica para cobranca anual (12x R$119,00 a partir de 15/12/2026)

### P2
- Exportar Raio-X como PDF
- Prevencao de print de tela para expirados

### P3
- Limpeza de estado morto no AdminDashboard.jsx
- Notificacoes push por email (Resend) para mensagens urgentes

## Issues Conhecidas
- Redis instavel (requer restarts manuais intermitentes)
- Race condition no AuthContext durante testes E2E Playwright
