# /app/backend/services/moderacao_service.py
# Sistema de Moderação de Conteúdo - Ranking Run

import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from enum import Enum

class NivelInfracao(Enum):
    LEVE = "leve"      # Aviso
    MEDIO = "medio"    # Ocultar comentário
    GRAVE = "grave"    # Bloquear usuário temporariamente


# =============================================================================
# LISTA DE PALAVRAS E FRASES PARA MODERAÇÃO
# =============================================================================

# 🚫 1. SPAM, FRAUDE E PROMESSAS ENGANOSAS (GRAVE)
SPAM_FRAUDE = [
    "ganhe dinheiro rápido", "ganhe dinheiro rapido", "renda extra garantida",
    "fique rico", "dinheiro fácil", "dinheiro facil", "crédito fácil", "credito facil",
    "lucro imediato", "método secreto", "metodo secreto", "fórmula mágica", "formula magica",
    "resultado garantido", "trabalhe de casa e ganhe", "renda automática", "renda automatica",
    "investimento sem risco", "dinheiro na hora", "enriquecimento rápido", "enriquecimento rapido",
    "esquema milionário", "esquema milionario", "ganhe dinheiro", "oportunidade única",
    "clique aqui e ganhe", "método infalível", "metodo infalivel"
]

# ⚠️ 2. AMEAÇAS E VIOLÊNCIA (GRAVE)
AMEACAS_VIOLENCIA = [
    "vou te matar", "te arrebento", "vou te pegar", "vou acabar com você",
    "vou acabar com voce", "vou te quebrar", "te destruir", "vou te caçar",
    "vou te cacar", "vou te espancar", "vou te socar", "bater em você",
    "bater em voce", "vou te achar", "sei onde você mora", "sei onde voce mora"
]

# Palavras de violência isoladas (precisam de contexto)
VIOLENCIA_CONTEXTO = [
    "matar", "ameaça", "ameaca", "agressão", "agressao", "violência", "violencia",
    "brutal", "espancar", "socar"
]

# 🚫 3. OFENSAS DIRETAS / XINGAMENTOS
OFENSAS_GRAVES = [
    "filho da puta", "fdp", "arrombado", "desgraçado", "desgraçada",
    "desgracado", "desgracada", "vagabundo", "vagabunda", "escroto", "escrot"
]

OFENSAS_MEDIAS = [
    "idiota", "burro", "burra", "imbecil", "otário", "otario", "otária", "otaria",
    "trouxa", "lixo", "inútil", "inutil", "retardado", "retardada", "fracassado",
    "fracassada", "merda", "porcaria", "safado", "safada"
]

# 🚫 4. CONTEÚDO SEXUAL / VULGARIDADE (GRAVE)
CONTEUDO_SEXUAL = [
    "sexo", "pica", "pau", "meu pau", "buceta", "boceta", "xana", "rola",
    "pica dura", "cú", "cu", "foder", "fudendo", "foda-se", "fodase",
    "gozar", "pornografia", "transar", "punheta", "siririca", "chupa",
    "chupar", "boquete"
]

# ⚠️ 5. DISCRIMINAÇÃO E PRECONCEITO (GRAVE)
RACISMO_XENOFOBIA = [
    "macaco", "volta pro seu país", "volta pro seu pais", "sua raça", "sua raca",
    "imigrante lixo", "estrangeiro lixo", "preto lixo", "branco lixo",
    "nordestino lixo", "baiano lixo"
]

HOMOFOBIA = [
    "viado", "viadinho", "aberração", "aberracao", "traveco", "sapatão", "sapatao",
    "bicha", "bichinha", "gay lixo", "lésbica lixo", "lesbica lixo"
]

MISOGINIA = [
    "mulher não serve", "mulher nao serve", "lugar de mulher", "vadia",
    "puta", "piranha", "galinha"
]

# 🚫 6. HUMILHAÇÃO E BULLYING (MÉDIO/GRAVE)
BULLYING = [
    "ninguém gosta de você", "ninguem gosta de voce", "você não presta",
    "voce nao presta", "você é um lixo", "voce e um lixo", "se mata",
    "some daqui", "desiste da vida", "você é ridículo", "voce e ridiculo",
    "seu fracassado", "seu fracasado", "ninguém te quer", "ninguem te quer",
    "vai se matar"
]

