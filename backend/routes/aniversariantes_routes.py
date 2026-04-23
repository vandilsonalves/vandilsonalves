# /app/backend/routes/aniversariantes_routes.py
# Módulo de Aniversariantes - Gestão de mensagens de aniversário

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone

from config import db
from models import MensagemAniversario
from routes.auth_routes import get_admin_user

router = APIRouter(tags=["Aniversariantes"])


# ==================== CONSULTAS ====================

@router.get("/admin/aniversariantes")
async def get_aniversariantes_mes(
    mes: int = None, 
    ano: int = None, 
    admin: dict = Depends(get_admin_user)
):
    """Retorna os aniversariantes do mês com calendário"""
    hoje = datetime.now()
    mes_atual = mes or hoje.month
    ano_atual = ano or hoje.year
    
    atletas = await db.usuarios.find({"role": {"$in": ["atleta", "dono_assessoria"]}}, {"_id": 0}).to_list(None)
    
    calendario = {dia: [] for dia in range(1, 32)}
    
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


@router.get("/admin/aniversariantes/hoje")
async def get_aniversariantes_hoje(admin: dict = Depends(get_admin_user)):
    """Retorna os aniversariantes do dia"""
    hoje = datetime.now()
    
    atletas = await db.usuarios.find({"role": {"$in": ["atleta", "dono_assessoria"]}}, {"_id": 0}).to_list(None)
    
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


@router.get("/admin/aniversariantes/semana")
async def get_aniversariantes_semana(admin: dict = Depends(get_admin_user)):
    """Retorna os aniversariantes da semana atual"""
    from datetime import timedelta
    
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    atletas = await db.usuarios.find({"role": {"$in": ["atleta", "dono_assessoria"]}}, {"_id": 0}).to_list(None)
    
    aniversariantes = []
    for atleta in atletas:
        if atleta.get("data_nascimento"):
            try:
                data_nasc = datetime.strptime(atleta["data_nascimento"], "%Y-%m-%d")
                # Criar data de aniversário no ano atual
                aniversario = data_nasc.replace(year=hoje.year)
                
                if inicio_semana.date() <= aniversario.date() <= fim_semana.date():
                    aniversariantes.append({
                        "id": atleta["id"],
                        "nome": atleta["nome"],
                        "apelido": atleta.get("apelido", ""),
                        "foto_url": atleta.get("foto_url", ""),
                        "equipe": atleta.get("equipe", ""),
                        "email": atleta["email"],
                        "idade": hoje.year - data_nasc.year,
                        "data_aniversario": aniversario.strftime("%Y-%m-%d"),
                        "dia_semana": aniversario.strftime("%A")
                    })
            except ValueError:
                pass
    
    # Ordenar por data
    aniversariantes.sort(key=lambda x: x["data_aniversario"])
    
    return {
        "aniversariantes": aniversariantes,
        "periodo": f"{inicio_semana.strftime('%d/%m')} - {fim_semana.strftime('%d/%m/%Y')}"
    }


# ==================== ENVIO DE MENSAGENS ====================

@router.post("/admin/aniversariantes/enviar-mensagem")
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


@router.post("/admin/aniversariantes/enviar-agora")
async def enviar_aniversarios_agora(admin: dict = Depends(get_admin_user)):
    """Força o envio imediato de mensagens de aniversário para os aniversariantes de hoje"""
    hoje = datetime.now()
    
    config = await db.configuracoes.find_one({"tipo": "mensagem_aniversario"}, {"_id": 0})
    mensagem_padrao = config.get("mensagem_padrao", 
        "Feliz Aniversário! 🎂 Que este novo ciclo traga muitas conquistas nas pistas. O Ranking Run Pró deseja a você muita saúde e velocidade! 🏃‍♂️"
    ) if config else "Feliz Aniversário! 🎂 O Ranking Run Pró deseja a você muita saúde e velocidade! 🏃‍♂️"
    
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
    
    mensagens_enviadas = 0
    for atleta in aniversariantes:
        # Verificar se já recebeu mensagem hoje
        existente = await db.mensagens_aniversario.find_one({
            "usuario_id": atleta["id"],
            "ano": hoje.year
        })
        
        if not existente:
            msg = MensagemAniversario(
                usuario_id=atleta["id"],
                mensagem=mensagem_padrao,
                ano=hoje.year
            )
            await db.mensagens_aniversario.insert_one(msg.model_dump())
            mensagens_enviadas += 1
    
    return {
        "message": f"{mensagens_enviadas} mensagem(ns) enviada(s) com sucesso!",
        "total_aniversariantes": len(aniversariantes),
        "mensagens_enviadas": mensagens_enviadas
    }


