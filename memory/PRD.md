# Ranking Run Pró - PRD (Product Requirements Document)

## Visão Geral
Plataforma completa de ranking de corrida com sistema de ranking duplo (Nacional e Estadual), filtráveis por categoria e faixa etária.

---

## Status: IMPLEMENTADO ✅

### 1. Sistema de Ranking ✅
- Rankings Nacionais e Estaduais
- Filtros por categoria: Masculino, Feminino, PCD M/F, Cadeirante M/F
- **Novos filtros**: Faixa Etária, Equipe, Cidade
- Sistema de pontuação:
  - Normal: 1º-10º lugar (10 a 1 ponto)
  - PCD/Cadeirante: 1º-3º lugar (10 a 8 pontos)
- Selo "P" para atletas com menos de 12 provas (8 para PCD/Cadeirante)
- Badge "Elite" para atletas com 100+ pontos

### 2. Autenticação e Perfis ✅
- Cadastro e login para atletas e administradores
- JWT para autenticação
- Roles: `atleta` e `admin`
- **Nome do atleta visível** no header quando logado

### 3. Painel do Atleta ✅
- **Campos editáveis**: Nome, Cidade, UF, Data de Nascimento, Equipe, Redes Sociais, Bio
- **Upload de foto de perfil (CORRIGIDO)**: Foto visível após upload com timestamp para forçar reload
- Visualização de estatísticas (pontos, corridas)
- **Exportar Meus Dados** (download Excel do histórico)
- **Acesso Rápido**: Botões Strava, WhatsApp, TikTok, YouTube
- **Compartilhamento**: WhatsApp e Instagram
- Sistema de Conquistas (Campeão, Pódio, Veterano, Elite, etc.)
- Sistema de Notificações (sininho com badge)
- **Mensagem "Ação Concluída"**: Toast de sucesso em todas as alterações

### 4. Painel de Administração ✅
- **Dashboard** com estatísticas e gráficos:
  - Total de atletas, pendentes, corridas, selo "P"
  - Gráficos de distribuição por estado/categoria/gênero/faixa etária
  - Gráfico de corridas por mês
- **Aba Aprovações**: 
  - Aprovar/Reprovar resultados submetidos
  - **Visualizar foto do pódio** enviada pelo atleta
  - **Botão excluir foto** do pódio
  - Fotos auto-excluídas em 24h após aprovação/reprovação
- **Aba Atletas** (ATUALIZADA):
  - **Barra de pesquisa** por nome, equipe ou cidade
  - **Ordenação A-Z** (crescente)
  - Filtros: Todos, Atletas M/F, PCD M/F, Cadeirante M/F
  - Botão "+ Adicionar" para cadastrar atletas
  - Botão "Exportar Dados" (Excel) - **CORRIGIDO**
  - Cards de atletas com Ver/Editar/Excluir
  - Modal de edição completo
- **Aba + Submeter Resultado** (REFORMULADA):
  - Selecionar atleta (dropdown ordenado A-Z)
  - Tipo de operação: Adicionar Pontos / Remover Pontos
  - **Adicionar Pontos**: Formulário completo igual ao atleta:
    - Nome da Competição, Colocação, Distância, Cidade, Estado UF, Data, Tempo, Link
  - **Remover Pontos**: Lista corridas anteriores do atleta para editar ou excluir
- **Aba Gráficos**: Visualizações detalhadas
- **Aba Ranking** (CORRIGIDO de "Rankings"):
  - **Exportação de TODAS as modalidades** em um único arquivo
  - Masculino, Feminino, PCD M/F, Cadeirante M/F
  - Exportar CSV e Excel
- **Mensagem "Ação Concluída"**: Toast de sucesso em todas as alterações/exclusões

### 5. Submissão de Resultados (Atleta) ✅
- **Botão "Adicionar uma Foto do Pódio ou sua no Evento"** (melhorado)
- Formatos aceitos: JPG, PNG, GIF (máx 5MB)
- Prazo de 6 dias úteis após o evento
- Validação de colocações por categoria

### 6. Compartilhamento Avançado (Estilo Strava) ✅
- Página de detalhes do atleta com botão "Compartilhar"
- Modal de compartilhamento com:
  - Preview da imagem (formato 9:16 para Stories)
  - Botões: WhatsApp, Instagram, Facebook, Baixar
  - Copiar Link

### 7. Sistema de Notificações ✅
- Notificações automáticas para:
  - Resultado aprovado
  - Resultado reprovado (com motivo)
  - Conquistas desbloqueadas
  - Ajustes de pontos pelo admin
- Sininho no header com badge de não lidas
- Dropdown com lista de notificações

### 8. Sistema de Conquistas ✅
- Campeão (1º lugar em corrida)
- Pódio (top 3 em corrida)
- Veterano (10 corridas)
- Elite (100+ pontos)
- Maratonista (completou 42KM)
- Consistente (corridas em 6+ meses)

---

## Arquitetura Técnica

### Backend (FastAPI)
- `/app/backend/server.py` - API principal
- `/app/backend/models/__init__.py` - Modelos Pydantic
- `/app/backend/services/__init__.py` - Serviços e helpers
- MongoDB para persistência
- JWT para autenticação
- Endpoints principais:
  - `/api/auth/*` - Autenticação
  - `/api/ranking/*` - Rankings e exportação
  - `/api/atletas/*` - Perfis de atletas
  - `/api/admin/*` - Endpoints administrativos
  - `/api/admin/adicionar-corrida` - Admin adiciona corrida
  - `/api/admin/corridas/{id}` - Admin edita/exclui corrida
  - `/api/admin/pendentes/{id}/foto` - Admin exclui foto
  - `/api/notificacoes/*` - Sistema de notificações
  - `/api/conquistas/*` - Sistema de conquistas

### Frontend (React)
- `/app/frontend/src/pages/` - Páginas da aplicação
- `/app/frontend/src/components/` - Componentes reutilizáveis
- Componentes shadcn/ui
- Recharts para gráficos
- html2canvas para gerar imagens de compartilhamento
- React Router para navegação
- **Sonner** para toasts ("Ação Concluída")

---

## Credenciais de Teste
- **Admin**: admin@runpro.com / admin123
- **Atleta**: gabrielsouza_normal_1@email.com / atleta123

---

## Dados de Teste
- 94 atletas (15 por categoria)
- Aproximadamente 971 corridas
- Distribuição uniforme por estados e faixas etárias

## Novas Funcionalidades (02/03/2026)
25. ✅ **Ranking do Povão - Pace Livre** - Nova modalidade de ranking:
    - **Cadastro**: Campo obrigatório para escolher modalidade (Profissional/Amador vs Povão)
    - **Pontuação por distância**: 5-9km = 5pts, 10-20km = 7pts, 21km+ = 9pts
    - **Ranking isolado**: Completamente separado do ranking Profissional/Amador
    - **Filtros**: Apenas Masculino e Feminino (PCD/Cadeirante não podem participar)
    - **View dedicada**: Cards de estatísticas, explicação do sistema de pontos
    - **Submissão adaptada**: Formulário sem campos de colocação/tempo para atletas Povão
    - **Admin**: Filtro por modalidade na lista de atletas + badge de modalidade nos cards
    - **Endpoints**: `/api/ranking/povao`, `/api/ranking/povao/stats`
    - **Validação**: Backend bloqueia PCD/Cadeirante de selecionar modalidade Povão

## Correções e Melhorias (02/03/2026 - Sessão 2)
26. ✅ **Modal de Foto do Pódio** - Nas aprovações do admin, clique na foto para ampliar em modal
27. ✅ **Ranking Semanal/Mensal Isolados** - Atletas do Povão não aparecem mais no ranking Profissional/Amador
28. ✅ **Novos Gráficos no Dashboard Admin**:
    - Gráfico de pizza: Distribuição por Modalidade (Profissional/Amador vs Povão)
    - Card especial: Ranking do Povão - Estatísticas (total atletas, provas, pontos)
    - Gráfico de barras: Top 10 Equipes / Assessorias
    - Gráfico de barras: Distribuição por Categoria (Normal, PCD, Cadeirante M/F)

## Correções Críticas (02/03/2026 - Sessão 3)
29. ✅ **CRÍTICO: Isolamento Total de Rankings** - Paulo Malheiros e Ravir Luiz (Povão) removidos completamente do ranking Profissional/Amador
    - `calcular_ranking()` modificado para ignorar atletas com `modalidade_usuario='povao_pace_livre'`
    - `get_ranking_por_categoria()` com verificação dupla de segurança
    - Banco de dados recalculado para remover atletas Povão do ranking_anual principal
