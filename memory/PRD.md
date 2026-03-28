# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas com monetizacao, feed social, Raio-X, Strava e notificacoes.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Efi Bank PRODUCAO (PIX + Cartao de Credito) via SDK efipay
- Emails: Resend (dominio rankingrun.com.br VERIFICADO)
- Scheduler: APScheduler
- WebSocket: Notificacoes em tempo real

## Funcionalidades Implementadas

### Pagamento Efi Bank (PRODUCAO)
- [x] PIX (QR Code, Copia e Cola, polling 5s, ativacao automatica)
- [x] Cartao de Credito (formulario inline, tokenizacao, create_one_step_charge)
- [x] Seletor de Parcelas (1x a 12x)
- [x] Desbloqueio automatico: Premium ate 31/12/2026 apos pagamento
- [x] Bloqueio de vendas: A partir de 15/12/2026 pagamentos sao recusados
- [x] Certificado .p12 producao instalado (valido ate 2029)

### Autorizacoes Admin (28/03/2026)
- [x] POST /api/admin/autorizacoes/autorizar (tipo_plano: ate_fim_ano ou plano_anual)
- [x] POST /api/admin/autorizacoes/revogar (por atleta_id com confirmacao)
- [x] Botao "Ate 31/12/2026" (verde) para atletas nao autorizados
- [x] Botao "Anual" (azul) - 1 ano a partir da ativacao
- [x] Botao "Revogar" (vermelho) para atletas autorizados
- [x] GET /api/efi/pagamento/status - verifica se vendas estao abertas

### Painel de Conversao
- [x] Funil: Visitantes -> Cadastros -> Pagamentos
- [x] Toggle periodo (7d, 30d, Total)
- [x] Tendencia diaria (14 dias)

### Relatorio Semanal
- [x] APScheduler (domingos 20h) + endpoint manual

## Config
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456
- Efi Bank: PRODUCAO (is_sandbox=false)
- Certificado: /app/backend/certs/producao-pix.pem

## Regras de Negocio
- Pagamentos: abertos ate 14/12/2026. Bloqueados a partir de 15/12/2026.
- Apos bloqueio: apenas admin pode autorizar manualmente
- Premium via pagamento: valido ate 31/12/2026
- Plano Anual (admin): valido por 365 dias a partir da ativacao

## Issues Conhecidas
- Redis instavel (restarts manuais)
