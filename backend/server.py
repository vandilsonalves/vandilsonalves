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
from datetime import datetime, timezone, date
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
    genero: str  # M ou F
    categoria: str  # normal, pcd, cadeirante
    data_nascimento: str  # YYYY-MM-DD
    faixa_etaria: str  # 18-29, 30-39, 40-49, 50-59, 60+
    foto_url: str = ""
    
class Corrida(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    usuario_id: str
    nome: str
    colocacao: int
    tempo: str  # HH:MM:SS
    pontos: int
    local: str  # Cidade/UF
    distancia: str  # 5KM, 10KM, 21KM, 42KM
    data: str  # YYYY-MM-DD
    ano: int

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
    is_pendente: bool  # True se < 12 corridas

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

class CorridaResponse(BaseModel):
    id: str
    nome: str
    colocacao: int
    tempo: str
    pontos: int
    local: str
    distancia: str
    data: str


# ==================== HELPER FUNCTIONS ====================

def calcular_faixa_etaria(data_nascimento: str) -> str:
    """Calcula faixa etária baseado na data de nascimento"""
    ano_nasc = int(data_nascimento.split('-')[0])
    idade = 2025 - ano_nasc
    
    if idade < 18:
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
    """Gera URL de avatar com iniciais usando UI Avatars"""
    nome_encoded = nome.replace(' ', '+')
    return f"https://ui-avatars.com/api/?name={nome_encoded}&size=128&background=random&bold=true"

def gerar_tempo_corrida(distancia: str, colocacao: int) -> str:
    """Gera tempo realista baseado na distância e colocação"""
    tempos_base = {
        "5KM": (15, 25),    # 15-25 min
        "10KM": (32, 55),   # 32-55 min
        "21KM": (65, 120),  # 1h05-2h00
        "42KM": (140, 240)  # 2h20-4h00
    }
    
    min_tempo, max_tempo = tempos_base.get(distancia, (30, 60))
    
    # Colocações melhores = tempos menores
    fator_colocacao = 1 + (colocacao - 1) * 0.05
    tempo_min = int(min_tempo * fator_colocacao)
    
    minutos_total = random.randint(tempo_min, tempo_min + 10)
    horas = minutos_total // 60
    minutos = minutos_total % 60
    segundos = random.randint(0, 59)
    
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

async def calcular_ranking():
    """Calcula o ranking anual agregando corridas"""
    ano_atual = 2025
    
    # Limpar ranking antigo
    await db.ranking_anual.delete_many({"ano": ano_atual})
    
    # Agregação: somar pontos e contar corridas por usuário
    pipeline = [
        {"$match": {"ano": ano_atual}},
        {"$group": {
            "_id": "$usuario_id",
            "pontos_total": {"$sum": "$pontos"},
            "total_corridas": {"$sum": 1}
        }}
    ]
    
    agregados = await db.corridas.aggregate(pipeline).to_list(None)
    
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
                "estado": usuario["estado"],
                "genero": usuario["genero"],
                "categoria": usuario["categoria"],
                "faixa_etaria": usuario["faixa_etaria"]
            })
    
    # Ordenar por pontos (nacional)
    ranking_docs.sort(key=lambda x: x["pontos_total"], reverse=True)
    
    # Atribuir ranking nacional
    for idx, doc in enumerate(ranking_docs, start=1):
        doc["ranking_nacional"] = idx
    
    # Calcular ranking por categoria
    categorias_generos = [
        ("normal", "M"), ("normal", "F"),
        ("pcd", "M"), ("pcd", "F"),
        ("cadeirante", "M"), ("cadeirante", "F")
    ]
    
    for cat, gen in categorias_generos:
        docs_cat = [d for d in ranking_docs if d["categoria"] == cat and d["genero"] == gen]
        docs_cat.sort(key=lambda x: x["pontos_total"], reverse=True)
        for idx, doc in enumerate(docs_cat, start=1):
            doc["ranking_categoria"] = idx
    
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

