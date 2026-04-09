# /app/backend/routes/instagram_routes.py
# Módulo Instagram - Ranking Run Inside (Análise de perfis Instagram)
# Consolidado de server.py + rotas existentes

from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from openpyxl import Workbook
from openpyxl.styles import Font
import uuid
import csv
import io
import logging
import asyncio

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


class InstagramAnaliseSimplificada(BaseModel):
    """Modelo para análise simplificada - apenas dados básicos necessários"""
    username: str
    nome_completo: str = ""
    nicho: str = "corrida"
    seguidores: int
    seguindo: int
    total_posts: int
    bio: str = ""


class InstagramAnalysis(BaseModel):
    id: str
    username: str
    seguidores: int
    seguindo: int
    total_posts: int
    engagement_rate: float
    nota_bio: float
    nota_frequencia: float
    nota_engajamento: float
    nota_crescimento: float
    nota_consistencia: float
    nota_padroes: float
    nota_reels: float
    nota_formatos: float
    score_final: float
    classificacao: str
    data_analise: str


class InstagramAnalysisResponse(BaseModel):
    analysis: InstagramAnalysis
    recomendacoes: List[str]
    graficos_data: dict


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


# ==================== FUNÇÕES AUXILIARES ====================

def calcular_engagement_rate(seguidores: int, media_likes: int, media_comentarios: int) -> float:
    """Calcula a taxa de engajamento"""
    if seguidores <= 0:
        return 0.0
    return round(((media_likes + media_comentarios) / seguidores) * 100, 2)


def analisar_bio_automatico(bio: str) -> dict:
    """
    Analisa automaticamente a bio do Instagram.
    Retorna scores para: descrição, keywords, CTA, link, clareza.
    """
    if not bio:
        return {
            "tem_descricao": False,
            "tem_keywords": False,
            "tem_cta": False,
            "tem_link": False,
            "clareza": "ruim",
            "nota": 0
        }
    
    bio_lower = bio.lower()
    
    # Keywords comuns de corrida/fitness
    keywords_nicho = ['corrida', 'runner', 'running', 'maratona', 'atleta', 'corredor', 
                      'treino', 'fitness', 'personal', 'coach', 'assessoria', 'km', 
                      'pace', 'trilha', 'ultra', 'meia maratona', '10k', '21k', '42k',
                      'crossfit', 'musculação', 'gym', 'academia', 'esporte', 'sport']
    
    # CTAs comuns
    ctas = ['link', 'clique', 'acesse', 'saiba mais', 'conheça', 'siga', 'inscreva', 
            'compre', 'whatsapp', 'contato', 'agenda', 'agende', 'participe', 'baixe',
            'bio', 'dm', 'direct', '👇', '⬇️', 'linktree']
    
    tem_descricao = len(bio) > 20
    tem_keywords = any(kw in bio_lower for kw in keywords_nicho)
    tem_cta = any(cta in bio_lower for cta in ctas)
    tem_link = 'http' in bio_lower or 'link' in bio_lower or '.com' in bio_lower or 'wa.me' in bio_lower or '.br' in bio_lower
    
    # Avaliar clareza baseado em estrutura
    linhas = bio.split('\n')
    tem_emojis = any(ord(c) > 127 for c in bio)
    bem_estruturado = len(linhas) >= 2 or tem_emojis
    
    if len(bio) > 100 and bem_estruturado and tem_keywords:
        clareza = "excelente"
    elif len(bio) > 50 and (bem_estruturado or tem_keywords):
        clareza = "boa"
    elif len(bio) > 20:
        clareza = "regular"
    else:
        clareza = "ruim"
    
    # Calcular nota da bio
    clareza_scores = {"excelente": 2.0, "boa": 1.5, "regular": 1.0, "ruim": 0.0}
    nota = (
        (1.5 if tem_descricao else 0) +
        (3.0 if tem_keywords else 0) +
        (2.0 if tem_cta else 0) +
        (1.5 if tem_link else 0) +
        clareza_scores.get(clareza, 1.0)
    )
    
    return {
        "tem_descricao": tem_descricao,
        "tem_keywords": tem_keywords,
        "tem_cta": tem_cta,
        "tem_link": tem_link,
        "clareza": clareza,
        "nota": min(nota, 10.0)
    }


def analisar_posts_automatico(posts: list) -> dict:
    """
    Analisa automaticamente os posts recentes do Instagram.
    Calcula: média de likes, comentários, views de reels, frequência, etc.
    """
    if not posts:
        return {
            "media_likes": 0,
            "media_comentarios": 0,
            "media_views_reels": 0,
            "posts_por_semana": 0,
            "total_analisados": 0,
            "percentual_reels": 0,
            "percentual_carrossel": 0,
            "percentual_foto": 0,
            "picos_anormais": 0,
            "comentarios_repetitivos": 0,
            "horarios_artificiais": 0,
            "desvio_engajamento": 0
        }
    
    total_likes = 0
    total_comments = 0
    total_views = 0
    count_reels = 0
    count_carrossel = 0
    count_foto = 0
    timestamps = []
    likes_list = []
    
    for post in posts:
        likes = post.get('edge_liked_by', {}).get('count', 0) or post.get('like_count', 0)
        comments = post.get('edge_media_to_comment', {}).get('count', 0) or post.get('comment_count', 0)
        views = post.get('video_view_count', 0) or post.get('play_count', 0)
        timestamp = post.get('taken_at_timestamp', 0) or post.get('taken_at', 0)
        
        total_likes += likes
        total_comments += comments
        likes_list.append(likes)
        
        if timestamp:
            timestamps.append(timestamp)
        
        typename = post.get('__typename', '') or post.get('media_type', '')
        is_video = post.get('is_video', False) or typename in ['GraphVideo', 'XDTGraphVideo', 2]
        is_carousel = typename in ['GraphSidecar', 'XDTGraphSidecar', 8]
        
        if is_video:
            count_reels += 1
            total_views += views
        elif is_carousel:
            count_carrossel += 1
        else:
            count_foto += 1
    
    total_posts = len(posts)
    
    media_likes = total_likes / total_posts if total_posts > 0 else 0
    media_comentarios = total_comments / total_posts if total_posts > 0 else 0
    media_views_reels = total_views / count_reels if count_reels > 0 else 0
    
    percentual_reels = (count_reels / total_posts * 100) if total_posts > 0 else 0
    percentual_carrossel = (count_carrossel / total_posts * 100) if total_posts > 0 else 0
    percentual_foto = (count_foto / total_posts * 100) if total_posts > 0 else 0
    
    posts_por_semana = 0
    if len(timestamps) >= 2:
        timestamps.sort(reverse=True)
        time_span_seconds = timestamps[0] - timestamps[-1]
        if time_span_seconds > 0:
            weeks = time_span_seconds / (7 * 24 * 60 * 60)
            if weeks > 0:
                posts_por_semana = total_posts / weeks
    
    picos_anormais = 0
    if len(likes_list) >= 3:
        avg_likes = sum(likes_list) / len(likes_list)
        if avg_likes > 0:
            for likes in likes_list:
                if likes > avg_likes * 3:
                    picos_anormais += 1
    
    desvio_engajamento = 0
    if len(likes_list) >= 3:
        avg = sum(likes_list) / len(likes_list)
        if avg > 0:
            variance = sum((x - avg) ** 2 for x in likes_list) / len(likes_list)
            std_dev = variance ** 0.5
            desvio_engajamento = (std_dev / avg) * 100
    
    return {
        "media_likes": round(media_likes, 1),
        "media_comentarios": round(media_comentarios, 1),
        "media_views_reels": round(media_views_reels, 1),
        "posts_por_semana": round(posts_por_semana, 1),
        "total_analisados": total_posts,
        "percentual_reels": round(percentual_reels, 1),
        "percentual_carrossel": round(percentual_carrossel, 1),
        "percentual_foto": round(percentual_foto, 1),
        "picos_anormais": picos_anormais,
        "comentarios_repetitivos": 0,
        "horarios_artificiais": 0,
        "desvio_engajamento": round(desvio_engajamento, 1)
    }


def calcular_crescimento_estimado(seguidores: int, total_posts: int, engagement_rate: float) -> float:
    """Estima o crescimento mensal baseado em métricas conhecidas."""
    base_growth = 0.5
    
    if engagement_rate > 5:
        engagement_bonus = 2.0
    elif engagement_rate > 3:
        engagement_bonus = 1.0
    elif engagement_rate > 1:
        engagement_bonus = 0.5
    else:
        engagement_bonus = 0
    
    if seguidores < 1000:
        size_multiplier = 2.0
    elif seguidores < 10000:
        size_multiplier = 1.5
    elif seguidores < 100000:
        size_multiplier = 1.0
    else:
        size_multiplier = 0.5
    
    crescimento = (base_growth + engagement_bonus) * size_multiplier
    return round(min(crescimento, 10.0), 1)


