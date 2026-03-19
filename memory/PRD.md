# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Feed de Atividades Melhorado (P0)** - IMPLEMENTADO!
   - **Posts Automáticos:** Criados automaticamente quando corridas são aprovadas ou conquistas desbloqueadas
   - **Reações:** 8 tipos de reações incluindo 'parabéns' (🎊)
   - **Comentários:** Sistema completo de comentários com validação
   - **Botão Parabéns:** Reação rápida para posts de conquistas/resultados
   - **Visual Especial:** Cards diferenciados para posts de conquista (roxo) e resultado (verde)
   - **21/21 testes passando** (`/app/test_reports/iteration_51.json`)
   
   **Arquivos modificados:**
   - `/app/frontend/src/pages/FeedPage.jsx` - UI melhorada com componentes PostConteudoEspecial e BotaoParabens
   - `/app/backend/routes/admin_routes.py` - Integração com criar_post_corrida_aprovada()
   - `/app/backend/routes/conquistas_routes.py` - Integração com criar_post_conquista()

### ✅ Completed Previous Session

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

4. **Notificações por Email** - IMPLEMENTADO!
   - Atletas recebem e-mails quando seus resultados são aprovados ou rejeitados

5. **Histórico de Submissões** - IMPLEMENTADO!
   - Nova página `/historico` onde atletas podem ver o status de todas as suas corridas enviadas

---

## Key Endpoints

**Feed Social (Atualizado):**
- `GET /api/feed` - Lista posts com reações, comentários e dados do autor
- `POST /api/feed/posts` - Cria novo post de texto
- `POST /api/feed/posts/{post_id}/reagir` - Reações (👏🏃💪🔥❤️🎉🏆🎊)
- `POST /api/feed/posts/{post_id}/parabens` - Reação rápida de parabéns
- `POST /api/feed/posts/{post_id}/comentarios` - Adicionar comentário
- `GET /api/feed/posts/{post_id}/comentarios` - Listar comentários
- `GET /api/feed/reacoes-disponiveis` - Lista 8 tipos de reações

**Exportação de Dados:**
- `GET /api/liga-assessorias/exportar-dados/{equipe}?formato=csv` - Planilha simples
- `GET /api/liga-assessorias/exportar-dados/{equipe}?formato=xlsx` - Excel formatado
- `GET /api/liga-assessorias/exportar-dados/{equipe}?formato=pdf` - Relatório visual

---

## Test Reports
- `/app/test_reports/iteration_51.json` - Feed de Atividades Melhorado (21/21 passed)
- `/app/test_reports/iteration_50.json` - Sistema de Configurações e Regras (13/13 passed)
- `/app/test_reports/iteration_49.json` - Correção Tabela de Pontuação (26/26 passed)
- `/app/test_reports/iteration_48.json` - Bug Tempo Obrigatório + 30 Dias (11/11 passed)

---

## Pending Tasks

### P1 - Próximas Tarefas (Priorizadas pelo Usuário)
- [ ] **Ranking por Cidade/Bairro** - Nova visão de ranking filtrada por localização para modalidades "Profissional/Amador" e "Povão"
- [ ] **Integração Strava/Garmin** - Importação automática de corridas (usar integration_playbook_expert_v2)
- [ ] **App Mobile (PWA)** - Configurar aplicação como Progressive Web App

### P2 - Backlog/Refatoração
- [ ] **Refatoração do RankingPage.js** - 2.100+ linhas, precisa ser dividido em componentes menores
- [ ] **Refatoração do AdminDashboard.jsx** - 3.600+ linhas
- [ ] Verificação de domínio no Resend

### Concluído nesta sessão
- [x] Feed de Atividades Melhorado
  - [x] Posts automáticos de conquistas
  - [x] Posts automáticos de resultados aprovados
  - [x] Reação "Parabéns" (🎊)
  - [x] Visual especial para posts automáticos
  - [x] Botão de reação rápida "Parabéns"

---

## Credentials
- **Admin**: admin@runpro.com / admin
- **Atleta Teste**: aline.rocha@example.com (Aline Rocha, Assessoria TOP RUN)
- **Preview URL**: https://feed-likes-comments.preview.emergentagent.com

---

## Known Issues
- **Redis no Supervisor:** Pode mostrar status FATAL no supervisor, mas funciona se `redis-cli ping` retornar PONG (gerenciado pelo sistema operacional)
- **Instagram Routes:** As rotas em `/app/backend/routes/instagram_routes.py` são apenas stubs (esqueletos de código)

---

*Última atualização: 19/Mar/2026*
