# RunPro - Fitness Ranking Platform

## Problema Original
Plataforma de ranking fitness esportivo com rankings por categorias e cidades, painel "RAIO-X" avancado, integracao com Strava, geracao de share cards via Canvas API e painel de administracao completo.

## Stack Tecnologico
- **Frontend:** React (CRA) + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI + MongoDB + WebSocket
- **Background Jobs:** Celery + Redis
- **Integracoes:** Strava, Resend (e-mails), IBGE Localidades API (cidades)

## Funcionalidades Implementadas

### Concluido
- [x] Rankings (Profissional, Galera, Equipes, Por Cidade)
- [x] Compartilhamento Ranking/RaioX (Canvas 9:16 completo)
- [x] Integracao Strava
- [x] Painel Admin completo com RBAC e lazy loading
- [x] Sistema de Mensagens em massa (filtros geograficos, agendamento, splash screen)
- [x] Dashboard de Engajamento
- [x] WebSocket para notificacoes em tempo real
- [x] CidadeCombobox com busca por texto em TODOS dropdowns de cidade (Iteration 72)
- [x] Upload de FOTOS no Feed Social (Iteration 73)
  - 1 foto por vez, limite 2/dia, texto opcional, preview, badge "Foto"
- [x] Duplo-toque para curtir fotos estilo Instagram (Iteration 74-75)
  - Animacao de coracao grande com fade-out
- [x] Stories no Feed Social (Iteration 76) - NOVO
  - Barra de stories no topo com circulos de avatar
  - Anel colorido gradiente = story nao visto, cinza = visto
  - Botao + para adicionar story (1 por dia)
  - Viewer fullscreen: barra de progresso, texto overlay, reacoes rapidas
  - Ordenacao: nao vistos primeiro
  - Auto-expira em 24h

### Backlog
- [ ] Limpeza de codigo morto no AdminDashboard.jsx (P3)
- [ ] Notificacoes push por email (Resend) (P3)
- [ ] Relatorios semanais para assessorias (P3)

## Endpoints Chave - Stories
- `POST /api/feed/stories` - Cria story (Form: foto + texto)
- `GET /api/feed/stories` - Lista stories ativos (24h) agrupados por autor
- `POST /api/feed/stories/{id}/visualizar` - Marca como visto
- `POST /api/feed/stories/{id}/reagir` - Reacao rapida com emoji
- `GET /api/feed/stories/restantes` - Stories restantes no dia (limite: 1)

## Endpoints Chave - Feed
- `POST /api/feed/posts/com-foto` - Upload de foto (Form: foto + texto)
- `GET /api/feed/fotos-restantes` - Fotos restantes no dia (limite: 2)
- `GET /api/feed` - Feed social paginado
- `POST /api/feed/posts/{id}/reagir` - Reagir a um post

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## DB Collections - Stories
- `stories`: id, autor_id, autor_nome, imagem_url, texto, data_criacao, visualizacoes[], reacoes[]
- Imagens salvas em /app/uploads/stories/

## Notas
- **Redis:** Instavel no preview. Restart manual se Celery falhar.
- **Upload Fotos/Stories:** Form() obrigatorio para campos texto com UploadFile.
- **Auth Race Condition:** FeedPage checa authLoading antes de user null + timeout de seguranca 10s.
- **Stories Auto-Expire:** Filtro por data_criacao >= 24h no query, sem cronjob.