# Stubs para funções de busca Instagram (não implementadas - requer API keys)
async def buscar_instagram_api_direta(username: str) -> dict:
    """Busca dados do Instagram via endpoint web_profile_info e fallback HTML parsing"""
    import httpx
    from bs4 import BeautifulSoup
    import json
    import re
    
    headers_api = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/{username}/",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    headers_html = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.instagram.com/"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            # Método 1: API endpoint web_profile_info
            try:
                url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
                resp = await client.get(url, headers=headers_api)
                if resp.status_code == 200:
                    data = resp.json()
                    user = data.get("data", {}).get("user")
                    if user:
                        logging.info(f"Instagram API direta: sucesso para @{username}")
                        return {"success": True, "user": user}
                elif resp.status_code == 429:
                    logging.warning(f"Instagram rate limited para @{username}")
                    return {"success": False, "error": "rate_limited"}
            except Exception as e:
                logging.warning(f"Método 1 (API) falhou para @{username}: {e}")
            
            # Método 2: HTML parsing com JSON-LD
            try:
                html_url = f"https://www.instagram.com/{username}/"
                resp_html = await client.get(html_url, headers=headers_html)
                if resp_html.status_code == 200:
                    soup = BeautifulSoup(resp_html.text, "html.parser")
                    
                    # Tentar JSON-LD
                    script_tag = soup.find("script", type="application/ld+json")
                    if script_tag and script_tag.string:
                        try:
                            ld_data = json.loads(script_tag.string)
                            stats = ld_data.get("author", {}).get("interactionStatistic", [])
                            followers = 0
                            posts_count = 0
                            for stat in stats:
                                if stat.get("interactionType") == "http://schema.org/FollowAction":
                                    followers = int(stat.get("userInteractionCount", 0))
                                elif "interactionCount" in str(stat):
                                    posts_count = int(stat.get("userInteractionCount", 0))
                            
                            if followers > 0 or posts_count > 0:
                                user = {
                                    "username": username,
                                    "full_name": ld_data.get("name", ""),
                                    "biography": ld_data.get("description", ""),
                                    "edge_followed_by": {"count": followers},
                                    "edge_follow": {"count": 0},
                                    "edge_owner_to_timeline_media": {"count": posts_count, "edges": []},
                                    "is_verified": False,
                                    "is_business_account": False,
                                    "external_url": ld_data.get("url", ""),
                                    "profile_pic_url": ld_data.get("image", "")
                                }
                                logging.info(f"HTML JSON-LD parse: sucesso para @{username}")
                                return {"success": True, "user": user}
                        except json.JSONDecodeError:
                            pass
                    
                    # Tentar extrair meta tags
                    meta_desc = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
                    if meta_desc:
                        desc = meta_desc.get("content", "")
                        # Parse "1,234 Followers, 567 Following, 89 Posts"
                        nums = re.findall(r'([\d,.]+[KkMm]?)\s*(Followers|Following|Posts)', desc)
                        if nums:
                            def parse_num(s):
                                s = s.replace(",", "").replace(".", "")
                                if s.upper().endswith("K"):
                                    return int(float(s[:-1]) * 1000)
                                elif s.upper().endswith("M"):
                                    return int(float(s[:-1]) * 1000000)
                                return int(s)
                            
                            followers = 0
                            following = 0
                            posts_ct = 0
                            for val, typ in nums:
                                if typ == "Followers":
                                    followers = parse_num(val)
                                elif typ == "Following":
                                    following = parse_num(val)
                                elif typ == "Posts":
                                    posts_ct = parse_num(val)
                            
                            # Extrair bio do resto da description
                            bio_match = re.search(r'Posts\s*-\s*(.+)', desc)
                            bio = bio_match.group(1).strip() if bio_match else ""
                            
                            meta_title = soup.find("meta", {"property": "og:title"})
                            full_name = meta_title.get("content", "").replace(f"(@{username})", "").strip() if meta_title else ""
                            
                            user = {
                                "username": username,
                                "full_name": full_name,
                                "biography": bio,
                                "edge_followed_by": {"count": followers},
                                "edge_follow": {"count": following},
                                "edge_owner_to_timeline_media": {"count": posts_ct, "edges": []},
                                "is_verified": False,
                                "is_business_account": False,
                                "external_url": ""
                            }
                            logging.info(f"HTML meta parse: sucesso para @{username}")
                            return {"success": True, "user": user}
            except Exception as e:
                logging.warning(f"Método 2 (HTML) falhou para @{username}: {e}")
            
            return {"success": False, "error": "not_found", "message": "Não foi possível obter dados do perfil."}
    except Exception as e:
        logging.error(f"Erro geral no scraping Instagram: {e}")
        return {"success": False, "error": str(e)}


async def buscar_instagram_rapidapi(username: str) -> dict:
    """Fallback - RapidAPI não configurada"""
    return {"success": False, "error": "not_implemented", "message": "RapidAPI não configurada"}


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
    
    # Se for análise tipo Social Blade, regenerar graficos_data completo
    if analysis.get("tipo") == "social_blade":
        seguidores = max(analysis.get("seguidores", 1), 1)
        views_score = analysis.get("views_score", 0)
        eng_score = analysis.get("eng_score", 0)
        curt_score = analysis.get("curt_score", 0)
        coment_score = analysis.get("coment_score", 0)
        cresc_score = analysis.get("cresc_score", 0)
        posts_score = analysis.get("posts_score", 0)
        score_medio = analysis.get("score_medio", 0)

        nota_nivel_map = {
            "A++": "Elite / Viral", "A+": "Excelente", "A": "Muito Forte",
            "B+": "Forte", "B": "Boa", "C+": "Saudável", "C": "Fraca",
            "D": "Muito fraca", "E": "Péssima", "F": "Péssima"
        }

        def score_to_metrica(s):
            if s >= 10: return "Excelente"
            if s >= 9: return "Ótimo"
            if s >= 8: return "Bom"
            if s >= 6: return "Regular"
            return "Péssimo"

        graficos_data = {
            "nota_gauge": {
                "nota": analysis.get("nota", "C"),
                "nota_calc": analysis.get("nota_calc", ""),
                "nivel": nota_nivel_map.get(analysis.get("nota", "C"), ""),
                "taxa_curtidas_pct": analysis.get("taxa_curtidas_pct", 0)
            },
            "views_reels": {
                "media_views": analysis.get("media_views_reels", 0),
                "taxa_views_pct": analysis.get("taxa_views_pct", 0),
                "metrica": score_to_metrica(views_score),
                "score": views_score,
                "escala": [
                    {"label": "< 10%", "range": "Péssimo", "min": 0, "max": 10},
                    {"label": "10-30%", "range": "Regular", "min": 10, "max": 30},
                    {"label": "30-70%", "range": "Bom", "min": 30, "max": 70},
                    {"label": "70-120%", "range": "Ótimo", "min": 70, "max": 120},
                    {"label": "> 120%", "range": "Excelente", "min": 120, "max": 200}
                ]
            },
            "engajamento": {
                "taxa": analysis.get("engajamento_pct", 0),
                "metrica": score_to_metrica(eng_score),
                "score": eng_score,
                "labels": ["Curtidas Médias", "Comentários Médios"],
                "values": [analysis.get("curtidas_medias", 0), analysis.get("comentarios_medios", 0)]
            },
            "curtidas": {
                "valor": analysis.get("curtidas_medias", 0),
                "taxa": analysis.get("taxa_curtidas_pct", 0),
                "metrica": score_to_metrica(curt_score),
                "score": curt_score
            },
            "comentarios": {
                "valor": analysis.get("comentarios_medios", 0),
                "taxa": analysis.get("taxa_comentarios_pct", 0),
                "metrica": score_to_metrica(coment_score),
                "score": coment_score
            },
            "crescimento": {
                "taxa": analysis.get("crescimento_pct", 0),
                "metrica": score_to_metrica(cresc_score),
                "score": cresc_score,
                "saldo": analysis.get("saldo_seguidores", 0),
                "radar_labels": ["Crescimento %", "Ganho 30d", "Frequência Posts", "Engajamento", "Curtidas", "Comentários"],
                "radar_values": [round(v, 1) for v in [
                    cresc_score,
                    min(10, analysis.get("ganho_seguidores_30d", 0) / max(seguidores * 0.01, 1)),
                    posts_score, eng_score, curt_score, coment_score
                ]]
            },
            "posts": {
                "total": analysis.get("posts_30d", 0),
                "metrica": score_to_metrica(posts_score),
                "score": posts_score,
                "semanal": analysis.get("media_semanal_posts", 0),
                "escala": [
                    {"label": "0-4", "range": "Péssimo", "score": "1-4"},
                    {"label": "5-8", "range": "Regular", "score": "5-6"},
                    {"label": "9-16", "range": "Bom", "score": "7-8"},
                    {"label": "17-30", "range": "Ótimo", "score": "9"},
                    {"label": "30+", "range": "Excelente", "score": "10"}
                ]
            },
            "scores": {
                "views": views_score, "engajamento": eng_score, "curtidas": curt_score,
                "comentarios": coment_score, "crescimento": cresc_score, "posts": posts_score,
                "media": score_medio
            }
        }
        return {"analysis": analysis, "graficos_data": graficos_data}
    
    # Análise legada
    graficos_data = {
        "radar": {
            "labels": ["Bio", "Frequência", "Engajamento", "Crescimento", 
                      "Consistência", "Padrões", "Reels", "Formatos"],
            "values": [
                analysis.get('nota_bio', 0), analysis.get('nota_frequencia', 0), 
                analysis.get('nota_engajamento', 0), analysis.get('nota_crescimento', 0),
                analysis.get('nota_consistencia', 0), analysis.get('nota_padroes', 0), 
                analysis.get('nota_reels', 0), analysis.get('nota_formatos', 0)
            ]
        }
    }
    
    return {"analysis": analysis, "graficos_data": graficos_data}


