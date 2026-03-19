# /app/backend/routes/rivais_routes.py
# Sistema de Rivais entre atletas

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel
import uuid

from config import db
from routes.auth_routes import get_current_user
from routes.notificacoes_routes import criar_notificacao

router = APIRouter()


class RivalRequest(BaseModel):
    atleta_id: str
    mensagem: Optional[str] = None


@router.get("/rivais/meus")
async def get_meus_rivais(current_user: dict = Depends(get_current_user)):
    """Retorna a lista de rivais do atleta logado"""
    
    # Buscar rivais aceitos (bilateral)
    rivais = await db.rivais.find({
        "$or": [
            {"atleta1_id": current_user["id"], "status": "aceito"},
            {"atleta2_id": current_user["id"], "status": "aceito"}
        ]
    }, {"_id": 0}).to_list(50)
    
    # Enriquecer com dados dos atletas
    resultado = []
    for rival in rivais:
        outro_id = rival["atleta2_id"] if rival["atleta1_id"] == current_user["id"] else rival["atleta1_id"]
        outro_atleta = await db.usuarios.find_one(
            {"id": outro_id},
            {"_id": 0, "id": 1, "nome": 1, "cidade": 1, "estado": 1, "equipe": 1, "foto_url": 1, "pontos_geral": 1}
        )
        if outro_atleta:
            # Calcular vantagem de pontos
            meus_pontos = current_user.get("pontos_geral", 0)
            pontos_rival = outro_atleta.get("pontos_geral", 0)
            vantagem = meus_pontos - pontos_rival
            
            resultado.append({
                "id": rival["id"],
                "rival": outro_atleta,
                "vantagem_pontos": vantagem,
                "status": "ganhando" if vantagem > 0 else ("perdendo" if vantagem < 0 else "empatado"),
                "data_inicio": rival.get("data_aceite", rival.get("data_criacao"))
            })
    
    # Ordenar por nome
    resultado.sort(key=lambda x: x["rival"]["nome"])
    
    return {"rivais": resultado, "total": len(resultado)}


@router.get("/rivais/pendentes")
async def get_solicitacoes_rivais_pendentes(current_user: dict = Depends(get_current_user)):
    """Retorna solicitações de rivalidade pendentes"""
    
    # Solicitações recebidas
    recebidas = await db.rivais.find({
        "atleta2_id": current_user["id"],
        "status": "pendente"
    }, {"_id": 0}).to_list(20)
    
    # Enriquecer com dados dos solicitantes
    for sol in recebidas:
        solicitante = await db.usuarios.find_one(
            {"id": sol["atleta1_id"]},
            {"_id": 0, "id": 1, "nome": 1, "cidade": 1, "estado": 1, "equipe": 1, "foto_url": 1}
        )
        sol["solicitante"] = solicitante
    
    # Solicitações enviadas
    enviadas = await db.rivais.find({
        "atleta1_id": current_user["id"],
        "status": "pendente"
    }, {"_id": 0}).to_list(20)
    
    for sol in enviadas:
        destinatario = await db.usuarios.find_one(
            {"id": sol["atleta2_id"]},
            {"_id": 0, "id": 1, "nome": 1, "cidade": 1, "estado": 1, "equipe": 1, "foto_url": 1}
        )
        sol["destinatario"] = destinatario
    
    return {
        "recebidas": recebidas,
        "enviadas": enviadas,
        "total_recebidas": len(recebidas),
        "total_enviadas": len(enviadas)
    }


