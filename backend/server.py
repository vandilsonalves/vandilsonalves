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
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# Import models and services
from models import (
    Usuario, UsuarioRegister, UsuarioLogin, PerfilUpdate,
    ResultadoPendente, ResultadoSubmissao, AprovacaoRequest,
    Corrida, RankingAnual, RankingResponse, AtletaDetalhes,
    CorridaResponse, EvolucaoMensal, Notificacao, Conquista, ConquistaAtleta,
    MensagemAniversario
)
from services import (
    verify_password, get_password_hash, create_access_token,
    calcular_faixa_etaria, gerar_foto_url, calcular_pontos_colocacao,
    get_min_corridas_categoria, SECRET_KEY, ALGORITHM, CONQUISTAS
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
        apelido=dados.apelido
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
        "foto_url": current_user["foto_url"]
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
        update_data["bio"] = dados.bio
    
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
    
    # VALIDAR COLOCAÇÃO (APENAS POSIÇÕES QUE PONTUAM)
    categoria = current_user.get("categoria", "normal")
    
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
        local=f"{resultado['cidade_competicao']}/{resultado['estado_competicao']}",
        distancia=resultado["distancia"],
        data=resultado["data_competicao"],
        ano=2025
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


# ==================== RANKING SEMANAL E MENSAL ====================

@api_router.get("/ranking/semanal")
async def get_ranking_semanal(categoria: str = "masculino"):
    """Retorna o ranking semanal baseado em corridas da última semana"""
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
        if usuario and usuario.get("categoria") == cat_db and usuario.get("genero") == gen_db:
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
    """Retorna o ranking mensal baseado em corridas do mês"""
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
        if usuario and usuario.get("categoria") == cat_db and usuario.get("genero") == gen_db:
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
        "url_compartilhar": f"https://runner-scores.preview.emergentagent.com/atleta/{atleta_id}"
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