@router.delete("/admin/instagram/analises/{analysis_id}")
async def deletar_analise_instagram(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Deleta uma análise"""
    result = await db.instagram_analyses.delete_one({"id": analysis_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    return {"message": "Análise deletada com sucesso"}



def extrair_username_do_link(link_ou_username: str) -> str:
    """Extrai o username de um link do Instagram ou de um @username"""
    import re
    texto = link_ou_username.strip()
    # Remove @ se presente
    if texto.startswith('@'):
        return texto[1:].strip().lower()
    # Extrai de URLs como https://instagram.com/username ou https://www.instagram.com/username/
    match = re.search(r'(?:instagram\.com|instagr\.am)/([A-Za-z0-9_.]+)', texto)
    if match:
        return match.group(1).lower()
    # Se não é link nem @, assume que é username direto
    return texto.lower().replace(' ', '')



# ==================== BUSCAR DADOS INSTAGRAM ====================

@router.get("/admin/instagram/buscar/{username:path}")
async def buscar_dados_instagram(username: str, admin: dict = Depends(get_admin_user)):
    """
    Busca dados completos de um perfil Instagram automaticamente.
    Aceita: @username, username, ou link completo do Instagram.
    """
    username = extrair_username_do_link(username)
    
    if not username:
        raise HTTPException(status_code=400, detail="Username é obrigatório")
    
    user = None
    source = "unknown"
    
    try:
        result = await buscar_instagram_api_direta(username)
        
        if result.get('success') and result.get('user'):
            user = result['user']
            source = "instagram_direct"
        elif result.get('error') == 'rate_limited':
            logging.info(f"Instagram rate limited, tentando RapidAPI para {username}")
            rapid_result = await buscar_instagram_rapidapi(username)
            if rapid_result.get('success') and rapid_result.get('data'):
                rapid_data = rapid_result['data']
                user = {
                    'username': rapid_data.get('username', username),
                    'full_name': rapid_data.get('full_name', ''),
                    'biography': rapid_data.get('biography', ''),
                    'edge_followed_by': {'count': rapid_data.get('follower_count', 0)},
                    'edge_follow': {'count': rapid_data.get('following_count', 0)},
                    'edge_owner_to_timeline_media': {
                        'count': rapid_data.get('media_count', 0),
                        'edges': []
                    },
                    'is_verified': rapid_data.get('is_verified', False),
                    'is_business_account': rapid_data.get('is_business', False),
                    'external_url': rapid_data.get('external_url', '')
                }
                source = "rapidapi"
        
        if not user:
            return {
                "success": False,
                "error": "scraping_failed",
                "message": f"Não foi possível obter dados de @{username}. O perfil pode ser privado ou o Instagram bloqueou a requisição. Use a inserção manual."
            }
        
        # Extrair dados
        seguidores = user.get('edge_followed_by', {}).get('count', 0) or user.get('follower_count', 0)
        seguindo = user.get('edge_follow', {}).get('count', 0) or user.get('following_count', 0)
        total_posts = user.get('edge_owner_to_timeline_media', {}).get('count', 0) or user.get('media_count', 0)
        bio = user.get('biography', '')
        nome_completo = user.get('full_name', '')
        profile_pic = user.get('profile_pic_url_hd', '') or user.get('profile_pic_url', '')
        
        posts = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
        posts_data = [edge.get('node', edge) for edge in posts] if posts else []
        
        analise_bio = analisar_bio_automatico(bio)
        analise_posts = analisar_posts_automatico(posts_data)
        
        media_likes = analise_posts.get('media_likes', 0)
        media_comentarios = analise_posts.get('media_comentarios', 0)
        engagement_rate = calcular_engagement_rate(seguidores, media_likes, media_comentarios)
        
        crescimento_estimado = calcular_crescimento_estimado(seguidores, total_posts, engagement_rate)
        
        ratio_ff = seguidores / seguindo if seguindo > 0 else 0
        
        return {
            "success": True,
            "source": source,
            "profile": {
                "username": user.get('username', username),
                "nome_completo": nome_completo,
                "bio": bio,
                "profile_pic": profile_pic,
                "seguidores": seguidores,
                "seguindo": seguindo,
                "total_posts": total_posts,
                "is_verified": user.get('is_verified', False),
                "is_business": user.get('is_business_account', False),
                "external_url": user.get('external_url', '')
            },
            "metricas_calculadas": {
                "engagement_rate": engagement_rate,
                "media_likes": media_likes,
                "media_comentarios": media_comentarios,
                "media_views_reels": analise_posts.get('media_views_reels', 0),
                "posts_por_semana": analise_posts.get('posts_por_semana', 0),
                "crescimento_estimado": crescimento_estimado,
                "ratio_followers_following": round(ratio_ff, 2)
            },
            "analise_bio": analise_bio,
            "analise_posts": analise_posts
        }
        
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "timeout",
            "error": "Timeout ao acessar Instagram. Tente novamente.",
        }
    except Exception as e:
        logging.error(f"Erro ao buscar dados do Instagram: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Erro ao buscar dados. Use a análise manual."
        }


# ==================== ANÁLISE AUTOMÁTICA ====================

@router.post("/admin/instagram/analisar-automatico/{username:path}")
async def analisar_instagram_automatico(username: str, nicho: str = "corrida", admin: dict = Depends(get_admin_user)):
    """
    Busca dados do Instagram e faz análise completa automaticamente.
    Aceita: @username, username, ou link completo do Instagram.
    """
    username = extrair_username_do_link(username)
    busca_result = await buscar_dados_instagram(username, admin)
    
    if not busca_result.get('success'):
        raise HTTPException(
            status_code=400,
            detail=busca_result.get('message', 'Não foi possível obter dados do perfil. O Instagram pode estar bloqueando as requisições. Use a inserção manual.')
        )
    
    profile = busca_result['profile']
    metricas = busca_result['metricas_calculadas']
    analise_bio = busca_result['analise_bio']
    analise_posts = busca_result.get('analise_posts', {})
    
    media_nicho = MEDIAS_NICHO.get(nicho, MEDIAS_NICHO['corrida'])
    
    # Calcular notas
    nota_bio = analise_bio.get('nota', 5.0)
    
    posts_semana = metricas.get('posts_por_semana', 0) or analise_posts.get('posts_por_semana', 0)
    if posts_semana >= media_nicho['posts_semana']:
        nota_frequencia = 10.0
    elif posts_semana >= media_nicho['posts_semana'] * 0.7:
        nota_frequencia = 8.0
    elif posts_semana >= media_nicho['posts_semana'] * 0.5:
        nota_frequencia = 6.0
    elif posts_semana > 0:
        nota_frequencia = 4.0
    else:
        nota_frequencia = 2.0
    
    er = metricas.get('engagement_rate', 0)
    if er >= media_nicho['engagement_rate'] * 1.5:
        nota_engajamento = 10.0
    elif er >= media_nicho['engagement_rate']:
        nota_engajamento = 8.0
    elif er >= media_nicho['engagement_rate'] * 0.7:
        nota_engajamento = 6.0
    elif er > 0:
        nota_engajamento = 4.0
    else:
        nota_engajamento = 2.0
    
    crescimento = metricas.get('crescimento_estimado', 0)
    if crescimento >= media_nicho['crescimento_medio'] * 1.5:
        nota_crescimento = 10.0
    elif crescimento >= media_nicho['crescimento_medio']:
        nota_crescimento = 8.0
    elif crescimento >= media_nicho['crescimento_medio'] * 0.5:
        nota_crescimento = 6.0
    else:
        nota_crescimento = 4.0
    
    desvio = analise_posts.get('desvio_engajamento', 0)
    picos = analise_posts.get('picos_anormais', 0)
    if desvio < 50 and picos == 0:
        nota_consistencia = 10.0
    elif desvio < 80 and picos <= 1:
        nota_consistencia = 8.0
    elif desvio < 100:
        nota_consistencia = 6.0
    else:
        nota_consistencia = 4.0
    
    nota_padroes = min(10.0, nota_consistencia + 1) if picos == 0 else max(4.0, nota_consistencia - 2)
    
    perc_reels = analise_posts.get('percentual_reels', 0)
    if perc_reels >= 40:
        nota_reels = 10.0
    elif perc_reels >= 25:
        nota_reels = 8.0
    elif perc_reels >= 10:
        nota_reels = 6.0
    else:
        nota_reels = 4.0
    
    perc_carrossel = analise_posts.get('percentual_carrossel', 0)
    variedade = (perc_reels > 0) + (perc_carrossel > 0) + (analise_posts.get('percentual_foto', 0) > 0)
    nota_formatos = min(10.0, variedade * 3 + 1)
    
    # Score final
    pesos = {
        'bio': 0.10, 'frequencia': 0.15, 'engajamento': 0.20,
        'crescimento': 0.15, 'consistencia': 0.15, 'padroes': 0.10,
        'reels': 0.08, 'formatos': 0.07
    }
    
    score_ponderado = (
        nota_bio * pesos['bio'] +
        nota_frequencia * pesos['frequencia'] +
        nota_engajamento * pesos['engajamento'] +
        nota_crescimento * pesos['crescimento'] +
        nota_consistencia * pesos['consistencia'] +
        nota_padroes * pesos['padroes'] +
        nota_reels * pesos['reels'] +
        nota_formatos * pesos['formatos']
    )
    
    score_final = round(score_ponderado * 10, 2)
    
    if score_final >= 90:
        classificacao = "Elite Platinum"
    elif score_final >= 80:
        classificacao = "Elite Gold"
    elif score_final >= 70:
        classificacao = "Premium"
    elif score_final >= 60:
        classificacao = "Profissional"
    else:
        classificacao = "Alto Risco"
    
    # Salvar análise
    analysis_doc = {
        "id": str(uuid.uuid4()),
        "username": profile['username'],
        "nome_completo": profile.get('nome_completo', ''),
        "seguidores": profile['seguidores'],
        "seguindo": profile['seguindo'],
        "total_posts": profile['total_posts'],
        "bio": profile.get('bio', ''),
        "profile_pic": profile.get('profile_pic', ''),
        "engagement_rate": metricas.get('engagement_rate', 0),
        "engagement_rate_reels": 0,
        "crescimento_30_dias": metricas.get('crescimento_estimado', 0),
        "comparativo_crescimento": metricas.get('crescimento_estimado', 0),
        "media_likes": metricas.get('media_likes', 0),
        "media_comentarios": metricas.get('media_comentarios', 0),
        "media_views_reels": metricas.get('media_views_reels', 0),
        "posts_semana": posts_semana,
        "nota_bio": round(nota_bio, 2),
        "nota_frequencia": round(nota_frequencia, 2),
        "nota_engajamento": round(nota_engajamento, 2),
        "nota_crescimento": round(nota_crescimento, 2),
        "nota_consistencia": round(nota_consistencia, 2),
        "nota_padroes": round(nota_padroes, 2),
        "nota_reels": round(nota_reels, 2),
        "nota_formatos": round(nota_formatos, 2),
        "score_final": score_final,
        "classificacao": classificacao,
        "data_analise": datetime.now(timezone.utc).isoformat(),
        "analisado_por": admin.get("id"),
        "nicho": "corrida",
        "source": "instagram_api_automatico"
    }
    
    await db.instagram_analyses.insert_one(analysis_doc)
    
    return {
        "message": "Análise automática concluída!",
        "analysis": {k: v for k, v in analysis_doc.items() if k != "_id"},
        "profile": profile,
        "metricas_calculadas": metricas
    }


# ==================== ANÁLISE MANUAL ====================

@router.post("/admin/instagram/analisar")
async def analisar_perfil_instagram(dados: InstagramProfileInput, admin: dict = Depends(get_admin_user)):
    """
    Analisa um perfil do Instagram com dados inseridos manualmente
    """
    media_nicho = MEDIAS_NICHO.get(dados.nicho, MEDIAS_NICHO['corrida'])
    
    analise_bio = analisar_bio_automatico(dados.bio)
    nota_bio = analise_bio.get('nota', 5.0)
    
    if dados.posts_semana >= media_nicho['posts_semana']:
        nota_frequencia = 10.0
    elif dados.posts_semana >= media_nicho['posts_semana'] * 0.7:
        nota_frequencia = 8.0
    elif dados.posts_semana >= media_nicho['posts_semana'] * 0.5:
        nota_frequencia = 6.0
    elif dados.posts_semana > 0:
        nota_frequencia = 4.0
    else:
        nota_frequencia = 2.0
    
    er = dados.engagement_rate
    if er >= media_nicho['engagement_rate'] * 1.5:
        nota_engajamento = 10.0
    elif er >= media_nicho['engagement_rate']:
        nota_engajamento = 8.0
    elif er >= media_nicho['engagement_rate'] * 0.7:
        nota_engajamento = 6.0
    elif er > 0:
        nota_engajamento = 4.0
    else:
        nota_engajamento = 2.0
    
    crescimento = dados.crescimento_30_dias
    if crescimento >= media_nicho['crescimento_medio'] * 1.5:
        nota_crescimento = 10.0
    elif crescimento >= media_nicho['crescimento_medio']:
        nota_crescimento = 8.0
    elif crescimento >= media_nicho['crescimento_medio'] * 0.5:
        nota_crescimento = 6.0
    else:
        nota_crescimento = 4.0
    
    nota_consistencia = 7.0
    nota_padroes = 7.0
    
    nota_reels = 8.0 if dados.usa_reels else 4.0
    nota_formatos = 6.0
    
    pesos = {
        'bio': 0.10, 'frequencia': 0.15, 'engajamento': 0.20,
        'crescimento': 0.15, 'consistencia': 0.15, 'padroes': 0.10,
        'reels': 0.08, 'formatos': 0.07
    }
    
    score_ponderado = (
        nota_bio * pesos['bio'] +
        nota_frequencia * pesos['frequencia'] +
        nota_engajamento * pesos['engajamento'] +
        nota_crescimento * pesos['crescimento'] +
        nota_consistencia * pesos['consistencia'] +
        nota_padroes * pesos['padroes'] +
        nota_reels * pesos['reels'] +
        nota_formatos * pesos['formatos']
    )
    
    score_final = round(score_ponderado * 10, 2)
    
    if score_final >= 90:
        classificacao = "Elite Platinum"
    elif score_final >= 80:
        classificacao = "Elite Gold"
    elif score_final >= 70:
        classificacao = "Premium"
    elif score_final >= 60:
        classificacao = "Profissional"
    else:
        classificacao = "Alto Risco"
    
    recomendacoes = []
    if nota_bio < 7:
        recomendacoes.append("Melhore sua bio: adicione palavras-chave do nicho, CTA e link")
    if nota_frequencia < 7:
        recomendacoes.append(f"Aumente a frequência de posts para {media_nicho['posts_semana']}x por semana")
    if nota_engajamento < 7:
        recomendacoes.append("Trabalhe o engajamento: responda comentários e interaja com seguidores")
    if not dados.usa_reels:
        recomendacoes.append("Comece a usar Reels - é o formato com maior alcance atualmente")
    
    analysis_id = str(uuid.uuid4())
    analysis_dict = {
        "id": analysis_id,
        "username": dados.username,
        "seguidores": dados.seguidores,
        "seguindo": dados.seguindo,
        "total_posts": dados.total_posts,
        "bio": dados.bio,
        "engagement_rate": dados.engagement_rate,
        "engagement_rate_reels": dados.engagement_rate_reels,
        "crescimento_30_dias": dados.crescimento_30_dias,
        "comparativo_crescimento": dados.crescimento_30_dias - media_nicho['crescimento_medio'],
        "media_likes": dados.media_likes,
        "media_comentarios": dados.media_comentarios,
        "media_views_reels": dados.media_views_reels,
        "posts_semana": dados.posts_semana,
        "nota_bio": round(nota_bio, 2),
        "nota_frequencia": round(nota_frequencia, 2),
        "nota_engajamento": round(nota_engajamento, 2),
        "nota_crescimento": round(nota_crescimento, 2),
        "nota_consistencia": round(nota_consistencia, 2),
        "nota_padroes": round(nota_padroes, 2),
        "nota_reels": round(nota_reels, 2),
        "nota_formatos": round(nota_formatos, 2),
        "score_final": score_final,
        "classificacao": classificacao,
        "data_analise": datetime.now(timezone.utc).isoformat(),
        "analisado_por": admin.get("id"),
        "nicho": dados.nicho,
        "source": "manual"
    }
    
    await db.instagram_analyses.insert_one(analysis_dict)
    
    graficos_data = {
        "radar": {
            "labels": ["Bio", "Frequência", "Engajamento", "Crescimento", 
                      "Consistência", "Padrões", "Reels", "Formatos"],
            "values": [nota_bio, nota_frequencia, nota_engajamento, nota_crescimento,
                      nota_consistencia, nota_padroes, nota_reels, nota_formatos],
            "max": 10
        },
        "gauge": {
            "value": score_final,
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
        }
    }
    
    analysis = InstagramAnalysis(
        id=analysis_id,
        username=dados.username,
        seguidores=dados.seguidores,
        seguindo=dados.seguindo,
        total_posts=dados.total_posts,
        engagement_rate=dados.engagement_rate,
        nota_bio=round(nota_bio, 2),
        nota_frequencia=round(nota_frequencia, 2),
        nota_engajamento=round(nota_engajamento, 2),
        nota_crescimento=round(nota_crescimento, 2),
        nota_consistencia=round(nota_consistencia, 2),
        nota_padroes=round(nota_padroes, 2),
        nota_reels=round(nota_reels, 2),
        nota_formatos=round(nota_formatos, 2),
        score_final=score_final,
        classificacao=classificacao,
        data_analise=datetime.now(timezone.utc).isoformat()
    )
    
    return InstagramAnalysisResponse(
        analysis=analysis,
        recomendacoes=recomendacoes,
        graficos_data=graficos_data
    )


# ==================== EXPORTAÇÃO ====================

@router.get("/admin/instagram/export/{analysis_id}")
async def exportar_analise_xlsx(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Exporta análise em formato XLSX"""
    analysis = await db.instagram_analyses.find_one(
        {"id": analysis_id}, {"_id": 0}
    )
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Análise Instagram"
    
    ws.merge_cells('A1:D1')
    ws['A1'] = f"Ranking Run Inside - Análise de @{analysis['username']}"
    ws['A1'].font = Font(bold=True, size=16)
    
    ws['A3'] = "Data da Análise:"
    ws['B3'] = analysis['data_analise'][:10]
    ws['A4'] = "Classificação:"
    ws['B4'] = analysis['classificacao']
    ws['A5'] = "Score Final:"
    ws['B5'] = f"{analysis['score_final']}/100"
    
    ws['A7'] = "MÉTRICAS DO PERFIL"
    ws['A7'].font = Font(bold=True)
    
    metricas = [
        ("Seguidores", analysis.get('seguidores', 0)),
        ("Seguindo", analysis.get('seguindo', 0)),
        ("Total de Posts", analysis.get('total_posts', 0)),
        ("Engagement Rate", f"{analysis.get('engagement_rate', 0)}%"),
    ]
    
    for i, (label, value) in enumerate(metricas, start=8):
        ws[f'A{i}'] = label
        ws[f'B{i}'] = value
    
    row = 13
    ws[f'A{row}'] = "NOTAS INDIVIDUAIS (0-10)"
    ws[f'A{row}'].font = Font(bold=True)
    
    notas = [
        ("Bio", analysis.get('nota_bio', 0)),
        ("Frequência", analysis.get('nota_frequencia', 0)),
        ("Engajamento", analysis.get('nota_engajamento', 0)),
        ("Crescimento", analysis.get('nota_crescimento', 0)),
        ("Consistência", analysis.get('nota_consistencia', 0)),
        ("Padrões", analysis.get('nota_padroes', 0)),
        ("Reels", analysis.get('nota_reels', 0)),
        ("Formatos", analysis.get('nota_formatos', 0))
    ]
    
    for i, (label, value) in enumerate(notas, start=row+1):
        ws[f'A{i}'] = label
        ws[f'B{i}'] = value
    
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 20
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=analise_{analysis['username']}.xlsx"
        }
    )


