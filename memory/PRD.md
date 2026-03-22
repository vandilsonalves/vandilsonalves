# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (22/Mar/2026)

### ✅ Latest Fix: Frontend de Moderação do Feed - CORRIGIDO! (22/Mar/2026)

**Problema reportado:** "Sistema de Moderação do Feed não está funcionando"

**Diagnóstico:** O backend estava funcionando corretamente (retornando HTTP 400 com mensagem estruturada), mas o frontend não estava exibindo o toast de erro corretamente.

**Correções aplicadas:**

1. **FeedPage.jsx - `handleComentar`:**
   - Adicionada verificação robusta `errorData.message` para detectar erros de moderação
   - Adicionado `setTimeout` para mostrar toasts em sequência (evita sobreposição)
   - Adicionado log de debug para facilitar troubleshooting futuro

2. **FeedPage.jsx - `handleCriarPost`:**
   - Adicionado tratamento completo de erros de moderação (antes não existia)
   - Posts agora também são moderados com feedback visual

3. **feed_routes.py - `criar_post`:**
   - Adicionada chamada à moderação antes de criar o post
   - Usuários bloqueados não conseguem postar

**Teste visual confirmado:** Toast "💡 Linguagem ofensiva pode machucar..." aparece corretamente

---

### ✅ Sistema de Moderação do Feed (Backend + Frontend)

**Sistema completo de moderação de conteúdo:**

1. **Serviço de Moderação** (`/app/backend/services/moderacao_service.py`):
   - Lista de palavras/frases proibidas em 7 categorias
   - Normalização de texto para detectar tentativas de burla (p1ca → pica)
   - Análise de contexto esportivo ("matei o treino" = OK)
   - Sistema de níveis: LEVE (aviso), MÉDIO (ocultar), GRAVE (bloquear)

2. **Categorias de Bloqueio:**
   - 🚫 Spam/Fraude (ganhe dinheiro, renda extra, etc.)
   - ⚠️ Ameaças/Violência (vou te matar, te arrebento, etc.)
   - 🚫 Ofensas diretas (idiota, burro, fdp, etc.)
   - 🚫 Conteúdo sexual/vulgar
   - ⚠️ Discriminação (racismo, homofobia, misoginia)
   - 🚫 Bullying/Humilhação

3. **Selo de Atleta Respeitoso 🏅:**
   - Usuários sem infrações ganham o selo
   - Critérios: Score >= 80, 10+ comentários aprovados, zero bloqueios em 90 dias
   - Exibido ao lado do nome nos comentários

4. **Feedback Educativo:**
   - Mensagens explicativas quando comentário/post é bloqueado
   - Níveis visuais: 🚫 grave, ⚠️ médio, ℹ️ leve
   - Toast com mensagem educativa exibido no frontend

5. **Regra de Transferência de Atletas:**
   - Pontos conquistados ficam na assessoria onde foram obtidos
   - Não acompanham o atleta em caso de mudança de equipe
   - Histórico de equipes registrado

### ✅ Bug Fixes (Completed)

1. **Bug Fix: Texto longo sem espaços no Feed** - CORRIGIDO!
   - Adicionado CSS `break-all` no texto dos comentários
   - Arquivo: `/app/frontend/src/pages/FeedPage.jsx` (linha 754)
   - Previne que textos como "jjjjjjjjjjjjj..." quebrem o layout

2. **Bug Fix: Filtro de Gênero incompleto no Ranking por Cidade** - CORRIGIDO!
   - Adicionadas opções "PCD" e "Cadeirante" no dropdown de gênero
   - Arquivo: `/app/frontend/src/pages/RankingCidadePage.jsx` (linhas 260-263)

3. **Bug Fix: Ranking da Galera por Cidade não carregava dados** - CORRIGIDO!
   - Problema: Query buscava em `resultados` com campo `modalidade` inexistente
   - Solução: Alterado para usar coleção `ranking_povao` corretamente
   - Arquivo: `/app/backend/routes/ranking_routes.py` (linhas 764-800)

4. **Redis atualizado** - Versão 7.0.15 instalada e funcionando

### ✅ Completed This Session

