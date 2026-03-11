# /app/backend/routes/dashboard_stats_routes.py
# Endpoints para os 31 gráficos estratégicos do Dashboard do Super Admin

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

router = APIRouter(tags=["Dashboard Stats"])
logger = logging.getLogger(__name__)

# Importar dependências do servidor principal
from server import db, get_admin_user

# ============================================================
# DADOS INICIAIS - VISÃO GERAL DA PLATAFORMA
# ============================================================

@router.get("/dashboard/visao-geral")
async def get_visao_geral(admin: dict = Depends(get_admin_user)):
    """
    Retorna os dados iniciais da visão geral da plataforma.
    12 métricas principais em números.
    """
    hoje = datetime.now(timezone.utc)
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total de atletas
    total_atletas = await db.usuarios.count_documents({"role": "atleta"})
    
    # Total de corridas
    total_corridas = await db.corridas.count_documents({})
    
    # Total de resultados
    total_resultados = await db.resultados_pendentes.count_documents({})
    total_resultados += total_corridas  # Resultados aprovados = corridas
    
    # Total de assessorias (equipes únicas)
    pipeline_assessorias = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
        {"$group": {"_id": "$equipe"}},
        {"$count": "total"}
    ]
    result = await db.usuarios.aggregate(pipeline_assessorias).to_list(1)
    total_assessorias = result[0]["total"] if result else 0
    
    # Regiões com mais corredores (top 5 estados)
    pipeline_regioes = [
        {"$match": {"role": "atleta", "estado": {"$nin": ["", None]}}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    regioes = await db.usuarios.aggregate(pipeline_regioes).to_list(5)
    
    # Novos atletas Profissional/Amador (este mês)
    novos_prof_amador = await db.usuarios.count_documents({
        "role": "atleta",
        "modalidade_usuario": {"$ne": "povao_pace_livre"},
        "created_at": {"$gte": inicio_mes.isoformat()}
    })
    
    # Novos atletas Povão (este mês)
    novos_povao = await db.usuarios.count_documents({
        "role": "atleta",
        "modalidade_usuario": "povao_pace_livre",
        "created_at": {"$gte": inicio_mes.isoformat()}
    })
    
    # Novas corridas (este mês)
    novas_corridas = await db.corridas.count_documents({
        "data": {"$gte": inicio_mes.strftime("%Y-%m-%d")}
    })
    
    # Novos donos de assessoria (este mês)
    novos_donos = await db.usuarios.count_documents({
        "role": "dono_assessoria",
        "created_at": {"$gte": inicio_mes.isoformat()}
    })
    
    # Distâncias mais corridas
    pipeline_distancias = [
        {"$group": {"_id": "$distancia", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    distancias = await db.corridas.aggregate(pipeline_distancias).to_list(5)
    
    # Tempo médio (Profissional/Amador) - em minutos
    pipeline_tempo = [
        {"$match": {"modalidade": {"$ne": "povao_pace_livre"}, "tempo": {"$exists": True, "$ne": ""}}},
        {"$project": {
            "tempo_minutos": {
                "$let": {
                    "vars": {
                        "partes": {"$split": ["$tempo", ":"]}
                    },
                    "in": {
                        "$add": [
                            {"$multiply": [{"$toInt": {"$arrayElemAt": ["$$partes", 0]}}, 60]},
                            {"$toInt": {"$arrayElemAt": ["$$partes", 1]}}
                        ]
                    }
                }
            }
        }},
        {"$group": {"_id": None, "media": {"$avg": "$tempo_minutos"}}}
    ]
    try:
        tempo_result = await db.corridas.aggregate(pipeline_tempo).to_list(1)
        tempo_medio_min = tempo_result[0]["media"] if tempo_result else 0
        horas = int(tempo_medio_min // 60)
        minutos = int(tempo_medio_min % 60)
        tempo_medio = f"{horas}h{minutos:02d}min" if tempo_medio_min > 0 else "N/A"
    except:
        tempo_medio = "N/A"
    
    # Pace médio (Povão) - min/km
    pipeline_pace = [
        {"$match": {"modalidade": "povao_pace_livre", "pace": {"$exists": True, "$ne": ""}}},
        {"$project": {
            "pace_segundos": {
                "$let": {
                    "vars": {
                        "partes": {"$split": ["$pace", ":"]}
                    },
                    "in": {
                        "$add": [
                            {"$multiply": [{"$toInt": {"$arrayElemAt": ["$$partes", 0]}}, 60]},
                            {"$toInt": {"$arrayElemAt": ["$$partes", 1]}}
                        ]
                    }
                }
            }
        }},
        {"$group": {"_id": None, "media": {"$avg": "$pace_segundos"}}}
    ]
    try:
        pace_result = await db.corridas.aggregate(pipeline_pace).to_list(1)
        pace_medio_seg = pace_result[0]["media"] if pace_result else 0
        pace_min = int(pace_medio_seg // 60)
        pace_seg = int(pace_medio_seg % 60)
        pace_medio = f"{pace_min}:{pace_seg:02d}/km" if pace_medio_seg > 0 else "N/A"
    except:
        pace_medio = "N/A"
    
    return {
        "total_atletas": total_atletas,
        "total_corridas": total_corridas,
        "total_resultados": total_resultados,
        "total_assessorias": total_assessorias,
        "regioes_top": [{"estado": r["_id"], "count": r["count"]} for r in regioes],
        "novos_prof_amador": novos_prof_amador,
        "novos_povao": novos_povao,
        "novas_corridas": novas_corridas,
        "novos_donos_assessoria": novos_donos,
        "distancias_top": [{"distancia": d["_id"], "count": d["count"]} for d in distancias],
        "tempo_medio_prof_amador": tempo_medio,
        "pace_medio_povao": pace_medio
    }


# ============================================================
# GRÁFICOS 1-10
# ============================================================

@router.get("/dashboard/grafico/crescimento-atletas")
async def get_crescimento_atletas(admin: dict = Depends(get_admin_user)):
    """Gráfico 1: Crescimento de Atletas na Plataforma (linha) - últimos 12 meses"""
    hoje = datetime.now(timezone.utc)
    
    # Gerar dados para os últimos 12 meses
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1)
        
        count = await db.usuarios.count_documents({
            "role": "atleta",
            "created_at": {"$gte": inicio_mes.isoformat(), "$lt": fim_mes.isoformat()}
        })
        
        dados.append({
            "mes": inicio_mes.strftime("%b/%y"),
            "mes_num": inicio_mes.month,
            "ano": inicio_mes.year,
            "novos_atletas": count
        })
    
    # Calcular total acumulado
    acumulado = 0
    for d in dados:
        acumulado += d["novos_atletas"]
        d["total_acumulado"] = acumulado
    
    return {"dados": dados, "titulo": "Crescimento de Atletas na Plataforma"}


@router.get("/dashboard/grafico/atletas-ativos")
async def get_atletas_ativos(admin: dict = Depends(get_admin_user)):
    """Gráfico 2: Total de Atletas Ativos por Mês (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        # Atletas que participaram de corridas no mês
        pipeline = [
            {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
            {"$group": {"_id": "$usuario_id"}},
            {"$count": "ativos"}
        ]
        result = await db.corridas.aggregate(pipeline).to_list(1)
        ativos = result[0]["ativos"] if result else 0
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "atletas_ativos": ativos
        })
    
    return {"dados": dados, "titulo": "Atletas Ativos por Mês"}


@router.get("/dashboard/grafico/crescimento-eventos")
async def get_crescimento_eventos(admin: dict = Depends(get_admin_user)):
    """Gráfico 3: Crescimento de Eventos de Corrida (barras)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        # Eventos únicos (nome_evento) no mês
        pipeline = [
            {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
            {"$group": {"_id": "$nome_evento"}},
            {"$count": "eventos"}
        ]
        result = await db.corridas.aggregate(pipeline).to_list(1)
        eventos = result[0]["eventos"] if result else 0
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "eventos": eventos
        })
    
    return {"dados": dados, "titulo": "Eventos de Corrida por Mês"}


@router.get("/dashboard/grafico/crescimento-donos-assessoria")
async def get_crescimento_donos(admin: dict = Depends(get_admin_user)):
    """Gráfico 4: Crescimento de Donos de Assessoria (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1)
        
        count = await db.usuarios.count_documents({
            "role": "dono_assessoria",
            "created_at": {"$gte": inicio_mes.isoformat(), "$lt": fim_mes.isoformat()}
        })
        
        dados.append({
            "mes": inicio_mes.strftime("%b/%y"),
            "novos_donos": count
        })
    
    return {"dados": dados, "titulo": "Crescimento de Donos de Assessoria"}


@router.get("/dashboard/grafico/crescimento-assessorias")
async def get_crescimento_assessorias(admin: dict = Depends(get_admin_user)):
    """Gráfico 5: Crescimento de Assessorias Esportivas (barras)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1)
        
        # Contar equipes únicas criadas no mês
        pipeline = [
            {"$match": {
                "role": "atleta",
                "equipe": {"$nin": ["", None, "Sem equipe"]},
                "created_at": {"$gte": inicio_mes.isoformat(), "$lt": fim_mes.isoformat()}
            }},
            {"$group": {"_id": "$equipe"}},
            {"$count": "novas_equipes"}
        ]
        result = await db.usuarios.aggregate(pipeline).to_list(1)
        novas = result[0]["novas_equipes"] if result else 0
        
        dados.append({
            "mes": inicio_mes.strftime("%b/%y"),
            "novas_assessorias": novas
        })
    
    return {"dados": dados, "titulo": "Crescimento de Assessorias Esportivas"}


@router.get("/dashboard/grafico/resultados-registrados")
async def get_resultados_registrados(admin: dict = Depends(get_admin_user)):
    """Gráfico 6: Resultados Registrados na Plataforma (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        count = await db.corridas.count_documents({
            "data": {"$gte": inicio_mes, "$lt": fim_mes}
        })
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "resultados": count
        })
    
    return {"dados": dados, "titulo": "Resultados Registrados por Mês"}


@router.get("/dashboard/grafico/corridas-mes")
async def get_corridas_mes(admin: dict = Depends(get_admin_user)):
    """Gráfico 7: Corridas Registradas por Mês (barras)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        count = await db.corridas.count_documents({
            "data": {"$gte": inicio_mes, "$lt": fim_mes}
        })
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "corridas": count
        })
    
    return {"dados": dados, "titulo": "Corridas por Mês"}


@router.get("/dashboard/grafico/distribuicao-estados")
async def get_distribuicao_estados(admin: dict = Depends(get_admin_user)):
    """Gráfico 8: Distribuição de Atletas por Estado (mapa)"""
    pipeline = [
        {"$match": {"role": "atleta", "estado": {"$nin": ["", None]}}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    estados = await db.usuarios.aggregate(pipeline).to_list(None)
    
    total = sum(e["count"] for e in estados)
    
    return {
        "dados": [
            {
                "estado": e["_id"],
                "count": e["count"],
                "percentual": round((e["count"] / total * 100) if total > 0 else 0, 1)
            }
            for e in estados
        ],
        "total": total,
        "titulo": "Distribuição de Atletas por Estado"
    }


@router.get("/dashboard/grafico/distribuicao-cidades")
async def get_distribuicao_cidades(admin: dict = Depends(get_admin_user)):
    """Gráfico 9: Distribuição de Atletas por Cidade (ranking)"""
    pipeline = [
        {"$match": {"role": "atleta", "cidade": {"$nin": ["", None]}}},
        {"$group": {"_id": {"cidade": "$cidade", "estado": "$estado"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    cidades = await db.usuarios.aggregate(pipeline).to_list(15)
    
    total = await db.usuarios.count_documents({"role": "atleta"})
    
    return {
        "dados": [
            {
                "cidade": c["_id"]["cidade"],
                "estado": c["_id"]["estado"],
                "count": c["count"],
                "percentual": round((c["count"] / total * 100) if total > 0 else 0, 1)
            }
            for c in cidades
        ],
        "titulo": "Top 15 Cidades com Mais Corredores"
    }


@router.get("/dashboard/grafico/distribuicao-faixa-etaria")
async def get_distribuicao_faixa_etaria(admin: dict = Depends(get_admin_user)):
    """Gráfico 10: Distribuição por Faixa Etária (pizza)"""
    pipeline = [
        {"$match": {"role": "atleta", "faixa_etaria": {"$nin": ["", None, "Não informado"]}}},
        {"$group": {"_id": "$faixa_etaria", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    faixas = await db.usuarios.aggregate(pipeline).to_list(None)
    
    total = sum(f["count"] for f in faixas)
    
    # Ordenar faixas etárias
    ordem_faixas = ["até 17 anos", "18-29", "30-39", "40-49", "50-59", "60+"]
    dados_ordenados = []
    
    for ordem in ordem_faixas:
        encontrado = next((f for f in faixas if ordem.lower() in f["_id"].lower()), None)
        if encontrado:
            dados_ordenados.append({
                "faixa": encontrado["_id"],
                "count": encontrado["count"],
                "percentual": round((encontrado["count"] / total * 100) if total > 0 else 0, 1)
            })
        else:
            dados_ordenados.append({
                "faixa": ordem,
                "count": 0,
                "percentual": 0
            })
    
    # Adicionar faixas não mapeadas
    for f in faixas:
        if not any(d["faixa"] == f["_id"] for d in dados_ordenados):
            dados_ordenados.append({
                "faixa": f["_id"],
                "count": f["count"],
                "percentual": round((f["count"] / total * 100) if total > 0 else 0, 1)
            })
    
    return {"dados": dados_ordenados, "total": total, "titulo": "Distribuição por Faixa Etária"}


# ============================================================
# GRÁFICOS 11-20
# ============================================================

@router.get("/dashboard/grafico/distribuicao-sexo")
async def get_distribuicao_sexo(admin: dict = Depends(get_admin_user)):
    """Gráfico 11: Distribuição por Sexo (pizza)"""
    masculino = await db.usuarios.count_documents({"role": "atleta", "genero": "M"})
    feminino = await db.usuarios.count_documents({"role": "atleta", "genero": "F"})
    total = masculino + feminino
    
    return {
        "dados": [
            {"genero": "Masculino", "count": masculino, "percentual": round((masculino / total * 100) if total > 0 else 0, 1)},
            {"genero": "Feminino", "count": feminino, "percentual": round((feminino / total * 100) if total > 0 else 0, 1)}
        ],
        "total": total,
        "titulo": "Distribuição por Sexo"
    }


@router.get("/dashboard/grafico/distancias-mais-corridas")
async def get_distancias_mais_corridas(admin: dict = Depends(get_admin_user)):
    """Gráfico 12: Distâncias Mais Corridas (barras)"""
    pipeline = [
        {"$match": {"distancia": {"$nin": ["", None]}}},
        {"$group": {"_id": "$distancia", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    distancias = await db.corridas.aggregate(pipeline).to_list(None)
    
    total = sum(d["count"] for d in distancias)
    
    return {
        "dados": [
            {
                "distancia": d["_id"],
                "count": d["count"],
                "percentual": round((d["count"] / total * 100) if total > 0 else 0, 1)
            }
            for d in distancias
        ],
        "total": total,
        "titulo": "Distâncias Mais Corridas"
    }


@router.get("/dashboard/grafico/media-corridas-atleta")
async def get_media_corridas_atleta(admin: dict = Depends(get_admin_user)):
    """Gráfico 13: Número Médio de Corridas por Atleta (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        # Total de corridas no mês
        total_corridas = await db.corridas.count_documents({
            "data": {"$gte": inicio_mes, "$lt": fim_mes}
        })
        
        # Total de atletas únicos que correram
        pipeline = [
            {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
            {"$group": {"_id": "$usuario_id"}},
            {"$count": "atletas"}
        ]
        result = await db.corridas.aggregate(pipeline).to_list(1)
        atletas = result[0]["atletas"] if result else 1
        
        media = round(total_corridas / atletas, 2) if atletas > 0 else 0
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "media_corridas": media
        })
    
    return {"dados": dados, "titulo": "Média de Corridas por Atleta"}


@router.get("/dashboard/grafico/eventos-populares")
async def get_eventos_populares(admin: dict = Depends(get_admin_user)):
    """Gráfico 14: Eventos Mais Populares (ranking barras)"""
    pipeline = [
        {"$match": {"nome_evento": {"$nin": ["", None]}}},
        {"$group": {"_id": "$nome_evento", "participantes": {"$sum": 1}}},
        {"$sort": {"participantes": -1}},
        {"$limit": 10}
    ]
    eventos = await db.corridas.aggregate(pipeline).to_list(10)
    
    return {
        "dados": [
            {"evento": e["_id"], "participantes": e["participantes"]}
            for e in eventos
        ],
        "titulo": "Top 10 Eventos Mais Populares"
    }


@router.get("/dashboard/grafico/assessorias-mais-atletas")
async def get_assessorias_mais_atletas(admin: dict = Depends(get_admin_user)):
    """Gráfico 15: Assessorias com Mais Atletas (ranking)"""
    pipeline = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
        {"$group": {"_id": "$equipe", "atletas": {"$sum": 1}}},
        {"$sort": {"atletas": -1}},
        {"$limit": 10}
    ]
    assessorias = await db.usuarios.aggregate(pipeline).to_list(10)
    
    return {
        "dados": [
            {"assessoria": a["_id"], "atletas": a["atletas"]}
            for a in assessorias
        ],
        "titulo": "Top 10 Assessorias com Mais Atletas"
    }


@router.get("/dashboard/grafico/assessorias-mais-pontos")
async def get_assessorias_mais_pontos(admin: dict = Depends(get_admin_user)):
    """Gráfico 16: Assessorias com Mais Pontos no Ranking (barras)"""
    # Primeiro buscar equipes
    pipeline_equipes = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
        {"$group": {"_id": "$equipe", "atletas": {"$push": "$id"}}}
    ]
    equipes = await db.usuarios.aggregate(pipeline_equipes).to_list(None)
    
    # Calcular pontos por equipe
    ranking = []
    for equipe in equipes:
        # Buscar pontos dos atletas da equipe no ranking anual
        pipeline_pontos = [
            {"$match": {"usuario_id": {"$in": equipe["atletas"]}}},
            {"$group": {"_id": None, "total_pontos": {"$sum": "$pontos_total"}}}
        ]
        result = await db.ranking_anual.aggregate(pipeline_pontos).to_list(1)
        pontos = result[0]["total_pontos"] if result else 0
        
        if pontos > 0:
            ranking.append({
                "assessoria": equipe["_id"],
                "pontos": pontos
            })
    
    # Ordenar e pegar top 10
    ranking.sort(key=lambda x: x["pontos"], reverse=True)
    
    return {"dados": ranking[:10], "titulo": "Top 10 Assessorias por Pontos"}


@router.get("/dashboard/grafico/atletas-mais-ativos")
async def get_atletas_mais_ativos(admin: dict = Depends(get_admin_user)):
    """Gráfico 17: Atletas Mais Ativos (ranking)"""
    pipeline = [
        {"$group": {"_id": "$usuario_id", "total_corridas": {"$sum": 1}}},
        {"$sort": {"total_corridas": -1}},
        {"$limit": 10}
    ]
    atletas = await db.corridas.aggregate(pipeline).to_list(10)
    
    resultado = []
    for a in atletas:
        usuario = await db.usuarios.find_one({"id": a["_id"]}, {"_id": 0, "nome": 1, "equipe": 1})
        if usuario:
            resultado.append({
                "atleta": usuario["nome"],
                "equipe": usuario.get("equipe", ""),
                "total_corridas": a["total_corridas"]
            })
    
    return {"dados": resultado, "titulo": "Top 10 Atletas Mais Ativos"}


@router.get("/dashboard/grafico/atletas-maior-pontuacao")
async def get_atletas_maior_pontuacao(admin: dict = Depends(get_admin_user)):
    """Gráfico 18: Atletas com Maior Pontuação (ranking)"""
    pipeline = [
        {"$sort": {"pontos_total": -1}},
        {"$limit": 10}
    ]
    ranking = await db.ranking_anual.aggregate(pipeline).to_list(10)
    
    resultado = []
    for r in ranking:
        usuario = await db.usuarios.find_one({"id": r["usuario_id"]}, {"_id": 0, "nome": 1, "equipe": 1})
        if usuario:
            resultado.append({
                "atleta": usuario["nome"],
                "equipe": usuario.get("equipe", ""),
                "pontos": r["pontos_total"]
            })
    
    return {"dados": resultado, "titulo": "Top 10 Atletas por Pontuação"}


@router.get("/dashboard/grafico/evolucao-pontuacao")
async def get_evolucao_pontuacao(admin: dict = Depends(get_admin_user)):
    """Gráfico 19: Evolução de Pontuação do Ranking (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        # Total de pontos das corridas do mês
        pipeline = [
            {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
            {"$group": {"_id": None, "total_pontos": {"$sum": "$pontos"}}}
        ]
        result = await db.corridas.aggregate(pipeline).to_list(1)
        pontos = result[0]["total_pontos"] if result else 0
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "pontos_totais": pontos
        })
    
    return {"dados": dados, "titulo": "Evolução de Pontuação Total"}


@router.get("/dashboard/grafico/tempo-medio-corridas")
async def get_tempo_medio_corridas(admin: dict = Depends(get_admin_user)):
    """Gráfico 20: Tempo Médio das Corridas (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        # Calcular tempo médio em minutos
        pipeline = [
            {"$match": {
                "data": {"$gte": inicio_mes, "$lt": fim_mes},
                "tempo": {"$exists": True, "$ne": ""}
            }},
            {"$project": {
                "tempo_minutos": {
                    "$let": {
                        "vars": {"partes": {"$split": ["$tempo", ":"]}},
                        "in": {
                            "$add": [
                                {"$multiply": [{"$toInt": {"$arrayElemAt": ["$$partes", 0]}}, 60]},
                                {"$toInt": {"$arrayElemAt": ["$$partes", 1]}}
                            ]
                        }
                    }
                }
            }},
            {"$group": {"_id": None, "media": {"$avg": "$tempo_minutos"}}}
        ]
        
        try:
            result = await db.corridas.aggregate(pipeline).to_list(1)
            media = round(result[0]["media"], 0) if result and result[0]["media"] else 0
        except:
            media = 0
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "tempo_medio_min": media
        })
    
    return {"dados": dados, "titulo": "Tempo Médio das Corridas (minutos)"}


# ============================================================
# GRÁFICOS 21-31
# ============================================================

@router.get("/dashboard/grafico/pace-medio-distancia")
async def get_pace_medio_distancia(admin: dict = Depends(get_admin_user)):
    """Gráfico 21: Pace Médio por Distância (comparativo)"""
    distancias = ["5KM", "10KM", "21KM", "42KM"]
    
    dados = []
    for dist in distancias:
        pipeline = [
            {"$match": {
                "distancia": {"$regex": dist, "$options": "i"},
                "pace": {"$exists": True, "$ne": ""}
            }},
            {"$project": {
                "pace_segundos": {
                    "$let": {
                        "vars": {"partes": {"$split": ["$pace", ":"]}},
                        "in": {
                            "$add": [
                                {"$multiply": [{"$toInt": {"$arrayElemAt": ["$$partes", 0]}}, 60]},
                                {"$toInt": {"$arrayElemAt": ["$$partes", 1]}}
                            ]
                        }
                    }
                }
            }},
            {"$group": {"_id": None, "media": {"$avg": "$pace_segundos"}}}
        ]
        
        try:
            result = await db.corridas.aggregate(pipeline).to_list(1)
            if result and result[0]["media"]:
                pace_seg = result[0]["media"]
                pace_min = int(pace_seg // 60)
                pace_s = int(pace_seg % 60)
                pace_str = f"{pace_min}:{pace_s:02d}"
            else:
                pace_str = "N/A"
                pace_seg = 0
        except:
            pace_str = "N/A"
            pace_seg = 0
        
        dados.append({
            "distancia": dist,
            "pace_medio": pace_str,
            "pace_segundos": pace_seg
        })
    
    return {"dados": dados, "titulo": "Pace Médio por Distância"}


@router.get("/dashboard/grafico/participacao-media-evento")
async def get_participacao_media_evento(admin: dict = Depends(get_admin_user)):
    """Gráfico 22: Participação Média por Evento (barras)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        # Contar eventos e participantes
        pipeline = [
            {"$match": {
                "data": {"$gte": inicio_mes, "$lt": fim_mes},
                "nome_evento": {"$nin": ["", None]}
            }},
            {"$group": {
                "_id": "$nome_evento",
                "participantes": {"$sum": 1}
            }},
            {"$group": {
                "_id": None,
                "total_eventos": {"$sum": 1},
                "media_participantes": {"$avg": "$participantes"}
            }}
        ]
        result = await db.corridas.aggregate(pipeline).to_list(1)
        media = round(result[0]["media_participantes"], 1) if result else 0
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "media_participantes": media
        })
    
    return {"dados": dados, "titulo": "Participação Média por Evento"}


@router.get("/dashboard/grafico/taxa-retorno-atletas")
async def get_taxa_retorno_atletas(admin: dict = Depends(get_admin_user)):
    """Gráfico 23: Taxa de Retorno de Atletas (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        inicio_mes_anterior = (mes.replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
        
        # Atletas que correram no mês atual
        pipeline_atual = [
            {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
            {"$group": {"_id": "$usuario_id"}}
        ]
        atletas_atual = await db.corridas.aggregate(pipeline_atual).to_list(None)
        ids_atual = [a["_id"] for a in atletas_atual]
        
        # Atletas que também correram no mês anterior
        if ids_atual:
            pipeline_retorno = [
                {"$match": {
                    "data": {"$gte": inicio_mes_anterior, "$lt": inicio_mes},
                    "usuario_id": {"$in": ids_atual}
                }},
                {"$group": {"_id": "$usuario_id"}}
            ]
            atletas_retorno = await db.corridas.aggregate(pipeline_retorno).to_list(None)
            taxa = round((len(atletas_retorno) / len(ids_atual) * 100) if ids_atual else 0, 1)
        else:
            taxa = 0
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "taxa_retorno": taxa
        })
    
    return {"dados": dados, "titulo": "Taxa de Retorno de Atletas (%)"}


@router.get("/dashboard/grafico/novos-vs-recorrentes")
async def get_novos_vs_recorrentes(admin: dict = Depends(get_admin_user)):
    """Gráfico 24: Atletas Novos vs Recorrentes (comparativo)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        # Atletas que correram no mês
        pipeline = [
            {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
            {"$group": {"_id": "$usuario_id"}}
        ]
        atletas_mes = await db.corridas.aggregate(pipeline).to_list(None)
        ids_mes = [a["_id"] for a in atletas_mes]
        
        # Verificar quais são novos (primeira corrida no mês)
        novos = 0
        recorrentes = 0
        for atleta_id in ids_mes:
            primeira = await db.corridas.find_one(
                {"usuario_id": atleta_id},
                sort=[("data", 1)]
            )
            if primeira and primeira.get("data", "") >= inicio_mes:
                novos += 1
            else:
                recorrentes += 1
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "novos": novos,
            "recorrentes": recorrentes
        })
    
    return {"dados": dados, "titulo": "Atletas Novos vs Recorrentes"}


@router.get("/dashboard/grafico/engajamento-plataforma")
async def get_engajamento_plataforma(admin: dict = Depends(get_admin_user)):
    """Gráfico 25: Engajamento na Plataforma (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(29, -1, -1):
        dia = hoje - timedelta(days=i)
        data_str = dia.strftime("%Y-%m-%d")
        
        # Contar corridas registradas no dia (proxy para atividade)
        corridas_dia = await db.corridas.count_documents({
            "data": data_str
        })
        
        # Contar logins do dia
        logins_dia = await db.login_history.count_documents({
            "data_hora": {"$regex": f"^{data_str}"}
        })
        
        dados.append({
            "dia": dia.strftime("%d/%m"),
            "atividades": corridas_dia,
            "logins": logins_dia
        })
    
    return {"dados": dados, "titulo": "Engajamento nos Últimos 30 Dias"}


@router.get("/dashboard/grafico/atletas-por-assessoria")
async def get_atletas_por_assessoria(admin: dict = Depends(get_admin_user)):
    """Gráfico 26: Atletas por Assessoria (barras)"""
    pipeline = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
        {"$group": {"_id": "$equipe", "atletas": {"$sum": 1}}},
        {"$sort": {"atletas": -1}},
        {"$limit": 15}
    ]
    assessorias = await db.usuarios.aggregate(pipeline).to_list(15)
    
    return {
        "dados": [{"assessoria": a["_id"], "atletas": a["atletas"]} for a in assessorias],
        "titulo": "Atletas por Assessoria"
    }


@router.get("/dashboard/grafico/crescimento-regional")
async def get_crescimento_regional(admin: dict = Depends(get_admin_user)):
    """Gráfico 27: Crescimento Regional (mapa)"""
    # Mapeamento de estados para regiões
    regioes = {
        "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
        "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
        "Centro-Oeste": ["DF", "GO", "MT", "MS"],
        "Sudeste": ["ES", "MG", "RJ", "SP"],
        "Sul": ["PR", "RS", "SC"]
    }
    
    pipeline = [
        {"$match": {"role": "atleta", "estado": {"$nin": ["", None]}}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}}
    ]
    estados = await db.usuarios.aggregate(pipeline).to_list(None)
    
    # Agrupar por região
    dados_regioes = {}
    for regiao, ufs in regioes.items():
        total = sum(e["count"] for e in estados if e["_id"] in ufs)
        dados_regioes[regiao] = total
    
    total_geral = sum(dados_regioes.values())
    
    return {
        "dados": [
            {
                "regiao": r,
                "count": c,
                "percentual": round((c / total_geral * 100) if total_geral > 0 else 0, 1)
            }
            for r, c in dados_regioes.items()
        ],
        "estados": [{"estado": e["_id"], "count": e["count"]} for e in estados],
        "titulo": "Crescimento Regional"
    }


@router.get("/dashboard/grafico/provas-competitivas")
async def get_provas_competitivas(admin: dict = Depends(get_admin_user)):
    """Gráfico 28: Provas Mais Competitivas (comparativo)"""
    pipeline = [
        {"$match": {"nome_evento": {"$nin": ["", None]}}},
        {"$group": {
            "_id": "$nome_evento",
            "participantes": {"$sum": 1},
            "atletas_unicos": {"$addToSet": "$usuario_id"}
        }},
        {"$project": {
            "nome_evento": "$_id",
            "participantes": 1,
            "atletas_unicos": {"$size": "$atletas_unicos"}
        }},
        {"$sort": {"atletas_unicos": -1}},
        {"$limit": 10}
    ]
    eventos = await db.corridas.aggregate(pipeline).to_list(10)
    
    return {
        "dados": [
            {
                "evento": e["_id"],
                "participantes": e["participantes"],
                "atletas_unicos": e["atletas_unicos"]
            }
            for e in eventos
        ],
        "titulo": "Provas Mais Competitivas"
    }


@router.get("/dashboard/grafico/evolucao-rankings")
async def get_evolucao_rankings(admin: dict = Depends(get_admin_user)):
    """Gráfico 29: Evolução de Rankings (linha)"""
    hoje = datetime.now(timezone.utc)
    
    dados = []
    for i in range(11, -1, -1):
        mes = hoje - timedelta(days=30 * i)
        inicio_mes = mes.replace(day=1).strftime("%Y-%m-%d")
        fim_mes = (mes.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
        
        # Total de atletas no ranking até esse mês
        total_ranking = await db.ranking_anual.count_documents({})
        
        # Novos entrantes no ranking (atletas que fizeram primeira corrida)
        pipeline = [
            {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
            {"$group": {"_id": "$usuario_id"}}
        ]
        novos = await db.corridas.aggregate(pipeline).to_list(None)
        
        dados.append({
            "mes": mes.strftime("%b/%y"),
            "total_ranking": total_ranking,
            "movimentacoes": len(novos)
        })
    
    return {"dados": dados, "titulo": "Evolução do Ranking"}


@router.get("/dashboard/grafico/donos-assessoria-mapa")
async def get_donos_assessoria_mapa(admin: dict = Depends(get_admin_user)):
    """Gráfico 30: Donos de Assessoria por Estado (mapa)"""
    pipeline = [
        {"$match": {"role": "dono_assessoria", "estado": {"$nin": ["", None]}}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    estados = await db.usuarios.aggregate(pipeline).to_list(None)
    
    total = sum(e["count"] for e in estados)
    
    return {
        "dados": [
            {
                "estado": e["_id"],
                "count": e["count"],
                "percentual": round((e["count"] / total * 100) if total > 0 else 0, 1)
            }
            for e in estados
        ],
        "total": total,
        "titulo": "Donos de Assessoria por Estado"
    }


@router.get("/dashboard/grafico/distribuicao-etnia")
async def get_distribuicao_etnia(admin: dict = Depends(get_admin_user)):
    """Gráfico 31: Distribuição por Etnia (pizza)"""
    pipeline = [
        {"$match": {"role": "atleta", "etnia": {"$nin": ["", None, "Não informado"]}}},
        {"$group": {"_id": "$etnia", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    etnias = await db.usuarios.aggregate(pipeline).to_list(None)
    
    total = sum(e["count"] for e in etnias)
    
    # Garantir todas as etnias mesmo com 0
    etnias_padrao = ["Branca", "Negra", "Parda", "Indígena", "Amarela"]
    dados = []
    
    for etnia in etnias_padrao:
        encontrado = next((e for e in etnias if e["_id"].lower() == etnia.lower()), None)
        if encontrado:
            dados.append({
                "etnia": encontrado["_id"],
                "count": encontrado["count"],
                "percentual": round((encontrado["count"] / total * 100) if total > 0 else 0, 1)
            })
        else:
            dados.append({
                "etnia": etnia,
                "count": 0,
                "percentual": 0
            })
    
    return {"dados": dados, "total": total, "titulo": "Distribuição por Etnia"}
