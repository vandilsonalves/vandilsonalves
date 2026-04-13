# /app/backend/routes/temporadas_routes.py
# Sistema de Gestao de Temporadas Anuais - Ranking Run Pro

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import logging

from config import db
from routes.auth_routes import get_current_user, get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["temporadas"])

ANO_ATUAL = datetime.now(timezone.utc).year


async def get_temporada_ativa():
    """Retorna a temporada ativa ou cria a padrao"""
    temp = await db.temporadas.find_one({"status": "ativa"}, {"_id": 0})
    if not temp:
        doc = {
            "season_id": ANO_ATUAL,
            "status": "ativa",
            "data_inicio": f"{ANO_ATUAL}-01-01",
            "data_fim": f"{ANO_ATUAL}-12-31",
            "data_criacao": datetime.now(timezone.utc).isoformat(),
            "criado_por": "sistema",
        }
        await db.temporadas.insert_one(doc)
        return doc
    return temp


# ==================== ENDPOINTS PUBLICOS ====================

@router.get("/temporadas/ativa")
async def temporada_ativa():
    """Retorna a temporada ativa atual"""
    temp = await get_temporada_ativa()
    return {
        "season_id": temp["season_id"],
        "status": temp["status"],
        "data_inicio": temp.get("data_inicio"),
        "data_fim": temp.get("data_fim"),
    }


@router.get("/temporadas/historico")
async def historico_temporadas():
    """Retorna todas as temporadas com ranking final"""
    temporadas = []
    cursor = db.temporadas.find({}, {"_id": 0}).sort("season_id", -1)
    async for t in cursor:
        temporadas.append(t)
    return {"temporadas": temporadas}


