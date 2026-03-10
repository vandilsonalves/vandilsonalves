# /app/backend/routes/celery_routes.py
"""
Endpoints para gerenciamento de tarefas Celery
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime

from routes.auth_routes import get_admin_user

router = APIRouter(tags=["Celery Tasks"])


# ==================== STATUS DO CELERY ====================

@router.get("/celery/status")
async def get_celery_status(admin: dict = Depends(get_admin_user)):
    """
    Retorna status do Celery e workers
    """
    try:
        from celery_app import celery_app
        
        # Verificar workers ativos
        inspect = celery_app.control.inspect()
        active_workers = inspect.active() or {}
        stats = inspect.stats() or {}
        
        # Buscar tarefas agendadas
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}
        
        return {
            "status": "online" if active_workers else "offline",
            "workers": list(active_workers.keys()),
            "active_tasks": sum(len(tasks) for tasks in active_workers.values()),
            "scheduled_tasks": sum(len(tasks) for tasks in scheduled.values()),
            "reserved_tasks": sum(len(tasks) for tasks in reserved.values()),
            "stats": stats
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "workers": [],
            "tip": "Verifique se o worker Celery está rodando: celery -A celery_app worker"
        }


# ==================== DISPARAR TAREFAS ====================

@router.post("/celery/tasks/recalcular-ranking")
async def disparar_recalculo_ranking(
    tipo: str = "geral",
    admin: dict = Depends(get_admin_user)
):
    """
    Dispara recálculo de ranking em background
    tipo: 'geral', 'povao'
    """
    try:
        from tasks.ranking_tasks import recalcular_ranking_task
        
        task = recalcular_ranking_task.delay(tipo)
        
        return {
            "message": f"Recálculo de ranking '{tipo}' iniciado",
            "task_id": task.id,
            "status": "PENDING"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/celery/tasks/verificar-conquistas/{usuario_id}")
async def disparar_verificacao_conquistas(
    usuario_id: str,
    admin: dict = Depends(get_admin_user)
):
    """
    Dispara verificação de conquistas para um atleta
    """
    try:
        from tasks.ranking_tasks import verificar_conquistas_task
        
        task = verificar_conquistas_task.delay(usuario_id)
        
        return {
            "message": f"Verificação de conquistas iniciada para {usuario_id}",
            "task_id": task.id,
            "status": "PENDING"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/celery/tasks/enviar-aniversarios")
async def disparar_emails_aniversario(
    data: str = None,
    admin: dict = Depends(get_admin_user)
):
    """
    Dispara envio de emails de aniversário
    data: formato MM-DD (ex: '03-10' para 10 de março)
    """
    try:
        from tasks.email_tasks import enviar_emails_aniversario_task
        
        task = enviar_emails_aniversario_task.delay(data)
        
        return {
            "message": f"Envio de aniversários iniciado" + (f" para {data}" if data else ""),
            "task_id": task.id,
            "status": "PENDING"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/celery/tasks/gerar-relatorio")
async def disparar_geracao_relatorio(
    tipo: str = "ranking",
    subtipo: str = "geral",
    mes: int = None,
    ano: int = None,
    admin: dict = Depends(get_admin_user)
):
    """
    Dispara geração de relatório em background
    tipo: 'ranking', 'atletas', 'corridas'
    subtipo: para ranking - 'geral', 'povao'
    """
    try:
        from tasks.report_tasks import (
            gerar_relatorio_ranking_task,
            gerar_relatorio_atletas_task,
            gerar_relatorio_corridas_task
        )
        
        if tipo == "ranking":
            task = gerar_relatorio_ranking_task.delay(subtipo)
        elif tipo == "atletas":
            task = gerar_relatorio_atletas_task.delay({})
        elif tipo == "corridas":
            task = gerar_relatorio_corridas_task.delay(mes, ano)
        else:
            raise HTTPException(status_code=400, detail="Tipo de relatório inválido")
        
        return {
            "message": f"Geração de relatório '{tipo}' iniciada",
            "task_id": task.id,
            "status": "PENDING"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CONSULTAR STATUS DA TAREFA ====================

@router.get("/celery/tasks/{task_id}")
async def get_task_status(task_id: str, admin: dict = Depends(get_admin_user)):
    """
    Consulta status de uma tarefa específica
    """
    try:
        from celery_app import celery_app
        
        result = celery_app.AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "status": result.status,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
        }
        
        if result.ready():
            if result.successful():
                response["result"] = result.result
            else:
                response["error"] = str(result.result)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CANCELAR TAREFA ====================

@router.delete("/celery/tasks/{task_id}")
async def cancel_task(task_id: str, admin: dict = Depends(get_admin_user)):
    """
    Cancela/revoga uma tarefa pendente
    """
    try:
        from celery_app import celery_app
        
        celery_app.control.revoke(task_id, terminate=True)
        
        return {
            "message": f"Tarefa {task_id} cancelada",
            "task_id": task_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LISTAR TAREFAS ATIVAS ====================

@router.get("/celery/tasks")
async def list_active_tasks(admin: dict = Depends(get_admin_user)):
    """
    Lista tarefas ativas e reservadas
    """
    try:
        from celery_app import celery_app
        
        inspect = celery_app.control.inspect()
        
        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}
        
        all_tasks = []
        
        for worker, tasks in active.items():
            for task in tasks:
                all_tasks.append({
                    "worker": worker,
                    "status": "ACTIVE",
                    **task
                })
        
        for worker, tasks in scheduled.items():
            for task in tasks:
                all_tasks.append({
                    "worker": worker,
                    "status": "SCHEDULED",
                    **task
                })
        
        for worker, tasks in reserved.items():
            for task in tasks:
                all_tasks.append({
                    "worker": worker,
                    "status": "RESERVED",
                    **task
                })
        
        return {
            "total": len(all_tasks),
            "tasks": all_tasks
        }
    
    except Exception as e:
        return {
            "total": 0,
            "tasks": [],
            "error": str(e)
        }


# ==================== PURGAR FILAS ====================

@router.post("/celery/purge")
async def purge_queues(queue: str = None, admin: dict = Depends(get_admin_user)):
    """
    Limpa filas de tarefas pendentes
    queue: 'ranking', 'email', 'reports', 'default' ou None para todas
    """
    try:
        from celery_app import celery_app
        
        if queue:
            celery_app.control.purge()
        else:
            celery_app.control.purge()
        
        return {
            "message": f"Fila(s) {'todas' if not queue else queue} limpas",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
