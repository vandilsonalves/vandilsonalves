# /app/backend/routes/autorizacoes_routes.py
# Rotas relacionadas a autorizações e período de teste

from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import uuid
import json
import os
import shutil

from config import db
from routes.auth_routes import get_current_user, get_admin_user

router = APIRouter()

ANO_ATUAL = datetime.now(timezone.utc).year

UPLOAD_DIR_AUT = "/app/backend/uploads/autorizacoes"
os.makedirs(UPLOAD_DIR_AUT, exist_ok=True)


class AutorizacaoCreate(BaseModel):
    atleta_id: str
    tipo: str = "completo"  # completo, parcial, teste
    duracao_dias: int = 365
    observacao: Optional[str] = None


@router.get("/autorizacoes")
async def listar_autorizacoes(admin: dict = Depends(get_admin_user)):
    """Lista todas as autorizações ativas"""
    
    autorizacoes = await db.autorizacoes.find(
        {"status": "ativa"},
        {"_id": 0}
    ).sort("data_criacao", -1).to_list(500)
    
    # Enriquecer com dados dos atletas
    for auth in autorizacoes:
        atleta = await db.usuarios.find_one(
            {"id": auth.get("atleta_id")},
            {"_id": 0, "nome": 1, "email": 1, "equipe": 1}
        )
        if atleta:
            auth["atleta_nome"] = atleta.get("nome")
            auth["atleta_email"] = atleta.get("email")
            auth["atleta_equipe"] = atleta.get("equipe")
    
    return {"autorizacoes": autorizacoes, "total": len(autorizacoes)}


@router.get("/atletas-periodo-teste")
async def listar_atletas_periodo_teste(admin: dict = Depends(get_admin_user)):
    """Lista atletas em período de teste"""
    
    # Buscar atletas criados nos últimos 30 dias sem autorização
    data_limite = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    
    atletas_novos = await db.usuarios.find(
        {
            "role": "atleta",
            "data_criacao": {"$gte": data_limite}
        },
        {"_id": 0, "id": 1, "nome": 1, "email": 1, "equipe": 1, "data_criacao": 1}
    ).to_list(500)
    
    # Verificar quais não têm autorização
    resultado = []
    for atleta in atletas_novos:
        auth = await db.autorizacoes.find_one({
            "atleta_id": atleta["id"],
            "status": "ativa"
        })
        if not auth:
            # Calcular dias restantes do período de teste
            data_criacao = datetime.fromisoformat(atleta["data_criacao"].replace("Z", "+00:00"))
            dias_desde_criacao = (datetime.now(timezone.utc) - data_criacao).days
            dias_restantes = max(0, 30 - dias_desde_criacao)
            atleta["dias_restantes_teste"] = dias_restantes
            atleta["em_periodo_teste"] = True
            resultado.append(atleta)
    
    return {"atletas": resultado, "total": len(resultado)}


@router.post("/autorizacoes")
async def criar_autorizacao(
    dados: AutorizacaoCreate,
    admin: dict = Depends(get_admin_user)
):
    """Cria uma nova autorização para um atleta"""
    
    # Verificar se atleta existe
    atleta = await db.usuarios.find_one({"id": dados.atleta_id})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Verificar se já existe autorização ativa
    auth_existente = await db.autorizacoes.find_one({
        "atleta_id": dados.atleta_id,
        "status": "ativa"
    })
    
    if auth_existente:
        raise HTTPException(status_code=400, detail="Atleta já possui autorização ativa")
    
    # Criar autorização
    data_expiracao = datetime.now(timezone.utc) + timedelta(days=dados.duracao_dias)
    
    autorizacao = {
        "id": str(uuid.uuid4()),
        "atleta_id": dados.atleta_id,
        "tipo": dados.tipo,
        "duracao_dias": dados.duracao_dias,
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "data_expiracao": data_expiracao.isoformat(),
        "criado_por": admin["id"],
        "criado_por_nome": admin.get("nome", "Admin"),
        "observacao": dados.observacao,
        "status": "ativa"
    }
    
    await db.autorizacoes.insert_one(autorizacao)
    
    return {
        "message": f"Autorização criada com sucesso. Válida até {data_expiracao.strftime('%d/%m/%Y')}",
        "autorizacao_id": autorizacao["id"]
    }


