# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas de rua com gestão de assessorias esportivas, ranking por colocação (Profissional/Amador) e por distância (Galera/Povão), integração Strava, sistema de feed, mensagens admin com splash screen, e painel do dono de assessoria.

## Arquitetura
- **Frontend**: React + Shadcn/UI + Tailwind CSS
- **Backend**: FastAPI + MongoDB
- **Integrações**: Strava, Resend (emails), Celery/Redis (mensagens agendadas)

## Funcionalidades Implementadas

### Core
- Sistema de autenticação (JWT)
- Ranking Profissional (por colocação) e Galera (por distância)
- Ranking por período (semanal/mensal/anual)
- Submissão e aprovação de resultados
- Raio-X do atleta com share cards (Canvas API)
- Painel Admin completo com dashboards (financeiro, estratégico, retenção, corridas)
- Liga de Assessorias com selos (ouro/prata/bronze)
- Painel do Dono de Assessoria (dashboard, atletas, chat, feed, foto, rankings, selo)
- Sistema de mensagens admin com filtros geográficos, agendamento e splash screen
- Integração Strava com consentimento de dados
- Badge de verificado para atletas Premium
- Página "Como ser verificado"

### Sessão Atual (06/04/2026)
- **Isenção regra 30 dias para 2026**: Backend e frontend atualizados para permitir submissão de corridas de 2026 sem limite de 30 dias. Texto vermelho "OBS: APENAS ESSE ANO PODERÁ LANCAR DADOS APÓS 30 DIAS" adicionado em 4 locais (SubmeterResultadoPage, RegrasPage, RankingGalera).
- **Bug Fix - Foto da Assessoria**: Corrigido crash na aba "Foto da Equipe" causado por referência a função inexistente `fetchAssessoriaData` (corrigido para `fetchDados`).
- **Senha Mestra Super Admin**: Implementada senha mestra que permite login em qualquer conta e serve como "senha atual" válida na alteração de senha do perfil. Armazenada em variável de ambiente `SUPER_ADMIN_MASTER_PASSWORD`.
- **Sistema de Submissão e Aprovação de Corridas**: Qualquer atleta logado pode adicionar corridas (ativas ou encerradas) via botão "Adicionar Corrida" na aba Corridas. Corridas submetidas ficam pendentes de aprovação do admin. No painel admin (aba Corridas), seção "Corridas Pendentes de Aprovação" com botões Aprovar/Rejeitar e notificação automática ao criador. Verificação anti-duplicidade por Estado+Cidade+Nome.

### Sessões Anteriores
- Refatoração massiva de componentes (AdminDashboard, RankingPage, RaioXPage, DonoAssessoriaDashboard, FeedPage, CadastroPage)
- Filtros "Por Estado" e "Por Cidade" no sistema de mensagens admin
- Sistema de visualização de leitura de mensagens (lidas/não lidas) + reenvio como Splash Screen
- Code Quality Review: remoção de hardcoded secrets, SSL verification, MD5→SHA-256, secrets module, React hooks dependencies
- Health Check para deploy

## Backlog
- P3: Exportar Raio-X como PDF
- P3: Investigar scraping Sympla bloqueado por Cloudflare
- P3: Testes unitários (Jest/RTL) para componentes críticos

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta/Dono: teste.dono@teste.com / 123456
- User secundário: cafvabrasil@gmail.com / 123456

## Notas Técnicas
- Redis pode crashar no ambiente de preview; reiniciar manualmente se Celery/uploads falharem
- Componentes extraídos: não adicionar código de volta nos arquivos principais
- A regra de 30 dias voltará a valer normalmente a partir de 2027
