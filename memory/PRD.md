# Ranking Run Pró - PRD (Product Requirements Document)

## Original Problem Statement
O usuário solicitou a reestruturação do painel de administração e implementação de um sistema completo de gerenciamento de ranking para corridas, incluindo:
1. Sistema RBAC (Role Based Access Control)
2. Sistema de Monitoramento de Saúde do Backend
3. Cache Inteligente com Redis
4. Filas de Tarefas com Celery
5. Notificações em Tempo Real via WebSocket
6. Refatoração do backend monolítico (server.py) em módulos

## User Personas
- **Super Admin**: Acesso total ao sistema, gerencia outros admins
- **Colaborador Admin**: Acesso limitado baseado em permissões RBAC
- **Atleta Profissional/Amador**: Participa do ranking por colocação
- **Atleta Povão (Pace Livre)**: Participa do ranking por distância acumulada
- **Dono de Assessoria**: Visualiza relatórios da sua equipe

## Core Requirements

### 1. Sistema de Ranking (DONE)
- Ranking Profissional/Amador por categoria, gênero, faixa etária
- Ranking Povão (Pace Livre) por distância acumulada
- Rankings Semanal e Mensal
- Destaques do mês
- Exportação CSV/Excel

### 2. Sistema RBAC (DONE)
- Múltiplos níveis de administradores
- Permissões granulares por funcionalidade
- Logs de auditoria de todas as ações
- Conta de emergência para recuperação
- 2FA opcional para admins

### 3. Sistema de Monitoramento (DONE)
- Métricas em tempo real (CPU, memória, requisições)
- Dashboard visual no frontend
- Alertas automáticos por email para anomalias
- Histórico de métricas para análise

### 4. Cache com Redis (DONE)
- Cache inteligente para endpoints de alto tráfego
- Invalidação automática por TTL
- Cache de rankings para melhor performance

### 5. Filas com Celery (DONE)
- Processamento assíncrono de tarefas pesadas
- Recálculo de rankings em background
- Envio de emails em massa

### 6. WebSocket Notifications (DONE)
- Notificações em tempo real para usuários conectados
- Alertas para admins sobre eventos do sistema
- Persistência de notificações no banco

---

## Implementation Status

### Completed (March 2026)
- [x] Sistema RBAC completo
- [x] Sistema de Monitoramento de Saúde
- [x] Cache com Redis integrado
- [x] Celery para tarefas assíncronas
- [x] WebSocket para notificações em tempo real
- [x] Bug fix: Geolocalização não bloqueante no login (~25s -> ~1.3s)
- [x] Instalação do Redis no ambiente
- [x] **Refatoração MAJOR do server.py** - Reduzido de 6263 para 4498 linhas (~28% reduction)
- [x] **Redis no Supervisor** - Auto-start configurado
- [x] **Celery no Supervisor** - Auto-start configurado com 2 workers
- [x] **Dashboard Estratégico com 31 Gráficos** - Implementação completa para Super Admin
- [x] **Geração de Dados de Teste** - 390 atletas (270 Profissional/Amador + 120 Povão)
- [x] **Bug Fix do Ranking (11/Mar/2026)** - Rankings funcionando corretamente para todas as categorias
- [x] **Sistema de Gamificação com Badges (11/Mar/2026)** - 13 badges visuais com compartilhamento social
- [x] **Bloqueio de Colocações Inválidas (11/Mar/2026)** - Validação por modalidade implementada

### Sistema de Validação de Colocações (ATUALIZADO - 16/Mar/2026)
- **Profissional/Amador Normal**: Aceita apenas 1º a 10º lugar (10-1 pontos)
- **PCD**: Aceita apenas 1º a 3º lugar (10-8 pontos)
- **Cadeirante**: Aceita apenas 1º a 3º lugar (10-8 pontos)
- **Povão - Pace Livre**: Campo colocação bloqueado (=0), pontua APENAS por distância
  - 5-9km = 5 pontos
  - 10-20km = 10 pontos  
  - 21km+ = distância em pontos (ex: 42km = 42pts, 100km = 100pts)
- **Distância Customizada**: Campo adicional aparece quando "Outra distância" é selecionado
- **Correção de dados existentes**: 941 registros corrigidos (482 Povão, 162 Normal, 187 PCD, 110 Cadeirante)
- **Rankings recalculados**: 390 atletas com pontuação corrigida

