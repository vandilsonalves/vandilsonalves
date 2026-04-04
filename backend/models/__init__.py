# Backend Models
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List
import uuid
from datetime import datetime, timezone

class Usuario(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    email: str
    password_hash: str = ""
    equipe: str
    cidade: str
    estado: str
    genero: str  # M ou F
    categoria: str  # normal, pcd, cadeirante
    data_nascimento: str  # YYYY-MM-DD
    faixa_etaria: str
    foto_url: str = ""
    role: str = "atleta"  # atleta ou admin
    is_active: bool = True
    facebook_url: str = ""
    instagram_url: str = ""
    telefone: str = ""
    bio: str = ""
    primeira_submissao: bool = False
    # Novos campos
    etnia: str = ""  # Branco, Negro, Indígena, Pardo, Amarelo
    apelido: str = ""
    # Modalidade - profissional_amador ou povao_pace_livre
    modalidade_usuario: str = "profissional_amador"

class UsuarioRegister(BaseModel):
    nome: str
    email: EmailStr
    password: str
    equipe: str
    cidade: str
    estado: str
    genero: str
    categoria: str
    data_nascimento: str
    etnia: str = ""
    apelido: str = ""
    modalidade_usuario: str = "profissional_amador"
    telefone: str = ""
    tipo_corredor: str = ""
    terreno_preferido: str = ""
    is_dono_assessoria: bool = False
    assessoria_data: Optional[dict] = None
    codigo_indicacao: Optional[str] = None

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class PerfilUpdate(BaseModel):
    nome: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    data_nascimento: Optional[str] = None
    equipe: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    telefone: Optional[str] = None
    bio: Optional[str] = None
    # Novos campos
    etnia: Optional[str] = None
    apelido: Optional[str] = None
    whatsapp_link: Optional[str] = None  # Para donos de assessoria
    tipo_corredor: Optional[str] = None
    terreno_preferido: Optional[str] = None

# Mensagem de Aniversário
class MensagemAniversario(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    usuario_id: str
    mensagem: str
    enviada_em: str = Field(default_factory=lambda: datetime.now().isoformat())
    visualizada: bool = False
    data_visualizacao: str = ""
    ano: int = 2026  # Ano do aniversário

class ResultadoPendente(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    usuario_id: str
    nome_competicao: str
    colocacao: int
    cidade_competicao: str
    estado_competicao: str
    data_competicao: str  # YYYY-MM-DD
    link_resultado: str
    tempo: str  # HH:MM:SS
    distancia: str  # 5KM, 10KM, 21KM, 42KM, OUTRA
    foto_podio_url: str = ""
    status: str = "pendente"  # pendente, aprovado, reprovado
    motivo_reprovacao: str = ""
    data_submissao: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    ano: int = 2025

class ResultadoSubmissao(BaseModel):
    nome_competicao: str
    colocacao: int
    cidade_competicao: str
    estado_competicao: str
    data_competicao: str
    link_resultado: str
    tempo: str
    distancia: str

class AprovacaoRequest(BaseModel):
    motivo: Optional[str] = ""

class Corrida(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    usuario_id: str
    nome: str
    colocacao: int
    tempo: str
    pontos: int
    local: str
    distancia: str
    data: str
    ano: int
    # Povão - pontos calculados por distância
    pontos_povao: int = 0
    modalidade: str = "profissional_amador"  # profissional_amador ou povao_pace_livre

class RankingAnual(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    usuario_id: str
    ano: int
    pontos_total: int
    total_corridas: int
    estado: str
    genero: str
    categoria: str
    faixa_etaria: str
    ranking_nacional: int = 0
    ranking_estadual: int = 0
    ranking_categoria: int = 0
    # Modalidade
    modalidade: str = "profissional_amador"

# Ranking Povão
class RankingPovao(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    usuario_id: str
    ano: int
    pontos_total: int
    total_corridas: int
    distancia_acumulada: float = 0  # Para desempate
    estado: str
    genero: str
    ranking_geral: int = 0
    ranking_genero: int = 0

class RankingResponse(BaseModel):
    id: str
    colocacao: int
    uf: str
    foto_url: str
    nome: str
    cidade: str
    equipe: str
    faixa_etaria: str
    total_corridas: int
    pontos: int
    is_elite: bool
    is_pendente: bool
    is_premium: bool = False

class AtletaDetalhes(BaseModel):
    id: str
    nome: str
    cidade: str
    estado: str
    genero: str
    categoria: str
    faixa_etaria: str
    foto_url: str
    equipe: str
    pontos_carreira: int
    total_corridas: int
    melhor_colocacao: int
    is_pendente: bool
    # Novos campos
    bio: str = ""
    apelido: str = ""
    etnia: str = ""
    instagram_url: str = ""
    facebook_url: str = ""
    modalidade_usuario: str = "profissional_amador"
    # Campos para dono de assessoria
    role: str = "atleta"
    is_dono_assessoria: bool = False
    assessoria_nome: Optional[str] = None

class CorridaResponse(BaseModel):
    id: str
    nome: str
    colocacao: int
    tempo: str
    pontos: int
    local: str
    distancia: str
    data: str

class EvolucaoMensal(BaseModel):
    mes: str
    pontos: int
    corridas: int

# Notificações
class Notificacao(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    usuario_id: str
    tipo: str  # reprovacao, aprovacao, conquista, etc
    titulo: str
    mensagem: str
    lida: bool = False
    data_criacao: str = Field(default_factory=lambda: datetime.now().isoformat())
    dados_extras: dict = {}

# Conquistas
class Conquista(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str  # primeiro_lugar, 10_corridas, elite, etc
    nome: str
    descricao: str
    icone: str
    pontos_bonus: int = 0

class ConquistaAtleta(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    usuario_id: str
    conquista_codigo: str
    data_conquista: str = Field(default_factory=lambda: datetime.now().isoformat())



# ========== RANKING RUN INSIDE - INSTAGRAM ANALYTICS ==========

class InstagramProfileInput(BaseModel):
    """Dados de entrada para análise de perfil Instagram"""
    model_config = ConfigDict(extra="ignore")
    
    username: str
    nome_completo: Optional[str] = None
    nicho: str = "corrida"  # corrida, fitness, esportivo
    
    # Métricas básicas do perfil
    seguidores: int
    seguindo: int
    total_posts: int
    
    # Métricas de engajamento (últimos 18 posts)
    media_likes: float
    media_comentarios: float
    media_views_reels: float = 0
    
    # Frequência e crescimento
    posts_por_semana: float
    dias_ultimo_post: int = 0
    crescimento_30_dias: float = 0  # percentual
    
    # Consistência (desvios padrão)
    desvio_intervalo_posts: float = 0  # dias
    desvio_engajamento: float = 0
    
    # Análise de Bio (campos booleanos para check simples)
    bio_descricao: bool = True  # Perfil tem descrição na bio?
    bio_keywords: bool = True  # Bio tem palavras-chave do nicho?
    bio_cta: bool = False  # Bio tem call-to-action?
    bio_link: bool = True  # Bio tem link externo?
    bio_clareza: str = "boa"  # Qualidade: "excelente", "boa", "regular", "ruim"
    
    # Distribuição de formatos (soma = 100%)
    percentual_reels: float = 50
    percentual_carrossel: float = 30
    percentual_foto: float = 20
    
    # Indicadores anti-fake
    picos_anormais: int = 0  # número de picos suspeitos
    comentarios_repetitivos: int = 0  # comentários genéricos/bots
    horarios_artificiais: int = 0  # posts em horários não naturais


class InstagramAnalysis(BaseModel):
    """Resultado completo da análise"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Dados do perfil
    username: str
    nome_completo: Optional[str] = None
    nicho: str
    seguidores: int
    seguindo: int
    total_posts: int
    
    # Notas individuais (0-10)
    nota_bio: float
    nota_frequencia: float
    nota_engajamento: float
    nota_crescimento: float
    nota_consistencia: float
    nota_padroes: float  # anti-fake
    nota_reels: float
    nota_formatos: float
    
    # Score final (0-100)
    score_final: float
    classificacao: str  # Elite Platinum, Elite Gold, Premium, etc.
    
    # Métricas calculadas
    engagement_rate: float
    engagement_rate_reels: float
    indice_anomalia: float
    
    # Comparativo com média do nicho
    comparativo_engajamento: float  # percentual acima/abaixo da média
    comparativo_crescimento: float
    
    # Metadados
    data_analise: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    analisado_por: str  # ID do admin


class InstagramAnalysisResponse(BaseModel):
    """Resposta da API com análise"""
    model_config = ConfigDict(extra="ignore")
    
    analysis: InstagramAnalysis
    graficos_data: dict  # Dados estruturados para gráficos
    recomendacoes: List[str]
