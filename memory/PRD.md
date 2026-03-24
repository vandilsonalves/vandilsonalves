# RunPro - Fitness Ranking Platform

## Problema Original
Plataforma de ranking fitness esportivo com rankings por categorias e cidades, painel "RAIO-X" avançado, integração com Strava, geração de share cards via Canvas API e painel de administração completo.

## Stack Tecnológico
- **Frontend:** React (CRA) + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI + MongoDB + WebSocket
- **Background Jobs:** Celery + Redis
- **Integrações:** Strava, Resend (e-mails)

## Arquitetura de Componentes

### AdminDashboard.jsx (~1450 linhas, limpo)
Shell principal do painel admin com sidebar. Componentes extraídos:
- DashboardGeral, DashboardAtletas, DashboardAssessorias, DashboardCorridas
- DashboardResultados, DashboardRBAC, DashboardSubmeter, DashboardAutorizacoes
- DashboardRegulamento, DashboardAniversariantes, DashboardInstagram
- DashboardMensagens (mensagens em massa + agendamento + leitura + splash)
- DashboardEngajamento (métricas de abertura/leitura ao longo do tempo)

### RankingPage.js (~232 linhas)
Sub-componentes: RankingProfissional, RankingGalera, RankingEquipes

### RaioXPage.jsx (~1815 linhas)
Canvas share card extraído para: `/utils/canvasShareGenerator.js`

## Funcionalidades Implementadas

### Concluído
- [x] Rankings (Profissional, Galera, Equipes, Por Cidade)
- [x] Compartilhamento Ranking/RaioX (Canvas 9:16)
- [x] Integração Strava
- [x] Painel Admin completo com RBAC
- [x] Sistema de Mensagens em massa (filtros geográficos, agendamento Celery/Redis)
- [x] Splash Screen global para mensagens urgentes
- [x] Stats de leitura de mensagens (Lidas/Não Lidas)
- [x] Dashboard de Engajamento (KPIs, gráficos, tabela)
- [x] WebSocket para notificações em tempo real (fix 403)
- [x] Refatoração massiva (AdminDashboard -62%, RankingPage -90%)
- [x] data-testid nos componentes críticos (RaioX, Strava, SplashScreen, Admin)

### Backlog
- [ ] Implementar "Exportar como PDF" no Raio-X do atleta (P2)
- [ ] Fix /api/admin/stats/categorias KeyError 'categoria' (P3, pre-existing)

## Endpoints Chave
- `GET /api/admin/mensagens/engajamento` - Dashboard de engajamento
- `GET /api/admin/mensagens/{id}/leitura` - Stats de leitura
- `POST /api/admin/mensagens/{id}/reenviar-splash` - Splash screen
- `GET /api/notificacoes/splash-pendente` - Splash pendente do atleta
- `WS /api/ws/notifications?token=JWT` - WebSocket notificações em tempo real

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Notas Importantes
- **Redis:** Pode cair no preview. Se Celery falhar, reinstalar Redis.
- **Rotas Splash:** Em `notificacoes_routes.py` para evitar conflito com path params.
- **WebSocket:** SECRET_KEY importada de auth_routes (fonte única). Conexão funciona mas pode cair rápido no preview Kubernetes.
