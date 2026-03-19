# /app/backend/routes/badges_routes.py
# Sistema de Gamificação com Badges Visuais

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import io

from config import db
from routes.auth_routes import get_current_user

router = APIRouter(prefix="/badges", tags=["Badges"])


# ==================== DEFINIÇÃO DOS BADGES ====================

BADGES_CONFIG = {
    # === Performance ===
    "atleta_elite": {
        "nome": "Atleta Elite",
        "descricao": "Conquistou 100+ pontos no ranking",
        "icone": "star",
        "cor_primaria": "#FFD700",
        "cor_secundaria": "#FFA500",
        "categoria": "performance",
        "criterio": {"pontos_minimos": 100}
    },
    "corredor_maratona": {
        "nome": "Corredor de Maratona",
        "descricao": "Completou uma prova de 42km",
        "icone": "medal",
        "cor_primaria": "#8B5CF6",
        "cor_secundaria": "#6D28D9",
        "categoria": "performance",
        "criterio": {"distancia_minima": 42}
    },
    "top_10_mes": {
        "nome": "Top 10 do Mês",
        "descricao": "Ficou entre os 10 melhores do mês",
        "icone": "trophy",
        "cor_primaria": "#10B981",
        "cor_secundaria": "#059669",
        "categoria": "performance",
        "criterio": {"ranking_mes_maximo": 10},
        "exclusivo_profissional": True  # Não disponível para Povão
    },
    "podio": {
        "nome": "Pódio",
        "descricao": "Conquistou 1º, 2º ou 3º lugar em uma corrida",
        "icone": "award",
        "cor_primaria": "#F59E0B",
        "cor_secundaria": "#D97706",
        "categoria": "performance",
        "criterio": {"colocacao_maxima": 3},
        "exclusivo_profissional": True  # Não disponível para Povão
    },
    "rei_velocidade": {
        "nome": "Rei da Velocidade",
        "descricao": "Maior pontuação semanal",
        "icone": "zap",
        "cor_primaria": "#EF4444",
        "cor_secundaria": "#DC2626",
        "categoria": "performance",
        "criterio": {"top_semanal": 1},
        "exclusivo_profissional": True  # Não disponível para Povão
    },
    
    # === Participação ===
    "iniciante": {
        "nome": "Iniciante",
        "descricao": "Primeira corrida registrada",
        "icone": "play",
        "cor_primaria": "#06B6D4",
        "cor_secundaria": "#0891B2",
        "categoria": "participacao",
        "criterio": {"corridas_minimas": 1}
    },
    "veterano": {
        "nome": "Veterano",
        "descricao": "Completou 10+ corridas",
        "icone": "shield",
        "cor_primaria": "#3B82F6",
        "cor_secundaria": "#2563EB",
        "categoria": "participacao",
        "criterio": {"corridas_minimas": 10}
    },
    "maratonista": {
        "nome": "Maratonista",
        "descricao": "Completou 20+ corridas",
        "icone": "target",
        "cor_primaria": "#8B5CF6",
        "cor_secundaria": "#7C3AED",
        "categoria": "participacao",
        "criterio": {"corridas_minimas": 20}
    },
    "lenda": {
        "nome": "Lenda",
        "descricao": "Completou 50+ corridas",
        "icone": "crown",
        "cor_primaria": "#FFD700",
        "cor_secundaria": "#FFC000",
        "categoria": "participacao",
        "criterio": {"corridas_minimas": 50}
    },
    "consistente": {
        "nome": "Consistente",
        "descricao": "Participou de corridas em 6 meses consecutivos",
        "icone": "calendar",
        "cor_primaria": "#14B8A6",
        "cor_secundaria": "#0D9488",
        "categoria": "participacao",
        "criterio": {"meses_consecutivos": 6}
    },
    
    # === Especiais ===
    "embaixador_run": {
        "nome": "Embaixador Run",
        "descricao": "Indicou 5+ atletas para a plataforma",
        "icone": "users",
        "cor_primaria": "#EC4899",
        "cor_secundaria": "#DB2777",
        "categoria": "especial",
        "criterio": {"indicacoes_minimas": 5}
    },
    "indicador_bronze": {
        "nome": "Indicador Bronze",
        "descricao": "Indicou 10+ atletas para a plataforma",
        "icone": "award",
        "cor_primaria": "#CD7F32",
        "cor_secundaria": "#B87333",
        "categoria": "especial",
        "criterio": {"indicacoes_minimas": 10}
    },
    "indicador_prata": {
        "nome": "Indicador Prata",
        "descricao": "Indicou 20+ atletas para a plataforma",
        "icone": "medal",
        "cor_primaria": "#C0C0C0",
        "cor_secundaria": "#A8A8A8",
        "categoria": "especial",
        "criterio": {"indicacoes_minimas": 20}
    },
    "indicador_ouro": {
        "nome": "Indicador Ouro",
        "descricao": "Indicou 30+ atletas para a plataforma",
        "icone": "trophy",
        "cor_primaria": "#FFD700",
        "cor_secundaria": "#FFC000",
        "categoria": "especial",
        "criterio": {"indicacoes_minimas": 30}
    },
    "indicador_diamante": {
        "nome": "Indicador Diamante",
        "descricao": "Indicou 50+ atletas para a plataforma",
        "icone": "gem",
        "cor_primaria": "#B9F2FF",
        "cor_secundaria": "#00CED1",
        "categoria": "especial",
        "criterio": {"indicacoes_minimas": 50}
    },
    "influencer": {
        "nome": "Influencer",
        "descricao": "Perfil mais visualizado do mês",
        "icone": "eye",
        "cor_primaria": "#F472B6",
        "cor_secundaria": "#EC4899",
        "categoria": "especial",
        "criterio": {"top_visualizacoes": 1}
    },
    "estrela_assessoria": {
        "nome": "Estrela da Assessoria",
        "descricao": "Maior pontuação da equipe",
        "icone": "sparkles",
        "cor_primaria": "#FBBF24",
        "cor_secundaria": "#F59E0B",
        "categoria": "especial",
        "criterio": {"top_equipe": 1},
        "exclusivo_profissional": True  # Não disponível para Povão
    }
}


