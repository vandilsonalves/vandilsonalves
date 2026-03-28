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
- [x] Validacao rigorosa de status: somente "approved"/"paid" ativa premium
- [x] Aviso de sandbox no frontend e backend quando EFI_SANDBOX=true
- [x] Webhook PIX + Tela confirmacao confetti
- [x] Notificacoes push para atleta e admin (PIX e Cartao)

### Painel de Conversao (28/03/2026)
- [x] Endpoint GET /api/admin/financeiro/conversao
- [x] Funil visual: Visitantes -> Cadastros -> Pagamentos com taxas percentuais
- [x] Toggle de periodo: 7 dias / 30 dias / Total
- [x] Tendencia diaria (14 dias) com grafico de barras
- [x] Middleware de tracking de visitantes unicos por dia (IP+UA hash)

### Relatorio Semanal Automatico (28/03/2026)
- [x] APScheduler (domingos 20:00) + endpoint manual POST /api/admin/financeiro/relatorio-semanal/enviar
- [x] Email HTML: receita, atletas, corridas, PIX vs Cartao

### Bug Fixes (28/03/2026)
- [x] atletas.forEach: optional chaining (atletasRes.data?.atletas)
- [x] financeiro_routes: filtro tipo=="cartao" em vez de gateway=="stripe"
- [x] Label "Cartao (Stripe)" -> "Cartao (Efi Bank)" no DashboardFinanceiro
- [x] Telefone formato Efi: regex ^[1-9]{2}9?[0-9]{8}$

### Dashboard Financeiro Admin
- [x] KPIs, graficos, tabela transacoes
- [x] Funil de Conversao integrado
- [x] Auto-refresh via WebSocket

## Config
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456
- EFI_PAYEE_CODE: f96ce1225005dfed63a78f3694fcbbc1
- EFI_SANDBOX: true

## Issues Conhecidas
- Redis instavel (restarts manuais)
- Sandbox Efi: cartoes NAO sao validados por saldo/bloqueio (comportamento esperado em homologacao)

## Backlog
- Nenhuma tarefa pendente prioritaria
