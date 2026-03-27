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
    receita_pix = sum(t.get("amount", 0) for t in pagas if t.get("gateway") == "efi_bank")
    receita_cartao = sum(t.get("amount", 0) for t in pagas if t.get("gateway") == "stripe")

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

    # Distribuicao por gateway
    count_pix = len([t for t in all_txs if t.get("gateway") == "efi_bank"])
    count_cartao = len([t for t in all_txs if t.get("gateway") == "stripe"])

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
