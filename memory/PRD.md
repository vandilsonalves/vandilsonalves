# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas com monetizacao, feed social, Raio-X, Strava e notificacoes.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Efi Bank (PIX + Cartao de Credito) via SDK efipay
- Emails: Resend (dominio rankingrun.com.br VERIFICADO)
- Scheduler: APScheduler (Relatorio semanal dom 20h, metricas 5min, alertas 1min, Strava 1h)
- WebSocket: Notificacoes em tempo real
- Producao: Nginx mTLS + Docker + SSL (Let's Encrypt)

## Funcionalidades Implementadas

### Pagamento Efi Bank
- [x] PIX (QR Code, Copia e Cola, polling 5s, ativacao automatica)
- [x] Cartao de Credito (formulario inline, tokenizacao payment-token-efi, create_one_step_charge)
- [x] Seletor de Parcelas (1x a 12x) com valor dinamico
- [x] Webhook PIX + Tela confirmacao confetti
- [x] Notificacoes push para atleta e admin

### Relatorio Semanal Automatico (28/03/2026)
- [x] Servico /app/backend/services/relatorio_semanal.py
- [x] Agendado via APScheduler (domingos 20:00)
- [x] Endpoint manual: POST /api/admin/financeiro/relatorio-semanal/enviar
- [x] HTML email com KPIs: receita semana, total atletas, novos cadastros, corridas, PIX vs Cartao
- [x] Enviado para todos os admins na collection administradores
- [x] Testado: 8/8 admins receberam o email via Resend

### Dashboard Financeiro Admin
- [x] KPIs corrigidos: filtra por campo tipo (pix/cartao) em vez de gateway
- [x] Graficos e tabela transacoes

### Bug Fix: atletas.forEach (28/03/2026)
- [x] Optional chaining em atletasRes.data?.atletas no AdminDashboard.jsx

### Limpeza AdminDashboard.jsx (28/03/2026)
- [x] Auditoria completa: todos estados e imports estao em uso (limpeza anterior ja removeu dead code)

## Config
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456
- EFI_PAYEE_CODE: f96ce1225005dfed63a78f3694fcbbc1
- EFI_SANDBOX: true

## Endpoints Efi
- POST /api/efi/pix/criar
- POST /api/efi/cartao/criar
- POST /api/efi/webhook/pix
- GET /api/efi/config
- GET /api/efi/pix/status/{txid}

## Issues Conhecidas
- Redis instavel (restarts manuais, APScheduler como alternativa)

## Backlog
- Nenhuma tarefa pendente prioritaria
