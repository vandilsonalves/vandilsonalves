# /app/backend/routes/rbac.py
# Sistema RBAC - Role Based Access Control
# Gerenciamento de Administradores, Permissões e Logs

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from jose import JWTError, jwt
import os
import logging

from models.rbac import (
    Administrador, AdminCreate, AdminUpdate, 
    AdminLog, LoginHistory, CodigoVerificacao, AlertaSeguranca,
    PERMISSOES_SISTEMA, ROLES_PREDEFINIDOS
)
from services.rbac_service import (
    gerar_codigo_2fa, extrair_info_dispositivo, 
    criar_log_acao, criar_alerta_seguranca
)
from services.email_service import (
    enviar_codigo_2fa, enviar_alerta_emergencia,
    enviar_boas_vindas_admin, enviar_notificacao_bloqueio,
    is_email_configured
)
from services import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)

# MongoDB connection (usando as mesmas variáveis do server.py)
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'test_database')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Security
security = HTTPBearer()

router = APIRouter(tags=["RBAC - Administração"])


# ==================== AUTH HELPERS (local) ====================

async def get_current_user_rbac(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica token JWT e retorna usuário atual"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = await db.usuarios.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        return user
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token inválido")


async def get_admin_user_rbac(current_user: dict = Depends(get_current_user_rbac)):
    """Verifica se usuário é admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user


# ==================== HELPERS ====================

def get_client_ip(request: Request) -> str:
    """Obtém IP real do cliente (considera proxy)"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def get_super_admin(current_user: dict = Depends(get_current_user_rbac)):
    """Verifica se é Super Admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito")
    
    # Verificar se é super_admin na coleção de administradores
    admin = await db.administradores.find_one({"email": current_user.get("email")}, {"_id": 0})
    if not admin:
        # Fallback: admin antigo ainda é considerado super_admin
        return current_user
    
    if admin.get("role_nome") != "Super Admin" and not admin.get("is_super_admin"):
        raise HTTPException(status_code=403, detail="Apenas Super Admin pode realizar esta ação")
    
    return {**current_user, "admin_data": admin}


async def registrar_log(
    request: Request,
    admin: dict,
    tipo_acao: str,
    descricao: str,
    entidade_tipo: str = None,
    entidade_id: str = None,
    entidade_nome: str = None,
    dados_extras: dict = None
):
    """Registra log de ação administrativa"""
    admin_data = admin.get("admin_data", {})
    
    log = criar_log_acao(
        admin_id=admin.get("id"),
        admin_nome=admin.get("nome"),
        admin_role=admin_data.get("role_nome", "Admin Legado"),
        tipo_acao=tipo_acao,
        descricao=descricao,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
        entidade_tipo=entidade_tipo,
        entidade_id=entidade_id,
        entidade_nome=entidade_nome,
        dados_extras=dados_extras
    )
    
    await db.admin_logs.insert_one(log)
    return log


# ==================== SETUP INICIAL ====================

@router.post("/rbac/setup")
async def setup_rbac_inicial(request: Request, super_admin: dict = Depends(get_super_admin)):
    """
    Configura o sistema RBAC inicial.
    Cria as roles padrão e migra o admin existente para Super Admin.
    """
    # Verificar se já foi configurado
    roles_existentes = await db.roles.count_documents({})
    if roles_existentes > 0:
        raise HTTPException(status_code=400, detail="Sistema RBAC já configurado")
    
    # Criar roles padrão
    roles_criadas = []
    for codigo, dados in ROLES_PREDEFINIDOS.items():
        role = {
            "id": str(uuid.uuid4()),
            "codigo": codigo,
            "nome": dados["nome"],
            "descricao": dados["descricao"],
            "nivel": dados["nivel"],
            "permissoes": dados["permissoes"],
            "ativo": True,
            "criado_em": datetime.now(timezone.utc).isoformat()
        }
        await db.roles.insert_one(role)
        roles_criadas.append(role["nome"])
    
    # Migrar admin existente para administradores
    admin_existente = await db.usuarios.find_one({"role": "admin"}, {"_id": 0})
    if admin_existente:
        role_super = await db.roles.find_one({"codigo": "super_admin"}, {"_id": 0})
        
        admin_doc = {
            "id": admin_existente.get("id"),
            "nome": admin_existente.get("nome"),
            "email": admin_existente.get("email"),
            "password_hash": admin_existente.get("password_hash", ""),
            "role_id": role_super["id"],
            "role_nome": "Super Admin",
            "status": "ativo",
            "foto_url": admin_existente.get("foto_url", ""),
            "dois_fatores_ativo": False,
            "criado_em": datetime.now(timezone.utc).isoformat(),
            "criado_por": "sistema",
            "is_super_admin": True,
            "is_emergencia": False,
            "invisivel": False
        }
        await db.administradores.insert_one(admin_doc)
    
    # Criar Admin de Emergência
    role_emergencia = await db.roles.find_one({"codigo": "admin_emergencia"}, {"_id": 0})
    admin_emergencia = {
        "id": str(uuid.uuid4()),
        "nome": "Admin de Emergência",
        "email": "suporte@rankingrun.com.br",
        "password_hash": get_password_hash("EmergenciaRankingRun2026!"),
        "role_id": role_emergencia["id"],
        "role_nome": "Admin de Emergência",
        "status": "ativo",
        "foto_url": "",
        "dois_fatores_ativo": True,  # 2FA obrigatório
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "criado_por": "sistema",
        "is_super_admin": False,
        "is_emergencia": True,
        "invisivel": True  # Não aparece no painel
    }
    await db.administradores.insert_one(admin_emergencia)
    
    # Registrar log
    await registrar_log(
        request, super_admin, "setup_rbac",
        "Sistema RBAC configurado inicialmente",
        dados_extras={"roles_criadas": roles_criadas}
    )
    
    return {
        "message": "Sistema RBAC configurado com sucesso!",
        "roles_criadas": roles_criadas,
        "admin_emergencia_email": "suporte@rankingrun.com.br",
        "aviso": "IMPORTANTE: Guarde a senha do Admin de Emergência em local seguro!"
    }


# ==================== ADMINISTRADORES ====================

@router.get("/rbac/admins")
async def listar_administradores(
    request: Request,
    super_admin: dict = Depends(get_super_admin)
):
    """Lista todos os administradores (exceto invisíveis)"""
    admins = await db.administradores.find(
        {"invisivel": {"$ne": True}},
        {"_id": 0, "password_hash": 0, "dois_fatores_secret": 0}
    ).to_list(None)
    
    return {
        "administradores": admins,
        "total": len(admins)
    }


@router.post("/rbac/admins")
async def criar_administrador(
    dados: AdminCreate,
    request: Request,
    super_admin: dict = Depends(get_super_admin)
):
    """Cria novo administrador (colaborador)"""
    # Verificar email único
    existente = await db.administradores.find_one({"email": dados.email})
    if existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Verificar se email existe em usuários
    existente_usuario = await db.usuarios.find_one({"email": dados.email})
    if existente_usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado como atleta")
    
    # Buscar role
    role = await db.roles.find_one({"id": dados.role_id}, {"_id": 0})
    if not role:
        raise HTTPException(status_code=404, detail="Role não encontrada")
    
    # Não permitir criar admin de emergência por aqui
    if role.get("codigo") == "admin_emergencia":
        raise HTTPException(status_code=403, detail="Não é permitido criar Admin de Emergência")
    
    admin = {
        "id": str(uuid.uuid4()),
        "nome": dados.nome,
        "email": dados.email,
        "password_hash": get_password_hash(dados.password),
        "role_id": role["id"],
        "role_nome": role["nome"],
        "status": "ativo",
        "foto_url": f"https://ui-avatars.com/api/?name={dados.nome.replace(' ', '+')}&size=128&background=random",
        "dois_fatores_ativo": False,
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "criado_por": super_admin.get("id"),
        "is_super_admin": role.get("codigo") == "super_admin",
        "is_emergencia": False,
        "invisivel": False
    }
    
    await db.administradores.insert_one(admin)
    
    # Também criar na coleção usuarios para compatibilidade
    usuario_doc = {
        "id": admin["id"],
        "nome": dados.nome,
        "email": dados.email,
        "password_hash": admin["password_hash"],
        "role": "admin",
        "categoria": "normal",
        "genero": "M",
        "estado": "BR",
        "cidade": "",
        "equipe": "",
        "foto_url": admin["foto_url"],
        "is_active": True,
        "data_nascimento": "1990-01-01",
        "faixa_etaria": "30-39"
    }
    await db.usuarios.insert_one(usuario_doc)
    
    # Registrar log
    await registrar_log(
        request, super_admin, "criar_admin",
        f"Criou administrador: {dados.nome} ({role['nome']})",
        entidade_tipo="administrador",
        entidade_id=admin["id"],
        entidade_nome=dados.nome
    )
    
    # Enviar email de boas-vindas
    email_result = await enviar_boas_vindas_admin(
        admin_nome=dados.nome,
        admin_email=dados.email,
        role_nome=role["nome"],
        senha=dados.password  # Envia a senha inicial
    )
    logger.info(f"Email de boas-vindas enviado para {dados.email}: {email_result.get('status')}")
    
    return {
        "message": f"Administrador '{dados.nome}' criado com sucesso!",
        "admin": {
            "id": admin["id"],
            "nome": admin["nome"],
            "email": admin["email"],
            "role": role["nome"]
        },
        "email_status": email_result.get("status")
    }


@router.put("/rbac/admins/{admin_id}")
async def atualizar_administrador(
    admin_id: str,
    dados: AdminUpdate,
    request: Request,
    super_admin: dict = Depends(get_super_admin)
):
    """Atualiza dados de um administrador"""
    admin = await db.administradores.find_one({"id": admin_id}, {"_id": 0})
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador não encontrado")
    
    # Não permitir editar admin de emergência
    if admin.get("is_emergencia"):
        raise HTTPException(status_code=403, detail="Admin de Emergência não pode ser editado")
    
    # Não permitir auto-rebaixamento de super admin
    if admin_id == super_admin.get("id") and dados.role_id:
        raise HTTPException(status_code=403, detail="Você não pode alterar sua própria role")
    
    update_data = {}
    
    if dados.nome:
        update_data["nome"] = dados.nome
    if dados.email:
        # Verificar se email já existe
        existente = await db.administradores.find_one({"email": dados.email, "id": {"$ne": admin_id}})
        if existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        update_data["email"] = dados.email
    if dados.status:
        update_data["status"] = dados.status
    if dados.role_id:
        role = await db.roles.find_one({"id": dados.role_id}, {"_id": 0})
        if not role:
            raise HTTPException(status_code=404, detail="Role não encontrada")
        if role.get("codigo") == "admin_emergencia":
            raise HTTPException(status_code=403, detail="Não é permitido atribuir role de Admin de Emergência")
        update_data["role_id"] = dados.role_id
        update_data["role_nome"] = role["nome"]
        update_data["is_super_admin"] = role.get("codigo") == "super_admin"
    
    if update_data:
        await db.administradores.update_one({"id": admin_id}, {"$set": update_data})
        
        # Atualizar também na coleção usuarios
        update_usuario = {}
        if dados.nome:
            update_usuario["nome"] = dados.nome
        if dados.email:
            update_usuario["email"] = dados.email
        if update_usuario:
            await db.usuarios.update_one({"id": admin_id}, {"$set": update_usuario})
    
    # Registrar log
    await registrar_log(
        request, super_admin, "editar_admin",
        f"Editou administrador: {admin.get('nome')}",
        entidade_tipo="administrador",
        entidade_id=admin_id,
        entidade_nome=admin.get("nome"),
        dados_extras={"alteracoes": list(update_data.keys())}
    )
    
    return {"message": "Administrador atualizado com sucesso!"}


@router.delete("/rbac/admins/{admin_id}")
async def excluir_administrador(
    admin_id: str,
    request: Request,
    super_admin: dict = Depends(get_super_admin)
):
    """Exclui um administrador"""
    admin = await db.administradores.find_one({"id": admin_id}, {"_id": 0})
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador não encontrado")
    
    # Não permitir excluir admin de emergência
    if admin.get("is_emergencia"):
        raise HTTPException(status_code=403, detail="Admin de Emergência não pode ser excluído")
    
    # Não permitir auto-exclusão
    if admin_id == super_admin.get("id"):
        raise HTTPException(status_code=403, detail="Você não pode excluir a si mesmo")
    
    # Não permitir excluir o último super admin
    super_admins = await db.administradores.count_documents({"is_super_admin": True, "id": {"$ne": admin_id}})
    if admin.get("is_super_admin") and super_admins == 0:
        raise HTTPException(status_code=403, detail="Não é possível excluir o último Super Admin")
    
    await db.administradores.delete_one({"id": admin_id})
    await db.usuarios.delete_one({"id": admin_id})
    
    # Registrar log
    await registrar_log(
        request, super_admin, "excluir_admin",
        f"Excluiu administrador: {admin.get('nome')}",
        entidade_tipo="administrador",
        entidade_id=admin_id,
        entidade_nome=admin.get("nome")
    )
    
    return {"message": f"Administrador '{admin.get('nome')}' excluído com sucesso!"}


@router.post("/rbac/admins/{admin_id}/bloquear")
async def bloquear_administrador(
    admin_id: str,
    request: Request,
    super_admin: dict = Depends(get_super_admin)
):
    """Bloqueia um administrador"""
    admin = await db.administradores.find_one({"id": admin_id}, {"_id": 0})
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador não encontrado")
    
    if admin_id == super_admin.get("id"):
        raise HTTPException(status_code=403, detail="Você não pode bloquear a si mesmo")
    
    await db.administradores.update_one(
        {"id": admin_id},
        {"$set": {"status": "bloqueado"}}
    )
    
    # Registrar log
    await registrar_log(
        request, super_admin, "bloquear_admin",
        f"Bloqueou administrador: {admin.get('nome')}",
        entidade_tipo="administrador",
        entidade_id=admin_id,
        entidade_nome=admin.get("nome")
    )
    
    # Enviar notificação de bloqueio por email
    email_result = await enviar_notificacao_bloqueio(
        admin_nome=admin.get("nome"),
        admin_email=admin.get("email"),
        motivo="Bloqueado pelo Super Administrador"
    )
    logger.info(f"Email de bloqueio enviado para {admin.get('email')}: {email_result.get('status')}")
    
    return {"message": f"Administrador '{admin.get('nome')}' bloqueado!"}


# ==================== ROLES E PERMISSÕES ====================

@router.get("/rbac/roles")
async def listar_roles(super_admin: dict = Depends(get_super_admin)):
    """Lista todas as roles disponíveis"""
    roles = await db.roles.find({"codigo": {"$ne": "admin_emergencia"}}, {"_id": 0}).to_list(None)
    return {"roles": roles}


@router.get("/rbac/permissoes")
async def listar_permissoes(super_admin: dict = Depends(get_super_admin)):
    """Lista todas as permissões disponíveis"""
    permissoes = []
    for codigo, dados in PERMISSOES_SISTEMA.items():
        if dados["categoria"] != "emergencia":  # Não mostrar permissões de emergência
            permissoes.append({
                "codigo": codigo,
                "nome": dados["nome"],
                "descricao": dados["descricao"],
                "categoria": dados["categoria"]
            })
    return {"permissoes": permissoes}


# ==================== LOGS DE AUDITORIA ====================

@router.get("/rbac/logs")
async def listar_logs(
    limite: int = 100,
    admin_id: Optional[str] = None,
    tipo_acao: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    super_admin: dict = Depends(get_super_admin)
):
    """Lista logs de ações administrativas"""
    query = {}
    
    if admin_id:
        query["admin_id"] = admin_id
    if tipo_acao:
        query["tipo_acao"] = tipo_acao
    if data_inicio:
        query["data_hora"] = {"$gte": data_inicio}
    if data_fim:
        if "data_hora" in query:
            query["data_hora"]["$lte"] = data_fim
        else:
            query["data_hora"] = {"$lte": data_fim}
    
    logs = await db.admin_logs.find(query, {"_id": 0}).sort("data_hora", -1).limit(limite).to_list(None)
    
    return {
        "logs": logs,
        "total": len(logs)
    }


@router.get("/rbac/logs/export")
async def exportar_logs(
    formato: str = "json",
    super_admin: dict = Depends(get_super_admin)
):
    """Exporta logs de auditoria"""
    logs = await db.admin_logs.find({}, {"_id": 0}).sort("data_hora", -1).to_list(None)
    
    if formato == "json":
        return {"logs": logs, "total": len(logs)}
    
    # TODO: Implementar CSV se necessário
    return {"logs": logs, "total": len(logs)}


# ==================== HISTÓRICO DE LOGIN ====================

@router.get("/rbac/login-history")
async def historico_login(
    admin_id: Optional[str] = None,
    limite: int = 50,
    super_admin: dict = Depends(get_super_admin)
):
    """Lista histórico de login dos administradores"""
    query = {}
    if admin_id:
        query["admin_id"] = admin_id
    
    historico = await db.login_history.find(query, {"_id": 0}).sort("data_hora", -1).limit(limite).to_list(None)
    
    return {
        "historico": historico,
        "total": len(historico)
    }


# ==================== ALERTAS DE SEGURANÇA ====================

@router.get("/rbac/alertas")
async def listar_alertas(
    apenas_nao_resolvidos: bool = True,
    super_admin: dict = Depends(get_super_admin)
):
    """Lista alertas de segurança"""
    query = {}
    if apenas_nao_resolvidos:
        query["resolvido"] = False
    
    alertas = await db.alertas_seguranca.find(query, {"_id": 0}).sort("data_hora", -1).to_list(None)
    
    return {
        "alertas": alertas,
        "total": len(alertas)
    }


@router.post("/rbac/alertas/{alerta_id}/resolver")
async def resolver_alerta(
    alerta_id: str,
    request: Request,
    super_admin: dict = Depends(get_super_admin)
):
    """Marca alerta como resolvido"""
    await db.alertas_seguranca.update_one(
        {"id": alerta_id},
        {"$set": {
            "resolvido": True,
            "resolvido_por": super_admin.get("id"),
            "resolvido_em": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Alerta marcado como resolvido"}


# ==================== ESTATÍSTICAS RBAC ====================

@router.get("/rbac/stats")
async def estatisticas_rbac(super_admin: dict = Depends(get_super_admin)):
    """Estatísticas do sistema RBAC"""
    total_admins = await db.administradores.count_documents({"invisivel": {"$ne": True}})
    admins_ativos = await db.administradores.count_documents({"status": "ativo", "invisivel": {"$ne": True}})
    admins_bloqueados = await db.administradores.count_documents({"status": "bloqueado"})
    total_logs_hoje = await db.admin_logs.count_documents({
        "data_hora": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()}
    })
    alertas_pendentes = await db.alertas_seguranca.count_documents({"resolvido": False})
    
    # Distribuição por role
    pipeline = [
        {"$match": {"invisivel": {"$ne": True}}},
        {"$group": {"_id": "$role_nome", "total": {"$sum": 1}}}
    ]
    dist_roles = await db.administradores.aggregate(pipeline).to_list(None)
    
    return {
        "total_administradores": total_admins,
        "administradores_ativos": admins_ativos,
        "administradores_bloqueados": admins_bloqueados,
        "logs_hoje": total_logs_hoje,
        "alertas_pendentes": alertas_pendentes,
        "distribuicao_roles": [{"role": r["_id"], "total": r["total"]} for r in dist_roles],
        "email_configurado": is_email_configured()
    }


@router.get("/rbac/email-status")
async def verificar_status_email(super_admin: dict = Depends(get_super_admin)):
    """Verifica se o serviço de email está configurado"""
    return {
        "configurado": is_email_configured(),
        "mensagem": "Serviço de email configurado e pronto" if is_email_configured() 
                   else "RESEND_API_KEY não configurada. Emails não serão enviados.",
        "instrucoes": None if is_email_configured() else {
            "passo_1": "Acesse https://resend.com e crie uma conta",
            "passo_2": "Vá em Dashboard → API Keys → Create API Key",
            "passo_3": "Adicione RESEND_API_KEY=re_sua_chave no arquivo /app/backend/.env",
            "passo_4": "Reinicie o backend: sudo supervisorctl restart backend"
        },
        "nota": "Em modo de teste, o Resend só envia para o email da conta. Verifique um domínio em resend.com/domains para enviar para outros emails."
    }


@router.post("/rbac/email-test")
async def testar_envio_email(
    dados: dict,
    request: Request,
    super_admin: dict = Depends(get_super_admin)
):
    """Envia email de teste para verificar configuração"""
    from services.email_service import enviar_email
    
    email_destino = dados.get("email", "")
    if not email_destino:
        raise HTTPException(status_code=400, detail="Email de destino é obrigatório")
    
    result = await enviar_email(
        destinatario=email_destino,
        assunto="🧪 Teste de Email - Ranking Run",
        html_content="""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #10B981;">✅ Email de Teste</h1>
            <p>Se você está vendo esta mensagem, o serviço de email está funcionando corretamente!</p>
            <p style="color: #666;">Ranking Run - Sistema de Ranking de Corridas</p>
        </body>
        </html>
        """,
        texto_alternativo="Teste de email - Ranking Run. Se você está vendo esta mensagem, o email está funcionando!"
    )
    
    await registrar_log(
        request, super_admin, "teste_email",
        f"Testou envio de email para {email_destino}",
        dados_extras={"resultado": result.get("status")}
    )
    
    return result


# ==================== 2FA E LOGIN ADMIN ====================

@router.post("/rbac/login")
async def login_admin(
    dados: dict,
    request: Request
):
    """Login de administrador com suporte a 2FA"""
    email = dados.get("email")
    password = dados.get("password")
    codigo_2fa = dados.get("codigo_2fa")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")
    
    # Buscar administrador
    admin = await db.administradores.find_one({"email": email}, {"_id": 0})
    
    if not admin:
        # Tentar na coleção usuarios (admin legado)
        usuario = await db.usuarios.find_one({"email": email, "role": "admin"}, {"_id": 0})
        if not usuario:
            await registrar_tentativa_login(request, email, False, "Email não encontrado")
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        # Login de admin legado
        if not verify_password(password, usuario.get("password_hash", "")):
            await registrar_tentativa_login(request, email, False, "Senha incorreta")
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        token = create_access_token({"sub": usuario["id"]})
        await registrar_tentativa_login(request, email, True, admin_id=usuario["id"], admin_nome=usuario.get("nome"))
        
        return {
            "token": token,
            "user": {
                "id": usuario["id"],
                "nome": usuario.get("nome"),
                "email": usuario["email"],
                "role": "admin",
                "tipo_admin": "legado",
                "permissoes": list(PERMISSOES_SISTEMA.keys())  # Todas as permissões
            },
            "requer_2fa": False
        }
    
    # Verificar status
    if admin.get("status") == "bloqueado":
        await registrar_tentativa_login(request, email, False, "Admin bloqueado")
        raise HTTPException(status_code=403, detail="Administrador bloqueado. Contate o Super Admin.")
    
    if admin.get("status") == "inativo":
        await registrar_tentativa_login(request, email, False, "Admin inativo")
        raise HTTPException(status_code=403, detail="Administrador inativo.")
    
    # Verificar senha
    if not verify_password(password, admin.get("password_hash", "")):
        await registrar_tentativa_login(request, email, False, "Senha incorreta")
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Verificar 2FA
    if admin.get("dois_fatores_ativo"):
        if not codigo_2fa:
            # Gerar e enviar código 2FA
            codigo = gerar_codigo_2fa()
            expira_em = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
            
            codigo_doc = {
                "id": str(uuid.uuid4()),
                "admin_id": admin["id"],
                "email": email,
                "codigo": codigo,
                "tipo": "login",
                "criado_em": datetime.now(timezone.utc).isoformat(),
                "expira_em": expira_em,
                "usado": False
            }
            await db.codigos_verificacao.insert_one(codigo_doc)
            
            # Enviar email com código 2FA
            email_result = await enviar_codigo_2fa(email, codigo, admin.get("nome", "Admin"))
            logger.info(f"2FA email enviado para {email}: {email_result.get('status')}")
            
            return {
                "requer_2fa": True,
                "message": "Código de verificação enviado para seu email",
                "email_status": email_result.get("status")
            }
        
        # Verificar código 2FA
        codigo_valido = await db.codigos_verificacao.find_one({
            "admin_id": admin["id"],
            "codigo": codigo_2fa,
            "usado": False,
            "expira_em": {"$gt": datetime.now(timezone.utc).isoformat()}
        })
        
        if not codigo_valido:
            await registrar_tentativa_login(request, email, False, "Código 2FA inválido")
            raise HTTPException(status_code=401, detail="Código de verificação inválido ou expirado")
        
        # Marcar código como usado
        await db.codigos_verificacao.update_one(
            {"id": codigo_valido["id"]},
            {"$set": {"usado": True, "usado_em": datetime.now(timezone.utc).isoformat()}}
        )
    
    # Login bem-sucedido
    token = create_access_token({"sub": admin["id"]})
    
    # Atualizar último login
    info_dispositivo = extrair_info_dispositivo(request.headers.get("User-Agent", ""))
    await db.administradores.update_one(
        {"id": admin["id"]},
        {"$set": {
            "ultimo_login": datetime.now(timezone.utc).isoformat(),
            "ultimo_ip": get_client_ip(request),
            "ultimo_dispositivo": info_dispositivo["descricao_completa"]
        }}
    )
    
    await registrar_tentativa_login(request, email, True, admin_id=admin["id"], admin_nome=admin.get("nome"))
    
    # Se for Admin de Emergência, criar alerta e enviar email
    if admin.get("is_emergencia"):
        data_hora = datetime.now(timezone.utc).isoformat()
        alerta = criar_alerta_seguranca(
            tipo="admin_emergencia_usado",
            titulo="Admin de Emergência Utilizado",
            descricao=f"A conta de Admin de Emergência foi utilizada para login",
            ip_address=get_client_ip(request),
            admin_id=admin["id"],
            admin_nome=admin.get("nome"),
            dispositivo=info_dispositivo["descricao_completa"]
        )
        await db.alertas_seguranca.insert_one(alerta)
        
        # Enviar email de alerta de segurança
        email_result = await enviar_alerta_emergencia(
            admin_nome=admin.get("nome", "Admin de Emergência"),
            acao="Login no sistema",
            ip=get_client_ip(request),
            dispositivo=info_dispositivo["descricao_completa"],
            data_hora=data_hora
        )
        logger.warning(f"⚠️ Admin de Emergência utilizado! Email de alerta: {email_result.get('status')}")
    
    # Buscar permissões da role
    role = await db.roles.find_one({"id": admin.get("role_id")}, {"_id": 0})
    permissoes = role.get("permissoes", []) if role else list(PERMISSOES_SISTEMA.keys())
    
    return {
        "token": token,
        "user": {
            "id": admin["id"],
            "nome": admin.get("nome"),
            "email": admin["email"],
            "role": "admin",
            "tipo_admin": admin.get("role_nome"),
            "is_super_admin": admin.get("is_super_admin", False),
            "is_emergencia": admin.get("is_emergencia", False),
            "permissoes": permissoes
        },
        "requer_2fa": False
    }


async def registrar_tentativa_login(
    request: Request,
    email: str,
    sucesso: bool,
    motivo_falha: str = None,
    admin_id: str = None,
    admin_nome: str = None
):
    """Registra tentativa de login"""
    info_dispositivo = extrair_info_dispositivo(request.headers.get("User-Agent", ""))
    
    registro = {
        "id": str(uuid.uuid4()),
        "admin_id": admin_id,
        "admin_nome": admin_nome,
        "email": email,
        "sucesso": sucesso,
        "ip_address": get_client_ip(request),
        "user_agent": request.headers.get("User-Agent", ""),
        "dispositivo": info_dispositivo["dispositivo"],
        "navegador": info_dispositivo["navegador"],
        "cidade_aproximada": "Brasil",
        "data_hora": datetime.now(timezone.utc).isoformat(),
        "motivo_falha": motivo_falha
    }
    
    await db.login_history.insert_one(registro)


# ==================== VERIFICAR PERMISSÃO ====================

@router.get("/rbac/verificar-permissao/{permissao}")
async def verificar_permissao_admin(
    permissao: str,
    current_user: dict = Depends(get_current_user_rbac)
):
    """Verifica se o usuário atual tem uma permissão específica"""
    if current_user.get("role") != "admin":
        return {"tem_permissao": False, "motivo": "Não é administrador"}
    
    # Buscar dados do admin
    admin = await db.administradores.find_one({"email": current_user.get("email")}, {"_id": 0})
    
    if not admin:
        # Admin legado tem todas as permissões
        return {"tem_permissao": True, "motivo": "Admin legado"}
    
    # Buscar permissões da role
    role = await db.roles.find_one({"id": admin.get("role_id")}, {"_id": 0})
    if not role:
        return {"tem_permissao": False, "motivo": "Role não encontrada"}
    
    tem_permissao = permissao in role.get("permissoes", [])
    
    return {
        "tem_permissao": tem_permissao,
        "role": admin.get("role_nome"),
        "permissao_solicitada": permissao
    }
