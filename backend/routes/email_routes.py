# /app/backend/routes/email_routes.py
# Servico de envio de emails via Resend

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
import asyncio
import logging
import resend

from config import db
from routes.auth_routes import get_current_user, get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["email"])

# Configurar Resend
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


class EmailNotificacao(BaseModel):
    destinatario: str
    assunto: str
    html: str


async def enviar_email(destinatario: str, assunto: str, html: str) -> dict:
    """Envia email via Resend de forma non-blocking"""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY nao configurada, email nao enviado")
        return {"status": "skipped", "reason": "api_key_missing"}

    params = {
        "from": SENDER_EMAIL,
        "to": [destinatario],
        "subject": assunto,
        "html": html
    }

    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email enviado para {destinatario}: {result}")
        return {"status": "success", "email_id": result.get("id")}
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Erro ao enviar email para {destinatario}: {error_msg}")
        return {"status": "error", "detail": error_msg}


async def enviar_email_mensagem_admin(atletas: list, titulo: str, mensagem: str, link: str = None):
    """Envia emails em lote para atletas sobre mensagem do admin"""
    if not RESEND_API_KEY:
        return {"enviados": 0, "reason": "api_key_missing"}

    html = _montar_html_mensagem(titulo, mensagem, link)
    assunto = f"Ranking Run Pro - {titulo}" if titulo else "Ranking Run Pro - Nova Mensagem"

    enviados = 0
    erros = 0

    for atleta in atletas:
        email = atleta.get("email")
        if not email:
            continue
        try:
            result = await enviar_email(email, assunto, html)
            if result.get("status") == "success":
                enviados += 1
            else:
                erros += 1
        except Exception:
            erros += 1

    logger.info(f"Email em lote: {enviados} enviados, {erros} erros de {len(atletas)} atletas")
    return {"enviados": enviados, "erros": erros, "total": len(atletas)}


def _montar_html_mensagem(titulo: str, mensagem: str, link: str = None) -> str:
    """Monta HTML inline do email"""
    link_html = ""
    if link:
        link_html = f"""
        <tr>
          <td style="padding: 16px 24px;">
            <a href="{link}" style="display:inline-block;background:#059669;color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;">
              Acessar Link
            </a>
          </td>
        </tr>
        """

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:24px 0;">
      <tr>
        <td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <tr>
              <td style="background:#059669;padding:20px 24px;">
                <h1 style="color:#fff;margin:0;font-size:20px;font-family:Arial,sans-serif;">Ranking Run Pro</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:24px;">
                <h2 style="color:#1e293b;margin:0 0 12px;font-size:18px;font-family:Arial,sans-serif;">{titulo}</h2>
                <p style="color:#475569;font-size:14px;line-height:1.6;font-family:Arial,sans-serif;margin:0;white-space:pre-wrap;">{mensagem}</p>
              </td>
            </tr>
            {link_html}
            <tr>
              <td style="padding:16px 24px;border-top:1px solid #e2e8f0;">
                <p style="color:#94a3b8;font-size:12px;font-family:Arial,sans-serif;margin:0;">
                  Este email foi enviado pela administracao do Ranking Run Pro.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """


@router.post("/enviar")
async def enviar_email_endpoint(dados: EmailNotificacao, admin: dict = Depends(get_admin_user)):
    """Endpoint para admin enviar email individual"""
    result = await enviar_email(dados.destinatario, dados.assunto, dados.html)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("detail"))
    return result


@router.post("/teste")
async def enviar_email_teste(admin: dict = Depends(get_admin_user)):
    """Envia email de teste para o admin"""
    html = _montar_html_mensagem(
        "Email de Teste",
        "Se voce recebeu este email, a integracao com o Resend esta funcionando corretamente!",
        None
    )
    result = await enviar_email(admin.get("email", ""), "Ranking Run Pro - Teste de Email", html)
    return result
