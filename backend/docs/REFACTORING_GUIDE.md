# Guia de Refatoração do Backend - Ranking Run

## Status Atual

O arquivo `server.py` original tem **~7000 linhas**. A refatoração está sendo feita de forma incremental para garantir que nada quebre.

## Módulos Criados

| Módulo | Arquivo | Status | Linhas | Descrição |
|--------|---------|--------|--------|-----------|
| Config | `config.py` | ✅ Ativo | 22 | Configurações compartilhadas (DB, Security) |
| RBAC | `routes/rbac.py` | ✅ Ativo | ~850 | Sistema de administradores e permissões |
| Auth | `routes/auth_routes.py` | 🟡 Pronto | ~170 | Autenticação (login, registro, me) |
| Notificações | `routes/notificacoes_routes.py` | 🟡 Pronto | ~60 | Sistema de notificações |
| Conquistas | `routes/conquistas_routes.py` | 🟡 Pronto | ~200 | Selos e conquistas |
| Atletas | `routes/atletas_routes.py` | 🟡 Pronto | ~280 | Perfil, troca de equipe, aniversário |
| Resultados | `routes/resultados_routes.py` | 🟡 Pronto | ~115 | Submissão de resultados |
| Email | `services/email_service.py` | ✅ Ativo | ~350 | Serviço de email (Resend) |

### Legenda:
- ✅ **Ativo**: Código removido do server.py e router incluído
- 🟡 **Pronto**: Módulo criado e testado, mas endpoints ainda duplicados no server.py

## Próximos Módulos a Criar

| Módulo | Linhas no server.py | Prioridade |
|--------|---------------------|------------|
| Admin | 1010-1880 (~870 linhas) | P1 |
| Ranking | 1881-2635 (~755 linhas) | P1 |
| Ranking Povão | 2009-2070 (~60 linhas) | P2 |
| Ranking Semanal/Mensal | 2073-2320 (~250 linhas) | P2 |
| Assessorias | 2640-2960 (~320 linhas) | P2 |
| Corridas | 2960-3140 (~180 linhas) | P2 |
| Aniversariantes | 3142-4683 (~1540 linhas) | P3 |
| Instagram Insight | 4700-7000 (~2300 linhas) | P3 |

## Como Ativar um Módulo

1. **No server.py**: Remover (ou comentar) os endpoints que foram movidos para o módulo
2. **No server.py (INCLUDE ROUTER)**: Adicionar o import e include do router
3. **Testar**: Verificar se todos os endpoints funcionam corretamente
4. **Commit**: Salvar as alterações

## Estrutura de Arquivos

```
/app/backend/
├── server.py              # Arquivo principal (reduzindo gradualmente)
├── config.py              # Configurações compartilhadas
├── models.py              # Modelos Pydantic
├── services.py            # Serviços auxiliares
├── routes/
│   ├── __init__.py        # Exporta todos os routers
│   ├── auth_routes.py     # Autenticação
│   ├── notificacoes_routes.py
│   ├── conquistas_routes.py
│   ├── atletas_routes.py
│   ├── resultados_routes.py
│   ├── rbac.py            # Sistema RBAC (ativo)
│   └── (futuros...)
├── models/
│   └── rbac.py            # Modelos RBAC
└── services/
    ├── rbac_service.py    # Serviços RBAC
    └── email_service.py   # Serviço de email
```

## Dependências Entre Módulos

```
config.py
    └── db, security (usado por todos)

auth_routes.py
    └── get_current_user, get_admin_user (usado por todos os outros routes)

notificacoes_routes.py
    └── criar_notificacao() (usado por conquistas)

conquistas_routes.py
    └── verificar_conquistas() (chamado após aprovar resultado)
```

## Notas Importantes

1. **Não modificar models.py** sem testar extensivamente
2. **Manter funções de auth** no server.py até todos os módulos serem migrados
3. **Testar após cada mudança** para garantir que nada quebrou
4. **Hot reload** deve reiniciar automaticamente após cada save

## Última Atualização

Data: 09/03/2026
Progresso: 6 módulos criados, 1 ativo (RBAC)
Linhas removidas do server.py: ~850 (RBAC)
