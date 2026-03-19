from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, UploadFile, File, Form, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import random
from jose import JWTError, jwt
import csv
import io
import re
import httpx
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

"""
================================================================================
                        RANKING RUN PRÓ - API SERVER
================================================================================

ÍNDICE DE SEÇÕES (para navegação rápida, use Ctrl+F):

    [AUTH]              - Autenticação (login, registro, token)          ~Linha 90
    [NOTIFICACOES]      - Sistema de notificações                        ~Linha 230
    [CONQUISTAS]        - Selos e conquistas de atletas                  ~Linha 278
    [PERFIL]            - Perfil do atleta                               ~Linha 485
    [TROCA_EQUIPE]      - Troca de equipe pelo atleta                    ~Linha 667
    [ANIVERSARIO]       - Mensagens de aniversário                       ~Linha 819
    [RESULTADOS]        - Submissão de resultados                        ~Linha 847
    [ADMIN_APROVACOES]  - Aprovação/reprovação de resultados             ~Linha 964
    [ADMIN_STATS]       - Estatísticas do admin                          ~Linha 1126
    [ADMIN_ATLETAS]     - Gestão de atletas (admin)                      ~Linha 1274
    [ADMIN_ASSESSORIAS] - Gestão de assessorias (admin)                  ~Linha 2000
    [ADMIN_ANIVERSARIOS]- Aniversariantes (admin)                        ~Linha 2400
    [ADMIN_INSTAGRAM]   - Análise Instagram (admin)                      ~Linha 2600
    [RANKING_PUBLICO]   - Rankings públicos                              ~Linha 3000
    [LIGA_ASSESSORIAS]  - Liga de Assessorias (ROE-RR)                   ~Linha 4600
    [DONO_ASSESSORIA]   - Dashboard do dono de assessoria                ~Linha 5000
    [RELATORIOS]        - Relatórios detalhados                          ~Linha 5300
    [REGULAMENTO]       - Gestão do regulamento                          ~Linha 5500
    [AUTORIZACOES]      - Sistema de autorizações (30 dias)              ~Linha 5600
    [REPUTACAO]         - Reputação de avaliadores                       ~Linha 5750
    [RANKING_CORRIDAS]  - Ranking e avaliação de corridas                ~Linha 6100
    [SCHEDULER]         - Tarefas agendadas                              ~Linha 6900

Para refatoração futura, veja: /app/backend/ARCHITECTURE.md
================================================================================
"""

# Import models and services
from models import (
    Usuario, UsuarioRegister, UsuarioLogin, PerfilUpdate,
    ResultadoPendente, ResultadoSubmissao, AprovacaoRequest,
    Corrida, RankingAnual, RankingResponse, AtletaDetalhes,
    CorridaResponse, EvolucaoMensal, Notificacao, Conquista, ConquistaAtleta,
    MensagemAniversario, RankingPovao, InstagramProfileInput, InstagramAnalysis, InstagramAnalysisResponse
)
from services import (
    verify_password, get_password_hash, create_access_token,
    calcular_faixa_etaria, gerar_foto_url, calcular_pontos_colocacao,
    get_min_corridas_categoria, SECRET_KEY, ALGORITHM, CONQUISTAS,
    calcular_pontos_povao, extrair_distancia_km,
    calcular_nota_bio, calcular_nota_frequencia, calcular_nota_engajamento,
    calcular_nota_crescimento, calcular_nota_consistencia, calcular_nota_padroes,
    calcular_nota_reels, calcular_nota_formatos, calcular_score_final,
    classificar_influenciador, gerar_recomendacoes, MEDIAS_NICHO
)

# Import RBAC models and services
from models.rbac import (
    Role, Permissao, Administrador, AdminCreate, AdminUpdate, 
    AdminLog, LoginHistory, CodigoVerificacao, AlertaSeguranca,
    PERMISSOES_SISTEMA, ROLES_PREDEFINIDOS
)
from services.rbac_service import (
    gerar_codigo_2fa, extrair_info_dispositivo, 
    criar_log_acao, criar_alerta_seguranca,
    gerar_email_alerta_emergencia, gerar_email_codigo_2fa
)

# Import refactored route helpers (REFATORAÇÃO EM ANDAMENTO)
from routes.auth_routes import get_current_user, get_admin_user
from routes.notificacoes_routes import criar_notificacao
from routes.conquistas_routes import verificar_conquistas

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
security = HTTPBearer()

# Create the main app
app = FastAPI(title="Ranking Run Pró API")
api_router = APIRouter(prefix="/api")

# ==================== MIDDLEWARE DE MONITORAMENTO ====================
from services.monitoring_service import metrics_collector
from middleware import MetricsMiddleware
app.add_middleware(MetricsMiddleware, metrics_collector=metrics_collector)

# Servir arquivos de uploads
uploads_path = Path("/app/uploads")
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


# ==================== [REFATORADO] AUTH, NOTIFICAÇÕES, CONQUISTAS, ATLETAS, RESULTADOS, RANKING ====================
# Endpoints migrados para módulos em /app/backend/routes/
# - auth_routes.py: /auth/register, /auth/login, /auth/me
# - notificacoes_routes.py: /notificacoes, marcar lida
# - conquistas_routes.py: /conquistas, /selos-atleta, verificar-conquistas
# - atletas_routes.py: /atletas/meu-perfil, perfil, senha, foto, troca-equipe, aniversario
# - resultados_routes.py: /resultados/submeter
# - ranking_routes.py: /ranking/povao, semanal, mensal, categoria, etc.
# - monitoring_routes.py: /health, /monitoring/*
# ====================================================================================

# Incluir routers modulares PRIMEIRO (ordem importa para evitar conflitos de path params)
from routes.rbac import router as rbac_router
from routes.auth_routes import router as auth_routes_router
from routes.notificacoes_routes import router as notificacoes_router
from routes.conquistas_routes import router as conquistas_router
from routes.atletas_routes import router as atletas_router
from routes.resultados_routes import router as resultados_router
from routes.ranking_routes import router as ranking_router
from routes.monitoring_routes import router as monitoring_router
from routes.admin_routes import router as admin_routes_router
from routes.assessorias_routes import router as assessorias_router
from routes.celery_routes import router as celery_router
from routes.corridas_eventos_routes import router as corridas_eventos_router
from routes.aniversariantes_routes import router as aniversariantes_router
from routes.instagram_routes import router as instagram_router
from routes.websocket_routes import router as websocket_router
from routes.dashboard_stats_routes import router as dashboard_stats_router
from routes.assessorias_routes import get_ranking_assessorias
from routes.badges_routes import router as badges_router
from routes.indicacao_routes import router as indicacao_router
from routes.rankings_routes import router as rankings_router
from routes.regulamento_routes import router as regulamento_router
from routes.autorizacoes_routes import router as autorizacoes_router
from routes.rivais_routes import router as rivais_router
from routes.feed_routes import router as feed_router
from routes.liga_assessorias_routes import router as liga_assessorias_router
from routes.ranking_corridas_routes import router as ranking_corridas_router

api_router.include_router(rbac_router)
api_router.include_router(auth_routes_router)
api_router.include_router(notificacoes_router)
api_router.include_router(conquistas_router)
api_router.include_router(atletas_router)
api_router.include_router(resultados_router)
api_router.include_router(ranking_router)
api_router.include_router(monitoring_router)
api_router.include_router(admin_routes_router)
api_router.include_router(assessorias_router)
api_router.include_router(celery_router)
api_router.include_router(corridas_eventos_router)
api_router.include_router(aniversariantes_router)
api_router.include_router(instagram_router)
api_router.include_router(websocket_router)
api_router.include_router(dashboard_stats_router)
api_router.include_router(badges_router)
api_router.include_router(indicacao_router)
api_router.include_router(rankings_router)
api_router.include_router(regulamento_router)
api_router.include_router(autorizacoes_router)
api_router.include_router(rivais_router)
api_router.include_router(feed_router)
api_router.include_router(liga_assessorias_router)
api_router.include_router(ranking_corridas_router)

# ==================== ADMIN ENDPOINTS ====================
# [REFATORADO] Endpoints migrados para routes/admin_routes.py:
# - /admin/pendentes (GET)
# - /admin/aprovar/{resultado_id} (POST)
# - /admin/reprovar/{resultado_id} (POST)
# - /admin/pendentes/{resultado_id}/foto (DELETE)
# - /admin/stats/* (GET)
# - /admin/atletas (GET, POST)
# - /admin/atletas/{atleta_id} (PUT, DELETE)
# - /admin/atletas/export (GET)
# - /admin/atletas/{atleta_id}/transferir-modalidade (POST)

# Endpoints NÃO migrados (permanecem aqui):
# - /admin/atletas/{atleta_id}/promover-dono-assessoria (POST)
# - /admin/popular-dados-teste (POST)
# - /admin/ajustar-pontos (POST)
# - /admin/adicionar-corrida (POST)
# - /admin/corridas/{corrida_id} (PUT, DELETE)

@api_router.post("/admin/atletas/{atleta_id}/promover-dono-assessoria")
async def promover_dono_assessoria(atleta_id: str, admin: dict = Depends(get_admin_user)):
    """Promove um atleta a Dono de Assessoria"""
    
    # Buscar atleta
    atleta = await db.usuarios.find_one({"id": atleta_id, "role": "atleta"}, {"_id": 0})
    
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    if not atleta.get("equipe") or atleta.get("equipe") == "Sem equipe":
        raise HTTPException(status_code=400, detail="Atleta precisa estar vinculado a uma equipe para ser promovido")
    
    # Atualizar role do atleta
    await db.usuarios.update_one(
        {"id": atleta_id},
        {"$set": {"role": "dono_assessoria"}}
    )
    
    return {
        "message": f"Atleta {atleta['nome']} promovido a Dono de Assessoria!",
        "equipe": atleta.get("equipe")
    }


@api_router.post("/admin/popular-dados-teste")
async def popular_dados_teste(admin: dict = Depends(get_admin_user)):
    """Exclui atletas existentes e cria 160 novos atletas de teste"""
    import random
    
    # Excluir atletas existentes (exceto admin)
    await db.usuarios.delete_many({"role": "atleta"})
    await db.corridas.delete_many({})
    
    EQUIPES = [
        "Assessoria CAFAV", "Run Pro Team", "Elite Runners BA", "Speed Force SP",
        "Maratona Club RJ", "Corredores MG", "Ultra Running RS", "Fast Track ES",
        "Victory Run PE", "Champions SC", "Power Runners DF", "Trail Blazers GO"
    ]
    
    ESTADOS_CIDADES = {
        "SP": ["São Paulo", "Campinas", "Santos"],
        "RJ": ["Rio de Janeiro", "Niterói"],
        "MG": ["Belo Horizonte", "Uberlândia"],
        "BA": ["Salvador", "Feira de Santana"],
        "RS": ["Porto Alegre", "Caxias do Sul"],
        "PR": ["Curitiba", "Londrina"],
        "SC": ["Florianópolis", "Joinville"],
        "PE": ["Recife", "Olinda"],
        "ES": ["Vitória", "Vila Velha"],
        "GO": ["Goiânia"],
        "DF": ["Brasília"]
    }
    
    NOMES_M = ["Lucas", "Gabriel", "Pedro", "Rafael", "Matheus", "Bruno", "João", "Carlos",
               "André", "Felipe", "Marcos", "Diego", "Thiago", "Daniel", "Eduardo", "Ricardo",
               "Leonardo", "Gustavo", "Rodrigo", "Fernando"]
    
    NOMES_F = ["Ana", "Maria", "Julia", "Fernanda", "Camila", "Beatriz", "Amanda", "Patricia",
               "Carla", "Bruna", "Larissa", "Juliana", "Aline", "Gabriela", "Mariana", "Leticia",
               "Raquel", "Priscila", "Vanessa", "Michele"]
    
    SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa", "Ferreira",
                  "Rodrigues", "Almeida", "Nascimento", "Carvalho", "Gomes", "Martins", "Araújo"]
    
    ETNIAS = ["Branco", "Negro", "Pardo", "Indígena", "Amarelo", "Mulato"]
    
    BIOS = [
        "Apaixonado por corrida desde criança. Cada quilômetro é uma vitória!",
        "Correr é minha terapia. Vivo para superar meus limites a cada dia.",
        "Atleta dedicado, sempre em busca de melhorar meu pace.",
        "A corrida me ensinou disciplina e perseverança. Nunca desisto!",
        "Correr é mais que esporte, é estilo de vida. #RunForLife",
        "Cada maratona concluída é um troféu na minha história.",
        "A estrada é minha companheira. Correr me faz livre!",
        "Do sofá para a maratona. Minha transformação começou correndo.",
        "Corredor amador com coração de campeão!",
        "Treino forte, corro mais forte. Essa é minha filosofia."
    ]
    
    FACEBOOK = "https://www.facebook.com/assessoriaesportivacafva?locale=pt_BR"
    INSTAGRAM = "https://www.instagram.com/rankingrun/"
    
    atletas = []
    idx = 0
    
    configs = [
        # Profissional/Amador
        {"qtd": 20, "genero": "M", "categoria": "normal", "modalidade": "profissional_amador", "nomes": NOMES_M},
        {"qtd": 20, "genero": "F", "categoria": "normal", "modalidade": "profissional_amador", "nomes": NOMES_F},
        {"qtd": 20, "genero": "M", "categoria": "pcd", "modalidade": "profissional_amador", "nomes": NOMES_M},
        {"qtd": 20, "genero": "F", "categoria": "pcd", "modalidade": "profissional_amador", "nomes": NOMES_F},
        {"qtd": 20, "genero": "M", "categoria": "cadeirante", "modalidade": "profissional_amador", "nomes": NOMES_M},
        {"qtd": 20, "genero": "F", "categoria": "cadeirante", "modalidade": "profissional_amador", "nomes": NOMES_F},
        # Povão
        {"qtd": 20, "genero": "M", "categoria": "normal", "modalidade": "povao_pace_livre", "nomes": NOMES_M},
        {"qtd": 20, "genero": "F", "categoria": "normal", "modalidade": "povao_pace_livre", "nomes": NOMES_F},
    ]
    
    for cfg in configs:
        for i in range(cfg["qtd"]):
            idx += 1
            estado = random.choice(list(ESTADOS_CIDADES.keys()))
            cidade = random.choice(ESTADOS_CIDADES[estado])
            equipe = random.choice(EQUIPES)
            nome = f"{random.choice(cfg['nomes'])} {random.choice(SOBRENOMES)}"
            
            peso = random.randint(65, 85) if cfg["genero"] == "M" else random.randint(50, 70)
            altura = random.randint(168, 188) if cfg["genero"] == "M" else random.randint(155, 175)
            ano_nasc = random.randint(1981, 2006)
            
            atleta = {
                "id": str(uuid.uuid4()),
                "nome": nome,
                "email": f"{nome.lower().replace(' ', '_')}_{idx}@email.com",
                "password_hash": get_password_hash("atleta123"),
                "role": "atleta",
                "genero": cfg["genero"],
                "categoria": cfg["categoria"],
                "modalidade_usuario": cfg["modalidade"],
                "equipe": equipe,
                "estado": estado,
                "cidade": cidade,
                "etnia": random.choice(ETNIAS),
                "data_nascimento": f"{ano_nasc}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                "peso": peso,
                "altura": altura,
                "bio": random.choice(BIOS),
                "facebook": FACEBOOK,
                "instagram": INSTAGRAM,
                "pontos_carreira": random.randint(50, 500),
                "pontos_povao": random.randint(20, 200) if cfg["modalidade"] == "povao_pace_livre" else 0,
                "total_corridas": random.randint(5, 30),
                "aprovado": True
            }
            atletas.append(atleta)
    
    await db.usuarios.insert_many(atletas)
    
    # Criar corridas de teste
    corridas = []
    provas = ["Maratona de São Paulo", "Meia do Rio", "10K Brasília", "Corrida de Rua BH", "Ultra Trail RS"]
    
    for atleta in atletas[:100]:
        num_corridas = random.randint(2, 8)
        for _ in range(num_corridas):
            colocacao = random.randint(1, 50)
            pontos = 100 if colocacao == 1 else (80 - (colocacao-2)*10 if colocacao <= 5 else 15)
            
            corrida = {
                "id": str(uuid.uuid4()),
                "usuario_id": atleta["id"],
                "usuario_nome": atleta["nome"],
                "prova": random.choice(provas),
                "data": f"2026-{random.randint(1,3):02d}-{random.randint(1,28):02d}",
                "distancia": random.choice([5, 10, 21, 42]),
                "tempo": f"{random.randint(0,3)}:{random.randint(10,59):02d}:{random.randint(0,59):02d}",
                "colocacao": colocacao,
                "pontos": pontos,
                "pontos_povao": random.randint(10, 50) if atleta["modalidade_usuario"] == "povao_pace_livre" else 0,
                "categoria": atleta["categoria"],
                "genero": atleta["genero"],
                "modalidade": atleta["modalidade_usuario"],
                "estado": atleta["estado"],
                "cidade": atleta["cidade"],
                "equipe": atleta["equipe"],
                "status": "aprovado"
            }
            corridas.append(corrida)
    
    if corridas:
        await db.corridas.insert_many(corridas)
    
    return {
        "message": "Dados de teste criados com sucesso!",
        "total_atletas": len(atletas),
        "total_corridas": len(corridas)
    }

# [REFATORADO] /admin/atletas/export migrado para routes/admin_routes.py

@api_router.post("/admin/ajustar-pontos")
async def admin_ajustar_pontos(dados: dict, admin: dict = Depends(get_admin_user)):
    """Admin ajusta pontos de um atleta (adicionar ou remover)"""
    atleta_id = dados.get("atleta_id")
    pontos = dados.get("pontos", 0)
    motivo = dados.get("motivo", "Ajuste administrativo")
    
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Criar corrida de ajuste
    corrida = Corrida(
        usuario_id=atleta_id,
        nome=f"Ajuste Admin: {motivo}",
        colocacao=0,
        tempo="00:00:00",
        pontos=pontos,
        local="Administrativo",
        distancia="N/A",
        data=datetime.now().strftime("%Y-%m-%d"),
        ano=2025
    )
    
    await db.corridas.insert_one(corrida.model_dump())
    await calcular_ranking()
    
    # Notificar atleta
    tipo_ajuste = "adicionados" if pontos > 0 else "removidos"
    await criar_notificacao(
        usuario_id=atleta_id,
        tipo="ajuste",
        titulo=f"Pontos {tipo_ajuste}",
        mensagem=f"Foram {tipo_ajuste} {abs(pontos)} pontos. Motivo: {motivo}",
        dados_extras={"pontos": pontos, "motivo": motivo}
    )
    
    return {"message": f"Pontos ajustados com sucesso! ({pontos:+d} pontos)"}


@api_router.post("/admin/adicionar-corrida")
async def admin_adicionar_corrida(dados: dict, admin: dict = Depends(get_admin_user)):
    """Admin adiciona corrida completa para um atleta"""
    atleta_id = dados.get("atleta_id")
    
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    colocacao = int(dados.get("colocacao", 0))
    pontos = calcular_pontos_colocacao(colocacao, atleta["categoria"])
    
    corrida = Corrida(
        usuario_id=atleta_id,
        nome=dados.get("nome_competicao", ""),
        colocacao=colocacao,
        tempo=dados.get("tempo", "00:00:00"),
        pontos=pontos,
        local=f"{dados.get('cidade_competicao', '')}/{dados.get('estado_competicao', '')}",
        distancia=dados.get("distancia", ""),
        data=dados.get("data_competicao", datetime.now().strftime("%Y-%m-%d")),
        ano=2025
    )
    
    await db.corridas.insert_one(corrida.model_dump())
    await calcular_ranking()
    
    # Notificar atleta
    await criar_notificacao(
        usuario_id=atleta_id,
        tipo="aprovacao",
        titulo="Nova corrida adicionada!",
        mensagem=f"A corrida '{dados.get('nome_competicao')}' foi adicionada ao seu histórico. Você ganhou {pontos} pontos.",
        dados_extras={"pontos": pontos, "competicao": dados.get("nome_competicao")}
    )
    
    # Verificar conquistas
    await verificar_conquistas(atleta_id)
    
    return {"message": "Corrida adicionada com sucesso!", "pontos_adicionados": pontos}


