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

---

## Próximos Passos (Backlog)
1. **P0**: Implementação de notificações por e-mail (Resend)
2. **P1**: Ranking histórico por ano (filtro por temporada)
3. Melhorias de performance (cache)
4. Integração real com Strava API

---

## Correções Implementadas (25/02/2026)
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

---

Última atualização: 25/02/2026
