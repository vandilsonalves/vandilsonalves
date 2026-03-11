#!/bin/bash
# =============================================================================
# Ranking Run Pró - Script de Inicialização de Serviços
# =============================================================================
# Este script garante que todos os serviços necessários estejam rodando
# Pode ser executado manualmente ou adicionado ao startup do container
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de log
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
echo "=============================================="
echo "   Ranking Run Pró - Inicialização"
echo "=============================================="
echo ""

# Verificar se supervisor está rodando
check_supervisor() {
    log_info "Verificando Supervisor..."
    if pgrep -x "supervisord" > /dev/null; then
        log_success "Supervisor está rodando"
        return 0
    else
        log_warning "Supervisor não está rodando. Iniciando..."
        supervisord -c /etc/supervisor/supervisord.conf
        sleep 2
        if pgrep -x "supervisord" > /dev/null; then
            log_success "Supervisor iniciado com sucesso"
            return 0
        else
            log_error "Falha ao iniciar Supervisor"
            return 1
        fi
    fi
}

# Verificar e iniciar Redis
check_redis() {
    log_info "Verificando Redis..."
    
    # Primeiro, tentar via supervisor
    status=$(supervisorctl status redis 2>/dev/null | awk '{print $2}' || echo "NOT_FOUND")
    
    if [[ "$status" == "RUNNING" ]]; then
        log_success "Redis está rodando via Supervisor"
        return 0
    elif [[ "$status" == "NOT_FOUND" ]]; then
        # Redis não está no supervisor, verificar se está rodando standalone
        if redis-cli ping 2>/dev/null | grep -q "PONG"; then
            log_warning "Redis rodando standalone (não gerenciado pelo Supervisor)"
            return 0
        else
            log_warning "Redis não configurado no Supervisor. Iniciando manualmente..."
            redis-server --daemonize yes --bind 127.0.0.1 --port 6379
            sleep 2
        fi
    else
        # Tentar iniciar via supervisor
        log_warning "Redis status: $status. Tentando iniciar..."
        supervisorctl start redis 2>/dev/null || true
        sleep 2
    fi
    
    # Verificar se Redis está respondendo
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log_success "Redis está respondendo"
        return 0
    else
        log_error "Redis não está respondendo"
        return 1
    fi
}

# Verificar e iniciar Celery
check_celery() {
    log_info "Verificando Celery..."
    
    status=$(supervisorctl status celery 2>/dev/null | awk '{print $2}' || echo "NOT_FOUND")
    
    if [[ "$status" == "RUNNING" ]]; then
        log_success "Celery está rodando via Supervisor"
        return 0
    elif [[ "$status" == "NOT_FOUND" ]]; then
        log_warning "Celery não configurado no Supervisor"
        log_info "Verifique se /etc/supervisor/conf.d/services.conf existe"
        return 1
    else
        log_warning "Celery status: $status. Tentando iniciar..."
        supervisorctl start celery 2>/dev/null || true
        sleep 5
        
        new_status=$(supervisorctl status celery 2>/dev/null | awk '{print $2}')
        if [[ "$new_status" == "RUNNING" ]]; then
            log_success "Celery iniciado com sucesso"
            return 0
        else
            log_error "Falha ao iniciar Celery. Verifique os logs: /var/log/supervisor/celery.err.log"
            return 1
        fi
    fi
}

# Verificar MongoDB
check_mongodb() {
    log_info "Verificando MongoDB..."
    
    status=$(supervisorctl status mongodb 2>/dev/null | awk '{print $2}' || echo "NOT_FOUND")
    
    if [[ "$status" == "RUNNING" ]]; then
        log_success "MongoDB está rodando"
        return 0
    else
        log_warning "MongoDB status: $status. Tentando iniciar..."
        supervisorctl start mongodb 2>/dev/null || true
        sleep 3
        return 0
    fi
}

# Verificar Backend
check_backend() {
    log_info "Verificando Backend (FastAPI)..."
    
    status=$(supervisorctl status backend 2>/dev/null | awk '{print $2}' || echo "NOT_FOUND")
    
    if [[ "$status" == "RUNNING" ]]; then
        # Verificar se está respondendo
        if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
            log_success "Backend está rodando e respondendo"
            return 0
        else
            log_warning "Backend rodando mas não responde. Aguardando..."
            sleep 5
            if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
                log_success "Backend está respondendo"
                return 0
            fi
        fi
    else
        log_warning "Backend status: $status. Tentando iniciar..."
        supervisorctl start backend 2>/dev/null || true
        sleep 5
    fi
    return 0
}

# Verificar Frontend
check_frontend() {
    log_info "Verificando Frontend (React)..."
    
    status=$(supervisorctl status frontend 2>/dev/null | awk '{print $2}' || echo "NOT_FOUND")
    
    if [[ "$status" == "RUNNING" ]]; then
        log_success "Frontend está rodando"
        return 0
    else
        log_warning "Frontend status: $status. Tentando iniciar..."
        supervisorctl start frontend 2>/dev/null || true
        sleep 3
        return 0
    fi
}

# Mostrar status final
show_status() {
    echo ""
    echo "=============================================="
    echo "   Status Final dos Serviços"
    echo "=============================================="
    supervisorctl status
    echo ""
    
    # Verificar cache Redis
    echo "--- Cache Redis ---"
    redis_keys=$(redis-cli keys "cache:*" 2>/dev/null | wc -l)
    echo "Chaves de cache: $redis_keys"
    
    # Verificar workers Celery
    echo ""
    echo "--- Workers Celery ---"
    celery_status=$(cd /app/backend && /root/.venv/bin/celery -A celery_app inspect ping 2>/dev/null | grep -c "pong" || echo "0")
    echo "Workers ativos: $celery_status"
}

# Função principal
main() {
    local errors=0
    
    check_supervisor || ((errors++))
    check_mongodb || ((errors++))
    check_redis || ((errors++))
    check_celery || ((errors++))
    check_backend || ((errors++))
    check_frontend || ((errors++))
    
    show_status
    
    if [[ $errors -eq 0 ]]; then
        echo ""
        log_success "Todos os serviços iniciados com sucesso!"
        echo ""
    else
        echo ""
        log_warning "Alguns serviços podem ter problemas. Verifique os logs."
        echo ""
    fi
    
    return $errors
}

# Executar
main "$@"
