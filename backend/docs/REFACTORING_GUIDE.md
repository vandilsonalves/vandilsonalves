# Guia de Refatoração do Backend - Ranking Run

## Status Atual: 7 Módulos Ativos

O arquivo `server.py` original tem **~7000 linhas**. A refatoração está em andamento com 7 módulos ativos.

## Módulos Ativos ✅

| Módulo | Arquivo | Linhas | Descrição |
|--------|---------|--------|-----------|
| Config | `config.py` | ~22 | Configurações compartilhadas (DB, Security) |
| RBAC | `routes/rbac.py` | ~920 | Sistema de administradores e permissões |
| Auth | `routes/auth_routes.py` | ~170 | Autenticação (login, registro, me) |
| Notificações | `routes/notificacoes_routes.py` | ~60 | Sistema de notificações |
| Conquistas | `routes/conquistas_routes.py` | ~200 | Selos e conquistas |
| Atletas | `routes/atletas_routes.py` | ~280 | Perfil, troca de equipe, aniversário |
| Resultados | `routes/resultados_routes.py` | ~115 | Submissão de resultados |
| Ranking | `routes/ranking_routes.py` | ~340 | Rankings (povão, semanal, mensal, categoria) |

**Total de linhas em módulos: ~2100**

## Serviços Modulares ✅

| Serviço | Arquivo | Descrição |
|---------|---------|-----------|
| Email | `services/email_service.py` | Envio de emails (Resend) |
| RBAC | `services/rbac_service.py` | Funções auxiliares RBAC |
| Geolocalização | `services/geolocation_service.py` | Localização por IP |

## Próximos Módulos a Criar

| Módulo | Endpoints | Prioridade |
|--------|-----------|------------|
| Admin | /admin/* | P1 |
| Assessorias | /assessorias/* | P2 |
| Corridas | /corridas/* | P2 |
| Ranking Corridas | /ranking-corridas/* | P2 |
| Aniversariantes | /aniversariantes/* | P3 |
| Instagram Insight | /instagram/* | P3 |

## Estrutura de Arquivos

```
/app/backend/
├── server.py              # Arquivo principal (~7000 linhas, reduzindo)
├── config.py              # Configurações compartilhadas
├── models.py              # Modelos Pydantic
├── services.py            # Serviços auxiliares (original)
├── routes/
│   ├── __init__.py        # Exporta todos os routers
│   ├── auth_routes.py     ✅
│   ├── notificacoes_routes.py ✅
│   ├── conquistas_routes.py ✅
│   ├── atletas_routes.py  ✅
│   ├── resultados_routes.py ✅
│   ├── ranking_routes.py  ✅
│   └── rbac.py            ✅
├── models/
│   └── rbac.py            # Modelos RBAC
└── services/
    ├── rbac_service.py    ✅
    ├── email_service.py   ✅
    └── geolocation_service.py ✅
```

## Como Adicionar Novo Módulo

1. Criar arquivo em `routes/nome_routes.py`
2. Importar e usar `APIRouter`, `db`, funções de auth
3. Adicionar import no `server.py` (seção INCLUDE ROUTER)
4. Adicionar ao `routes/__init__.py`
5. Testar endpoints

## Notas Importantes

- Os endpoints podem estar duplicados (server.py + módulos)
- FastAPI usa a PRIMEIRA rota que corresponde
- Routers incluídos DEPOIS têm prioridade (sobrescrevem)
- Manter funções `get_current_user` e `get_admin_user` no server.py (usadas por muitos endpoints)

## Última Atualização

Data: 10/03/2026
Módulos ativos: 7
Linhas em módulos: ~2100
