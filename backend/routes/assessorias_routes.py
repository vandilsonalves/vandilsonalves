# /app/backend/routes/assessorias_routes.py
# Módulo de Liga de Assessorias - Ranking ROE-RR

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from config import db
from routes.auth_routes import get_current_user, get_admin_user
from services.cache_service import cached, invalidate_on_liga_change

router = APIRouter(tags=["Liga de Assessorias"])


# ==================== LISTA DE ASSESSORIAS ====================

@router.get("/assessorias/lista")
@cached(prefix='liga', ttl_key='liga_assessorias')
async def get_assessorias_lista():
    """Lista assessorias cadastradas para dropdown do cadastro"""
    assessorias = await db.assessorias.find(
        {},
        {"_id": 0, "nome": 1, "cidade": 1, "estado": 1}
    ).to_list(None)
    
    if len(assessorias) == 0:
        pipeline = [
            {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
            {"$group": {
                "_id": "$equipe",
                "cidade": {"$first": "$cidade"},
                "estado": {"$first": "$estado"}
            }}
        ]
        equipes_raw = await db.usuarios.aggregate(pipeline).to_list(None)
        assessorias = [
            {"nome": e["_id"], "cidade": e.get("cidade", ""), "estado": e.get("estado", "")}
            for e in equipes_raw if e["_id"]
        ]
    
    return assessorias


# ==================== RANKING LIGA ASSESSORIAS ====================

@router.get("/liga-assessorias/ranking")
@cached(prefix='liga', ttl_key='liga_assessorias')
async def get_ranking_assessorias(
    tipo: str = "nacional",
    estado: str = None,
    cidade: str = None,
    mes: int = None
):
    """
    Retorna ranking das assessorias baseado no sistema ROE-RR
    
    Sistema de Pontuação:
    - +0,5 por atleta cadastrado e vinculado
    - +1,0 por resultado aprovado
    - +0,5 adicional para 2º-5º lugar
    - +1,0 adicional para 1º lugar
    """
    agora = datetime.now()
    ano_atual = agora.year
    
    filtro_corridas = {}
    
    if tipo != "historico":
        if mes and 1 <= mes <= 12:
            inicio_mes = f"{ano_atual}-{mes:02d}-01"
            if mes == 12:
                fim_mes = f"{ano_atual + 1}-01-01"
            else:
                fim_mes = f"{ano_atual}-{mes + 1:02d}-01"
            filtro_corridas["data"] = {"$gte": inicio_mes, "$lt": fim_mes}
        else:
            inicio_ano = f"{ano_atual}-01-01"
            filtro_corridas["data"] = {"$gte": inicio_ano}
    
    pipeline_equipes = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe", "sem equipe"], "$exists": True}}},
        {"$group": {
            "_id": "$equipe",
            "estado": {"$first": "$estado"},
            "cidade": {"$first": "$cidade"},
            "atletas": {"$push": {
                "id": "$id",
                "nome": "$nome",
                "foto_url": "$foto_url",
                "estado": "$estado",
                "cidade": "$cidade"
            }},
            "total_atletas": {"$sum": 1},
            "data_mais_antiga": {"$min": "$id"}
        }},
        {"$match": {"_id": {"$nin": ["Sem equipe", "sem equipe", "", None]}}}
    ]
    
    # Filtrar por estado/cidade APÓS o agrupamento para pegar assessorias desse local
    if tipo == "estadual" and estado:
        pipeline_equipes.append({"$match": {"estado": estado}})
    elif tipo == "cidade" and cidade:
        pipeline_equipes.append({"$match": {"cidade": cidade}})
    
    equipes_raw = await db.usuarios.aggregate(pipeline_equipes).to_list(None)
    
    ranking_assessorias = []
    
    for equipe in equipes_raw:
        nome_equipe = equipe["_id"]
        atletas_ids = [a["id"] for a in equipe["atletas"]]
        
        pontos_cadastro = len(atletas_ids) * 0.5
        
        # Buscar dados da assessoria cadastrada (se existir)
        assessoria_db = await db.assessorias.find_one(
            {"nome": nome_equipe},
            {"_id": 0, "dono_id": 1, "dono_nome": 1}
        )
        
        dono_nome = None
        dono_id = None
        
        if assessoria_db:
            dono_nome = assessoria_db.get("dono_nome")
            dono_id = assessoria_db.get("dono_id")
        
        # Se não tem dono_nome na assessoria, buscar no usuário
        if not dono_nome and dono_id:
            dono_user = await db.usuarios.find_one(
                {"id": dono_id},
                {"_id": 0, "nome": 1}
            )
            if dono_user:
                dono_nome = dono_user.get("nome")
        
        filtro_corridas_equipe = {
            "usuario_id": {"$in": atletas_ids},
            **filtro_corridas
        }
        
        corridas = await db.corridas.find(filtro_corridas_equipe, {"_id": 0}).to_list(None)
        
        pontos_resultados = 0
        total_primeiros = 0
        total_podios = 0
        total_resultados = len(corridas)
        
        for corrida in corridas:
            pontos_resultados += 1.0
            
            colocacao = corrida.get("colocacao", 0)
            modalidade = corrida.get("modalidade", "profissional_amador")
            
            if modalidade == "profissional_amador" and colocacao > 0:
                if colocacao == 1:
                    pontos_resultados += 1.0
                    total_primeiros += 1
                elif 2 <= colocacao <= 5:
                    pontos_resultados += 0.5
                    total_podios += 1
        
        pontos_total = pontos_cadastro + pontos_resultados
        
        ranking_assessorias.append({
            "nome": nome_equipe,
            "estado": equipe.get("estado", ""),
            "cidade": equipe.get("cidade", ""),
            "total_atletas": equipe["total_atletas"],
            "pontos_cadastro": pontos_cadastro,
            "pontos_resultados": pontos_resultados,
            "pontos_total": round(pontos_total, 1),
            "total_resultados": total_resultados,
            "total_primeiros": total_primeiros,
            "total_podios": total_podios,
            "dono_nome": dono_nome,
            "dono_id": dono_id,
            "verificada": bool(dono_nome and equipe["total_atletas"] >= 10 and total_resultados >= 5),
            "atletas": equipe["atletas"][:10],
            "data_mais_antiga": equipe.get("data_mais_antiga", "")
        })
    
    ranking_assessorias.sort(key=lambda x: (
        -x["pontos_total"],
        -x["total_primeiros"],
        -x["total_atletas"],
        -x["total_resultados"],
        x["data_mais_antiga"]
    ))
    
    for idx, equipe in enumerate(ranking_assessorias):
        equipe["posicao"] = idx + 1
        
        if tipo in ["nacional", "historico", "anual"]:
            if idx < 20:
                equipe["selo"] = "ouro"
            elif idx < 50:
                equipe["selo"] = "prata"
            else:
                equipe["selo"] = "bronze"
        elif tipo == "estadual":
            if idx < 10:
                equipe["selo"] = "prata"
            else:
                equipe["selo"] = "bronze"
        else:
            equipe["selo"] = "bronze"
    
    return {
        "tipo": tipo,
        "periodo": {
            "mensal": f"{agora.strftime('%B %Y')}",
            "anual": str(ano_atual),
            "historico": "Todo período",
            "nacional": "Todo período",
            "estadual": f"Estado: {estado}" if estado else "Todos",
            "cidade": f"Cidade: {cidade}" if cidade else "Todas"
        }.get(tipo, ""),
        "total_assessorias": len(ranking_assessorias),
        "ranking": ranking_assessorias
    }