30. ✅ **Filtros no Ranking do Povão** - Adicionados todos os filtros conforme ranking Profissional:
    - Nome, Colocação, UF, Faixa Etária, Equipe, Cidade
    - Botão "Limpar Filtros" funcionando
    - Layout responsivo com sidebar de filtros

31. ✅ **Transferência de Modalidade (Admin)** - Botão para transferir atletas entre rankings:
    - Botão "↔️" no card de cada atleta NORMAL (não aparece para PCD/Cadeirante)
    - Modal de confirmação com explicação das regras de pontuação
    - **Pro/Amador → Povão**: Recalcula pontos por distância (5-9km=5pts, 10-20km=7pts, 21km+=9pts)
    - **Povão → Pro/Amador**: Recalcula pontos por colocação (1º=10pts, 2º=9pts, etc.)
    - Atleta é removido do ranking antigo e inserido no novo
    - Notificação automática enviada ao atleta
    - Endpoint: POST `/api/admin/atletas/{id}/transferir-modalidade`

## Nova Funcionalidade (03/03/2026)

32. ✅ **Ranking Run Inside** - Sistema completo de análise de perfis Instagram:
    - **Nova aba no Admin**: "Ranking Run Inside" com ícone dedicado
    - **Barra de Pesquisa Inteligente** (03/03/2026):
      - Input para @username com busca automática via Social Blade
      - Botão "Buscar Dados" tenta buscar métricas automaticamente
      - Fallback gracioso: se bloqueado, mostra mensagem e abre formulário manual
      - Link "Ou preencha os dados manualmente" sempre disponível
    - **Formulário de entrada manual**: Administrador insere dados do perfil:
      - Dados básicos: username, nome completo, nicho
      - Métricas: seguidores, seguindo, total de posts
      - Engajamento: média de likes, comentários, views de Reels
      - Frequência: posts por semana, dias desde último post, crescimento 30 dias
      - Análise de Bio: descrição, keywords, CTA, link, **clareza (select: excelente/boa/regular/ruim)**
      - Distribuição de formatos: % Reels, Carrossel, Fotos
      - Indicadores anti-fake: picos anormais, comentários repetitivos, horários artificiais
    - **Motor de cálculo (8 métricas com 0-10)**:
      - Bio (com clareza ponderada), Frequência, Engajamento, Crescimento, Consistência, Padrões (anti-fake), Reels, Formatos
    - **Score Final (0-100)**: Média ponderada das notas (Engajamento 30%, Crescimento/Consistência/Padrões 15%, Reels 10%, outros 5%)
    - **Sistema de Classificação**:
      - Elite Platinum: 95-100
      - Elite Gold: 90-94
      - Premium: 80-89
      - Profissional: 70-79
      - Regular: 60-69
      - Alto Risco: <60
    - **Dashboard Visual com Gráficos (recharts)**:
      - Gráfico Radar: 8 métricas visualizadas
      - Gráfico Gauge/Velocímetro: Score de Influência
      - Gráfico de Barras Horizontal: Notas individuais
      - Gráfico de Pizza: Distribuição de formatos
      - Gráfico de Barras Comparativo: Perfil vs Média do Nicho
    - **Recomendações Personalizadas**: Sistema gera dicas baseadas nas notas
    - **Histórico de Análises**: Lista todas análises salvas com ações ver/excluir
    - **Exportação**:
      - XLSX: Relatório completo em Excel
      - CSV: Dados em formato CSV
    - **Endpoints**:
      - GET `/api/admin/instagram/buscar/{username}` - Busca automática via Social Blade
      - POST `/api/admin/instagram/analisar` - Criar análise
      - GET `/api/admin/instagram/analises` - Listar análises
      - GET `/api/admin/instagram/analises/{id}` - Detalhes com gráficos
      - DELETE `/api/admin/instagram/analises/{id}` - Excluir análise
      - GET `/api/admin/instagram/export/{id}` - Exportar XLSX
      - GET `/api/admin/instagram/export-csv/{id}` - Exportar CSV

---

## Novas Funcionalidades (04/03/2026)
33. ✅ **Melhorias no Formulário de Cadastro**:
    - **Cidade dependente do Estado**: Campo cidade desabilitado até selecionar UF, depois preenchido com cidades via API IBGE
    - **Equipe/Assessoria com autocomplete**: Dropdown com busca, sugestão de equipes existentes e opção "Sem equipe"
    - **Dropdown de Etnia**: 6 opções (Branco, Negro, Pardo, Indígena, Amarelo, Mulato)

34. ✅ **Alterar Senha no Perfil do Atleta**:
    - Seção expansível no perfil do atleta
    - Campos: senha atual, nova senha, confirmação
    - Validações: senha atual correta, mínimo 6 caracteres, confirmação idêntica
    - Endpoint: POST `/api/atletas/alterar-senha`

35. ✅ **Liga Nacional de Assessorias Ranking Run - Fase 1**:
    - **Nova aba no Admin**: "Assessorias/Equipes" com dashboard completo
    - **Sistema de Pontuação ROE-RR**:
      - +0,5 por atleta cadastrado e vinculado
      - +1,0 por resultado aprovado
      - +0,5 adicional para 2º-5º lugar
      - +1,0 adicional para 1º lugar
    - **Estatísticas**: Total assessorias, atletas vinculados, resultados, estados ativos
    - **6 Tipos de Ranking**: Nacional, Estadual, Cidade, Mensal, Anual, Histórico
    - **Sistema de Selos**: Ouro (Top 20), Prata (21-50), Bronze (51+)
    - **Tabela de Ranking**: Posição, Selo, Assessoria, UF, Cidade, Atletas, 1º lugares, Resultados, Pontos
    - **Modal de Detalhes**: Estatísticas, lista de atletas, gráfico de evolução mensal
    - **Endpoints**:
      - GET `/api/liga-assessorias/stats`
      - GET `/api/liga-assessorias/ranking?tipo=nacional`
      - GET `/api/liga-assessorias/assessoria/{nome}`
      - GET `/api/liga-assessorias/estados`
      - GET `/api/liga-assessorias/cidades`

36. ✅ **Liga Nacional de Assessorias - Bloco A (Melhorias)**:
    - **Liga movida para página pública**: 3ª aba "Ranking de Equipes" no seletor principal
    - **Filtro de Cidade**: Ao selecionar "Por Cidade", aparece dropdown de Estado e depois Cidade
    - **Endpoints públicos**: Todos os endpoints da Liga agora são acessíveis sem autenticação
    - **Botão "Promover a Dono de Assessoria"**: No Admin, atletas com equipe têm botão amarelo para promoção
    - **Modal de confirmação**: Ao clicar em promover, abre modal com detalhes e confirmação
    - **Endpoint de promoção**: POST `/api/admin/atletas/{id}/promover-dono-assessoria`

37. ✅ **Liga Nacional de Assessorias - Bloco B (Fases 2, 3, 4)**:
    - **Fase 2 - Rankings por Período**:
      - 3 abas visuais: Mensal, Anual, Histórico
      - Critérios de desempate oficiais: 1º lugares → atletas → resultados → data cadastro
    - **Fase 3 - Página Pública da Assessoria** (`/assessoria/{nome}`):
      - Stats: posição, atletas, resultados, pontos
      - Conquistas: primeiros lugares, pódios
      - Lista de atletas com avatares (clicável para perfil)
      - Selo Digital Oficial com botão "Baixar Selo Oficial"
      - Botão "Quero Treinar com Essa Assessoria"
    - **Fase 4 - Painel do Dono de Assessoria** (`/minha-assessoria`):
      - Dashboard exclusivo com métricas da equipe
      - Rankings: Nacional, Estadual, Mensal, Anual
      - Lista de atletas com exportação CSV
      - Sistema de mensagens para atletas
      - Download de selo oficial
      - Botão "Minha Assessoria" no header (usuários com role dono_assessoria)

38. ✅ **Dados de Teste Atualizados**:
    - 160 atletas criados (12 assessorias)
    - Profissional/Amador: 20 M, 20 F, 20 PCD-M, 20 PCD-F, 20 Cad-M, 20 Cad-F
    - Povão: 20 M, 20 F
    - 515 corridas de teste geradas
    - Todos os atletas com dados completos (bio, Facebook, Instagram)

