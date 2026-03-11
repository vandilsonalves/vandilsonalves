# Ranking Run Pró - PRD (Product Requirements Document)

## Original Problem Statement
O usuário solicitou a reestruturação do painel de administração e implementação de um sistema completo de gerenciamento de ranking para corridas, incluindo:
1. Sistema RBAC (Role Based Access Control)
2. Sistema de Monitoramento de Saúde do Backend
3. Cache Inteligente com Redis
4. Filas de Tarefas com Celery
5. Notificações em Tempo Real via WebSocket
6. Refatoração do backend monolítico (server.py) em módulos

## User Personas
- **Super Admin**: Acesso total ao sistema, gerencia outros admins
- **Colaborador Admin**: Acesso limitado baseado em permissões RBAC
- **Atleta Profissional/Amador**: Participa do ranking por colocação
- **Atleta Povão (Pace Livre)**: Participa do ranking por distância acumulada
- **Dono de Assessoria**: Visualiza relatórios da sua equipe

## Core Requirements

### 1. Sistema de Ranking (DONE)
- Ranking Profissional/Amador por categoria, gênero, faixa etária
- Ranking Povão (Pace Livre) por distância acumulada
- Rankings Semanal e Mensal
- Destaques do mês
- Exportação CSV/Excel

### 2. Sistema RBAC (DONE)
- Múltiplos níveis de administradores
- Permissões granulares por funcionalidade
- Logs de auditoria de todas as ações
- Conta de emergência para recuperação
- 2FA opcional para admins

### 3. Sistema de Monitoramento (DONE)
- Métricas em tempo real (CPU, memória, requisições)
- Dashboard visual no frontend
- Alertas automáticos por email para anomalias
- Histórico de métricas para análise

### 4. Cache com Redis (DONE)
- Cache inteligente para endpoints de alto tráfego
- Invalidação automática por TTL
- Cache de rankings para melhor performance

### 5. Filas com Celery (DONE)
- Processamento assíncrono de tarefas pesadas
- Recálculo de rankings em background
- Envio de emails em massa

### 6. WebSocket Notifications (DONE)
- Notificações em tempo real para usuários conectados
- Alertas para admins sobre eventos do sistema
- Persistência de notificações no banco

---

## Implementation Status

### Completed (March 2026)
- [x] Sistema RBAC completo
- [x] Sistema de Monitoramento de Saúde
- [x] Cache com Redis integrado
- [x] Celery para tarefas assíncronas
- [x] WebSocket para notificações em tempo real
- [x] Bug fix: Geolocalização não bloqueante no login (~25s -> ~1.3s)
- [x] Instalação do Redis no ambiente
- [x] Refatoração parcial do server.py (~200 linhas removidas)

### In Progress
- [ ] Refatoração completa do server.py
  - Módulos criados: 16 (auth, notificacoes, conquistas, atletas, resultados, ranking, rbac, admin, assessorias, corridas_eventos, aniversariantes, instagram, monitoring, celery, websocket)
  - Código duplicado ainda presente no server.py
  - Próximo: Remover endpoints duplicados de admin, assessorias, instagram, aniversariantes

### Backlog (P2-P3)
- [ ] Verificar domínio no Resend para emails de produção (P3)
- [ ] Testes automatizados completos
- [ ] Documentação da API (Swagger)

---

## Technical Architecture

### Backend Stack
- FastAPI (Python 3.11)
- MongoDB (Motor async driver)
- Redis (Cache + Celery broker)
- Celery (Task queue)
- WebSockets (Notificações tempo real)

### Frontend Stack  
- React 18
- Tailwind CSS + shadcn/ui
- Context API para estado global
- Custom hooks (useWebSocketNotifications)

### File Structure
```
/app/backend/
├── server.py           # Monolítico (alvo da refatoração)
├── routes/
│   ├── auth_routes.py
│   ├── ranking_routes.py  # Com cache Redis
│   ├── admin_routes.py
│   ├── monitoring_routes.py
│   ├── websocket_routes.py
│   └── ... (16 módulos)
├── services/
│   ├── cache_service.py
│   ├── monitoring_service.py
│   ├── websocket_service.py
│   └── rbac_service.py
└── celery_worker.py

/app/frontend/src/
├── pages/admin/
│   ├── AdminDashboard.jsx
│   └── dashboards/
│       ├── DashboardMonitoring.jsx
│       └── DashboardRBAC.jsx
└── hooks/
    └── useWebSocketNotifications.js
```

---

## Key API Endpoints

### Ranking (via ranking_routes.py)
- GET /api/ranking/povao
- GET /api/ranking/semanal
- GET /api/ranking/mensal
- GET /api/ranking/destaque-mes
- GET /api/ranking/categoria/{categoria}/{genero}

### Monitoring
- GET /api/health
- GET /api/monitoring/dashboard
- GET /api/monitoring/history

### WebSocket
- WS /api/ws/notifications?token=JWT

### Cache
- GET /api/monitoring/cache
- POST /api/monitoring/cache/invalidate

---

## Test Credentials
- **Super Admin**: admin@rankingrun.com / admin123
- **Atleta Masculino**: rafael_souza_1@email.com / senha123
- **Atleta Feminina**: raquel_pereira_21@email.com / senha123

---

## Known Issues
- Redis não persiste entre restarts (deve ser iniciado manualmente)
- Celery worker não configurado no supervisor ainda

---

## Next Priority Tasks
1. Continuar refatoração do server.py (remover código dos módulos já criados)
2. Adicionar Celery ao supervisor para auto-start
3. Configurar persistência do Redis
