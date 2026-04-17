# /app/backend/routes/feed_routes.py
# Feed Social da plataforma com sistema de reações e posts automáticos de conquistas

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import uuid
from pathlib import Path
from io import BytesIO
from PIL import Image as PILImage

from config import db
from routes.auth_routes import get_current_user, require_premium_access
from services.moderacao_service import (
    analisar_conteudo, NivelInfracao, registrar_infracao,
    verificar_usuario_bloqueado, bloquear_usuario_temporariamente,
    incrementar_comentarios_aprovados, verificar_selo_respeitoso,
    calcular_score_respeito, gerar_feedback_educativo
)

router = APIRouter()

UPLOAD_DIR = Path("/app/uploads/feed")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Reações disponíveis
REACOES_DISPONIVEIS = {
    "aplausos": {"emoji": "👏", "nome": "Aplausos"},
    "corrida": {"emoji": "🏃", "nome": "Correndo"},
    "forca": {"emoji": "💪", "nome": "Força"},
    "fogo": {"emoji": "🔥", "nome": "Em chamas"},
    "coracao": {"emoji": "❤️", "nome": "Amei"},
    "festa": {"emoji": "🎉", "nome": "Celebrando"},
    "trofeu": {"emoji": "🏆", "nome": "Campeão"},
    "parabens": {"emoji": "🎊", "nome": "Parabéns"}
}

# Tipos de post
TIPOS_POST = ["texto", "resultado", "conquista", "corrida_aprovada"]


class PostCreate(BaseModel):
    texto: str
    tipo: str = "texto"  # texto, resultado, conquista, foto
    resultado_id: Optional[str] = None
    conquista_id: Optional[str] = None


class ReacaoCreate(BaseModel):
    tipo_reacao: str  # aplausos, corrida, forca, fogo, coracao, festa, trofeu


class ComentarioCreate(BaseModel):
    texto: str


MAX_FOTOS_DIA = 2
MAX_FOTO_SIZE_MB = 5
MAX_STORIES_DIA = 1
EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}

STORIES_DIR = Path("/app/uploads/stories")
STORIES_DIR.mkdir(parents=True, exist_ok=True)

MAX_IMG_WIDTH = 1200  # largura máxima em pixels
MAX_IMG_HEIGHT = 1200
JPEG_QUALITY = 82


def _comprimir_imagem(conteudo: bytes, ext: str) -> tuple[bytes, str]:
    """Redimensiona e comprime a imagem para tamanho adequado."""
    try:
        img = PILImage.open(BytesIO(conteudo))

        # Converter RGBA/palette para RGB
        if img.mode in ('RGBA', 'P', 'LA'):
            bg = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA' or (img.mode == 'P' and 'transparency' in img.info):
                bg.paste(img, mask=img.convert('RGBA').split()[-1])
            else:
                bg.paste(img)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Corrigir orientação EXIF
        try:
            from PIL import ExifTags
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif and orientation in exif:
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)
        except Exception:
            pass

        # Redimensionar se necessário
        w, h = img.size
        if w > MAX_IMG_WIDTH or h > MAX_IMG_HEIGHT:
            ratio = min(MAX_IMG_WIDTH / w, MAX_IMG_HEIGHT / h)
            new_size = (int(w * ratio), int(h * ratio))
            img = img.resize(new_size, PILImage.LANCZOS)

        # Salvar como JPEG comprimido
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        return buffer.getvalue(), '.jpg'
    except Exception:
        # Se falhar a compressão, retorna original
        return conteudo, ext


async def _contar_fotos_hoje(usuario_id: str) -> int:
    """Conta quantas fotos o usuário postou nas últimas 24h"""
    data_limite = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    return await db.feed_posts.count_documents({
        "autor_id": usuario_id,
        "tipo": "foto",
        "status": "ativo",
        "data_criacao": {"$gte": data_limite}
    })


async def _contar_stories_hoje(usuario_id: str) -> int:
    """Conta quantos stories o usuário postou nas últimas 24h"""
    data_limite = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    return await db.stories.count_documents({
        "autor_id": usuario_id,
        "data_criacao": {"$gte": data_limite}
    })


