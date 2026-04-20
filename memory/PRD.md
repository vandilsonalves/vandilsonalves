# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas de rua com gestão de assessorias esportivas, ranking por colocação (Profissional/Amador) e por distância (Galera/Povão), integração Strava, sistema de feed, mensagens admin com splash screen, e painel do dono de assessoria.

## Arquitetura
- **Frontend**: React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend**: FastAPI + MongoDB
- **Storage**: Emergent Object Storage (nuvem) com compressão automática
- **Integrações**: Strava, Resend (emails), Celery/Redis (mensagens agendadas)

## Funcionalidades Implementadas

### Core
- Sistema de autenticação (JWT), Ranking Profissional e Galera, Submissão de resultados
- Raio-X do atleta com share cards, Painel Admin com dashboards, Liga de Assessorias
- Painel do Dono de Assessoria, Mensagens admin com splash screen, Strava
- Parceiros, Política de Privacidade LGPD, Ranking Run Inside Social Blade

### Blindagem Jurídica do Regulamento (08/04/2026)
- Seções 1-A (Objetivo Central) e 1-B (Natureza Complementar), 9 leis + GDPR

### Object Storage em Nuvem (09/04/2026)
- 98 arquivos migrados do disco local → Emergent Object Storage
- Todos os 11 endpoints de upload atualizados para nuvem
- Endpoint proxy /api/cloud-files/{path} com cache 24h
- Backward compatibility mantida via /api/uploads/

### Compressão Automática de Imagens (09/04/2026)
- Redimensionamento automático para max 1200px (largura ou altura)
- Compressão JPEG/WebP com qualidade 80%, PNG com otimização
- Conversão RGBA→RGB automática para JPEG
- Economia média: ~90% em tamanho de arquivo

### Blindagem Jurídica Completa - 3 Pilares (09/04/2026)
- **RANKING PROFISSIONAL/AMADOR**: Tabela de pontos (1º=10 a 10º=1), categorias PCD/Cadeirante, prazo 30 dias, Art. 186 CC, proteção LGPD
- **RANKING DA GALERA (PACE LIVRE)**: Pontuação por distância (5-9km=5pts, 10-20km=7pts, 21km+=9pts), disclaimer saúde, sem colocação
- **RANKING DAS ASSESSORIAS/EQUIPES (LIGA ROE-RR)**: Sistema ROE-RR (+0,5/atleta, +1,0/resultado, bônus pódio), regra transferência temporal, selos Ouro/Prata/Bronze, CREF/CONFEF disclaimer, licenciamento de marca
- Suporte a tabelas Markdown adicionado ao RegulamentoModal.jsx
- Regulamento atualizado de v1.6 para v1.7 (106K → 130K caracteres)

## Backlog
- P2: Implementar Cloudflare Turnstile no cadastro/login (requer ação do usuário no painel Cloudflare)
- P3: Finalizar integração do scraper Sympla via sitemap nas rotas de scraping

### Sistema de Votação - Prêmio Nacional Ranking Run (10/04/2026)
- Sistema completo de votação interna substituindo Google Forms
- Backend: 10+ endpoints em `premiacao_routes.py` (config, categorias CRUD, votar, resultados, consolidar)
- Frontend Atleta: `VotacaoPage.jsx` com formulário de texto livre (nome + link Instagram)
- Frontend Admin: `DashboardPremiacao.jsx` com gestão de categorias, abrir/fechar votação, resultados e consolidação de nomes
- Navegação integrada: rota `/votacao` no App.js, botão desktop e mobile nav
- Controle antifraude manual pelo admin (visualização de IP, votantes, consolidação de variantes)
- Resultados públicos bloqueados enquanto votação aberta (403)
- Testado: 16/16 testes backend + todos os fluxos frontend verificados

