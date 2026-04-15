from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, UploadFile, File, Form, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from security_middleware import SecurityHeadersMiddleware
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

ANO_ATUAL = datetime.now().year
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

# Servir arquivos de uploads (local - legado)
uploads_path = Path("/app/uploads")
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Também montar em /api/uploads para funcionar com o ingress do Kubernetes
app.mount("/api/uploads", StaticFiles(directory=str(uploads_path)), name="api_uploads")


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
from routes.corridas_eventos_routes import router as corridas_eventos_router
from routes.aniversariantes_routes import router as aniversariantes_router
from routes.instagram_routes import router as instagram_router
from routes.websocket_routes import router as websocket_router
from routes.dashboard_stats_routes import router as dashboard_stats_router
from routes.mensagens_admin_routes import router as mensagens_admin_router
from routes.assessorias_routes import get_ranking_assessorias
from routes.badges_routes import router as badges_router
from routes.indicacao_routes import router as indicacao_router
from routes.rankings_routes import router as rankings_router
from routes.regulamento_routes import router as regulamento_router
from routes.autorizacoes_routes import router as autorizacoes_router
from routes.feed_routes import router as feed_router
from routes.liga_assessorias_routes import router as liga_assessorias_router
from routes.ranking_corridas_routes import router as ranking_corridas_router
from routes.configuracoes_routes import router as configuracoes_router
from routes.historico_routes import router as historico_router
from routes.strava_routes import router as strava_router
from routes.strava_atividades_routes import router as strava_atividades_router
from routes.raio_x_routes import router as raio_x_router
from routes.pagamentos_routes import router as pagamentos_router
from routes.email_routes import router as email_router
from routes.efi_routes import router as efi_router
from routes.financeiro_routes import router as financeiro_router
from routes.equipe_chat_routes import router as equipe_chat_router
from routes.retencao_routes import router as retencao_router
from routes.scraping_routes import router as scraping_router
from routes.backup_routes import router as backup_router
from routes.whatsapp_routes import router as whatsapp_router
from routes.corridas_parceiras_routes import router as corridas_parceiras_router
from routes.parceiros_routes import router as parceiros_router
from routes.exportacoes_routes import router as exportacoes_router
from routes.cloud_storage_routes import router as cloud_storage_router
from routes.premiacao_routes import router as premiacao_router
from routes.temporadas_routes import router as temporadas_router

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
api_router.include_router(corridas_eventos_router)
api_router.include_router(aniversariantes_router)
api_router.include_router(instagram_router)
api_router.include_router(websocket_router)
api_router.include_router(dashboard_stats_router)
api_router.include_router(mensagens_admin_router)
api_router.include_router(badges_router)
api_router.include_router(indicacao_router)
api_router.include_router(rankings_router)
api_router.include_router(regulamento_router)
api_router.include_router(autorizacoes_router)
api_router.include_router(feed_router)
api_router.include_router(liga_assessorias_router)
api_router.include_router(ranking_corridas_router)
api_router.include_router(configuracoes_router)
api_router.include_router(historico_router)
api_router.include_router(strava_router)
api_router.include_router(strava_atividades_router)
api_router.include_router(raio_x_router)
api_router.include_router(pagamentos_router)
api_router.include_router(email_router)
api_router.include_router(efi_router)
api_router.include_router(financeiro_router)
api_router.include_router(equipe_chat_router)
api_router.include_router(retencao_router)
api_router.include_router(scraping_router)
api_router.include_router(backup_router)
api_router.include_router(whatsapp_router)
api_router.include_router(corridas_parceiras_router)
api_router.include_router(parceiros_router)
api_router.include_router(exportacoes_router)
api_router.include_router(cloud_storage_router)
api_router.include_router(premiacao_router)
api_router.include_router(temporadas_router)


