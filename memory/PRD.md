# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (20/Mar/2026)

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
- **Preview URL**: https://feed-likes-comments.preview.emergentagent.com

---

*Última atualização: 20/Mar/2026*
