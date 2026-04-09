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
- P3: Finalizar integração do scraper Sympla via sitemap nas rotas de scraping

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
