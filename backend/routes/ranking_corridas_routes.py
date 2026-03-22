# /app/backend/routes/ranking_corridas_routes.py
# Ranking de Corridas e Avaliações - Sistema IQC

from fastapi import APIRouter, HTTPException, Depends, Query, Form, Request
from typing import Optional
from datetime import datetime
import uuid

from config import db
from routes.auth_routes import get_current_user, get_admin_user

router = APIRouter(tags=["Ranking Corridas"])


# ============================================================
# NÍVEIS DE REPUTAÇÃO
# ============================================================

NIVEIS_REPUTACAO = {
    "iniciante": {
        "nome": "Iniciante",
        "descricao": "Começando a avaliar corridas",
        "min_avaliacoes": 0,
        "icone": "⭐",
        "cor": "#6B7280",
        "nivel": 0
    },
    "bronze": {
        "nome": "Avaliador Bronze",
        "descricao": "Avaliador experiente com 5+ avaliações",
        "min_avaliacoes": 5,
        "icone": "🥉",
        "cor": "#CD7F32",
        "nivel": 1
    },
    "prata": {
        "nome": "Avaliador Prata",
        "descricao": "Avaliador dedicado com 15+ avaliações",
        "min_avaliacoes": 15,
        "icone": "🥈",
        "cor": "#C0C0C0",
        "nivel": 2
    },
    "ouro": {
        "nome": "Avaliador Ouro",
        "descricao": "Avaliador exemplar com 30+ avaliações",
        "min_avaliacoes": 30,
        "icone": "🥇",
        "cor": "#FFD700",
        "nivel": 3
    }
}


def calcular_nivel_reputacao(total_avaliacoes: int) -> dict:
    """Calcula o nível de reputação baseado no número de avaliações"""
    nivel_atual = NIVEIS_REPUTACAO["iniciante"]
    
    for codigo, nivel in NIVEIS_REPUTACAO.items():
        if total_avaliacoes >= nivel["min_avaliacoes"]:
            nivel_atual = {**nivel, "codigo": codigo}
    
    return nivel_atual


async def atualizar_stats_corrida(corrida_id: str):
    """Atualiza as estatísticas de uma corrida após nova avaliação"""
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"corrida_id": corrida_id}, {"_id": 0}
    ).to_list(None)
    
    if not avaliacoes:
        return
    
    total = len(avaliacoes)
    media_geral = sum(a["nota_corrida"] for a in avaliacoes) / total
    media_org = sum(a["organizacao"] for a in avaliacoes) / total
    media_perc = sum(a["percurso"] for a in avaliacoes) / total
    media_kit = sum(a["kit_atleta"] for a in avaliacoes) / total
    media_hidr = sum(a["hidratacao"] for a in avaliacoes) / total
    media_pos = sum(a["pos_prova"] for a in avaliacoes) / total
    media_prem = sum(a.get("premiacao", 3) for a in avaliacoes) / total  # Default 3 para avaliações antigas
    
    await db.corridas_eventos.update_one(
        {"id": corrida_id},
        {"$set": {
            "total_avaliacoes": total,
            "media_geral": round(media_geral, 2),
            "media_organizacao": round(media_org, 2),
            "media_percurso": round(media_perc, 2),
            "media_kit": round(media_kit, 2),
            "media_hidratacao": round(media_hidr, 2),
            "media_pos_prova": round(media_pos, 2),
            "media_premiacao": round(media_prem, 2)
        }}
    )


# ============================================================
# RANKING DE CORRIDAS
# ============================================================

