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
  - **Filtro por Período/Data** com opções:
    - Próximos 30 dias
    - Próximos 90 dias
    - Últimos 30 dias
    - Últimos 90 dias
    - Período personalizado (data início/fim)
  - **Filtro por Status** (Ativas / Encerradas / Canceladas)
  - Botões de ordenação alfabética (A-Z / Z-A)
  - Botão "Excluir Selecionadas" com contador de itens selecionados
  - **Botão "Exportar CSV"** com opções:
    - Por Estado (CSV agrupado por UF)
    - Por Data (CSV ordenado por data da corrida)
  - **Botão "Relatório PDF"** com gráficos visuais:
    - Cards de resumo (Total, Ativas, Média, Avaliações)
    - Gráfico de barras: Top 10 Estados
    - Gráfico de pizza: Status das Corridas
    - Gráfico temporal: Evolução Mensal
    - Tabela resumida por Estado
  - Botão "Limpar" para resetar filtros e seleção

### Filtros e Exportação de Assessorias (NOVO - 18/Mar/2026)
- **Funcionalidade implementada** em `/app/frontend/src/pages/admin/DashboardAssessorias.jsx`:
  - Filtros locais por **Estado** (27 UFs) e **Cidade** (via API do IBGE)
  - **Botão "Exportar CSV"** com opções:
    - Por Estado (CSV agrupado por UF)
    - Por Cidade (CSV agrupado por cidade)
  - **Botão "Relatório PDF"** com gráficos visuais:
    - Cards de resumo (Total, Atletas, Resultados, Verificadas)
    - Gráfico de barras: Top 10 por Pontos
    - Gráfico de pizza: Distribuição por Selo
    - Gráfico de barras: Assessorias por Estado
    - Tabela resumida Top 10
  - Contador "Mostrando X de Y assessorias"
  - Botão "Limpar" para resetar filtros

- **Endpoint de backend** em `/app/backend/routes/corridas_eventos_routes.py`:
  - `POST /api/corridas-eventos/excluir-lote` - Aceita IDs separados por vírgula

- **Bugs corrigidos durante implementação:**
  1. Role `super_admin` não permitido para criar corridas (adicionado à lista de roles)
  2. Endpoint de batch delete não parseava IDs corretamente (corrigido parsing)
  3. MongoDB `_id` aparecendo nas respostas (adicionado `$project: {_id: 0}`)
  4. SelectItem com `value=""` causando crash no React (mudado para `value="__all__"`)

---

## P1 (Próximas Tarefas)
- **Foto da Assessoria**: Exibir foto no cabeçalho e perfil da assessoria
- **Link WhatsApp**: Adicionar campo para configurar link do WhatsApp no botão "Quero Treinar"
- **Sistema de Aprovação de Membros**: Permitir dono aprovar/reprovar novos membros
- Refatoração do Backend (server.py → módulos específicos)
- Sistema de Metas Pessoais para atletas
- Sistema de Streaks (consistência)
- Melhorar Web Scraper com Selenium/Playwright

## P2+ (Tarefas Futuras)
- Sistema de Rivais, Feed Social, Desafios Mensais
- Gráficos de Evolução, Níveis/XP
- Previsão de Ranking com IA, Certificados Digitais
- Configuração de `REDIS_URL` para produção

---

### Correções de Bugs - Painel Assessoria (18/Mar/2026)
- **Bug 1 - Ranking Estadual**: Corrigido filtro que retornava assessorias de outros estados. Agora filtra após agrupamento no pipeline MongoDB.
- **Bug 2 - Envio de Mensagens**: Criado endpoint `POST /api/notificacoes/enviar` para dono de assessoria enviar mensagens aos atletas.
- **Bug 3 - Dono na lista de atletas**: Modificado endpoint para incluir o dono na lista de atletas com flag `is_dono: true`.
- **Campo whatsapp_link**: Adicionado campo na resposta da API para suportar link do WhatsApp.
- **Permissão super_admin**: Adicionado role `super_admin` aos endpoints de relatórios.

