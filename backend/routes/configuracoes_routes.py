# /app/backend/routes/configuracoes_routes.py
# Módulo de Configurações do Sistema - Regras e Pontuação

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime, timezone

from config import db
from routes.auth_routes import get_current_user, get_admin_user

router = APIRouter(tags=["Configurações"])


# ==================== MODELOS ====================

class TabelaPontuacaoNormal(BaseModel):
    primeiro: int = 10
    segundo: int = 9
    terceiro: int = 8
    quarto: int = 7
    quinto: int = 6
    sexto: int = 5
    setimo: int = 4
    oitavo: int = 3
    nono: int = 2
    decimo: int = 1


class TabelaPontuacaoPCD(BaseModel):
    primeiro: int = 10
    segundo: int = 9
    terceiro: int = 8


class TabelaPontuacaoPovao(BaseModel):
    faixa_5_9km: int = 5
    faixa_10_20km: int = 7
    faixa_21km_mais: int = 9


class TabelaPontuacaoEquipes(BaseModel):
    por_atleta: float = 0.5
    por_resultado: float = 1.0
    bonus_2_a_5_lugar: float = 0.5
    bonus_1_lugar: float = 1.0


class ConfiguracoesGerais(BaseModel):
    prazo_submissao_dias: int = 30
    minimo_provas_normal: int = 12
    minimo_provas_pcd: int = 8
    pontos_status_elite: int = 100


class RegrasTextos(BaseModel):
    titulo_profissional: str = "RANKING PROFISSIONAL/AMADOR"
    descricao_profissional: str = "Os atletas acumulam pontos ao participar de corridas oficiais. A pontuação varia de acordo com a colocação."
    titulo_povao: str = "RANKING DA GALERA"
    descricao_galera: str = "O Ranking da Galera é uma modalidade especial que valoriza a participação acima da colocação. Aqui, todos ganham pontos por correr, independente de onde chegaram!"
    titulo_equipes: str = "RANKING DAS EQUIPES"
    descricao_equipes: str = "A Liga Nacional de Assessorias é o sistema oficial de classificação de equipes do Ranking Run. Ela avalia assessorias esportivas de corrida de rua em todo o Brasil com base em critérios técnicos e desempenho dos atletas vinculados."


class ConfiguracoesSistema(BaseModel):
    pontuacao_normal: TabelaPontuacaoNormal = TabelaPontuacaoNormal()
    pontuacao_pcd: TabelaPontuacaoPCD = TabelaPontuacaoPCD()
    pontuacao_povao: TabelaPontuacaoPovao = TabelaPontuacaoPovao()
    pontuacao_equipes: TabelaPontuacaoEquipes = TabelaPontuacaoEquipes()
    configuracoes_gerais: ConfiguracoesGerais = ConfiguracoesGerais()
    textos: RegrasTextos = RegrasTextos()


# ==================== VALORES PADRÃO ====================

CONFIGURACOES_PADRAO = {
    "id": "config_sistema",
    "pontuacao_normal": {
        "primeiro": 10, "segundo": 9, "terceiro": 8, "quarto": 7, "quinto": 6,
        "sexto": 5, "setimo": 4, "oitavo": 3, "nono": 2, "decimo": 1
    },
    "pontuacao_pcd": {
        "primeiro": 10, "segundo": 9, "terceiro": 8
    },
    "pontuacao_povao": {
        "faixa_5_9km": 5, "faixa_10_20km": 7, "faixa_21km_mais": 9
    },
    "pontuacao_equipes": {
        "por_atleta": 0.5, "por_resultado": 1.0,
        "bonus_2_a_5_lugar": 0.5, "bonus_1_lugar": 1.0
    },
    "configuracoes_gerais": {
        "prazo_submissao_dias": 30,
        "minimo_provas_normal": 12,
        "minimo_provas_pcd": 8,
        "pontos_status_elite": 100
    },
    "textos": {
        "titulo_profissional": "RANKING PROFISSIONAL/AMADOR",
        "descricao_profissional": "Os atletas acumulam pontos ao participar de corridas oficiais. A pontuação varia de acordo com a colocação.",
        "titulo_povao": "RANKING DA GALERA",
        "descricao_galera": "O Ranking da Galera é uma modalidade especial que valoriza a participação acima da colocação. Aqui, todos ganham pontos por correr, independente de onde chegaram!",
        "titulo_equipes": "RANKING DAS EQUIPES",
        "descricao_equipes": "A Liga Nacional de Assessorias é o sistema oficial de classificação de equipes do Ranking Run. Ela avalia assessorias esportivas de corrida de rua em todo o Brasil com base em critérios técnicos e desempenho dos atletas vinculados."
    },
    "ultima_atualizacao": None,
    "atualizado_por": None
}


