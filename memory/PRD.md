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
- [x] Webhook Efi Bank para confirmacao automatica (requer mTLS em producao)
- [x] Polling frontend a cada 5s para confirmar pagamento PIX
- [x] Ativacao automatica do Premium apos pagamento confirmado

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

## API Endpoints - Efi Bank
- POST /api/efi/pix/criar - Cria cobranca PIX (retorna txid + QR Code)
- GET /api/efi/pix/status/{txid} - Consulta status da cobranca
- POST /api/efi/webhook/pix - Webhook para confirmacao automatica

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456
- Expirado: expirado@teste.com / 123456

## Backlog
- P1: Verificar DNS do dominio rankingrun.com.br no Resend para enviar emails reais
- P2: Exportar Raio-X como PDF
- P3: Configurar mTLS no servidor de producao para webhook Efi Bank funcionar (polling funciona como fallback)

## Issues Conhecidas
- Redis instavel (restarts manuais necessarios)
- Resend: dominio nao verificado (apenas vandy1250@gmail.com recebe por enquanto)
- Webhook Efi Bank requer mTLS (polling ativo como alternativa)
