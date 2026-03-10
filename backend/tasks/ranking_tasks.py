# /app/backend/tasks/ranking_tasks.py
"""
Tarefas de Ranking para processamento em background
"""

from celery_app import celery_app
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

# Conexão MongoDB para tarefas Celery (síncrona)
def get_db():
    from pymongo import MongoClient
    client = MongoClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    return client[os.environ.get('DB_NAME', 'test_database')]


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def recalcular_ranking_task(self, tipo: str = "geral"):
    """
    Recalcula rankings em background
    tipo: 'geral', 'povao', 'semanal', 'mensal'
    """
    try:
        logger.info(f"🔄 Iniciando recálculo de ranking: {tipo}")
        db = get_db()
        
        if tipo == "povao":
            recalcular_ranking_povao_sync(db)
        else:
            recalcular_ranking_geral_sync(db)
        
        # Invalidar cache após recálculo
        invalidar_cache_ranking()
        
        logger.info(f"✅ Ranking {tipo} recalculado com sucesso!")
        return {"status": "success", "tipo": tipo}
    
    except Exception as e:
        logger.error(f"❌ Erro ao recalcular ranking {tipo}: {e}")
        raise self.retry(exc=e)


def recalcular_ranking_geral_sync(db):
    """Recalcula ranking geral (síncrono para Celery)"""
    from datetime import datetime
    
    ano_atual = datetime.now().year
    
    # Buscar todas as corridas do ano
    corridas = list(db.corridas.find({
        "ano": ano_atual,
        "modalidade": {"$ne": "povao_pace_livre"}
    }))
    
    # Agrupar por usuário
    pontos_por_usuario = {}
    for corrida in corridas:
        uid = corrida["usuario_id"]
        if uid not in pontos_por_usuario:
            pontos_por_usuario[uid] = {"pontos": 0, "corridas": 0}
        pontos_por_usuario[uid]["pontos"] += corrida.get("pontos", 0)
        pontos_por_usuario[uid]["corridas"] += 1
    
    # Atualizar ranking_anual
    for uid, dados in pontos_por_usuario.items():
        db.ranking_anual.update_one(
            {"usuario_id": uid, "ano": ano_atual},
            {"$set": {
                "pontos_total": dados["pontos"],
                "total_corridas": dados["corridas"],
                "atualizado_em": datetime.now().isoformat()
            }},
            upsert=True
        )
    
    logger.info(f"Ranking geral atualizado: {len(pontos_por_usuario)} atletas")


def recalcular_ranking_povao_sync(db):
    """Recalcula ranking do povão (síncrono para Celery)"""
    from datetime import datetime
    
    # Buscar corridas do povão
    corridas = list(db.corridas.find({
        "modalidade": "povao_pace_livre"
    }))
    
    # Agrupar por usuário
    pontos_por_usuario = {}
    for corrida in corridas:
        uid = corrida["usuario_id"]
        if uid not in pontos_por_usuario:
            pontos_por_usuario[uid] = {"pontos": 0, "participacoes": 0}
        pontos_por_usuario[uid]["pontos"] += corrida.get("pontos_povao", 0)
        pontos_por_usuario[uid]["participacoes"] += 1
    
    # Atualizar ranking_povao
    for uid, dados in pontos_por_usuario.items():
        db.ranking_povao.update_one(
            {"usuario_id": uid},
            {"$set": {
                "pontos_total": dados["pontos"],
                "total_participacoes": dados["participacoes"],
                "atualizado_em": datetime.now().isoformat()
            }},
            upsert=True
        )
    
    logger.info(f"Ranking Povão atualizado: {len(pontos_por_usuario)} atletas")


def invalidar_cache_ranking():
    """Invalida cache de rankings no Redis"""
    import redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        keys = r.keys("cache:ranking:*")
        if keys:
            r.delete(*keys)
            logger.info(f"🗑️ Cache invalidado: {len(keys)} chaves de ranking")
    except Exception as e:
        logger.warning(f"Erro ao invalidar cache: {e}")


