# /app/backend/services/strava_sync_scheduler.py
# Scheduler para sincronização automática do Strava

import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("strava_sync")

# Instância global do scheduler
scheduler = None


async def sync_all_strava_users():
    """
    Sincroniza as atividades do Strava de todos os usuários conectados.
    Executado automaticamente a cada hora.
    """
    from config import db
    from services.strava_service import import_strava_activities, refresh_access_token
    import time
    
    logger.info(f"[{datetime.now()}] Iniciando sincronização automática do Strava...")
    
    try:
        # Buscar todos os usuários com Strava conectado
        usuarios = await db.usuarios.find(
            {"strava_conectado": True},
            {
                "id": 1,
                "nome": 1,
                "strava_access_token": 1,
                "strava_refresh_token": 1,
                "strava_token_expires_at": 1
            }
        ).to_list(500)
        
        if not usuarios:
            logger.info("Nenhum usuário com Strava conectado encontrado.")
            return
        
        logger.info(f"Encontrados {len(usuarios)} usuários para sincronizar.")
        
        total_importadas = 0
        total_atualizadas = 0
        erros = 0
        
        for usuario in usuarios:
            try:
                usuario_id = usuario["id"]
                access_token = usuario.get("strava_access_token")
                refresh_token = usuario.get("strava_refresh_token")
                token_expires_at = usuario.get("strava_token_expires_at", 0)
                
                if not access_token or not refresh_token:
                    logger.warning(f"Usuário {usuario.get('nome')} sem tokens válidos, pulando...")
                    continue
                
                # Verificar se token expirou e renovar
                current_time = int(time.time())
                if token_expires_at <= current_time:
                    logger.info(f"Renovando token para {usuario.get('nome')}...")
                    try:
                        new_tokens = refresh_access_token(refresh_token)
                        access_token = new_tokens["access_token"]
                        refresh_token = new_tokens["refresh_token"]
                        token_expires_at = new_tokens["expires_at"]
                        
                        # Atualizar tokens no banco
                        await db.usuarios.update_one(
                            {"id": usuario_id},
                            {"$set": {
                                "strava_access_token": access_token,
                                "strava_refresh_token": refresh_token,
                                "strava_token_expires_at": token_expires_at
                            }}
                        )
                    except Exception as e:
                        logger.error(f"Erro ao renovar token de {usuario.get('nome')}: {e}")
                        erros += 1
                        continue
                
                # Importar atividades (últimas 20 apenas para sync periódico)
                results = await import_strava_activities(
                    db=db,
                    usuario_id=usuario_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_expires_at=token_expires_at,
                    max_activities=20
                )
                
                total_importadas += results.get("total_importadas", 0)
                total_atualizadas += results.get("total_atualizadas", 0)
                
                logger.info(f"  ✓ {usuario.get('nome')}: {results.get('total_importadas', 0)} novas, {results.get('total_atualizadas', 0)} atualizadas")
                
                # Pequeno delay para não sobrecarregar a API do Strava
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao sincronizar {usuario.get('nome', 'desconhecido')}: {e}")
                erros += 1
        
        # Registrar log da sincronização
        await db.strava_sync_logs.insert_one({
            "data": datetime.now(timezone.utc).isoformat(),
            "usuarios_sincronizados": len(usuarios) - erros,
            "total_importadas": total_importadas,
            "total_atualizadas": total_atualizadas,
            "erros": erros
        })
        
        logger.info(f"[{datetime.now()}] Sincronização concluída! "
                   f"{total_importadas} novas atividades, "
                   f"{total_atualizadas} atualizadas, "
                   f"{erros} erros.")
        
    except Exception as e:
        logger.error(f"Erro geral na sincronização automática: {e}")


def start_scheduler():
    """
    Inicia o scheduler para sincronização automática.
    """
    global scheduler
    
    if scheduler is not None:
        logger.info("Scheduler já está rodando.")
        return scheduler
    
    scheduler = AsyncIOScheduler()
    
    # Adicionar job de sincronização a cada hora
    scheduler.add_job(
        sync_all_strava_users,
        trigger=IntervalTrigger(hours=1),
        id="strava_sync_hourly",
        name="Sincronização Strava Horária",
        replace_existing=True,
        max_instances=1  # Evita execuções paralelas
    )
    
    # Também executar 5 minutos após iniciar (para pegar dados recentes)
    scheduler.add_job(
        sync_all_strava_users,
        trigger="date",
        run_date=datetime.now(timezone.utc).replace(second=0, microsecond=0),
        id="strava_sync_startup",
        name="Sincronização Strava Inicial"
    )
    
    scheduler.start()
    logger.info("✅ Scheduler de sincronização do Strava iniciado! (Execução a cada 1 hora)")
    
    return scheduler


def stop_scheduler():
    """
    Para o scheduler.
    """
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler parado.")


def get_scheduler_status():
    """
    Retorna o status do scheduler.
    """
    global scheduler
    if scheduler is None:
        return {"running": False, "jobs": []}
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None
        })
    
    return {
        "running": scheduler.running,
        "jobs": jobs
    }
