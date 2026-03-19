# /app/backend/routes/assessorias_routes.py
# Módulo de Liga de Assessorias - Ranking ROE-RR

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid

from config import db
from routes.auth_routes import get_current_user, get_admin_user
from services.cache_service import cached, invalidate_on_liga_change

router = APIRouter(tags=["Liga de Assessorias"])


# ==================== LISTA DE ASSESSORIAS ====================

@router.get("/assessorias/lista")
@cached(prefix='liga', ttl_key='liga_assessorias')
async def get_assessorias_lista():
    """Lista assessorias cadastradas para dropdown do cadastro"""
    assessorias = await db.assessorias.find(
        {},
        {"_id": 0, "nome": 1, "cidade": 1, "estado": 1}
    ).to_list(None)
    
    if len(assessorias) == 0:
        pipeline = [
            {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
            {"$group": {
                "_id": "$equipe",
                "cidade": {"$first": "$cidade"},
                "estado": {"$first": "$estado"}
            }}
        ]
        equipes_raw = await db.usuarios.aggregate(pipeline).to_list(None)
        assessorias = [
            {"nome": e["_id"], "cidade": e.get("cidade", ""), "estado": e.get("estado", "")}
            for e in equipes_raw if e["_id"]
        ]
    
    return assessorias


# ==================== RANKING LIGA ASSESSORIAS ====================

@router.get("/liga-assessorias/ranking")
@cached(prefix='liga', ttl_key='liga_assessorias')
async def get_ranking_assessorias(
    tipo: str = "nacional",
    estado: str = None,
    cidade: str = None,
    mes: int = None
):
    """
    Retorna ranking das assessorias baseado no sistema ROE-RR
    
    Sistema de Pontuação:
    - +0,5 por atleta cadastrado e vinculado
    - +1,0 por resultado aprovado
    - +0,5 adicional para 2º-5º lugar
    - +1,0 adicional para 1º lugar
    """
    agora = datetime.now()
    ano_atual = agora.year
    
    filtro_corridas = {}
    
    if tipo != "historico":
        if mes and 1 <= mes <= 12:
            inicio_mes = f"{ano_atual}-{mes:02d}-01"
            if mes == 12:
                fim_mes = f"{ano_atual + 1}-01-01"
            else:
                fim_mes = f"{ano_atual}-{mes + 1:02d}-01"
            filtro_corridas["data"] = {"$gte": inicio_mes, "$lt": fim_mes}
        else:
            inicio_ano = f"{ano_atual}-01-01"
            filtro_corridas["data"] = {"$gte": inicio_ano}
    
    pipeline_equipes = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe", "sem equipe"], "$exists": True}}},
        {"$group": {
            "_id": "$equipe",
            "estado": {"$first": "$estado"},
            "cidade": {"$first": "$cidade"},
            "atletas": {"$push": {
                "id": "$id",
                "nome": "$nome",
                "foto_url": "$foto_url",
                "estado": "$estado",
                "cidade": "$cidade"
            }},
            "total_atletas": {"$sum": 1},
            "data_mais_antiga": {"$min": "$id"}
        }},
        {"$match": {"_id": {"$nin": ["Sem equipe", "sem equipe", "", None]}}}
    ]
    
    # Filtrar por estado/cidade APÓS o agrupamento para pegar assessorias desse local
    if tipo == "estadual" and estado:
        pipeline_equipes.append({"$match": {"estado": estado}})
    elif tipo == "cidade" and cidade:
        pipeline_equipes.append({"$match": {"cidade": cidade}})
    
    equipes_raw = await db.usuarios.aggregate(pipeline_equipes).to_list(None)
    
    ranking_assessorias = []
    
    for equipe in equipes_raw:
        nome_equipe = equipe["_id"]
        atletas_ids = [a["id"] for a in equipe["atletas"]]
        
        pontos_cadastro = len(atletas_ids) * 0.5
        
        # Buscar dados da assessoria cadastrada (se existir)
        assessoria_db = await db.assessorias.find_one(
            {"nome": nome_equipe},
            {"_id": 0, "dono_id": 1, "dono_nome": 1}
        )
        
        dono_nome = None
        dono_id = None
        
        if assessoria_db:
            dono_nome = assessoria_db.get("dono_nome")
            dono_id = assessoria_db.get("dono_id")
        
        # Se não tem dono_nome na assessoria, buscar no usuário
        if not dono_nome and dono_id:
            dono_user = await db.usuarios.find_one(
                {"id": dono_id},
                {"_id": 0, "nome": 1}
            )
            if dono_user:
                dono_nome = dono_user.get("nome")
        
        filtro_corridas_equipe = {
            "usuario_id": {"$in": atletas_ids},
            **filtro_corridas
        }
        
        corridas = await db.corridas.find(filtro_corridas_equipe, {"_id": 0}).to_list(None)
        
        pontos_resultados = 0
        total_primeiros = 0
        total_podios = 0
        total_resultados = len(corridas)
        
        for corrida in corridas:
            pontos_resultados += 1.0
            
            colocacao = corrida.get("colocacao", 0)
            modalidade = corrida.get("modalidade", "profissional_amador")
            
            if modalidade == "profissional_amador" and colocacao > 0:
                if colocacao == 1:
                    pontos_resultados += 1.0
                    total_primeiros += 1
                elif 2 <= colocacao <= 5:
                    pontos_resultados += 0.5
                    total_podios += 1
        
        pontos_total = pontos_cadastro + pontos_resultados
        
        ranking_assessorias.append({
            "nome": nome_equipe,
            "estado": equipe.get("estado", ""),
            "cidade": equipe.get("cidade", ""),
            "total_atletas": equipe["total_atletas"],
            "pontos_cadastro": pontos_cadastro,
            "pontos_resultados": pontos_resultados,
            "pontos_total": round(pontos_total, 1),
            "total_resultados": total_resultados,
            "total_primeiros": total_primeiros,
            "total_podios": total_podios,
            "dono_nome": dono_nome,
            "dono_id": dono_id,
            "verificada": bool(dono_nome and equipe["total_atletas"] >= 10 and total_resultados >= 5),
            "atletas": equipe["atletas"][:10],
            "data_mais_antiga": equipe.get("data_mais_antiga", "")
        })
    
    ranking_assessorias.sort(key=lambda x: (
        -x["pontos_total"],
        -x["total_primeiros"],
        -x["total_atletas"],
        -x["total_resultados"],
        x["data_mais_antiga"]
    ))
    
    for idx, equipe in enumerate(ranking_assessorias):
        equipe["posicao"] = idx + 1
        
        if tipo in ["nacional", "historico", "anual"]:
            if idx < 20:
                equipe["selo"] = "ouro"
            elif idx < 50:
                equipe["selo"] = "prata"
            else:
                equipe["selo"] = "bronze"
        elif tipo == "estadual":
            if idx < 10:
                equipe["selo"] = "prata"
            else:
                equipe["selo"] = "bronze"
        else:
            equipe["selo"] = "bronze"
    
    return {
        "tipo": tipo,
        "periodo": {
            "mensal": f"{agora.strftime('%B %Y')}",
            "anual": str(ano_atual),
            "historico": "Todo período",
            "nacional": "Todo período",
            "estadual": f"Estado: {estado}" if estado else "Todos",
            "cidade": f"Cidade: {cidade}" if cidade else "Todas"
        }.get(tipo, ""),
        "total_assessorias": len(ranking_assessorias),
        "ranking": ranking_assessorias
    }


