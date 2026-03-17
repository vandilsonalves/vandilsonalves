# /app/backend/routes/corridas_eventos_routes.py
# Módulo de Corridas e Eventos - Ranking de Corridas de Rua

from fastapi import APIRouter, HTTPException, Depends, Form, Query
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from config import db
from routes.auth_routes import get_current_user, get_admin_user
from services.cache_service import cached, invalidate_on_corrida_change

router = APIRouter(tags=["Corridas e Eventos"])


# ==================== CRUD CORRIDAS EVENTOS ====================

@router.post("/corridas-eventos")
async def criar_corrida_evento(
    nome_corrida: str = Form(...),
    organizador: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    data_corrida: str = Form(...),
    pagina_link: str = Form(None),
    status: str = Form("ativa"),
    current_user: dict = Depends(get_current_user)
):
    """Cadastra uma nova corrida de rua (Admin ou Dono de Assessoria)"""
    
    if current_user.get("role") not in ["admin", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Apenas Admin ou Dono de Assessoria podem cadastrar corridas")
    
    corrida = {
        "id": str(uuid.uuid4()),
        "nome_corrida": nome_corrida,
        "organizador": organizador,
        "cidade": cidade,
        "estado": estado,
        "data_corrida": data_corrida,
        "pagina_link": pagina_link or "",
        "status": status,
        "criado_por": current_user.get("id"),
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "total_avaliacoes": 0,
        "media_geral": 0,
        "media_organizacao": 0,
        "media_percurso": 0,
        "media_kit": 0,
        "media_hidratacao": 0,
        "media_pos_prova": 0,
        "pontuacao_ranking": 0
    }
    
    await db.corridas_eventos.insert_one(corrida)
    await invalidate_on_corrida_change()
    
    return {"message": "Corrida cadastrada com sucesso!", "id": corrida["id"]}


@router.get("/corridas-eventos")
@cached(prefix='corridas', ttl_key='corridas_eventos')
async def listar_corridas_eventos(
    estado: str = None,
    cidade: str = None,
    status: str = None
):
    """Lista corridas de rua com filtros opcionais"""
    
    filtro = {}
    if estado:
        filtro["estado"] = estado
    if cidade:
        filtro["cidade"] = cidade
    if status:
        filtro["status"] = status
    
    corridas = await db.corridas_eventos.find(filtro, {"_id": 0}).sort("data_corrida", -1).to_list(None)
    return corridas


@router.get("/corridas-eventos/{corrida_id}")
async def get_corrida_evento(corrida_id: str):
    """Retorna detalhes de uma corrida específica"""
    
    corrida = await db.corridas_eventos.find_one({"id": corrida_id}, {"_id": 0})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    return corrida


@router.put("/corridas-eventos/{corrida_id}")
async def atualizar_corrida_evento(
    corrida_id: str,
    nome_corrida: str = Form(None),
    organizador: str = Form(None),
    cidade: str = Form(None),
    estado: str = Form(None),
    data_corrida: str = Form(None),
    pagina_link: str = Form(None),
    status: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Atualiza uma corrida existente"""
    
    if current_user.get("role") not in ["admin", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    update_data = {}
    if nome_corrida:
        update_data["nome_corrida"] = nome_corrida
    if organizador:
        update_data["organizador"] = organizador
    if cidade:
        update_data["cidade"] = cidade
    if estado:
        update_data["estado"] = estado
    if data_corrida:
        update_data["data_corrida"] = data_corrida
    if pagina_link is not None:
        update_data["pagina_link"] = pagina_link
    if status:
        update_data["status"] = status
    
    if update_data:
        await db.corridas_eventos.update_one({"id": corrida_id}, {"$set": update_data})
        await invalidate_on_corrida_change()
    
    return {"message": "Corrida atualizada com sucesso!"}


@router.delete("/corridas-eventos/{corrida_id}")
async def deletar_corrida_evento(corrida_id: str, admin: dict = Depends(get_admin_user)):
    """Deleta uma corrida (apenas Admin)"""
    
    await db.corridas_eventos.delete_one({"id": corrida_id})
    await db.avaliacoes_corridas.delete_many({"corrida_id": corrida_id})
    await invalidate_on_corrida_change()
    
    return {"message": "Corrida excluída com sucesso!"}


# ==================== RANKING DE CORRIDAS ====================

@router.get("/ranking-corridas")
@cached(prefix='corridas', ttl_key='corridas_eventos')
async def get_ranking_corridas(
    tipo: str = "nacional",
    estado: str = None,
    cidade: str = None
):
    """
    Retorna ranking das corridas baseado em avaliações
    Usa Média Bayesiana para cálculo justo
    """
    
    filtro = {}
    if tipo == "estadual" and estado:
        filtro["estado"] = estado
    elif tipo == "cidade":
        # Sempre filtra pelo estado quando está na aba cidade
        if estado:
            filtro["estado"] = estado
        # E também pela cidade se especificada
        if cidade:
            filtro["cidade"] = cidade
    
    corridas = await db.corridas_eventos.find(filtro, {"_id": 0}).to_list(None)
    
    # Calcular média global e número mínimo de avaliações
    total_avaliacoes_global = sum(c.get("total_avaliacoes", 0) for c in corridas)
    num_corridas_avaliadas = sum(1 for c in corridas if c.get("total_avaliacoes", 0) > 0)
    
    if num_corridas_avaliadas > 0:
        media_global = sum(c.get("media_geral", 0) * c.get("total_avaliacoes", 0) for c in corridas) / max(total_avaliacoes_global, 1)
        m = max(3, total_avaliacoes_global // max(num_corridas_avaliadas, 1))
    else:
        media_global = 0
        m = 3
    
    # Calcular pontuação Bayesiana para cada corrida
    for corrida in corridas:
        v = corrida.get("total_avaliacoes", 0)
        R = corrida.get("media_geral", 0)
        
        if v > 0:
            WR = (v / (v + m)) * R + (m / (v + m)) * media_global
        else:
            WR = 0
        
        corrida["pontuacao_ranking"] = round(WR, 2)
    
    # Ordenar por pontuação
    corridas.sort(key=lambda x: (
        -x.get("pontuacao_ranking", 0),
        -x.get("total_avaliacoes", 0),
        -x.get("media_geral", 0)
    ))
    
    # Adicionar posições e selos
    for idx, corrida in enumerate(corridas):
        corrida["posicao"] = idx + 1
        
        if idx < 10:
            corrida["selo"] = "ouro"
        elif idx < 30:
            corrida["selo"] = "prata"
        else:
            corrida["selo"] = "bronze"
    
    return {
        "tipo": tipo,
        "total_corridas": len(corridas),
        "media_global": round(media_global, 2),
        "minimo_avaliacoes": m,
        "ranking": corridas
    }


@router.get("/ranking-corridas/stats")
@cached(prefix='corridas', ttl_key='stats')
async def get_stats_ranking_corridas():
    """Estatísticas gerais do ranking de corridas"""
    
    total_corridas = await db.corridas_eventos.count_documents({})
    total_avaliacoes = await db.avaliacoes_corridas.count_documents({})
    total_avaliadores = len(await db.avaliacoes_corridas.distinct("usuario_id"))
    
    # Melhor avaliada
    pipeline = [
        {"$match": {"total_avaliacoes": {"$gte": 3}}},
        {"$sort": {"media_geral": -1}},
        {"$limit": 1}
    ]
    melhor = await db.corridas_eventos.aggregate(pipeline).to_list(1)
    
    # Mais avaliada
    pipeline_mais = [
        {"$sort": {"total_avaliacoes": -1}},
        {"$limit": 1}
    ]
    mais_avaliada = await db.corridas_eventos.aggregate(pipeline_mais).to_list(1)
    
    return {
        "total_corridas": total_corridas,
        "total_avaliacoes": total_avaliacoes,
        "total_avaliadores": total_avaliadores,
        "melhor_avaliada": melhor[0] if melhor else None,
        "mais_avaliada": mais_avaliada[0] if mais_avaliada else None
    }


@router.get("/ranking-corridas/estados")
@cached(prefix='corridas', ttl_key='estados')
async def get_estados_corridas():
    """Lista estados com corridas cadastradas"""
    estados = await db.corridas_eventos.distinct("estado")
    return {"estados": sorted([e for e in estados if e])}


@router.get("/ranking-corridas/cidades")
@cached(prefix='corridas', ttl_key='estados')
async def get_cidades_corridas(estado: str = None):
    """Lista cidades com corridas cadastradas"""
    filtro = {}
    if estado:
        filtro["estado"] = estado
    
    cidades = await db.corridas_eventos.distinct("cidade", filtro)
    return {"cidades": sorted([c for c in cidades if c])}


# ==================== AVALIAÇÕES ====================

@router.post("/corridas-eventos/{corrida_id}/avaliar")
async def avaliar_corrida(
    corrida_id: str,
    dados: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submete avaliação de uma corrida"""
    
    corrida = await db.corridas_eventos.find_one({"id": corrida_id})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    # Verificar se já avaliou
    avaliacao_existente = await db.avaliacoes_corridas.find_one({
        "corrida_id": corrida_id,
        "usuario_id": current_user["id"]
    })
    
    if avaliacao_existente:
        raise HTTPException(status_code=400, detail="Você já avaliou esta corrida")
    
    avaliacao = {
        "id": str(uuid.uuid4()),
        "corrida_id": corrida_id,
        "usuario_id": current_user["id"],
        "usuario_nome": current_user.get("nome", ""),
        "organizacao": dados.get("organizacao", 0),
        "percurso": dados.get("percurso", 0),
        "kit": dados.get("kit", 0),
        "hidratacao": dados.get("hidratacao", 0),
        "pos_prova": dados.get("pos_prova", 0),
        "comentario": dados.get("comentario", ""),
        "data_avaliacao": datetime.now(timezone.utc).isoformat()
    }
    
    # Calcular média da avaliação
    notas = [avaliacao["organizacao"], avaliacao["percurso"], avaliacao["kit"], 
             avaliacao["hidratacao"], avaliacao["pos_prova"]]
    avaliacao["media"] = sum(notas) / len(notas)
    
    await db.avaliacoes_corridas.insert_one(avaliacao)
    
    # Recalcular médias da corrida
    await recalcular_medias_corrida(corrida_id)
    await invalidate_on_corrida_change()
    
    return {"message": "Avaliação registrada com sucesso!", "id": avaliacao["id"]}


@router.get("/corridas-eventos/{corrida_id}/avaliacoes")
async def get_avaliacoes_corrida(corrida_id: str):
    """Lista avaliações de uma corrida"""
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"corrida_id": corrida_id},
        {"_id": 0}
    ).sort("data_avaliacao", -1).to_list(None)
    
    return avaliacoes


async def recalcular_medias_corrida(corrida_id: str):
    """Recalcula médias de uma corrida após nova avaliação"""
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"corrida_id": corrida_id}
    ).to_list(None)
    
    if not avaliacoes:
        return
    
    n = len(avaliacoes)
    
    medias = {
        "total_avaliacoes": n,
        "media_organizacao": sum(a["organizacao"] for a in avaliacoes) / n,
        "media_percurso": sum(a["percurso"] for a in avaliacoes) / n,
        "media_kit": sum(a["kit"] for a in avaliacoes) / n,
        "media_hidratacao": sum(a["hidratacao"] for a in avaliacoes) / n,
        "media_pos_prova": sum(a["pos_prova"] for a in avaliacoes) / n,
    }
    
    medias["media_geral"] = sum([
        medias["media_organizacao"],
        medias["media_percurso"],
        medias["media_kit"],
        medias["media_hidratacao"],
        medias["media_pos_prova"]
    ]) / 5
    
    # Arredondar
    for k in medias:
        if isinstance(medias[k], float):
            medias[k] = round(medias[k], 2)
    
    await db.corridas_eventos.update_one(
        {"id": corrida_id},
        {"$set": medias}
    )
