# /app/backend/services/email_service.py
# Serviço de envio de emails usando Resend

import os
import asyncio
import logging
import resend
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Configuração
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
ALERT_EMAIL = os.environ.get('ALERT_EMAIL', 'suporte@rankingrun.com.br')

# Inicializar Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

logger = logging.getLogger(__name__)


def is_email_configured() -> bool:
    """Verifica se o serviço de email está configurado"""
    return bool(RESEND_API_KEY and RESEND_API_KEY != 're_your_api_key_here')


async def enviar_email(
    destinatario: str,
    assunto: str,
    html_content: str,
    texto_alternativo: str = None
) -> dict:
    """
    Envia um email usando Resend de forma assíncrona
    
    Args:
        destinatario: Email do destinatário
        assunto: Assunto do email
        html_content: Conteúdo HTML do email
        texto_alternativo: Texto alternativo (plain text)
    
    Returns:
        dict com status e detalhes do envio
    """
    if not is_email_configured():
        logger.warning("Resend API não configurada. Email não enviado.")
        return {
            "status": "skipped",
            "message": "Email service not configured (RESEND_API_KEY missing)",
            "destinatario": destinatario
        }
    
    params = {
        "from": SENDER_EMAIL,
        "to": [destinatario],
        "subject": assunto,
        "html": html_content
    }
    
    if texto_alternativo:
        params["text"] = texto_alternativo
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email enviado com sucesso para {destinatario}")
        return {
            "status": "success",
            "message": f"Email enviado para {destinatario}",
            "email_id": email.get("id") if isinstance(email, dict) else str(email)
        }
    except Exception as e:
        logger.error(f"Falha ao enviar email para {destinatario}: {str(e)}")
        return {
            "status": "error",
            "message": f"Falha ao enviar email: {str(e)}",
            "destinatario": destinatario
        }


# ==================== TEMPLATES DE EMAIL ====================

def gerar_email_codigo_2fa(codigo: str, admin_nome: str) -> dict:
    """Gera conteúdo do email com código 2FA"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto;">
        <tr>
            <td style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding-bottom: 20px; border-bottom: 2px solid #10B981;">
                            <h1 style="color: #10B981; margin: 0; font-size: 24px;">
                                🔐 Código de Verificação
                            </h1>
                        </td>
                    </tr>
                </table>
                
                <!-- Content -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="font-size: 16px; color: #333; margin: 0 0 10px 0;">
                                Olá <strong>{admin_nome}</strong>,
                            </p>
                            <p style="color: #666; margin: 0 0 20px 0;">
                                Use o código abaixo para completar seu login:
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center;">
                            <table cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                                <tr>
                                    <td style="background: #ECFDF5; border: 2px solid #10B981; border-radius: 10px; padding: 25px 40px;">
                                        <span style="font-size: 42px; font-weight: bold; color: #059669; letter-spacing: 8px; font-family: monospace;">
                                            {codigo}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <p style="color: #EF4444; font-size: 14px; margin: 0;">
                                ⏱️ Este código expira em <strong>10 minutos</strong>.
                            </p>
                            <p style="color: #666; font-size: 14px; margin: 15px 0 0 0;">
                                Se você não solicitou este código, ignore este email.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                Ranking Run - Sistema de Ranking de Corridas
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    texto = f"""
Código de Verificação - Ranking Run

Olá {admin_nome},

Use o código abaixo para completar seu login:

{codigo}

Este código expira em 10 minutos.

Se você não solicitou este código, ignore este email.

