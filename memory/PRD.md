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
- [x] Fix distancia total 0 km no Raio-X
- [x] Refatoracao massiva (AdminDashboard, RankingPage, RaioXPage)
- [x] Novos campos de cadastro (telefone, tipo_corredor, terreno_preferido)
- [x] Fix performance (indices MongoDB, lazy loading Admin)
- [x] Fix ano hardcoded (2025 -> dinamico)
- [x] Fix WebSocket 403, navigate not defined, KeyError categoria
- [x] Dropdown de cidades via API IBGE (CadastroPage + Admin modais) - Iteration 71
- [x] CidadeCombobox com busca por texto em TODOS os dropdowns de cidade do app - Iteration 72
  - Componente reutilizavel: `/app/frontend/src/components/CidadeCombobox.jsx`
  - Usa Popover + Command (cmdk) para filtrar cidades enquanto digita
  - Substituido em 11 locais: CadastroPage (2x), AdminDashboard (2x), DashboardCorridas (2x), DashboardAtletas (1x), DashboardAssessorias (1x), SubmeterResultadoPage (1x), RankingCorridasPage (1x), CriarAssessoria (1x)

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

## Notas
- **Redis:** Pode cair no preview. Reinstalar se Celery falhar.
- **Ano Dinamico:** `ANO_ATUAL = datetime.now().year` em server.py.
- **CidadeCombobox:** Componente reutilizavel em `/app/frontend/src/components/CidadeCombobox.jsx`. Props: cidades, value, onValueChange, loading, disabled, placeholder, allOption, triggerClassName, data-testid.
