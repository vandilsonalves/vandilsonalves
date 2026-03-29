"""
Rotas para Chat da Assessoria, Feed da Equipe e Desvinculação de Atletas.
"""
import os
import uuid
import aiofiles
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from config import db
from routes.auth_routes import get_current_user
from pathlib import Path

router = APIRouter()

BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "")
UPLOADS_DIR = Path("/app/uploads/chat")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_nome_display(user: dict) -> str:
    apelido = user.get("apelido", "").strip()
    if apelido:
        return apelido
    nome = user.get("nome", "")
    partes = nome.split()
    if len(partes) >= 2:
        return f"{partes[0]} {partes[1]}"
    return nome


# ==================== CHAT DA ASSESSORIA ====================

@router.post("/assessoria/chat/enviar")
async def enviar_mensagem_chat(
    mensagem: str = Form(default=""),
    destinatarios: str = Form(default=""),
    arquivo: UploadFile = File(default=None),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria")

    equipe = current_user.get("equipe", "")
    if not equipe:
        raise HTTPException(status_code=400, detail="Sem equipe vinculada")

    if not mensagem.strip() and not arquivo:
        raise HTTPException(status_code=400, detail="Envie uma mensagem ou arquivo")

    arquivo_info = None
    if arquivo and arquivo.filename:
        ext = os.path.splitext(arquivo.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Tipo de arquivo não permitido: {ext}")

        content = await arquivo.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 10MB)")

        file_id = str(uuid.uuid4())
        filename = f"{file_id}{ext}"
        filepath = UPLOADS_DIR / filename

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        tipo_arquivo = "imagem" if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp"} else "documento"
        arquivo_info = {
            "nome_original": arquivo.filename,
            "caminho": f"/api/uploads/chat/{filename}",
            "tipo": tipo_arquivo,
            "tamanho": len(content),
            "extensao": ext
        }

    dest_list = [d.strip() for d in destinatarios.split(",") if d.strip()] if destinatarios else []
    if not dest_list:
        atletas = await db.usuarios.find(
            {"equipe": equipe, "role": {"$in": ["atleta", "dono_assessoria"]}},
            {"_id": 0, "id": 1}
        ).to_list(500)
        dest_list = [a["id"] for a in atletas if a["id"] != current_user["id"]]

    msg = {
        "id": str(uuid.uuid4()),
        "equipe": equipe,
        "remetente_id": current_user["id"],
        "remetente_nome": get_nome_display(current_user),
        "remetente_foto": current_user.get("foto_url", ""),
        "mensagem": mensagem.strip(),
        "arquivo": arquivo_info,
        "destinatarios": dest_list,
        "lido_por": [current_user["id"]],
        "data_envio": datetime.now(timezone.utc).isoformat(),
        "tipo": "chat_assessoria"
    }

    await db.chat_assessoria.insert_one(msg)

    from routes.notificacoes_routes import criar_notificacao
    for dest_id in dest_list:
        await criar_notificacao(
            usuario_id=dest_id,
            tipo="mensagem_assessoria",
            titulo=f"Mensagem de {equipe}",
            mensagem=mensagem[:100] if mensagem else f"Arquivo: {arquivo_info['nome_original']}" if arquivo_info else "",
            dados_extras={"chat_msg_id": msg["id"]}
        )

    msg.pop("_id", None)
    return {"message": "Enviada com sucesso", "msg": msg}


@router.get("/assessoria/chat/historico")
async def historico_chat(
    page: int = 1,
    limit: int = 30,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria")

    equipe = current_user.get("equipe", "")
    if not equipe:
        return {"mensagens": [], "total": 0}

    total = await db.chat_assessoria.count_documents({"equipe": equipe})
    skip = (page - 1) * limit

    mensagens = await db.chat_assessoria.find(
        {"equipe": equipe},
        {"_id": 0}
    ).sort("data_envio", -1).skip(skip).limit(limit).to_list(limit)

    return {
        "mensagens": list(reversed(mensagens)),
        "total": total,
        "page": page,
        "has_more": skip + limit < total
    }


# ==================== DESVINCULAR ATLETA ====================

class DesvincularRequest(BaseModel):
    atleta_id: str
    motivo: str = ""

@router.post("/assessoria/desvincular-atleta")
async def desvincular_atleta(
    dados: DesvincularRequest,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria")

    equipe = current_user.get("equipe", "")
    if not equipe:
        raise HTTPException(status_code=400, detail="Sem equipe vinculada")

    atleta = await db.usuarios.find_one({"id": dados.atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")

    if atleta.get("equipe", "").upper() != equipe.upper():
        raise HTTPException(status_code=400, detail="Atleta não pertence à sua equipe")

    if atleta.get("id") == current_user.get("id"):
        raise HTTPException(status_code=400, detail="Você não pode desvincular a si mesmo")

    historico_entry = {
        "equipe": equipe,
        "data_saida": datetime.now(timezone.utc).isoformat(),
        "motivo": dados.motivo or "Desvinculado pelo dono da assessoria"
    }

    await db.usuarios.update_one(
        {"id": dados.atleta_id},
        {
            "$set": {"equipe": "Individual", "role": "atleta"},
            "$push": {"historico_equipes": historico_entry}
        }
    )

    from routes.notificacoes_routes import criar_notificacao
    await criar_notificacao(
        usuario_id=dados.atleta_id,
        tipo="desvinculacao",
        titulo="Desvinculado da equipe",
        mensagem=f"Você foi desvinculado da equipe {equipe}. Motivo: {dados.motivo or 'Não informado'}",
        dados_extras={"equipe": equipe, "motivo": dados.motivo}
    )

    from services.cache_service import invalidate_on_liga_change
    await invalidate_on_liga_change()

    return {
        "message": f"Atleta {atleta.get('nome', '')} foi desvinculado e agora é Individual.",
        "atleta_nome": atleta.get("nome", "")
    }


# ==================== FEED DA EQUIPE (Grupo) ====================

@router.post("/equipe/feed/enviar")
async def enviar_feed(
    mensagem: str = Form(default=""),
    arquivo: UploadFile = File(default=None),
    current_user: dict = Depends(get_current_user)
):
    equipe = current_user.get("equipe", "")
    if not equipe or equipe.upper() in ["INDIVIDUAL", "SEM EQUIPE"]:
        raise HTTPException(status_code=400, detail="Você não pertence a nenhuma equipe")

    if not mensagem.strip() and not arquivo:
        raise HTTPException(status_code=400, detail="Envie uma mensagem ou arquivo")

    arquivo_info = None
    if arquivo and arquivo.filename:
        ext = os.path.splitext(arquivo.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Tipo não permitido: {ext}")

        content = await arquivo.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 10MB)")

        file_id = str(uuid.uuid4())
        filename = f"{file_id}{ext}"
        filepath = UPLOADS_DIR / filename

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        tipo_arquivo = "imagem" if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp"} else "documento"
        arquivo_info = {
            "nome_original": arquivo.filename,
            "caminho": f"/api/uploads/chat/{filename}",
            "tipo": tipo_arquivo,
            "tamanho": len(content),
            "extensao": ext
        }

    post = {
        "id": str(uuid.uuid4()),
        "equipe": equipe,
        "autor_id": current_user["id"],
        "autor_nome": get_nome_display(current_user),
        "autor_foto": current_user.get("foto_url", ""),
        "mensagem": mensagem.strip(),
        "arquivo": arquivo_info,
        "curtidas": [],
        "data_envio": datetime.now(timezone.utc).isoformat()
    }

    await db.feed_equipe.insert_one(post)
    post.pop("_id", None)
    return {"message": "Publicado no feed!", "post": post}


@router.get("/equipe/feed")
async def get_feed(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    equipe = current_user.get("equipe", "")
    if not equipe or equipe.upper() in ["INDIVIDUAL", "SEM EQUIPE"]:
        return {"posts": [], "total": 0, "equipe": ""}

    total = await db.feed_equipe.count_documents({"equipe": equipe})
    skip = (page - 1) * limit

    posts = await db.feed_equipe.find(
        {"equipe": equipe},
        {"_id": 0}
    ).sort("data_envio", -1).skip(skip).limit(limit).to_list(limit)

    return {
        "posts": posts,
        "total": total,
        "page": page,
        "has_more": skip + limit < total,
        "equipe": equipe
    }


@router.post("/equipe/feed/{post_id}/curtir")
async def curtir_feed(post_id: str, current_user: dict = Depends(get_current_user)):
    post = await db.feed_equipe.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")

    uid = current_user["id"]
    if uid in post.get("curtidas", []):
        await db.feed_equipe.update_one({"id": post_id}, {"$pull": {"curtidas": uid}})
        return {"curtiu": False}
    else:
        await db.feed_equipe.update_one({"id": post_id}, {"$push": {"curtidas": uid}})
        return {"curtiu": True}


@router.delete("/equipe/feed/{post_id}")
async def deletar_feed(post_id: str, current_user: dict = Depends(get_current_user)):
    post = await db.feed_equipe.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")

    if post["autor_id"] != current_user["id"] and current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Sem permissão")

    await db.feed_equipe.delete_one({"id": post_id})
    return {"message": "Post removido"}