### Modo "Votar" com Opções por Categoria (12/04/2026)
- Admin cria categorias com opções (A, B, C, D, E...) no modo "Votar"
- Modal "Nova Categoria" mostra campo dinâmico de opções com botão "+ Adicionar Opção"
- Listagem de categorias mostra opções inline (A) Opção · B) Opção...)
- Atleta vê botões clicáveis para selecionar opção (destaque amber + checkmark)
- Fallback: categorias sem opções usam campo de texto livre
- Testado: 11/11 backend + todas as features frontend verificadas (iteration_112)
- Admin define "Data Limite da Votação" no painel de Premiação (datetime-local input)
- Campo `data_limite` salvo via PUT /api/premiacao/admin/config e retornado no GET /api/premiacao/status
- Atleta vê countdown em tempo real (dias, horas, minutos, segundos) na página /votacao
- Quando timer zera: exibe "Prazo de votação encerrado" (admin encerra manualmente)

### Melhorias Premiação v2 (11/04/2026)
- Admin: Campos de Data de Abertura e Encerramento da votação (datetime-local)
- Admin: Upload de foto/logo da premiação (via Object Storage, max 5MB)
- Admin: Botão "Exportar Excel" exporta todos os votos com nome, email, data, IP, ID, categoria
- Atleta: Campos "Nome do indicado" e "Link do Site Oficial ou Instagram" ambos obrigatórios
- Atleta: Botão "Voltar" na página de votação
- Página principal: Banner animado dourado quando votação aberta, com link direto para /votacao
- Backend: Validação rejeita voto com link vazio (HTTP 400)
- Testado: 13/13 backend + todas as features frontend verificadas (iteration_110)

### Sistema Multi-Premiação + Bug Fix Cadastro (11/04/2026)
- **Multi-Premiação**: Admin pode criar/editar/excluir múltiplas premiações independentes
- Cada premiação tem título/subtítulo editáveis, foto, modo de votação (indicar/votar), regulamento
- Categorias com upload de foto/ícone por categoria
- Migração automática de dados antigos (single → multi)
- Atleta: Splash de advertência antes do primeiro voto
- Atleta: Votação única — após finalizar, não pode mais editar
- Atleta: Splash animado de parabéns + notificação in-app + email com resumo
- Atleta: Botão de regulamento por premiação
- **Bug Fix**: Import CadastroTermoModal faltando na página de Cadastro
- Testado: 20/20 backend + todos os fluxos frontend verificados (iteration_111)

### Modo "Votar" com Opções por Categoria (12/04/2026)
- Admin cria categorias com opções (A, B, C...) no modo "Votar"
- Atleta vê botões clicáveis para selecionar opção
- Testado: 11/11 backend + frontend (iteration_112)

### Histórico de Votações + Banner Inteligente (12/04/2026)
- Atleta vê premiações separadas em "Votação Aberta" e "Encerradas" com pódio (1°, 2°, 3°)
- Banner laranja desaparece após atleta finalizar todas as votações ativas
- Testado: 9/9 backend + frontend (iteration_113)

### Precos Editaveis do Atleta Premium + Integracao EFI/Stripe (12/04/2026)
- Admin edita precos do plano Premium via DashboardFinanceiro (Preco Original, Desconto, Parcelas, Data Fim Oferta, Validade, Pos-Oferta)
- Novos endpoints: GET /api/financeiro/config-precos-publico (publico), GET/POST /api/admin/financeiro/config-precos (admin)
- PagamentoPage.jsx e AccessGate.jsx consomem precos dinamicos via API (eliminados todos os valores hardcoded)
- Backend (efi_routes.py, pagamentos_routes.py) busca precos do MongoDB ao criar cobranças PIX e Cartao
- Certificado EFI produção (.p12) configurado, chaves Stripe de teste configuradas no .env
- Valor da parcela recalculado automaticamente ao salvar (preco_desconto / parcelas)
- Testado: 16/16 backend + todos os fluxos frontend verificados (iteration_114)

### Bug Fixes Painel Dono de Assessoria (12/04/2026)
- Bug 1: Exportar "Graficos" agora retorna Content-Disposition:attachment (força download ao invés de exibir JSON)
- Bug 2: "Exportar Lista" de atletas agora gera CSV client-side via Blob (não chama mais endpoint admin-only)
- Bug 3: Upload de foto agora usa URL correta `/api/assessorias/upload-foto` (antes usava rota inexistente `/api/assessoria/foto`)
- Testado: 18/18 backend + todos os fluxos frontend verificados (iteration_115)