39. ✅ **Ranking das Corridas - Fase 1 (Base)**:
    - **Nova página** `/ranking-corridas` com sistema de avaliação de eventos
    - **4ª aba** no seletor principal da página inicial
    - **Estrutura de banco**: Coleções `corridas_eventos` e `avaliacoes_corridas`
    - **CRUD de Corridas**: Admin e Dono de Assessoria podem cadastrar
    - **Campos**: Nome, Organizador, Cidade, Estado, Data, Link, Status
    - **Filtros**: Nacional, Estadual, Cidade, Mensal, Anual, Histórico
    - **Stats Cards**: Total corridas, avaliações, média geral, melhor avaliada
    - **Legenda de estrelas**: 1-5 (Péssima a Excelente)
    - **Algoritmo Média Bayesiana** preparado (m=30, min 10 aval. para ranking)
    - **Endpoints**:
      - POST/GET/PUT/DELETE `/api/corridas-eventos`
      - GET `/api/ranking-corridas`
      - GET `/api/ranking-corridas/stats`
      - GET `/api/ranking-corridas/estados`
      - GET `/api/ranking-corridas/cidades`

40. ✅ **Ranking das Corridas - Fase 2 (Sistema de Avaliação)** (08/03/2026):
    - **Modal de Avaliação**: Interface completa para avaliar corridas
    - **5 Critérios IQC**: Organização, Percurso, Kit Atleta, Hidratação, Pós-Prova
    - **Estrelas Interativas**: Clique para selecionar nota 1-5 com hover effect
    - **Cálculo em Tempo Real**: Nota final calculada automaticamente
    - **Checkbox Obrigatório**: "Confirmo que participei desta corrida"
    - **Validações Backend**:
      - Apenas 1 avaliação por atleta/corrida
      - Avaliação somente após data da corrida
      - Todas as notas devem ser entre 1 e 5
    - **Botão "Avaliar"**: Em cada linha da tabela de ranking
    - **Endpoints**:
      - POST `/api/avaliar-corrida` - Enviar avaliação (5 critérios + participei)
      - GET `/api/verificar-avaliacao/{corrida_id}` - Verificar se já avaliou
      - GET `/api/minhas-avaliacoes-corridas` - Minhas avaliações

41. ✅ **Ranking das Corridas - Fase 3 (Sistema de Selos)** (08/03/2026):
    - **3 Tipos de Selos Automáticos**:
      - ⭐ **Selo 5 Estrelas**: Média ≥ 4.5 E mínimo 50 avaliações
      - 🏆 **Top 10 Brasil**: 10 melhores no ranking nacional (min 10 aval.)
      - 📍 **Top 10 Estado**: 10 melhores por estado
    - **Exibição no Ranking Público**: Badges exibidos ao lado do nome da corrida
    - **Lógica no Backend**: Cálculo automático baseado em média e quantidade

42. ✅ **Ranking das Corridas - Fase 4 (Dashboard Admin)** (08/03/2026):
    - **Nova aba "Ranking Corridas"** no menu lateral do Admin Dashboard
    - **Stats Cards**: Total Corridas, Total Avaliações, Média Geral, Melhor Avaliada
    - **Gráfico de Distribuição de Notas**: Bar chart com recharts
    - **Top 10 - Melhores Corridas**: Lista ordenada por pontuação
    - **Melhores Corridas por Estado**: Grid com badge e média
    - **Sistema de Selos - Certificações**: 3 tipos de selo com contadores
    - **Tabela de Gerenciamento**: CRUD completo de corridas
      - Colunas: Corrida, Organizador, Local, Avaliações, Média, Status, Ações
      - Botões: Editar (abre modal), Excluir (com confirmação)
    - **Modal Cadastrar/Editar**: Todos os campos da corrida
    - **Endpoints Admin**:
      - GET `/api/admin/ranking-corridas/dashboard`
      - PUT `/api/corridas-eventos/{id}`
      - DELETE `/api/corridas-eventos/{id}`

## Próximos Passos - Ranking das Corridas
**TODAS AS FASES CONCLUÍDAS!** ✅
- Fase 1: Estrutura base (página, filtros, tabela)
- Fase 2: Sistema de avaliação (modal 5 critérios IQC)
- Fase 3: Selos automáticos (5 Estrelas, Top 10)
- Fase 4: Dashboard Admin (gráficos, CRUD)

## Backlog / Melhorias Futuras
- **Painel do Dono de Assessoria**: Métricas detalhadas, gestão de atletas
- **Selo "Atleta Avaliador"**: Badge para atletas que avaliarem 5+ corridas
- **Notificações por E-mail**: Resend/SendGrid
- **Ranking histórico por ano**: Filtro de períodos anteriores
- **Integração com Strava API**: Importação automática de resultados
- **Proteções anti-fraude**: Detecção de padrões suspeitos de avaliação

## Backlog Geral
1. **P1**: Implementação de notificações por e-mail (Resend/SendGrid)
2. **P2**: Ranking histórico por ano (filtro por temporada)
3. **P2**: Ranking Run Inside - Exportação PDF com visual do dashboard
4. Melhorias de performance (cache)
5. Integração real com Strava API
6. **Roadmap Run Inside (Futuro)**:
   - Machine Learning para análise preditiva
   - API pública para marcas consultarem scores
   - Selo digital verificável para influenciadores certificados

---

Última atualização: 08/03/2026
1. ✅ Botão "Exportar Dados" na aba Atletas - funcional com download de Excel
2. ✅ Mensagem "Ação Concluída" em todas as alterações (toast.success)
3. ✅ Upload de foto de perfil do atleta - corrigido com timestamp para forçar reload
4. ✅ Botão "Adicionar uma Foto do Pódio ou sua no Evento" na submissão
5. ✅ Visualização da foto do pódio na aba Aprovações + botão excluir
6. ✅ Barra de pesquisa na aba Atletas (nome, equipe, cidade)
7. ✅ Ordenação de atletas A-Z (crescente)
8. ✅ Reformulação da aba "+ Submeter Resultado" (formulário completo)
9. ✅ Correção de "Rankings" para "Ranking" no menu
10. ✅ Exportação de ranking com TODAS as modalidades

## Novas Funcionalidades (25/02/2026)
11. ✅ **Ranking Semanal** - Top 10 atletas da última semana
12. ✅ **Ranking Mensal** - Top 10 atletas do mês atual
13. ✅ **Destaque do Mês** - Card com estatísticas:
    - Total de corridas no mês
    - Atletas no pódio
    - Atleta mais ativo (mais corridas)
    - Atleta com mais pontos
14. ✅ **Botão "Ver/Ocultar Destaques"** - Toggle na sidebar de filtros
15. ✅ **Medalhas visuais** - Ouro, prata e bronze nos rankings

## Novas Funcionalidades (25/02/2026 - Sessão 2)
16. ✅ **Campo Etnia** - No cadastro e perfil (Branco, Negro, Indígena, Pardo, Amarelo)
17. ✅ **Campo Apelido** - No cadastro e perfil
18. ✅ **"Bio do Atleta"** - Substituiu "Sobre Você" com limite de 150 caracteres
19. ✅ **Instagram + Apelido** - Exibido na página de detalhes do atleta (ícone + @apelido)
20. ✅ **Facebook + Primeiro Nome** - Exibido na página de detalhes do atleta (ícone + nome)
21. ✅ **Bio visível** - Exibida na página de detalhes do atleta entre aspas
22. ✅ **Aba Aniversariantes** - Nova aba no painel do admin com:
    - Calendário interativo do mês
    - Navegação entre meses
    - Destaque rosa para dias com aniversários
    - Avatares dos atletas nos dias
    - Painel lateral com lista de aniversariantes do dia
    - Campo de mensagem de felicitação editável
    - Botão "Enviar para X atleta(s)"
    - Botão "Selecionar Todos"
23. ✅ **Popup de Aniversário** - Exibido ao atleta quando recebe mensagem:
    - Design moderno com gradiente rosa/roxo
    - Ícone de bolo animado
    - Mensagem personalizada
    - Botão "Obrigado!" para fechar
    - Não aparece novamente após visualização
24. ✅ **Envio Automático de Aniversário** - Sistema automatizado:
    - Scheduler usando APScheduler
    - Executa às 00:00 todos os dias
    - Verifica aniversariantes do dia automaticamente
    - Envia mensagem padrão configurável
    - Cada atleta recebe apenas 1 mensagem por ano
    - Toggle para ativar/desativar via modal de configuração
    - Botão "Enviar Agora (Hoje)" para envio manual
    - Logs de execução do scheduler

---

Última atualização: 08/03/2026

## Correções e Melhorias (08/03/2026)