@router.get("/admin/instagram/export-csv/{analysis_id}")
async def exportar_analise_csv(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Exporta análise em formato CSV"""
    analysis = await db.instagram_analyses.find_one(
        {"id": analysis_id}, {"_id": 0}
    )
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Ranking Run Inside - Análise de Instagram"])
    writer.writerow([])
    writer.writerow(["Campo", "Valor"])
    writer.writerow(["Username", f"@{analysis.get('username', '')}"])
    writer.writerow(["Score Final", analysis.get('score_final', 0)])
    writer.writerow(["Classificação", analysis.get('classificacao', '')])
    writer.writerow([])
    writer.writerow(["Métricas"])
    writer.writerow(["Seguidores", analysis.get('seguidores', 0)])
    writer.writerow(["Engagement Rate", f"{analysis.get('engagement_rate', 0)}%"])
    writer.writerow([])
    writer.writerow(["Notas (0-10)"])
    writer.writerow(["Bio", analysis.get('nota_bio', 0)])
    writer.writerow(["Frequência", analysis.get('nota_frequencia', 0)])
    writer.writerow(["Engajamento", analysis.get('nota_engajamento', 0)])
    writer.writerow(["Crescimento", analysis.get('nota_crescimento', 0)])
    writer.writerow(["Consistência", analysis.get('nota_consistencia', 0)])
    writer.writerow(["Padrões", analysis.get('nota_padroes', 0)])
    writer.writerow(["Reels", analysis.get('nota_reels', 0)])
    writer.writerow(["Formatos", analysis.get('nota_formatos', 0)])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=analise_{analysis['username']}.csv"
        }
    )


# ==================== EXPORTAÇÃO PDF ====================

@router.get("/admin/instagram/export-pdf/{analysis_id}")
async def exportar_analise_pdf(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Exporta análise em formato PDF com gráficos e tabelas de referência"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                     Spacer, HRFlowable, Image as RLImage, PageBreak)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    analysis = await db.instagram_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    # -------- helpers --------
    seguidores = max(analysis.get("seguidores", 1), 1)

    def score_to_metrica(s):
        if s >= 10: return "Excelente"
        if s >= 9: return "Ótimo"
        if s >= 8: return "Bom"
        if s >= 6: return "Regular"
        return "Péssimo"

    scores = {
        "views": analysis.get("views_score", 0),
        "engajamento": analysis.get("eng_score", 0),
        "curtidas": analysis.get("curt_score", 0),
        "comentarios": analysis.get("coment_score", 0),
        "crescimento": analysis.get("cresc_score", 0),
        "posts": analysis.get("posts_score", 0),
        "media": analysis.get("score_medio", 0),
    }

    dark_bg = '#0F172A'
    card_bg = '#1E293B'
    grid_c = '#334155'
    text_c = '#CBD5E1'

    def make_chart_image(fig) -> io.BytesIO:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                    facecolor=dark_bg, edgecolor='none', transparent=False)
        plt.close(fig)
        buf.seek(0)
        return buf

    chart_images = []

    # ===== 1. DONUT - Nota =====
    nota_val = analysis.get("nota", "C")
    nota_num = {"A++":100,"A+":93,"A":86,"A-":79,"B+":72,"B":65,"B-":58,"C+":51,"C":44,"C-":37,"D+":30,"D":23,"D-":16,"F":8}
    nota_colors_map = {"A++":"#059669","A+":"#10B981","A":"#22C55E","A-":"#4ADE80","B+":"#3B82F6","B":"#60A5FA","B-":"#93C5FD","C+":"#F59E0B","C":"#FBBF24","C-":"#FCD34D","D+":"#FB923C","D":"#F97316","D-":"#EA580C","F":"#DC2626"}
    pct = nota_num.get(nota_val, 40)
    fig, ax = plt.subplots(figsize=(5, 3.5), facecolor=dark_bg)
    ax.set_facecolor(dark_bg)
    cor = nota_colors_map.get(nota_val, '#94A3B8')
    ax.pie([pct, 100-pct], colors=[cor, card_bg], startangle=90,
           wedgeprops=dict(width=0.35, edgecolor=dark_bg), radius=1)
    ax.text(0, 0.05, nota_val, ha='center', va='center', fontsize=28, fontweight='bold', color=cor)
    ax.text(0, -0.2, analysis.get("nota_nivel", ""), ha='center', va='center', fontsize=9, color=text_c)
    ax.set_title("1. Nota – Taxa de Curtidas (Donut)", color='white', fontsize=11, fontweight='bold', pad=15)
    chart_images.append(make_chart_image(fig))

    # ===== 2. BARRAS HORIZONTAIS - Views de Reels =====
    taxa_views = round(analysis.get("media_views_reels", 0) / seguidores * 100, 1) if seguidores else 0
    escala_labels = ["< 10%", "10-30%", "30-70%", "70-120%", "> 120%"]
    escala_ranges = [(0,10),(10,30),(30,70),(70,120),(120,200)]
    bar_colors = ['#475569']*5
    for i,(mn,mx) in enumerate(escala_ranges):
        if mn <= taxa_views < (mx if mx < 200 else float('inf')):
            bar_colors[i] = '#8B5CF6'
    fig, ax = plt.subplots(figsize=(5, 3), facecolor=dark_bg)
    ax.set_facecolor(dark_bg)
    ax.barh(escala_labels, [r[1]-r[0] for r in escala_ranges], color=bar_colors, edgecolor=dark_bg, height=0.6)
    ax.set_title("2. Views de Reels (Barras)", color='white', fontsize=11, fontweight='bold', pad=10)
    ax.tick_params(colors=text_c, labelsize=8)
    ax.spines[:].set_visible(False)
    ax.text(0.98, 0.02, f"Média: {analysis.get('media_views_reels',0):,}  |  Taxa: {taxa_views}%  |  Score: {scores['views']}/10",
            transform=ax.transAxes, ha='right', va='bottom', fontsize=7, color=text_c)
    chart_images.append(make_chart_image(fig))

    # ===== 3. PIZZA - Engajamento =====
    curt_m = analysis.get("curtidas_medias", 0)
    coment_m = analysis.get("comentarios_medios", 0)
    eng_vals = [curt_m, coment_m] if (curt_m + coment_m) > 0 else [1, 1]
    fig, ax = plt.subplots(figsize=(5, 3.5), facecolor=dark_bg)
    ax.set_facecolor(dark_bg)
    wedges, texts, autotexts = ax.pie(eng_vals, labels=["Curtidas", "Comentários"],
        colors=['#EC4899', '#8B5CF6'], autopct='%1.0f%%', startangle=90,
        wedgeprops=dict(width=0.6, edgecolor=dark_bg),
        textprops=dict(color=text_c, fontsize=8))
    for t in autotexts: t.set_fontsize(8); t.set_color('white')
    ax.set_title(f"3. Engajamento – {analysis.get('engajamento_pct',0)}% (Pizza)", color='white', fontsize=11, fontweight='bold', pad=10)
    chart_images.append(make_chart_image(fig))

    # ===== 4. COLUNAS - Curtidas =====
    fig, ax = plt.subplots(figsize=(5, 3), facecolor=dark_bg)
    ax.set_facecolor(dark_bg)
    cols = ["Curtidas/Post", "Taxa %"]
    vals = [analysis.get("curtidas_medias", 0), analysis.get("taxa_curtidas_pct", 0)]
    ax.bar(cols, vals, color=['#F59E0B', '#FB923C'], width=0.5, edgecolor=dark_bg)
    for i, v in enumerate(vals): ax.text(i, v + max(vals)*0.03, str(v), ha='center', fontsize=9, color='white', fontweight='bold')
    ax.set_title("4. Curtidas Médias (Colunas)", color='white', fontsize=11, fontweight='bold', pad=10)
    ax.tick_params(colors=text_c, labelsize=8)
    ax.spines[:].set_visible(False)
    ax.set_ylabel('')
    chart_images.append(make_chart_image(fig))

    # ===== 5. LINHAS - Comentários =====
    c_val = analysis.get("comentarios_medios", 0)
    x_labels = ["Péssimo", "Regular", "Atual", "Bom", "Excelente"]
    y_vals = [c_val*0.2, c_val*0.5, c_val, c_val*1.5, c_val*3]
    fig, ax = plt.subplots(figsize=(5, 3), facecolor=dark_bg)
    ax.set_facecolor(dark_bg)
    ax.plot(x_labels, y_vals, '-o', color='#3B82F6', linewidth=2.5, markersize=7, markerfacecolor='#3B82F6')
    ax.fill_between(range(len(x_labels)), y_vals, alpha=0.15, color='#3B82F6')
    ax.axvline(x=2, color='#60A5FA', linestyle='--', alpha=0.5, linewidth=1)
    ax.set_title(f"5. Comentários Médios – {c_val}/post (Linhas)", color='white', fontsize=11, fontweight='bold', pad=10)
    ax.tick_params(colors=text_c, labelsize=8)
    ax.spines[:].set_visible(False)
    ax.grid(axis='y', color=grid_c, alpha=0.3)
    chart_images.append(make_chart_image(fig))

    # ===== 6. RADAR - Crescimento =====
    radar_labels = ["Crescimento", "Ganho 30d", "Freq. Posts", "Engajamento", "Curtidas", "Comentários"]
    cresc_score = scores["crescimento"]
    ganho_norm = min(10, analysis.get("ganho_seguidores_30d", 0) / max(seguidores * 0.01, 1))
    radar_values = [cresc_score, round(ganho_norm, 1), scores["posts"], scores["engajamento"], scores["curtidas"], scores["comentarios"]]
    angles = np.linspace(0, 2*np.pi, len(radar_labels), endpoint=False).tolist()
    radar_values_closed = radar_values + [radar_values[0]]
    angles_closed = angles + [angles[0]]
    fig, ax = plt.subplots(figsize=(5, 4), subplot_kw=dict(polar=True), facecolor=dark_bg)
    ax.set_facecolor(dark_bg)
    ax.plot(angles_closed, radar_values_closed, 'o-', color='#10B981', linewidth=2)
    ax.fill(angles_closed, radar_values_closed, alpha=0.25, color='#10B981')
    ax.set_thetagrids([a*180/np.pi for a in angles], radar_labels, color=text_c, fontsize=7)
    ax.set_ylim(0, 10)
    ax.set_rticks([2, 4, 6, 8, 10])
    ax.tick_params(axis='y', labelcolor='#6B7280', labelsize=6)
    ax.grid(color=grid_c, alpha=0.3)
    ax.set_title(f"6. Crescimento – {analysis.get('crescimento_pct',0)}% (Radar)", color='white', fontsize=11, fontweight='bold', pad=20)
    chart_images.append(make_chart_image(fig))

    # ===== 7. HISTOGRAMA - Posts =====
    hist_labels = ["0-4", "5-8", "9-16", "17-30", "30+"]
    hist_scores = [3, 5, 8, 9, 10]
    total_posts = analysis.get("posts_30d", 0)
    hist_colors = ['#475569']*5
    if total_posts <= 4: hist_colors[0] = '#EF4444'
    elif total_posts <= 8: hist_colors[1] = '#EF4444'
    elif total_posts <= 16: hist_colors[2] = '#EF4444'
    elif total_posts <= 30: hist_colors[3] = '#EF4444'
    else: hist_colors[4] = '#EF4444'
    fig, ax = plt.subplots(figsize=(5, 3), facecolor=dark_bg)
    ax.set_facecolor(dark_bg)
    ax.bar(hist_labels, hist_scores, color=hist_colors, width=0.6, edgecolor=dark_bg)
    ax.set_title(f"7. Posts 30d – {total_posts} posts (Histograma)", color='white', fontsize=11, fontweight='bold', pad=10)
    ax.set_ylabel("Score", color=text_c, fontsize=8)
    ax.set_ylim(0, 11)
    ax.tick_params(colors=text_c, labelsize=8)
    ax.spines[:].set_visible(False)
    ax.grid(axis='y', color=grid_c, alpha=0.3)
    chart_images.append(make_chart_image(fig))

    # ===== BUILD PDF =====
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm, leftMargin=15*mm, rightMargin=15*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=20, textColor=colors.HexColor('#1E293B'), spaceAfter=3*mm)
    subtitle_style = ParagraphStyle('S', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#64748B'), spaceAfter=6*mm)
    section_style = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#3B82F6'), spaceBefore=5*mm, spaceAfter=3*mm)
    footer_style = ParagraphStyle('F', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#94A3B8'), alignment=TA_CENTER)
    elements = []

    # ---- Header ----
    elements.append(Paragraph("RANKING RUN INSIDE", title_style))
    elements.append(Paragraph(f"Análise de Perfil Instagram — @{analysis.get('username', '')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1')))
    elements.append(Spacer(1, 4*mm))

    # ---- Identificação ----
    elements.append(Paragraph("Identificação", section_style))
    info_data = [
        ["Username", f"@{analysis.get('username', '')}"],
        ["Nome", analysis.get('nome_completo', '-')],
        ["Data", analysis.get('data_analise', '-')],
        ["Nota", f"{analysis.get('nota', '-')} ({analysis.get('nota_nivel', '')})"],
        ["Nota Calc.", analysis.get('nota_calc', '-')],
        ["Classif. SB", analysis.get('classificacao_sb', '-')],
        ["Classif. Seg.", analysis.get('classificacao_seguidores', '-')],
    ]
    t = Table(info_data, colWidths=[45*mm, 130*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F1F5F9')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t)

    # ---- Métricas + Crescimento + Interações (compacto) ----
    elements.append(Paragraph("Métricas Completas", section_style))
    all_metrics = [
        ["Métrica", "Valor", "Métrica", "Valor"],
        ["Seguidores", f"{analysis.get('seguidores',0):,}", "Seguindo", f"{analysis.get('seguindo',0):,}"],
        ["Total Posts", f"{analysis.get('total_posts',0):,}", "Engajamento", f"{analysis.get('engajamento_pct',0)}%"],
        ["Taxa Curtidas", f"{analysis.get('taxa_curtidas_pct',0)}%", "Crescimento", f"{analysis.get('crescimento_pct',0)}%"],
        ["Ganho 30d", f"+{analysis.get('ganho_seguidores_30d',0):,}", "Perda 30d", f"-{analysis.get('perda_seguidores_30d',0):,}"],
        ["Méd. Sem. Ganho", str(analysis.get('media_semanal_ganho',0)), "Méd. Sem. Perda", str(analysis.get('media_semanal_perda',0))],
        ["Posts 30d", str(analysis.get('posts_30d',0)), "Posts/Semana", str(analysis.get('media_semanal_posts',0))],
        ["Curtidas/Post", str(analysis.get('curtidas_medias',0)), "Coment./Post", str(analysis.get('comentarios_medios',0))],
        ["Views Reels", f"{analysis.get('media_views_reels',0):,}", "Saldo Seg.", f"{analysis.get('saldo_seguidores',0):,}"],
    ]
    t2 = Table(all_metrics, colWidths=[40*mm, 47*mm, 40*mm, 47*mm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (2,1), (2,-1), colors.HexColor('#F1F5F9')),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,1), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t2)

    # ---- Scores ----
    elements.append(Paragraph("Scores por Métrica", section_style))
    score_data = [
        ["Views", "Engaj.", "Curtidas", "Coment.", "Cresc.", "Posts", "MÉDIA"],
        [str(scores['views']), str(scores['engajamento']), str(scores['curtidas']),
         str(scores['comentarios']), str(scores['crescimento']), str(scores['posts']),
         str(scores['media'])],
    ]
    t3 = Table(score_data, colWidths=[25*mm]*7)
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#8B5CF6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9), ('FONTSIZE', (0,1), (-1,1), 14),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (-1,1), (-1,1), colors.HexColor('#EDE9FE')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t3)

    elements.append(PageBreak())

    # ---- 7 GRÁFICOS ----
    elements.append(Paragraph("Gráficos de Análise", title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1')))
    elements.append(Spacer(1, 3*mm))

    chart_w = 170*mm
    chart_h_small = 85*mm
    chart_h_radar = 110*mm

    for i, buf in enumerate(chart_images):
        h = chart_h_radar if i == 5 else chart_h_small
        elements.append(RLImage(buf, width=chart_w, height=h))
        elements.append(Spacer(1, 3*mm))
        if i == 2:
            elements.append(PageBreak())
        elif i == 4:
            elements.append(PageBreak())

    elements.append(PageBreak())

    # ---- TABELA NOTA REFERÊNCIA ----
    elements.append(Paragraph("Tabela de Referência – NOTA (A++ a F)", section_style))
    nota_ref_header = [["Nota", "Taxa de Curtidas", "Nível", "Score"]]
    nota_ref_data = [
        ["A++", "7%+", "Elite / Viral", "10"],
        ["A+", "6% – 6.99%", "Excelente", "9.5"],
        ["A", "5% – 5.99%", "Muito Forte", "9"],
        ["A-", "4.5% – 4.99%", "Forte+", "8.5"],
        ["B+", "4% – 4.49%", "Forte", "8"],
        ["B", "3.5% – 3.99%", "Boa", "7.5"],
        ["B-", "3% – 3.49%", "Boa-", "7"],
        ["C+", "2.5% – 2.99%", "Saudável", "6.5"],
        ["C", "2% – 2.49%", "Regular", "6"],
        ["C-", "1.5% – 1.99%", "Fraca", "5.5"],
        ["D+", "1% – 1.49%", "Muito Fraca", "5"],
        ["D", "0.5% – 0.99%", "Péssima", "4.5"],
        ["D-", "0.25% – 0.49%", "Crítica", "4"],
        ["F", "< 0.25%", "Inativa", "0"],
    ]
    nota_row_colors = [
        '#4ADE80','#22D3EE','#FACC15','#A3E635','#A855F7','#EC4899','#F472B6',
        '#9CA3AF','#D97706','#B45309','#475569','#1E293B','#7F1D1D','#DC2626'
    ]
    nota_text_colors = [
        '#000','#000','#000','#000','#fff','#000','#000',
        '#000','#000','#fff','#fff','#fff','#fff','#fff'
    ]
    t_nota = Table(nota_ref_header + nota_ref_data, colWidths=[25*mm, 45*mm, 50*mm, 25*mm])
    style_cmds = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]
    for idx, (bg, tc) in enumerate(zip(nota_row_colors, nota_text_colors)):
        row = idx + 1
        style_cmds.append(('BACKGROUND', (0, row), (-1, row), colors.HexColor(bg)))
        style_cmds.append(('TEXTCOLOR', (0, row), (-1, row), colors.HexColor(tc)))
    t_nota.setStyle(TableStyle(style_cmds))
    elements.append(t_nota)
    elements.append(Spacer(1, 8*mm))

    # ---- TABELA CLASSIFICAÇÃO + SCORE ----
    elements.append(Paragraph("Tabela de Referência – CLASSIFICAÇÃO + SCORE", section_style))
    classif_data = [
        ["Crescimento (%)", "Classificação", "Score"],
        ["< 1%", "Péssimo", "1–4"],
        ["1% – 3%", "Regular (Fraco)", "5–6"],
        ["3% – 6%", "Bom", "7–8"],
        ["6% – 10%", "Ótimo (Muito bom)", "9"],
        ["> 10%", "Excelente", "10"],
    ]
    classif_row_colors = ['#0F172A', '#F87171', '#FB923C', '#FACC15', '#34D399', '#60A5FA']
    t_classif = Table(classif_data, colWidths=[50*mm, 55*mm, 40*mm])
    classif_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#94A3B8')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#334155')),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]
    for idx, bg in enumerate(classif_row_colors[1:], 1):
        classif_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#1E293B')))
        classif_style.append(('TEXTCOLOR', (0, idx), (-1, idx), colors.white))
    t_classif.setStyle(TableStyle(classif_style))
    elements.append(t_classif)

    # ---- Footer ----
    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1')))
    elements.append(Paragraph(f"Ranking Run Inside — Relatório gerado automaticamente — {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}", footer_style))

    doc.build(elements)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=analise_{analysis['username']}.pdf"
        }
    )



# ==================== UPLOAD FOTO DE PERFIL INSIDE ====================

@router.post("/admin/instagram/upload-foto")
async def upload_foto_inside(foto: UploadFile = File(...), admin: dict = Depends(get_admin_user)):
    """Upload de foto de perfil para análise Inside"""
    from services.object_storage import upload_file as cloud_upload
    content = await foto.read()
    result = cloud_upload(content, foto.filename or "inside.jpg", pasta="inside")
    return {"foto_url": result["url"]}


# ==================== ANÁLISE COMPLETA MANUAL (SOCIAL BLADE) ====================

@router.post("/admin/instagram/analisar-simplificado")
async def analisar_perfil_simplificado(dados: dict, admin: dict = Depends(get_admin_user)):
    """
    Análise completa com todos os campos manuais. 
    Calcula fórmulas e gera scores para 7 métricas com gráficos.
    """
    username = dados.get("username", "").strip().replace("@", "")
    if not username:
        raise HTTPException(status_code=400, detail="Username é obrigatório")

    # Campos manuais
    seguidores = max(int(dados.get("seguidores", 0)), 1)
    seguindo = int(dados.get("seguindo", 0))
    total_posts = int(dados.get("total_posts", 0))
    nota_manual = dados.get("nota", "C")
    classificacao_sb = dados.get("classificacao_sb", "")
    classificacao_seguidores = dados.get("classificacao_seguidores", "")
    ganho_seg_30d = int(dados.get("ganho_seguidores_30d", 0))
    perda_seg_30d = int(dados.get("perda_seguidores_30d", 0))
    media_semanal_ganho = float(dados.get("media_semanal_ganho", 0))
    media_semanal_perda = float(dados.get("media_semanal_perda", 0))
    posts_30d = int(dados.get("posts_30d", 0))
    media_semanal_posts = float(dados.get("media_semanal_posts", 0))
    views_reels_6 = int(dados.get("views_reels_6", 0))
    curtidas_medias = float(dados.get("curtidas_medias", 0))
    comentarios_medios = float(dados.get("comentarios_medios", 0))
    nome_completo = dados.get("nome_completo", "")
    data_analise = dados.get("data_analise", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    foto_url = dados.get("foto_url", "")

    # ==================== FÓRMULA 1: NOTA (Taxa de Curtidas) ====================
    taxa_curtidas_pct = round((curtidas_medias / seguidores) * 100, 2)
    
    nota_nivel_map = {
        "A++": "Elite / Viral", "A+": "Excelente", "A": "Muito Forte",
        "B+": "Forte", "B": "Boa", "C+": "Saudável", "C": "Fraca",
        "D": "Muito fraca", "E": "Péssima", "F": "Péssima"
    }
    # Nota calculada pela taxa de curtidas
    if taxa_curtidas_pct >= 7: nota_calc = "A++"
    elif taxa_curtidas_pct >= 6: nota_calc = "A+"
    elif taxa_curtidas_pct >= 5: nota_calc = "A"
    elif taxa_curtidas_pct >= 4: nota_calc = "B+"
    elif taxa_curtidas_pct >= 3: nota_calc = "B"
    elif taxa_curtidas_pct >= 2: nota_calc = "C+"
    elif taxa_curtidas_pct >= 1: nota_calc = "C"
    elif taxa_curtidas_pct >= 0.5: nota_calc = "D"
    else: nota_calc = "E"
    
    nota_nivel = nota_nivel_map.get(nota_manual, "")

    # ==================== FÓRMULA 2: VIEWS DE REELS ====================
    media_views_reels = round(views_reels_6 / 6, 1) if views_reels_6 > 0 else 0
    taxa_views_pct = round((media_views_reels / seguidores) * 100, 2) if seguidores > 0 else 0
    
    if taxa_views_pct > 120: views_metrica, views_score = "Excelente", 10
    elif taxa_views_pct >= 70: views_metrica, views_score = "Ótimo", 9
    elif taxa_views_pct >= 30: views_metrica, views_score = "Bom", 8
    elif taxa_views_pct >= 10: views_metrica, views_score = "Regular", 6
    else: views_metrica, views_score = "Péssimo", 3

    # ==================== FÓRMULA 3: TAXA DE ENGAJAMENTO ====================
    engajamento_pct = round(((curtidas_medias + comentarios_medios) / seguidores) * 100, 2)
    
    if engajamento_pct > 6: eng_metrica, eng_score = "Excelente", 10
    elif engajamento_pct >= 4: eng_metrica, eng_score = "Ótimo", 9
    elif engajamento_pct >= 2: eng_metrica, eng_score = "Bom", 8
    elif engajamento_pct >= 1: eng_metrica, eng_score = "Regular", 6
    else: eng_metrica, eng_score = "Péssimo", 3

    # ==================== FÓRMULA 4: CURTIDAS MÉDIAS ====================
    if taxa_curtidas_pct > 10: curt_metrica, curt_score = "Excelente", 10
    elif taxa_curtidas_pct >= 6: curt_metrica, curt_score = "Ótimo", 9
    elif taxa_curtidas_pct >= 3: curt_metrica, curt_score = "Bom", 8
    elif taxa_curtidas_pct >= 1: curt_metrica, curt_score = "Regular", 6
    else: curt_metrica, curt_score = "Péssimo", 3

    # ==================== FÓRMULA 5: COMENTÁRIOS MÉDIOS ====================
    taxa_comentarios_pct = round((comentarios_medios / seguidores) * 100, 3)
    
    if taxa_comentarios_pct > 0.6: coment_metrica, coment_score = "Excelente", 10
    elif taxa_comentarios_pct >= 0.3: coment_metrica, coment_score = "Ótimo", 9
    elif taxa_comentarios_pct >= 0.1: coment_metrica, coment_score = "Bom", 8
    elif taxa_comentarios_pct >= 0.05: coment_metrica, coment_score = "Regular", 6
    else: coment_metrica, coment_score = "Péssimo", 3

    # ==================== FÓRMULA 6: CRESCIMENTO MENSAL ====================
    crescimento_pct = round((ganho_seg_30d / seguidores) * 100, 2)
    
    if crescimento_pct > 10: cresc_metrica, cresc_score = "Excelente", 10
    elif crescimento_pct >= 6: cresc_metrica, cresc_score = "Ótimo", 9
    elif crescimento_pct >= 3: cresc_metrica, cresc_score = "Bom", 8
    elif crescimento_pct >= 1: cresc_metrica, cresc_score = "Regular", 6
    else: cresc_metrica, cresc_score = "Péssimo", 3

    # ==================== FÓRMULA 7: POSTS (30 DIAS) ====================
    if posts_30d > 30: posts_metrica, posts_score = "Excelente", 10
    elif posts_30d >= 17: posts_metrica, posts_score = "Ótimo", 9
    elif posts_30d >= 9: posts_metrica, posts_score = "Bom", 8
    elif posts_30d >= 5: posts_metrica, posts_score = "Regular", 6
    else: posts_metrica, posts_score = "Péssimo", 3

    saldo_seguidores = ganho_seg_30d - perda_seg_30d

    # ==================== DADOS PARA GRÁFICOS ====================
    graficos_data = {
        # 1. Gauge/Círculo - NOTA
        "nota_gauge": {
            "nota": nota_manual,
            "nota_calc": nota_calc,
            "nivel": nota_nivel,
            "taxa_curtidas_pct": taxa_curtidas_pct
        },
        # 2. Barras horizontais - VIEWS DE REELS
        "views_reels": {
            "media_views": media_views_reels,
            "taxa_views_pct": taxa_views_pct,
            "metrica": views_metrica,
            "score": views_score,
            "escala": [
                {"label": "< 10%", "range": "Péssimo", "min": 0, "max": 10},
                {"label": "10-30%", "range": "Regular", "min": 10, "max": 30},
                {"label": "30-70%", "range": "Bom", "min": 30, "max": 70},
                {"label": "70-120%", "range": "Ótimo", "min": 70, "max": 120},
                {"label": "> 120%", "range": "Excelente", "min": 120, "max": 200}
            ]
        },
        # 3. Pizza - ENGAJAMENTO
        "engajamento": {
            "taxa": engajamento_pct,
            "metrica": eng_metrica,
            "score": eng_score,
            "labels": ["Curtidas Médias", "Comentários Médios"],
            "values": [curtidas_medias, comentarios_medios]
        },
        # 4. Colunas - CURTIDAS MÉDIAS
        "curtidas": {
            "valor": curtidas_medias,
            "taxa": taxa_curtidas_pct,
            "metrica": curt_metrica,
            "score": curt_score
        },
        # 5. Linhas - COMENTÁRIOS MÉDIOS
        "comentarios": {
            "valor": comentarios_medios,
            "taxa": taxa_comentarios_pct,
            "metrica": coment_metrica,
            "score": coment_score
        },
        # 6. Radar - CRESCIMENTO MENSAL
        "crescimento": {
            "taxa": crescimento_pct,
            "metrica": cresc_metrica,
            "score": cresc_score,
            "saldo": saldo_seguidores,
            "radar_labels": ["Crescimento %", "Ganho 30d", "Frequência Posts", "Engajamento", "Curtidas", "Comentários"],
            "radar_values": [cresc_score, min(10, ganho_seg_30d / max(seguidores * 0.01, 1)), posts_score, eng_score, curt_score, coment_score]
        },
        # 7. Histograma - POSTS (30 DIAS)
        "posts": {
            "total": posts_30d,
            "metrica": posts_metrica,
            "score": posts_score,
            "semanal": media_semanal_posts,
            "escala": [
                {"label": "0-4", "range": "Péssimo", "score": "1-4"},
                {"label": "5-8", "range": "Regular", "score": "5-6"},
                {"label": "9-16", "range": "Bom", "score": "7-8"},
                {"label": "17-30", "range": "Ótimo", "score": "9"},
                {"label": "30+", "range": "Excelente", "score": "10"}
            ]
        },
        # Score geral (média dos 7 scores, exceto nota que é manual)
        "scores": {
            "views": views_score,
            "engajamento": eng_score,
            "curtidas": curt_score,
            "comentarios": coment_score,
            "crescimento": cresc_score,
            "posts": posts_score,
            "media": round((views_score + eng_score + curt_score + coment_score + cresc_score + posts_score) / 6, 1)
        }
    }

    graficos_data["crescimento"]["radar_values"] = [round(v, 1) for v in graficos_data["crescimento"]["radar_values"]]

    # ==================== MONTAR RESULTADO ====================
    analysis_id = str(uuid.uuid4())
    analysis = {
        "id": analysis_id,
        "username": username,
        "nome_completo": nome_completo,
        "foto_url": foto_url,
        "tipo": "social_blade",
        "data_analise": data_analise,
        # Dados de entrada
        "seguidores": seguidores, "seguindo": seguindo, "total_posts": total_posts,
        "nota": nota_manual, "classificacao_sb": classificacao_sb,
        "classificacao_seguidores": classificacao_seguidores,
        "ganho_seguidores_30d": ganho_seg_30d, "perda_seguidores_30d": perda_seg_30d,
        "media_semanal_ganho": media_semanal_ganho, "media_semanal_perda": media_semanal_perda,
        "posts_30d": posts_30d, "media_semanal_posts": media_semanal_posts,
        "views_reels_6": views_reels_6, "curtidas_medias": curtidas_medias,
        "comentarios_medios": comentarios_medios,
        # Métricas calculadas
        "nota_calc": nota_calc, "nota_nivel": nota_nivel,
        "engajamento_pct": engajamento_pct, "taxa_curtidas_pct": taxa_curtidas_pct,
        "taxa_comentarios_pct": taxa_comentarios_pct, "taxa_views_pct": taxa_views_pct,
        "media_views_reels": media_views_reels, "crescimento_pct": crescimento_pct,
        "saldo_seguidores": saldo_seguidores,
        # Scores
        "views_score": views_score, "eng_score": eng_score, "curt_score": curt_score,
        "coment_score": coment_score, "cresc_score": cresc_score, "posts_score": posts_score,
        "score_medio": graficos_data["scores"]["media"],
        "score_final": graficos_data["scores"]["media"] * 10,
        # Meta
        "classificacao": classificacao_sb or nota_manual,
        "analisado_por": admin.get("id"),
        "analisado_por_nome": admin.get("nome", ""),
    }

    await db.instagram_analyses.insert_one({**analysis})

    return {
        "analysis": {k: v for k, v in analysis.items() if k != "_id"},
        "graficos_data": graficos_data
    }


# ==================== ESTATÍSTICAS ====================

@router.get("/admin/instagram/stats")
async def get_instagram_stats(admin: dict = Depends(get_admin_user)):
    """Estatísticas gerais das análises de Instagram"""
    
    total_analises = await db.instagram_analyses.count_documents({})
    
    pipeline = [
        {"$group": {
            "_id": None,
            "media_score": {"$avg": "$score_final"},
            "media_engagement": {"$avg": "$engagement_rate"}
        }}
    ]
    
    result = await db.instagram_analyses.aggregate(pipeline).to_list(1)
    
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
