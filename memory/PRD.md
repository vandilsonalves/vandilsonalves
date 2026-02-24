# Ranking Run Pró - PRD (Product Requirements Document)

## Visão Geral
Plataforma completa de ranking de corrida com sistema de ranking duplo (Nacional e Estadual), filtráveis por categoria e faixa etária.

## Requisitos Implementados

### 1. Sistema de Ranking ✅
- Rankings Nacionais e Estaduais
- Filtros por categoria: Masculino, Feminino, PCD M/F, Cadeirante M/F
- Sistema de pontuação:
  - Normal: 1º-10º lugar (10 a 1 ponto)
  - PCD/Cadeirante: 1º-3º lugar (10 a 8 pontos)
- Selo "P" para atletas com menos de 12 provas (8 para PCD/Cadeirante)
- Badge "Elite" para atletas com 100+ pontos

### 2. Autenticação e Perfis ✅
- Cadastro e login para atletas e administradores
- JWT para autenticação
- Roles: `atleta` e `admin`

### 3. Painel do Atleta ✅
- Edição de perfil: equipe, redes sociais, telefone, bio
- Upload de foto de perfil
- Visualização de estatísticas (pontos, corridas)
- Email não pode ser alterado

### 4. Painel de Administração ✅
- Dashboard com estatísticas:
  - Total de atletas por gênero
  - Gráficos de distribuição por estado
  - Gráficos de distribuição por categoria/gênero
  - Gráficos de distribuição por faixa etária
  - Atletas com selo "P" (pendentes de corridas)
- Aprovação/Reprovação de resultados submetidos
- Visualização de resultados pendentes

### 5. Submissão de Resultados ✅
- Atletas podem submeter resultados de corridas
- Campos: competição, colocação, tempo, link, foto (opcional)
- Validação de colocação (apenas posições que pontuam)
- Prazo de 6 dias para submissão

### 6. Funcionalidades Adicionais ✅
- Exportação do ranking para CSV e Excel
- Busca com filtros (nome, colocação, UF)
- Página de detalhes do atleta com histórico de corridas
- Modal "Como funciona?" explicando o sistema

## Arquitetura Técnica

### Backend (FastAPI)
- `/app/backend/server.py` - API principal
- MongoDB para persistência
- JWT para autenticação
- Endpoints principais:
  - `/api/auth/*` - Autenticação
  - `/api/ranking/*` - Rankings e exportação
  - `/api/atletas/*` - Perfis de atletas
  - `/api/admin/*` - Endpoints administrativos
  - `/api/resultados/*` - Submissão de resultados

### Frontend (React)
- `/app/frontend/src/pages/` - Páginas da aplicação
- Componentes shadcn/ui
- Recharts para gráficos
- React Router para navegação

## Credenciais de Teste
- Admin: admin@runpro.com / admin123
- Atleta: pedrosantos_normal_0@email.com / atleta123

## Dados de Teste
- 90 atletas (15 por categoria)
- Aproximadamente 940 corridas
- Distribuição uniforme por estados e faixas etárias

## Status do Projeto
- ✅ Backend completo e testado
- ✅ Frontend completo
- ✅ Painel Admin com gráficos
- ✅ Painel do Atleta com edição de perfil
- ✅ Sistema de ranking funcionando

## Próximos Passos (Backlog)
1. Refatoração do server.py em módulos menores
2. Implementação de notificações por email
3. Sistema de conquistas/medalhas
4. Ranking histórico por ano
5. Integração com redes sociais para compartilhamento

---
Última atualização: 24/02/2026
