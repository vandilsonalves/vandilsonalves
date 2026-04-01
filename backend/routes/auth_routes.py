# /app/backend/routes/auth_routes.py
# Módulo de Autenticação - Rotas de login, registro e perfil

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from typing import Optional
import uuid

from config import db, security
from models import Usuario, UsuarioRegister, UsuarioLogin
from services import (
    verify_password, get_password_hash, create_access_token,
    calcular_faixa_etaria, gerar_foto_url, SECRET_KEY, ALGORITHM
)

# Security scheme that doesn't auto-error (allows query param fallback)
security_optional = HTTPBearer(auto_error=False)

# Função auxiliar para registrar indicação
async def registrar_indicacao_interna(indicado_id: str, indicado_nome: str, codigo_indicacao: str):
    """Registra uma indicação quando um novo usuário se cadastra com código"""
    if not codigo_indicacao:
        return None
    
    # Buscar indicador pelo código
    indicador = await db.usuarios.find_one(
        {"codigo_indicacao": codigo_indicacao.upper()},
        {"_id": 0, "id": 1, "nome": 1}
    )
    
    if not indicador:
        return None
    
    # Não permitir auto-indicação
    if indicador["id"] == indicado_id:
        return None
    
    # Verificar se já existe essa indicação
    existente = await db.indicacoes.find_one({
        "indicador_id": indicador["id"],
        "indicado_id": indicado_id
    })
    
    if existente:
        return None
    
    # Registrar indicação
    await db.indicacoes.insert_one({
        "id": str(uuid.uuid4()),
        "indicador_id": indicador["id"],
        "indicado_id": indicado_id,
        "codigo_usado": codigo_indicacao.upper(),
        "data_indicacao": datetime.now(timezone.utc).isoformat(),
        "status": "confirmada"
    })
    
    # Atualizar contador no indicador
    await db.usuarios.update_one(
        {"id": indicador["id"]},
        {"$inc": {"total_indicacoes": 1}}
    )
    
    # Contar total de indicações para verificar badge
    total_indicacoes = await db.indicacoes.count_documents({
        "indicador_id": indicador["id"],
        "status": "confirmada"
    })
    
    # Criar notificação push para o indicador
    from models import Notificacao
    notificacao = Notificacao(
        usuario_id=indicador["id"],
        tipo="indicacao",
        titulo="🎉 Nova indicação!",
        mensagem=f"{indicado_nome} se cadastrou usando seu código de indicação!",
        dados_extras={
            "indicado_id": indicado_id,
            "indicado_nome": indicado_nome,
            "total_indicacoes": total_indicacoes
        }
    )
    await db.notificacoes.insert_one(notificacao.model_dump())
    
    # Verificar e conceder insígnias por indicação
    # Níveis: Embaixador Run (5), Bronze (10), Prata (20), Ouro (30), Diamante (50)
    niveis_insignias = [
        {"id": "embaixador_run", "nome": "Embaixador Run", "minimo": 5, "emoji": "🏃"},
        {"id": "indicador_bronze", "nome": "Indicador Bronze", "minimo": 10, "emoji": "🥉"},
        {"id": "indicador_prata", "nome": "Indicador Prata", "minimo": 20, "emoji": "🥈"},
        {"id": "indicador_ouro", "nome": "Indicador Ouro", "minimo": 30, "emoji": "🥇"},
        {"id": "indicador_diamante", "nome": "Indicador Diamante", "minimo": 50, "emoji": "💎"},
    ]
    
    for nivel in niveis_insignias:
        if total_indicacoes >= nivel["minimo"]:
            # Verificar se já tem a insígnia
            badge_existente = await db.badges_atleta.find_one({
                "atleta_id": indicador["id"],
                "badge_id": nivel["id"]
            })
            
            if not badge_existente:
                # Conceder insígnia
                await db.badges_atleta.insert_one({
                    "atleta_id": indicador["id"],
                    "badge_id": nivel["id"],
                    "data_conquista": datetime.now(timezone.utc).isoformat()
                })
                
                # Notificação de conquista de badge
                notificacao_badge = Notificacao(
                    usuario_id=indicador["id"],
                    tipo="badge",
                    titulo=f"{nivel['emoji']} Nova Insígnia Desbloqueada!",
                    mensagem=f"Parabéns! Você conquistou a insígnia '{nivel['nome']}' por indicar {nivel['minimo']} amigos!",
                    dados_extras={
                        "badge_id": nivel["id"],
                        "badge_nome": nivel["nome"],
                        "total_indicacoes": total_indicacoes
                    }
                )
                await db.notificacoes.insert_one(notificacao_badge.model_dump())
    
    return indicador["nome"]