1. **Sistema de Gerenciamento de Comentários (P0)** - IMPLEMENTADO!
   - **Limite de 200 caracteres** nos comentários (era 500)
   - **Reset semanal automático:** Todo domingo às 23:59:59 (APScheduler CronTrigger)
   - **Admin pode fixar comentários:** Badge "Fixado" com destaque visual (amarelo)
   - **Admin pode excluir comentários:** Com log de auditoria
   - **Admin pode bloquear usuários:** Usuário bloqueado recebe erro 403 ao tentar comentar
   - **Backup automático:** Comentários são salvos antes da limpeza
   - **Comentários fixados são preservados** na limpeza semanal
   - **17/17 testes passando** (`/app/test_reports/iteration_55.json`)
   
   **Endpoints criados:**
   - `POST /api/feed/admin/comentarios/{id}/fixar` - Fixar/desfixar (toggle)
   - `DELETE /api/feed/admin/comentarios/{id}` - Excluir comentário
   - `POST /api/feed/admin/usuarios/bloquear` - Bloquear usuário
   - `POST /api/feed/admin/usuarios/{id}/desbloquear` - Desbloquear
   - `GET /api/feed/admin/usuarios/bloqueados` - Listar bloqueados
   - `DELETE /api/feed/admin/comentarios/limpar-todos` - Limpar todos (manual)

2. **Renomeação "Povão" → "Galera"** - IMPLEMENTADO!
   - Todos os textos visíveis alterados em toda a plataforma
   - Lógica e cálculos mantidos (apenas nome)

3. **Ícone PWA atualizado** - IMPLEMENTADO!
   - Logo personalizado do Ranking Run em todos os tamanhos

4. **Correção botões Histórico** - IMPLEMENTADO!
   - Botões "Nova Submissão" agora navegam corretamente

### ✅ Completed Previous Session

- App Mobile (PWA) - 33/33 testes
- Ranking por Cidade/Bairro - 16/16 testes
- Sistema de Notificações Push - 15/16 testes
- Feed de Atividades Melhorado - 21/21 testes

---

## Key Endpoints - Gerenciamento de Comentários

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/feed/posts/{id}/comentarios` | POST | Criar comentário (máx 200 chars) |
| `/api/feed/admin/comentarios/{id}/fixar` | POST | Fixar/desfixar comentário |
| `/api/feed/admin/comentarios/{id}` | DELETE | Excluir comentário |
| `/api/feed/admin/usuarios/bloquear` | POST | Bloquear usuário |
| `/api/feed/admin/usuarios/{id}/desbloquear` | POST | Desbloquear usuário |
| `/api/feed/admin/usuarios/bloqueados` | GET | Listar bloqueados |
| `/api/feed/admin/comentarios/limpar-todos` | DELETE | Limpar todos (preserva fixados) |

---

## Scheduler Jobs

| Job | Schedule | Função |
|-----|----------|--------|
| `limpar_comentarios_semanal` | Domingo 23:59:59 | Limpa comentários não fixados, faz backup, limpa cache Redis |
| `check_alerts` | A cada 1 minuto | Verifica alertas do sistema |
| `collect_metrics` | A cada 5 minutos | Coleta métricas de uso |

---

## Test Reports
- `/app/test_reports/iteration_56.json` - Bug Fixes CSS e Filtro Gênero (VERIFIED)
- `/app/test_reports/iteration_55.json` - Gerenciamento Comentários (17/17 passed)
- `/app/test_reports/iteration_54.json` - PWA (33/33 passed)
- `/app/test_reports/iteration_53.json` - Ranking por Cidade (16/16 passed)

---

## Pending Tasks

### P1 - Próximas Tarefas
- [ ] **Integração Strava/Garmin** - Aguardando chaves API

### P2 - Backlog/Refatoração
- [ ] **Refatoração do RankingPage.js** - 2.100+ linhas
- [ ] **Refatoração do AdminDashboard.jsx** - 3.600+ linhas

---

## Credentials
- **Admin**: admin@runpro.com / admin
- **Preview URL**: https://assessoria-ranking.preview.emergentagent.com

---

*Última atualização: 22/Mar/2026*
