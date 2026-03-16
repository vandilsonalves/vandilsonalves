# /app/backend/routes/admin_routes.py
# Módulo de Admin - Aprovações, estatísticas, gestão de atletas

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
import io
import uuid
from pathlib import Path

from config import db
from routes.auth_routes import get_current_user, get_admin_user
from routes.notificacoes_routes import criar_notificacao
from routes.conquistas_routes import verificar_conquistas
from services.cache_service import invalidate_on_ranking_change

router = APIRouter(tags=["Admin"])


# ==================== HELPERS ====================

def calcular_pontos_colocacao(colocacao: int, categoria: str) -> int:
    """Calcula pontos baseado na colocação e categoria"""
    if categoria in ["pcd", "cadeirante"]:
        pontos_tabela = {1: 100, 2: 90, 3: 80}
    else:
        pontos_tabela = {
            1: 100, 2: 90, 3: 80, 4: 70, 5: 60,
            6: 50, 7: 40, 8: 30, 9: 20, 10: 10
        }
    return pontos_tabela.get(colocacao, 0)


def calcular_pontos_povao(distancia: str) -> int:
    """Calcula pontos para o Ranking do Povão baseado na distância"""
    pontos_por_distancia = {
        "5KM": 5,
        "10KM": 10,
        "15KM": 15,
        "21KM": 21,
        "42KM": 42
    }
    return pontos_por_distancia.get(distancia.upper(), 5)


# ==================== PENDENTES E APROVAÇÕES ====================

@router.get("/admin/pendentes")
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
            resultado["atleta_email"] = usuario.get("email", "")
            resultado["atleta_equipe"] = usuario.get("equipe", "")
            resultado["atleta_categoria"] = usuario.get("categoria", "normal")
            resultado["modalidade_usuario"] = usuario.get("modalidade_usuario", "profissional_amador")
    
    return resultados


