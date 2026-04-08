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
- Formulário 100% manual com 15+ campos organizados em 4 seções
- 14 Notas no sistema: A++, A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F
- 7 fórmulas de cálculo no backend com 7 gráficos distintos
- Upload de foto com crop: Modal de recorte circular com zoom e rotação
- Exportação XLSX, CSV e PDF (com gráficos via Matplotlib)

### Política de Privacidade (07/04/2026)
- Página completa em /politica-de-privacidade com 19 seções expansíveis
- Blindagem jurídica: LGPD, Marco Civil da Internet, CDC, CRFB, GDPR

### Parceiros e Patrocinadores (07/04/2026)
- Aba "Parceiros" no painel admin (CRUD: Nome, Instagram, Site, Imagem com crop 1:1)
- Exportação Excel dos parceiros
- Página pública /parceiros com grid de imagens

### Correções Mobile (08/04/2026)
- Strava redirect corrigido com FRONTEND_URL no backend .env
- Ranking de corridas com paginação e cache (endpoint em corridas_eventos_routes.py)
- Cache localStorage para API IBGE no formulário de submissão de resultados
- Botão Compartilhar do Raio-X ajustado com flex-wrap para mobile
- Endpoints duplicados removidos de ranking_corridas_routes.py (limpeza de código)

### Blindagem Jurídica do Regulamento (08/04/2026)
- **Seção 1-A**: "Objetivo Central da Plataforma" — declaração explícita de que a plataforma nunca substituirá entidades oficiais
- **Seção 1-B**: "Natureza Complementar da Plataforma" — 6 declarações (a-f) incluindo conformidade constitucional e Lei Pelé
- **Fundamentação legal na Seção 1**: 8 leis referenciadas (LGPD, Marco Civil, CDC, CF/88, GDPR, Decreto 8.771, Lei de Direitos Autorais, Lei de Propriedade Industrial)
- **Proteção de dados na avaliação** (Seção 5): Art. 7° LGPD, coleta de IP/user-agent, direitos do titular (Arts. 17-22)
- **Conduta dos Usuários** (Seção 12): Marco Civil Arts. 21-22, CDC Art. 39, Código Civil Arts. 186/927, Código Penal Arts. 138-140
- **Responsabilidade** (Seção 13): Marco Civil Arts. 18-19 (limitação de responsabilidade do provedor)
- **Isenção** (Seção 14): CF Art. 5° IV/IX, CDC Art. 14 §3°
- **Liberdade de Opinião** (Seção 19): CF Art. 5° IV/IX, Marco Civil Art. 3° e Arts. 19/21, direito de ampla defesa (Art. 5° LV)
- **Foro** (Seção 22): 8 leis listadas + Lei de Mediação 13.140/2015 + Lei de Arbitragem 9.307/1996
- **Participação Voluntária** (Seção 23): Direito constitucional de acesso à informação (Art. 5° XIV/XXXIII)
- **Uso Comercial** (Seção 27): Proteção de propriedade intelectual (Leis 9.279/96 e 9.610/98)
- **Carta de Princípios**: Livre iniciativa (Art. 170 CF), Lei Pelé (Lei 9.615/98)
- **Política de Integridade**: LGPD e GDPR como objetivos formais
- Regulamento atualizado de v1.3 para v1.5 (93.8KB → 106.4KB)

## 9 Leis Referenciadas no Regulamento
1. Constituição Federal de 1988 (múltiplos artigos)
2. Lei n. 13.709/2018 (LGPD)
3. Lei n. 12.965/2014 (Marco Civil da Internet)
4. Lei n. 8.078/1990 (CDC)
5. Lei n. 10.406/2002 (Código Civil)
6. Lei n. 9.610/1998 (Direitos Autorais)
7. Lei n. 9.279/1996 (Propriedade Industrial)
8. Lei n. 9.615/1998 (Lei Pelé)
9. Regulamento UE 2016/679 (GDPR)
+ Decreto 8.771/2016, Lei 13.140/2015 (Mediação), Lei 9.307/1996 (Arbitragem)

## Backlog
- P3: Exportar Raio-X como PDF
- P3: Investigar scraping Sympla bloqueado por Cloudflare

## Credenciais de Teste
- Admin: admin@runpro.com / admin
- Atleta/Dono: teste.dono@teste.com / 123456
- Senha Mestra: d7ff103ad1250@#$

## Notas Técnicas
- Redis pode crashar no ambiente de preview; reiniciar manualmente se Celery/uploads falharem
- Componentes extraídos: não adicionar código de volta nos arquivos principais
- A regra de 30 dias voltará a valer normalmente a partir de 2027
- Endpoint /ranking-corridas principal está em corridas_eventos_routes.py (com cache e paginação)
- ranking_corridas_routes.py contém apenas endpoints de avaliação e reputação (sem duplicatas)
