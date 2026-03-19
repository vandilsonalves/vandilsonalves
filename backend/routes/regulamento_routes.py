# /app/backend/routes/regulamento_routes.py
# Rotas relacionadas ao regulamento e termos

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from config import db
from routes.auth_routes import get_admin_user

router = APIRouter()


class RegulamentoUpdate(BaseModel):
    conteudo: str
    versao: Optional[str] = None


@router.get("/regulamento")
async def get_regulamento():
    """Retorna o regulamento atual público"""
    
    regulamento = await db.configuracoes.find_one(
        {"tipo": "regulamento"},
        {"_id": 0}
    )
    
    if not regulamento:
        return {
            "conteudo": "Regulamento em elaboração.",
            "versao": "1.0",
            "data_atualizacao": datetime.now(timezone.utc).isoformat()
        }
    
    return {
        "conteudo": regulamento.get("conteudo", ""),
        "versao": regulamento.get("versao", "1.0"),
        "data_atualizacao": regulamento.get("data_atualizacao", "")
    }


@router.get("/regulamento/admin")
async def get_regulamento_admin(admin: dict = Depends(get_admin_user)):
    """Retorna o regulamento com informações adicionais para admin"""
    
    regulamento = await db.configuracoes.find_one(
        {"tipo": "regulamento"},
        {"_id": 0}
    )
    
    if not regulamento:
        return {
            "conteudo": "",
            "versao": "1.0",
            "data_atualizacao": None,
            "atualizado_por": None
        }
    
    return regulamento


@router.put("/regulamento")
async def atualizar_regulamento(
    dados: RegulamentoUpdate,
    admin: dict = Depends(get_admin_user)
):
    """Atualiza o regulamento (apenas admin)"""
    
    regulamento_atual = await db.configuracoes.find_one({"tipo": "regulamento"})
    
    nova_versao = dados.versao
    if not nova_versao and regulamento_atual:
        versao_atual = regulamento_atual.get("versao", "1.0")
        partes = versao_atual.split(".")
        partes[-1] = str(int(partes[-1]) + 1)
        nova_versao = ".".join(partes)
    elif not nova_versao:
        nova_versao = "1.0"
    
    await db.configuracoes.update_one(
        {"tipo": "regulamento"},
        {
            "$set": {
                "conteudo": dados.conteudo,
                "versao": nova_versao,
                "data_atualizacao": datetime.now(timezone.utc).isoformat(),
                "atualizado_por": admin["id"],
                "atualizado_por_nome": admin.get("nome", "Admin")
            }
        },
        upsert=True
    )
    
    return {
        "message": "Regulamento atualizado com sucesso",
        "versao": nova_versao
    }


@router.get("/termo-avaliacao")
async def get_texto_termo():
    """Retorna o texto do termo de avaliação"""
    
    termo = await db.configuracoes.find_one(
        {"tipo": "termo_avaliacao"},
        {"_id": 0}
    )
    
    if not termo:
        return {
            "texto": "Ao avaliar uma corrida, você concorda em fornecer uma avaliação honesta e construtiva.",
            "versao": "1.0"
        }
    
    return termo


@router.put("/termo-avaliacao")
async def atualizar_termo_avaliacao(
    dados: dict,
    admin: dict = Depends(get_admin_user)
):
    """Atualiza o termo de avaliação"""
    
    await db.configuracoes.update_one(
        {"tipo": "termo_avaliacao"},
        {
            "$set": {
                "texto": dados.get("texto", ""),
                "versao": dados.get("versao", "1.0"),
                "data_atualizacao": datetime.now(timezone.utc).isoformat(),
                "atualizado_por": admin["id"]
            }
        },
        upsert=True
    )
    
    return {"message": "Termo de avaliação atualizado"}
