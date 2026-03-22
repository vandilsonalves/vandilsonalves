# /app/backend/routes/feed_routes.py
# Feed Social da plataforma com sistema de reações e posts automáticos de conquistas

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import uuid
from pathlib import Path

from config import db
from routes.auth_routes import get_current_user
from routes.notificacoes_routes import criar_notificacao
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
    current_user: dict = Depends(get_current_user)
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


# Endpoint de upload de imagem removido - usuários só podem criar posts de texto


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
    current_user: dict = Depends(get_current_user)
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
    
    # Notificar autor do post (se não for o próprio)
    if post["autor_id"] != current_user["id"]:
        emoji = REACOES_DISPONIVEIS[dados.tipo_reacao]["emoji"]
        nome_reacao = REACOES_DISPONIVEIS[dados.tipo_reacao]["nome"]
        await criar_notificacao(
            usuario_id=post["autor_id"],
            tipo="reacao",
            titulo=f"{emoji} Nova reação!",
            mensagem=f"{current_user.get('nome', 'Alguém')} reagiu com {emoji} ({nome_reacao}) ao seu post.",
            dados_extras={"post_id": post_id, "tipo_reacao": dados.tipo_reacao}
        )
    
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
async def get_reacoes_post(post_id: str):
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
    current_user: dict = Depends(get_current_user)
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
    
    # 5. Notificar autor do post (se não for o próprio)
    if post["autor_id"] != current_user["id"]:
        await criar_notificacao(
            usuario_id=post["autor_id"],
            tipo="comentario",
            titulo="Novo comentário!",
            mensagem=f"{current_user.get('nome', 'Alguém')} comentou: \"{dados.texto[:50]}...\"",
            dados_extras={"post_id": post_id, "comentario_id": comentario["id"]}
        )
    
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
    limite: int = Query(20, ge=1, le=50)
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
async def get_trending(limite: int = Query(10, ge=1, le=20)):
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
    usuario = await db.usuarios.find_one({"id": usuario_id}, {"_id": 0, "equipe": 1})
    if usuario and usuario.get("equipe"):
        colegas = await db.usuarios.find(
            {"equipe": usuario["equipe"], "id": {"$ne": usuario_id}},
            {"_id": 0, "id": 1}
        ).limit(50).to_list(50)
        
        for colega in colegas:
            await criar_notificacao(
                usuario_id=colega["id"],
                tipo="conquista_equipe",
                titulo=f"🏆 {usuario_nome} conquistou {conquista_nome}!",
                mensagem=f"Um colega da sua equipe acabou de ganhar uma nova insígnia. Parabenize!",
                dados_extras={"post_id": post["id"], "conquista": conquista_nome}
            )
    
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
    current_user: dict = Depends(get_current_user)
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
    
    # Notificar autor
    if post["autor_id"] != current_user["id"]:
        await criar_notificacao(
            usuario_id=post["autor_id"],
            tipo="parabens",
            titulo=f"🎊 {current_user.get('nome', 'Alguém')} te parabenizou!",
            mensagem=f"Você recebeu parabéns pela sua conquista!",
            dados_extras={"post_id": post_id}
        )
    
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
    
    # Limpar cache do Redis
    try:
        from services.cache_service import redis_client
        if redis_client:
            keys = redis_client.keys("feed:*")
            if keys:
                redis_client.delete(*keys)
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
    
    # Limpar cache do Redis
    try:
        from services.cache_service import redis_client
        if redis_client:
            keys = redis_client.keys("feed:*")
            if keys:
                redis_client.delete(*keys)
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
