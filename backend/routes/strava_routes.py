# /app/backend/routes/strava_routes.py
# Rotas de integração com Strava API

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from typing import Optional
from datetime import datetime, timezone
import os
import uuid

from config import db
from routes.auth_routes import get_current_user, require_premium_access, get_admin_user
from services.strava_service import (
    get_authorization_url,
    exchange_code_for_token,
    refresh_access_token,
    get_athlete_info,
    import_strava_activities
)

router = APIRouter()

# URL do frontend para redirecionamento após autenticação
FRONTEND_URL = os.environ.get("FRONTEND_URL") or os.environ.get("APP_URL") or os.environ.get("REACT_APP_BACKEND_URL", "")


@router.get("/strava/authorize")
async def strava_authorize(current_user: dict = Depends(get_current_user)):
    """
    Inicia o fluxo de autenticação OAuth2 do Strava.
    Redireciona o usuário para a página de autorização do Strava.
    """
    # Callback URL para o Strava redirecionar após autorização
    callback_url = f"{FRONTEND_URL}/api/strava/callback"
    
    # Gerar URL de autorização
    auth_url = get_authorization_url(callback_url)
    
    # Salvar state para verificação (usando user_id como state)
    await db.strava_auth_states.insert_one({
        "state": current_user["id"],
        "usuario_id": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": datetime.now(timezone.utc).timestamp() + 600  # 10 minutos
    })
    
    # Adicionar state à URL
    auth_url_with_state = f"{auth_url}&state={current_user['id']}"
    
    return {"auth_url": auth_url_with_state}


