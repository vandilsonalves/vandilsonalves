# /app/backend/routes/instagram_routes.py
# Módulo Instagram - Ranking Run Inside (Análise de perfis Instagram)

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from config import db
from routes.auth_routes import get_admin_user

router = APIRouter(tags=["Instagram - Ranking Run Inside"])


# ==================== MODELS ====================

class InstagramProfileInput(BaseModel):
    username: str
    seguidores: int = 0
    seguindo: int = 0
    total_posts: int = 0
    bio: str = ""
    engagement_rate: float = 0.0
    engagement_rate_reels: float = 0.0
    crescimento_30_dias: float = 0.0
    media_likes: int = 0
    media_comentarios: int = 0
    media_views_reels: int = 0
    posts_semana: float = 0.0
    usa_hashtags: bool = True
    tem_cta: bool = False
    usa_stories: bool = True
    usa_reels: bool = True
    nicho: str = "corrida"


# ==================== MÉDIAS DE REFERÊNCIA POR NICHO ====================

MEDIAS_NICHO = {
    "corrida": {
        "engagement_rate": 3.5,
        "crescimento_medio": 2.0,
        "posts_semana": 4
    },
    "fitness": {
        "engagement_rate": 4.0,
        "crescimento_medio": 3.0,
        "posts_semana": 5
    },
    "lifestyle": {
        "engagement_rate": 2.5,
        "crescimento_medio": 1.5,
        "posts_semana": 3
    }
}


# ==================== LISTAR ANÁLISES ====================

@router.get("/admin/instagram/analises")
async def listar_analises_instagram(admin: dict = Depends(get_admin_user)):
    """Lista todas as análises de Instagram já realizadas"""
    analyses = await db.instagram_analyses.find(
        {}, {"_id": 0}
    ).sort("data_analise", -1).to_list(100)
    
    return analyses