@router.get("/feed")
async def get_feed(
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=50),
    tipo: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Retorna o feed social do usuário"""
    
    skip = (pagina - 1) * limite
    
    # Filtro base
    filtro = {"status": "ativo"}
    if tipo:
        filtro["tipo"] = tipo
    
    # Buscar posts
    posts = await db.feed_posts.find(
        filtro,
        {"_id": 0}
    ).sort("data_criacao", -1).skip(skip).limit(limite).to_list(limite)
    
    # Enriquecer com dados dos autores e reações
    for post in posts:
        # Dados do autor
        autor = await db.usuarios.find_one(
            {"id": post["autor_id"]},
            {"_id": 0, "id": 1, "nome": 1, "foto_url": 1, "equipe": 1, "cidade": 1}
        )
        post["autor"] = autor
        
        # Buscar todas as reações do post
        reacoes_pipeline = [
            {"$match": {"post_id": post["id"]}},
            {"$group": {"_id": "$tipo_reacao", "count": {"$sum": 1}}}
        ]
        reacoes_agrupadas = await db.feed_reacoes.aggregate(reacoes_pipeline).to_list(None)
        
        # Formatar reações com emojis
        post["reacoes"] = {}
        post["total_reacoes"] = 0
        for r in reacoes_agrupadas:
            tipo_reacao = r["_id"]
            if tipo_reacao in REACOES_DISPONIVEIS:
                post["reacoes"][tipo_reacao] = {
                    "count": r["count"],
                    "emoji": REACOES_DISPONIVEIS[tipo_reacao]["emoji"],
                    "nome": REACOES_DISPONIVEIS[tipo_reacao]["nome"]
                }
                post["total_reacoes"] += r["count"]
        
        # Verificar qual reação o usuário atual fez (se houver)
        minha_reacao = await db.feed_reacoes.find_one({
            "post_id": post["id"],
            "usuario_id": current_user["id"]
        })
        post["minha_reacao"] = minha_reacao["tipo_reacao"] if minha_reacao else None
        
        # Contagem de comentários
        post["total_comentarios"] = await db.feed_comentarios.count_documents({"post_id": post["id"]})
        
        # Últimos 3 comentários
        comentarios = await db.feed_comentarios.find(
            {"post_id": post["id"]},
            {"_id": 0}
        ).sort([("fixado", -1), ("data_criacao", -1)]).limit(3).to_list(3)
        
        for com in comentarios:
            com_autor = await db.usuarios.find_one(
                {"id": com["autor_id"]},
                {"_id": 0, "id": 1, "nome": 1, "foto_url": 1}
            )
            com["autor"] = com_autor
            # Garantir que o campo fixado existe
            if "fixado" not in com:
                com["fixado"] = False
        
        # Ordenar: fixados primeiro, depois por data
        comentarios_ordenados = sorted(comentarios, key=lambda x: (not x.get("fixado", False), x.get("data_criacao", "")))
        post["comentarios_preview"] = comentarios_ordenados
    
    # Total de posts
    total = await db.feed_posts.count_documents(filtro)
    
    return {
        "posts": posts,
        "pagina": pagina,
        "limite": limite,
        "total": total,
        "total_paginas": (total + limite - 1) // limite,
        "reacoes_disponiveis": REACOES_DISPONIVEIS
    }


@router.get("/feed/meus-posts")
async def get_meus_posts(
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Retorna os posts do usuário logado"""
    
    skip = (pagina - 1) * limite
    
    posts = await db.feed_posts.find(
        {"autor_id": current_user["id"], "status": "ativo"},
        {"_id": 0}
    ).sort("data_criacao", -1).skip(skip).limit(limite).to_list(limite)
    
    # Enriquecer posts com reações
    for post in posts:
        reacoes_pipeline = [
            {"$match": {"post_id": post["id"]}},
            {"$group": {"_id": "$tipo_reacao", "count": {"$sum": 1}}}
        ]
        reacoes_agrupadas = await db.feed_reacoes.aggregate(reacoes_pipeline).to_list(None)
        
        post["reacoes"] = {}
        post["total_reacoes"] = 0
        for r in reacoes_agrupadas:
            tipo_reacao = r["_id"]
            if tipo_reacao in REACOES_DISPONIVEIS:
                post["reacoes"][tipo_reacao] = {
                    "count": r["count"],
                    "emoji": REACOES_DISPONIVEIS[tipo_reacao]["emoji"]
                }
                post["total_reacoes"] += r["count"]
    
    total = await db.feed_posts.count_documents({"autor_id": current_user["id"], "status": "ativo"})
    
    return {
        "posts": posts,
        "total": total
    }


@router.post("/feed/posts")
async def criar_post(
    dados: PostCreate,
    current_user: dict = Depends(require_premium_access)
):
    """Cria um novo post no feed"""
    
    if not dados.texto.strip():
        raise HTTPException(status_code=400, detail="O texto do post não pode estar vazio")
    
    if len(dados.texto) > 1000:
        raise HTTPException(status_code=400, detail="O texto do post não pode ter mais de 1000 caracteres")
    
    # MODERAÇÃO: Verificar se o usuário está bloqueado
    bloqueado, data_desbloqueio = await verificar_usuario_bloqueado(db, current_user["id"])
    if bloqueado:
        raise HTTPException(
            status_code=403, 
            detail=f"Você está temporariamente bloqueado de postar até {data_desbloqueio[:10]}."
        )
    
    # MODERAÇÃO: Analisar conteúdo do post
    bloqueado_mod, categoria, nivel, mensagem_feedback = analisar_conteudo(dados.texto)
    
    if bloqueado_mod and nivel:
        # Registrar infração
        await registrar_infracao(db, current_user["id"], nivel, categoria, dados.texto)
        
        # Gerar feedback educativo
        feedback_educativo = gerar_feedback_educativo(nivel, categoria)
        
        raise HTTPException(
            status_code=400,
            detail={
                "message": mensagem_feedback,
                "nivel": nivel.value,
                "categoria": categoria,
                "educativo": feedback_educativo
            }
        )
    
    # Se for post de resultado, buscar dados do resultado
    resultado_dados = None
    if dados.tipo == "resultado" and dados.resultado_id:
        resultado_dados = await db.resultados.find_one(
            {"id": dados.resultado_id},
            {"_id": 0}
        )
    
    # Se for post de conquista, buscar dados da conquista
    conquista_dados = None
    if dados.tipo == "conquista" and dados.conquista_id:
        conquista_dados = await db.conquistas_atleta.find_one(
            {"id": dados.conquista_id},
            {"_id": 0}
        )
    
    post = {
        "id": str(uuid.uuid4()),
        "autor_id": current_user["id"],
        "autor_nome": current_user.get("nome", ""),
        "texto": dados.texto.strip(),
        "tipo": dados.tipo,
        "resultado_dados": resultado_dados,
        "conquista_dados": conquista_dados,
        "imagem_url": None,
        "status": "ativo",
        "data_criacao": datetime.now(timezone.utc).isoformat()
    }
    
    await db.feed_posts.insert_one(post)
    
    return {
        "message": "Post criado com sucesso!",
        "post_id": post["id"]
    }