---
Ranking Run - Sistema de Ranking de Corridas
"""
    
    return {
        "assunto": "🔐 Código de Verificação - Ranking Run",
        "html": html,
        "texto": texto
    }


def gerar_email_alerta_emergencia(
    admin_nome: str,
    acao: str,
    ip: str,
    dispositivo: str,
    data_hora: str
) -> dict:
    """Gera conteúdo do email de alerta de segurança"""
    
    # Formatar data
    try:
        dt = datetime.fromisoformat(data_hora.replace("Z", "+00:00"))
        data_formatada = dt.strftime("%d/%m/%Y")
        hora_formatada = dt.strftime("%H:%M:%S")
    except:
        data_formatada = data_hora[:10]
        hora_formatada = data_hora[11:19] if len(data_hora) > 19 else ""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto;">
        <tr>
            <td style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding-bottom: 20px; border-bottom: 3px solid #EF4444;">
                            <h1 style="color: #EF4444; margin: 0; font-size: 24px;">
                                ⚠️ ALERTA DE SEGURANÇA
                            </h1>
                        </td>
                    </tr>
                </table>
                
                <!-- Alert Message -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                                A conta <strong style="color: #EF4444;">ADMIN DE EMERGÊNCIA</strong> foi utilizada no sistema Ranking Run.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Details Box -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; margin: 20px 0;">
                    <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #991B1B; margin: 0 0 15px 0; font-size: 16px;">
                                📋 Detalhes do Acesso:
                            </h3>
                            <table width="100%" cellpadding="8" cellspacing="0">
                                <tr style="border-bottom: 1px solid #FECACA;">
                                    <td style="color: #666; width: 120px;"><strong>Admin:</strong></td>
                                    <td style="color: #333;">{admin_nome}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #FECACA;">
                                    <td style="color: #666;"><strong>Ação:</strong></td>
                                    <td style="color: #333;">{acao}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #FECACA;">
                                    <td style="color: #666;"><strong>Data:</strong></td>
                                    <td style="color: #333;">{data_formatada}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #FECACA;">
                                    <td style="color: #666;"><strong>Hora:</strong></td>
                                    <td style="color: #333;">{hora_formatada}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #FECACA;">
                                    <td style="color: #666;"><strong>IP:</strong></td>
                                    <td style="color: #333; font-family: monospace;">{ip}</td>
                                </tr>
                                <tr>
                                    <td style="color: #666;"><strong>Dispositivo:</strong></td>
                                    <td style="color: #333;">{dispositivo}</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <!-- Warning -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding: 15px; background: #FFF7ED; border-radius: 8px; border: 1px solid #FDBA74;">
                            <p style="color: #9A3412; font-size: 14px; margin: 0;">
                                <strong>⚠️ Atenção:</strong> Se você não reconhece esta atividade, tome medidas imediatas para proteger o sistema.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                Este é um email automático do sistema Ranking Run.
                            </p>
                            <p style="color: #999; font-size: 12px; margin: 5px 0 0 0;">
                                Não responda a este email.
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    texto = f"""
⚠️ ALERTA DE SEGURANÇA - Ranking Run

A conta ADMIN DE EMERGÊNCIA foi utilizada.

Detalhes do Acesso:
- Admin: {admin_nome}
- Ação: {acao}
- Data: {data_formatada}
- Hora: {hora_formatada}
- IP: {ip}
- Dispositivo: {dispositivo}

Se você não reconhece esta atividade, tome medidas imediatas para proteger o sistema.

