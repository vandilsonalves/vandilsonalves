# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas com monetizacao, feed social, Raio-X, Strava e notificacoes.

## Arquitetura
- Frontend: React + TailwindCSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor)
- Pagamentos: Efi Bank PRODUCAO (PIX + Cartao)
- Emails: Resend (rankingrun.com.br)
- Scheduler: APScheduler
- WebSocket: Notificacoes em tempo real

## Funcionalidades Implementadas

### Pagamento Efi Bank (PRODUCAO)
- [x] PIX + Cartao de Credito (parcelas 1x-12x)
- [x] Desbloqueio automatico: Premium ate 31/12/2026
- [x] Bloqueio vendas: a partir 15/12/2026
- [x] Certificado .p12 producao (valido ate 2029)

### Integracao Autorizacoes <-> Financeiro (28/03/2026)
- [x] Autorizacao manual cria transacao financeira automaticamente
- [x] Transacao manual: gateway=admin_manual, amount=0, is_manual=true
- [x] Tag "Pago?" (amarelo com ?) para cortesias/pagamentos externos
- [x] Tooltip no hover: "Autorizado manualmente por [Admin]"
- [x] Badge "Manual" (amarelo) na coluna Gateway
- [x] Valor mostra "Cortesia" em vez de R$0
- [x] Manual/Cortesia aparece na distribuicao por gateway

### Exportacao Financeira (28/03/2026)
- [x] Botao "Exportar Dados" no canto superior direito
- [x] PDF: Resumo geral + tabela detalhada (fpdf2)
- [x] Excel: 2 abas - Resumo Geral + Transacoes Detalhadas (openpyxl)
- [x] Ambos incluem: origem (Cortesia/PIX/Cartao), admin responsavel

### Autorizacoes Admin
- [x] Botao "Ate 31/12/2026" (verde)
- [x] Botao "Anual" (azul) - 1 ano a partir da ativacao
- [x] Botao "Revogar" (vermelho) com confirmacao

### Dashboard Financeiro Admin
- [x] KPIs: Receita Total, PIX, Cartao, Ticket Medio
- [x] Distribuicao: PIX / Cartao / Manual-Cortesia
- [x] Funil de Conversao (Visitantes -> Cadastros -> Pagamentos)
- [x] Relatorio Semanal (APScheduler dom 20h + endpoint manual)

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Regras de Negocio
- Pagamentos abertos ate 14/12/2026
- Apos 15/12/2026: apenas admin autoriza manualmente
- Premium via pagamento: ate 31/12/2026
- Plano Anual (admin): 365 dias a partir da ativacao

## Issues Conhecidas
- ~~Redis instavel (restarts manuais)~~ RESOLVIDO (28/03/2026): Redis eliminado completamente. Cache em memoria (cachetools) + asyncio background tasks

## Migracoes Realizadas (28/03/2026)
- Redis -> cachetools (TTLCache em memoria) para cache
- Celery -> asyncio.create_task para tarefas em background
- celery_routes.py reescrito sem dependencia de Redis/Celery
- feed_routes.py e server.py: redis_client removido
- requirements.txt: redis e celery removidos, cachetools adicionado
- Rankings por Periodo (Semanal/Mensal) filtrados por modalidade (Masculino, Feminino, PCD/M, PCD/F, Cadeirante/M, Cadeirante/F)
- Badges "Top 10 do Mes" e "Rei da Velocidade" agora verificados por modalidade

## Backlog
- P2: Exportar como PDF no Raio-X do atleta
- P3: Limpeza de arquivos mortos (tasks/, celery_app.py, pagamentos_routes.py antigo)
