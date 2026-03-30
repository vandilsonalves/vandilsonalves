from fastapi import APIRouter, Depends
from datetime import datetime, timedelta, timezone
from routes.auth_routes import get_admin_user
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


@router.get("/admin/retencao/inativos")
async def get_atletas_inativos(dias: int = 30, admin: dict = Depends(get_admin_user)):
    """
    Retorna atletas que não submeteram resultados nos últimos X dias.
    Inclui info de equipe/assessoria para alertas ao dono.
    """
    data_limite = datetime.now(timezone.utc) - timedelta(days=dias)
    data_limite_str = data_limite.strftime("%Y-%m-%d")

    # Buscar todos atletas
    atletas = await db.usuarios.find(
        {"role": "atleta"},
        {"_id": 0, "id": 1, "nome": 1, "email": 1, "equipe": 1, "estado": 1,
         "cidade": 1, "total_corridas": 1, "data_criacao": 1, "modalidade_usuario": 1}
    ).to_list(None)

    # Buscar submissões recentes (últimos X dias) agrupadas por usuario_id
    submissoes_recentes = await db.resultados_pendentes.aggregate([
        {"$match": {"data_submissao": {"$gte": data_limite_str}}},
        {"$group": {"_id": "$usuario_id", "ultima_submissao": {"$max": "$data_submissao"}, "total_recente": {"$sum": 1}}}
    ]).to_list(None)

    ativos_ids = {s["_id"] for s in submissoes_recentes}

    # Também checar resultados pela data_competicao
    competicoes_recentes = await db.resultados_pendentes.aggregate([
        {"$match": {"data_competicao": {"$gte": data_limite_str}}},
        {"$group": {"_id": "$usuario_id"}}
    ]).to_list(None)
    ativos_ids.update({c["_id"] for c in competicoes_recentes})

    # Buscar última atividade de cada atleta (qualquer submissão)
    ultima_atividade = await db.resultados_pendentes.aggregate([
        {"$group": {
            "_id": "$usuario_id",
            "ultima_submissao": {"$max": "$data_submissao"},
            "ultima_competicao": {"$max": "$data_competicao"},
            "total_submissoes": {"$sum": 1}
        }}
    ]).to_list(None)
    atividade_map = {a["_id"]: a for a in ultima_atividade}

    inativos = []
    for atleta in atletas:
        if atleta["id"] not in ativos_ids:
            atividade = atividade_map.get(atleta["id"], {})
            ultima = atividade.get("ultima_submissao") or atividade.get("ultima_competicao")

            dias_inativo = None
            if ultima:
                try:
                    ultima_date = datetime.strptime(str(ultima)[:10], "%Y-%m-%d")
                    dias_inativo = (datetime.now() - ultima_date).days
                except Exception:
                    dias_inativo = None

            inativos.append({
                "id": atleta["id"],
                "nome": atleta.get("nome", ""),
                "email": atleta.get("email", ""),
                "equipe": atleta.get("equipe", "") or "Individual",
                "estado": atleta.get("estado", ""),
                "cidade": atleta.get("cidade", ""),
                "total_corridas": atleta.get("total_corridas", 0),
                "modalidade": atleta.get("modalidade_usuario", ""),
                "data_criacao": atleta.get("data_criacao", ""),
                "ultima_atividade": ultima,
                "dias_inativo": dias_inativo,
                "total_submissoes": atividade.get("total_submissoes", 0),
                "nunca_submeteu": atleta["id"] not in atividade_map
            })

    # Ordenar: quem tem mais corridas mas parou primeiro (maior potencial de retorno)
    inativos.sort(key=lambda x: (not x["nunca_submeteu"], -(x["dias_inativo"] or 9999)))

    # Estatísticas gerais
    total_atletas = len(atletas)
    total_inativos = len(inativos)
    total_ativos = total_atletas - total_inativos
    nunca_submeteram = sum(1 for i in inativos if i["nunca_submeteu"])
    pararam = total_inativos - nunca_submeteram

    # Agrupamento por equipe
    equipes_map = {}
    for inativo in inativos:
        eq = inativo["equipe"]
        if eq not in equipes_map:
            equipes_map[eq] = 0
        equipes_map[eq] += 1

    equipes_ranking = sorted(equipes_map.items(), key=lambda x: -x[1])[:15]

    return {
        "resumo": {
            "total_atletas": total_atletas,
            "total_ativos": total_ativos,
            "total_inativos": total_inativos,
            "taxa_retencao": round((total_ativos / total_atletas * 100), 1) if total_atletas > 0 else 0,
            "nunca_submeteram": nunca_submeteram,
            "pararam_de_competir": pararam,
            "periodo_dias": dias
        },
        "equipes_com_inativos": [{"equipe": eq, "inativos": count} for eq, count in equipes_ranking],
        "atletas_inativos": inativos[:200]
    }


@router.post("/admin/retencao/alertar-assessoria")
async def alertar_assessoria_inativos(dados: dict, admin: dict = Depends(get_admin_user)):
    """
    Cria notificações para os donos de assessoria sobre atletas inativos de sua equipe.
    """
    equipe = dados.get("equipe", "")
    if not equipe or equipe == "Individual":
        return {"detail": "Não é possível alertar equipes individuais"}

    # Buscar dono da assessoria (equipe)
    dono = await db.usuarios.find_one(
        {"role": "dono_assessoria", "equipe": equipe},
        {"_id": 0, "id": 1, "nome": 1}
    )
    if not dono:
        # Tentar buscar assessoria pelo nome
        assessoria = await db.assessorias.find_one(
            {"nome": equipe},
            {"_id": 0, "dono_id": 1}
        )
        if assessoria:
            dono = await db.usuarios.find_one(
                {"id": assessoria["dono_id"]},
                {"_id": 0, "id": 1, "nome": 1}
            )

    if not dono:
        return {"detail": f"Dono da assessoria '{equipe}' não encontrado", "enviado": False}

    # Contar inativos desta equipe
    total_atletas_equipe = await db.usuarios.count_documents({"role": "atleta", "equipe": equipe})

    # Criar notificação
    from uuid import uuid4
    notificacao = {
        "id": str(uuid4()),
        "usuario_id": dono["id"],
        "tipo": "alerta_retencao",
        "titulo": "Atletas Inativos na sua Equipe",
        "mensagem": f"Sua equipe '{equipe}' possui atletas que não registraram atividades recentemente. "
                     f"Total de atletas na equipe: {total_atletas_equipe}. "
                     f"Acesse o painel para ver detalhes e engajar seus atletas!",
        "lida": False,
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "dados_extras": {
            "equipe": equipe,
            "total_equipe": total_atletas_equipe
        }
    }
    await db.notificacoes.insert_one(notificacao)

    return {"enviado": True, "dono": dono.get("nome", ""), "equipe": equipe}
