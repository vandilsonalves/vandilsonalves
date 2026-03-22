# /app/backend/routes/strava_atividades_routes.py
# Rotas para exibição pública das atividades do Strava

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone, timedelta
from typing import Optional
from config import db

router = APIRouter()


def get_week_range(week_offset: int = 0):
    """
    Retorna o início e fim da semana.
    week_offset: 0 = esta semana, -1 = semana passada
    """
    today = datetime.now(timezone.utc)
    # Encontrar segunda-feira da semana atual
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Aplicar offset
    start_of_week = start_of_week + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    return start_of_week, end_of_week


@router.get("/strava-atividades/membros")
async def get_membros_conectados():
    """
    Lista todos os membros que conectaram o Strava.
    """
    # Buscar usuários com Strava conectado
    usuarios = await db.usuarios.find(
        {"strava_conectado": True},
        {
            "_id": 0,
            "id": 1,
            "nome": 1,
            "foto_url": 1,
            "strava_username": 1,
            "strava_firstname": 1,
            "strava_lastname": 1,
            "strava_profile_picture": 1,
            "strava_athlete_id": 1,
            "strava_ultima_sincronizacao": 1
        }
    ).to_list(500)
    
    return {
        "total": len(usuarios),
        "membros": usuarios
    }


@router.get("/strava-atividades/classificacao")
async def get_classificacao_semanal(
    periodo: str = Query("esta_semana", description="esta_semana ou semana_passada"),
    ordenar_por: str = Query("distancia", description="distancia, corridas, maior_corrida, ritmo, elevacao")
):
    """
    Retorna a classificação semanal dos atletas baseada nas atividades do Strava.
    Similar ao "Classificação do Clube" do Strava.
    """
    # Determinar período
    if periodo == "semana_passada":
        start_date, end_date = get_week_range(-1)
    else:
        start_date, end_date = get_week_range(0)
    
    # Pipeline de agregação
    pipeline = [
        # Filtrar por período
        {
            "$match": {
                "data_inicio": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
        },
        # Agrupar por usuário
        {
            "$group": {
                "_id": "$usuario_id",
                "total_distancia_km": {"$sum": "$distancia_km"},
                "total_corridas": {"$sum": 1},
                "maior_corrida_km": {"$max": "$distancia_km"},
                "total_tempo_segundos": {"$sum": "$tempo_movimento"},
                "total_elevacao": {"$sum": "$elevacao_total"},
                "atividades": {"$push": {
                    "nome": "$nome",
                    "distancia_km": "$distancia_km",
                    "tempo": "$tempo_movimento_formatado",
                    "pace": "$pace",
                    "data": "$data_inicio_local"
                }}
            }
        },
        # Calcular ritmo médio
        {
            "$addFields": {
                "ritmo_medio_segundos": {
                    "$cond": {
                        "if": {"$gt": ["$total_distancia_km", 0]},
                        "then": {"$divide": ["$total_tempo_segundos", "$total_distancia_km"]},
                        "else": 0
                    }
                }
            }
        }
    ]
    
    # Ordenação
    sort_field = {
        "distancia": ("total_distancia_km", -1),
        "corridas": ("total_corridas", -1),
        "maior_corrida": ("maior_corrida_km", -1),
        "ritmo": ("ritmo_medio_segundos", 1),  # Menor é melhor
        "elevacao": ("total_elevacao", -1)
    }.get(ordenar_por, ("total_distancia_km", -1))
    
    pipeline.append({"$sort": {sort_field[0]: sort_field[1]}})
    
    # Executar agregação
    resultados = await db.strava_activities.aggregate(pipeline).to_list(100)
    
    # Buscar informações dos usuários
    classificacao = []
    for idx, resultado in enumerate(resultados):
        usuario = await db.usuarios.find_one(
            {"id": resultado["_id"]},
            {
                "_id": 0,
                "id": 1,
                "nome": 1,
                "foto_url": 1,
                "strava_profile_picture": 1,
                "strava_username": 1
            }
        )
        
        if not usuario:
            continue
        
        # Formatar ritmo médio
        ritmo_segundos = resultado.get("ritmo_medio_segundos", 0)
        ritmo_min = int(ritmo_segundos // 60)
        ritmo_seg = int(ritmo_segundos % 60)
        ritmo_formatado = f"{ritmo_min}:{ritmo_seg:02d}" if ritmo_segundos > 0 else "-"
        
        classificacao.append({
            "posicao": idx + 1,
            "usuario_id": resultado["_id"],
            "nome": usuario.get("nome", "Atleta"),
            "foto": usuario.get("strava_profile_picture") or usuario.get("foto_url"),
            "strava_username": usuario.get("strava_username"),
            "total_distancia_km": round(resultado["total_distancia_km"], 1),
            "total_corridas": resultado["total_corridas"],
            "maior_corrida_km": round(resultado["maior_corrida_km"], 1),
            "ritmo_medio": ritmo_formatado,
            "total_elevacao_m": round(resultado.get("total_elevacao", 0), 0),
            "atividades_recentes": resultado.get("atividades", [])[:3]
        })
    
    return {
        "periodo": {
            "inicio": start_date.strftime("%d/%m/%Y"),
            "fim": end_date.strftime("%d/%m/%Y"),
            "tipo": periodo
        },
        "ordenado_por": ordenar_por,
        "total_atletas": len(classificacao),
        "classificacao": classificacao
    }


@router.get("/strava-atividades/lideres")
async def get_lideres_semana(
    periodo: str = Query("semana_passada", description="esta_semana ou semana_passada")
):
    """
    Retorna os líderes da semana em cada categoria:
    - Maior distância total
    - Maior tempo de corrida
    - Maior elevação (subida)
    """
    if periodo == "semana_passada":
        start_date, end_date = get_week_range(-1)
    else:
        start_date, end_date = get_week_range(0)
    
    # Pipeline base
    match_stage = {
        "$match": {
            "data_inicio": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }
    }
    
    async def get_leader(group_field, sort_order=-1):
        pipeline = [
            match_stage,
            {
                "$group": {
                    "_id": "$usuario_id",
                    "valor": {"$sum": f"${group_field}"}
                }
            },
            {"$sort": {"valor": sort_order}},
            {"$limit": 3}
        ]
        return await db.strava_activities.aggregate(pipeline).to_list(3)
    
    # Buscar líderes
    lideres_distancia = await get_leader("distancia_km")
    lideres_tempo = await get_leader("tempo_movimento")
    lideres_elevacao = await get_leader("elevacao_total")
    
    async def format_leaders(leaders, format_func):
        result = []
        for idx, leader in enumerate(leaders):
            usuario = await db.usuarios.find_one(
                {"id": leader["_id"]},
                {"_id": 0, "nome": 1, "foto_url": 1, "strava_profile_picture": 1}
            )
            if usuario:
                result.append({
                    "posicao": idx + 1,
                    "nome": usuario.get("nome", "Atleta"),
                    "foto": usuario.get("strava_profile_picture") or usuario.get("foto_url"),
                    "valor": format_func(leader["valor"])
                })
        return result
    
    def format_km(val):
        return f"{round(val, 1)} km"
    
    def format_tempo(segundos):
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segs = int(segundos % 60)
        if horas > 0:
            return f"{horas}:{minutos:02d}:{segs:02d}"
        return f"{minutos}:{segs:02d}"
    
    def format_elevacao(val):
        return f"{int(val)} m"
    
    return {
        "periodo": {
            "inicio": start_date.strftime("%d/%m/%Y"),
            "fim": end_date.strftime("%d/%m/%Y"),
            "tipo": periodo
        },
        "distancia": await format_leaders(lideres_distancia, format_km),
        "tempo_total": await format_leaders(lideres_tempo, format_tempo),
        "elevacao": await format_leaders(lideres_elevacao, format_elevacao)
    }


@router.get("/strava-atividades/recentes")
async def get_atividades_recentes(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Lista as atividades mais recentes de todos os usuários conectados.
    """
    # Pipeline para buscar atividades com dados do usuário
    pipeline = [
        {"$sort": {"data_inicio": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "usuarios",
                "localField": "usuario_id",
                "foreignField": "id",
                "as": "usuario_info"
            }
        },
        {"$unwind": {"path": "$usuario_info", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "strava_id": 1,
                "nome": 1,
                "tipo": 1,
                "distancia_km": 1,
                "tempo_movimento_formatado": 1,
                "pace": 1,
                "elevacao_total": 1,
                "data_inicio_local": 1,
                "usuario_nome": "$usuario_info.nome",
                "usuario_foto": {"$ifNull": ["$usuario_info.strava_profile_picture", "$usuario_info.foto_url"]}
            }
        }
    ]
    
    atividades = await db.strava_activities.aggregate(pipeline).to_list(limit)
    
    # Total de atividades
    total = await db.strava_activities.count_documents({})
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "atividades": atividades
    }