# Endpoint de upload de foto no feed
@router.post("/feed/posts/com-foto")
async def criar_post_com_foto(
    texto: str = Form(""),
    foto: UploadFile = File(...),
    current_user: dict = Depends(require_premium_access)
):
    """Cria um post com foto no feed. Limite de 2 fotos por dia (24h)."""

    # 1. Verificar bloqueio de moderação
    bloqueado, data_desbloqueio = await verificar_usuario_bloqueado(db, current_user["id"])
    if bloqueado:
        raise HTTPException(
            status_code=403,
            detail=f"Você está temporariamente bloqueado de postar até {data_desbloqueio[:10]}."
        )

    # 2. Verificar limite diário de fotos
    fotos_hoje = await _contar_fotos_hoje(current_user["id"])
    if fotos_hoje >= MAX_FOTOS_DIA:
        raise HTTPException(
            status_code=429,
            detail=f"Você já atingiu o limite de {MAX_FOTOS_DIA} fotos por dia. Tente novamente amanhã!"
        )

    # 3. Validar extensão
    ext = Path(foto.filename or "").suffix.lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não permitido. Use: {', '.join(EXTENSOES_PERMITIDAS)}"
        )

    # 4. Ler e validar tamanho
    conteudo = await foto.read()
    tamanho_mb = len(conteudo) / (1024 * 1024)
    if tamanho_mb > MAX_FOTO_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Imagem muito grande ({tamanho_mb:.1f}MB). Máximo: {MAX_FOTO_SIZE_MB}MB"
        )

    # 5. Moderar texto (se houver)
    if texto.strip():
        if len(texto) > 1000:
            raise HTTPException(status_code=400, detail="O texto não pode ter mais de 1000 caracteres")
        bloqueado_mod, categoria, nivel, mensagem_feedback = analisar_conteudo(texto)
        if bloqueado_mod and nivel:
            await registrar_infracao(db, current_user["id"], nivel, categoria, texto)
            feedback_educativo = gerar_feedback_educativo(nivel, categoria)
            raise HTTPException(status_code=400, detail={
                "message": mensagem_feedback,
                "nivel": nivel.value,
                "categoria": categoria,
                "educativo": feedback_educativo
            })

    # 6. Comprimir e salvar na nuvem
    conteudo_final, ext_final = _comprimir_imagem(conteudo, ext)
    from services.object_storage import upload_file as cloud_upload
    result = cloud_upload(conteudo_final, f"feed{ext_final}", pasta="feed")
    imagem_url = result["url"]

    # 7. Criar post
    post = {
        "id": str(uuid.uuid4()),
        "autor_id": current_user["id"],
        "autor_nome": current_user.get("nome", ""),
        "texto": texto.strip(),
        "tipo": "foto",
        "resultado_dados": None,
        "conquista_dados": None,
        "imagem_url": imagem_url,
        "status": "ativo",
        "data_criacao": datetime.now(timezone.utc).isoformat()
    }

    await db.feed_posts.insert_one(post)

    restantes = MAX_FOTOS_DIA - fotos_hoje - 1

    return {
        "message": "Foto publicada com sucesso!",
        "post_id": post["id"],
        "imagem_url": imagem_url,
        "fotos_restantes_hoje": restantes
    }


@router.get("/feed/fotos-restantes")
async def fotos_restantes_hoje(current_user: dict = Depends(get_current_user)):
    """Retorna quantas fotos o atleta ainda pode postar hoje"""
    fotos_hoje = await _contar_fotos_hoje(current_user["id"])
    return {
        "fotos_hoje": fotos_hoje,
        "limite_diario": MAX_FOTOS_DIA,
        "restantes": max(0, MAX_FOTOS_DIA - fotos_hoje)
    }


@router.delete("/feed/posts/{post_id}")
async def deletar_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Deleta um post"""
    
    post = await db.feed_posts.find_one({
        "id": post_id,
        "autor_id": current_user["id"]
    })
    
    if not post:
        # Verificar se é admin
        if current_user.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Marcar como deletado (soft delete)
    await db.feed_posts.update_one(
        {"id": post_id},
        {"$set": {"status": "deletado", "data_delecao": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Post deletado com sucesso"}


@router.get("/feed/reacoes-disponiveis")
async def get_reacoes_disponiveis():
    """Retorna as reações disponíveis no sistema"""
    return {"reacoes": REACOES_DISPONIVEIS}


@router.post("/feed/posts/{post_id}/reagir")
async def reagir_post(
    post_id: str,
    dados: ReacaoCreate,
    current_user: dict = Depends(require_premium_access)
):
    """Adiciona ou altera reação a um post"""
    
    if dados.tipo_reacao not in REACOES_DISPONIVEIS:
        raise HTTPException(
            status_code=400, 
            detail=f"Reação inválida. Opções: {list(REACOES_DISPONIVEIS.keys())}"
        )
    
    post = await db.feed_posts.find_one({"id": post_id, "status": "ativo"})
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Verificar se já reagiu
    reacao_existente = await db.feed_reacoes.find_one({
        "post_id": post_id,
        "usuario_id": current_user["id"]
    })
    
    if reacao_existente:
        # Se for a mesma reação, remover (toggle)
        if reacao_existente["tipo_reacao"] == dados.tipo_reacao:
            await db.feed_reacoes.delete_one({"id": reacao_existente["id"]})
            return {
                "message": "Reação removida",
                "reacao": None,
                "removida": True
            }
        else:
            # Alterar para nova reação
            await db.feed_reacoes.update_one(
                {"id": reacao_existente["id"]},
                {"$set": {
                    "tipo_reacao": dados.tipo_reacao,
                    "data_atualizacao": datetime.now(timezone.utc).isoformat()
                }}
            )
            return {
                "message": f"Reação alterada para {REACOES_DISPONIVEIS[dados.tipo_reacao]['emoji']}",
                "reacao": dados.tipo_reacao,
                "removida": False
            }
    
    # Nova reação
    reacao = {
        "id": str(uuid.uuid4()),
        "post_id": post_id,
        "usuario_id": current_user["id"],
        "tipo_reacao": dados.tipo_reacao,
        "data_criacao": datetime.now(timezone.utc).isoformat()
    }
    await db.feed_reacoes.insert_one(reacao)
    
    # Notificação de reação removida - apenas admin/dono enviam notificações
    
    return {
        "message": f"Reação {REACOES_DISPONIVEIS[dados.tipo_reacao]['emoji']} adicionada!",
        "reacao": dados.tipo_reacao,
        "removida": False
    }


@router.delete("/feed/posts/{post_id}/reagir")
async def remover_reacao(post_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a reação do usuário de um post"""
    
    reacao = await db.feed_reacoes.find_one({
        "post_id": post_id,
        "usuario_id": current_user["id"]
    })
    
    if not reacao:
        raise HTTPException(status_code=404, detail="Reação não encontrada")
    
    await db.feed_reacoes.delete_one({"id": reacao["id"]})
    
    return {"message": "Reação removida"}


