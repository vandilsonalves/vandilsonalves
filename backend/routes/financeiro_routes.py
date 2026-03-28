# /app/backend/routes/financeiro_routes.py
# Rotas de dashboard financeiro (Admin)

from fastapi import APIRouter, Depends
from datetime import datetime, timezone, timedelta
import logging

from config import db
from routes.auth_routes import get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/financeiro", tags=["financeiro"])


@router.get("/resumo")
async def resumo_financeiro(admin_user: dict = Depends(get_admin_user)):
    """Retorna resumo financeiro completo: totais, por gateway, por periodo"""

    # Todas as transacoes
    all_txs = []
    cursor = db.payment_transactions.find({}, {"_id": 0})
    async for tx in cursor:
        all_txs.append(tx)

    total_transacoes = len(all_txs)
    pagas = [t for t in all_txs if t.get("payment_status") == "paid"]
    pendentes = [t for t in all_txs if t.get("payment_status") == "pending"]

    receita_total = sum(t.get("amount", 0) for t in pagas)
    receita_pix = sum(t.get("amount", 0) for t in pagas if t.get("tipo") == "pix")
    receita_cartao = sum(t.get("amount", 0) for t in pagas if t.get("tipo") == "cartao")

    # Receita por dia (ultimos 30 dias)
    hoje = datetime.now(timezone.utc)
    inicio_30d = (hoje - timedelta(days=30)).isoformat()
    receita_diaria = {}
    for t in pagas:
        data = t.get("data_criacao", "")
        if data >= inicio_30d:
            dia = data[:10]
            receita_diaria[dia] = receita_diaria.get(dia, 0) + t.get("amount", 0)

    dias_30 = []
    for i in range(30, -1, -1):
        d = (hoje - timedelta(days=i)).strftime("%Y-%m-%d")
        dias_30.append({"data": d, "valor": round(receita_diaria.get(d, 0), 2)})

    # Receita por mes (ultimos 12 meses)
    receita_mensal = {}
    for t in pagas:
        data = t.get("data_criacao", "")
        if len(data) >= 7:
            mes = data[:7]
            receita_mensal[mes] = receita_mensal.get(mes, 0) + t.get("amount", 0)

    meses_labels = []
    for i in range(11, -1, -1):
        d = hoje - timedelta(days=i * 30)
        m = d.strftime("%Y-%m")
        meses_labels.append({"mes": m, "valor": round(receita_mensal.get(m, 0), 2)})
    # Dedup meses
    seen = set()
    meses_uniq = []
    for m in meses_labels:
        if m["mes"] not in seen:
            seen.add(m["mes"])
            meses_uniq.append(m)

    # Transacoes recentes (top 20)
    recentes = sorted(all_txs, key=lambda x: x.get("data_criacao", ""), reverse=True)[:20]
    recentes_clean = []
    for t in recentes:
        recentes_clean.append({
            "id": t.get("id", ""),
            "txid": t.get("txid", t.get("session_id", "")),
            "gateway": t.get("gateway", "desconhecido"),
            "tipo": t.get("tipo", "cartao"),
            "amount": t.get("amount", 0),
            "parcelas": t.get("parcelas", 1),
            "valor_parcela": t.get("valor_parcela", t.get("amount", 0)),
            "payment_status": t.get("payment_status", "unknown"),
            "user_nome": t.get("user_nome", ""),
            "user_email": t.get("user_email", ""),
            "data_criacao": t.get("data_criacao", ""),
            "plano_nome": t.get("plano_nome", t.get("plano", "")),
        })

    # Distribuicao por tipo (pix vs cartao)
    count_pix = len([t for t in all_txs if t.get("tipo") == "pix"])
    count_cartao = len([t for t in all_txs if t.get("tipo") == "cartao"])

    return {
        "totais": {
            "receita_total": round(receita_total, 2),
            "receita_pix": round(receita_pix, 2),
            "receita_cartao": round(receita_cartao, 2),
            "total_transacoes": total_transacoes,
            "transacoes_pagas": len(pagas),
            "transacoes_pendentes": len(pendentes),
            "ticket_medio": round(receita_total / len(pagas), 2) if pagas else 0,
        },
        "distribuicao_gateway": {
            "pix": {"count": count_pix, "valor": round(receita_pix, 2)},
            "cartao": {"count": count_cartao, "valor": round(receita_cartao, 2)},
        },
        "receita_diaria": dias_30,
        "receita_mensal": meses_uniq,
        "transacoes_recentes": recentes_clean,
    }


@router.post("/relatorio-semanal/enviar")
async def enviar_relatorio_manual(admin_user: dict = Depends(get_admin_user)):
    """Dispara manualmente o relatorio semanal por e-mail"""
    from services.relatorio_semanal import enviar_relatorio_semanal
    try:
        await enviar_relatorio_semanal()
        return {"status": "success", "message": "Relatorio semanal enviado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao enviar relatorio semanal: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/conversao")
