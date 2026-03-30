"""
Rotas de Scraping Avançado de Corridas
- Busca por URL com fallback Playwright
- Gerenciamento de fontes monitoradas
- Anti-duplicidade contra o banco
- Cadastro automático de corridas encontradas
- Atualização automática a cada 12h
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from uuid import uuid4
import os
import logging

from motor.motor_asyncio import AsyncIOMotorClient
from routes.auth_routes import get_admin_user
from services.scraping_corridas import fazer_scraping, calcular_status

logger = logging.getLogger(__name__)

router = APIRouter()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


class FonteMonitorada(BaseModel):
    url: str
    nome: Optional[str] = ""
    ativa: Optional[bool] = True


class BuscarCorridasRequest(BaseModel):
    url: str
    usar_playwright: Optional[bool] = False
    cadastrar_automaticamente: Optional[bool] = True


async def verificar_duplicatas(corridas: list) -> dict:
    """
    Verifica corridas contra o banco de dados para evitar duplicatas.
    Retorna dict com corridas novas e duplicatas.
    """
    existentes = await db.corridas_eventos.find(
        {}, {"_id": 0, "nome_corrida": 1, "data_corrida": 1, "pagina_link": 1}
    ).to_list(None)

    # Criar set de chaves existentes
    chaves_existentes = set()
    links_existentes = set()
    for e in existentes:
        nome = (e.get("nome_corrida") or "").lower().strip()
        data = (e.get("data_corrida") or "").strip()
        chaves_existentes.add((nome, data))
        link = (e.get("pagina_link") or "").strip().lower()
        if link:
            links_existentes.add(link)

    novas = []
    duplicatas = []
    for c in corridas:
        nome = (c.get("nome_corrida") or "").lower().strip()
        data = (c.get("data_corrida") or "").strip()
        link = (c.get("pagina_link") or "").strip().lower()

        is_dup = (nome, data) in chaves_existentes
        if not is_dup and link:
            is_dup = link in links_existentes

        if is_dup:
            c["_duplicata"] = True
            duplicatas.append(c)
        else:
            c["_duplicata"] = False
            novas.append(c)

    return {"novas": novas, "duplicatas": duplicatas}


async def cadastrar_corridas_novas(corridas: list, admin_id: str, fonte_url: str) -> int:
    """Cadastra corridas novas no banco de dados"""
    count = 0
    for c in corridas:
        if c.get("_duplicata"):
            continue
        doc = {
            "id": str(uuid4()),
            "nome_corrida": c.get("nome_corrida", ""),
            "organizador": c.get("organizador", ""),
            "cidade": c.get("cidade", ""),
            "estado": c.get("estado", ""),
            "pagina_link": c.get("pagina_link", ""),
            "data_corrida": c.get("data_corrida", ""),
            "status": c.get("status", "ativa"),
            "criado_por": admin_id,
            "criado_em": datetime.now(timezone.utc).isoformat(),
            "fonte_scraping": fonte_url,
            "total_avaliacoes": 0,
            "media_geral": 0,
            "media_organizacao": 0,
            "media_percurso": 0,
            "media_kit": 0,
            "media_hidratacao": 0,
            "media_pos_prova": 0,
            "pontuacao_ranking": 0,
        }
        await db.corridas_eventos.insert_one(doc)
        count += 1
    return count


# ============== ENDPOINTS ==============

@router.post("/scraping/buscar")
async def buscar_corridas_url(req: BuscarCorridasRequest, admin: dict = Depends(get_admin_user)):
    """
    Busca corridas em uma URL usando scraping inteligente.
    - Auto-detecta se precisa de Playwright
    - Verifica duplicatas contra o banco
    - Cadastra automaticamente as novas
    """
    resultado = fazer_scraping(req.url, usar_playwright=req.usar_playwright)

    if not resultado["success"] or resultado["total_encontradas"] == 0:
        # Log
        await db.logs_sistema.insert_one({
            "id": str(uuid4()),
            "tipo": "scraping_busca",
            "admin_id": admin["id"],
            "url": req.url,
            "corridas_encontradas": 0,
            "metodo": resultado.get("metodo", "none"),
            "sucesso": False,
            "data": datetime.now(timezone.utc).isoformat()
        })
        return resultado

    # Verificar duplicatas
    check = await verificar_duplicatas(resultado["corridas"])
    novas = check["novas"]
    duplicatas = check["duplicatas"]

    # Cadastrar automaticamente
    cadastradas = 0
    if req.cadastrar_automaticamente and novas:
        cadastradas = await cadastrar_corridas_novas(novas, admin["id"], req.url)

    # Log
    await db.logs_sistema.insert_one({
        "id": str(uuid4()),
        "tipo": "scraping_busca",
        "admin_id": admin["id"],
        "url": req.url,
        "corridas_encontradas": resultado["total_encontradas"],
        "novas": len(novas),
        "duplicatas": len(duplicatas),
        "cadastradas": cadastradas,
        "metodo": resultado.get("metodo", ""),
        "sucesso": True,
        "data": datetime.now(timezone.utc).isoformat()
    })

    return {
        **resultado,
        "novas": len(novas),
        "duplicatas": len(duplicatas),
        "cadastradas": cadastradas,
        "corridas_novas": [
            {k: v for k, v in c.items() if k != "_duplicata"} for c in novas
        ],
        "corridas_duplicatas": [
            {k: v for k, v in c.items() if k != "_duplicata"} for c in duplicatas
        ],
    }


@router.get("/scraping/fontes")
async def listar_fontes(admin: dict = Depends(get_admin_user)):
    """Lista todas as fontes monitoradas"""
    fontes = await db.scraping_fontes.find(
        {}, {"_id": 0}
    ).sort("criado_em", -1).to_list(None)
    return fontes


@router.post("/scraping/fontes")
async def adicionar_fonte(fonte: FonteMonitorada, admin: dict = Depends(get_admin_user)):
    """Adiciona uma nova fonte para monitoramento"""
    # Verificar se já existe
    existente = await db.scraping_fontes.find_one({"url": fonte.url})
    if existente:
        return {"detail": "Fonte já cadastrada", "id": existente.get("id")}

    doc = {
        "id": str(uuid4()),
        "url": fonte.url,
        "nome": fonte.nome or fonte.url.split("//")[-1].split("/")[0],
        "ativa": fonte.ativa,
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "criado_por": admin["id"],
        "ultima_varredura": None,
        "total_corridas_encontradas": 0,
        "total_novas_ultima": 0,
    }
    await db.scraping_fontes.insert_one(doc)
    return {"id": doc["id"], "mensagem": "Fonte adicionada com sucesso"}


@router.delete("/scraping/fontes/{fonte_id}")
async def remover_fonte(fonte_id: str, admin: dict = Depends(get_admin_user)):
    """Remove uma fonte monitorada"""
    result = await db.scraping_fontes.delete_one({"id": fonte_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    return {"mensagem": "Fonte removida"}


@router.post("/scraping/atualizar-todas")
async def atualizar_todas_fontes(admin: dict = Depends(get_admin_user)):
    """Executa varredura em todas as fontes ativas"""
    fontes = await db.scraping_fontes.find({"ativa": True}, {"_id": 0}).to_list(None)

    if not fontes:
        return {"mensagem": "Nenhuma fonte ativa cadastrada", "total_fontes": 0}

    resultados = []
    total_novas = 0
    total_duplicatas = 0

    for fonte in fontes:
        try:
            resultado = fazer_scraping(fonte["url"])
            if resultado["success"] and resultado["total_encontradas"] > 0:
                check = await verificar_duplicatas(resultado["corridas"])
                novas = check["novas"]
                cadastradas = await cadastrar_corridas_novas(novas, admin["id"], fonte["url"])
                total_novas += cadastradas
                total_duplicatas += len(check["duplicatas"])

                # Atualizar fonte
                await db.scraping_fontes.update_one(
                    {"id": fonte["id"]},
                    {"$set": {
                        "ultima_varredura": datetime.now(timezone.utc).isoformat(),
                        "total_corridas_encontradas": resultado["total_encontradas"],
                        "total_novas_ultima": cadastradas,
                    }}
                )
                resultados.append({
                    "fonte": fonte["nome"],
                    "url": fonte["url"],
                    "encontradas": resultado["total_encontradas"],
                    "novas": cadastradas,
                    "duplicatas": len(check["duplicatas"]),
                    "metodo": resultado.get("metodo", ""),
                })
            else:
                resultados.append({
                    "fonte": fonte["nome"],
                    "url": fonte["url"],
                    "encontradas": 0,
                    "novas": 0,
                    "duplicatas": 0,
                    "erro": resultado.get("mensagem", ""),
                })
        except Exception as e:
            logger.error(f"Erro ao atualizar fonte {fonte['url']}: {e}")
            resultados.append({
                "fonte": fonte["nome"],
                "url": fonte["url"],
                "encontradas": 0,
                "novas": 0,
                "duplicatas": 0,
                "erro": str(e),
            })

    # Log
    await db.logs_sistema.insert_one({
        "id": str(uuid4()),
        "tipo": "scraping_atualizacao_geral",
        "admin_id": admin["id"],
        "total_fontes": len(fontes),
        "total_novas": total_novas,
        "total_duplicatas": total_duplicatas,
        "data": datetime.now(timezone.utc).isoformat()
    })

    return {
        "mensagem": f"Varredura completa: {total_novas} novas corridas cadastradas",
        "total_fontes": len(fontes),
        "total_novas": total_novas,
        "total_duplicatas": total_duplicatas,
        "resultados": resultados,
    }


@router.get("/scraping/status")
async def status_scraping(admin: dict = Depends(get_admin_user)):
    """Retorna status do último scraping"""
    ultimo_log = await db.logs_sistema.find_one(
        {"tipo": {"$in": ["scraping_busca", "scraping_atualizacao_geral"]}},
        {"_id": 0},
        sort=[("data", -1)]
    )
    total_fontes = await db.scraping_fontes.count_documents({"ativa": True})
    return {
        "total_fontes_ativas": total_fontes,
        "ultimo_scraping": ultimo_log,
    }
