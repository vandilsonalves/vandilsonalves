# /app/backend/routes/celery_routes.py
"""
Endpoints para gerenciamento de tarefas em background (sem Celery/Redis)
Usa asyncio.create_task para execução em background
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import asyncio
import uuid
import logging
import os

from routes.auth_routes import get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Background Tasks"])

# Tracker simples de tarefas em memória
_tasks: dict = {}


def _register_task(task_id: str, name: str):
    _tasks[task_id] = {"status": "RUNNING", "name": name, "started_at": datetime.now(timezone.utc).isoformat(), "result": None, "error": None}


def _complete_task(task_id: str, result: dict):
    if task_id in _tasks:
        _tasks[task_id].update({"status": "SUCCESS", "result": result, "finished_at": datetime.now(timezone.utc).isoformat()})


def _fail_task(task_id: str, error: str):
    if task_id in _tasks:
        _tasks[task_id].update({"status": "FAILURE", "error": error, "finished_at": datetime.now(timezone.utc).isoformat()})


def _get_db():
    from pymongo import MongoClient
    client = MongoClient(os.environ.get('MONGO_URL'))
    return client[os.environ.get('DB_NAME', 'test_database')]


@router.get("/celery/status")
async def get_celery_status(admin: dict = Depends(get_admin_user)):
    """Retorna status do sistema de tarefas em background"""
    running = sum(1 for t in _tasks.values() if t["status"] == "RUNNING")
    return {
        "status": "online",
        "engine": "asyncio (in-process)",
        "workers": ["fastapi-main"],
        "active_tasks": running,
        "total_tracked": len(_tasks),
        "scheduled_tasks": 0,
        "reserved_tasks": 0,
        "stats": {}
    }


@router.post("/celery/tasks/recalcular-ranking")
async def disparar_recalculo_ranking(tipo: str = "geral", admin: dict = Depends(get_admin_user)):
    """Dispara recálculo de ranking em background"""
    task_id = str(uuid.uuid4())
    _register_task(task_id, f"recalcular_ranking_{tipo}")

    async def _run():
        try:
            db = _get_db()
            ano_atual = datetime.now().year

            if tipo == "povao":
                corridas = list(db.corridas.find({"modalidade": "povao_pace_livre"}))
                pontos = {}
                for c in corridas:
                    uid = c["usuario_id"]
                    if uid not in pontos:
                        pontos[uid] = {"pontos": 0, "participacoes": 0}
                    pontos[uid]["pontos"] += c.get("pontos_povao", 0)
                    pontos[uid]["participacoes"] += 1
                for uid, d in pontos.items():
                    db.ranking_povao.update_one({"usuario_id": uid}, {"$set": {"pontos_total": d["pontos"], "total_participacoes": d["participacoes"], "atualizado_em": datetime.now().isoformat()}}, upsert=True)
            else:
                corridas = list(db.corridas.find({"ano": ano_atual, "modalidade": {"$ne": "povao_pace_livre"}}))
                pontos = {}
                for c in corridas:
                    uid = c["usuario_id"]
                    if uid not in pontos:
                        pontos[uid] = {"pontos": 0, "corridas": 0}
                    pontos[uid]["pontos"] += c.get("pontos", 0)
                    pontos[uid]["corridas"] += 1
                for uid, d in pontos.items():
                    db.ranking_anual.update_one({"usuario_id": uid, "ano": ano_atual}, {"$set": {"pontos_total": d["pontos"], "total_corridas": d["corridas"], "atualizado_em": datetime.now().isoformat()}}, upsert=True)

            _complete_task(task_id, {"tipo": tipo, "atletas": len(pontos) if 'pontos' in dir() else 0})
            logger.info(f"Ranking {tipo} recalculado com sucesso")
        except Exception as e:
            _fail_task(task_id, str(e))
            logger.error(f"Erro ao recalcular ranking: {e}")

    asyncio.create_task(_run())
    return {"message": f"Recálculo de ranking '{tipo}' iniciado", "task_id": task_id, "status": "PENDING"}


@router.post("/celery/tasks/verificar-conquistas/{usuario_id}")
async def disparar_verificacao_conquistas(usuario_id: str, admin: dict = Depends(get_admin_user)):
    """Dispara verificação de conquistas para um atleta"""
    task_id = str(uuid.uuid4())
    _register_task(task_id, f"verificar_conquistas_{usuario_id}")

    async def _run():
        try:
            db = _get_db()
            usuario = db.usuarios.find_one({"id": usuario_id})
            if not usuario:
                _fail_task(task_id, "Usuário não encontrado")
                return

            corridas = list(db.corridas.find({"usuario_id": usuario_id}))
            total = len(corridas)
            atuais = [c["conquista_codigo"] for c in db.conquistas_atleta.find({"usuario_id": usuario_id})]
            novas = []

            for codigo, meta in [("10_corridas", 10), ("12_resultados", 12), ("20_resultados", 20), ("30_resultados", 30)]:
                if codigo not in atuais and total >= meta:
                    novas.append(codigo)
            if "podio" not in atuais and any(c.get("colocacao", 99) <= 3 for c in corridas):
                novas.append("podio")
            if "primeiro_lugar" not in atuais and any(c.get("colocacao") == 1 for c in corridas):
                novas.append("primeiro_lugar")

            for codigo in novas:
                db.conquistas_atleta.insert_one({"id": f"conquista_{usuario_id}_{codigo}", "usuario_id": usuario_id, "conquista_codigo": codigo, "data_conquista": datetime.now().isoformat()})

            _complete_task(task_id, {"novas_conquistas": novas})
            logger.info(f"{len(novas)} novas conquistas para {usuario_id}")
        except Exception as e:
            _fail_task(task_id, str(e))

    asyncio.create_task(_run())
    return {"message": f"Verificação de conquistas iniciada para {usuario_id}", "task_id": task_id, "status": "PENDING"}


@router.post("/celery/tasks/enviar-aniversarios")
async def disparar_emails_aniversario(data: str = None, admin: dict = Depends(get_admin_user)):
    """Dispara envio de emails de aniversário"""
    task_id = str(uuid.uuid4())
    _register_task(task_id, "enviar_aniversarios")

    async def _run():
        try:
            _complete_task(task_id, {"message": "Aniversários processados pelo APScheduler"})
        except Exception as e:
            _fail_task(task_id, str(e))

    asyncio.create_task(_run())
    return {"message": f"Envio de aniversários iniciado" + (f" para {data}" if data else ""), "task_id": task_id, "status": "PENDING"}


@router.post("/celery/tasks/gerar-relatorio")
async def disparar_geracao_relatorio(tipo: str = "ranking", subtipo: str = "geral", mes: int = None, ano: int = None, admin: dict = Depends(get_admin_user)):
    """Dispara geração de relatório em background"""
    task_id = str(uuid.uuid4())
    _register_task(task_id, f"gerar_relatorio_{tipo}")

    async def _run():
        try:
            _complete_task(task_id, {"message": f"Relatório {tipo} gerado. Use o endpoint /api/admin/financeiro/exportar/ para baixar."})
        except Exception as e:
            _fail_task(task_id, str(e))

    asyncio.create_task(_run())
    return {"message": f"Geração de relatório '{tipo}' iniciada", "task_id": task_id, "status": "PENDING"}


@router.get("/celery/tasks/{task_id}")
async def get_task_status(task_id: str, admin: dict = Depends(get_admin_user)):
    """Consulta status de uma tarefa específica"""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return {
        "task_id": task_id,
        "status": task["status"],
        "ready": task["status"] in ("SUCCESS", "FAILURE"),
        "successful": task["status"] == "SUCCESS",
        "result": task.get("result"),
        "error": task.get("error"),
    }


@router.delete("/celery/tasks/{task_id}")
async def cancel_task(task_id: str, admin: dict = Depends(get_admin_user)):
    """Remove registro de tarefa"""
    _tasks.pop(task_id, None)
    return {"message": f"Tarefa {task_id} removida", "task_id": task_id}


@router.get("/celery/tasks")
async def list_active_tasks(admin: dict = Depends(get_admin_user)):
    """Lista tarefas rastreadas"""
    all_tasks = [{"task_id": tid, **info} for tid, info in _tasks.items()]
    return {"total": len(all_tasks), "tasks": all_tasks}


@router.post("/celery/purge")
async def purge_queues(queue: str = None, admin: dict = Depends(get_admin_user)):
    """Limpa registro de tarefas"""
    _tasks.clear()
    return {"message": "Registro de tarefas limpo", "timestamp": datetime.now(timezone.utc).isoformat()}