@router.post("/rivais/solicitar")
async def solicitar_rivalidade(
    dados: RivalRequest,
    current_user: dict = Depends(get_current_user)
):
    """Envia solicitação de rivalidade para outro atleta"""
    
    if dados.atleta_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Você não pode ser rival de si mesmo")
    
    # Verificar se o atleta existe
    outro_atleta = await db.usuarios.find_one({"id": dados.atleta_id})
    if not outro_atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Verificar se já existe rivalidade (em qualquer direção)
    existente = await db.rivais.find_one({
        "$or": [
            {"atleta1_id": current_user["id"], "atleta2_id": dados.atleta_id},
            {"atleta1_id": dados.atleta_id, "atleta2_id": current_user["id"]}
        ]
    })
    
    if existente:
        if existente["status"] == "aceito":
            raise HTTPException(status_code=400, detail="Vocês já são rivais")
        elif existente["status"] == "pendente":
            raise HTTPException(status_code=400, detail="Já existe uma solicitação pendente")
    
    # Criar solicitação
    rivalidade = {
        "id": str(uuid.uuid4()),
        "atleta1_id": current_user["id"],
        "atleta1_nome": current_user.get("nome", ""),
        "atleta2_id": dados.atleta_id,
        "atleta2_nome": outro_atleta.get("nome", ""),
        "mensagem": dados.mensagem,
        "status": "pendente",
        "data_criacao": datetime.now(timezone.utc).isoformat()
    }
    
    await db.rivais.insert_one(rivalidade)
    
    # Notificar o outro atleta
    await criar_notificacao(
        usuario_id=dados.atleta_id,
        tipo="solicitacao_rival",
        titulo="⚔️ Desafio de Rivalidade!",
        mensagem=f"{current_user.get('nome', 'Um atleta')} quer ser seu rival! Aceite o desafio?",
        dados_extras={
            "rivalidade_id": rivalidade["id"],
            "solicitante_id": current_user["id"],
            "solicitante_nome": current_user.get("nome", "")
        }
    )
    
    return {
        "message": f"Solicitação de rivalidade enviada para {outro_atleta.get('nome')}!",
        "rivalidade_id": rivalidade["id"]
    }