# ==================== ESTATÍSTICAS DA LIGA ====================

@router.get("/liga-assessorias/stats")
@cached(prefix='liga', ttl_key='stats')
async def get_stats_liga_assessorias():
    """Estatísticas gerais da liga de assessorias"""
    
    pipeline_total = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe", "sem equipe"]}}},
        {"$group": {"_id": "$equipe"}},
        {"$count": "total"}
    ]
    
    result = await db.usuarios.aggregate(pipeline_total).to_list(1)
    total_assessorias = result[0]["total"] if result else 0
    
    total_atletas_vinculados = await db.usuarios.count_documents({
        "role": "atleta",
        "equipe": {"$nin": ["", None, "Sem equipe", "sem equipe"]}
    })
    
    total_resultados_aprovados = await db.corridas.count_documents({})
    
    pipeline_top = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
        {"$group": {"_id": "$equipe", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    top_result = await db.usuarios.aggregate(pipeline_top).to_list(1)
    maior_assessoria = top_result[0]["_id"] if top_result else "N/A"
    
    return {
        "total_assessorias": total_assessorias,
        "total_atletas_vinculados": total_atletas_vinculados,
        "total_resultados_aprovados": total_resultados_aprovados,
        "maior_assessoria": maior_assessoria
    }


# ==================== EVOLUÇÃO MENSAL ====================

@router.get("/liga-assessorias/evolucao-mensal")
@cached(prefix='liga', ttl=600)
async def get_evolucao_mensal_equipes(top: int = 5):
    """Retorna a evolução mensal de pontos das top equipes"""
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    
    pipeline_top_equipes = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
        {"$group": {"_id": "$equipe", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": top}
    ]
    
    top_equipes = await db.usuarios.aggregate(pipeline_top_equipes).to_list(None)
    equipes_nomes = [e["_id"] for e in top_equipes]
    
    meses = []
    for i in range(6):
        mes = mes_atual - i
        ano = ano_atual
        if mes < 1:
            mes += 12
            ano -= 1
        meses.append((ano, mes))
    
    meses.reverse()
    
    evolucao = {nome: [] for nome in equipes_nomes}
    
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    labels = []
    
    for ano, mes in meses:
        labels.append(f"{meses_nomes[mes-1]}/{str(ano)[-2:]}")
        
        inicio_mes = f"{ano}-{mes:02d}-01"
        if mes == 12:
            fim_mes = f"{ano + 1}-01-01"
        else:
            fim_mes = f"{ano}-{mes + 1:02d}-01"
        
        for nome_equipe in equipes_nomes:
            atletas_equipe = await db.usuarios.find(
                {"role": "atleta", "equipe": nome_equipe},
                {"id": 1}
            ).to_list(None)
            atletas_ids = [a["id"] for a in atletas_equipe]
            
            corridas_mes = await db.corridas.find({
                "usuario_id": {"$in": atletas_ids},
                "data": {"$gte": inicio_mes, "$lt": fim_mes}
            }).to_list(None)
            
            pontos_mes = len(corridas_mes)
            for c in corridas_mes:
                col = c.get("colocacao", 0)
                if col == 1:
                    pontos_mes += 1
                elif 2 <= col <= 5:
                    pontos_mes += 0.5
            
            evolucao[nome_equipe].append(round(pontos_mes, 1))
    
    datasets = []
    cores = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6"]
    
    for idx, nome in enumerate(equipes_nomes):
        datasets.append({
            "label": nome,
            "data": evolucao[nome],
            "borderColor": cores[idx % len(cores)],
            "tension": 0.1
        })
    
    return {
        "labels": labels,
        "datasets": datasets
    }


# ==================== DETALHE DA ASSESSORIA ====================

@router.get("/liga-assessorias/assessoria/{nome_equipe}")
async def get_detalhes_assessoria(nome_equipe: str):
    """Retorna detalhes de uma assessoria específica"""
    import urllib.parse
    nome_equipe = urllib.parse.unquote(nome_equipe)
    
    atletas = await db.usuarios.find(
        {"role": "atleta", "equipe": nome_equipe},
        {"_id": 0, "password_hash": 0}
    ).to_list(None)
    
    if not atletas:
        raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    atletas_ids = [a["id"] for a in atletas]
    
    # Buscar dados da assessoria cadastrada
    assessoria_doc = await db.assessorias.find_one(
        {"nome": nome_equipe},
        {"_id": 0}
    )
    
    # Buscar dono da assessoria
    dono_info = None
    responsavel_nome = None
    responsavel_id = None
    dono_atleta = None
    
    if assessoria_doc and assessoria_doc.get("dono_id"):
        dono = await db.usuarios.find_one(
            {"id": assessoria_doc["dono_id"]},
            {"_id": 0, "password_hash": 0}
        )
        if dono:
            dono_info = dono
            responsavel_nome = dono.get("nome")
            responsavel_id = dono.get("id")
            
            # Se o dono não está na lista de atletas, incluí-lo
            if dono.get("id") not in atletas_ids:
                dono_atleta = dono
                atletas_ids.append(dono.get("id"))
    
    # Buscar pontos de cada atleta
    atletas_com_pontos = []
    
    # Processar atletas normais
    for atleta in atletas:
        ranking_atleta = await db.ranking_anual.find_one(
            {"usuario_id": atleta["id"], "ano": 2025},
            {"_id": 0, "pontos_total": 1, "total_corridas": 1}
        )
        ranking_povao = await db.ranking_povao.find_one(
            {"usuario_id": atleta["id"], "ano": 2025},
            {"_id": 0, "pontos_total": 1, "total_corridas": 1}
        )
        
        pontos_atleta = 0
        corridas_atleta = 0
        if ranking_atleta:
            pontos_atleta = ranking_atleta.get("pontos_total", 0)
            corridas_atleta = ranking_atleta.get("total_corridas", 0)
        if ranking_povao:
            pontos_atleta = max(pontos_atleta, ranking_povao.get("pontos_total", 0))
            corridas_atleta = max(corridas_atleta, ranking_povao.get("total_corridas", 0))
        
        atletas_com_pontos.append({
            **atleta,
            "pontos": pontos_atleta,
            "total_corridas": corridas_atleta,
            "is_dono": atleta.get("id") == responsavel_id
        })
    
    # Adicionar o dono se ele não estava na lista de atletas
    if dono_atleta:
        ranking_dono = await db.ranking_anual.find_one(
            {"usuario_id": dono_atleta["id"], "ano": 2025},
            {"_id": 0, "pontos_total": 1, "total_corridas": 1}
        )
        ranking_povao_dono = await db.ranking_povao.find_one(
            {"usuario_id": dono_atleta["id"], "ano": 2025},
            {"_id": 0, "pontos_total": 1, "total_corridas": 1}
        )
        
        pontos_dono = 0
        corridas_dono = 0
        if ranking_dono:
            pontos_dono = ranking_dono.get("pontos_total", 0)
            corridas_dono = ranking_dono.get("total_corridas", 0)
        if ranking_povao_dono:
            pontos_dono = max(pontos_dono, ranking_povao_dono.get("pontos_total", 0))
            corridas_dono = max(corridas_dono, ranking_povao_dono.get("total_corridas", 0))
        
        atletas_com_pontos.append({
            **dono_atleta,
            "pontos": pontos_dono,
            "total_corridas": corridas_dono,
            "is_dono": True
        })
    
    # Ordenar atletas por pontos (decrescente)
    atletas_com_pontos.sort(key=lambda x: x.get("pontos", 0), reverse=True)
    
    corridas = await db.corridas.find(
        {"usuario_id": {"$in": atletas_ids}},
        {"_id": 0}
    ).to_list(None)
    
    pontos_cadastro = len(atletas) * 0.5
    pontos_resultados = len(corridas)
    total_primeiros = sum(1 for c in corridas if c.get("colocacao") == 1)
    total_podios = sum(1 for c in corridas if 2 <= c.get("colocacao", 0) <= 5)
    
    for c in corridas:
        if c.get("colocacao") == 1:
            pontos_resultados += 1
        elif 2 <= c.get("colocacao", 0) <= 5:
            pontos_resultados += 0.5
    
    # Buscar posição no ranking NACIONAL
    ranking_nacional = await get_ranking_assessorias(tipo="nacional")
    posicao_nacional = next(
        (eq["posicao"] for eq in ranking_nacional.get("ranking", []) if eq["nome"] == nome_equipe),
        None
    )
    
    # Buscar posição no ranking ESTADUAL
    estado_equipe = atletas[0].get("estado", "") if atletas else ""
    posicao_estadual = None
    if estado_equipe:
        ranking_estadual = await get_ranking_assessorias(tipo="estadual", estado=estado_equipe)
        posicao_estadual = next(
            (eq["posicao"] for eq in ranking_estadual.get("ranking", []) if eq["nome"] == nome_equipe),
            None
        )
    
    # Determinar selo baseado na posição
    selo = "participante"
    if posicao_nacional:
        if posicao_nacional <= 20:
            selo = "ouro"
        elif posicao_nacional <= 50:
            selo = "prata"
        else:
            selo = "bronze"
    
    # Total de atletas inclui o dono se ele for contado
    total_atletas_count = len(atletas_com_pontos)
    
    return {
        "nome": nome_equipe,
        "estado": estado_equipe,
        "cidade": atletas[0].get("cidade", "") if atletas else "",
        "total_atletas": total_atletas_count,
        "pontos_cadastro": pontos_cadastro,
        "pontos_resultados": pontos_resultados,
        "pontos_total": round(pontos_cadastro + pontos_resultados, 1),
        "total_resultados": len(corridas),
        "total_primeiros": total_primeiros,
        "total_podios": total_podios,
        "posicao_ranking": posicao_nacional,
        "posicao_nacional": posicao_nacional,
        "posicao_estadual": posicao_estadual,
        "selo": selo,
        "atletas": atletas_com_pontos,
        "dono": dono_info,
        "responsavel_nome": responsavel_nome,
        "responsavel_id": responsavel_id,
        "mensagem_bio": assessoria_doc.get("mensagem_bio", "") if assessoria_doc else "",
        "foto_url": assessoria_doc.get("foto_url", "") if assessoria_doc else "",
        "whatsapp_link": assessoria_doc.get("whatsapp_link", "") if assessoria_doc else ""
    }
