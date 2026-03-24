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
    filtro_estados: str = Form("[]"),
    filtro_cidades: str = Form("[]"),
    agendar_para: str = Form(""),
    admin: dict = Depends(get_admin_user)
):
    """
    Envia mensagem imediatamente ou agenda para envio futuro.
    agendar_para: ISO datetime string (ex: "2026-03-25T10:00") ou vazio para envio imediato
    """
    import json

    if not mensagem.strip() and not link.strip():
        raise HTTPException(status_code=400, detail="Mensagem ou link é obrigatório")

    modalidades = json.loads(filtro_modalidades) if filtro_modalidades != "[]" else []
    generos = json.loads(filtro_generos) if filtro_generos != "[]" else []
    especiais = json.loads(filtro_especial) if filtro_especial != "[]" else []
    estados = json.loads(filtro_estados) if filtro_estados != "[]" else []
    cidades = json.loads(filtro_cidades) if filtro_cidades != "[]" else []
    anexos_list = json.loads(anexos) if anexos != "[]" else []

    agora = datetime.now(timezone.utc).isoformat()
    mensagem_id = str(uuid.uuid4())
    is_agendada = bool(agendar_para and agendar_para.strip())

    # Save message record
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
        "filtro_estados": estados,
        "filtro_cidades": cidades,
        "total_enviados": 0,
        "admin_id": admin["id"],
        "admin_nome": admin.get("nome", "Admin"),
        "data_criacao": agora,
        "data_envio": None if is_agendada else agora,
        "agendar_para": agendar_para.strip() if is_agendada else None,
        "status": "agendada" if is_agendada else "enviada"
    }

    if is_agendada:
        await db.mensagens_admin.insert_one(registro)
        return {
            "message": f"Mensagem agendada para {agendar_para}",
            "total_enviados": 0,
            "mensagem_id": mensagem_id,
            "status": "agendada"
        }

    # Envio imediato - build query and send
    total = await _enviar_notificacoes(mensagem_id, titulo, mensagem, link, anexos_list,
                                         filtro_tipo, modalidades, generos, especiais, admin,
                                         estados, cidades)

    registro["total_enviados"] = total
    await db.mensagens_admin.insert_one(registro)

    return {
        "message": f"Mensagem enviada para {total} atleta(s)",
        "total_enviados": total,
        "mensagem_id": mensagem_id,
        "status": "enviada"
    }


async def _build_destinatarios_query(filtro_tipo, modalidades, generos, especiais, estados=None, cidades=None):
    """Constrói a query MongoDB para filtrar destinatários"""
    query = {"role": {"$in": ["atleta", "dono_assessoria"]}}

    if filtro_tipo == "todos":
        pass
    elif filtro_tipo == "estado" and estados:
        query["estado"] = {"$in": estados}
    elif filtro_tipo == "cidade" and cidades:
        query["cidade"] = {"$in": cidades}
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
            return None
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

    return query


async def _enviar_notificacoes(mensagem_id, titulo, mensagem, link, anexos_list,
                                filtro_tipo, modalidades, generos, especiais, admin,
                                estados=None, cidades=None):
    """Cria notificações para todos os destinatários que correspondem ao filtro"""
    query = await _build_destinatarios_query(filtro_tipo, modalidades, generos, especiais, estados, cidades)
    if not query:
        return 0

    destinatarios = await db.usuarios.find(query, {"_id": 0, "id": 1}).to_list(None)
    destinatario_ids = [d["id"] for d in destinatarios]

    if not destinatario_ids:
        return 0

    agora = datetime.now(timezone.utc).isoformat()
    notificacoes_criadas = 0
    for uid in destinatario_ids:
        notificacao = {
            "id": str(uuid.uuid4()),
            "mensagem_id": mensagem_id,
            "usuario_id": uid,
            "tipo": "mensagem_admin",
            "titulo": titulo or "Mensagem da Administração",
            "mensagem": mensagem,
            "link": link if link else None,
            "anexos": anexos_list,
            "lida": False,
            "data_criacao": agora,
            "remetente_id": admin.get("id", "system"),
            "remetente_nome": "Ranking Run"
        }
        await db.notificacoes.insert_one(notificacao)
        notificacoes_criadas += 1

    return notificacoes_criadas


@router.get("/admin/mensagens/historico")
async def historico_mensagens(admin: dict = Depends(get_admin_user)):
    """Lista histórico de mensagens enviadas e agendadas"""
    mensagens = await db.mensagens_admin.find(
        {},
        {"_id": 0}
    ).sort("data_criacao", -1).limit(50).to_list(None)

    return {"mensagens": mensagens}


@router.get("/admin/mensagens/agendadas")
async def listar_agendadas(admin: dict = Depends(get_admin_user)):
    """Lista mensagens agendadas pendentes"""
    agendadas = await db.mensagens_admin.find(
        {"status": "agendada"},
        {"_id": 0}
    ).sort("agendar_para", 1).to_list(None)

    return {"agendadas": agendadas}


