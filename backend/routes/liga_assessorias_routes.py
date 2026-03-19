# /app/backend/routes/liga_assessorias_routes.py
# Liga de Assessorias - ROE-RR

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime
import urllib.parse

from config import db
from routes.auth_routes import get_current_user
from routes.assessorias_routes import get_ranking_assessorias

router = APIRouter(prefix="/liga-assessorias", tags=["Liga Assessorias"])


@router.get("/estados")
async def get_estados_com_assessorias():
    """Lista estados que têm assessorias cadastradas"""
    pipeline = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None], "$exists": True}}},
        {"$group": {"_id": "$estado"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [e["_id"] for e in result]


@router.get("/cidades")
async def get_cidades_com_assessorias(estado: str = None):
    """Lista cidades que têm assessorias cadastradas"""
    match_filter = {"role": "atleta", "equipe": {"$nin": ["", None], "$exists": True}}
    if estado:
        match_filter["estado"] = estado
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {"_id": "$cidade"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [c["_id"] for c in result]


@router.get("/comparacao-mensal/{nome_equipe}")
async def get_comparacao_mensal_assessoria(nome_equipe: str):
    """
    Retorna comparação de desempenho entre mês atual e mês anterior
    Para uso no Dashboard do Dono de Assessoria
    """
    nome_decoded = urllib.parse.unquote(nome_equipe)
    
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    # Calcular mês anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual
    
    # Formatação de datas
    inicio_mes_atual = f"{ano_atual}-{mes_atual:02d}-01"
    inicio_mes_anterior = f"{ano_anterior}-{mes_anterior:02d}-01"
    fim_mes_anterior = inicio_mes_atual
    
    # Próximo mês para fim do mês atual
    if mes_atual == 12:
        fim_mes_atual = f"{ano_atual + 1}-01-01"
    else:
        fim_mes_atual = f"{ano_atual}-{mes_atual + 1:02d}-01"
    
    # Buscar atletas da equipe
    atletas = await db.usuarios.find(
        {"role": "atleta", "equipe": nome_decoded},
        {"_id": 0, "id": 1, "created_at": 1}
    ).to_list(None)
    
    if not atletas:
        raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    atletas_ids = [a["id"] for a in atletas]
    
    # Resultados do mês atual
    resultados_mes_atual = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_atual, "$lt": fim_mes_atual}
    })
    
    # Resultados do mês anterior
    resultados_mes_anterior = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_anterior, "$lt": fim_mes_anterior}
    })
    
    # Novos atletas no mês atual
    novos_atletas_atual = sum(1 for a in atletas 
        if a.get("created_at", "").startswith(f"{ano_atual}-{mes_atual:02d}"))
    
    # Novos atletas no mês anterior
    novos_atletas_anterior = sum(1 for a in atletas 
        if a.get("created_at", "").startswith(f"{ano_anterior}-{mes_anterior:02d}"))
    
    # Buscar ranking do mês atual
    ranking_atual_data = await get_ranking_assessorias(tipo="nacional", mes=mes_atual)
    posicao_atual = next(
        (e["posicao"] for e in ranking_atual_data["ranking"] if e["nome"] == nome_decoded),
        None
    )
    
    # Buscar ranking do mês anterior
    ranking_anterior_data = await get_ranking_assessorias(tipo="nacional", mes=mes_anterior)
    posicao_anterior = next(
        (e["posicao"] for e in ranking_anterior_data["ranking"] if e["nome"] == nome_decoded),
        None
    )
    
    # Calcular pontos do mês atual e anterior
    corridas_atual = await db.corridas.find({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_atual, "$lt": fim_mes_atual}
    }).to_list(None)
    
    corridas_anterior = await db.corridas.find({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_anterior, "$lt": fim_mes_anterior}
    }).to_list(None)
    
    def calcular_pontos(corridas_lista):
        pontos = 0
        for c in corridas_lista:
            pontos += 1.0  # Por resultado
            colocacao = c.get("colocacao", 0)
            modalidade = c.get("modalidade", "profissional_amador")
            if modalidade == "profissional_amador" and colocacao > 0:
                if colocacao == 1:
                    pontos += 1.0
                elif 2 <= colocacao <= 5:
                    pontos += 0.5
        return round(pontos, 1)
    
    pontos_atual = calcular_pontos(corridas_atual)
    pontos_anterior = calcular_pontos(corridas_anterior)
    
    # Nomes dos meses
    meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    def calc_variacao(atual, anterior):
        if anterior == 0:
            return 100 if atual > 0 else 0
        return round(((atual - anterior) / anterior) * 100, 1)
    
    return {
        "equipe": nome_decoded,
        "mes_atual": {
            "nome": meses_nomes[mes_atual - 1],
            "numero": mes_atual,
            "ano": ano_atual,
            "resultados": resultados_mes_atual,
            "novos_atletas": novos_atletas_atual,
            "pontos": pontos_atual,
            "posicao_ranking": posicao_atual
        },
        "mes_anterior": {
            "nome": meses_nomes[mes_anterior - 1],
            "numero": mes_anterior,
            "ano": ano_anterior,
            "resultados": resultados_mes_anterior,
            "novos_atletas": novos_atletas_anterior,
            "pontos": pontos_anterior,
            "posicao_ranking": posicao_anterior
        },
        "variacoes": {
            "resultados": calc_variacao(resultados_mes_atual, resultados_mes_anterior),
            "novos_atletas": calc_variacao(novos_atletas_atual, novos_atletas_anterior),
            "pontos": calc_variacao(pontos_atual, pontos_anterior),
            "posicao": (posicao_anterior - posicao_atual) if posicao_atual and posicao_anterior else 0
        }
    }