# ==================== MODELS ====================

class BadgeResponse(BaseModel):
    id: str
    nome: str
    descricao: str
    icone: str
    cor_primaria: str
    cor_secundaria: str
    categoria: str
    conquistado: bool
    data_conquista: Optional[str] = None


class BadgeAtletaResponse(BaseModel):
    atleta_id: str
    atleta_nome: str
    badges: List[BadgeResponse]
    total_badges: int
    pontos_totais: int


# ==================== FUNÇÕES AUXILIARES ====================

async def verificar_badges_atleta(atleta_id: str) -> List[dict]:
    """Verifica e atualiza os badges de um atleta baseado em seus dados"""
    
    usuario = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not usuario:
        return []
    
    # Buscar dados do atleta
    ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    ranking_povao = await db.ranking_povao.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    
    corridas = await db.corridas.find({"usuario_id": atleta_id}, {"_id": 0}).to_list(None)
    
    pontos_total = ranking.get("pontos_total", 0) if ranking else 0
    if ranking_povao:
        pontos_total = max(pontos_total, ranking_povao.get("pontos_total", 0))
    
    total_corridas = len(corridas)
    
    # Verificar cada badge
    badges_conquistados = []
    
    for badge_id, config in BADGES_CONFIG.items():
        criterio = config.get("criterio", {})
        conquistado = False
        
        # Verificar critérios
        if "pontos_minimos" in criterio:
            conquistado = pontos_total >= criterio["pontos_minimos"]
        
        elif "corridas_minimas" in criterio:
            conquistado = total_corridas >= criterio["corridas_minimas"]
        
        elif "colocacao_maxima" in criterio:
            for c in corridas:
                if c.get("colocacao", 99) <= criterio["colocacao_maxima"]:
                    conquistado = True
                    break
        
        elif "distancia_minima" in criterio:
            for c in corridas:
                dist = c.get("distancia", "0")
                if isinstance(dist, str):
                    dist = float(dist.upper().replace("KM", "").replace("K", "").strip() or 0)
                if dist >= criterio["distancia_minima"]:
                    conquistado = True
                    break
        
        elif "meses_consecutivos" in criterio:
            # Verificar meses consecutivos com corridas
            meses = set()
            for c in corridas:
                data = c.get("data", "")
                if data:
                    mes = data[:7]  # YYYY-MM
                    meses.add(mes)
            
            # Verificar consecutividade
            meses_sorted = sorted(meses)
            consecutivos = 1
            max_consecutivos = 1
            for i in range(1, len(meses_sorted)):
                ano1, mes1 = map(int, meses_sorted[i-1].split('-'))
                ano2, mes2 = map(int, meses_sorted[i].split('-'))
                
                diff_meses = (ano2 - ano1) * 12 + (mes2 - mes1)
                if diff_meses == 1:
                    consecutivos += 1
                    max_consecutivos = max(max_consecutivos, consecutivos)
                else:
                    consecutivos = 1
            
            conquistado = max_consecutivos >= criterio["meses_consecutivos"]
        
        elif "indicacoes_minimas" in criterio:
            # Verificar indicações bem-sucedidas
            total_indicacoes = await db.indicacoes.count_documents({
                "indicador_id": atleta_id,
                "status": "confirmada"
            })
            conquistado = total_indicacoes >= criterio["indicacoes_minimas"]
        
        # Salvar badge no banco se conquistado
        if conquistado:
            badge_existente = await db.badges_atleta.find_one({
                "atleta_id": atleta_id,
                "badge_id": badge_id
            })
            
            if not badge_existente:
                await db.badges_atleta.insert_one({
                    "atleta_id": atleta_id,
                    "badge_id": badge_id,
                    "data_conquista": datetime.now(timezone.utc).isoformat()
                })
        
        # Buscar data de conquista
        badge_db = await db.badges_atleta.find_one({
            "atleta_id": atleta_id,
            "badge_id": badge_id
        }, {"_id": 0})
        
        badges_conquistados.append({
            "id": badge_id,
            "nome": config["nome"],
            "descricao": config["descricao"],
            "icone": config["icone"],
            "cor_primaria": config["cor_primaria"],
            "cor_secundaria": config["cor_secundaria"],
            "categoria": config["categoria"],
            "conquistado": conquistado or (badge_db is not None),
            "data_conquista": badge_db.get("data_conquista") if badge_db else None
        })
    
    return badges_conquistados