### Melhorias Painel Admin e Perfil (18/Mar/2026)
- **Campo WhatsApp no Perfil**: Adicionado campo "Link de Mensagem WhatsApp" no Meu Perfil apenas para donos de assessoria
- **Ícone de Mensagem no Admin**: Adicionado botão de mensagem (azul) na lista de atletas do painel admin
- **Modal de Mensagem Individual**: Modal para admin enviar mensagem individual para cada atleta
- **Modal de Promover Dono**: Modal de confirmação para promover atleta a dono de assessoria
- **Ranking Estadual (DonoAssessoriaDashboard)**: Corrigido para buscar ranking do estado correto da assessoria, não do usuário

### Melhorias P0 - Notificações, Assessoria e UX (18/Mar/2026)
- **Botão Atualizar Página**: Adicionado ícone de refresh (RefreshCw) no header ao lado do nome do usuário e sino de notificações
- **Notificações Aprimoradas**:
  - Modal de detalhes ao clicar em uma notificação
  - Suporte a links clicáveis (URLs são convertidas automaticamente)
  - Indicador de imagem quando notificação contém anexo
  - Modal para visualização de imagem ampliada
  - Botão de exclusão de notificação com confirmação
  - Novo endpoint `DELETE /api/notificacoes/{id}` para excluir notificações
  - Novo endpoint `GET /api/notificacoes/{id}` para obter detalhes completos
- **Formulário de Criação de Assessoria**:
  - Autocomplete de Estado/Cidade via API do IBGE
  - Dropdown de cidades carrega automaticamente ao selecionar estado
  - Fallback para input manual se API do IBGE falhar
  - Modal obrigatório que bloqueia navegação até preenchimento (para novos donos)
  - Pontuação inicial de 0,5 pontos para novas assessorias
- **Arquivos modificados**:
  - `/app/frontend/src/components/NotificacoesBell.jsx` - Componente completo refatorado
  - `/app/frontend/src/components/CriarAssessoria.jsx` - Com IBGE e modo modal
  - `/app/frontend/src/pages/RankingPage.js` - Botão refresh no header
  - `/app/frontend/src/pages/PerfilAtletaPage.jsx` - Modal obrigatório para assessoria
  - `/app/backend/routes/notificacoes_routes.py` - Endpoints GET/{id} e DELETE/{id}
  - `/app/backend/routes/atletas_routes.py` - Pontuação inicial 0.5

### Sistema de Solicitações de Entrada em Assessorias (18/Mar/2026)
- **Contador de Pendentes no Painel do Dono**:
  - Nova aba "Solicitações" no menu lateral do DonoAssessoriaDashboard
  - Badge animado mostrando quantidade de solicitações pendentes
  - Lista de solicitações com avatar, nome, cidade/estado, data e mensagem do atleta
  - Botões de "Aprovar" e "Reprovar" com feedback via toast
  - Estado vazio quando não há solicitações
- **Botão "Solicitar Entrada" na Página da Assessoria**:
  - Botão azul "Solicitar Entrada na Equipe" visível para atletas sem equipe
  - Modal com campo de mensagem opcional para apresentação
  - Verificação automática de solicitação pendente
  - Mensagem "aguardando aprovação" quando já tem solicitação
  - Mensagem informativa para quem já tem equipe
  - Link "Faça login" para usuários não autenticados
  - Integração com WhatsApp quando configurado pelo dono
- **Endpoints de Backend**:
  - `POST /api/assessorias/solicitar-entrada` - Atleta sem equipe solicita entrada
  - `GET /api/assessorias/solicitacoes-pendentes` - Lista solicitações pendentes para o dono
  - `POST /api/assessorias/aprovar-solicitacao/{id}` - Aprova e adiciona atleta à equipe
  - `POST /api/assessorias/reprovar-solicitacao/{id}` - Reprova solicitação com motivo opcional
  - `GET /api/assessorias/minhas-solicitacoes` - Atleta vê suas solicitações
- **Lógica de Negócio**:
  - Atleta só pode solicitar se não tiver equipe
  - Não permite solicitar se já há solicitação pendente para mesma assessoria
  - Aprovação atualiza a equipe do atleta e notifica
  - Reprovação notifica atleta com motivo
