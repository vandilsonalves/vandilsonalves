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
    
    # Verificar se o atleta está no período de teste (30 dias após cadastro)
    data_cadastro_str = current_user.get("data_criacao", "")
    hoje = datetime.now()
    
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
    
    # Validação para Profissional/Amador
    if modalidade_usuario == "profissional_amador":
        if categoria in ["pcd", "cadeirante"]:
            if colocacao < 1 or colocacao > 3:
                raise HTTPException(
                    status_code=400,
                    detail=f"Para categoria {categoria.upper()}, apenas colocações de 1º a 3º são válidas."
                )
        else:
            if colocacao < 1 or colocacao > 10:
                raise HTTPException(
                    status_code=400,
                    detail="Para categoria Normal, apenas colocações de 1º a 10º são válidas."
                )
    
    # Salvar foto (opcional)
    foto_url = ""
    if foto_podio and foto_podio.filename:
        foto_filename = f"{uuid.uuid4()}_{foto_podio.filename}"
        foto_path = Path("/app/uploads") / foto_filename
        foto_path.parent.mkdir(exist_ok=True)
        
        with foto_path.open("wb") as f:
            f.write(await foto_podio.read())
        
        foto_url = f"/uploads/{foto_filename}"
    
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
    
    doc = resultado.model_dump()
    doc["modalidade"] = modalidade_usuario
    await db.resultados_pendentes.insert_one(doc)
    
    return {
        "message": "Resultado submetido com sucesso! Aguarde aprovação do administrador.",
        "id": resultado.id
    }
