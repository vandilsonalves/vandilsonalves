# /app/backend/services/strava_service.py
# Serviço de integração com Strava API

import os
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"
STRAVA_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
STRAVA_API_BASE = "https://www.strava.com/api/v3"


def get_authorization_url(redirect_uri: str) -> str:
    """
    Gera a URL de autorização OAuth2 do Strava.
    O usuário será redirecionado para esta URL para autorizar o app.
    """
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "activity:read_all,profile:read_all",
        "approval_prompt": "auto"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{STRAVA_AUTHORIZE_URL}?{query_string}"


def exchange_code_for_token(code: str) -> Dict:
    """
    Troca o código de autorização por tokens de acesso.
    Retorna: {access_token, refresh_token, expires_at, athlete}
    """
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    
    response = requests.post(STRAVA_TOKEN_URL, data=payload)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao trocar código: {response.text}")
    
    return response.json()


def refresh_access_token(refresh_token: str) -> Dict:
    """
    Usa o refresh token para obter um novo access token.
    Chamado quando o token expira.
    """
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(STRAVA_TOKEN_URL, data=payload)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao renovar token: {response.text}")
    
    return response.json()


def get_athlete_info(access_token: str) -> Dict:
    """
    Busca informações do atleta autenticado.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(f"{STRAVA_API_BASE}/athlete", headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao buscar atleta: {response.text}")
    
    return response.json()


def get_athlete_activities(
    access_token: str,
    before: Optional[int] = None,
    after: Optional[int] = None,
    per_page: int = 30,
    page: int = 1
) -> List[Dict]:
    """
    Busca as atividades do atleta no Strava.
    
    Args:
        access_token: Token de acesso do Strava
        before: Timestamp epoch - atividades antes desta data
        after: Timestamp epoch - atividades após esta data
        per_page: Quantidade por página (máx 200)
        page: Número da página
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "per_page": min(per_page, 200),
        "page": page
    }
    
    if before:
        params["before"] = before
    if after:
        params["after"] = after
    
    response = requests.get(
        f"{STRAVA_API_BASE}/athlete/activities",
        headers=headers,
        params=params
    )
    
    if response.status_code != 200:
        raise Exception(f"Erro ao buscar atividades: {response.text}")
    
    return response.json()


def calculate_pace(distance_meters: float, moving_time_seconds: int) -> Optional[str]:
    """
    Calcula o pace em min/km.
    Retorna string formatada "MM:SS"
    """
    if distance_meters <= 0 or moving_time_seconds <= 0:
        return None
    
    distance_km = distance_meters / 1000
    pace_seconds_per_km = moving_time_seconds / distance_km
    
    minutes = int(pace_seconds_per_km // 60)
    seconds = int(pace_seconds_per_km % 60)
    
    return f"{minutes}:{seconds:02d}"


def format_time(seconds: int) -> str:
    """
    Formata tempo em segundos para HH:MM:SS
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def transform_activity(strava_activity: Dict) -> Dict:
    """
    Transforma uma atividade do Strava para o formato do Ranking Run.
    """
    distance_km = strava_activity.get("distance", 0) / 1000
    moving_time = strava_activity.get("moving_time", 0)
    
    return {
        "strava_id": strava_activity["id"],
        "nome": strava_activity.get("name", "Atividade sem nome"),
        "tipo": strava_activity.get("type", "Run"),
        "distancia_metros": strava_activity.get("distance", 0),
        "distancia_km": round(distance_km, 2),
        "tempo_movimento": moving_time,
        "tempo_movimento_formatado": format_time(moving_time),
        "tempo_total": strava_activity.get("elapsed_time", 0),
        "elevacao_total": strava_activity.get("total_elevation_gain", 0),
        "pace": calculate_pace(strava_activity.get("distance", 0), moving_time),
        "velocidade_media": strava_activity.get("average_speed", 0),
        "velocidade_maxima": strava_activity.get("max_speed", 0),
        "data_inicio": strava_activity.get("start_date"),
        "data_inicio_local": strava_activity.get("start_date_local"),
        "latitude_inicio": strava_activity.get("start_latitude"),
        "longitude_inicio": strava_activity.get("start_longitude"),
        "cidade": strava_activity.get("location_city"),
        "pais": strava_activity.get("location_country"),
        "mapa_polyline": strava_activity.get("map", {}).get("summary_polyline"),
        "importado_em": datetime.now(timezone.utc).isoformat()
    }


async def import_strava_activities(
    db,
    usuario_id: str,
    access_token: str,
    refresh_token: str,
    token_expires_at: int,
    max_activities: int = 50
) -> Dict:
    """
    Importa atividades do Strava para o banco de dados.
    
    Retorna: {
        "total_importadas": int,
        "total_atualizadas": int,
        "total_ignoradas": int,
        "atividades": list
    }
    """
    import time
    
    # Verificar se token expirou e renovar se necessário
    current_time = int(time.time())
    if token_expires_at <= current_time:
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
    
    results = {
        "total_importadas": 0,
        "total_atualizadas": 0,
        "total_ignoradas": 0,
        "atividades": []
    }
    
    try:
        # Buscar atividades (apenas corridas)
        activities = get_athlete_activities(
            access_token=access_token,
            per_page=max_activities
        )
        
        for activity in activities:
            # Filtrar apenas corridas
            if activity.get("type") not in ["Run", "VirtualRun", "TrailRun"]:
                results["total_ignoradas"] += 1
                continue
            
            # Transformar atividade
            transformed = transform_activity(activity)
            transformed["usuario_id"] = usuario_id
            
            # Verificar se já existe
            existing = await db.strava_activities.find_one({
                "strava_id": transformed["strava_id"],
                "usuario_id": usuario_id
            })
            
            if existing:
                # Atualizar existente
                await db.strava_activities.update_one(
                    {"_id": existing["_id"]},
                    {"$set": transformed}
                )
                results["total_atualizadas"] += 1
            else:
                # Inserir nova
                await db.strava_activities.insert_one(transformed)
                results["total_importadas"] += 1
            
            results["atividades"].append({
                "nome": transformed["nome"],
                "distancia_km": transformed["distancia_km"],
                "tempo": transformed["tempo_movimento_formatado"],
                "pace": transformed["pace"],
                "data": transformed["data_inicio_local"]
            })
        
        # Atualizar última sincronização do usuário
        await db.usuarios.update_one(
            {"id": usuario_id},
            {"$set": {
                "strava_ultima_sincronizacao": datetime.now(timezone.utc).isoformat()
            }}
        )
        
    except Exception as e:
        results["erro"] = str(e)
    
    return results