@api_router.get("/ranking/categoria/{categoria}/{genero}", response_model=List[RankingResponse])
async def get_ranking_por_categoria(categoria: str, genero: str, ano: int = Query(2025)):
    """Retorna ranking filtrado por categoria e gênero"""
    
    # Validar categoria
    if categoria not in ["masculino", "feminino", "pcd-m", "pcd-f", "cadeirante-m", "cadeirante-f"]:
        raise HTTPException(status_code=400, detail="Categoria inválida")
    
    # Mapear categoria
    cat_map = {
        "masculino": ("normal", "M"),
        "feminino": ("normal", "F"),
        "pcd-m": ("pcd", "M"),
        "pcd-f": ("pcd", "F"),
        "cadeirante-m": ("cadeirante", "M"),
        "cadeirante-f": ("cadeirante", "F")
    }
    
    cat_db, gen_db = cat_map[categoria]
    
    # Buscar ranking
    ranking_list = await db.ranking_anual.find(
        {"ano": ano, "categoria": cat_db, "genero": gen_db},
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
                id=usuario["id"],
                colocacao=rank["ranking_categoria"],
                uf=rank["estado"],
                foto_url=usuario["foto_url"],
                nome=usuario["nome"],
                cidade=f"{usuario['cidade']}/{usuario['estado']}",
                equipe=usuario["equipe"],
                faixa_etaria=rank["faixa_etaria"],
                total_corridas=rank["total_corridas"],
                pontos=rank["pontos_total"],
                is_elite=(rank["pontos_total"] >= 100),
                is_pendente=(rank["total_corridas"] < 12)
            ))
    
    return response

