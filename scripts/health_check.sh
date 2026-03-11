#!/bin/bash
# =============================================================================
# Ranking Run Pró - Health Check Rápido
# =============================================================================
# Verifica rapidamente o status de todos os serviços
# Uso: ./health_check.sh
# =============================================================================

echo "🔍 Health Check - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check() {
    local status_ok=false
    case "$2" in
        "OK"|"RUNNING"|"PONG"|"RUNNING (API: OK)")
            status_ok=true
            ;;
    esac
    
    if $status_ok; then
        echo -e "$1: ${GREEN}✓ $2${NC}"
    else
        echo -e "$1: ${RED}✗ $2${NC}"
    fi
}

# Supervisor
sup_status=$(pgrep -x supervisord > /dev/null && echo "RUNNING" || echo "STOPPED")
check "Supervisor" "$sup_status"

# MongoDB
mongo_status=$(supervisorctl status mongodb 2>/dev/null | awk '{print $2}')
check "MongoDB" "$mongo_status"

# Redis
redis_status=$(redis-cli ping 2>/dev/null || echo "FAILED")
check "Redis" "$redis_status"

# Celery
celery_status=$(supervisorctl status celery 2>/dev/null | awk '{print $2}')
check "Celery" "$celery_status"

# Backend
backend_status=$(supervisorctl status backend 2>/dev/null | awk '{print $2}')
api_health=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health 2>/dev/null)
if [ "$backend_status" == "RUNNING" ] && [ "$api_health" == "200" ]; then
    check "Backend" "RUNNING (API: OK)"
else
    check "Backend" "$backend_status (API: $api_health)"
fi

# Frontend
frontend_status=$(supervisorctl status frontend 2>/dev/null | awk '{print $2}')
check "Frontend" "$frontend_status"

echo "================================================"
