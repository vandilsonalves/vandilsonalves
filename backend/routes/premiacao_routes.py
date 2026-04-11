"""
Rotas de Premiação / Votação - PRÊMIO NACIONAL RANKING RUN
Troféu Destaque Internet - Sistema de indicação aberta
"""
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import io

router = APIRouter(prefix="/premiacao", tags=["Premiação"])

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Auth dependencies
from routes.auth_routes import get_current_user, get_admin_user

# ==================== MODELS ====================

class CategoriaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = ""
    icone: Optional[str] = "trophy"

class VotoCreate(BaseModel):
    categoria_id: str
    nome_indicado: str
    link_indicado: Optional[str] = ""

class ConsolidarModel(BaseModel):
    nome_principal: str
    nomes_variantes: List[str]

# ==================== ADMIN: Gerenciar Premiação ====================

@router.get("/admin/config")
async def get_premiacao_config(current_user: dict = Depends(get_admin_user)):
    config = await db.premiacao_config.find_one({"id": "config_atual"}, {"_id": 0})
    if not config:
        config = {
            "id": "config_atual",
            "titulo": "PRÊMIO NACIONAL RANKING RUN",
            "subtitulo": "Troféu Destaque Internet",
            "ano": datetime.now().year,
            "votacao_aberta": False,
            "data_abertura": None,
            "data_encerramento": None
        }
        await db.premiacao_config.insert_one(config)
    return config


@router.put("/admin/config")
async def update_premiacao_config(dados: dict, current_user: dict = Depends(get_admin_user)):
    campos = {}
    for key in ["titulo", "subtitulo", "ano", "data_limite", "data_abertura_programada", "data_encerramento_programada"]:
        if key in dados:
            campos[key] = dados[key]
    if campos:
        await db.premiacao_config.update_one(
            {"id": "config_atual"},
            {"$set": campos},
            upsert=True
        )
    return {"message": "Configuração atualizada"}


@router.post("/admin/foto")
async def upload_foto_premiacao(foto: UploadFile = File(...), current_user: dict = Depends(get_admin_user)):
    """Upload de foto/logo da premiação"""
    data = await foto.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande (max 5MB)")
    try:
        from services.object_storage import upload_file
        result = upload_file(data, foto.filename, pasta="premiacao")
        url = result.get("url", "")
        await db.premiacao_config.update_one(
            {"id": "config_atual"},
            {"$set": {"foto_url": url}},
            upsert=True
        )
        return {"message": "Foto enviada!", "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")


