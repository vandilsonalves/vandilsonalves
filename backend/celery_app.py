# /app/backend/celery_app.py
"""
Configuração do Celery para processamento de tarefas em background
Broker: Redis (localhost:6379)
"""

from celery import Celery
import os

# Configuração do Redis como broker
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Criar instância do Celery
celery_app = Celery(
    'ranking_run_pro',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks.ranking_tasks', 'tasks.email_tasks', 'tasks.report_tasks', 'tasks.mensagens_tasks']
)

# Configurações do Celery
celery_app.conf.update(
    # Resultados expiram em 1 hora
    result_expires=3600,
    
    # Timezone
    timezone='America/Sao_Paulo',
    enable_utc=True,
    
    # Serialização
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Configurações de retry
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Limitar concorrência
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
    
    # Rotas de tarefas por prioridade
    task_routes={
        'tasks.ranking_tasks.*': {'queue': 'ranking'},
        'tasks.email_tasks.*': {'queue': 'email'},
        'tasks.report_tasks.*': {'queue': 'reports'},
    },
    
    # Filas padrão
    task_default_queue='default',
    
    # Beat schedule para tarefas periódicas
    beat_schedule={
        'snapshot-metricas-5min': {
            'task': 'tasks.ranking_tasks.save_metrics_snapshot_task',
            'schedule': 300.0,  # 5 minutos
        },
        'verificar-alertas-1min': {
            'task': 'tasks.ranking_tasks.check_alerts_task',
            'schedule': 60.0,  # 1 minuto
        },
        'limpar-cache-expirado-1h': {
            'task': 'tasks.ranking_tasks.cleanup_expired_cache',
            'schedule': 3600.0,  # 1 hora
        },
        'processar-mensagens-agendadas-1min': {
            'task': 'tasks.mensagens_tasks.processar_mensagens_agendadas',
            'schedule': 60.0,  # 1 minuto
        },
    }
)

# Configuração de logging
celery_app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
celery_app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
