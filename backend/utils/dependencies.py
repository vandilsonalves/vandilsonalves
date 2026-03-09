# /app/backend/utils/dependencies.py
# Dependências compartilhadas para todas as rotas

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Configurações
SECRET_KEY = os.environ.get("SECRET_KEY", "ranking_run_secret_key_2025")
ALGORITHM = "HS256"

# MongoDB
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "ranking_run")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Security
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Verifica se usuário é admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user


async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    """Retorna usuário se autenticado, None caso contrário"""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            user = await db.usuarios.find_one({"id": user_id}, {"_id": 0})
            return user
    except:
        pass
    return None
