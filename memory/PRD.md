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
- [x] **Refatoração MAJOR do server.py** - Reduzido de 6263 para 4498 linhas (~28% reduction)
- [x] **Redis no Supervisor** - Auto-start configurado
- [x] **Celery no Supervisor** - Auto-start configurado com 2 workers

### Módulos Refatorados (16 módulos criados)
- `auth_routes.py` - Autenticação
- `notificacoes_routes.py` - Sistema de notificações
- `conquistas_routes.py` - Conquistas/badges
- `atletas_routes.py` - Perfil do atleta
- `resultados_routes.py` - Resultados de corridas
- `ranking_routes.py` - Rankings (com cache Redis)
- `rbac.py` - Controle de acesso
- `admin_routes.py` - Gestão administrativa
- `assessorias_routes.py` - Liga de assessorias
- `corridas_eventos_routes.py` - Eventos e corridas
- `aniversariantes_routes.py` - Sistema de aniversariantes
- `instagram_routes.py` - Analytics do Instagram
- `monitoring_routes.py` - Monitoramento de saúde
- `celery_routes.py` - Tarefas assíncronas
- `websocket_routes.py` - Notificações em tempo real

### Backlog (P2-P3)
- [ ] **Verificar domínio no Resend** - Atualmente usando `onboarding@resend.dev` (domínio de teste)
  - Só envia para o email do dono da conta Resend
  - Para produção: verificar domínio próprio em https://resend.com/domains
- [ ] Testes automatizados completos
- [ ] Documentação Swagger da API

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
├── server.py           # Reduzido de 6263 para 4498 linhas
├── routes/             # 16 módulos de rotas
│   ├── auth_routes.py
│   ├── ranking_routes.py
│   ├── admin_routes.py
│   ├── assessorias_routes.py
│   ├── aniversariantes_routes.py
│   ├── instagram_routes.py
│   ├── monitoring_routes.py
│   ├── websocket_routes.py
│   └── ... (8 outros)
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

### Admin (via admin_routes.py)
- GET /api/admin/pendentes
- POST /api/admin/aprovar/{id}
- GET /api/admin/stats
- GET /api/admin/atletas

### Liga Assessorias (via assessorias_routes.py)
- GET /api/liga-assessorias/ranking
- GET /api/liga-assessorias/stats

### Monitoring
- GET /api/health
- GET /api/monitoring/dashboard

---

## Test Credentials
- **Super Admin**: admin@rankingrun.com / admin123
- **Atleta Masculino**: rafael_souza_1@email.com / senha123
- **Atleta Feminina**: raquel_pereira_21@email.com / senha123

---

## Refactoring Summary (Session March 11, 2026)

### Lines Removed from server.py: ~1765 lines
- Endpoints de admin (pendentes, stats, atletas) → admin_routes.py
- Endpoints de ranking (povao, semanal, mensal) → ranking_routes.py
- Endpoints de assessorias/liga → assessorias_routes.py
- Endpoints de aniversariantes → aniversariantes_routes.py
- Endpoints de instagram (analises) → instagram_routes.py

### Bug Fixes Applied
- Login RBAC lento (25s → 1.3s) - geolocalização em background
- Redefinições de funções duplicadas corrigidas
- Imports de funções entre módulos corrigidos
