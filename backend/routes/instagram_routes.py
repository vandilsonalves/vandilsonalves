# /app/backend/routes/instagram_routes.py
# Módulo Instagram - Ranking Run Inside (Análise de perfis Instagram)
# Consolidado de server.py + rotas existentes

from fastapi import APIRouter, HTTPException, Depends, Form
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
    
    # Se for análise tipo Social Blade, gerar gráficos com os dados calculados
    if analysis.get("tipo") == "social_blade":
        seguidores = max(analysis.get("seguidores", 1), 1)
        graficos_data = {
            "radar": {
                "labels": ["Engajamento", "Curtidas", "Comentários", "Crescimento", "Frequência", "Consistência"],
                "values": [
                    min(10, analysis.get("engajamento_pct", 0) * 2),
                    min(10, analysis.get("taxa_curtidas_pct", 0) * 2),
                    min(10, (analysis.get("comentarios_medios", 0) / max(analysis.get("curtidas_medias", 1), 1)) * 50),
                    min(10, analysis.get("crescimento_pct", 0)),
                    min(10, analysis.get("posts_semanais", 0) * 1.5),
                    min(10, min(analysis.get("posts_30d", 0), 30) / 3)
                ]
            },
            "barras_metricas": {
                "labels": ["Engajamento %", "Taxa Curtidas %", "Crescimento %", "Posts/Semana"],
                "values": [
                    analysis.get("engajamento_pct", 0),
                    analysis.get("taxa_curtidas_pct", 0),
                    analysis.get("crescimento_pct", 0),
                    analysis.get("posts_semanais", 0)
                ]
            },
            "pizza_distribuicao": {
                "labels": ["Curtidas", "Comentários"],
                "values": [analysis.get("curtidas_30d", 0), analysis.get("comentarios_30d", 0)]
            },
            "crescimento_semanal": {
                "labels": ["Semana 1", "Semana 2", "Semana 3", "Semana 4"],
                "ganho": [round(analysis.get("ganho_semanal", 0) * x) for x in [0.9, 1.1, 0.95, 1.05]],
                "perda": [round(analysis.get("perda_semanal", 0) * x) for x in [1.1, 0.9, 1.05, 0.95]]
            }
        }
        graficos_data["radar"]["values"] = [round(v, 1) for v in graficos_data["radar"]["values"]]
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


# ==================== ANÁLISE SIMPLIFICADA ====================