43. ✅ **Bug Fix - Perfil do Atleta** (08/03/2026):
    - Corrigido erro "Página não encontrada" ao clicar no perfil de um atleta
    - Problema: KeyError 'faixa_etaria' no endpoint GET /api/atletas/{id}
    - Solução: Campos obrigatórios agora usam .get() com valores default
    - Também corrigido endpoint GET /api/atletas/{id}/corridas

44. ✅ **Termo de Aceite no Cadastro** (08/03/2026):
    - Modal com regulamento completo da plataforma
    - Usuário deve rolar até o final para habilitar botão "EU CONCORDO"
    - Checkbox "Li e concordo com o Regulamento da Plataforma"
    - Botão "Cadastrar" desabilitado até aceitar o termo
    - 10 seções do regulamento: Disposições Gerais, Cadastro, Modalidades, Pontuação, Submissão de Resultados, Equipes, Avaliação de Corridas, Privacidade, Condutas Proibidas, Disposições Finais

45. ✅ **Campo Equipe/Assessoria com Dropdown** (08/03/2026):
    - Novo endpoint: GET /api/assessorias/lista (retorna [{nome, cidade, estado}])
    - Dropdown mostra APENAS equipes cadastradas + opção "INDIVIDUAL"
    - Opção "INDIVIDUAL" em destaque no topo com badge "Sem equipe"
    - Assessorias exibem Nome na primeira linha e Cidade/UF na segunda
    - Atleta NÃO pode escrever livremente - deve selecionar do dropdown
    - Alerta amarelo aparece ao selecionar "INDIVIDUAL" com mensagem:
      "Não encontrou sua equipe? É normal! Fale com o Dono(a) da sua Assessoria/Equipe para fazer o cadastro. Assim que ele(a) fizer, você já poderá alterar no seu Perfil."

46. ✅ **Fluxo Dono de Assessoria no Cadastro** (08/03/2026):
    - Seção em **laranja claro** "Você é Dono de Uma Assessoria/Equipe?" aparece quando INDIVIDUAL selecionado
    - Botões SIM/NÃO com tooltip explicativo
    - Se SIM, aparecem campos:
      - Nome da Assessoria/Equipe *
      - Estado (UF) * (dropdown)
      - Cidade * (dropdown carregado via IBGE)
      - Foto da Equipe/Assessoria (opcional, upload)
      - Mensagem da BIO * (textarea, max 200 caracteres)
    - Se NÃO, campos ficam ocultos
    - Backend: POST /api/auth/register com is_dono_assessoria=true
      - Cria assessoria na coleção `assessorias`
      - Define role como "dono_assessoria"
      - Define equipe como nome da assessoria
    - Validação: não permite nome de assessoria duplicado

47. ✅ **Responsável e BIO na Página de Equipes** (08/03/2026):
    - Página /assessoria/{nome} agora exibe no header:
      - ⚡️ **Responsável / Nome do Dono** (texto verde/emerald com ícone Zap)
      - 📊 *"Mensagem da BIO"* (texto azul itálico com ícone BarChart3)
    - Backend: GET /api/liga-assessorias/assessoria/{nome} retorna:
      - responsavel_nome, responsavel_id, mensagem_bio, foto_assessoria
    - Busca dados da coleção `assessorias` e do usuário `dono_assessoria`
    - Endpoint admin: POST /api/admin/setup-assessoria-dono/{equipe_nome}
      - Configura atleta existente como dono e cria dados da assessoria

48. ✅ **Sincronização de Atletas entre Modalidades** (08/03/2026):
    - Corrigido bug: atletas agora aparecem corretamente nas 3 modalidades
    - **Ranking Povão**: 40 atletas (20M + 20F), 482 provas registradas
    - **Ranking Profissional/Amador**: 33 atletas
    - **Ranking Equipes**: 16 assessorias (Victory Run PE em 1º com 189.5 pts)
    - Sistema de pontuação verificado:
      - Equipes: Atleta=+0.5, Resultado=+1.0, 2º-5º=+0.5, 1º=+1.0
      - Povão: 5km-9km=5pts, 10km-20km=7pts, 21km+=9pts
      - Profissional: 1º=10pts até 10º=1pt
    - Novo endpoint: POST /api/admin/recalcular-rankings
    - Corrigido KeyError 'faixa_etaria' em múltiplos endpoints


49. ✅ **Novos Filtros no Ranking de Equipes (6ª Tarefa)** (08/03/2026):
    - **Novas abas**: Nacional, Estadual, Cidade, Histórico
    - **Abas removidas**: Mensal, Anual (substituídas pelo dropdown de mês)
    - **Dropdown de Mês**: Filtro por mês específico (Janeiro a mês atual)
    - **Aba Nacional**: Ranking nacional com filtro de mês
    - **Aba Estadual**: Dropdown de Estado + filtro de mês
    - **Aba Cidade**: Dropdowns de Estado e Cidade + filtro de mês
    - **Aba Histórico**: Sem filtro de mês (mostra todos os dados históricos)
    - **Backend**: Endpoint GET /api/liga-assessorias/ranking aceita parâmetro mes=1-12
    - **Frontend**: Componente getMesesDisponiveis() filtra meses até o atual

---

## Próximas Tarefas (P0-P2)

### P0 - Reestruturação do Dashboard Admin
- Dividir AdminDashboard.jsx em dashboards especializados:
  - DashboardGeral, DashboardAtletas, DashboardAssessorias, DashboardCorridas, DashboardResultados

### P1 - Tarefas 7-10
- **7ª Tarefa**: Permitir atleta mudar de equipe a cada 15 dias
- **8ª Tarefa**: Melhorias na página de detalhes da assessoria
- **9ª Tarefa**: Dashboard "Minha Assessoria" para donos
- **10ª Tarefa**: Botão "REGULAMENTO" nas páginas de ranking

### P2 - Tarefas 11-13
- **11ª Tarefa**: Sistema de selos/medalhas de conquista
- **12ª Tarefa**: Aprimorar sistema de avaliação de corridas
- **13ª Tarefa**: Sistema de reputação para avaliadores

### Backlog
- Seção "Autorizações" no Admin (gerenciar acesso pós-teste 30 dias)

---

## Changelog - 08/03/2026

### ✅ Reestruturação do Dashboard Admin (P0)
Dividido o AdminDashboard monolítico em componentes modulares:
- `/app/frontend/src/pages/admin/DashboardGeral.jsx` - Estatísticas gerais da plataforma
- `/app/frontend/src/pages/admin/DashboardAtletas.jsx` - Gestão de atletas
- `/app/frontend/src/pages/admin/DashboardAssessorias.jsx` - Ranking das assessorias
- `/app/frontend/src/pages/admin/DashboardCorridas.jsx` - Gestão de corridas/eventos
- `/app/frontend/src/pages/admin/DashboardResultados.jsx` - Aprovações pendentes

**Menu reorganizado:**
1. Dashboard Geral - KPIs, gráficos de modalidade/categoria/estados
2. Atletas - Lista completa com filtros e ações
3. Assessorias - Ranking ROE-RR com gráficos
4. Corridas - Gestão de eventos e avaliações
5. Aprovações - Resultados pendentes
6. + Submeter Resultado - Formulário de submissão
7. Exportar Ranking - Relatórios PDF
8. Aniversariantes - Calendário e notificações
9. Ranking Run Inside - Analytics Instagram

### ✅ Gráfico de Evolução Mensal das Equipes
- Endpoint: `GET /api/liga-assessorias/evolucao-mensal?top=5`
- Exibido na página de Ranking de Equipes
- LineChart com cores distintas para cada equipe
- Mostra evolução de pontos de Janeiro até o mês atual

### ✅ Dashboard de Comparação Mensal para Donos de Assessoria
- Página `/minha-assessoria` (DonoAssessoriaDashboard.jsx)
- Endpoint: `GET /api/liga-assessorias/comparacao-mensal/{nome_equipe}`
- Comparação Março vs Fevereiro 2026:
  - Resultados (quantidade e variação %)
  - Pontos conquistados (quantidade e variação %)
  - Novos atletas (quantidade e variação %)
  - Posição no ranking (posição e variação)
- Mensagem automática de performance (parabéns ou alerta)

### ✅ 7ª Tarefa - Troca de Equipe a Cada 15 Dias
- Endpoint: `GET /api/atletas/status-troca-equipe`
- Endpoint: `POST /api/atletas/trocar-equipe`
- Regras implementadas:
  - Atletas podem trocar de equipe a cada 15 dias
  - Donos de assessoria NÃO podem trocar (bloqueado)
  - Administradores não têm equipe
  - Período de cooldown com contagem de dias restantes
  - Validação de equipe existente ou INDIVIDUAL