# ⚠️ 7. PALAVRAS SENSÍVEIS (CONTEXTO)
PALAVRAS_SENSIVEIS = [
    "morrer", "dor", "sofrimento", "sangue", "guerra", "morte"
]

# Frases positivas de contexto esportivo que podem usar "matar"
CONTEXTO_ESPORTIVO_POSITIVO = [
    "matar treino", "matei o treino", "matando treino", "matar a prova",
    "matei a prova", "matar corrida", "matei a corrida", "matar no pace",
    "matando no pace", "treino matador"
]


# =============================================================================
# MAPA DE SUBSTITUIÇÃO PARA NORMALIZAÇÃO
# =============================================================================

SUBSTITUICOES = {
    '0': 'o', '1': 'i', '2': 'z', '3': 'e', '4': 'a', '5': 's',
    '6': 'g', '7': 't', '8': 'b', '9': 'g', '@': 'a', '$': 's',
    '*': '', '#': '', '!': 'i', '+': 't', '&': 'e'
}


def normalizar_texto(texto: str) -> str:
    """
    Normaliza o texto para detectar tentativas de burlar o filtro.
    Ex: "p1ca" -> "pica", "b0ceta" -> "boceta"
    """
    texto_normalizado = texto.lower()
    
    # Substituir caracteres especiais por letras
    for char, replacement in SUBSTITUICOES.items():
        texto_normalizado = texto_normalizado.replace(char, replacement)
    
    # Remover caracteres especiais restantes
    texto_normalizado = re.sub(r'[^\w\s]', '', texto_normalizado)
    
    # Remover espaços duplicados
    texto_normalizado = re.sub(r'\s+', ' ', texto_normalizado).strip()
    
    # Remover letras repetidas excessivamente (ex: "idiooota" -> "idiota")
    texto_normalizado = re.sub(r'(.)\1{2,}', r'\1\1', texto_normalizado)
    
    return texto_normalizado


def verificar_contexto_esportivo(texto: str) -> bool:
    """
    Verifica se o texto está em contexto esportivo positivo.
    Ex: "matei o treino" é aceitável, "vou te matar" não é.
    """
    texto_lower = texto.lower()
    
    for frase in CONTEXTO_ESPORTIVO_POSITIVO:
        if frase in texto_lower:
            return True
    
    # Palavras que indicam contexto esportivo
    palavras_esportivas = [
        'treino', 'corrida', 'prova', 'maratona', 'pace', 'km', 'quilômetros',
        'quilometros', 'tempo', 'meta', 'objetivo', 'resultado', 'pódio', 'podio'
    ]
    
    return any(palavra in texto_lower for palavra in palavras_esportivas)