@api_router.put("/admin/corridas/{corrida_id}")
async def admin_update_corrida(corrida_id: str, dados: dict, admin: dict = Depends(get_admin_user)):
    """Admin edita uma corrida existente"""
    corrida = await db.corridas.find_one({"id": corrida_id}, {"_id": 0})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    update_data = {}
    
    if "nome" in dados:
        update_data["nome"] = dados["nome"]
    if "colocacao" in dados:
        update_data["colocacao"] = dados["colocacao"]
        # Recalcular pontos
        atleta = await db.usuarios.find_one({"id": corrida["usuario_id"]}, {"_id": 0})
        if atleta:
            update_data["pontos"] = calcular_pontos_colocacao(dados["colocacao"], atleta["categoria"])
    if "distancia" in dados:
        update_data["distancia"] = dados["distancia"]
    if "data" in dados:
        update_data["data"] = dados["data"]
    if "tempo" in dados:
        update_data["tempo"] = dados["tempo"]
    
    if update_data:
        await db.corridas.update_one({"id": corrida_id}, {"$set": update_data})
        await calcular_ranking()
    
    return {"message": "Corrida atualizada com sucesso!"}


@api_router.delete("/admin/corridas/{corrida_id}")
async def admin_delete_corrida(corrida_id: str, admin: dict = Depends(get_admin_user)):
    """Admin exclui uma corrida"""
    corrida = await db.corridas.find_one({"id": corrida_id}, {"_id": 0})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    await db.corridas.delete_one({"id": corrida_id})
    await calcular_ranking()
    
    return {"message": "Corrida excluída com sucesso!"}

# [REFATORADO] /admin/pendentes/{resultado_id}/foto (DELETE) migrado para routes/admin_routes.py

# ==================== RANKING ENDPOINTS ====================

