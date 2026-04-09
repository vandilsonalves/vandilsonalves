# /app/backend/routes/parceiros_routes.py
# CRUD de Parceiros/Patrocinadores

import uuid
import io
import shutil
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from config import db
from routes.auth_routes import get_admin_user

router = APIRouter()

UPLOADS_DIR = Path("/app/uploads/parceiros")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ==================== PUBLIC ====================

@router.get("/parceiros")
async def listar_parceiros():
    """Lista todos os parceiros (público)."""
    parceiros = await db.parceiros.find(
        {"ativo": True}, {"_id": 0}
    ).sort("ordem", 1).to_list(None)
    return parceiros


# ==================== ADMIN ====================

@router.get("/admin/parceiros")
async def admin_listar_parceiros(admin: dict = Depends(get_admin_user)):
    """Lista todos os parceiros (admin)."""
    parceiros = await db.parceiros.find({}, {"_id": 0}).sort("created_at", -1).to_list(None)
    return parceiros


@router.post("/admin/parceiros")
async def criar_parceiro(
    admin: dict = Depends(get_admin_user),
    nome: str = Form(""),
    instagram: str = Form(""),
    site: str = Form(""),
    imagem: UploadFile = File(None),
):
    """Cria um novo parceiro."""
    parceiro_id = str(uuid.uuid4())[:8]
    imagem_url = ""

    if imagem and imagem.filename:
        from services.object_storage import upload_file as cloud_upload
        img_data = imagem.file.read()
        result = cloud_upload(img_data, imagem.filename, pasta="parceiros")
        imagem_url = result["url"]

    doc = {
        "id": parceiro_id,
        "nome": nome,
        "instagram": instagram,
        "site": site,
        "imagem_url": imagem_url,
        "ativo": True,
        "ordem": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.parceiros.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.put("/admin/parceiros/{parceiro_id}")
async def editar_parceiro(
    parceiro_id: str,
    admin: dict = Depends(get_admin_user),
    nome: str = Form(""),
    instagram: str = Form(""),
    site: str = Form(""),
    imagem: UploadFile = File(None),
):
    """Edita um parceiro existente."""
    existing = await db.parceiros.find_one({"id": parceiro_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Parceiro não encontrado")

    update = {
        "nome": nome,
        "instagram": instagram,
        "site": site,
    }

    if imagem and imagem.filename:
        from services.object_storage import upload_file as cloud_upload
        img_data = imagem.file.read()
        result = cloud_upload(img_data, imagem.filename, pasta="parceiros")
        update["imagem_url"] = result["url"]

    await db.parceiros.update_one({"id": parceiro_id}, {"$set": update})
    return {"success": True}


@router.delete("/admin/parceiros/{parceiro_id}")
async def deletar_parceiro(parceiro_id: str, admin: dict = Depends(get_admin_user)):
    """Remove um parceiro."""
    result = await db.parceiros.delete_one({"id": parceiro_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Parceiro não encontrado")
    return {"success": True}


@router.post("/admin/parceiros/upload-imagem")
async def upload_imagem_parceiro(
    admin: dict = Depends(get_admin_user),
    imagem: UploadFile = File(...),
):
    """Upload avulso de imagem (retorna URL)."""
    from services.object_storage import upload_file as cloud_upload
    img_data = imagem.file.read()
    result = cloud_upload(img_data, imagem.filename or "parceiro.png", pasta="parceiros")
    return {"imagem_url": result["url"]}


# ==================== EXPORTAÇÃO EXCEL ====================

@router.get("/admin/parceiros/export-excel")
async def exportar_parceiros_excel(admin: dict = Depends(get_admin_user)):
    """Exporta parceiros em Excel."""
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill

    parceiros = await db.parceiros.find({}, {"_id": 0}).sort("created_at", -1).to_list(None)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Parceiros"

    headers = ["Nome", "Instagram", "Site", "Imagem URL", "Ativo", "Data Cadastro"]
    header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for row, p in enumerate(parceiros, 2):
        ws.cell(row=row, column=1, value=p.get("nome", ""))
        ws.cell(row=row, column=2, value=p.get("instagram", ""))
        ws.cell(row=row, column=3, value=p.get("site", ""))
        ws.cell(row=row, column=4, value=p.get("imagem_url", ""))
        ws.cell(row=row, column=5, value="Sim" if p.get("ativo") else "Não")
        ws.cell(row=row, column=6, value=p.get("created_at", "")[:10])

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[chr(64 + col)].width = 25

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=parceiros_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )
