from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
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

# Servir arquivos de uploads
uploads_path = Path("/app/uploads")
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


# ==================== AUTHENTICATION ====================

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


# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/register")
async def register_atleta(dados: UsuarioRegister):
    """Cadastro de novo atleta"""
    existing = await db.usuarios.find_one({"email": dados.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Validar: PCD e Cadeirante não podem participar do Povão
    if dados.modalidade_usuario == "povao_pace_livre" and dados.categoria in ["pcd", "cadeirante"]:
        raise HTTPException(
            status_code=400, 
            detail="A modalidade 'Ranking do Povão - Pace Livre' não está disponível para atletas PCD ou Cadeirantes."
        )
    
    faixa = calcular_faixa_etaria(dados.data_nascimento)
    
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
        is_active=True,
        etnia=dados.etnia,
        apelido=dados.apelido,
        modalidade_usuario=dados.modalidade_usuario
    )
    
    doc = usuario.model_dump()
    await db.usuarios.insert_one(doc)
    
    token = create_access_token({"sub": usuario.id})
    
    return {
        "message": "Cadastro realizado com sucesso!",
        "token": token,
        "user": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "role": usuario.role,
            "modalidade_usuario": usuario.modalidade_usuario
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
            "role": user["role"],
            "foto_url": user.get("foto_url", ""),
            "categoria": user.get("categoria", "normal")
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
        "foto_url": current_user["foto_url"],
        "modalidade_usuario": current_user.get("modalidade_usuario", "profissional_amador")
    }


# ==================== NOTIFICAÇÕES ====================

@api_router.get("/notificacoes")
async def get_notificacoes(current_user: dict = Depends(get_current_user)):
    """Retorna notificações do usuário"""
    notificacoes = await db.notificacoes.find(
        {"usuario_id": current_user["id"]},
        {"_id": 0}
    ).sort("data_criacao", -1).limit(50).to_list(None)
    
    nao_lidas = sum(1 for n in notificacoes if not n.get("lida", False))
    
    return {
        "notificacoes": notificacoes,
        "nao_lidas": nao_lidas
    }

@api_router.post("/notificacoes/{notificacao_id}/ler")
async def marcar_notificacao_lida(notificacao_id: str, current_user: dict = Depends(get_current_user)):
    """Marca notificação como lida"""
    await db.notificacoes.update_one(
        {"id": notificacao_id, "usuario_id": current_user["id"]},
        {"$set": {"lida": True}}
    )
    return {"message": "Notificação marcada como lida"}

@api_router.post("/notificacoes/ler-todas")
async def marcar_todas_lidas(current_user: dict = Depends(get_current_user)):
    """Marca todas notificações como lidas"""
    await db.notificacoes.update_many(
        {"usuario_id": current_user["id"]},
        {"$set": {"lida": True}}
    )
    return {"message": "Todas notificações marcadas como lidas"}

async def criar_notificacao(usuario_id: str, tipo: str, titulo: str, mensagem: str, dados_extras: dict = {}):
    """Helper para criar notificação"""
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        dados_extras=dados_extras
    )
    await db.notificacoes.insert_one(notificacao.model_dump())
    return notificacao


# ==================== CONQUISTAS ====================

@api_router.get("/conquistas")
async def get_conquistas(current_user: dict = Depends(get_current_user)):
    """Retorna conquistas do atleta"""
    conquistas_atleta = await db.conquistas_atleta.find(
        {"usuario_id": current_user["id"]},
        {"_id": 0}
    ).to_list(None)
    
    conquistas_com_detalhes = []
    for ca in conquistas_atleta:
        if ca["conquista_codigo"] in CONQUISTAS:
            conquista = CONQUISTAS[ca["conquista_codigo"]]
            conquistas_com_detalhes.append({
                **conquista,
                "codigo": ca["conquista_codigo"],
                "data_conquista": ca["data_conquista"]
            })
    
    return {
        "conquistas": conquistas_com_detalhes,
        "total": len(conquistas_com_detalhes)
    }

@api_router.get("/conquistas/disponiveis")
async def get_conquistas_disponiveis():
    """Lista todas conquistas disponíveis"""
    return [
        {"codigo": k, **v}
        for k, v in CONQUISTAS.items()
    ]

async def verificar_conquistas(usuario_id: str):
    """Verifica e concede conquistas ao atleta"""
    usuario = await db.usuarios.find_one({"id": usuario_id}, {"_id": 0})
    if not usuario:
        return
    
    corridas = await db.corridas.find({"usuario_id": usuario_id}, {"_id": 0}).to_list(None)
    ranking = await db.ranking_anual.find_one({"usuario_id": usuario_id, "ano": 2025}, {"_id": 0})
    
    conquistas_atuais = await db.conquistas_atleta.find(
        {"usuario_id": usuario_id},
        {"_id": 0}
    ).to_list(None)
    conquistas_codigos = [c["conquista_codigo"] for c in conquistas_atuais]
    
    novas_conquistas = []
    
    # Verificar primeiro lugar
    if "primeiro_lugar" not in conquistas_codigos:
        if any(c["colocacao"] == 1 for c in corridas):
            novas_conquistas.append("primeiro_lugar")
    
    # Verificar pódio
    if "podio" not in conquistas_codigos:
        if any(c["colocacao"] <= 3 for c in corridas):
            novas_conquistas.append("podio")
    
    # Verificar 10 corridas
    if "10_corridas" not in conquistas_codigos:
        if len(corridas) >= 10:
            novas_conquistas.append("10_corridas")
    
    # Verificar elite
    if "elite" not in conquistas_codigos and ranking:
        if ranking.get("pontos_total", 0) >= 100:
            novas_conquistas.append("elite")
    
    # Verificar maratonista
    if "maratonista" not in conquistas_codigos:
        if any(c["distancia"] == "42KM" for c in corridas):
            novas_conquistas.append("maratonista")
    
    # Verificar consistente (6 meses diferentes)
    if "consistente" not in conquistas_codigos:
        meses = set(c["data"][:7] for c in corridas)
        if len(meses) >= 6:
            novas_conquistas.append("consistente")
    
    # Conceder novas conquistas
    for codigo in novas_conquistas:
        conquista_atleta = ConquistaAtleta(
            usuario_id=usuario_id,
            conquista_codigo=codigo
        )
        await db.conquistas_atleta.insert_one(conquista_atleta.model_dump())
        
        # Notificar
        conquista = CONQUISTAS[codigo]
        await criar_notificacao(
            usuario_id=usuario_id,
            tipo="conquista",
            titulo=f"Nova conquista: {conquista['nome']}!",
            mensagem=conquista['descricao'],
            dados_extras={"conquista_codigo": codigo, "icone": conquista['icone']}
        )
    
    return novas_conquistas


