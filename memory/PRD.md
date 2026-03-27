# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas com monetizacao, feed social, Raio-X, Strava e notificacoes.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Stripe + Efi Bank PIX (efipay SDK)
- Emails: Resend (dominio rankingrun.com.br VERIFICADO)
- Messaging: Celery + Redis
- WebSocket: Notificacoes em tempo real
- Producao: Nginx mTLS + Docker + SSL (Let's Encrypt)

## Funcionalidades Implementadas

### Pagamento
- [x] Plano Lancamento: De R$197 por 5x R$19,40 (R$97 total)
- [x] Checkout Stripe (Cartao) + Efi Bank (PIX QR Code)
- [x] Webhook PIX com notificacoes push
- [x] Tela confirmacao PIX com confetti
- [x] Polling frontend 5s + ativacao automatica Premium
- [x] AccessGate + PrintProtection

### Notificacoes Push (27/03/2026)
- [x] WebSocket broadcast para admins quando pagamento confirmado
- [x] Toast notification no painel admin com detalhes do pagamento
- [x] Browser Notification API (push nativo do navegador)
- [x] Auto-refresh do Dashboard Financeiro ao receber pagamento
- [x] Notificacao para atleta (pagamento_confirmado)
- [x] Mesmo pattern implementado para Stripe e Efi Bank

### Email (27/03/2026)
- [x] Dominio rankingrun.com.br VERIFICADO no Resend
- [x] DKIM + SPF (MX + TXT) todos verificados
- [x] Remetente: noreply@rankingrun.com.br
- [x] Email de teste enviado com sucesso para qualquer destinatario

### Deploy Producao (27/03/2026)
- [x] Script deploy-producao.sh (SSL + mTLS + Docker)
- [x] Gera SSL via certbot (Let's Encrypt) automaticamente
- [x] Configura Nginx mTLS com CA Efi Bank
- [x] Verifica DNS antes de gerar certificado
- [x] Docker Compose com proxy + backend + frontend

### Dashboard Financeiro Admin
- [x] KPIs: Receita total, PIX, Cartao, Ticket medio
- [x] Grafico barras receita diaria/mensal com toggle
- [x] Donut chart distribuicao PIX vs Cartao
- [x] Tabela transacoes recentes
- [x] Auto-refresh via WebSocket

### Navegacao
- [x] Botao "Atleta Premium" no desktop e mobile

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Arquivos de Deploy
- /app/deploy-producao.sh - Script completo (SSL + mTLS + Docker)
- /app/docker-compose.mtls.yml - Docker Compose
- /app/backend/nginx/nginx-mtls.conf - Config Nginx
- /app/backend/certs/ - Certificados CA Efi Bank

## Issues Conhecidas
- Redis instavel (restarts manuais)
