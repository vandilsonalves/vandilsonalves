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
- [x] Limpeza de codigo morto (P3 - 25/03/2026)

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

### Sistema de Pagamento (25/03/2026)
- [x] Integracao Stripe via emergentintegrations
- [x] **Plano Lancamento**: R$97,00 (de R$197,00) pagamento unico ate 14/12/2026
- [x] **Plano Anual** (preparado): 12x R$119,00 a partir de 15/12/2026
- [x] Funcao get_plano_vigente() alterna automaticamente por data
- [x] GET /api/pagamentos/planos retorna plano vigente + info transicao
- [x] Checkout session com redirect para Stripe
- [x] Webhook para confirmar pagamento
- [x] Polling de status no frontend
- [x] Pagina de pagamento com "De R$197 por R$97" + badge OFERTA
- [x] Pagina de sucesso com polling
- [x] Pagina de cancelamento

### Bloqueio de Acesso para Expirados (25/03/2026)
- [x] Dependency require_premium_access no backend
- [x] Bloqueio: Raio-X, edicao perfil, Strava, Feed (postar/reagir/comentar), Stories
- [x] Componente AccessGate no frontend
- [x] Ranking publico continua acessivel

### Prevencao de Print de Tela (25/03/2026)
- [x] Componente PrintProtection global para usuarios expirados
- [x] Bloqueia: PrintScreen, Ctrl+P, Ctrl+Shift+S, Ctrl+Shift+I
- [x] CSS @media print oculta conteudo
- [x] user-select: none impede copia
- [x] Warning overlay quando detecta tentativa

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta (em teste): teste.dono@teste.com / 123456
- Atleta (expirado): expirado@teste.com / 123456

## Endpoints Chave
- POST /api/pagamentos/checkout - Cria sessao Stripe (plano vigente)
- GET /api/pagamentos/planos - Lista planos disponiveis com info de transicao
- GET /api/pagamentos/status/{session_id} - Status do pagamento
- GET /api/pagamentos/meu-plano - Status do plano do usuario + plano_vigente
- POST /api/webhook/stripe - Webhook Stripe

## Backlog Priorizado

### P2
- Exportar Raio-X como PDF

### P3
- Notificacoes push por email (Resend) para mensagens urgentes

## Issues Conhecidas
- Redis instavel (requer restarts manuais intermitentes)
- Race condition no AuthContext durante testes E2E Playwright (nao afeta usuarios reais)
