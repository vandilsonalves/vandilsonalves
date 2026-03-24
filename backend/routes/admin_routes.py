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
from services.email_service import notificar_resultado_aprovado, notificar_resultado_rejeitado

router = APIRouter(tags=["Admin"])


# ==================== HELPERS ====================

def calcular_pontos_colocacao(colocacao: int, categoria: str) -> int:
    """
    Calcula pontos baseado na colocação e categoria
    
    RANKING PROFISSIONAL/AMADOR:
    - Normal: 1º lugar = 10pts, 2º = 9pts, ... até 10º = 1pt
    - PCD/Cadeirante: 1º = 10pts, 2º = 9pts, 3º = 8pts
    """
    if categoria in ["pcd", "cadeirante"]:
        # PCD/Cadeirante: apenas 1º a 3º lugar pontuam
        pontos_tabela = {1: 10, 2: 9, 3: 8}
    else:
        # Normal: 1º a 10º lugar pontuam
        pontos_tabela = {
            1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
            6: 5, 7: 4, 8: 3, 9: 2, 10: 1
        }
    return pontos_tabela.get(colocacao, 0)


def calcular_pontos_povao(distancia: str) -> int:
    """Calcula pontos para o Ranking da Galera baseado na distância
    
    Regra de Pontuação (Sistema da Galera):
    - 5km a 9km = 5 pontos
    - 10km a 20km = 7 pontos
    - 21km ou mais = 9 pontos
    
    A pontuação NÃO depende da colocação, apenas da distância percorrida.
    """
    # Tentar extrair valor numérico
    try:
        # Remove "KM" e espaços
        distancia_upper = distancia.upper().strip()
        valor_str = distancia_upper.replace("KM", "").replace("K", "").strip()
        valor_km = float(valor_str)
        
        # Aplicar regras de pontuação do Povão
        if valor_km < 5:
            return 0  # Menos de 5km não pontua
        elif valor_km < 10:
            return 5  # 5km a 9km = 5 pontos
        elif valor_km < 21:
            return 7  # 10km a 20km = 7 pontos
        else:
            return 9  # 21km ou mais = 9 pontos
            
    except (ValueError, AttributeError):
        # Se não conseguir processar, retorna 5 (padrão mínimo)
        return 5


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
    nome_competicao = resultado.get("nome_competicao") or resultado.get("competicao") or "competição"
    cidade_competicao = resultado.get("cidade_competicao") or resultado.get("cidade") or ""
    estado_competicao = resultado.get("estado_competicao") or resultado.get("estado") or ""
    data_competicao = resultado.get("data_competicao") or resultado.get("data") or ""
    
    if modalidade_usuario == "povao_pace_livre":
        pontos_povao = calcular_pontos_povao(resultado.get("distancia", "0"))
        tempo_resultado = resultado.get("tempo", "00:00:00")
        
        corrida = Corrida(
            usuario_id=resultado["usuario_id"],
            nome=nome_competicao,
            colocacao=resultado.get("colocacao", 0),  # Pode ter colocação, mas não pontua por ela
            tempo=tempo_resultado,  # Salvar o tempo real
            pontos=pontos_povao,  # Usar pontos_povao como pontos para somar no total
            pontos_povao=pontos_povao,
            local=f"{cidade_competicao}/{estado_competicao}",
            distancia=resultado.get("distancia", "0"),
            data=data_competicao,
            ano=2025,
            modalidade="povao_pace_livre"
        )
        
        await db.corridas.insert_one(corrida.model_dump())
        
        # Atualizar pontos_total e total_corridas do usuário
        await db.usuarios.update_one(
            {"id": resultado["usuario_id"]},
            {
                "$inc": {"pontos_total": pontos_povao, "total_corridas": 1}
            }
        )
        
        # Atualizar ranking da Galera
        await db.ranking_povao.update_one(
            {"usuario_id": resultado["usuario_id"], "ano": 2025},
            {
                "$inc": {"pontos_total": pontos_povao, "total_corridas": 1},
                "$setOnInsert": {
                    "usuario_id": resultado["usuario_id"],
                    "ano": 2025,
                    "categoria": usuario.get("categoria", "normal"),
                    "genero": usuario.get("genero", "M")
                }
            },
            upsert=True
        )
        
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
            mensagem=f"Seu resultado na {nome_competicao} foi aprovado! Você ganhou {pontos_povao} pontos no Ranking da Galera.",
            dados_extras={"pontos": pontos_povao, "competicao": nome_competicao, "modalidade": "povao"}
        )
        
        # Post automático DESABILITADO - atletas devem compartilhar manualmente
        # try:
        #     from routes.feed_routes import criar_post_corrida_aprovada
        #     await criar_post_corrida_aprovada(...)
        # except Exception as e:
        #     print(f"Erro ao criar post automático no feed (Povão): {e}")
        
        # Enviar email de notificação (Povão)
        try:
            await notificar_resultado_aprovado(
                email=usuario.get("email", ""),
                atleta_nome=usuario.get("nome", "Atleta"),
                nome_corrida=nome_competicao,
                colocacao=0,  # Povão não tem colocação
                pontos=pontos_povao,
                data_corrida=data_competicao,
                distancia=resultado.get("distancia", "N/A")
            )
        except Exception as e:
            print(f"Erro ao enviar email de aprovação Povão: {e}")
        
        return {"message": "Resultado aprovado com sucesso!", "pontos_adicionados": pontos_povao, "modalidade": "povao_pace_livre"}
    
    else:
        pontos = calcular_pontos_colocacao(resultado.get("colocacao", 0), usuario.get("categoria", "normal"))
        
        if pontos == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Colocação {resultado.get('colocacao', 0)}º não pontua para categoria {usuario.get('categoria', 'normal')}"
            )
        
        corrida = Corrida(
            usuario_id=resultado["usuario_id"],
            nome=nome_competicao,
            colocacao=resultado.get("colocacao", 0),
            tempo=resultado.get("tempo", "00:00:00"),
            pontos=pontos,
            pontos_povao=0,
            local=f"{cidade_competicao}/{estado_competicao}",
            distancia=resultado.get("distancia", 0),
            data=data_competicao,
            ano=2025,
            modalidade="profissional_amador"
        )
        
        await db.corridas.insert_one(corrida.model_dump())
        
        # Atualizar pontos_total e total_corridas do usuário
        await db.usuarios.update_one(
            {"id": resultado["usuario_id"]},
            {
                "$inc": {"pontos_total": pontos, "total_corridas": 1}
            }
        )
        
        # Atualizar ranking anual
        await db.ranking_anual.update_one(
            {"usuario_id": resultado["usuario_id"], "ano": 2025},
            {
                "$inc": {"pontos_total": pontos, "total_corridas": 1},
                "$setOnInsert": {
                    "usuario_id": resultado["usuario_id"],
                    "ano": 2025,
                    "categoria": usuario.get("categoria", "normal"),
                    "genero": usuario.get("genero", "M")
                }
            },
            upsert=True
        )
        
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
            mensagem=f"Seu resultado na {nome_competicao} foi aprovado! Você ganhou {pontos} pontos.",
            dados_extras={"pontos": pontos, "competicao": nome_competicao}
        )
        
        await verificar_conquistas(resultado["usuario_id"])
        
        # Post automático DESABILITADO - atletas devem compartilhar manualmente
        # try:
        #     from routes.feed_routes import criar_post_corrida_aprovada
        #     await criar_post_corrida_aprovada(...)
        # except Exception as e:
        #     print(f"Erro ao criar post automático no feed: {e}")
        
        # Enviar email de notificação
        try:
            await notificar_resultado_aprovado(
                email=usuario.get("email", ""),
                atleta_nome=usuario.get("nome", "Atleta"),
                nome_corrida=nome_competicao,
                colocacao=resultado.get("colocacao", 0),
                pontos=pontos,
                data_corrida=data_competicao,
                distancia=resultado.get("distancia", "N/A")
            )
        except Exception as e:
            print(f"Erro ao enviar email de aprovação: {e}")
        
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
    nome_competicao = resultado.get("nome_competicao") or resultado.get("competicao") or "competição"
    
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
        mensagem=f"Seu resultado na {nome_competicao} foi reprovado. Motivo: {motivo}",
        dados_extras={
            "competicao": nome_competicao,
            "motivo": motivo,
            "resultado_id": resultado_id
        }
    )
    
    # Enviar email de notificação de rejeição
    try:
        usuario = await db.usuarios.find_one({"id": resultado["usuario_id"]}, {"_id": 0, "email": 1, "nome": 1})
        if usuario and usuario.get("email"):
            await notificar_resultado_rejeitado(
                email=usuario.get("email", ""),
                atleta_nome=usuario.get("nome", "Atleta"),
                nome_corrida=nome_competicao,
                motivo=motivo,
                data_corrida=resultado.get("data_competicao", "N/A")
            )
    except Exception as e:
        print(f"Erro ao enviar email de rejeição: {e}")
    
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


