# RunPro - Fitness Ranking Platform

## Problema Original
Plataforma de ranking fitness esportivo com rankings por categorias e cidades, painel "RAIO-X" avançado, integração com Strava, geração de share cards via Canvas API e painel de administração completo.

## Stack Tecnológico
- **Frontend:** React (CRA) + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI + MongoDB + WebSocket
- **Background Jobs:** Celery + Redis
- **Integrações:** Strava, Resend (e-mails)

## Funcionalidades Implementadas

### Concluído
- [x] Rankings (Profissional, Galera, Equipes, Por Cidade)
- [x] Compartilhamento Ranking/RaioX (Canvas 9:16 completo: Score, Métricas, Evolução, Records, Comparativo, Previsões IA, Badges)
- [x] Exportar PDF/Excel no Raio-X
- [x] Integração Strava
- [x] Painel Admin completo com RBAC
- [x] Sistema de Mensagens em massa (filtros geográficos, agendamento Celery/Redis)
- [x] Splash Screen global para mensagens urgentes
- [x] Stats de leitura de mensagens (Lidas/Não Lidas)
- [x] Dashboard de Engajamento (KPIs, gráficos, tabela)
- [x] WebSocket para notificações em tempo real
- [x] Filtros Estado/Cidade na página de Atletas (Admin)
- [x] Filtros Estado/Cidade na página de Mensagens (Admin)
- [x] Fix distância total 0 km no Raio-X (extrair_distancia helper)
- [x] Refatoração massiva (AdminDashboard, RankingPage, RaioXPage)
- [x] Fix stats/categorias KeyError
- [x] data-testid nos componentes críticos

### Backlog
- [ ] Notificações push por email (Resend) para mensagens urgentes

## Endpoints Chave
- `GET /api/admin/mensagens/engajamento` - Dashboard de engajamento
- `GET /api/admin/stats/categorias` - Stats por categoria
- `GET /api/admin/atletas?limit=1000` - Lista atletas com estado/cidade
- `GET /api/raio-x/completo` - Dados completos do Raio-X
- `WS /api/ws/notifications?token=JWT` - WebSocket tempo real

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Notas
- **Redis:** Pode cair no preview. Reinstalar se Celery falhar.
- **Rotas Splash:** Em `notificacoes_routes.py` para evitar conflito path params.
- **Distância:** Função `extrair_distancia()` em raio_x_routes.py trata int, float, string (KM, K), None.
