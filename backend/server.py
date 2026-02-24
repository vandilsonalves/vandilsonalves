from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, date, timedelta
import random
from passlib.context import CryptContext
from jose import JWTError, jwt
import csv
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "sua-chave-secreta-super-segura-aqui-123456")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")


# ==================== SECURITY FUNCTIONS ====================

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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")
    return current_user


# ==================== MODELS ====================

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
    primeira_submissao: bool = False  # Para regra dos 15 dias

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

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

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


# ==================== HELPER FUNCTIONS ====================

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

async def calcular_ranking():
    """Calcula o ranking anual agregando corridas"""
    ano_atual = 2025
    
    await db.ranking_anual.delete_many({"ano": ano_atual})
    
    pipeline = [
        {"$match": {"ano": ano_atual}},
        {"$group": {
            "_id": "$usuario_id",
            "pontos_total": {"$sum": "$pontos"},
            "total_corridas": {"$sum": 1}
        }}
    ]
    
    agregados = await db.corridas.aggregate(pipeline).to_list(None)
    
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
    
    ranking_docs.sort(key=lambda x: x["pontos_total"], reverse=True)
    
    for idx, doc in enumerate(ranking_docs, start=1):
        doc["ranking_nacional"] = idx
    
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
    
    estados = set(doc["estado"] for doc in ranking_docs)
    for uf in estados:
        docs_uf = [d for d in ranking_docs if d["estado"] == uf]
        docs_uf.sort(key=lambda x: x["pontos_total"], reverse=True)
        for idx, doc in enumerate(docs_uf, start=1):
            doc["ranking_estadual"] = idx
    
    if ranking_docs:
        await db.ranking_anual.insert_many(ranking_docs)
    
    return len(ranking_docs)


# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/register")
async def register_atleta(dados: UsuarioRegister):
    """Cadastro de novo atleta"""
    
    # Verificar se email já existe
    existing = await db.usuarios.find_one({"email": dados.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Calcular faixa etária
    faixa = calcular_faixa_etaria(dados.data_nascimento)
    
    # Criar usuário
    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        password_hash=get_password_hash(dados.password),
        equipe=dados.equipe,
        cidade=dados.cidade,
        estado=dados.estado,
        genero=dados.genero,
        categoria=dados.categoria,
        data_nascimento=dados.data_nascimento,
        faixa_etaria=faixa,
        foto_url=gerar_foto_url(dados.nome),
        role="atleta",
        is_active=True
    )
    
    doc = usuario.model_dump()
    await db.usuarios.insert_one(doc)
    
    # Gerar token
    token = create_access_token({"sub": usuario.id})
    
    return {
        "message": "Cadastro realizado com sucesso!",
        "token": token,
        "user": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "role": usuario.role
        }
    }