# ==================== ESTATÍSTICAS DA LIGA ====================

@router.get("/liga-assessorias/stats")
@cached(prefix='liga', ttl_key='stats')
async def get_stats_liga_assessorias():
    """Estatísticas gerais da liga de assessorias"""
    
    pipeline_total = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe", "sem equipe"]}}},
        {"$group": {"_id": "$equipe"}},
        {"$count": "total"}
    ]
    
    result = await db.usuarios.aggregate(pipeline_total).to_list(1)
    total_assessorias = result[0]["total"] if result else 0
    
    total_atletas_vinculados = await db.usuarios.count_documents({
        "role": "atleta",
        "equipe": {"$nin": ["", None, "Sem equipe", "sem equipe"]}
    })
    
    total_resultados_aprovados = await db.corridas.count_documents({})
    
    pipeline_top = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
        {"$group": {"_id": "$equipe", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    top_result = await db.usuarios.aggregate(pipeline_top).to_list(1)
    maior_assessoria = top_result[0]["_id"] if top_result else "N/A"
    
    return {
        "total_assessorias": total_assessorias,
        "total_atletas_vinculados": total_atletas_vinculados,
        "total_resultados_aprovados": total_resultados_aprovados,
        "maior_assessoria": maior_assessoria
    }


# ==================== EVOLUÇÃO MENSAL ====================

@router.get("/liga-assessorias/evolucao-mensal")
@cached(prefix='liga', ttl=600)
async def get_evolucao_mensal_equipes(top: int = 5):
    """Retorna a evolução mensal de pontos das top equipes"""
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    
    pipeline_top_equipes = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None, "Sem equipe"]}}},
        {"$group": {"_id": "$equipe", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": top}
    ]
    
    top_equipes = await db.usuarios.aggregate(pipeline_top_equipes).to_list(None)
    equipes_nomes = [e["_id"] for e in top_equipes]
    
    meses = []
    for i in range(6):
        mes = mes_atual - i
        ano = ano_atual
        if mes < 1:
            mes += 12
            ano -= 1
        meses.append((ano, mes))
    
    meses.reverse()
    
    evolucao = {nome: [] for nome in equipes_nomes}
    
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    labels = []
    
    for ano, mes in meses:
        labels.append(f"{meses_nomes[mes-1]}/{str(ano)[-2:]}")
        
        inicio_mes = f"{ano}-{mes:02d}-01"
        if mes == 12:
            fim_mes = f"{ano + 1}-01-01"
        else:
            fim_mes = f"{ano}-{mes + 1:02d}-01"
        
        for nome_equipe in equipes_nomes:
            atletas_equipe = await db.usuarios.find(
                {"role": "atleta", "equipe": nome_equipe},
                {"id": 1}
            ).to_list(None)
            atletas_ids = [a["id"] for a in atletas_equipe]
            
            corridas_mes = await db.corridas.find({
                "usuario_id": {"$in": atletas_ids},
                "data": {"$gte": inicio_mes, "$lt": fim_mes}
            }).to_list(None)
            
            pontos_mes = len(corridas_mes)
            for c in corridas_mes:
                col = c.get("colocacao", 0)
                if col == 1:
                    pontos_mes += 1
                elif 2 <= col <= 5:
                    pontos_mes += 0.5
            
            evolucao[nome_equipe].append(round(pontos_mes, 1))
    
    datasets = []
    cores = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6"]
    
    for idx, nome in enumerate(equipes_nomes):
        datasets.append({
            "label": nome,
            "data": evolucao[nome],
            "borderColor": cores[idx % len(cores)],
            "tension": 0.1
        })
    
    return {
        "labels": labels,
        "datasets": datasets
    }


# ==================== DETALHE DA ASSESSORIA ====================

@router.get("/liga-assessorias/assessoria/{nome_equipe}")
async def get_detalhes_assessoria(nome_equipe: str):
    """Retorna detalhes de uma assessoria específica"""
    import urllib.parse
    nome_equipe = urllib.parse.unquote(nome_equipe)
    
    # Buscar atletas e donos de assessoria com essa equipe
    atletas = await db.usuarios.find(
        {"role": {"$in": ["atleta", "dono_assessoria"]}, "equipe": nome_equipe},
        {"_id": 0, "password_hash": 0}
    ).to_list(None)
    
    # Se não encontrou, verificar se existe a assessoria cadastrada
    if not atletas:
        assessoria_doc = await db.assessorias.find_one({"nome": nome_equipe})
        if assessoria_doc:
            # Buscar o dono pelo ID
            if assessoria_doc.get("dono_id"):
                dono = await db.usuarios.find_one(
                    {"id": assessoria_doc["dono_id"]},
                    {"_id": 0, "password_hash": 0}
                )
                if dono:
                    atletas = [dono]
        
        if not atletas:
            raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    atletas_ids = [a["id"] for a in atletas]
    
    # Buscar dados da assessoria cadastrada
    assessoria_doc = await db.assessorias.find_one(
        {"nome": nome_equipe},
        {"_id": 0}
    )
    
    # Buscar dono da assessoria
    dono_info = None
    responsavel_nome = None
    responsavel_id = None
    dono_atleta = None
    
    if assessoria_doc and assessoria_doc.get("dono_id"):
        dono = await db.usuarios.find_one(
            {"id": assessoria_doc["dono_id"]},
            {"_id": 0, "password_hash": 0}
        )
        if dono:
            dono_info = dono
            responsavel_nome = dono.get("nome")
            responsavel_id = dono.get("id")
            
            # Se o dono não está na lista de atletas, incluí-lo
            if dono.get("id") not in atletas_ids:
                dono_atleta = dono
                atletas_ids.append(dono.get("id"))
    
    # Buscar pontos de cada atleta
    atletas_com_pontos = []
    
    # Processar atletas normais
    for atleta in atletas:
        ranking_atleta = await db.ranking_anual.find_one(
            {"usuario_id": atleta["id"], "ano": 2025},
            {"_id": 0, "pontos_total": 1, "total_corridas": 1}
        )
        ranking_povao = await db.ranking_povao.find_one(
            {"usuario_id": atleta["id"], "ano": 2025},
            {"_id": 0, "pontos_total": 1, "total_corridas": 1}
        )
        
        pontos_atleta = 0
        corridas_atleta = 0
        if ranking_atleta:
            pontos_atleta = ranking_atleta.get("pontos_total", 0)
            corridas_atleta = ranking_atleta.get("total_corridas", 0)
        if ranking_povao:
            pontos_atleta = max(pontos_atleta, ranking_povao.get("pontos_total", 0))
            corridas_atleta = max(corridas_atleta, ranking_povao.get("total_corridas", 0))
        
        atletas_com_pontos.append({
            **atleta,
            "pontos": pontos_atleta,
            "total_corridas": corridas_atleta,
            "is_dono": atleta.get("id") == responsavel_id
        })
    
    # Adicionar o dono se ele não estava na lista de atletas
    if dono_atleta:
        ranking_dono = await db.ranking_anual.find_one(
            {"usuario_id": dono_atleta["id"], "ano": 2025},
            {"_id": 0, "pontos_total": 1, "total_corridas": 1}
        )
        ranking_povao_dono = await db.ranking_povao.find_one(
            {"usuario_id": dono_atleta["id"], "ano": 2025},
            {"_id": 0, "pontos_total": 1, "total_corridas": 1}
        )
        
        pontos_dono = 0
        corridas_dono = 0
        if ranking_dono:
            pontos_dono = ranking_dono.get("pontos_total", 0)
            corridas_dono = ranking_dono.get("total_corridas", 0)
        if ranking_povao_dono:
            pontos_dono = max(pontos_dono, ranking_povao_dono.get("pontos_total", 0))
            corridas_dono = max(corridas_dono, ranking_povao_dono.get("total_corridas", 0))
        
        atletas_com_pontos.append({
            **dono_atleta,
            "pontos": pontos_dono,
            "total_corridas": corridas_dono,
            "is_dono": True
        })
    
    # Ordenar atletas por pontos (decrescente)
    atletas_com_pontos.sort(key=lambda x: x.get("pontos", 0), reverse=True)
    
    corridas = await db.corridas.find(
        {"usuario_id": {"$in": atletas_ids}},
        {"_id": 0}
    ).to_list(None)
    
    pontos_cadastro = len(atletas) * 0.5
    pontos_resultados = len(corridas)
    total_primeiros = sum(1 for c in corridas if c.get("colocacao") == 1)
    total_podios = sum(1 for c in corridas if 2 <= c.get("colocacao", 0) <= 5)
    
    for c in corridas:
        if c.get("colocacao") == 1:
            pontos_resultados += 1
        elif 2 <= c.get("colocacao", 0) <= 5:
            pontos_resultados += 0.5
    
    # Buscar posição no ranking NACIONAL
    ranking_nacional = await get_ranking_assessorias(tipo="nacional")
    posicao_nacional = next(
        (eq["posicao"] for eq in ranking_nacional.get("ranking", []) if eq["nome"] == nome_equipe),
        None
    )
    
    # Buscar posição no ranking ESTADUAL
    estado_equipe = atletas[0].get("estado", "") if atletas else ""
    posicao_estadual = None
    if estado_equipe:
        ranking_estadual = await get_ranking_assessorias(tipo="estadual", estado=estado_equipe)
        posicao_estadual = next(
            (eq["posicao"] for eq in ranking_estadual.get("ranking", []) if eq["nome"] == nome_equipe),
            None
        )
    
    # Determinar selo baseado na posição
    selo = "participante"
    if posicao_nacional:
        if posicao_nacional <= 20:
            selo = "ouro"
        elif posicao_nacional <= 50:
            selo = "prata"
        else:
            selo = "bronze"
    
    # Total de atletas inclui o dono se ele for contado
    total_atletas_count = len(atletas_com_pontos)
    
    return {
        "nome": nome_equipe,
        "estado": estado_equipe,
        "cidade": atletas[0].get("cidade", "") if atletas else "",
        "total_atletas": total_atletas_count,
        "pontos_cadastro": pontos_cadastro,
        "pontos_resultados": pontos_resultados,
        "pontos_total": round(pontos_cadastro + pontos_resultados, 1),
        "total_resultados": len(corridas),
        "total_primeiros": total_primeiros,
        "total_podios": total_podios,
        "posicao_ranking": posicao_nacional,
        "posicao_nacional": posicao_nacional,
        "posicao_estadual": posicao_estadual,
        "selo": selo,
        "atletas": atletas_com_pontos,
        "dono": dono_info,
        "responsavel_nome": responsavel_nome,
        "responsavel_id": responsavel_id,
        "mensagem_bio": assessoria_doc.get("mensagem_bio", "") if assessoria_doc else "",
        "foto_url": assessoria_doc.get("foto_url", "") if assessoria_doc else "",
        "whatsapp_link": assessoria_doc.get("whatsapp_link", "") if assessoria_doc else ""
    }


# ==================== SISTEMA DE SOLICITAÇÕES DE ENTRADA ====================

from pydantic import BaseModel
import uuid

class SolicitacaoEntradaRequest(BaseModel):
    assessoria_nome: str
    mensagem: str = ""


@router.post("/assessorias/solicitar-entrada")
async def solicitar_entrada_assessoria(
    dados: SolicitacaoEntradaRequest,
    current_user: dict = Depends(get_current_user)
):
    """Atleta solicita entrada em uma assessoria"""
    
    # Verificar se atleta já tem equipe (não individual)
    equipe_atual = current_user.get("equipe", "")
    if equipe_atual and equipe_atual.upper() not in ["", "INDIVIDUAL", "SEM EQUIPE"]:
        raise HTTPException(
            status_code=400, 
            detail="Você já pertence a uma equipe. Saia da equipe atual antes de solicitar entrada em outra."
        )
    
    # Verificar se assessoria existe
    assessoria = await db.assessorias.find_one({"nome": dados.assessoria_nome})
    if not assessoria:
        # Verificar se existe como equipe informal
        equipe_existe = await db.usuarios.find_one({"equipe": dados.assessoria_nome})
        if not equipe_existe:
            raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    # Verificar se já existe solicitação pendente
    solicitacao_existente = await db.solicitacoes_assessoria.find_one({
        "atleta_id": current_user["id"],
        "assessoria_nome": dados.assessoria_nome,
        "status": "pendente"
    })
    
    if solicitacao_existente:
        raise HTTPException(status_code=400, detail="Você já tem uma solicitação pendente para esta assessoria")
    
    # Criar solicitação
    solicitacao = {
        "id": str(uuid.uuid4()),
        "atleta_id": current_user["id"],
        "atleta_nome": current_user.get("nome", ""),
        "atleta_email": current_user.get("email", ""),
        "atleta_foto": current_user.get("foto_url", ""),
        "atleta_cidade": current_user.get("cidade", ""),
        "atleta_estado": current_user.get("estado", ""),
        "assessoria_nome": dados.assessoria_nome,
        "mensagem": dados.mensagem,
        "status": "pendente",
        "data_solicitacao": datetime.now(timezone.utc).isoformat(),
        "data_resposta": None,
        "respondido_por": None
    }
    
    await db.solicitacoes_assessoria.insert_one(solicitacao)
    
    # Notificar o dono da assessoria
    if assessoria and assessoria.get("dono_id"):
        from routes.notificacoes_routes import criar_notificacao
        await criar_notificacao(
            usuario_id=assessoria["dono_id"],
            tipo="solicitacao_entrada",
            titulo="📩 Nova solicitação de entrada!",
            mensagem=f"{current_user.get('nome', 'Um atleta')} quer entrar na sua assessoria.",
            dados_extras={
                "solicitacao_id": solicitacao["id"],
                "atleta_id": current_user["id"],
                "atleta_nome": current_user.get("nome", "")
            }
        )
    
    return {
        "message": "Solicitação enviada com sucesso! Aguarde a aprovação do dono da assessoria.",
        "solicitacao_id": solicitacao["id"]
    }


@router.get("/assessorias/solicitacoes-pendentes")
async def get_solicitacoes_pendentes(current_user: dict = Depends(get_current_user)):
    """Retorna solicitações pendentes para a assessoria do dono logado"""
    
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria podem ver solicitações")
    
    equipe = current_user.get("equipe", "")
    if not equipe:
        return {"solicitacoes": [], "total_pendentes": 0}
    
    solicitacoes = await db.solicitacoes_assessoria.find(
        {"assessoria_nome": equipe, "status": "pendente"},
        {"_id": 0}
    ).sort("data_solicitacao", -1).to_list(100)
    
    return {
        "solicitacoes": solicitacoes,
        "total_pendentes": len(solicitacoes)
    }


@router.post("/assessorias/aprovar-solicitacao/{solicitacao_id}")
async def aprovar_solicitacao(solicitacao_id: str, current_user: dict = Depends(get_current_user)):
    """Dono aprova solicitação de entrada"""
    
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria podem aprovar solicitações")
    
    solicitacao = await db.solicitacoes_assessoria.find_one({"id": solicitacao_id})
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    if solicitacao["status"] != "pendente":
        raise HTTPException(status_code=400, detail="Esta solicitação já foi processada")
    
    # Verificar se o dono tem permissão (é da mesma assessoria)
    if current_user.get("role") == "dono_assessoria":
        if solicitacao["assessoria_nome"] != current_user.get("equipe"):
            raise HTTPException(status_code=403, detail="Você não tem permissão para aprovar esta solicitação")
    
    # Atualizar equipe do atleta
    await db.usuarios.update_one(
        {"id": solicitacao["atleta_id"]},
        {"$set": {
            "equipe": solicitacao["assessoria_nome"],
            "ultima_troca_equipe": datetime.now().isoformat()
        }}
    )
    
    # Atualizar solicitação
    await db.solicitacoes_assessoria.update_one(
        {"id": solicitacao_id},
        {"$set": {
            "status": "aprovada",
            "data_resposta": datetime.now(timezone.utc).isoformat(),
            "respondido_por": current_user["id"]
        }}
    )
    
    # Notificar o atleta
    from routes.notificacoes_routes import criar_notificacao
    await criar_notificacao(
        usuario_id=solicitacao["atleta_id"],
        tipo="aprovacao_entrada",
        titulo="🎉 Solicitação aprovada!",
        mensagem=f"Parabéns! Sua solicitação para entrar na {solicitacao['assessoria_nome']} foi aprovada!",
        dados_extras={"assessoria_nome": solicitacao["assessoria_nome"]}
    )
    
    # Invalidar cache
    await invalidate_on_liga_change()
    
    return {
        "message": f"{solicitacao['atleta_nome']} foi adicionado(a) à assessoria!",
        "atleta_nome": solicitacao["atleta_nome"]
    }


@router.post("/assessorias/reprovar-solicitacao/{solicitacao_id}")
async def reprovar_solicitacao(
    solicitacao_id: str,
    dados: dict = None,
    current_user: dict = Depends(get_current_user)
):
    """Dono reprova solicitação de entrada"""
    
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria podem reprovar solicitações")
    
    solicitacao = await db.solicitacoes_assessoria.find_one({"id": solicitacao_id})
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    if solicitacao["status"] != "pendente":
        raise HTTPException(status_code=400, detail="Esta solicitação já foi processada")
    
    # Verificar permissão
    if current_user.get("role") == "dono_assessoria":
        if solicitacao["assessoria_nome"] != current_user.get("equipe"):
            raise HTTPException(status_code=403, detail="Você não tem permissão para reprovar esta solicitação")
    
    motivo = dados.get("motivo", "Solicitação não aprovada") if dados else "Solicitação não aprovada"
    
    # Atualizar solicitação
    await db.solicitacoes_assessoria.update_one(
        {"id": solicitacao_id},
        {"$set": {
            "status": "reprovada",
            "motivo_reprovacao": motivo,
            "data_resposta": datetime.now(timezone.utc).isoformat(),
            "respondido_por": current_user["id"]
        }}
    )
    
    # Notificar o atleta
    from routes.notificacoes_routes import criar_notificacao
    await criar_notificacao(
        usuario_id=solicitacao["atleta_id"],
        tipo="reprovacao_entrada",
        titulo="Solicitação não aprovada",
        mensagem=f"Sua solicitação para entrar na {solicitacao['assessoria_nome']} não foi aprovada. Motivo: {motivo}",
        dados_extras={"assessoria_nome": solicitacao["assessoria_nome"], "motivo": motivo}
    )
    
    return {
        "message": "Solicitação reprovada",
        "atleta_nome": solicitacao["atleta_nome"]
    }


@router.get("/assessorias/minhas-solicitacoes")
async def get_minhas_solicitacoes(current_user: dict = Depends(get_current_user)):
    """Atleta vê suas solicitações pendentes"""
    
    solicitacoes = await db.solicitacoes_assessoria.find(
        {"atleta_id": current_user["id"]},
        {"_id": 0}
    ).sort("data_solicitacao", -1).to_list(20)
    
    return {"solicitacoes": solicitacoes}


# ==================== UPLOAD DE FOTO DA ASSESSORIA ====================

from fastapi import UploadFile, File
import os
import shutil
from pathlib import Path

UPLOAD_DIR = Path("/app/uploads/assessorias")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/assessorias/upload-foto")
async def upload_foto_assessoria(
    foto: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Faz upload da foto da assessoria.
    Apenas o dono da assessoria pode fazer upload.
    """
    
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria podem fazer upload de foto")
    
    equipe = current_user.get("equipe", "")
    if not equipe:
        raise HTTPException(status_code=400, detail="Você não tem uma assessoria cadastrada")
    
    # Validar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if foto.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de arquivo não permitido. Use: JPEG, PNG, WebP ou GIF"
        )
    
    # Validar tamanho (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    content = await foto.read()
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo: 5MB")
    
    # Gerar nome único para o arquivo
    ext = foto.filename.split('.')[-1] if '.' in foto.filename else 'jpg'
    filename = f"{equipe.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Salvar arquivo
    with open(filepath, "wb") as f:
        f.write(content)
    
    # URL pública do arquivo
    foto_url = f"/uploads/assessorias/{filename}"
    
    # Atualizar no banco de dados
    # Primeiro, verificar se existe na coleção assessorias
    assessoria = await db.assessorias.find_one({"nome": equipe})
    if assessoria:
        await db.assessorias.update_one(
            {"nome": equipe},
            {"$set": {"foto_url": foto_url}}
        )
    else:
        # Criar registro da assessoria
        await db.assessorias.insert_one({
            "id": str(uuid.uuid4()),
            "nome": equipe,
            "foto_url": foto_url,
            "dono_id": current_user["id"],
            "dono_nome": current_user.get("nome", ""),
            "cidade": current_user.get("cidade", ""),
            "estado": current_user.get("estado", ""),
            "status": "ativa",
            "data_criacao": datetime.now(timezone.utc).isoformat()
        })
    
    # Invalidar cache
    await invalidate_on_liga_change()
    
    return {
        "message": "Foto da assessoria atualizada com sucesso!",
        "foto_url": foto_url
    }


@router.delete("/assessorias/remover-foto")
async def remover_foto_assessoria(current_user: dict = Depends(get_current_user)):
    """Remove a foto da assessoria"""
    
    if current_user.get("role") not in ["dono_assessoria", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Apenas donos de assessoria podem remover a foto")
    
    equipe = current_user.get("equipe", "")
    if not equipe:
        raise HTTPException(status_code=400, detail="Você não tem uma assessoria cadastrada")
    
    # Buscar assessoria
    assessoria = await db.assessorias.find_one({"nome": equipe})
    if assessoria and assessoria.get("foto_url"):
        # Tentar remover arquivo físico
        foto_path = Path(f"/app{assessoria['foto_url']}")
        if foto_path.exists():
            foto_path.unlink()
        
        # Atualizar banco
        await db.assessorias.update_one(
            {"nome": equipe},
            {"$set": {"foto_url": ""}}
        )
    
    await invalidate_on_liga_change()
    
    return {"message": "Foto removida com sucesso"}
