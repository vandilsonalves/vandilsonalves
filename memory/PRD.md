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
- [x] Exportar PDF/Excel no Raio-X
- [x] Integracao Strava
- [x] Painel Admin completo com RBAC
- [x] Sistema de Mensagens em massa (filtros geograficos, agendamento Celery/Redis)
- [x] Splash Screen global para mensagens urgentes
- [x] Stats de leitura de mensagens (Lidas/Nao Lidas)
- [x] Dashboard de Engajamento (KPIs, graficos, tabela)
- [x] WebSocket para notificacoes em tempo real
- [x] Filtros Estado/Cidade em Atletas, Mensagens, Corridas, Assessorias (Admin)
- [x] Refatoracao massiva (AdminDashboard, RankingPage, RaioXPage)
- [x] Novos campos de cadastro (telefone, tipo_corredor, terreno_preferido)
- [x] Fix performance (indices MongoDB, lazy loading Admin)
- [x] CidadeCombobox com busca por texto em TODOS os dropdowns de cidade - Iteration 72
- [x] Upload de FOTOS no Feed Social - Iteration 73
  - Upload 1 foto por vez (max 5MB, jpg/png/webp/heic/heif)
  - Limite de 2 fotos por dia (24h) por atleta
  - Foto com texto opcional (legenda)
  - Preview antes de publicar, botao remover, contador restantes
  - Badge "Foto" nos posts com imagem
- [x] Duplo-toque para curtir fotos (estilo Instagram) - Iteration 74-75
  - 2 cliques rapidos (<350ms) na imagem dispara reacao 'coracao'
  - Animacao de coracao grande com fade-out sobre a foto
  - Clique unico nao dispara reacao
- [x] Fix race condition authLoading no FeedPage - Iteration 75

### Backlog
- [ ] Limpeza de codigo morto no AdminDashboard.jsx (P3)
- [ ] Notificacoes push por email (Resend) para mensagens urgentes (P3)
- [ ] Relatorios semanais automaticos para donos de assessoria (P3)

## Endpoints Chave
- `POST /api/feed/posts/com-foto` - Upload de foto (Form: foto + texto)
- `GET /api/feed/fotos-restantes` - Fotos restantes no dia
- `GET /api/feed` - Feed social paginado
- `POST /api/feed/posts/{id}/reagir` - Reagir a um post (coracao, aplausos, etc)
- `POST /api/feed/posts/{id}/comentarios` - Comentar em um post
- `GET /api/admin/mensagens/engajamento` - Dashboard de engajamento
- `GET /api/raio-x/completo` - Dados completos do Raio-X
- IBGE: `https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios`

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Notas
- **Redis:** Instavel no preview. Reinstalar se Celery falhar.
- **Ano Dinamico:** `ANO_ATUAL = datetime.now().year` em server.py.
- **Upload Fotos:** Salvas em /app/uploads/feed/, servidas via /api/uploads/feed/{nome}. Limite 2/dia.
- **Form vs Query:** Ao usar UploadFile + campos texto, usar Form("") nao str = "".
- **Auth Race Condition:** FeedPage precisa checar authLoading antes de user null.
