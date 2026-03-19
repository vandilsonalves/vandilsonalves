# /app/backend/routes/autorizacoes_routes.py
# Rotas relacionadas a autorizações e período de teste

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import uuid

from config import db
from routes.auth_routes import get_current_user, get_admin_user

router = APIRouter()


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