async def calcular_ranking():
    """Calcula o ranking anual agregando corridas (apenas Profissional/Amador)"""
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
            # IMPORTANTE: Filtrar apenas atletas Profissional/Amador (não Povão)
            modalidade = usuario.get("modalidade_usuario", "profissional_amador")
            if modalidade == "povao_pace_livre":
                continue  # Ignorar atletas do Povão no ranking principal
            
            ranking_docs.append({
                "usuario_id": agg["_id"],
                "ano": ano_atual,
                "pontos_total": agg["pontos_total"],
                "total_corridas": agg["total_corridas"],
                "estado": usuario.get("estado", ""),
                "genero": usuario.get("genero", "M"),
                "categoria": usuario.get("categoria", "normal"),
                "faixa_etaria": usuario.get("faixa_etaria", "Não informado"),
                "modalidade_usuario": modalidade
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


# ==================== RANKING DO POVÃO ====================

async def calcular_ranking_povao():
    """Calcula ranking para modalidade Povão - Pace Livre"""
    await db.ranking_povao.delete_many({"ano": 2025})
    
    # Buscar usuários da modalidade Povão (excluindo PCD e Cadeirante)
    usuarios_povao = await db.usuarios.find({
        "role": "atleta",
        "modalidade_usuario": "povao_pace_livre",
        "categoria": "normal"  # Apenas atletas normais
    }, {"_id": 0}).to_list(None)
    
    ranking_docs = []
    
    for usuario in usuarios_povao:
        corridas = await db.corridas.find({
            "usuario_id": usuario["id"],
            "ano": 2025,
            "modalidade": "povao_pace_livre"
        }, {"_id": 0}).to_list(None)
        
        if not corridas:
            continue
        
        pontos_total = sum(c.get("pontos_povao", 0) for c in corridas)
        total_corridas = len(corridas)
        distancia_acumulada = sum(extrair_distancia_km(c.get("distancia", "5KM")) for c in corridas)
        
        ranking_docs.append(RankingPovao(
            usuario_id=usuario["id"],
            ano=2025,
            pontos_total=pontos_total,
            total_corridas=total_corridas,
            distancia_acumulada=distancia_acumulada,
            estado=usuario["estado"],
            genero=usuario["genero"]
        ).model_dump())
    
    # Ordenar: 1º Pontos, 2º Nº Provas, 3º Distância acumulada
    ranking_docs.sort(key=lambda x: (-x["pontos_total"], -x["total_corridas"], -x["distancia_acumulada"]))
    
    # Atribuir posições por gênero
    for genero in ["M", "F"]:
        genero_docs = [r for r in ranking_docs if r["genero"] == genero]
        for i, doc in enumerate(genero_docs, 1):
            doc["ranking_genero"] = i
    
    # Atribuir posição geral
    for i, doc in enumerate(ranking_docs, 1):
        doc["ranking_geral"] = i
    
    if ranking_docs:
        await db.ranking_povao.insert_many(ranking_docs)
    
    return len(ranking_docs)


# [REFATORADO] Endpoints /ranking/povao e /ranking/povao/stats migrados para routes/ranking_routes.py
# [REFATORADO] Endpoints /ranking/semanal, /ranking/mensal, /ranking/destaque-mes migrados para routes/ranking_routes.py


@api_router.get("/ranking/destaque-mes")
async def get_destaque_mes(mes: int = None, ano: int = None):
    """Retorna os destaques do mês (top 3 de cada categoria + estatísticas)"""
    
    hoje = datetime.now()
    mes_atual = mes or hoje.month
    ano_atual = ano or hoje.year
    
    # Calcular início e fim do mês
    inicio_mes = f"{ano_atual}-{mes_atual:02d}-01"
    if mes_atual == 12:
        fim_mes = f"{ano_atual + 1}-01-01"
    else:
        fim_mes = f"{ano_atual}-{mes_atual + 1:02d}-01"
    
    meses_nome = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    categorias = [
        ("Masculino", "normal", "M"),
        ("Feminino", "normal", "F"),
        ("PCD Masculino", "pcd", "M"),
        ("PCD Feminino", "pcd", "F"),
        ("Cadeirante Masculino", "cadeirante", "M"),
        ("Cadeirante Feminino", "cadeirante", "F")
    ]
    
    destaques = {}
    
    for nome_cat, cat_db, gen_db in categorias:
        # Buscar corridas do mês para esta categoria
        pipeline = [
            {"$match": {
                "data": {"$gte": inicio_mes, "$lt": fim_mes}
            }},
            {"$group": {
                "_id": "$usuario_id",
                "pontos_mes": {"$sum": "$pontos"},
                "corridas_mes": {"$sum": 1}
            }},
            {"$sort": {"pontos_mes": -1}}
        ]
        
        agregados = await db.corridas.aggregate(pipeline).to_list(None)
        
        top3 = []
        for agg in agregados:
            usuario = await db.usuarios.find_one({"id": agg["_id"]}, {"_id": 0})
            if usuario and usuario.get("categoria") == cat_db and usuario.get("genero") == gen_db:
                top3.append({
                    "atleta_id": agg["_id"],
                    "nome": usuario["nome"],
                    "equipe": usuario["equipe"],
                    "cidade": usuario["cidade"],
                    "estado": usuario["estado"],
                    "foto_url": usuario.get("foto_url", ""),
                    "pontos_mes": agg["pontos_mes"],
                    "corridas_mes": agg["corridas_mes"]
                })
                if len(top3) >= 3:
                    break
        
        destaques[nome_cat] = top3
    
    # Estatísticas gerais do mês
    total_corridas_mes = await db.corridas.count_documents({
        "data": {"$gte": inicio_mes, "$lt": fim_mes}
    })
    
    # Atleta mais ativo do mês (mais corridas)
    pipeline_mais_ativo = [
        {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
        {"$group": {"_id": "$usuario_id", "total_corridas": {"$sum": 1}}},
        {"$sort": {"total_corridas": -1}},
        {"$limit": 1}
    ]
    mais_ativo_result = await db.corridas.aggregate(pipeline_mais_ativo).to_list(1)
    
    mais_ativo = None
    if mais_ativo_result:
        usuario_ativo = await db.usuarios.find_one({"id": mais_ativo_result[0]["_id"]}, {"_id": 0})
        if usuario_ativo:
            mais_ativo = {
                "atleta_id": mais_ativo_result[0]["_id"],
                "nome": usuario_ativo["nome"],
                "equipe": usuario_ativo["equipe"],
                "foto_url": usuario_ativo.get("foto_url", ""),
                "total_corridas": mais_ativo_result[0]["total_corridas"]
            }
    
    # Atleta com mais pontos no mês (geral)
    pipeline_mais_pontos = [
        {"$match": {"data": {"$gte": inicio_mes, "$lt": fim_mes}}},
        {"$group": {"_id": "$usuario_id", "total_pontos": {"$sum": "$pontos"}}},
        {"$sort": {"total_pontos": -1}},
        {"$limit": 1}
    ]
    mais_pontos_result = await db.corridas.aggregate(pipeline_mais_pontos).to_list(1)
    
    mais_pontos = None
    if mais_pontos_result:
        usuario_pontos = await db.usuarios.find_one({"id": mais_pontos_result[0]["_id"]}, {"_id": 0})
        if usuario_pontos:
            mais_pontos = {
                "atleta_id": mais_pontos_result[0]["_id"],
                "nome": usuario_pontos["nome"],
                "equipe": usuario_pontos["equipe"],
                "foto_url": usuario_pontos.get("foto_url", ""),
                "total_pontos": mais_pontos_result[0]["total_pontos"]
            }
    
    return {
        "mes": meses_nome[mes_atual],
        "ano": ano_atual,
        "total_corridas_mes": total_corridas_mes,
        "destaques_categoria": destaques,
        "mais_ativo_mes": mais_ativo,
        "mais_pontos_mes": mais_pontos
    }

@api_router.get("/ranking/categoria/{categoria}/{genero}", response_model=List[RankingResponse])
async def get_ranking_por_categoria(
    categoria: str, 
    genero: str, 
    ano: int = Query(2025),
    faixa: Optional[str] = None,
    equipe: Optional[str] = None,
    cidade: Optional[str] = None
):
    """Retorna ranking por categoria (apenas Profissional/Amador)"""
    cat_map = {
        "masculino": ("normal", "M"),
        "feminino": ("normal", "F"),
        "pcd-m": ("pcd", "M"),
        "pcd-f": ("pcd", "F"),
        "cadeirante-m": ("cadeirante", "M"),
        "cadeirante-f": ("cadeirante", "F")
    }
    
    cat_db, gen_db = cat_map.get(categoria, ("normal", "M"))
    
    query = {"ano": ano, "categoria": cat_db, "genero": gen_db}
    if faixa:
        query["faixa_etaria"] = faixa
    
    ranking_list = await db.ranking_anual.find(
        query,
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    response = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            # IMPORTANTE: Garantir que atletas do Povão não apareçam no ranking Profissional
            modalidade = usuario.get("modalidade_usuario", "profissional_amador")
            if modalidade == "povao_pace_livre":
                continue  # Ignorar atletas do Povão
            
            # Filtros adicionais
            if equipe and equipe.lower() not in usuario["equipe"].lower():
                continue
            if cidade and cidade.lower() not in usuario["cidade"].lower():
                continue
            
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

@api_router.get("/ranking/historico/{ano}")
async def get_ranking_historico(ano: int, categoria: str = "masculino"):
    """Retorna ranking de um ano específico"""
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
            response.append({
                "colocacao": rank.get("ranking_categoria", 0),
                "nome": usuario["nome"],
                "equipe": usuario["equipe"],
                "pontos": rank["pontos_total"],
                "corridas": rank["total_corridas"]
            })
    
    return {"ano": ano, "categoria": categoria, "ranking": response}

@api_router.get("/ranking/anos-disponiveis")
async def get_anos_disponiveis():
    """Lista anos com dados de ranking"""
    pipeline = [
        {"$group": {"_id": "$ano"}},
        {"$sort": {"_id": -1}}
    ]
    result = await db.ranking_anual.aggregate(pipeline).to_list(None)
    return {"anos": [r["_id"] for r in result]}

@api_router.get("/ranking/export/csv")
async def export_ranking_csv(categoria: str = "masculino", todas_modalidades: bool = False):
    """Exporta ranking em CSV - todas modalidades ou uma específica"""
    
    modalidades = [
        ("Masculino", "normal", "M"),
        ("Feminino", "normal", "F"),
        ("PCD Masculino", "pcd", "M"),
        ("PCD Feminino", "pcd", "F"),
        ("Cadeirante Masculino", "cadeirante", "M"),
        ("Cadeirante Feminino", "cadeirante", "F")
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if todas_modalidades:
        # Exportar todas as modalidades
        for nome_mod, cat_db, gen_db in modalidades:
            writer.writerow([f"=== {nome_mod} ==="])
            writer.writerow(["Colocação", "Nome", "Equipe", "Cidade", "UF", "Faixa", "Corridas", "Pontos"])
            
            ranking_list = await db.ranking_anual.find(
                {"ano": 2025, "categoria": cat_db, "genero": gen_db},
                {"_id": 0}
            ).sort("pontos_total", -1).to_list(None)
            
            for rank in ranking_list:
                usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
                if usuario:
                    writer.writerow([
                        rank.get("ranking_categoria", 0),
                        usuario["nome"],
                        usuario["equipe"],
                        usuario["cidade"],
                        usuario["estado"],
                        rank["faixa_etaria"],
                        rank["total_corridas"],
                        rank["pontos_total"]
                    ])
            writer.writerow([])  # Linha em branco entre modalidades
    else:
        # Exportar apenas uma categoria
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
        
        writer.writerow(["Colocação", "Nome", "Equipe", "Cidade", "UF", "Faixa", "Corridas", "Pontos"])
        
        for rank in ranking_list:
            usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
            if usuario:
                writer.writerow([
                    rank.get("ranking_categoria", 0),
                    usuario["nome"],
                    usuario["equipe"],
                    usuario["cidade"],
                    usuario["estado"],
                    rank["faixa_etaria"],
                    rank["total_corridas"],
                    rank["pontos_total"]
                ])
    
    output.seek(0)
    filename = "ranking_todas_modalidades.csv" if todas_modalidades else f"ranking_{categoria}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@api_router.get("/ranking/export/excel")
async def export_ranking_excel(categoria: str = "masculino", todas_modalidades: bool = False):
    """Exporta ranking em Excel - todas modalidades ou uma específica"""
    
    wb = Workbook()
    
    modalidades = [
        ("Masculino", "normal", "M"),
        ("Feminino", "normal", "F"),
        ("PCD Masculino", "pcd", "M"),
        ("PCD Feminino", "pcd", "F"),
        ("Cadeirante Masculino", "cadeirante", "M"),
        ("Cadeirante Feminino", "cadeirante", "F")
    ]
    
    header_fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    if todas_modalidades:
        # Criar uma aba para cada modalidade
        first_sheet = True
        for nome_mod, cat_db, gen_db in modalidades:
            if first_sheet:
                ws = wb.active
                ws.title = nome_mod
                first_sheet = False
            else:
                ws = wb.create_sheet(title=nome_mod)
            
            headers = ["Colocação", "Nome", "Equipe", "Cidade", "UF", "Faixa", "Corridas", "Pontos"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")
            
            ranking_list = await db.ranking_anual.find(
                {"ano": 2025, "categoria": cat_db, "genero": gen_db},
                {"_id": 0}
            ).sort("pontos_total", -1).to_list(None)
            
            for rank in ranking_list:
                usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
                if usuario:
                    ws.append([
                        rank.get("ranking_categoria", 0),
                        usuario["nome"],
                        usuario["equipe"],
                        usuario["cidade"],
                        usuario["estado"],
                        rank["faixa_etaria"],
                        rank["total_corridas"],
                        rank["pontos_total"]
                    ])
    else:
        # Exportar apenas uma categoria
        cat_map = {
            "masculino": ("normal", "M"),
            "feminino": ("normal", "F"),
            "pcd-m": ("pcd", "M"),
            "pcd-f": ("pcd", "F"),
            "cadeirante-m": ("cadeirante", "M"),
            "cadeirante-f": ("cadeirante", "F")
        }
        
        cat_db, gen_db = cat_map.get(categoria, ("normal", "M"))
        
        ws = wb.active
        ws.title = f"Ranking {categoria.title()}"
        
        headers = ["Colocação", "Nome", "Equipe", "Cidade", "UF", "Faixa", "Corridas", "Pontos"]
        ws.append(headers)
        
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        
        ranking_list = await db.ranking_anual.find(
            {"ano": 2025, "categoria": cat_db, "genero": gen_db},
            {"_id": 0}
        ).sort("pontos_total", -1).to_list(None)
        
        for rank in ranking_list:
            usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
            if usuario:
                ws.append([
                    rank.get("ranking_categoria", 0),
                    usuario["nome"],
                    usuario["equipe"],
                    usuario["cidade"],
                    usuario["estado"],
                    rank["faixa_etaria"],
                    rank["total_corridas"],
                    rank["pontos_total"]
                ])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = "ranking_todas_modalidades.xlsx" if todas_modalidades else f"ranking_{categoria}.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==================== ATLETAS ENDPOINTS ====================

@api_router.get("/atletas/{atleta_id}", response_model=AtletaDetalhes)
async def get_atleta_detalhes(atleta_id: str):
    usuario = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    modalidade_usuario = usuario.get("modalidade_usuario", "profissional_amador")
    
    # Buscar ranking de acordo com a modalidade
    if modalidade_usuario == "povao_pace_livre":
        ranking = await db.ranking_povao.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
        # Para Povão, mostrar a posição no ranking
        melhor_colocacao = ranking.get("ranking_genero", 0) if ranking else 0
        total_corridas = ranking["total_corridas"] if ranking else 0
        pontos_carreira = ranking["pontos_total"] if ranking else 0
    else:
        ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
        # Para Profissional/Amador, mostrar a posição no ranking (não a melhor colocação em corrida)
        melhor_colocacao = ranking.get("ranking_categoria", 0) if ranking else 0
        total_corridas = ranking["total_corridas"] if ranking else 0
        pontos_carreira = ranking["pontos_total"] if ranking else 0
    
    min_corridas = get_min_corridas_categoria(usuario.get("categoria", "normal"))
    
    return AtletaDetalhes(
        id=usuario["id"],
        nome=usuario["nome"],
        cidade=usuario.get("cidade", ""),
        estado=usuario.get("estado", ""),
        genero=usuario.get("genero", ""),
        categoria=usuario.get("categoria", "normal"),
        faixa_etaria=usuario.get("faixa_etaria", "Não informado"),
        foto_url=usuario.get("foto_url", ""),
        equipe=usuario.get("equipe", ""),
        pontos_carreira=pontos_carreira,
        total_corridas=total_corridas,
        melhor_colocacao=melhor_colocacao,
        is_pendente=(total_corridas < min_corridas),
        bio=usuario.get("bio", ""),
        apelido=usuario.get("apelido", ""),
        etnia=usuario.get("etnia", ""),
        instagram_url=usuario.get("instagram_url", ""),
        facebook_url=usuario.get("facebook_url", ""),
        modalidade_usuario=modalidade_usuario,
        role=usuario.get("role", "atleta"),
        is_dono_assessoria=usuario.get("is_dono_assessoria", False),
        assessoria_nome=usuario.get("assessoria_nome")
    )

@api_router.get("/atletas/{atleta_id}/corridas", response_model=List[CorridaResponse])
async def get_atleta_corridas(atleta_id: str):
    corridas = await db.corridas.find(
        {"usuario_id": atleta_id},
        {"_id": 0}
    ).sort("data", -1).to_list(None)
    
    # Handle legacy/seed data format - normalize fields
    result = []
    for corrida in corridas:
        try:
            # Map prova to nome if nome is missing
            nome = corrida.get("nome") or corrida.get("prova", "Corrida")
            # Ensure distancia is string
            distancia = corrida.get("distancia", "")
            if isinstance(distancia, (int, float)):
                distancia = f"{distancia}KM"
            # Ensure local exists
            local = corrida.get("local", "")
            if not local:
                cidade = corrida.get("cidade", "")
                estado = corrida.get("estado", "")
                local = f"{cidade}/{estado}" if cidade else "Local não informado"
            
            result.append(CorridaResponse(
                id=corrida.get("id", ""),
                nome=nome,
                colocacao=corrida.get("colocacao", 0),
                tempo=corrida.get("tempo", "00:00:00"),
                pontos=corrida.get("pontos", 0),
                local=local,
                distancia=distancia,
                data=corrida.get("data", "")
            ))
        except Exception as e:
            # Skip invalid corrida records
            logging.warning(f"Skipping invalid corrida record: {e}")
            continue
    
    return result

@api_router.get("/atletas/{atleta_id}/evolucao", response_model=List[EvolucaoMensal])
async def get_evolucao_atleta(atleta_id: str):
    """Retorna evolução mensal do atleta para gráficos"""
    corridas = await db.corridas.find(
        {"usuario_id": atleta_id, "ano": 2025},
        {"_id": 0}
    ).sort("data", 1).to_list(None)
    
    evolucao_dict = {}
    for corrida in corridas:
        mes = corrida["data"][:7]
        if mes not in evolucao_dict:
            evolucao_dict[mes] = {"pontos": 0, "corridas": 0}
        evolucao_dict[mes]["pontos"] += corrida["pontos"]
        evolucao_dict[mes]["corridas"] += 1
    
    evolucao = [
        EvolucaoMensal(mes=mes, pontos=dados["pontos"], corridas=dados["corridas"])
        for mes, dados in sorted(evolucao_dict.items())
    ]
    
    return evolucao

@api_router.get("/atletas/{atleta_id}/compartilhar")
async def get_compartilhar_atleta(atleta_id: str):
    """Gera dados para compartilhamento nas redes sociais"""
    usuario = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": 2025}, {"_id": 0})
    
    categoria_nome = {
        "normal": "Normal",
        "pcd": "PCD",
        "cadeirante": "Cadeirante"
    }.get(usuario["categoria"], "Normal")
    
    genero_nome = "Masculino" if usuario["genero"] == "M" else "Feminino"
    
    texto_compartilhar = "🏆 Ranking Run Pró 2025\n\n"
    texto_compartilhar += f"👤 {usuario['nome']}\n"
    texto_compartilhar += f"🏅 {ranking['ranking_categoria'] if ranking else 0}º lugar - {categoria_nome} {genero_nome}\n"
    texto_compartilhar += f"⭐ {ranking['pontos_total'] if ranking else 0} pontos\n"
    texto_compartilhar += f"🏃 {ranking['total_corridas'] if ranking else 0} corridas\n\n"
    texto_compartilhar += "#RankingRunPro #Corrida #Running"
    
    return {
        "atleta": usuario["nome"],
        "colocacao": ranking["ranking_categoria"] if ranking else 0,
        "categoria": f"{categoria_nome} {genero_nome}",
        "pontos": ranking["pontos_total"] if ranking else 0,
        "corridas": ranking["total_corridas"] if ranking else 0,
        "texto_whatsapp": texto_compartilhar,
        "url_compartilhar": f"https://community-feed-28.preview.emergentagent.com/atleta/{atleta_id}"
    }


# ==================== OUTROS ====================

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

@api_router.get("/ranking/faixas-etarias")
async def get_faixas_disponiveis():
    """Lista faixas etárias disponíveis"""
    return {
        "faixas": ["0-11", "12-17", "18-29", "30-39", "40-49", "50-59", "60+"]
    }

@api_router.get("/ranking/equipes")
async def get_equipes_disponiveis():
    """Lista equipes disponíveis (nomes únicos)"""
    pipeline = [
        {"$match": {"role": "atleta", "equipe": {"$ne": "", "$exists": True}}},
        {"$group": {"_id": "$equipe"}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    # Retorna array direto para facilitar uso no frontend
    return [e["_id"] for e in result if e["_id"] and e["_id"].lower() != 'sem equipe']

# [REFATORADO] /assessorias/lista migrado para routes/assessorias_routes.py

@api_router.get("/")
async def root():
    return {"message": "Ranking Run Pro API"}

@api_router.post("/admin/sync-resultados-atletas")
async def sync_resultados_atletas(admin: dict = Depends(get_admin_user)):
    """Gera resultados de teste para todos os atletas cadastrados, sincronizando as modalidades"""
    import random
    from datetime import datetime
    
    # Recalcular rankings existentes
    total_ranking = await calcular_ranking()
    total_povao = await calcular_ranking_povao()
    
    return {
        "message": "Rankings recalculados com sucesso!",
        "ranking_profissional": total_ranking,
        "ranking_povao": total_povao
    }

@api_router.post("/admin/recalcular-rankings")
async def recalcular_rankings(admin: dict = Depends(get_admin_user)):
    """Recalcula todos os rankings (Profissional/Amador e Povão)"""
    total_ranking = await calcular_ranking()
    total_povao = await calcular_ranking_povao()
    
    return {
        "message": "Rankings recalculados com sucesso!",
        "ranking_profissional": total_ranking,
        "ranking_povao": total_povao
    }

@api_router.post("/admin/setup-assessoria-dono/{equipe_nome}")
async def setup_assessoria_dono(
    equipe_nome: str,
    admin: dict = Depends(get_admin_user)
):
    """Setup de teste: define um atleta como dono e adiciona dados da assessoria"""
    import urllib.parse
    nome_decoded = urllib.parse.unquote(equipe_nome)
    
    # Buscar primeiro atleta da equipe
    atleta = await db.usuarios.find_one(
        {"equipe": nome_decoded, "role": "atleta"},
        {"_id": 0}
    )
    
    if not atleta:
        raise HTTPException(status_code=404, detail="Nenhum atleta encontrado nesta equipe")
    
    # Promover a dono de assessoria
    await db.usuarios.update_one(
        {"id": atleta["id"]},
        {"$set": {"role": "dono_assessoria", "is_dono_assessoria": True}}
    )
    
    # Criar/atualizar registro da assessoria
    await db.assessorias.update_one(
        {"nome": nome_decoded},
        {"$set": {
            "nome": nome_decoded,
            "cidade": atleta.get("cidade", ""),
            "estado": atleta.get("estado", ""),
            "dono_id": atleta["id"],
            "dono_nome": atleta["nome"],
            "mensagem_bio": f"Ajudamos milhares de Atletas pelo Brasil, faça parte do nosso Time!",
            "foto_url": "",
            "status": "ativa"
        }},
        upsert=True
    )
    
    return {
        "message": f"Assessoria {nome_decoded} configurada com sucesso!",
        "dono": atleta["nome"],
        "dono_id": atleta["id"]
    }

@api_router.post("/ranking/popular")
async def popular_ranking_dados_teste():
    """Popula banco com 15 atletas por modalidade (90 atletas total) com corridas"""
    
    # Limpar dados existentes
    await db.usuarios.delete_many({"role": "atleta"})
    await db.corridas.delete_many({})
    await db.ranking_anual.delete_many({})
    await db.resultados_pendentes.delete_many({})
    await db.notificacoes.delete_many({})
    await db.conquistas_atleta.delete_many({})
    
    # Manter admin
    admin_exists = await db.usuarios.find_one({"email": "admin@runpro.com"})
    if not admin_exists:
        admin = Usuario(
            nome="Administrador",
            email="admin@runpro.com",
            password_hash=get_password_hash("admin123"),
            equipe="Run Pró",
            cidade="São Paulo",
            estado="SP",
            genero="M",
            categoria="normal",
            data_nascimento="1985-01-01",
            faixa_etaria="30-39",
            foto_url=gerar_foto_url("Admin"),
            role="admin"
        )
        await db.usuarios.insert_one(admin.model_dump())
    
    # Nomes brasileiros
    nomes_masculinos = [
        "João Silva", "Pedro Santos", "Lucas Oliveira", "Matheus Costa", "Gabriel Souza",
        "Rafael Lima", "Felipe Pereira", "Bruno Almeida", "Daniel Rodrigues", "Thiago Fernandes",
        "Gustavo Martins", "André Ribeiro", "Carlos Eduardo", "Fernando Gomes", "Leonardo Carvalho",
        "Marcos Vinícius", "Paulo Ricardo", "Ricardo Barbosa", "Vinícius Nunes", "Alexandre Moreira"
    ]
    
    nomes_femininos = [
        "Maria Silva", "Ana Santos", "Juliana Oliveira", "Camila Costa", "Fernanda Souza",
        "Patrícia Lima", "Bruna Pereira", "Carolina Almeida", "Débora Rodrigues", "Érica Fernandes",
        "Gabriela Martins", "Helena Ribeiro", "Isabela Gomes", "Jéssica Carvalho", "Larissa Barbosa",
        "Mariana Nunes", "Natália Moreira", "Paula Mendes", "Renata Araújo", "Tatiana Rocha"
    ]
    
    equipes = [
        "Runners BR", "Maratona Club", "Speed Team", "Força Atlética", "Corrida Livre",
        "Team Run", "Atletas Unidos", "Fast Runners", "Elite Running", "Pro Runners",
        "Corredores SP", "Run Fast", "Vitória Runners", "Campinas Running", "BH Runners"
    ]
    
    estados = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "CE", "GO", "DF", "ES"]
    
    cidades_por_estado = {
        "SP": ["São Paulo", "Campinas", "Santos", "Ribeirão Preto", "Sorocaba"],
        "RJ": ["Rio de Janeiro", "Niterói", "Petrópolis", "Campos", "Nova Iguaçu"],
        "MG": ["Belo Horizonte", "Uberlândia", "Juiz de Fora", "Contagem", "Ouro Preto"],
        "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Canoas", "Santa Maria"],
        "PR": ["Curitiba", "Londrina", "Maringá", "Foz do Iguaçu", "Cascavel"],
        "SC": ["Florianópolis", "Joinville", "Blumenau", "Balneário Camboriú", "Chapecó"],
        "BA": ["Salvador", "Feira de Santana", "Vitória da Conquista", "Ilhéus", "Camaçari"],
        "PE": ["Recife", "Olinda", "Jaboatão", "Caruaru", "Petrolina"],
        "CE": ["Fortaleza", "Caucaia", "Juazeiro do Norte", "Sobral", "Maracanaú"],
        "GO": ["Goiânia", "Aparecida de Goiânia", "Anápolis", "Rio Verde", "Luziânia"],
        "DF": ["Brasília", "Taguatinga", "Ceilândia", "Gama", "Planaltina"],
        "ES": ["Vitória", "Vila Velha", "Serra", "Cariacica", "Linhares"]
    }
    
    competicoes = [
        "Maratona de São Paulo", "Meia Maratona Internacional do Rio", "Corrida de Reis",
        "Maratona de Porto Alegre", "São Silvestre", "Volta da Pampulha",
        "Maratona de Curitiba", "Meia Maratona de Brasília", "Circuito das Estações",
        "Night Run", "Maratona de Salvador", "Corrida do Soldado",
        "Maratona do Rio", "Meia Maratona de Florianópolis", "Corrida Cidade de Campinas",
        "Run 21K", "Maratona Internacional de Foz do Iguaçu", "Corrida Duque de Caxias"
    ]
    
    distancias = ["5KM", "10KM", "21KM", "42KM"]
    
    def gerar_data_nascimento():
        ano = random.randint(1960, 2010)
        mes = random.randint(1, 12)
        dia = random.randint(1, 28)
        return f"{ano}-{mes:02d}-{dia:02d}"
    
    modalidades = [
        ("normal", "M"),
        ("normal", "F"),
        ("pcd", "M"),
        ("pcd", "F"),
        ("cadeirante", "M"),
        ("cadeirante", "F")
    ]
    
    atletas_criados = 0
    corridas_criadas = 0
    
    for cat, gen in modalidades:
        nomes = nomes_masculinos if gen == "M" else nomes_femininos
        random.shuffle(nomes)
        
        for i in range(15):
            nome = f"{nomes[i % len(nomes)]} {random.choice(['Jr.', 'Filho', 'Neto', ''])}".strip()
            if i >= len(nomes):
                nome = f"{nomes[i % len(nomes)]} {random.randint(1, 99)}"
            
            estado = random.choice(estados)
            cidade = random.choice(cidades_por_estado[estado])
            data_nasc = gerar_data_nascimento()
            
            atleta = Usuario(
                nome=nome,
                email=f"{nome.lower().replace(' ', '.').replace('.', '')}_{cat}_{i}@email.com",
                password_hash=get_password_hash("atleta123"),
                equipe=random.choice(equipes),
                cidade=cidade,
                estado=estado,
                genero=gen,
                categoria=cat,
                data_nascimento=data_nasc,
                faixa_etaria=calcular_faixa_etaria(data_nasc),
                foto_url=gerar_foto_url(nome),
                role="atleta"
            )
            
            await db.usuarios.insert_one(atleta.model_dump())
            atletas_criados += 1
            
            if cat in ["pcd", "cadeirante"]:
                num_corridas = random.randint(6, 12)
                max_colocacao = 3
            else:
                num_corridas = random.randint(8, 18)
                max_colocacao = 10
            
            meses_usados = []
            for j in range(num_corridas):
                mes = random.randint(1, 11)
                while mes in meses_usados and len(meses_usados) < 11:
                    mes = random.randint(1, 11)
                meses_usados.append(mes)
                
                dia = random.randint(1, 28)
                data_corrida = f"2025-{mes:02d}-{dia:02d}"
                
                colocacao = random.randint(1, max_colocacao)
                pontos = calcular_pontos_colocacao(colocacao, cat)
                
                distancia = random.choice(distancias)
                if distancia == "5KM":
                    tempo = f"00:{random.randint(18, 35)}:{random.randint(0, 59):02d}"
                elif distancia == "10KM":
                    tempo = f"00:{random.randint(35, 60)}:{random.randint(0, 59):02d}"
                elif distancia == "21KM":
                    tempo = f"01:{random.randint(25, 55)}:{random.randint(0, 59):02d}"
                else:
                    tempo = f"0{random.randint(3, 5)}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
                
                corrida = Corrida(
                    usuario_id=atleta.id,
                    nome=random.choice(competicoes),
                    colocacao=colocacao,
                    tempo=tempo,
                    pontos=pontos,
                    local=f"{random.choice(list(cidades_por_estado.values())[0])}/{random.choice(estados)}",
                    distancia=distancia,
                    data=data_corrida,
                    ano=2025
                )
                
                await db.corridas.insert_one(corrida.model_dump())
                corridas_criadas += 1
    
    await calcular_ranking()
    
    # Verificar conquistas para todos os atletas
    atletas = await db.usuarios.find({"role": "atleta"}, {"_id": 0}).to_list(None)
    for atleta in atletas:
        await verificar_conquistas(atleta["id"])
    
    return {
        "message": "Dados populados com sucesso!",
        "atletas_criados": atletas_criados,
        "corridas_criadas": corridas_criadas
    }


# ==================== ANIVERSARIANTES ====================
# [REFATORADO] Endpoints migrados para routes/aniversariantes_routes.py:
# - /admin/aniversariantes (GET)
# - /admin/aniversariantes/hoje (GET)
# - /admin/aniversariantes/semana (GET)
# - /admin/aniversariantes/enviar-mensagem (POST)
# - /admin/aniversariantes/enviar-agora (POST)
# - /admin/aniversariantes/enviar-email-massa (POST)
# - /admin/aniversariantes/configuracao (GET, PUT)
# - /admin/aniversariantes/historico (GET) [antigo /admin/aniversariantes/logs]



# ========== RANKING RUN INSIDE - INSTAGRAM ANALYTICS (SISTEMA HÍBRIDO) ==========

def calcular_metricas_automaticas(seguidores: int, seguindo: int, total_posts: int, nicho: str = "corrida") -> dict:
    """
    Calcula automaticamente todas as métricas baseado em dados básicos.
    Usa benchmarks do nicho e proporções conhecidas.
    """
    # Benchmarks por nicho (engagement rate médio, posts/semana típico)
    benchmarks = {
        "corrida": {"er": 3.5, "posts_semana": 4.5, "ratio_likes_comments": 50},
        "fitness": {"er": 3.0, "posts_semana": 5.0, "ratio_likes_comments": 40},
        "lifestyle": {"er": 2.5, "posts_semana": 4.0, "ratio_likes_comments": 35},
        "moda": {"er": 2.0, "posts_semana": 5.0, "ratio_likes_comments": 30},
        "gastronomia": {"er": 4.0, "posts_semana": 3.5, "ratio_likes_comments": 25},
        "viagem": {"er": 3.5, "posts_semana": 3.0, "ratio_likes_comments": 40},
        "tech": {"er": 2.0, "posts_semana": 4.0, "ratio_likes_comments": 60},
        "outros": {"er": 2.5, "posts_semana": 4.0, "ratio_likes_comments": 40}
    }
    
    bench = benchmarks.get(nicho, benchmarks["outros"])
    
    # Calcular engagement rate estimado baseado no tamanho da conta
    # Contas menores geralmente têm ER maior
    if seguidores < 1000:
        er_modifier = 1.5
    elif seguidores < 10000:
        er_modifier = 1.2
    elif seguidores < 100000:
        er_modifier = 1.0
    elif seguidores < 1000000:
        er_modifier = 0.7
    else:
        er_modifier = 0.4
    
    estimated_er = bench["er"] * er_modifier
    
    # Calcular média de likes baseado no ER estimado
    media_likes = (seguidores * estimated_er / 100)
    
    # Calcular média de comentários (proporção típica likes/comments)
    media_comentarios = media_likes / bench["ratio_likes_comments"]
    
    # Estimar posts por semana baseado no total de posts
    # Assumindo conta ativa há pelo menos 1 ano
    posts_por_semana = min(total_posts / 52, bench["posts_semana"] * 1.5) if total_posts > 0 else bench["posts_semana"]
    
    # Estimar views de reels (geralmente 2-5x os likes)
    media_views_reels = media_likes * 3
    
    # Calcular ratio followers/following para detecção de anomalias
    ratio_ff = seguidores / seguindo if seguindo > 0 else seguidores
    
    # Indicadores anti-fake baseados em proporções
    picos_anormais = 0
    comentarios_repetitivos = 0
    horarios_artificiais = 0
    
    # Verificar proporção suspeita followers/following
    if ratio_ff < 0.5:  # Seguindo muito mais do que seguidores
        picos_anormais += 2
    elif ratio_ff > 100:  # Muito mais seguidores do que seguindo (pode ser compra)
        if seguidores < 10000:  # Só é suspeito em contas pequenas
            picos_anormais += 1
    
    # Verificar proporção posts/seguidores
    posts_per_follower = total_posts / seguidores if seguidores > 0 else 0
    if posts_per_follower > 0.1:  # Muito mais posts do que seguidores
        comentarios_repetitivos += 1
    
    # Estimar desvio de engajamento (quanto mais estável, melhor)
    desvio_engajamento = 15 + (10 if ratio_ff < 1 else 0)  # Valor estimado
    
    # Calcular crescimento estimado
    if estimated_er > 5:
        crescimento = 3.0
    elif estimated_er > 3:
        crescimento = 2.0
    elif estimated_er > 1:
        crescimento = 1.0
    else:
        crescimento = 0.5
    
    # Ajustar crescimento pelo tamanho
    if seguidores < 10000:
        crescimento *= 1.5
    elif seguidores > 100000:
        crescimento *= 0.5
    
    # Distribuição de formatos típica
    percentual_reels = 45 + random.randint(-10, 10)
    percentual_carrossel = 30 + random.randint(-10, 10)
    percentual_foto = 100 - percentual_reels - percentual_carrossel
    
    return {
        "engagement_rate": round(estimated_er, 2),
        "media_likes": round(media_likes, 1),
        "media_comentarios": round(media_comentarios, 1),
        "media_views_reels": round(media_views_reels, 1),
        "posts_por_semana": round(posts_por_semana, 1),
        "crescimento_30_dias": round(crescimento, 1),
        "percentual_reels": percentual_reels,
        "percentual_carrossel": percentual_carrossel,
        "percentual_foto": percentual_foto,
        "picos_anormais": picos_anormais,
        "comentarios_repetitivos": comentarios_repetitivos,
        "horarios_artificiais": horarios_artificiais,
        "desvio_engajamento": round(desvio_engajamento, 1),
        "ratio_followers_following": round(ratio_ff, 2)
    }


def analisar_bio_automatico(bio: str) -> dict:
    """
    Analisa automaticamente a bio do Instagram.
    Retorna scores para: descrição, keywords, CTA, link, clareza.
    """
    if not bio:
        return {
            "tem_descricao": False,
            "tem_keywords": False,
            "tem_cta": False,
            "tem_link": False,
            "clareza": "ruim",
            "nota": 0
        }
    
    bio_lower = bio.lower()
    
    # Keywords comuns de corrida/fitness
    keywords_nicho = ['corrida', 'runner', 'running', 'maratona', 'atleta', 'corredor', 
                      'treino', 'fitness', 'personal', 'coach', 'assessoria', 'km', 
                      'pace', 'trilha', 'ultra', 'meia maratona', '10k', '21k', '42k',
                      'crossfit', 'musculação', 'gym', 'academia', 'esporte', 'sport']
    
    # CTAs comuns
    ctas = ['link', 'clique', 'acesse', 'saiba mais', 'conheça', 'siga', 'inscreva', 
            'compre', 'whatsapp', 'contato', 'agenda', 'agende', 'participe', 'baixe',
            'bio', 'dm', 'direct', '👇', '⬇️', 'linktree']
    
    tem_descricao = len(bio) > 20
    tem_keywords = any(kw in bio_lower for kw in keywords_nicho)
    tem_cta = any(cta in bio_lower for cta in ctas)
    tem_link = 'http' in bio_lower or 'link' in bio_lower or '.com' in bio_lower or 'wa.me' in bio_lower or '.br' in bio_lower
    
    # Avaliar clareza baseado em estrutura
    linhas = bio.split('\n')
    tem_emojis = any(ord(c) > 127 for c in bio)
    bem_estruturado = len(linhas) >= 2 or tem_emojis
    
    if len(bio) > 100 and bem_estruturado and tem_keywords:
        clareza = "excelente"
    elif len(bio) > 50 and (bem_estruturado or tem_keywords):
        clareza = "boa"
    elif len(bio) > 20:
        clareza = "regular"
    else:
        clareza = "ruim"
    
    # Calcular nota da bio
    clareza_scores = {"excelente": 2.0, "boa": 1.5, "regular": 1.0, "ruim": 0.0}
    nota = (
        (1.5 if tem_descricao else 0) +
        (3.0 if tem_keywords else 0) +
        (2.0 if tem_cta else 0) +
        (1.5 if tem_link else 0) +
        clareza_scores.get(clareza, 1.0)
    )
    
    return {
        "tem_descricao": tem_descricao,
        "tem_keywords": tem_keywords,
        "tem_cta": tem_cta,
        "tem_link": tem_link,
        "clareza": clareza,
        "nota": min(nota, 10.0)
    }


class InstagramAnaliseSimplificada(BaseModel):
    """Modelo para análise simplificada - apenas dados básicos necessários"""
    username: str
    nome_completo: str = ""
    nicho: str = "corrida"
    seguidores: int
    seguindo: int
    total_posts: int
    bio: str = ""  # Opcional - para análise de bio


# [REFATORADO] /admin/instagram/analisar-simplificado migrado para routes/instagram_routes.py





def analisar_posts_automatico(posts: list) -> dict:
    """
    Analisa automaticamente os posts recentes do Instagram.
    Calcula: média de likes, comentários, views de reels, frequência, etc.
    """
    if not posts:
        return {
            "media_likes": 0,
            "media_comentarios": 0,
            "media_views_reels": 0,
            "posts_por_semana": 0,
            "total_analisados": 0,
            "percentual_reels": 0,
            "percentual_carrossel": 0,
            "percentual_foto": 0,
            "picos_anormais": 0,
            "comentarios_repetitivos": 0,
            "horarios_artificiais": 0,
            "desvio_engajamento": 0
        }
    
    total_likes = 0
    total_comments = 0
    total_views = 0
    count_reels = 0
    count_carrossel = 0
    count_foto = 0
    timestamps = []
    likes_list = []
    comments_list = []
    
    for post in posts:
        # Extrair métricas
        likes = post.get('edge_liked_by', {}).get('count', 0) or post.get('like_count', 0)
        comments = post.get('edge_media_to_comment', {}).get('count', 0) or post.get('comment_count', 0)
        views = post.get('video_view_count', 0) or post.get('play_count', 0)
        timestamp = post.get('taken_at_timestamp', 0) or post.get('taken_at', 0)
        
        total_likes += likes
        total_comments += comments
        likes_list.append(likes)
        comments_list.append(comments)
        
        if timestamp:
            timestamps.append(timestamp)
        
        # Tipo de post
        typename = post.get('__typename', '') or post.get('media_type', '')
        is_video = post.get('is_video', False) or typename in ['GraphVideo', 'XDTGraphVideo', 2]
        is_carousel = typename in ['GraphSidecar', 'XDTGraphSidecar', 8]
        
        if is_video:
            count_reels += 1
            total_views += views
        elif is_carousel:
            count_carrossel += 1
        else:
            count_foto += 1
    
    total_posts = len(posts)
    
    # Calcular médias
    media_likes = total_likes / total_posts if total_posts > 0 else 0
    media_comentarios = total_comments / total_posts if total_posts > 0 else 0
    media_views_reels = total_views / count_reels if count_reels > 0 else 0
    
    # Calcular percentuais de formatos
    percentual_reels = (count_reels / total_posts * 100) if total_posts > 0 else 0
    percentual_carrossel = (count_carrossel / total_posts * 100) if total_posts > 0 else 0
    percentual_foto = (count_foto / total_posts * 100) if total_posts > 0 else 0
    
    # Calcular frequência (posts por semana)
    posts_por_semana = 0
    if len(timestamps) >= 2:
        timestamps.sort(reverse=True)
        time_span_seconds = timestamps[0] - timestamps[-1]
        if time_span_seconds > 0:
            weeks = time_span_seconds / (7 * 24 * 60 * 60)
            if weeks > 0:
                posts_por_semana = total_posts / weeks
    
    # Detectar anomalias (indicadores anti-fake)
    picos_anormais = 0
    if len(likes_list) >= 3:
        avg_likes = sum(likes_list) / len(likes_list)
        if avg_likes > 0:
            for likes in likes_list:
                # Pico é quando tem mais de 3x a média
                if likes > avg_likes * 3:
                    picos_anormais += 1
    
    # Desvio do engajamento
    desvio_engajamento = 0
    if len(likes_list) >= 3:
        avg = sum(likes_list) / len(likes_list)
        if avg > 0:
            variance = sum((x - avg) ** 2 for x in likes_list) / len(likes_list)
            std_dev = variance ** 0.5
            desvio_engajamento = (std_dev / avg) * 100  # Coeficiente de variação em %
    
    # Comentários repetitivos (placeholder - precisaria de análise de texto)
    comentarios_repetitivos = 0
    
    # Horários artificiais (placeholder - precisaria de análise de horários)
    horarios_artificiais = 0
    
    return {
        "media_likes": round(media_likes, 1),
        "media_comentarios": round(media_comentarios, 1),
        "media_views_reels": round(media_views_reels, 1),
        "posts_por_semana": round(posts_por_semana, 1),
        "total_analisados": total_posts,
        "percentual_reels": round(percentual_reels, 1),
        "percentual_carrossel": round(percentual_carrossel, 1),
        "percentual_foto": round(percentual_foto, 1),
        "picos_anormais": picos_anormais,
        "comentarios_repetitivos": comentarios_repetitivos,
        "horarios_artificiais": horarios_artificiais,
        "desvio_engajamento": round(desvio_engajamento, 1)
    }


def calcular_crescimento_estimado(seguidores: int, total_posts: int, engagement_rate: float) -> float:
    """
    Estima o crescimento mensal baseado em métricas conhecidas.
    """
    # Fórmula simplificada baseada em benchmarks
    # Perfis com bom engagement tendem a crescer mais
    base_growth = 0.5  # 0.5% base
    
    # Bonus por engagement
    if engagement_rate > 5:
        engagement_bonus = 2.0
    elif engagement_rate > 3:
        engagement_bonus = 1.0
    elif engagement_rate > 1:
        engagement_bonus = 0.5
    else:
        engagement_bonus = 0
    
    # Perfis menores crescem mais rápido percentualmente
    if seguidores < 1000:
        size_multiplier = 2.0
    elif seguidores < 10000:
        size_multiplier = 1.5
    elif seguidores < 100000:
        size_multiplier = 1.0
    else:
        size_multiplier = 0.5
    
    crescimento = (base_growth + engagement_bonus) * size_multiplier
    return round(min(crescimento, 10.0), 1)  # Cap em 10%


# Stubs para funções de busca Instagram (não implementadas - requer API keys)
async def buscar_instagram_api_direta(username: str) -> dict:
    """Stub - API direta do Instagram não configurada"""
    return {"success": False, "error": "not_implemented", "message": "API direta do Instagram não configurada"}

async def buscar_instagram_rapidapi(username: str) -> dict:
    """Stub - RapidAPI não configurada"""
    return {"success": False, "error": "not_implemented", "message": "RapidAPI não configurada"}


@api_router.get("/admin/instagram/buscar/{username}")
async def buscar_dados_instagram(username: str, admin: dict = Depends(get_admin_user)):
    """
    Busca dados completos de um perfil Instagram automaticamente.
    Tenta primeiro a API direta, depois RapidAPI como fallback.
    """
    # Limpar username
    username = username.strip().lstrip('@').lower()
    
    if not username:
        raise HTTPException(status_code=400, detail="Username é obrigatório")
    
    user = None
    source = "unknown"
    
    try:
        # Tentar primeiro a API direta do Instagram
        result = await buscar_instagram_api_direta(username)
        
        if result.get('success') and result.get('user'):
            user = result['user']
            source = "instagram_direct"
        elif result.get('error') == 'rate_limited':
            # Tentar RapidAPI como fallback
            logging.info(f"Instagram rate limited, tentando RapidAPI para {username}")
            rapid_result = await buscar_instagram_rapidapi(username)
            if rapid_result.get('success') and rapid_result.get('data'):
                # Converter formato RapidAPI para formato esperado
                rapid_data = rapid_result['data']
                user = {
                    'username': rapid_data.get('username', username),
                    'full_name': rapid_data.get('full_name', ''),
                    'biography': rapid_data.get('biography', ''),
                    'edge_followed_by': {'count': rapid_data.get('follower_count', 0)},
                    'edge_follow': {'count': rapid_data.get('following_count', 0)},
                    'edge_owner_to_timeline_media': {
                        'count': rapid_data.get('media_count', 0),
                        'edges': []
                    },
                    'is_verified': rapid_data.get('is_verified', False),
                    'is_business_account': rapid_data.get('is_business', False),
                    'external_url': rapid_data.get('external_url', '')
                }
                source = "rapidapi"
        
        if not user:
            return {
                "success": False,
                "error": result.get('error', 'Não foi possível acessar o perfil. Verifique se o username está correto e tente novamente.'),
                "data": None
            }
        
        # Extrair dados básicos
        seguidores = user.get('edge_followed_by', {}).get('count', 0)
        seguindo = user.get('edge_follow', {}).get('count', 0)
        total_posts = user.get('edge_owner_to_timeline_media', {}).get('count', 0)
        nome_completo = user.get('full_name', '')
        bio = user.get('biography', '')
        is_verified = user.get('is_verified', False)
        is_business = user.get('is_business_account', False)
        external_url = user.get('external_url', '')
        
        # Extrair posts recentes (até 12 posts)
        posts_edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
        posts = [edge.get('node', {}) for edge in posts_edges[:12]]
        
        # Analisar bio automaticamente
        analise_bio = analisar_bio_automatico(bio + (' ' + external_url if external_url else ''))
        
        # Analisar posts automaticamente
        analise_posts = analisar_posts_automatico(posts)
        
        # Calcular engagement rate
        if seguidores > 0 and analise_posts['media_likes'] > 0:
            engagement_rate = ((analise_posts['media_likes'] + analise_posts['media_comentarios']) / seguidores) * 100
        else:
            engagement_rate = 0
        
        # Estimar crescimento
        crescimento_estimado = calcular_crescimento_estimado(seguidores, total_posts, engagement_rate)
        
        # Montar resposta completa
        data = {
            "username": username,
            "nome_completo": nome_completo,
            "bio": bio,
            "seguidores": seguidores,
            "seguindo": seguindo,
            "total_posts": total_posts,
            "is_verified": is_verified,
            "is_business": is_business,
            "external_url": external_url,
            
            # Métricas calculadas automaticamente
            "media_likes": analise_posts['media_likes'],
            "media_comentarios": analise_posts['media_comentarios'],
            "media_views_reels": analise_posts['media_views_reels'],
            "posts_por_semana": analise_posts['posts_por_semana'],
            "engagement_rate": round(engagement_rate, 2),
            "crescimento_30_dias": crescimento_estimado,
            
            # Análise da bio automática
            "bio_tem_descricao": analise_bio['tem_descricao'],
            "bio_tem_keywords": analise_bio['tem_keywords'],
            "bio_tem_cta": analise_bio['tem_cta'],
            "bio_tem_link": analise_bio['tem_link'],
            "bio_clareza": analise_bio['clareza'],
            "bio_nota": analise_bio['nota'],
            
            # Distribuição de formatos
            "percentual_reels": analise_posts['percentual_reels'],
            "percentual_carrossel": analise_posts['percentual_carrossel'],
            "percentual_foto": analise_posts['percentual_foto'],
            
            # Indicadores anti-fake
            "picos_anormais": analise_posts['picos_anormais'],
            "comentarios_repetitivos": analise_posts['comentarios_repetitivos'],
            "horarios_artificiais": analise_posts['horarios_artificiais'],
            "desvio_engajamento": analise_posts['desvio_engajamento'],
            
            # Metadados
            "posts_analisados": analise_posts['total_analisados'],
            "source": source
        }
        
        return {
            "success": True,
            "error": None,
            "data": data
        }
        
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Timeout ao acessar Instagram. Tente novamente.",
            "data": None
        }
    except Exception as e:
        logging.error(f"Erro ao buscar dados do Instagram: {str(e)}")
        return {
            "success": False,
            "error": f"Erro ao buscar dados: {str(e)}",
            "data": None
        }


@api_router.post("/admin/instagram/analisar-automatico/{username}")
async def analisar_perfil_automatico(username: str, nicho: str = "corrida", admin: dict = Depends(get_admin_user)):
    """
    Busca dados do Instagram e faz análise completa automaticamente.
    O único input necessário é o username.
    """
    # Buscar dados do Instagram
    busca_result = await buscar_dados_instagram(username, admin)
    
    if not busca_result.get('success') or not busca_result.get('data'):
        raise HTTPException(
            status_code=400, 
            detail=busca_result.get('error', 'Não foi possível buscar dados do perfil')
        )
    
    data = busca_result['data']
    
    # Usar os dados já calculados automaticamente
    nota_bio = data.get('bio_nota', 5.0)
    
    # Calcular nota Frequência
    nota_frequencia = calcular_nota_frequencia(
        data.get('posts_por_semana', 0), 
        1  # Assumir último post há 1 dia (dados recentes)
    )
    
    # Calcular nota Engajamento
    nota_engajamento, er_post, er_reels = calcular_nota_engajamento(
        data.get('media_likes', 0),
        data.get('media_comentarios', 0),
        data.get('media_views_reels', 0),
        data.get('seguidores', 1)
    )
    
    # Calcular nota Crescimento
    nota_crescimento = calcular_nota_crescimento(data.get('crescimento_30_dias', 0))
    
    # Calcular nota Consistência
    nota_consistencia = calcular_nota_consistencia(
        2.0,  # Desvio intervalo estimado
        data.get('desvio_engajamento', 0)
    )
    
    # Calcular nota Padrões (anti-fake)
    nota_padroes = calcular_nota_padroes(
        data.get('picos_anormais', 0),
        data.get('comentarios_repetitivos', 0),
        data.get('horarios_artificiais', 0)
    )
    
    # Calcular nota Reels
    nota_reels = calcular_nota_reels(
        data.get('media_views_reels', 0),
        data.get('seguidores', 1)
    )
    
    # Calcular nota Formatos
    nota_formatos = calcular_nota_formatos(
        data.get('percentual_reels', 33),
        data.get('percentual_carrossel', 33),
        data.get('percentual_foto', 34)
    )
    
    # Score final
    score_final = calcular_score_final(
        nota_bio, nota_frequencia, nota_engajamento, nota_crescimento,
        nota_consistencia, nota_padroes, nota_reels, nota_formatos
    )
    
    # Classificação
    classificacao = classificar_influenciador(score_final)
    
    # Gerar ID
    analysis_id = str(uuid.uuid4())
    
    # Preparar documento para salvar
    analysis_doc = {
        "id": analysis_id,
        "username": data.get('username', username),
        "nome_completo": data.get('nome_completo', ''),
        "nicho": nicho,
        "seguidores": data.get('seguidores', 0),
        "seguindo": data.get('seguindo', 0),
        "total_posts": data.get('total_posts', 0),
        "bio": data.get('bio', ''),
        "is_verified": data.get('is_verified', False),
        "is_business": data.get('is_business', False),
        
        # Métricas automáticas
        "media_likes": data.get('media_likes', 0),
        "media_comentarios": data.get('media_comentarios', 0),
        "media_views_reels": data.get('media_views_reels', 0),
        "posts_por_semana": data.get('posts_por_semana', 0),
        "crescimento_30_dias": data.get('crescimento_30_dias', 0),
        
        # Análise da Bio
        "bio_tem_descricao": data.get('bio_tem_descricao', False),
        "bio_tem_keywords": data.get('bio_tem_keywords', False),
        "bio_tem_cta": data.get('bio_tem_cta', False),
        "bio_tem_link": data.get('bio_tem_link', False),
        "bio_clareza": data.get('bio_clareza', 'regular'),
        
        # Formatos
        "percentual_reels": data.get('percentual_reels', 33),
        "percentual_carrossel": data.get('percentual_carrossel', 33),
        "percentual_foto": data.get('percentual_foto', 34),
        
        # Anti-fake
        "picos_anormais": data.get('picos_anormais', 0),
        "comentarios_repetitivos": data.get('comentarios_repetitivos', 0),
        "horarios_artificiais": data.get('horarios_artificiais', 0),
        "desvio_engajamento": data.get('desvio_engajamento', 0),
        
        # Notas calculadas
        "nota_bio": nota_bio,
        "nota_frequencia": nota_frequencia,
        "nota_engajamento": nota_engajamento,
        "nota_crescimento": nota_crescimento,
        "nota_consistencia": nota_consistencia,
        "nota_padroes": nota_padroes,
        "nota_reels": nota_reels,
        "nota_formatos": nota_formatos,
        
        # Score e classificação
        "score_final": score_final,
        "classificacao": classificacao,
        "engagement_rate": er_post,
        "engagement_rate_reels": er_reels,
        
        # Metadados
        "posts_analisados": data.get('posts_analisados', 0),
        "data_analise": datetime.now(timezone.utc).isoformat(),
        "source": "instagram_api_automatico"
    }
    
    # Salvar no banco
    await db.instagram_analyses.insert_one(analysis_doc)
    
    # Preparar dados para gráficos
    media_nicho = MEDIAS_NICHO.get(nicho, MEDIAS_NICHO['corrida'])
    
    graficos_data = {
        "radar": {
            "labels": ["Bio", "Frequência", "Engajamento", "Crescimento", 
                      "Consistência", "Padrões", "Reels", "Formatos"],
            "values": [nota_bio, nota_frequencia, nota_engajamento, nota_crescimento,
                      nota_consistencia, nota_padroes, nota_reels, nota_formatos],
            "max": 10
        },
        "gauge": {
            "value": score_final,
            "min": 0,
            "max": 100,
            "ranges": [
                {"min": 0, "max": 40, "color": "#DC2626", "label": "Péssimo"},
                {"min": 40, "max": 60, "color": "#EF4444", "label": "Ruim"},
                {"min": 60, "max": 70, "color": "#F59E0B", "label": "Regular"},
                {"min": 70, "max": 80, "color": "#3B82F6", "label": "Bom"},
                {"min": 80, "max": 90, "color": "#8B5CF6", "label": "Ótimo"},
                {"min": 90, "max": 100, "color": "#10B981", "label": "Excelente"}
            ]
        },
        "comparativo": {
            "labels": ["Engajamento", "Crescimento", "Frequência"],
            "perfil": [er_post, data.get('crescimento_30_dias', 0), data.get('posts_por_semana', 0)],
            "media_nicho": [media_nicho['engagement_rate'], media_nicho['crescimento_medio'], media_nicho['posts_semana']]
        },
        "formatos": {
            "labels": ["Reels", "Carrossel", "Fotos"],
            "values": [data.get('percentual_reels', 33), data.get('percentual_carrossel', 33), data.get('percentual_foto', 34)]
        },
        "metricas": {
            "seguidores": data.get('seguidores', 0),
            "seguindo": data.get('seguindo', 0),
            "posts": data.get('total_posts', 0),
            "er_post": er_post,
            "er_reels": er_reels,
            "crescimento": data.get('crescimento_30_dias', 0),
            "indice_anomalia": (data.get('picos_anormais', 0) + data.get('comentarios_repetitivos', 0)) * 10
        }
    }
    
    # Gerar recomendações
    notas = {
        'bio': nota_bio,
        'frequencia': nota_frequencia,
        'engajamento': nota_engajamento,
        'crescimento': nota_crescimento,
        'consistencia': nota_consistencia,
        'padroes': nota_padroes,
        'reels': nota_reels,
        'formatos': nota_formatos
    }
    recomendacoes = gerar_recomendacoes(notas, {'crescimento_30_dias': data.get('crescimento_30_dias', 0)})
    
    # Remover _id do documento antes de retornar
    analysis_doc.pop('_id', None)
    
    return {
        "analysis": analysis_doc,
        "graficos_data": graficos_data,
        "recomendacoes": recomendacoes,
        "dados_brutos": data
    }


@api_router.post("/admin/instagram/analisar")
async def analisar_perfil_instagram(dados: InstagramProfileInput, admin: dict = Depends(get_admin_user)):
    """
    Analisa um perfil do Instagram com dados inseridos manualmente
    Retorna score, classificação e dados para gráficos
    """
    # Calcular nota Bio
    nota_bio = calcular_nota_bio(
        dados.bio_descricao, dados.bio_keywords, dados.bio_cta,
        dados.bio_link, dados.bio_clareza
    )
    
    # Calcular nota Frequência
    nota_frequencia = calcular_nota_frequencia(
        dados.posts_por_semana, dados.dias_ultimo_post
    )
    
    # Calcular nota Engajamento
    nota_engajamento, er_post, er_reels = calcular_nota_engajamento(
        dados.media_likes, dados.media_comentarios,
        dados.media_views_reels, dados.seguidores
    )
    
    # Calcular nota Crescimento
    nota_crescimento = calcular_nota_crescimento(dados.crescimento_30_dias)
    
    # Calcular nota Consistência
    nota_consistencia = calcular_nota_consistencia(
        dados.desvio_intervalo_posts, dados.desvio_engajamento
    )
    
    # Calcular nota Padrões (Anti-Fake)
    nota_padroes, indice_anomalia = calcular_nota_padroes(
        dados.picos_anormais, dados.comentarios_repetitivos,
        dados.horarios_artificiais, dados.total_posts
    )
    
    # Calcular nota Reels
    nota_reels = calcular_nota_reels(dados.media_views_reels, dados.seguidores)
    
    # Calcular nota Formatos
    er_medio = er_post
    nota_formatos = calcular_nota_formatos(
        dados.percentual_reels, dados.percentual_carrossel,
        dados.percentual_foto, er_medio
    )
    
    # Montar dicionário de notas
    notas = {
        'bio': nota_bio,
        'frequencia': nota_frequencia,
        'engajamento': nota_engajamento,
        'crescimento': nota_crescimento,
        'consistencia': nota_consistencia,
        'padroes': nota_padroes,
        'reels': nota_reels,
        'formatos': nota_formatos
    }
    
    # Calcular score final
    score_final = calcular_score_final(notas)
    
    # Classificar
    classificacao = classificar_influenciador(score_final)
    
    # Comparativo com média do nicho
    media_nicho = MEDIAS_NICHO.get(dados.nicho, MEDIAS_NICHO['corrida'])
    comparativo_engajamento = round(((er_post / media_nicho['engagement_rate']) - 1) * 100, 1) if media_nicho['engagement_rate'] > 0 else 0
    comparativo_crescimento = round(((dados.crescimento_30_dias / media_nicho['crescimento_medio']) - 1) * 100, 1) if media_nicho['crescimento_medio'] > 0 else 0
    
    # Gerar recomendações
    recomendacoes = gerar_recomendacoes(notas, {
        'crescimento_30_dias': dados.crescimento_30_dias
    })
    
    # Criar objeto de análise
    analysis = InstagramAnalysis(
        username=dados.username,
        nome_completo=dados.nome_completo,
        nicho=dados.nicho,
        seguidores=dados.seguidores,
        seguindo=dados.seguindo,
        total_posts=dados.total_posts,
        nota_bio=round(nota_bio, 2),
        nota_frequencia=round(nota_frequencia, 2),
        nota_engajamento=round(nota_engajamento, 2),
        nota_crescimento=round(nota_crescimento, 2),
        nota_consistencia=round(nota_consistencia, 2),
        nota_padroes=round(nota_padroes, 2),
        nota_reels=round(nota_reels, 2),
        nota_formatos=round(nota_formatos, 2),
        score_final=score_final,
        classificacao=classificacao,
        engagement_rate=er_post,
        engagement_rate_reels=er_reels,
        indice_anomalia=indice_anomalia,
        comparativo_engajamento=comparativo_engajamento,
        comparativo_crescimento=comparativo_crescimento,
        analisado_por=admin['id']
    )
    
    # Salvar no banco
    analysis_dict = analysis.model_dump()
    await db.instagram_analyses.insert_one(analysis_dict)
    
    # Preparar dados para gráficos
    graficos_data = {
        "radar": {
            "labels": ["Bio", "Frequência", "Engajamento", "Crescimento", 
                      "Consistência", "Padrões", "Reels", "Formatos"],
            "values": [nota_bio, nota_frequencia, nota_engajamento, nota_crescimento,
                      nota_consistencia, nota_padroes, nota_reels, nota_formatos],
            "max": 10
        },
        "gauge": {
            "value": score_final,
            "min": 0,
            "max": 100,
            "ranges": [
                {"min": 0, "max": 60, "color": "#EF4444", "label": "Alto Risco"},
                {"min": 60, "max": 70, "color": "#F59E0B", "label": "Regular"},
                {"min": 70, "max": 80, "color": "#3B82F6", "label": "Profissional"},
                {"min": 80, "max": 90, "color": "#8B5CF6", "label": "Premium"},
                {"min": 90, "max": 95, "color": "#F59E0B", "label": "Elite Gold"},
                {"min": 95, "max": 100, "color": "#10B981", "label": "Elite Platinum"}
            ]
        },
        "comparativo": {
            "labels": ["Engajamento", "Crescimento", "Frequência"],
            "perfil": [er_post, dados.crescimento_30_dias, dados.posts_por_semana],
            "media_nicho": [media_nicho['engagement_rate'], media_nicho['crescimento_medio'], media_nicho['posts_semana']]
        },
        "formatos": {
            "labels": ["Reels", "Carrossel", "Fotos"],
            "values": [dados.percentual_reels, dados.percentual_carrossel, dados.percentual_foto]
        },
        "metricas": {
            "seguidores": dados.seguidores,
            "seguindo": dados.seguindo,
            "posts": dados.total_posts,
            "er_post": er_post,
            "er_reels": er_reels,
            "crescimento": dados.crescimento_30_dias,
            "indice_anomalia": indice_anomalia * 100
        }
    }
    
    return InstagramAnalysisResponse(
        analysis=analysis,
        graficos_data=graficos_data,
        recomendacoes=recomendacoes
    )

# [REFATORADO] Endpoints migrados para routes/instagram_routes.py:
# - /admin/instagram/analises (GET)
# - /admin/instagram/analises/{analysis_id} (GET)
# - /admin/instagram/analises/{analysis_id} (DELETE)
# - /admin/instagram/analisar-simplificado (POST)
# - /admin/instagram/stats (GET)
# - /admin/instagram/ranking (GET)

# Endpoints NÃO migrados (permanecem aqui):
# - /admin/instagram/buscar/{username} (GET)
# - /admin/instagram/analisar-automatico/{username} (POST)
# - /admin/instagram/analisar (POST)
# - /admin/instagram/export/{analysis_id} (GET)
# - /admin/instagram/export-csv/{analysis_id} (GET)

@api_router.get("/admin/instagram/export/{analysis_id}")
async def exportar_analise_xlsx(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Exporta análise em formato XLSX"""
    analysis = await db.instagram_analyses.find_one(
        {"id": analysis_id}, {"_id": 0}
    )
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Análise Instagram"
    
    ws.merge_cells('A1:D1')
    ws['A1'] = f"Ranking Run Inside - Análise de @{analysis['username']}"
    ws['A1'].font = Font(bold=True, size=16)
    
    ws['A3'] = "Data da Análise:"
    ws['B3'] = analysis['data_analise'][:10]
    ws['A4'] = "Classificação:"
    ws['B4'] = analysis['classificacao']
    ws['A5'] = "Score Final:"
    ws['B5'] = f"{analysis['score_final']}/100"
    
    ws['A7'] = "MÉTRICAS DO PERFIL"
    ws['A7'].font = Font(bold=True)
    
    metricas = [
        ("Seguidores", analysis['seguidores']),
        ("Seguindo", analysis['seguindo']),
        ("Total de Posts", analysis['total_posts']),
        ("Engagement Rate", f"{analysis['engagement_rate']}%"),
    ]
    
    for i, (label, value) in enumerate(metricas, start=8):
        ws[f'A{i}'] = label
        ws[f'B{i}'] = value
    
    row = 13
    ws[f'A{row}'] = "NOTAS INDIVIDUAIS (0-10)"
    ws[f'A{row}'].font = Font(bold=True)
    
    notas = [
        ("Bio", analysis['nota_bio']),
        ("Frequência", analysis['nota_frequencia']),
        ("Engajamento", analysis['nota_engajamento']),
        ("Crescimento", analysis['nota_crescimento']),
        ("Consistência", analysis['nota_consistencia']),
        ("Padrões", analysis['nota_padroes']),
        ("Reels", analysis['nota_reels']),
        ("Formatos", analysis['nota_formatos'])
    ]
    
    for i, (label, value) in enumerate(notas, start=row+1):
        ws[f'A{i}'] = label
        ws[f'B{i}'] = value
    
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 20
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=analise_{analysis['username']}.xlsx"
        }
    )


@api_router.get("/admin/instagram/export-csv/{analysis_id}")
async def exportar_analise_csv(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Exporta análise em formato CSV"""
    analysis = await db.instagram_analyses.find_one(
        {"id": analysis_id}, {"_id": 0}
    )
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Ranking Run Inside - Análise de Instagram"])
    writer.writerow([])
    writer.writerow(["Campo", "Valor"])
    writer.writerow(["Username", f"@{analysis['username']}"])
    writer.writerow(["Score Final", analysis['score_final']])
    writer.writerow(["Classificação", analysis['classificacao']])
    writer.writerow([])
    writer.writerow(["Métricas"])
    writer.writerow(["Seguidores", analysis['seguidores']])
    writer.writerow(["Engagement Rate", f"{analysis['engagement_rate']}%"])
    writer.writerow([])
    writer.writerow(["Notas (0-10)"])
    writer.writerow(["Bio", analysis['nota_bio']])
    writer.writerow(["Frequência", analysis['nota_frequencia']])
    writer.writerow(["Engajamento", analysis['nota_engajamento']])
    writer.writerow(["Crescimento", analysis['nota_crescimento']])
    writer.writerow(["Consistência", analysis['nota_consistencia']])
    writer.writerow(["Padrões", analysis['nota_padroes']])
    writer.writerow(["Reels", analysis['nota_reels']])
    writer.writerow(["Formatos", analysis['nota_formatos']])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=analise_{analysis['username']}.csv"
        }
    )


# ==================== INCLUDE ROUTER (movido para o final) ====================

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

# ==================== SCHEDULER DE ANIVERSÁRIOS ====================

scheduler = AsyncIOScheduler()

async def enviar_mensagens_aniversario_automatico():
    """Função que roda às 00:00 para enviar mensagens de aniversário automaticamente"""
    logger.info("🎂 Iniciando envio automático de mensagens de aniversário...")
    
    try:
        # Verificar se envio automático está habilitado
        config = await db.configuracoes.find_one({"tipo": "mensagem_aniversario"}, {"_id": 0})
        if not config or not config.get("envio_automatico", False):
            logger.info("⏸️ Envio automático desabilitado. Pulando...")
            return
        
        mensagem_padrao = config.get(
            "mensagem_padrao", 
            "Feliz Aniversário! 🎂 Que este novo ciclo traga muitas conquistas nas pistas. O Ranking Run Pró deseja a você muita saúde e velocidade! 🏃‍♂️"
        )
        
        # Buscar aniversariantes de hoje
        hoje = datetime.now()
        atletas = await db.usuarios.find({"role": "atleta"}, {"_id": 0}).to_list(None)
        
        aniversariantes = []
        for atleta in atletas:
            if atleta.get("data_nascimento"):
                try:
                    data_nasc = datetime.strptime(atleta["data_nascimento"], "%Y-%m-%d")
                    if data_nasc.month == hoje.month and data_nasc.day == hoje.day:
                        aniversariantes.append(atleta)
                except ValueError:
                    pass
        
        if not aniversariantes:
            logger.info("📭 Nenhum aniversariante hoje.")
            return
        
        logger.info(f"🎉 Encontrados {len(aniversariantes)} aniversariante(s) hoje!")
        
        # Verificar se já enviou mensagem para cada atleta este ano
        mensagens_enviadas = 0
        for atleta in aniversariantes:
            # Verificar se já existe mensagem para este atleta neste ano
            existente = await db.mensagens_aniversario.find_one({
                "usuario_id": atleta["id"],
                "ano": hoje.year
            }, {"_id": 0})
            
            if existente:
                logger.info(f"⏭️ Mensagem já enviada para {atleta['nome']} em {hoje.year}")
                continue
            
            # Criar mensagem
            msg = MensagemAniversario(
                usuario_id=atleta["id"],
                mensagem=mensagem_padrao,
                ano=hoje.year
            )
            await db.mensagens_aniversario.insert_one(msg.model_dump())
            mensagens_enviadas += 1
            logger.info(f"✅ Mensagem enviada para {atleta['nome']}")
        
        logger.info(f"🎂 Total de mensagens enviadas: {mensagens_enviadas}")
        
        # Registrar log de execução
        await db.logs_scheduler.insert_one({
            "tipo": "aniversario_automatico",
            "data_execucao": hoje.isoformat(),
            "aniversariantes_encontrados": len(aniversariantes),
            "mensagens_enviadas": mensagens_enviadas
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no envio automático de aniversários: {str(e)}")




# ============================================================
# LIGA NACIONAL DE ASSESSORIAS - RANKING OFICIAL ROE-RR
# ============================================================
# [REFATORADO] Endpoints migrados para routes/assessorias_routes.py:
# - /liga-assessorias/ranking
# - /liga-assessorias/evolucao-mensal
# - /liga-assessorias/stats
# - /liga-assessorias/assessoria/{nome_equipe}

# Endpoints NÃO migrados (permanecem aqui):
# - /liga-assessorias/estados
# - /liga-assessorias/comparacao-mensal/{nome_equipe}
# - /liga-assessorias/cidades



@api_router.get("/liga-assessorias/estados")
async def get_estados_com_assessorias():
    """Lista estados que têm assessorias cadastradas"""
    pipeline = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None], "$exists": True}}},
        {"$group": {"_id": "$estado"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [e["_id"] for e in result]


@api_router.get("/liga-assessorias/comparacao-mensal/{nome_equipe}")
async def get_comparacao_mensal_assessoria(nome_equipe: str):
    """
    Retorna comparação de desempenho entre mês atual e mês anterior
    Para uso no Dashboard do Dono de Assessoria
    """
    from datetime import datetime
    import urllib.parse
    
    nome_decoded = urllib.parse.unquote(nome_equipe)
    
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    # Calcular mês anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual
    
    # Formatação de datas
    inicio_mes_atual = f"{ano_atual}-{mes_atual:02d}-01"
    inicio_mes_anterior = f"{ano_anterior}-{mes_anterior:02d}-01"
    fim_mes_anterior = inicio_mes_atual
    
    # Próximo mês para fim do mês atual
    if mes_atual == 12:
        fim_mes_atual = f"{ano_atual + 1}-01-01"
    else:
        fim_mes_atual = f"{ano_atual}-{mes_atual + 1:02d}-01"
    
    # Buscar atletas da equipe
    atletas = await db.usuarios.find(
        {"role": "atleta", "equipe": nome_decoded},
        {"_id": 0, "id": 1, "created_at": 1}
    ).to_list(None)
    
    if not atletas:
        raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    atletas_ids = [a["id"] for a in atletas]
    
    # Resultados do mês atual
    resultados_mes_atual = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_atual, "$lt": fim_mes_atual}
    })
    
    # Resultados do mês anterior
    resultados_mes_anterior = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_anterior, "$lt": fim_mes_anterior}
    })
    
    # Novos atletas no mês atual
    novos_atletas_atual = sum(1 for a in atletas 
        if a.get("created_at", "").startswith(f"{ano_atual}-{mes_atual:02d}"))
    
    # Novos atletas no mês anterior
    novos_atletas_anterior = sum(1 for a in atletas 
        if a.get("created_at", "").startswith(f"{ano_anterior}-{mes_anterior:02d}"))
    
    # Buscar ranking do mês atual
    ranking_atual_data = await get_ranking_assessorias(tipo="nacional", mes=mes_atual)
    posicao_atual = next(
        (e["posicao"] for e in ranking_atual_data["ranking"] if e["nome"] == nome_decoded),
        None
    )
    
    # Buscar ranking do mês anterior
    ranking_anterior_data = await get_ranking_assessorias(tipo="nacional", mes=mes_anterior)
    posicao_anterior = next(
        (e["posicao"] for e in ranking_anterior_data["ranking"] if e["nome"] == nome_decoded),
        None
    )
    
    # Calcular pontos do mês atual e anterior
    corridas_atual = await db.corridas.find({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_atual, "$lt": fim_mes_atual}
    }).to_list(None)
    
    corridas_anterior = await db.corridas.find({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_anterior, "$lt": fim_mes_anterior}
    }).to_list(None)
    
    def calcular_pontos(corridas_lista):
        pontos = 0
        for c in corridas_lista:
            pontos += 1.0  # Por resultado
            colocacao = c.get("colocacao", 0)
            modalidade = c.get("modalidade", "profissional_amador")
            if modalidade == "profissional_amador" and colocacao > 0:
                if colocacao == 1:
                    pontos += 1.0
                elif 2 <= colocacao <= 5:
                    pontos += 0.5
        return round(pontos, 1)
    
    pontos_atual = calcular_pontos(corridas_atual)
    pontos_anterior = calcular_pontos(corridas_anterior)
    
    # Nomes dos meses
    meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    def calc_variacao(atual, anterior):
        if anterior == 0:
            return 100 if atual > 0 else 0
        return round(((atual - anterior) / anterior) * 100, 1)
    
    return {
        "equipe": nome_decoded,
        "mes_atual": {
            "nome": meses_nomes[mes_atual - 1],
            "numero": mes_atual,
            "ano": ano_atual,
            "resultados": resultados_mes_atual,
            "novos_atletas": novos_atletas_atual,
            "pontos": pontos_atual,
            "posicao_ranking": posicao_atual
        },
        "mes_anterior": {
            "nome": meses_nomes[mes_anterior - 1],
            "numero": mes_anterior,
            "ano": ano_anterior,
            "resultados": resultados_mes_anterior,
            "novos_atletas": novos_atletas_anterior,
            "pontos": pontos_anterior,
            "posicao_ranking": posicao_anterior
        },
        "variacoes": {
            "resultados": calc_variacao(resultados_mes_atual, resultados_mes_anterior),
            "novos_atletas": calc_variacao(novos_atletas_atual, novos_atletas_anterior),
            "pontos": calc_variacao(pontos_atual, pontos_anterior),
            "posicao": (posicao_anterior - posicao_atual) if posicao_atual and posicao_anterior else 0  # Positivo = subiu
        }
    }

