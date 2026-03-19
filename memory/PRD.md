# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Bug Fix: Ranking Estadual (P0)**
   - Problema: Mostrava ".0" ou "." em vez da posição real
   - Causa: Estado vinha dos atletas, não do ranking
   - Solução: Prioridade de estado: ranking > dono > atletas
   - **Testado: Assessoria CAFAV = ES, posição estadual 1**

2. **Remoção do Sistema de Rivais**
   - Removido: `/app/frontend/src/pages/RivaisPage.jsx`
   - Removido: `/app/backend/routes/rivais_routes.py`
   - Removido: Rota e ícone do menu

3. **Feed Social - Comentários + Sem Upload**
   - Adicionado: Endpoints de comentários (POST/GET/DELETE)
   - Adicionado: UI de comentários no frontend
   - Removido: Endpoint de upload de imagem
   - Removido: Botão de foto na UI
   - **13/13 testes passando**

4. **Refatoração do server.py (Sessão Anterior)**
   - Reduzido de 4347 → 3419 linhas
   - 45 endpoints restantes

5. **Exportação de Dados (Sessão Anterior)**
   - CSV, JSON e Gráficos funcionando

---

## Key Endpoints

**Feed Social (Atualizado):**
- `POST /api/feed/posts/{post_id}/comentarios` - Adicionar comentário
- `GET /api/feed/posts/{post_id}/comentarios` - Listar comentários
- `DELETE /api/feed/comentarios/{id}` - Deletar comentário
- `POST /api/feed/posts/{post_id}/reagir` - Reações (👏🏃💪🔥❤️🎉🏆)
- ~~`POST /api/feed/posts/{post_id}/imagem`~~ - REMOVIDO

**Ranking Estadual (Corrigido):**
- `GET /api/liga-assessorias/assessoria/{nome}` - Inclui posicao_estadual correta

---

## Test Reports
- `/app/test_reports/iteration_46.json` - Bug fixes (13/13 passed)
- `/app/test_reports/iteration_45.json` - Exportação (23/23 passed)

---

## Pending Tasks

### P2 - Backlog
- [ ] Continuar refatoração do server.py (3419 linhas)
- [ ] Configuração de REDIS_URL para produção
- [ ] Verificação de domínio no Resend

---

## Credentials
- **Test User**: admin@runpro.com / admin123
- **Preview URL**: https://community-feed-28.preview.emergentagent.com

---

*Última atualização: 19/Mar/2026*
