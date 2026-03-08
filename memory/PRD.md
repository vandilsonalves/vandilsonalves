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
