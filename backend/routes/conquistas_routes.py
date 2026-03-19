# /app/backend/routes/conquistas_routes.py
# Módulo de Conquistas e Selos

from fastapi import APIRouter, HTTPException, Depends

from config import db
from models import ConquistaAtleta
from services import CONQUISTAS
from routes.auth_routes import get_current_user
from routes.notificacoes_routes import criar_notificacao

router = APIRouter(tags=["Conquistas"])


# ==================== CONQUISTAS ENDPOINTS ====================

@router.get("/conquistas")
async def get_conquistas(current_user: dict = Depends(get_current_user)):
    """Retorna conquistas do atleta"""
    conquistas_atleta = await db.conquistas_atleta.find(
        {"usuario_id": current_user["id"]},
        {"_id": 0}
    ).to_list(None)
    
    conquistas_com_detalhes = []
    for ca in conquistas_atleta:
        if ca["conquista_codigo"] in CONQUISTAS:
            conquista = CONQUISTAS[ca["conquista_codigo"]]
            conquistas_com_detalhes.append({
                **conquista,
                "codigo": ca["conquista_codigo"],
                "data_conquista": ca["data_conquista"]
            })
    
    return {
        "conquistas": conquistas_com_detalhes,
        "total": len(conquistas_com_detalhes)
    }


@router.get("/conquistas/disponiveis")
async def get_conquistas_disponiveis():
    """Lista todas conquistas disponíveis"""
    return [
        {"codigo": k, **v}
        for k, v in CONQUISTAS.items()
    ]


@router.get("/selos-atleta/{atleta_id}")
async def get_selos_atleta(atleta_id: str):
    """Retorna os selos do atleta com informações de progresso (público)"""
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    total_resultados = atleta.get("total_corridas", 0)
    
    # Buscar conquistas do atleta
    conquistas_atleta = await db.conquistas_atleta.find(
        {"usuario_id": atleta_id},
        {"_id": 0}
    ).to_list(None)
    conquistas_codigos = [c["conquista_codigo"] for c in conquistas_atleta]
    
    # Selos de resultados
    selos_resultados = [
        {
            "codigo": "12_resultados",
            "nome": "Atleta Bronze",
            "descricao": "Lançou 12 resultados no ranking",
            "icone": "🥉",
            "cor": "#CD7F32",
            "meta": 12,
            "atual": min(total_resultados, 12),
            "conquistado": "12_resultados" in conquistas_codigos,
            "progresso": min(100, (total_resultados / 12) * 100)
        },
        {
            "codigo": "20_resultados",
            "nome": "Atleta Prata",
            "descricao": "Lançou 20 resultados no ranking",
            "icone": "🥈",
            "cor": "#C0C0C0",
            "meta": 20,
            "atual": min(total_resultados, 20),
            "conquistado": "20_resultados" in conquistas_codigos,
            "progresso": min(100, (total_resultados / 20) * 100)
        },
        {
            "codigo": "30_resultados",
            "nome": "Atleta Ouro",
            "descricao": "Lançou 30 resultados no ranking",
            "icone": "🥇",
            "cor": "#FFD700",
            "meta": 30,
            "atual": min(total_resultados, 30),
            "conquistado": "30_resultados" in conquistas_codigos,
            "progresso": min(100, (total_resultados / 30) * 100)
        }
    ]
    
    # Todas as conquistas do atleta
    todas_conquistas = []
    for ca in conquistas_atleta:
        if ca["conquista_codigo"] in CONQUISTAS:
            conquista = CONQUISTAS[ca["conquista_codigo"]]
            todas_conquistas.append({
                **conquista,
                "codigo": ca["conquista_codigo"],
                "data_conquista": ca["data_conquista"]
            })
    
    return {
        "atleta": {
            "id": atleta["id"],
            "nome": atleta.get("nome", ""),
            "total_resultados": total_resultados
        },
        "selos_resultados": selos_resultados,
        "todas_conquistas": todas_conquistas,
        "total_conquistas": len(todas_conquistas)
    }


