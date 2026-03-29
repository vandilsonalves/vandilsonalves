# Ranking Run Pro - PRD

## Problema Original
Plataforma de ranking de corridas de rua no Brasil. Sistema full-stack (React/FastAPI/MongoDB) com rankings profissionais, amadores ("Galera"), equipes (Liga de Assessorias) e corridas. Inclui sistema de insígnias, compartilhamento via Canvas, pagamentos via Efí Bank e painel administrativo completo.

## Arquitetura
- **Frontend**: React + Shadcn/UI + Recharts
- **Backend**: FastAPI + MongoDB (Motor async)
- **Cache**: cachetools (in-memory) - Redis/Celery foram removidos
- **Agendamento**: APScheduler (nativo Python)
- **Pagamentos**: Efí Bank (PRODUÇÃO REAL)
- **Compressão**: GZip Middleware

## O que foi implementado

### Sessão Anterior (Refatoração/Features)
- Refatoração de AdminDashboard.jsx (3876→1657 linhas)
- Refatoração de RankingPage.js (2267→232 linhas)
- Refatoração de RaioXPage.jsx (-22% com extração canvas)
- Filtros "Por Estado" e "Por Cidade" no Admin Mensagens
- Botões "Selecionar Todos" e "Limpar" nos filtros
- Sistema de visualização de leitura de mensagens (Lidas/Não lidas)
- Reenvio de mensagem como Splash Screen
- Componente SplashScreen.jsx global no App.js

### Sessão Anterior (Performance/Features)
- Remoção completa de Redis/Celery → cachetools + APScheduler
- Faixa etária "Até 17 anos" nos rankings
- Correção do erro fatal Canvas (null style) usando React state
- Rankings Semanais/Mensais e "Destaque do Mês" filtrados por Modalidade
- Insígnias "Top 10 do Mês" e "Rei da Velocidade" por Modalidade
- Card de compartilhamento de Insígnias formato 9:16 com foto e download
- Guia de Insígnias com 17 insígnias em formato 3D
- GZip Middleware (-78% payload)
- +14 índices MongoDB
- Paginação na página de Ranking de Corridas

### Sessão Atual (29/03/2026)
- Paginação "Carregar Mais" (20 itens/página) no RankingProfissional ✅
- Paginação "Carregar Mais" (20 itens/página) no RankingGalera ✅
- Paginação "Carregar Mais" (20 itens/página) no RankingEquipes ✅
- Correção de erro de parsing no RankingGalera.jsx (fragment wrapper) ✅
- Componente reutilizável LoadMoreButton.jsx com barra de progresso visual + percentual ✅
- Aplicado em todos os 4 rankings (Profissional, Galera, Equipes, Corridas) ✅
- Testes: 14/14 backend, 100% frontend (iteration_90)

## Backlog Priorizado

### P2
- Exportar como PDF no Raio-X do atleta (usar canvasShareGenerator.js)

### P3
- Limpeza de código morto: pasta tasks/, celery_app.py, rotas antigas Stripe
- Limpeza de states obsoletos no AdminDashboard.jsx

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Integrações
- Efí Bank (Pagamentos) - PRODUÇÃO REAL
- Resend (Emails)
- Strava (Atividades)

## Notas Importantes
- NÃO iniciar Redis ou Celery (removidos da arquitetura)
- Pagamentos em PRODUÇÃO REAL (não testar com dados falsos)
- App.js usa imports diretos (sem React.lazy - causava lag mobile)
- Acesso 90% via celular - performance é prioridade
