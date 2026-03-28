# /app/backend/services/relatorio_semanal.py
"""
Servico de Relatorio Semanal Automatico
Envia por e-mail (Resend) um resumo para os admins todo domingo as 20h
"""

import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta

import resend
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


def _get_db():
    from config import db
    return db


async def _coletar_dados_semana():
    """Coleta KPIs da ultima semana"""
    db = _get_db()
    agora = datetime.now(timezone.utc)
    inicio_semana = (agora - timedelta(days=7)).isoformat()

    # Novos atletas na semana
    novos_atletas = await db.usuarios.count_documents({
        "role": "atleta",
        "data_criacao": {"$gte": inicio_semana}
    })

    total_atletas = await db.usuarios.count_documents({"role": "atleta"})

    # Transacoes pagas na semana
    txs_semana = []
    cursor = db.payment_transactions.find({
        "payment_status": "paid",
        "data_criacao": {"$gte": inicio_semana}
    }, {"_id": 0})
    async for tx in cursor:
        txs_semana.append(tx)

    receita_semana = sum(t.get("amount", 0) for t in txs_semana)
    count_pix = len([t for t in txs_semana if t.get("tipo") == "pix"])
    count_cartao = len([t for t in txs_semana if t.get("tipo") == "cartao"])

    # Receita total historica
    all_pagas = []
    cursor2 = db.payment_transactions.find({"payment_status": "paid"}, {"_id": 0, "amount": 1})
    async for tx in cursor2:
        all_pagas.append(tx)
    receita_total = sum(t.get("amount", 0) for t in all_pagas)

    # Novas corridas na semana
    novas_corridas = await db.corridas.count_documents({
        "data_criacao": {"$gte": inicio_semana}
    })

    return {
        "periodo_inicio": (agora - timedelta(days=7)).strftime("%d/%m/%Y"),
        "periodo_fim": agora.strftime("%d/%m/%Y"),
        "novos_atletas": novos_atletas,
        "total_atletas": total_atletas,
        "receita_semana": round(receita_semana, 2),
        "receita_total": round(receita_total, 2),
        "total_pagamentos_semana": len(txs_semana),
        "pagamentos_pix": count_pix,
        "pagamentos_cartao": count_cartao,
        "novas_corridas": novas_corridas,
    }


