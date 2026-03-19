# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Exportação de Dados em PDF e Excel (P1)** - NOVO!
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
- `/app/test_reports/iteration_47.json` - Exportação PDF/Excel (14/14 passed)
- `/app/test_reports/iteration_46.json` - Bug fixes (13/13 passed)
- `/app/test_reports/iteration_45.json` - Exportação CSV/JSON (23/23 passed)

---

## Pending Tasks

### P1 - Refatoração
- [x] Refatoração do server.py - Reduzido de 3422 para 2958 linhas (464 linhas removidas)
  - Removidos endpoints duplicados de ranking, regulamento, corridas-eventos
  - Removido endpoint duplicado promover-dono-assessoria

### P2 - Backlog
- [ ] Continuar refatoração do server.py (2958 linhas, ~30 endpoints restantes)
- [ ] Configuração de REDIS_URL para produção
- [ ] Verificação de domínio no Resend
- [ ] Refatoração de componentes grandes do frontend (DonoAssessoriaDashboard.jsx)

---

## Credentials
- **Test User**: admin@runpro.com / admin123
- **Preview URL**: https://assess-photo-fix.preview.emergentagent.com

---

*Última atualização: 19/Mar/2026*
