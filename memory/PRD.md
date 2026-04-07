# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas de rua com gestão de assessorias esportivas, ranking por colocação (Profissional/Amador) e por distância (Galera/Povão), integração Strava, sistema de feed, mensagens admin com splash screen, e painel do dono de assessoria.

## Arquitetura
- **Frontend**: React + Shadcn/UI + Tailwind CSS + Recharts
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
- Isenção regra 30 dias para 2026
- Senha Mestra Super Admin
- 15 botões de exportação Excel
- Sistema de submissão de Novas Corridas por atletas (anti-duplicidade + aprovação)
- 29 testes unitários cobrindo funcionalidades críticas

### Ranking Run Inside - Social Blade (07/04/2026)
- **Formulário 100% manual** com 15+ campos organizados em 4 seções:
  - Identificação (@Username, Nome, Data, Upload Foto de Perfil)
  - Dados Gerais (Seguidores, Seguindo, Posts, Nota A++..F, Classificação SB, Classif. Seguidores)
  - Crescimento 30d (Ganho, Perda, Médias Semanais)
  - Interações 30d (Posts 30d, Média Semanal Posts, Views Reels 6 últimos, Curtidas/Comentários Médios)
- **7 fórmulas de cálculo** no backend:
  1. Nota (Taxa de Curtidas) → Gauge/Donut
  2. Views de Reels → Barras Horizontais
  3. Taxa de Engajamento → Pizza
  4. Curtidas Médias → Colunas Verticais
  5. Comentários Médios → Linhas
  6. Crescimento Mensal → Radar (6 eixos)
  7. Posts 30 dias → Histograma
- **Score Médio** calculado automaticamente (média dos 6 scores numéricos)
- **Upload de foto de perfil** com preview
- **Exportação** XLSX e CSV
- **Painel de Scores** consolidado com barras de progresso por métrica

## Backlog
- P3: Exportar Raio-X como PDF
- P3: Investigar scraping Sympla bloqueado por Cloudflare

## Testes Unitários
- `/app/backend/tests/test_critical_features.py` — 29 testes
- `/app/backend/tests/test_iter104_instagram_social_blade.py` — 10 testes (Social Blade)

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta/Dono: teste.dono@teste.com / 123456
- Senha Mestra: d7ff103ad1250@#$

## Notas Técnicas
- Redis pode crashar no ambiente de preview; reiniciar manualmente se Celery/uploads falharem
- Componentes extraídos: não adicionar código de volta nos arquivos principais
- A regra de 30 dias voltará a valer normalmente a partir de 2027