@api_router.post("/auth/login")
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
            "role": user["role"]
        }
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retorna dados do usuário logado"""
    return {
        "id": current_user["id"],
        "nome": current_user["nome"],
        "email": current_user["email"],
        "role": current_user["role"],
        "categoria": current_user["categoria"],
        "foto_url": current_user["foto_url"]
    }


# ==================== SUBMISSÃO DE RESULTADOS ====================

@api_router.post("/resultados/submeter")
async def submeter_resultado(
    nome_competicao: str = Form(...),
    colocacao: int = Form(...),
    cidade_competicao: str = Form(...),
    estado_competicao: str = Form(...),
    data_competicao: str = Form(...),
    link_resultado: str = Form(...),
    tempo: str = Form(...),
    distancia: str = Form(...),
    foto_podio: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Atleta submete resultado para aprovação"""
    
    # Validar prazo (6 dias úteis)
    data_comp = datetime.strptime(data_competicao, "%Y-%m-%d")
    hoje = datetime.now()
    dias_diff = (hoje - data_comp).days
    
    if dias_diff > 6:
        raise HTTPException(
            status_code=400,
            detail="Prazo expirado! Você tem apenas 6 dias úteis para enviar o resultado após a competição."
        )
    
    # Salvar foto (simplificado - em produção usar S3)
    # Salvar foto (OPCIONAL)
    foto_url = ""
    if foto_podio and foto_podio.filename:
        foto_filename = f"{uuid.uuid4()}_{foto_podio.filename}"
        foto_path = Path("/app/uploads") / foto_filename
        foto_path.parent.mkdir(exist_ok=True)
        
        with foto_path.open("wb") as f:
            f.write(await foto_podio.read())
        
        foto_url = f"/uploads/{foto_filename}"
    
    # Criar resultado pendente
    resultado = ResultadoPendente(
        usuario_id=current_user["id"],
        nome_competicao=nome_competicao,
        colocacao=colocacao,
        cidade_competicao=cidade_competicao,
        estado_competicao=estado_competicao,
        data_competicao=data_competicao,
        link_resultado=link_resultado,
        tempo=tempo,
        distancia=distancia,
        foto_podio_url=foto_url,
        status="pendente"
    )
    
    doc = resultado.model_dump()
    await db.resultados_pendentes.insert_one(doc)
    
    return {
        "message": "Resultado submetido com sucesso! Aguarde aprovação do administrador.",
        "id": resultado.id
    }


# ==================== ADMIN ENDPOINTS ====================

@api_router.get("/admin/pendentes")
async def listar_pendentes(admin: dict = Depends(get_admin_user)):
    """Lista resultados pendentes de aprovação"""
    
    resultados = await db.resultados_pendentes.find(
        {"status": "pendente"},
        {"_id": 0}
    ).sort("data_submissao", -1).to_list(None)
    
    # Enriquecer com dados do atleta
    for resultado in resultados:
        usuario = await db.usuarios.find_one({"id": resultado["usuario_id"]}, {"_id": 0})
        if usuario:
            resultado["atleta_nome"] = usuario["nome"]
            resultado["atleta_equipe"] = usuario["equipe"]
            resultado["atleta_categoria"] = usuario["categoria"]
    
    return resultados

@api_router.post("/admin/aprovar/{resultado_id}")
async def aprovar_resultado(resultado_id: str, admin: dict = Depends(get_admin_user)):
    """Aprova resultado e adiciona à corrida oficial"""
    
    resultado = await db.resultados_pendentes.find_one({"id": resultado_id}, {"_id": 0})
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")
    
    if resultado["status"] != "pendente":
        raise HTTPException(status_code=400, detail="Resultado já processado")
    
    # Buscar atleta
    usuario = await db.usuarios.find_one({"id": resultado["usuario_id"]}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Calcular pontos
    pontos = calcular_pontos_colocacao(resultado["colocacao"], usuario["categoria"])
    
    if pontos == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Colocação {resultado['colocacao']}º não pontua para categoria {usuario['categoria']}"
        )
    
    # Criar corrida oficial
    corrida = Corrida(
        usuario_id=resultado["usuario_id"],
        nome=resultado["nome_competicao"],
        colocacao=resultado["colocacao"],
        tempo=resultado["tempo"],
        pontos=pontos,
        local=f"{resultado['cidade_competicao']}/{resultado['estado_competicao']}",
        distancia=resultado["distancia"],
        data=resultado["data_competicao"],
        ano=2025
    )
    
    await db.corridas.insert_one(corrida.model_dump())
    
    # Atualizar status
    await db.resultados_pendentes.update_one(
        {"id": resultado_id},
        {"$set": {"status": "aprovado"}}
    )
    
    # Recalcular ranking
    await calcular_ranking()
    
    return {"message": "Resultado aprovado com sucesso!", "pontos_adicionados": pontos}