# ==================== PERFIL DO ATLETA ====================

@api_router.get("/atletas/meu-perfil")
async def get_meu_perfil(current_user: dict = Depends(get_current_user)):
    """Retorna dados completos do perfil do atleta logado"""
    usuario = await db.usuarios.find_one({"id": current_user["id"]}, {"_id": 0, "password_hash": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    ranking = await db.ranking_anual.find_one({"usuario_id": current_user["id"], "ano": 2025}, {"_id": 0})
    
    return {
        **usuario,
        "pontos_carreira": ranking["pontos_total"] if ranking else 0,
        "total_corridas": ranking["total_corridas"] if ranking else 0
    }

@api_router.patch("/atletas/perfil")
async def atualizar_perfil(dados: PerfilUpdate, current_user: dict = Depends(get_current_user)):
    """Atleta atualiza seu próprio perfil"""
    update_data = {}
    
    # Campos editáveis pelo atleta
    if dados.nome is not None:
        update_data["nome"] = dados.nome
    if dados.cidade is not None:
        update_data["cidade"] = dados.cidade
    if dados.estado is not None:
        update_data["estado"] = dados.estado
    if dados.data_nascimento is not None:
        update_data["data_nascimento"] = dados.data_nascimento
        # Recalcular faixa etária
        update_data["faixa_etaria"] = calcular_faixa_etaria(dados.data_nascimento)
    if dados.equipe is not None:
        update_data["equipe"] = dados.equipe
    if dados.facebook_url is not None:
        update_data["facebook_url"] = dados.facebook_url
    if dados.instagram_url is not None:
        update_data["instagram_url"] = dados.instagram_url
    if dados.telefone is not None:
        update_data["telefone"] = dados.telefone
    if dados.bio is not None:
        # Limitar bio a 150 caracteres
        update_data["bio"] = dados.bio[:150] if dados.bio else ""
    if dados.etnia is not None:
        update_data["etnia"] = dados.etnia
    if dados.apelido is not None:
        update_data["apelido"] = dados.apelido
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    await db.usuarios.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    return {"message": "Perfil atualizado com sucesso!"}

@api_router.get("/atletas/meu-ranking/export")
async def export_meu_ranking(current_user: dict = Depends(get_current_user)):
    """Exporta histórico de corridas do atleta logado"""
    usuario = await db.usuarios.find_one({"id": current_user["id"]}, {"_id": 0, "password_hash": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    corridas = await db.corridas.find(
        {"usuario_id": current_user["id"]},
        {"_id": 0}
    ).sort("data", -1).to_list(None)
    
    ranking = await db.ranking_anual.find_one({"usuario_id": current_user["id"], "ano": 2025}, {"_id": 0})
    
    # Criar Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Meu Ranking"
    
    # Info do atleta
    ws.append(["RANKING RUN PRÓ - HISTÓRICO DO ATLETA"])
    ws.append([])
    ws.append(["Nome:", usuario["nome"]])
    ws.append(["Equipe:", usuario.get("equipe", "")])
    ws.append(["Cidade:", f"{usuario['cidade']}/{usuario['estado']}"])
    ws.append(["Categoria:", usuario["categoria"].upper()])
    ws.append(["Pontos Totais:", ranking["pontos_total"] if ranking else 0])
    ws.append(["Total de Corridas:", ranking["total_corridas"] if ranking else 0])
    ws.append([])
    
    # Header das corridas
    headers = ["Data", "Competição", "Distância", "Colocação", "Tempo", "Pontos", "Local"]
    ws.append(headers)
    
    header_fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    for cell in ws[10]:
        cell.fill = header_fill
        cell.font = header_font
    
    # Dados das corridas
    for corrida in corridas:
        ws.append([
            corrida.get("data", ""),
            corrida.get("nome", ""),
            corrida.get("distancia", ""),
            f"{corrida.get('colocacao', '')}º",
            corrida.get("tempo", ""),
            corrida.get("pontos", 0),
            corrida.get("local", "")
        ])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=meu_ranking_{usuario['nome'].replace(' ', '_')}.xlsx"}
    )

@api_router.post("/atletas/foto")
async def upload_foto_perfil(
    foto: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload de foto de perfil"""
    foto_filename = f"perfil_{current_user['id']}_{uuid.uuid4()}.jpg"
    foto_path = Path("/app/uploads") / foto_filename
    foto_path.parent.mkdir(exist_ok=True)
    
    with foto_path.open("wb") as f:
        f.write(await foto.read())
    
    foto_url = f"/uploads/{foto_filename}"
    
    await db.usuarios.update_one(
        {"id": current_user["id"]},
        {"$set": {"foto_url": foto_url}}
    )
    
    return {"message": "Foto atualizada!", "foto_url": foto_url}


# ==================== ATLETA - MENSAGEM DE ANIVERSÁRIO ====================

@api_router.get("/atletas/mensagem-aniversario")
async def get_mensagem_aniversario(current_user: dict = Depends(get_current_user)):
    """Retorna mensagem de aniversário não visualizada do atleta"""
    ano_atual = datetime.now().year
    
    mensagem = await db.mensagens_aniversario.find_one(
        {"usuario_id": current_user["id"], "ano": ano_atual, "visualizada": False},
        {"_id": 0}
    )
    
    return {"mensagem": mensagem}


@api_router.post("/atletas/mensagem-aniversario/visualizar")
async def marcar_mensagem_visualizada(current_user: dict = Depends(get_current_user)):
    """Marca mensagem de aniversário como visualizada"""
    ano_atual = datetime.now().year
    
    await db.mensagens_aniversario.update_many(
        {"usuario_id": current_user["id"], "ano": ano_atual, "visualizada": False},
        {"$set": {"visualizada": True, "data_visualizacao": datetime.now().isoformat()}}
    )
    
    return {"message": "Mensagem marcada como visualizada"}


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
    
    # Verificar modalidade do usuário
    modalidade_usuario = current_user.get("modalidade_usuario", "profissional_amador")
    categoria = current_user.get("categoria", "normal")
    
    # VALIDAÇÃO PARA PROFISSIONAL/AMADOR
    if modalidade_usuario == "profissional_amador":
        # VALIDAR COLOCAÇÃO (APENAS POSIÇÕES QUE PONTUAM)
        if categoria in ["pcd", "cadeirante"]:
            if colocacao < 1 or colocacao > 3:
                raise HTTPException(
                    status_code=400,
                    detail=f"Para categoria {categoria.upper()}, apenas colocações de 1º a 3º são válidas e pontuam."
                )
        else:
            if colocacao < 1 or colocacao > 10:
                raise HTTPException(
                    status_code=400,
                    detail="Para categoria Normal, apenas colocações de 1º a 10º são válidas e pontuam."
                )
    # VALIDAÇÃO PARA POVÃO - não valida colocação, apenas participação
    # Colocação será 0 ou ignorada
    
    # Salvar foto (OPCIONAL)
    foto_url = ""
    if foto_podio and foto_podio.filename:
        foto_filename = f"{uuid.uuid4()}_{foto_podio.filename}"
        foto_path = Path("/app/uploads") / foto_filename
        foto_path.parent.mkdir(exist_ok=True)
        
        with foto_path.open("wb") as f:
            f.write(await foto_podio.read())
        
        foto_url = f"/uploads/{foto_filename}"
    
    # Criar resultado pendente com modalidade
    resultado = ResultadoPendente(
        usuario_id=current_user["id"],
        nome_competicao=nome_competicao,
        colocacao=colocacao if modalidade_usuario == "profissional_amador" else 0,
        cidade_competicao=cidade_competicao,
        estado_competicao=estado_competicao,
        data_competicao=data_competicao,
        link_resultado=link_resultado,
        tempo=tempo if modalidade_usuario == "profissional_amador" else "00:00:00",
        distancia=distancia,
        foto_podio_url=foto_url,
        status="pendente"
    )
    
    # Adicionar modalidade ao resultado pendente
    doc = resultado.model_dump()
    doc["modalidade"] = modalidade_usuario
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
    
    usuario = await db.usuarios.find_one({"id": resultado["usuario_id"]}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Verificar modalidade do usuário
    modalidade_usuario = usuario.get("modalidade_usuario", "profissional_amador")
    
    if modalidade_usuario == "povao_pace_livre":
        # PONTUAÇÃO POVÃO - baseada apenas na distância
        pontos = 0  # Pontos normais zerados
        pontos_povao = calcular_pontos_povao(resultado["distancia"])
        
        corrida = Corrida(
            usuario_id=resultado["usuario_id"],
            nome=resultado["nome_competicao"],
            colocacao=0,  # Não importa para Povão
            tempo="00:00:00",  # Não importa para Povão
            pontos=0,  # Não usa pontos tradicionais
            pontos_povao=pontos_povao,
            local=f"{resultado['cidade_competicao']}/{resultado['estado_competicao']}",
            distancia=resultado["distancia"],
            data=resultado["data_competicao"],
            ano=2025,
            modalidade="povao_pace_livre"
        )
        
        await db.corridas.insert_one(corrida.model_dump())
        
        await db.resultados_pendentes.update_one(
            {"id": resultado_id},
            {"$set": {"status": "aprovado"}}
        )
        
        # Recalcular ranking Povão
        await calcular_ranking_povao()
        
        # Notificar atleta
        await criar_notificacao(
            usuario_id=resultado["usuario_id"],
            tipo="aprovacao",
            titulo="Resultado aprovado!",
            mensagem=f"Seu resultado na {resultado['nome_competicao']} foi aprovado! Você ganhou {pontos_povao} pontos no Ranking do Povão.",
            dados_extras={"pontos": pontos_povao, "competicao": resultado["nome_competicao"], "modalidade": "povao"}
        )
        
        return {"message": "Resultado aprovado com sucesso!", "pontos_adicionados": pontos_povao, "modalidade": "povao_pace_livre"}
    
    else:
        # PONTUAÇÃO PROFISSIONAL/AMADOR - tradicional
        pontos = calcular_pontos_colocacao(resultado["colocacao"], usuario["categoria"])
        
        if pontos == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Colocação {resultado['colocacao']}º não pontua para categoria {usuario['categoria']}"
            )
        
        corrida = Corrida(
            usuario_id=resultado["usuario_id"],
            nome=resultado["nome_competicao"],
            colocacao=resultado["colocacao"],
            tempo=resultado["tempo"],
            pontos=pontos,
            pontos_povao=0,
            local=f"{resultado['cidade_competicao']}/{resultado['estado_competicao']}",
            distancia=resultado["distancia"],
            data=resultado["data_competicao"],
            ano=2025,
            modalidade="profissional_amador"
        )
        
        await db.corridas.insert_one(corrida.model_dump())
        
        await db.resultados_pendentes.update_one(
            {"id": resultado_id},
            {"$set": {"status": "aprovado"}}
        )
        
        await calcular_ranking()
        
        # Notificar atleta
        await criar_notificacao(
            usuario_id=resultado["usuario_id"],
            tipo="aprovacao",
            titulo="Resultado aprovado!",
            mensagem=f"Seu resultado na {resultado['nome_competicao']} foi aprovado! Você ganhou {pontos} pontos.",
            dados_extras={"pontos": pontos, "competicao": resultado["nome_competicao"]}
        )
        
        # Verificar conquistas
        await verificar_conquistas(resultado["usuario_id"])
        
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
    
    motivo = dados.motivo or "Não atende aos critérios do regulamento"
    
    await db.resultados_pendentes.update_one(
        {"id": resultado_id},
        {"$set": {
            "status": "reprovado",
            "motivo_reprovacao": motivo
        }}
    )
    
    # Notificar atleta sobre reprovação
    await criar_notificacao(
        usuario_id=resultado["usuario_id"],
        tipo="reprovacao",
        titulo="Resultado reprovado",
        mensagem=f"Seu resultado na {resultado['nome_competicao']} foi reprovado. Motivo: {motivo}",
        dados_extras={
            "competicao": resultado["nome_competicao"],
            "motivo": motivo,
            "resultado_id": resultado_id
        }
    )
    
    return {"message": "Resultado reprovado"}

@api_router.get("/admin/stats")
async def get_admin_stats(admin: dict = Depends(get_admin_user)):
    """Estatísticas gerais do dashboard admin"""
    total_atletas = await db.usuarios.count_documents({"role": "atleta"})
    resultados_pendentes = await db.resultados_pendentes.count_documents({"status": "pendente"})
    
    rankings = await db.ranking_anual.find({"ano": 2025}, {"_id": 0}).to_list(None)
    atletas_pendentes = 0
    for rank in rankings:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            min_corridas = 8 if usuario["categoria"] in ["pcd", "cadeirante"] else 12
            if rank["total_corridas"] < min_corridas:
                atletas_pendentes += 1
    
    total_homens = await db.usuarios.count_documents({"role": "atleta", "genero": "M"})
    total_mulheres = await db.usuarios.count_documents({"role": "atleta", "genero": "F"})
    total_corridas = await db.corridas.count_documents({})
    
    return {
        "total_atletas": total_atletas,
        "resultados_pendentes": resultados_pendentes,
        "atletas_pendentes_corridas": atletas_pendentes,
        "total_homens": total_homens,
        "total_mulheres": total_mulheres,
        "total_corridas": total_corridas
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

@api_router.get("/admin/stats/corridas-por-mes")
async def get_corridas_por_mes(admin: dict = Depends(get_admin_user)):
    """Corridas por mês"""
    pipeline = [
        {"$match": {"ano": 2025}},
        {"$group": {
            "_id": {"$substr": ["$data", 0, 7]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    result = await db.corridas.aggregate(pipeline).to_list(None)
    return [{"mes": r["_id"], "total": r["count"]} for r in result]


# ==================== ADMIN - GERENCIAMENTO DE ATLETAS ====================

@api_router.get("/admin/atletas")
async def get_all_atletas(
    categoria: Optional[str] = None,
    admin: dict = Depends(get_admin_user)
):
    """Lista todos atletas com filtros"""
    query = {"role": "atleta"}
    
    if categoria and categoria != 'all':
        if categoria == 'normal-m':
            query["categoria"] = "normal"
            query["genero"] = "M"
        elif categoria == 'normal-f':
            query["categoria"] = "normal"
            query["genero"] = "F"
        elif categoria == 'pcd':
            query["categoria"] = "pcd"
        elif categoria == 'cadeirante':
            query["categoria"] = "cadeirante"
    
    atletas = await db.usuarios.find(query, {"_id": 0, "password_hash": 0}).to_list(None)
    return atletas

@api_router.post("/admin/atletas")
async def admin_create_atleta(dados: dict, admin: dict = Depends(get_admin_user)):
    """Admin cadastra novo atleta"""
    existing = await db.usuarios.find_one({"email": dados.get("email")}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    faixa = calcular_faixa_etaria(dados.get("data_nascimento", "1990-01-01"))
    
    usuario = Usuario(
        nome=dados.get("nome", ""),
        email=dados.get("email", ""),
        password_hash=get_password_hash(dados.get("password", "atleta123")),
        equipe=dados.get("equipe", ""),
        cidade=dados.get("cidade", ""),
        estado=dados.get("estado", "SP"),
        genero=dados.get("genero", "M"),
        categoria=dados.get("categoria", "normal"),
        data_nascimento=dados.get("data_nascimento", "1990-01-01"),
        faixa_etaria=faixa,
        foto_url=gerar_foto_url(dados.get("nome", "")),
        role="atleta"
    )
    
    await db.usuarios.insert_one(usuario.model_dump())
    return {"message": "Atleta cadastrado com sucesso!", "id": usuario.id}

@api_router.put("/admin/atletas/{atleta_id}")
async def admin_update_atleta(atleta_id: str, dados: dict, admin: dict = Depends(get_admin_user)):
    """Admin atualiza dados do atleta"""
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    update_data = {}
    campos_permitidos = ["nome", "email", "equipe", "cidade", "estado", "genero", "categoria", "data_nascimento"]
    
    for campo in campos_permitidos:
        if campo in dados and dados[campo] is not None:
            update_data[campo] = dados[campo]
    
    if "data_nascimento" in update_data:
        update_data["faixa_etaria"] = calcular_faixa_etaria(update_data["data_nascimento"])
    
    if update_data:
        await db.usuarios.update_one({"id": atleta_id}, {"$set": update_data})
    
    return {"message": "Atleta atualizado com sucesso!"}

@api_router.delete("/admin/atletas/{atleta_id}")
async def admin_delete_atleta(atleta_id: str, admin: dict = Depends(get_admin_user)):
    """Admin exclui atleta"""
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Remover atleta e dados relacionados
    await db.usuarios.delete_one({"id": atleta_id})
    await db.corridas.delete_many({"usuario_id": atleta_id})
    await db.ranking_anual.delete_many({"usuario_id": atleta_id})
    await db.resultados_pendentes.delete_many({"usuario_id": atleta_id})
    await db.notificacoes.delete_many({"usuario_id": atleta_id})
    await db.conquistas_atleta.delete_many({"usuario_id": atleta_id})
    
    return {"message": "Atleta excluído com sucesso!"}


@api_router.post("/admin/atletas/{atleta_id}/transferir-modalidade")
async def admin_transferir_modalidade(atleta_id: str, admin: dict = Depends(get_admin_user)):
    """
    Transfere atleta entre modalidades (Profissional/Amador <-> Povão).
    
    - Profissional -> Povão: Perde pontos por colocação, recalcula por distância
    - Povão -> Profissional: Perde pontos por distância, recalcula por colocação
    """
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Verificar se é PCD ou Cadeirante (não podem ir para Povão)
    if atleta.get("categoria") in ["pcd", "cadeirante"]:
        modalidade_atual = atleta.get("modalidade_usuario", "profissional_amador")
        if modalidade_atual == "profissional_amador":
            raise HTTPException(
                status_code=400, 
                detail="Atletas PCD e Cadeirante não podem ser transferidos para o Ranking do Povão"
            )
    
    # Determinar nova modalidade
    modalidade_atual = atleta.get("modalidade_usuario", "profissional_amador")
    nova_modalidade = "povao_pace_livre" if modalidade_atual == "profissional_amador" else "profissional_amador"
    
    # Buscar todas as corridas do atleta
    corridas = await db.corridas.find({"usuario_id": atleta_id}, {"_id": 0}).to_list(None)
    
    # Estatísticas para retorno
    stats = {
        "corridas_processadas": len(corridas),
        "pontos_antigos": sum(c.get("pontos", 0) for c in corridas),
        "pontos_novos": 0,
        "modalidade_anterior": modalidade_atual,
        "modalidade_nova": nova_modalidade
    }
    
    # Recalcular pontos de cada corrida baseado na nova modalidade
    for corrida in corridas:
        if nova_modalidade == "povao_pace_livre":
            # Transferindo para Povão: calcular por distância
            distancia = corrida.get("distancia", "5KM")
            novos_pontos = calcular_pontos_povao(distancia)
        else:
            # Transferindo para Profissional: calcular por colocação
            colocacao = corrida.get("colocacao", 0)
            categoria = atleta.get("categoria", "normal")
            novos_pontos = calcular_pontos_colocacao(colocacao, categoria)
        
        stats["pontos_novos"] += novos_pontos
        
        # Atualizar pontos da corrida no banco
        await db.corridas.update_one(
            {"id": corrida["id"]},
            {"$set": {"pontos": novos_pontos}}
        )
    
    # Atualizar modalidade do atleta
    await db.usuarios.update_one(
        {"id": atleta_id},
        {"$set": {"modalidade_usuario": nova_modalidade}}
    )
    
    # Remover do ranking antigo
    await db.ranking_anual.delete_many({"usuario_id": atleta_id})
    
    # Recalcular rankings
    await calcular_ranking()
    await calcular_ranking_povao()
    
    # Criar notificação para o atleta
    notificacao = {
        "id": str(uuid.uuid4()),
        "usuario_id": atleta_id,
        "tipo": "transferencia_modalidade",
        "titulo": "Transferência de Modalidade",
        "mensagem": f"Você foi transferido para o {'Ranking do Povão - Pace Livre' if nova_modalidade == 'povao_pace_livre' else 'Ranking Profissional/Amador'}. Seus pontos foram recalculados.",
        "lida": False,
        "data": datetime.now(timezone.utc).isoformat()
    }
    await db.notificacoes.insert_one(notificacao)
    
    return {
        "message": f"Atleta transferido com sucesso para {'Ranking do Povão' if nova_modalidade == 'povao_pace_livre' else 'Ranking Profissional/Amador'}!",
        "stats": stats
    }

@api_router.get("/admin/atletas/export")
async def admin_export_atletas(categoria: str = "all", admin: dict = Depends(get_admin_user)):
    """Exporta lista de atletas em Excel"""
    query = {"role": "atleta"}
    
    if categoria and categoria != 'all':
        if categoria == 'normal-m':
            query["categoria"] = "normal"
            query["genero"] = "M"
        elif categoria == 'normal-f':
            query["categoria"] = "normal"
            query["genero"] = "F"
        elif categoria == 'pcd':
            query["categoria"] = "pcd"
        elif categoria == 'cadeirante':
            query["categoria"] = "cadeirante"
    
    atletas = await db.usuarios.find(query, {"_id": 0, "password_hash": 0}).to_list(None)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Atletas"
    
    headers = ["Nome", "Email", "Equipe", "Cidade", "UF", "Categoria", "Gênero", "Faixa Etária"]
    ws.append(headers)
    
    header_fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    
    for atleta in atletas:
        ws.append([
            atleta.get("nome", ""),
            atleta.get("email", ""),
            atleta.get("equipe", ""),
            atleta.get("cidade", ""),
            atleta.get("estado", ""),
            atleta.get("categoria", "").upper(),
            "Masculino" if atleta.get("genero") == "M" else "Feminino",
            atleta.get("faixa_etaria", "")
        ])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=atletas_{categoria}.xlsx"}
    )

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


@api_router.delete("/admin/pendentes/{resultado_id}/foto")
async def admin_delete_foto_podio(resultado_id: str, admin: dict = Depends(get_admin_user)):
    """Admin exclui a foto do pódio de um resultado pendente"""
    resultado = await db.resultados_pendentes.find_one({"id": resultado_id}, {"_id": 0})
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")
    
    foto_url = resultado.get("foto_podio_url", "")
    if foto_url:
        # Remover arquivo físico
        foto_path = Path("/app/uploads") / foto_url.replace("/uploads/", "")
        if foto_path.exists():
            foto_path.unlink()
        
        # Atualizar no banco
        await db.resultados_pendentes.update_one(
            {"id": resultado_id},
            {"$set": {"foto_podio_url": ""}}
        )
    
    return {"message": "Foto excluída com sucesso!"}


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
                "estado": usuario["estado"],
                "genero": usuario["genero"],
                "categoria": usuario["categoria"],
                "faixa_etaria": usuario["faixa_etaria"],
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


@api_router.get("/ranking/povao")
async def get_ranking_povao(genero: str = "M"):
    """Retorna o ranking do Povão - Pace Livre"""
    
    ranking_list = await db.ranking_povao.find(
        {"ano": 2025, "genero": genero},
        {"_id": 0}
    ).sort([("pontos_total", -1), ("total_corridas", -1), ("distancia_acumulada", -1)]).to_list(None)
    
    result = []
    for rank in ranking_list:
        usuario = await db.usuarios.find_one({"id": rank["usuario_id"]}, {"_id": 0})
        if usuario:
            result.append({
                "colocacao": rank["ranking_genero"],
                "atleta_id": rank["usuario_id"],
                "nome": usuario["nome"],
                "uf": usuario["estado"],
                "cidade": usuario["cidade"],
                "faixa_etaria": usuario["faixa_etaria"],
                "foto_url": usuario.get("foto_url", ""),
                "equipe": usuario.get("equipe", ""),
                "total_corridas": rank["total_corridas"],
                "distancia_acumulada": rank["distancia_acumulada"],
                "pontos": rank["pontos_total"]
            })
    
    return {
        "genero": "Masculino" if genero == "M" else "Feminino",
        "total_atletas": len(result),
        "ranking": result
    }


@api_router.get("/ranking/povao/stats")
async def get_povao_stats():
    """Retorna estatísticas do ranking do Povão"""
    
    total_atletas_m = await db.ranking_povao.count_documents({"ano": 2025, "genero": "M"})
    total_atletas_f = await db.ranking_povao.count_documents({"ano": 2025, "genero": "F"})
    
    # Total de provas e pontos
    pipeline = [
        {"$match": {"modalidade": "povao_pace_livre", "ano": 2025}},
        {"$group": {
            "_id": None,
            "total_provas": {"$sum": 1},
            "total_pontos": {"$sum": "$pontos_povao"},
            "total_distancia": {"$sum": {"$toDouble": {"$replaceAll": {"input": {"$toUpper": "$distancia"}, "find": "KM", "replacement": ""}}}}
        }}
    ]
    
    stats = await db.corridas.aggregate(pipeline).to_list(1)
    
    return {
        "total_atletas_masculino": total_atletas_m,
        "total_atletas_feminino": total_atletas_f,
        "total_atletas": total_atletas_m + total_atletas_f,
        "total_provas": stats[0]["total_provas"] if stats else 0,
        "total_pontos": stats[0]["total_pontos"] if stats else 0
    }


# ==================== RANKING SEMANAL E MENSAL ====================

@api_router.get("/ranking/semanal")
async def get_ranking_semanal(categoria: str = "masculino"):
    """Retorna o ranking semanal baseado em corridas da última semana (apenas Profissional/Amador)"""
    cat_map = {
        "masculino": ("normal", "M"),
        "feminino": ("normal", "F"),
        "pcd-m": ("pcd", "M"),
        "pcd-f": ("pcd", "F"),
        "cadeirante-m": ("cadeirante", "M"),
        "cadeirante-f": ("cadeirante", "F")
    }
    
    cat_db, gen_db = cat_map.get(categoria, ("normal", "M"))
    
    # Calcular data da semana atual (últimos 7 dias)
    hoje = datetime.now()
    inicio_semana = (hoje - timedelta(days=7)).strftime("%Y-%m-%d")
    fim_semana = hoje.strftime("%Y-%m-%d")
    
    # Buscar corridas da semana
    pipeline = [
        {"$match": {
            "data": {"$gte": inicio_semana, "$lte": fim_semana}
        }},
        {"$group": {
            "_id": "$usuario_id",
            "pontos_semana": {"$sum": "$pontos"},
            "corridas_semana": {"$sum": 1}
        }},
        {"$sort": {"pontos_semana": -1}}
    ]
    
    agregados = await db.corridas.aggregate(pipeline).to_list(None)
    
    ranking = []
    posicao = 1
    for agg in agregados:
        usuario = await db.usuarios.find_one({"id": agg["_id"]}, {"_id": 0})
        # Filtrar apenas atletas Profissional/Amador (não Povão)
        if usuario and usuario.get("categoria") == cat_db and usuario.get("genero") == gen_db:
            # Verificar modalidade - apenas profissional_amador ou não definido (default)
            modalidade = usuario.get("modalidade_usuario", "profissional_amador")
            if modalidade != "povao_pace_livre":
                ranking.append({
                    "posicao": posicao,
                    "atleta_id": agg["_id"],
                    "nome": usuario["nome"],
                    "equipe": usuario["equipe"],
                    "cidade": usuario["cidade"],
                    "estado": usuario["estado"],
                    "foto_url": usuario.get("foto_url", ""),
                    "pontos_semana": agg["pontos_semana"],
                    "corridas_semana": agg["corridas_semana"]
                })
                posicao += 1
                if posicao > 10:  # Top 10
                    break
    
    return {
        "periodo": f"{inicio_semana} a {fim_semana}",
        "categoria": categoria,
        "ranking": ranking
    }


@api_router.get("/ranking/mensal")
async def get_ranking_mensal(categoria: str = "masculino", mes: int = None, ano: int = None):
    """Retorna o ranking mensal baseado em corridas do mês (apenas Profissional/Amador)"""
    cat_map = {
        "masculino": ("normal", "M"),
        "feminino": ("normal", "F"),
        "pcd-m": ("pcd", "M"),
        "pcd-f": ("pcd", "F"),
        "cadeirante-m": ("cadeirante", "M"),
        "cadeirante-f": ("cadeirante", "F")
    }
    
    cat_db, gen_db = cat_map.get(categoria, ("normal", "M"))
    
    # Se não especificado, usar mês atual
    hoje = datetime.now()
    mes_atual = mes or hoje.month
    ano_atual = ano or hoje.year
    
    # Calcular início e fim do mês
    inicio_mes = f"{ano_atual}-{mes_atual:02d}-01"
    if mes_atual == 12:
        fim_mes = f"{ano_atual + 1}-01-01"
    else:
        fim_mes = f"{ano_atual}-{mes_atual + 1:02d}-01"
    
    # Buscar corridas do mês
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
    
    ranking = []
    posicao = 1
    for agg in agregados:
        usuario = await db.usuarios.find_one({"id": agg["_id"]}, {"_id": 0})
        # Filtrar apenas atletas Profissional/Amador (não Povão)
        if usuario and usuario.get("categoria") == cat_db and usuario.get("genero") == gen_db:
            # Verificar modalidade - apenas profissional_amador ou não definido (default)
            modalidade = usuario.get("modalidade_usuario", "profissional_amador")
            if modalidade != "povao_pace_livre":
                ranking.append({
                    "posicao": posicao,
                    "atleta_id": agg["_id"],
                    "nome": usuario["nome"],
                    "equipe": usuario["equipe"],
                    "cidade": usuario["cidade"],
                    "estado": usuario["estado"],
                    "foto_url": usuario.get("foto_url", ""),
                    "pontos_mes": agg["pontos_mes"],
                    "corridas_mes": agg["corridas_mes"]
                })
                posicao += 1
                if posicao > 10:  # Top 10
                    break
    
    meses_nome = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    return {
        "mes": meses_nome[mes_atual],
        "ano": ano_atual,
        "categoria": categoria,
        "ranking": ranking
    }


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
        melhor_colocacao = 0  # Não se aplica ao Povão
        total_corridas = ranking["total_corridas"] if ranking else 0
        pontos_carreira = ranking["pontos_total"] if ranking else 0
    else:
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
        is_pendente=(total_corridas < min_corridas),
        bio=usuario.get("bio", ""),
        apelido=usuario.get("apelido", ""),
        etnia=usuario.get("etnia", ""),
        instagram_url=usuario.get("instagram_url", ""),
        facebook_url=usuario.get("facebook_url", ""),
        modalidade_usuario=modalidade_usuario
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
        "url_compartilhar": f"https://admin-analytics-52.preview.emergentagent.com/atleta/{atleta_id}"
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
    """Lista equipes disponíveis"""
    pipeline = [
        {"$match": {"role": "atleta"}},
        {"$group": {"_id": "$equipe"}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return {"equipes": [e["_id"] for e in result if e["_id"]]}

@api_router.get("/")
async def root():
    return {"message": "Ranking Run Pro API"}

@api_router.post("/ranking/popular")
async def popular_dados_teste():
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

@api_router.get("/admin/aniversariantes")
async def get_aniversariantes_mes(mes: int = None, ano: int = None, admin: dict = Depends(get_admin_user)):
    """Retorna os aniversariantes do mês com calendário"""
    hoje = datetime.now()
    mes_atual = mes or hoje.month
    ano_atual = ano or hoje.year
    
    # Buscar todos os atletas
    atletas = await db.usuarios.find({"role": "atleta"}, {"_id": 0}).to_list(None)
    
    # Organizar por dia do mês
    calendario = {}
    for dia in range(1, 32):
        calendario[dia] = []
    
    for atleta in atletas:
        if atleta.get("data_nascimento"):
            try:
                data_nasc = datetime.strptime(atleta["data_nascimento"], "%Y-%m-%d")
                if data_nasc.month == mes_atual:
                    calendario[data_nasc.day].append({
                        "id": atleta["id"],
                        "nome": atleta["nome"],
                        "apelido": atleta.get("apelido", ""),
                        "foto_url": atleta.get("foto_url", ""),
                        "equipe": atleta.get("equipe", ""),
                        "idade": ano_atual - data_nasc.year
                    })
            except ValueError:
                pass
    
    meses_nome = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    return {
        "mes": meses_nome[mes_atual],
        "ano": ano_atual,
        "calendario": calendario,
        "total_aniversariantes": sum(len(v) for v in calendario.values())
    }


@api_router.get("/admin/aniversariantes/hoje")
async def get_aniversariantes_hoje(admin: dict = Depends(get_admin_user)):
    """Retorna os aniversariantes do dia"""
    hoje = datetime.now()
    
    atletas = await db.usuarios.find({"role": "atleta"}, {"_id": 0}).to_list(None)
    
    aniversariantes = []
    for atleta in atletas:
        if atleta.get("data_nascimento"):
            try:
                data_nasc = datetime.strptime(atleta["data_nascimento"], "%Y-%m-%d")
                if data_nasc.month == hoje.month and data_nasc.day == hoje.day:
                    aniversariantes.append({
                        "id": atleta["id"],
                        "nome": atleta["nome"],
                        "apelido": atleta.get("apelido", ""),
                        "foto_url": atleta.get("foto_url", ""),
                        "equipe": atleta.get("equipe", ""),
                        "email": atleta["email"],
                        "idade": hoje.year - data_nasc.year
                    })
            except ValueError:
                pass
    
    return {"aniversariantes": aniversariantes, "data": hoje.strftime("%Y-%m-%d")}


@api_router.post("/admin/aniversariantes/enviar-mensagem")
async def enviar_mensagem_aniversario(dados: dict, admin: dict = Depends(get_admin_user)):
    """Envia mensagem de aniversário para atleta(s)"""
    atleta_ids = dados.get("atleta_ids", [])
    mensagem = dados.get("mensagem", "Feliz Aniversário! Que este novo ciclo traga muitas conquistas nas pistas. 🎂🏃")
    
    mensagens_enviadas = 0
    for atleta_id in atleta_ids:
        atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
        if atleta:
            msg = MensagemAniversario(
                usuario_id=atleta_id,
                mensagem=mensagem,
                ano=datetime.now().year
            )
            await db.mensagens_aniversario.insert_one(msg.model_dump())
            mensagens_enviadas += 1
    
    return {"message": f"{mensagens_enviadas} mensagem(ns) enviada(s) com sucesso!"}


@api_router.get("/admin/aniversariantes/configuracao")
async def get_configuracao_aniversario(admin: dict = Depends(get_admin_user)):
    """Retorna configuração de mensagem de aniversário"""
    config = await db.configuracoes.find_one({"tipo": "mensagem_aniversario"}, {"_id": 0})
    if not config:
        config_doc = {
            "tipo": "mensagem_aniversario",
            "mensagem_padrao": "Feliz Aniversário! 🎂 Que este novo ciclo traga muitas conquistas nas pistas. O Ranking Run Pró deseja a você muita saúde e velocidade! 🏃‍♂️",
            "envio_automatico": False
        }
        await db.configuracoes.insert_one(config_doc)
        # Return without the _id field
        return {
            "tipo": config_doc["tipo"],
            "mensagem_padrao": config_doc["mensagem_padrao"],
            "envio_automatico": config_doc["envio_automatico"]
        }
    
    return config


@api_router.put("/admin/aniversariantes/configuracao")
async def update_configuracao_aniversario(dados: dict, admin: dict = Depends(get_admin_user)):
    """Atualiza configuração de mensagem de aniversário"""
    await db.configuracoes.update_one(
        {"tipo": "mensagem_aniversario"},
        {"$set": {
            "mensagem_padrao": dados.get("mensagem_padrao", ""),
            "envio_automatico": dados.get("envio_automatico", False)
        }},
        upsert=True
    )
    return {"message": "Configuração atualizada com sucesso!"}


@api_router.post("/admin/aniversariantes/enviar-agora")
async def enviar_aniversarios_agora(admin: dict = Depends(get_admin_user)):
    """Força o envio imediato de mensagens de aniversário para os aniversariantes de hoje"""
    hoje = datetime.now()
    
    # Buscar configuração
    config = await db.configuracoes.find_one({"tipo": "mensagem_aniversario"}, {"_id": 0})
    mensagem_padrao = config.get(
        "mensagem_padrao", 
        "Feliz Aniversário! 🎂 Que este novo ciclo traga muitas conquistas nas pistas. O Ranking Run Pró deseja a você muita saúde e velocidade! 🏃‍♂️"
    ) if config else "Feliz Aniversário! 🎂 O Ranking Run Pró deseja a você muita saúde e velocidade! 🏃‍♂️"
    
    # Buscar aniversariantes de hoje
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
        return {"message": "Nenhum aniversariante hoje!", "enviados": 0}
    
    mensagens_enviadas = 0
    ja_enviadas = 0
    
    for atleta in aniversariantes:
        # Verificar se já existe mensagem para este atleta neste ano
        existente = await db.mensagens_aniversario.find_one({
            "usuario_id": atleta["id"],
            "ano": hoje.year
        }, {"_id": 0})
        
        if existente:
            ja_enviadas += 1
            continue
        
        # Criar mensagem
        msg = MensagemAniversario(
            usuario_id=atleta["id"],
            mensagem=mensagem_padrao,
            ano=hoje.year
        )
        await db.mensagens_aniversario.insert_one(msg.model_dump())
        mensagens_enviadas += 1
    
    return {
        "message": "Processo concluído!",
        "aniversariantes_hoje": len(aniversariantes),
        "mensagens_enviadas": mensagens_enviadas,
        "ja_enviadas_anteriormente": ja_enviadas
    }


@api_router.get("/admin/aniversariantes/logs")
async def get_logs_aniversario(admin: dict = Depends(get_admin_user)):
    """Retorna os logs de execução do scheduler de aniversários"""
    logs = await db.logs_scheduler.find(
        {"tipo": "aniversario_automatico"},
        {"_id": 0}
    ).sort("data_execucao", -1).limit(10).to_list(10)
    
    return {"logs": logs}


# ========== RANKING RUN INSIDE - INSTAGRAM ANALYTICS ==========

# Chave API RapidAPI para Instagram Scraper
RAPIDAPI_KEY = os.environ.get('INSTAGRAM_API_KEY', 'a0ed9ffeb49a41be9047e1a72f50a75da8323b10777')


async def buscar_instagram_rapidapi(username: str) -> dict:
    """
    Busca dados do Instagram usando RapidAPI Instagram Scraper.
    """
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "instagram-scraper-api2.p.rapidapi.com"
    }
    
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    params = {"username_or_id_or_url": username}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    return {"success": True, "data": data['data']}
            
            # Tentar API alternativa
            url2 = "https://instagram-scraper.p.rapidapi.com/api/v1/profile"
            headers2 = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": "instagram-scraper.p.rapidapi.com"
            }
            params2 = {"username": username}
            
            response2 = await client.get(url2, headers=headers2, params=params2)
            if response2.status_code == 200:
                return {"success": True, "data": response2.json()}
            
            return {"success": False, "error": f"API retornou código {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


async def buscar_instagram_api_direta(username: str) -> dict:
    """
    Busca dados do Instagram usando a API privada do Instagram.
    Retorna dados completos do perfil e posts recentes.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-IG-App-ID': '936619743392459',
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': f'https://www.instagram.com/{username}/'
    }
    
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code == 404:
            return {"success": False, "error": "Perfil não encontrado"}
        
        if response.status_code == 429:
            return {"success": False, "error": "rate_limited"}
        
        if response.status_code != 200:
            return {"success": False, "error": f"Erro {response.status_code}"}
        
        data = response.json()
        user = data.get('data', {}).get('user', {})
        
        if not user:
            return {"success": False, "error": "Dados não disponíveis"}
        
        return {"success": True, "user": user}


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
                      'pace', 'trilha', 'ultra', 'meia maratona', '10k', '21k', '42k']
    
    # CTAs comuns
    ctas = ['link', 'clique', 'acesse', 'saiba mais', 'conheça', 'siga', 'inscreva', 
            'compre', 'whatsapp', 'contato', 'agenda', 'agende', 'participe', 'baixe']
    
    tem_descricao = len(bio) > 20
    tem_keywords = any(kw in bio_lower for kw in keywords_nicho)
    tem_cta = any(cta in bio_lower for cta in ctas)
    tem_link = 'http' in bio_lower or 'link' in bio_lower or '.com' in bio_lower or 'wa.me' in bio_lower
    
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


@api_router.get("/admin/instagram/analises")
async def listar_analises_instagram(admin: dict = Depends(get_admin_user)):
    """Lista todas as análises de Instagram já realizadas"""
    analyses = await db.instagram_analyses.find(
        {}, {"_id": 0}
    ).sort("data_analise", -1).to_list(100)
    
    return analyses


@api_router.get("/admin/instagram/analises/{analysis_id}")
async def obter_analise_instagram(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Obtém uma análise específica por ID"""
    analysis = await db.instagram_analyses.find_one(
        {"id": analysis_id}, {"_id": 0}
    )
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    media_nicho = MEDIAS_NICHO.get(analysis.get('nicho', 'corrida'), MEDIAS_NICHO['corrida'])
    
    graficos_data = {
        "radar": {
            "labels": ["Bio", "Frequência", "Engajamento", "Crescimento", 
                      "Consistência", "Padrões", "Reels", "Formatos"],
            "values": [
                analysis['nota_bio'], analysis['nota_frequencia'], 
                analysis['nota_engajamento'], analysis['nota_crescimento'],
                analysis['nota_consistencia'], analysis['nota_padroes'], 
                analysis['nota_reels'], analysis['nota_formatos']
            ],
            "max": 10
        },
        "gauge": {
            "value": analysis['score_final'],
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
            "perfil": [analysis['engagement_rate'], analysis.get('comparativo_crescimento', 0), 4],
            "media_nicho": [media_nicho['engagement_rate'], media_nicho['crescimento_medio'], media_nicho['posts_semana']]
        },
        "formatos": {
            "labels": ["Reels", "Carrossel", "Fotos"],
            "values": [50, 30, 20]  # Valores padrão se não armazenados
        },
        "metricas": {
            "seguidores": analysis.get('seguidores', 0),
            "seguindo": analysis.get('seguindo', 0),
            "posts": analysis.get('total_posts', 0),
            "er_post": analysis.get('engagement_rate', 0),
            "er_reels": analysis.get('engagement_rate_reels', 0),
            "crescimento": analysis.get('comparativo_crescimento', 0),
            "indice_anomalia": analysis.get('indice_anomalia', 0) * 100
        }
    }
    
    # Gerar recomendações baseadas nas notas
    notas = {
        'bio': analysis['nota_bio'],
        'frequencia': analysis['nota_frequencia'],
        'engajamento': analysis['nota_engajamento'],
        'crescimento': analysis['nota_crescimento'],
        'consistencia': analysis['nota_consistencia'],
        'padroes': analysis['nota_padroes'],
        'reels': analysis['nota_reels'],
        'formatos': analysis['nota_formatos']
    }
    recomendacoes = gerar_recomendacoes(notas, {'crescimento_30_dias': analysis.get('comparativo_crescimento', 0)})
    
    return {
        "analysis": analysis,
        "graficos_data": graficos_data,
        "recomendacoes": recomendacoes
    }


@api_router.delete("/admin/instagram/analises/{analysis_id}")
async def deletar_analise_instagram(analysis_id: str, admin: dict = Depends(get_admin_user)):
    """Deleta uma análise por ID"""
    result = await db.instagram_analyses.delete_one({"id": analysis_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    return {"message": "Análise excluída com sucesso"}


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



@app.on_event("startup")
async def startup_event():
    """Inicia o scheduler de aniversários"""
    logger.info("🚀 Iniciando scheduler de aniversários...")
    
    # Agendar tarefa para rodar às 00:00 todos os dias
    scheduler.add_job(
        enviar_mensagens_aniversario_automatico,
        CronTrigger(hour=0, minute=0),  # 00:00
        id="envio_aniversario_diario",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler de aniversários iniciado! Próxima execução às 00:00")


@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    client.close()
