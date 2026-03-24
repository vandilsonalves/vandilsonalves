# RunPro - Fitness Ranking Platform

## Problema Original
Plataforma de ranking fitness esportivo com rankings por categorias e cidades, painel "RAIO-X" avançado, integração com Strava, geração de share cards via Canvas API e painel de administração completo.

## Stack Tecnológico
- **Frontend:** React (CRA) + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI + MongoDB + WebSocket
- **Background Jobs:** Celery + Redis
- **Integrações:** Strava, Resend (e-mails)

## Funcionalidades Implementadas (Todas Concluídas)
- [x] Rankings (Profissional, Galera, Equipes, Por Cidade)
- [x] Compartilhamento Ranking/RaioX (Canvas 9:16)
- [x] Exportar PDF/Excel no Raio-X
- [x] Integração Strava
- [x] Painel Admin completo com RBAC
- [x] Sistema de Mensagens em massa (filtros geográficos, agendamento Celery/Redis)
- [x] Splash Screen global para mensagens urgentes
- [x] Stats de leitura de mensagens (Lidas/Não Lidas)
- [x] Dashboard de Engajamento (KPIs, gráficos, tabela)
- [x] WebSocket para notificações em tempo real
- [x] Refatoração massiva (AdminDashboard, RankingPage, RaioXPage)
- [x] Fix stats/categorias KeyError
- [x] data-testid nos componentes críticos

## Endpoints Chave
- `GET /api/admin/mensagens/engajamento` - Dashboard de engajamento
- `GET /api/admin/stats/categorias` - Stats por categoria (fixado)
- `WS /api/ws/notifications?token=JWT` - WebSocket tempo real

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Notas
- Redis pode cair no preview. Reinstalar se Celery falhar.
- Rotas Splash em `notificacoes_routes.py` (evitar conflito path params).
