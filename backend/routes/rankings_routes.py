# /app/backend/routes/rankings_routes.py
# Rotas relacionadas a rankings de atletas e estatísticas

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timezone

ANO_ATUAL = datetime.now(timezone.utc).year

from config import db
from routes.auth_routes import get_current_user, get_admin_user

router = APIRouter()


@router.get("/ranking-nacional")
async def get_ranking_nacional(ano: int = Query(ANO_ATUAL)):
    """Retorna o ranking nacional de atletas"""
    
    pipeline = [
        {"$match": {"ano": ano, "role": "atleta"}},
        {"$sort": {"pontos_geral": -1}},
        {"$limit": 500},
        {"$project": {
            "_id": 0,
            "id": 1,
            "nome": 1,
            "cidade": 1,
            "estado": 1,
            "equipe": 1,
            "pontos_geral": 1,
            "posicao_geral": 1,
            "total_resultados": 1,
            "foto_url": 1
        }}
    ]
    
    atletas = await db.usuarios.aggregate(pipeline).to_list(500)
    
    # Adicionar posições
    for i, atleta in enumerate(atletas):
        atleta["posicao"] = i + 1
    
    return {"ranking": atletas, "ano": ano, "total": len(atletas)}


@router.get("/estados-disponiveis")
async def get_estados_disponiveis(ano: int = Query(ANO_ATUAL)):
    """Retorna lista de estados com atletas cadastrados"""
    
    estados = await db.usuarios.distinct("estado", {"role": "atleta", "estado": {"$ne": None}})
    estados = [e for e in estados if e]
    estados.sort()
    
    return {"estados": estados}


@router.get("/faixas-disponiveis")
async def get_faixas_disponiveis():
    """Retorna lista de faixas etárias disponíveis"""
    return {
        "faixas": [
            "18-29", "30-34", "35-39", "40-44", "45-49",
            "50-54", "55-59", "60-64", "65-69", "70+"
        ]
    }


@router.get("/equipes-disponiveis")
async def get_equipes_disponiveis():
    """Retorna lista de equipes/assessorias cadastradas"""
    
    equipes = await db.usuarios.distinct("equipe", {"equipe": {"$nin": [None, "", "Individual"]}})
    equipes = [e for e in equipes if e]
    equipes.sort()
    
    return {"equipes": equipes}


@router.get("/destaque-mes")
async def get_destaque_mes(mes: int = None, ano: int = None):
    """Retorna atletas destaque do mês"""
    
    if not mes:
        mes = datetime.now().month
    if not ano:
        ano = datetime.now().year
    
    # Buscar resultados do mês
    inicio_mes = datetime(ano, mes, 1)
    if mes == 12:
        fim_mes = datetime(ano + 1, 1, 1)
    else:
        fim_mes = datetime(ano, mes + 1, 1)
    
    pipeline = [
        {
            "$match": {
                "data_corrida": {
                    "$gte": inicio_mes.strftime("%Y-%m-%d"),
                    "$lt": fim_mes.strftime("%Y-%m-%d")
                }
            }
        },
        {
            "$group": {
                "_id": "$atleta_id",
                "total_corridas": {"$sum": 1},
                "pontos_mes": {"$sum": "$pontos"},
                "total_primeiros": {
                    "$sum": {"$cond": [{"$eq": ["$posicao", 1]}, 1, 0]}
                }
            }
        },
        {"$sort": {"pontos_mes": -1}},
        {"$limit": 10}
    ]
    
    destaques = await db.resultados.aggregate(pipeline).to_list(10)
    
    # Enriquecer com dados dos atletas
    for destaque in destaques:
        atleta = await db.usuarios.find_one(
            {"id": destaque["_id"]},
            {"_id": 0, "nome": 1, "equipe": 1, "cidade": 1, "estado": 1, "foto_url": 1}
        )
        if atleta:
            destaque.update(atleta)
    
    return {
        "mes": mes,
        "ano": ano,
        "destaques": destaques
    }
