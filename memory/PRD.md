# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas com monetizacao, feed social, Raio-X, Strava e notificacoes.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Efi Bank (PIX + Cartao de Credito) via SDK efipay
- Emails: Resend (dominio rankingrun.com.br VERIFICADO)
- Messaging: Celery + Redis
- WebSocket: Notificacoes em tempo real
- Producao: Nginx mTLS + Docker + SSL (Let's Encrypt)

## Funcionalidades Implementadas

### Pagamento
- [x] Plano Lancamento: R$97 total
- [x] Efi Bank PIX (QR Code, Copia e Cola, polling 5s, ativacao automatica)
- [x] Efi Bank Cartao de Credito (formulario inline, tokenizacao payment-token-efi, create_one_step_charge)
- [x] Seletor de Parcelas (1x a 12x) com valor atualizado dinamicamente no botao
- [x] Campo Telefone obrigatorio no formato brasileiro (DDD+numero)
- [x] Deteccao automatica de bandeira (Visa, Mastercard, Elo, Amex)
- [x] Webhook PIX com notificacoes push
- [x] Tela confirmacao com confetti (unificada PIX e Cartao)
- [x] AccessGate + PrintProtection
- [x] Tratamento correto de erros da API Efi (validation_error, recusa)

### Config Efi Bank
- EFI_PAYEE_CODE: f96ce1225005dfed63a78f3694fcbbc1
- EFI_SANDBOX: true (homologacao)

### Endpoints Efi
- POST /api/efi/pix/criar
- POST /api/efi/cartao/criar
- POST /api/efi/webhook/pix
- GET /api/efi/config
- GET /api/efi/pix/status/{txid}

### Notificacoes Push
- [x] WebSocket broadcast para admins quando pagamento confirmado (PIX e Cartao)
- [x] Toast + Browser Notification
- [x] Auto-refresh Dashboard Financeiro

### Email
- [x] Dominio rankingrun.com.br VERIFICADO no Resend (DKIM + SPF)

### Deploy Producao
- [x] Scripts deploy-producao.sh (SSL + mTLS + Docker)

### Dashboard Financeiro Admin
- [x] KPIs, graficos, tabela transacoes

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Issues Conhecidas
- Redis instavel (restarts manuais)

## Backlog
- P2: Relatorio Semanal Automatico por E-mail (Celery + Resend)
- P2: Corrigir atletas.forEach error no fetchStats
- P3: Limpeza de estados mortos no AdminDashboard.jsx
