# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas com monetizacao, feed social, Raio-X, Strava e notificacoes.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Stripe + Efi Bank PIX (efipay SDK)
- Emails: Resend + Celery/Redis
- Producao: Nginx mTLS reverse proxy (Docker)

## Funcionalidades Implementadas

### Pagamento
- [x] Plano Lancamento: De R$197 por 5x R$19,40 (R$97 total)
- [x] AccessGate + PrintProtection + require_premium_access
- [x] Checkout Stripe (Cartao) + Efi Bank (PIX QR Code)
- [x] Webhook PIX skip-mTLS + HMAC + mTLS Nginx config producao
- [x] Tela confirmacao PIX com confetti
- [x] Polling frontend 5s + ativacao automatica Premium

### Dashboard Financeiro Admin (27/03/2026)
- [x] KPIs: Receita total, PIX, Cartao, Ticket medio
- [x] Grafico barras receita diaria (30 dias) / mensal (12 meses) com toggle
- [x] Donut chart distribuicao PIX vs Cartao
- [x] Tabela transacoes recentes (20 ultimas) com status/gateway/valor
- [x] Botao atualizar, superAdminOnly
- [x] API: GET /api/admin/financeiro/resumo

### Raio-X do Atleta
- [x] Exportar PDF/Excel + Share Card Canvas

### Mobile
- [x] MobileNav drawer, overflow-x: hidden

### Emails
- [x] Integracao Resend + Celery background

### Deploy Producao mTLS
- [x] nginx-mtls.conf + docker-compose.mtls.yml + deploy-mtls.sh
- [x] Certificados CA Efi Bank (prod + homolog)

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Backlog
- P1: Verificar DNS rankingrun.com.br no Resend
- P2: fullchain.pem + privkey.pem para mTLS real em producao

## Issues Conhecidas
- Redis instavel (restarts manuais)
- Resend: dominio nao verificado
