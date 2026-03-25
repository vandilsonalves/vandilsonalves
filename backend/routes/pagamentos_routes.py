# /app/backend/routes/pagamentos_routes.py
# Rotas de pagamento com Stripe para Atleta Premium

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import os
import uuid
import logging

from config import db
from routes.auth_routes import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])

# Plano fixo - NÃO aceitar valores do frontend
PLANO_PREMIUM = {
    "id": "atleta_premium_2026",
    "nome": "Atleta Premium",
    "valor": 97.00,
    "moeda": "brl",
    "validade": "2026-12-31",
    "descricao": "Acesso completo ao Ranking Run Pro ate 31/12/2026"
}


class CheckoutRequest(BaseModel):
    origin_url: str


class CheckoutStatusRequest(BaseModel):
    session_id: str


@router.post("/checkout")
async def criar_checkout(dados: CheckoutRequest, request: Request, current_user: dict = Depends(get_current_user)):
    """Cria sessao de checkout Stripe para o plano Atleta Premium"""
    from emergentintegrations.payments.stripe.checkout import (
        StripeCheckout, CheckoutSessionRequest, CheckoutSessionResponse
    )

    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Stripe nao configurado")

    # Verificar se usuario ja tem acesso ativo
    auth_existente = await db.autorizacoes.find_one({
        "atleta_id": current_user["id"],
        "status": "ativa"
    })
    if auth_existente:
        try:
            exp_str = auth_existente["data_expiracao"].replace("Z", "+00:00")
            if "+" not in exp_str and "T" in exp_str:
                exp_str = exp_str + "+00:00"
            data_exp = datetime.fromisoformat(exp_str)
            if data_exp.tzinfo is None:
                data_exp = data_exp.replace(tzinfo=timezone.utc)
            if data_exp > datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="Voce ja possui acesso Premium ativo")
        except HTTPException:
            raise
        except Exception:
            pass

    origin = dados.origin_url.rstrip("/")
    success_url = f"{origin}/pagamento/sucesso?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin}/pagamento/cancelado"

    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"

    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)

    checkout_request = CheckoutSessionRequest(
        amount=PLANO_PREMIUM["valor"],
        currency=PLANO_PREMIUM["moeda"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": current_user["id"],
            "user_email": current_user.get("email", ""),
            "plano": PLANO_PREMIUM["id"],
            "validade": PLANO_PREMIUM["validade"]
        }
    )

    session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)

    # Registrar transacao como pendente
    transaction = {
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "user_id": current_user["id"],
        "user_email": current_user.get("email", ""),
        "plano": PLANO_PREMIUM["id"],
        "plano_nome": PLANO_PREMIUM["nome"],
        "amount": PLANO_PREMIUM["valor"],
        "currency": PLANO_PREMIUM["moeda"],
        "payment_status": "pending",
        "status": "initiated",
        "metadata": {
            "user_id": current_user["id"],
            "plano": PLANO_PREMIUM["id"],
            "validade": PLANO_PREMIUM["validade"]
        },
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "data_atualizacao": datetime.now(timezone.utc).isoformat()
    }
    await db.payment_transactions.insert_one(transaction)

    return {
        "url": session.url,
        "session_id": session.session_id,
        "plano": PLANO_PREMIUM
    }


