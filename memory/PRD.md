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

### Completed (19/Mar/2026)
- [x] Sistema RBAC completo
- [x] Sistema de Monitoramento de Saúde
- [x] Cache com Redis integrado
- [x] Celery para tarefas assíncronas
- [x] WebSocket para notificações em tempo real
- [x] Sistema de Aprovação de Membros para Assessorias
- [x] Upload de Foto da Assessoria
- [x] Botão "Solicitar Entrada" em assessorias públicas
- [x] Web Scraper com Playwright para sites JavaScript
- [x] Gráficos no Dashboard do Dono de Assessoria
- [x] **Feed Social (apenas curtidas)** - Posts com texto/imagem, curtidas, trending
- [x] **Refatoração: liga_assessorias_routes.py** - Estados, cidades, comparação mensal
- [x] **Refatoração: ranking_corridas_routes.py** - Ranking de corridas, avaliações, reputação

### Feed Social - Funcionalidades (19/Mar/2026)
- **Criar posts**: Texto (máx 1000 chars) + imagem opcional
- **Curtidas**: Toggle curtir/descurtir com notificação
- **Trending**: Posts em alta baseado em curtidas (últimas 24h)
- **Meus posts**: Listagem de posts do próprio usuário
- **Deletar post**: Soft delete (autor ou admin)
- **SEM COMENTÁRIOS**: Funcionalidade removida conforme solicitação do usuário

### Refatoração do Backend (EM PROGRESSO)
**Arquivos de rotas criados:**
- `/app/backend/routes/liga_assessorias_routes.py` - Liga de assessorias
- `/app/backend/routes/ranking_corridas_routes.py` - Ranking e avaliação de corridas

**Ainda no server.py (para refatorar):**
- Endpoints de ranking duplicados (precisam ser removidos)
- Endpoints de admin diversos
- Funções de Instagram
- Funções de regulamento
- Funções de autorizações

---

## Architecture

### Backend Structure
```
/app/backend/
├── routes/
│   ├── auth_routes.py         # Autenticação (login, registro, me)
│   ├── atletas_routes.py      # Perfil, foto, troca equipe
│   ├── ranking_routes.py      # Rankings (povão, semanal, mensal)
│   ├── admin_routes.py        # Gestão de atletas, aprovações
│   ├── assessorias_routes.py  # Assessorias, solicitações, foto
│   ├── feed_routes.py         # Feed Social (posts, curtidas)
│   ├── liga_assessorias_routes.py  # Liga de assessorias [NOVO]
│   ├── ranking_corridas_routes.py  # Ranking de corridas [NOVO]
│   └── ... (outros módulos)
├── services/
│   ├── cache_service.py       # Redis cache
│   ├── monitoring_service.py  # Métricas
│   └── scraping_corridas.py   # Scraper com Playwright
├── models/
│   ├── __init__.py           # Pydantic models
│   └── rbac.py               # Models RBAC
└── server.py                  # FastAPI app + rotas não migradas
```

### Frontend Structure
```
/app/frontend/src/
├── pages/
│   ├── RankingPage.js         # Página principal de ranking
│   ├── FeedPage.jsx           # Feed Social [ATUALIZADO]
│   ├── DonoAssessoriaDashboard.jsx  # Dashboard do dono
│   ├── AssessoriaPage.jsx     # Página pública da assessoria
│   └── ... (outras páginas)
└── components/
    ├── ui/                    # Shadcn components
    └── NotificacoesBell.jsx   # Componente de notificações
```

---

## Pending Tasks (P0-P2)

### P0 - Crítico
- [ ] Remover endpoints duplicados do server.py (ranking-corridas, liga-assessorias)
- [ ] Continuar refatoração do server.py (ainda 4500+ linhas)

### P1 - Alta Prioridade
- [ ] Implementar Sistema de Rivais (placeholder criado)
- [ ] Mais gráficos para Dono de Assessoria
- [ ] Exportação de dados dos gráficos

### P2 - Média/Baixa Prioridade
- [ ] Desafios Mensais
- [ ] Sistema de Níveis/XP
- [ ] Configuração de REDIS_URL para produção
- [ ] Verificação de domínio no Resend
- [ ] Refatoração de componentes grandes do frontend

---

## Known Issues
- **Redis instável**: Pode precisar reinstalar com `sudo apt-get install --reinstall redis-server && sudo service redis-server start`
- **Funções vazias de Instagram**: `buscar_instagram_api_direta` e `buscar_instagram_rapidapi` estão vazias

---

## Test Reports
- `/app/test_reports/iteration_43.json` - Feed Social e módulos refatorados (24/24 testes passando)

---

## API Credentials
- **Test User**: admin@runpro.com / admin123
- **Preview URL**: https://community-feed-28.preview.emergentagent.com

---

*Última atualização: 19/Mar/2026*