@router.get("/ranking-corridas")
async def get_ranking_corridas(
    tipo: str = "nacional",
    estado: str = None,
    cidade: str = None
):
    """
    Retorna ranking das corridas baseado em avaliações
    Usa Média Bayesiana para cálculo justo
    """
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    # Buscar todas as corridas
    filtro_corridas = {"status": {"$ne": "cancelada"}}
    
    if tipo == "estadual" and estado:
        filtro_corridas["estado"] = estado
    elif tipo == "cidade" and cidade:
        filtro_corridas["cidade"] = cidade
    
    corridas = await db.corridas_eventos.find(filtro_corridas, {"_id": 0}).to_list(None)
    
    if not corridas:
        return {"tipo": tipo, "total_corridas": 0, "ranking": []}
    
    # Filtro de período para avaliações
    filtro_avaliacoes = {}
    if tipo == "mensal":
        inicio_mes = f"{ano_atual}-{mes_atual:02d}-01"
        filtro_avaliacoes["data_avaliacao"] = {"$gte": inicio_mes}
    elif tipo == "anual":
        inicio_ano = f"{ano_atual}-01-01"
        filtro_avaliacoes["data_avaliacao"] = {"$gte": inicio_ano}
    
    # Calcular média geral da plataforma (C na fórmula Bayesiana)
    pipeline_media_geral = [
        {"$match": filtro_avaliacoes} if filtro_avaliacoes else {"$match": {}},
        {"$group": {"_id": None, "media": {"$avg": "$nota_corrida"}, "total": {"$sum": 1}}}
    ]
    result_media = await db.avaliacoes_corridas.aggregate(pipeline_media_geral).to_list(1)
    media_geral_plataforma = result_media[0]["media"] if result_media and result_media[0]["media"] else 3.5
    
    # Parâmetros
    m = 30  # mínimo de avaliações para peso completo
    min_avaliacoes_ranking = 10
    
    ranking = []
    
    for corrida in corridas:
        corrida_id = corrida["id"]
        
        # Buscar avaliações desta corrida
        filtro_aval = {"corrida_id": corrida_id, **filtro_avaliacoes}
        avaliacoes = await db.avaliacoes_corridas.find(filtro_aval, {"_id": 0}).to_list(None)
        
        v = len(avaliacoes)
        
        if v == 0:
            media_corrida = 0
            pontuacao_bayesiana = 0
        else:
            soma_notas = sum(a.get("nota_corrida", 0) for a in avaliacoes)
            media_corrida = soma_notas / v
            pontuacao_bayesiana = (v / (v + m)) * media_corrida + (m / (v + m)) * media_geral_plataforma
        
        # Calcular médias por critério
        if v > 0:
            media_org = sum(a.get("organizacao", 0) for a in avaliacoes) / v
            media_perc = sum(a.get("percurso", 0) for a in avaliacoes) / v
            media_kit = sum(a.get("kit_atleta", 0) for a in avaliacoes) / v
            media_hidr = sum(a.get("hidratacao", 0) for a in avaliacoes) / v
            media_pos = sum(a.get("pos_prova", 0) for a in avaliacoes) / v
        else:
            media_org = media_perc = media_kit = media_hidr = media_pos = 0
        
        # Determinar selo
        selo = None
        if v >= 50 and media_corrida >= 4.5:
            selo = "5_estrelas"
        
        ranking.append({
            "id": corrida_id,
            "nome_corrida": corrida.get("nome_corrida"),
            "organizador": corrida.get("organizador"),
            "cidade": corrida.get("cidade"),
            "estado": corrida.get("estado"),
            "data_corrida": corrida.get("data_corrida"),
            "pagina_link": corrida.get("pagina_link"),
            "status": corrida.get("status"),
            "total_avaliacoes": v,
            "media_geral": round(media_corrida, 2),
            "pontuacao_ranking": round(pontuacao_bayesiana, 2),
            "media_organizacao": round(media_org, 2),
            "media_percurso": round(media_perc, 2),
            "media_kit": round(media_kit, 2),
            "media_hidratacao": round(media_hidr, 2),
            "media_pos_prova": round(media_pos, 2),
            "selo": selo,
            "no_ranking": v >= min_avaliacoes_ranking
        })
    
    # Ordenar por pontuação bayesiana
    ranking.sort(key=lambda x: (-x["pontuacao_ranking"], -x["total_avaliacoes"]))
    
    # Adicionar posição
    posicao = 1
    for item in ranking:
        if item["no_ranking"]:
            item["posicao"] = posicao
            posicao += 1
        else:
            item["posicao"] = None
    
    # Top 10 e selos
    corridas_no_ranking = [c for c in ranking if c["no_ranking"]]
    for i, c in enumerate(corridas_no_ranking[:10]):
        if tipo == "nacional":
            c["selo_top10"] = "top10_brasil"
        elif tipo == "estadual":
            c["selo_top10"] = "top10_estado"
    
    return {
        "tipo": tipo,
        "periodo": {
            "mensal": f"{agora.strftime('%B')} {ano_atual}",
            "anual": str(ano_atual),
            "historico": "Todo período",
            "nacional": "Todo período",
            "estadual": f"Estado: {estado}" if estado else "Todos",
            "cidade": f"Cidade: {cidade}" if cidade else "Todas"
        }.get(tipo, ""),
        "total_corridas": len(ranking),
        "corridas_no_ranking": len(corridas_no_ranking),
        "media_geral_plataforma": round(media_geral_plataforma, 2),
        "ranking": ranking
    }


