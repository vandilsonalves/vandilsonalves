# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Ranking por Cidade/Bairro (P1)** - IMPLEMENTADO!
   - **Nova Página:** `/ranking-cidade` com visual profissional (gradiente verde)
   - **Filtros:** Estado, Cidade, Modalidade (Profissional/Amador ou Povão), Gênero
   - **Cards de Estatísticas:** Cidade, Estado, Total de Atletas
   - **Lista de Ranking:** Medalhas (🥇🥈🥉), badge Elite, pontos e corridas
   - **Busca de Cidade:** Input de pesquisa dentro do seletor de cidades
   - **Link no Header:** Botão "Por Cidade" na página principal
   - **16/16 testes passando** (`/app/test_reports/iteration_53.json`)
   
   **Arquivos criados:**
   - `/app/frontend/src/pages/RankingCidadePage.jsx` - Nova página
   - `/app/backend/routes/ranking_routes.py` - Endpoints: `/ranking/cidades`, `/ranking/por-cidade/{estado}/{cidade}`

2. **Sistema de Notificações Push (P0)** - IMPLEMENTADO!
   - WebSocket + Polling fallback (10s)
   - Toast para notificações importantes
   - Som de notificação
   - **15/16 testes passando** (`/app/test_reports/iteration_52.json`)

3. **Feed de Atividades Melhorado (P0)** - IMPLEMENTADO!
   - Posts automáticos de conquistas e resultados
   - Reações (8 tipos) + Comentários
   - Botão "Parabéns" para posts especiais
   - **21/21 testes passando** (`/app/test_reports/iteration_51.json`)

---

## Key Endpoints

**Ranking por Cidade (Novo):**
- `GET /api/ranking/estados` - Lista estados com atletas
- `GET /api/ranking/cidades` - Lista cidades com contagem de atletas
- `GET /api/ranking/cidades?estado=SP` - Cidades filtradas por estado
- `GET /api/ranking/por-cidade/{estado}/{cidade}` - Ranking da cidade
  - Query params: `modalidade` (profissional/povao), `genero` (M/F), `ano`, `limit`

**Notificações:**
- `GET /api/notificacoes` - Lista notificações
- `POST /api/notificacoes/{id}/ler` - Marca como lida
- `POST /api/notificacoes/ler-todas` - Marca todas como lidas

**Feed Social:**
- `GET /api/feed` - Lista posts
- `POST /api/feed/posts` - Cria post
- `POST /api/feed/posts/{id}/reagir` - Reações
- `POST /api/feed/posts/{id}/parabens` - Parabéns

---

## Test Reports
- `/app/test_reports/iteration_53.json` - Ranking por Cidade (16/16 passed)
- `/app/test_reports/iteration_52.json` - Notificações Push (15/16 passed)
- `/app/test_reports/iteration_51.json` - Feed Melhorado (21/21 passed)

---

## Pending Tasks

### P1 - Próximas Tarefas
- [ ] **Integração Strava/Garmin** - Importação automática de corridas (usar integration_playbook_expert_v2)
- [ ] **App Mobile (PWA)** - Configurar como Progressive Web App

### P2 - Backlog/Refatoração
- [ ] **Refatoração do RankingPage.js** - 2.100+ linhas
- [ ] **Refatoração do AdminDashboard.jsx** - 3.600+ linhas
- [ ] Verificação de domínio no Resend

### Concluído nesta sessão
- [x] Ranking por Cidade/Bairro
  - [x] Endpoint de cidades
  - [x] Endpoint de ranking por cidade
  - [x] Página frontend com filtros
  - [x] Link no header principal
- [x] Sistema de Notificações Push
- [x] Feed de Atividades Melhorado

---

## Credentials
- **Admin**: admin@runpro.com / admin
- **Preview URL**: https://feed-likes-comments.preview.emergentagent.com

---

## Known Issues
- **WebSocket 403:** Proxy Emergent bloqueia WebSocket. Polling ativo como fallback
- **Redis Supervisor:** Pode mostrar FATAL, mas funciona via `redis-cli ping`

---

*Última atualização: 19/Mar/2026*