# ==================== ENDPOINTS PÚBLICOS ====================

@router.get("/configuracoes/regras")
async def get_regras_sistema():
    """
    Retorna as regras e configurações do sistema (público)
    Usado na página de regras visível para todos os usuários
    """
    config = await db.configuracoes.find_one({"id": "config_sistema"}, {"_id": 0})
    
    if not config:
        # Inicializar com valores padrão se não existir
        await db.configuracoes.insert_one(CONFIGURACOES_PADRAO.copy())
        config = CONFIGURACOES_PADRAO.copy()
    
    # Formatar para exibição na página de regras
    pontuacao_normal = config.get("pontuacao_normal", {})
    pontuacao_pcd = config.get("pontuacao_pcd", {})
    pontuacao_povao = config.get("pontuacao_povao", {})
    pontuacao_equipes = config.get("pontuacao_equipes", {})
    config_gerais = config.get("configuracoes_gerais", {})
    textos = config.get("textos", {})
    
    return {
        "ranking_profissional": {
            "titulo": textos.get("titulo_profissional", "RANKING PROFISSIONAL/AMADOR"),
            "descricao": textos.get("descricao_profissional", ""),
            "pontuacao_normal": [
                {"posicao": "1º lugar", "pontos": pontuacao_normal.get("primeiro", 10)},
                {"posicao": "2º lugar", "pontos": pontuacao_normal.get("segundo", 9)},
                {"posicao": "3º lugar", "pontos": pontuacao_normal.get("terceiro", 8)},
                {"posicao": "4º lugar", "pontos": pontuacao_normal.get("quarto", 7)},
                {"posicao": "5º lugar", "pontos": pontuacao_normal.get("quinto", 6)},
                {"posicao": "6º lugar", "pontos": pontuacao_normal.get("sexto", 5)},
                {"posicao": "7º lugar", "pontos": pontuacao_normal.get("setimo", 4)},
                {"posicao": "8º lugar", "pontos": pontuacao_normal.get("oitavo", 3)},
                {"posicao": "9º lugar", "pontos": pontuacao_normal.get("nono", 2)},
                {"posicao": "10º lugar", "pontos": pontuacao_normal.get("decimo", 1)},
            ],
            "pontuacao_pcd": [
                {"posicao": "1º lugar", "pontos": pontuacao_pcd.get("primeiro", 10)},
                {"posicao": "2º lugar", "pontos": pontuacao_pcd.get("segundo", 9)},
                {"posicao": "3º lugar", "pontos": pontuacao_pcd.get("terceiro", 8)},
            ],
            "minimo_provas_normal": config_gerais.get("minimo_provas_normal", 12),
            "minimo_provas_pcd": config_gerais.get("minimo_provas_pcd", 8),
            "pontos_elite": config_gerais.get("pontos_status_elite", 100)
        },
        "ranking_povao": {
            "titulo": textos.get("titulo_povao", "RANKING DA GALERA"),
            "descricao": textos.get("descricao_galera", ""),
            "faixas": [
                {"distancia": "5km a 9km", "pontos": pontuacao_povao.get("faixa_5_9km", 5)},
                {"distancia": "10km a 20km", "pontos": pontuacao_povao.get("faixa_10_20km", 7)},
                {"distancia": "21km ou mais", "pontos": pontuacao_povao.get("faixa_21km_mais", 9)},
            ]
        },
        "ranking_equipes": {
            "titulo": textos.get("titulo_equipes", "RANKING DAS EQUIPES"),
            "descricao": textos.get("descricao_equipes", ""),
            "pontuacao": [
                {"criterio": "Por atleta vinculado", "pontos": f"+{pontuacao_equipes.get('por_atleta', 0.5)}"},
                {"criterio": "Por resultado aprovado", "pontos": f"+{pontuacao_equipes.get('por_resultado', 1.0)}"},
                {"criterio": "Bônus 2º ao 5º lugar", "pontos": f"+{pontuacao_equipes.get('bonus_2_a_5_lugar', 0.5)}"},
                {"criterio": "Bônus 1º lugar (vitória)", "pontos": f"+{pontuacao_equipes.get('bonus_1_lugar', 1.0)}"},
            ]
        },
        "configuracoes_gerais": {
            "prazo_submissao_dias": config_gerais.get("prazo_submissao_dias", 30),
            "minimo_provas_normal": config_gerais.get("minimo_provas_normal", 12),
            "minimo_provas_pcd": config_gerais.get("minimo_provas_pcd", 8),
            "pontos_status_elite": config_gerais.get("pontos_status_elite", 100)
        },
        "ultima_atualizacao": config.get("ultima_atualizacao"),
        "atualizado_por": config.get("atualizado_por")
    }


