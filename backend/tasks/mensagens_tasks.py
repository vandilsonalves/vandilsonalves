# /app/backend/tasks/mensagens_tasks.py
"""Task para processar mensagens agendadas"""

from celery_app import celery_app
import requests
import os


@celery_app.task(name='tasks.mensagens_tasks.processar_mensagens_agendadas')
def processar_mensagens_agendadas():
    """Verifica e envia mensagens agendadas cujo horário já passou"""
    try:
        response = requests.post(
            "http://localhost:8001/api/admin/mensagens/processar-agendadas",
            timeout=30
        )
        if response.ok:
            data = response.json()
            if data.get("processadas", 0) > 0:
                print(f"[Mensagens] {data['processadas']} mensagem(ns) agendada(s) processada(s)")
            return data
    except Exception as e:
        print(f"[Mensagens] Erro ao processar agendadas: {e}")
        return {"error": str(e)}
