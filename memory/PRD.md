# RunPro - Fitness Ranking Platform

## Problema Original
Plataforma de ranking fitness esportivo com rankings por categorias e cidades, painel "RAIO-X" avancado, integracao com Strava, geracao de share cards via Canvas API e painel de administracao completo.

## Stack Tecnologico
- **Frontend:** React (CRA) + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI + MongoDB + WebSocket
- **Background Jobs:** Celery + Redis
- **Integracoes:** Strava, Resend, IBGE Localidades API

## Funcionalidades Implementadas

### Concluido
- [x] Rankings (Profissional, Galera, Equipes, Por Cidade)
- [x] Compartilhamento Ranking/RaioX (Canvas 9:16)
- [x] Integracao Strava
- [x] Painel Admin completo com RBAC e lazy loading
- [x] Sistema de Mensagens em massa (filtros, agendamento, splash)
- [x] CidadeCombobox com busca IBGE em todos dropdowns
- [x] Upload de fotos no Feed + Duplo-toque para curtir
- [x] Stories no Feed (fotos temporarias 24h, sem limite, 10s por story)
- [x] Compressao automatica de imagens no upload (max 1200x1200, JPEG 82%)
- [x] **Sistema de Mensagens em Autorizacoes (NOVO - Iteration 77)**
  - Envio segmentado por status: Em Teste, Autorizados, Expirados
  - Filtros: Estado, Cidade (IBGE), Genero (6 categorias)
  - Formulario: Titulo, Mensagem, Link, Anexar Arquivo/Imagem
  - Envio Splash (popup bloqueante para atletas)
  - Agendamento de mensagens (datetime-local)
  - Historico de mensagens enviadas
  - Tabela de atletas com Autorizar/Revogar
  - Stats cards: Em Teste (278), Autorizados (27), Expirados (144), Total (449)

### Backlog
- [ ] Sistema de pagamentos (Stripe/Pix) para Premium/Membro Oficial (P1 - proximo)
- [ ] Limpeza de codigo morto no AdminDashboard.jsx (P3)
- [ ] Notificacoes push por email (Resend) (P3)
- [ ] Relatorios semanais para assessorias (P3)

## Endpoints - Autorizacoes
- `GET /api/admin/autorizacoes/atletas-completo` - Lista atletas com status_periodo
- `POST /api/admin/autorizacoes/mensagens/enviar` - Envia mensagem filtrada
- `POST /api/admin/autorizacoes/mensagens/upload` - Upload de arquivo/imagem
- `GET /api/admin/autorizacoes/mensagens/arquivo/{filename}` - Serve arquivo
- `GET /api/admin/autorizacoes/mensagens/historico` - Historico de mensagens

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## DB Collections
- `autorizacoes`: atleta_id, tipo, status, data_criacao, data_expiracao
- `mensagens_admin`: id, titulo, mensagem, status_filtro, origem("autorizacoes"), splash, total_enviados
- `notificacoes`: usuario_id, mensagem_admin_id, lida, splash

## Notas
- **Status Periodo**: em_teste (< 30 dias sem autorizacao), autorizado (autorizacao ativa nao expirada), expirado (> 30 dias ou autorizacao expirada)
- **Datetime**: Sempre usar timezone.utc e tratar tanto naive quanto aware datetimes do MongoDB
- **Redis:** Instavel no preview. Restart manual se Celery falhar.