### Exportação de Rankings por Modalidade (13/04/2026)
- 4 novos endpoints Excel: ranking-profissional (6 abas por categoria/genero), ranking-galera (M/F), ranking-assessorias, ranking-corridas-avaliadas
- Botões adicionados na aba "Exportar Ranking" do Admin com destaque amber
- Testado: iteration_116

### Sistema de Gestão de Temporadas (13/04/2026)
- Backend: `temporadas_routes.py` com GET /api/temporadas/ativa, /historico, /{id}/ranking-final, /admin/temporadas, POST /admin/temporadas/encerrar
- Temporada 2026 criada automaticamente como "ativa"
- Encerramento protegido: janela 01-02 janeiro, super_admin only, senha master, confirmação textual "ENCERRAR {ano}"
- Snapshot automático dos rankings finais (profissional, galera, assessorias, corridas avaliadas)
- Reset lógico: pontuações zeradas para nova temporada, histórico preservado em campo `historico_pontos.{ano}`
- Frontend Admin: DashboardTemporadas na sidebar SISTEMA com card da temporada ativa, botão encerrar (desabilitado fora da janela), histórico expansível
- Frontend Público: /historico-temporadas com lista de temporadas encerradas e ranking final expandível
- Testado: 15/15 backend + todos os fluxos frontend verificados (iteration_116)

### Hall da Fama na Pagina Principal (13/04/2026)
- Componente `HallDaFama.jsx` adicionado na RankingPage (homepage /)
- Exibe campeões de cada temporada encerrada: Profissional M/F top 5, PCD M/F top 5, Cadeirante M/F top 5, Galera M/F top 5, Assessorias top 10, Corridas Avaliadas top 10
- Auto-expande a temporada mais recente encerrada com visual de medalhas (ouro/prata/bronze)
- Condicional: só aparece se houver temporadas finalizadas no banco
- Seed data: Temporada 2025 criada como exemplo com snapshot de rankings
- Testado: 18/18 backend + todos os fluxos frontend verificados (iteration_117)

### 8 Tarefas Implementadas em Paralelo (13/04/2026)
1. **Bug Fix Feed/Stories**: Corrigido URL duplo `/api/api/` nas imagens de posts e stories (FeedPostCard.jsx, StoriesBar.jsx)
2. **Hall da Fama Contraste**: Melhorado contraste com bg-gray-900, texto branco bold, pontos emerald-300
3. **Ranking por Cidade Mobile**: Layout responsivo com gap-2/gap-4, text-sm/text-base, flex-shrink-0
4. **Pontuação Galera**: Corrigido preview: 5KM=5pts, 10KM=7pts, 21KM=9pts, 42KM=9pts + custom
5. **Frase Bíblica**: "All honor and glory be given to the Lord Jesus Christ. 1 Co 9:24" em itálico
6. **Exportar Excel Corridas**: Novo endpoint `/api/admin/exportar/corridas-completas` + botão no Admin
7. **Autorizações Data Customizada**: Admin pode definir data específica de expiração (tipo_plano=data_customizada)
7b. **Super Admin Restrito**: Apenas vandy1250@gmail.com e suporte@rankingrun.com.br via SUPER_ADMIN_EMAILS
8. **Restaurar Backup**: Upload de .zip no DashboardBackup via `/api/admin/backup/restaurar-upload`
- Testado: 19/19 backend + todos os fluxos frontend verificados (iteration_118)

## Status: PRONTA PARA PRODUCAO (13/04/2026)
- 11.566 docs de teste removidos, banco limpo
- Usuario preservado: vandy1250@gmail.com (super_admin)
- Catalogo de 1.315 corridas mantido, Temporada 2026 ativa

### Segurança para Produção (14/04/2026)
- CORS restrito: apenas app.rankingrun.com.br, rankingrun.com.br, www.rankingrun.com.br, geo-filtered-admin.emergent.host
- Endpoints protegidos com auth: ranking/povao, semanal, mensal, destaque-mes, equipes, faixas-etarias, ranking-por-cidade, ranking-nacional
- Endpoints públicos mantidos: stats agregados, configurações básicas
- Rate Limiting: 60 req/min geral, 10 req/min login, 5 req/min export, 30 req/min rankings
- Security Headers: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy, Cache-Control
- Parameter Validation: limit max 20, page validado, ano validado
- URLs hardcoded de preview removidas (usam FRONTEND_URL env var)