- **Arquivos modificados**:
  - `/app/backend/routes/assessorias_routes.py` - Todos os endpoints de solicitações
  - `/app/frontend/src/pages/DonoAssessoriaDashboard.jsx` - Aba de solicitações completa
  - `/app/frontend/src/pages/AssessoriaPage.jsx` - Botão solicitar entrada na página pública

### Melhorias P1 - Foto da Assessoria, Refatoração e Web Scraper (18/Mar/2026)
- **Foto da Assessoria em vez do Selo**:
  - Na página da assessoria (AssessoriaPage.jsx), a foto da assessoria é exibida no header se existir
  - O selo é mantido como badge pequeno no canto inferior direito da foto
  - Se não houver foto, mantém o ícone do selo como antes
  - Também atualizado no certificado/selo digital lateral
- **Correção no Campo de Equipe (Cadastro)**:
  - Removido `readOnly` do campo quando "Individual" selecionado
  - Adicionado ícone "X" para limpar a seleção
  - Adicionado link "Clique aqui para selecionar outra equipe" no alerta
  - Agora o atleta pode mudar de Individual para outra assessoria durante o cadastro
- **Web Scraper com Playwright**:
  - Instalado Playwright + Chromium para scraping de sites com JavaScript
  - Nova função `fazer_scraping_playwright()` para sites modernos com SPAs
  - Fallback automático: se scraping normal não encontrar nada, tenta com Playwright
  - Parâmetro `usar_playwright=true` no endpoint para forçar uso
  - Extrator genérico de eventos para HTML renderizado por JavaScript
- **Arquivos modificados**:
  - `/app/frontend/src/pages/AssessoriaPage.jsx` - Foto no header e selo digital
  - `/app/frontend/src/pages/CadastroPage.js` - Campo de equipe editável
  - `/app/backend/services/scraping_corridas.py` - Suporte a Playwright
  - `/app/backend/routes/corridas_eventos_routes.py` - Parâmetro usar_playwright

### Upload de Foto e Gráficos para Dono da Assessoria (19/Mar/2026)
- **Upload de Foto da Assessoria**:
  - Novo endpoint `POST /api/assessorias/upload-foto` para upload de imagem
  - Novo endpoint `DELETE /api/assessorias/remover-foto` para remover foto
  - Validação de tipo de arquivo (JPEG, PNG, WebP, GIF) e tamanho (máx 5MB)
  - Armazenamento em `/app/uploads/assessorias/`
  - Nova aba "Foto da Equipe" no menu do DonoAssessoriaDashboard
  - Interface de upload com drag-and-drop e preview
  - Preview de como a assessoria aparece com a foto
- **Novos Gráficos no Painel do Dono**:
  - Gráfico de Distribuição por Cidade (BarChart horizontal)
  - Gráfico Top 5 Atletas - Mais Pontos (BarChart)
  - Card de Conquistas da Equipe (pódios: 1º, 2º, 3º lugares)
  - Card de Posições nos Rankings (nacional, estadual, mensal)
- **Arquivos modificados**:
  - `/app/backend/routes/assessorias_routes.py` - Endpoints de upload/remoção de foto
  - `/app/frontend/src/pages/DonoAssessoriaDashboard.jsx` - Aba foto + novos gráficos

### Refatoração do Backend - Novos Módulos (19/Mar/2026)
- **Novos arquivos de rotas criados**:
  - `/app/backend/routes/rankings_routes.py` - Ranking nacional, estados, faixas, equipes, destaque do mês
  - `/app/backend/routes/regulamento_routes.py` - Regulamento público e admin, termo de avaliação
  - `/app/backend/routes/autorizacoes_routes.py` - Autorizações, período de teste, status de acesso
- **Routers registrados no server.py**:
  - `rankings_router`, `regulamento_router`, `autorizacoes_router`
- **Funções migradas do server.py**:
  - `get_ranking_nacional`, `get_estados_disponiveis`, `get_faixas_disponiveis`, `get_equipes_disponiveis`, `get_destaque_mes`
  - `get_regulamento`, `atualizar_regulamento`, `get_regulamento_admin`, `get_texto_termo`, `atualizar_termo_avaliacao`
  - `listar_autorizacoes`, `listar_atletas_periodo_teste`, `criar_autorizacao`, `revogar_autorizacao`, `verificar_status_acesso`
