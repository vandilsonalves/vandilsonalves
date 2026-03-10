# /app/backend/services/monitoring_service.py
"""
Sistema de Monitoramento de Saúde do Backend
- Coleta métricas de CPU, memória, requisições
- Armazena histórico de 7 dias no MongoDB
- Envia alertas por email quando há problemas críticos
"""

import psutil
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import time
import os

# Métricas em tempo real (in-memory)
class MetricsCollector:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.request_times: List[float] = []
        self.endpoint_times: Dict[str, List[float]] = defaultdict(list)
        self.status_codes: Dict[int, int] = defaultdict(int)
        self.start_time = time.time()
        self.last_reset = datetime.now(timezone.utc)
        
        # Limites para alertas
        self.alert_thresholds = {
            "cpu_percent": 90,
            "memory_percent": 85,
            "error_rate": 10,  # % de erros
            "response_time_avg": 5.0,  # segundos
            "disk_percent": 90
        }
        
        # Controle de alertas (evitar spam)
        self.last_alert_time: Dict[str, datetime] = {}
        self.alert_cooldown = timedelta(minutes=15)
    
    def record_request(self, path: str, method: str, status_code: int, duration: float):
        """Registra uma requisição processada"""
        self.request_count += 1
        self.request_times.append(duration)
        self.status_codes[status_code] += 1
        
        # Agrupar por endpoint (sem IDs dinâmicos)
        endpoint = self._normalize_endpoint(path, method)
        self.endpoint_times[endpoint].append(duration)
        
        if status_code >= 400:
            self.error_count += 1
        
        # Manter apenas últimas 1000 requisições em memória
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
        
        for ep in self.endpoint_times:
            if len(self.endpoint_times[ep]) > 100:
                self.endpoint_times[ep] = self.endpoint_times[ep][-100:]
    
    def _normalize_endpoint(self, path: str, method: str) -> str:
        """Normaliza endpoint removendo IDs dinâmicos"""
        import re
        # Substituir UUIDs por {id}
        normalized = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{id}', path)
        # Substituir números por {id}
        normalized = re.sub(r'/\d+', '/{id}', normalized)
        return f"{method} {normalized}"
    
    def get_system_metrics(self) -> Dict:
        """Coleta métricas do sistema"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Conexões de rede
        try:
            connections = len(psutil.net_connections())
        except:
            connections = 0
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "network_connections": connections
        }
    
    def get_request_metrics(self) -> Dict:
        """Calcula métricas de requisições"""
        uptime_seconds = time.time() - self.start_time
        
        avg_response_time = 0
        if self.request_times:
            avg_response_time = sum(self.request_times) / len(self.request_times)
        
        error_rate = 0
        if self.request_count > 0:
            error_rate = (self.error_count / self.request_count) * 100
        
        # Requisições por minuto
        minutes_elapsed = uptime_seconds / 60
        requests_per_minute = self.request_count / max(minutes_elapsed, 1)
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "requests_per_minute": round(requests_per_minute, 2),
            "uptime_seconds": round(uptime_seconds),
            "uptime_formatted": self._format_uptime(uptime_seconds),
            "status_codes": dict(self.status_codes)
        }
    
    def get_slowest_endpoints(self, limit: int = 10) -> List[Dict]:
        """Retorna os endpoints mais lentos"""
        endpoints = []
        for endpoint, times in self.endpoint_times.items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                endpoints.append({
                    "endpoint": endpoint,
                    "avg_time_ms": round(avg_time * 1000, 2),
                    "max_time_ms": round(max_time * 1000, 2),
                    "request_count": len(times)
                })
        
        # Ordenar por tempo médio (mais lento primeiro)
        endpoints.sort(key=lambda x: x["avg_time_ms"], reverse=True)
        return endpoints[:limit]
    
    def _format_uptime(self, seconds: float) -> str:
        """Formata uptime em formato legível"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        
        return " ".join(parts)
    
    def check_alerts(self) -> List[Dict]:
        """Verifica se há condições de alerta"""
        alerts = []
        system = self.get_system_metrics()
        requests = self.get_request_metrics()
        now = datetime.now(timezone.utc)
        
        # CPU alta
        if system["cpu_percent"] > self.alert_thresholds["cpu_percent"]:
            if self._should_send_alert("cpu"):
                alerts.append({
                    "type": "cpu_high",
                    "severity": "critical",
                    "message": f"CPU em {system['cpu_percent']}% (limite: {self.alert_thresholds['cpu_percent']}%)",
                    "value": system["cpu_percent"],
                    "threshold": self.alert_thresholds["cpu_percent"]
                })
        
        # Memória alta
        if system["memory_percent"] > self.alert_thresholds["memory_percent"]:
            if self._should_send_alert("memory"):
                alerts.append({
                    "type": "memory_high",
                    "severity": "critical",
                    "message": f"Memória em {system['memory_percent']}% (limite: {self.alert_thresholds['memory_percent']}%)",
                    "value": system["memory_percent"],
                    "threshold": self.alert_thresholds["memory_percent"]
                })
        
        # Disco cheio
        if system["disk_percent"] > self.alert_thresholds["disk_percent"]:
            if self._should_send_alert("disk"):
                alerts.append({
                    "type": "disk_high",
                    "severity": "warning",
                    "message": f"Disco em {system['disk_percent']}% (limite: {self.alert_thresholds['disk_percent']}%)",
                    "value": system["disk_percent"],
                    "threshold": self.alert_thresholds["disk_percent"]
                })
        
        # Taxa de erros alta
        if requests["error_rate_percent"] > self.alert_thresholds["error_rate"]:
            if self._should_send_alert("error_rate"):
                alerts.append({
                    "type": "error_rate_high",
                    "severity": "critical",
                    "message": f"Taxa de erros em {requests['error_rate_percent']}% (limite: {self.alert_thresholds['error_rate']}%)",
                    "value": requests["error_rate_percent"],
                    "threshold": self.alert_thresholds["error_rate"]
                })
        
        # Tempo de resposta lento
        avg_time_sec = requests["avg_response_time_ms"] / 1000
        if avg_time_sec > self.alert_thresholds["response_time_avg"]:
            if self._should_send_alert("response_time"):
                alerts.append({
                    "type": "slow_response",
                    "severity": "warning",
                    "message": f"Tempo médio de resposta em {requests['avg_response_time_ms']}ms (limite: {self.alert_thresholds['response_time_avg']*1000}ms)",
                    "value": avg_time_sec,
                    "threshold": self.alert_thresholds["response_time_avg"]
                })
        
        return alerts
    
    def _should_send_alert(self, alert_type: str) -> bool:
        """Verifica se deve enviar alerta (evita spam)"""
        now = datetime.now(timezone.utc)
        last = self.last_alert_time.get(alert_type)
        
        if last is None or (now - last) > self.alert_cooldown:
            self.last_alert_time[alert_type] = now
            return True
        return False
    
    def get_health_status(self) -> Dict:
        """Retorna status geral de saúde"""
        system = self.get_system_metrics()
        requests = self.get_request_metrics()
        alerts = self.check_alerts()
        
        # Determinar status geral
        status = "healthy"
        if any(a["severity"] == "warning" for a in alerts):
            status = "degraded"
        if any(a["severity"] == "critical" for a in alerts):
            status = "unhealthy"
        
        return {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": system,
            "requests": requests,
            "slowest_endpoints": self.get_slowest_endpoints(5),
            "active_alerts": alerts
        }


