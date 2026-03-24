# RunPro - Fitness Ranking Platform

## Problem Statement
Plataforma full-stack de ranking fitness para corridas. O sistema possui rankings por categoria, cidade, equipes, e um painel avançado "RAIO-X" com gráficos de performance, exportação PDF/Excel e compartilhamento em redes sociais.

## Tech Stack
- Frontend: React + Shadcn UI + Tailwind CSS
- Backend: FastAPI + MongoDB + Redis
- Integrações: Strava, Resend (Email)

## Core Features
- Sistema de ranking (profissional, amador, "galera/povão")
- Ranking por cidade com filtros de gênero e modalidade
- RAIO-X: painel de análise de performance individual
- Exportação PDF/Excel de dados do RAIO-X
- Share Card (Canvas API 9:16) com insígnias 3D
- Sistema de badges/conquistas
- Painel admin completo
- Integração Strava

## What's Been Implemented

### Completed (Previous Sessions)
- Sistema completo de ranking (categoria, equipe, semanal, mensal)
- RAIO-X com gráficos de performance, pace, recordes
- Exportação PDF/Excel (todas as abas)
- Compartilhamento redes sociais via Canvas API (formato 9:16)
- Aba de Conquistas (Badges) visuais no RAIO-X
- Botão RAIO-X na nav bar
- Correção distância total (tratamento strings KM)
- Comparativo dinâmico mês a mês com seletores
- Nomes das corridas nos recordes
- Remoção de "Dias Favoritos"
- Refatoração Canvas API (substituiu html2canvas)
- Desenho de ícones 3D no Share Card

### Completed (Session 2026-03-24)
- Bug Fix: Filtro de Gênero/Modalidade no Ranking por Cidade
  - Backend: Adicionado filtro por gênero nos 3 caminhos (povão, profissional, fallback) em ranking_routes.py
  - Frontend: Seletor de Gênero visível para ambas as modalidades (profissional E galera)
  - Testado: 100% backend (12/12) e 100% frontend - iteration_60.json
- Feature: Compartilhar Ranking da Cidade nas Redes Sociais
  - Share Card via Canvas API (9:16 / 1080x1920) com top 10 atletas, cidade, estado, modalidade e gênero
  - Modal com WhatsApp, Facebook, Twitter/X, Copiar Link e Download para Instagram
  - Botão só aparece quando há ranking carregado
  - Testado: 100% frontend (12/12) - iteration_61.json
- Bug Fix: Distinção entre Profissional/Amador e Galera no Ranking por Cidade
  - Backend: Exclusão cruzada entre ranking_anual e ranking_povao (profissional tem prioridade)
  - Galera exclui IDs de ranking_anual; Profissional fallback exclui IDs de ranking_povao
  - Frontend: Corrigido ano de 2026 para 2025 (dados existentes)
  - Testado: 100% (10/10) em 6 cidades sem overlap - iteration_62.json
- Bug Fix: Conexão Strava - redirect_uri atualizado para assessoria-ranking.preview.emergentagent.com
- Bug Fix: Dados inconsistentes no Ranking (6 atletas com pontos inflados em ranking_anual e 5 em ranking_povao)
  - Auditoria e sincronização de 301 entradas no ranking_anual e 122 no ranking_povao
- Feature: Endpoint admin para recalcular/sincronizar rankings automaticamente
  - POST /api/admin/recalcular-rankings - Recalcula pontos e corridas de TODOS atletas a partir da coleção corridas
  - Atualiza usuarios, ranking_anual e ranking_povao automaticamente
  - Retorna relatório detalhado de divergências corrigidas
  - Botão no painel Admin > Monitoramento > "Sincronizar Rankings"
  - Testado via API: 391 atletas verificados, 33 rankings galera recalculados
- Atualização de datas: Todas as 944 corridas migradas para Jan/Fev/Mar 2026 (distribuição: 312/309/323)
  - ranking_anual (301) e ranking_povao (122) atualizados de ano 2025 → 2026
  - resultados_pendentes (29) atualizados
  - Código backend: 22 substituições de ano hardcoded 2025 → ANO_ATUAL dinâmico em 7 arquivos
  - Código frontend: RankingPage.js e RankingCidadePage.jsx agora usam new Date().getFullYear()
  - Zero referências a 2025 em código e banco de dados
  - Frontend: 10+ arquivos atualizados (RankingPage, CadastroPage, SubmeterResultado, RegrasPage, AdminDashboard, etc.)
  - Backend: configuracoes_routes.py, admin_routes.py, auth_routes.py, ranking_routes.py, services/__init__.py
  - Zero ocorrências de "Povão" ou "Pace Livre" em textos visíveis ao usuário

## Backlog (P2 - Refatoração)
- [ ] Refatoração RankingPage.js (~2.200 linhas) - componentização
- [ ] Refatoração AdminDashboard.jsx (~3.900 linhas) - componentização  
- [ ] Refatoração RaioXPage.jsx (~2.300 linhas) - extrair Canvas para utilitários

## Known Technical Notes
- Canvas: NÃO usar ctx.ellipse() ou ctx.roundRect() (quebra no ambiente do usuário)
- Redis: Pode cair. Reinstalar com: sudo apt-get install --reinstall libjemalloc2 liblzf1 redis-tools redis-server
- Campo "distancia" no MongoDB é inconsistente (int 10, str "10KM", str "10km") - backend trata com .upper().replace("KM","")
- ObjectId do MongoDB: sempre excluir _id nas queries

## Key Files
- /app/backend/routes/ranking_routes.py
- /app/backend/routes/raio_x_routes.py
- /app/backend/routes/badges_routes.py
- /app/frontend/src/pages/RaioXPage.jsx
- /app/frontend/src/pages/RankingPage.js
- /app/frontend/src/pages/RankingCidadePage.jsx

## Credentials
- Admin: admin@runpro.com / admin
- Atleta: teste.dono@teste.com / 123456
