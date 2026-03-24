# RunPro - Fitness Ranking Platform

## Problema Original
Plataforma de ranking fitness esportivo com rankings por categorias e cidades, painel "RAIO-X" avançado, integração com Strava, geração de share cards via Canvas API e painel de administração completo.

## Stack Tecnológico
- **Frontend:** React (CRA) + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI + MongoDB
- **Background Jobs:** Celery + Redis
- **Integrações:** Strava, Resend (e-mails)

## Arquitetura de Componentes (Pós-refatoração)

### AdminDashboard.jsx (~1657 linhas)
Shell principal do painel admin com sidebar. Componentes extraídos:
- `DashboardGeral` - Visão geral / estatísticas
- `DashboardAtletas` - Gestão de atletas
- `DashboardAssessorias` - Liga de assessorias
- `DashboardCorridas` - Gestão de corridas
- `DashboardResultados` - Aprovação de resultados
- `DashboardRBAC` - Controle de acesso
- `DashboardSubmeter` - Submeter resultados **[NOVO]**
- `DashboardAutorizacoes` - Gerenciar autorizações **[NOVO]**
- `DashboardRegulamento` - Editor de regulamento **[NOVO]**
- `DashboardAniversariantes` - Calendário de aniversários **[NOVO]**
- `DashboardInstagram` - Instagram Analytics **[NOVO]**
- `DashboardMensagens` - Mensagens em massa + agendamento

### RankingPage.js (~232 linhas)
Shell com tab switcher. Componentes extraídos:
- `RankingProfissional` - Ranking por colocação **[NOVO]**
- `RankingGalera` - Ranking por distância **[NOVO]**
- `RankingEquipes` - Liga Nacional de Assessorias **[NOVO]**

### RaioXPage.jsx (~1813 linhas)
Canvas share card extraído para:
- `/utils/canvasShareGenerator.js` **[NOVO]**

## Funcionalidades Implementadas

### Concluído
- [x] Filtro Gênero/Modalidade no Ranking por Cidade
- [x] Compartilhamento do Ranking da Cidade (Canvas 9:16)
- [x] Bug fix: Zero Overlap Profissional vs Galera
- [x] Bug fix: Strava redirect_uri
- [x] Bug fix: Sincronização pontos/corridas
- [x] Renomeação "Povão" → "Galera" na UI
- [x] Endpoint admin para recalcular rankings
- [x] Migração datas 2025→2026 + ANO_ATUAL dinâmico
- [x] Aba Mensagens no Admin (filtros + notificações)
- [x] Agendamento de mensagens (Celery + Redis)
- [x] **Refatoração AdminDashboard.jsx** (3876→1657 linhas, -57%)
- [x] **Refatoração RankingPage.js** (2267→232 linhas, -90%)
- [x] **Refatoração RaioXPage.jsx** (2325→1813 linhas, -22%)
- [x] **Filtros "Por Estado" e "Por Cidade" no Admin Mensagens**

### Backlog
- [ ] Limpeza de estado morto residual no AdminDashboard.jsx
- [ ] Adicionar mais data-testid onde necessário

## Endpoints Chave
- `POST /api/admin/mensagens/enviar` - Envio/agendamento de mensagens
- `POST /api/admin/recalcular-rankings` - Recálculo de rankings
- `GET /api/ranking/por-cidade/{estado}/{cidade}` - Ranking por cidade

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456

## Notas Importantes
- **Nomenclatura:** "Povão" substituído por "Galera" na UI. Backend/DB mantém `ranking_povao`.
- **Datas:** Sistema usa `ANO_ATUAL` dinâmico. NUNCA hardcode ano.
- **Redis:** Pode cair. Se Celery falhar, restaurar Redis primeiro.