### Segurança Anti-Scraping v2 (17/04/2026)
- Rate Limiting por User ID (JWT sub): 100 req/min + 1000 req/dia auth, 30 req/min anon (NÃO por IP)
- Bloqueio automático: 10 minutos ao exceder rate limit
- Anti-bot: detecção de intervalos < 50ms entre requisições (8+ triggers = block 10min)
- Anti-scraping: detecção de paginação sequencial (>15 pages/60s = block 10min)
- Validação estrita: page max 100, limit max 20-50 conforme rota, ano validado
- Token Rotation: access token 10 minutos, refresh token 7 dias
- Endpoint /api/auth/refresh para renovação automática de tokens
- Frontend: Axios interceptor auto-refresh em 401 (retry transparente)
- Token blacklist em memória para invalidação
- 25+ rotas adicionais protegidas: assessorias, liga, badges, strava-atividades, feed, indicação, corridas detalhes
- Rotas públicas mantidas apenas para: auth, webhooks, health, catálogo, temporadas, regulamento, preços, parceiros
- Lista PUBLIC_PATHS centralizada no middleware
- Guia Cloudflare WAF/Turnstile criado em /app/memory/CLOUDFLARE_SECURITY_GUIDE.md
- Testado: 36/36 backend + todos os fluxos frontend verificados (iteration_120)

### Bug Fixes Segurança (17/04/2026)
- Bug 1: Feed bloqueado por anti-bot (escopo incluía /feed/) → Anti-bot reduzido para apenas /ranking, /liga-assessorias, /strava-atividades, /badges/ranking
- Bug 2: Cadastro fechava automaticamente → /assessorias/lista tornado público (necessário para dropdown de equipes) + interceptor Axios não redireciona em /login e /cadastro
- Bug 3: Feed da equipe/assessoria bloqueado → Anti-bot não monitora mais /assessorias
- Testado: 16/16 backend + 3 bugs verificados corrigidos (iteration_121)

## Credenciais de Producao
- Super Admin: vandy1250@gmail.com (senha do cadastro)
- Super Admin: suporte@rankingrun.com.br (promovido ao cadastrar)
- Senha Master: d7ff103ad1250@#$

## Notas Técnicas
- Object Storage inicializa automaticamente no startup (pode ter 503 temporário)
- Compressão automática acontece ANTES do upload para a nuvem
- Pillow (PIL) é usado para redimensionamento e compressão
- Chave EMERGENT_LLM_KEY necessária no .env para Object Storage
- Regulamento é DB-driven (collection `configuracoes`, tipo `regulamento`), nunca hardcoded no frontend

### Sumário Navegável no Regulamento (09/04/2026)
- Botão "Sumário" colapsável no header do modal do Regulamento
- Painel de Navegação Rápida com grid 2 colunas, badges numerados
- Scroll suave automático para cada seção ao clicar
- Painel fecha automaticamente após navegação

### Limpeza AdminDashboard.jsx (09/04/2026)
- Import duplicado de lucide-react consolidado
- DashboardGeral tornado auto-suficiente (busca próprios dados)
- 12 useState e 3 fetchers removidos do AdminDashboard
- Prop onStatsRefresh removido do DashboardSubmeter
- AdminDashboard: 849→761 linhas, 54→42 states, 11→8 fetchers
- 13 bugs de responsividade mobile corrigidos no painel Admin
- Sidebar responsiva: esconde em mobile, abre como overlay com hamburger
- Grids, tabelas, modais e cards ajustados para viewport 390px
- Cores dos títulos Retenção/Financeiro alteradas de branco para verde
- Contraste melhorado no Corridas Parceiras
- Busca de atletas no Submeter Resultados substituída por combobox funcional
- Bug de salvamento nas Configurações corrigido (descricao_galera -> descricao_povao)
