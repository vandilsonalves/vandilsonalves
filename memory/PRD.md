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
- [x] Webhook PIX skip-mTLS + HMAC + config Nginx mTLS producao
- [x] Tela confirmacao PIX com confetti
- [x] Polling frontend 5s + ativacao automatica Premium

### Dashboard Financeiro Admin (27/03/2026)
- [x] KPIs: Receita total, PIX, Cartao, Ticket medio
- [x] Grafico barras receita diaria/mensal com toggle
- [x] Donut chart distribuicao PIX vs Cartao
- [x] Tabela transacoes recentes com status/gateway/valor

### Navegacao
- [x] Botao "Atleta Premium" no header desktop (RankingPage.js) - 27/03/2026
- [x] Botao "Atleta Premium" no MobileNav
- [x] Menu "Financeiro" visivel para todos admins - 27/03/2026

### Raio-X, Mobile, Emails
- [x] Exportar PDF/Excel + Share Card
- [x] MobileNav drawer, overflow-x: hidden
- [x] Integracao Resend + Celery background

### DNS Resend (27/03/2026)
- [x] DKIM verificado
- [ ] SPF MX e TXT pendentes (DNS propagado, aguardando Resend detectar)
- [x] Remetente atualizado: noreply@send.rankingrun.com.br

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Backlog
- Verificacao SPF no Resend (aguardando auto-detect)
- Deploy producao: fullchain.pem + privkey.pem + deploy-mtls.sh

## Issues Conhecidas
- Redis instavel (restarts manuais)