- UI no perfil do atleta:
  - Botão "Trocar Equipe"
  - Modal de seleção de nova equipe
  - Mensagem de bloqueio com data da próxima troca

### ✅ 8ª Tarefa - Melhorias na Página de Detalhes da Assessoria
- **AssessoriaPage.jsx** completamente redesenhado:
  - Header com gradiente laranja/âmbar
  - Informações do responsável com ícone de coroa e link clicável
  - Bio/mensagem da assessoria exibida em destaque
  - Posição no Ranking Nacional em destaque
- Cards de estatísticas com ícones coloridos:
  - Ranking Estadual, Atletas Ativos, Resultados Aprovados, Pontos ROE-RR
- Seção "Conquistas e Destaques" com emojis (🥇 🏅 👥 ✅)
- **Botões implementados:**
  - "Ver Perfil Completo" - navega para `/atleta/{responsavel_id}`
  - "Ver Perfil do Responsável" - navega para `/atleta/{responsavel_id}`
  - "Baixar Selo Oficial" - download do selo em PNG
  - "Compartilhar" - abre dialog de compartilhamento ou copia URL
  - "Voltar ao Ranking" - navega para a home
- Card do responsável com avatar e informações
- Sistema de Pontuação ROE-RR na barra lateral

### ✅ Galeria de Fotos de Pódio (Enhancement)
- Seção "Galeria de Pódios" na página de detalhes da assessoria
- Grid responsivo de fotos (2x2 mobile, 3x3 tablet, 4x4 desktop)
- Hover effect com informações do atleta, competição e colocação
- Badge de posição (1º=ouro, 2º=prata, 3º=bronze)
- Modal de visualização em tela cheia ao clicar
- Limite de 12 fotos mais recentes
- Backend: campo `fotos_podio` adicionado ao endpoint `/liga-assessorias/assessoria/{nome}`

---

## 🐛 Bug Fix - Login de Usuários Não-Admin (09/03/2026 - Sessão 6)

### Problema Identificado
- Usuários (atletas e donos de assessoria) não conseguiam fazer login
- O login funcionava via API, mas a UI não mostrava o usuário logado
- Erro: `KeyError: 'foto_url'` no endpoint `/api/auth/me`

### Causa Raiz
1. **Senhas não hasheadas**: Os usuários de teste não tinham senhas salvas no banco
2. **Campo foto_url ausente**: O endpoint `/api/auth/me` usava `current_user["foto_url"]` diretamente, mas alguns usuários não tinham esse campo

### Correções Aplicadas
1. Senhas hasheadas (`senha123`) adicionadas aos usuários de teste no banco
2. Endpoint `/api/auth/me` corrigido para usar `.get()` com valores padrão:
   ```python
   "categoria": current_user.get("categoria", "normal"),
   "foto_url": current_user.get("foto_url", ""),
   "equipe": current_user.get("equipe", ""),
   "estado": current_user.get("estado", ""),
   ```

### Status
- ✅ Login funcionando para Admin, Atleta e Dono de Assessoria
- ✅ Token salvo no localStorage
- ✅ Nome do usuário exibido no header
- ✅ Botões específicos por role (ex: "Minha Assessoria" apenas para dono_assessoria)

---

## ✅ 9ª Tarefa - Relatórios Detalhados para Donos de Assessoria (09/03/2026)

### Nova Aba "Relatórios" no Dashboard Minha Assessoria

**Endpoint Backend:**
- `GET /api/dono-assessoria/relatorios/{nome_equipe}` - Retorna todos os dados agregados

**Visualizações Implementadas:**

1. **Indicadores Principais** (5 cards coloridos):
   - Atletas Ativos
   - Total Resultados
   - Pontos Totais
   - 1º Lugares
   - Pódios

2. **Indicadores Percentuais** (4 cards com ícones):
   - Média Pontos/Atleta
   - Média Corridas/Atleta
   - Taxa de Pódio (%)
   - Taxa de Vitória (%)

3. **Gráfico de Linha** - Evolução Mensal:
   - Eixo duplo: Resultados (esquerda) e Pontos (direita)
   - Últimos 6 meses

4. **Gráfico de Barras Horizontal** - Distribuição por Faixa Etária

5. **Gráfico de Pizza (Donut)** - Distribuição por Gênero:
   - Masculino vs Feminino com percentuais

6. **Gráfico de Pizza** - Distribuição por Categoria:
   - Normal, PCD, Cadeirante

7. **Gráfico Radar** - Performance Geral:
   - 6 métricas normalizadas (0-100)

8. **Mapa Geográfico do Brasil**:
   - Estados coloridos por quantidade de atletas
   - Legenda com escala de cores
   - Badges com contagem por UF

9. **Rankings Dinâmicos** - Top 10 Atletas:
   - Posição com medalhas (ouro/prata/bronze)
   - Pontos e corridas

10. **Treemap** - Distribuição de Colocações:
    - 1º, 2º, 3º, 4º-5º, 6º-10º, Outros

11. **Gráfico de Área** - Evolução de Novos Atletas:
    - Cadastros por mês

**Tecnologias:**
- recharts (LineChart, BarChart, PieChart, RadarChart, AreaChart, Treemap)
- react-simple-maps (Mapa do Brasil)
- d3-scale, d3-geo

**Arquivos Criados/Modificados:**
- `/app/frontend/src/components/RelatoriosAssessoria.jsx` (NOVO)
- `/app/frontend/src/pages/DonoAssessoriaDashboard.jsx` (MODIFICADO)
- `/app/backend/server.py` (NOVO endpoint)

---

## ✅ 10ª Tarefa - Botão "REGULAMENTO" (09/03/2026)

### Implementação Completa

**1. Modal de Visualização do Regulamento**
- Componente: `/app/frontend/src/components/RegulamentoModal.jsx`
- Exibição em modal estilo "Como funciona?"
- Formatação Markdown renderizada (títulos, listas, negrito, etc.)
- Mostra data de atualização e quem atualizou

**2. Seção de Gerenciamento no Admin**
- Menu: "Regulamento" na sidebar do Admin Dashboard
- Interface com:
  - Dicas de formatação Markdown
  - Campo de título
  - Textarea para conteúdo
  - Pré-visualização em tempo real
  - Botões "Recarregar" e "Salvar Regulamento"

**3. Botão nas Páginas de Ranking**
- ✅ RankingPage.js (Ranking Principal) - ao lado do "Como funciona?"
- ✅ RankingCorridasPage.jsx (Ranking das Corridas) - no header

**4. Endpoints Backend**
- `GET /api/regulamento` - Público, retorna regulamento para visualização
- `GET /api/admin/regulamento` - Admin, retorna para edição
- `PUT /api/admin/regulamento` - Admin, salva alterações

**5. Armazenamento**
- Collection: `configuracoes` (MongoDB)
- Documento com `tipo: "regulamento"`, `titulo`, `conteudo`, `ultima_atualizacao`, `atualizado_por`

**Arquivos Criados/Modificados:**
- `/app/frontend/src/components/RegulamentoModal.jsx` (NOVO)
- `/app/frontend/src/pages/RankingPage.js` (MODIFICADO)
- `/app/frontend/src/pages/RankingCorridasPage.jsx` (MODIFICADO)
- `/app/frontend/src/pages/AdminDashboard.jsx` (MODIFICADO - nova seção)
- `/app/backend/server.py` (NOVO endpoints)

---

## ✅ Seção "Autorizações" - Sistema de Gerenciamento de Acesso (09/03/2026)

### Funcionalidades Implementadas

**1. Novo Sistema de Período de Teste**
- Atletas têm 30 dias de acesso gratuito após o cadastro
- Após esse período, precisam de autorização do admin para continuar
- O lançamento de resultados verifica: período de teste OU autorização ativa

**2. Seção "Autorizações" no Admin Dashboard**
- **Cards de estatísticas:** Em Teste, Autorizados, Expirados, Total
- **Tabela de atletas** com: Nome, Equipe, Status, Dias Restantes, Ações
- **Status com cores:**
  - Azul: Em Teste
  - Verde: Autorizado
  - Vermelho: Expirado
- **Filtro por status**
- **Botões de ação:**
  - "Autorizar" para conceder acesso
  - "Carteirinha" para gerar documento
  - "Revogar" para cancelar autorização

