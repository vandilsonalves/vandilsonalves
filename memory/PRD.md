# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas completa com monetizacao, feed social, Raio-X, Strava e notificacoes por email.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Stripe + Efi Bank (PIX via efipay SDK)
- Emails: Resend
- Messaging: Celery + Redis
- Producao: Nginx mTLS reverse proxy (Docker)

## Funcionalidades Implementadas

### Pagamento + Bloqueio
- [x] Plano Lancamento: De R$197 por 5x R$19,40 (R$97 total)
- [x] AccessGate + PrintProtection + require_premium_access
- [x] Checkout Stripe (Cartao de credito)
- [x] Checkout Efi Bank (PIX com QR Code)
- [x] Webhook Efi Bank skip-mTLS + HMAC
- [x] Tela de confirmacao PIX com confetti
- [x] Polling frontend 5s para confirmar pagamento
- [x] Ativacao automatica Premium apos pagamento

### mTLS Producao (27/03/2026)
- [x] Configuracao Nginx mTLS (nginx-mtls.conf)
- [x] Docker Compose para deploy (docker-compose.mtls.yml)
- [x] Script de deploy automatizado (deploy-mtls.sh)
- [x] Certificados CA Efi Bank (prod + homolog)
- [x] Endpoint admin suporta modo "mtls" e "skip_mtls"
- [x] ssl_verify_client com CA chain do Efi Bank
- [x] Redirect HTTP -> HTTPS

### Raio-X do Atleta
- [x] Exportar como PDF e Excel
- [x] Share Card Canvas 9:16

### Mobile Responsiveness
- [x] MobileNav drawer, overflow-x: hidden global

### Notificacoes por Email
- [x] Integracao Resend + Celery background

### Limpeza de Codigo (27/03/2026)
- [x] Removido import morto CardContent do AdminDashboard
- [x] Removidos states mortos assessoriaDetalhe e showAssessoriaModal

## Arquivos de Deploy mTLS
- /app/backend/nginx/nginx-mtls.conf - Config Nginx completa
- /app/backend/certs/efi-ca-prod.crt - CA Efi Bank producao
- /app/backend/certs/efi-ca-homolog.crt - CA Efi Bank homologacao
- /app/docker-compose.mtls.yml - Docker Compose com proxy mTLS
- /app/deploy-mtls.sh - Script automatizado de deploy

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Backlog
- P1: Verificar DNS rankingrun.com.br no Resend
- P2: Em producao: obter fullchain.pem e privkey.pem (Let's Encrypt) para habilitar mTLS real

## Issues Conhecidas
- Redis instavel (restarts manuais necessarios)
- Resend: dominio nao verificado (apenas vandy1250@gmail.com)
