# /app/backend/routes/indicacao_routes.py
# Sistema de Indicação de Atletas

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib

from config import db
from routes.auth_routes import get_current_user

router = APIRouter(prefix="/indicacao", tags=["Indicação"])


# ==================== MODELS ====================

class IndicacaoResponse(BaseModel):
    codigo: str
    link: str
    total_indicacoes: int
    indicacoes_para_embaixador: int
    is_embaixador: bool


class IndicacaoRegistro(BaseModel):
    codigo_indicacao: str


# ==================== FUNÇÕES AUXILIARES ====================

def gerar_codigo_indicacao(usuario_id: str, nome: str) -> str:
    """Gera um código de indicação único baseado no usuário"""
    # Pegar as primeiras letras do nome
    nome_parts = nome.upper().split()
    prefixo = ''.join([p[0] for p in nome_parts[:2]]) if len(nome_parts) >= 2 else nome[:2].upper()
    
    # Gerar hash curto do ID
    hash_id = hashlib.md5(usuario_id.encode()).hexdigest()[:6].upper()
    
    return f"REF-{prefixo}{hash_id}"


async def atualizar_codigo_usuario(usuario_id: str, nome: str) -> str:
    """Atualiza ou cria o código de indicação do usuário"""
    usuario = await db.usuarios.find_one({"id": usuario_id}, {"_id": 0})
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se já tem código
    codigo_existente = usuario.get("codigo_indicacao")
    
    if codigo_existente:
        return codigo_existente
    
    # Gerar novo código
    codigo = gerar_codigo_indicacao(usuario_id, nome)
    
    # Garantir que é único
    existente = await db.usuarios.find_one({"codigo_indicacao": codigo})
    if existente:
        # Adicionar sufixo aleatório
        codigo = f"{codigo}{uuid.uuid4().hex[:3].upper()}"
    
    # Salvar no usuário
    await db.usuarios.update_one(
        {"id": usuario_id},
        {"$set": {"codigo_indicacao": codigo}}
    )
    
    return codigo


async def verificar_insignia_embaixador(usuario_id: str):
    """Verifica e concede a insígnia de Embaixador se elegível"""
    # Contar indicações bem-sucedidas
    total_indicacoes = await db.indicacoes.count_documents({
        "indicador_id": usuario_id,
        "status": "confirmada"
    })
    
    if total_indicacoes >= 5:
        # Verificar se já tem a insígnia
        badge_existente = await db.badges_atleta.find_one({
            "atleta_id": usuario_id,
            "badge_id": "embaixador"
        })
        
        if not badge_existente:
            # Conceder insígnia
            await db.badges_atleta.insert_one({
                "atleta_id": usuario_id,
                "badge_id": "embaixador",
                "data_conquista": datetime.now(timezone.utc).isoformat()
            })
            return True
    
    return False


# ==================== ENDPOINTS ====================

@router.get("/meu-codigo")
async def get_meu_codigo(current_user: dict = Depends(get_current_user)):
    """Retorna o código de indicação do usuário logado"""
    
    usuario_id = current_user["id"]
    nome = current_user.get("nome", "ATLETA")
    
    # Obter ou criar código
    codigo = await atualizar_codigo_usuario(usuario_id, nome)
    
    # Contar indicações
    total_indicacoes = await db.indicacoes.count_documents({
        "indicador_id": usuario_id,
        "status": "confirmada"
    })
    
    # Verificar insígnia
    is_embaixador = await db.badges_atleta.find_one({
        "atleta_id": usuario_id,
        "badge_id": "embaixador"
    }) is not None
    
    # Gerar link
    base_url = "https://athlete-dashboard-15.preview.emergentagent.com"
    link = f"{base_url}/cadastro?ref={codigo}"
    
    return {
        "codigo": codigo,
        "link": link,
        "total_indicacoes": total_indicacoes,
        "indicacoes_para_embaixador": max(0, 5 - total_indicacoes),
        "is_embaixador": is_embaixador
    }