def analisar_conteudo(texto: str) -> Tuple[bool, Optional[str], Optional[NivelInfracao], Optional[str]]:
    """
    Analisa o conteúdo e retorna:
    - bloqueado: bool
    - motivo: str (categoria da infração)
    - nivel: NivelInfracao
    - mensagem: str (feedback para o usuário)
    """
    texto_original = texto
    texto_normalizado = normalizar_texto(texto)
    
    # 1. Verificar SPAM/FRAUDE (GRAVE)
    for frase in SPAM_FRAUDE:
        if frase in texto_normalizado:
            return (True, "spam_fraude", NivelInfracao.GRAVE,
                    "Seu comentário foi bloqueado por conter conteúdo promocional ou spam.")
    
    # 2. Verificar AMEAÇAS (GRAVE)
    for frase in AMEACAS_VIOLENCIA:
        if frase in texto_normalizado:
            return (True, "ameaca_violencia", NivelInfracao.GRAVE,
                    "Seu comentário foi bloqueado por conter ameaças ou incitação à violência.")
    
    # 3. Verificar CONTEÚDO SEXUAL (GRAVE)
    for palavra in CONTEUDO_SEXUAL:
        if palavra in texto_normalizado or palavra in texto_normalizado.replace(' ', ''):
            return (True, "conteudo_sexual", NivelInfracao.GRAVE,
                    "Seu comentário foi bloqueado por conter conteúdo sexual ou vulgar.")
    
    # 4. Verificar DISCRIMINAÇÃO (GRAVE)
    for palavra in RACISMO_XENOFOBIA + HOMOFOBIA + MISOGINIA:
        if palavra in texto_normalizado:
            return (True, "discriminacao", NivelInfracao.GRAVE,
                    "Seu comentário foi bloqueado por conter conteúdo discriminatório.")
    
    # 5. Verificar OFENSAS GRAVES (GRAVE)
    for palavra in OFENSAS_GRAVES:
        if palavra in texto_normalizado:
            return (True, "ofensa_grave", NivelInfracao.GRAVE,
                    "Seu comentário foi bloqueado por conter ofensas graves.")
    
    # 6. Verificar BULLYING (MÉDIO)
    for frase in BULLYING:
        if frase in texto_normalizado:
            return (True, "bullying", NivelInfracao.MEDIO,
                    "Seu comentário foi ocultado por conter conteúdo de bullying ou humilhação.")
    
    # 7. Verificar OFENSAS MÉDIAS (MÉDIO)
    for palavra in OFENSAS_MEDIAS:
        if palavra in texto_normalizado.split():  # Palavra exata, não substring
            return (True, "ofensa_media", NivelInfracao.MEDIO,
                    "Seu comentário contém linguagem ofensiva. Por favor, revise.")
    
    # 8. Verificar VIOLÊNCIA COM CONTEXTO
    for palavra in VIOLENCIA_CONTEXTO:
        if palavra in texto_normalizado:
            # Verificar se está em contexto esportivo
            if not verificar_contexto_esportivo(texto_original):
                return (False, "violencia_contexto", NivelInfracao.LEVE,
                        "Atenção: seu comentário contém palavras sensíveis. Ele será revisado.")
    
    # 9. Verificar PALAVRAS SENSÍVEIS (AVISO)
    for palavra in PALAVRAS_SENSIVEIS:
        if palavra in texto_normalizado.split():
            if not verificar_contexto_esportivo(texto_original):
                # Apenas aviso, não bloqueia
                return (False, "palavra_sensivel", NivelInfracao.LEVE, None)
    
    # Conteúdo aprovado
    return (False, None, None, None)


def calcular_score_respeito(usuario_data: dict) -> int:
    """
    Calcula o score de respeito do atleta (0-100).
    Quanto maior, mais respeitoso é o atleta.
    """
    # Iniciar com 100 pontos
    score = 100
    
    # Subtrair por infrações
    advertencias = usuario_data.get("advertencias_moderacao", 0)
    bloqueios = usuario_data.get("bloqueios_moderacao", 0)
    comentarios_ocultados = usuario_data.get("comentarios_ocultados", 0)
    
    # Penalidades
    score -= advertencias * 5      # -5 por advertência
    score -= comentarios_ocultados * 10  # -10 por comentário ocultado
    score -= bloqueios * 25        # -25 por bloqueio
    
    # Bônus por bom comportamento
    comentarios_positivos = usuario_data.get("comentarios_aprovados", 0)
    tempo_sem_infracao_dias = usuario_data.get("dias_sem_infracao", 0)
    
    # Bônus
    if comentarios_positivos >= 10:
        score += 5
    if comentarios_positivos >= 50:
        score += 10
    if tempo_sem_infracao_dias >= 30:
        score += 5
    if tempo_sem_infracao_dias >= 90:
        score += 10
    
    return max(0, min(100, score))


def verificar_selo_respeitoso(usuario_data: dict) -> bool:
    """
    Verifica se o atleta merece o Selo de Atleta Respeitoso 🏅
    
    Critérios:
    - Mínimo 10 comentários aprovados
    - Zero bloqueios nos últimos 90 dias
    - Score de respeito >= 80
    """
    score = calcular_score_respeito(usuario_data)
    comentarios_aprovados = usuario_data.get("comentarios_aprovados", 0)
    bloqueios_recentes = usuario_data.get("bloqueios_ultimos_90_dias", 0)
    
    return (
        score >= 80 and
        comentarios_aprovados >= 10 and
        bloqueios_recentes == 0
    )


