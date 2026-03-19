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

---

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Refatoração do server.py (P0)**
   - Removidos endpoints duplicados de liga-assessorias e ranking-corridas
   - Reduzido de 4519 para 4347 linhas (-172 linhas)
   - Reduzido de 63 para 60 endpoints (-3 duplicatas)

2. **Sistema de Reações no Feed Social (P1)**
   - Substituído sistema de curtidas por 7 tipos de reações:
     - 👏 Aplausos, 🏃 Correndo, 💪 Força, 🔥 Em chamas
     - ❤️ Amei, 🎉 Celebrando, 🏆 Campeão
   - Toggle de reações (adicionar/alterar/remover)
   - Notificações ao autor do post
   - UI com popover para seleção de reações
   - Collection MongoDB: `feed_reacoes`

3. **Novos Gráficos no Dashboard do Dono (P1)**
   - Distribuição por Gênero (PieChart)
   - Distribuição por Categoria (PieChart)
   - Distribuição por Faixa Etária (BarChart)
   - Resultados por Mês - últimos 6 meses (AreaChart)
   - Distâncias Mais Corridas (BarChart horizontal)
   - Novos Atletas por Mês (BarChart)
   - Indicadores de Performance (cards com métricas)
   - Endpoint: `/api/liga-assessorias/graficos-avancados/{nome_equipe}`

### ✅ Previously Completed
- Sistema RBAC completo
- Sistema de Monitoramento de Saúde
- Cache com Redis integrado
- Celery para tarefas assíncronas
- WebSocket para notificações em tempo real
- Sistema de Aprovação de Membros para Assessorias
- Upload de Foto da Assessoria
- Botão "Solicitar Entrada" em assessorias públicas
- Web Scraper com Playwright
- Sistema de Badges com 13 tipos
- Sistema de Indicação de Amigos

---

## Architecture

### Backend Structure
```
/app/backend/
├── routes/
│   ├── auth_routes.py           # Autenticação
│   ├── atletas_routes.py        # Perfil de atletas
│   ├── ranking_routes.py        # Rankings
│   ├── admin_routes.py          # Gestão administrativa
│   ├── assessorias_routes.py    # Assessorias e solicitações
│   ├── feed_routes.py           # Feed Social com Reações ✅ ATUALIZADO
│   ├── liga_assessorias_routes.py  # Liga + Gráficos avançados ✅ ATUALIZADO
│   ├── ranking_corridas_routes.py  # Ranking de corridas ✅ CRIADO
│   └── ... (outros módulos)
├── services/
│   ├── cache_service.py
│   ├── monitoring_service.py
│   └── scraping_corridas.py
└── server.py                    # FastAPI app (4347 linhas, 60 endpoints)
```

### Frontend Structure
```
/app/frontend/src/
├── pages/
│   ├── FeedPage.jsx           # Feed com Sistema de Reações ✅ ATUALIZADO
│   ├── DonoAssessoriaDashboard.jsx  # +7 novos gráficos ✅ ATUALIZADO
│   └── ... (outras páginas)
└── components/
    └── ui/                    # Shadcn components
```

---

## Key API Endpoints

### Feed Social (Reações)
- `GET /api/feed/reacoes-disponiveis` - Lista reações disponíveis
- `POST /api/feed/posts/{post_id}/reagir` - Adicionar/alterar/remover reação
- `GET /api/feed/posts/{post_id}/reacoes` - Reações de um post agrupadas
- `GET /api/feed` - Feed com reações (requer auth)
- `GET /api/feed/trending` - Posts em alta baseado em reações

### Gráficos Avançados
- `GET /api/liga-assessorias/graficos-avancados/{nome_equipe}` - Dados para gráficos (requer dono_assessoria ou admin)

---

## Pending Tasks

### P0 - Crítico
- [ ] Continuar refatoração do server.py (ainda tem 4347 linhas)

### P1 - Descartado pelo Usuário
- ~~Sistema de Rivais~~
- ~~Desafios Mensais~~
- ~~Sistema de Níveis/XP~~

### P2 - Backlog
- [ ] Exportação de dados dos gráficos (CSV/PDF)
- [ ] Configuração de REDIS_URL para produção
- [ ] Verificação de domínio no Resend
- [ ] Refatoração de componentes grandes do frontend

---

## Known Issues
- **Redis instável**: Use `sudo apt-get install --reinstall redis-server && sudo service redis-server start` se necessário
- **Funções vazias de Instagram**: `buscar_instagram_api_direta` e `buscar_instagram_rapidapi` estão vazias

---

## Test Reports
- `/app/test_reports/iteration_43.json` - Feed Social (24/24 passed)
- `/app/test_reports/iteration_44.json` - Reações + Gráficos (23/23 passed)

---

## Credentials
- **Test User**: admin@runpro.com / admin123
- **Preview URL**: https://community-feed-28.preview.emergentagent.com

---

*Última atualização: 19/Mar/2026*
