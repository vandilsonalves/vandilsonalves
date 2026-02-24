# Helper Functions and Services
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "sua-chave-secreta-super-segura-aqui-123456")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def calcular_faixa_etaria(data_nascimento: str) -> str:
    ano_nasc = int(data_nascimento.split('-')[0])
    idade = 2025 - ano_nasc
    
    if idade < 12:
        return "0-11"
    elif idade <= 17:
        return "12-17"
    elif idade <= 29:
        return "18-29"
    elif idade <= 39:
        return "30-39"
    elif idade <= 49:
        return "40-49"
    elif idade <= 59:
        return "50-59"
    else:
        return "60+"

def gerar_foto_url(nome: str) -> str:
    nome_encoded = nome.replace(' ', '+')
    return f"https://ui-avatars.com/api/?name={nome_encoded}&size=128&background=random&bold=true"

def calcular_pontos_colocacao(colocacao: int, categoria: str) -> int:
    """Calcula pontos conforme regulamento Art.16 e Art.17"""
    if categoria in ["pcd", "cadeirante"]:
        # PCD e Cadeirante: apenas top 3
        if colocacao == 1:
            return 10
        elif colocacao == 2:
            return 9
        elif colocacao == 3:
            return 8
        else:
            return 0
    else:
        # Normal: top 10
        pontuacao = {
            1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
            6: 5, 7: 4, 8: 3, 9: 2, 10: 1
        }
        return pontuacao.get(colocacao, 0)

def get_min_corridas_categoria(categoria: str) -> int:
    """Retorna número mínimo de corridas conforme Art.19"""
    if categoria in ["pcd", "cadeirante"]:
        return 8
    return 12

# Conquistas disponíveis
CONQUISTAS = {
    "primeiro_lugar": {
        "nome": "Campeão",
        "descricao": "Conquistou o 1º lugar em uma corrida",
        "icone": "🥇",
        "pontos_bonus": 5
    },
    "podio": {
        "nome": "Pódio",
        "descricao": "Subiu ao pódio (top 3) em uma corrida",
        "icone": "🏆",
        "pontos_bonus": 2
    },
    "10_corridas": {
        "nome": "Veterano",
        "descricao": "Completou 10 corridas",
        "icone": "🏃",
        "pontos_bonus": 10
    },
    "elite": {
        "nome": "Elite",
        "descricao": "Alcançou 100 pontos no ranking",
        "icone": "⭐",
        "pontos_bonus": 20
    },
    "maratonista": {
        "nome": "Maratonista",
        "descricao": "Completou uma maratona (42KM)",
        "icone": "🎯",
        "pontos_bonus": 15
    },
    "consistente": {
        "nome": "Consistente",
        "descricao": "Completou corridas em 6 meses diferentes",
        "icone": "📅",
        "pontos_bonus": 10
    }
}