---
Este é um email automático do sistema Ranking Run.
"""
    
    return {
        "assunto": "⚠️ ALERTA DE SEGURANÇA - Admin de Emergência Utilizado",
        "html": html,
        "texto": texto
    }


def gerar_email_novo_admin(
    admin_nome: str,
    admin_email: str,
    role_nome: str,
    senha_temporaria: str = None
) -> dict:
    """Gera email de boas-vindas para novo administrador"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto;">
        <tr>
            <td style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding-bottom: 20px; border-bottom: 2px solid #10B981;">
                            <h1 style="color: #10B981; margin: 0; font-size: 24px;">
                                🎉 Bem-vindo ao Ranking Run!
                            </h1>
                        </td>
                    </tr>
                </table>
                
                <!-- Content -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                    <tr>
                        <td>
                            <p style="font-size: 16px; color: #333; margin: 0 0 15px 0;">
                                Olá <strong>{admin_nome}</strong>,
                            </p>
                            <p style="color: #666; margin: 0 0 20px 0;">
                                Sua conta de administrador foi criada com sucesso no sistema Ranking Run.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Credentials Box -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; margin: 20px 0;">
                    <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #166534; margin: 0 0 15px 0; font-size: 16px;">
                                🔑 Suas Credenciais:
                            </h3>
                            <table width="100%" cellpadding="8" cellspacing="0">
                                <tr style="border-bottom: 1px solid #BBF7D0;">
                                    <td style="color: #666; width: 100px;"><strong>Email:</strong></td>
                                    <td style="color: #333;">{admin_email}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #BBF7D0;">
                                    <td style="color: #666;"><strong>Função:</strong></td>
                                    <td style="color: #333;">{role_nome}</td>
                                </tr>
                                {f'<tr><td style="color: #666;"><strong>Senha:</strong></td><td style="color: #333; font-family: monospace;">{senha_temporaria}</td></tr>' if senha_temporaria else ''}
                            </table>
                        </td>
                    </tr>
                </table>
                
                <!-- Warning -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding: 15px; background: #FEF3C7; border-radius: 8px; border: 1px solid #FDE68A;">
                            <p style="color: #92400E; font-size: 14px; margin: 0;">
                                <strong>🔒 Importante:</strong> Recomendamos alterar sua senha no primeiro acesso.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                Ranking Run - Sistema de Ranking de Corridas
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    texto = f"""
🎉 Bem-vindo ao Ranking Run!

Olá {admin_nome},

Sua conta de administrador foi criada com sucesso.

Suas Credenciais:
- Email: {admin_email}
- Função: {role_nome}
{f'- Senha: {senha_temporaria}' if senha_temporaria else ''}

🔒 Importante: Recomendamos alterar sua senha no primeiro acesso.

---
Ranking Run - Sistema de Ranking de Corridas
"""
    
    return {
        "assunto": "🎉 Bem-vindo ao Ranking Run - Conta de Administrador Criada",
        "html": html,
        "texto": texto
    }


def gerar_email_admin_bloqueado(admin_nome: str, motivo: str = None) -> dict:
    """Gera email de notificação quando admin é bloqueado"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto;">
        <tr>
            <td style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding-bottom: 20px; border-bottom: 3px solid #EF4444;">
                            <h1 style="color: #EF4444; margin: 0; font-size: 24px;">
                                🔒 Conta Bloqueada
                            </h1>
                        </td>
                    </tr>
                </table>
                
                <!-- Content -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="font-size: 16px; color: #333; margin: 0 0 15px 0;">
                                Olá <strong>{admin_nome}</strong>,
                            </p>
                            <p style="color: #666; margin: 0 0 20px 0;">
                                Sua conta de administrador no sistema Ranking Run foi <strong style="color: #EF4444;">bloqueada</strong>.
                            </p>
                            {f'<p style="color: #666; margin: 0;"><strong>Motivo:</strong> {motivo}</p>' if motivo else ''}
                        </td>
                    </tr>
                </table>
                
                <!-- Contact Info -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px;">
                    <tr>
                        <td style="text-align: center; padding: 15px; background: #F3F4F6; border-radius: 8px;">
                            <p style="color: #4B5563; font-size: 14px; margin: 0;">
                                Se você acredita que isso foi um erro, entre em contato com o Super Administrador.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                Ranking Run - Sistema de Ranking de Corridas
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    texto = f"""
🔒 Conta Bloqueada - Ranking Run

Olá {admin_nome},

Sua conta de administrador no sistema Ranking Run foi bloqueada.
{f'Motivo: {motivo}' if motivo else ''}

Se você acredita que isso foi um erro, entre em contato com o Super Administrador.

