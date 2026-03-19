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



@router.get("/graficos-avancados/{nome_equipe}")
async def get_graficos_avancados(nome_equipe: str, current_user: dict = Depends(get_current_user)):
    """
    Retorna dados para gráficos avançados do Dashboard do Dono
    Inclui: distribuição por gênero, faixa etária, distâncias, ranking histórico, etc.
    """
    import urllib.parse
    from datetime import datetime, timedelta
    
    nome_decoded = urllib.parse.unquote(nome_equipe)
    
    # Verificar permissão
    if current_user.get("role") not in ["admin", "super_admin", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if current_user.get("role") == "dono_assessoria" and current_user.get("equipe") != nome_decoded:
        raise HTTPException(status_code=403, detail="Você só pode ver dados da sua assessoria")
    
    # Buscar atletas da equipe
    atletas = await db.usuarios.find(
        {"equipe": nome_decoded, "role": "atleta"},
        {"_id": 0, "id": 1, "nome": 1, "genero": 1, "categoria": 1, "faixa_etaria": 1, 
         "cidade": 1, "estado": 1, "pontos_total": 1, "total_corridas": 1, "created_at": 1}
    ).to_list(None)
    
    if not atletas:
        raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    atletas_ids = [a["id"] for a in atletas]
    
    # 1. Distribuição por Gênero
    genero_count = {"Masculino": 0, "Feminino": 0}
    for a in atletas:
        g = a.get("genero", "M")
        if g == "M":
            genero_count["Masculino"] += 1
        else:
            genero_count["Feminino"] += 1
    
    grafico_genero = [
        {"name": k, "value": v, "fill": "#3B82F6" if k == "Masculino" else "#EC4899"}
        for k, v in genero_count.items() if v > 0
    ]
    
    # 2. Distribuição por Faixa Etária
    faixa_count = {}
    for a in atletas:
        faixa = a.get("faixa_etaria", "N/A") or "N/A"
        faixa_count[faixa] = faixa_count.get(faixa, 0) + 1
    
    grafico_faixa_etaria = [
        {"faixa": k, "atletas": v}
        for k, v in sorted(faixa_count.items())
    ]
    
    # 3. Distribuição por Categoria
    categoria_count = {}
    for a in atletas:
        cat = a.get("categoria", "normal") or "normal"
        categoria_count[cat] = categoria_count.get(cat, 0) + 1
    
    cores_categoria = {
        "normal": "#10B981",
        "pcd": "#F59E0B", 
        "cadeirante": "#8B5CF6",
        "povao": "#EF4444"
    }
    
    grafico_categoria = [
        {"name": k.upper(), "value": v, "fill": cores_categoria.get(k, "#6B7280")}
        for k, v in categoria_count.items() if v > 0
    ]
    
    # 4. Resultados por Mês (últimos 6 meses)
    agora = datetime.now()
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    resultados_por_mes = []
    
    for i in range(5, -1, -1):
        mes_data = agora - timedelta(days=30 * i)
        mes_num = mes_data.month
        ano_num = mes_data.year
        
        inicio = f"{ano_num}-{mes_num:02d}-01"
        if mes_num == 12:
            fim = f"{ano_num + 1}-01-01"
        else:
            fim = f"{ano_num}-{mes_num + 1:02d}-01"
        
        count = await db.corridas.count_documents({
            "usuario_id": {"$in": atletas_ids},
            "data": {"$gte": inicio, "$lt": fim}
        })
        
        resultados_por_mes.append({
            "mes": meses_nomes[mes_num - 1],
            "resultados": count
        })
    
    # 5. Distâncias mais corridas
    distancias = await db.corridas.find(
        {"usuario_id": {"$in": atletas_ids}},
        {"_id": 0, "distancia": 1}
    ).to_list(None)
    
    distancia_count = {}
    for d in distancias:
        dist = d.get("distancia", "N/A") or "N/A"
        distancia_count[dist] = distancia_count.get(dist, 0) + 1
    
    grafico_distancias = sorted(
        [{"distancia": k, "corridas": v} for k, v in distancia_count.items()],
        key=lambda x: x["corridas"],
        reverse=True
    )[:10]
    
    # 6. Evolução de Atletas (novos cadastros por mês)
    evolucao_atletas = []
    for i in range(5, -1, -1):
        mes_data = agora - timedelta(days=30 * i)
        mes_num = mes_data.month
        ano_num = mes_data.year
        prefixo = f"{ano_num}-{mes_num:02d}"
        
        novos = sum(1 for a in atletas if a.get("created_at", "").startswith(prefixo))
        evolucao_atletas.append({
            "mes": meses_nomes[mes_num - 1],
            "novos_atletas": novos
        })
    
    # 7. Top 10 Atletas por Pontos
    top_atletas = sorted(atletas, key=lambda x: x.get("pontos_total", 0), reverse=True)[:10]
    ranking_interno = [
        {
            "posicao": i + 1,
            "nome": a["nome"],
            "pontos": a.get("pontos_total", 0),
            "corridas": a.get("total_corridas", 0)
        }
        for i, a in enumerate(top_atletas)
    ]
    
    # 8. Distribuição por Estado (se tiver atletas de vários estados)
    estado_count = {}
    for a in atletas:
        est = a.get("estado", "N/A") or "N/A"
        estado_count[est] = estado_count.get(est, 0) + 1
    
    grafico_estados = [
        {"estado": k, "atletas": v}
        for k, v in sorted(estado_count.items(), key=lambda x: x[1], reverse=True)
    ][:10]
    
    # 9. Estatísticas de Performance
    total_atletas = len(atletas)
    total_pontos = sum(a.get("pontos_total", 0) for a in atletas)
    total_corridas = sum(a.get("total_corridas", 0) for a in atletas)
    
    # Buscar podiums
    podiums = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "colocacao": {"$lte": 3, "$gte": 1}
    })
    
    vitorias = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "colocacao": 1
    })
    
    estatisticas = {
        "total_atletas": total_atletas,
        "total_pontos": total_pontos,
        "total_corridas": total_corridas,
        "total_podiums": podiums,
        "total_vitorias": vitorias,
        "media_pontos_atleta": round(total_pontos / max(1, total_atletas), 1),
        "media_corridas_atleta": round(total_corridas / max(1, total_atletas), 1),
        "taxa_podio": round((podiums / max(1, total_corridas)) * 100, 1) if total_corridas > 0 else 0
    }
    
    return {
        "equipe": nome_decoded,
        "grafico_genero": grafico_genero,
        "grafico_faixa_etaria": grafico_faixa_etaria,
        "grafico_categoria": grafico_categoria,
        "resultados_por_mes": resultados_por_mes,
        "grafico_distancias": grafico_distancias,
        "evolucao_atletas": evolucao_atletas,
        "ranking_interno": ranking_interno,
        "grafico_estados": grafico_estados,
        "estatisticas": estatisticas
    }
