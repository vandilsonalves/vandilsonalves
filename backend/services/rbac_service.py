# /app/backend/services/rbac_service.py
# Serviços para o Sistema RBAC

from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid
import random
import string
from user_agents import parse as parse_user_agent


def gerar_codigo_2fa() -> str:
    """Gera código de 6 dígitos para 2FA"""
    return ''.join(random.choices(string.digits, k=6))


def extrair_info_dispositivo(user_agent: str) -> dict:
    """Extrai informações do dispositivo a partir do User-Agent"""
    try:
        ua = parse_user_agent(user_agent)
        return {
            "navegador": f"{ua.browser.family} {ua.browser.version_string}",
            "sistema_operacional": f"{ua.os.family} {ua.os.version_string}",
            "dispositivo": ua.device.family if ua.device.family != "Other" else "Desktop",
            "is_mobile": ua.is_mobile,
            "is_tablet": ua.is_tablet,
            "is_pc": ua.is_pc,
            "descricao_completa": f"{ua.browser.family} / {ua.os.family}"
        }
    except:
        return {
            "navegador": "Desconhecido",
            "sistema_operacional": "Desconhecido",
            "dispositivo": "Desconhecido",
            "is_mobile": False,
            "is_tablet": False,
            "is_pc": True,
            "descricao_completa": user_agent[:100] if user_agent else "Desconhecido"
        }


async def get_localizacao_aproximada(ip: str) -> str:
    """Obtém localização aproximada baseada no IP"""
    # Implementação simplificada - em produção usar serviço de geolocalização
    if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10.") or ip == "localhost":
        return "Rede Local"
    
    # Para produção: usar api como ip-api.com ou similar
    return "Brasil"


def formatar_data_hora_br(iso_string: str) -> str:
    """Formata data ISO para formato brasileiro"""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y às %H:%M")
    except:
        return iso_string


def verificar_permissao(permissoes_usuario: list, permissao_necessaria: str) -> bool:
    """Verifica se o usuário tem uma permissão específica"""
    return permissao_necessaria in permissoes_usuario


def criar_log_acao(
    admin_id: str,
    admin_nome: str,
    admin_role: str,
    tipo_acao: str,
    descricao: str,
    ip_address: str,
    user_agent: str = "",
    entidade_tipo: str = None,
    entidade_id: str = None,
    entidade_nome: str = None,
    dados_extras: dict = None
) -> dict:
    """Cria um registro de log de ação administrativa"""
    info_dispositivo = extrair_info_dispositivo(user_agent)
    
    return {
        "id": str(uuid.uuid4()),
        "admin_id": admin_id,
        "admin_nome": admin_nome,
        "admin_role": admin_role,
        "tipo_acao": tipo_acao,
        "descricao": descricao,
        "entidade_tipo": entidade_tipo,
        "entidade_id": entidade_id,
        "entidade_nome": entidade_nome,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "dispositivo": info_dispositivo["descricao_completa"],
        "localizacao_aproximada": "Brasil",  # Simplificado
        "data_hora": datetime.now(timezone.utc).isoformat(),
        "dados_extras": dados_extras or {}
    }


def criar_alerta_seguranca(
    tipo: str,
    titulo: str,
    descricao: str,
    ip_address: str,
    admin_id: str = None,
    admin_nome: str = None,
    dispositivo: str = ""
) -> dict:
    """Cria um alerta de segurança"""
    return {
        "id": str(uuid.uuid4()),
        "tipo": tipo,
        "titulo": titulo,
        "descricao": descricao,
        "admin_id": admin_id,
        "admin_nome": admin_nome,
        "ip_address": ip_address,
        "dispositivo": dispositivo,
        "data_hora": datetime.now(timezone.utc).isoformat(),
        "email_enviado": False,
        "email_enviado_para": "",
        "email_enviado_em": None,
        "resolvido": False,
        "resolvido_por": None,
        "resolvido_em": None
    }


def gerar_email_alerta_emergencia(
    admin_nome: str,
    acao: str,
    ip: str,
    dispositivo: str,
    data_hora: str
) -> dict:
    """Gera conteúdo do email de alerta de segurança"""
    return {
        "assunto": "⚠️ ALERTA DE SEGURANÇA - Admin de Emergência Utilizado",
        "corpo_html": f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #EF4444; border-bottom: 2px solid #EF4444; padding-bottom: 10px;">
                    ⚠️ ALERTA DE SEGURANÇA
                </h1>
                
                <p style="font-size: 16px; color: #333;">
                    A conta <strong>ADMIN DE EMERGÊNCIA</strong> foi utilizada no sistema Ranking Run.
                </p>
                
                <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #991B1B; margin-top: 0;">Detalhes do Acesso:</h3>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        <li style="padding: 8px 0; border-bottom: 1px solid #FECACA;">
                            <strong>Admin:</strong> {admin_nome}
                        </li>
                        <li style="padding: 8px 0; border-bottom: 1px solid #FECACA;">
                            <strong>Ação:</strong> {acao}
                        </li>
                        <li style="padding: 8px 0; border-bottom: 1px solid #FECACA;">
                            <strong>Data/Hora:</strong> {data_hora}
                        </li>
                        <li style="padding: 8px 0; border-bottom: 1px solid #FECACA;">
                            <strong>IP:</strong> {ip}
                        </li>
                        <li style="padding: 8px 0;">
                            <strong>Dispositivo:</strong> {dispositivo}
                        </li>
                    </ul>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    Se você não reconhece esta atividade, tome medidas imediatas para proteger o sistema.
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    Este é um email automático do sistema Ranking Run.
                </p>
            </div>
        </body>
        </html>
        """,
        "corpo_texto": f"""
ALERTA DE SEGURANÇA - Ranking Run

A conta ADMIN DE EMERGÊNCIA foi utilizada.

Detalhes:
- Admin: {admin_nome}
- Ação: {acao}
- Data/Hora: {data_hora}
- IP: {ip}
- Dispositivo: {dispositivo}

Se você não reconhece esta atividade, tome medidas imediatas.
        """
    }


def gerar_email_codigo_2fa(codigo: str, admin_nome: str) -> dict:
    """Gera conteúdo do email com código 2FA"""
    return {
        "assunto": "🔐 Código de Verificação - Ranking Run",
        "corpo_html": f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #10B981; text-align: center;">
                    🔐 Código de Verificação
                </h1>
                
                <p style="font-size: 16px; color: #333; text-align: center;">
                    Olá <strong>{admin_nome}</strong>,
                </p>
                
                <p style="text-align: center; color: #666;">
                    Use o código abaixo para completar seu login:
                </p>
                
                <div style="background: #ECFDF5; border: 2px solid #10B981; border-radius: 10px; padding: 30px; margin: 20px 0; text-align: center;">
                    <span style="font-size: 48px; font-weight: bold; color: #059669; letter-spacing: 10px;">
                        {codigo}
                    </span>
                </div>
                
                <p style="color: #EF4444; text-align: center; font-size: 14px;">
                    ⏱️ Este código expira em <strong>10 minutos</strong>.
                </p>
                
                <p style="color: #666; font-size: 14px; text-align: center;">
                    Se você não solicitou este código, ignore este email.
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    Ranking Run - Sistema de Ranking de Corridas
                </p>
            </div>
        </body>
        </html>
        """,
        "corpo_texto": f"""
Código de Verificação - Ranking Run

Olá {admin_nome},

Use o código abaixo para completar seu login:

{codigo}

Este código expira em 10 minutos.

Se você não solicitou este código, ignore este email.
        """
    }