def gerar_feedback_educativo(nivel: NivelInfracao, categoria: str) -> str:
    """
    Gera uma mensagem educativa baseada no tipo de infração.
    """
    mensagens = {
        "spam_fraude": "A comunidade Ranking Run não permite spam ou ofertas enganosas. Mantenha o foco no esporte!",
        "ameaca_violencia": "Ameaças e violência não são toleradas. Lembre-se: somos todos atletas unidos pelo esporte.",
        "conteudo_sexual": "Conteúdo sexual ou vulgar não é permitido. Mantenha a comunidade segura para todos.",
        "discriminacao": "Discriminação de qualquer tipo é inaceitável. Respeite todos os atletas.",
        "ofensa_grave": "Ofensas graves prejudicam o ambiente. Vamos manter o respeito mútuo!",
        "bullying": "Humilhar outros atletas não é aceitável. Apoie seus colegas de corrida!",
        "ofensa_media": "Linguagem ofensiva pode machucar. Que tal reformular de forma mais respeitosa?",
        "violencia_contexto": "Palavras de violência devem ser usadas com cuidado. Contexto esportivo é ok!",
        "palavra_sensivel": "Cuidado com palavras sensíveis. Seu comentário será revisado."
    }
    
    return mensagens.get(categoria, "Seu comentário não segue as diretrizes da comunidade Ranking Run.")


# =============================================================================
# FUNÇÕES DE BANCO DE DADOS
# =============================================================================

async def registrar_infracao(db, usuario_id: str, nivel: NivelInfracao, categoria: str, texto_original: str):
    """
    Registra uma infração no histórico do usuário.
    """
    infracao = {
        "data": datetime.now(timezone.utc).isoformat(),
        "nivel": nivel.value,
        "categoria": categoria,
        "texto": texto_original[:100] + "..." if len(texto_original) > 100 else texto_original
    }
    
    # Atualizar contadores do usuário
    update_fields = {
        f"$push": {"historico_infracoes": infracao}
    }
    
    if nivel == NivelInfracao.LEVE:
        update_fields["$inc"] = {"advertencias_moderacao": 1}
    elif nivel == NivelInfracao.MEDIO:
        update_fields["$inc"] = {"comentarios_ocultados": 1}
    elif nivel == NivelInfracao.GRAVE:
        update_fields["$inc"] = {"bloqueios_moderacao": 1, "bloqueios_ultimos_90_dias": 1}
    
    await db.usuarios.update_one(
        {"id": usuario_id},
        update_fields
    )


async def verificar_usuario_bloqueado(db, usuario_id: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica se o usuário está temporariamente bloqueado de comentar.
    """
    usuario = await db.usuarios.find_one(
        {"id": usuario_id},
        {"_id": 0, "bloqueado_feed_ate": 1, "bloqueios_moderacao": 1}
    )
    
    if not usuario:
        return False, None
    
    bloqueado_ate = usuario.get("bloqueado_feed_ate")
    if bloqueado_ate:
        try:
            data_bloqueio = datetime.fromisoformat(bloqueado_ate.replace('Z', '+00:00'))
            if data_bloqueio > datetime.now(timezone.utc):
                return True, bloqueado_ate
        except:
            pass
    
    return False, None


async def bloquear_usuario_temporariamente(db, usuario_id: str, dias: int = 7):
    """
    Bloqueia o usuário de comentar por X dias.
    """
    data_desbloqueio = datetime.now(timezone.utc) + timedelta(days=dias)
    
    await db.usuarios.update_one(
        {"id": usuario_id},
        {"$set": {"bloqueado_feed_ate": data_desbloqueio.isoformat()}}
    )


async def incrementar_comentarios_aprovados(db, usuario_id: str):
    """
    Incrementa o contador de comentários aprovados do usuário.
    """
    await db.usuarios.update_one(
        {"id": usuario_id},
        {"$inc": {"comentarios_aprovados": 1}}
    )