@router.get("/temporadas/{season_id}/ranking-final")
async def ranking_final_temporada(season_id: int):
    """Retorna o ranking final consolidado de uma temporada encerrada"""
    temp = await db.temporadas.find_one({"season_id": season_id}, {"_id": 0})
    if not temp:
        raise HTTPException(status_code=404, detail="Temporada nao encontrada")

    snapshot = await db.temporadas_snapshots.find_one(
        {"season_id": season_id}, {"_id": 0}
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot de ranking nao encontrado para esta temporada")

    return {
        "season_id": season_id,
        "status": temp.get("status"),
        "data_encerramento": temp.get("data_encerramento"),
        "ranking_profissional": snapshot.get("ranking_profissional", []),
        "ranking_galera": snapshot.get("ranking_galera", []),
        "ranking_assessorias": snapshot.get("ranking_assessorias", []),
        "ranking_corridas": snapshot.get("ranking_corridas", []),
        "estatisticas": snapshot.get("estatisticas", {}),
    }


# ==================== ENDPOINTS ADMIN ====================

@router.get("/admin/temporadas")
async def listar_temporadas_admin(admin: dict = Depends(get_admin_user)):
    """Lista todas as temporadas para o Admin"""
    temporadas = []
    cursor = db.temporadas.find({}, {"_id": 0}).sort("season_id", -1)
    async for t in cursor:
        temporadas.append(t)

    ativa = await get_temporada_ativa()

    # Verificar janela de encerramento (01-02 de janeiro)
    agora = datetime.now(timezone.utc)
    pode_encerrar = agora.month == 1 and agora.day <= 2

    return {
        "temporadas": temporadas,
        "temporada_ativa": ativa,
        "pode_encerrar": pode_encerrar,
        "data_atual": agora.isoformat(),
    }


class EncerrarTemporadaRequest(BaseModel):
    confirmacao: str  # Deve ser "ENCERRAR {ano}"
    senha_master: str


@router.post("/admin/temporadas/encerrar")
async def encerrar_temporada(dados: EncerrarTemporadaRequest, admin: dict = Depends(get_admin_user)):
    """
    Encerra a temporada ativa e cria uma nova.
    Requer: Admin Master, janela 01-02 de janeiro, confirmacao textual.
    """
    import os

    # 1. Verificar se eh super_admin
    if admin.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Apenas o Admin Master pode encerrar temporadas")

    # 2. Verificar janela de data (01-02 de janeiro)
    agora = datetime.now(timezone.utc)
    if not (agora.month == 1 and agora.day <= 2):
        raise HTTPException(
            status_code=403,
            detail=f"O encerramento de temporada so pode ser executado entre 01 e 02 de janeiro. Data atual: {agora.strftime('%d/%m/%Y')}"
        )

    # 3. Verificar senha master
    master_pwd = os.environ.get("SUPER_ADMIN_MASTER_PASSWORD", "")
    if not master_pwd or dados.senha_master != master_pwd:
        raise HTTPException(status_code=403, detail="Senha master incorreta")

    # 4. Buscar temporada ativa
    temp_ativa = await db.temporadas.find_one({"status": "ativa"}, {"_id": 0})
    if not temp_ativa:
        raise HTTPException(status_code=404, detail="Nenhuma temporada ativa encontrada")

    season_id = temp_ativa["season_id"]

    # 5. Verificar confirmacao textual
    esperado = f"ENCERRAR {season_id}"
    if dados.confirmacao.strip().upper() != esperado:
        raise HTTPException(status_code=400, detail=f"Confirmacao incorreta. Digite: {esperado}")

    # 6. Executar encerramento
    logger.info(f"[TEMPORADAS] Iniciando encerramento da temporada {season_id} por {admin.get('nome')}")

    # 6.1 Gerar snapshot dos rankings finais
    snapshot = await _gerar_snapshot_ranking(season_id)
    _ = snapshot  # snapshot saved to DB

    # 6.2 Congelar temporada
    await db.temporadas.update_one(
        {"season_id": season_id},
        {"$set": {
            "status": "finalizada",
            "data_encerramento": agora.isoformat(),
            "encerrado_por": admin.get("nome", "Admin"),
            "encerrado_por_id": admin.get("id"),
        }}
    )

    # 6.3 Criar nova temporada
    nova_season = season_id + 1
    nova_temp = {
        "season_id": nova_season,
        "status": "ativa",
        "data_inicio": f"{nova_season}-01-01",
        "data_fim": f"{nova_season}-12-31",
        "data_criacao": agora.isoformat(),
        "criado_por": admin.get("nome", "Admin"),
        "temporada_anterior": season_id,
    }
    await db.temporadas.insert_one(nova_temp)

    # 6.4 Reset logico: zerar pontuacao dos atletas para a nova temporada
    # Salvar pontos antigos em campo historico e zerar
    await db.usuarios.update_many(
        {"role": {"$in": ["atleta", "dono_assessoria"]}},
        [{"$set": {
            f"historico_pontos.{season_id}": {
                "pontos_total": "$pontos_total",
                "pontos_povao": {"$ifNull": ["$pontos_povao", 0]},
                "total_corridas": "$total_corridas",
                "total_podios": {"$ifNull": ["$total_podios", 0]},
                "total_vitorias": {"$ifNull": ["$total_vitorias", 0]},
            },
            "pontos_total": 0,
            "pontos_povao": 0,
            "total_corridas": 0,
            "total_corridas_povao": 0,
            "total_podios": 0,
            "total_vitorias": 0,
            "temporada_atual": nova_season,
        }}]
    )

    logger.info(f"[TEMPORADAS] Temporada {season_id} encerrada. Nova temporada {nova_season} criada.")

    return {
        "message": f"Temporada {season_id} encerrada com sucesso! Nova temporada {nova_season} ativa.",
        "temporada_encerrada": season_id,
        "nova_temporada": nova_season,
        "snapshot_gerado": True,
        "atletas_resetados": True,
    }


async def _gerar_snapshot_ranking(season_id: int):
    """Gera e salva snapshot completo dos rankings da temporada"""

    # Ranking Profissional/Amador (top 100 por categoria)
    ranking_pro = []
    for gen in ["M", "F"]:
        atletas = await db.usuarios.find(
            {"role": {"$in": ["atleta", "dono_assessoria"]}, "genero": gen, "modalidade_usuario": {"$ne": "povao_pace_livre"}, "pontos_total": {"$gt": 0}},
            {"_id": 0, "id": 1, "nome": 1, "equipe": 1, "cidade": 1, "estado": 1, "genero": 1, "categoria": 1, "faixa_etaria": 1, "pontos_total": 1, "total_corridas": 1, "total_podios": 1, "total_vitorias": 1}
        ).sort("pontos_total", -1).to_list(100)
        for i, a in enumerate(atletas, 1):
            a["posicao"] = i
        ranking_pro.append({"genero": gen, "atletas": atletas})

    # Ranking Galera
    ranking_galera = []
    for gen in ["M", "F"]:
        atletas = await db.usuarios.find(
            {"role": {"$in": ["atleta", "dono_assessoria"]}, "genero": gen, "modalidade_usuario": "povao_pace_livre", "pontos_povao": {"$gt": 0}},
            {"_id": 0, "id": 1, "nome": 1, "equipe": 1, "cidade": 1, "estado": 1, "pontos_povao": 1, "total_corridas": 1}
        ).sort("pontos_povao", -1).to_list(100)
        for i, a in enumerate(atletas, 1):
            a["posicao"] = i
        ranking_galera.append({"genero": gen, "atletas": atletas})

    # Ranking Assessorias
    try:
        from routes.liga_assessorias_routes import get_ranking_assessorias
        data = await get_ranking_assessorias(tipo="nacional")
        ranking_assessorias = data.get("ranking", [])[:50]
    except Exception:
        ranking_assessorias = []

    # Ranking Corridas Avaliadas
    corridas = await db.corridas_eventos.find(
        {"total_avaliacoes": {"$gte": 1}},
        {"_id": 0, "id": 1, "nome_corrida": 1, "organizador": 1, "cidade": 1, "estado": 1, "data_corrida": 1, "total_avaliacoes": 1, "media_geral": 1}
    ).sort("media_geral", -1).to_list(50)
    for i, c in enumerate(corridas, 1):
        c["posicao"] = i

    # Estatisticas gerais
    total_atletas = await db.usuarios.count_documents({"role": {"$in": ["atleta", "dono_assessoria"]}})
    total_resultados = await db.resultados_pendentes.count_documents({"status": "aprovado"})
    total_avaliacoes = await db.avaliacoes_corridas.count_documents({})

    snapshot = {
        "season_id": season_id,
        "ranking_profissional": ranking_pro,
        "ranking_galera": ranking_galera,
        "ranking_assessorias": ranking_assessorias,
        "ranking_corridas": corridas,
        "estatisticas": {
            "total_atletas": total_atletas,
            "total_resultados": total_resultados,
            "total_avaliacoes": total_avaliacoes,
        },
        "data_geracao": datetime.now(timezone.utc).isoformat(),
    }

    await db.temporadas_snapshots.update_one(
        {"season_id": season_id},
        {"$set": snapshot},
        upsert=True,
    )

    return snapshot
