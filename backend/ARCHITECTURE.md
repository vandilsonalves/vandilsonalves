# Arquitetura do Backend - Ranking Run Pró

## Estrutura Atual

```
/app/backend/
├── server.py           # Servidor principal (monolítico - 7000+ linhas)
├── models/
│   └── __init__.py     # Modelos Pydantic
├── services/
│   └── __init__.py     # Serviços e constantes (CONQUISTAS, etc.)
├── routes/             # Routers modulares (parcialmente implementado)
│   ├── __init__.py
│   └── auth.py         # Autenticação (exemplo de refatoração)
├── utils/
│   ├── __init__.py
│   └── dependencies.py # Dependências compartilhadas (db, auth)
└── tests/
```

## Seções do server.py (para refatoração futura)

| Linha | Seção | Sugestão de Arquivo |
|-------|-------|---------------------|
| 68-90 | Authentication helpers | `utils/dependencies.py` ✅ |
| 91-228 | Auth Endpoints | `routes/auth.py` ✅ |
| 230-276 | Notificações | `routes/notificacoes.py` |
| 278-480 | Conquistas/Selos | `routes/conquistas.py` |
| 485-665 | Perfil do Atleta | `routes/atletas.py` |
| 667-845 | Troca de Equipe | `routes/atletas.py` |
| 847-960 | Submissão de Resultados | `routes/resultados.py` |
| 964-1500 | Admin - Aprovações | `routes/admin/aprovacoes.py` |
| 1500-2000 | Admin - Stats | `routes/admin/stats.py` |
| 2000-3000 | Admin - Atletas/Assessorias | `routes/admin/gestao.py` |
| 3000-4500 | Liga de Assessorias | `routes/assessorias.py` |
| 4500-5400 | Dono Assessoria Dashboard | `routes/dono_assessoria.py` |
| 5400-5600 | Regulamento | `routes/configuracoes.py` |
| 5600-5800 | Autorizações | `routes/autorizacoes.py` |
| 5800-6100 | Reputação Avaliadores | `routes/reputacao.py` |
| 6100-7000 | Ranking de Corridas | `routes/corridas.py` |

## Como Refatorar (Passo a Passo)

### 1. Criar o Router

```python
# routes/notificacoes.py
from fastapi import APIRouter, Depends
from utils import db, get_current_user

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])

@router.get("/")
async def get_notificacoes(current_user: dict = Depends(get_current_user)):
    # ... código existente
```

### 2. Registrar no server.py

```python
from routes.notificacoes import router as notificacoes_router
app.include_router(notificacoes_router, prefix="/api")
```

### 3. Remover código duplicado do server.py

## Dependências Compartilhadas

O arquivo `utils/dependencies.py` contém:
- `db` - Conexão MongoDB
- `get_current_user()` - Verifica autenticação
- `get_admin_user()` - Verifica se é admin
- `SECRET_KEY`, `ALGORITHM` - Configurações JWT

## Prioridade de Refatoração

1. **Alta**: Rotas de Admin (muito código)
2. **Média**: Conquistas e Reputação
3. **Baixa**: Auth (já funciona bem)

## Notas

- O server.py funciona bem como está
- Refatorar gradualmente sem quebrar funcionalidades
- Sempre testar após cada mudança
- Manter compatibilidade com frontend