**3. Modal de Autorização**
- Tipos: 6 Meses, 1 Ano, Até o Final do Ano
- Campo de observação opcional
- Confirmação com data de expiração

**4. Carteirinha de Membro**
- Design profissional com gradiente verde
- Dados do atleta (nome, equipe, email)
- Número único da carteirinha
- Data de validade
- Botão de impressão

**5. Endpoints Backend**
- `GET /api/admin/atletas-periodo-teste` - Lista atletas com status
- `GET /api/admin/autorizacoes` - Lista todas as autorizações
- `POST /api/admin/autorizacoes` - Cria nova autorização
- `DELETE /api/admin/autorizacoes/{id}` - Revoga autorização
- `GET /api/admin/carteirinha/{atleta_id}` - Gera dados da carteirinha
- `GET /api/atleta/status-acesso` - Verifica status do atleta logado

**6. Validação de Submissão de Resultados**
- Alterado de "6 dias após a corrida" para "30 dias após o cadastro"
- Se período expirado: verifica se tem autorização ativa
- Mensagem clara quando acesso é negado

---

## ✅ 11ª Tarefa - Selos/Medalhas de Conquista (09/03/2026)

### Sistema de Selos por Número de Resultados

**Novos Selos Implementados:**
| Selo | Requisito | Cor | Ícone |
|------|-----------|-----|-------|
| Atleta Bronze | 12 resultados | #CD7F32 (Bronze) | 🥉 |
| Atleta Prata | 20 resultados | #C0C0C0 (Prata) | 🥈 |
| Atleta Ouro | 30 resultados | #FFD700 (Ouro) | 🥇 |

**Endpoints Backend:**
- `GET /api/selos-atleta/{atleta_id}` - Retorna selos com progresso
- `POST /api/verificar-conquistas-atleta` - Verifica e atribui conquistas pendentes

**Componente Frontend:** `/app/frontend/src/components/SelosAtleta.jsx`
- Exibição visual dos selos com cards coloridos
- Barra de progresso para selos não conquistados
- Badge "✓ Conquistado" para selos obtidos
- Versão compacta para perfil e completa para página de detalhes

**Páginas Atualizadas:**
- `PerfilAtletaPage.jsx` - Seção compacta de selos
- `AtletaDetalhes.js` - Seção completa de "Selos e Conquistas"

**Verificação Automática:**
- Função `verificar_conquistas()` atualizada para verificar 12, 20 e 30 resultados
- Notificação enviada ao atleta quando conquista novo selo

---

## ✅ 12ª Tarefa - Sistema de Avaliação com Termo + IP (09/03/2026)

### Funcionalidades Implementadas

**1. Termo de Responsabilidade Obrigatório**
- Texto editável pelo admin via painel
- Checkbox obrigatório para aceitar o termo antes de avaliar
- Validação no backend: avaliação rejeitada se termo não aceito
- Visual destacado em vermelho no modal de avaliação

**2. Registro de IP do Avaliador**
- IP capturado automaticamente no endpoint de avaliação
- Suporte a proxy (X-Forwarded-For)
- User-Agent também registrado
- Data/hora de aceite do termo

**3. Painel Admin - Visualização de Avaliações**
- Endpoint `GET /api/admin/avaliacoes` lista todas avaliações com IPs
- Inclui nome da corrida, atleta, nota e dados de auditoria

**4. Texto do Termo**
- Endpoint `GET /api/admin/avaliacoes/termo` - Retorna texto atual
- Endpoint `PUT /api/admin/avaliacoes/termo` - Admin pode editar
- Texto padrão com 6 cláusulas sobre responsabilidade, LGPD e fraude

**Campos Adicionados na Avaliação:**
```json
{
  "aceito_termo": true,
  "termo_aceito_em": "2026-03-09T12:00:00",
  "ip_avaliador": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "atleta_email": "atleta@email.com"
}
```

**Arquivos Modificados:**
- `/app/backend/server.py` - Endpoint de avaliação atualizado
- `/app/frontend/src/pages/RankingCorridasPage.jsx` - Modal com termo

---

## ✅ 13ª Tarefa - Sistema de Reputação para Avaliadores (09/03/2026)

### Níveis de Reputação

| Nível | Requisito | Ícone | Cor |
|-------|-----------|-------|-----|
| Iniciante | 0+ avaliações | ⭐ | Cinza |
| **Avaliador Bronze** | 5+ avaliações | 🥉 | Bronze |
| **Avaliador Prata** | 15+ avaliações | 🥈 | Prata |
| **Avaliador Ouro** | 30+ avaliações | 🥇 | Ouro |

### Funcionalidades Implementadas

**1. Endpoints Backend**
- `GET /api/reputacao-avaliador/{atleta_id}` - Reputação de um avaliador
- `GET /api/ranking-avaliadores` - Top avaliadores
- `GET /api/minha-reputacao` - Reputação do atleta logado

**2. Componente Frontend:** `ReputacaoAvaliador.jsx`
- Exibição compacta (badge) no perfil do atleta
- Modal com detalhes completos ao clicar
- Barra de progresso para próximo nível
- Estatísticas: média das notas, meses ativos

**3. Ranking de Avaliadores**
- Botão "Top Avaliadores" na página de Ranking das Corridas
- Lista com posição, nome, média, nível e total de avaliações
- Top 3 destacados com medalhas visuais
- Legenda dos níveis disponíveis

**4. Informações Exibidas**
- Nível atual com ícone e cor
- Progresso percentual para próximo nível
- Quantas avaliações faltam
- Média das notas dadas pelo avaliador
- Meses ativos avaliando

**Arquivos Criados/Modificados:**
- `/app/frontend/src/components/ReputacaoAvaliador.jsx` (NOVO)
- `/app/frontend/src/pages/PerfilAtletaPage.jsx` (MODIFICADO)
- `/app/frontend/src/pages/RankingCorridasPage.jsx` (MODIFICADO)
- `/app/backend/server.py` (NOVOS endpoints)

---

## Credenciais de Teste

| Tipo | Email | Senha |
|------|-------|-------|
| Admin | admin@rankingrun.com | admin123 |
| Dono Assessoria | gustavo_gomes_2@email.com | senha123 |
| Atleta | rafael_souza_1@email.com | senha123 |

Última atualização: 09/03/2026 (Sessão 6 - Todas as 13 Tarefas Completas!)

---

## Novas Funcionalidades (09/03/2026 - Sessão 7)

### 14. Sistema RBAC (Role Based Access Control) ✅ NOVO

**Descrição**: Sistema completo de gerenciamento de administradores com controle de permissões granular, logs de auditoria obrigatórios, e conta de emergência com 2FA.

**Componentes Implementados:**

**1. Três Níveis de Acesso:**
- **Super Admin (Nível 1)**: Acesso total ao sistema (24 permissões)
  - Criar/editar/excluir administradores
  - Acesso total ao banco de dados
  - Visualizar histórico de ações de todos os administradores
  - Gerenciar configurações da plataforma
  - Exportar dados completos
  - Visualizar logs de segurança
  
- **Colaborador (Nível 2)**: Permissões operacionais limitadas (7 permissões)
  - Aprovar/reprovar corridas
  - Aprovar resultados de provas
  - Moderar avaliações
  - Visualizar atletas e assessorias
  - Enviar mensagens limitadas
  - **NÃO pode**: criar admins, alterar sistema, acessar dados financeiros, exportar banco

- **Admin de Emergência (Nível 3)**: Conta especial para situações críticas
  - Acesso total ao sistema (como Super Admin)
  - Invisível no painel administrativo
  - Não pode ser editada ou excluída
  - **2FA obrigatório** por email
  - Login gera **alerta automático** de segurança

**2. Sistema de Logs de Auditoria Obrigatório:**
- Registro automático de TODAS as ações administrativas
- Informações registradas:
  - ID e nome do administrador
  - Tipo de ação realizada
  - Descrição detalhada
  - Registro/entidade afetada
  - Data e hora (timestamp UTC)
  - Endereço IP
  - Dispositivo/Navegador (User-Agent parsing)
  - Localização aproximada

**3. Histórico de Login:**
- Registro de todas tentativas de login (sucesso/falha)
- Motivo de falha quando aplicável
- IP, navegador, dispositivo
- Data/hora da tentativa

**4. Sistema de Alertas de Segurança:**
- Alertas automáticos para:
  - Uso do Admin de Emergência
  - Tentativas de invasão
  - Ações suspeitas
- Botão "Resolver" para marcar alertas como tratados
- Badge de contagem na aba de Alertas