# Endpoint genérico para download de conteúdo CSV gerado no frontend
@api_router.post("/admin/download-csv")
async def download_csv_content(
    request: Request,
    current_user: dict = Depends(get_admin_user)
):
    """Recebe conteúdo CSV do frontend e retorna como arquivo para download"""
    form = await request.form()
    csv_content = form.get("csv_content", "")
    filename = request.query_params.get("filename", "export.csv")
    
    if not csv_content:
        raise HTTPException(status_code=400, detail="Conteúdo CSV vazio")
    
    csv_bytes = csv_content.encode('utf-8')
    
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

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
# - /admin/atletas/{atleta_id}/promover-dono-assessoria migrado para routes/admin_routes.py


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
        ano=ANO_ATUAL
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


@api_router.post("/admin/resumo-semanal/disparar")
async def admin_disparar_resumo_semanal(admin: dict = Depends(get_admin_user)):
    """Admin dispara manualmente o resumo semanal para todos os atletas"""
    from services.resumo_semanal_atleta import gerar_resumo_semanal_atletas
    resultado = await gerar_resumo_semanal_atletas()
    return {"message": "Resumo semanal enviado!", "resultado": resultado}


@api_router.get("/admin/resumo-semanal/historico")
async def admin_historico_resumo_semanal(admin: dict = Depends(get_admin_user)):
    """Retorna historico dos disparos de resumo semanal"""
    logs = await db.logs_scheduler.find(
        {"tipo": "resumo_semanal_atletas"},
        {"_id": 0}
    ).sort("data", -1).limit(20).to_list(None)
    return {"historico": logs}



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
        ano=ANO_ATUAL
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
    ano_atual = ANO_ATUAL
    
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
    await db.ranking_povao.delete_many({"ano": ANO_ATUAL})
    
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
            "ano": ANO_ATUAL,
            "modalidade": "povao_pace_livre"
        }, {"_id": 0}).to_list(None)
        
        if not corridas:
            continue
        
        pontos_total = sum(c.get("pontos_povao", 0) for c in corridas)
        total_corridas = len(corridas)
        distancia_acumulada = sum(extrair_distancia_km(c.get("distancia", "5KM")) for c in corridas)
        
        ranking_docs.append(RankingPovao(
            usuario_id=usuario["id"],
            ano=ANO_ATUAL,
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
# [REFATORADO] Endpoints /ranking/categoria, /ranking/anos-disponiveis migrados para routes/ranking_routes.py

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

# [REFATORADO] /ranking/anos-disponiveis migrado para routes/ranking_routes.py

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
                {"ano": ANO_ATUAL, "categoria": cat_db, "genero": gen_db},
                {"_id": 0}
            ).sort("pontos_total", -1).to_list(None)
            
            for rank in ranking_list:
                usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
                if usuario:
                    writer.writerow([
                        rank.get("ranking_categoria", 0),
                        usuario["nome"],
                        usuario.get("equipe", ""),
                        usuario.get("cidade", ""),
                        usuario.get("estado", ""),
                        rank.get("faixa_etaria", ""),
                        rank.get("total_corridas", 0),
                        rank.get("pontos_total", 0)
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
            {"ano": ANO_ATUAL, "categoria": cat_db, "genero": gen_db},
            {"_id": 0}
        ).sort("pontos_total", -1).to_list(None)
        
        writer.writerow(["Colocação", "Nome", "Equipe", "Cidade", "UF", "Faixa", "Corridas", "Pontos"])
        
        for rank in ranking_list:
            usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
            if usuario:
                writer.writerow([
                    rank.get("ranking_categoria", 0),
                    usuario["nome"],
                    usuario.get("equipe", ""),
                    usuario.get("cidade", ""),
                    usuario.get("estado", ""),
                    rank.get("faixa_etaria", ""),
                    rank.get("total_corridas", 0),
                    rank.get("pontos_total", 0)
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
                {"ano": ANO_ATUAL, "categoria": cat_db, "genero": gen_db},
                {"_id": 0}
            ).sort("pontos_total", -1).to_list(None)
            
            for rank in ranking_list:
                usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
                if usuario:
                    ws.append([
                        rank.get("ranking_categoria", 0),
                        usuario["nome"],
                        usuario.get("equipe", ""),
                        usuario.get("cidade", ""),
                        usuario.get("estado", ""),
                        rank.get("faixa_etaria", ""),
                        rank.get("total_corridas", 0),
                        rank.get("pontos_total", 0)
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
            {"ano": ANO_ATUAL, "categoria": cat_db, "genero": gen_db},
            {"_id": 0}
        ).sort("pontos_total", -1).to_list(None)
        
        for rank in ranking_list:
            usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
            if usuario:
                ws.append([
                    rank.get("ranking_categoria", 0),
                    usuario["nome"],
                    usuario.get("equipe", ""),
                    usuario.get("cidade", ""),
                    usuario.get("estado", ""),
                    rank.get("faixa_etaria", ""),
                    rank.get("total_corridas", 0),
                    rank.get("pontos_total", 0)
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
        ranking = await db.ranking_povao.find_one({"usuario_id": atleta_id, "ano": ANO_ATUAL}, {"_id": 0})
        # Para Povão, mostrar a posição no ranking
        melhor_colocacao = ranking.get("ranking_genero", 0) if ranking else 0
        total_corridas = ranking["total_corridas"] if ranking else 0
        pontos_carreira = ranking["pontos_total"] if ranking else 0
    else:
        ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": ANO_ATUAL}, {"_id": 0})
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
        {"usuario_id": atleta_id, "ano": ANO_ATUAL},
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
    
    ranking = await db.ranking_anual.find_one({"usuario_id": atleta_id, "ano": ANO_ATUAL}, {"_id": 0})
    
    categoria_nome = {
        "normal": "Normal",
        "pcd": "PCD",
        "cadeirante": "Cadeirante"
    }.get(usuario["categoria"], "Normal")
    
    genero_nome = "Masculino" if usuario["genero"] == "M" else "Feminino"
    
    texto_compartilhar = f"🏆 Ranking Run Pró {ANO_ATUAL}\n\n"
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
        "url_compartilhar": f"{os.environ.get('FRONTEND_URL', 'https://app.rankingrun.com.br')}/atleta/{atleta_id}"
    }


# ==================== OUTROS ====================

@api_router.get("/ranking/nacional", response_model=List[RankingResponse])
async def get_ranking_nacional(ano: int = Query(ANO_ATUAL)):
    ranking_list = await db.ranking_anual.find(
        {"ano": ano},
        {"_id": 0}
    ).sort("pontos_total", -1).to_list(None)
    
    response = []
    # Buscar IDs de atletas com autorização ativa
    autorizacoes_ativas = set()
    auth_cursor = db.autorizacoes.find({"status": "ativa"}, {"_id": 0, "atleta_id": 1})
    async for auth in auth_cursor:
        autorizacoes_ativas.add(auth["atleta_id"])

    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            min_corridas = get_min_corridas_categoria(rank.get("categoria", "normal"))
            response.append(RankingResponse(
                id=usuario["id"],
                colocacao=rank.get("ranking_nacional", 0),
                uf=rank.get("estado", ""),
                foto_url=usuario.get("foto_url", ""),
                nome=usuario.get("nome", ""),
                cidade=f"{usuario.get('cidade', '')}/{usuario.get('estado', '')}",
                equipe=usuario.get("equipe", ""),
                faixa_etaria=rank.get("faixa_etaria", ""),
                total_corridas=rank.get("total_corridas", 0),
                pontos=rank.get("pontos_total", 0),
                is_elite=(rank.get("pontos_total", 0) >= 100),
                is_pendente=(rank.get("total_corridas", 0) < min_corridas),
                is_premium=(usuario["id"] in autorizacoes_ativas)
            ))
    
    return response

# [REFATORADO] /ranking/estados, /ranking/faixas-etarias, /ranking/equipes migrados para routes/ranking_routes.py
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
            "mensagem_bio": "Ajudamos milhares de Atletas pelo Brasil, faça parte do nosso Time!",
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
                data_corrida = f"{ANO_ATUAL}-{mes:02d}-{dia:02d}"
                
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
                    ano=ANO_ATUAL
                )
                
                await db.corridas.insert_one(corrida.model_dump())
                corridas_criadas += 1
    
    await calcular_ranking()
    
    # Verificar conquistas para todos os atletas (incluindo donos de assessoria)
    atletas = await db.usuarios.find({"role": {"$in": ["atleta", "dono_assessoria"]}}, {"_id": 0}).to_list(None)
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




# ========== RANKING RUN INSIDE - INSTAGRAM ANALYTICS ==========
# [REFATORADO] Todos os endpoints e funções de Instagram migrados para routes/instagram_routes.py:
# - /admin/instagram/buscar/{username} (GET)
# - /admin/instagram/analisar-automatico/{username} (POST)
# - /admin/instagram/analisar (POST)
# - /admin/instagram/export/{analysis_id} (GET)
# - /admin/instagram/export-csv/{analysis_id} (GET)
# - /admin/instagram/analises (GET)
# - /admin/instagram/analises/{analysis_id} (GET, DELETE)
# - /admin/instagram/analisar-simplificado (POST)
# - /admin/instagram/stats (GET)
# - /admin/instagram/ranking (GET)

# ==================== INCLUDE ROUTER (movido para o final) ====================

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', 'https://app.rankingrun.com.br').split(','),
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "Content-Disposition"],
)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# GZip compression - comprime respostas > 500 bytes (reduz ~70% do trafego)
app.add_middleware(GZipMiddleware, minimum_size=500)

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
        
        # Buscar aniversariantes de hoje (atletas e donos de assessoria)
        hoje = datetime.now()
        atletas = await db.usuarios.find({"role": {"$in": ["atleta", "dono_assessoria"]}}, {"_id": 0}).to_list(None)
        
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



# Endpoints de liga-assessorias removidos - migrados para routes/liga_assessorias_routes.py

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
    
    # Buscar atletas da equipe (incluindo dono de assessoria)
    atletas = await db.usuarios.find(
        {"equipe": nome_equipe, "role": {"$in": ["atleta", "dono_assessoria"]}},
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
# [REFATORADO] REGULAMENTO - migrado para routes/regulamento_routes.py
# ============================================================


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
        {"role": {"$in": ["atleta", "dono_assessoria"]}},
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
    
    # Verificar se o atleta existe (pode ser atleta ou dono de assessoria)
    atleta = await db.usuarios.find_one({"id": atleta_id, "role": {"$in": ["atleta", "dono_assessoria"]}}, {"_id": 0})
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


# Rotas de autorizar/revogar por atleta_id (usadas pelo DashboardAutorizacoes)
class AutorizarAtletaRequest(BaseModel):
    atleta_id: str
    tipo_plano: str = "ate_fim_ano"  # ate_fim_ano, plano_anual, data_customizada
    dias: int = 365
    data_expiracao_custom: Optional[str] = None  # formato YYYY-MM-DD


class RevogarAtletaRequest(BaseModel):
    atleta_id: str


@api_router.post("/admin/autorizacoes/autorizar")
async def autorizar_atleta(dados: AutorizarAtletaRequest, admin: dict = Depends(get_admin_user)):
    """Autoriza acesso premium de um atleta (por atleta_id)"""
    atleta = await db.usuarios.find_one(
        {"id": dados.atleta_id, "role": {"$in": ["atleta", "dono_assessoria"]}},
        {"_id": 0, "id": 1, "nome": 1, "email": 1}
    )
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta nao encontrado")

    agora = datetime.now(timezone.utc)

    # Desativar autorizacoes anteriores
    await db.autorizacoes.update_many(
        {"atleta_id": dados.atleta_id, "status": "ativa"},
        {"$set": {"status": "substituida", "data_substituicao": agora.isoformat()}}
    )

    # Calcular data de expiracao baseado no tipo
    if dados.tipo_plano == "data_customizada" and dados.data_expiracao_custom:
        try:
            parts = dados.data_expiracao_custom.split("-")
            data_expiracao = datetime(int(parts[0]), int(parts[1]), int(parts[2]), 23, 59, 59, tzinfo=timezone.utc)
        except Exception:
            raise HTTPException(status_code=400, detail="Data invalida. Use formato AAAA-MM-DD")
        descricao = f"Plano Premium ate {dados.data_expiracao_custom}"
        plano_nome = f"Ate {parts[2]}/{parts[1]}/{parts[0]}"
    elif dados.tipo_plano == "ate_fim_ano":
        data_expiracao = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        descricao = "Plano Premium ate 31/12/2026"
        plano_nome = "Ate 31/12/2026"
    elif dados.tipo_plano == "plano_anual":
        data_expiracao = agora + timedelta(days=365)
        descricao = "Plano Anual (1 ano a partir da ativacao)"
        plano_nome = "Plano Anual"
    else:
        data_expiracao = agora + timedelta(days=dados.dias)
        descricao = f"Plano por {dados.dias} dias"
        plano_nome = f"{dados.dias} dias"

    autorizacao = {
        "id": str(uuid.uuid4()),
        "atleta_id": dados.atleta_id,
        "tipo": "premium",
        "plano_id": dados.tipo_plano,
        "plano_nome": plano_nome,
        "descricao": descricao,
        "duracao_dias": (data_expiracao - agora).days,
        "data_criacao": agora.isoformat(),
        "data_inicio": agora.isoformat(),
        "data_expiracao": data_expiracao.isoformat(),
        "criado_por": "admin_manual",
        "criado_por_nome": admin.get("nome", "Admin"),
        "admin_id": admin.get("id"),
        "observacao": f"Autorizado manualmente por {admin.get('nome', 'Admin')}",
        "status": "ativa",
    }
    await db.autorizacoes.insert_one(autorizacao)

    # Registrar transacao financeira (vinculo com Financeiro)
    tx_id = str(uuid.uuid4())
    transaction = {
        "id": tx_id,
        "user_id": dados.atleta_id,
        "user_email": atleta.get("email", ""),
        "user_nome": atleta.get("nome", ""),
        "gateway": "admin_manual",
        "tipo": "admin_manual",
        "origem": "admin_manual",
        "plano": dados.tipo_plano,
        "plano_nome": plano_nome,
        "amount": 0,
        "parcelas": 0,
        "valor_parcela": 0,
        "currency": "brl",
        "payment_status": "paid",
        "status": "approved",
        "admin_nome": admin.get("nome", "Admin"),
        "admin_id": admin.get("id"),
        "autorizacao_id": autorizacao["id"],
        "data_criacao": agora.isoformat(),
        "data_atualizacao": agora.isoformat(),
    }
    await db.payment_transactions.insert_one(transaction)

    return {
        "message": f"Atleta {atleta.get('nome', '')} autorizado! Acesso ate {data_expiracao.strftime('%d/%m/%Y')}",
        "autorizacao_id": autorizacao["id"],
        "data_expiracao": data_expiracao.isoformat(),
    }


@api_router.post("/admin/autorizacoes/revogar")
async def revogar_atleta(dados: RevogarAtletaRequest, admin: dict = Depends(get_admin_user)):
    """Revoga todas as autorizacoes ativas de um atleta (por atleta_id)"""
    result = await db.autorizacoes.update_many(
        {"atleta_id": dados.atleta_id, "status": "ativa"},
        {"$set": {
            "status": "revogada",
            "revogado_por": admin.get("nome", "Admin"),
            "admin_revogacao_id": admin.get("id"),
            "data_revogacao": datetime.now(timezone.utc).isoformat(),
        }}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Nenhuma autorizacao ativa encontrada para este atleta")

    return {"message": f"Autorizacao revogada ({result.modified_count} revogada(s))"}


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
# [REFATORADO] Endpoints de corridas-eventos migrados para routes/corridas_eventos_routes.py
# ============================================================

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
    
    # Agendar limpeza semanal COMPLETA do feed todo domingo às 23:59:59
    scheduler.add_job(
        limpeza_semanal_completa,
        CronTrigger(day_of_week='sun', hour=23, minute=59, second=0),
        id="limpeza_semanal_completa",
        replace_existing=True
    )
    
    # Agendar sincronização automática do Strava a cada hora
    from services.strava_sync_scheduler import sync_all_strava_users
    scheduler.add_job(
        sync_all_strava_users,
        'interval',
        hours=1,
        id="strava_sync_hourly",
        replace_existing=True
    )
    logger.info("📊 Sincronização Strava agendada para cada 1 hora")
    
    # Agendar relatório semanal por e-mail (todo domingo às 20:00)
    from services.relatorio_semanal import enviar_relatorio_semanal
    scheduler.add_job(
        enviar_relatorio_semanal,
        CronTrigger(day_of_week='sun', hour=20, minute=0),
        id="relatorio_semanal_email",
        replace_existing=True
    )
    logger.info("📧 Relatório semanal agendado para domingos às 20:00")
    
    # Agendar resumo semanal para atletas (toda segunda às 8:00)
    from services.resumo_semanal_atleta import gerar_resumo_semanal_atletas
    scheduler.add_job(
        gerar_resumo_semanal_atletas,
        CronTrigger(day_of_week='mon', hour=8, minute=0),
        id="resumo_semanal_atletas",
        replace_existing=True
    )
    logger.info("📊 Resumo semanal para atletas agendado para segundas às 08:00")
    
    # Varredura automática de corridas REMOVIDA (agora é manual)
    
    # Agendar backup automático toda quarta-feira às 02:30
    from routes.backup_routes import executar_backup
    async def job_backup_semanal():
        try:
            await executar_backup(tipo="automatico", admin_id="system")
            logger.info("Backup semanal automático concluído com sucesso")
        except Exception as e:
            logger.error(f"Erro no backup semanal automático: {e}")

    scheduler.add_job(
        job_backup_semanal,
        CronTrigger(day_of_week='wed', hour=2, minute=30),
        id="backup_semanal_quarta",
        replace_existing=True
    )
    logger.info("Backup semanal agendado para quartas às 02:30")
    
    scheduler.start()
    logger.info("✅ Scheduler iniciado! Métricas a cada 5min, alertas a cada 1min, limpeza dom 23:59, Strava 1h, Relatório dom 20h")

    # Inicializar Object Storage em nuvem
    try:
        from services.object_storage import init_storage
        init_storage()
        logger.info("☁️ Object Storage em nuvem inicializado com sucesso")
    except Exception as e:
        logger.warning(f"⚠️ Object Storage não inicializado (uploads usarão disco local): {e}")

    # Criar índices MongoDB para performance
    try:
        # Garantir super_admin para emails autorizados
        super_admin_emails_str = os.environ.get("SUPER_ADMIN_EMAILS", "")
        if super_admin_emails_str:
            for email in super_admin_emails_str.split(","):
                email = email.strip()
                if email:
                    await db.usuarios.update_one(
                        {"email": email},
                        {"$set": {"role": "super_admin"}},
                    )

        await db.usuarios.create_index("id", unique=True)
        await db.usuarios.create_index("email")
        await db.usuarios.create_index([("estado", 1), ("cidade", 1)])
        await db.usuarios.create_index("role")
        await db.usuarios.create_index("equipe")
        await db.usuarios.create_index([("genero", 1), ("categoria", 1)])
        await db.corridas.create_index("usuario_id")
        await db.corridas.create_index([("usuario_id", 1), ("status", 1)])
        await db.corridas.create_index("status")
        await db.corridas.create_index("data")
        await db.corridas.create_index([("data", 1), ("usuario_id", 1)])
        await db.corridas.create_index([("data", 1), ("modalidade", 1)])
        await db.ranking_anual.create_index([("ano", 1), ("usuario_id", 1)])
        await db.ranking_anual.create_index([("ano", 1), ("categoria", 1), ("genero", 1)])
        await db.ranking_anual.create_index([("ano", 1), ("pontos_total", -1)])
        await db.ranking_povao.create_index([("ano", 1), ("usuario_id", 1)])
        await db.ranking_povao.create_index([("ano", 1), ("pontos_total", -1)])
        await db.notificacoes.create_index([("usuario_id", 1), ("tipo", 1), ("lida", 1)])
        await db.notificacoes.create_index([("mensagem_id", 1), ("tipo", 1)])
        await db.mensagens_admin.create_index("id")
        await db.resultados.create_index("usuario_id")
        await db.transacoes.create_index("usuario_id")
        await db.transacoes.create_index("status")
        await db.transacoes.create_index("created_at")
        await db.transacoes.create_index([("gateway", 1), ("status", 1)])
        await db.conquistas_atleta.create_index("usuario_id")
        await db.conquistas_atleta.create_index([("usuario_id", 1), ("conquista_codigo", 1)])
        await db.feed_posts.create_index([("created_at", -1)])
        await db.feed_posts.create_index("usuario_id")
        logger.info("Indices MongoDB criados/verificados")
    except Exception as e:
        logger.warning(f"Erro ao criar índices: {e}")


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


async def limpeza_semanal_completa():
    """
    Limpeza semanal completa: posts, comentários, reações, stories, chat e arquivos da nuvem.
    Executado automaticamente todo domingo às 23:59.
    Garante privacidade dos usuários e mantém o sistema leve.
    """
    logger.info("🧹 Iniciando limpeza semanal COMPLETA (feed + stories + chat + arquivos)...")

    resumo = {
        "posts": 0, "comentarios": 0, "reacoes": 0,
        "stories": 0, "chat_msgs": 0, "chat_feed": 0,
    }

    try:
        # 1. Feed Posts
        posts = await db.feed_posts.count_documents({})
        if posts:
            await db.feed_posts.delete_many({})
            resumo["posts"] = posts

        # 2. Feed Comentários (não fixados)
        comentarios = await db.feed_comentarios.count_documents({"fixado": {"$ne": True}})
        if comentarios:
            await db.feed_comentarios.delete_many({"fixado": {"$ne": True}})
            resumo["comentarios"] = comentarios

        # 3. Feed Reações
        reacoes = await db.feed_reacoes.count_documents({})
        if reacoes:
            await db.feed_reacoes.delete_many({})
            resumo["reacoes"] = reacoes

        # 4. Stories
        stories = await db.stories.count_documents({})
        if stories:
            await db.stories.delete_many({})
            resumo["stories"] = stories

        # 5. Chat Mensagens (equipe)
        chat_msgs = await db.equipe_mensagens.count_documents({})
        if chat_msgs:
            await db.equipe_mensagens.delete_many({})
            resumo["chat_msgs"] = chat_msgs

        # 6. Chat Feed (equipe)
        chat_feed = await db.equipe_feed.count_documents({})
        if chat_feed:
            await db.equipe_feed.delete_many({})
            resumo["chat_feed"] = chat_feed

        # 7. Limpar cache do feed
        try:
            from services.cache_service import cache_service
            await cache_service.invalidate_feed()
        except Exception:
            pass

        total = sum(resumo.values())

        # Registrar log
        await db.logs_scheduler.insert_one({
            "tipo": "limpeza_semanal_completa",
            "data": datetime.now(timezone.utc).isoformat(),
            "resumo": resumo,
            "total_removidos": total,
            "status": "sucesso"
        })

        logger.info(f"✅ Limpeza semanal concluída! {total} itens removidos: "
                     f"{resumo['posts']} posts, {resumo['comentarios']} comentários, "
                     f"{resumo['reacoes']} reações, {resumo['stories']} stories, "
                     f"{resumo['chat_msgs']} mensagens chat, {resumo['chat_feed']} posts chat")

    except Exception as e:
        logger.error(f"❌ Erro na limpeza semanal: {e}")
        await db.logs_scheduler.insert_one({
            "tipo": "limpeza_semanal_completa",
            "data": datetime.now(timezone.utc).isoformat(),
            "status": "erro",
            "erro": str(e)
        })


@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    client.close()
