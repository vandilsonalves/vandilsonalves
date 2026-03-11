# Scripts de Gerenciamento - Ranking Run Pró

## Visão Geral

Esta pasta contém scripts utilitários para gerenciar os serviços da aplicação.

## Scripts Disponíveis

### 1. `start_services.sh`

Script principal de inicialização que verifica e inicia todos os serviços necessários.

```bash
./scripts/start_services.sh
```

**O que faz:**
- Verifica se o Supervisor está rodando
- Inicia MongoDB, Redis, Celery, Backend e Frontend
- Mostra status detalhado de cada serviço
- Exibe informações de cache e workers

**Quando usar:**
- Após restart do container
- Quando algum serviço não está respondendo
- Para diagnóstico inicial de problemas

---

### 2. `health_check.sh`

Verificação rápida do status de todos os serviços.

```bash
./scripts/health_check.sh
```

**Output exemplo:**
```
🔍 Health Check - 2026-03-11 00:32:31
================================================
Supervisor: ✓ RUNNING
MongoDB: ✓ RUNNING
Redis: ✓ PONG
Celery: ✓ RUNNING
Backend: ✓ RUNNING (API: OK)
Frontend: ✓ RUNNING
================================================
```

---

## Serviços Gerenciados

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Backend | 8001 | API FastAPI |
| Frontend | 3000 | React App |
| MongoDB | 27017 | Banco de dados |
| Redis | 6379 | Cache + Broker Celery |
| Celery | - | Workers para tarefas assíncronas |

---

## Configuração do Supervisor

Os serviços são gerenciados pelo Supervisor. Configurações em:

- `/etc/supervisor/conf.d/supervisord.conf` - Backend, Frontend, MongoDB (READONLY)
- `/etc/supervisor/conf.d/services.conf` - Redis, Celery (customizável)

### Comandos úteis do Supervisor:

```bash
# Ver status de todos os serviços
sudo supervisorctl status

# Reiniciar um serviço específico
sudo supervisorctl restart backend

# Ver logs em tempo real
tail -f /var/log/supervisor/backend.err.log

# Recarregar configurações
sudo supervisorctl reread
sudo supervisorctl update
```

---

## Logs

Todos os logs estão em `/var/log/supervisor/`:

- `backend.err.log` / `backend.out.log`
- `frontend.err.log` / `frontend.out.log`
- `redis.err.log` / `redis.out.log`
- `celery.err.log` / `celery.out.log`

---

## Troubleshooting

### Redis não inicia
```bash
# Verificar se já está rodando
redis-cli ping

# Matar processo anterior
pkill redis-server

# Iniciar via supervisor
sudo supervisorctl start redis
```

### Celery não inicia
```bash
# Verificar logs
tail -50 /var/log/supervisor/celery.err.log

# Verificar se Redis está disponível
redis-cli ping

# Reiniciar
sudo supervisorctl restart celery
```

### Backend não responde
```bash
# Verificar health
curl http://localhost:8001/api/health

# Ver logs
tail -50 /var/log/supervisor/backend.err.log

# Reiniciar
sudo supervisorctl restart backend
```
