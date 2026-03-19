# /app/backend/routes/resultados_routes.py
# Módulo de Submissão de Resultados

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from datetime import datetime, timezone
from pathlib import Path
import uuid

from config import db
from models import ResultadoPendente
from routes.auth_routes import get_current_user

router = APIRouter(tags=["Resultados"])


# ==================== SUBMISSÃO DE RESULTADOS ====================

@router.post("/resultados/submeter")
async def submeter_resultado(
    nome_competicao: str = Form(...),
    colocacao: int = Form(0),  # Opcional para Povão (default=0)
    cidade_competicao: str = Form(...),
    estado_competicao: str = Form(...),
    data_competicao: str = Form(...),
    link_resultado: str = Form(...),
    tempo: str = Form(...),  # Obrigatório para TODOS
    distancia: str = Form(...),
    foto_podio: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Atleta submete resultado para aprovação"""
    
    hoje = datetime.now()
    
    # ==================== VALIDAÇÃO DE DATA DA COMPETIÇÃO (30 DIAS) ====================
    try:
        # Tentar parsear a data da competição
        data_competicao_dt = datetime.strptime(data_competicao, "%Y-%m-%d")
        dias_desde_competicao = (hoje - data_competicao_dt).days
        
        if dias_desde_competicao > 30:
            raise HTTPException(
                status_code=400,
                detail=f"Não é permitido submeter resultados de corridas com mais de 30 dias. A corrida foi há {dias_desde_competicao} dias."
            )
        
        if dias_desde_competicao < 0:
            raise HTTPException(
                status_code=400,
                detail="A data da competição não pode ser uma data futura."
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use o formato YYYY-MM-DD."
        )
    
    # ==================== VALIDAÇÃO DE TEMPO ====================
    # Tempo é obrigatório para TODOS - validar formato HH:MM:SS
    if not tempo or tempo == "00:00:00":
        raise HTTPException(
            status_code=400,
            detail="O tempo é obrigatório. Informe seu tempo no formato HH:MM:SS."
        )
    
    # Validar formato do tempo
    import re
    tempo_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    if not tempo_pattern.match(tempo):
        raise HTTPException(
            status_code=400,
            detail="Formato de tempo inválido. Use o formato HH:MM:SS (ex: 01:30:45)."
        )
    
    # ==================== VALIDAÇÃO DE PERÍODO DE TESTE/AUTORIZAÇÃO ====================
    data_cadastro_str = current_user.get("data_criacao", "")
    
    # Verificar se tem autorização ativa
    autorizacao = await db.autorizacoes.find_one({"atleta_id": current_user["id"], "status": "ativa"}, {"_id": 0})
    
    em_periodo_teste = False
    autorizado = False
    
    if autorizacao:
        data_expiracao = datetime.fromisoformat(autorizacao["data_expiracao"].replace("Z", "+00:00").replace("+00:00", ""))
        if hoje <= data_expiracao:
            autorizado = True
    
    if data_cadastro_str:
        try:
            if "T" in data_cadastro_str:
                data_cadastro = datetime.fromisoformat(data_cadastro_str.replace("Z", "+00:00").replace("+00:00", ""))
            else:
                data_cadastro = datetime.strptime(data_cadastro_str[:10], "%Y-%m-%d")
            
            dias_desde_cadastro = (hoje - data_cadastro).days
            em_periodo_teste = dias_desde_cadastro <= 30
        except:
            em_periodo_teste = True
    else:
        em_periodo_teste = True
    
    if not em_periodo_teste and not autorizado:
        raise HTTPException(
            status_code=403,
            detail="Seu período de teste de 30 dias expirou. Entre em contato com a administração."
        )
    
    modalidade_usuario = current_user.get("modalidade_usuario", "profissional_amador")
    categoria = current_user.get("categoria", "normal")
    
    # ==================== VALIDAÇÃO DE COLOCAÇÃO POR MODALIDADE ====================
    
    # POVÃO - Pace Livre: NÃO ACEITA colocação, apenas distância
    if modalidade_usuario == "povao_pace_livre":
        # Forçar colocação = 0 para Povão (ignora qualquer valor enviado)
        colocacao = 0
        # Povão pontua APENAS por distância, colocação é irrelevante
    
    # PROFISSIONAL/AMADOR: Validação por categoria
    elif modalidade_usuario == "profissional_amador":
        # PCD e CADEIRANTE: apenas 1º a 3º lugar
        if categoria in ["pcd", "cadeirante"]:
            if colocacao < 1 or colocacao > 3:
                raise HTTPException(
                    status_code=400,
                    detail=f"Atletas {categoria.upper()} só podem registrar colocações de 1º a 3º lugar. Colocação informada: {colocacao}º"
                )
        # NORMAL (Masculino/Feminino): apenas 1º a 10º lugar
        else:
            if colocacao < 1 or colocacao > 10:
                raise HTTPException(
                    status_code=400,
                    detail=f"Atletas Profissional/Amador só podem registrar colocações de 1º a 10º lugar. Colocação informada: {colocacao}º"
                )
    
    # Salvar foto (opcional)
    foto_url = ""
    if foto_podio and foto_podio.filename:
        foto_filename = f"{uuid.uuid4()}_{foto_podio.filename}"
        foto_path = Path("/app/uploads") / foto_filename
        foto_path.parent.mkdir(exist_ok=True)
        
        with foto_path.open("wb") as f:
            f.write(await foto_podio.read())
        
        foto_url = f"/api/uploads/{foto_filename}"
    
    resultado = ResultadoPendente(
        usuario_id=current_user["id"],
        nome_competicao=nome_competicao,
        colocacao=colocacao if modalidade_usuario == "profissional_amador" else 0,
        cidade_competicao=cidade_competicao,
        estado_competicao=estado_competicao,
        data_competicao=data_competicao,
        link_resultado=link_resultado,
        tempo=tempo,  # Tempo obrigatório para TODOS
        distancia=distancia,
        foto_podio_url=foto_url,
        status="pendente"
    )
    
    doc = resultado.model_dump()
    doc["modalidade"] = modalidade_usuario
    await db.resultados_pendentes.insert_one(doc)
    
    return {
        "message": "Resultado submetido com sucesso! Aguarde aprovação do administrador.",
        "id": resultado.id
    }
