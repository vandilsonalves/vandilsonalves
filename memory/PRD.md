# RunPro - Fitness Ranking Platform

## Problema Original
Plataforma de ranking fitness esportivo com rankings por categorias e cidades, painel "RAIO-X" avançado, integração com Strava, geração de share cards via Canvas API e painel de administração completo.

## Stack Tecnológico
- **Frontend:** React (CRA) + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI + MongoDB + WebSocket
- **Background Jobs:** Celery + Redis
- **Integrações:** Strava, Resend (e-mails), IBGE Localidades API (cidades)

## Funcionalidades Implementadas

### Concluido
- [x] Rankings (Profissional, Galera, Equipes, Por Cidade)
- [x] Compartilhamento Ranking/RaioX (Canvas 9:16 completo: Score, Metricas, Evolucao, Records, Comparativo, Previsoes IA, Badges)
- [x] Exportar PDF/Excel no Raio-X
- [x] Integracao Strava
- [x] Painel Admin completo com RBAC
- [x] Sistema de Mensagens em massa (filtros geograficos, agendamento Celery/Redis)
- [x] Splash Screen global para mensagens urgentes
- [x] Stats de leitura de mensagens (Lidas/Nao Lidas)
- [x] Dashboard de Engajamento (KPIs, graficos, tabela)
- [x] WebSocket para notificacoes em tempo real
- [x] Filtros Estado/Cidade na pagina de Atletas (Admin)
- [x] Filtros Estado/Cidade na pagina de Mensagens (Admin)
- [x] Fix distancia total 0 km no Raio-X (extrair_distancia helper)
- [x] Refatoracao massiva (AdminDashboard, RankingPage, RaioXPage)
- [x] Fix stats/categorias KeyError
- [x] data-testid nos componentes criticos
- [x] Novos campos de cadastro (telefone, tipo_corredor, terreno_preferido)
- [x] Fix performance (indices MongoDB, lazy loading Admin)
- [x] Fix ano hardcoded (2025 -> dinamico)
- [x] Fix WebSocket 403 (SECRET_KEY unificada)
- [x] Fix navigate not defined (RankingEquipes)
- [x] Dropdown de cidades via API IBGE no CadastroPage
- [x] Dropdown de cidades via API IBGE nos modais Admin (Criar/Editar Atleta) - Iteration 71

### Backlog
- [ ] Limpeza de codigo morto no AdminDashboard.jsx (P3)
- [ ] Notificacoes push por email (Resend) para mensagens urgentes (P3)
- [ ] Relatorios semanais automaticos para donos de assessoria (P3)

## Endpoints Chave
- `GET /api/admin/mensagens/engajamento` - Dashboard de engajamento
- `GET /api/admin/stats/categorias` - Stats por categoria
- `GET /api/admin/atletas?limit=1000` - Lista atletas com estado/cidade
- `GET /api/raio-x/completo` - Dados completos do Raio-X
- `WS /api/ws/notifications?token=JWT` - WebSocket tempo real
- `POST /api/register` - Registro com campos de perfil
- `POST /api/admin/atletas` - Criar atleta via admin
- IBGE: `https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios`

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456
- Atleta (resetado): beatriz_araujo_643@email.com / 123456

## Notas
- **Redis:** Pode cair no preview. Reinstalar se Celery falhar. (`sudo service redis-server restart`)
- **Rotas Splash:** Em `notificacoes_routes.py` para evitar conflito path params.
- **Distancia:** Funcao `extrair_distancia()` em raio_x_routes.py trata int, float, string (KM, K), None.
- **Ano Dinamico:** `ANO_ATUAL = datetime.now().year` em server.py.
- **Hook IBGE:** `useCidadesIBGE.js` reutilizavel para buscar cidades por UF.