### Sistema de Badges (NOVO - 11/Mar/2026)
- **13 tipos de badges** em 3 categorias (performance, participação, especial)
- **Badges de Performance**: Atleta Elite (100+ pts), Corredor de Maratona (42km), Top 10 do Mês, Pódio (top 3), Rei da Velocidade
- **Badges de Participação**: Iniciante (1 corrida), Veterano (10+ corridas), Maratonista (20+), Lenda (50+), Consistente (6 meses)
- **Badges Especiais**: Embaixador (5+ indicações), Influencer, Estrela da Assessoria
- **Design visual elaborado** com gradientes e ícones coloridos
- **Compartilhamento social** via WhatsApp, Twitter, Copiar Texto
- **Badges mini** na tabela de ranking ao lado do nome do atleta
- **Seção completa** na página de detalhes do atleta

### Sistema de Indicação de Amigos (NOVO - 14/Mar/2026)
- **Código de Indicação Único**: Formato REF-[INICIAIS][HASH] (ex: REF-CS123ABC)
- **Campo no Cadastro**: Campo "Código de Indicação de Amigo(a)" opcional na página de cadastro
- **Captura via URL**: Código preenchido automaticamente via `?ref=CODIGO` na URL
- **Validação em Tempo Real**: Verifica código enquanto digita, mostra nome do indicador se válido
- **Registro Automático**: Indicação registrada automaticamente ao completar cadastro com código válido
- **Contador de Indicações**: Indicador acumula indicações para desbloquear badge "Embaixador" (5+)
- **Notificação Push (15/Mar/2026)**: Quando alguém usa o código, o indicador recebe notificação "🎉 [Nome] se cadastrou usando seu código de indicação!"
- **Quadro no Perfil (15/Mar/2026)**: Componente MinhasIndicacoes mostra estatísticas e lista de indicados
  - Dono vê: código, botão copiar, botão WhatsApp, lista de indicados
  - Visitante vê: apenas dados públicos (contagem e lista)
- **Endpoints**:
  - GET /api/indicacao/verificar-codigo/{codigo} - Valida código
  - GET /api/indicacao/meu-codigo - Retorna código do usuário logado
  - GET /api/indicacao/minhas-indicacoes - Lista pessoas indicadas
  - GET /api/indicacao/ranking - Ranking de indicadores
  - GET /api/indicacao/atleta/{id}/publico - Dados públicos de indicação
- **Arquivos**: `indicacao_routes.py`, `MinhasIndicacoes.jsx`, `IndicarAmigos.jsx`, campo em `CadastroPage.js`

### Módulos Refatorados (18 módulos criados)
- `auth_routes.py` - Autenticação (com sistema de indicação integrado)
- `notificacoes_routes.py` - Sistema de notificações
- `conquistas_routes.py` - Conquistas/badges
- `atletas_routes.py` - Perfil do atleta
- `resultados_routes.py` - Resultados de corridas
- `ranking_routes.py` - Rankings (com cache Redis)
- `rbac.py` - Controle de acesso
- `admin_routes.py` - Gestão administrativa
- `assessorias_routes.py` - Liga de assessorias
- `corridas_eventos_routes.py` - Eventos e corridas
- `aniversariantes_routes.py` - Sistema de aniversariantes
- `instagram_routes.py` - Analytics do Instagram
- `monitoring_routes.py` - Monitoramento de saúde
- `celery_routes.py` - Tarefas assíncronas
- `websocket_routes.py` - Notificações em tempo real
- `badges_routes.py` - Sistema de gamificação com badges
- `indicacao_routes.py` - Sistema de indicação de amigos (NOVO)

### Backlog (P2-P3)
- [ ] **Verificar domínio no Resend** - Atualmente usando `onboarding@resend.dev` (domínio de teste)
  - Só envia para o email do dono da conta Resend
  - Para produção: verificar domínio próprio em https://resend.com/domains
- [ ] Testes automatizados completos
- [ ] Documentação Swagger da API

---

## 🚀 ROADMAP DE ENGAJAMENTO E RETENÇÃO (Aprovado pelo usuário)

### Fase 1: Notificações e Gamificação Avançada
- [ ] **Notificações Push para Badges** - In-app + Toast quando conquista + Botão compartilhar
- [ ] **Sistema de Metas Pessoais** - Atleta define metas, barra de progresso, celebração
- [ ] **Sistema de Streaks** - Sequências de semanas com corridas, badges especiais

### Fase 2: Social e Competição
- [ ] **Comparação com Rivais** - Adicionar atletas como rivais, notificação quando ultrapassar
- [ ] **Feed Social/Timeline** - Ver conquistas da assessoria, curtir/comentar
- [ ] **Desafios Mensais/Semanais** - Desafios coletivos e individuais com ranking especial