**5. 2FA (Two-Factor Authentication):**
- Implementado via código de 6 dígitos por email
- Códigos expiram em 10 minutos
- Obrigatório para Admin de Emergência
- Opcional para outros admins (pode ser habilitado)

**6. Interface de Gerenciamento (Frontend):**
- Nova seção "Administradores" no menu do Admin
- 4 abas: Administradores, Funções, Logs de Auditoria, Alertas
- Cards de estatísticas: Total, Ativos, Bloqueados, Ações Hoje, Alertas
- CRUD completo de administradores
- Visualização de permissões por role
- ScrollArea com logs detalhados
- Confirmação para ações críticas

**Arquivos Criados/Modificados:**
- `/app/backend/models/rbac.py` (NOVO) - Modelos RBAC
- `/app/backend/services/rbac_service.py` (NOVO) - Serviços auxiliares
- `/app/backend/routes/rbac.py` (NOVO) - Endpoints RBAC
- `/app/frontend/src/pages/admin/DashboardRBAC.jsx` (NOVO) - Interface
- `/app/frontend/src/pages/AdminDashboard.jsx` (MODIFICADO) - Menu atualizado

**Endpoints RBAC:**
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/rbac/setup` | Configuração inicial do sistema |
| GET | `/api/rbac/admins` | Listar administradores |
| POST | `/api/rbac/admins` | Criar novo administrador |
| PUT | `/api/rbac/admins/{id}` | Atualizar administrador |
| DELETE | `/api/rbac/admins/{id}` | Excluir administrador |
| POST | `/api/rbac/admins/{id}/bloquear` | Bloquear administrador |
| GET | `/api/rbac/roles` | Listar roles/funções |
| GET | `/api/rbac/permissoes` | Listar permissões |
| GET | `/api/rbac/logs` | Logs de auditoria |
| GET | `/api/rbac/login-history` | Histórico de login |
| GET | `/api/rbac/alertas` | Alertas de segurança |
| POST | `/api/rbac/alertas/{id}/resolver` | Resolver alerta |
| GET | `/api/rbac/stats` | Estatísticas RBAC |
| POST | `/api/rbac/login` | Login especial com 2FA |
| GET | `/api/rbac/verificar-permissao/{perm}` | Verificar permissão |

**Credenciais RBAC:**

| Tipo | Email | Senha | 2FA |
|------|-------|-------|-----|
| Super Admin | admin@rankingrun.com | admin123 | Não |
| Colaborador 1 | colaborador1@rankingrun.com | colab123 | Não |
| Colaborador 2 | colaborador2@rankingrun.com | colab123 | Não |
| Colaborador 3 | colaborador3@rankingrun.com | colab123 | Não |
| Colaborador 4 | colaborador4@rankingrun.com | colab123 | Não |
| Admin Emergência | suporte@rankingrun.com.br | EmergenciaRankingRun2026! | **Sim** |

**Coleções MongoDB Criadas:**
- `administradores` - Dados dos admins com role e permissões
- `roles` - Definição das roles
- `admin_logs` - Logs de ações administrativas
- `login_history` - Histórico de tentativas de login
- `alertas_seguranca` - Alertas de segurança
- `codigos_verificacao` - Códigos 2FA temporários

---

## Próximas Tarefas

### Backlog (Priorizado):
1. ~~**P1** - Integração de envio de email para 2FA e alertas de segurança~~ ✅ CONCLUÍDO
2. ~~**P2** - Refatoração do server.py em módulos~~ 🔄 EM PROGRESSO (6 módulos criados)
3. ~~**P2** - Painel diferenciado para Colaboradores (menu reduzido)~~ ✅ CONCLUÍDO
4. ~~**P3** - Geolocalização real baseada em IP~~ ✅ CONCLUÍDO
5. **P3** - Verificar domínio no Resend para emails de produção

### 18. Geolocalização Real Baseada em IP ✅ CONCLUÍDO (09/03/2026)

**Descrição**: Sistema de geolocalização que identifica a localização aproximada do administrador baseada no IP usando a API ip-api.com.

**Funcionalidades:**
- **Localização em tempo real** nos logs de auditoria (cidade, região, país)
- **Cache em memória** (1 hora) para evitar requisições repetidas
- **Suporte a IPs privados** (detecta "Rede Local" para localhost, 192.168.x.x, etc.)
- **ISP e organização** registrados nos logs
- **Frontend atualizado** com ícone de localização (📍) nos logs

**Informações capturadas:**
- Cidade, Região, País
- Código do país
- ISP (Provedor de Internet)
- Organização
- Localização formatada para exibição

**Arquivos criados:**
- `/app/backend/services/geolocation_service.py` - Serviço de geolocalização

**Arquivos modificados:**
- `/app/backend/services/rbac_service.py` - Integração com geolocalização
- `/app/backend/routes/rbac.py` - Logs e histórico com geolocalização
- `/app/frontend/src/pages/admin/DashboardRBAC.jsx` - Exibição de localização

### 17. Painel Diferenciado para Colaboradores ✅ CONCLUÍDO (09/03/2026)

**Descrição**: Sistema que exibe um menu reduzido para Colaboradores baseado em suas permissões.

**Funcionalidades:**
- **Badge de tipo de admin** na sidebar (Super Admin = roxo, Colaborador = azul)
- **Menu filtrado** por permissões:
  - Super Admin: Acesso a todos os 12 itens
  - Colaborador: Acesso a apenas 7 itens (operacionais)
- **Itens ocultos para Colaboradores:**
  - Autorizações
  - Administradores
  - Regulamento
  - Exportar Ranking
  - Ranking Run Inside

**Arquivos modificados:**
- `/app/frontend/src/context/AuthContext.js` - Adicionado suporte a permissões RBAC
- `/app/frontend/src/pages/AdminDashboard.jsx` - Menu filtrado por permissões

### 16. Refatoração do Backend em Módulos 🔄 EM PROGRESSO (09-10/03/2026)

**Descrição**: Divisão do arquivo monolítico `server.py` (~7000 linhas) em módulos menores usando `APIRouter`.

**Progresso Atualizado (7 módulos ativos):**

| Módulo | Status | Linhas | Descrição |
|--------|--------|--------|-----------|
| `config.py` | ✅ Ativo | 22 | Configurações compartilhadas |
| `routes/rbac.py` | ✅ Ativo | 920 | Sistema RBAC |
| `routes/auth_routes.py` | ✅ Ativo | 170 | Autenticação |
| `routes/notificacoes_routes.py` | ✅ Ativo | 60 | Notificações |
| `routes/conquistas_routes.py` | ✅ Ativo | 200 | Selos e conquistas |
| `routes/atletas_routes.py` | ✅ Ativo | 280 | Perfil, troca de equipe |
| `routes/resultados_routes.py` | ✅ Ativo | 115 | Submissão de resultados |
| `routes/ranking_routes.py` | ✅ Ativo | 340 | Rankings (povão, semanal, mensal) |

**Total: ~2100 linhas em módulos**

**Serviços Modulares:**
- `services/email_service.py` ✅
- `services/rbac_service.py` ✅
- `services/geolocation_service.py` ✅

**Guia completo:** `/app/backend/docs/REFACTORING_GUIDE.md`

### 15. Integração de Email com Resend ✅ NOVO (09/03/2026)

**Descrição**: Sistema completo de envio de emails transacionais usando Resend API para 2FA e alertas de segurança.

**Funcionalidades Implementadas:**
- **Envio de código 2FA** por email para Admin de Emergência
- **Alertas de segurança** enviados automaticamente quando Admin de Emergência faz login
- **Email de boas-vindas** para novos administradores (com credenciais)
- **Notificação de bloqueio** para administradores bloqueados
- **Templates HTML responsivos** para todos os tipos de email
- **Verificação de status** do serviço de email no painel
- **Graceful degradation**: Sistema funciona mesmo sem API key configurada

**Configuração atual:**
- API Key configurada: `re_RipiP5Y3_GtCnhJmwgdaAbVoQARetJYB4`
- Emails funcionam apenas para `vandy1250@gmail.com` (modo teste)
- Para enviar para outros emails, verificar domínio em https://resend.com/domains

**Arquivos criados:**
- `/app/backend/services/email_service.py` - Serviço completo de email

**Endpoints:**
- `GET /api/rbac/email-status` - Verifica se o email está configurado
- `POST /api/rbac/email-test` - Envia email de teste

---

## RESUMO DA SESSÃO 7 (09-10/03/2026)

### Funcionalidades Implementadas Nesta Sessão:

#### 1. Sistema RBAC Completo ✅
- 3 níveis de acesso (Super Admin, Colaborador, Admin Emergência)
- 24 permissões granulares
- Logs de auditoria obrigatórios
- 2FA por email para Admin de Emergência
- 4 colaboradores criados

#### 2. Integração de Email (Resend) ✅
- API Key configurada e funcionando
- Templates HTML para 2FA, alertas, boas-vindas, bloqueio
- Endpoint de teste de email

#### 3. Painel Diferenciado para Colaboradores ✅
- Menu reduzido (7 itens vs 12 do Super Admin)
- Badge de tipo de admin na sidebar
- Permissões verificadas no frontend

#### 4. Geolocalização Real por IP ✅
- Integração com ip-api.com
- Cidade, país, ISP nos logs
- Cache em memória (1 hora)

#### 5. Refatoração do Backend ✅
- 7 módulos de rotas ativos
- 3 serviços modulares
- ~2100 linhas extraídas do server.py

---

## CREDENCIAIS DE ACESSO

### Administradores RBAC:
| Tipo | Email | Senha | 2FA |
|------|-------|-------|-----|
| Super Admin | admin@rankingrun.com | admin123 | Não |
| Colaborador 1 | colaborador1@rankingrun.com | colab123 | Não |
| Colaborador 2 | colaborador2@rankingrun.com | colab123 | Não |
| Colaborador 3 | colaborador3@rankingrun.com | colab123 | Não |
| Colaborador 4 | colaborador4@rankingrun.com | colab123 | Não |
| Colaborador Teste Geo | testegeo@rankingrun.com | teste123 | Não |
| Admin Emergência | suporte@rankingrun.com.br | EmergenciaRankingRun2026! | **Sim** |

### Atletas de Teste:
| Email | Senha |
|-------|-------|
| rafael_souza_1@email.com | senha123 |
| gustavo_gomes_2@email.com | senha123 |
| marcos_martins_3@email.com | senha123 |
| andré_almeida_5@email.com | senha123 |

### Dono de Assessoria:
| Email | Senha |
|-------|-------|
| gustavo_gomes_2@email.com | senha123 |

---

## ARQUIVOS PRINCIPAIS

### Backend:
```
/app/backend/
├── server.py                    # Principal (~7000 linhas)
├── config.py                    # Configurações compartilhadas
├── models.py                    # Modelos Pydantic
├── services.py                  # Serviços originais
├── .env                         # Variáveis de ambiente
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py           ✅ Ativo
│   ├── notificacoes_routes.py   ✅ Ativo
│   ├── conquistas_routes.py     ✅ Ativo
│   ├── atletas_routes.py        ✅ Ativo
│   ├── resultados_routes.py     ✅ Ativo
│   ├── ranking_routes.py        ✅ Ativo
│   └── rbac.py                  ✅ Ativo
├── models/
│   └── rbac.py                  # Modelos RBAC
├── services/
│   ├── rbac_service.py          ✅ Ativo
│   ├── email_service.py         ✅ Ativo
│   └── geolocation_service.py   ✅ Ativo
└── docs/
    └── REFACTORING_GUIDE.md     # Guia de refatoração