@router.post("/admin/aniversariantes/enviar-email-massa")
async def enviar_email_aniversario_massa(admin: dict = Depends(get_admin_user)):
    """Envia emails de aniversário em massa via background task"""
    import asyncio
    import uuid

    task_id = str(uuid.uuid4())

    async def _enviar():
        try:
            from datetime import datetime as dt
            hoje = dt.now().strftime("%m-%d")
            pipeline = [
                {"$match": {"role": {"$in": ["atleta", "dono_assessoria"]}, "is_active": True}},
                {"$addFields": {"mes_dia": {"$substr": ["$data_nascimento", 5, 5]}}},
                {"$match": {"mes_dia": hoje}}
            ]
            aniversariantes = await db.usuarios.aggregate(pipeline).to_list(None)
            logger.info(f"Email massa aniversário: {len(aniversariantes)} atletas encontrados")
        except Exception as e:
            logger.error(f"Erro no envio de aniversários em massa: {e}")

    asyncio.create_task(_enviar())

    return {
        "message": "Envio de emails enfileirado com sucesso!",
        "task_id": task_id
    }


# ==================== CONFIGURAÇÃO ====================

@router.get("/admin/aniversariantes/configuracao")
async def get_configuracao_aniversario(admin: dict = Depends(get_admin_user)):
    """Retorna configuração de mensagem de aniversário"""
    config = await db.configuracoes.find_one({"tipo": "mensagem_aniversario"}, {"_id": 0})
    if not config:
        config_doc = {
            "tipo": "mensagem_aniversario",
            "mensagem_padrao": "Feliz Aniversário! 🎂 Que este novo ciclo traga muitas conquistas nas pistas. O Ranking Run Pró deseja a você muita saúde e velocidade! 🏃‍♂️",
            "envio_automatico": False,
            "horario_envio": "08:00"
        }
        await db.configuracoes.insert_one(config_doc)
        return {k: v for k, v in config_doc.items() if k != "_id"}
    
    return config


@router.put("/admin/aniversariantes/configuracao")
async def update_configuracao_aniversario(dados: dict, admin: dict = Depends(get_admin_user)):
    """Atualiza configuração de mensagem de aniversário"""
    await db.configuracoes.update_one(
        {"tipo": "mensagem_aniversario"},
        {"$set": {
            "mensagem_padrao": dados.get("mensagem_padrao", ""),
            "envio_automatico": dados.get("envio_automatico", False),
            "horario_envio": dados.get("horario_envio", "08:00")
        }},
        upsert=True
    )
    return {"message": "Configuração atualizada com sucesso!"}


# ==================== HISTÓRICO ====================

@router.get("/admin/aniversariantes/historico")
async def get_historico_mensagens(
    mes: int = None,
    ano: int = None,
    admin: dict = Depends(get_admin_user)
):
    """Retorna histórico de mensagens enviadas"""
    hoje = datetime.now()
    ano_filtro = ano or hoje.year
    
    filtro = {"ano": ano_filtro}
    if mes:
        # Filtrar por mês da data_criacao
        inicio = f"{ano_filtro}-{mes:02d}-01"
        if mes == 12:
            fim = f"{ano_filtro + 1}-01-01"
        else:
            fim = f"{ano_filtro}-{mes + 1:02d}-01"
        filtro["data_criacao"] = {"$gte": inicio, "$lt": fim}
    
    mensagens = await db.mensagens_aniversario.find(
        filtro,
        {"_id": 0}
    ).sort("data_criacao", -1).to_list(None)
    
    # Enriquecer com dados do atleta
    for msg in mensagens:
        atleta = await db.usuarios.find_one(
            {"id": msg["usuario_id"]},
            {"_id": 0, "nome": 1, "foto_url": 1}
        )
        if atleta:
            msg["atleta_nome"] = atleta.get("nome", "")
            msg["atleta_foto"] = atleta.get("foto_url", "")
    
    return {
        "mensagens": mensagens,
        "total": len(mensagens),
        "ano": ano_filtro
    }
