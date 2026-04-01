# /app/backend/routes/whatsapp_routes.py
# Integração com WhatsApp Cloud API (Meta) para envio de mensagens e webhook

import os
import httpx
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter()

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "ranking_run_whatsapp_2026")
GRAPH_API_VERSION = "v21.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


# ==================== WEBHOOK VERIFICATION (Meta) ====================

@router.get("/whatsapp/webhook")
async def whatsapp_webhook_verify(
    request: Request,
):
    """
    Endpoint de verificação do webhook do Meta.
    O Meta envia um GET com hub.mode, hub.verify_token e hub.challenge.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)

    return PlainTextResponse(content="Forbidden", status_code=403)


@router.post("/whatsapp/webhook")
async def whatsapp_webhook_receive(request: Request):
    """
    Recebe notificações do WhatsApp (mensagens recebidas, status, etc.)
    """
    body = await request.json()
    # Log para debug - pode ser expandido futuramente
    print(f"[WhatsApp Webhook] Received: {body}")
    return {"status": "ok"}


# ==================== ENVIO DE MENSAGENS ====================

async def enviar_mensagem_whatsapp(telefone: str, mensagem: str) -> dict:
    """
    Envia uma mensagem de texto via WhatsApp Cloud API.
    
    Args:
        telefone: Número do destinatário com código do país (ex: 5511999998888)
        mensagem: Texto da mensagem
    
    Returns:
        dict com resultado da API
    """
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        raise HTTPException(
            status_code=500,
            detail="WhatsApp não configurado. Verifique WHATSAPP_TOKEN e WHATSAPP_PHONE_NUMBER_ID no .env"
        )

    url = f"{GRAPH_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": telefone,
        "type": "text",
        "text": {
            "body": mensagem
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code in (200, 201):
            return {"success": True, "data": response.json()}
        else:
            print(f"[WhatsApp] Erro ao enviar: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text, "status_code": response.status_code}


def formatar_telefone_brasil(telefone: str) -> str:
    """
    Formata telefone brasileiro para o padrão internacional (55...).
    Remove caracteres especiais e adiciona código do país se necessário.
    """
    # Remove tudo que não é dígito
    numeros = ''.join(c for c in telefone if c.isdigit())

    # Se já começa com 55 e tem 12-13 dígitos, está ok
    if numeros.startswith('55') and len(numeros) >= 12:
        return numeros

    # Se começa com 0, remove o 0
    if numeros.startswith('0'):
        numeros = numeros[1:]

    # Adiciona 55 (Brasil)
    if not numeros.startswith('55'):
        numeros = '55' + numeros

    return numeros
