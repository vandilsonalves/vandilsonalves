# /app/backend/routes/webhook_stripe_routes.py
# Webhook do Stripe para processar eventos de pagamento

from fastapi import APIRouter, Request, HTTPException
import os
import logging

from config import db
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Processa webhooks do Stripe"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout

    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Stripe nao configurado")

    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")

    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)

    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
    except Exception as e:
        logger.error(f"Erro ao processar webhook Stripe: {e}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    logger.info(f"Webhook Stripe recebido: event_type={webhook_response.event_type}, session_id={webhook_response.session_id}, payment_status={webhook_response.payment_status}")

    session_id = webhook_response.session_id
    if not session_id:
        return {"status": "ignored", "reason": "no session_id"}

    # Buscar transacao
    transaction = await db.payment_transactions.find_one(
        {"session_id": session_id},
        {"_id": 0}
    )

    if not transaction:
        logger.warning(f"Transacao nao encontrada para session_id: {session_id}")
        return {"status": "ignored", "reason": "transaction not found"}

    # Atualizar status da transacao
    agora = datetime.now(timezone.utc)
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "payment_status": webhook_response.payment_status,
            "event_type": webhook_response.event_type,
            "event_id": webhook_response.event_id,
            "data_atualizacao": agora.isoformat()
        }}
    )

    # Se pagamento confirmado, ativar acesso premium
    if webhook_response.payment_status == "paid" and transaction.get("payment_status") != "paid":
        user_id = transaction.get("user_id") or webhook_response.metadata.get("user_id")
        if user_id:
            await _ativar_acesso_via_webhook(user_id, session_id)

    return {"status": "processed", "event_type": webhook_response.event_type}


async def _ativar_acesso_via_webhook(user_id: str, session_id: str):
    """Ativa acesso premium via webhook"""
    agora = datetime.now(timezone.utc)
    data_expiracao = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    # Verificar se ja tem autorizacao ativa deste pagamento
    existing = await db.autorizacoes.find_one({
        "atleta_id": user_id,
        "origem_pagamento": session_id,
        "status": "ativa"
    })
    if existing:
        return

    # Desativar autorizacoes anteriores
    await db.autorizacoes.update_many(
        {"atleta_id": user_id, "status": "ativa"},
        {"$set": {"status": "substituida", "data_substituicao": agora.isoformat()}}
    )

    autorizacao = {
        "id": str(uuid.uuid4()),
        "atleta_id": user_id,
        "tipo": "premium",
        "duracao_dias": (data_expiracao - agora).days,
        "data_criacao": agora.isoformat(),
        "data_expiracao": data_expiracao.isoformat(),
        "criado_por": "stripe_webhook",
        "criado_por_nome": "Pagamento Stripe (Webhook)",
        "observacao": f"Plano Atleta Premium - Webhook Session {session_id}",
        "status": "ativa",
        "origem_pagamento": session_id
    }
    await db.autorizacoes.insert_one(autorizacao)

    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "payment_status": "paid",
            "status": "complete",
            "data_atualizacao": agora.isoformat(),
            "autorizacao_id": autorizacao["id"]
        }}
    )

    logger.info(f"[WEBHOOK] Acesso Premium ativado para usuario {user_id}")
