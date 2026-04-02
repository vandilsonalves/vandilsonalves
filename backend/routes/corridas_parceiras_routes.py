# /app/backend/routes/corridas_parceiras_routes.py
# CRUD de Corridas Parceiras + Tracking de Clicks + Configurações

import os
import uuid
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel

from config import db
from routes.auth_routes import get_current_user, get_admin_user

router = APIRouter()

UPLOADS_DIR = Path("/app/uploads/corridas_parceiras")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ==================== CONFIGURAÇÕES ====================

@router.get("/corridas-parceiras/config")
async def get_config():
    """Retorna configurações públicas (link whatsapp, cupom)."""
    config = await db.config_corridas_parceiras.find_one({}, {"_id": 0})
    if not config:
        config = {
            "link_whatsapp": "https://wa.me/5577998626875",
            "cupom_nome": "RANKINGRUN10",
            "cupom_descricao": "Use Nosso Cupom e Pague Menos"
        }
        await db.config_corridas_parceiras.insert_one(config)
    return config


@router.put("/admin/corridas-parceiras/config")
async def update_config(
    admin: dict = Depends(get_admin_user),
    link_whatsapp: str = Form(None),
    cupom_nome: str = Form(None),
    cupom_descricao: str = Form(None)
):
    """Atualiza configurações (link whatsapp, cupom)."""
    update_data = {}
    if link_whatsapp is not None:
        update_data["link_whatsapp"] = link_whatsapp
    if cupom_nome is not None:
        update_data["cupom_nome"] = cupom_nome
    if cupom_descricao is not None:
        update_data["cupom_descricao"] = cupom_descricao

    if update_data:
        await db.config_corridas_parceiras.update_one(
            {}, {"$set": update_data}, upsert=True
        )

    return await get_config()


# ==================== CRUD CORRIDAS PARCEIRAS ====================

@router.get("/corridas-parceiras")
async def listar_corridas_parceiras():
    """Lista todas as corridas parceiras ordenadas por data (próximas primeiro)."""
    cursor = db.corridas_parceiras.find(
        {"ativo": True},
        {"_id": 0}
    ).sort("data_evento", 1)

    corridas = await cursor.to_list(100)
    return corridas


@router.get("/admin/corridas-parceiras")
async def admin_listar_corridas(admin: dict = Depends(get_admin_user)):
    """Lista todas as corridas (incluindo inativas) para o admin."""
    cursor = db.corridas_parceiras.find({}, {"_id": 0}).sort("data_evento", 1)
    corridas = await cursor.to_list(200)
    return corridas


@router.post("/admin/corridas-parceiras")
async def criar_corrida(
    admin: dict = Depends(get_admin_user),
    nome_evento: str = Form(...),
    data_evento: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    valor_inscricao: str = Form(...),
    link_inscricao: str = Form(""),
    link_resultado: str = Form(""),
    link_fotos: str = Form(""),
    link_instagram: str = Form(""),
    imagem: UploadFile = File(None)
):
    """Cria uma nova corrida parceira."""
    corrida_id = str(uuid.uuid4())
    imagem_url = ""

    if imagem and imagem.filename:
        ext = imagem.filename.split(".")[-1].lower()
        nome_arquivo = f"{corrida_id}.{ext}"
        caminho = UPLOADS_DIR / nome_arquivo
        with open(caminho, "wb") as f:
            content = await imagem.read()
            f.write(content)
        imagem_url = f"/api/uploads/corridas_parceiras/{nome_arquivo}"

    corrida = {
        "id": corrida_id,
        "nome_evento": nome_evento,
        "data_evento": data_evento,
        "cidade": cidade,
        "estado": estado,
        "valor_inscricao": valor_inscricao,
        "link_inscricao": link_inscricao,
        "link_resultado": link_resultado,
        "link_fotos": link_fotos,
        "link_instagram": link_instagram,
        "imagem_url": imagem_url,
        "ativo": True,
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "clicks": {"inscricao": 0, "resultado": 0, "fotos": 0, "instagram": 0}
    }

    await db.corridas_parceiras.insert_one(corrida)
    corrida.pop("_id", None)
    return corrida


