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
# RANKING DE CORRIDAS (endpoints em corridas_eventos_routes.py)
# Os endpoints /ranking-corridas, /ranking-corridas/stats,
# /ranking-corridas/estados e /ranking-corridas/cidades
# já existem em corridas_eventos_routes.py com cache e paginação.
# ============================================================


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
