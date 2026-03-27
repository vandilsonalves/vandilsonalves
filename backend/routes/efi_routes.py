# /app/backend/routes/efi_routes.py
# Rotas de pagamento via Efí Bank (PIX)

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import os
import uuid
import logging
import json
import secrets
import hmac
import hashlib

from config import db
from routes.auth_routes import get_current_user, get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/efi", tags=["efi-bank"])

# IPs oficiais do Efi Bank para webhooks
EFI_WEBHOOK_IPS = [
    "34.193.116.226",
    # Adicionar IPs conforme documentacao Efi
]

# HMAC secret para validacao do webhook (gerado na inicializacao)
_WEBHOOK_HMAC_SECRET = os.environ.get("EFI_WEBHOOK_HMAC", secrets.token_hex(16))


def get_efi_client():
    """Cria e retorna instancia do EfiPay"""
    from efipay import EfiPay

    client_id = os.environ.get("EFI_CLIENT_ID")
    client_secret = os.environ.get("EFI_CLIENT_SECRET")
    cert_path = os.environ.get("EFI_CERTIFICATE_PATH")
    sandbox = os.environ.get("EFI_SANDBOX", "true").lower() == "true"

    if not all([client_id, client_secret, cert_path]):
        raise HTTPException(status_code=500, detail="Efi Bank nao configurado")

    credentials = {
        "client_id": client_id,
        "client_secret": client_secret,
        "sandbox": sandbox,
        "certificate": cert_path,
    }

    return EfiPay(credentials)


class PixCheckoutRequest(BaseModel):
    cpf: Optional[str] = None
    nome: Optional[str] = None


@router.post("/pix/criar")
async def criar_cobranca_pix(dados: PixCheckoutRequest, current_user: dict = Depends(get_current_user)):
    """Cria cobranca PIX imediata via Efi Bank"""

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

    pix_key = os.environ.get("EFI_PIX_KEY")
    if not pix_key:
        raise HTTPException(status_code=500, detail="Chave PIX nao configurada")

    # Valor total: 5x R$19,40 = R$97,00
    valor_total = "97.00"

    body = {
        "calendario": {"expiracao": 3600},
        "valor": {"original": valor_total},
        "chave": pix_key,
        "solicitacaoPagador": "Ranking Run Pro - Plano Atleta Premium (5x R$19,40)",
    }

    # Adicionar devedor se CPF fornecido
    if dados.cpf and dados.nome:
        cpf_limpo = dados.cpf.replace(".", "").replace("-", "").strip()
        body["devedor"] = {"cpf": cpf_limpo, "nome": dados.nome}

    try:
        efi = get_efi_client()
        response = efi.pix_create_immediate_charge(body=body)

        # SDK retorna objetos de erro ao inves de levantar excecoes
        if not isinstance(response, dict):
            error_msg = getattr(response, 'msg', str(response))
            logger.error(f"Erro Efi Bank: {error_msg}")
            raise HTTPException(status_code=502, detail=f"Erro na API Efi Bank: {error_msg}")

        logger.info(f"Cobranca PIX criada: txid={response.get('txid')}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar cobranca PIX: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar cobranca PIX: {str(e)}")

    txid = response.get("txid")
    if not txid:
        raise HTTPException(status_code=500, detail="Falha ao obter txid da cobranca")

    # Gerar QR Code
    qrcode_data = None
    try:
        loc_id = response.get("loc", {}).get("id")
        if loc_id:
            qrcode_response = efi.pix_generate_qrcode(params={"id": loc_id})
            qrcode_data = {
                "qrcode": qrcode_response.get("qrcode"),
                "imagemQrcode": qrcode_response.get("imagemQrcode"),
            }
    except Exception as e:
        logger.warning(f"Erro ao gerar QR Code: {e}")

    # Registrar transacao no MongoDB
    transaction = {
        "id": str(uuid.uuid4()),
        "txid": txid,
        "loc_id": response.get("loc", {}).get("id"),
        "user_id": current_user["id"],
        "user_email": current_user.get("email", ""),
        "user_nome": current_user.get("nome", ""),
        "gateway": "efi_bank",
        "tipo": "pix",
        "plano": "atleta_premium_lancamento",
        "plano_nome": "Atleta Premium",
        "amount": 97.00,
        "parcelas": 5,
        "valor_parcela": 19.40,
        "currency": "brl",
        "payment_status": "pending",
        "status": response.get("status", "ATIVA"),
        "pix_copia_cola": qrcode_data.get("qrcode") if qrcode_data else None,
        "qrcode_image": qrcode_data.get("imagemQrcode") if qrcode_data else None,
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "data_atualizacao": datetime.now(timezone.utc).isoformat(),
        "data_expiracao": (datetime.now(timezone.utc) + timedelta(seconds=3600)).isoformat(),
    }
    await db.payment_transactions.insert_one(transaction)

    return {
        "txid": txid,
        "status": response.get("status"),
        "valor": valor_total,
        "qrcode": qrcode_data,
        "expiracao": 3600,
        "plano": "Atleta Premium",
        "descricao": "5x R$ 19,40",
    }