@api_router.get("/liga-assessorias/cidades")
async def get_cidades_com_assessorias(estado: str = None):
    """Lista cidades que têm assessorias cadastradas"""
    match_filter = {"role": "atleta", "equipe": {"$nin": ["", None], "$exists": True}}
    if estado:
        match_filter["estado"] = estado
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {"_id": "$cidade"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [c["_id"] for c in result]


# ============================================================
# RELATÓRIOS DETALHADOS PARA DONO DE ASSESSORIA
# ============================================================

@api_router.get("/dono-assessoria/relatorios/{nome_equipe}")
async def get_relatorios_assessoria(nome_equipe: str, current_user: dict = Depends(get_current_user)):
    """Retorna dados completos para relatórios da assessoria"""
    
    # Verificar permissão
    if current_user.get("role") not in ["admin", "super_admin", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Dono de assessoria só pode ver sua própria assessoria
    if current_user.get("role") == "dono_assessoria" and current_user.get("equipe") != nome_equipe:
        raise HTTPException(status_code=403, detail="Você só pode ver relatórios da sua assessoria")
    
    # Buscar atletas da equipe
    atletas = await db.usuarios.find(
        {"equipe": nome_equipe, "role": "atleta"},
        {"_id": 0, "id": 1, "nome": 1, "genero": 1, "categoria": 1, "estado": 1, "cidade": 1, 
         "pontos_total": 1, "total_corridas": 1, "faixa_etaria": 1, "data_criacao": 1}
    ).to_list(None)
    
    # Buscar resultados dos atletas
    atleta_ids = [a["id"] for a in atletas]
    resultados = await db.ranking_anual.find(
        {"atleta_id": {"$in": atleta_ids}},
        {"_id": 0}
    ).to_list(None)
    
    # 1. Distribuição por gênero
    dist_genero = {"M": 0, "F": 0}
    for a in atletas:
        g = a.get("genero", "M")
        dist_genero[g] = dist_genero.get(g, 0) + 1
    
    grafico_genero = [
        {"name": "Masculino", "value": dist_genero.get("M", 0), "fill": "#3B82F6"},
        {"name": "Feminino", "value": dist_genero.get("F", 0), "fill": "#EC4899"}
    ]
    
    # 2. Distribuição por categoria
    dist_categoria = {}
    for a in atletas:
        cat = a.get("categoria", "normal") or "normal"
        dist_categoria[cat] = dist_categoria.get(cat, 0) + 1
    
    grafico_categoria = [
        {"name": cat.upper(), "value": count, "fill": ["#10B981", "#F59E0B", "#8B5CF6", "#EF4444"][i % 4]}
        for i, (cat, count) in enumerate(dist_categoria.items())
    ]
    
    # 3. Distribuição por faixa etária
    dist_faixa = {}
    for a in atletas:
        faixa = a.get("faixa_etaria", "N/A") or "N/A"
        dist_faixa[faixa] = dist_faixa.get(faixa, 0) + 1
    
    grafico_faixa = [
        {"faixa": faixa, "atletas": count}
        for faixa, count in sorted(dist_faixa.items())
    ]
    
    # 4. Distribuição por estado (para mapa)
    dist_estado = {}
    for a in atletas:
        estado = a.get("estado", "N/A") or "N/A"
        dist_estado[estado] = dist_estado.get(estado, 0) + 1
    
    mapa_estados = [
        {"estado": estado, "atletas": count}
        for estado, count in dist_estado.items()
    ]
    
    # 5. Evolução mensal de resultados (últimos 6 meses)
    from datetime import datetime, timedelta
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    mes_atual = datetime.now().month
    evolucao_mensal = []
    
    for i in range(6):
        mes_idx = (mes_atual - 5 + i - 1) % 12
        mes_num = mes_idx + 1
        mes_nome = meses[mes_idx]
        
        # Contar resultados do mês
        count_resultados = 0
        pontos_mes = 0
        for r in resultados:
            if r.get("mes") == mes_num:
                count_resultados += 1
                pontos_mes += r.get("pontos", 0)
        
        evolucao_mensal.append({
            "mes": mes_nome,
            "resultados": count_resultados,
            "pontos": pontos_mes
        })
    
    # 6. Radar de performance (métricas normalizadas 0-100)
    total_atletas = len(atletas)
    total_resultados = len(resultados)
    total_pontos = sum(r.get("pontos", 0) for r in resultados)
    total_primeiros = sum(1 for r in resultados if r.get("colocacao") == 1)
    total_podios = sum(1 for r in resultados if r.get("colocacao", 99) <= 3)
    
    # Normalizar para 0-100 (baseado em médias esperadas)
    radar_data = [
        {"metrica": "Atletas", "valor": min(100, total_atletas * 5), "fullMark": 100},
        {"metrica": "Resultados", "valor": min(100, total_resultados * 2), "fullMark": 100},
        {"metrica": "Pontos", "valor": min(100, total_pontos / 10), "fullMark": 100},
        {"metrica": "1º Lugares", "valor": min(100, total_primeiros * 10), "fullMark": 100},
        {"metrica": "Pódios", "valor": min(100, total_podios * 5), "fullMark": 100},
        {"metrica": "Engajamento", "valor": min(100, (total_resultados / max(1, total_atletas)) * 20), "fullMark": 100}
    ]
    
    # 7. Top atletas (ranking interno)
    top_atletas = sorted(atletas, key=lambda x: x.get("pontos_total", 0), reverse=True)[:10]
    ranking_atletas = [
        {"pos": i+1, "nome": a["nome"], "pontos": a.get("pontos_total", 0), "corridas": a.get("total_corridas", 0)}
        for i, a in enumerate(top_atletas)
    ]
    
    # 8. Indicadores percentuais
    media_pontos = total_pontos / max(1, total_atletas)
    media_corridas = total_resultados / max(1, total_atletas)
    taxa_podio = (total_podios / max(1, total_resultados)) * 100
    taxa_vitoria = (total_primeiros / max(1, total_resultados)) * 100
    
    indicadores = {
        "media_pontos_atleta": round(media_pontos, 1),
        "media_corridas_atleta": round(media_corridas, 1),
        "taxa_podio": round(taxa_podio, 1),
        "taxa_vitoria": round(taxa_vitoria, 1),
        "total_atletas": total_atletas,
        "total_resultados": total_resultados,
        "total_pontos": total_pontos,
        "total_primeiros": total_primeiros,
        "total_podios": total_podios
    }
    
    # 9. Distribuição de colocações (sunburst data)
    dist_colocacao = {}
    for r in resultados:
        col = r.get("colocacao", 0)
        if col == 1:
            key = "1º Lugar"
        elif col == 2:
            key = "2º Lugar"
        elif col == 3:
            key = "3º Lugar"
        elif col <= 5:
            key = "4º-5º"
        elif col <= 10:
            key = "6º-10º"
        else:
            key = "Outros"
        dist_colocacao[key] = dist_colocacao.get(key, 0) + 1
    
    sunburst_data = [
        {"name": "Resultados", "children": [
            {"name": key, "size": value}
            for key, value in dist_colocacao.items()
        ]}
    ]
    
    # 10. Evolução de cadastros de atletas
    cadastros_por_mes = {}
    for a in atletas:
        data_str = a.get("data_criacao", "")
        if data_str:
            try:
                mes = data_str[:7]  # YYYY-MM
                cadastros_por_mes[mes] = cadastros_por_mes.get(mes, 0) + 1
            except:
                pass
    
    evolucao_cadastros = [
        {"mes": mes, "novos": count}
        for mes, count in sorted(cadastros_por_mes.items())[-6:]
    ]
    
    return {
        "equipe": nome_equipe,
        "grafico_genero": grafico_genero,
        "grafico_categoria": grafico_categoria,
        "grafico_faixa_etaria": grafico_faixa,
        "mapa_estados": mapa_estados,
        "evolucao_mensal": evolucao_mensal,
        "radar_performance": radar_data,
        "ranking_atletas": ranking_atletas,
        "indicadores": indicadores,
        "sunburst_colocacoes": sunburst_data,
        "evolucao_cadastros": evolucao_cadastros
    }


# ============================================================
# REGULAMENTO - Gerenciamento de Conteúdo
# ============================================================

@api_router.get("/regulamento")
async def get_regulamento():
    """Retorna o regulamento atual (público)"""
    regulamento = await db.configuracoes.find_one({"tipo": "regulamento"}, {"_id": 0})
    
    if not regulamento:
        # Retorna regulamento padrão se não existir
        return {
            "titulo": "Regulamento do Ranking Run Pró",
            "conteudo": """
## Regulamento Oficial do Ranking Run Pró

### 1. Objetivo
O Ranking Run Pró tem como objetivo classificar e premiar os atletas de corrida de rua em território nacional.

### 2. Categorias
- **Profissional/Amador**: Masculino e Feminino
- **PCD**: Masculino e Feminino
- **Cadeirante**: Masculino e Feminino

### 3. Sistema de Pontuação
- 1º lugar: 10 pontos
- 2º lugar: 9 pontos
- 3º lugar: 8 pontos
- 4º lugar: 7 pontos
- 5º lugar: 6 pontos
- 6º lugar: 5 pontos
- 7º lugar: 4 pontos
- 8º lugar: 3 pontos
- 9º lugar: 2 pontos
- 10º lugar: 1 ponto

### 4. Requisitos
- Mínimo de 12 corridas para atletas normais
- Mínimo de 8 corridas para PCD e Cadeirantes
- Resultados devem ser submetidos em até 6 dias úteis após a prova

### 5. Validação
Todos os resultados são verificados pela equipe administrativa antes de serem contabilizados.

---
*Este é um regulamento padrão. O conteúdo oficial será atualizado pelo administrador.*
            """,
            "ultima_atualizacao": datetime.now(timezone.utc).isoformat(),
            "atualizado_por": "Sistema"
        }
    
    return regulamento


@api_router.put("/admin/regulamento")
async def atualizar_regulamento(
    titulo: str = Form(...),
    conteudo: str = Form(...),
    admin: dict = Depends(get_admin_user)
):
    """Atualiza o regulamento (apenas admin)"""
    
    regulamento = {
        "tipo": "regulamento",
        "titulo": titulo,
        "conteudo": conteudo,
        "ultima_atualizacao": datetime.now(timezone.utc).isoformat(),
        "atualizado_por": admin["nome"]
    }
    
    await db.configuracoes.update_one(
        {"tipo": "regulamento"},
        {"$set": regulamento},
        upsert=True
    )
    
    return {"message": "Regulamento atualizado com sucesso", "regulamento": regulamento}


@api_router.get("/admin/regulamento")
async def get_regulamento_admin(admin: dict = Depends(get_admin_user)):
    """Retorna o regulamento para edição (admin)"""
    regulamento = await db.configuracoes.find_one({"tipo": "regulamento"}, {"_id": 0})
    
    if not regulamento:
        # Retorna regulamento padrão para edição
        return {
            "titulo": "Regulamento do Ranking Run Pró",
            "conteudo": """## Regulamento Oficial do Ranking Run Pró

### 1. Objetivo
O Ranking Run Pró tem como objetivo classificar e premiar os atletas de corrida de rua em território nacional.

### 2. Categorias
- **Profissional/Amador**: Masculino e Feminino
- **PCD**: Masculino e Feminino
- **Cadeirante**: Masculino e Feminino

### 3. Sistema de Pontuação
- 1º lugar: 10 pontos
- 2º lugar: 9 pontos
- 3º lugar: 8 pontos
- 4º lugar: 7 pontos
- 5º lugar: 6 pontos
- 6º lugar: 5 pontos
- 7º lugar: 4 pontos
- 8º lugar: 3 pontos
- 9º lugar: 2 pontos
- 10º lugar: 1 ponto

### 4. Requisitos
- Mínimo de 12 corridas para atletas normais
- Mínimo de 8 corridas para PCD e Cadeirantes
- Resultados devem ser submetidos em até 6 dias úteis após a prova

### 5. Validação
Todos os resultados são verificados pela equipe administrativa antes de serem contabilizados.

---
*Este é um regulamento padrão. Edite o conteúdo conforme necessário.*""",
            "ultima_atualizacao": None,
            "atualizado_por": None
        }
    
    return regulamento


# ============================================================
# AUTORIZAÇÕES - Sistema de Gerenciamento de Acesso
# ============================================================

@api_router.get("/admin/autorizacoes")
async def listar_autorizacoes(admin: dict = Depends(get_admin_user)):
    """Lista todas as autorizações (admin)"""
    autorizacoes = await db.autorizacoes.find({}, {"_id": 0}).to_list(None)
    
    # Enriquecer com dados do atleta
    for auth in autorizacoes:
        atleta = await db.usuarios.find_one({"id": auth["atleta_id"]}, {"_id": 0, "nome": 1, "email": 1, "equipe": 1})
        if atleta:
            auth["atleta_nome"] = atleta.get("nome", "N/A")
            auth["atleta_email"] = atleta.get("email", "N/A")
            auth["atleta_equipe"] = atleta.get("equipe", "Individual")
    
    return autorizacoes


@api_router.get("/admin/atletas-periodo-teste")
async def listar_atletas_periodo_teste(admin: dict = Depends(get_admin_user)):
    """Lista atletas que estão no período de teste ou que o período expirou"""
    hoje = datetime.now()
    
    atletas = await db.usuarios.find(
        {"role": "atleta"},
        {"_id": 0, "id": 1, "nome": 1, "email": 1, "equipe": 1, "data_criacao": 1, "categoria": 1, "estado": 1}
    ).to_list(None)
    
    resultado = []
    for atleta in atletas:
        # Verificar se tem autorização ativa
        autorizacao = await db.autorizacoes.find_one({"atleta_id": atleta["id"], "status": "ativa"}, {"_id": 0})
        
        data_cadastro_str = atleta.get("data_criacao", "")
        dias_restantes = None
        status_periodo = "desconhecido"
        
        if data_cadastro_str:
            try:
                if "T" in data_cadastro_str:
                    data_cadastro = datetime.fromisoformat(data_cadastro_str.replace("Z", "+00:00").replace("+00:00", ""))
                else:
                    data_cadastro = datetime.strptime(data_cadastro_str[:10], "%Y-%m-%d")
                
                dias_desde_cadastro = (hoje - data_cadastro).days
                dias_restantes = 30 - dias_desde_cadastro
                
                if dias_restantes > 0:
                    status_periodo = "em_teste"
                else:
                    status_periodo = "expirado"
            except:
                status_periodo = "desconhecido"
        
        # Status final
        if autorizacao:
            data_exp = datetime.fromisoformat(autorizacao["data_expiracao"].replace("Z", "+00:00").replace("+00:00", ""))
            if hoje <= data_exp:
                status_periodo = "autorizado"
                dias_restantes = (data_exp - hoje).days
        
        resultado.append({
            **atleta,
            "dias_restantes": dias_restantes,
            "status_periodo": status_periodo,
            "autorizacao": autorizacao
        })
    
    return resultado


@api_router.post("/admin/autorizacoes")
async def criar_autorizacao(
    atleta_id: str = Form(...),
    tipo_autorizacao: str = Form(...),  # "6_meses", "1_ano", "ate_fim_ano"
    observacao: str = Form(""),
    admin: dict = Depends(get_admin_user)
):
    """Cria autorização de acesso para um atleta"""
    
    # Verificar se o atleta existe
    atleta = await db.usuarios.find_one({"id": atleta_id, "role": "atleta"}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    hoje = datetime.now()
    
    # Calcular data de expiração baseado no tipo
    if tipo_autorizacao == "6_meses":
        data_expiracao = hoje + timedelta(days=180)
        descricao = "Autorização por 6 meses"
    elif tipo_autorizacao == "1_ano":
        data_expiracao = hoje + timedelta(days=365)
        descricao = "Autorização por 1 ano"
    elif tipo_autorizacao == "ate_fim_ano":
        data_expiracao = datetime(hoje.year, 12, 31, 23, 59, 59)
        descricao = f"Autorização até fim de {hoje.year}"
    else:
        raise HTTPException(status_code=400, detail="Tipo de autorização inválido")
    
    # Desativar autorizações anteriores
    await db.autorizacoes.update_many(
        {"atleta_id": atleta_id},
        {"$set": {"status": "substituida"}}
    )
    
    # Criar nova autorização
    autorizacao = {
        "id": str(uuid.uuid4()),
        "atleta_id": atleta_id,
        "tipo": tipo_autorizacao,
        "descricao": descricao,
        "data_inicio": hoje.isoformat(),
        "data_expiracao": data_expiracao.isoformat(),
        "autorizado_por": admin["nome"],
        "admin_id": admin["id"],
        "observacao": observacao,
        "status": "ativa",
        "data_criacao": hoje.isoformat()
    }
    
    await db.autorizacoes.insert_one(autorizacao)
    
    return {
        "message": f"Autorização criada com sucesso! {atleta['nome']} tem acesso até {data_expiracao.strftime('%d/%m/%Y')}",
        "autorizacao": {k: v for k, v in autorizacao.items() if k != "_id"}
    }


@api_router.delete("/admin/autorizacoes/{autorizacao_id}")
async def revogar_autorizacao(autorizacao_id: str, admin: dict = Depends(get_admin_user)):
    """Revoga uma autorização"""
    result = await db.autorizacoes.update_one(
        {"id": autorizacao_id},
        {"$set": {"status": "revogada", "revogado_por": admin["nome"], "data_revogacao": datetime.now().isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Autorização não encontrada")
    
    return {"message": "Autorização revogada com sucesso"}


@api_router.get("/atleta/status-acesso")
async def verificar_status_acesso(current_user: dict = Depends(get_current_user)):
    """Verifica o status de acesso do atleta logado"""
    hoje = datetime.now()
    
    # Verificar autorização ativa
    autorizacao = await db.autorizacoes.find_one({"atleta_id": current_user["id"], "status": "ativa"}, {"_id": 0})
    
    # Calcular dias desde cadastro
    data_cadastro_str = current_user.get("data_criacao", "")
    dias_desde_cadastro = None
    dias_restantes_teste = None
    
    if data_cadastro_str:
        try:
            if "T" in data_cadastro_str:
                data_cadastro = datetime.fromisoformat(data_cadastro_str.replace("Z", "+00:00").replace("+00:00", ""))
            else:
                data_cadastro = datetime.strptime(data_cadastro_str[:10], "%Y-%m-%d")
            
            dias_desde_cadastro = (hoje - data_cadastro).days
            dias_restantes_teste = max(0, 30 - dias_desde_cadastro)
        except:
            pass
    
    status = "em_teste"
    dias_restantes = dias_restantes_teste
    mensagem = f"Você está no período de teste. Restam {dias_restantes_teste} dias."
    
    if autorizacao:
        data_exp = datetime.fromisoformat(autorizacao["data_expiracao"].replace("Z", "+00:00").replace("+00:00", ""))
        if hoje <= data_exp:
            status = "autorizado"
            dias_restantes = (data_exp - hoje).days
            mensagem = f"Acesso autorizado até {data_exp.strftime('%d/%m/%Y')}. Restam {dias_restantes} dias."
        else:
            status = "expirado"
            dias_restantes = 0
            mensagem = "Sua autorização expirou. Entre em contato com a administração."
    elif dias_restantes_teste is not None and dias_restantes_teste <= 0:
        status = "expirado"
        dias_restantes = 0
        mensagem = "Seu período de teste expirou. Entre em contato com a administração para liberar seu acesso."
    
    return {
        "status": status,
        "dias_restantes": dias_restantes,
        "mensagem": mensagem,
        "autorizacao": autorizacao,
        "dias_desde_cadastro": dias_desde_cadastro
    }


@api_router.get("/admin/carteirinha/{atleta_id}")
async def gerar_carteirinha(atleta_id: str, admin: dict = Depends(get_admin_user)):
    """Gera dados para carteirinha de membro"""
    
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    autorizacao = await db.autorizacoes.find_one({"atleta_id": atleta_id, "status": "ativa"}, {"_id": 0})
    
    if not autorizacao:
        raise HTTPException(status_code=400, detail="Atleta não possui autorização ativa")
    
    return {
        "atleta": {
            "id": atleta["id"],
            "nome": atleta.get("nome", ""),
            "email": atleta.get("email", ""),
            "equipe": atleta.get("equipe", "Individual"),
            "categoria": atleta.get("categoria", "normal"),
            "estado": atleta.get("estado", ""),
            "cidade": atleta.get("cidade", ""),
            "foto_url": atleta.get("foto_url", "")
        },
        "autorizacao": autorizacao,
        "valido_ate": autorizacao["data_expiracao"],
        "numero_carteirinha": f"RRP-{atleta_id[:8].upper()}-{datetime.now().year}"
    }


# ============================================================
# RANKING DAS CORRIDAS - Sistema de Avaliação de Eventos
# ============================================================

# Coleções MongoDB para o módulo
# db.corridas_eventos = corridas de rua cadastradas
# db.avaliacoes_corridas = avaliações dos atletas

@api_router.post("/corridas-eventos")
async def criar_corrida_evento(
    nome_corrida: str = Form(...),
    organizador: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    data_corrida: str = Form(...),
    pagina_link: str = Form(None),
    status: str = Form("ativa"),
    current_user: dict = Depends(get_current_user)
):
    """Cadastra uma nova corrida de rua (Admin ou Dono de Assessoria)"""
    
    # Verificar permissão
    if current_user.get("role") not in ["admin", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Apenas Admin ou Dono de Assessoria podem cadastrar corridas")
    
    corrida = {
        "id": str(uuid.uuid4()),
        "nome_corrida": nome_corrida,
        "organizador": organizador,
        "cidade": cidade,
        "estado": estado,
        "data_corrida": data_corrida,
        "pagina_link": pagina_link or "",
        "status": status,  # ativa, encerrada, cancelada
        "criado_por": current_user.get("id"),
        "criado_em": datetime.now().isoformat(),
        # Campos de estatísticas (atualizados automaticamente)
        "total_avaliacoes": 0,
        "media_geral": 0,
        "media_organizacao": 0,
        "media_percurso": 0,
        "media_kit": 0,
        "media_hidratacao": 0,
        "media_pos_prova": 0,
        "pontuacao_ranking": 0  # Calculada com Média Bayesiana
    }
    
    await db.corridas_eventos.insert_one(corrida)
    
    return {"message": "Corrida cadastrada com sucesso!", "id": corrida["id"]}


@api_router.get("/corridas-eventos")
async def listar_corridas_eventos(
    estado: str = None,
    cidade: str = None,
    status: str = None
):
    """Lista corridas de rua com filtros opcionais"""
    
    filtro = {}
    if estado:
        filtro["estado"] = estado
    if cidade:
        filtro["cidade"] = cidade
    if status:
        filtro["status"] = status
    
    corridas = await db.corridas_eventos.find(filtro, {"_id": 0}).sort("data_corrida", -1).to_list(None)
    return corridas


@api_router.get("/corridas-eventos/{corrida_id}")
async def get_corrida_evento(corrida_id: str):
    """Retorna detalhes de uma corrida específica"""
    
    corrida = await db.corridas_eventos.find_one({"id": corrida_id}, {"_id": 0})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    return corrida


@api_router.put("/corridas-eventos/{corrida_id}")
async def atualizar_corrida_evento(
    corrida_id: str,
    nome_corrida: str = Form(None),
    organizador: str = Form(None),
    cidade: str = Form(None),
    estado: str = Form(None),
    data_corrida: str = Form(None),
    pagina_link: str = Form(None),
    status: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Atualiza uma corrida existente"""
    
    if current_user.get("role") not in ["admin", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    update_data = {}
    if nome_corrida:
        update_data["nome_corrida"] = nome_corrida
    if organizador:
        update_data["organizador"] = organizador
    if cidade:
        update_data["cidade"] = cidade
    if estado:
        update_data["estado"] = estado
    if data_corrida:
        update_data["data_corrida"] = data_corrida
    if pagina_link is not None:
        update_data["pagina_link"] = pagina_link
    if status:
        update_data["status"] = status
    
    if update_data:
        await db.corridas_eventos.update_one({"id": corrida_id}, {"$set": update_data})
    
    return {"message": "Corrida atualizada com sucesso!"}


@api_router.delete("/corridas-eventos/{corrida_id}")
async def deletar_corrida_evento(corrida_id: str, admin: dict = Depends(get_admin_user)):
    """Deleta uma corrida (apenas Admin)"""
    
    await db.corridas_eventos.delete_one({"id": corrida_id})
    await db.avaliacoes_corridas.delete_many({"corrida_id": corrida_id})
    
    return {"message": "Corrida excluída com sucesso!"}


@api_router.get("/ranking-corridas")
async def get_ranking_corridas(
    tipo: str = "nacional",  # nacional, estadual, cidade, mensal, anual, historico
    estado: str = None,
    cidade: str = None
):
    """
    Retorna ranking das corridas baseado em avaliações
    Usa Média Bayesiana para cálculo justo
    """
    from datetime import datetime
    
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    # Buscar todas as corridas
    filtro_corridas = {"status": {"$ne": "cancelada"}}
    
    if tipo == "estadual" and estado:
        filtro_corridas["estado"] = estado
    elif tipo == "cidade" and cidade:
        filtro_corridas["cidade"] = cidade
    
    corridas = await db.corridas_eventos.find(filtro_corridas, {"_id": 0}).to_list(None)
    
    if not corridas:
        return {"tipo": tipo, "total_corridas": 0, "ranking": []}
    
    # Filtro de período para avaliações
    filtro_avaliacoes = {}
    if tipo == "mensal":
        inicio_mes = f"{ano_atual}-{mes_atual:02d}-01"
        filtro_avaliacoes["data_avaliacao"] = {"$gte": inicio_mes}
    elif tipo == "anual":
        inicio_ano = f"{ano_atual}-01-01"
        filtro_avaliacoes["data_avaliacao"] = {"$gte": inicio_ano}
    
    # Calcular média geral da plataforma (C na fórmula Bayesiana)
    pipeline_media_geral = [
        {"$match": filtro_avaliacoes} if filtro_avaliacoes else {"$match": {}},
        {"$group": {"_id": None, "media": {"$avg": "$nota_corrida"}, "total": {"$sum": 1}}}
    ]
    result_media = await db.avaliacoes_corridas.aggregate(pipeline_media_geral).to_list(1)
    media_geral_plataforma = result_media[0]["media"] if result_media and result_media[0]["media"] else 3.5
    
    # Parâmetro m (mínimo de avaliações para peso completo)
    m = 30
    min_avaliacoes_ranking = 10
    
    ranking = []
    
    for corrida in corridas:
        corrida_id = corrida["id"]
        
        # Buscar avaliações desta corrida
        filtro_aval = {"corrida_id": corrida_id, **filtro_avaliacoes}
        avaliacoes = await db.avaliacoes_corridas.find(filtro_aval, {"_id": 0}).to_list(None)
        
        v = len(avaliacoes)  # número de avaliações
        
        if v == 0:
            media_corrida = 0
            pontuacao_bayesiana = 0
        else:
            # Calcular média da corrida (R)
            soma_notas = sum(a.get("nota_corrida", 0) for a in avaliacoes)
            media_corrida = soma_notas / v
            
            # Média Bayesiana: (v/(v+m))*R + (m/(v+m))*C
            pontuacao_bayesiana = (v / (v + m)) * media_corrida + (m / (v + m)) * media_geral_plataforma
        
        # Calcular médias por critério
        if v > 0:
            media_org = sum(a.get("organizacao", 0) for a in avaliacoes) / v
            media_perc = sum(a.get("percurso", 0) for a in avaliacoes) / v
            media_kit = sum(a.get("kit_atleta", 0) for a in avaliacoes) / v
            media_hidr = sum(a.get("hidratacao", 0) for a in avaliacoes) / v
            media_pos = sum(a.get("pos_prova", 0) for a in avaliacoes) / v
        else:
            media_org = media_perc = media_kit = media_hidr = media_pos = 0
        
        # Determinar selo
        selo = None
        if v >= 50 and media_corrida >= 4.5:
            selo = "5_estrelas"
        
        ranking.append({
            "id": corrida_id,
            "nome_corrida": corrida.get("nome_corrida"),
            "organizador": corrida.get("organizador"),
            "cidade": corrida.get("cidade"),
            "estado": corrida.get("estado"),
            "data_corrida": corrida.get("data_corrida"),
            "pagina_link": corrida.get("pagina_link"),
            "status": corrida.get("status"),
            "total_avaliacoes": v,
            "media_geral": round(media_corrida, 2),
            "pontuacao_ranking": round(pontuacao_bayesiana, 2),
            "media_organizacao": round(media_org, 2),
            "media_percurso": round(media_perc, 2),
            "media_kit": round(media_kit, 2),
            "media_hidratacao": round(media_hidr, 2),
            "media_pos_prova": round(media_pos, 2),
            "selo": selo,
            "no_ranking": v >= min_avaliacoes_ranking
        })
    
    # Ordenar por pontuação bayesiana, desempate por número de avaliações, depois data mais recente
    ranking.sort(key=lambda x: (
        -x["pontuacao_ranking"],
        -x["total_avaliacoes"],
        x["data_corrida"] if x["data_corrida"] else ""
    ), reverse=False)
    
    # Re-sort para manter ordem correta
    ranking.sort(key=lambda x: (-x["pontuacao_ranking"], -x["total_avaliacoes"]))
    
    # Adicionar posição
    posicao = 1
    for item in ranking:
        if item["no_ranking"]:
            item["posicao"] = posicao
            posicao += 1
        else:
            item["posicao"] = None
    
    # Determinar Top 10 e adicionar selos
    corridas_no_ranking = [c for c in ranking if c["no_ranking"]]
    for i, c in enumerate(corridas_no_ranking[:10]):
        if tipo == "nacional":
            c["selo_top10"] = "top10_brasil"
        elif tipo == "estadual":
            c["selo_top10"] = "top10_estado"
    
    return {
        "tipo": tipo,
        "periodo": {
            "mensal": f"{agora.strftime('%B')} {ano_atual}",
            "anual": str(ano_atual),
            "historico": "Todo período",
            "nacional": "Todo período",
            "estadual": f"Estado: {estado}" if estado else "Todos",
            "cidade": f"Cidade: {cidade}" if cidade else "Todas"
        }.get(tipo, ""),
        "total_corridas": len(ranking),
        "corridas_no_ranking": len([c for c in ranking if c["no_ranking"]]),
        "media_geral_plataforma": round(media_geral_plataforma, 2),
        "ranking": ranking
    }


@api_router.get("/ranking-corridas/stats")
async def get_stats_ranking_corridas():
    """Retorna estatísticas gerais do Ranking das Corridas"""
    
    total_corridas = await db.corridas_eventos.count_documents({"status": {"$ne": "cancelada"}})
    total_avaliacoes = await db.avaliacoes_corridas.count_documents({})
    
    # Média geral
    pipeline_media = [
        {"$group": {"_id": None, "media": {"$avg": "$nota_corrida"}}}
    ]
    result = await db.avaliacoes_corridas.aggregate(pipeline_media).to_list(1)
    media_geral = result[0]["media"] if result and result[0]["media"] else 0
    
    # Corrida mais bem avaliada (mínimo 10 avaliações)
    pipeline_melhor = [
        {"$group": {
            "_id": "$corrida_id",
            "media": {"$avg": "$nota_corrida"},
            "total": {"$sum": 1}
        }},
        {"$match": {"total": {"$gte": 10}}},
        {"$sort": {"media": -1}},
        {"$limit": 1}
    ]
    result_melhor = await db.avaliacoes_corridas.aggregate(pipeline_melhor).to_list(1)
    
    corrida_melhor_avaliada = None
    if result_melhor:
        corrida_id = result_melhor[0]["_id"]
        corrida = await db.corridas_eventos.find_one({"id": corrida_id}, {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1})
        if corrida:
            corrida_melhor_avaliada = {
                **corrida,
                "media": round(result_melhor[0]["media"], 2),
                "avaliacoes": result_melhor[0]["total"]
            }
    
    # Corrida com mais avaliações
    pipeline_mais_aval = [
        {"$group": {
            "_id": "$corrida_id",
            "total": {"$sum": 1}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
    result_mais = await db.avaliacoes_corridas.aggregate(pipeline_mais_aval).to_list(1)
    
    corrida_mais_avaliada = None
    if result_mais:
        corrida_id = result_mais[0]["_id"]
        corrida = await db.corridas_eventos.find_one({"id": corrida_id}, {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1})
        if corrida:
            corrida_mais_avaliada = {
                **corrida,
                "avaliacoes": result_mais[0]["total"]
            }
    
    # Distribuição por estado
    pipeline_estados = [
        {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]
    dist_estados = await db.corridas_eventos.aggregate(pipeline_estados).to_list(None)
    
    return {
        "total_corridas": total_corridas,
        "total_avaliacoes": total_avaliacoes,
        "media_geral": round(media_geral, 2) if media_geral else 0,
        "corrida_melhor_avaliada": corrida_melhor_avaliada,
        "corrida_mais_avaliada": corrida_mais_avaliada,
        "distribuicao_estados": [{"estado": e["_id"], "corridas": e["total"]} for e in dist_estados if e["_id"]]
    }


@api_router.get("/ranking-corridas/estados")
async def get_estados_com_corridas():
    """Lista estados que têm corridas cadastradas"""
    pipeline = [
        {"$match": {"status": {"$ne": "cancelada"}}},
        {"$group": {"_id": "$estado"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.corridas_eventos.aggregate(pipeline).to_list(None)
    return [e["_id"] for e in result]


@api_router.get("/ranking-corridas/cidades")
async def get_cidades_com_corridas(estado: str = None):
    """Lista cidades que têm corridas cadastradas"""
    match_filter = {"status": {"$ne": "cancelada"}}
    if estado:
        match_filter["estado"] = estado
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {"_id": "$cidade"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.corridas_eventos.aggregate(pipeline).to_list(None)
    return [c["_id"] for c in result]


# ============================================================
# AVALIAÇÃO DE CORRIDAS - Sistema IQC (5 critérios)
# ============================================================

@api_router.post("/avaliar-corrida")
async def avaliar_corrida(
    request: Request,
    corrida_id: str = Form(...),
    organizacao: int = Form(...),  # 1-5
    percurso: int = Form(...),     # 1-5
    kit_atleta: int = Form(...),   # 1-5
    hidratacao: int = Form(...),   # 1-5
    pos_prova: int = Form(...),    # 1-5
    participei: bool = Form(...),  # Checkbox obrigatório
    aceito_termo: bool = Form(...),  # Termo de responsabilidade obrigatório
    current_user: dict = Depends(get_current_user)
):
    """
    Registra avaliação de uma corrida por um atleta
    5 critérios IQC (Índice de Qualidade da Corrida)
    Inclui termo de responsabilidade e registro de IP
    """
    from datetime import datetime
    
    # Verificar se é atleta
    if current_user.get("role") not in ["atleta", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Apenas atletas podem avaliar corridas")
    
    # Verificar se confirmou participação
    if not participei:
        raise HTTPException(status_code=400, detail="Você precisa confirmar que participou desta corrida")
    
    # Verificar se aceitou o termo de responsabilidade
    if not aceito_termo:
        raise HTTPException(
            status_code=400, 
            detail="Você precisa aceitar o termo de responsabilidade para submeter a avaliação"
        )
    
    # Capturar IP do avaliador
    ip_avaliador = request.client.host if request.client else "unknown"
    # Tentar capturar IP real se estiver atrás de proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip_avaliador = forwarded_for.split(",")[0].strip()
    
    # Validar notas (1-5)
    for nota, nome in [(organizacao, "Organização"), (percurso, "Percurso"), 
                       (kit_atleta, "Kit Atleta"), (hidratacao, "Hidratação"), 
                       (pos_prova, "Pós Prova")]:
        if not 1 <= nota <= 5:
            raise HTTPException(status_code=400, detail=f"{nome} deve ser entre 1 e 5")
    
    # Verificar se corrida existe
    corrida = await db.corridas_eventos.find_one({"id": corrida_id}, {"_id": 0})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    # Verificar se corrida já ocorreu
    data_corrida = corrida.get("data_corrida", "")
    if data_corrida:
        try:
            data_evento = datetime.strptime(data_corrida, "%Y-%m-%d")
            if data_evento > datetime.now():
                raise HTTPException(
                    status_code=400, 
                    detail="Avaliações disponíveis apenas após a realização da corrida"
                )
        except ValueError:
            pass  # Se não conseguir parsear a data, permite avaliação
    
    # Verificar se já avaliou esta corrida
    avaliacao_existente = await db.avaliacoes_corridas.find_one({
        "corrida_id": corrida_id,
        "atleta_id": current_user.get("id")
    })
    
    if avaliacao_existente:
        raise HTTPException(status_code=400, detail="Você já avaliou esta corrida")
    
    # Calcular nota da corrida (média dos 5 critérios)
    nota_corrida = (organizacao + percurso + kit_atleta + hidratacao + pos_prova) / 5
    
    # Criar avaliação com termo e IP
    avaliacao = {
        "id": str(uuid.uuid4()),
        "corrida_id": corrida_id,
        "atleta_id": current_user.get("id"),
        "atleta_nome": current_user.get("nome"),
        "atleta_email": current_user.get("email"),
        "organizacao": organizacao,
        "percurso": percurso,
        "kit_atleta": kit_atleta,
        "hidratacao": hidratacao,
        "pos_prova": pos_prova,
        "nota_corrida": round(nota_corrida, 2),
        "participei": participei,
        "aceito_termo": aceito_termo,
        "termo_aceito_em": datetime.now().isoformat(),
        "ip_avaliador": ip_avaliador,
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "data_avaliacao": datetime.now().isoformat()
    }
    
    await db.avaliacoes_corridas.insert_one(avaliacao)
    
    # Atualizar estatísticas da corrida
    await atualizar_stats_corrida(corrida_id)
    
    return {
        "message": "Avaliação registrada com sucesso!",
        "nota_corrida": round(nota_corrida, 2),
        "ip_registrado": True
    }


async def atualizar_stats_corrida(corrida_id: str):
    """Atualiza as estatísticas de uma corrida após nova avaliação"""
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"corrida_id": corrida_id}, {"_id": 0}
    ).to_list(None)
    
    if not avaliacoes:
        return
    
    total = len(avaliacoes)
    media_geral = sum(a["nota_corrida"] for a in avaliacoes) / total
    media_org = sum(a["organizacao"] for a in avaliacoes) / total
    media_perc = sum(a["percurso"] for a in avaliacoes) / total
    media_kit = sum(a["kit_atleta"] for a in avaliacoes) / total
    media_hidr = sum(a["hidratacao"] for a in avaliacoes) / total
    media_pos = sum(a["pos_prova"] for a in avaliacoes) / total
    
    await db.corridas_eventos.update_one(
        {"id": corrida_id},
        {"$set": {
            "total_avaliacoes": total,
            "media_geral": round(media_geral, 2),
            "media_organizacao": round(media_org, 2),
            "media_percurso": round(media_perc, 2),
            "media_kit": round(media_kit, 2),
            "media_hidratacao": round(media_hidr, 2),
            "media_pos_prova": round(media_pos, 2)
        }}
    )


@api_router.get("/minhas-avaliacoes-corridas")
async def get_minhas_avaliacoes_corridas(current_user: dict = Depends(get_current_user)):
    """Retorna avaliações feitas pelo atleta logado"""
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"atleta_id": current_user.get("id")},
        {"_id": 0}
    ).to_list(None)
    
    # Enriquecer com dados da corrida
    for aval in avaliacoes:
        corrida = await db.corridas_eventos.find_one(
            {"id": aval["corrida_id"]},
            {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1}
        )
        if corrida:
            aval["corrida"] = corrida
    
    return avaliacoes


@api_router.get("/corrida-avaliacoes/{corrida_id}")
async def get_avaliacoes_corrida(corrida_id: str):
    """Retorna todas as avaliações de uma corrida específica"""
    
    avaliacoes = await db.avaliacoes_corridas.find(
        {"corrida_id": corrida_id},
        {"_id": 0}
    ).sort("data_avaliacao", -1).to_list(None)
    
    return avaliacoes


@api_router.get("/verificar-avaliacao/{corrida_id}")
async def verificar_avaliacao(corrida_id: str, current_user: dict = Depends(get_current_user)):
    """Verifica se o atleta já avaliou uma corrida"""
    
    avaliacao = await db.avaliacoes_corridas.find_one({
        "corrida_id": corrida_id,
        "atleta_id": current_user.get("id")
    })
    
    return {"ja_avaliou": avaliacao is not None}


@api_router.get("/admin/avaliacoes")
async def listar_avaliacoes_admin(
    corrida_id: str = None,
    limite: int = 50,
    admin: dict = Depends(get_admin_user)
):
    """Lista avaliações com informações de IP e termo (admin)"""
    filtro = {}
    if corrida_id:
        filtro["corrida_id"] = corrida_id
    
    avaliacoes = await db.avaliacoes_corridas.find(
        filtro,
        {"_id": 0}
    ).sort("data_avaliacao", -1).limit(limite).to_list(None)
    
    # Enriquecer com nome da corrida
    for av in avaliacoes:
        corrida = await db.corridas_eventos.find_one({"id": av["corrida_id"]}, {"_id": 0, "nome": 1})
        av["corrida_nome"] = corrida.get("nome", "N/A") if corrida else "N/A"
    
    return avaliacoes


@api_router.get("/admin/avaliacoes/termo")
async def get_texto_termo():
    """Retorna o texto do termo de responsabilidade"""
    termo = await db.configuracoes.find_one({"tipo": "termo_avaliacao"}, {"_id": 0})
    
    if not termo:
        return {
            "titulo": "Termo de Responsabilidade para Avaliação de Corridas",
            "texto": """Ao submeter esta avaliação, declaro que:

1. **Participei efetivamente** desta corrida como atleta inscrito;

2. **As informações prestadas são verdadeiras** e baseadas na minha experiência pessoal durante o evento;

3. **Tenho ciência** de que avaliações falsas ou fraudulentas podem resultar em suspensão da minha conta;

4. **Autorizo** o Ranking Run Pró a registrar meu IP e dados de acesso para fins de auditoria e prevenção de fraudes;

5. **Comprometo-me** a avaliar de forma justa e imparcial, considerando apenas os critérios de qualidade do evento;

6. **Estou ciente** de que esta avaliação será pública e poderá influenciar a reputação do evento avaliado.

Este termo tem validade legal conforme a Lei Geral de Proteção de Dados (LGPD) e demais legislações aplicáveis."""
        }
    
    return termo


@api_router.put("/admin/avaliacoes/termo")
async def atualizar_termo_avaliacao(
    titulo: str = Form(...),
    texto: str = Form(...),
    admin: dict = Depends(get_admin_user)
):
    """Atualiza o texto do termo de responsabilidade"""
    termo = {
        "tipo": "termo_avaliacao",
        "titulo": titulo,
        "texto": texto,
        "atualizado_por": admin["nome"],
        "atualizado_em": datetime.now().isoformat()
    }
    
    await db.configuracoes.update_one(
        {"tipo": "termo_avaliacao"},
        {"$set": termo},
        upsert=True
    )
    
    return {"message": "Termo atualizado com sucesso"}


# ============================================================
# REPUTAÇÃO DE AVALIADORES - Sistema Bronze/Prata/Ouro
# ============================================================

# Níveis de reputação
NIVEIS_REPUTACAO = {
    "iniciante": {
        "nome": "Iniciante",
        "descricao": "Começando a avaliar corridas",
        "min_avaliacoes": 0,
        "icone": "⭐",
        "cor": "#6B7280",
        "nivel": 0
    },
    "bronze": {
        "nome": "Avaliador Bronze",
        "descricao": "Avaliador experiente com 5+ avaliações",
        "min_avaliacoes": 5,
        "icone": "🥉",
        "cor": "#CD7F32",
        "nivel": 1
    },
    "prata": {
        "nome": "Avaliador Prata",
        "descricao": "Avaliador dedicado com 15+ avaliações",
        "min_avaliacoes": 15,
        "icone": "🥈",
        "cor": "#C0C0C0",
        "nivel": 2
    },
    "ouro": {
        "nome": "Avaliador Ouro",
        "descricao": "Avaliador exemplar com 30+ avaliações",
        "min_avaliacoes": 30,
        "icone": "🥇",
        "cor": "#FFD700",
        "nivel": 3
    }
}


def calcular_nivel_reputacao(total_avaliacoes: int) -> dict:
    """Calcula o nível de reputação baseado no número de avaliações"""
    nivel_atual = NIVEIS_REPUTACAO["iniciante"]
    
    for codigo, nivel in NIVEIS_REPUTACAO.items():
        if total_avaliacoes >= nivel["min_avaliacoes"]:
            nivel_atual = {**nivel, "codigo": codigo}
    
    return nivel_atual


@api_router.get("/reputacao-avaliador/{atleta_id}")
async def get_reputacao_avaliador(atleta_id: str):
    """Retorna a reputação de um avaliador (público)"""
    
    # Buscar atleta
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0, "id": 1, "nome": 1})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Contar avaliações
    total_avaliacoes = await db.avaliacoes_corridas.count_documents({"atleta_id": atleta_id})
    
    # Calcular nível atual
    nivel_atual = calcular_nivel_reputacao(total_avaliacoes)
    
    # Calcular progresso para o próximo nível
    proximo_nivel = None
    progresso = 100
    faltam = 0
    
    niveis_ordenados = sorted(NIVEIS_REPUTACAO.items(), key=lambda x: x[1]["min_avaliacoes"])
    for i, (codigo, nivel) in enumerate(niveis_ordenados):
        if nivel["min_avaliacoes"] > total_avaliacoes:
            proximo_nivel = {**nivel, "codigo": codigo}
            faltam = nivel["min_avaliacoes"] - total_avaliacoes
            # Calcular progresso entre o nível atual e o próximo
            nivel_anterior = niveis_ordenados[i-1][1]["min_avaliacoes"] if i > 0 else 0
            range_nivel = nivel["min_avaliacoes"] - nivel_anterior
            progresso_atual = total_avaliacoes - nivel_anterior
            progresso = (progresso_atual / range_nivel) * 100 if range_nivel > 0 else 100
            break
    
    # Buscar estatísticas das avaliações
    avaliacoes = await db.avaliacoes_corridas.find(
        {"atleta_id": atleta_id},
        {"_id": 0, "nota_corrida": 1, "data_avaliacao": 1}
    ).to_list(None)
    
    media_notas = sum(a.get("nota_corrida", 0) for a in avaliacoes) / max(1, len(avaliacoes))
    
    # Meses únicos com avaliações
    meses_ativos = len(set(a.get("data_avaliacao", "")[:7] for a in avaliacoes if a.get("data_avaliacao")))
    
    return {
        "atleta": {
            "id": atleta["id"],
            "nome": atleta.get("nome", "")
        },
        "total_avaliacoes": total_avaliacoes,
        "nivel_atual": nivel_atual,
        "proximo_nivel": proximo_nivel,
        "progresso": round(progresso, 1),
        "faltam_para_proximo": faltam,
        "estatisticas": {
            "media_notas_dadas": round(media_notas, 2),
            "meses_ativos": meses_ativos
        },
        "todos_niveis": [
            {
                **nivel,
                "codigo": codigo,
                "conquistado": total_avaliacoes >= nivel["min_avaliacoes"],
                "atual": total_avaliacoes,
                "progresso": min(100, (total_avaliacoes / nivel["min_avaliacoes"]) * 100) if nivel["min_avaliacoes"] > 0 else 100
            }
            for codigo, nivel in sorted(NIVEIS_REPUTACAO.items(), key=lambda x: x[1]["min_avaliacoes"])
            if nivel["min_avaliacoes"] > 0  # Excluir iniciante da lista visual
        ]
    }


@api_router.get("/ranking-avaliadores")
async def get_ranking_avaliadores(limite: int = 20):
    """Retorna o ranking dos melhores avaliadores"""
    
    # Agregar avaliações por atleta
    pipeline = [
        {
            "$group": {
                "_id": "$atleta_id",
                "total_avaliacoes": {"$sum": 1},
                "nome": {"$first": "$atleta_nome"},
                "media_notas": {"$avg": "$nota_corrida"},
                "primeira_avaliacao": {"$min": "$data_avaliacao"},
                "ultima_avaliacao": {"$max": "$data_avaliacao"}
            }
        },
        {"$sort": {"total_avaliacoes": -1}},
        {"$limit": limite}
    ]
    
    resultado = await db.avaliacoes_corridas.aggregate(pipeline).to_list(None)
    
    ranking = []
    for i, r in enumerate(resultado, 1):
        nivel = calcular_nivel_reputacao(r["total_avaliacoes"])
        ranking.append({
            "posicao": i,
            "atleta_id": r["_id"],
            "nome": r.get("nome", "N/A"),
            "total_avaliacoes": r["total_avaliacoes"],
            "media_notas": round(r.get("media_notas", 0), 2),
            "nivel": nivel,
            "primeira_avaliacao": r.get("primeira_avaliacao"),
            "ultima_avaliacao": r.get("ultima_avaliacao")
        })
    
    return {
        "ranking": ranking,
        "total_avaliadores": len(resultado),
        "niveis_disponiveis": [
            {**v, "codigo": k}
            for k, v in sorted(NIVEIS_REPUTACAO.items(), key=lambda x: x[1]["min_avaliacoes"])
            if v["min_avaliacoes"] > 0
        ]
    }


@api_router.get("/minha-reputacao")
async def get_minha_reputacao(current_user: dict = Depends(get_current_user)):
    """Retorna a reputação do atleta logado"""
    return await get_reputacao_avaliador(current_user["id"])


# ============================================================
# RANKING DAS CORRIDAS - ADMIN DASHBOARD
# ============================================================

@api_router.get("/admin/ranking-corridas/dashboard")
async def get_dashboard_ranking_corridas(admin: dict = Depends(get_admin_user)):
    """Dashboard administrativo do Ranking das Corridas"""
    
    # Stats gerais
    total_corridas = await db.corridas_eventos.count_documents({"status": {"$ne": "cancelada"}})
    total_avaliacoes = await db.avaliacoes_corridas.count_documents({})
    
    # Média geral da plataforma
    pipeline_media = [
        {"$group": {"_id": None, "media": {"$avg": "$nota_corrida"}}}
    ]
    result = await db.avaliacoes_corridas.aggregate(pipeline_media).to_list(1)
    media_geral = result[0]["media"] if result and result[0]["media"] else 0
    
    # Corrida melhor avaliada (nacional, mínimo 10 avaliações)
    pipeline_melhor = [
        {"$group": {
            "_id": "$corrida_id",
            "media": {"$avg": "$nota_corrida"},
            "total": {"$sum": 1}
        }},
        {"$match": {"total": {"$gte": 10}}},
        {"$sort": {"media": -1}},
        {"$limit": 1}
    ]
    result_melhor = await db.avaliacoes_corridas.aggregate(pipeline_melhor).to_list(1)
    
    melhor_nacional = None
    if result_melhor:
        corrida = await db.corridas_eventos.find_one(
            {"id": result_melhor[0]["_id"]}, 
            {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1}
        )
        if corrida:
            melhor_nacional = {
                **corrida,
                "media": round(result_melhor[0]["media"], 2),
                "avaliacoes": result_melhor[0]["total"]
            }
    
    # Corrida com mais avaliações (nacional)
    pipeline_mais = [
        {"$group": {"_id": "$corrida_id", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
    result_mais = await db.avaliacoes_corridas.aggregate(pipeline_mais).to_list(1)
    
    mais_avaliada_nacional = None
    if result_mais:
        corrida = await db.corridas_eventos.find_one(
            {"id": result_mais[0]["_id"]},
            {"_id": 0, "nome_corrida": 1, "cidade": 1, "estado": 1}
        )
        if corrida:
            mais_avaliada_nacional = {
                **corrida,
                "avaliacoes": result_mais[0]["total"]
            }
    
    # Melhor avaliada por estado
    pipeline_estados = [
        {"$lookup": {
            "from": "corridas_eventos",
            "localField": "corrida_id",
            "foreignField": "id",
            "as": "corrida"
        }},
        {"$unwind": "$corrida"},
        {"$group": {
            "_id": {"estado": "$corrida.estado", "corrida_id": "$corrida_id"},
            "nome_corrida": {"$first": "$corrida.nome_corrida"},
            "cidade": {"$first": "$corrida.cidade"},
            "media": {"$avg": "$nota_corrida"},
            "total": {"$sum": 1}
        }},
        {"$match": {"total": {"$gte": 5}}},
        {"$sort": {"_id.estado": 1, "media": -1}},
        {"$group": {
            "_id": "$_id.estado",
            "melhor": {"$first": {
                "nome_corrida": "$nome_corrida",
                "cidade": "$cidade",
                "media": "$media",
                "avaliacoes": "$total"
            }}
        }},
        {"$sort": {"_id": 1}}
    ]
    melhores_por_estado = await db.avaliacoes_corridas.aggregate(pipeline_estados).to_list(None)
    
    # Mais avaliada por estado
    pipeline_mais_estado = [
        {"$lookup": {
            "from": "corridas_eventos",
            "localField": "corrida_id",
            "foreignField": "id",
            "as": "corrida"
        }},
        {"$unwind": "$corrida"},
        {"$group": {
            "_id": {"estado": "$corrida.estado", "corrida_id": "$corrida_id"},
            "nome_corrida": {"$first": "$corrida.nome_corrida"},
            "cidade": {"$first": "$corrida.cidade"},
            "total": {"$sum": 1}
        }},
        {"$sort": {"_id.estado": 1, "total": -1}},
        {"$group": {
            "_id": "$_id.estado",
            "mais_avaliada": {"$first": {
                "nome_corrida": "$nome_corrida",
                "cidade": "$cidade",
                "avaliacoes": "$total"
            }}
        }},
        {"$sort": {"_id": 1}}
    ]
    mais_avaliadas_por_estado = await db.avaliacoes_corridas.aggregate(pipeline_mais_estado).to_list(None)
    
    # Distribuição de notas
    pipeline_dist = [
        {"$group": {
            "_id": {"$floor": "$nota_corrida"},
            "total": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    dist_notas = await db.avaliacoes_corridas.aggregate(pipeline_dist).to_list(None)
    
    # Ranking geral (top 20)
    ranking = await get_ranking_corridas_interno(limite=20)
    
    return {
        "stats": {
            "total_corridas": total_corridas,
            "total_avaliacoes": total_avaliacoes,
            "media_geral": round(media_geral, 2) if media_geral else 0
        },
        "melhor_avaliada_nacional": melhor_nacional,
        "mais_avaliada_nacional": mais_avaliada_nacional,
        "melhores_por_estado": [
            {"estado": e["_id"], **e["melhor"]} 
            for e in melhores_por_estado if e["_id"]
        ],
        "mais_avaliadas_por_estado": [
            {"estado": e["_id"], **e["mais_avaliada"]} 
            for e in mais_avaliadas_por_estado if e["_id"]
        ],
        "distribuicao_notas": [
            {"nota": int(d["_id"]), "total": d["total"]} 
            for d in dist_notas if d["_id"] is not None
        ],
        "ranking_top20": ranking
    }


async def get_ranking_corridas_interno(limite: int = 100):
    """Função interna para gerar ranking com Média Bayesiana"""
    
    # Buscar todas as corridas ativas
    corridas = await db.corridas_eventos.find(
        {"status": {"$ne": "cancelada"}},
        {"_id": 0}
    ).to_list(None)
    
    if not corridas:
        return []
    
    # Calcular média geral (C)
    pipeline = [
        {"$group": {"_id": None, "media": {"$avg": "$nota_corrida"}}}
    ]
    result = await db.avaliacoes_corridas.aggregate(pipeline).to_list(1)
    C = result[0]["media"] if result and result[0]["media"] else 3.5
    
    m = 30  # Parâmetro m
    
    ranking = []
    for corrida in corridas:
        v = corrida.get("total_avaliacoes", 0)
        R = corrida.get("media_geral", 0)
        
        # Média Bayesiana
        if v > 0:
            pontuacao = (v / (v + m)) * R + (m / (v + m)) * C
        else:
            pontuacao = 0
        
        # Determinar selos
        selo_5estrelas = v >= 50 and R >= 4.5
        
        ranking.append({
            "id": corrida["id"],
            "nome_corrida": corrida.get("nome_corrida"),
            "organizador": corrida.get("organizador"),
            "cidade": corrida.get("cidade"),
            "estado": corrida.get("estado"),
            "total_avaliacoes": v,
            "media_geral": R,
            "pontuacao_ranking": round(pontuacao, 2),
            "selo_5estrelas": selo_5estrelas,
            "no_ranking": v >= 10
        })
    
    # Ordenar
    ranking.sort(key=lambda x: (-x["pontuacao_ranking"], -x["total_avaliacoes"]))
    
    # Adicionar posição e selo Top 10
    for i, c in enumerate(ranking[:limite]):
        if c["no_ranking"]:
            c["posicao"] = i + 1
            if i < 10:
                c["selo_top10"] = True
        else:
            c["posicao"] = None
    
    return ranking[:limite]


app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Inicia o scheduler de aniversários e monitoramento"""
    logger.info("🚀 Iniciando scheduler de aniversários...")
    
    # Agendar tarefa para rodar às 00:00 todos os dias
    scheduler.add_job(
        enviar_mensagens_aniversario_automatico,
        CronTrigger(hour=0, minute=0),  # 00:00
        id="envio_aniversario_diario",
        replace_existing=True
    )
    
    # Agendar snapshot de métricas a cada 5 minutos
    from services.monitoring_service import save_metrics_snapshot
    scheduler.add_job(
        save_metrics_snapshot,
        'interval',
        minutes=5,
        args=[db],
        id="metrics_snapshot",
        replace_existing=True
    )
    
    # Agendar verificação de alertas a cada 1 minuto
    scheduler.add_job(
        check_and_send_alerts,
        'interval',
        minutes=1,
        id="check_alerts",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler iniciado! Métricas a cada 5min, alertas a cada 1min")


async def check_and_send_alerts():
    """Verifica alertas e envia emails se necessário"""
    from services.monitoring_service import metrics_collector, generate_alert_email_html
    from services.email_service import enviar_email
    
    alerts = metrics_collector.check_alerts()
    
    if alerts:
        # Buscar email do super admin
        admin = await db.admins.find_one({"role": "super_admin"}, {"_id": 0, "email": 1})
        if admin and admin.get("email"):
            health = metrics_collector.get_health_status()
            html = generate_alert_email_html(alerts, health)
            
            await enviar_email(
                destinatario=admin["email"],
                assunto=f"[ALERTA] Sistema - {len(alerts)} problemas detectados",
                html_content=html
            )
            logger.warning(f"⚠️ Alerta enviado para {admin['email']}: {[a['type'] for a in alerts]}")


@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    client.close()
