# /app/backend/routes/auth_routes.py
# Módulo de Autenticação - Rotas de login, registro e perfil

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
from jose import JWTError, jwt
import uuid

from config import db, security
from models import Usuario, UsuarioRegister, UsuarioLogin
from services import (
    verify_password, get_password_hash, create_access_token,
    calcular_faixa_etaria, gerar_foto_url, SECRET_KEY, ALGORITHM
)

# Função auxiliar para registrar indicação
async def registrar_indicacao_interna(indicado_id: str, codigo_indicacao: str):
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
    
    # Verificar se ganhou insígnia de embaixador (5+ indicações)
    total_indicacoes = await db.indicacoes.count_documents({
        "indicador_id": indicador["id"],
        "status": "confirmada"
    })
    
    if total_indicacoes >= 5:
        # Verificar se já tem a insígnia
        badge_existente = await db.badges_atleta.find_one({
            "atleta_id": indicador["id"],
            "badge_id": "embaixador"
        })
        
        if not badge_existente:
            # Conceder insígnia
            await db.badges_atleta.insert_one({
                "atleta_id": indicador["id"],
                "badge_id": "embaixador",
                "data_conquista": datetime.now(timezone.utc).isoformat()
            })
    
    return indicador["nome"]

router = APIRouter(tags=["Autenticação"])


# ==================== AUTH HELPERS ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica token JWT e retorna usuário atual"""
    try:
        token = credentials.credentials
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
    """Verifica se o usuário é administrador"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")
    return current_user


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
            detail="A modalidade 'Ranking do Povão - Pace Livre' não está disponível para atletas PCD ou Cadeirantes."
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
        indicador_nome = await registrar_indicacao_interna(usuario.id, dados.codigo_indicacao)
    
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
            "categoria": user.get("categoria", "normal")
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
