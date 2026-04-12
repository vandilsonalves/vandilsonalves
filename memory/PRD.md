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
- P1: Validar e concluir integracao Pix EFI end-to-end (credenciais já configuradas, testar geração de QR Code real)
- P2: Ranking de participação nas votações (barra de progresso no admin)
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

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta/Dono: teste.dono@teste.com / 123456
- Senha Mestra: d7ff103ad1250@#$

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
