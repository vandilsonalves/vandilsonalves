# /app/backend/routes/mensagens_admin_routes.py
# Módulo de Mensagens do Admin - envio em massa para atletas

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
import uuid
import os
import shutil
from datetime import datetime, timezone

ANO_ATUAL = datetime.now(timezone.utc).year

from config import db
from routes.auth_routes import get_current_user

router = APIRouter(tags=["Mensagens Admin"])

UPLOAD_DIR = "/app/backend/uploads/mensagens"
os.makedirs(UPLOAD_DIR, exist_ok=True)

BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", os.environ.get("FRONTEND_URL", ""))


def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito a admins")
    return current_user


@router.post("/admin/mensagens/upload")
async def upload_arquivo(
    arquivo: UploadFile = File(...),
    admin: dict = Depends(get_admin_user)
):
    """Upload de arquivo/imagem para mensagens"""
    ext = os.path.splitext(arquivo.filename)[1].lower()
    allowed = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt', '.zip']
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Tipo de arquivo não permitido: {ext}")

    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{arquivo.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(arquivo.file, f)

    is_image = ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']

    return {
        "filename": filename,
        "original_name": arquivo.filename,
        "url": f"/api/admin/mensagens/arquivo/{filename}",
        "tipo": "imagem" if is_image else "arquivo",
        "tamanho": os.path.getsize(filepath)
    }


@router.get("/admin/mensagens/arquivo/{filename}")
async def servir_arquivo(filename: str):
    """Serve arquivos enviados nas mensagens"""
    from fastapi.responses import FileResponse
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(filepath)


@router.post("/admin/mensagens/enviar")
async def enviar_mensagem_admin(
    titulo: str = Form(""),
    mensagem: str = Form(""),
    link: str = Form(""),
    anexos: str = Form("[]"),
    filtro_tipo: str = Form("todos"),
    filtro_modalidades: str = Form("[]"),
    filtro_generos: str = Form("[]"),
    filtro_especial: str = Form("[]"),
    admin: dict = Depends(get_admin_user)
):
    """
    Envia mensagem para atletas com filtros.
    filtro_tipo: todos | modalidade | genero | especial | individual
    filtro_modalidades: ["profissional_amador", "povao_pace_livre"]
    filtro_generos: ["M", "F", "pcd_m", "pcd_f", "cadeirante_m", "cadeirante_f"]
    filtro_especial: ["donos_assessoria", "individual_sem_assessoria"]
    """
    import json

    if not mensagem.strip() and not link.strip():
        raise HTTPException(status_code=400, detail="Mensagem ou link é obrigatório")

    modalidades = json.loads(filtro_modalidades) if filtro_modalidades != "[]" else []
    generos = json.loads(filtro_generos) if filtro_generos != "[]" else []
    especiais = json.loads(filtro_especial) if filtro_especial != "[]" else []
    anexos_list = json.loads(anexos) if anexos != "[]" else []

    # Build query for target users
    query = {"role": {"$in": ["atleta", "dono_assessoria"]}}

    if filtro_tipo == "todos":
        pass  # No additional filter
    elif filtro_tipo == "modalidade" and modalidades:
        # Determine users by which ranking collection they belong to
        modalidade_ids = set()
        if "profissional_amador" in modalidades:
            anual_ids = await db.ranking_anual.distinct("usuario_id", {"ano": ANO_ATUAL})
            modalidade_ids.update(anual_ids)
        if "povao_pace_livre" in modalidades:
            povao_ids = await db.ranking_povao.distinct("usuario_id", {"ano": ANO_ATUAL})
            modalidade_ids.update(povao_ids)
        if modalidade_ids:
            query["id"] = {"$in": list(modalidade_ids)}
        else:
            return {"ranking": [], "total": 0} if "contagem" not in str(type(query)) else query
    elif filtro_tipo == "genero" and generos:
        genero_conditions = []
        for g in generos:
            if g == "M":
                genero_conditions.append({"$or": [{"genero": "M"}, {"sexo": "M"}], "categoria": {"$in": ["normal", None, ""]}})
            elif g == "F":
                genero_conditions.append({"$or": [{"genero": "F"}, {"sexo": "F"}], "categoria": {"$in": ["normal", None, ""]}})
            elif g == "pcd_m":
                genero_conditions.append({"$or": [{"genero": "M"}, {"sexo": "M"}], "categoria": "pcd"})
            elif g == "pcd_f":
                genero_conditions.append({"$or": [{"genero": "F"}, {"sexo": "F"}], "categoria": "pcd"})
            elif g == "cadeirante_m":
                genero_conditions.append({"$or": [{"genero": "M"}, {"sexo": "M"}], "categoria": "cadeirante"})
            elif g == "cadeirante_f":
                genero_conditions.append({"$or": [{"genero": "F"}, {"sexo": "F"}], "categoria": "cadeirante"})
        if genero_conditions:
            query["$or"] = genero_conditions
    elif filtro_tipo == "especial" and especiais:
        conditions = []
        if "donos_assessoria" in especiais:
            conditions.append({"role": "dono_assessoria"})
        if "individual_sem_assessoria" in especiais:
            conditions.append({"role": "atleta", "$or": [{"equipe": {"$in": [None, "", "INDIVIDUAL"]}}, {"equipe": {"$exists": False}}]})
        if conditions:
            query = {"$or": conditions}

    # Get target users
    destinatarios = await db.usuarios.find(query, {"_id": 0, "id": 1}).to_list(None)
    destinatario_ids = [d["id"] for d in destinatarios]

    if not destinatario_ids:
        raise HTTPException(status_code=400, detail="Nenhum destinatário encontrado com os filtros selecionados")

    # Create notifications for each user
    agora = datetime.now(timezone.utc).isoformat()
    mensagem_id = str(uuid.uuid4())

    notificacoes_criadas = 0
    for uid in destinatario_ids:
        notificacao = {
            "id": str(uuid.uuid4()),
            "mensagem_id": mensagem_id,
            "usuario_id": uid,
            "tipo": "mensagem_admin",
            "titulo": titulo or "Mensagem da Administração",
            "mensagem": mensagem,
            "link": link if link.strip() else None,
            "anexos": anexos_list,
            "lida": False,
            "data_criacao": agora,
            "remetente_id": admin["id"],
            "remetente_nome": "Ranking Run"
        }
        await db.notificacoes.insert_one(notificacao)
        notificacoes_criadas += 1

    # Save message record for history
    registro = {
        "id": mensagem_id,
        "titulo": titulo or "Mensagem da Administração",
        "mensagem": mensagem,
        "link": link if link.strip() else None,
        "anexos": anexos_list,
        "filtro_tipo": filtro_tipo,
        "filtro_modalidades": modalidades,
        "filtro_generos": generos,
        "filtro_especial": especiais,
        "total_enviados": notificacoes_criadas,
        "admin_id": admin["id"],
        "admin_nome": admin.get("nome", "Admin"),
        "data_envio": agora
    }
    await db.mensagens_admin.insert_one(registro)

    return {
        "message": f"Mensagem enviada para {notificacoes_criadas} atleta(s)",
        "total_enviados": notificacoes_criadas,
        "mensagem_id": mensagem_id
    }


@router.get("/admin/mensagens/historico")
async def historico_mensagens(admin: dict = Depends(get_admin_user)):
    """Lista histórico de mensagens enviadas"""
    mensagens = await db.mensagens_admin.find(
        {},
        {"_id": 0}
    ).sort("data_envio", -1).limit(50).to_list(None)

    return {"mensagens": mensagens}


@router.get("/admin/mensagens/contagem-destinatarios")
async def contagem_destinatarios(
    filtro_tipo: str = "todos",
    filtro_modalidades: str = "[]",
    filtro_generos: str = "[]",
    filtro_especial: str = "[]",
    admin: dict = Depends(get_admin_user)
):
    """Retorna quantos atletas serão impactados pelos filtros"""
    import json

    query = {"role": {"$in": ["atleta", "dono_assessoria"]}}

    modalidades = json.loads(filtro_modalidades) if filtro_modalidades != "[]" else []
    generos = json.loads(filtro_generos) if filtro_generos != "[]" else []
    especiais = json.loads(filtro_especial) if filtro_especial != "[]" else []

    if filtro_tipo == "todos":
        pass
    elif filtro_tipo == "modalidade" and modalidades:
        modalidade_ids = set()
        if "profissional_amador" in modalidades:
            anual_ids = await db.ranking_anual.distinct("usuario_id", {"ano": ANO_ATUAL})
            modalidade_ids.update(anual_ids)
        if "povao_pace_livre" in modalidades:
            povao_ids = await db.ranking_povao.distinct("usuario_id", {"ano": ANO_ATUAL})
            modalidade_ids.update(povao_ids)
        if modalidade_ids:
            query["id"] = {"$in": list(modalidade_ids)}
        else:
            return {"total": 0}
    elif filtro_tipo == "genero" and generos:
        genero_conditions = []
        for g in generos:
            if g == "M":
                genero_conditions.append({"$or": [{"genero": "M"}, {"sexo": "M"}], "categoria": {"$in": ["normal", None, ""]}})
            elif g == "F":
                genero_conditions.append({"$or": [{"genero": "F"}, {"sexo": "F"}], "categoria": {"$in": ["normal", None, ""]}})
            elif g == "pcd_m":
                genero_conditions.append({"$or": [{"genero": "M"}, {"sexo": "M"}], "categoria": "pcd"})
            elif g == "pcd_f":
                genero_conditions.append({"$or": [{"genero": "F"}, {"sexo": "F"}], "categoria": "pcd"})
            elif g == "cadeirante_m":
                genero_conditions.append({"$or": [{"genero": "M"}, {"sexo": "M"}], "categoria": "cadeirante"})
            elif g == "cadeirante_f":
                genero_conditions.append({"$or": [{"genero": "F"}, {"sexo": "F"}], "categoria": "cadeirante"})
        if genero_conditions:
            query["$or"] = genero_conditions
    elif filtro_tipo == "especial" and especiais:
        conditions = []
        if "donos_assessoria" in especiais:
            conditions.append({"role": "dono_assessoria"})
        if "individual_sem_assessoria" in especiais:
            conditions.append({"role": "atleta", "$or": [{"equipe": {"$in": [None, "", "INDIVIDUAL"]}}, {"equipe": {"$exists": False}}]})
        if conditions:
            query = {"$or": conditions}

    total = await db.usuarios.count_documents(query)
    return {"total": total}
