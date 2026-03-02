# Backend Models
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List
import uuid
from datetime import datetime

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
    # Novos campos
    etnia: str = ""
    apelido: str = ""
    # Modalidade obrigatória
    modalidade_usuario: str = "profissional_amador"

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
