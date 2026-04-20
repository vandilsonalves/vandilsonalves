# Helper Functions and Services
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Garantir que .env é carregado ANTES de usar variáveis
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "sua-chave-secreta-super-segura-aqui-123456")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
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


def calcular_pontos_povao(distancia: str) -> int:
    """Calcula pontos para a modalidade Galera
    
    Regras:
    - 5km até 9km: 5 pontos
    - 10km até 20km: 7 pontos
    - 21km ou mais: 9 pontos
    """
    # Converter distância para número
    dist_str = distancia.upper().replace('KM', '').replace('K', '').strip()
    
    try:
        dist_num = float(dist_str)
    except ValueError:
        # Tentar extrair número da string
        if '5' in distancia:
            dist_num = 5
        elif '10' in distancia:
            dist_num = 10
        elif '21' in distancia or 'MEIA' in distancia.upper():
            dist_num = 21
        elif '42' in distancia or 'MARATONA' in distancia.upper():
            dist_num = 42
        else:
            dist_num = 5  # Default
    
    # Calcular pontos por faixa de distância
    if dist_num >= 21:
        return 9
    elif dist_num >= 10:
        return 7
    elif dist_num >= 5:
        return 5
    else:
        return 0


def extrair_distancia_km(distancia: str) -> float:
    """Extrai o valor numérico da distância em KM"""
    dist_str = distancia.upper().replace('KM', '').replace('K', '').strip()
    
    try:
        return float(dist_str)
    except ValueError:
        if '5' in distancia:
            return 5.0
        elif '10' in distancia:
            return 10.0
        elif '21' in distancia or 'MEIA' in distancia.upper():
            return 21.0
        elif '42' in distancia or 'MARATONA' in distancia.upper():
            return 42.0
        else:
            return 5.0

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
    "12_resultados": {
        "nome": "Atleta Bronze",
        "descricao": "Lançou 12 resultados no ranking",
        "icone": "🥉",
        "pontos_bonus": 12,
        "cor": "#CD7F32",
        "nivel": 1
    },
    "20_resultados": {
        "nome": "Atleta Prata",
        "descricao": "Lançou 20 resultados no ranking",
        "icone": "🥈",
        "pontos_bonus": 20,
        "cor": "#C0C0C0",
        "nivel": 2
    },
    "30_resultados": {
        "nome": "Atleta Ouro",
        "descricao": "Lançou 30 resultados no ranking",
        "icone": "🥇",
        "pontos_bonus": 30,
        "cor": "#FFD700",
        "nivel": 3
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



# ========== RANKING RUN INSIDE - SCORING ENGINE ==========

def normalize_score(value: float, min_val: float = 0, max_val: float = 10) -> float:
    """Normaliza um valor entre min_val e max_val"""
    return max(min_val, min(value, max_val))


def calcular_nota_bio(desc: bool, keywords: bool, cta: bool, link: bool, clareza: str) -> float:
    """
    Calcula nota da bio (0-10)
    Desc*1.5 + Keywords*3 + CTA*2 + Link*1.5 + Clareza (baseado em string)
    """
    # Mapear clareza string para pontuação
    clareza_pontos = {
        "excelente": 2.0,
        "boa": 1.5,
        "regular": 1.0,
        "ruim": 0.0
    }
    clareza_score = clareza_pontos.get(clareza.lower() if isinstance(clareza, str) else "boa", 1.0)
    
    score = (
        (1.5 if desc else 0) +
        (3.0 if keywords else 0) +
        (2.0 if cta else 0) +
        (1.5 if link else 0) +
        clareza_score
    )
    return normalize_score(score)


def calcular_nota_frequencia(posts_por_semana: float, dias_ultimo_post: int) -> float:
    """
    Calcula nota de frequência (0-10)
    Base: (posts_por_semana / 5) * 10
    Penalização: -2 se dias_ultimo_post > 14
    """
    nota = min((posts_por_semana / 5) * 10, 10)
    
    if dias_ultimo_post > 14:
        nota -= 2
    
    return normalize_score(nota)


def calcular_nota_engajamento(media_likes: float, media_comentarios: float, 
                               media_views_reels: float, seguidores: int) -> tuple:
    """
    Calcula nota de engajamento e retorna (nota, ER_post, ER_reels)
    ER_Post = ((Likes + Comentarios) / Seguidores) * 100
    ER_Reels = (Views / Seguidores) * 100
    ER_Final = (ER_Post * 0.6) + (ER_Reels * 0.4)
    Nota = (ER_Final / 4) * 10
    """
    if seguidores == 0:
        return (0, 0, 0)
    
    er_post = ((media_likes + media_comentarios) / seguidores) * 100
    er_reels = (media_views_reels / seguidores) * 100 if media_views_reels > 0 else er_post * 0.8
    er_final = (er_post * 0.6) + (er_reels * 0.4)
    
    nota = (er_final / 4) * 10
    return (normalize_score(nota), round(er_post, 2), round(er_reels, 2))


def calcular_nota_crescimento(crescimento_percentual: float) -> float:
    """
    Calcula nota de crescimento (0-10)
    Base: (crescimento_percentual / 10) * 10
    Penalização: -3 se crescimento > 15% em período curto (suspeito)
    """
    nota = (crescimento_percentual / 10) * 10
    
    # Penalizar crescimento muito rápido (suspeito de compra de seguidores)
    if crescimento_percentual > 15:
        nota -= 3
    
    return normalize_score(nota)


def calcular_nota_consistencia(desvio_intervalo: float, desvio_engajamento: float) -> float:
    """
    Calcula nota de consistência (0-10)
    Nota = 10 - ((desvio_intervalo / 7) * 6) - (desvio_engajamento / 5)
    """
    nota = 10 - ((desvio_intervalo / 7) * 6) - (desvio_engajamento / 5)
    return normalize_score(nota)


def calcular_nota_padroes(picos_anormais: int, comentarios_repetitivos: int, 
                          horarios_artificiais: int, total_posts: int) -> tuple:
    """
    Calcula nota de padrões anti-fake (0-10)
    Indice_Anomalia = (picos + repetitivos + artificiais) / total_posts
    Nota = 10 - (Indice_Anomalia * 10)
    """
    if total_posts == 0:
        return (10, 0)
    
    total_anomalias = picos_anormais + comentarios_repetitivos + horarios_artificiais
    indice_anomalia = total_anomalias / total_posts
    
    nota = 10 - (indice_anomalia * 10)
    return (normalize_score(nota), round(indice_anomalia, 4))


def calcular_nota_reels(media_views_reels: float, seguidores: int) -> float:
    """
    Calcula nota de alcance de Reels (0-10)
    Base: (ER_Reels / 4) * 10
    """
    if seguidores == 0:
        return 0
    
    er_reels = (media_views_reels / seguidores) * 100
    nota = (er_reels / 4) * 10
    return normalize_score(nota)


def calcular_nota_formatos(percentual_reels: float, percentual_carrossel: float, 
                            percentual_foto: float, er_medio: float) -> float:
    """
    Calcula nota de diversidade de formatos (0-10)
    Score = (ER por formato) / 3
    Nota = (Score / 4) * 10
    """
    # Simular ER por formato com base na distribuição
    er_reels = er_medio * (percentual_reels / 100) * 1.2  # Reels geralmente tem mais alcance
    er_carrossel = er_medio * (percentual_carrossel / 100) * 1.1
    er_foto = er_medio * (percentual_foto / 100) * 0.9
    
    score_formatos = (er_reels + er_carrossel + er_foto) / 3
    nota = (score_formatos / 4) * 10
    return normalize_score(nota)


def calcular_score_final(notas: dict) -> float:
    """
    Calcula score final (0-100) com ponderação:
    - Engajamento: 30%
    - Crescimento: 15%
    - Consistência: 15%
    - Padrões: 15%
    - Alcance Reels: 10%
    - Frequência: 5%
    - Bio: 5%
    - Formatos: 5%
    """
    score = (
        (notas['engajamento'] * 0.30) +
        (notas['crescimento'] * 0.15) +
        (notas['consistencia'] * 0.15) +
        (notas['padroes'] * 0.15) +
        (notas['reels'] * 0.10) +
        (notas['frequencia'] * 0.05) +
        (notas['bio'] * 0.05) +
        (notas['formatos'] * 0.05)
    )
    return round(score * 10, 1)


def classificar_influenciador(score: float) -> str:
    """
    Classifica o influenciador com base no score (0-100)
    """
    if score >= 95:
        return "Elite Platinum"
    elif score >= 90:
        return "Elite Gold"
    elif score >= 80:
        return "Premium"
    elif score >= 70:
        return "Profissional"
    elif score >= 60:
        return "Regular"
    else:
        return "Alto Risco"


def gerar_recomendacoes(notas: dict, dados: dict) -> list:
    """
    Gera recomendações personalizadas baseadas nas notas
    """
    recomendacoes = []
    
    if notas['frequencia'] < 6:
        recomendacoes.append("Aumente a frequência de posts para pelo menos 3-5 por semana")
    
    if notas['engajamento'] < 6:
        recomendacoes.append("Melhore o engajamento com CTAs nos posts e interação com seguidores")
    
    if notas['consistencia'] < 6:
        recomendacoes.append("Mantenha uma regularidade maior nos horários e intervalos de postagem")
    
    if notas['padroes'] < 7:
        recomendacoes.append("Atenção: padrões suspeitos detectados. Evite práticas de automação")
    
    if notas['bio'] < 7:
        recomendacoes.append("Otimize sua bio com CTA claro, link e palavras-chave do nicho")
    
    if notas['reels'] < 6:
        recomendacoes.append("Invista mais em Reels - formato com maior alcance orgânico")
    
    if dados.get('crescimento_30_dias', 0) < 2:
        recomendacoes.append("Trabalhe estratégias para aumentar o crescimento orgânico")
    
    if not recomendacoes:
        recomendacoes.append("Excelente perfil! Continue mantendo a qualidade e consistência")
    
    return recomendacoes


# Médias de referência por nicho (para comparativo)
MEDIAS_NICHO = {
    "corrida": {
        "engagement_rate": 3.5,
        "crescimento_medio": 5.0,
        "posts_semana": 4.0
    },
    "fitness": {
        "engagement_rate": 4.0,
        "crescimento_medio": 6.0,
        "posts_semana": 5.0
    },
    "esportivo": {
        "engagement_rate": 3.8,
        "crescimento_medio": 5.5,
        "posts_semana": 4.5
    }
}
