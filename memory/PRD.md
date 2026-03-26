# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas completa com monetizacao, feed social, Raio-X, Strava e notificacoes por email.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Stripe (emergentintegrations)
- Emails: Resend
- Messaging: Celery + Redis

## Funcionalidades Implementadas

### Pagamento + Bloqueio
- [x] Plano Lancamento R$97 (de R$197) ate 14/12/2026
- [x] Plano Anual 12x R$119 a partir de 15/12/2026
- [x] AccessGate + PrintProtection + require_premium_access

### Mobile Responsiveness
- [x] MobileNav drawer hamburger
- [x] Headers responsivos em todas as paginas
- [x] overflow-x: hidden global

### Notificacoes por Email (26/03/2026)
- [x] Integracao Resend (API key configurada)
- [x] Checkbox "Enviar tambem por email" no painel de mensagens admin
- [x] Envio em background (nao bloqueia resposta)
- [x] Template HTML profissional (inline CSS)
- [x] Endpoints: POST /api/email/enviar, POST /api/email/teste
- [x] NOTA: Dominio rankingrun.com.br NAO verificado ainda. Emails so vao para vandy1250@gmail.com ate verificar DNS

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456
- Expirado: expirado@teste.com / 123456

## Backlog
- P2: Exportar Raio-X como PDF
- P1: Verificar DNS do dominio rankingrun.com.br no Resend para enviar emails reais

## Issues Conhecidas
- Redis instavel (restarts manuais)
- Resend: dominio nao verificado (apenas vandy1250@gmail.com recebe por enquanto)