@router.get("/feed/posts/{post_id}/reacoes")
async def get_reacoes_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Retorna todas as reações de um post agrupadas por tipo"""
    
    # Buscar reações agrupadas
    pipeline = [
        {"$match": {"post_id": post_id}},
        {"$group": {"_id": "$tipo_reacao", "count": {"$sum": 1}, "usuarios": {"$push": "$usuario_id"}}}
    ]
    reacoes_agrupadas = await db.feed_reacoes.aggregate(pipeline).to_list(None)
    
    resultado = {}
    total = 0
    
    for r in reacoes_agrupadas:
        tipo = r["_id"]
        if tipo in REACOES_DISPONIVEIS:
            # Buscar nomes dos usuários que reagiram
            usuarios_info = []
            for uid in r["usuarios"][:10]:  # Limitar a 10 para performance
                user = await db.usuarios.find_one({"id": uid}, {"_id": 0, "id": 1, "nome": 1})
                if user:
                    usuarios_info.append(user)
            
            resultado[tipo] = {
                "count": r["count"],
                "emoji": REACOES_DISPONIVEIS[tipo]["emoji"],
                "nome": REACOES_DISPONIVEIS[tipo]["nome"],
                "usuarios_preview": usuarios_info
            }
            total += r["count"]
    
    return {
        "post_id": post_id,
        "total_reacoes": total,
        "reacoes": resultado
    }


# ============================================================
# COMENTÁRIOS
# ============================================================

@router.post("/feed/posts/{post_id}/comentarios")
async def comentar_post(
    post_id: str,
    dados: ComentarioCreate,
    current_user: dict = Depends(require_premium_access)
):
    """Adiciona um comentário em um post com sistema de moderação"""
    
    # 1. Verificar se o usuário está bloqueado temporariamente
    bloqueado, data_desbloqueio = await verificar_usuario_bloqueado(db, current_user["id"])
    if bloqueado:
        raise HTTPException(
            status_code=403, 
            detail=f"Você está temporariamente bloqueado de comentar até {data_desbloqueio[:10]}. Motivo: Violações repetidas das diretrizes da comunidade."
        )
    
    # Verificar bloqueio antigo
    usuario_bloqueado = await db.usuarios_bloqueados_feed.find_one({
        "usuario_id": current_user["id"],
        "ativo": True
    })
    if usuario_bloqueado:
        raise HTTPException(
            status_code=403, 
            detail="Você está bloqueado de comentar no feed. Motivo: " + usuario_bloqueado.get("motivo", "Violação das regras")
        )
    
    post = await db.feed_posts.find_one({"id": post_id, "status": "ativo"})
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    if not dados.texto.strip():
        raise HTTPException(status_code=400, detail="O comentário não pode estar vazio")
    
    if len(dados.texto) > 200:
        raise HTTPException(status_code=400, detail="O comentário não pode ter mais de 200 caracteres")
    
    # 2. MODERAÇÃO: Analisar conteúdo do comentário
    bloqueado_mod, categoria, nivel, mensagem_feedback = analisar_conteudo(dados.texto)
    
    if bloqueado_mod and nivel:
        # Registrar infração
        await registrar_infracao(db, current_user["id"], nivel, categoria, dados.texto)
        
        # Se infração GRAVE, bloquear usuário por 7 dias após 3 infrações
        usuario = await db.usuarios.find_one(
            {"id": current_user["id"]},
            {"_id": 0, "bloqueios_moderacao": 1}
        )
        if usuario and usuario.get("bloqueios_moderacao", 0) >= 3:
            await bloquear_usuario_temporariamente(db, current_user["id"], dias=7)
            mensagem_feedback += " Você foi bloqueado de comentar por 7 dias devido a infrações repetidas."
        
        # Gerar feedback educativo
        feedback_educativo = gerar_feedback_educativo(nivel, categoria)
        
        raise HTTPException(
            status_code=400,
            detail={
                "message": mensagem_feedback,
                "nivel": nivel.value,
                "categoria": categoria,
                "educativo": feedback_educativo
            }
        )
    
    # 3. Criar comentário (aprovado)
    comentario = {
        "id": str(uuid.uuid4()),
        "post_id": post_id,
        "autor_id": current_user["id"],
        "autor_nome": current_user.get("nome", ""),
        "texto": dados.texto.strip(),
        "fixado": False,
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "moderado": True,  # Passou pela moderação
        "status": "aprovado"
    }
    
    await db.feed_comentarios.insert_one(comentario)
    
    # 4. Incrementar contador de comentários aprovados
    await incrementar_comentarios_aprovados(db, current_user["id"])
    
    # Notificação de comentário removida - apenas admin/dono enviam notificações
    
    # 6. Verificar se o usuário ganhou o selo de respeitoso
    usuario_atualizado = await db.usuarios.find_one(
        {"id": current_user["id"]},
        {"_id": 0, "comentarios_aprovados": 1, "advertencias_moderacao": 1, 
         "bloqueios_moderacao": 1, "comentarios_ocultados": 1, "bloqueios_ultimos_90_dias": 1}
    )
    tem_selo = verificar_selo_respeitoso(usuario_atualizado or {})
    
    return {
        "message": "Comentário adicionado!",
        "comentario_id": comentario["id"],
        "selo_respeitoso": tem_selo
    }


@router.get("/feed/posts/{post_id}/comentarios")
async def get_comentarios_post(
    post_id: str,
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Retorna os comentários de um post"""
    
    skip = (pagina - 1) * limite
    
    comentarios = await db.feed_comentarios.find(
        {"post_id": post_id},
        {"_id": 0}
    ).sort("data_criacao", 1).skip(skip).limit(limite).to_list(limite)
    
    # Enriquecer com dados dos autores e selo respeitoso
    for com in comentarios:
        autor = await db.usuarios.find_one(
            {"id": com["autor_id"]},
            {"_id": 0, "id": 1, "nome": 1, "foto_url": 1, "comentarios_aprovados": 1,
             "advertencias_moderacao": 1, "bloqueios_moderacao": 1, 
             "comentarios_ocultados": 1, "bloqueios_ultimos_90_dias": 1}
        )
        if autor:
            tem_selo = verificar_selo_respeitoso(autor)
            com["autor"] = {
                "id": autor.get("id"),
                "nome": autor.get("nome"),
                "foto_url": autor.get("foto_url"),
                "selo_respeitoso": tem_selo
            }
        else:
            com["autor"] = None
    
    total = await db.feed_comentarios.count_documents({"post_id": post_id})
    
    return {
        "comentarios": comentarios,
        "total": total,
        "pagina": pagina,
        "total_paginas": (total + limite - 1) // limite
    }