@router.post("/rivais/aceitar/{rivalidade_id}")
async def aceitar_rivalidade(rivalidade_id: str, current_user: dict = Depends(get_current_user)):
    """Aceita uma solicitação de rivalidade"""
    
    rivalidade = await db.rivais.find_one({
        "id": rivalidade_id,
        "atleta2_id": current_user["id"],
        "status": "pendente"
    })
    
    if not rivalidade:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada ou já processada")
    
    # Atualizar para aceito
    await db.rivais.update_one(
        {"id": rivalidade_id},
        {"$set": {
            "status": "aceito",
            "data_aceite": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Notificar o solicitante
    await criar_notificacao(
        usuario_id=rivalidade["atleta1_id"],
        tipo="rival_aceito",
        titulo="🎯 Rivalidade Aceita!",
        mensagem=f"{current_user.get('nome', 'O atleta')} aceitou seu desafio de rivalidade! A competição começou!",
        dados_extras={
            "rivalidade_id": rivalidade_id,
            "rival_id": current_user["id"],
            "rival_nome": current_user.get("nome", "")
        }
    )
    
    return {"message": f"Rivalidade com {rivalidade['atleta1_nome']} aceita! Boa competição!"}


@router.post("/rivais/recusar/{rivalidade_id}")
async def recusar_rivalidade(rivalidade_id: str, current_user: dict = Depends(get_current_user)):
    """Recusa uma solicitação de rivalidade"""
    
    rivalidade = await db.rivais.find_one({
        "id": rivalidade_id,
        "atleta2_id": current_user["id"],
        "status": "pendente"
    })
    
    if not rivalidade:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    # Remover solicitação
    await db.rivais.delete_one({"id": rivalidade_id})
    
    return {"message": "Solicitação de rivalidade recusada"}


@router.delete("/rivais/{rivalidade_id}")
async def encerrar_rivalidade(rivalidade_id: str, current_user: dict = Depends(get_current_user)):
    """Encerra uma rivalidade existente"""
    
    rivalidade = await db.rivais.find_one({
        "id": rivalidade_id,
        "$or": [
            {"atleta1_id": current_user["id"]},
            {"atleta2_id": current_user["id"]}
        ],
        "status": "aceito"
    })
    
    if not rivalidade:
        raise HTTPException(status_code=404, detail="Rivalidade não encontrada")
    
    # Marcar como encerrada
    await db.rivais.update_one(
        {"id": rivalidade_id},
        {"$set": {
            "status": "encerrada",
            "data_encerramento": datetime.now(timezone.utc).isoformat(),
            "encerrado_por": current_user["id"]
        }}
    )
    
    return {"message": "Rivalidade encerrada"}


@router.get("/rivais/ranking-duelos")
async def get_ranking_duelos(current_user: dict = Depends(get_current_user)):
    """Retorna o histórico de duelos/comparações com rivais"""
    
    # Buscar rivais aceitos
    rivais = await db.rivais.find({
        "$or": [
            {"atleta1_id": current_user["id"], "status": "aceito"},
            {"atleta2_id": current_user["id"], "status": "aceito"}
        ]
    }, {"_id": 0}).to_list(50)
    
    resultado = []
    for rival in rivais:
        outro_id = rival["atleta2_id"] if rival["atleta1_id"] == current_user["id"] else rival["atleta1_id"]
        
        # Buscar resultados em comum (mesma corrida)
        meus_resultados = await db.resultados.find(
            {"atleta_id": current_user["id"]},
            {"_id": 0, "corrida_nome": 1, "data_corrida": 1, "posicao": 1, "tempo": 1}
        ).to_list(100)
        
        rival_resultados = await db.resultados.find(
            {"atleta_id": outro_id},
            {"_id": 0, "corrida_nome": 1, "data_corrida": 1, "posicao": 1, "tempo": 1}
        ).to_list(100)
        
        # Encontrar corridas em comum
        meus_corridas = {r["corrida_nome"] for r in meus_resultados}
        rival_corridas = {r["corrida_nome"] for r in rival_resultados}
        corridas_comum = meus_corridas & rival_corridas
        
        vitorias = 0
        derrotas = 0
        empates = 0
        
        for corrida in corridas_comum:
            meu_res = next((r for r in meus_resultados if r["corrida_nome"] == corrida), None)
            rival_res = next((r for r in rival_resultados if r["corrida_nome"] == corrida), None)
            
            if meu_res and rival_res:
                if meu_res["posicao"] < rival_res["posicao"]:
                    vitorias += 1
                elif meu_res["posicao"] > rival_res["posicao"]:
                    derrotas += 1
                else:
                    empates += 1
        
        outro_atleta = await db.usuarios.find_one(
            {"id": outro_id},
            {"_id": 0, "id": 1, "nome": 1, "foto_url": 1}
        )
        
        resultado.append({
            "rival": outro_atleta,
            "corridas_em_comum": len(corridas_comum),
            "vitorias": vitorias,
            "derrotas": derrotas,
            "empates": empates,
            "saldo": vitorias - derrotas
        })
    
    # Ordenar por saldo (melhor primeiro)
    resultado.sort(key=lambda x: x["saldo"], reverse=True)
    
    return {"duelos": resultado}


@router.get("/rivais/sugestoes")
async def get_sugestoes_rivais(current_user: dict = Depends(get_current_user)):
    """Sugere atletas para rivalidade baseado em critérios"""
    
    # Buscar atletas com pontuação similar (+/- 20%)
    meus_pontos = current_user.get("pontos_geral", 0)
    margem = max(meus_pontos * 0.2, 10)
    
    sugestoes = await db.usuarios.find({
        "role": "atleta",
        "id": {"$ne": current_user["id"]},
        "pontos_geral": {"$gte": meus_pontos - margem, "$lte": meus_pontos + margem}
    }, {"_id": 0, "id": 1, "nome": 1, "cidade": 1, "estado": 1, "equipe": 1, "foto_url": 1, "pontos_geral": 1}).limit(10).to_list(10)
    
    # Remover quem já é rival
    rivais_existentes = await db.rivais.find({
        "$or": [
            {"atleta1_id": current_user["id"]},
            {"atleta2_id": current_user["id"]}
        ],
        "status": {"$in": ["aceito", "pendente"]}
    }).to_list(100)
    
    ids_rivais = set()
    for r in rivais_existentes:
        ids_rivais.add(r["atleta1_id"])
        ids_rivais.add(r["atleta2_id"])
    
    sugestoes = [s for s in sugestoes if s["id"] not in ids_rivais]
    
    # Adicionar info de diferença de pontos
    for s in sugestoes:
        s["diferenca_pontos"] = abs((s.get("pontos_geral", 0) or 0) - meus_pontos)
    
    return {"sugestoes": sugestoes[:5]}