# ==================== ENDPOINTS ADMIN ====================

@router.get("/admin/configuracoes")
async def get_configuracoes_admin(current_user: dict = Depends(get_admin_user)):
    """
    Retorna configurações completas para edição no painel admin
    """
    config = await db.configuracoes.find_one({"id": "config_sistema"}, {"_id": 0})
    
    if not config:
        await db.configuracoes.insert_one(CONFIGURACOES_PADRAO.copy())
        config = CONFIGURACOES_PADRAO.copy()
    
    return config


@router.put("/admin/configuracoes")
async def atualizar_configuracoes(
    dados: ConfiguracoesSistema,
    current_user: dict = Depends(get_admin_user)
):
    """
    Atualiza as configurações do sistema (apenas admin)
    """
    config_atualizada = {
        "id": "config_sistema",
        "pontuacao_normal": dados.pontuacao_normal.model_dump(),
        "pontuacao_pcd": dados.pontuacao_pcd.model_dump(),
        "pontuacao_povao": dados.pontuacao_povao.model_dump(),
        "pontuacao_equipes": dados.pontuacao_equipes.model_dump(),
        "configuracoes_gerais": dados.configuracoes_gerais.model_dump(),
        "textos": dados.textos.model_dump(),
        "ultima_atualizacao": datetime.now(timezone.utc).isoformat(),
        "atualizado_por": current_user.get("nome", "Admin")
    }
    
    await db.configuracoes.update_one(
        {"id": "config_sistema"},
        {"$set": config_atualizada},
        upsert=True
    )
    
    return {
        "message": "Configurações atualizadas com sucesso!",
        "atualizado_em": config_atualizada["ultima_atualizacao"],
        "atualizado_por": config_atualizada["atualizado_por"]
    }


@router.post("/admin/configuracoes/resetar")
async def resetar_configuracoes(current_user: dict = Depends(get_admin_user)):
    """
    Reseta as configurações para os valores padrão
    """
    config_padrao = CONFIGURACOES_PADRAO.copy()
    config_padrao["ultima_atualizacao"] = datetime.now(timezone.utc).isoformat()
    config_padrao["atualizado_por"] = f"{current_user.get('nome', 'Admin')} (reset)"
    
    await db.configuracoes.update_one(
        {"id": "config_sistema"},
        {"$set": config_padrao},
        upsert=True
    )
    
    return {
        "message": "Configurações resetadas para os valores padrão!",
        "configuracoes": config_padrao
    }