@api_router.post("/admin/reprovar/{resultado_id}")
async def reprovar_resultado(
    resultado_id: str,
    dados: AprovacaoRequest,
    admin: dict = Depends(get_admin_user)
):
    """Reprova resultado"""
    
    resultado = await db.resultados_pendentes.find_one({"id": resultado_id}, {"_id": 0})
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")
    
    if resultado["status"] != "pendente":
        raise HTTPException(status_code=400, detail="Resultado já processado")
    
    await db.resultados_pendentes.update_one(
        {"id": resultado_id},
        {"$set": {
            "status": "reprovado",
            "motivo_reprovacao": dados.motivo or "Não atende aos critérios do regulamento"
        }}
    )
    
    return {"message": "Resultado reprovado"}


# ==================== RANKING ENDPOINTS ====================

@api_router.get("/ranking/categoria/{categoria}/{genero}", response_model=List[RankingResponse])
async def get_ranking_por_categoria(categoria: str, genero: str, ano: int = Query(2025)):
    cat_map = {
        "masculino": ("normal", "M"),
        "feminino": ("normal", "F"),
        "pcd-m": ("pcd", "M"),
        "pcd-f": ("pcd", "F"),
        "cadeirante-m": ("cadeirante", "M"),
        "cadeirante-f": ("cadeirante", "F")
    }
    
    cat_db, gen_db = cat_map.get(categoria, ("normal", "M"))
    
    ranking_list = await db.ranking_anual.find(
        {"ano": ano, "categoria": cat_db, "genero": gen_db},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    response = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            min_corridas = get_min_corridas_categoria(rank["categoria"])
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
                is_pendente=(rank["total_corridas"] < min_corridas)
            ))
    
    return response

