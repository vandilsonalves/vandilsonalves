# /app/backend/routes/monitoring_routes.py
"""
Endpoints de Monitoramento de Saúde do Backend
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone, timedelta
from typing import Optional

from config import db
from routes.auth_routes import get_current_user, get_admin_user
from services.monitoring_service import (
    metrics_collector, 
    save_metrics_snapshot, 
    get_metrics_history,
    generate_alert_email_html
)
from services.email_service import enviar_email

router = APIRouter(tags=["Monitoramento"])


# ==================== HEALTH CHECK PÚBLICO ====================

@router.get("/health")
async def health_check():
    """
    Endpoint público de health check.
    Retorna status básico do sistema para monitoramento externo.
    """
    health = metrics_collector.get_health_status()
    
    return {
        "status": health["status"],
        "timestamp": health["timestamp"],
        "uptime": health["requests"]["uptime_formatted"],
        "version": "7.1"
    }


@router.get("/health/detailed")
async def health_check_detailed():
    """
    Health check detalhado (público mas com menos info sensível).
    """
    health = metrics_collector.get_health_status()
    
    return {
        "status": health["status"],
        "timestamp": health["timestamp"],
        "system": {
            "cpu_percent": health["system"]["cpu_percent"],
            "memory_percent": health["system"]["memory_percent"],
            "disk_percent": health["system"]["disk_percent"]
        },
        "requests": {
            "total": health["requests"]["total_requests"],
            "errors": health["requests"]["total_errors"],
            "avg_response_ms": health["requests"]["avg_response_time_ms"]
        },
        "uptime": health["requests"]["uptime_formatted"],
        "alerts_count": len(health["active_alerts"])
    }


# ==================== ENDPOINTS ADMIN ====================

@router.get("/monitoring/dashboard")
async def get_monitoring_dashboard(current_user: dict = Depends(get_admin_user)):
    """
    Dashboard completo de monitoramento (apenas admin).
    """
    health = metrics_collector.get_health_status()
    
    # Buscar histórico das últimas 24h
    history_24h = await get_metrics_history(db, hours=24)
    
    # Buscar histórico dos últimos 7 dias (agregado por hora)
    history_7d = await get_metrics_history(db, hours=168)
    
    return {
        "current": health,
        "history_24h": history_24h,
        "history_7d": history_7d,
        "thresholds": metrics_collector.alert_thresholds
    }


@router.get("/monitoring/history")
async def get_monitoring_history(
    hours: int = 24,
    current_user: dict = Depends(get_admin_user)
):
    """
    Busca histórico de métricas (apenas admin).
    """
    if hours > 168:  # Máximo 7 dias
        hours = 168
    
    history = await get_metrics_history(db, hours=hours)
    return {"history": history, "hours": hours}


@router.get("/monitoring/alerts")
async def get_active_alerts(current_user: dict = Depends(get_admin_user)):
    """
    Retorna alertas ativos (apenas admin).
    """
    alerts = metrics_collector.check_alerts()
    return {
        "alerts": alerts,
        "total": len(alerts),
        "thresholds": metrics_collector.alert_thresholds
    }


@router.post("/monitoring/test-alert")
async def test_alert_email(current_user: dict = Depends(get_admin_user)):
    """
    Envia email de teste de alerta (apenas admin).
    """
    health = metrics_collector.get_health_status()
    
    # Criar alerta de teste
    test_alerts = [{
        "type": "test_alert",
        "severity": "warning",
        "message": "Este é um email de teste do sistema de monitoramento.",
        "value": 0,
        "threshold": 0
    }]
    
    html = generate_alert_email_html(test_alerts, health)
    
    # Buscar email do admin
    admin_email = current_user.get("email", "")
    
    result = await enviar_email(
        destinatario=admin_email,
        assunto="[TESTE] Alerta de Sistema - Ranking Run Pró",
        html_content=html
    )
    
    if result.get("status") == "success":
        return {"message": "Email de teste enviado com sucesso!", "email": admin_email}
    else:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email: {result.get('message')}")


@router.put("/monitoring/thresholds")
async def update_thresholds(
    thresholds: dict,
    current_user: dict = Depends(get_admin_user)
):
    """
    Atualiza limites de alertas (apenas admin).
    """
    valid_keys = ["cpu_percent", "memory_percent", "error_rate", "response_time_avg", "disk_percent"]
    
    updated = []
    for key, value in thresholds.items():
        if key in valid_keys and isinstance(value, (int, float)) and value > 0:
            metrics_collector.alert_thresholds[key] = value
            updated.append(key)
    
    return {
        "message": "Limites atualizados",
        "updated": updated,
        "current_thresholds": metrics_collector.alert_thresholds
    }


@router.get("/monitoring/endpoints")
async def get_endpoint_stats(current_user: dict = Depends(get_admin_user)):
    """
    Estatísticas por endpoint (apenas admin).
    """
    slowest = metrics_collector.get_slowest_endpoints(20)
    return {
        "endpoints": slowest,
        "total_tracked": len(metrics_collector.endpoint_times)
    }


# ==================== SNAPSHOT MANUAL ====================

@router.post("/monitoring/snapshot")
async def create_snapshot(current_user: dict = Depends(get_admin_user)):
    """
    Cria snapshot manual das métricas (apenas admin).
    """
    await save_metrics_snapshot(db)
    return {"message": "Snapshot criado com sucesso", "timestamp": datetime.now(timezone.utc).isoformat()}


# ==================== CACHE STATS ====================

from services.cache_service import cache_service, invalidate_on_ranking_change

@router.get("/monitoring/cache")
async def get_cache_stats(current_user: dict = Depends(get_admin_user)):
    """
    Retorna estatísticas do cache Redis (apenas admin).
    """
    return cache_service.get_stats()


@router.post("/monitoring/cache/invalidate")
async def invalidate_cache(
    prefix: str = None,
    current_user: dict = Depends(get_admin_user)
):
    """
    Invalida cache (apenas admin).
    prefix: 'ranking', 'liga', 'corridas', 'all' ou None para tudo
    """
    if prefix == 'all' or prefix is None:
        await cache_service.invalidate_all()
        return {"message": "Todo o cache foi invalidado"}
    elif prefix == 'ranking':
        count = await cache_service.invalidate_prefix("cache:ranking:")
        return {"message": f"Cache de ranking invalidado ({count} chaves)"}
    elif prefix == 'liga':
        count = await cache_service.invalidate_prefix("cache:liga:")
        return {"message": f"Cache da liga invalidado ({count} chaves)"}
    elif prefix == 'corridas':
        count = await cache_service.invalidate_prefix("cache:corridas:")
        return {"message": f"Cache de corridas invalidado ({count} chaves)"}
    else:
        return {"message": "Prefixo inválido. Use: ranking, liga, corridas ou all"}