---
Ranking Run - Sistema de Ranking de Corridas
"""
    
    return {
        "assunto": "🔒 Conta Bloqueada - Ranking Run",
        "html": html,
        "texto": texto
    }


# ==================== FUNÇÕES DE ENVIO ESPECÍFICAS ====================

async def enviar_codigo_2fa(email: str, codigo: str, admin_nome: str) -> dict:
    """Envia código 2FA por email"""
    template = gerar_email_codigo_2fa(codigo, admin_nome)
    return await enviar_email(
        destinatario=email,
        assunto=template["assunto"],
        html_content=template["html"],
        texto_alternativo=template["texto"]
    )


async def enviar_alerta_emergencia(
    admin_nome: str,
    acao: str,
    ip: str,
    dispositivo: str,
    data_hora: str
) -> dict:
    """Envia alerta de segurança quando Admin de Emergência é usado"""
    template = gerar_email_alerta_emergencia(admin_nome, acao, ip, dispositivo, data_hora)
    return await enviar_email(
        destinatario=ALERT_EMAIL,
        assunto=template["assunto"],
        html_content=template["html"],
        texto_alternativo=template["texto"]
    )


async def enviar_boas_vindas_admin(
    admin_nome: str,
    admin_email: str,
    role_nome: str,
    senha: str = None
) -> dict:
    """Envia email de boas-vindas para novo administrador"""
    template = gerar_email_novo_admin(admin_nome, admin_email, role_nome, senha)
    return await enviar_email(
        destinatario=admin_email,
        assunto=template["assunto"],
        html_content=template["html"],
        texto_alternativo=template["texto"]
    )


async def enviar_notificacao_bloqueio(
    admin_nome: str,
    admin_email: str,
    motivo: str = None
) -> dict:
    """Envia notificação quando admin é bloqueado"""
    template = gerar_email_admin_bloqueado(admin_nome, motivo)
    return await enviar_email(
        destinatario=admin_email,
        assunto=template["assunto"],
        html_content=template["html"],
        texto_alternativo=template["texto"]
    )


# ==================== NOTIFICAÇÕES PARA ATLETAS ====================

def gerar_email_resultado_aprovado(
    atleta_nome: str,
    nome_corrida: str,
    colocacao: int,
    pontos: int,
    data_corrida: str,
    distancia: str
) -> dict:
    """Gera email de notificação quando resultado é aprovado"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto;">
        <tr>
            <td style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding-bottom: 20px; border-bottom: 2px solid #10B981;">
                            <h1 style="color: #10B981; margin: 0; font-size: 28px;">
                                Resultado Aprovado!
                            </h1>
                        </td>
                    </tr>
                </table>
                
                <!-- Content -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                    <tr>
                        <td>
                            <p style="font-size: 16px; color: #333; margin: 0 0 15px 0;">
                                Ola <strong>{atleta_nome}</strong>,
                            </p>
                            <p style="color: #666; margin: 0 0 20px 0;">
                                Parabens! Seu resultado foi aprovado e ja esta valendo no ranking!
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Result Box -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); border-radius: 12px; margin: 20px 0;">
                    <tr>
                        <td style="padding: 25px; text-align: center;">
                            <h2 style="color: white; margin: 0 0 5px 0; font-size: 20px;">{nome_corrida}</h2>
                            <p style="color: rgba(255,255,255,0.8); margin: 0 0 15px 0; font-size: 14px;">{data_corrida} | {distancia}</p>
                            
                            <table width="100%" cellpadding="10" cellspacing="0">
                                <tr>
                                    <td style="text-align: center; width: 50%;">
                                        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 12px;">COLOCACAO</p>
                                        <p style="color: white; margin: 5px 0 0 0; font-size: 36px; font-weight: bold;">{colocacao}</p>
                                    </td>
                                    <td style="text-align: center; width: 50%;">
                                        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 12px;">PONTOS GANHOS</p>
                                        <p style="color: #FFD700; margin: 5px 0 0 0; font-size: 36px; font-weight: bold;">+{pontos}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px; border-top: 1px solid #eee; padding-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                Continue participando e subindo no ranking!
                            </p>
                            <p style="color: #999; font-size: 12px; margin: 10px 0 0 0;">
                                Ranking Run Pro - O seu ranking de corridas
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    texto = f"""
Resultado Aprovado! - Ranking Run

Ola {atleta_nome},

Parabens! Seu resultado foi aprovado e ja esta valendo no ranking!

{nome_corrida}
{data_corrida} | {distancia}

Colocacao: {colocacao} lugar
Pontos ganhos: +{pontos}

Continue participando e subindo no ranking!

---
Ranking Run Pro - O seu ranking de corridas
"""
    
    return {
        "assunto": f"+{pontos} pontos! Seu resultado em {nome_corrida} foi aprovado",
        "html": html,
        "texto": texto
    }