@router.post("/admin/aprovar/{resultado_id}")
async def aprovar_resultado(resultado_id: str, admin: dict = Depends(get_admin_user)):
    """Aprova resultado e adiciona à corrida oficial"""
    from models import Corrida
    
    resultado = await db.resultados_pendentes.find_one({"id": resultado_id}, {"_id": 0})
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")
    
    if resultado["status"] != "pendente":
        raise HTTPException(status_code=400, detail="Resultado já processado")
    
    usuario = await db.usuarios.find_one({"id": resultado["usuario_id"]}, {"_id": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    modalidade_usuario = usuario.get("modalidade_usuario", "profissional_amador")
    
    if modalidade_usuario == "povao_pace_livre":
        pontos_povao = calcular_pontos_povao(resultado["distancia"])
        
        corrida = Corrida(
            usuario_id=resultado["usuario_id"],
            nome=resultado["nome_competicao"],
            colocacao=0,
            tempo="00:00:00",
            pontos=0,
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
        
        # Invalidar cache de rankings
        await invalidate_on_ranking_change()
        
        await criar_notificacao(
            usuario_id=resultado["usuario_id"],
            tipo="aprovacao",
            titulo="Resultado aprovado!",
            mensagem=f"Seu resultado na {resultado['nome_competicao']} foi aprovado! Você ganhou {pontos_povao} pontos no Ranking do Povão.",
            dados_extras={"pontos": pontos_povao, "competicao": resultado["nome_competicao"], "modalidade": "povao"}
        )
        
        return {"message": "Resultado aprovado com sucesso!", "pontos_adicionados": pontos_povao, "modalidade": "povao_pace_livre"}
    
    else:
        pontos = calcular_pontos_colocacao(resultado["colocacao"], usuario.get("categoria", "normal"))
        
        if pontos == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Colocação {resultado['colocacao']}º não pontua para categoria {usuario.get('categoria', 'normal')}"
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
        
        # Invalidar cache de rankings
        await invalidate_on_ranking_change()
        
        await criar_notificacao(
            usuario_id=resultado["usuario_id"],
            tipo="aprovacao",
            titulo="Resultado aprovado!",
            mensagem=f"Seu resultado na {resultado['nome_competicao']} foi aprovado! Você ganhou {pontos} pontos.",
            dados_extras={"pontos": pontos, "competicao": resultado["nome_competicao"]}
        )
        
        await verificar_conquistas(resultado["usuario_id"])
        
        return {"message": "Resultado aprovado com sucesso!", "pontos_adicionados": pontos}


@router.post("/admin/reprovar/{resultado_id}")
async def reprovar_resultado(
    resultado_id: str,
    dados: dict,
    admin: dict = Depends(get_admin_user)
):
    """Reprova resultado"""
    resultado = await db.resultados_pendentes.find_one({"id": resultado_id}, {"_id": 0})
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")
    
    if resultado["status"] != "pendente":
        raise HTTPException(status_code=400, detail="Resultado já processado")
    
    motivo = dados.get("motivo") or "Não atende aos critérios do regulamento"
    
    await db.resultados_pendentes.update_one(
        {"id": resultado_id},
        {"$set": {
            "status": "reprovado",
            "motivo_reprovacao": motivo
        }}
    )
    
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


@router.delete("/admin/pendentes/{resultado_id}/foto")
async def remover_foto_resultado(resultado_id: str, admin: dict = Depends(get_admin_user)):
    """Remove foto de um resultado pendente"""
    resultado = await db.resultados_pendentes.find_one({"id": resultado_id})
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")
    
    foto_url = resultado.get("foto_podio_url")
    if foto_url:
        foto_path = Path(f"/app{foto_url}")
        if foto_path.exists():
            foto_path.unlink()
    
    await db.resultados_pendentes.update_one(
        {"id": resultado_id},
        {"$set": {"foto_podio_url": ""}}
    )
    
    return {"message": "Foto removida com sucesso"}


# ==================== ESTATÍSTICAS ====================

@router.get("/admin/stats")
async def get_admin_stats(admin: dict = Depends(get_admin_user)):
    """Estatísticas gerais do dashboard admin"""
    total_atletas = await db.usuarios.count_documents({"role": "atleta"})
    resultados_pendentes = await db.resultados_pendentes.count_documents({"status": "pendente"})
    total_corridas = await db.corridas.count_documents({})
    total_assessorias = await db.assessorias.count_documents({})
    
    atletas_masc = await db.usuarios.count_documents({"role": "atleta", "genero": "M"})
    atletas_fem = await db.usuarios.count_documents({"role": "atleta", "genero": "F"})
    
    return {
        "total_atletas": total_atletas,
        "resultados_pendentes": resultados_pendentes,
        "total_corridas": total_corridas,
        "total_assessorias": total_assessorias,
        "atletas_masculino": atletas_masc,
        "atletas_feminino": atletas_fem
    }


@router.get("/admin/stats/estados")
async def get_stats_estados(admin: dict = Depends(get_admin_user)):
    """Estatísticas por estado"""
    pipeline = [
        {"$match": {"role": "atleta"}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [{"estado": r["_id"], "atletas": r["count"]} for r in result if r["_id"]]


@router.get("/admin/stats/categorias")
async def get_stats_categorias(admin: dict = Depends(get_admin_user)):
    """Estatísticas por categoria"""
    pipeline = [
        {"$match": {"role": "atleta"}},
        {"$group": {
            "_id": {"categoria": "$categoria", "genero": "$genero"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    
    stats = []
    for r in result:
        if r["_id"]["categoria"]:
            stats.append({
                "categoria": r["_id"]["categoria"],
                "genero": r["_id"]["genero"],
                "atletas": r["count"]
            })
    return stats


@router.get("/admin/stats/faixa-etaria")
async def get_stats_faixa_etaria(admin: dict = Depends(get_admin_user)):
    """Estatísticas por faixa etária"""
    pipeline = [
        {"$match": {"role": "atleta"}},
        {"$group": {"_id": "$faixa_etaria", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [{"faixa_etaria": r["_id"], "atletas": r["count"]} for r in result if r["_id"]]


@router.get("/admin/stats/corridas-por-mes")
async def get_stats_corridas_mes(admin: dict = Depends(get_admin_user)):
    """Estatísticas de corridas por mês"""
    pipeline = [
        {"$addFields": {"mes": {"$substr": ["$data", 0, 7]}}},
        {"$group": {"_id": "$mes", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.corridas.aggregate(pipeline).to_list(None)
    return [{"mes": r["_id"], "corridas": r["count"]} for r in result if r["_id"]]


@router.get("/admin/stats/etnia")
async def get_stats_etnia(admin: dict = Depends(get_admin_user)):
    """Estatísticas por etnia"""
    pipeline = [
        {"$match": {"role": "atleta", "etnia": {"$exists": True, "$ne": ""}}},
        {"$group": {"_id": "$etnia", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    
    etnias_map = {
        "branco": "Branco",
        "pardo": "Pardo", 
        "preto": "Preto",
        "amarelo": "Amarelo",
        "indigena": "Indígena",
        "prefiro_nao_informar": "Prefiro não informar"
    }
    
    return [
        {"etnia": etnias_map.get(r["_id"], r["_id"]), "atletas": r["count"]}
        for r in result if r["_id"]
    ]


@router.get("/admin/stats/equipes-por-estado")
async def get_stats_equipes_estado(admin: dict = Depends(get_admin_user)):
    """Estatísticas de equipes/assessorias por estado"""
    pipeline = [
        {"$match": {"role": "atleta", "equipe": {"$exists": True, "$ne": ""}}},
        {"$group": {
            "_id": {"estado": "$estado", "equipe": "$equipe"},
            "atletas": {"$sum": 1}
        }},
        {"$group": {
            "_id": "$_id.estado",
            "equipes": {"$push": {"nome": "$_id.equipe", "atletas": "$atletas"}},
            "total_equipes": {"$sum": 1}
        }},
        {"$sort": {"total_equipes": -1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [
        {"estado": r["_id"], "total_equipes": r["total_equipes"], "equipes": r["equipes"][:5]}
        for r in result if r["_id"]
    ]


# ==================== GESTÃO DE ATLETAS ====================

@router.get("/admin/atletas")
async def listar_atletas(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = None,
    estado: str = None,
    categoria: str = None,
    admin: dict = Depends(get_admin_user)
):
    """Lista atletas com paginação e filtros"""
    filtro = {"role": "atleta"}
    
    if search:
        filtro["$or"] = [
            {"nome": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"equipe": {"$regex": search, "$options": "i"}}
        ]
    if estado:
        filtro["estado"] = estado
    if categoria:
        filtro["categoria"] = categoria
    
    skip = (page - 1) * limit
    
    atletas = await db.usuarios.find(
        filtro,
        {"_id": 0, "password_hash": 0}
    ).skip(skip).limit(limit).to_list(None)
    
    total = await db.usuarios.count_documents(filtro)
    
    return {
        "atletas": atletas,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }


@router.post("/admin/atletas")
async def criar_atleta(dados: dict, admin: dict = Depends(get_admin_user)):
    """Cria novo atleta (admin)"""
    from models import Usuario
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    existing = await db.usuarios.find_one({"email": dados.get("email")})
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    usuario = Usuario(
        nome=dados.get("nome"),
        email=dados.get("email"),
        password_hash=pwd_context.hash(dados.get("password", "senha123")),
        equipe=dados.get("equipe", ""),
        cidade=dados.get("cidade", ""),
        estado=dados.get("estado", ""),
        genero=dados.get("genero", "M"),
        categoria=dados.get("categoria", "normal"),
        data_nascimento=dados.get("data_nascimento", "1990-01-01"),
        faixa_etaria=dados.get("faixa_etaria", "30-39"),
        role="atleta"
    )
    
    await db.usuarios.insert_one(usuario.model_dump())
    
    return {"message": "Atleta criado com sucesso!", "id": usuario.id}


@router.put("/admin/atletas/{atleta_id}")
async def atualizar_atleta(atleta_id: str, dados: dict, admin: dict = Depends(get_admin_user)):
    """Atualiza dados do atleta"""
    atleta = await db.usuarios.find_one({"id": atleta_id})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    campos_permitidos = ["nome", "email", "equipe", "cidade", "estado", "genero", 
                         "categoria", "data_nascimento", "faixa_etaria", "is_active",
                         "modalidade_usuario", "etnia", "apelido"]
    
    update_data = {k: v for k, v in dados.items() if k in campos_permitidos}
    
    if update_data:
        await db.usuarios.update_one({"id": atleta_id}, {"$set": update_data})
    
    return {"message": "Atleta atualizado com sucesso!"}


@router.delete("/admin/atletas/{atleta_id}")
async def deletar_atleta(atleta_id: str, admin: dict = Depends(get_admin_user)):
    """Desativa atleta (soft delete)"""
    atleta = await db.usuarios.find_one({"id": atleta_id})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    await db.usuarios.update_one(
        {"id": atleta_id},
        {"$set": {"is_active": False}}
    )
    
    return {"message": "Atleta desativado com sucesso!"}


@router.get("/admin/atletas/export")
async def exportar_atletas(admin: dict = Depends(get_admin_user)):
    """Exporta lista de atletas em Excel"""
    atletas = await db.usuarios.find(
        {"role": "atleta"},
        {"_id": 0, "password_hash": 0}
    ).to_list(None)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Atletas"
    
    headers = ["Nome", "Email", "Equipe", "Cidade", "Estado", "Gênero", 
               "Categoria", "Faixa Etária", "Modalidade", "Status"]
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
            atleta.get("genero", ""),
            atleta.get("categoria", ""),
            atleta.get("faixa_etaria", ""),
            atleta.get("modalidade_usuario", "profissional_amador"),
            "Ativo" if atleta.get("is_active", True) else "Inativo"
        ])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=atletas_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )


# ==================== TRANSFERÊNCIA DE MODALIDADE ====================

@router.post("/admin/atletas/{atleta_id}/transferir-modalidade")
async def transferir_modalidade(
    atleta_id: str,
    dados: dict,
    admin: dict = Depends(get_admin_user)
):
    """Transfere atleta entre modalidades (Profissional/Amador <-> Povão)"""
    atleta = await db.usuarios.find_one({"id": atleta_id})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    nova_modalidade = dados.get("nova_modalidade")
    manter_historico = dados.get("manter_historico", True)
    
    if nova_modalidade not in ["profissional_amador", "povao_pace_livre"]:
        raise HTTPException(status_code=400, detail="Modalidade inválida")
    
    modalidade_atual = atleta.get("modalidade_usuario", "profissional_amador")
    
    if modalidade_atual == nova_modalidade:
        raise HTTPException(status_code=400, detail="Atleta já está nesta modalidade")
    
    if atleta.get("categoria") in ["pcd", "cadeirante"] and nova_modalidade == "povao_pace_livre":
        raise HTTPException(
            status_code=400,
            detail="Atletas PCD e Cadeirantes não podem participar do Ranking do Povão"
        )
    
    # Atualizar modalidade
    await db.usuarios.update_one(
        {"id": atleta_id},
        {"$set": {
            "modalidade_usuario": nova_modalidade,
            "data_transferencia_modalidade": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if not manter_historico:
        # Zerar pontuação na modalidade anterior
        if modalidade_atual == "profissional_amador":
            await db.ranking_anual.update_one(
                {"usuario_id": atleta_id, "ano": 2025},
                {"$set": {"pontos_total": 0, "total_corridas": 0}}
            )
        else:
            await db.ranking_povao.update_one(
                {"usuario_id": atleta_id},
                {"$set": {"pontos_total": 0, "total_participacoes": 0}}
            )
    
    # Invalidar cache
    await invalidate_on_ranking_change()
    
    await criar_notificacao(
        usuario_id=atleta_id,
        tipo="sistema",
        titulo="Modalidade Alterada",
        mensagem=f"Sua modalidade foi alterada para {'Ranking do Povão - Pace Livre' if nova_modalidade == 'povao_pace_livre' else 'Profissional/Amador'}.",
        dados_extras={"nova_modalidade": nova_modalidade}
    )
    
    return {
        "message": f"Atleta transferido para {nova_modalidade}",
        "atleta_id": atleta_id,
        "modalidade_anterior": modalidade_atual,
        "nova_modalidade": nova_modalidade
    }
