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

### Sistema de Pagamento
- [x] Plano Lancamento: R$97 (de R$197) pagamento unico ate 14/12/2026
- [x] Plano Anual (preparado): 12x R$119 a partir de 15/12/2026
- [x] get_plano_vigente() alterna automaticamente por data
- [x] Checkout Stripe + Webhook + Polling
- [x] Paginas: pagamento, sucesso, cancelado
- [x] Banner contagem regressiva (ultimos 30 dias da oferta)

### Bloqueio de Acesso Expirados
- [x] require_premium_access no backend
- [x] AccessGate no frontend
- [x] PrintProtection (anti-print para expirados)

### Admin, Feed, Strava, Raio-X
- [x] Todas funcionalidades completas (ver sessoes anteriores)

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta (teste): teste.dono@teste.com / 123456
- Atleta (expirado): expirado@teste.com / 123456

## Backlog
- P2: Exportar Raio-X como PDF
- P3: Notificacoes push por email (Resend)

## Issues Conhecidas
- Redis instavel (restarts manuais)
- Race condition AuthContext em testes Playwright