@celery_app.task(bind=True, max_retries=2)
def verificar_conquistas_task(self, usuario_id: str):
    """Verifica e atribui conquistas a um atleta em background"""
    try:
        logger.info(f"🏆 Verificando conquistas para usuário: {usuario_id}")
        db = get_db()
        
        usuario = db.usuarios.find_one({"id": usuario_id})
        if not usuario:
            return {"status": "error", "message": "Usuário não encontrado"}
        
        corridas = list(db.corridas.find({"usuario_id": usuario_id}))
        total_corridas = len(corridas)
        
        conquistas_atuais = list(db.conquistas_atleta.find({"usuario_id": usuario_id}))
        codigos_atuais = [c["conquista_codigo"] for c in conquistas_atuais]
        
        novas = []
        
        # Verificar conquistas por número de corridas
        conquistas_corridas = [
            ("10_corridas", 10),
            ("12_resultados", 12),
            ("20_resultados", 20),
            ("30_resultados", 30),
        ]
        
        for codigo, meta in conquistas_corridas:
            if codigo not in codigos_atuais and total_corridas >= meta:
                novas.append(codigo)
        
        # Verificar pódio
        if "podio" not in codigos_atuais:
            if any(c.get("colocacao", 99) <= 3 for c in corridas):
                novas.append("podio")
        
        # Verificar primeiro lugar
        if "primeiro_lugar" not in codigos_atuais:
            if any(c.get("colocacao") == 1 for c in corridas):
                novas.append("primeiro_lugar")
        
        # Registrar novas conquistas
        from datetime import datetime
        for codigo in novas:
            db.conquistas_atleta.insert_one({
                "id": f"conquista_{usuario_id}_{codigo}",
                "usuario_id": usuario_id,
                "conquista_codigo": codigo,
                "data_conquista": datetime.now().isoformat()
            })
        
        logger.info(f"✅ {len(novas)} novas conquistas para {usuario_id}")
        return {"status": "success", "novas_conquistas": novas}
    
    except Exception as e:
        logger.error(f"❌ Erro ao verificar conquistas: {e}")
        raise self.retry(exc=e)


@celery_app.task
def save_metrics_snapshot_task():
    """Salva snapshot de métricas (tarefa periódica)"""
    try:
        import psutil
        from datetime import datetime
        
        db = get_db()
        
        snapshot = {
            "timestamp": datetime.now(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        }
        
        db.metrics_history.insert_one(snapshot)
        
        # Limpar métricas antigas (> 7 dias)
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=7)
        deleted = db.metrics_history.delete_many({"timestamp": {"$lt": cutoff}})
        
        logger.debug(f"📊 Snapshot salvo, {deleted.deleted_count} antigos removidos")
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Erro ao salvar snapshot: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task
def check_alerts_task():
    """Verifica alertas do sistema (tarefa periódica)"""
    try:
        import psutil
        
        alerts = []
        
        cpu = psutil.cpu_percent()
        if cpu > 90:
            alerts.append({"type": "cpu_high", "value": cpu})
        
        mem = psutil.virtual_memory().percent
        if mem > 85:
            alerts.append({"type": "memory_high", "value": mem})
        
        disk = psutil.disk_usage('/').percent
        if disk > 90:
            alerts.append({"type": "disk_high", "value": disk})
        
        if alerts:
            logger.warning(f"⚠️ {len(alerts)} alertas ativos: {alerts}")
            # Aqui poderia chamar task de email
        
        return {"status": "success", "alerts": len(alerts)}
    
    except Exception as e:
        logger.error(f"Erro ao verificar alertas: {e}")
        return {"status": "error"}


@celery_app.task
def cleanup_expired_cache():
    """Limpa cache expirado (tarefa periódica)"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Redis já remove automaticamente chaves expiradas
        # Mas podemos forçar uma limpeza de memória
        info = r.info('memory')
        
        logger.info(f"🧹 Cache cleanup - Memória: {info.get('used_memory_human', 'N/A')}")
        return {"status": "success", "memory": info.get('used_memory_human')}
    
    except Exception as e:
        logger.error(f"Erro no cleanup: {e}")
        return {"status": "error"}