@router.get("/admin/stats/donos-por-estado")
async def get_stats_donos_por_estado(admin: dict = Depends(get_admin_user)):
    """Estatísticas de Donos de Assessoria por estado"""
    pipeline = [
        {"$match": {"role": "dono_assessoria"}},
        {"$group": {
            "_id": "$estado",
            "total": {"$sum": 1}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [{"estado": r["_id"] or "N/A", "total": r["total"]} for r in result]


@router.get("/admin/stats/assessorias-verificadas")
async def get_stats_assessorias_verificadas(admin: dict = Depends(get_admin_user)):
    """Estatísticas de Assessorias Verificadas vs Não Verificadas"""
    # Buscar dados do ranking de assessorias (mesma lógica da liga)
    from routes.assessorias_routes import router as assessorias_router
    
    # Buscar equipes com atletas
    pipeline = [
        {"$match": {"role": {"$in": ["atleta", "dono_assessoria"]}, "equipe": {"$exists": True, "$ne": ""}}},
        {"$group": {
            "_id": "$equipe",
            "total_atletas": {"$sum": 1}
        }}
    ]
    equipes = await db.usuarios.aggregate(pipeline).to_list(None)
    
    verificadas = 0
    nao_verificadas = 0
    
    for equipe in equipes:
        nome = equipe.get("_id")
        if not nome or nome.lower() in ["individual", "sem equipe"]:
            continue
            
        total_atletas = equipe.get("total_atletas", 0)
        
        # Contar resultados aprovados
        total_resultados = await db.corridas.count_documents({
            "$or": [
                {"nome_assessoria": nome},
                {"equipe": nome}
            ],
            "status": "aprovado"
        })
        
        # Buscar se tem dono
        assessoria_db = await db.assessorias.find_one({"nome": nome}, {"_id": 0, "dono_nome": 1})
        dono_nome = assessoria_db.get("dono_nome") if assessoria_db else None
        
        # Verificar critérios: 10+ atletas, 5+ resultados, dono definido
        if total_atletas >= 10 and total_resultados >= 5 and dono_nome:
            verificadas += 1
        else:
            nao_verificadas += 1
    
    total = verificadas + nao_verificadas
    return {
        "verificadas": verificadas,
        "nao_verificadas": nao_verificadas,
        "total": total,
        "percentual_verificadas": round((verificadas / max(total, 1)) * 100, 1)
    }


@router.get("/admin/stats/insignias")
async def get_stats_insignias(admin: dict = Depends(get_admin_user)):
    """Estatísticas de Insígnias - quantidade de atletas por tipo de insígnia"""
    from services import CONQUISTAS
    
    # Definir todas as insígnias possíveis do sistema
    tipos_insignias = {
        "elite": {"nome": "Atleta Elite", "icone": "⭐", "cor": "#FFD700", "total": 0},
        "maratonista": {"nome": "Maratonista", "icone": "🎯", "cor": "#8B5CF6", "total": 0},
        "primeiro_lugar": {"nome": "Campeão", "icone": "🥇", "cor": "#FFD700", "total": 0},
        "podio": {"nome": "Pódio", "icone": "🏆", "cor": "#F59E0B", "total": 0},
        "10_corridas": {"nome": "Veterano", "icone": "🏃", "cor": "#10B981", "total": 0},
        "12_resultados": {"nome": "Atleta Bronze", "icone": "🥉", "cor": "#CD7F32", "total": 0},
        "20_resultados": {"nome": "Atleta Prata", "icone": "🥈", "cor": "#C0C0C0", "total": 0},
        "30_resultados": {"nome": "Atleta Ouro", "icone": "🥇", "cor": "#FFD700", "total": 0},
        "consistente": {"nome": "Consistente", "icone": "📅", "cor": "#3B82F6", "total": 0},
        "embaixador": {"nome": "Embaixador Run", "icone": "🎖️", "cor": "#EC4899", "total": 0},
    }
    
    # Buscar conquistas de todos os atletas
    conquistas = await db.conquistas_atleta.find({}, {"_id": 0, "conquista_codigo": 1}).to_list(None)
    
    # Contar por tipo de insígnia
    for conquista in conquistas:
        codigo = conquista.get("conquista_codigo", "")
        if codigo in tipos_insignias:
            tipos_insignias[codigo]["total"] += 1
    
    # Converter para lista e ordenar por total (maior primeiro)
    resultado = [
        {
            "codigo": codigo,
            "nome": info["nome"],
            "icone": info["icone"],
            "cor": info["cor"],
            "total": info["total"]
        }
        for codigo, info in tipos_insignias.items()
    ]
    
    # Ordenar: primeiro os que têm atletas, depois por nome
    resultado.sort(key=lambda x: (-x["total"], x["nome"]))
    
    return resultado


@router.get("/admin/stats/insignias-distribuicao")
async def get_stats_insignias_distribuicao(admin: dict = Depends(get_admin_user)):
    """Estatísticas de Insígnias - distribuição por quantidade de insígnias por atleta"""
    # Buscar todos os atletas
    atletas = await db.usuarios.find(
        {"role": {"$in": ["atleta", "dono_assessoria"]}},
        {"_id": 0, "id": 1}
    ).to_list(None)
    
    # Buscar conquistas por atleta
    insignia_counts = {
        "0": 0,
        "1-2": 0,
        "3-5": 0,
        "6-10": 0,
        "10+": 0
    }
    
    for atleta in atletas:
        # Contar conquistas do atleta
        num_conquistas = await db.conquistas_atleta.count_documents({"usuario_id": atleta["id"]})
        
        if num_conquistas == 0:
            insignia_counts["0"] += 1
        elif num_conquistas <= 2:
            insignia_counts["1-2"] += 1
        elif num_conquistas <= 5:
            insignia_counts["3-5"] += 1
        elif num_conquistas <= 10:
            insignia_counts["6-10"] += 1
        else:
            insignia_counts["10+"] += 1
    
    return [
        {"faixa": "0 insígnias", "total": insignia_counts["0"]},
        {"faixa": "1-2 insígnias", "total": insignia_counts["1-2"]},
        {"faixa": "3-5 insígnias", "total": insignia_counts["3-5"]},
        {"faixa": "6-10 insígnias", "total": insignia_counts["6-10"]},
        {"faixa": "10+ insígnias", "total": insignia_counts["10+"]}
    ]


# ==================== GESTÃO DE ATLETAS ====================

@router.get("/admin/atletas")
async def listar_atletas(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=1000),
    search: str = None,
    estado: str = None,
    categoria: str = None,
    modalidade: str = None,
    equipe: str = None,
    admin: dict = Depends(get_admin_user)
):
    """Lista atletas com paginação e filtros"""
    # Incluir atletas e donos de assessoria
    filtro = {"role": {"$in": ["atleta", "dono_assessoria"]}}
    
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
    if modalidade:
        if modalidade == "povao_pace_livre":
            filtro["modalidade_usuario"] = "povao_pace_livre"
        elif modalidade == "profissional_amador":
            filtro["modalidade_usuario"] = {"$ne": "povao_pace_livre"}
    
    # Filtro por tipo de equipe
    if equipe:
        if equipe == "com_assessoria":
            filtro["equipe"] = {"$nin": ["", None, "Individual", "INDIVIDUAL", "Sem equipe"]}
        elif equipe == "individual":
            filtro["$or"] = [
                {"equipe": {"$in": ["", None, "Individual", "INDIVIDUAL", "Sem equipe"]}},
                {"equipe": {"$exists": False}}
            ]
        elif equipe == "dono_assessoria":
            filtro["$or"] = [
                {"role": "dono_assessoria"},
                {"is_dono_assessoria": True}
            ]
    
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
async def exportar_atletas(
    categoria: str = None,
    modalidade: str = None,
    equipe: str = None,
    admin: dict = Depends(get_admin_user)
):
    """Exporta lista de atletas em Excel com filtros"""
    filtro = {"role": "atleta"}
    
    # Aplicar filtros
    if modalidade:
        if modalidade == "povao_pace_livre":
            filtro["modalidade_usuario"] = "povao_pace_livre"
        elif modalidade == "profissional_amador":
            filtro["modalidade_usuario"] = {"$ne": "povao_pace_livre"}
    
    if equipe:
        if equipe == "com_assessoria":
            filtro["equipe"] = {"$nin": ["", None, "Individual", "INDIVIDUAL", "Sem equipe"]}
        elif equipe == "individual":
            filtro["$or"] = [
                {"equipe": {"$in": ["", None, "Individual", "INDIVIDUAL", "Sem equipe"]}},
                {"equipe": {"$exists": False}}
            ]
    
    atletas = await db.usuarios.find(
        filtro,
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
        equipe_nome = atleta.get("equipe", "") or "Individual"
        ws.append([
            atleta.get("nome", ""),
            atleta.get("email", ""),
            equipe_nome,
            atleta.get("cidade", ""),
            atleta.get("estado", ""),
            atleta.get("genero", ""),
            atleta.get("categoria", ""),
            atleta.get("faixa_etaria", ""),
            "Galera" if atleta.get("modalidade_usuario") == "povao_pace_livre" else "Pro/Amador",
            "Ativo" if atleta.get("is_active", True) else "Inativo"
        ])
    
    # Nome do arquivo com filtros
    filtro_nome = []
    if modalidade:
        filtro_nome.append(modalidade)
    if equipe:
        filtro_nome.append(equipe)
    nome_arquivo = f"atletas_{'_'.join(filtro_nome) if filtro_nome else 'todos'}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
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
            detail="Atletas PCD e Cadeirantes não podem participar do Ranking da Galera"
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
        mensagem=f"Sua modalidade foi alterada para {'Ranking da Galera' if nova_modalidade == 'povao_pace_livre' else 'Profissional/Amador'}.",
        dados_extras={"nova_modalidade": nova_modalidade}
    )
    
    return {
        "message": f"Atleta transferido para {nova_modalidade}",
        "atleta_id": atleta_id,
        "modalidade_anterior": modalidade_atual,
        "nova_modalidade": nova_modalidade
    }



# ==================== PROMOVER A DONO DE ASSESSORIA ====================

@router.post("/admin/atletas/{atleta_id}/promover-dono-assessoria")
async def promover_dono_assessoria(
    atleta_id: str,
    admin: dict = Depends(get_admin_user)
):
    """Promove um atleta a Dono de Assessoria - ele poderá criar sua assessoria depois"""
    
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    if atleta.get("role") == "dono_assessoria":
        raise HTTPException(status_code=400, detail="Atleta já é Dono de Assessoria")
    
    if atleta.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Administradores não podem ser promovidos")
    
    # Atualizar atleta para pré-dono de assessoria (aguardando criar assessoria)
    await db.usuarios.update_one(
        {"id": atleta_id},
        {"$set": {
            "role": "dono_assessoria",
            "is_dono_assessoria": True,
            "assessoria_pendente": True,  # Flag indicando que precisa criar a assessoria
            "data_promocao": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Notificar o atleta
    await criar_notificacao(
        usuario_id=atleta_id,
        tipo="promocao",
        titulo="🎉 Você foi promovido a Dono de Assessoria!",
        mensagem="Parabéns! Agora você pode criar sua própria assessoria. Acesse seu perfil e preencha os dados da sua equipe.",
        dados_extras={"tipo_promocao": "dono_assessoria"}
    )
    
    return {
        "message": f"{atleta['nome']} foi promovido a Dono de Assessoria!",
        "atleta_id": atleta_id,
        "atleta_nome": atleta["nome"]
    }


@router.post("/admin/atletas/{atleta_id}/rebaixar-dono-assessoria")
async def rebaixar_dono_assessoria(
    atleta_id: str,
    admin: dict = Depends(get_admin_user)
):
    """Rebaixa um Dono de Assessoria a atleta comum"""
    
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    if atleta.get("role") != "dono_assessoria":
        raise HTTPException(status_code=400, detail="Atleta não é Dono de Assessoria")
    
    # Verificar se tem assessoria vinculada
    assessoria = await db.assessorias.find_one({"dono_id": atleta_id})
    if assessoria:
        # Remover vínculo da assessoria
        await db.assessorias.update_one(
            {"dono_id": atleta_id},
            {"$set": {"dono_id": None, "dono_nome": None}}
        )
    
    # Rebaixar atleta
    await db.usuarios.update_one(
        {"id": atleta_id},
        {"$set": {
            "role": "atleta",
            "is_dono_assessoria": False,
            "assessoria_pendente": False,
            "assessoria_id": None,
            "assessoria_nome": None
        }}
    )
    
    # Notificar o atleta
    await criar_notificacao(
        usuario_id=atleta_id,
        tipo="sistema",
        titulo="Alteração de Função",
        mensagem="Sua função foi alterada para Atleta.",
        dados_extras={"tipo_alteracao": "rebaixamento"}
    )
    
    return {
        "message": f"{atleta['nome']} foi rebaixado a Atleta",
        "atleta_id": atleta_id
    }


# ==================== GESTÃO DE ASSESSORIAS ====================

@router.delete("/admin/assessorias/{nome_assessoria}")
async def deletar_assessoria(nome_assessoria: str, admin: dict = Depends(get_admin_user)):
    """
    Deleta uma assessoria e migra todos os atletas vinculados para 'Individual'.
    Os pontos dos atletas são mantidos intactos.
    
    Apenas Super Admin pode executar esta ação.
    """
    from urllib.parse import unquote
    
    # Verificar se é super_admin
    if admin.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Apenas Super Admin pode deletar assessorias")
    
    nome_decoded = unquote(nome_assessoria)
    
    # Buscar atletas vinculados a esta assessoria
    atletas_vinculados = await db.usuarios.find(
        {"equipe": nome_decoded},
        {"_id": 0, "id": 1, "nome": 1, "email": 1, "role": 1}
    ).to_list(None)
    
    total_atletas = len(atletas_vinculados)
    
    # Registrar log antes da exclusão
    log_exclusao = {
        "id": str(uuid.uuid4()),
        "tipo": "exclusao_assessoria",
        "assessoria_nome": nome_decoded,
        "admin_id": admin["id"],
        "admin_nome": admin.get("nome", "Admin"),
        "total_atletas_migrados": total_atletas,
        "atletas_afetados": [{"id": a["id"], "nome": a["nome"]} for a in atletas_vinculados],
        "data_exclusao": datetime.now(timezone.utc).isoformat()
    }
    await db.logs_sistema.insert_one(log_exclusao)
    
    # Migrar todos os atletas para Individual
    if total_atletas > 0:
        # Atualizar equipe para "Individual" e remover flags de dono se existirem
        await db.usuarios.update_many(
            {"equipe": nome_decoded},
            {
                "$set": {
                    "equipe": "Individual",
                    "equipe_anterior": nome_decoded  # Guardar histórico
                },
                "$unset": {
                    "is_dono_assessoria": "",
                    "assessoria_pendente": "",
                    "assessoria_nome": ""
                }
            }
        )
        
        # Rebaixar donos de assessoria para atleta
        await db.usuarios.update_many(
            {"equipe_anterior": nome_decoded, "role": "dono_assessoria"},
            {"$set": {"role": "atleta"}}
        )
    
    # Deletar a assessoria do banco (se existir na coleção assessorias)
    await db.assessorias.delete_one({"nome": nome_decoded})
    
    # Invalidar cache relacionado
    try:
        from services.cache_service import cache_service
        await cache_service.invalidate_pattern("liga:*")
    except Exception:
        pass
    
    return {
        "message": f"Assessoria '{nome_decoded}' deletada com sucesso!",
        "atletas_migrados": total_atletas,
        "atletas_afetados": [a["nome"] for a in atletas_vinculados[:10]],  # Primeiros 10
        "log_id": log_exclusao["id"]
    }


@router.get("/admin/assessorias/{nome_assessoria}/atletas")
async def listar_atletas_assessoria(nome_assessoria: str, admin: dict = Depends(get_admin_user)):
    """Lista todos os atletas de uma assessoria (para confirmar antes de deletar)"""
    from urllib.parse import unquote
    nome_decoded = unquote(nome_assessoria)
    
    atletas = await db.usuarios.find(
        {"equipe": nome_decoded},
        {"_id": 0, "id": 1, "nome": 1, "email": 1, "role": 1, "pontos_total": 1}
    ).to_list(None)
    
    return {
        "assessoria": nome_decoded,
        "total_atletas": len(atletas),
        "atletas": atletas
    }


# ==================== SENHA DE EMERGÊNCIA ====================

import secrets
import hashlib

# Senha de emergência - armazenada de forma segura
# Esta senha é gerada apenas uma vez e salva no banco
EMERGENCY_PASSWORD_COLLECTION = "configuracoes_sistema"

@router.get("/admin/senha-emergencia")
async def get_senha_emergencia(admin: dict = Depends(get_admin_user)):
    """
    Retorna a senha de emergência atual (apenas Super Admin).
    Se não existir, gera uma nova.
    """
    if admin.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Apenas Super Admin pode visualizar a senha de emergência")
    
    config = await db.configuracoes_sistema.find_one(
        {"tipo": "senha_emergencia"},
        {"_id": 0}
    )
    
    if not config:
        # Gerar nova senha
        nova_senha = secrets.token_urlsafe(24)  # ~32 caracteres seguros
        config = {
            "tipo": "senha_emergencia",
            "senha_plain": nova_senha,  # Armazenada para visualização pelo Super Admin
            "senha_hash": hashlib.sha256(nova_senha.encode()).hexdigest(),
            "criada_em": datetime.now(timezone.utc).isoformat(),
            "criada_por": admin["id"]
        }
        await db.configuracoes_sistema.insert_one(config)
    
    return {
        "senha": config["senha_plain"],
        "criada_em": config.get("criada_em"),
        "aviso": "Esta senha permite acesso a qualquer conta de atleta. Limite: 3 usos por atleta."
    }


@router.post("/admin/senha-emergencia/regenerar")
async def regenerar_senha_emergencia(admin: dict = Depends(get_admin_user)):
    """Gera uma nova senha de emergência (invalida a anterior)"""
    if admin.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Apenas Super Admin pode regenerar a senha")
    
    nova_senha = secrets.token_urlsafe(24)
    
    await db.configuracoes_sistema.update_one(
        {"tipo": "senha_emergencia"},
        {
            "$set": {
                "senha_plain": nova_senha,
                "senha_hash": hashlib.sha256(nova_senha.encode()).hexdigest(),
                "criada_em": datetime.now(timezone.utc).isoformat(),
                "criada_por": admin["id"],
                "regenerada": True
            }
        },
        upsert=True
    )
    
    # Log da regeneração
    await db.logs_sistema.insert_one({
        "id": str(uuid.uuid4()),
        "tipo": "senha_emergencia_regenerada",
        "admin_id": admin["id"],
        "admin_nome": admin.get("nome"),
        "data": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "message": "Senha de emergência regenerada com sucesso!",
        "nova_senha": nova_senha
    }


@router.get("/admin/senha-emergencia/usos")
async def listar_usos_senha_emergencia(
    admin: dict = Depends(get_admin_user),
    limit: int = 50
):
    """Lista os usos da senha de emergência (log de acessos)"""
    if admin.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Apenas Super Admin pode visualizar")
    
    usos = await db.logs_senha_emergencia.find(
        {},
        {"_id": 0}
    ).sort("data_uso", -1).limit(limit).to_list(None)
    
    return {
        "total_registros": len(usos),
        "usos": usos
    }


@router.post("/admin/senha-emergencia/resetar-contador/{atleta_id}")
async def resetar_contador_senha_emergencia(
    atleta_id: str,
    admin: dict = Depends(get_admin_user)
):
    """Reseta o contador de usos da senha de emergência para um atleta específico"""
    if admin.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Apenas Super Admin pode resetar contadores")
    
    atleta = await db.usuarios.find_one({"id": atleta_id}, {"_id": 0, "nome": 1})
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Deletar registros de uso para este atleta
    result = await db.logs_senha_emergencia.delete_many({"atleta_id": atleta_id})
    
    # Log do reset
    await db.logs_sistema.insert_one({
        "id": str(uuid.uuid4()),
        "tipo": "reset_senha_emergencia",
        "atleta_id": atleta_id,
        "atleta_nome": atleta["nome"],
        "admin_id": admin["id"],
        "admin_nome": admin.get("nome"),
        "usos_resetados": result.deleted_count,
        "data": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "message": f"Contador resetado para {atleta['nome']}",
        "usos_removidos": result.deleted_count
    }