@router.get("/admin/instagram/analises/{analysis_id}")
async def obter_analise_instagram(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Obtém uma análise específica por ID"""
    analysis = await db.instagram_analyses.find_one(
        {"id": analysis_id}, {"_id": 0}
    )
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    media_nicho = MEDIAS_NICHO.get(analysis.get('nicho', 'corrida'), MEDIAS_NICHO['corrida'])
    
    graficos_data = {
        "radar": {
            "labels": ["Bio", "Frequência", "Engajamento", "Crescimento", 
                      "Consistência", "Padrões", "Reels", "Formatos"],
            "values": [
                analysis.get('nota_bio', 0), analysis.get('nota_frequencia', 0), 
                analysis.get('nota_engajamento', 0), analysis.get('nota_crescimento', 0),
                analysis.get('nota_consistencia', 0), analysis.get('nota_padroes', 0), 
                analysis.get('nota_reels', 0), analysis.get('nota_formatos', 0)
            ],
            "max": 10
        },
        "gauge": {
            "value": analysis.get('score_final', 0),
            "min": 0,
            "max": 100,
            "ranges": [
                {"min": 0, "max": 60, "color": "#EF4444", "label": "Alto Risco"},
                {"min": 60, "max": 70, "color": "#F59E0B", "label": "Regular"},
                {"min": 70, "max": 80, "color": "#3B82F6", "label": "Profissional"},
                {"min": 80, "max": 90, "color": "#8B5CF6", "label": "Premium"},
                {"min": 90, "max": 95, "color": "#F59E0B", "label": "Elite Gold"},
                {"min": 95, "max": 100, "color": "#10B981", "label": "Elite Platinum"}
            ]
        },
        "metricas": {
            "seguidores": analysis.get('seguidores', 0),
            "seguindo": analysis.get('seguindo', 0),
            "posts": analysis.get('total_posts', 0),
            "er_post": analysis.get('engagement_rate', 0),
            "er_reels": analysis.get('engagement_rate_reels', 0),
            "crescimento": analysis.get('comparativo_crescimento', 0)
        }
    }
    
    return {
        "analysis": analysis,
        "graficos_data": graficos_data
    }


@router.delete("/admin/instagram/analises/{analysis_id}")
async def deletar_analise_instagram(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Deleta uma análise"""
    result = await db.instagram_analyses.delete_one({"id": analysis_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    return {"message": "Análise deletada com sucesso"}


# ==================== ANÁLISE SIMPLIFICADA ====================

@router.post("/admin/instagram/analisar-simplificado")
async def analisar_perfil_simplificado(dados: dict, admin: dict = Depends(get_admin_user)):
    """
    Análise simplificada de perfil Instagram
    Aceita dados básicos e calcula score
    """
    
    # Extrair dados
    username = dados.get("username", "")
    seguidores = dados.get("seguidores", 0)
    engagement_rate = dados.get("engagement_rate", 0)
    crescimento = dados.get("crescimento_30_dias", 0)
    posts_semana = dados.get("posts_semana", 0)
    
    # Calcular notas (0-10)
    nota_engajamento = min(10, engagement_rate * 2)
    nota_crescimento = min(10, (crescimento + 5) / 1.5)
    nota_frequencia = min(10, posts_semana * 1.5)
    nota_alcance = min(10, (seguidores / 10000) * 2)
    
    # Score final (média ponderada)
    score_final = (
        nota_engajamento * 0.35 +
        nota_crescimento * 0.25 +
        nota_frequencia * 0.20 +
        nota_alcance * 0.20
    ) * 10  # Escala 0-100
    
    # Determinar classificação
    if score_final >= 90:
        classificacao = "Elite Platinum"
    elif score_final >= 80:
        classificacao = "Elite Gold"
    elif score_final >= 70:
        classificacao = "Premium"
    elif score_final >= 60:
        classificacao = "Profissional"
    elif score_final >= 50:
        classificacao = "Regular"
    else:
        classificacao = "Alto Risco"
    
    # Criar documento de análise
    analysis = {
        "id": str(uuid.uuid4()),
        "username": username,
        "seguidores": seguidores,
        "engagement_rate": engagement_rate,
        "crescimento_30_dias": crescimento,
        "posts_semana": posts_semana,
        "nota_engajamento": round(nota_engajamento, 2),
        "nota_crescimento": round(nota_crescimento, 2),
        "nota_frequencia": round(nota_frequencia, 2),
        "nota_alcance": round(nota_alcance, 2),
        "score_final": round(score_final, 2),
        "classificacao": classificacao,
        "data_analise": datetime.now(timezone.utc).isoformat(),
        "analisado_por": admin.get("id"),
        "tipo": "simplificado"
    }
    
    await db.instagram_analyses.insert_one(analysis)
    
    return {
        "message": "Análise realizada com sucesso",
        "analysis": {k: v for k, v in analysis.items() if k != "_id"}
    }


# ==================== ESTATÍSTICAS ====================

@router.get("/admin/instagram/stats")
async def get_instagram_stats(admin: dict = Depends(get_admin_user)):
    """Estatísticas gerais das análises de Instagram"""
    
    total_analises = await db.instagram_analyses.count_documents({})
    
    # Média de scores
    pipeline = [
        {"$group": {
            "_id": None,
            "media_score": {"$avg": "$score_final"},
            "media_engagement": {"$avg": "$engagement_rate"}
        }}
    ]
    
    result = await db.instagram_analyses.aggregate(pipeline).to_list(1)
    
    # Distribuição por classificação
    pipeline_class = [
        {"$group": {"_id": "$classificacao", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    classificacoes = await db.instagram_analyses.aggregate(pipeline_class).to_list(None)
    
    return {
        "total_analises": total_analises,
        "media_score": round(result[0]["media_score"], 2) if result else 0,
        "media_engagement": round(result[0]["media_engagement"], 2) if result else 0,
        "distribuicao_classificacao": {c["_id"]: c["count"] for c in classificacoes if c["_id"]}
    }


# ==================== RANKING ====================

@router.get("/admin/instagram/ranking")
async def get_ranking_instagram(
    limit: int = 20,
    admin: dict = Depends(get_admin_user)
):
    """Ranking dos perfis analisados por score"""
    
    analyses = await db.instagram_analyses.find(
        {},
        {"_id": 0}
    ).sort("score_final", -1).limit(limit).to_list(None)
    
    for idx, analysis in enumerate(analyses):
        analysis["posicao"] = idx + 1
    
    return {
        "ranking": analyses,
        "total": len(analyses)
    }