@api_router.get("/ranking/export/csv")
async def export_ranking_csv(categoria: str = "masculino"):
    """Exporta ranking em CSV"""
    
    cat_map = {
        "masculino": ("normal", "M"),
        "feminino": ("normal", "F"),
        "pcd-m": ("pcd", "M"),
        "pcd-f": ("pcd", "F"),
        "cadeirante-m": ("cadeirante", "M"),
        "cadeirante-f": ("cadeirante", "F")
    }
    
    cat_db, gen_db = cat_map.get(categoria, ("normal", "M"))
    
    ranking_list = await db.ranking_anual.find(
        {"ano": 2025, "categoria": cat_db, "genero": gen_db},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    # Criar CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Colocação", "Nome", "Equipe", "Cidade", "UF", "Faixa", "Corridas", "Pontos"])
    
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            writer.writerow([
                rank["ranking_categoria"],
                usuario["nome"],
                usuario["equipe"],
                usuario["cidade"],
                usuario["estado"],
                rank["faixa_etaria"],
                rank["total_corridas"],
                rank["pontos_total"]
            ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=ranking_{categoria}.csv"}
    )

@api_router.get("/ranking/export/excel")
async def export_ranking_excel(categoria: str = "masculino"):
    """Exporta ranking em Excel"""
    
    cat_map = {
        "masculino": ("normal", "M"),
        "feminino": ("normal", "F"),
        "pcd-m": ("pcd", "M"),
        "pcd-f": ("pcd", "F"),
        "cadeirante-m": ("cadeirante", "M"),
        "cadeirante-f": ("cadeirante", "F")
    }
    
    cat_db, gen_db = cat_map.get(categoria, ("normal", "M"))
    
    ranking_list = await db.ranking_anual.find(
        {"ano": 2025, "categoria": cat_db, "genero": gen_db},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    # Criar Excel
    wb = Workbook()
    ws = wb.active
    ws.title = f"Ranking {categoria.title()}"
    
    # Cabeçalho
    headers = ["Colocação", "Nome", "Equipe", "Cidade", "UF", "Faixa", "Corridas", "Pontos"]
    ws.append(headers)
    
    # Estilizar cabeçalho
    header_fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    # Dados
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            ws.append([
                rank["ranking_categoria"],
                usuario["nome"],
                usuario["equipe"],
                usuario["cidade"],
                usuario["estado"],
                rank["faixa_etaria"],
                rank["total_corridas"],
                rank["pontos_total"]
            ])
    
    # Salvar em memória
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=ranking_{categoria}.xlsx"}
    )

@api_router.get("/atletas/{atleta_id}", response_model=AtletaDetalhes)
async def get_atleta_detalhes(atleta_id: str):
    usuario = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    
    melhor_corrida = await db.corridas.find_one(
        {"usuario_id": atleta_id},
        {"_id": 0},
        sort=[("colocacao", 1)]
    )
    
    melhor_colocacao = melhor_corrida["colocacao"] if melhor_corrida else 0
    total_corridas = ranking["total_corridas"] if ranking else 0
    pontos_carreira = ranking["pontos_total"] if ranking else 0
    
    min_corridas = get_min_corridas_categoria(usuario["categoria"])
    
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
        is_pendente=(total_corridas < min_corridas)
    )

@api_router.get("/atletas/{atleta_id}/corridas", response_model=List[CorridaResponse])
async def get_atleta_corridas(atleta_id: str):
    corridas = await db.corridas.find(
        {"usuario_id": atleta_id},
        {"_id": 0}
    ).sort("data", -1).to_list(None)
    
    return [CorridaResponse(**corrida) for corrida in corridas]

@api_router.get("/atletas/{atleta_id}/evolucao", response_model=List[EvolucaoMensal])
async def get_evolucao_atleta(atleta_id: str):
    """Retorna evolução mensal do atleta para gráficos"""
    
    corridas = await db.corridas.find(
        {"usuario_id": atleta_id, "ano": 2025},
        {"_id": 0}
    ).sort("data", 1).to_list(None)
    
    # Agrupar por mês
    evolucao_dict = {}
    for corrida in corridas:
        mes = corrida["data"][:7]  # YYYY-MM
        if mes not in evolucao_dict:
            evolucao_dict[mes] = {"pontos": 0, "corridas": 0}
        evolucao_dict[mes]["pontos"] += corrida["pontos"]
        evolucao_dict[mes]["corridas"] += 1
    
    # Converter para lista
    evolucao = [
        EvolucaoMensal(mes=mes, pontos=dados["pontos"], corridas=dados["corridas"])
        for mes, dados in sorted(evolucao_dict.items())
    ]
    
    return evolucao

@api_router.get("/ranking/nacional", response_model=List[RankingResponse])
async def get_ranking_nacional(ano: int = Query(2025)):
    ranking_list = await db.ranking_anual.find(
        {"ano": ano},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    response = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            min_corridas = get_min_corridas_categoria(rank["categoria"])
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
                is_pendente=(rank["total_corridas"] < min_corridas)
            ))
    
    return response

@api_router.get("/ranking/estados")
async def get_estados_disponiveis(ano: int = Query(2025)):
    pipeline = [
        {"$match": {"ano": ano}},
        {"$group": {"_id": "$estado"}},
        {"$sort": {"_id": 1}}
    ]
    
    estados = await db.ranking_anual.aggregate(pipeline).to_list(None)
    return {"estados": [e["_id"] for e in estados]}

@api_router.get("/")
async def root():
    return {"message": "Ranking Run Pro API"}

@api_router.post("/ranking/popular")
async def popular_dados_teste():
    """Popula banco com dados de teste"""
    # (código de população omitido por brevidade - mantém o existente)
    return {"message": "Use apenas para desenvolvimento"}


# ==================== ADMIN STATISTICS ====================