```

### Frontend:
```
/app/frontend/src/
├── App.js
├── context/
│   └── AuthContext.js           # Atualizado com permissões RBAC
├── pages/
│   ├── AdminDashboard.jsx       # Menu filtrado por permissões
│   └── admin/
│       ├── DashboardRBAC.jsx    # Painel de administradores
│       └── ...
└── components/
    └── ...
```

---

## REFATORAÇÃO DO BACKEND (10/03/2026)

### ✅ Módulos Criados e Funcionando:
| Módulo | Endpoints | Status |
|--------|-----------|--------|
| `auth_routes.py` | /auth/register, /auth/login, /auth/me | ✅ Funcionando |
| `notificacoes_routes.py` | /notificacoes, marcar lida | ✅ Funcionando |
| `conquistas_routes.py` | /conquistas, /selos-atleta | ✅ Funcionando |
| `atletas_routes.py` | /atletas/meu-perfil, perfil, senha, foto, troca-equipe | ✅ Funcionando |
| `resultados_routes.py` | /resultados/submeter | ✅ Funcionando |
| `ranking_routes.py` | /ranking/povao, semanal, mensal, destaque-mes, etc | ✅ Funcionando |

### Progresso:
- **Linhas originais:** 7082
- **Linhas atuais:** 6199
- **Linhas removidas:** 883 (12.5%)
- **Testes:** 100% passaram (19/19 backend + frontend OK)

### Próximos Módulos a Criar:
- `admin_routes.py` (endpoints de administração)
- `assessorias_routes.py` (Liga de Assessorias)
- `corridas_eventos_routes.py` (Ranking de Corridas)

---

## SISTEMA DE MONITORAMENTO (10/03/2026)

### ✅ Funcionalidades Implementadas:

| Componente | Descrição | Status |
|------------|-----------|--------|
| Middleware de Métricas | Coleta automática de todas as requisições | ✅ |
| Endpoint /api/health | Health check público básico | ✅ |
| Endpoint /api/health/detailed | Health check detalhado público | ✅ |
| Dashboard Admin | Painel visual completo de métricas | ✅ |
| Histórico 7 dias | Snapshots salvos a cada 5 minutos no MongoDB | ✅ |
| Alertas por Email | Via Resend quando limites são ultrapassados | ✅ |

### Métricas Coletadas:
- **Sistema:** CPU, Memória, Disco, Conexões de Rede
- **Requisições:** Total, Req/min, Tempo médio, Taxa de erros, Status HTTP
- **Endpoints:** Tempo médio/máximo por endpoint, mais lentos

### Limites de Alerta Configurados:
- CPU > 90%
- Memória > 85%
- Disco > 90%
- Taxa de Erros > 10%
- Tempo de Resposta > 5s

### Arquivos Criados:
- `/app/backend/services/monitoring_service.py`
- `/app/backend/routes/monitoring_routes.py`
- `/app/backend/middleware/__init__.py`
- `/app/frontend/src/pages/admin/dashboards/DashboardMonitoramento.jsx`

---

## CACHE REDIS INTELIGENTE (10/03/2026)

### ✅ Funcionalidades Implementadas:

| Componente | Descrição | Status |
|------------|-----------|--------|
| Serviço de Cache | Redis com TTL configurável por tipo de dado | ✅ |
| Decorator @cached | Aplica cache automaticamente em funções async | ✅ |
| Invalidação por Prefixo | Permite invalidar grupos de cache (ranking, liga, etc) | ✅ |
| Estatísticas | Endpoint /api/monitoring/cache com hit rate e memória | ✅ |
| Invalidação Manual | Endpoint POST /api/monitoring/cache/invalidate | ✅ |

### TTL Configurados:
- **ranking**: 5 minutos
- **ranking_mensal**: 10 minutos
- **estados/faixas_etarias**: 1 hora (raramente muda)
- **liga_assessorias**: 5 minutos
- **stats**: 1 minuto

### Performance Observada:
- Hit Rate: ~71%
- Memória: ~1MB
- Redução média de tempo de resposta: 20-30%

---

## REFATORAÇÃO DO BACKEND - FASE 2 (10/03/2026)

### ✅ Novos Módulos Criados:

| Módulo | Linhas | Endpoints | Status |
|--------|--------|-----------|--------|
| `admin_routes.py` | ~500 | /admin/pendentes, aprovar, reprovar, stats, atletas | ✅ |
| `assessorias_routes.py` | ~400 | /assessorias/lista, /liga-assessorias/* | ✅ |

### Progresso Total da Refatoração:
- **Linhas originais:** 7082
- **Linhas atuais:** 6253
- **Linhas removidas:** 829 (12%)
- **Total de módulos de rotas:** 11
- **Total de serviços:** 6

---

## PRÓXIMAS TAREFAS (BACKLOG)

### P3 - Pendentes:
1. Verificar domínio no Resend para emails de produção
2. Criar módulo `corridas_eventos_routes.py` (Ranking de Corridas)
3. Criar módulo `aniversariantes_routes.py`
4. Criar módulo `instagram_routes.py` (Ranking Run Inside)

### Melhorias Futuras:
- Dashboard com mapa de acessos (usando lat/lon da geolocalização)
- Sistema de backup automático
- Notificações push

---

**Última Atualização:** 10/03/2026
**Versão:** 7.3 (Cache Redis + Refatoração Fase 2)


