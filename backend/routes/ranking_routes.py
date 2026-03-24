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
from services.cache_service import cached, cache_service, invalidate_on_ranking_change

router = APIRouter(tags=["Ranking"])


# ==================== RANKING POVÃO ====================

@router.get("/ranking/povao")
@cached(prefix='ranking', ttl_key='ranking_povao')
async def get_ranking_povao(genero: str = "M"):
    """Retorna o ranking da Galera - Pace Livre"""
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
@cached(prefix='ranking', ttl_key='stats')
async def get_povao_stats():
    """Retorna estatísticas do ranking da Galera"""
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


@router.get("/ranking/povao/semanal")
async def get_povao_ranking_semanal(genero: str = "M", limit: int = 10):
    """Retorna o Top 10 da Galera da última semana"""
    from datetime import datetime, timedelta
    
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=7)
    
    # Buscar corridas da última semana para atletas do Povão
    pipeline = [
        {
            "$match": {
                "modalidade": "povao_pace_livre",
                "data_competicao": {"$gte": inicio_semana.strftime("%Y-%m-%d")},
                "status": "aprovado"
            }
        },
        {
            "$group": {
                "_id": "$usuario_id",
                "total_corridas": {"$sum": 1},
                "total_pontos": {"$sum": "$pontos_povao"},
                "distancia_acumulada": {"$sum": {"$toDouble": {"$replaceAll": {"input": {"$toUpper": "$distancia"}, "find": "KM", "replacement": ""}}}}
            }
        },
        {"$sort": {"total_pontos": -1, "total_corridas": -1}},
        {"$limit": limit}
    ]
    
    resultados = await db.corridas.aggregate(pipeline).to_list(None)
    
    ranking = []
    for idx, r in enumerate(resultados):
        usuario = await db.usuarios.find_one({"id": r["_id"], "genero": genero}, {"_id": 0})
        if usuario:
            ranking.append({
                "posicao": idx + 1,
                "atleta_id": r["_id"],
                "nome": usuario.get("nome", ""),
                "foto_url": usuario.get("foto_url", ""),
                "equipe": usuario.get("equipe", ""),
                "cidade": usuario.get("cidade", ""),
                "uf": usuario.get("estado", ""),
                "total_corridas": r["total_corridas"],
                "pontos": r["total_pontos"],
                "distancia_acumulada": r.get("distancia_acumulada", 0)
            })
    
    return {
        "periodo": f"{inicio_semana.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')}",
        "total": len(ranking),
        "ranking": ranking
    }


@router.get("/ranking/povao/mensal")
async def get_povao_ranking_mensal(genero: str = "M", limit: int = 10):
    """Retorna o Top 10 da Galera do mês atual"""
    from datetime import datetime
    
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1).strftime("%Y-%m-%d")
    
    pipeline = [
        {
            "$match": {
                "modalidade": "povao_pace_livre",
                "data_competicao": {"$gte": inicio_mes},
                "status": "aprovado"
            }
        },
        {
            "$group": {
                "_id": "$usuario_id",
                "total_corridas": {"$sum": 1},
                "total_pontos": {"$sum": "$pontos_povao"},
                "distancia_acumulada": {"$sum": {"$toDouble": {"$replaceAll": {"input": {"$toUpper": "$distancia"}, "find": "KM", "replacement": ""}}}}
            }
        },
        {"$sort": {"total_pontos": -1, "total_corridas": -1}},
        {"$limit": limit}
    ]
    
    resultados = await db.corridas.aggregate(pipeline).to_list(None)
    
    ranking = []
    for idx, r in enumerate(resultados):
        usuario = await db.usuarios.find_one({"id": r["_id"], "genero": genero}, {"_id": 0})
        if usuario:
            ranking.append({
                "posicao": idx + 1,
                "atleta_id": r["_id"],
                "nome": usuario.get("nome", ""),
                "foto_url": usuario.get("foto_url", ""),
                "equipe": usuario.get("equipe", ""),
                "cidade": usuario.get("cidade", ""),
                "uf": usuario.get("estado", ""),
                "total_corridas": r["total_corridas"],
                "pontos": r["total_pontos"],
                "distancia_acumulada": r.get("distancia_acumulada", 0)
            })
    
    meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    return {
        "periodo": f"{meses[hoje.month]} {hoje.year}",
        "total": len(ranking),
        "ranking": ranking
    }


