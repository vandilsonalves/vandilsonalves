# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Nova Funcionalidade: Página de Regras + Painel Admin (P1)** - IMPLEMENTADO!
   - **Página Pública `/regras`:** Exibe todas as regras de pontuação em 3 tabs
   - **Painel Admin - Configurações:** Nova aba para editar valores de pontuação, prazos e textos
   - **Endpoints:** GET/PUT `/api/admin/configuracoes`, GET `/api/configuracoes/regras`
   - **13/13 testes passando** (`/app/test_reports/iteration_50.json`)

2. **CRÍTICO - Correção da Tabela de Pontuação (P0)** - CORRIGIDO!
   - **Tabela Correta:**
     - Normal: 1º=10pts, 2º=9pts, 3º=8pts, ... 10º=1pt
     - PCD/Cadeirante: 1º=10pts, 2º=9pts, 3º=8pts
     - Povão: 5-9km=5pts, 10-20km=7pts, 21km+=9pts
   - **26/26 testes passando** (`/app/test_reports/iteration_49.json`)

3. **Bug Fix: Campo Tempo Obrigatório + Validação 30 dias (P0)** - CORRIGIDO!
   - **11/11 testes passando** (`/app/test_reports/iteration_48.json`)

### ✅ Completed Previous Session

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

4. **Refatoração do server.py**
   - Reduzido de 4347 → 3419 linhas
   - 45 endpoints restantes

---

## Key Endpoints

**Exportação de Dados (Atualizado):**
- `GET /api/liga-assessorias/exportar-dados/{equipe}?formato=csv` - Planilha simples
- `GET /api/liga-assessorias/exportar-dados/{equipe}?formato=json` - Dados estruturados
- `GET /api/liga-assessorias/exportar-dados/{equipe}?formato=xlsx` - Excel formatado (NOVO!)
- `GET /api/liga-assessorias/exportar-dados/{equipe}?formato=pdf` - Relatório visual (NOVO!)
- `GET /api/liga-assessorias/exportar-graficos/{equipe}` - Dados dos gráficos

**Feed Social:**
- `POST /api/feed/posts/{post_id}/comentarios` - Adicionar comentário
- `GET /api/feed/posts/{post_id}/comentarios` - Listar comentários
- `DELETE /api/feed/comentarios/{id}` - Deletar comentário
- `POST /api/feed/posts/{post_id}/reagir` - Reações (👏🏃💪🔥❤️🎉🏆)

**Ranking Estadual:**
- `GET /api/liga-assessorias/assessoria/{nome}` - Inclui posicao_estadual correta

---

## Test Reports
- `/app/test_reports/iteration_50.json` - Sistema de Configurações e Regras (13/13 passed)
- `/app/test_reports/iteration_49.json` - Correção Tabela de Pontuação (26/26 passed)
- `/app/test_reports/iteration_48.json` - Bug Tempo Obrigatório + 30 Dias (11/11 passed)
- `/app/test_reports/iteration_47.json` - Exportação PDF/Excel (14/14 passed)

---

## Pending Tasks

### P1 - Refatoração ✅
- [x] Refatoração do server.py - **CONCLUÍDA**
  - Reduzido de 2929 para **1945 linhas** (33,6% de redução)
  - Migrados 11 endpoints de Instagram para `routes/instagram_routes.py`

- [x] Refatoração do DonoAssessoriaDashboard.jsx - **CONCLUÍDA**
  - Reduzido de 1877 para **1596 linhas** (15% de redução)
  - 5 subcomponentes criados em `/components/dono-assessoria/`:
    - DashboardStats.jsx (RankingCards, MetricasCards)
    - ExportacaoCard.jsx
    - SolicitacoesTab.jsx
    - AtletasTab.jsx
    - FotoEquipeTab.jsx

### Concluído nesta sessão
- [x] Bug Fix: Campo tempo obrigatório para TODOS (incluindo Povão)
- [x] Bug Fix: Validação de 30 dias para submissão de resultados
- [x] Redis reinstalado e funcionando
- [x] REDIS_URL adicionado ao /app/backend/.env
- [x] Exportação de dados em PDF e Excel implementada
- [x] Bug da imagem da assessoria corrigido

### P1 - Próxima Tarefa
- [ ] **Refatoração do RankingPage.js** - O componente possui mais de 2.100 linhas e precisa ser dividido em subcomponentes menores

### P2 - Backlog
- [ ] Verificação de domínio no Resend
- [ ] Continuar refatoração do server.py (ainda com ~1945 linhas)

---

## Credentials
- **Test User**: admin@runpro.com / admin123
- **Preview URL**: https://feed-likes-comments.preview.emergentagent.com

---

*Última atualização: 19/Mar/2026*
