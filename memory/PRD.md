# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas de rua com gestão de assessorias esportivas, ranking por colocação (Profissional/Amador) e por distância (Galera/Povão), integração Strava, sistema de feed, mensagens admin com splash screen, e painel do dono de assessoria.

## Arquitetura
- **Frontend**: React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend**: FastAPI + MongoDB
- **Storage**: Emergent Object Storage (nuvem)
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
- Senha Mestra Super Admin
- 15 botões de exportação Excel
- Sistema de submissão de Novas Corridas por atletas

### Ranking Run Inside - Social Blade (07/04/2026)
- Formulário 100% manual com 15+ campos
- 14 Notas no sistema: A++ a F
- 7 gráficos distintos + Exportação PDF/XLSX/CSV

### Política de Privacidade e LGPD (07/04/2026)
- Página completa com 19 seções expansíveis
- Blindagem jurídica: LGPD, Marco Civil, CDC, CF, GDPR

### Parceiros e Patrocinadores (07/04/2026)
- CRUD no admin + Página pública + Exportação Excel

### Blindagem Jurídica do Regulamento (08/04/2026)
- Seções 1-A (Objetivo Central) e 1-B (Natureza Complementar)
- 9 leis brasileiras + GDPR referenciadas
- v1.3 → v1.5 (93.8KB → 106.4KB)

### Correções Mobile (08/04/2026)
- Strava redirect, ranking paginado, cache IBGE, botão Compartilhar responsivo
- Regulamento legível no mobile (width responsivo + text-sm + break-word)

### Object Storage em Nuvem (09/04/2026)
- **Migração completa**: 98 arquivos do disco local → Emergent Object Storage
- **Todos os uploads migrados**: perfil, feed, stories, chat, parceiros, assessorias, corridas parceiras, mensagens admin, autorizações, ranking inside
- **Endpoint proxy**: `/api/cloud-files/{path}` serve arquivos da nuvem com cache
- **Compatibilidade**: `/api/uploads/` legado mantido para arquivos antigos
- **29 URLs atualizadas no MongoDB** automaticamente
- **Testado**: 15/15 testes passaram (iteration_108)

### Sympla Scraper (09/04/2026 - em andamento)
- Removido da lista SITES_PLAYWRIGHT (Cloudflare bloqueia)
- Implementado scraper via sitemap XML (acessível sem Cloudflare)
- Filtro por keywords de corrida nas URLs do sitemap
- Extração de nome/local/estado a partir dos slugs das URLs

## Backlog
- P3: Finalizar integração do scraper Sympla nas rotas de scraping existentes

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta/Dono: teste.dono@teste.com / 123456
- Senha Mestra: d7ff103ad1250@#$

## Notas Técnicas
- Redis pode crashar no ambiente de preview; reiniciar manualmente se Celery/uploads falharem
- Endpoint /ranking-corridas principal em corridas_eventos_routes.py (com cache e paginação)
- Object Storage inicializa automaticamente no startup do servidor
- Chave EMERGENT_LLM_KEY necessária no .env para Object Storage
- Arquivos antigos em /app/uploads/ são servidos via mount StaticFiles (backward compatibility)
