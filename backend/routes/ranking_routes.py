# /app/backend/routes/ranking_routes.py
# Módulo de Ranking - Rankings gerais, povão, semanal, mensal

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
import io
import csv

from config import db
from models import RankingResponse
from routes.auth_routes import get_current_user, get_admin_user

router = APIRouter(tags=["Ranking"])


# ==================== RANKING POVÃO ====================

@router.get("/ranking/povao")
async def get_ranking_povao(genero: str = "M"):
    """Retorna o ranking do Povão - Pace Livre"""
    ranking_list = await db.ranking_povao.find(
        {"ano": 2025, "genero": genero},
        {"_id": 0}
    ).sort([("pontos_total", -1), ("total_corridas", -1), ("distancia_acumulada", -1)]).to_list(None)
    
    result = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            result.append({
                "colocacao": rank.get("ranking_genero", 0),
                "posicao": rank.get("ranking_genero", 0),
                "atleta_id": rank["usuario_id"],
                "nome": usuario.get("nome", ""),
                "uf": usuario.get("estado", ""),
                "cidade": usuario.get("cidade", ""),
                "faixa_etaria": usuario.get("faixa_etaria", "Não informado"),
                "foto_url": usuario.get("foto_url", ""),
                "equipe": usuario.get("equipe", ""),
                "total_corridas": rank.get("total_corridas", 0),
                "distancia_acumulada": rank.get("distancia_acumulada", 0),
                "pontos": rank.get("pontos_total", 0)
            })
    
    return {
        "genero": "Masculino" if genero == "M" else "Feminino",
        "total_atletas": len(result),
        "ranking": result
    }


@router.get("/ranking/povao/stats")
async def get_povao_stats():
    """Retorna estatísticas do ranking do Povão"""
    total_atletas_m = await db.ranking_povao.count_documents({"ano": 2025, "genero": "M"})
    total_atletas_f = await db.ranking_povao.count_documents({"ano": 2025, "genero": "F"})
    
    pipeline = [
        {"$match": {"modalidade": "povao_pace_livre", "ano": 2025}},
        {"$group": {
            "_id": None,
            "total_provas": {"$sum": 1},
            "total_pontos": {"$sum": "$pontos_povao"},
            "total_distancia": {"$sum": {"$toDouble": {"$replaceAll": {"input": {"$toUpper": "$distancia"}, "find": "KM", "replacement": ""}}}}
        }}
    ]
    
    stats = await db.corridas.aggregate(pipeline).to_list(1)
    
    return {
        "total_atletas_masculino": total_atletas_m,
        "total_atletas_feminino": total_atletas_f,
        "total_atletas": total_atletas_m + total_atletas_f,
        "total_provas": stats[0]["total_provas"] if stats else 0,
        "total_pontos": stats[0]["total_pontos"] if stats else 0
    }


# ==================== RANKING SEMANAL ====================

@router.get("/ranking/semanal")
async def get_ranking_semanal(
    genero: str = "M",
    categoria: str = "normal",
    semana_offset: int = 0
):
    """Ranking da semana atual ou anterior"""
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday() + (semana_offset * 7))
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_semana = inicio_semana + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    data_inicio = inicio_semana.strftime("%Y-%m-%d")
    data_fim = fim_semana.strftime("%Y-%m-%d")
    
    pipeline = [
        {
            "$match": {
                "data": {"$gte": data_inicio, "$lte": data_fim},
                "modalidade": {"$ne": "povao_pace_livre"}
            }
        },
        {
            "$lookup": {
                "from": "usuarios",
                "localField": "usuario_id",
                "foreignField": "id",
                "as": "usuario"
            }
        },
        {"$unwind": "$usuario"},
        {
            "$match": {
                "usuario.genero": genero,
                "usuario.categoria": categoria
            }
        },
        {
            "$group": {
                "_id": "$usuario_id",
                "nome": {"$first": "$usuario.nome"},
                "foto_url": {"$first": "$usuario.foto_url"},
                "estado": {"$first": "$usuario.estado"},
                "cidade": {"$first": "$usuario.cidade"},
                "equipe": {"$first": "$usuario.equipe"},
                "faixa_etaria": {"$first": "$usuario.faixa_etaria"},
                "pontos_semana": {"$sum": "$pontos"},
                "corridas_semana": {"$sum": 1}
            }
        },
        {"$sort": {"pontos_semana": -1, "corridas_semana": -1}},
        {"$limit": 100}
    ]
    
    resultado = await db.corridas.aggregate(pipeline).to_list(None)
    
    ranking = []
    for i, r in enumerate(resultado, 1):
        ranking.append({
            "posicao": i,
            "atleta_id": r["_id"],
            "nome": r["nome"],
            "foto_url": r.get("foto_url", ""),
            "uf": r.get("estado", ""),
            "cidade": r.get("cidade", ""),
            "equipe": r.get("equipe", ""),
            "faixa_etaria": r.get("faixa_etaria", ""),
            "pontos": r["pontos_semana"],
            "total_corridas": r["corridas_semana"]
        })
    
    return {
        "periodo": f"{inicio_semana.strftime('%d/%m/%Y')} a {fim_semana.strftime('%d/%m/%Y')}",
        "genero": "Masculino" if genero == "M" else "Feminino",
        "categoria": categoria,
        "ranking": ranking
    }


