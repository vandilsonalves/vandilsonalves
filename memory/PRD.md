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
- Upload de foto de perfil (corrigido)
- Visualização de estatísticas (pontos, corridas)
- **Exportar Meus Dados** (download Excel do histórico)
- **Acesso Rápido**: Botões Strava, WhatsApp, TikTok, YouTube
- **Compartilhamento**: WhatsApp e Instagram
- Sistema de Conquistas (Campeão, Pódio, Veterano, Elite, etc.)
- Sistema de Notificações (sininho com badge)

### 4. Painel de Administração ✅
- **Dashboard** com estatísticas e gráficos:
  - Total de atletas, pendentes, corridas, selo "P"
  - Gráficos de distribuição por estado/categoria/gênero/faixa etária
  - Gráfico de corridas por mês
- **Aba Aprovações**: Aprovar/Reprovar resultados submetidos
- **Aba Atletas** (NOVA):
  - Filtros: Todos, Atletas M/F, PCD M/F, Cadeirante M/F
  - Botão "+ Adicionar" para cadastrar atletas
  - Botão "Exportar Dados" (Excel)
  - Cards de atletas com Ver/Editar/Excluir
  - Modal de edição completo
- **Aba Submeter Resultado** (NOVA):
  - Selecionar atleta
  - Adicionar ou Remover pontos
  - Informar motivo/justificativa
- **Aba Gráficos**: Visualizações detalhadas
- **Aba Rankings**: Exportar CSV e Excel

### 5. Compartilhamento Avançado (Estilo Strava) ✅
- Página de detalhes do atleta com botão "Compartilhar"
- Modal de compartilhamento com:
  - Preview da imagem (formato 9:16 para Stories)
  - Botões: WhatsApp, Instagram, Facebook, Baixar
  - Copiar Link

### 6. Sistema de Notificações ✅
- Notificações automáticas para:
  - Resultado aprovado
  - Resultado reprovado (com motivo)
  - Conquistas desbloqueadas
  - Ajustes de pontos pelo admin
- Sininho no header com badge de não lidas
- Dropdown com lista de notificações

### 7. Sistema de Conquistas ✅
- Campeão (1º lugar em corrida)
- Pódio (top 3 em corrida)
- Veterano (10 corridas)
- Elite (100+ pontos)
- Maratonista (completou 42KM)
- Consistente (corridas em 6+ meses)

---

## Arquitetura Técnica

### Backend (FastAPI)
- `/app/backend/server.py` - API principal (refatorado)
- `/app/backend/models/__init__.py` - Modelos Pydantic
- `/app/backend/services/__init__.py` - Serviços e helpers
- MongoDB para persistência
- JWT para autenticação
- Endpoints principais:
  - `/api/auth/*` - Autenticação
  - `/api/ranking/*` - Rankings e exportação
  - `/api/atletas/*` - Perfis de atletas
  - `/api/admin/*` - Endpoints administrativos (atletas, ajuste de pontos)
  - `/api/notificacoes/*` - Sistema de notificações
  - `/api/conquistas/*` - Sistema de conquistas

### Frontend (React)
- `/app/frontend/src/pages/` - Páginas da aplicação
- `/app/frontend/src/components/` - Componentes reutilizáveis
- Componentes shadcn/ui
- Recharts para gráficos
- html2canvas para gerar imagens de compartilhamento
- React Router para navegação

---

## Credenciais de Teste
- **Admin**: admin@runpro.com / admin123
- **Atleta**: gabrielsouza_normal_1@email.com / atleta123

---

## Dados de Teste
- 90 atletas (15 por categoria)
- Aproximadamente 960 corridas
- Distribuição uniforme por estados e faixas etárias

---

## Próximos Passos (Backlog)
1. Implementação de notificações por e-mail (Resend)
2. Ranking histórico por ano
3. Melhorias de performance (cache)
4. Integração real com Strava API

---

Última atualização: 25/02/2026