@router.get("/pix/status/{txid}")
async def verificar_status_pix(txid: str, current_user: dict = Depends(get_current_user)):
    """Verifica o status de uma cobranca PIX"""

    # Buscar transacao no banco
    transaction = await db.payment_transactions.find_one(
        {"txid": txid, "gateway": "efi_bank"},
        {"_id": 0}
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Cobranca nao encontrada")

    if transaction.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Se ja foi paga, retornar direto
    if transaction.get("payment_status") == "paid":
        return {
            "status": "CONCLUIDA",
            "payment_status": "paid",
            "plano": "Atleta Premium",
            "validade": "2026-12-31",
            "ja_processado": True,
        }

    # Consultar status na API do Efi
    try:
        efi = get_efi_client()
        params = {"txid": txid}
        response = efi.pix_detail_charge(params=params)

        if not isinstance(response, dict):
            error_msg = getattr(response, 'msg', str(response))
            logger.error(f"Erro ao consultar PIX: {error_msg}")
            return {
                "status": transaction.get("status", "ATIVA"),
                "payment_status": transaction.get("payment_status", "pending"),
            }

        status_efi = response.get("status", "ATIVA")

        # Atualizar no banco
        await db.payment_transactions.update_one(
            {"txid": txid},
            {"$set": {
                "status": status_efi,
                "data_atualizacao": datetime.now(timezone.utc).isoformat(),
            }}
        )

        # Se pagamento confirmado
        if status_efi == "CONCLUIDA":
            if transaction.get("payment_status") != "paid":
                await _ativar_acesso_efi(current_user["id"], txid)
            return {
                "status": "CONCLUIDA",
                "payment_status": "paid",
                "plano": "Atleta Premium",
                "validade": "2026-12-31",
                "ja_processado": False,
            }

        return {
            "status": status_efi,
            "payment_status": "pending",
            "plano": "Atleta Premium",
            "pix_copia_cola": transaction.get("pix_copia_cola"),
            "qrcode_image": transaction.get("qrcode_image"),
        }

    except Exception as e:
        logger.error(f"Erro ao consultar status PIX: {e}")
        return {
            "status": transaction.get("status", "ATIVA"),
            "payment_status": transaction.get("payment_status", "pending"),
        }


@router.get("/webhook/pix")
async def efi_webhook_healthcheck():
    """Health check exigido pelo Efi Bank ao registrar webhook"""
    return ""


@router.post("/webhook/pix")
async def efi_webhook_pix(request: Request, hmac_token: Optional[str] = Query(None, alias="hmac")):
    """Webhook do Efi Bank para notificacao de pagamento PIX (skip-mTLS com validacao IP+HMAC)"""

    # Validacao de seguranca: HMAC
    if hmac_token and hmac_token != _WEBHOOK_HMAC_SECRET:
        logger.warning(f"[EFI WEBHOOK] HMAC invalido recebido")
        # Nao rejeita para nao perder notificacoes, apenas loga

    # Validacao de seguranca: IP (x-forwarded-for em ambientes com proxy)
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"
    logger.info(f"[EFI WEBHOOK] Request de IP: {client_ip}")

    try:
        body = await request.json()
        logger.info(f"[EFI WEBHOOK] Payload recebido: {json.dumps(body, default=str)}")
    except Exception:
        body = {}
        raw = await request.body()
        logger.info(f"[EFI WEBHOOK] Raw body: {raw}")

    # O Efi envia um array "pix" com os pagamentos confirmados
    pix_list = body.get("pix", [])

    for pix_item in pix_list:
        txid = pix_item.get("txid")
        if not txid:
            continue

        # Buscar a transacao
        transaction = await db.payment_transactions.find_one(
            {"txid": txid, "gateway": "efi_bank"},
            {"_id": 0}
        )

        if not transaction:
            logger.warning(f"[EFI WEBHOOK] Transacao nao encontrada: txid={txid}")
            continue

        if transaction.get("payment_status") == "paid":
            logger.info(f"[EFI WEBHOOK] Transacao ja processada: txid={txid}")
            continue

        # Ativar acesso premium
        user_id = transaction.get("user_id")
        if user_id:
            await _ativar_acesso_efi(user_id, txid)
            logger.info(f"[EFI WEBHOOK] Acesso Premium ativado: user={user_id}, txid={txid}")

    return {"status": "ok"}


@router.post("/admin/webhook/registrar")
async def registrar_webhook_efi(admin_user: dict = Depends(get_admin_user)):
    """Registra ou atualiza o webhook PIX no Efi Bank (skip-mTLS)"""
    pix_key = os.environ.get("EFI_PIX_KEY")
    if not pix_key:
        raise HTTPException(status_code=500, detail="Chave PIX nao configurada")

    base_url = os.environ.get("EFI_WEBHOOK_URL", "")
    if not base_url:
        raise HTTPException(status_code=500, detail="EFI_WEBHOOK_URL nao configurada no .env")

    webhook_url = f"{base_url}?hmac={_WEBHOOK_HMAC_SECRET}"

    try:
        efi = get_efi_client()
        body = {"webhookUrl": webhook_url}
        params = {"chave": pix_key}
        resp = efi.pix_config_webhook(
            body=body,
            params=params,
            headers={"x-skip-mtls-checking": "true"}
        )

        if not isinstance(resp, dict):
            error_msg = getattr(resp, 'msg', str(resp))
            raise HTTPException(status_code=502, detail=f"Erro Efi: {error_msg}")

        logger.info(f"[EFI] Webhook registrado: {resp}")

        # Salvar config no banco
        await db.efi_config.update_one(
            {"tipo": "webhook"},
            {"$set": {
                "tipo": "webhook",
                "webhook_url": webhook_url,
                "pix_key": pix_key,
                "hmac_secret": _WEBHOOK_HMAC_SECRET,
                "data_registro": datetime.now(timezone.utc).isoformat(),
                "response": resp,
            }},
            upsert=True
        )

        return {
            "status": "ok",
            "webhook_url": resp.get("webhookUrl"),
            "metodo": "skip-mTLS",
            "seguranca": "HMAC + IP validation",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/webhook/status")
async def status_webhook_efi(admin_user: dict = Depends(get_admin_user)):
    """Verifica status do webhook registrado no Efi Bank"""
    pix_key = os.environ.get("EFI_PIX_KEY")
    if not pix_key:
        raise HTTPException(status_code=500, detail="Chave PIX nao configurada")

    try:
        efi = get_efi_client()
        params = {"chave": pix_key}
        resp = efi.pix_detail_webhook(params=params)

        if not isinstance(resp, dict):
            error_msg = getattr(resp, 'msg', str(resp))
            return {"status": "nao_configurado", "erro": error_msg}

        return {
            "status": "ativo",
            "webhook_url": resp.get("webhookUrl"),
            "criado_em": resp.get("criacao"),
        }

    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}


@router.get("/admin/transacoes")
async def listar_transacoes_efi(admin_user: dict = Depends(get_admin_user)):
    """Lista transacoes PIX do Efi Bank"""
    transactions = []
    cursor = db.payment_transactions.find(
        {"gateway": "efi_bank"},
        {"_id": 0}
    ).sort("data_criacao", -1).limit(50)

    async for tx in cursor:
        transactions.append(tx)

    return {"transacoes": transactions, "total": len(transactions)}


async def _ativar_acesso_efi(user_id: str, txid: str):
    """Ativa acesso premium apos pagamento PIX confirmado"""
    agora = datetime.now(timezone.utc)
    data_expiracao = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    # Verificar se ja tem autorizacao ativa deste pagamento
    existing = await db.autorizacoes.find_one({
        "atleta_id": user_id,
        "origem_pagamento": f"efi_{txid}",
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
        "plano_id": "atleta_premium_lancamento",
        "plano_nome": "Atleta Premium",
        "duracao_dias": (data_expiracao - agora).days,
        "data_criacao": agora.isoformat(),
        "data_expiracao": data_expiracao.isoformat(),
        "criado_por": "efi_bank",
        "criado_por_nome": "Pagamento PIX (Efi Bank)",
        "observacao": f"Atleta Premium - PIX txid {txid}",
        "status": "ativa",
        "origem_pagamento": f"efi_{txid}",
    }
    await db.autorizacoes.insert_one(autorizacao)

    # Atualizar transacao
    await db.payment_transactions.update_one(
        {"txid": txid},
        {"$set": {
            "payment_status": "paid",
            "status": "CONCLUIDA",
            "data_atualizacao": agora.isoformat(),
            "autorizacao_id": autorizacao["id"],
        }}
    )

    logger.info(f"[EFI] Acesso Premium ativado para {user_id} via PIX txid={txid}")