@router.get("/feed/meu-status-moderacao")
async def get_status_moderacao(current_user: dict = Depends(get_current_user)):
    """Retorna o status de moderação do usuário logado"""
    
    usuario = await db.usuarios.find_one(
        {"id": current_user["id"]},
        {"_id": 0, "comentarios_aprovados": 1, "advertencias_moderacao": 1,
         "bloqueios_moderacao": 1, "comentarios_ocultados": 1, 
         "bloqueios_ultimos_90_dias": 1, "bloqueado_feed_ate": 1,
         "historico_infracoes": 1}
    )
    
    if not usuario:
        usuario = {}
    
    # Calcular score e selo
    score = calcular_score_respeito(usuario)
    tem_selo = verificar_selo_respeitoso(usuario)
    
    # Verificar bloqueio
    bloqueado, data_desbloqueio = await verificar_usuario_bloqueado(db, current_user["id"])
    
    return {
        "score_respeito": score,
        "selo_respeitoso": tem_selo,
        "comentarios_aprovados": usuario.get("comentarios_aprovados", 0),
        "advertencias": usuario.get("advertencias_moderacao", 0),
        "comentarios_ocultados": usuario.get("comentarios_ocultados", 0),
        "bloqueios": usuario.get("bloqueios_moderacao", 0),
        "bloqueado": bloqueado,
        "bloqueado_ate": data_desbloqueio,
        "ultimas_infracoes": (usuario.get("historico_infracoes") or [])[-5:]  # Últimas 5
    }


@router.delete("/feed/comentarios/{comentario_id}")
async def deletar_comentario(comentario_id: str, current_user: dict = Depends(get_current_user)):
    """Deleta um comentário"""
    
    comentario = await db.feed_comentarios.find_one({"id": comentario_id})
    
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    
    # Verificar se é o autor do comentário ou admin
    if comentario["autor_id"] != current_user["id"] and current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Sem permissão para deletar este comentário")
    
    await db.feed_comentarios.delete_one({"id": comentario_id})
    
    return {"message": "Comentário deletado"}


@router.get("/feed/trending")
async def get_trending(limite: int = Query(10, ge=1, le=20), current_user: dict = Depends(get_current_user)):
    """Retorna os posts mais populares das últimas 24 horas (baseado em reações)"""
    
    # Posts das últimas 24 horas
    data_limite = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    
    posts = await db.feed_posts.find(
        {"status": "ativo", "data_criacao": {"$gte": data_limite}},
        {"_id": 0}
    ).to_list(100)
    
    # Calcular engajamento (baseado em reações)
    for post in posts:
        total_reacoes = await db.feed_reacoes.count_documents({"post_id": post["id"]})
        post["engajamento"] = total_reacoes
        post["total_reacoes"] = total_reacoes
        
        # Buscar resumo das reações
        pipeline = [
            {"$match": {"post_id": post["id"]}},
            {"$group": {"_id": "$tipo_reacao", "count": {"$sum": 1}}}
        ]
        reacoes_agrupadas = await db.feed_reacoes.aggregate(pipeline).to_list(None)
        
        post["reacoes"] = {}
        for r in reacoes_agrupadas:
            tipo = r["_id"]
            if tipo in REACOES_DISPONIVEIS:
                post["reacoes"][tipo] = {
                    "count": r["count"],
                    "emoji": REACOES_DISPONIVEIS[tipo]["emoji"]
                }
        
        # Dados do autor
        autor = await db.usuarios.find_one(
            {"id": post["autor_id"]},
            {"_id": 0, "id": 1, "nome": 1, "foto_url": 1}
        )
        post["autor"] = autor
    
    # Ordenar por engajamento (reações)
    posts.sort(key=lambda x: x["engajamento"], reverse=True)
    
    return {"trending": posts[:limite]}


# ============================================================
# POSTS AUTOMÁTICOS DE CONQUISTAS E RESULTADOS
# ============================================================

async def criar_post_conquista(
    usuario_id: str,
    usuario_nome: str,
    conquista_nome: str,
    conquista_descricao: str,
    conquista_emoji: str = "🏆"
):
    """
    Cria um post automático quando o atleta ganha uma conquista/insígnia.
    Chamado pelo sistema de conquistas.
    """
    texto = f"🎉 Acabei de conquistar a insígnia **{conquista_nome}**! {conquista_emoji}\n\n{conquista_descricao}"
    
    post = {
        "id": str(uuid.uuid4()),
        "autor_id": usuario_id,
        "autor_nome": usuario_nome,
        "texto": texto,
        "tipo": "conquista",
        "conquista_dados": {
            "nome": conquista_nome,
            "descricao": conquista_descricao,
            "emoji": conquista_emoji
        },
        "resultado_dados": None,
        "imagem_url": None,
        "status": "ativo",
        "auto_gerado": True,
        "data_criacao": datetime.now(timezone.utc).isoformat()
    }
    
    await db.feed_posts.insert_one(post)
    
    # Notificar membros da mesma equipe
    # Notificação de conquista para colegas removida - apenas admin/dono enviam notificações
    
    return post["id"]


