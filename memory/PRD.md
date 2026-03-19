# Ranking Run Pró - PRD (Product Requirements Document)

## Original Problem Statement
Plataforma de ranking de atletas de corrida com sistema RBAC, monitoramento, cache Redis, Celery, WebSockets e refatoração do backend.

---

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Refatoração do server.py (P0)**
   - Removidos endpoints duplicados de ranking-corridas (927 linhas)
   - **Antes: 4347 linhas → Depois: 3421 linhas (-926 linhas)**
   - **Antes: 60 endpoints → Depois: 45 endpoints (-15 duplicatas)**
   - Total reduzido desde início da sessão: ~1100 linhas

2. **Exportação de Dados (P1)**
   - Endpoint CSV: `/api/liga-assessorias/exportar-dados/{equipe}?formato=csv`
   - Endpoint JSON: `/api/liga-assessorias/exportar-dados/{equipe}?formato=json`
   - Endpoint Gráficos: `/api/liga-assessorias/exportar-graficos/{equipe}`
   - Botões de exportação no Dashboard do Dono
   - CSV com UTF-8 BOM para compatibilidade Excel
   - **23/23 testes passando**

3. **Sistema de Reações no Feed (Sessão Anterior)**
   - 7 tipos: 👏🏃💪🔥❤️🎉🏆
   - Toggle de reações
   - UI com popover

4. **Novos Gráficos no Dashboard (Sessão Anterior)**
   - Gênero, Categoria, Faixa Etária (PieCharts)
   - Resultados/Atletas por Mês (Charts)
   - Distâncias Mais Corridas
   - Indicadores de Performance

---

## Architecture

### Backend Modules
```
/app/backend/routes/
├── auth_routes.py
├── atletas_routes.py
├── ranking_routes.py
├── admin_routes.py
├── assessorias_routes.py
├── feed_routes.py              # Reações
├── liga_assessorias_routes.py  # Gráficos + Exportação
├── ranking_corridas_routes.py  # Migrado do server.py
└── ... (outros)

/app/backend/server.py          # 3421 linhas, 45 endpoints
```

### Key Endpoints

**Exportação de Dados:**
- `GET /api/liga-assessorias/exportar-dados/{equipe}?formato=csv|json`
- `GET /api/liga-assessorias/exportar-graficos/{equipe}`

**Feed Social:**
- `POST /api/feed/posts/{post_id}/reagir` (reações)
- `GET /api/feed/reacoes-disponiveis`

**Gráficos Dashboard:**
- `GET /api/liga-assessorias/graficos-avancados/{equipe}`

---

## Test Reports
- `/app/test_reports/iteration_43.json` - Feed Social (24/24)
- `/app/test_reports/iteration_44.json` - Reações + Gráficos (23/23)
- `/app/test_reports/iteration_45.json` - Exportação (23/23)

---

## Pending Tasks

### P0 - Ainda Restante
- [ ] Continuar refatoração do server.py (ainda tem 3421 linhas)

### P2 - Backlog
- [ ] Configuração de REDIS_URL para produção
- [ ] Verificação de domínio no Resend
- [ ] Refatoração de componentes frontend grandes

### Descartado pelo Usuário
- ~~Sistema de Rivais~~
- ~~Desafios Mensais~~
- ~~Sistema de Níveis/XP~~

---

## Credentials
- **Test User**: admin@runpro.com / admin123
- **Preview URL**: https://community-feed-28.preview.emergentagent.com

---

*Última atualização: 19/Mar/2026*
