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
- [x] Plano Lancamento: De R$197 por 5x R$19,40 (R$97 total)
- [x] Efi Bank PIX (QR Code, Copia e Cola, polling 5s, ativacao automatica)
- [x] Efi Bank Cartao de Credito (formulario inline, tokenizacao payment-token-efi, create_one_step_charge)
- [x] Webhook PIX com notificacoes push
- [x] Tela confirmacao PIX com confetti
- [x] AccessGate + PrintProtection

### Integracao Efi Bank Cartao (27/03/2026)
- [x] Endpoint GET /api/efi/config (payee_code + environment)
- [x] Endpoint POST /api/efi/cartao/criar (one-step charge com payment_token)
- [x] Frontend: Formulario inline (numero, CVV, validade, titular, CPF, email)
- [x] Frontend: Deteccao automatica de bandeira (Visa, Mastercard, Elo, Amex)
- [x] Frontend: Tokenizacao segura via payment-token-efi v3.2.1
- [x] Funcao _ativar_acesso_efi unificada para PIX e Cartao
- [x] Notificacoes push para atleta e admin em ambos os tipos

### Notificacoes Push (27/03/2026)
- [x] WebSocket broadcast para admins quando pagamento confirmado
- [x] Toast notification no painel admin com detalhes do pagamento
- [x] Browser Notification API (push nativo do navegador)
- [x] Auto-refresh do Dashboard Financeiro ao receber pagamento
- [x] Notificacao para atleta (pagamento_confirmado)
- [x] Pattern implementado para PIX e Cartao via Efi Bank

### Email (27/03/2026)
- [x] Dominio rankingrun.com.br VERIFICADO no Resend
- [x] DKIM + SPF (MX + TXT) todos verificados
- [x] Remetente: noreply@rankingrun.com.br

### Deploy Producao (27/03/2026)
- [x] Script deploy-producao.sh (SSL + mTLS + Docker)
- [x] Gera SSL via certbot (Let's Encrypt) automaticamente
- [x] Configura Nginx mTLS com CA Efi Bank
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

## Config Efi Bank
- EFI_PAYEE_CODE: f96ce1225005dfed63a78f3694fcbbc1
- EFI_SANDBOX: true (homologacao)

## Arquivos de Deploy
- /app/deploy-producao.sh - Script completo (SSL + mTLS + Docker)
- /app/docker-compose.mtls.yml - Docker Compose
- /app/backend/nginx/nginx-mtls.conf - Config Nginx
- /app/backend/certs/ - Certificados CA Efi Bank

## Issues Conhecidas
- Redis instavel (restarts manuais)

## Backlog
- P2: Relatorio Semanal Automatico por E-mail (Celery + Resend)
- P2: Corrigir atletas.forEach error no fetchStats
- P3: Limpeza de estados mortos no AdminDashboard.jsx
