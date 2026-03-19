# Ranking Run Pró - PRD (Product Requirements Document)

## Implementation Status (19/Mar/2026)

### ✅ Completed This Session

1. **Sistema de Notificações Push (P0)** - IMPLEMENTADO!
   - **WebSocket:** Tentativa de conexão em tempo real (limitado pelo proxy Emergent - erro 403 esperado)
   - **Polling Fallback:** Atualização automática a cada 10 segundos quando WebSocket não conecta
   - **Toast Notifications:** Notificações importantes exibem toast na tela
   - **Som de Notificação:** Beep via Web Audio API (800Hz, 0.15s)
   - **Indicador Visual:** Ponto verde no sino quando WebSocket está conectado
   - **Tipos Importantes:** conquista, aprovacao, reprovacao, parabens, mensagem_assessoria, promocao, aniversario
   - **15/16 testes passando** (`/app/test_reports/iteration_52.json`)
   
   **Arquivos modificados:**
   - `/app/frontend/src/context/AuthContext.js` - WebSocket + polling + toasts
   - `/app/frontend/src/components/NotificacoesBell.jsx` - Indicador de conexão
   - `/app/backend/routes/notificacoes_routes.py` - Integração com WebSocket service

2. **Feed de Atividades Melhorado (P0)** - IMPLEMENTADO!
   - **Posts Automáticos:** Criados automaticamente quando corridas são aprovadas ou conquistas desbloqueadas
   - **Reações:** 8 tipos de reações incluindo 'parabéns' (🎊)
   - **Comentários:** Sistema completo de comentários com validação
   - **Botão Parabéns:** Reação rápida para posts de conquistas/resultados
   - **Visual Especial:** Cards diferenciados para posts de conquista (roxo) e resultado (verde)
   - **21/21 testes passando** (`/app/test_reports/iteration_51.json`)

### ✅ Completed Previous Sessions

- Sistema de Regras + Painel Admin de Configurações
- Correção da Tabela de Pontuação (bug crítico 10x)
- Bug Fix: Campo Tempo Obrigatório + Validação 30 dias
- Notificações por Email (Resend)
- Histórico de Submissões
- Gráficos de Insígnias no Dashboard

---

## Key Endpoints

**Notificações (Atualizado):**
- `GET /api/notificacoes` - Lista notificações com `notificacoes[]` e `nao_lidas`
- `POST /api/notificacoes/{id}/ler` - Marca notificação como lida
- `POST /api/notificacoes/ler-todas` - Marca todas como lidas
- `GET /api/notificacoes/{id}` - Detalhes da notificação
- `DELETE /api/notificacoes/{id}` - Exclui notificação
- `GET /api/notifications/unread-count` - Contador de não lidas
- `GET /api/notifications/ws-status` - Status do WebSocket
- `POST /api/notifications/send-test` - Envia notificação de teste
- `WebSocket /api/ws/notifications?token=...` - Conexão tempo real (proxy 403 em Emergent)

**Feed Social:**
- `GET /api/feed` - Lista posts com reações, comentários e dados do autor
- `POST /api/feed/posts` - Cria novo post de texto
- `POST /api/feed/posts/{post_id}/reagir` - Reações (👏🏃💪🔥❤️🎉🏆🎊)
- `POST /api/feed/posts/{post_id}/parabens` - Reação rápida de parabéns
- `POST /api/feed/posts/{post_id}/comentarios` - Adicionar comentário
- `GET /api/feed/posts/{post_id}/comentarios` - Listar comentários

---

## Test Reports
- `/app/test_reports/iteration_52.json` - Sistema de Notificações Push (15/16 passed)
- `/app/test_reports/iteration_51.json` - Feed de Atividades Melhorado (21/21 passed)
- `/app/test_reports/iteration_50.json` - Sistema de Configurações e Regras (13/13 passed)
- `/app/test_reports/iteration_49.json` - Correção Tabela de Pontuação (26/26 passed)

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
- [x] Sistema de Notificações Push
  - [x] WebSocket para tempo real
  - [x] Polling fallback (10s)
  - [x] Toast para notificações importantes
  - [x] Som de notificação
  - [x] Indicador de conexão no sino
- [x] Feed de Atividades Melhorado
  - [x] Posts automáticos de conquistas
  - [x] Posts automáticos de resultados aprovados
  - [x] Reação "Parabéns" (🎊)
  - [x] Visual especial para posts automáticos

---

## Credentials
- **Admin**: admin@runpro.com / admin
- **Atleta Teste**: aline.rocha@example.com (Aline Rocha, Assessoria TOP RUN)
- **Preview URL**: https://feed-likes-comments.preview.emergentagent.com

---

## Known Issues
- **WebSocket 403:** O proxy da plataforma Emergent bloqueia conexões WebSocket. O sistema usa polling como fallback (10s). Isso é esperado e documentado.
- **Redis no Supervisor:** Pode mostrar status FATAL no supervisor, mas funciona se `redis-cli ping` retornar PONG
- **Instagram Routes:** As rotas em `/app/backend/routes/instagram_routes.py` são apenas stubs

---

*Última atualização: 19/Mar/2026*
