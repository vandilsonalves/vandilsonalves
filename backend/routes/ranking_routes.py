# /app/backend/routes/ranking_routes.py
# Módulo de Ranking - Rankings gerais, povão, semanal, mensal

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, timezone, timedelta

ANO_ATUAL = datetime.now(timezone.utc).year
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
import io
import csv

from config import db
from models import RankingResponse
from routes.auth_routes import get_current_user, get_admin_user
from services.cache_service import cached, cache_service, invalidate_on_ranking_change

router = APIRouter(tags=["Ranking"])


# Helper para validar e limitar parâmetros
def validate_limit(limit: int, max_limit: int = 20) -> int:
    return min(max(1, limit), max_limit)

def validate_page(page: int) -> int:
    return max(1, page)

def validate_ano(ano: int) -> int:
    if ano < 2020 or ano > ANO_ATUAL + 1:
        raise HTTPException(status_code=400, detail="Ano invalido")
    return ano


# ==================== RANKING POVÃO ====================

@router.get("/ranking/povao")
@cached(prefix='ranking', ttl_key='ranking_povao')
async def get_ranking_povao(genero: str = "M", page: int = 1, limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Retorna o ranking da Galera (paginado) - requer autenticacao"""
    limit = validate_limit(limit)
    page = validate_page(page)
    # Buscar ranking existente
    ranking_list = await db.ranking_povao.find(
        {"ano": ANO_ATUAL, "genero": genero},
        {"_id": 0}
    ).sort([("pontos_total", -1), ("total_corridas", -1), ("distancia_acumulada", -1)]).to_list(None)

    ranked_user_ids = set(r["usuario_id"] for r in ranking_list)

    # Buscar TODOS os atletas da galera desse genero (incluindo sem resultado)
    all_galera = await db.usuarios.find(
        {"role": {"$in": ["atleta", "dono_assessoria"]}, "modalidade_usuario": "povao_pace_livre", "genero": genero},
        {"_id": 0, "id": 1, "nome": 1, "estado": 1, "cidade": 1, "faixa_etaria": 1, "foto_url": 1, "equipe": 1}
    ).to_list(None)
    user_map = {u["id"]: u for u in all_galera}

    result = []
    # Primeiro: atletas com pontos (ranking_povao)
    for rank in ranking_list:
        usuario = user_map.get(rank["usuario_id"])
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

    # Depois: atletas sem resultado ainda (0 pontos)
    pos_base = len(result)
    for u in all_galera:
        if u["id"] not in ranked_user_ids:
            pos_base += 1
            result.append({
                "colocacao": pos_base,
                "posicao": pos_base,
                "atleta_id": u["id"],
                "nome": u.get("nome", ""),
                "uf": u.get("estado", ""),
                "cidade": u.get("cidade", ""),
                "faixa_etaria": u.get("faixa_etaria", "Não informado"),
                "foto_url": u.get("foto_url", ""),
                "equipe": u.get("equipe", ""),
                "total_corridas": 0,
                "distancia_acumulada": 0,
                "pontos": 0
            })

    total = len(result)
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]

    return {
        "genero": "Masculino" if genero == "M" else "Feminino",
        "total_atletas": total,
        "page": page,
        "limit": limit,
        "has_more": end < total,
        "ranking": paginated
    }


@router.get("/ranking/povao/stats")
@cached(prefix='ranking', ttl_key='stats')
async def get_povao_stats():
    """Retorna estatísticas do ranking da Galera"""
    # Contar TODOS os atletas cadastrados na modalidade galera (não apenas os com resultado)
    total_atletas_m = await db.usuarios.count_documents({
        "role": {"$in": ["atleta", "dono_assessoria"]},
        "modalidade_usuario": "povao_pace_livre",
        "genero": "M"
    })
    total_atletas_f = await db.usuarios.count_documents({
        "role": {"$in": ["atleta", "dono_assessoria"]},
        "modalidade_usuario": "povao_pace_livre",
        "genero": "F"
    })
    
    pipeline = [
        {"$match": {"modalidade": "povao_pace_livre", "ano": ANO_ATUAL}},
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
async def get_povao_ranking_semanal(genero: str = "M", limit: int = 10, current_user: dict = Depends(get_current_user)):
    """Retorna o Top 10 da Galera da última semana"""
    limit = validate_limit(limit)
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
    
    # Batch fetch usuarios (evita N+1 queries)
    user_ids = [r["_id"] for r in resultados]
    usuarios_list = await db.usuarios.find({"id": {"$in": user_ids}, "genero": genero}, {"_id": 0}).to_list(None)
    user_map = {u["id"]: u for u in usuarios_list}
    
    ranking = []
    for idx, r in enumerate(resultados):
        usuario = user_map.get(r["_id"])
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
async def get_povao_ranking_mensal(genero: str = "M", limit: int = 10, current_user: dict = Depends(get_current_user)):
    """Retorna o Top 10 da Galera do mês atual"""
    limit = validate_limit(limit)
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
    
    # Batch fetch usuarios (evita N+1 queries)
    user_ids = [r["_id"] for r in resultados]
    usuarios_list = await db.usuarios.find({"id": {"$in": user_ids}, "genero": genero}, {"_id": 0}).to_list(None)
    user_map = {u["id"]: u for u in usuarios_list}
    
    ranking = []
    for idx, r in enumerate(resultados):
        usuario = user_map.get(r["_id"])
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
async def get_povao_destaque_mes(current_user: dict = Depends(get_current_user)):
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
    semana_offset: int = 0,
    current_user: dict = Depends(get_current_user)
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
    
    genero_label = {"M": "Masculino", "F": "Feminino"}.get(genero, genero)
    categoria_label = {"normal": "", "pcd": "PCD", "cadeirante": "Cadeirante"}.get(categoria, "")
    modalidade_label = f"{categoria_label} / {genero_label}" if categoria_label else genero_label
    
    return {
        "periodo": f"{inicio_semana.strftime('%d/%m/%Y')} a {fim_semana.strftime('%d/%m/%Y')}",
        "genero": genero_label,
        "categoria": categoria,
        "modalidade": modalidade_label,
        "ranking": ranking
    }


# ==================== RANKING MENSAL ====================

@router.get("/ranking/mensal")
@cached(prefix='ranking', ttl_key='ranking_mensal')
async def get_ranking_mensal(
    genero: str = "M",
    categoria: str = "normal",
    mes_offset: int = 0,
    current_user: dict = Depends(get_current_user)
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
    
    genero_label = {"M": "Masculino", "F": "Feminino"}.get(genero, genero)
    categoria_label = {"normal": "", "pcd": "PCD", "cadeirante": "Cadeirante"}.get(categoria, "")
    modalidade_label = f"{categoria_label} / {genero_label}" if categoria_label else genero_label
    
    return {
        "periodo": f"{meses[mes_atual-1]} {ano_atual}",
        "mes": meses[mes_atual-1],
        "ano": ano_atual,
        "genero": genero_label,
        "categoria": categoria,
        "modalidade": modalidade_label,
        "ranking": ranking
    }


# ==================== DESTAQUE DO MÊS ====================

@router.get("/ranking/destaque-mes")
@cached(prefix='ranking', ttl_key='ranking_destaque')
async def get_destaque_mes(mes: int = None, ano: int = None, genero: str = None, categoria: str = None, current_user: dict = Depends(get_current_user)):
    """Retorna os destaques do mês (top 3 + estatísticas), filtrado por modalidade se informado"""
    
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
    
    # Se genero e categoria foram informados, filtra para UMA modalidade
    if genero and categoria:
        categorias_filtro = []
        genero_label = {"M": "Masculino", "F": "Feminino"}.get(genero, genero)
        cat_label = {"normal": "", "pcd": "PCD", "cadeirante": "Cadeirante"}.get(categoria, "")
        nome_cat = f"{cat_label} / {genero_label}" if cat_label else genero_label
        categorias_filtro.append((nome_cat, categoria, genero))
    else:
        categorias_filtro = [
            ("Masculino", "normal", "M"),
            ("Feminino", "normal", "F"),
            ("PCD / M", "pcd", "M"),
            ("PCD / F", "pcd", "F"),
            ("Cadeirante / M", "cadeirante", "M"),
            ("Cadeirante / F", "cadeirante", "F")
        ]
    
    destaques = {}
    
    for nome_cat, cat_db, gen_db in categorias_filtro:
        pipeline = [
            {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
            {"$lookup": {"from": "usuarios", "localField": "usuario_id", "foreignField": "id", "as": "u"}},
            {"$unwind": "$u"},
            {"$match": {"u.categoria": cat_db, "u.genero": gen_db}},
            {"$group": {
                "_id": "$usuario_id",
                "nome": {"$first": "$u.nome"},
                "equipe": {"$first": "$u.equipe"},
                "cidade": {"$first": "$u.cidade"},
                "estado": {"$first": "$u.estado"},
                "foto_url": {"$first": "$u.foto_url"},
                "pontos_mes": {"$sum": "$pontos"},
                "corridas_mes": {"$sum": 1}
            }},
            {"$sort": {"pontos_mes": -1}},
            {"$limit": 3}
        ]
        
        top3_raw = await db.corridas.aggregate(pipeline).to_list(None)
        top3 = [{
            "atleta_id": r["_id"],
            "nome": r["nome"],
            "equipe": r.get("equipe", ""),
            "cidade": r.get("cidade", ""),
            "estado": r.get("estado", ""),
            "foto_url": r.get("foto_url", ""),
            "pontos_mes": r["pontos_mes"],
            "corridas_mes": r["corridas_mes"]
        } for r in top3_raw]
        
        destaques[nome_cat] = top3
    
    # Filtro de corridas (por modalidade se informado)
    match_corridas = {"data": {"$gte": inicio_mes, "$lt": fim_mes}}
    
    # Buscar usuario_ids da modalidade se filtrado
    usuario_ids_filtro = None
    if genero and categoria:
        usuarios_mod = await db.usuarios.find(
            {"genero": genero, "categoria": categoria}, {"id": 1, "_id": 0}
        ).to_list(None)
        usuario_ids_filtro = [u["id"] for u in usuarios_mod]
        match_corridas["usuario_id"] = {"$in": usuario_ids_filtro}
    
    # Total de corridas
    total_corridas_mes = await db.corridas.count_documents(match_corridas)
    
    # Mais ativo (por modalidade se filtrado)
    pipeline_mais_ativo = [
        {"$match": match_corridas},
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
                "equipe": usuario_ativo.get("equipe", ""),
                "foto_url": usuario_ativo.get("foto_url", ""),
                "total_corridas": mais_ativo_result[0]["total_corridas"]
            }
    
    # Mais pontos (por modalidade se filtrado)
    pipeline_mais_pontos = [
        {"$match": match_corridas},
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
                "equipe": usuario_pontos.get("equipe", ""),
                "foto_url": usuario_pontos.get("foto_url", ""),
                "total_pontos": mais_pontos_result[0]["total_pontos"]
            }
    
    # Label da modalidade
    modalidade_label = None
    if genero and categoria:
        genero_label = {"M": "Masculino", "F": "Feminino"}.get(genero, genero)
        cat_label = {"normal": "", "pcd": "PCD", "cadeirante": "Cadeirante"}.get(categoria, "")
        modalidade_label = f"{cat_label} / {genero_label}" if cat_label else genero_label
    
    return {
        "mes": meses_nome[mes_atual],
        "ano": ano_atual,
        "modalidade": modalidade_label,
        "total_corridas_mes": total_corridas_mes,
        "destaques_categoria": destaques,
        "mais_ativo_mes": mais_ativo,
        "mais_pontos_mes": mais_pontos
    }


# ==================== RANKING POR CATEGORIA ====================

@router.get("/ranking/categoria/{categoria}/{genero}", response_model=None)
async def get_ranking_por_categoria(
    categoria: str,
    genero: str,
    ano: int = ANO_ATUAL,
    limit: int = 20,
    page: int = 1,
    faixa: str = None,
    equipe: str = None,
    cidade: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Retorna ranking por categoria e gênero - requer autenticacao
    
    Categoria pode ser:
    - masculino, feminino -> normal M/F
    - pcd-m, pcd-f -> pcd M/F
    - cadeirante-m, cadeirante-f -> cadeirante M/F
    - normal, pcd, cadeirante -> usa gênero passado
    """
    limit = validate_limit(limit)
    page = validate_page(page)
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
    ).sort([("pontos_total", -1), ("total_corridas", -1)]).to_list(None)

    ranked_user_ids = set(r["usuario_id"] for r in ranking_list)

    # Buscar IDs de atletas com autorização ativa
    autorizacoes_ativas = set()
    auth_cursor = db.autorizacoes.find({"status": "ativa"}, {"_id": 0, "atleta_id": 1})
    async for auth in auth_cursor:
        autorizacoes_ativas.add(auth["atleta_id"])

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
                is_pendente=rank.get("total_corridas", 0) < 3,
                is_premium=(rank["usuario_id"] in autorizacoes_ativas)
            ))

    # Incluir atletas cadastrados SEM resultado (0 pontos) no final
    user_query = {
        "role": {"$in": ["atleta", "dono_assessoria"]},
        "modalidade_usuario": {"$ne": "povao_pace_livre"},
        "genero": gen_db,
        "categoria": cat_db,
    }
    if faixa:
        user_query["faixa_etaria"] = faixa

    all_users = await db.usuarios.find(user_query, {"_id": 0, "id": 1, "nome": 1, "estado": 1, "cidade": 1, "equipe": 1, "faixa_etaria": 1, "foto_url": 1}).to_list(None)
    for u in all_users:
        if u["id"] not in ranked_user_ids:
            if equipe and equipe.lower() not in u.get("equipe", "").lower():
                continue
            if cidade and cidade.lower() not in u.get("cidade", "").lower():
                continue
            result.append(RankingResponse(
                id=u["id"],
                colocacao=len(result) + 1,
                uf=u.get("estado", ""),
                foto_url=u.get("foto_url", ""),
                nome=u.get("nome", ""),
                cidade=u.get("cidade", ""),
                equipe=u.get("equipe", ""),
                faixa_etaria=u.get("faixa_etaria", "Não informado"),
                total_corridas=0,
                pontos=0,
                is_elite=False,
                is_pendente=True,
                is_premium=(u["id"] in autorizacoes_ativas)
            ))
    
    total = len(result)
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]
    
    return {
        "total_atletas": total,
        "page": page,
        "limit": limit,
        "has_more": end < total,
        "ranking": [r.dict() if hasattr(r, 'dict') else r for r in paginated]
    }


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
    return {"faixas": ["Até 17", "18-29", "30-39", "40-49", "50-59", "60-69", "70+"]}


@router.get("/ranking/equipes")
@cached(prefix='ranking', ttl_key='equipes')
async def get_equipes(page: int = 1, limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Lista equipes/assessorias ativas (paginado) - requer autenticacao"""
    limit = validate_limit(limit)
    page = validate_page(page)
    pipeline = [
        {"$match": {"role": {"$in": ["atleta", "dono_assessoria"]}, "equipe": {"$ne": "", "$exists": True}}},
        {"$group": {"_id": "$equipe", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    equipes_all = await db.usuarios.aggregate(pipeline).to_list(None)
    equipes_filtered = [{"nome": e["_id"], "atletas": e["count"]} for e in equipes_all if e["_id"]]
    
    total = len(equipes_filtered)
    start = (page - 1) * limit
    end = start + limit
    paginated = equipes_filtered[start:end]
    
    return {
        "total_equipes": total,
        "page": page,
        "limit": limit,
        "has_more": end < total,
        "equipes": paginated
    }


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
    modalidade: str = "profissional",
    genero: str = "M",
    categoria: str = "normal",
    ano: int = ANO_ATUAL,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Ranking filtrado por cidade - requer autenticacao"""
    limit = validate_limit(limit)
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
        ano_povao = ANO_ATUAL
        
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
