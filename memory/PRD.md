# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Bug Fix: Campo Tempo Obrigatório para Povão (P0)** - CORRIGIDO!
   - Problema: Atletas da modalidade "Povão" podiam submeter resultados com tempo zerado
   - Solução: Campo tempo agora é obrigatório para TODOS (frontend + backend)
   - Arquivos: `SubmeterResultadoPage.js` (linha 460-467), `resultados_routes.py` (linhas 58-73)
   - **11/11 testes passando** (`/app/test_reports/iteration_48.json`)

2. **Bug Fix: Validação de 30 Dias (P0)** - CORRIGIDO!
   - Problema: Atletas conseguiam submeter corridas com mais de 30 dias de antecedência
   - Solução: Validação no frontend (linhas 120-138) e backend (linhas 35-56)
   - **Testado e verificado com datas de 31, 45 dias e datas futuras**

3. **Exportação de Dados em PDF e Excel (P1)** - Sessão Anterior
   - Implementado: Exportação em PDF (relatório visual formatado)
   - Implementado: Exportação em Excel (XLSX com 3 abas: Resumo, Atletas, Corridas)
   - Bibliotecas: reportlab (PDF), xlsxwriter (Excel)
   - Frontend: 5 botões de exportação (CSV, JSON, Excel, PDF, Gráficos)
   - **14/14 testes passando** (`/app/test_reports/iteration_47.json`)

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
- `/app/test_reports/iteration_48.json` - Bug Tempo Obrigatório + 30 Dias (11/11 passed)
- `/app/test_reports/iteration_47.json` - Exportação PDF/Excel (14/14 passed)
- `/app/test_reports/iteration_46.json` - Bug fixes (13/13 passed)
- `/app/test_reports/iteration_45.json` - Exportação CSV/JSON (23/23 passed)

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
- **Preview URL**: https://time-required-fix.preview.emergentagent.com

---

*Última atualização: 19/Mar/2026*