# ==================== RANKING MENSAL ====================

@router.get("/ranking/mensal")
async def get_ranking_mensal(
    genero: str = "M",
    categoria: str = "normal",
    mes_offset: int = 0
):
    """Ranking do mês atual ou anterior"""
    hoje = datetime.now()
    mes_atual = hoje.month - mes_offset
    ano_atual = hoje.year
    
    while mes_atual < 1:
        mes_atual += 12
        ano_atual -= 1
    
    primeiro_dia = datetime(ano_atual, mes_atual, 1)
    if mes_atual == 12:
        ultimo_dia = datetime(ano_atual + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = datetime(ano_atual, mes_atual + 1, 1) - timedelta(days=1)
    
    data_inicio = primeiro_dia.strftime("%Y-%m-%d")
    data_fim = ultimo_dia.strftime("%Y-%m-%d")
    
    pipeline = [
        {
            "$match": {
                "data": {"$gte": data_inicio, "$lte": data_fim},
                "modalidade": {"$ne": "povao_pace_livre"}
            }
        },
        {
            "$lookup": {
                "from": "usuarios",
                "localField": "usuario_id",
                "foreignField": "id",
                "as": "usuario"
            }
        },
        {"$unwind": "$usuario"},
        {
            "$match": {
                "usuario.genero": genero,
                "usuario.categoria": categoria
            }
        },
        {
            "$group": {
                "_id": "$usuario_id",
                "nome": {"$first": "$usuario.nome"},
                "foto_url": {"$first": "$usuario.foto_url"},
                "estado": {"$first": "$usuario.estado"},
                "cidade": {"$first": "$usuario.cidade"},
                "equipe": {"$first": "$usuario.equipe"},
                "faixa_etaria": {"$first": "$usuario.faixa_etaria"},
                "pontos_mes": {"$sum": "$pontos"},
                "corridas_mes": {"$sum": 1}
            }
        },
        {"$sort": {"pontos_mes": -1, "corridas_mes": -1}},
        {"$limit": 100}
    ]
    
    resultado = await db.corridas.aggregate(pipeline).to_list(None)
    
    ranking = []
    for i, r in enumerate(resultado, 1):
        ranking.append({
            "posicao": i,
            "atleta_id": r["_id"],
            "nome": r["nome"],
            "foto_url": r.get("foto_url", ""),
            "uf": r.get("estado", ""),
            "cidade": r.get("cidade", ""),
            "equipe": r.get("equipe", ""),
            "faixa_etaria": r.get("faixa_etaria", ""),
            "pontos": r["pontos_mes"],
            "total_corridas": r["corridas_mes"]
        })
    
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    return {
        "periodo": f"{meses[mes_atual-1]} {ano_atual}",
        "genero": "Masculino" if genero == "M" else "Feminino",
        "categoria": categoria,
        "ranking": ranking
    }


# ==================== DESTAQUE DO MÊS ====================

@router.get("/ranking/destaque-mes")
async def get_destaque_mes():
    """Retorna o atleta destaque do mês atual"""
    hoje = datetime.now()
    primeiro_dia = datetime(hoje.year, hoje.month, 1)
    
    if hoje.month == 12:
        ultimo_dia = datetime(hoje.year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = datetime(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
    
    data_inicio = primeiro_dia.strftime("%Y-%m-%d")
    data_fim = ultimo_dia.strftime("%Y-%m-%d")
    
    pipeline = [
        {
            "$match": {
                "data": {"$gte": data_inicio, "$lte": data_fim},
                "modalidade": {"$ne": "povao_pace_livre"}
            }
        },
        {
            "$group": {
                "_id": "$usuario_id",
                "pontos_mes": {"$sum": "$pontos"},
                "corridas_mes": {"$sum": 1},
                "primeiro_lugar": {"$sum": {"$cond": [{"$eq": ["$colocacao", 1]}, 1, 0]}},
                "podios": {"$sum": {"$cond": [{"$lte": ["$colocacao", 3]}, 1, 0]}}
            }
        },
        {"$sort": {"pontos_mes": -1, "corridas_mes": -1}},
        {"$limit": 1}
    ]
    
    resultado = await db.corridas.aggregate(pipeline).to_list(1)
    
    if not resultado:
        return {"destaque": None, "mensagem": "Nenhum resultado no mês atual"}
    
    destaque_data = resultado[0]
    usuario = await db.usuarios.find_one({"id": destaque_data["_id"]}, {"_id": 0})
    
    if not usuario:
        return {"destaque": None, "mensagem": "Usuário não encontrado"}
    
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    return {
        "destaque": {
            "atleta_id": destaque_data["_id"],
            "nome": usuario.get("nome", ""),
            "foto_url": usuario.get("foto_url", ""),
            "equipe": usuario.get("equipe", ""),
            "cidade": usuario.get("cidade", ""),
            "estado": usuario.get("estado", ""),
            "pontos_mes": destaque_data["pontos_mes"],
            "corridas_mes": destaque_data["corridas_mes"],
            "primeiro_lugar": destaque_data["primeiro_lugar"],
            "podios": destaque_data["podios"]
        },
        "mes": meses[hoje.month - 1],
        "ano": hoje.year
    }


# ==================== RANKING POR CATEGORIA ====================

@router.get("/ranking/categoria/{categoria}/{genero}", response_model=List[RankingResponse])
async def get_ranking_por_categoria(
    categoria: str,
    genero: str,
    ano: int = 2025,
    limit: int = 100
):
    """Retorna ranking por categoria e gênero"""
    ranking_list = await db.ranking_anual.find(
        {"ano": ano, "genero": genero, "categoria": categoria},
        {"_id": 0}
    ).sort([("pontos_total", -1), ("total_corridas", -1)]).limit(limit).to_list(None)
    
    result = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            result.append(RankingResponse(
                posicao=rank.get("ranking_categoria_genero", 0),
                atleta_id=rank["usuario_id"],
                nome=usuario.get("nome", ""),
                uf=usuario.get("estado", ""),
                cidade=usuario.get("cidade", ""),
                faixa_etaria=usuario.get("faixa_etaria", "Não informado"),
                foto_url=usuario.get("foto_url", ""),
                equipe=usuario.get("equipe", ""),
                total_corridas=rank.get("total_corridas", 0),
                pontos=rank.get("pontos_total", 0)
            ))
    
    return result


# ==================== HISTÓRICO E ANOS ====================

@router.get("/ranking/anos-disponiveis")
async def get_anos_disponiveis():
    """Retorna anos com dados no ranking"""
    anos = await db.ranking_anual.distinct("ano")
    return sorted(anos, reverse=True)


# ==================== FILTROS AUXILIARES ====================

@router.get("/ranking/estados")
async def get_estados():
    """Lista estados com atletas"""
    estados = await db.usuarios.distinct("estado", {"role": "atleta"})
    return sorted([e for e in estados if e])


@router.get("/ranking/faixas-etarias")
async def get_faixas_etarias():
    """Lista faixas etárias disponíveis"""
    return ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]


@router.get("/ranking/equipes")
async def get_equipes():
    """Lista equipes/assessorias ativas"""
    pipeline = [
        {"$match": {"role": "atleta", "equipe": {"$ne": "", "$exists": True}}},
        {"$group": {"_id": "$equipe", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 100}
    ]
    
    equipes = await db.usuarios.aggregate(pipeline).to_list(None)
    return [{"nome": e["_id"], "atletas": e["count"]} for e in equipes if e["_id"]]