# Instância global do coletor
metrics_collector = MetricsCollector()


async def save_metrics_snapshot(db):
    """Salva snapshot das métricas no MongoDB"""
    health = metrics_collector.get_health_status()
    
    snapshot = {
        "timestamp": datetime.now(timezone.utc),
        "status": health["status"],
        "cpu_percent": health["system"]["cpu_percent"],
        "memory_percent": health["system"]["memory_percent"],
        "disk_percent": health["system"]["disk_percent"],
        "total_requests": health["requests"]["total_requests"],
        "error_rate": health["requests"]["error_rate_percent"],
        "avg_response_time_ms": health["requests"]["avg_response_time_ms"],
        "requests_per_minute": health["requests"]["requests_per_minute"]
    }
    
    await db.metrics_history.insert_one(snapshot)
    
    # Limpar métricas antigas (mais de 7 dias)
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    await db.metrics_history.delete_many({"timestamp": {"$lt": cutoff}})


async def get_metrics_history(db, hours: int = 24) -> List[Dict]:
    """Busca histórico de métricas"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    cursor = db.metrics_history.find(
        {"timestamp": {"$gte": cutoff}},
        {"_id": 0}
    ).sort("timestamp", 1)
    
    history = await cursor.to_list(None)
    
    # Converter datetime para string ISO
    for item in history:
        if isinstance(item.get("timestamp"), datetime):
            item["timestamp"] = item["timestamp"].isoformat()
    
    return history


def generate_alert_email_html(alerts: List[Dict], health: Dict) -> str:
    """Gera HTML do email de alerta"""
    alerts_html = ""
    for alert in alerts:
        color = "#dc2626" if alert["severity"] == "critical" else "#f59e0b"
        alerts_html += f"""
        <div style="background: {color}15; border-left: 4px solid {color}; padding: 12px; margin: 8px 0; border-radius: 4px;">
            <strong style="color: {color};">{alert['type'].upper()}</strong>
            <p style="margin: 4px 0 0 0; color: #374151;">{alert['message']}</p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">⚠️ Alerta de Sistema</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0;">Ranking Run Pró - Monitoramento</p>
            </div>
            
            <div style="padding: 24px;">
                <h2 style="color: #111827; margin: 0 0 16px 0; font-size: 18px;">Alertas Ativos</h2>
                {alerts_html}
                
                <h2 style="color: #111827; margin: 24px 0 16px 0; font-size: 18px;">Status do Sistema</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">CPU</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">{health['system']['cpu_percent']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">Memória</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">{health['system']['memory_percent']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">Disco</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">{health['system']['disk_percent']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">Taxa de Erros</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">{health['requests']['error_rate_percent']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">Tempo de Resposta</td>
                        <td style="padding: 8px; text-align: right; font-weight: 600;">{health['requests']['avg_response_time_ms']}ms</td>
                    </tr>
                </table>
                
                <div style="margin-top: 24px; padding: 16px; background: #f9fafb; border-radius: 8px; text-align: center;">
                    <p style="margin: 0; color: #6b7280; font-size: 14px;">
                        Uptime: {health['requests']['uptime_formatted']} | 
                        Requisições: {health['requests']['total_requests']}
                    </p>
                </div>
            </div>
            
            <div style="background: #f9fafb; padding: 16px; text-align: center; border-top: 1px solid #e5e7eb;">
                <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                    Este é um alerta automático do sistema de monitoramento.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
