# RunPro - Fitness Ranking Platform

## Problema Original
Plataforma de ranking fitness esportivo com rankings por categorias e cidades, painel "RAIO-X" avançado, integração com Strava, geração de share cards via Canvas API e painel de administração completo.

## Stack Tecnológico
- **Frontend:** React (CRA) + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI + MongoDB
- **Background Jobs:** Celery + Redis
- **Integrações:** Strava, Resend (e-mails)

## Arquitetura de Componentes (Pós-refatoração)

### AdminDashboard.jsx (~1657 linhas)
Shell principal do painel admin com sidebar. Componentes extraídos:
- `DashboardGeral` - Visão geral / estatísticas
- `DashboardAtletas` - Gestão de atletas
- `DashboardAssessorias` - Liga de assessorias
- `DashboardCorridas` - Gestão de corridas
- `DashboardResultados` - Aprovação de resultados
- `DashboardRBAC` - Controle de acesso
- `DashboardSubmeter` - Submeter resultados
- `DashboardAutorizacoes` - Gerenciar autorizações
- `DashboardRegulamento` - Editor de regulamento
- `DashboardAniversariantes` - Calendário de aniversários
- `DashboardInstagram` - Instagram Analytics
- `DashboardMensagens` - Mensagens em massa + agendamento + leitura stats + splash

### RankingPage.js (~232 linhas)
Shell com tab switcher. Componentes extraídos:
- `RankingProfissional` - Ranking por colocação
- `RankingGalera` - Ranking por distância
- `RankingEquipes` - Liga Nacional de Assessorias

### RaioXPage.jsx (~1813 linhas)
Canvas share card extraído para:
- `/utils/canvasShareGenerator.js`

## Funcionalidades Implementadas

### Concluído
- [x] Filtro Gênero/Modalidade no Ranking por Cidade
- [x] Compartilhamento do Ranking da Cidade (Canvas 9:16)
- [x] Bug fix: Zero Overlap Profissional vs Galera
- [x] Bug fix: Strava redirect_uri
- [x] Bug fix: Sincronização pontos/corridas
- [x] Renomeação "Povão" → "Galera" na UI
- [x] Endpoint admin para recalcular rankings
- [x] Migração datas 2025→2026 + ANO_ATUAL dinâmico
- [x] Aba Mensagens no Admin (filtros + notificações)
- [x] Agendamento de mensagens (Celery + Redis)
- [x] Refatoração AdminDashboard.jsx (3876→1657 linhas, -57%)
- [x] Refatoração RankingPage.js (2267→232 linhas, -90%)
- [x] Refatoração RaioXPage.jsx (2325→1813 linhas, -22%)
- [x] Filtros "Por Estado" e "Por Cidade" no Admin Mensagens
- [x] Botões "Selecionar Todos" e "Limpar" nos filtros Estado/Cidade
- [x] Sistema de visualização de leitura (Lidas/Não Lidas) no Admin Mensagens
- [x] Reenvio de mensagem como Splash Screen bloqueante
- [x] Componente SplashScreen.jsx global injetado no App.js
- [x] Bug fix: Rota splash-pendente conflitando com /notificacoes/{id} (movida para notificacoes_routes.py)
- [x] Bug fix: atletas.forEach is not a function no fetchStats (resposta paginada)
- [x] Redis reinstalado (v7.0.15)

### Backlog
- [ ] Limpeza de estado morto residual no AdminDashboard.jsx (P3)
- [ ] Implementar "Exportar como PDF" no Raio-X do atleta (P2)
- [ ] Adicionar mais data-testid onde necessário (P3)

## Endpoints Chave
- `POST /api/admin/mensagens/enviar` - Envio/agendamento de mensagens
- `POST /api/admin/recalcular-rankings` - Recálculo de rankings
- `GET /api/ranking/por-cidade/{estado}/{cidade}` - Ranking por cidade
- `GET /api/admin/mensagens/cidades?estado={UF}` - Filtro dinâmico de cidades
- `GET /api/admin/mensagens/{id}/leitura` - Stats de leitura (total, lidas, não lidas)
- `POST /api/admin/mensagens/{id}/reenviar-splash` - Força splash screen para quem não leu
- `GET /api/notificacoes/splash-pendente` - Splash pendente do atleta logado
- `POST /api/notificacoes/splash/{id}/confirmar` - Confirma leitura do splash

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Notas Importantes
- **Nomenclatura:** "Povão" substituído por "Galera" na UI. Backend/DB mantém `ranking_povao`.
- **Datas:** Sistema usa `ANO_ATUAL` dinâmico. NUNCA hardcode ano.
- **Redis:** Pode cair no ambiente preview. Se Celery falhar, reinstalar/restaurar Redis primeiro.
- **Rotas Splash:** Definidas em `notificacoes_routes.py` (não em mensagens_admin_routes.py) para evitar conflito com path param `{notificacao_id}`.
