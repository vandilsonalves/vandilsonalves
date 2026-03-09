# /app/backend/routes/auth.py
# Rotas de autenticação: login, registro, perfil

from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import jwt
import uuid

from models import UsuarioRegister, UsuarioLogin
from utils import db, get_current_user, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Autenticação"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register")
async def register_atleta(dados: UsuarioRegister):
    """Registra novo atleta"""
    # Verificar se email já existe
    if await db.usuarios.find_one({"email": dados.email}):
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Hash da senha
    password_hash = pwd_context.hash(dados.password)
    
    # Criar usuário
    usuario = {
        "id": str(uuid.uuid4()),
        "nome": dados.nome,
        "email": dados.email,
        "password_hash": password_hash,
        "role": "atleta",
        "categoria": dados.categoria or "normal",
        "genero": dados.genero,
        "data_nascimento": dados.data_nascimento,
        "estado": dados.estado,
        "cidade": dados.cidade,
        "equipe": dados.equipe or "",
        "etnia": dados.etnia or "",
        "faixa_etaria": dados.faixa_etaria or "",
        "modalidade_usuario": dados.modalidade_usuario or "profissional_amador",
        "foto_url": "",
        "pontos_total": 0,
        "total_corridas": 0,
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "ativo": True
    }
    
    await db.usuarios.insert_one(usuario)
    
    # Gerar token
    token = jwt.encode(
        {"sub": usuario["id"], "exp": datetime.now(timezone.utc) + timedelta(days=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {
        "token": token,
        "user": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "role": usuario["role"],
            "foto_url": usuario["foto_url"],
            "categoria": usuario["categoria"]
        }
    }


@router.post("/login")
async def login(dados: UsuarioLogin):
    """Login de usuário"""
    user = await db.usuarios.find_one({"email": dados.email}, {"_id": 0})
    
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    if not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    if not pwd_context.verify(dados.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    # Gerar token
    token = jwt.encode(
        {"sub": user["id"], "exp": datetime.now(timezone.utc) + timedelta(days=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "nome": user.get("nome", ""),
            "email": user["email"],
            "role": user.get("role", "atleta"),
            "foto_url": user.get("foto_url", ""),
            "categoria": user.get("categoria", "normal")
        }
    }


@router.get("/me")
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