async def criar_post_corrida_aprovada(
    usuario_id: str,
    usuario_nome: str,
    nome_corrida: str,
    colocacao: int,
    pontos: int,
    distancia: str,
    tempo: str = None
):
    """
    Cria um post automático quando uma corrida é aprovada.
    """
    if colocacao == 1:
        emoji_coloc = "🥇"
        texto_coloc = "CAMPEÃO! 1º lugar"
    elif colocacao == 2:
        emoji_coloc = "🥈"
        texto_coloc = "2º lugar no pódio"
    elif colocacao == 3:
        emoji_coloc = "🥉"
        texto_coloc = "3º lugar no pódio"
    else:
        emoji_coloc = "🏃"
        texto_coloc = f"{colocacao}º lugar"
    
    texto = f"{emoji_coloc} **{texto_coloc}** na {nome_corrida}!\n\n"
    texto += f"📏 Distância: {distancia}\n"
    if tempo:
        texto += f"⏱️ Tempo: {tempo}\n"
    texto += f"⭐ +{pontos} pontos no ranking!"
    
    post = {
        "id": str(uuid.uuid4()),
        "autor_id": usuario_id,
        "autor_nome": usuario_nome,
        "texto": texto,
        "tipo": "corrida_aprovada",
        "conquista_dados": None,
        "resultado_dados": {
            "nome_corrida": nome_corrida,
            "colocacao": colocacao,
            "pontos": pontos,
            "distancia": distancia,
            "tempo": tempo
        },
        "imagem_url": None,
        "status": "ativo",
        "auto_gerado": True,
        "data_criacao": datetime.now(timezone.utc).isoformat()
    }
    
    await db.feed_posts.insert_one(post)
    return post["id"]


@router.post("/feed/posts/{post_id}/parabens")
async def dar_parabens(
    post_id: str,
    current_user: dict = Depends(require_premium_access)
):
    """
    Atalho para dar parabéns em um post de conquista ou resultado.
    Adiciona reação 'parabens' + comentário automático.
    """
    post = await db.feed_posts.find_one({"id": post_id, "status": "ativo"})
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Adicionar reação de parabéns
    reacao_existente = await db.feed_reacoes.find_one({
        "post_id": post_id,
        "usuario_id": current_user["id"]
    })
    
    if not reacao_existente:
        reacao = {
            "id": str(uuid.uuid4()),
            "post_id": post_id,
            "usuario_id": current_user["id"],
            "tipo_reacao": "parabens",
            "data_criacao": datetime.now(timezone.utc).isoformat()
        }
        await db.feed_reacoes.insert_one(reacao)
    
    # Notificação de parabéns removida - apenas admin/dono enviam notificações
    
    return {
        "message": "Parabéns enviado!",
        "emoji": "🎊"
    }