@router.post("/admin/instagram/analisar-simplificado")
async def analisar_perfil_simplificado(dados: dict, admin: dict = Depends(get_admin_user)):
    """
    Análise completa estilo Social Blade com dados manuais.
    Campos de entrada:
      - username, nome_completo, nicho
      - seguidores, seguindo, total_posts
      - curtidas_30d, comentarios_30d
      - ganho_seguidores_30d, perda_seguidores_30d
      - posts_30d
    Calcula automaticamente todas as métricas, classificações e gráficos.
    """
    username = dados.get("username", "").strip().replace("@", "")
    if not username:
        raise HTTPException(status_code=400, detail="Username é obrigatório")

    seguidores = max(int(dados.get("seguidores", 0)), 1)
    seguindo = int(dados.get("seguindo", 0))
    total_posts = int(dados.get("total_posts", 0))
    curtidas_30d = int(dados.get("curtidas_30d", 0))
    comentarios_30d = int(dados.get("comentarios_30d", 0))
    ganho_seg_30d = int(dados.get("ganho_seguidores_30d", 0))
    perda_seg_30d = int(dados.get("perda_seguidores_30d", 0))
    posts_30d = max(int(dados.get("posts_30d", 0)), 1)
    nome_completo = dados.get("nome_completo", "")
    nicho = dados.get("nicho", "corrida")
    bio = dados.get("bio", "")

    # ==================== CÁLCULOS AUTOMÁTICOS ====================
    
    # Engajamento geral
    engajamento_pct = round(((curtidas_30d + comentarios_30d) / seguidores) * 100, 2)
    
    # Taxa de curtidas
    taxa_curtidas_pct = round((curtidas_30d / seguidores) * 100, 2)
    
    # Curtidas e comentários médios por post
    curtidas_medias = round(curtidas_30d / posts_30d, 1)
    comentarios_medios = round(comentarios_30d / posts_30d, 1)
    
    # Crescimento
    saldo_seguidores = ganho_seg_30d - perda_seg_30d
    crescimento_pct = round((saldo_seguidores / seguidores) * 100, 2)
    
    # Médias semanais
    ganho_semanal = round(ganho_seg_30d / 4, 1)
    perda_semanal = round(perda_seg_30d / 4, 1)
    posts_semanais = round(posts_30d / 4, 1)
    
    # Ratio seguindo/seguidores
    ratio_seg = round(seguindo / seguidores, 3) if seguidores > 0 else 0

    # ==================== NOTA (ESTILO SOCIAL BLADE) ====================
    if taxa_curtidas_pct >= 8: nota = "A++"
    elif taxa_curtidas_pct >= 6: nota = "A+"
    elif taxa_curtidas_pct >= 5: nota = "A"
    elif taxa_curtidas_pct >= 4: nota = "A-"
    elif taxa_curtidas_pct >= 3: nota = "B+"
    elif taxa_curtidas_pct >= 2.5: nota = "B"
    elif taxa_curtidas_pct >= 2: nota = "B-"
    elif taxa_curtidas_pct >= 1.5: nota = "C+"
    elif taxa_curtidas_pct >= 1: nota = "C"
    elif taxa_curtidas_pct >= 0.8: nota = "C-"
    elif taxa_curtidas_pct >= 0.5: nota = "D+"
    elif taxa_curtidas_pct >= 0.3: nota = "D"
    elif taxa_curtidas_pct >= 0.1: nota = "D-"
    else: nota = "F"

    # ==================== CLASSIFICAÇÃO SB ====================
    score_sb = round((taxa_curtidas_pct * 10) + (crescimento_pct * 5), 2)
    if score_sb >= 90: classificacao_sb = "A+"
    elif score_sb >= 80: classificacao_sb = "A"
    elif score_sb >= 70: classificacao_sb = "B+"
    elif score_sb >= 60: classificacao_sb = "B"
    elif score_sb >= 50: classificacao_sb = "C+"
    elif score_sb >= 40: classificacao_sb = "C"
    elif score_sb >= 30: classificacao_sb = "D"
    else: classificacao_sb = "E"

    # ==================== CLASSIFICAÇÃO DE SEGUIDORES ====================
    if crescimento_pct > 10: classif_seguidores = "Excelente"
    elif crescimento_pct >= 5: classif_seguidores = "Bom"
    elif crescimento_pct >= 1: classif_seguidores = "Normal"
    else: classif_seguidores = "Fraco"

    # ==================== CLASSIFICAÇÃO DE CRESCIMENTO ====================
    if crescimento_pct > 10: crescimento_label = "Excelente"
    elif crescimento_pct >= 6: crescimento_label = "Muito bom"
    elif crescimento_pct >= 3: crescimento_label = "Ok"
    elif crescimento_pct >= 1: crescimento_label = "Fraco"
    else: crescimento_label = "Péssimo"

    # ==================== CLASSIFICAÇÃO DE CURTIDAS ====================
    if taxa_curtidas_pct > 6: curtidas_label = "Excelente"
    elif taxa_curtidas_pct >= 4: curtidas_label = "Ótima"
    elif taxa_curtidas_pct >= 2: curtidas_label = "Boa"
    elif taxa_curtidas_pct >= 1: curtidas_label = "Ruim"
    else: curtidas_label = "Péssima"

    # ==================== SELO ====================
    if nota in ("A++", "A+"): selo = "Elite"
    elif nota in ("A", "A-", "B+"): selo = "Destaque"
    elif nota in ("B", "B-"): selo = "Forte"
    elif nota in ("C+", "C"): selo = "Em crescimento"
    else: selo = "Baixo desempenho"

    # ==================== DADOS PARA GRÁFICOS ====================
    graficos_data = {
        "radar": {
            "labels": ["Engajamento", "Curtidas", "Comentários", "Crescimento", "Frequência", "Consistência"],
            "values": [
                min(10, engajamento_pct * 2),
                min(10, taxa_curtidas_pct * 2),
                min(10, (comentarios_medios / max(curtidas_medias, 1)) * 50),
                min(10, crescimento_pct),
                min(10, posts_semanais * 1.5),
                min(10, min(posts_30d, 30) / 3)
            ]
        },
        "barras_metricas": {
            "labels": ["Engajamento %", "Taxa Curtidas %", "Crescimento %", "Posts/Semana"],
            "values": [engajamento_pct, taxa_curtidas_pct, crescimento_pct, posts_semanais]
        },
        "pizza_distribuicao": {
            "labels": ["Curtidas", "Comentários"],
            "values": [curtidas_30d, comentarios_30d]
        },
        "crescimento_semanal": {
            "labels": ["Semana 1", "Semana 2", "Semana 3", "Semana 4"],
            "ganho": [round(ganho_semanal * 0.9), round(ganho_semanal * 1.1), round(ganho_semanal * 0.95), round(ganho_semanal * 1.05)],
            "perda": [round(perda_semanal * 1.1), round(perda_semanal * 0.9), round(perda_semanal * 1.05), round(perda_semanal * 0.95)]
        }
    }

    # Round radar values
    graficos_data["radar"]["values"] = [round(v, 1) for v in graficos_data["radar"]["values"]]

    # ==================== MONTAR RESULTADO ====================
    analysis_id = str(uuid.uuid4())
    analysis = {
        "id": analysis_id,
        "username": username,
        "nome_completo": nome_completo,
        "nicho": nicho,
        "bio": bio,
        "tipo": "social_blade",
        # Dados de entrada
        "seguidores": seguidores,
        "seguindo": seguindo,
        "total_posts": total_posts,
        "curtidas_30d": curtidas_30d,
        "comentarios_30d": comentarios_30d,
        "ganho_seguidores_30d": ganho_seg_30d,
        "perda_seguidores_30d": perda_seg_30d,
        "posts_30d": posts_30d,
        # Métricas calculadas
        "engajamento_pct": engajamento_pct,
        "taxa_curtidas_pct": taxa_curtidas_pct,
        "curtidas_medias": curtidas_medias,
        "comentarios_medios": comentarios_medios,
        "crescimento_pct": crescimento_pct,
        "saldo_seguidores": saldo_seguidores,
        "ganho_semanal": ganho_semanal,
        "perda_semanal": perda_semanal,
        "posts_semanais": posts_semanais,
        "ratio_seguindo_seguidores": ratio_seg,
        # Classificações
        "nota": nota,
        "classificacao_sb": classificacao_sb,
        "score_sb": score_sb,
        "classificacao_seguidores": classif_seguidores,
        "crescimento_label": crescimento_label,
        "curtidas_label": curtidas_label,
        "selo": selo,
        # Meta
        "score_final": score_sb,
        "classificacao": classificacao_sb,
        "data_analise": datetime.now(timezone.utc).isoformat(),
        "analisado_por": admin.get("id"),
        "analisado_por_nome": admin.get("nome", ""),
    }

    await db.instagram_analyses.insert_one({**analysis})

    return {
        "analysis": {k: v for k, v in analysis.items() if k != "_id"},
        "graficos_data": graficos_data,
        "recomendacoes": []
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
