# /app/backend/routes/feed_routes.py
# Feed Social da plataforma (apenas curtidas, sem comentários)

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import uuid
from pathlib import Path

from config import db
from routes.auth_routes import get_current_user
from routes.notificacoes_routes import criar_notificacao

router = APIRouter()

UPLOAD_DIR = Path("/app/uploads/feed")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class PostCreate(BaseModel):
    texto: str
    tipo: str = "texto"  # texto, resultado, conquista, foto
    resultado_id: Optional[str] = None
    conquista_id: Optional[str] = None


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
    
    # Enriquecer com dados dos autores e contagens
    for post in posts:
        # Dados do autor
        autor = await db.usuarios.find_one(
            {"id": post["autor_id"]},
            {"_id": 0, "id": 1, "nome": 1, "foto_url": 1, "equipe": 1, "cidade": 1}
        )
        post["autor"] = autor
        
        # Contagem de curtidas
        post["total_curtidas"] = await db.feed_curtidas.count_documents({"post_id": post["id"]})
        
        # Verificar se o usuário atual curtiu
        curtiu = await db.feed_curtidas.find_one({
            "post_id": post["id"],
            "usuario_id": current_user["id"]
        })
        post["curtido"] = curtiu is not None
    
    # Total de posts
    total = await db.feed_posts.count_documents(filtro)
    
    return {
        "posts": posts,
        "pagina": pagina,
        "limite": limite,
        "total": total,
        "total_paginas": (total + limite - 1) // limite
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
    
    # Enriquecer posts (apenas curtidas - comentários removidos)
    for post in posts:
        post["total_curtidas"] = await db.feed_curtidas.count_documents({"post_id": post["id"]})
    
    total = await db.feed_posts.count_documents({"autor_id": current_user["id"], "status": "ativo"})
    
    return {
        "posts": posts,
        "total": total
    }


@router.post("/feed/posts")
async def criar_post(
    dados: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    """Cria um novo post no feed"""
    
    if not dados.texto.strip():
        raise HTTPException(status_code=400, detail="O texto do post não pode estar vazio")
    
    if len(dados.texto) > 1000:
        raise HTTPException(status_code=400, detail="O texto do post não pode ter mais de 1000 caracteres")
    
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


@router.post("/feed/posts/{post_id}/imagem")
async def upload_imagem_post(
    post_id: str,
    imagem: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Faz upload de imagem para um post"""
    
    # Verificar se o post existe e pertence ao usuário
    post = await db.feed_posts.find_one({
        "id": post_id,
        "autor_id": current_user["id"]
    })
    
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Validar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if imagem.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido")
    
    # Validar tamanho (5MB)
    content = await imagem.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo: 5MB")
    
    # Salvar arquivo
    ext = imagem.filename.split('.')[-1] if '.' in imagem.filename else 'jpg'
    filename = f"{post_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    imagem_url = f"/uploads/feed/{filename}"
    
    # Atualizar post
    await db.feed_posts.update_one(
        {"id": post_id},
        {"$set": {"imagem_url": imagem_url, "tipo": "foto"}}
    )
    
    return {"message": "Imagem enviada com sucesso", "imagem_url": imagem_url}


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


@router.post("/feed/posts/{post_id}/curtir")
async def curtir_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Curte um post"""
    
    post = await db.feed_posts.find_one({"id": post_id, "status": "ativo"})
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Verificar se já curtiu
    curtida_existente = await db.feed_curtidas.find_one({
        "post_id": post_id,
        "usuario_id": current_user["id"]
    })
    
    if curtida_existente:
        # Descurtir
        await db.feed_curtidas.delete_one({"id": curtida_existente["id"]})
        return {"message": "Curtida removida", "curtido": False}
    
    # Curtir
    curtida = {
        "id": str(uuid.uuid4()),
        "post_id": post_id,
        "usuario_id": current_user["id"],
        "data_criacao": datetime.now(timezone.utc).isoformat()
    }
    await db.feed_curtidas.insert_one(curtida)
    
    # Notificar autor do post (se não for o próprio)
    if post["autor_id"] != current_user["id"]:
        await criar_notificacao(
            usuario_id=post["autor_id"],
            tipo="curtida",
            titulo="❤️ Novo curtir!",
            mensagem=f"{current_user.get('nome', 'Alguém')} curtiu seu post.",
            dados_extras={"post_id": post_id}
        )
    
    return {"message": "Post curtido!", "curtido": True}


@router.get("/feed/trending")
async def get_trending(limite: int = Query(10, ge=1, le=20)):
    """Retorna os posts mais populares das últimas 24 horas (baseado em curtidas)"""
    
    # Posts das últimas 24 horas
    data_limite = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    
    posts = await db.feed_posts.find(
        {"status": "ativo", "data_criacao": {"$gte": data_limite}},
        {"_id": 0}
    ).to_list(100)
    
    # Calcular engajamento (apenas curtidas)
    for post in posts:
        curtidas = await db.feed_curtidas.count_documents({"post_id": post["id"]})
        post["engajamento"] = curtidas
        post["total_curtidas"] = curtidas
        
        # Dados do autor
        autor = await db.usuarios.find_one(
            {"id": post["autor_id"]},
            {"_id": 0, "id": 1, "nome": 1, "foto_url": 1}
        )
        post["autor"] = autor
    
    # Ordenar por engajamento (curtidas)
    posts.sort(key=lambda x: x["engajamento"], reverse=True)
    
    return {"trending": posts[:limite]}