@router.get("/minhas-indicacoes")
async def get_minhas_indicacoes(current_user: dict = Depends(get_current_user)):
    """Retorna lista de pessoas indicadas pelo usuário"""
    
    usuario_id = current_user["id"]
    
    indicacoes = await db.indicacoes.find(
        {"indicador_id": usuario_id},
        {"_id": 0}
    ).sort("data_indicacao", -1).to_list(50)
    
    # Buscar nomes dos indicados
    resultado = []
    for ind in indicacoes:
        indicado = await db.usuarios.find_one(
            {"id": ind.get("indicado_id")},
            {"_id": 0, "nome": 1, "foto_url": 1, "created_at": 1}
        )
        
        if indicado:
            resultado.append({
                "id": ind.get("indicado_id"),
                "nome": indicado.get("nome", "Atleta"),
                "foto_url": indicado.get("foto_url", ""),
                "data_cadastro": ind.get("data_indicacao"),
                "status": ind.get("status", "confirmada")
            })
    
    return {
        "total": len(resultado),
        "indicacoes": resultado
    }


@router.get("/verificar-codigo/{codigo}")
async def verificar_codigo(codigo: str):
    """Verifica se um código de indicação é válido"""
    
    usuario = await db.usuarios.find_one(
        {"codigo_indicacao": codigo.upper()},
        {"_id": 0, "id": 1, "nome": 1}
    )
    
    if not usuario:
        return {"valido": False, "indicador": None}
    
    return {
        "valido": True,
        "indicador": {
            "nome": usuario.get("nome", "Atleta")
        }
    }


@router.post("/registrar")
async def registrar_indicacao(
    indicado_id: str,
    codigo_indicacao: str
):
    """Registra uma indicação quando um novo usuário se cadastra com código"""
    
    # Buscar indicador pelo código
    indicador = await db.usuarios.find_one(
        {"codigo_indicacao": codigo_indicacao.upper()},
        {"_id": 0, "id": 1, "nome": 1}
    )
    
    if not indicador:
        return {"success": False, "message": "Código de indicação inválido"}
    
    # Não permitir auto-indicação
    if indicador["id"] == indicado_id:
        return {"success": False, "message": "Não é possível se auto-indicar"}
    
    # Verificar se já existe essa indicação
    existente = await db.indicacoes.find_one({
        "indicador_id": indicador["id"],
        "indicado_id": indicado_id
    })
    
    if existente:
        return {"success": False, "message": "Indicação já registrada"}
    
    # Registrar indicação
    await db.indicacoes.insert_one({
        "id": str(uuid.uuid4()),
        "indicador_id": indicador["id"],
        "indicado_id": indicado_id,
        "codigo_usado": codigo_indicacao.upper(),
        "data_indicacao": datetime.now(timezone.utc).isoformat(),
        "status": "confirmada"
    })
    
    # Atualizar contador no indicador
    await db.usuarios.update_one(
        {"id": indicador["id"]},
        {"$inc": {"total_indicacoes": 1}}
    )
    
    # Verificar se ganhou insígnia
    ganhou_insignia = await verificar_insignia_embaixador(indicador["id"])
    
    return {
        "success": True,
        "message": f"Indicação de {indicador['nome']} registrada!",
        "indicador_ganhou_insignia": ganhou_insignia
    }


@router.get("/ranking")
async def ranking_indicacoes():
    """Retorna o ranking de quem mais indicou"""
    
    pipeline = [
        {"$match": {"status": "confirmada"}},
        {"$group": {
            "_id": "$indicador_id",
            "total": {"$sum": 1}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 20}
    ]
    
    ranking = await db.indicacoes.aggregate(pipeline).to_list(20)
    
    resultado = []
    for i, r in enumerate(ranking, 1):
        usuario = await db.usuarios.find_one(
            {"id": r["_id"]},
            {"_id": 0, "nome": 1, "foto_url": 1}
        )
        
        if usuario:
            resultado.append({
                "posicao": i,
                "usuario_id": r["_id"],
                "nome": usuario.get("nome", ""),
                "foto_url": usuario.get("foto_url", ""),
                "total_indicacoes": r["total"],
                "is_embaixador": r["total"] >= 5
            })
    
    return {
        "total": len(resultado),
        "ranking": resultado
    }