async def metricas_conversao(admin_user: dict = Depends(get_admin_user)):
    """Retorna metricas de funil de conversao: Visitantes -> Cadastro -> Pagamento"""

    agora = datetime.now(timezone.utc)

    # Periodos: 7d, 30d, total
    periodos = {
        "7d": (agora - timedelta(days=7)).isoformat(),
        "30d": (agora - timedelta(days=30)).isoformat(),
    }

    resultado = {}

    for label, inicio in periodos.items():
        # Visitantes unicos no periodo
        pipeline_visitors = [
            {"$match": {"data": {"$gte": inicio[:10]}}},
            {"$project": {"unique_count": {"$size": {"$ifNull": ["$visitors", []]}}, "total_hits": 1}},
            {"$group": {"_id": None, "unique_visitors": {"$sum": "$unique_count"}, "total_hits": {"$sum": "$total_hits"}}}
        ]
        visitors_result = await db.visitas_diarias.aggregate(pipeline_visitors).to_list(1)
        unique_visitors = visitors_result[0]["unique_visitors"] if visitors_result else 0
        total_hits = visitors_result[0]["total_hits"] if visitors_result else 0

        # Cadastros no periodo
        cadastros = await db.usuarios.count_documents({
            "role": "atleta",
            "data_criacao": {"$gte": inicio}
        })

        # Pagamentos confirmados no periodo
        pagamentos = await db.payment_transactions.count_documents({
            "payment_status": "paid",
            "data_criacao": {"$gte": inicio}
        })

        # Receita no periodo
        txs_pagas = []
        cursor = db.payment_transactions.find(
            {"payment_status": "paid", "data_criacao": {"$gte": inicio}},
            {"_id": 0, "amount": 1}
        )
        async for tx in cursor:
            txs_pagas.append(tx)
        receita = sum(t.get("amount", 0) for t in txs_pagas)

        # Taxas de conversao
        taxa_cadastro = round((cadastros / unique_visitors * 100), 1) if unique_visitors > 0 else 0
        taxa_pagamento = round((pagamentos / cadastros * 100), 1) if cadastros > 0 else 0
        taxa_total = round((pagamentos / unique_visitors * 100), 1) if unique_visitors > 0 else 0

        resultado[label] = {
            "visitantes_unicos": unique_visitors,
            "total_pageviews": total_hits,
            "cadastros": cadastros,
            "pagamentos": pagamentos,
            "receita": round(receita, 2),
            "taxa_visitante_cadastro": taxa_cadastro,
            "taxa_cadastro_pagamento": taxa_pagamento,
            "taxa_conversao_total": taxa_total,
        }

    # Totais historicos (all time)
    total_atletas = await db.usuarios.count_documents({"role": "atleta"})
    total_pagamentos = await db.payment_transactions.count_documents({"payment_status": "paid"})
    all_visitors = await db.visitas_diarias.aggregate([
        {"$project": {"unique_count": {"$size": {"$ifNull": ["$visitors", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$unique_count"}}}
    ]).to_list(1)
    total_visitors = all_visitors[0]["total"] if all_visitors else 0

    resultado["total"] = {
        "visitantes_unicos": total_visitors,
        "cadastros": total_atletas,
        "pagamentos": total_pagamentos,
        "taxa_visitante_cadastro": round((total_atletas / total_visitors * 100), 1) if total_visitors > 0 else 0,
        "taxa_cadastro_pagamento": round((total_pagamentos / total_atletas * 100), 1) if total_atletas > 0 else 0,
        "taxa_conversao_total": round((total_pagamentos / total_visitors * 100), 1) if total_visitors > 0 else 0,
    }

    # Funil diario (ultimos 14 dias)
    funil_diario = []
    for i in range(13, -1, -1):
        d = (agora - timedelta(days=i)).strftime("%Y-%m-%d")
        dia_inicio = f"{d}T00:00:00"
        dia_fim = f"{d}T23:59:59"

        visita = await db.visitas_diarias.find_one({"data": d}, {"_id": 0, "visitors": 1})
        vis_count = len(visita.get("visitors", [])) if visita else 0

        cad_count = await db.usuarios.count_documents({
            "role": "atleta",
            "data_criacao": {"$gte": dia_inicio, "$lte": dia_fim}
        })

        pag_count = await db.payment_transactions.count_documents({
            "payment_status": "paid",
            "data_criacao": {"$gte": dia_inicio, "$lte": dia_fim}
        })

        funil_diario.append({
            "data": d,
            "visitantes": vis_count,
            "cadastros": cad_count,
            "pagamentos": pag_count,
        })

    resultado["funil_diario"] = funil_diario

    return resultado