@router.get("/feed/equipe")
async def get_feed_equipe(
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna apenas posts de membros da mesma equipe do usuário.
    """
    usuario = await db.usuarios.find_one(
        {"id": current_user["id"]},
        {"_id": 0, "equipe": 1}
    )
    
    if not usuario or not usuario.get("equipe"):
        return {"posts": [], "message": "Você não está em uma equipe"}
    
    # Buscar IDs dos membros da equipe
    membros = await db.usuarios.find(
        {"equipe": usuario["equipe"]},
        {"_id": 0, "id": 1}
    ).to_list(500)
    
    membros_ids = [m["id"] for m in membros]
    
    skip = (pagina - 1) * limite
    
    posts = await db.feed_posts.find(
        {"autor_id": {"$in": membros_ids}, "status": "ativo"},
        {"_id": 0}
    ).sort("data_criacao", -1).skip(skip).limit(limite).to_list(limite)
    
    # Enriquecer posts
    for post in posts:
        autor = await db.usuarios.find_one(
            {"id": post["autor_id"]},
            {"_id": 0, "id": 1, "nome": 1, "foto_url": 1, "equipe": 1}
        )
        post["autor"] = autor
        
        # Reações
        pipeline = [
            {"$match": {"post_id": post["id"]}},
            {"$group": {"_id": "$tipo_reacao", "count": {"$sum": 1}}}
        ]
        reacoes = await db.feed_reacoes.aggregate(pipeline).to_list(None)
        
        post["reacoes"] = {}
        post["total_reacoes"] = 0
        for r in reacoes:
            tipo = r["_id"]
            if tipo in REACOES_DISPONIVEIS:
                post["reacoes"][tipo] = {
                    "count": r["count"],
                    "emoji": REACOES_DISPONIVEIS[tipo]["emoji"]
                }
                post["total_reacoes"] += r["count"]
        
        # Minha reação
        minha = await db.feed_reacoes.find_one({
            "post_id": post["id"],
            "usuario_id": current_user["id"]
        })
        post["minha_reacao"] = minha["tipo_reacao"] if minha else None
        
        # Comentários
        post["total_comentarios"] = await db.feed_comentarios.count_documents({"post_id": post["id"]})
    
    total = await db.feed_posts.count_documents({"autor_id": {"$in": membros_ids}, "status": "ativo"})
    
    return {
        "posts": posts,
        "equipe": usuario["equipe"],
        "total": total,
        "pagina": pagina
    }



# ============================================================
# ADMINISTRAÇÃO DE COMENTÁRIOS
# ============================================================

class BloqueioUsuarioCreate(BaseModel):
    usuario_id: str
    motivo: str = "Violação das regras do feed"


@router.post("/feed/admin/comentarios/{comentario_id}/fixar")
async def fixar_comentario(
    comentario_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Admin fixa um comentário no topo"""
    
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas administradores podem fixar comentários")
    
    comentario = await db.feed_comentarios.find_one({"id": comentario_id})
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    
    # Toggle fixar/desfixar
    novo_status = not comentario.get("fixado", False)
    
    await db.feed_comentarios.update_one(
        {"id": comentario_id},
        {"$set": {
            "fixado": novo_status,
            "fixado_por": current_user["id"] if novo_status else None,
            "data_fixacao": datetime.now(timezone.utc).isoformat() if novo_status else None
        }}
    )
    
    return {
        "message": f"Comentário {'fixado' if novo_status else 'desfixado'} com sucesso",
        "fixado": novo_status
    }


@router.delete("/feed/admin/comentarios/limpar-todos")
async def limpar_todos_comentarios(
    current_user: dict = Depends(get_current_user)
):
    """Admin limpa todos os comentários (exceto fixados). Usado pelo job semanal."""
    
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas administradores podem limpar comentários")
    
    # Contar comentários a serem removidos (exceto fixados)
    total_antes = await db.feed_comentarios.count_documents({"fixado": {"$ne": True}})
    
    # Fazer backup antes de excluir
    comentarios = await db.feed_comentarios.find({"fixado": {"$ne": True}}, {"_id": 0}).to_list(None)
    
    if comentarios:
        await db.feed_comentarios_backup.insert_one({
            "data_backup": datetime.now(timezone.utc).isoformat(),
            "executado_por": current_user["id"],
            "total_comentarios": len(comentarios),
            "comentarios": comentarios
        })
    
    # Excluir comentários não fixados
    resultado = await db.feed_comentarios.delete_many({"fixado": {"$ne": True}})
    
    # Limpar cache
    try:
        from services.cache_service import cache_service
        await cache_service.invalidate_feed()
    except Exception as e:
        print(f"Erro ao limpar cache: {e}")
    
    return {
        "message": f"Limpeza concluída! {resultado.deleted_count} comentários removidos.",
        "comentarios_removidos": resultado.deleted_count,
        "comentarios_fixados_preservados": total_antes - resultado.deleted_count if total_antes > resultado.deleted_count else 0
    }


@router.delete("/feed/admin/posts/limpar-todos")
async def limpar_todos_posts(
    current_user: dict = Depends(get_current_user)
):
    """Admin limpa todos os posts do feed."""
    
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas administradores podem limpar posts")
    
    # Contar posts a serem removidos
    total_posts = await db.feed_posts.count_documents({})
    
    # Fazer backup antes de excluir
    posts = await db.feed_posts.find({}, {"_id": 0}).to_list(None)
    
    if posts:
        await db.feed_posts_backup.insert_one({
            "data_backup": datetime.now(timezone.utc).isoformat(),
            "executado_por": current_user["id"],
            "total_posts": len(posts),
            "posts": posts
        })
    
    # Excluir todos os posts
    resultado = await db.feed_posts.delete_many({})
    
    # Excluir também reações e comentários relacionados
    await db.feed_reacoes.delete_many({})
    await db.feed_comentarios.delete_many({})
    
    # Limpar cache
    try:
        from services.cache_service import cache_service
        await cache_service.invalidate_feed()
    except Exception as e:
        print(f"Erro ao limpar cache: {e}")
    
    return {
        "message": f"Limpeza concluída! {resultado.deleted_count} posts removidos.",
        "posts_removidos": resultado.deleted_count
    }


@router.delete("/feed/admin/comentarios/{comentario_id}")
async def excluir_comentario_admin(
    comentario_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Admin exclui um comentário"""
    
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas administradores podem excluir comentários")
    
    comentario = await db.feed_comentarios.find_one({"id": comentario_id})
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    
    # Registrar exclusão para auditoria
    await db.feed_comentarios_excluidos.insert_one({
        **comentario,
        "excluido_por": current_user["id"],
        "data_exclusao": datetime.now(timezone.utc).isoformat()
    })
    
    # Remover comentário
    await db.feed_comentarios.delete_one({"id": comentario_id})
    
    return {"message": "Comentário excluído com sucesso"}


@router.post("/feed/admin/usuarios/bloquear")
async def bloquear_usuario_feed(
    dados: BloqueioUsuarioCreate,
    current_user: dict = Depends(get_current_user)
):
    """Admin bloqueia um usuário de comentar no feed"""
    
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas administradores podem bloquear usuários")
    
    usuario = await db.usuarios.find_one({"id": dados.usuario_id})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se já está bloqueado
    bloqueio_existente = await db.usuarios_bloqueados_feed.find_one({
        "usuario_id": dados.usuario_id,
        "ativo": True
    })
    
    if bloqueio_existente:
        raise HTTPException(status_code=400, detail="Usuário já está bloqueado")
    
    bloqueio = {
        "id": str(uuid.uuid4()),
        "usuario_id": dados.usuario_id,
        "usuario_nome": usuario.get("nome", ""),
        "motivo": dados.motivo,
        "bloqueado_por": current_user["id"],
        "ativo": True,
        "data_bloqueio": datetime.now(timezone.utc).isoformat()
    }
    
    await db.usuarios_bloqueados_feed.insert_one(bloqueio)
    
    return {
        "message": f"Usuário {usuario.get('nome')} bloqueado de comentar no feed",
        "bloqueio_id": bloqueio["id"]
    }


@router.post("/feed/admin/usuarios/{usuario_id}/desbloquear")
async def desbloquear_usuario_feed(
    usuario_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Admin desbloqueia um usuário"""
    
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas administradores podem desbloquear usuários")
    
    resultado = await db.usuarios_bloqueados_feed.update_one(
        {"usuario_id": usuario_id, "ativo": True},
        {"$set": {
            "ativo": False,
            "desbloqueado_por": current_user["id"],
            "data_desbloqueio": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if resultado.modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não está bloqueado")
    
    return {"message": "Usuário desbloqueado com sucesso"}


@router.get("/feed/admin/usuarios/bloqueados")
async def listar_usuarios_bloqueados(
    current_user: dict = Depends(get_current_user)
):
    """Lista usuários bloqueados do feed"""
    
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas administradores podem ver usuários bloqueados")
    
    bloqueados = await db.usuarios_bloqueados_feed.find(
        {"ativo": True},
        {"_id": 0}
    ).sort("data_bloqueio", -1).to_list(100)
    
    return {"usuarios_bloqueados": bloqueados, "total": len(bloqueados)}



# ============================================================
# STORIES - Fotos temporárias (24h) no topo do Feed
# ============================================================

@router.post("/feed/stories")
async def criar_story(
    texto: str = Form(""),
    foto: UploadFile = File(...),
    current_user: dict = Depends(require_premium_access)
):
    """Cria um story (foto temporária de 24h). Limite: 1 por dia."""

    bloqueado, data_desbloqueio = await verificar_usuario_bloqueado(db, current_user["id"])
    if bloqueado:
        raise HTTPException(status_code=403, detail=f"Bloqueado até {data_desbloqueio[:10]}.")

    # Stories não tem limite diário
    ext = Path(foto.filename or "").suffix.lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(status_code=400, detail=f"Formato não permitido. Use: {', '.join(EXTENSOES_PERMITIDAS)}")

    conteudo = await foto.read()
    if len(conteudo) / (1024 * 1024) > MAX_FOTO_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"Imagem muito grande. Máximo: {MAX_FOTO_SIZE_MB}MB")

    if texto.strip() and len(texto) > 200:
        raise HTTPException(status_code=400, detail="Texto do story máximo 200 caracteres")

    conteudo_final, ext_final = _comprimir_imagem(conteudo, ext)
    from services.object_storage import upload_file as cloud_upload
    result = cloud_upload(conteudo_final, f"story{ext_final}", pasta="stories")

    story = {
        "id": str(uuid.uuid4()),
        "autor_id": current_user["id"],
        "autor_nome": current_user.get("nome", ""),
        "autor_foto": current_user.get("foto_url", ""),
        "imagem_url": result["url"],
        "texto": texto.strip(),
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "visualizacoes": [],
        "reacoes": []
    }

    await db.stories.insert_one(story)

    return {"message": "Story publicado!", "story_id": story["id"], "imagem_url": story["imagem_url"]}


@router.get("/feed/stories")
async def listar_stories(current_user: dict = Depends(get_current_user)):
    """Lista todos os stories ativos (últimas 24h), agrupados por autor."""
    data_limite = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    stories = await db.stories.find(
        {"data_criacao": {"$gte": data_limite}},
        {"_id": 0}
    ).sort("data_criacao", -1).to_list(100)

    # Buscar fotos de perfil dos autores
    autor_ids = list(set(s["autor_id"] for s in stories))
    autores_info = {}
    if autor_ids:
        usuarios_cursor = db.usuarios.find(
            {"id": {"$in": autor_ids}},
            {"_id": 0, "id": 1, "foto_url": 1}
        )
        async for u in usuarios_cursor:
            autores_info[u["id"]] = u.get("foto_url", "")

    # Agrupar por autor
    autores = {}
    for s in stories:
        aid = s["autor_id"]
        if aid not in autores:
            autores[aid] = {
                "autor_id": aid,
                "autor_nome": s["autor_nome"],
                "autor_foto": s.get("autor_foto") or autores_info.get(aid, ""),
                "stories": [],
                "tem_nao_visto": False
            }
        visto = current_user["id"] in s.get("visualizacoes", [])
        s["visto"] = visto
        if not visto:
            autores[aid]["tem_nao_visto"] = True
        autores[aid]["stories"].append(s)

    # Ordenar: não vistos primeiro, depois vistos
    resultado = sorted(autores.values(), key=lambda a: (not a["tem_nao_visto"], a["stories"][0]["data_criacao"]), reverse=False)
    # Colocar não vistos primeiro
    nao_vistos = [a for a in resultado if a["tem_nao_visto"]]
    vistos = [a for a in resultado if not a["tem_nao_visto"]]

    return {"autores": nao_vistos + vistos, "total": len(stories)}


@router.post("/feed/stories/{story_id}/visualizar")
async def visualizar_story(story_id: str, current_user: dict = Depends(get_current_user)):
    """Marca um story como visualizado pelo usuário."""
    result = await db.stories.update_one(
        {"id": story_id},
        {"$addToSet": {"visualizacoes": current_user["id"]}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Story não encontrado")
    return {"ok": True}


@router.post("/feed/stories/{story_id}/reagir")
async def reagir_story(story_id: str, reacao: ReacaoCreate, current_user: dict = Depends(require_premium_access)):
    """Reage a um story com emoji."""
    if reacao.tipo_reacao not in REACOES_DISPONIVEIS:
        raise HTTPException(status_code=400, detail="Reação inválida")

    # Remove reação anterior do mesmo tipo e adiciona nova
    await db.stories.update_one(
        {"id": story_id},
        {"$pull": {"reacoes": {"usuario_id": current_user["id"], "tipo": reacao.tipo_reacao}}}
    )
    await db.stories.update_one(
        {"id": story_id},
        {"$push": {"reacoes": {
            "usuario_id": current_user["id"],
            "usuario_nome": current_user.get("nome", ""),
            "tipo": reacao.tipo_reacao,
            "emoji": REACOES_DISPONIVEIS[reacao.tipo_reacao]["emoji"],
            "data": datetime.now(timezone.utc).isoformat()
        }}}
    )
    return {"ok": True, "emoji": REACOES_DISPONIVEIS[reacao.tipo_reacao]["emoji"]}


@router.get("/feed/stories/restantes")
async def stories_restantes(current_user: dict = Depends(get_current_user)):
    """Stories não têm limite diário."""
    return {
        "stories_hoje": 0,
        "limite_diario": -1,
        "restantes": 999,
        "ilimitado": True
    }