@router.delete("/admin/mensagens/agendada/{mensagem_id}")
async def cancelar_agendada(mensagem_id: str, admin: dict = Depends(get_admin_user)):
    """Cancela uma mensagem agendada"""
    result = await db.mensagens_admin.update_one(
        {"id": mensagem_id, "status": "agendada"},
        {"$set": {"status": "cancelada", "data_cancelamento": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Mensagem agendada não encontrada")

    return {"message": "Mensagem agendada cancelada"}


@router.post("/admin/mensagens/processar-agendadas")
async def processar_agendadas():
    """
    Processa mensagens agendadas cujo horário já passou.
    Chamado pelo Celery beat ou manualmente.
    """
    agora = datetime.now(timezone.utc).isoformat()

    agendadas = await db.mensagens_admin.find(
        {"status": "agendada", "agendar_para": {"$lte": agora}},
        {"_id": 0}
    ).to_list(None)

    processadas = 0
    for msg in agendadas:
        admin_fake = {"id": msg.get("admin_id", "system"), "nome": msg.get("admin_nome", "Admin")}
        total = await _enviar_notificacoes(
            msg["id"], msg.get("titulo", ""), msg.get("mensagem", ""),
            msg.get("link", ""), msg.get("anexos", []),
            msg.get("filtro_tipo", "todos"), msg.get("filtro_modalidades", []),
            msg.get("filtro_generos", []), msg.get("filtro_especial", []),
            admin_fake, msg.get("filtro_estados", []), msg.get("filtro_cidades", [])
        )

        await db.mensagens_admin.update_one(
            {"id": msg["id"]},
            {"$set": {
                "status": "enviada",
                "total_enviados": total,
                "data_envio": agora
            }}
        )
        processadas += 1

    return {"processadas": processadas}


@router.get("/admin/mensagens/contagem-destinatarios")
async def contagem_destinatarios(
    filtro_tipo: str = "todos",
    filtro_modalidades: str = "[]",
    filtro_generos: str = "[]",
    filtro_especial: str = "[]",
    filtro_estados: str = "[]",
    filtro_cidades: str = "[]",
    admin: dict = Depends(get_admin_user)
):
    """Retorna quantos atletas serão impactados pelos filtros"""
    import json

    query = {"role": {"$in": ["atleta", "dono_assessoria"]}}

    modalidades = json.loads(filtro_modalidades) if filtro_modalidades != "[]" else []
    generos = json.loads(filtro_generos) if filtro_generos != "[]" else []
    especiais = json.loads(filtro_especial) if filtro_especial != "[]" else []
    estados = json.loads(filtro_estados) if filtro_estados != "[]" else []
    cidades = json.loads(filtro_cidades) if filtro_cidades != "[]" else []

    if filtro_tipo == "todos":
        pass
    elif filtro_tipo == "estado" and estados:
        query["estado"] = {"$in": estados}
    elif filtro_tipo == "cidade" and cidades:
        query["cidade"] = {"$in": cidades}
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


@router.get("/admin/mensagens/estados-disponiveis")
async def estados_disponiveis(admin: dict = Depends(get_admin_user)):
    """Lista todos os estados (UFs) com atletas cadastrados"""
    estados = await db.usuarios.distinct(
        "estado",
        {"role": {"$in": ["atleta", "dono_assessoria"]}, "estado": {"$exists": True, "$nin": [None, ""]}}
    )
    return {"estados": sorted(estados)}


@router.get("/admin/mensagens/cidades-disponiveis")
async def cidades_disponiveis(
    estado: str = "",
    admin: dict = Depends(get_admin_user)
):
    """Lista cidades com atletas cadastrados, opcionalmente filtradas por estado"""
    filtro = {"role": {"$in": ["atleta", "dono_assessoria"]}, "cidade": {"$exists": True, "$nin": [None, ""]}}
    if estado:
        filtro["estado"] = estado
    cidades = await db.usuarios.distinct("cidade", filtro)
    return {"cidades": sorted(cidades)}


@router.get("/admin/mensagens/{mensagem_id}/leitura")
async def stats_leitura_mensagem(mensagem_id: str, admin: dict = Depends(get_admin_user)):
    """Retorna estatísticas de leitura de uma mensagem específica"""
    msg = await db.mensagens_admin.find_one({"id": mensagem_id}, {"_id": 0})
    if not msg:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")

    # Count read/unread notifications
    total = await db.notificacoes.count_documents({"mensagem_id": mensagem_id, "tipo": "mensagem_admin"})
    lidas = await db.notificacoes.count_documents({"mensagem_id": mensagem_id, "tipo": "mensagem_admin", "lida": True})
    nao_lidas = total - lidas

    # Get list of unread users with their names
    nao_lidos_notifs = await db.notificacoes.find(
        {"mensagem_id": mensagem_id, "tipo": "mensagem_admin", "lida": False},
        {"_id": 0, "usuario_id": 1, "id": 1}
    ).to_list(None)

    nao_lidos_ids = [n["usuario_id"] for n in nao_lidos_notifs]

    # Fetch user details
    atletas_nao_leram = []
    if nao_lidos_ids:
        usuarios = await db.usuarios.find(
            {"id": {"$in": nao_lidos_ids}},
            {"_id": 0, "id": 1, "nome": 1, "email": 1, "equipe": 1, "estado": 1, "cidade": 1}
        ).to_list(None)
        atletas_nao_leram = usuarios

    # Get list of read users
    lidos_notifs = await db.notificacoes.find(
        {"mensagem_id": mensagem_id, "tipo": "mensagem_admin", "lida": True},
        {"_id": 0, "usuario_id": 1}
    ).to_list(None)
    lidos_ids = [n["usuario_id"] for n in lidos_notifs]
    atletas_leram = []
    if lidos_ids:
        usuarios_lidos = await db.usuarios.find(
            {"id": {"$in": lidos_ids}},
            {"_id": 0, "id": 1, "nome": 1, "email": 1, "equipe": 1}
        ).to_list(None)
        atletas_leram = usuarios_lidos

    return {
        "mensagem_id": mensagem_id,
        "titulo": msg.get("titulo", ""),
        "total_enviados": total,
        "total_lidas": lidas,
        "total_nao_lidas": nao_lidas,
        "percentual_leitura": round((lidas / total * 100) if total > 0 else 0, 1),
        "atletas_nao_leram": atletas_nao_leram,
        "atletas_leram": atletas_leram
    }


@router.post("/admin/mensagens/{mensagem_id}/reenviar-splash")
async def reenviar_como_splash(
    mensagem_id: str,
    admin: dict = Depends(get_admin_user)
):
    """
    Reenvia a mensagem como splash screen para todos que NÃO leram.
    O splash bloqueia a tela do atleta até ele confirmar a leitura.
    """
    msg = await db.mensagens_admin.find_one({"id": mensagem_id}, {"_id": 0})
    if not msg:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")

    # Find users who haven't read
    nao_lidos_notifs = await db.notificacoes.find(
        {"mensagem_id": mensagem_id, "tipo": "mensagem_admin", "lida": False},
        {"_id": 0, "usuario_id": 1, "id": 1}
    ).to_list(None)

    if not nao_lidos_notifs:
        return {"message": "Todos já leram esta mensagem!", "total_reenviados": 0}

    agora = datetime.now(timezone.utc).isoformat()
    splash_id = str(uuid.uuid4())
    reenviados = 0

    for notif in nao_lidos_notifs:
        # Create splash notification
        splash_notif = {
            "id": str(uuid.uuid4()),
            "mensagem_id": mensagem_id,
            "splash_id": splash_id,
            "usuario_id": notif["usuario_id"],
            "tipo": "splash_admin",
            "titulo": msg.get("titulo", "Mensagem Importante"),
            "mensagem": msg.get("mensagem", ""),
            "link": msg.get("link"),
            "anexos": msg.get("anexos", []),
            "lida": False,
            "data_criacao": agora,
            "remetente_id": admin.get("id", "system"),
            "remetente_nome": "Ranking Run"
        }
        await db.notificacoes.insert_one(splash_notif)
        reenviados += 1

    # Update mensagem_admin record
    await db.mensagens_admin.update_one(
        {"id": mensagem_id},
        {"$set": {
            "ultimo_reenvio_splash": agora,
            "total_splash_reenviados": reenviados
        }}
    )

    return {
        "message": f"Splash screen enviado para {reenviados} atleta(s) que não leram",
        "total_reenviados": reenviados,
        "splash_id": splash_id
    }


@router.get("/notificacoes/splash-pendente")
async def splash_pendente(current_user: dict = Depends(get_current_user)):
    """Retorna splash screen pendente do usuário (não lido)"""
    splash = await db.notificacoes.find_one(
        {"usuario_id": current_user["id"], "tipo": "splash_admin", "lida": False},
        {"_id": 0}
    )
    return {"splash": splash}


@router.post("/notificacoes/splash/{notificacao_id}/confirmar")
async def confirmar_splash(notificacao_id: str, current_user: dict = Depends(get_current_user)):
    """Marca splash screen como lido/confirmado"""
    result = await db.notificacoes.update_one(
        {"id": notificacao_id, "usuario_id": current_user["id"], "tipo": "splash_admin"},
        {"$set": {"lida": True, "data_leitura": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Splash não encontrado")

    # Also mark the original notification as read
    splash = await db.notificacoes.find_one({"id": notificacao_id}, {"_id": 0, "mensagem_id": 1, "usuario_id": 1})
    if splash and splash.get("mensagem_id"):
        await db.notificacoes.update_many(
            {"mensagem_id": splash["mensagem_id"], "usuario_id": current_user["id"], "tipo": "mensagem_admin"},
            {"$set": {"lida": True}}
        )

    return {"message": "Splash confirmado"}