@router.delete("/autorizacoes/{autorizacao_id}")
async def revogar_autorizacao(autorizacao_id: str, admin: dict = Depends(get_admin_user)):
    """Revoga uma autorização"""
    
    result = await db.autorizacoes.update_one(
        {"id": autorizacao_id},
        {
            "$set": {
                "status": "revogada",
                "data_revogacao": datetime.now(timezone.utc).isoformat(),
                "revogado_por": admin["id"]
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Autorização não encontrada")
    
    return {"message": "Autorização revogada com sucesso"}


@router.get("/meu-status-acesso")
async def verificar_status_acesso(current_user: dict = Depends(get_current_user)):
    """Verifica o status de acesso do usuário logado"""
    
    # Admin e super_admin sempre têm acesso total
    if current_user.get("role") in ["admin", "super_admin"]:
        return {
            "tem_acesso": True,
            "tipo": "admin",
            "expira_em": None,
            "em_periodo_teste": False
        }
    
    # Verificar autorização
    auth = await db.autorizacoes.find_one({
        "atleta_id": current_user["id"],
        "status": "ativa"
    })
    
    if auth:
        data_expiracao = datetime.fromisoformat(auth["data_expiracao"].replace("Z", "+00:00"))
        dias_restantes = (data_expiracao - datetime.now(timezone.utc)).days
        
        return {
            "tem_acesso": True,
            "tipo": auth.get("tipo", "completo"),
            "expira_em": data_expiracao.isoformat(),
            "dias_restantes": dias_restantes,
            "em_periodo_teste": False
        }
    
    # Verificar período de teste
    data_criacao = current_user.get("data_criacao")
    if data_criacao:
        data_criacao = datetime.fromisoformat(data_criacao.replace("Z", "+00:00"))
        dias_desde_criacao = (datetime.now(timezone.utc) - data_criacao).days
        
        if dias_desde_criacao <= 30:
            return {
                "tem_acesso": True,
                "tipo": "teste",
                "expira_em": (data_criacao + timedelta(days=30)).isoformat(),
                "dias_restantes": 30 - dias_desde_criacao,
                "em_periodo_teste": True
            }
    
    return {
        "tem_acesso": False,
        "tipo": None,
        "expira_em": None,
        "em_periodo_teste": False,
        "mensagem": "Período de teste expirado. Entre em contato para renovar seu acesso."
    }


# ============================================================
# ATLETAS COM STATUS COMPLETO
# ============================================================

@router.get("/admin/autorizacoes/atletas-completo")
async def listar_atletas_com_status(admin: dict = Depends(get_admin_user)):
    """Lista TODOS os atletas com seu status de acesso (em_teste, autorizado, expirado)."""
    atletas = await db.usuarios.find(
        {"role": {"$in": ["atleta", "dono_assessoria"]}},
        {"_id": 0, "id": 1, "nome": 1, "email": 1, "equipe": 1, "estado": 1,
         "cidade": 1, "genero": 1, "sexo": 1, "categoria": 1, "modalidade": 1,
         "data_criacao": 1}
    ).to_list(5000)

    autorizacoes_ativas = {}
    async for auth in db.autorizacoes.find({"status": "ativa"}, {"_id": 0}):
        autorizacoes_ativas[auth["atleta_id"]] = auth

    agora = datetime.now(timezone.utc)
    resultado = []
    for a in atletas:
        auth = autorizacoes_ativas.get(a["id"])
        if auth:
            try:
                exp_str = auth["data_expiracao"].replace("Z", "+00:00")
                if "+" not in exp_str and "T" in exp_str:
                    exp_str = exp_str + "+00:00"
                data_exp = datetime.fromisoformat(exp_str)
                if data_exp.tzinfo is None:
                    data_exp = data_exp.replace(tzinfo=timezone.utc)
            except Exception:
                data_exp = agora
            if data_exp > agora:
                a["status_periodo"] = "autorizado"
                a["dias_restantes"] = (data_exp - agora).days
                a["autorizacao"] = {"id": auth.get("id", ""), "tipo": auth.get("tipo"), "expira": auth.get("data_expiracao", "")}
            else:
                a["status_periodo"] = "expirado"
                a["dias_restantes"] = 0
                a["autorizacao"] = {"id": auth.get("id", "")}
        else:
            data_criacao_str = a.get("data_criacao", agora.isoformat())
            try:
                dc = data_criacao_str.replace("Z", "+00:00")
                if "+" not in dc and "T" in dc:
                    dc = dc + "+00:00"
                data_criacao = datetime.fromisoformat(dc)
                if data_criacao.tzinfo is None:
                    data_criacao = data_criacao.replace(tzinfo=timezone.utc)
            except Exception:
                data_criacao = agora
            dias = (agora - data_criacao).days
            if dias <= 30:
                a["status_periodo"] = "em_teste"
                a["dias_restantes"] = max(0, 30 - dias)
            else:
                a["status_periodo"] = "expirado"
                a["dias_restantes"] = 0
        resultado.append(a)

    return {"atletas": resultado, "total": len(resultado)}


# ============================================================
# UPLOAD DE ARQUIVO PARA MENSAGENS DE AUTORIZAÇÕES
# ============================================================

@router.post("/admin/autorizacoes/mensagens/upload")
async def upload_arquivo_autorizacao(
    arquivo: UploadFile = File(...),
    admin: dict = Depends(get_admin_user)
):
    ext = os.path.splitext(arquivo.filename)[1].lower()
    allowed = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt', '.zip']
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Tipo de arquivo não permitido: {ext}")
    from services.object_storage import upload_file as cloud_upload
    content = await arquivo.read()
    result = cloud_upload(content, arquivo.filename, pasta="autorizacoes")
    is_image = ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    return {
        "filename": arquivo.filename,
        "original_name": arquivo.filename,
        "url": result["url"],
        "tipo": "imagem" if is_image else "arquivo",
        "tamanho": result["size"]
    }


@router.get("/admin/autorizacoes/mensagens/arquivo/{filename}")
async def servir_arquivo_autorizacao(filename: str):
    from fastapi.responses import FileResponse
    filepath = os.path.join(UPLOAD_DIR_AUT, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(filepath)


# ============================================================
# ENVIO DE MENSAGEM PARA ATLETAS POR STATUS
# ============================================================

async def _build_query_autorizacoes(status_filtro, estados, cidades, modalidades, generos, especiais):
    """Constrói query para filtrar atletas por status + filtros geográficos/demográficos."""
    query = {"role": {"$in": ["atleta", "dono_assessoria"]}}

    if estados:
        query["estado"] = {"$in": estados}
    if cidades:
        query["cidade"] = {"$in": cidades}

    # Filtro de gênero
    if generos:
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
            if "$or" not in query:
                query["$or"] = genero_conditions
            else:
                query["$and"] = [{"$or": query.pop("$or")}, {"$or": genero_conditions}]

    # Filtro de grupos especiais
    if especiais:
        esp_conditions = []
        if "donos_assessoria" in especiais:
            esp_conditions.append({"role": "dono_assessoria"})
        if "individual_sem_assessoria" in especiais:
            esp_conditions.append({"role": "atleta", "$or": [{"equipe": {"$in": [None, "", "INDIVIDUAL"]}}, {"equipe": {"$exists": False}}]})
        if esp_conditions:
            query = {"$and": [query, {"$or": esp_conditions}]}

    return query


@router.post("/admin/autorizacoes/mensagens/enviar")
async def enviar_mensagem_autorizacoes(
    titulo: str = Form(""),
    mensagem: str = Form(""),
    link: str = Form(""),
    anexos: str = Form("[]"),
    status_filtro: str = Form("todos"),
    filtro_estados: str = Form("[]"),
    filtro_cidades: str = Form("[]"),
    filtro_modalidades: str = Form("[]"),
    filtro_generos: str = Form("[]"),
    filtro_especial: str = Form("[]"),
    splash: str = Form("false"),
    agendar_para: str = Form(""),
    admin: dict = Depends(get_admin_user)
):
    """Envia mensagem para atletas filtrados por status de autorização e outros filtros."""
    if not mensagem.strip() and not link.strip():
        raise HTTPException(status_code=400, detail="Mensagem ou link é obrigatório")

    estados = json.loads(filtro_estados) if filtro_estados != "[]" else []
    cidades = json.loads(filtro_cidades) if filtro_cidades != "[]" else []
    modalidades = json.loads(filtro_modalidades) if filtro_modalidades != "[]" else []
    generos = json.loads(filtro_generos) if filtro_generos != "[]" else []
    especiais = json.loads(filtro_especial) if filtro_especial != "[]" else []
    anexos_list = json.loads(anexos) if anexos != "[]" else []
    is_splash = splash.lower() == "true"
    is_agendada = bool(agendar_para and agendar_para.strip())

    agora = datetime.now(timezone.utc)
    mensagem_id = str(uuid.uuid4())

    registro = {
        "id": mensagem_id,
        "titulo": titulo or "Mensagem da Administração",
        "mensagem": mensagem,
        "link": link if link.strip() else None,
        "anexos": anexos_list,
        "status_filtro": status_filtro,
        "filtro_estados": estados,
        "filtro_cidades": cidades,
        "filtro_modalidades": modalidades,
        "filtro_generos": generos,
        "filtro_especial": especiais,
        "splash": is_splash,
        "total_enviados": 0,
        "admin_id": admin["id"],
        "admin_nome": admin.get("nome", "Admin"),
        "data_criacao": agora.isoformat(),
        "data_envio": None if is_agendada else agora.isoformat(),
        "agendar_para": agendar_para.strip() if is_agendada else None,
        "status": "agendada" if is_agendada else "enviada",
        "origem": "autorizacoes"
    }

    if is_agendada:
        await db.mensagens_admin.insert_one(registro)
        return {"message": f"Mensagem agendada para {agendar_para}", "total_enviados": 0, "mensagem_id": mensagem_id, "status": "agendada"}

    # Construir query base
    query = await _build_query_autorizacoes(status_filtro, estados, cidades, modalidades, generos, especiais)

    # Buscar todos os destinatários potenciais
    destinatarios = await db.usuarios.find(query, {"_id": 0, "id": 1, "data_criacao": 1}).to_list(None)

    # Filtrar por status_periodo
    autorizacoes_ativas = {}
    async for auth in db.autorizacoes.find({"status": "ativa"}, {"_id": 0, "atleta_id": 1, "data_expiracao": 1}):
        autorizacoes_ativas[auth["atleta_id"]] = auth

    ids_finais = []
    for d in destinatarios:
        uid = d["id"]
        auth = autorizacoes_ativas.get(uid)
        if auth:
            try:
                exp_str = auth["data_expiracao"].replace("Z", "+00:00")
                if "+" not in exp_str and "T" in exp_str:
                    exp_str = exp_str + "+00:00"
                data_exp = datetime.fromisoformat(exp_str)
                if data_exp.tzinfo is None:
                    data_exp = data_exp.replace(tzinfo=timezone.utc)
            except Exception:
                data_exp = agora
            status = "autorizado" if data_exp > agora else "expirado"
        else:
            dc = d.get("data_criacao", agora.isoformat())
            try:
                dc_str = dc.replace("Z", "+00:00")
                if "+" not in dc_str and "T" in dc_str:
                    dc_str = dc_str + "+00:00"
                data_c = datetime.fromisoformat(dc_str)
                if data_c.tzinfo is None:
                    data_c = data_c.replace(tzinfo=timezone.utc)
            except Exception:
                data_c = agora
            dias = (agora - data_c).days
            status = "em_teste" if dias <= 30 else "expirado"

        if status_filtro == "todos" or status == status_filtro:
            ids_finais.append(uid)

    # Criar notificações
    total = 0
    for uid in ids_finais:
        notificacao = {
            "id": str(uuid.uuid4()),
            "mensagem_id": mensagem_id,
            "mensagem_admin_id": mensagem_id,
            "usuario_id": uid,
            "tipo": "mensagem_admin",
            "titulo": titulo or "Mensagem da Administração",
            "mensagem": mensagem,
            "link": link if link.strip() else None,
            "anexos": anexos_list,
            "lida": False,
            "splash": is_splash,
            "data_criacao": agora.isoformat(),
            "remetente_id": admin.get("id", "system"),
            "remetente_nome": "Ranking Run"
        }
        await db.notificacoes.insert_one(notificacao)
        total += 1

    registro["total_enviados"] = total
    await db.mensagens_admin.insert_one(registro)

    tipo_envio = "Splash" if is_splash else "Normal"
    return {"message": f"Mensagem ({tipo_envio}) enviada para {total} atleta(s)", "total_enviados": total, "mensagem_id": mensagem_id, "status": "enviada"}


@router.get("/admin/autorizacoes/mensagens/historico")
async def historico_mensagens_autorizacoes(admin: dict = Depends(get_admin_user)):
    """Histórico de mensagens enviadas pela aba de Autorizações."""
    mensagens = await db.mensagens_admin.find(
        {"origem": "autorizacoes"},
        {"_id": 0}
    ).sort("data_criacao", -1).limit(50).to_list(None)
    return {"mensagens": mensagens}
