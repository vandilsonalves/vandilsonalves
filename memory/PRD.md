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

## Próximos Passos - Liga de Assessorias (Fases 2-4)
**Fase 2 - Rankings Públicos e Filtros**:
- Exibir rankings na página pública (3 abas: Mensal, Anual, Histórico)
- Critérios de desempate completos

**Fase 3 - Página da Assessoria Pública**:
- Página exclusiva para cada assessoria
- Botão "Quero treinar com essa assessoria"
- Selo digital oficial para download

**Fase 4 - Painel do Dono de Assessoria**:
- Novo role "dono_assessoria"
- Dashboard exclusivo com métricas da equipe
- Cadastrar atletas, enviar mensagens, baixar selo

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

Última atualização: 04/03/2026
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

Última atualização: 02/03/2026
