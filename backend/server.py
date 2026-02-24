from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ==================== MODELS ====================

class Usuario(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    equipe: str
    cidade: str
    estado: str  # UF (SP, RJ, PR, etc)
    foto_url: str = ""
    
class UsuarioCreate(BaseModel):
    nome: str
    equipe: str
    cidade: str
    estado: str

class Resultado(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    usuario_id: str
    ano: int
    pontos: int
    aprovado: bool = True

class RankingAnual(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    usuario_id: str
    ano: int
    pontos_total: int
    total_corridas: int
    estado: str
    ranking_nacional: int = 0
    ranking_estadual: int = 0

class RankingResponse(BaseModel):
    colocacao: int
    uf: str
    foto_url: str
    nome: str
    cidade: str
    equipe: str
    total_corridas: int
    pontos: int
    is_elite: bool  # True se pontos >= 100


# ==================== HELPER FUNCTIONS ====================

def gerar_foto_url(nome: str) -> str:
    """Gera URL de avatar com iniciais usando UI Avatars"""
    nome_encoded = nome.replace(' ', '+')
    return f"https://ui-avatars.com/api/?name={nome_encoded}&size=128&background=random&bold=true"

async def calcular_ranking():
    """Calcula o ranking anual agregando resultados aprovados"""
    ano_atual = 2025
    
    # Limpar ranking antigo
    await db.ranking_anual.delete_many({"ano": ano_atual})
    
    # Agregação: somar pontos e contar corridas por usuário
    pipeline = [
        {"$match": {"ano": ano_atual, "aprovado": True}},
        {"$group": {
            "_id": "$usuario_id",
            "pontos_total": {"$sum": "$pontos"},
            "total_corridas": {"$sum": 1}
        }}
    ]
    
    agregados = await db.resultados.aggregate(pipeline).to_list(None)
    
    # Criar documentos de ranking
    ranking_docs = []
    for agg in agregados:
        usuario = await db.usuarios.find_one({"id": agg["_id"]}, {"_id": 0})
        if usuario:
            ranking_docs.append({
                "usuario_id": agg["_id"],
                "ano": ano_atual,
                "pontos_total": agg["pontos_total"],
                "total_corridas": agg["total_corridas"],
                "estado": usuario["estado"]
            })
    
    # Ordenar por pontos (nacional)
    ranking_docs.sort(key=lambda x: x["pontos_total"], reverse=True)
    
    # Atribuir ranking nacional
    for idx, doc in enumerate(ranking_docs, start=1):
        doc["ranking_nacional"] = idx
    
    # Calcular ranking estadual por UF
    estados = set(doc["estado"] for doc in ranking_docs)
    for uf in estados:
        docs_uf = [d for d in ranking_docs if d["estado"] == uf]
        docs_uf.sort(key=lambda x: x["pontos_total"], reverse=True)
        for idx, doc in enumerate(docs_uf, start=1):
            doc["ranking_estadual"] = idx
    
    # Inserir no banco
    if ranking_docs:
        await db.ranking_anual.insert_many(ranking_docs)
    
    return len(ranking_docs)


# ==================== ENDPOINTS ====================

@api_router.get("/")
async def root():
    return {"message": "Ranking Run Pro API"}

@api_router.get("/ranking/nacional", response_model=List[RankingResponse])
async def get_ranking_nacional(ano: int = Query(2025)):
    """Retorna o ranking nacional ordenado por pontos"""
    
    # Buscar ranking anual ordenado
    ranking_list = await db.ranking_anual.find(
        {"ano": ano},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    if not ranking_list:
        return []
    
    # Enriquecer com dados do usuário
    response = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            response.append(RankingResponse(
                colocacao=rank["ranking_nacional"],
                uf=rank["estado"],
                foto_url=usuario["foto_url"],
                nome=usuario["nome"],
                cidade=f"{usuario['cidade']}/{usuario['estado']}",
                equipe=usuario["equipe"],
                total_corridas=rank["total_corridas"],
                pontos=rank["pontos_total"],
                is_elite=(rank["pontos_total"] >= 100)
            ))
    
    return response

@api_router.get("/ranking/estadual/{uf}", response_model=List[RankingResponse])
async def get_ranking_estadual(uf: str, ano: int = Query(2025)):
    """Retorna o ranking estadual filtrado por UF"""
    
    uf = uf.upper()
    
    # Buscar ranking do estado ordenado
    ranking_list = await db.ranking_anual.find(
        {"ano": ano, "estado": uf},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    if not ranking_list:
        return []
    
    # Enriquecer com dados do usuário
    response = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            response.append(RankingResponse(
                colocacao=rank["ranking_estadual"],
                uf=rank["estado"],
                foto_url=usuario["foto_url"],
                nome=usuario["nome"],
                cidade=f"{usuario['cidade']}/{usuario['estado']}",
                equipe=usuario["equipe"],
                total_corridas=rank["total_corridas"],
                pontos=rank["pontos_total"],
                is_elite=(rank["pontos_total"] >= 100)
            ))
    
    return response

@api_router.get("/ranking/estados")
async def get_estados_disponiveis(ano: int = Query(2025)):
    """Retorna lista de estados com atletas no ranking"""
    
    pipeline = [
        {"$match": {"ano": ano}},
        {"$group": {"_id": "$estado"}},
        {"$sort": {"_id": 1}}
    ]
    
    estados = await db.ranking_anual.aggregate(pipeline).to_list(None)
    return {"estados": [e["_id"] for e in estados]}

@api_router.post("/ranking/popular")
async def popular_dados_teste():
    """Popula o banco com dados de teste realistas"""
    
    # Limpar dados existentes
    await db.usuarios.delete_many({})
    await db.resultados.delete_many({})
    await db.ranking_anual.delete_many({})
    
    # Dados realistas de atletas brasileiros
    atletas_data = [
        # São Paulo (SP) - 15 atletas
        {"nome": "Fernando Vasque", "equipe": "FV Running", "cidade": "Colombo", "estado": "PR", "pontos": 125, "corridas": 25},
        {"nome": "Paulo de Paula Oly", "equipe": "Sem equipe", "cidade": "São Paulo", "estado": "SP", "pontos": 100, "corridas": 40},
        {"nome": "Anderson Teles Da Silva", "equipe": "ATRunners", "cidade": "São Paulo", "estado": "SP", "pontos": 80, "corridas": 35},
        {"nome": "Carlos Eduardo Santos", "equipe": "SP Runners", "cidade": "Campinas", "estado": "SP", "pontos": 118, "corridas": 28},
        {"nome": "Marina Silva Costa", "equipe": "Corredoras SP", "cidade": "São Paulo", "estado": "SP", "pontos": 95, "corridas": 30},
        {"nome": "Roberto Mendes", "equipe": "Fast Runners", "cidade": "Santos", "estado": "SP", "pontos": 88, "corridas": 22},
        {"nome": "Julia Almeida", "equipe": "SP Running Team", "cidade": "Ribeirão Preto", "estado": "SP", "pontos": 102, "corridas": 33},
        {"nome": "Diego Oliveira", "equipe": "Paulista Runners", "cidade": "Sorocaba", "estado": "SP", "pontos": 76, "corridas": 24},
        {"nome": "Fernanda Lima", "equipe": "Run SP", "cidade": "São José dos Campos", "estado": "SP", "pontos": 91, "corridas": 29},
        {"nome": "Ricardo Ferreira", "equipe": "SP Runners", "cidade": "Guarulhos", "estado": "SP", "pontos": 83, "corridas": 26},
        {"nome": "Camila Rodrigues", "equipe": "Fast Team", "cidade": "Campinas", "estado": "SP", "pontos": 97, "corridas": 31},
        {"nome": "Thiago Martins", "equipe": "SP Running Club", "cidade": "São Paulo", "estado": "SP", "pontos": 71, "corridas": 21},
        {"nome": "Beatriz Souza", "equipe": "Corredoras SP", "cidade": "Santos", "estado": "SP", "pontos": 86, "corridas": 27},
        {"nome": "Lucas Pereira", "equipe": "Paulista Team", "cidade": "São Paulo", "estado": "SP", "pontos": 79, "corridas": 25},
        {"nome": "Amanda Costa", "equipe": "SP Runners", "cidade": "Campinas", "estado": "SP", "pontos": 93, "corridas": 32},
        
        # Rio de Janeiro (RJ) - 12 atletas
        {"nome": "Fábio Sanches", "equipe": "Sanches Running", "cidade": "Magé", "estado": "RJ", "pontos": 98, "corridas": 30},
        {"nome": "Mariana Santos", "equipe": "Carioca Runners", "cidade": "Rio de Janeiro", "estado": "RJ", "pontos": 110, "corridas": 34},
        {"nome": "Bruno Costa", "equipe": "RJ Running Team", "cidade": "Niterói", "estado": "RJ", "pontos": 87, "corridas": 28},
        {"nome": "Juliana Ferreira", "equipe": "Carioca Runners", "cidade": "Rio de Janeiro", "estado": "RJ", "pontos": 94, "corridas": 29},
        {"nome": "André Luiz", "equipe": "RJ Runners", "cidade": "Duque de Caxias", "estado": "RJ", "pontos": 81, "corridas": 25},
        {"nome": "Patricia Oliveira", "equipe": "Run Rio", "cidade": "Niterói", "estado": "RJ", "pontos": 89, "corridas": 27},
        {"nome": "Rodrigo Silva", "equipe": "Carioca Team", "cidade": "Rio de Janeiro", "estado": "RJ", "pontos": 105, "corridas": 35},
        {"nome": "Carla Mendes", "equipe": "RJ Running", "cidade": "Petrópolis", "estado": "RJ", "pontos": 78, "corridas": 24},
        {"nome": "Felipe Santos", "equipe": "Carioca Runners", "cidade": "Rio de Janeiro", "estado": "RJ", "pontos": 92, "corridas": 30},
        {"nome": "Vanessa Lima", "equipe": "Run Rio", "cidade": "Niterói", "estado": "RJ", "pontos": 85, "corridas": 26},
        {"nome": "Gabriel Rocha", "equipe": "RJ Runners", "cidade": "Rio de Janeiro", "estado": "RJ", "pontos": 73, "corridas": 22},
        {"nome": "Tatiana Costa", "equipe": "Carioca Team", "cidade": "Nova Iguaçu", "estado": "RJ", "pontos": 96, "corridas": 31},
        
        # Paraná (PR) - 10 atletas
        {"nome": "Kaio Rocha Ferreira", "equipe": "Emerson PeriniID", "cidade": "Cuiabá", "estado": "MT", "pontos": 40, "corridas": 35},
        {"nome": "Marcelo Souza", "equipe": "Paraná Runners", "cidade": "Curitiba", "estado": "PR", "pontos": 108, "corridas": 32},
        {"nome": "Larissa Alves", "equipe": "PR Running", "cidade": "Londrina", "estado": "PR", "pontos": 90, "corridas": 28},
        {"nome": "Rafael Dias", "equipe": "Curitiba Runners", "cidade": "Curitiba", "estado": "PR", "pontos": 82, "corridas": 25},
        {"nome": "Bianca Lima", "equipe": "PR Team", "cidade": "Maringá", "estado": "PR", "pontos": 77, "corridas": 23},
        {"nome": "Gustavo Martins", "equipe": "Paraná Running", "cidade": "Ponta Grossa", "estado": "PR", "pontos": 84, "corridas": 26},
        {"nome": "Aline Santos", "equipe": "PR Runners", "cidade": "Curitiba", "estado": "PR", "pontos": 91, "corridas": 29},
        {"nome": "Eduardo Costa", "equipe": "Curitiba Team", "cidade": "Curitiba", "estado": "PR", "pontos": 75, "corridas": 24},
        {"nome": "Renata Silva", "equipe": "PR Running", "cidade": "Londrina", "estado": "PR", "pontos": 88, "corridas": 27},
        {"nome": "Daniel Oliveira", "equipe": "Paraná Runners", "cidade": "Cascavel", "estado": "PR", "pontos": 70, "corridas": 21},
        
        # Bahia (BA) - 8 atletas
        {"nome": "Isabela Ferreira", "equipe": "Bahia Runners", "cidade": "Salvador", "estado": "BA", "pontos": 115, "corridas": 36},
        {"nome": "Leonardo Santos", "equipe": "BA Running", "cidade": "Salvador", "estado": "BA", "pontos": 99, "corridas": 31},
        {"nome": "Carolina Souza", "equipe": "Salvador Runners", "cidade": "Salvador", "estado": "BA", "pontos": 87, "corridas": 28},
        {"nome": "Vinicius Lima", "equipe": "Bahia Team", "cidade": "Feira de Santana", "estado": "BA", "pontos": 80, "corridas": 25},
        {"nome": "Paula Rodrigues", "equipe": "BA Runners", "cidade": "Vitória da Conquista", "estado": "BA", "pontos": 74, "corridas": 23},
        {"nome": "Henrique Costa", "equipe": "Salvador Running", "cidade": "Salvador", "estado": "BA", "pontos": 92, "corridas": 29},
        {"nome": "Débora Alves", "equipe": "Bahia Runners", "cidade": "Ilhéus", "estado": "BA", "pontos": 85, "corridas": 26},
        {"nome": "Fábio Mendes", "equipe": "BA Team", "cidade": "Salvador", "estado": "BA", "pontos": 78, "corridas": 24},
        
        # Ceará (CE) - 8 atletas
        {"nome": "André Sales", "equipe": "Força Falcão de Atletismo", "cidade": "Fortaleza", "estado": "CE", "pontos": 76, "corridas": 20},
        {"nome": "Luciana Oliveira", "equipe": "Ceará Runners", "cidade": "Fortaleza", "estado": "CE", "pontos": 103, "corridas": 33},
        {"nome": "Marcos Silva", "equipe": "CE Running", "cidade": "Juazeiro do Norte", "estado": "CE", "pontos": 89, "corridas": 27},
        {"nome": "Adriana Costa", "equipe": "Fortaleza Runners", "cidade": "Fortaleza", "estado": "CE", "pontos": 81, "corridas": 25},
        {"nome": "Pedro Henrique", "equipe": "Ceará Team", "cidade": "Sobral", "estado": "CE", "pontos": 72, "corridas": 22},
        {"nome": "Natália Santos", "equipe": "CE Runners", "cidade": "Fortaleza", "estado": "CE", "pontos": 94, "corridas": 30},
        {"nome": "Guilherme Lima", "equipe": "Fortaleza Running", "cidade": "Fortaleza", "estado": "CE", "pontos": 77, "corridas": 24},
        {"nome": "Letícia Alves", "equipe": "Ceará Runners", "cidade": "Caucaia", "estado": "CE", "pontos": 86, "corridas": 26},
        
        # Minas Gerais (MG) - 8 atletas
        {"nome": "Alexandre Ribeiro", "equipe": "MG Runners", "cidade": "Belo Horizonte", "estado": "MG", "pontos": 112, "corridas": 35},
        {"nome": "Priscila Martins", "equipe": "BH Running", "cidade": "Belo Horizonte", "estado": "MG", "pontos": 98, "corridas": 31},
        {"nome": "João Pedro", "equipe": "Minas Team", "cidade": "Uberlândia", "estado": "MG", "pontos": 83, "corridas": 26},
        {"nome": "Simone Costa", "equipe": "MG Running", "cidade": "Contagem", "estado": "MG", "pontos": 79, "corridas": 24},
        {"nome": "Mateus Oliveira", "equipe": "BH Runners", "cidade": "Belo Horizonte", "estado": "MG", "pontos": 91, "corridas": 28},
        {"nome": "Raquel Santos", "equipe": "Minas Runners", "cidade": "Juiz de Fora", "estado": "MG", "pontos": 87, "corridas": 27},
        {"nome": "Bruno Ferreira", "equipe": "MG Team", "cidade": "Betim", "estado": "MG", "pontos": 74, "corridas": 23},
        {"nome": "Cristina Silva", "equipe": "BH Running", "cidade": "Belo Horizonte", "estado": "MG", "pontos": 95, "corridas": 30},
        
        # Rio Grande do Sul (RS) - 7 atletas
        {"nome": "Rodrigo Machado", "equipe": "Gaúcho Runners", "cidade": "Porto Alegre", "estado": "RS", "pontos": 107, "corridas": 34},
        {"nome": "Cláudia Pereira", "equipe": "RS Running", "cidade": "Porto Alegre", "estado": "RS", "pontos": 93, "corridas": 29},
        {"nome": "Luiz Fernando", "equipe": "POA Runners", "cidade": "Caxias do Sul", "estado": "RS", "pontos": 85, "corridas": 26},
        {"nome": "Sabrina Costa", "equipe": "Gaúcho Team", "cidade": "Porto Alegre", "estado": "RS", "pontos": 78, "corridas": 24},
        {"nome": "Anderson Silva", "equipe": "RS Runners", "cidade": "Canoas", "estado": "RS", "pontos": 82, "corridas": 25},
        {"nome": "Mônica Alves", "equipe": "POA Running", "cidade": "Porto Alegre", "estado": "RS", "pontos": 89, "corridas": 28},
        {"nome": "Tiago Souza", "equipe": "Gaúcho Runners", "cidade": "Pelotas", "estado": "RS", "pontos": 71, "corridas": 22},
        
        # Santa Catarina (SC) - 7 atletas
        {"nome": "Edson Luiz Brasiliano de Lima", "equipe": "ZULURun ASSESSORIA E CORRIDA DE RUA", "cidade": "Xanxerê", "estado": "SC", "pontos": 74, "corridas": 40},
        {"nome": "Cristiano Nunes", "equipe": "SC Runners", "cidade": "Florianópolis", "estado": "SC", "pontos": 109, "corridas": 33},
        {"nome": "Jéssica Oliveira", "equipe": "Floripa Running", "cidade": "Florianópolis", "estado": "SC", "pontos": 96, "corridas": 30},
        {"nome": "Márcio Santos", "equipe": "Catarinense Team", "cidade": "Joinville", "estado": "SC", "pontos": 84, "corridas": 26},
        {"nome": "Bruna Lima", "equipe": "SC Running", "cidade": "Blumenau", "estado": "SC", "pontos": 79, "corridas": 24},
        {"nome": "Paulo Roberto", "equipe": "Floripa Runners", "cidade": "Florianópolis", "estado": "SC", "pontos": 88, "corridas": 27},
        {"nome": "Andreia Costa", "equipe": "SC Team", "cidade": "Chapecó", "estado": "SC", "pontos": 75, "corridas": 23},
        
        # Outros estados - 5 atletas
        {"nome": "Samuel Souza do Nascimento", "equipe": "CAPB Paraíba", "cidade": "Limeiro", "estado": "PB", "pontos": 125, "corridas": 30},
        {"nome": "Ricardo Gomes", "equipe": "ES Runners", "cidade": "Vitória", "estado": "ES", "pontos": 101, "corridas": 32},
        {"nome": "Ana Paula Silva", "equipe": "Goiás Running", "cidade": "Goiânia", "estado": "GO", "pontos": 86, "corridas": 27},
        {"nome": "Sérgio Mendes", "equipe": "Brasília Runners", "cidade": "Brasília", "estado": "DF", "pontos": 92, "corridas": 29},
        {"nome": "Eliane Santos", "equipe": "Pernambuco Team", "cidade": "Recife", "estado": "PE", "pontos": 77, "corridas": 24},
    ]
    
    # Inserir usuários
    usuarios_inseridos = []
    for atleta in atletas_data:
        usuario = Usuario(
            nome=atleta["nome"],
            equipe=atleta["equipe"],
            cidade=atleta["cidade"],
            estado=atleta["estado"],
            foto_url=gerar_foto_url(atleta["nome"])
        )
        doc = usuario.model_dump()
        await db.usuarios.insert_one(doc)
        usuarios_inseridos.append((usuario.id, atleta["pontos"], atleta["corridas"]))
    
    # Inserir resultados (corridas) para cada usuário
    resultados_inseridos = []
    for usuario_id, pontos_total, num_corridas in usuarios_inseridos:
        # Distribuir pontos entre corridas (entre 3 e 6 pontos por corrida)
        for _ in range(num_corridas):
            pontos_corrida = random.randint(3, 6)
            resultado = Resultado(
                usuario_id=usuario_id,
                ano=2025,
                pontos=pontos_corrida,
                aprovado=True
            )
            doc = resultado.model_dump()
            await db.resultados.insert_one(doc)
            resultados_inseridos.append(resultado.id)
    
    # Calcular ranking
    total_ranking = await calcular_ranking()
    
    return {
        "message": "Dados populados com sucesso!",
        "usuarios": len(usuarios_inseridos),
        "resultados": len(resultados_inseridos),
        "ranking_calculado": total_ranking
    }


# ==================== INCLUDE ROUTER ====================

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