@router.get("/status/{session_id}")
async def verificar_status_pagamento(session_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    """Verifica o status de uma sessao de checkout"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutStatusResponse

    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Stripe nao configurado")

    # Verificar se a transacao pertence ao usuario
    transaction = await db.payment_transactions.find_one(
        {"session_id": session_id},
        {"_id": 0}
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacao nao encontrada")

    if transaction.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Se ja foi processada com sucesso, retornar direto
    if transaction.get("payment_status") == "paid":
        return {
            "status": "complete",
            "payment_status": "paid",
            "plano": PLANO_PREMIUM["nome"],
            "validade": PLANO_PREMIUM["validade"],
            "ja_processado": True
        }

    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)

    try:
        checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
    except Exception as e:
        logger.error(f"Erro ao consultar status Stripe: {e}")
        raise HTTPException(status_code=500, detail="Erro ao consultar pagamento")

    # Atualizar transacao
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "data_atualizacao": datetime.now(timezone.utc).isoformat()
        }}
    )

    # Se pagamento confirmado, ativar acesso
    if checkout_status.payment_status == "paid" and transaction.get("payment_status") != "paid":
        await _ativar_acesso_premium(current_user["id"], session_id)

    return {
        "status": checkout_status.status,
        "payment_status": checkout_status.payment_status,
        "amount_total": checkout_status.amount_total,
        "currency": checkout_status.currency,
        "plano": PLANO_PREMIUM["nome"],
        "validade": PLANO_PREMIUM["validade"]
    }


@router.get("/meu-plano")
async def meu_plano(current_user: dict = Depends(get_current_user)):
    """Retorna informacoes do plano do usuario"""
    # Admin sempre Premium
    if current_user.get("role") in ["admin", "super_admin"]:
        return {
            "status": "autorizado",
            "tipo": "admin",
            "plano": "Admin",
            "expira_em": None,
            "dias_restantes": None,
            "tem_acesso_premium": True
        }

    # Verificar autorizacao ativa
    auth = await db.autorizacoes.find_one({
        "atleta_id": current_user["id"],
        "status": "ativa"
    }, {"_id": 0})

    agora = datetime.now(timezone.utc)

    if auth:
        try:
            exp_str = auth["data_expiracao"].replace("Z", "+00:00")
            if "+" not in exp_str and "T" in exp_str:
                exp_str = exp_str + "+00:00"
            data_exp = datetime.fromisoformat(exp_str)
            if data_exp.tzinfo is None:
                data_exp = data_exp.replace(tzinfo=timezone.utc)
        except Exception:
            data_exp = agora

        if data_exp > agora:
            return {
                "status": "autorizado",
                "tipo": auth.get("tipo", "premium"),
                "plano": PLANO_PREMIUM["nome"],
                "expira_em": data_exp.isoformat(),
                "dias_restantes": (data_exp - agora).days,
                "tem_acesso_premium": True
            }

    # Verificar periodo de teste (30 dias)
    data_criacao_str = current_user.get("data_criacao", agora.isoformat())
    try:
        dc = data_criacao_str.replace("Z", "+00:00")
        if "+" not in dc and "T" in dc:
            dc = dc + "+00:00"
        data_criacao = datetime.fromisoformat(dc)
        if data_criacao.tzinfo is None:
            data_criacao = data_criacao.replace(tzinfo=timezone.utc)
    except Exception:
        data_criacao = agora

    dias_desde_criacao = (agora - data_criacao).days

    if dias_desde_criacao <= 30:
        return {
            "status": "em_teste",
            "tipo": "teste",
            "plano": "Periodo de Teste",
            "expira_em": (data_criacao + timedelta(days=30)).isoformat(),
            "dias_restantes": 30 - dias_desde_criacao,
            "tem_acesso_premium": True
        }

    return {
        "status": "expirado",
        "tipo": None,
        "plano": None,
        "expira_em": None,
        "dias_restantes": 0,
        "tem_acesso_premium": False,
        "valor_plano": PLANO_PREMIUM["valor"],
        "moeda_plano": PLANO_PREMIUM["moeda"]
    }


async def _ativar_acesso_premium(user_id: str, session_id: str):
    """Ativa o acesso premium para o usuario apos pagamento confirmado"""
    agora = datetime.now(timezone.utc)
    data_expiracao = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    # Desativar autorizacoes anteriores
    await db.autorizacoes.update_many(
        {"atleta_id": user_id, "status": "ativa"},
        {"$set": {"status": "substituida", "data_substituicao": agora.isoformat()}}
    )

    # Criar nova autorizacao
    autorizacao = {
        "id": str(uuid.uuid4()),
        "atleta_id": user_id,
        "tipo": "premium",
        "duracao_dias": (data_expiracao - agora).days,
        "data_criacao": agora.isoformat(),
        "data_expiracao": data_expiracao.isoformat(),
        "criado_por": "stripe",
        "criado_por_nome": "Pagamento Stripe",
        "observacao": f"Plano Atleta Premium - Sessao {session_id}",
        "status": "ativa",
        "origem_pagamento": session_id
    }
    await db.autorizacoes.insert_one(autorizacao)

    # Atualizar transacao
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "payment_status": "paid",
            "status": "complete",
            "data_atualizacao": agora.isoformat(),
            "autorizacao_id": autorizacao["id"]
        }}
    )

    logger.info(f"Acesso Premium ativado para usuario {user_id} via sessao {session_id}")