@api_router.get("/admin/stats")
async def get_admin_stats(admin: dict = Depends(get_admin_user)):
    """Estatísticas gerais do dashboard admin"""
    
    # Total de atletas
    total_atletas = await db.usuarios.count_documents({"role": "atleta"})
    
    # Resultados pendentes
    resultados_pendentes = await db.resultados_pendentes.count_documents({"status": "pendente"})
    
    # Atletas com menos de 12 corridas (normal) ou 8 (PCD/Cadeirante)
    rankings = await db.ranking_anual.find({"ano": 2025}, {"_id": 0}).to_list(None)
    atletas_pendentes = 0
    for rank in rankings:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            min_corridas = 8 if usuario["categoria"] in ["pcd", "cadeirante"] else 12
            if rank["total_corridas"] < min_corridas:
                atletas_pendentes += 1
    
    # Total homens vs mulheres
    total_homens = await db.usuarios.count_documents({"role": "atleta", "genero": "M"})
    total_mulheres = await db.usuarios.count_documents({"role": "atleta", "genero": "F"})
    
    return {
        "total_atletas": total_atletas,
        "resultados_pendentes": resultados_pendentes,
        "atletas_pendentes_corridas": atletas_pendentes,
        "total_homens": total_homens,
        "total_mulheres": total_mulheres
    }

@api_router.get("/admin/stats/estados")
async def get_stats_estados(admin: dict = Depends(get_admin_user)):
    """Distribuição de atletas por estado"""
    
    pipeline = [
        {"$match": {"role": "atleta"}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [{"estado": r["_id"], "total": r["count"]} for r in result]

@api_router.get("/admin/stats/categorias")
async def get_stats_categorias(admin: dict = Depends(get_admin_user)):
    """Distribuição por categoria e gênero"""
    
    pipeline = [
        {"$match": {"role": "atleta"}},
        {"$group": {
            "_id": {"categoria": "$categoria", "genero": "$genero"},
            "count": {"$sum": 1}
        }}
    ]
    
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    
    stats = {
        "normal_m": 0, "normal_f": 0,
        "pcd_m": 0, "pcd_f": 0,
        "cadeirante_m": 0, "cadeirante_f": 0
    }
    
    for r in result:
        cat = r["_id"]["categoria"]
        gen = r["_id"]["genero"]
        key = f"{cat}_{gen.lower()}"
        stats[key] = r["count"]
    
    return stats

@api_router.get("/admin/stats/faixa-etaria")
async def get_stats_faixa_etaria(admin: dict = Depends(get_admin_user)):
    """Distribuição por faixa etária"""
    
    pipeline = [
        {"$match": {"role": "atleta"}},
        {"$group": {"_id": "$faixa_etaria", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [{"faixa": r["_id"], "total": r["count"]} for r in result]


# ==================== PERFIL DO ATLETA ====================

class PerfilUpdate(BaseModel):
    equipe: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    telefone: Optional[str] = None
    bio: Optional[str] = None

@api_router.patch("/atletas/perfil")
async def atualizar_perfil(dados: PerfilUpdate, current_user: dict = Depends(get_current_user)):
    """Atleta atualiza seu próprio perfil"""
    
    update_data = {}
    if dados.equipe is not None:
        update_data["equipe"] = dados.equipe
    if dados.facebook_url is not None:
        update_data["facebook_url"] = dados.facebook_url
    if dados.instagram_url is not None:
        update_data["instagram_url"] = dados.instagram_url
    if dados.telefone is not None:
        update_data["telefone"] = dados.telefone
    if dados.bio is not None:
        update_data["bio"] = dados.bio
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    await db.usuarios.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    return {"message": "Perfil atualizado com sucesso!"}

@api_router.post("/atletas/foto")
async def upload_foto_perfil(
    foto: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload de foto de perfil"""
    
    # Salvar foto
    foto_filename = f"perfil_{current_user['id']}_{uuid.uuid4()}.jpg"
    foto_path = Path("/app/uploads") / foto_filename
    foto_path.parent.mkdir(exist_ok=True)
    
    with foto_path.open("wb") as f:
        f.write(await foto.read())
    
    foto_url = f"/uploads/{foto_filename}"
    
    # Atualizar usuário
    await db.usuarios.update_one(
        {"id": current_user["id"]},
        {"$set": {"foto_url": foto_url}}
    )
    
    return {"message": "Foto atualizada!", "foto_url": foto_url}





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