@router.get("/ranking-corridas/stats")
async def get_stats_ranking_corridas():
    """Retorna estatísticas gerais do Ranking das Corridas"""
    
    total_corridas = await db.corridas_eventos.count_documents({"status": {"$ne": "cancelada"}})
    total_avaliacoes = await db.avaliacoes_corridas.count_documents({})
    
    # Média geral
    pipeline_media = [{"$group": {"_id": None, "media": {"$avg": "$nota_corrida"}}}]
    result = await db.avaliacoes_corridas.aggregate(pipeline_media).to_list(1)
    media_geral = result[0]["media"] if result and result[0]["media"] else 0
    
    # Corrida mais bem avaliada (mínimo 10 avaliações)
    pipeline_melhor = [
        {"$group": {"_id": "$corrida_id", "media": {"$avg": "$nota_corrida"}, "total": {"$sum": 1}}},
        {"$match": {"total": {"$gte": 10}}},
        {"$sort": {"media": -1}},
        {"$limit": 1}
    ]
    result_melhor = await db.avaliacoes_corridas.aggregate(pipeline_melhor).to_list(1)
    
    corrida_melhor_avaliada = None
    if result_melhor:
        corrida = await db.corridas_eventos.find_one(
            {"id": result_melhor[0]["_id"]},
            {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1}
        )
        if corrida:
            corrida_melhor_avaliada = {
                **corrida,
                "media": round(result_melhor[0]["media"], 2),
                "avaliacoes": result_melhor[0]["total"]
            }
    
    # Corrida com mais avaliações
    pipeline_mais_aval = [
        {"$group": {"_id": "$corrida_id", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
    result_mais = await db.avaliacoes_corridas.aggregate(pipeline_mais_aval).to_list(1)
    
    corrida_mais_avaliada = None
    if result_mais:
        corrida = await db.corridas_eventos.find_one(
            {"id": result_mais[0]["_id"]},
            {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1}
        )
        if corrida:
            corrida_mais_avaliada = {**corrida, "avaliacoes": result_mais[0]["total"]}
    
    # Distribuição por estado
    pipeline_estados = [
        {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]
    dist_estados = await db.corridas_eventos.aggregate(pipeline_estados).to_list(None)
    
    return {
        "total_corridas": total_corridas,
        "total_avaliacoes": total_avaliacoes,
        "media_geral": round(media_geral, 2) if media_geral else 0,
        "corrida_melhor_avaliada": corrida_melhor_avaliada,
        "corrida_mais_avaliada": corrida_mais_avaliada,
        "distribuicao_estados": [{"estado": e["_id"], "corridas": e["total"]} for e in dist_estados if e["_id"]]
    }


@router.get("/ranking-corridas/estados")
async def get_estados_com_corridas():
    """Lista estados que têm corridas cadastradas"""
    pipeline = [
        {"$match": {"status": {"$ne": "cancelada"}}},
        {"$group": {"_id": "$estado"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.corridas_eventos.aggregate(pipeline).to_list(None)
    return {"estados": [e["_id"] for e in result]}


@router.get("/ranking-corridas/cidades")
async def get_cidades_com_corridas(estado: str = None):
    """Lista cidades que têm corridas cadastradas"""
    match_filter = {"status": {"$ne": "cancelada"}}
    if estado:
        match_filter["estado"] = estado
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {"_id": "$cidade"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.corridas_eventos.aggregate(pipeline).to_list(None)
    return {"cidades": [c["_id"] for c in result]}


# ============================================================
# AVALIAÇÃO DE CORRIDAS
# ============================================================

@router.post("/avaliar-corrida")
async def avaliar_corrida(
    request: Request,
    corrida_id: str = Form(...),
    organizacao: int = Form(...),
    percurso: int = Form(...),
    kit_atleta: int = Form(...),
    hidratacao: int = Form(...),
    pos_prova: int = Form(...),
    premiacao: int = Form(...),
    participei: bool = Form(...),
    aceito_termo: bool = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Registra avaliação de uma corrida por um atleta"""
    
    if current_user.get("role") not in ["atleta", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Apenas atletas podem avaliar corridas")
    
    if not participei:
        raise HTTPException(status_code=400, detail="Você precisa confirmar que participou desta corrida")
    
    if not aceito_termo:
        raise HTTPException(status_code=400, detail="Você precisa aceitar o termo de responsabilidade")
    
    # Capturar IP
    ip_avaliador = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip_avaliador = forwarded_for.split(",")[0].strip()
    
    # Validar notas
    for nota, nome in [(organizacao, "Organização"), (percurso, "Percurso"), 
                       (kit_atleta, "Kit Atleta"), (hidratacao, "Hidratação"), 
                       (pos_prova, "Pós Prova"), (premiacao, "Premiação")]:
        if not 1 <= nota <= 5:
            raise HTTPException(status_code=400, detail=f"{nome} deve ser entre 1 e 5")
    
    # Verificar corrida
    corrida = await db.corridas_eventos.find_one({"id": corrida_id}, {"_id": 0})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    # Verificar se corrida já ocorreu
    data_corrida = corrida.get("data_corrida", "")
    if data_corrida:
        try:
            data_evento = datetime.strptime(data_corrida, "%Y-%m-%d")
            if data_evento > datetime.now():
                raise HTTPException(status_code=400, detail="Avaliações disponíveis apenas após a realização da corrida")
        except ValueError:
            pass
    
    # Verificar se já avaliou
    avaliacao_existente = await db.avaliacoes_corridas.find_one({
        "corrida_id": corrida_id,
        "atleta_id": current_user.get("id")
    })
    
    if avaliacao_existente:
        raise HTTPException(status_code=400, detail="Você já avaliou esta corrida")
    
    nota_corrida = (organizacao + percurso + kit_atleta + hidratacao + pos_prova + premiacao) / 6
    
    avaliacao = {
        "id": str(uuid.uuid4()),
        "corrida_id": corrida_id,
        "atleta_id": current_user.get("id"),
        "atleta_nome": current_user.get("nome"),
        "atleta_email": current_user.get("email"),
        "organizacao": organizacao,
        "percurso": percurso,
        "kit_atleta": kit_atleta,
        "hidratacao": hidratacao,
        "pos_prova": pos_prova,
        "premiacao": premiacao,
        "nota_corrida": round(nota_corrida, 2),
        "participei": participei,
        "aceito_termo": aceito_termo,
        "termo_aceito_em": datetime.now().isoformat(),
        "ip_avaliador": ip_avaliador,
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "data_avaliacao": datetime.now().isoformat()
    }
    
    await db.avaliacoes_corridas.insert_one(avaliacao)
    await atualizar_stats_corrida(corrida_id)
    
    return {"message": "Avaliação registrada com sucesso!", "nota_corrida": round(nota_corrida, 2), "ip_registrado": True}


@router.get("/minhas-avaliacoes-corridas")
async def get_minhas_avaliacoes_corridas(current_user: dict = Depends(get_current_user)):
    """Retorna avaliações feitas pelo atleta logado"""
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"atleta_id": current_user.get("id")},
        {"_id": 0}
    ).to_list(None)
    
    for aval in avaliacoes:
        corrida = await db.corridas_eventos.find_one(
            {"id": aval["corrida_id"]},
            {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1}
        )
        if corrida:
            aval["corrida"] = corrida
    
    return avaliacoes


@router.get("/corrida-avaliacoes/{corrida_id}")
async def get_avaliacoes_corrida(corrida_id: str):
    """Retorna todas as avaliações de uma corrida específica"""
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"corrida_id": corrida_id},
        {"_id": 0}
    ).sort("data_avaliacao", -1).to_list(None)
    
    return avaliacoes


@router.get("/verificar-avaliacao/{corrida_id}")
async def verificar_avaliacao(corrida_id: str, current_user: dict = Depends(get_current_user)):
    """Verifica se o atleta já avaliou uma corrida"""
    
    avaliacao = await db.avaliacoes_corridas.find_one({
        "corrida_id": corrida_id,
        "atleta_id": current_user.get("id")
    })
    
    return {"ja_avaliou": avaliacao is not None}


# ============================================================
# REPUTAÇÃO DE AVALIADORES
# ============================================================

@router.get("/reputacao-avaliador/{atleta_id}")
async def get_reputacao_avaliador(atleta_id: str):
    """Retorna a reputação de um avaliador (público)"""
    
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0, "id": 1, "nome": 1})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    total_avaliacoes = await db.avaliacoes_corridas.count_documents({"atleta_id": atleta_id})
    nivel_atual = calcular_nivel_reputacao(total_avaliacoes)
    
    # Calcular progresso
    proximo_nivel = None
    progresso = 100
    faltam = 0
    
    niveis_ordenados = sorted(NIVEIS_REPUTACAO.items(), key=lambda x: x[1]["min_avaliacoes"])
    for i, (codigo, nivel) in enumerate(niveis_ordenados):
        if nivel["min_avaliacoes"] > total_avaliacoes:
            proximo_nivel = {**nivel, "codigo": codigo}
            faltam = nivel["min_avaliacoes"] - total_avaliacoes
            nivel_anterior = niveis_ordenados[i-1][1]["min_avaliacoes"] if i > 0 else 0
            range_nivel = nivel["min_avaliacoes"] - nivel_anterior
            progresso_atual = total_avaliacoes - nivel_anterior
            progresso = (progresso_atual / range_nivel) * 100 if range_nivel > 0 else 100
            break
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"atleta_id": atleta_id},
        {"_id": 0, "nota_corrida": 1, "data_avaliacao": 1}
    ).to_list(None)
    
    media_notas = sum(a.get("nota_corrida", 0) for a in avaliacoes) / max(1, len(avaliacoes))
    meses_ativos = len(set(a.get("data_avaliacao", "")[:7] for a in avaliacoes if a.get("data_avaliacao")))
    
    return {
        "atleta": {"id": atleta["id"], "nome": atleta.get("nome", "")},
        "total_avaliacoes": total_avaliacoes,
        "nivel_atual": nivel_atual,
        "proximo_nivel": proximo_nivel,
        "progresso": round(progresso, 1),
        "faltam_para_proximo": faltam,
        "estatisticas": {"media_notas_dadas": round(media_notas, 2), "meses_ativos": meses_ativos},
        "todos_niveis": [
            {
                **nivel, "codigo": codigo,
                "conquistado": total_avaliacoes >= nivel["min_avaliacoes"],
                "atual": total_avaliacoes,
                "progresso": min(100, (total_avaliacoes / nivel["min_avaliacoes"]) * 100) if nivel["min_avaliacoes"] > 0 else 100
            }
            for codigo, nivel in sorted(NIVEIS_REPUTACAO.items(), key=lambda x: x[1]["min_avaliacoes"])
            if nivel["min_avaliacoes"] > 0
        ]
    }


@router.get("/ranking-avaliadores")
async def get_ranking_avaliadores(limite: int = 20):
    """Retorna o ranking dos melhores avaliadores"""
    
    pipeline = [
        {
            "$group": {
                "_id": "$atleta_id",
                "total_avaliacoes": {"$sum": 1},
                "nome": {"$first": "$atleta_nome"},
                "media_notas": {"$avg": "$nota_corrida"},
                "primeira_avaliacao": {"$min": "$data_avaliacao"},
                "ultima_avaliacao": {"$max": "$data_avaliacao"}
            }
        },
        {"$sort": {"total_avaliacoes": -1}},
        {"$limit": limite}
    ]
    
    resultado = await db.avaliacoes_corridas.aggregate(pipeline).to_list(None)
    
    ranking = []
    for i, r in enumerate(resultado, 1):
        nivel = calcular_nivel_reputacao(r["total_avaliacoes"])
        ranking.append({
            "posicao": i,
            "atleta_id": r["_id"],
            "nome": r.get("nome", "N/A"),
            "total_avaliacoes": r["total_avaliacoes"],
            "media_notas": round(r.get("media_notas", 0), 2),
            "nivel": nivel,
            "primeira_avaliacao": r.get("primeira_avaliacao"),
            "ultima_avaliacao": r.get("ultima_avaliacao")
        })
    
    return {
        "ranking": ranking,
        "total_avaliadores": len(resultado),
        "niveis_disponiveis": [
            {**v, "codigo": k}
            for k, v in sorted(NIVEIS_REPUTACAO.items(), key=lambda x: x[1]["min_avaliacoes"])
            if v["min_avaliacoes"] > 0
        ]
    }


@router.get("/minha-reputacao")
async def get_minha_reputacao(current_user: dict = Depends(get_current_user)):
    """Retorna a reputação do atleta logado"""
    return await get_reputacao_avaliador(current_user["id"])


# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@router.get("/admin/avaliacoes")
async def listar_avaliacoes_admin(
    corrida_id: str = None,
    limite: int = 50,
    admin: dict = Depends(get_admin_user)
):
    """Lista avaliações com informações de IP e termo (admin)"""
    filtro = {}
    if corrida_id:
        filtro["corrida_id"] = corrida_id
    
    avaliacoes = await db.avaliacoes_corridas.find(
        filtro,
        {"_id": 0}
    ).sort("data_avaliacao", -1).limit(limite).to_list(None)
    
    for av in avaliacoes:
        corrida = await db.corridas_eventos.find_one({"id": av["corrida_id"]}, {"_id": 0, "nome": 1})
        av["corrida_nome"] = corrida.get("nome", "N/A") if corrida else "N/A"
    
    return avaliacoes


@router.get("/admin/avaliacoes/termo")
async def get_texto_termo():
    """Retorna o texto do termo de responsabilidade"""
    termo = await db.configuracoes.find_one({"tipo": "termo_avaliacao"}, {"_id": 0})
    
    if not termo:
        return {
            "titulo": "Termo de Responsabilidade para Avaliação de Corridas",
            "texto": """Ao submeter esta avaliação, declaro que:

1. **Participei efetivamente** desta corrida como atleta inscrito;

2. **As informações prestadas são verdadeiras** e baseadas na minha experiência pessoal durante o evento;

3. **Tenho ciência** de que avaliações falsas ou fraudulentas podem resultar em suspensão da minha conta;

4. **Autorizo** o Ranking Run Pró a registrar meu IP e dados de acesso para fins de auditoria e prevenção de fraudes;

5. **Comprometo-me** a avaliar de forma justa e imparcial, considerando apenas os critérios de qualidade do evento;

6. **Estou ciente** de que esta avaliação será pública e poderá influenciar a reputação do evento avaliado.

Este termo tem validade legal conforme a Lei Geral de Proteção de Dados (LGPD) e demais legislações aplicáveis."""
        }
    
    return termo


@router.put("/admin/avaliacoes/termo")
async def atualizar_termo_avaliacao(
    titulo: str = Form(...),
    texto: str = Form(...),
    admin: dict = Depends(get_admin_user)
):
    """Atualiza o texto do termo de responsabilidade"""
    termo = {
        "tipo": "termo_avaliacao",
        "titulo": titulo,
        "texto": texto,
        "atualizado_por": admin["nome"],
        "atualizado_em": datetime.now().isoformat()
    }
    
    await db.configuracoes.update_one(
        {"tipo": "termo_avaliacao"},
        {"$set": termo},
        upsert=True
    )
    
    return {"message": "Termo atualizado com sucesso"}


@router.get("/admin/ranking-corridas/dashboard")
async def get_dashboard_ranking_corridas(admin: dict = Depends(get_admin_user)):
    """Dashboard administrativo do Ranking das Corridas"""
    
    total_corridas = await db.corridas_eventos.count_documents({"status": {"$ne": "cancelada"}})
    total_avaliacoes = await db.avaliacoes_corridas.count_documents({})
    
    pipeline_media = [{"$group": {"_id": None, "media": {"$avg": "$nota_corrida"}}}]
    result = await db.avaliacoes_corridas.aggregate(pipeline_media).to_list(1)
    media_geral = result[0]["media"] if result and result[0]["media"] else 0
    
    # Corrida melhor avaliada
    pipeline_melhor = [
        {"$group": {"_id": "$corrida_id", "media": {"$avg": "$nota_corrida"}, "total": {"$sum": 1}}},
        {"$match": {"total": {"$gte": 10}}},
        {"$sort": {"media": -1}},
        {"$limit": 1}
    ]
    result_melhor = await db.avaliacoes_corridas.aggregate(pipeline_melhor).to_list(1)
    
    melhor_nacional = None
    if result_melhor:
        corrida = await db.corridas_eventos.find_one(
            {"id": result_melhor[0]["_id"]}, 
            {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1}
        )
        if corrida:
            melhor_nacional = {
                **corrida,
                "media": round(result_melhor[0]["media"], 2),
                "avaliacoes": result_melhor[0]["total"]
            }
    
    # Corrida com mais avaliações
    pipeline_mais = [
        {"$group": {"_id": "$corrida_id", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
    result_mais = await db.avaliacoes_corridas.aggregate(pipeline_mais).to_list(1)
    
    mais_avaliada_nacional = None
    if result_mais:
        corrida = await db.corridas_eventos.find_one(
            {"id": result_mais[0]["_id"]},
            {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1}
        )
        if corrida:
            mais_avaliada_nacional = {**corrida, "avaliacoes": result_mais[0]["total"]}
    
    return {
        "total_corridas": total_corridas,
        "total_avaliacoes": total_avaliacoes,
        "media_geral": round(media_geral, 2) if media_geral else 0,
        "melhor_avaliada_nacional": melhor_nacional,
        "mais_avaliada_nacional": mais_avaliada_nacional
    }