# ==================== ENDPOINTS ====================

@router.get("/lista")
async def listar_badges():
    """Lista todos os badges disponíveis no sistema"""
    badges = []
    for badge_id, config in BADGES_CONFIG.items():
        badges.append({
            "id": badge_id,
            "nome": config["nome"],
            "descricao": config["descricao"],
            "icone": config["icone"],
            "cor_primaria": config["cor_primaria"],
            "cor_secundaria": config["cor_secundaria"],
            "categoria": config["categoria"]
        })
    
    return {
        "total": len(badges),
        "categorias": ["performance", "participacao", "especial"],
        "badges": badges
    }


@router.get("/atleta/{atleta_id}")
async def get_badges_atleta(atleta_id: str):
    """Retorna badges de um atleta específico"""
    
    usuario = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Verificar se é atleta do Povão
    is_povao = usuario.get("modalidade_usuario") == "povao_pace_livre"
    
    # Verificar e atualizar badges
    badges = await verificar_badges_atleta(atleta_id)
    
    # Filtrar badges exclusivas do profissional se for atleta do Povão
    if is_povao:
        badges_exclusivos = ["top_10_mes", "podio", "rei_velocidade", "estrela_assessoria"]
        badges = [b for b in badges if b["id"] not in badges_exclusivos]
    
    # Calcular pontos e corridas
    ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    ranking_povao = await db.ranking_povao.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    
    pontos = ranking.get("pontos_total", 0) if ranking else 0
    total_corridas = ranking.get("total_corridas", 0) if ranking else 0
    
    if ranking_povao:
        pontos = max(pontos, ranking_povao.get("pontos_total", 0))
        total_corridas = max(total_corridas, ranking_povao.get("total_corridas", 0))
    
    badges_conquistados = [b for b in badges if b["conquistado"]]
    
    return {
        "atleta_id": atleta_id,
        "atleta_nome": usuario.get("nome", ""),
        "equipe": usuario.get("equipe", ""),
        "modalidade": usuario.get("modalidade_usuario", "profissional_amador"),
        "badges": badges,
        "badges_conquistados": len(badges_conquistados),
        "total_badges": len(badges),
        "pontos_totais": pontos,
        "total_corridas": total_corridas
    }