@api_router.get("/ranking/nacional", response_model=List[RankingResponse])
async def get_ranking_nacional(ano: int = Query(2025)):
    """Retorna o ranking nacional ordenado por pontos"""
    
    ranking_list = await db.ranking_anual.find(
        {"ano": ano},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    if not ranking_list:
        return []
    
    response = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            response.append(RankingResponse(
                id=usuario["id"],
                colocacao=rank["ranking_nacional"],
                uf=rank["estado"],
                foto_url=usuario["foto_url"],
                nome=usuario["nome"],
                cidade=f"{usuario['cidade']}/{usuario['estado']}",
                equipe=usuario["equipe"],
                faixa_etaria=rank["faixa_etaria"],
                total_corridas=rank["total_corridas"],
                pontos=rank["pontos_total"],
                is_elite=(rank["pontos_total"] >= 100),
                is_pendente=(rank["total_corridas"] < 12)
            ))
    
    return response

@api_router.get("/ranking/estadual/{uf}", response_model=List[RankingResponse])
async def get_ranking_estadual(uf: str, ano: int = Query(2025)):
    """Retorna o ranking estadual filtrado por UF"""
    
    uf = uf.upper()
    
    ranking_list = await db.ranking_anual.find(
        {"ano": ano, "estado": uf},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    if not ranking_list:
        return []
    
    response = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            response.append(RankingResponse(
                id=usuario["id"],
                colocacao=rank["ranking_estadual"],
                uf=rank["estado"],
                foto_url=usuario["foto_url"],
                nome=usuario["nome"],
                cidade=f"{usuario['cidade']}/{usuario['estado']}",
                equipe=usuario["equipe"],
                faixa_etaria=rank["faixa_etaria"],
                total_corridas=rank["total_corridas"],
                pontos=rank["pontos_total"],
                is_elite=(rank["pontos_total"] >= 100),
                is_pendente=(rank["total_corridas"] < 12)
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

@api_router.get("/atletas/{atleta_id}", response_model=AtletaDetalhes)
async def get_atleta_detalhes(atleta_id: str):
    """Retorna detalhes completos do atleta"""
    
    usuario = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Buscar estatísticas
    ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    
    # Buscar melhor colocação
    melhor_corrida = await db.corridas.find_one(
        {"usuario_id": atleta_id},
        {"_id": 0},
        sort=[("colocacao", 1)]
    )
    
    melhor_colocacao = melhor_corrida["colocacao"] if melhor_corrida else 0
    total_corridas = ranking["total_corridas"] if ranking else 0
    pontos_carreira = ranking["pontos_total"] if ranking else 0
    
    return AtletaDetalhes(
        id=usuario["id"],
        nome=usuario["nome"],
        cidade=usuario["cidade"],
        estado=usuario["estado"],
        genero=usuario["genero"],
        categoria=usuario["categoria"],
        faixa_etaria=usuario["faixa_etaria"],
        foto_url=usuario["foto_url"],
        equipe=usuario["equipe"],
        pontos_carreira=pontos_carreira,
        total_corridas=total_corridas,
        melhor_colocacao=melhor_colocacao,
        is_pendente=(total_corridas < 12)
    )

@api_router.get("/atletas/{atleta_id}/corridas", response_model=List[CorridaResponse])
async def get_atleta_corridas(atleta_id: str):
    """Retorna histórico de corridas do atleta"""
    
    corridas = await db.corridas.find(
        {"usuario_id": atleta_id},
        {"_id": 0}
    ).sort("data", -1).to_list(None)
    
    return [CorridaResponse(**corrida) for corrida in corridas]

@api_router.post("/ranking/popular")
async def popular_dados_teste():
    """Popula o banco com dados de teste realistas"""
    
    # Limpar dados existentes
    await db.usuarios.delete_many({})
    await db.corridas.delete_many({})
    await db.ranking_anual.delete_many({})
    
    # Nomes brasileiros realistas
    nomes_masculinos = [
        "Samuel Souza do Nascimento", "Paulo de Paula Oly", "Fábio Sanches",
        "André Sales", "Edson Luiz Brasiliano de Lima", "Anderson Teles Da Silva",
        "Fernando Vasque", "Kaio Rocha Ferreira", "Carlos Eduardo Santos",
        "Roberto Mendes", "Diego Oliveira", "Ricardo Ferreira", "Thiago Martins",
        "Lucas Pereira", "Bruno Costa", "André Luiz", "Rodrigo Silva", "Felipe Santos",
        "Gabriel Rocha", "Marcelo Souza", "Rafael Dias", "Gustavo Martins",
        "Eduardo Costa", "Daniel Oliveira", "Leonardo Santos", "Vinicius Lima",
        "Henrique Costa", "Fábio Mendes", "Marcos Silva", "Pedro Henrique",
        "Guilherme Lima", "Alexandre Ribeiro", "João Pedro", "Mateus Oliveira",
        "Bruno Ferreira", "Rodrigo Machado", "Luiz Fernando", "Anderson Silva",
        "Tiago Souza", "Cristiano Nunes", "Márcio Santos", "Paulo Roberto"
    ]
    
    nomes_femininos = [
        "Marina Silva Costa", "Julia Almeida", "Fernanda Lima", "Camila Rodrigues",
        "Beatriz Souza", "Amanda Costa", "Mariana Santos", "Juliana Ferreira",
        "Patricia Oliveira", "Carla Mendes", "Vanessa Lima", "Tatiana Costa",
        "Larissa Alves", "Bianca Lima", "Aline Santos", "Renata Silva",
        "Isabela Ferreira", "Carolina Souza", "Paula Rodrigues", "Débora Alves",
        "Luciana Oliveira", "Adriana Costa", "Natália Santos", "Letícia Alves",
        "Priscila Martins", "Simone Costa", "Raquel Santos", "Cristina Silva",
        "Cláudia Pereira", "Sabrina Costa", "Mônica Alves", "Jéssica Oliveira",
        "Bruna Lima", "Andreia Costa", "Ana Paula Silva", "Eliane Santos"
    ]
    
    equipes = [
        "CAPB Paraíba", "Sem equipe", "Sanches Running", "Força Falcão de Atletismo",
        "ZULURun ASSESSORIA E CORRIDA DE RUA", "ATRunners", "FV Running",
        "Emerson PeriniID", "SP Runners", "Fast Runners", "Run SP", "Carioca Runners",
        "RJ Running Team", "Paraná Runners", "Bahia Runners", "Ceará Runners",
        "MG Runners", "Gaúcho Runners", "SC Runners", "Floripa Running"
    ]
    
    cidades_estados = [
        ("Limeira", "SP"), ("São Paulo", "SP"), ("Campinas", "SP"), ("Santos", "SP"),
        ("Rio de Janeiro", "RJ"), ("Niterói", "RJ"), ("Magé", "RJ"),
        ("Curitiba", "PR"), ("Londrina", "PR"), ("Colombo", "PR"),
        ("Salvador", "BA"), ("Feira de Santana", "BA"), ("Vitória da Conquista", "BA"),
        ("Fortaleza", "CE"), ("Juazeiro do Norte", "CE"), ("Sobral", "CE"),
        ("Belo Horizonte", "MG"), ("Uberlândia", "MG"), ("Contagem", "MG"),
        ("Porto Alegre", "RS"), ("Caxias do Sul", "RS"), ("Canoas", "RS"),
        ("Florianópolis", "SC"), ("Joinville", "SC"), ("Xanxerê", "SC"),
        ("Cuiabá", "MT"), ("Lauro de Freitas", "BA"), ("Goiânia", "GO"),
        ("Brasília", "DF"), ("Recife", "PE"), ("Vitória", "ES")
    ]
    
    nomes_corridas = [
        "Corrida da Glória", "Caetité Run", "Meia Maratona de Vitória da Conquista",
        "São Silvestre", "Corrida de Reis", "Volta da Pampulha", "Corrida do Fogo",
        "Circuito das Estações", "Maratona do Rio", "Meia Maratona Internacional",
        "Corrida de São Pedro", "Desafio das Dunas", "Corrida do Sertão",
        "Prova Rústica", "Trail Run", "Corrida Noturna", "Beach Run"
    ]
    
    distancias = ["5KM", "10KM", "21KM", "42KM"]
    
    # Gerar atletas
    usuarios_inseridos = []
    
    # Distribuição: 40 M, 40 F, 10 PCD M, 10 PCD F, 5 CAD M, 5 CAD F
    distribuicao = [
        ("normal", "M", 40, nomes_masculinos[:40]),
        ("normal", "F", 40, nomes_femininos[:36]),
        ("pcd", "M", 10, ["João Silva PCD", "Pedro Santos PCD", "Lucas Oliveira PCD", 
                         "Rafael Costa PCD", "Marcos Lima PCD", "Bruno Alves PCD",
                         "Thiago Rocha PCD", "André Martins PCD", "Felipe Dias PCD", "Gabriel Nunes PCD"]),
        ("pcd", "F", 10, ["Maria Silva PCD", "Ana Santos PCD", "Julia Costa PCD",
                         "Fernanda Lima PCD", "Carla Alves PCD", "Patricia Rocha PCD",
                         "Vanessa Martins PCD", "Letícia Dias PCD", "Bianca Nunes PCD", "Renata Souza PCD"]),
        ("cadeirante", "M", 5, ["Roberto Silva Cadeirante", "Marcelo Costa Cadeirante",
                               "Fernando Lima Cadeirante", "Eduardo Alves Cadeirante", "Paulo Santos Cadeirante"]),
        ("cadeirante", "F", 5, ["Sandra Silva Cadeirante", "Cristina Costa Cadeirante",
                               "Juliana Lima Cadeirante", "Beatriz Alves Cadeirante", "Amanda Santos Cadeirante"])
    ]
    
    for categoria, genero, qtd, nomes in distribuicao:
        for i in range(qtd):
            nome = nomes[i % len(nomes)]
            cidade, estado = random.choice(cidades_estados)
            equipe = random.choice(equipes)
            
            # Gerar data de nascimento aleatória
            ano_nasc = random.randint(1960, 2007)
            data_nasc = f"{ano_nasc}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            faixa = calcular_faixa_etaria(data_nasc)
            
            usuario = Usuario(
                nome=nome,
                equipe=equipe,
                cidade=cidade,
                estado=estado,
                genero=genero,
                categoria=categoria,
                data_nascimento=data_nasc,
                faixa_etaria=faixa,
                foto_url=gerar_foto_url(nome)
            )
            
            doc = usuario.model_dump()
            await db.usuarios.insert_one(doc)
            usuarios_inseridos.append(usuario.id)
    
    # Gerar corridas para cada atleta
    corridas_inseridas = []
    for usuario_id in usuarios_inseridos:
        num_corridas = random.randint(3, 15)
        
        for _ in range(num_corridas):
            nome_corrida = random.choice(nomes_corridas)
            colocacao = random.randint(1, 20)
            distancia = random.choice(distancias)
            tempo = gerar_tempo_corrida(distancia, colocacao)
            
            # Pontos baseados na colocação
            if colocacao == 1:
                pontos = random.randint(8, 10)
            elif colocacao <= 3:
                pontos = random.randint(6, 8)
            elif colocacao <= 10:
                pontos = random.randint(4, 6)
            else:
                pontos = random.randint(2, 4)
            
            cidade, estado = random.choice(cidades_estados)
            local = f"{cidade}/{estado}"
            
            # Data aleatória em 2025
            mes = random.randint(1, 12)
            dia = random.randint(1, 28)
            data_corrida = f"2025-{mes:02d}-{dia:02d}"
            
            corrida = Corrida(
                usuario_id=usuario_id,
                nome=nome_corrida,
                colocacao=colocacao,
                tempo=tempo,
                pontos=pontos,
                local=local,
                distancia=distancia,
                data=data_corrida,
                ano=2025
            )
            
            doc = corrida.model_dump()
            await db.corridas.insert_one(doc)
            corridas_inseridas.append(corrida.id)
    
    # Calcular ranking
    total_ranking = await calcular_ranking()
    
    return {
        "message": "Dados populados com sucesso!",
        "usuarios": len(usuarios_inseridos),
        "corridas": len(corridas_inseridas),
        "ranking_calculado": total_ranking
    }


# ==================== INCLUDE ROUTER ====================

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