router = APIRouter(tags=["Autenticação"])


# ==================== AUTH HELPERS ====================

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
):
    """Verifica token JWT via Header OU Query Param (?token=...) e retorna usuário atual"""
    token = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.query_params.get("token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = await db.usuarios.find_one({"id": user_id}, {"_id": 0})
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user


async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Verifica se o usuário é administrador (admin ou super_admin)"""
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")
    return current_user


async def require_premium_access(current_user: dict = Depends(get_current_user)):
    """Bloqueia usuarios expirados. Permite admin, em_teste e autorizado."""
    if current_user.get("role") in ["admin", "super_admin"]:
        return current_user

    agora = datetime.now(timezone.utc)

    # Verificar autorizacao ativa
    auth = await db.autorizacoes.find_one({
        "atleta_id": current_user["id"],
        "status": "ativa"
    }, {"_id": 0})

    if auth:
        try:
            exp_str = auth["data_expiracao"].replace("Z", "+00:00")
            if "+" not in exp_str and "T" in exp_str:
                exp_str = exp_str + "+00:00"
            data_exp = datetime.fromisoformat(exp_str)
            if data_exp.tzinfo is None:
                data_exp = data_exp.replace(tzinfo=timezone.utc)
            if data_exp > agora:
                return current_user
        except Exception:
            pass

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

    if (agora - data_criacao).days <= 30:
        return current_user

    raise HTTPException(
        status_code=403,
        detail="Acesso expirado. Assine o plano Atleta Premium para continuar."
    )


# ==================== AUTH ENDPOINTS ====================

@router.post("/auth/register")
async def register_atleta(dados: UsuarioRegister):
    """Cadastro de novo atleta"""
    existing = await db.usuarios.find_one({"email": dados.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Validar: PCD e Cadeirante não podem participar do Povão
    if dados.modalidade_usuario == "povao_pace_livre" and dados.categoria in ["pcd", "cadeirante"]:
        raise HTTPException(
            status_code=400, 
            detail="A modalidade 'Ranking da Galera' não está disponível para atletas PCD ou Cadeirantes."
        )
    
    faixa = calcular_faixa_etaria(dados.data_nascimento)
    
    # Definir role e equipe com base em ser dono de assessoria
    role = "dono_assessoria" if dados.is_dono_assessoria else "atleta"
    equipe = dados.equipe
    
    # Se for dono de assessoria, criar a assessoria
    assessoria_id = None
    if dados.is_dono_assessoria and dados.assessoria_data:
        # Verificar se assessoria já existe
        existing_assessoria = await db.assessorias.find_one({
            "nome": dados.assessoria_data.get("nome")
        })
        if existing_assessoria:
            raise HTTPException(status_code=400, detail="Já existe uma assessoria com este nome")
        
        # Criar assessoria
        assessoria_id = str(uuid.uuid4())
        assessoria_doc = {
            "id": assessoria_id,
            "nome": dados.assessoria_data.get("nome"),
            "cidade": dados.assessoria_data.get("cidade"),
            "estado": dados.assessoria_data.get("estado"),
            "mensagem_bio": dados.assessoria_data.get("mensagem_bio", ""),
            "foto_url": "",
            "dono_id": "",
            "dono_nome": dados.nome,
            "status": "ativa",
            "data_criacao": datetime.now(timezone.utc).isoformat()
        }
        
        # Usar o nome da assessoria como equipe do usuário
        equipe = dados.assessoria_data.get("nome")
    
    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        password_hash=get_password_hash(dados.password),
        equipe=equipe,
        cidade=dados.cidade,
        estado=dados.estado,
        genero=dados.genero,
        categoria=dados.categoria,
        data_nascimento=dados.data_nascimento,
        faixa_etaria=faixa,
        foto_url=gerar_foto_url(dados.nome),
        role=role,
        is_active=True,
        etnia=dados.etnia,
        apelido=dados.apelido,
        modalidade_usuario=dados.modalidade_usuario
    )
    
    doc = usuario.model_dump()
    doc["telefone"] = dados.telefone
    doc["tipo_corredor"] = dados.tipo_corredor
    doc["terreno_preferido"] = dados.terreno_preferido
    
    # Se for dono, adicionar campos extras
    if dados.is_dono_assessoria and dados.assessoria_data:
        doc["is_dono_assessoria"] = True
        doc["assessoria_id"] = assessoria_id
        doc["assessoria_nome"] = dados.assessoria_data.get("nome")
        
        # Atualizar assessoria com o ID do dono
        assessoria_doc["dono_id"] = usuario.id
        await db.assessorias.insert_one(assessoria_doc)
    
    await db.usuarios.insert_one(doc)
    
    # Processar código de indicação (se fornecido)
    indicador_nome = None
    if dados.codigo_indicacao:
        indicador_nome = await registrar_indicacao_interna(usuario.id, usuario.nome, dados.codigo_indicacao)
    
    token = create_access_token({"sub": usuario.id})
    
    return {
        "message": "Cadastro realizado com sucesso!",
        "token": token,
        "user": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "role": role,
            "modalidade_usuario": usuario.modalidade_usuario
        },
        "indicacao": {
            "registrada": indicador_nome is not None,
            "indicador_nome": indicador_nome
        } if dados.codigo_indicacao else None
    }


@router.post("/auth/login")
async def login(dados: UsuarioLogin):
    """Login de atleta ou admin"""
    user = await db.usuarios.find_one({"email": dados.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    if not verify_password(dados.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Usuário inativo")
    
    token = create_access_token({"sub": user["id"]})
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "role": user["role"],
            "foto_url": user.get("foto_url", ""),
            "categoria": user.get("categoria", "normal"),
            "equipe": user.get("equipe", ""),
            "estado": user.get("estado", ""),
            "is_dono_assessoria": user.get("is_dono_assessoria", False)
        }
    }


@router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retorna dados do usuário logado"""
    return {
        "id": current_user["id"],
        "nome": current_user["nome"],
        "email": current_user["email"],
        "role": current_user["role"],
        "categoria": current_user.get("categoria", "normal"),
        "foto_url": current_user.get("foto_url", ""),
        "equipe": current_user.get("equipe", ""),
        "estado": current_user.get("estado", ""),
        "modalidade_usuario": current_user.get("modalidade_usuario", "profissional_amador")
    }


# ==================== LOGIN COM SENHA DE EMERGÊNCIA ====================

import hashlib
from pydantic import BaseModel

class LoginEmergencia(BaseModel):
    email: str
    senha_emergencia: str

@router.post("/auth/login-emergencia")
async def login_com_senha_emergencia(dados: LoginEmergencia):
    """
    Login usando a senha de emergência do sistema.
    
    - Apenas Super Admin pode ter gerado esta senha
    - Limite de 3 usos por atleta
    - Todos os usos são registrados em log
    """
    # Buscar o usuário pelo email
    user = await db.usuarios.find_one({"email": dados.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    # Verificar a senha de emergência
    config_senha = await db.configuracoes_sistema.find_one(
        {"tipo": "senha_emergencia"},
        {"_id": 0}
    )
    
    if not config_senha:
        raise HTTPException(status_code=401, detail="Senha de emergência não configurada")
    
    # Validar hash da senha
    senha_hash = hashlib.sha256(dados.senha_emergencia.encode()).hexdigest()
    if senha_hash != config_senha["senha_hash"]:
        raise HTTPException(status_code=401, detail="Senha de emergência inválida")
    
    # Verificar limite de usos para este atleta (máximo 3)
    usos_atleta = await db.logs_senha_emergencia.count_documents({"atleta_id": user["id"]})
    
    if usos_atleta >= 3:
        raise HTTPException(
            status_code=403, 
            detail=f"Limite de usos excedido para este atleta ({usos_atleta}/3). Solicite reset ao Super Admin."
        )
    
    # Registrar o uso
    log_uso = {
        "id": str(uuid.uuid4()),
        "atleta_id": user["id"],
        "atleta_nome": user["nome"],
        "atleta_email": user["email"],
        "data_uso": datetime.now(timezone.utc).isoformat(),
        "uso_numero": usos_atleta + 1
    }
    await db.logs_senha_emergencia.insert_one(log_uso)
    
    # Criar token de acesso
    token = create_access_token({"sub": user["id"]})
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "role": user["role"],
            "foto_url": user.get("foto_url", ""),
            "categoria": user.get("categoria", "normal")
        },
        "aviso": f"Login via senha de emergência. Uso {usos_atleta + 1}/3 para este atleta.",
        "usos_restantes": 3 - (usos_atleta + 1)
    }



# ==================== RECUPERAÇÃO DE SENHA ====================

import string
import random

class RecuperarSenhaRequest(BaseModel):
    email: str

@router.post("/auth/recuperar-senha")
async def recuperar_senha(dados: RecuperarSenhaRequest):
    """
    Recuperação de senha: gera uma nova senha aleatória,
    salva o hash no banco e envia a nova senha por e-mail via Resend.
    """
    # Buscar usuário pelo email
    user = await db.usuarios.find_one({"email": dados.email}, {"_id": 0})
    if not user:
        # Retornamos sucesso mesmo se não encontrou para não expor emails válidos
        return {
            "success": True,
            "message": "Se o email estiver cadastrado, você receberá uma nova senha em instantes."
        }
    
    # Gerar nova senha aleatória (8 caracteres: letras + dígitos)
    caracteres = string.ascii_letters + string.digits
    nova_senha = ''.join(random.choices(caracteres, k=8))
    
    # Gerar hash da nova senha
    novo_hash = get_password_hash(nova_senha)
    
    # Atualizar no banco
    await db.usuarios.update_one(
        {"id": user["id"]},
        {"$set": {"password_hash": novo_hash}}
    )
    
    # Enviar email com a nova senha via Resend
    from services.email_service import enviar_email
    
    nome_atleta = user.get("nome", "Atleta")
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto;">
        <tr>
            <td style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center; padding-bottom: 20px; border-bottom: 2px solid #10B981;">
                            <h1 style="color: #10B981; margin: 0; font-size: 24px;">
                                Recuperacao de Senha
                            </h1>
                        </td>
                    </tr>
                </table>
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="font-size: 16px; color: #333; margin: 0 0 10px 0;">
                                Ola <strong>{nome_atleta}</strong>,
                            </p>
                            <p style="color: #666; margin: 0 0 20px 0;">
                                Voce solicitou a recuperacao de senha. Sua nova senha e:
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center;">
                            <table cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                                <tr>
                                    <td style="background: #ECFDF5; border: 2px solid #10B981; border-radius: 10px; padding: 25px 40px;">
                                        <span style="font-size: 32px; font-weight: bold; color: #059669; letter-spacing: 4px; font-family: monospace;">
                                            {nova_senha}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <p style="color: #F59E0B; font-size: 14px; margin: 0;">
                                Recomendamos que voce altere esta senha apos o login.
                            </p>
                        </td>
                    </tr>
                </table>
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
    
    texto_alt = f"Ola {nome_atleta}, sua nova senha do Ranking Run e: {nova_senha}. Recomendamos alterar apos o login."
    
    await enviar_email(
        destinatario=dados.email,
        assunto="Sua Nova Senha - Ranking Run",
        html_content=html_content,
        texto_alternativo=texto_alt
    )
    
    return {
        "success": True,
        "message": "Se o email estiver cadastrado, você receberá uma nova senha em instantes."
    }



# ==================== RECUPERAÇÃO DE SENHA VIA WHATSAPP ====================

class RecuperarSenhaWhatsAppRequest(BaseModel):
    telefone: str

@router.post("/auth/recuperar-senha-whatsapp")
async def recuperar_senha_whatsapp(dados: RecuperarSenhaWhatsAppRequest):
    """
    Recuperação de senha via WhatsApp: gera nova senha aleatória,
    salva o hash no banco e envia via WhatsApp Cloud API.
    """
    from routes.whatsapp_routes import enviar_mensagem_whatsapp, formatar_telefone_brasil

    # Formatar telefone para padrão internacional
    telefone_formatado = formatar_telefone_brasil(dados.telefone)

    # Buscar usuário pelo telefone (campo "telefone" no banco)
    user = await db.usuarios.find_one(
        {"telefone": {"$regex": dados.telefone[-8:]}},
        {"_id": 0}
    )

    if not user:
        return {
            "success": True,
            "message": "Se o telefone estiver cadastrado, você receberá uma nova senha via WhatsApp."
        }

    # Gerar nova senha aleatória
    caracteres = string.ascii_letters + string.digits
    nova_senha = ''.join(random.choices(caracteres, k=8))

    # Salvar hash no banco
    novo_hash = get_password_hash(nova_senha)
    await db.usuarios.update_one(
        {"id": user["id"]},
        {"$set": {"password_hash": novo_hash}}
    )

    # Montar mensagem
    nome = user.get("nome", "Atleta")
    mensagem = (
        f"Ranking Run - Recuperacao de Senha\n\n"
        f"Ola {nome}!\n\n"
        f"Sua nova senha e: *{nova_senha}*\n\n"
        f"Use esta senha para acessar sua conta. "
        f"Recomendamos que voce altere a senha apos o login.\n\n"
        f"Ranking Run Pro"
    )

    # Enviar via WhatsApp
    resultado = await enviar_mensagem_whatsapp(telefone_formatado, mensagem)

    if resultado.get("success"):
        return {
            "success": True,
            "message": "Se o telefone estiver cadastrado, você receberá uma nova senha via WhatsApp."
        }
    else:
        error_detail = resultado.get("error", "")
        print(f"[WhatsApp Recovery] Erro: {error_detail}")
        return {
            "success": False,
            "message": "Não foi possível enviar a mensagem via WhatsApp. Tente a recuperação por email."
        }