@router.post("/verificar-conquistas-atleta")
async def verificar_conquistas_manual(current_user: dict = Depends(get_current_user)):
    """Verifica e atribui conquistas pendentes ao atleta logado"""
    novas = await verificar_conquistas(current_user["id"])
    return {
        "message": f"Verificação concluída. {len(novas) if novas else 0} novas conquistas!",
        "novas_conquistas": novas or []
    }


# ==================== HELPER FUNCTION ====================

async def verificar_conquistas(usuario_id: str):
    """Verifica e concede conquistas ao atleta"""
    usuario = await db.usuarios.find_one({"id": usuario_id}, {"_id": 0})
    if not usuario:
        return
    
    corridas = await db.corridas.find({"usuario_id": usuario_id}, {"_id": 0}).to_list(None)
    ranking = await db.ranking_anual.find_one({"usuario_id": usuario_id, "ano": 2025}, {"_id": 0})
    
    # Buscar total de resultados do atleta
    total_resultados = usuario.get("total_corridas", len(corridas))
    
    conquistas_atuais = await db.conquistas_atleta.find(
        {"usuario_id": usuario_id},
        {"_id": 0}
    ).to_list(None)
    conquistas_codigos = [c["conquista_codigo"] for c in conquistas_atuais]
    
    novas_conquistas = []
    
    # Verificar primeiro lugar
    if "primeiro_lugar" not in conquistas_codigos:
        if any(c.get("colocacao") == 1 for c in corridas):
            novas_conquistas.append("primeiro_lugar")
    
    # Verificar pódio
    if "podio" not in conquistas_codigos:
        if any(c.get("colocacao", 99) <= 3 for c in corridas):
            novas_conquistas.append("podio")
    
    # Verificar 10 corridas
    if "10_corridas" not in conquistas_codigos:
        if total_resultados >= 10:
            novas_conquistas.append("10_corridas")
    
    # === SELOS POR NÚMERO DE RESULTADOS ===
    if "12_resultados" not in conquistas_codigos:
        if total_resultados >= 12:
            novas_conquistas.append("12_resultados")
    
    if "20_resultados" not in conquistas_codigos:
        if total_resultados >= 20:
            novas_conquistas.append("20_resultados")
    
    if "30_resultados" not in conquistas_codigos:
        if total_resultados >= 30:
            novas_conquistas.append("30_resultados")
    
    # Verificar elite
    if "elite" not in conquistas_codigos and ranking:
        if ranking.get("pontos_total", 0) >= 100:
            novas_conquistas.append("elite")
    
    # Verificar maratonista
    if "maratonista" not in conquistas_codigos:
        if any(c.get("distancia") == "42KM" for c in corridas):
            novas_conquistas.append("maratonista")
    
    # Verificar consistente (6 meses diferentes)
    if "consistente" not in conquistas_codigos:
        meses = set(c.get("data", "")[:7] for c in corridas if c.get("data"))
        if len(meses) >= 6:
            novas_conquistas.append("consistente")
    
    # Conceder novas conquistas
    for codigo in novas_conquistas:
        conquista_atleta = ConquistaAtleta(
            usuario_id=usuario_id,
            conquista_codigo=codigo
        )
        await db.conquistas_atleta.insert_one(conquista_atleta.model_dump())
        
        # Notificar
        conquista = CONQUISTAS[codigo]
        await criar_notificacao(
            usuario_id=usuario_id,
            tipo="conquista",
            titulo=f"Nova conquista: {conquista['nome']}!",
            mensagem=conquista['descricao'],
            dados_extras={"conquista_codigo": codigo, "icone": conquista['icone']}
        )
        
        # Criar post automático no feed
        try:
            from routes.feed_routes import criar_post_conquista
            await criar_post_conquista(
                usuario_id=usuario_id,
                usuario_nome=usuario.get("nome", "Atleta"),
                conquista_nome=conquista['nome'],
                conquista_descricao=conquista['descricao'],
                conquista_emoji=conquista.get('icone', '🏆')
            )
        except Exception as e:
            print(f"Erro ao criar post de conquista no feed: {e}")
    
    return novas_conquistas