def _gerar_html_relatorio(dados: dict) -> str:
    """Gera HTML do relatorio semanal"""
    return f"""<!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; padding: 20px; color: #e2e8f0;">
  <div style="max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 16px; overflow: hidden; border: 1px solid #334155;">
    <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); padding: 32px; text-align: center;">
      <h1 style="color: white; margin: 0; font-size: 24px;">Relatorio Semanal</h1>
      <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0 0; font-size: 14px;">{dados['periodo_inicio']} a {dados['periodo_fim']}</p>
    </div>
    <div style="padding: 32px;">
      <h2 style="color: #10b981; font-size: 18px; margin: 0 0 20px 0; border-bottom: 1px solid #334155; padding-bottom: 12px;">Receita</h2>
      <table style="width: 100%; border-collapse: collapse;">
        <tr>
          <td style="padding: 8px 0; color: #94a3b8; font-size: 14px;">Receita da Semana</td>
          <td style="padding: 8px 0; color: #10b981; font-size: 18px; font-weight: bold; text-align: right;">R$ {dados['receita_semana']:.2f}</td>
        </tr>
        <tr>
          <td style="padding: 8px 0; color: #94a3b8; font-size: 14px;">Receita Total Acumulada</td>
          <td style="padding: 8px 0; color: #e2e8f0; font-size: 16px; text-align: right;">R$ {dados['receita_total']:.2f}</td>
        </tr>
        <tr>
          <td style="padding: 8px 0; color: #94a3b8; font-size: 14px;">Pagamentos na Semana</td>
          <td style="padding: 8px 0; color: #e2e8f0; text-align: right;">{dados['total_pagamentos_semana']} ({dados['pagamentos_pix']} PIX, {dados['pagamentos_cartao']} Cartao)</td>
        </tr>
      </table>

      <h2 style="color: #3b82f6; font-size: 18px; margin: 24px 0 16px 0; border-bottom: 1px solid #334155; padding-bottom: 12px;">Atletas</h2>
      <table style="width: 100%; border-collapse: collapse;">
        <tr>
          <td style="padding: 8px 0; color: #94a3b8; font-size: 14px;">Novos Cadastros</td>
          <td style="padding: 8px 0; color: #3b82f6; font-size: 18px; font-weight: bold; text-align: right;">+{dados['novos_atletas']}</td>
        </tr>
        <tr>
          <td style="padding: 8px 0; color: #94a3b8; font-size: 14px;">Total de Atletas</td>
          <td style="padding: 8px 0; color: #e2e8f0; text-align: right;">{dados['total_atletas']}</td>
        </tr>
      </table>

      <h2 style="color: #f59e0b; font-size: 18px; margin: 24px 0 16px 0; border-bottom: 1px solid #334155; padding-bottom: 12px;">Atividade</h2>
      <table style="width: 100%; border-collapse: collapse;">
        <tr>
          <td style="padding: 8px 0; color: #94a3b8; font-size: 14px;">Novas Corridas Registradas</td>
          <td style="padding: 8px 0; color: #f59e0b; font-size: 18px; font-weight: bold; text-align: right;">{dados['novas_corridas']}</td>
        </tr>
      </table>
    </div>
    <div style="background: #0f172a; padding: 20px; text-align: center; border-top: 1px solid #334155;">
      <p style="color: #64748b; font-size: 12px; margin: 0;">Ranking Run Pro - Relatorio automatico semanal</p>
    </div>
  </div>
</body>
</html>"""


async def enviar_relatorio_semanal():
    """Coleta dados e envia relatorio semanal para todos os super admins"""
    logger.info("Iniciando envio do relatorio semanal...")

    api_key = os.environ.get("RESEND_API_KEY")
    sender = os.environ.get("SENDER_EMAIL", "noreply@rankingrun.com.br")

    if not api_key:
        logger.warning("RESEND_API_KEY nao configurada, relatorio nao enviado")
        return

    resend.api_key = api_key

    try:
        dados = await _coletar_dados_semana()
        html = _gerar_html_relatorio(dados)

        db = _get_db()
        admins = []
        # Buscar na collection administradores (tipo_admin: Super Admin)
        cursor = db.administradores.find({}, {"_id": 0, "email": 1, "nome": 1})
        async for admin in cursor:
            if admin.get("email"):
                admins.append(admin)

        # Fallback: buscar na collection usuarios com role=admin
        if not admins:
            cursor2 = db.usuarios.find({"role": "admin"}, {"_id": 0, "email": 1, "nome": 1})
            async for u in cursor2:
                if u.get("email"):
                    admins.append(u)

        if not admins:
            logger.warning("Nenhum super admin encontrado para enviar relatorio")
            return

        assunto = f"Relatorio Semanal - {dados['periodo_inicio']} a {dados['periodo_fim']}"

        enviados = 0
        for admin in admins:
            try:
                result = await asyncio.to_thread(resend.Emails.send, {
                    "from": f"Ranking Run Pro <{sender}>",
                    "to": [admin["email"]],
                    "subject": assunto,
                    "html": html,
                })
                enviados += 1
                logger.info(f"Relatorio enviado para {admin['email']}: {result}")
            except Exception as e:
                logger.error(f"Erro ao enviar relatorio para {admin['email']}: {e}")

        # Registrar no banco
        await db.logs_scheduler.insert_one({
            "tipo": "relatorio_semanal",
            "data": datetime.now(timezone.utc).isoformat(),
            "dados": dados,
            "admins_enviados": enviados,
            "total_admins": len(admins),
        })

        logger.info(f"Relatorio semanal enviado para {enviados}/{len(admins)} admins")

    except Exception as e:
        logger.error(f"Erro ao gerar/enviar relatorio semanal: {e}")
