# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas completa com monetizacao, feed social, Raio-X, Strava e notificacoes por email.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Stripe (emergentintegrations) + Efi Bank (PIX via efipay SDK)
- Emails: Resend
- Messaging: Celery + Redis

## Funcionalidades Implementadas

### Pagamento + Bloqueio
- [x] Plano Lancamento: De R$197 por 5x R$19,40 (R$97 total) ate 14/12/2026
- [x] Plano Anual 12x R$119 a partir de 15/12/2026
- [x] AccessGate + PrintProtection + require_premium_access
- [x] Checkout Stripe (Cartao de credito)
- [x] Checkout Efi Bank (PIX com QR Code) - 27/03/2026
- [x] Webhook Efi Bank com skip-mTLS + validacao IP/HMAC - 27/03/2026
- [x] Tela de confirmacao PIX com animacao confetti - 27/03/2026
- [x] Polling frontend a cada 5s para confirmar pagamento PIX
- [x] Ativacao automatica do Premium apos pagamento confirmado

### Raio-X do Atleta
- [x] Exportar como PDF (multi-pagina)
- [x] Exportar como Excel (xlsx com abas)
- [x] Share Card Canvas 9:16 para Stories

### Mobile Responsiveness
- [x] MobileNav drawer hamburger
- [x] overflow-x: hidden global

### Notificacoes por Email
- [x] Integracao Resend (API key configurada)
- [x] Envio em background via Celery

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Backlog
- P1: Verificar DNS do dominio rankingrun.com.br no Resend
- P2: mTLS completo com Nginx em producao
- P3: Limpeza de imports mortos no AdminDashboard.jsx

## Issues Conhecidas
- Redis instavel (restarts manuais necessarios)
- Resend: dominio nao verificado (apenas vandy1250@gmail.com recebe)