def gerar_email_resultado_rejeitado(
    atleta_nome: str,
    nome_corrida: str,
    motivo: str,
    data_corrida: str
) -> dict:
    """Gera email de notificacao quando resultado e rejeitado"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto;">
        <tr>
            <td style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding-bottom: 20px; border-bottom: 2px solid #F59E0B;">
                            <h1 style="color: #F59E0B; margin: 0; font-size: 24px;">
                                Resultado Nao Aprovado
                            </h1>
                        </td>
                    </tr>
                </table>
                
                <!-- Content -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                    <tr>
                        <td>
                            <p style="font-size: 16px; color: #333; margin: 0 0 15px 0;">
                                Ola <strong>{atleta_nome}</strong>,
                            </p>
                            <p style="color: #666; margin: 0 0 20px 0;">
                                Infelizmente seu resultado nao foi aprovado. Mas nao desanime, voce pode enviar novamente!
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Details Box -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background: #FEF3C7; border: 1px solid #FDE68A; border-radius: 8px; margin: 20px 0;">
                    <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #92400E; margin: 0 0 10px 0; font-size: 16px;">
                                Detalhes:
                            </h3>
                            <p style="color: #78350F; margin: 0 0 10px 0;">
                                <strong>Corrida:</strong> {nome_corrida}
                            </p>
                            <p style="color: #78350F; margin: 0 0 10px 0;">
                                <strong>Data:</strong> {data_corrida}
                            </p>
                            <p style="color: #78350F; margin: 0;">
                                <strong>Motivo:</strong> {motivo}
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Tips -->
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="padding: 15px; background: #F0FDF4; border-radius: 8px; border: 1px solid #BBF7D0;">
                            <h4 style="color: #166534; margin: 0 0 10px 0;">Dicas para aprovacao:</h4>
                            <ul style="color: #166534; margin: 0; padding-left: 20px; font-size: 14px;">
                                <li>Envie fotos legiveis da classificacao</li>
                                <li>Verifique se os dados estao corretos</li>
                                <li>Envie dentro do prazo de 30 dias</li>
                            </ul>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer -->
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px; border-top: 1px solid #eee; padding-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                Ranking Run Pro - O seu ranking de corridas
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    texto = f"""
Resultado Nao Aprovado - Ranking Run

Ola {atleta_nome},

Infelizmente seu resultado nao foi aprovado.

Corrida: {nome_corrida}
Data: {data_corrida}
Motivo: {motivo}

Dicas para aprovacao:
- Envie fotos legiveis da classificacao
- Verifique se os dados estao corretos
- Envie dentro do prazo de 30 dias

Voce pode enviar novamente!

---
Ranking Run Pro - O seu ranking de corridas
"""
    
    return {
        "assunto": f"Resultado em {nome_corrida} nao foi aprovado",
        "html": html,
        "texto": texto
    }


async def notificar_resultado_aprovado(
    email: str,
    atleta_nome: str,
    nome_corrida: str,
    colocacao: int,
    pontos: int,
    data_corrida: str,
    distancia: str
) -> dict:
    """Envia notificacao quando resultado e aprovado"""
    template = gerar_email_resultado_aprovado(
        atleta_nome, nome_corrida, colocacao, pontos, data_corrida, distancia
    )
    return await enviar_email(
        destinatario=email,
        assunto=template["assunto"],
        html_content=template["html"],
        texto_alternativo=template["texto"]
    )


async def notificar_resultado_rejeitado(
    email: str,
    atleta_nome: str,
    nome_corrida: str,
    motivo: str,
    data_corrida: str
) -> dict:
    """Envia notificacao quando resultado e rejeitado"""
    template = gerar_email_resultado_rejeitado(
        atleta_nome, nome_corrida, motivo, data_corrida
    )
    return await enviar_email(
        destinatario=email,
        assunto=template["assunto"],
        html_content=template["html"],
        texto_alternativo=template["texto"]
    )