### Fase 3: Evolução e Níveis
- [ ] **Histórico de Evolução** - Gráficos mensais/anuais, comparativo com período anterior
- [ ] **Sistema de Níveis (XP)** - Iniciante → Amador → Profissional → Elite → Lenda
- [ ] **Lembretes Inteligentes** - Inatividade, eventos próximos, calendário

### Fase 4: Diferencial Competitivo
- [ ] **Previsão de Ranking com IA** - Simulador de pontuação, projeções
- [ ] **Certificados Digitais** - PDF personalizável, QR Code de validação

---

## Technical Architecture

### Backend Stack
- FastAPI (Python 3.11)
- MongoDB (Motor async driver)
- Redis (Cache + Celery broker)
- Celery (Task queue)
- WebSockets (Notificações tempo real)

### Frontend Stack  
- React 18
- Tailwind CSS + shadcn/ui
- Context API para estado global
- Custom hooks (useWebSocketNotifications)

### File Structure
```
/app/backend/
├── server.py           # Reduzido de 6263 para 4498 linhas
├── routes/             # 16 módulos de rotas
│   ├── auth_routes.py
│   ├── ranking_routes.py
│   ├── admin_routes.py
│   ├── assessorias_routes.py
│   ├── aniversariantes_routes.py
│   ├── instagram_routes.py
│   ├── monitoring_routes.py
│   ├── websocket_routes.py
│   └── ... (8 outros)
├── services/
│   ├── cache_service.py
│   ├── monitoring_service.py
│   ├── websocket_service.py
│   └── rbac_service.py
└── celery_worker.py

/app/frontend/src/
├── pages/admin/
│   ├── AdminDashboard.jsx
│   └── dashboards/
│       ├── DashboardMonitoring.jsx
│       └── DashboardRBAC.jsx
└── hooks/
    └── useWebSocketNotifications.js
```

---

## Key API Endpoints

### Ranking (via ranking_routes.py)
- GET /api/ranking/povao
- GET /api/ranking/semanal
- GET /api/ranking/mensal
- GET /api/ranking/destaque-mes

### Admin (via admin_routes.py)
- GET /api/admin/pendentes
- POST /api/admin/aprovar/{id}
- GET /api/admin/stats
- GET /api/admin/atletas

### Liga Assessorias (via assessorias_routes.py)
- GET /api/liga-assessorias/ranking
- GET /api/liga-assessorias/stats

### Monitoring
- GET /api/health
- GET /api/monitoring/dashboard

---

## Test Credentials
- **Super Admin**: admin@rankingrun.com / admin123
- **Atleta Indicador**: carlos.silva@teste.com / senha123 (código: REF-CSAC0455)
- **Atleta Masculino**: rafael_souza_1@email.com / senha123
- **Atleta Feminina**: raquel_pereira_21@email.com / senha123

---

## Refactoring Summary (Session March 11, 2026)

### Lines Removed from server.py: ~1765 lines
- Endpoints de admin (pendentes, stats, atletas) → admin_routes.py
- Endpoints de ranking (povao, semanal, mensal) → ranking_routes.py
- Endpoints de assessorias/liga → assessorias_routes.py
- Endpoints de aniversariantes → aniversariantes_routes.py
- Endpoints de instagram (analises) → instagram_routes.py

### Bug Fixes Applied
- Login RBAC lento (25s → 1.3s) - geolocalização em background
- Redefinições de funções duplicadas corrigidas
- Imports de funções entre módulos corrigidos



### Formulário de Submissão de Resultados (NOVO - 16/Mar/2026)
- **Campo de Distância Customizada**: 
  - Dropdown de distância inclui opção "Outra distância"
  - Quando selecionado, exibe campo numérico (1-500km, step 0.1)
  - Validação: apenas números, máximo 500km
  - Pontuação calculada automaticamente conforme regras do Povão

- **Dropdowns de Localização (Estado/Cidade)**:
  - Dropdown de Estado com todos os 27 estados brasileiros
  - Dropdown de Cidade carrega automaticamente via API do IBGE
  - Cidades são populadas após seleção do estado
  - Loading state exibido durante carregamento das cidades
  - Fallback para input de texto caso API falhe

- **Arquivos modificados**:
  - `/app/frontend/src/pages/SubmeterResultadoPage.js`
  - `/app/backend/routes/admin_routes.py` (função calcular_pontos_povao)
  - `/app/frontend/src/pages/CadastroPage.js` (correção de valores de pontuação)