@router.get("/ranking/povao/destaque-mes")
async def get_povao_destaque_mes():
    """Retorna os destaques do mês da Galera"""
    from datetime import datetime
    
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1).strftime("%Y-%m-%d")
    
    # Total de corridas no mês
    total_corridas_mes = await db.corridas.count_documents({
        "modalidade": "povao_pace_livre",
        "data_competicao": {"$gte": inicio_mes},
        "status": "aprovado"
    })
    
    # Atletas únicos que participaram
    pipeline_atletas = [
        {
            "$match": {
                "modalidade": "povao_pace_livre",
                "data_competicao": {"$gte": inicio_mes},
                "status": "aprovado"
            }
        },
        {"$group": {"_id": "$usuario_id"}}
    ]
    atletas_unicos = len(await db.corridas.aggregate(pipeline_atletas).to_list(None))
    
    # Mais ativo (mais corridas)
    pipeline_ativo = [
        {
            "$match": {
                "modalidade": "povao_pace_livre",
                "data_competicao": {"$gte": inicio_mes},
                "status": "aprovado"
            }
        },
        {"$group": {"_id": "$usuario_id", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
    mais_ativo_result = await db.corridas.aggregate(pipeline_ativo).to_list(1)
    mais_ativo = None
    if mais_ativo_result:
        usuario = await db.usuarios.find_one({"id": mais_ativo_result[0]["_id"]}, {"_id": 0})
        if usuario:
            mais_ativo = {
                "atleta_id": mais_ativo_result[0]["_id"],
                "nome": usuario.get("nome", ""),
                "foto_url": usuario.get("foto_url", ""),
                "total_corridas": mais_ativo_result[0]["total"]
            }
    
    # Mais pontos
    pipeline_pontos = [
        {
            "$match": {
                "modalidade": "povao_pace_livre",
                "data_competicao": {"$gte": inicio_mes},
                "status": "aprovado"
            }
        },
        {"$group": {"_id": "$usuario_id", "total": {"$sum": "$pontos_povao"}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
    mais_pontos_result = await db.corridas.aggregate(pipeline_pontos).to_list(1)
    mais_pontos = None
    if mais_pontos_result:
        usuario = await db.usuarios.find_one({"id": mais_pontos_result[0]["_id"]}, {"_id": 0})
        if usuario:
            mais_pontos = {
                "atleta_id": mais_pontos_result[0]["_id"],
                "nome": usuario.get("nome", ""),
                "foto_url": usuario.get("foto_url", ""),
                "total_pontos": mais_pontos_result[0]["total"]
            }
    
    meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    return {
        "mes": f"{meses[hoje.month]} {hoje.year}",
        "total_corridas": total_corridas_mes,
        "atletas_participantes": atletas_unicos,
        "mais_ativo": mais_ativo,
        "mais_pontos": mais_pontos
    }


# ==================== RANKING SEMANAL ====================

@router.get("/ranking/semanal")
@cached(prefix='ranking', ttl_key='ranking_semanal')
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
@cached(prefix='ranking', ttl_key='ranking_mensal')
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
@cached(prefix='ranking', ttl_key='ranking_destaque')
async def get_destaque_mes(mes: int = None, ano: int = None):
    """Retorna os destaques do mês (top 3 de cada categoria + estatísticas)"""
    
    hoje = datetime.now()
    mes_atual = mes or hoje.month
    ano_atual = ano or hoje.year
    
    # Calcular início e fim do mês
    inicio_mes = f"{ano_atual}-{mes_atual:02d}-01"
    if mes_atual == 12:
        fim_mes = f"{ano_atual + 1}-01-01"
    else:
        fim_mes = f"{ano_atual}-{mes_atual + 1:02d}-01"
    
    meses_nome = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    categorias = [
        ("Masculino", "normal", "M"),
        ("Feminino", "normal", "F"),
        ("PCD Masculino", "pcd", "M"),
        ("PCD Feminino", "pcd", "F"),
        ("Cadeirante Masculino", "cadeirante", "M"),
        ("Cadeirante Feminino", "cadeirante", "F")
    ]
    
    destaques = {}
    
    for nome_cat, cat_db, gen_db in categorias:
        # Buscar corridas do mês para esta categoria
        pipeline = [
            {"$match": {
                "data": {"$gte": inicio_mes, "$lt": fim_mes}
            }},
            {"$group": {
                "_id": "$usuario_id",
                "pontos_mes": {"$sum": "$pontos"},
                "corridas_mes": {"$sum": 1}
            }},
            {"$sort": {"pontos_mes": -1}}
        ]
        
        agregados = await db.corridas.aggregate(pipeline).to_list(None)
        
        top3 = []
        for agg in agregados:
            usuario = await db.usuarios.find_one({"id": agg["_id"]}, {"_id": 0})
            if usuario and usuario.get("categoria") == cat_db and usuario.get("genero") == gen_db:
                top3.append({
                    "atleta_id": agg["_id"],
                    "nome": usuario["nome"],
                    "equipe": usuario["equipe"],
                    "cidade": usuario["cidade"],
                    "estado": usuario["estado"],
                    "foto_url": usuario.get("foto_url", ""),
                    "pontos_mes": agg["pontos_mes"],
                    "corridas_mes": agg["corridas_mes"]
                })
                if len(top3) >= 3:
                    break
        
        destaques[nome_cat] = top3
    
    # Estatísticas gerais do mês
    total_corridas_mes = await db.corridas.count_documents({
        "data": {"$gte": inicio_mes, "$lt": fim_mes}
    })
    
    # Atleta mais ativo do mês (mais corridas)
    pipeline_mais_ativo = [
        {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
        {"$group": {"_id": "$usuario_id", "total_corridas": {"$sum": 1}}},
        {"$sort": {"total_corridas": -1}},
        {"$limit": 1}
    ]
    mais_ativo_result = await db.corridas.aggregate(pipeline_mais_ativo).to_list(1)
    
    mais_ativo = None
    if mais_ativo_result:
        usuario_ativo = await db.usuarios.find_one({"id": mais_ativo_result[0]["_id"]}, {"_id": 0})
        if usuario_ativo:
            mais_ativo = {
                "atleta_id": mais_ativo_result[0]["_id"],
                "nome": usuario_ativo["nome"],
                "equipe": usuario_ativo["equipe"],
                "foto_url": usuario_ativo.get("foto_url", ""),
                "total_corridas": mais_ativo_result[0]["total_corridas"]
            }
    
    # Atleta com mais pontos no mês (geral)
    pipeline_mais_pontos = [
        {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
        {"$group": {"_id": "$usuario_id", "total_pontos": {"$sum": "$pontos"}}},
        {"$sort": {"total_pontos": -1}},
        {"$limit": 1}
    ]
    mais_pontos_result = await db.corridas.aggregate(pipeline_mais_pontos).to_list(1)
    
    mais_pontos = None
    if mais_pontos_result:
        usuario_pontos = await db.usuarios.find_one({"id": mais_pontos_result[0]["_id"]}, {"_id": 0})
        if usuario_pontos:
            mais_pontos = {
                "atleta_id": mais_pontos_result[0]["_id"],
                "nome": usuario_pontos["nome"],
                "equipe": usuario_pontos["equipe"],
                "foto_url": usuario_pontos.get("foto_url", ""),
                "total_pontos": mais_pontos_result[0]["total_pontos"]
            }
    
    return {
        "mes": meses_nome[mes_atual],
        "ano": ano_atual,
        "total_corridas_mes": total_corridas_mes,
        "destaques_categoria": destaques,
        "mais_ativo_mes": mais_ativo,
        "mais_pontos_mes": mais_pontos
    }


# ==================== RANKING POR CATEGORIA ====================

@router.get("/ranking/categoria/{categoria}/{genero}", response_model=List[RankingResponse])
async def get_ranking_por_categoria(
    categoria: str,
    genero: str,
    ano: int = 2025,
    limit: int = 100,
    faixa: str = None,
    equipe: str = None,
    cidade: str = None
):
    """Retorna ranking por categoria e gênero
    
    Categoria pode ser:
    - masculino, feminino -> normal M/F
    - pcd-m, pcd-f -> pcd M/F
    - cadeirante-m, cadeirante-f -> cadeirante M/F
    - normal, pcd, cadeirante -> usa gênero passado
    """
    # Mapear categoria do frontend para valores do banco
    cat_map = {
        "masculino": ("normal", "M"),
        "feminino": ("normal", "F"),
        "pcd-m": ("pcd", "M"),
        "pcd-f": ("pcd", "F"),
        "cadeirante-m": ("cadeirante", "M"),
        "cadeirante-f": ("cadeirante", "F")
    }
    
    if categoria.lower() in cat_map:
        cat_db, gen_db = cat_map[categoria.lower()]
    else:
        # Valores diretos
        cat_db = categoria
        gen_db = genero
    
    query = {"ano": ano, "genero": gen_db, "categoria": cat_db}
    
    # Filtros adicionais
    if faixa:
        query["faixa_etaria"] = faixa
    
    ranking_list = await db.ranking_anual.find(
        query,
        {"_id": 0}
    ).sort([("pontos_total", -1), ("total_corridas", -1)]).limit(limit).to_list(None)
    
    result = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            # Filtros de equipe e cidade no nível do usuário
            if equipe and equipe.lower() not in usuario.get("equipe", "").lower():
                continue
            if cidade and cidade.lower() not in usuario.get("cidade", "").lower():
                continue
                
            posicao = rank.get("ranking_categoria", rank.get("ranking_genero", len(result) + 1))
            result.append(RankingResponse(
                id=rank["usuario_id"],
                colocacao=posicao,
                uf=usuario.get("estado", ""),
                foto_url=usuario.get("foto_url", ""),
                nome=usuario.get("nome", ""),
                cidade=usuario.get("cidade", ""),
                equipe=usuario.get("equipe", ""),
                faixa_etaria=usuario.get("faixa_etaria", "Não informado"),
                total_corridas=rank.get("total_corridas", 0),
                pontos=rank.get("pontos_total", 0),
                is_elite=rank.get("pontos_total", 0) >= 100,
                is_pendente=rank.get("total_corridas", 0) < 3
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
@cached(prefix='ranking', ttl_key='estados')
async def get_estados():
    """Lista estados com atletas"""
    estados = await db.usuarios.distinct("estado", {"role": {"$in": ["atleta", "dono_assessoria"]}})
    return {"estados": sorted([e for e in estados if e])}


@router.get("/ranking/faixas-etarias")
@cached(prefix='ranking', ttl_key='faixas_etarias')
async def get_faixas_etarias():
    """Lista faixas etárias disponíveis"""
    return {"faixas": ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]}


@router.get("/ranking/equipes")
@cached(prefix='ranking', ttl_key='equipes')
async def get_equipes():
    """Lista equipes/assessorias ativas"""
    pipeline = [
        {"$match": {"role": {"$in": ["atleta", "dono_assessoria"]}, "equipe": {"$ne": "", "$exists": True}}},
        {"$group": {"_id": "$equipe", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 100}
    ]
    
    equipes = await db.usuarios.aggregate(pipeline).to_list(None)
    return {"equipes": [{"nome": e["_id"], "atletas": e["count"]} for e in equipes if e["_id"]]}


@router.get("/ranking/cidades")
@cached(prefix='ranking', ttl_key='cidades')
async def get_cidades(estado: str = None):
    """Lista cidades com atletas, opcionalmente filtradas por estado"""
    query = {"role": {"$in": ["atleta", "dono_assessoria"]}, "cidade": {"$ne": "", "$exists": True}}
    
    if estado:
        query["estado"] = estado
    
    pipeline = [
        {"$match": query},
        {"$group": {"_id": {"cidade": "$cidade", "estado": "$estado"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 200}
    ]
    
    cidades = await db.usuarios.aggregate(pipeline).to_list(None)
    return {
        "cidades": [
            {
                "nome": c["_id"]["cidade"], 
                "estado": c["_id"]["estado"],
                "atletas": c["count"]
            } 
            for c in cidades if c["_id"]["cidade"]
        ]
    }


@router.get("/ranking/por-cidade/{estado}/{cidade}")
async def get_ranking_por_cidade(
    estado: str,
    cidade: str,
    modalidade: str = "profissional",  # profissional ou povao
    genero: str = "M",
    categoria: str = "normal",
    ano: int = 2025,
    limit: int = 100
):
    """
    Retorna ranking filtrado por cidade.
    Modalidades: profissional (por colocação) ou povao (por distância)
    """
    # Buscar usuários da cidade
    usuarios_query = {
        "role": {"$in": ["atleta", "dono_assessoria"]},
        "estado": {"$regex": f"^{estado}$", "$options": "i"},
        "cidade": {"$regex": f"^{cidade}$", "$options": "i"}
    }
    
    usuarios_cidade = await db.usuarios.find(usuarios_query, {"_id": 0}).to_list(None)
    usuario_ids = [u["id"] for u in usuarios_cidade]
    
    if not usuario_ids:
        return {"ranking": [], "total": 0, "cidade": cidade, "estado": estado}
    
    result = []
    
    if modalidade.lower() == "povao":
        # Ranking da Galera - usar coleção ranking_povao
        ano_povao = 2025
        
        # Filtrar usuários por gênero
        usuarios_filtrados = [u for u in usuarios_cidade if u.get("sexo") == genero or u.get("genero") == genero]
        usuario_ids_filtrados = [u["id"] for u in usuarios_filtrados]
        
        if not usuario_ids_filtrados:
            return {"ranking": [], "total": 0, "cidade": cidade, "estado": estado}
        
        ranking_data = await db.ranking_povao.find(
            {"usuario_id": {"$in": usuario_ids_filtrados}, "ano": ano_povao},
            {"_id": 0}
        ).sort([("pontos_total", -1), ("total_corridas", -1), ("distancia_acumulada", -1)]).limit(limit).to_list(None)
        
        # Excluir atletas que também estão no ranking_anual (profissional tem prioridade)
        anual_entries = await db.ranking_anual.find(
            {"usuario_id": {"$in": usuario_ids_filtrados}, "ano": ano_povao},
            {"_id": 0, "usuario_id": 1}
        ).to_list(None)
        ids_no_ranking_anual = {e["usuario_id"] for e in anual_entries}
        ranking_data = [r for r in ranking_data if r["usuario_id"] not in ids_no_ranking_anual]
        
        if ranking_data:
            for idx, rank in enumerate(ranking_data, 1):
                usuario = next((u for u in usuarios_filtrados if u["id"] == rank["usuario_id"]), None)
                if usuario:
                    result.append({
                        "colocacao": idx,
                        "id": rank["usuario_id"],
                        "nome": usuario.get("nome", ""),
                        "foto_url": usuario.get("foto_url", ""),
                        "equipe": usuario.get("equipe", ""),
                        "cidade": usuario.get("cidade", ""),
                        "estado": usuario.get("estado", ""),
                        "faixa_etaria": usuario.get("faixa_etaria", ""),
                        "pontos": rank.get("pontos_total", 0),
                        "total_corridas": rank.get("total_corridas", 0),
                        "distancia_total": rank.get("distancia_acumulada", 0),
                        "is_elite": rank.get("pontos_total", 0) >= 100
                    })
        else:
            # Fallback galera: usar pontos_total do usuário, excluindo quem está no ranking_anual
            usuarios_galera = [u for u in usuarios_filtrados if u["id"] not in ids_no_ranking_anual]
            usuarios_ordenados = sorted(
                usuarios_galera,
                key=lambda x: (x.get("pontos_total", 0), x.get("total_corridas", 0)),
                reverse=True
            )[:limit]
            
            for idx, usuario in enumerate(usuarios_ordenados, 1):
                result.append({
                    "colocacao": idx,
                    "id": usuario["id"],
                    "nome": usuario.get("nome", ""),
                    "foto_url": usuario.get("foto_url", ""),
                    "equipe": usuario.get("equipe", ""),
                    "cidade": usuario.get("cidade", ""),
                    "estado": usuario.get("estado", ""),
                    "faixa_etaria": usuario.get("faixa_etaria", ""),
                    "pontos": usuario.get("pontos_total", 0),
                    "total_corridas": usuario.get("total_corridas", 0),
                    "distancia_total": 0,
                    "is_elite": usuario.get("pontos_total", 0) >= 100
                })
    else:
        # Ranking Profissional/Amador
        ranking_query = {
            "usuario_id": {"$in": usuario_ids},
            "ano": ano,
            "genero": genero,
            "categoria": categoria
        }
        
        ranking_data = await db.ranking_anual.find(
            ranking_query,
            {"_id": 0}
        ).sort([("pontos_total", -1), ("total_corridas", -1)]).limit(limit).to_list(None)
        
        if ranking_data:
            for idx, rank in enumerate(ranking_data, 1):
                usuario = next((u for u in usuarios_cidade if u["id"] == rank["usuario_id"]), None)
                if usuario:
                    result.append({
                        "colocacao": idx,
                        "id": rank["usuario_id"],
                        "nome": usuario.get("nome", ""),
                        "foto_url": usuario.get("foto_url", ""),
                        "equipe": usuario.get("equipe", ""),
                        "cidade": usuario.get("cidade", ""),
                        "estado": usuario.get("estado", ""),
                        "faixa_etaria": usuario.get("faixa_etaria", ""),
                        "pontos": rank.get("pontos_total", 0),
                        "total_corridas": rank.get("total_corridas", 0),
                        "is_elite": rank.get("pontos_total", 0) >= 100
                    })
        else:
            # Fallback profissional: usar pontos_total do usuário, excluindo quem está no ranking_povao
            usuarios_filtrados = [u for u in usuarios_cidade if u.get("sexo") == genero or u.get("genero") == genero]
            usuario_ids_filtrados = [u["id"] for u in usuarios_filtrados]
            
            ids_no_ranking_povao = set()
            povao_entries = await db.ranking_povao.find(
                {"usuario_id": {"$in": usuario_ids_filtrados}, "ano": ano},
                {"_id": 0, "usuario_id": 1}
            ).to_list(None)
            ids_no_ranking_povao = {e["usuario_id"] for e in povao_entries}
            
            usuarios_prof = [u for u in usuarios_filtrados if u["id"] not in ids_no_ranking_povao]
            usuarios_ordenados = sorted(
                [u for u in usuarios_prof if u.get("pontos_total", 0) > 0],
                key=lambda x: (x.get("pontos_total", 0), x.get("total_corridas", 0)),
                reverse=True
            )[:limit]
            
            for idx, usuario in enumerate(usuarios_ordenados, 1):
                result.append({
                    "colocacao": idx,
                    "id": usuario["id"],
                    "nome": usuario.get("nome", ""),
                    "foto_url": usuario.get("foto_url", ""),
                    "equipe": usuario.get("equipe", ""),
                    "cidade": usuario.get("cidade", ""),
                    "estado": usuario.get("estado", ""),
                    "faixa_etaria": usuario.get("faixa_etaria", ""),
                    "pontos": usuario.get("pontos_total", 0),
                    "total_corridas": usuario.get("total_corridas", 0),
                    "is_elite": usuario.get("pontos_total", 0) >= 100
                })
    
    return {
        "ranking": result,
        "total": len(result),
        "cidade": cidade,
        "estado": estado,
        "modalidade": modalidade
    }