@router.get("/admin/exportar-excel")
async def exportar_votos_excel(current_user: dict = Depends(get_admin_user)):
    """Exporta todos os votos em Excel com dados completos"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment

    categorias = await db.premiacao_categorias.find({}, {"_id": 0}).sort("ordem", 1).to_list(100)
    cat_map = {c["id"]: c["nome"] for c in categorias}

    votos = await db.premiacao_votos.find({}, {"_id": 0}).sort("data_voto", -1).to_list(10000)

    wb = Workbook()
    ws = wb.active
    ws.title = "Votos Premiação"

    headers = ["Categoria", "Nome Indicado", "Link", "Atleta Nome", "Atleta Email", "Atleta ID", "Data/Hora", "IP", "ID Voto"]
    header_fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for i, v in enumerate(votos, 2):
        ws.cell(row=i, column=1, value=cat_map.get(v.get("categoria_id", ""), "Desconhecida"))
        ws.cell(row=i, column=2, value=v.get("nome_indicado", ""))
        ws.cell(row=i, column=3, value=v.get("link_indicado", ""))
        ws.cell(row=i, column=4, value=v.get("atleta_nome", ""))
        ws.cell(row=i, column=5, value=v.get("atleta_email", ""))
        ws.cell(row=i, column=6, value=v.get("atleta_id", ""))
        ws.cell(row=i, column=7, value=v.get("data_voto", ""))
        ws.cell(row=i, column=8, value=v.get("ip", ""))
        ws.cell(row=i, column=9, value=v.get("id", ""))

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[chr(64 + col)].width = 22

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=votos_premiacao_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )


@router.post("/admin/abrir")
async def abrir_votacao(current_user: dict = Depends(get_admin_user)):
    await db.premiacao_config.update_one(
        {"id": "config_atual"},
        {"$set": {
            "votacao_aberta": True,
            "data_abertura": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"message": "Votação aberta com sucesso!"}


@router.post("/admin/fechar")
async def fechar_votacao(current_user: dict = Depends(get_admin_user)):
    await db.premiacao_config.update_one(
        {"id": "config_atual"},
        {"$set": {
            "votacao_aberta": False,
            "data_encerramento": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"message": "Votação encerrada com sucesso!"}


# ==================== ADMIN: Categorias ====================

@router.get("/admin/categorias")
async def listar_categorias_admin(current_user: dict = Depends(get_admin_user)):
    cats = await db.premiacao_categorias.find({}, {"_id": 0}).sort("ordem", 1).to_list(100)
    # Add vote counts
    for cat in cats:
        total = await db.premiacao_votos.count_documents({"categoria_id": cat["id"]})
        cat["total_votos"] = total
    return cats


@router.post("/admin/categorias")
async def criar_categoria(cat: CategoriaCreate, current_user: dict = Depends(get_admin_user)):
    import uuid
    count = await db.premiacao_categorias.count_documents({})
    doc = {
        "id": str(uuid.uuid4())[:8],
        "nome": cat.nome,
        "descricao": cat.descricao,
        "icone": cat.icone,
        "ordem": count + 1,
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "criado_por": current_user.get("nome", "admin")
    }
    await db.premiacao_categorias.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.put("/admin/categorias/{cat_id}")
async def editar_categoria(cat_id: str, dados: dict, current_user: dict = Depends(get_admin_user)):
    campos = {}
    for key in ["nome", "descricao", "icone", "ordem"]:
        if key in dados:
            campos[key] = dados[key]
    if campos:
        await db.premiacao_categorias.update_one({"id": cat_id}, {"$set": campos})
    return {"message": "Categoria atualizada"}


@router.delete("/admin/categorias/{cat_id}")
async def excluir_categoria(cat_id: str, current_user: dict = Depends(get_admin_user)):
    await db.premiacao_categorias.delete_one({"id": cat_id})
    await db.premiacao_votos.delete_many({"categoria_id": cat_id})
    return {"message": "Categoria e votos removidos"}


# ==================== ADMIN: Resultados e Consolidação ====================

@router.get("/admin/resultados")
async def get_resultados_admin(current_user: dict = Depends(get_admin_user)):
    categorias = await db.premiacao_categorias.find({}, {"_id": 0}).sort("ordem", 1).to_list(100)
    resultados = []

    for cat in categorias:
        pipeline = [
            {"$match": {"categoria_id": cat["id"]}},
            {"$group": {
                "_id": {"$toLower": {"$trim": {"input": "$nome_indicado"}}},
                "nome_display": {"$first": "$nome_indicado"},
                "link": {"$first": "$link_indicado"},
                "total_votos": {"$sum": 1},
                "votantes": {"$push": {
                    "atleta_nome": "$atleta_nome",
                    "atleta_id": "$atleta_id",
                    "data": "$data_voto"
                }}
            }},
            {"$sort": {"total_votos": -1}},
            {"$limit": 20}
        ]
        indicados = await db.premiacao_votos.aggregate(pipeline).to_list(20)
        
        total_votos_cat = await db.premiacao_votos.count_documents({"categoria_id": cat["id"]})
        
        resultados.append({
            "categoria": cat,
            "total_votos": total_votos_cat,
            "indicados": [{
                "nome": ind["nome_display"],
                "nome_normalizado": ind["_id"],
                "link": ind.get("link", ""),
                "votos": ind["total_votos"],
                "votantes": ind["votantes"][:10]
            } for ind in indicados]
        })

    return resultados


@router.post("/admin/consolidar/{cat_id}")
async def consolidar_indicados(cat_id: str, dados: ConsolidarModel, current_user: dict = Depends(get_admin_user)):
    """Unifica variações de nome de um indicado"""
    count = 0
    for variante in dados.nomes_variantes:
        result = await db.premiacao_votos.update_many(
            {
                "categoria_id": cat_id,
                "nome_indicado": {"$regex": f"^{variante}$", "$options": "i"}
            },
            {"$set": {"nome_indicado": dados.nome_principal}}
        )
        count += result.modified_count
    
    return {"message": f"{count} votos consolidados para '{dados.nome_principal}'"}


@router.get("/admin/votos-detalhados/{cat_id}")
async def get_votos_detalhados(cat_id: str, current_user: dict = Depends(get_admin_user)):
    votos = await db.premiacao_votos.find(
        {"categoria_id": cat_id}, 
        {"_id": 0}
    ).sort("data_voto", -1).to_list(500)
    return votos


@router.delete("/admin/votos/{voto_id}")
async def invalidar_voto(voto_id: str, current_user: dict = Depends(get_admin_user)):
    await db.premiacao_votos.delete_one({"id": voto_id})
    return {"message": "Voto invalidado"}


# ==================== ATLETA: Votação ====================

@router.get("/status")
async def get_status_votacao():
    """Retorna se a votação está aberta (público)"""
    config = await db.premiacao_config.find_one({"id": "config_atual"}, {"_id": 0})
    if not config:
        return {"votacao_aberta": False}
    return {
        "votacao_aberta": config.get("votacao_aberta", False),
        "titulo": config.get("titulo", "PRÊMIO NACIONAL RANKING RUN"),
        "subtitulo": config.get("subtitulo", "Troféu Destaque Internet"),
        "ano": config.get("ano", datetime.now().year),
        "data_limite": config.get("data_limite", None),
        "foto_url": config.get("foto_url", None),
        "data_abertura_programada": config.get("data_abertura_programada", None),
        "data_encerramento_programada": config.get("data_encerramento_programada", None)
    }


@router.get("/categorias")
async def listar_categorias_publico():
    """Lista categorias (público, sem dados de votos)"""
    cats = await db.premiacao_categorias.find({}, {"_id": 0}).sort("ordem", 1).to_list(100)
    return cats


@router.get("/meus-votos")
async def get_meus_votos(current_user: dict = Depends(get_current_user)):
    """Retorna os votos do atleta logado"""
    votos = await db.premiacao_votos.find(
        {"atleta_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    return votos


@router.post("/votar")
async def votar(voto: VotoCreate, request: Request, current_user: dict = Depends(get_current_user)):
    """Atleta vota/indica em uma categoria"""
    # Verificar se votação está aberta
    config = await db.premiacao_config.find_one({"id": "config_atual"})
    if not config or not config.get("votacao_aberta"):
        raise HTTPException(status_code=400, detail="A votação não está aberta no momento")

    # Verificar se categoria existe
    cat = await db.premiacao_categorias.find_one({"id": voto.categoria_id})
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    if not voto.nome_indicado.strip():
        raise HTTPException(status_code=400, detail="Nome do indicado é obrigatório")

    if not (voto.link_indicado or "").strip():
        raise HTTPException(status_code=400, detail="Link do Site Oficial ou Instagram é obrigatório")

    import uuid
    # Verificar se já votou nesta categoria
    voto_existente = await db.premiacao_votos.find_one({
        "atleta_id": current_user["id"],
        "categoria_id": voto.categoria_id
    })

    ip = request.client.host if request.client else "unknown"

    if voto_existente:
        # Atualizar voto existente
        await db.premiacao_votos.update_one(
            {"id": voto_existente["id"]},
            {"$set": {
                "nome_indicado": voto.nome_indicado.strip(),
                "link_indicado": (voto.link_indicado or "").strip(),
                "data_voto": datetime.now(timezone.utc).isoformat(),
                "ip": ip
            }}
        )
        return {"message": "Voto atualizado com sucesso!", "atualizado": True}
    else:
        doc = {
            "id": str(uuid.uuid4())[:12],
            "categoria_id": voto.categoria_id,
            "atleta_id": current_user["id"],
            "atleta_nome": current_user.get("nome", ""),
            "atleta_email": current_user.get("email", ""),
            "nome_indicado": voto.nome_indicado.strip(),
            "link_indicado": (voto.link_indicado or "").strip(),
            "data_voto": datetime.now(timezone.utc).isoformat(),
            "ip": ip
        }
        await db.premiacao_votos.insert_one(doc)
        return {"message": "Voto registrado com sucesso!", "atualizado": False}


@router.get("/resultados-publicos")
async def get_resultados_publicos():
    """Retorna resultados SOMENTE se a votação estiver encerrada"""
    config = await db.premiacao_config.find_one({"id": "config_atual"})
    if not config:
        raise HTTPException(status_code=404, detail="Premiação não configurada")
    
    if config.get("votacao_aberta", False):
        raise HTTPException(status_code=403, detail="Resultados disponíveis apenas após encerramento da votação")

    if not config.get("data_encerramento"):
        raise HTTPException(status_code=403, detail="A votação ainda não foi encerrada")

    categorias = await db.premiacao_categorias.find({}, {"_id": 0}).sort("ordem", 1).to_list(100)
    resultados = []

    for cat in categorias:
        pipeline = [
            {"$match": {"categoria_id": cat["id"]}},
            {"$group": {
                "_id": {"$toLower": {"$trim": {"input": "$nome_indicado"}}},
                "nome_display": {"$first": "$nome_indicado"},
                "link": {"$first": "$link_indicado"},
                "total_votos": {"$sum": 1}
            }},
            {"$sort": {"total_votos": -1}},
            {"$limit": 3}
        ]
        top3 = await db.premiacao_votos.aggregate(pipeline).to_list(3)
        total = await db.premiacao_votos.count_documents({"categoria_id": cat["id"]})

        resultados.append({
            "categoria": cat,
            "total_votos": total,
            "top3": [{
                "posicao": i + 1,
                "nome": ind["nome_display"],
                "link": ind.get("link", ""),
                "votos": ind["total_votos"]
            } for i, ind in enumerate(top3)]
        })

    return {
        "titulo": config.get("titulo"),
        "subtitulo": config.get("subtitulo"),
        "ano": config.get("ano"),
        "data_encerramento": config.get("data_encerramento"),
        "resultados": resultados
    }