### Seção de Destaques do Ranking do Povão (NOVO - 17/Mar/2026)
- **Frontend implementado** em `/app/frontend/src/pages/RankingPage.js`:
  - Seção "Destaques do Povão" com toggle para exibir/ocultar
  - Seletor de período: Semanal ou Mensal
  - Card "Top 10" exibindo ranking do período selecionado
  - Card "Destaque do Mês" com stats (corridas no mês, atletas ativos)
  - Destaque para atleta "Mais Ativo" (mais corridas)
  - Destaque para atleta "Mais Pontos"
  - Botões: "Ocultar Destaques", "Como funciona?", "Regulamento"
  - Modal "Como funciona?" com explicação completa do sistema
  - Modal "Regulamento" com 7 seções detalhadas

- **Backend endpoints** em `/app/backend/routes/ranking_routes.py`:
  - `GET /api/ranking/povao/semanal` - Top 10 da última semana
  - `GET /api/ranking/povao/mensal` - Top 10 do mês atual
  - `GET /api/ranking/povao/destaque-mes` - Destaques do mês (mais ativo, mais pontos)

---

### Exclusão de Assessoria com Migração (NOVO - 17/Mar/2026)
- **Hard Delete implementado**: Ao deletar uma assessoria, todos os atletas são migrados automaticamente para "Individual"
- **Pontos preservados**: Os pontos dos atletas não são afetados pela exclusão
- **Histórico mantido**: Campo `equipe_anterior` armazena a assessoria original
- **Log completo**: Registro de quem deletou, quando e quais atletas foram afetados
- **Endpoint**: `DELETE /api/admin/assessorias/{nome_assessoria}` (apenas Super Admin)

### Sistema de Senha de Emergência (NOVO - 17/Mar/2026)
- **Senha aleatória segura**: Gerada com `secrets.token_urlsafe(24)` (~32 caracteres)
- **Acesso restrito**: Apenas Super Admin pode visualizar, regenerar e resetar
- **Limite de 3 usos por atleta**: Proteção contra uso abusivo
- **Reset manual**: Super Admin pode resetar o contador de qualquer atleta
- **Log completo**: Todos os usos são registrados (data, atleta, número do uso)

**Endpoints implementados:**
- `GET /api/admin/senha-emergencia` - Visualizar senha atual
- `POST /api/admin/senha-emergencia/regenerar` - Gerar nova senha
- `GET /api/admin/senha-emergencia/usos` - Listar log de usos
- `POST /api/admin/senha-emergencia/resetar-contador/{atleta_id}` - Resetar contador
- `POST /api/auth/login-emergencia` - Login usando senha de emergência

---

### Gerenciamento em Lote de Corridas (NOVO - 18/Mar/2026)
- **Funcionalidade completa implementada** em `/app/frontend/src/pages/admin/DashboardCorridas.jsx`:
  - Checkbox "Marcar todas" no cabeçalho da tabela
  - Checkboxes individuais em cada linha de corrida
  - Filtros por Estado (dropdown com 27 UFs) e Cidade (via API do IBGE)
  - Botões de ordenação alfabética (A-Z / Z-A)
  - Botão "Excluir Selecionadas" com contador de itens selecionados
  - Botão "Limpar" para resetar filtros e seleção

- **Endpoint de backend** em `/app/backend/routes/corridas_eventos_routes.py`:
  - `POST /api/corridas-eventos/excluir-lote` - Aceita IDs separados por vírgula

- **Bugs corrigidos durante implementação:**
  1. Role `super_admin` não permitido para criar corridas (adicionado à lista de roles)
  2. Endpoint de batch delete não parseava IDs corretamente (corrigido parsing)
  3. MongoDB `_id` aparecendo nas respostas (adicionado `$project: {_id: 0}`)
  4. SelectItem com `value=""` causando crash no React (mudado para `value="__all__"`)

---

## P1 (Próximas Tarefas)
- Refatoração do Backend (server.py → módulos específicos)
- Sistema de Metas Pessoais para atletas
- Sistema de Streaks (consistência)
- Melhorar Web Scraper com Selenium/Playwright (para sites com JavaScript)

## P2+ (Tarefas Futuras)
- Sistema de Rivais, Feed Social, Desafios Mensais
- Gráficos de Evolução, Níveis/XP
- Previsão de Ranking com IA, Certificados Digitais
- Configuração de `REDIS_URL` para produção