@router.get("/meus-badges")
async def get_meus_badges(current_user: dict = Depends(get_current_user)):
    """Retorna badges do usuário logado"""
    return await get_badges_atleta(current_user["id"])


@router.get("/atleta/{atleta_id}/card-compartilhamento")
async def gerar_card_compartilhamento(atleta_id: str):
    """Gera dados para o card de compartilhamento em redes sociais"""
    
    usuario = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Buscar badges conquistados
    badges = await verificar_badges_atleta(atleta_id)
    badges_conquistados = [b for b in badges if b["conquistado"]]
    
    # Buscar ranking
    ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    ranking_povao = await db.ranking_povao.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    
    pontos = ranking.get("pontos_total", 0) if ranking else 0
    colocacao = ranking.get("ranking_categoria", 0) if ranking else 0
    total_corridas = ranking.get("total_corridas", 0) if ranking else 0
    
    if ranking_povao:
        pontos = max(pontos, ranking_povao.get("pontos_total", 0))
        if ranking_povao.get("ranking_genero", 0) > 0:
            colocacao = ranking_povao.get("ranking_genero", 0)
        total_corridas = max(total_corridas, ranking_povao.get("total_corridas", 0))
    
    # Texto para compartilhamento
    texto = f"🏆 Meus Badges no Ranking Run Pró!\n\n"
    texto += f"👤 {usuario['nome']}\n"
    texto += f"🎯 {len(badges_conquistados)} badges conquistados\n"
    texto += f"⭐ {pontos} pontos | {total_corridas} corridas\n\n"
    
    if badges_conquistados:
        texto += "🏅 Badges:\n"
        for b in badges_conquistados[:5]:
            texto += f"• {b['nome']}\n"
    
    texto += "\n#RankingRunPro #Corrida #Running"
    
    return {
        "atleta": {
            "id": atleta_id,
            "nome": usuario.get("nome", ""),
            "foto_url": usuario.get("foto_url", ""),
            "equipe": usuario.get("equipe", ""),
            "cidade": usuario.get("cidade", ""),
            "estado": usuario.get("estado", "")
        },
        "stats": {
            "pontos": pontos,
            "colocacao": colocacao,
            "total_corridas": total_corridas,
            "total_badges": len(badges_conquistados)
        },
        "badges": badges_conquistados[:6],  # Máximo 6 badges no card
        "texto_compartilhamento": texto,
        "url_perfil": f"https://assess-photo-fix.preview.emergentagent.com/atleta/{atleta_id}"
    }


@router.get("/ranking-badges")
async def ranking_badges():
    """Retorna ranking de atletas com mais badges"""
    
    pipeline = [
        {"$group": {
            "_id": "$atleta_id",
            "total_badges": {"$sum": 1}
        }},
        {"$sort": {"total_badges": -1}},
        {"$limit": 20}
    ]
    
    ranking = await db.badges_atleta.aggregate(pipeline).to_list(None)
    
    resultado = []
    for i, r in enumerate(ranking, 1):
        usuario = await db.usuarios.find_one({"id": r["_id"]}, {"_id": 0})
        if usuario:
            resultado.append({
                "posicao": i,
                "atleta_id": r["_id"],
                "nome": usuario.get("nome", ""),
                "foto_url": usuario.get("foto_url", ""),
                "equipe": usuario.get("equipe", ""),
                "total_badges": r["total_badges"]
            })
    
    return {
        "total_participantes": len(resultado),
        "ranking": resultado
    }