@router.get("/strava/callback")
async def strava_callback(
    code: str = Query(..., description="Código de autorização do Strava"),
    state: Optional[str] = Query(None, description="State para verificação"),
    scope: Optional[str] = Query(None, description="Escopos concedidos"),
    error: Optional[str] = Query(None, description="Erro se autorização negada")
):
    """
    Callback do OAuth2 do Strava.
    Recebe o código de autorização e troca por tokens.
    """
    # Verificar se houve erro (usuário negou acesso)
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/perfil?strava_error={error}"
        )
    
    # Verificar state
    if not state:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/perfil?strava_error=state_missing"
        )
    
    # Buscar state salvo
    saved_state = await db.strava_auth_states.find_one({"state": state})
    if not saved_state:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/perfil?strava_error=invalid_state"
        )
    
    # Limpar state usado
    await db.strava_auth_states.delete_one({"state": state})
    
    usuario_id = saved_state["usuario_id"]
    
    try:
        # Trocar código por tokens
        token_data = exchange_code_for_token(code)
        
        # Extrair dados do atleta
        athlete = token_data.get("athlete", {})
        
        # Salvar tokens e dados do Strava no usuário
        await db.usuarios.update_one(
            {"id": usuario_id},
            {"$set": {
                "strava_conectado": True,
                "strava_athlete_id": athlete.get("id"),
                "strava_username": athlete.get("username"),
                "strava_firstname": athlete.get("firstname"),
                "strava_lastname": athlete.get("lastname"),
                "strava_profile_picture": athlete.get("profile"),
                "strava_city": athlete.get("city"),
                "strava_state": athlete.get("state"),
                "strava_country": athlete.get("country"),
                "strava_access_token": token_data.get("access_token"),
                "strava_refresh_token": token_data.get("refresh_token"),
                "strava_token_expires_at": token_data.get("expires_at"),
                "strava_conectado_em": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Redirecionar para o perfil com sucesso
        return RedirectResponse(
            url=f"{FRONTEND_URL}/perfil?strava_success=true"
        )
        
    except Exception as e:
        print(f"Erro no callback Strava: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/perfil?strava_error=token_exchange_failed"
        )


@router.get("/strava/status")
async def strava_status(current_user: dict = Depends(get_current_user)):
    """
    Retorna o status da conexão com o Strava do usuário.
    """
    usuario = await db.usuarios.find_one(
        {"id": current_user["id"]},
        {"_id": 0, "strava_conectado": 1, "strava_username": 1, 
         "strava_firstname": 1, "strava_lastname": 1,
         "strava_profile_picture": 1, "strava_ultima_sincronizacao": 1,
         "strava_athlete_id": 1}
    )
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {
        "conectado": usuario.get("strava_conectado", False),
        "athlete_id": usuario.get("strava_athlete_id"),
        "username": usuario.get("strava_username"),
        "nome": f"{usuario.get('strava_firstname', '')} {usuario.get('strava_lastname', '')}".strip(),
        "foto": usuario.get("strava_profile_picture"),
        "ultima_sincronizacao": usuario.get("strava_ultima_sincronizacao")
    }


@router.post("/strava/sync")
async def strava_sync(
    max_activities: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """
    Sincroniza as atividades do Strava do usuário.
    Importa corridas para o banco de dados.
    """
    # Buscar dados do Strava do usuário
    usuario = await db.usuarios.find_one(
        {"id": current_user["id"]},
        {"_id": 0, "strava_conectado": 1, "strava_access_token": 1,
         "strava_refresh_token": 1, "strava_token_expires_at": 1}
    )
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if not usuario.get("strava_conectado"):
        raise HTTPException(
            status_code=400, 
            detail="Strava não conectado. Conecte primeiro pelo /api/strava/authorize"
        )
    
    try:
        # Importar atividades
        results = await import_strava_activities(
            db=db,
            usuario_id=current_user["id"],
            access_token=usuario["strava_access_token"],
            refresh_token=usuario["strava_refresh_token"],
            token_expires_at=usuario["strava_token_expires_at"],
            max_activities=max_activities
        )
        
        return {
            "success": True,
            "message": f"Sincronização concluída! {results['total_importadas']} novas, {results['total_atualizadas']} atualizadas.",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na sincronização: {str(e)}"
        )


@router.get("/strava/activities")
async def strava_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista as atividades do Strava importadas do usuário.
    """
    # Buscar atividades
    activities = await db.strava_activities.find(
        {"usuario_id": current_user["id"]},
        {"_id": 0}
    ).sort("data_inicio", -1).skip(skip).limit(limit).to_list(limit)
    
    # Total
    total = await db.strava_activities.count_documents(
        {"usuario_id": current_user["id"]}
    )
    
    return {
        "activities": activities,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/strava/stats")
async def strava_stats(current_user: dict = Depends(get_current_user)):
    """
    Retorna estatísticas agregadas das atividades do Strava.
    """
    pipeline = [
        {"$match": {"usuario_id": current_user["id"]}},
        {
            "$group": {
                "_id": None,
                "total_atividades": {"$sum": 1},
                "total_distancia_km": {"$sum": "$distancia_km"},
                "total_tempo_segundos": {"$sum": "$tempo_movimento"},
                "total_elevacao": {"$sum": "$elevacao_total"},
                "media_distancia_km": {"$avg": "$distancia_km"},
                "maior_distancia_km": {"$max": "$distancia_km"}
            }
        }
    ]
    
    results = await db.strava_activities.aggregate(pipeline).to_list(1)
    
    if not results:
        return {
            "total_atividades": 0,
            "total_distancia_km": 0,
            "total_tempo_horas": 0,
            "total_elevacao_m": 0,
            "media_distancia_km": 0,
            "maior_distancia_km": 0
        }
    
    stats = results[0]
    total_horas = stats.get("total_tempo_segundos", 0) / 3600
    
    return {
        "total_atividades": stats.get("total_atividades", 0),
        "total_distancia_km": round(stats.get("total_distancia_km", 0), 2),
        "total_tempo_horas": round(total_horas, 2),
        "total_elevacao_m": round(stats.get("total_elevacao", 0), 0),
        "media_distancia_km": round(stats.get("media_distancia_km", 0), 2),
        "maior_distancia_km": round(stats.get("maior_distancia_km", 0), 2)
    }


@router.get("/strava/sync-status")
async def strava_sync_scheduler_status():
    """
    Retorna o status do scheduler de sincronização automática.
    """
    # Importar scheduler do server.py
    try:
        from server import scheduler as main_scheduler
        
        jobs = []
        for job in main_scheduler.get_jobs():
            if 'strava' in job.id.lower():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else None
                })
        
        return {
            "running": main_scheduler.running,
            "strava_jobs": jobs,
            "message": "Sincronização automática configurada para executar a cada 1 hora"
        }
    except Exception as e:
        return {
            "running": False,
            "strava_jobs": [],
            "error": str(e)
        }


@router.post("/strava/sync-all")
async def strava_sync_all_manual(
    current_user: dict = Depends(get_current_user)
):
    """
    Dispara uma sincronização manual de todos os usuários.
    Apenas admin pode executar.
    """
    # Verificar se é admin
    usuario = await db.usuarios.find_one({"id": current_user["id"]})
    if not usuario or usuario.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem executar esta ação")
    
    from services.strava_sync_scheduler import sync_all_strava_users
    import asyncio
    
    # Executar em background
    asyncio.create_task(sync_all_strava_users())
    
    return {"message": "Sincronização iniciada em background. Verifique os logs para acompanhar."}


@router.get("/strava/sync-logs")
async def strava_sync_logs(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna os logs das últimas sincronizações automáticas.
    """
    logs = await db.strava_sync_logs.find(
        {},
        {"_id": 0}
    ).sort("data", -1).limit(limit).to_list(limit)
    
    return {"logs": logs}


@router.delete("/strava/disconnect")
async def strava_disconnect(current_user: dict = Depends(get_current_user)):
    """
    Desconecta o Strava do usuário.
    Remove tokens e dados da conta Strava.
    """
    await db.usuarios.update_one(
        {"id": current_user["id"]},
        {"$unset": {
            "strava_conectado": "",
            "strava_athlete_id": "",
            "strava_username": "",
            "strava_firstname": "",
            "strava_lastname": "",
            "strava_profile_picture": "",
            "strava_city": "",
            "strava_state": "",
            "strava_country": "",
            "strava_access_token": "",
            "strava_refresh_token": "",
            "strava_token_expires_at": "",
            "strava_conectado_em": "",
            "strava_ultima_sincronizacao": ""
        }}
    )
    
    # Opcional: remover atividades importadas
    # await db.strava_activities.delete_many({"usuario_id": current_user["id"]})
    
    return {"message": "Strava desconectado com sucesso"}



@router.delete("/strava/admin/limpar-todos")
async def strava_limpar_todos(admin_user: dict = Depends(get_admin_user)):
    """
    [ADMIN] Remove TODOS os tokens Strava de todos os usuários.
    Útil para liberar o limite de 100 usuários do Strava API.
    """
    # Contar quantos têm Strava conectado
    total_conectados = await db.usuarios.count_documents({"strava_conectado": True})
    
    # Remover campos Strava de TODOS os usuários
    result = await db.usuarios.update_many(
        {"strava_conectado": {"$exists": True}},
        {"$unset": {
            "strava_conectado": "",
            "strava_athlete_id": "",
            "strava_username": "",
            "strava_firstname": "",
            "strava_lastname": "",
            "strava_profile_picture": "",
            "strava_city": "",
            "strava_state": "",
            "strava_country": "",
            "strava_access_token": "",
            "strava_refresh_token": "",
            "strava_token_expires_at": "",
            "strava_conectado_em": "",
            "strava_ultima_sincronizacao": ""
        }}
    )
    
    return {
        "message": f"Tokens Strava removidos com sucesso",
        "usuarios_desconectados": total_conectados,
        "documentos_atualizados": result.modified_count
    }
