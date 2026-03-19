# /app/backend/routes/historico_routes.py
# Módulo de Histórico de Submissões do Atleta

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime, timezone

from config import db
from routes.auth_routes import get_current_user

router = APIRouter(tags=["Histórico"])


@router.get("/historico/submissoes")
async def get_historico_submissoes(
    status: Optional[str] = Query(None, description="Filtro por status: pendente, aprovado, reprovado"),
    periodo: Optional[str] = Query(None, description="Período: 7d, 30d, 90d, all"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna o histórico de todas as submissões do atleta logado
    Com filtros por status e período
    """
    usuario_id = current_user.get("id")
    
    # Construir filtro
    filtro = {"usuario_id": usuario_id}
    
    # Filtro por status
    if status and status in ["pendente", "aprovado", "reprovado"]:
        filtro["status"] = status
    
    # Filtro por período
    if periodo:
        now = datetime.now(timezone.utc)
        if periodo == "7d":
            data_inicio = now - timedelta(days=7)
        elif periodo == "30d":
            data_inicio = now - timedelta(days=30)
        elif periodo == "90d":
            data_inicio = now - timedelta(days=90)
        else:
            data_inicio = None
        
        if data_inicio:
            filtro["data_submissao"] = {"$gte": data_inicio.isoformat()}
    
    # Buscar resultados pendentes
    skip = (page - 1) * limit
    
    pendentes = await db.resultados_pendentes.find(
        filtro,
        {"_id": 0}
    ).sort("data_submissao", -1).skip(skip).limit(limit).to_list(None)
    
    # Contar totais
    total_pendentes = await db.resultados_pendentes.count_documents({"usuario_id": usuario_id, "status": "pendente"})
    total_aprovados = await db.resultados_pendentes.count_documents({"usuario_id": usuario_id, "status": "aprovado"})
    total_reprovados = await db.resultados_pendentes.count_documents({"usuario_id": usuario_id, "status": "reprovado"})
    total_geral = await db.resultados_pendentes.count_documents({"usuario_id": usuario_id})
    
    # Formatar resultados
    submissoes = []
    for p in pendentes:
        submissoes.append({
            "id": p.get("id"),
            "nome_competicao": p.get("nome_competicao") or p.get("competicao", "N/A"),
            "data_competicao": p.get("data_competicao", "N/A"),
            "distancia": p.get("distancia", "N/A"),
            "colocacao": p.get("colocacao"),
            "tempo": p.get("tempo", "N/A"),
            "modalidade": p.get("modalidade", "profissional_amador"),
            "status": p.get("status", "pendente"),
            "data_submissao": p.get("data_submissao"),
            "motivo_reprovacao": p.get("motivo_reprovacao"),
            "foto_podio_url": p.get("foto_podio_url"),
            "pontos_ganhos": p.get("pontos_ganhos", 0)
        })
    
    return {
        "submissoes": submissoes,
        "estatisticas": {
            "total": total_geral,
            "pendentes": total_pendentes,
            "aprovados": total_aprovados,
            "reprovados": total_reprovados
        },
        "paginacao": {
            "page": page,
            "limit": limit,
            "total_pages": (total_geral + limit - 1) // limit if total_geral > 0 else 1,
            "total_items": total_geral
        }
    }


@router.get("/historico/submissoes/{submissao_id}")
async def get_submissao_detalhe(
    submissao_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna detalhes de uma submissão específica
    """
    usuario_id = current_user.get("id")
    
    submissao = await db.resultados_pendentes.find_one(
        {"id": submissao_id, "usuario_id": usuario_id},
        {"_id": 0}
    )
    
    if not submissao:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    
    # Se aprovado, buscar dados da corrida registrada
    corrida_registrada = None
    if submissao.get("status") == "aprovado":
        corrida_registrada = await db.corridas.find_one(
            {
                "usuario_id": usuario_id,
                "nome": submissao.get("nome_competicao") or submissao.get("competicao")
            },
            {"_id": 0, "pontos": 1, "data": 1}
        )
    
    return {
        **submissao,
        "corrida_registrada": corrida_registrada
    }


@router.get("/historico/resumo")
async def get_resumo_historico(current_user: dict = Depends(get_current_user)):
    """
    Retorna um resumo do histórico do atleta
    """
    usuario_id = current_user.get("id")
    
    # Estatísticas de submissões
    total = await db.resultados_pendentes.count_documents({"usuario_id": usuario_id})
    pendentes = await db.resultados_pendentes.count_documents({"usuario_id": usuario_id, "status": "pendente"})
    aprovados = await db.resultados_pendentes.count_documents({"usuario_id": usuario_id, "status": "aprovado"})
    reprovados = await db.resultados_pendentes.count_documents({"usuario_id": usuario_id, "status": "reprovado"})
    
    # Taxa de aprovação
    taxa_aprovacao = (aprovados / total * 100) if total > 0 else 0
    
    # Última submissão
    ultima = await db.resultados_pendentes.find_one(
        {"usuario_id": usuario_id},
        {"_id": 0, "nome_competicao": 1, "data_submissao": 1, "status": 1}
    )
    
    # Corridas registradas (aprovadas)
    total_corridas = await db.corridas.count_documents({"usuario_id": usuario_id})
    
    # Soma de pontos
    pipeline = [
        {"$match": {"usuario_id": usuario_id}},
        {"$group": {"_id": None, "total_pontos": {"$sum": "$pontos"}}}
    ]
    resultado = await db.corridas.aggregate(pipeline).to_list(1)
    total_pontos = resultado[0]["total_pontos"] if resultado else 0
    
    return {
        "submissoes": {
            "total": total,
            "pendentes": pendentes,
            "aprovados": aprovados,
            "reprovados": reprovados,
            "taxa_aprovacao": round(taxa_aprovacao, 1)
        },
        "corridas": {
            "total": total_corridas,
            "pontos_totais": total_pontos
        },
        "ultima_submissao": ultima
    }


# Import necessário
from datetime import timedelta