@router.put("/admin/corridas-parceiras/{corrida_id}")
async def editar_corrida(
    corrida_id: str,
    admin: dict = Depends(get_admin_user),
    nome_evento: str = Form(None),
    data_evento: str = Form(None),
    cidade: str = Form(None),
    estado: str = Form(None),
    valor_inscricao: str = Form(None),
    link_inscricao: str = Form(None),
    link_resultado: str = Form(None),
    link_fotos: str = Form(None),
    link_instagram: str = Form(None),
    imagem: UploadFile = File(None)
):
    """Edita uma corrida parceira existente."""
    corrida = await db.corridas_parceiras.find_one({"id": corrida_id}, {"_id": 0})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")

    update_data = {}
    if nome_evento is not None:
        update_data["nome_evento"] = nome_evento
    if data_evento is not None:
        update_data["data_evento"] = data_evento
    if cidade is not None:
        update_data["cidade"] = cidade
    if estado is not None:
        update_data["estado"] = estado
    if valor_inscricao is not None:
        update_data["valor_inscricao"] = valor_inscricao
    if link_inscricao is not None:
        update_data["link_inscricao"] = link_inscricao
    if link_resultado is not None:
        update_data["link_resultado"] = link_resultado
    if link_fotos is not None:
        update_data["link_fotos"] = link_fotos
    if link_instagram is not None:
        update_data["link_instagram"] = link_instagram

    if imagem and imagem.filename:
        ext = imagem.filename.split(".")[-1].lower()
        nome_arquivo = f"{corrida_id}.{ext}"
        caminho = UPLOADS_DIR / nome_arquivo
        with open(caminho, "wb") as f:
            content = await imagem.read()
            f.write(content)
        update_data["imagem_url"] = f"/api/uploads/corridas_parceiras/{nome_arquivo}"

    if update_data:
        await db.corridas_parceiras.update_one(
            {"id": corrida_id}, {"$set": update_data}
        )

    updated = await db.corridas_parceiras.find_one({"id": corrida_id}, {"_id": 0})
    return updated


@router.delete("/admin/corridas-parceiras/{corrida_id}")
async def excluir_corrida(corrida_id: str, admin: dict = Depends(get_admin_user)):
    """Exclui uma corrida parceira."""
    result = await db.corridas_parceiras.delete_one({"id": corrida_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    return {"message": "Corrida excluída com sucesso"}


# ==================== TRACKING DE CLICKS ====================

@router.post("/corridas-parceiras/{corrida_id}/click")
async def registrar_click(
    corrida_id: str,
    tipo: str = Query(..., description="inscricao|resultado|fotos|instagram"),
    current_user: dict = Depends(get_current_user)
):
    """Registra um click em um botão da corrida parceira."""
    tipos_validos = ["inscricao", "resultado", "fotos", "instagram"]
    if tipo not in tipos_validos:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Use: {tipos_validos}")

    # Incrementar contador na corrida
    await db.corridas_parceiras.update_one(
        {"id": corrida_id},
        {"$inc": {f"clicks.{tipo}": 1}}
    )

    # Registrar click detalhado para métricas
    click = {
        "id": str(uuid.uuid4()),
        "corrida_id": corrida_id,
        "tipo": tipo,
        "usuario_id": current_user.get("id"),
        "cidade": current_user.get("cidade", ""),
        "estado": current_user.get("estado", ""),
        "data_click": datetime.now(timezone.utc).isoformat()
    }
    await db.clicks_corridas_parceiras.insert_one(click)

    return {"success": True}


# ==================== DASHBOARD / MÉTRICAS ====================

@router.get("/admin/corridas-parceiras/stats")
async def dashboard_stats(admin: dict = Depends(get_admin_user)):
    """Retorna métricas de clicks das corridas parceiras."""
    # Total de corridas
    total_corridas = await db.corridas_parceiras.count_documents({})

    # Total de clicks
    total_clicks = await db.clicks_corridas_parceiras.count_documents({})

    # Clicks por corrida
    corridas = await db.corridas_parceiras.find(
        {}, {"_id": 0, "id": 1, "nome_evento": 1, "clicks": 1}
    ).to_list(200)

    # Clicks por tipo
    clicks_por_tipo = {"inscricao": 0, "resultado": 0, "fotos": 0, "instagram": 0}
    for c in corridas:
        for tipo in clicks_por_tipo:
            clicks_por_tipo[tipo] += c.get("clicks", {}).get(tipo, 0)

    # Top corridas por clicks
    top_corridas = sorted(
        corridas,
        key=lambda x: sum(x.get("clicks", {}).values()),
        reverse=True
    )[:10]

    # Clicks por região (estado/cidade)
    pipeline = [
        {"$group": {
            "_id": {"estado": "$estado", "cidade": "$cidade"},
            "total": {"$sum": 1}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 15}
    ]
    regioes = []
    async for doc in db.clicks_corridas_parceiras.aggregate(pipeline):
        regioes.append({
            "estado": doc["_id"].get("estado", ""),
            "cidade": doc["_id"].get("cidade", ""),
            "total": doc["total"]
        })

    return {
        "total_corridas": total_corridas,
        "total_clicks": total_clicks,
        "clicks_por_tipo": clicks_por_tipo,
        "top_corridas": top_corridas,
        "clicks_por_regiao": regioes
    }
