import os
import json
import zipfile
import shutil
import logging
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from config import db
from routes.auth_routes import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

BACKUPS_DIR = "/app/backups"
UPLOADS_DIR = "/app/uploads"

# Garantir que o diretório de backups existe
os.makedirs(BACKUPS_DIR, exist_ok=True)


async def get_super_admin(current_user: dict = Depends(get_current_user)):
    """Apenas Super Admin pode acessar backups"""
    is_super = (
        current_user.get("role") == "super_admin" or
        current_user.get("tipo_admin") == "Super Admin"
    )
    if not is_super:
        raise HTTPException(status_code=403, detail="Acesso restrito ao Super Admin")
    return current_user


async def limpar_backups_antigos(max_backups: int = 4):
    """Remove backups excedentes, mantendo apenas os N mais recentes"""
    todos = await db.backups.find({}, {"_id": 0}).sort("data_criacao", -1).to_list(None)
    if len(todos) <= max_backups:
        return

    excedentes = todos[max_backups:]
    for b in excedentes:
        zip_path = b.get("caminho", os.path.join(BACKUPS_DIR, b["nome_arquivo"]))
        if os.path.exists(zip_path):
            os.remove(zip_path)
        await db.backups.delete_one({"id": b["id"]})
        logger.info(f"Backup antigo removido (retenção {max_backups}): {b['nome_arquivo']}")


async def executar_backup(tipo: str = "manual", admin_id: str = "system"):
    """
    Executa backup completo: MongoDB (JSON) + Arquivos de Upload.
    Gera um .zip no diretório /app/backups/.
    """
    backup_id = str(uuid4())[:8]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}_{backup_id}"
    backup_dir = os.path.join(BACKUPS_DIR, backup_name)
    zip_path = f"{backup_dir}.zip"

    try:
        os.makedirs(backup_dir, exist_ok=True)

        # 1. Exportar todas as collections do MongoDB como JSON
        db_dir = os.path.join(backup_dir, "database")
        os.makedirs(db_dir, exist_ok=True)

        collections = await db.list_collection_names()
        total_docs = 0
        collections_info = {}

        for col_name in collections:
            try:
                docs = await db[col_name].find({}, {"_id": 0}).to_list(None)
                col_path = os.path.join(db_dir, f"{col_name}.json")
                with open(col_path, "w", encoding="utf-8") as f:
                    json.dump(docs, f, ensure_ascii=False, default=str)
                total_docs += len(docs)
                collections_info[col_name] = len(docs)
            except Exception as e:
                logger.error(f"Erro ao exportar collection {col_name}: {e}")
                collections_info[col_name] = f"ERRO: {str(e)}"

        # 2. Copiar arquivos de upload
        uploads_backup_dir = os.path.join(backup_dir, "uploads")
        if os.path.exists(UPLOADS_DIR):
            shutil.copytree(UPLOADS_DIR, uploads_backup_dir, dirs_exist_ok=True)

        # 3. Gerar metadados do backup
        meta = {
            "backup_id": backup_id,
            "data_criacao": datetime.now(timezone.utc).isoformat(),
            "tipo": tipo,
            "admin_id": admin_id,
            "collections": collections_info,
            "total_documentos": total_docs,
            "total_collections": len(collections),
            "versao": "1.0"
        }
        with open(os.path.join(backup_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        # 4. Comprimir tudo em .zip
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_dir)
                    zipf.write(file_path, arcname)

        # 5. Remover diretório temporário (manter apenas o .zip)
        shutil.rmtree(backup_dir)

        # 6. Calcular tamanho do arquivo
        file_size = os.path.getsize(zip_path)

        # 7. Salvar registro no MongoDB (apenas metadados, NÃO o arquivo)
        registro = {
            "id": backup_id,
            "nome_arquivo": f"{backup_name}.zip",
            "caminho": zip_path,
            "data_criacao": datetime.now(timezone.utc).isoformat(),
            "tipo": tipo,
            "admin_id": admin_id,
            "tamanho_bytes": file_size,
            "total_documentos": total_docs,
            "total_collections": len(collections),
            "collections": collections_info,
            "status": "concluido"
        }
        await db.backups.insert_one(registro)

        logger.info(f"Backup {tipo} concluído: {backup_name}.zip ({file_size / 1024 / 1024:.1f} MB)")

        # 8. Retenção: manter apenas os últimos 4 backups
        await limpar_backups_antigos(max_backups=4)

        return registro

    except Exception as e:
        # Limpar em caso de erro
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir, ignore_errors=True)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        logger.error(f"Erro ao criar backup: {e}")
        raise


@router.post("/admin/backup/criar")
async def criar_backup(admin: dict = Depends(get_super_admin)):
    """Cria backup manual completo (MongoDB + uploads)"""
    try:
        registro = await executar_backup(tipo="manual", admin_id=admin["id"])
        return {
            "sucesso": True,
            "mensagem": "Backup criado com sucesso!",
            "backup": {
                "id": registro["id"],
                "nome_arquivo": registro["nome_arquivo"],
                "tamanho_mb": round(registro["tamanho_bytes"] / 1024 / 1024, 2),
                "total_documentos": registro["total_documentos"],
                "total_collections": registro["total_collections"],
                "data_criacao": registro["data_criacao"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar backup: {str(e)}")


@router.get("/admin/backup/historico")
async def listar_backups(admin: dict = Depends(get_super_admin)):
    """Lista histórico de backups realizados"""
    backups = await db.backups.find(
        {},
        {"_id": 0, "caminho": 0}
    ).sort("data_criacao", -1).to_list(50)

    # Verificar se os arquivos ainda existem no disco
    for b in backups:
        zip_path = os.path.join(BACKUPS_DIR, b["nome_arquivo"])
        b["arquivo_disponivel"] = os.path.exists(zip_path)
        b["tamanho_mb"] = round(b.get("tamanho_bytes", 0) / 1024 / 1024, 2)

    return backups


@router.get("/admin/backup/download/{backup_id}")
async def download_backup(backup_id: str, admin: dict = Depends(get_super_admin)):
    """Download de um arquivo de backup"""
    registro = await db.backups.find_one({"id": backup_id}, {"_id": 0})
    if not registro:
        raise HTTPException(status_code=404, detail="Backup não encontrado")

    zip_path = registro.get("caminho", os.path.join(BACKUPS_DIR, registro["nome_arquivo"]))
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Arquivo de backup não encontrado no disco")

    def iter_file():
        with open(zip_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    return StreamingResponse(
        iter_file(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={registro['nome_arquivo']}",
            "Content-Length": str(os.path.getsize(zip_path))
        }
    )


@router.delete("/admin/backup/{backup_id}")
async def excluir_backup(backup_id: str, admin: dict = Depends(get_super_admin)):
    """Exclui um backup (arquivo + registro)"""
    registro = await db.backups.find_one({"id": backup_id}, {"_id": 0})
    if not registro:
        raise HTTPException(status_code=404, detail="Backup não encontrado")

    # Remover arquivo do disco
    zip_path = registro.get("caminho", os.path.join(BACKUPS_DIR, registro["nome_arquivo"]))
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # Remover registro do MongoDB
    await db.backups.delete_one({"id": backup_id})

    return {"sucesso": True, "mensagem": "Backup excluído com sucesso"}


@router.get("/admin/backup/info")
async def info_backup(admin: dict = Depends(get_super_admin)):
    """Informações gerais sobre o sistema de backup"""
    total_backups = await db.backups.count_documents({})
    ultimo = await db.backups.find_one({}, {"_id": 0}, sort=[("data_criacao", -1)])

    # Tamanho total em disco
    tamanho_total = 0
    if os.path.exists(BACKUPS_DIR):
        for f in os.listdir(BACKUPS_DIR):
            fp = os.path.join(BACKUPS_DIR, f)
            if os.path.isfile(fp):
                tamanho_total += os.path.getsize(fp)

    # Tamanho dos uploads
    tamanho_uploads = 0
    if os.path.exists(UPLOADS_DIR):
        for root, dirs, files in os.walk(UPLOADS_DIR):
            for f in files:
                tamanho_uploads += os.path.getsize(os.path.join(root, f))

    # Total de collections e documentos
    collections = await db.list_collection_names()
    total_docs = 0
    for col in collections:
        total_docs += await db[col].count_documents({})

    return {
        "total_backups": total_backups,
        "ultimo_backup": ultimo,
        "tamanho_backups_mb": round(tamanho_total / 1024 / 1024, 2),
        "tamanho_uploads_mb": round(tamanho_uploads / 1024 / 1024, 2),
        "total_collections": len(collections),
        "total_documentos": total_docs,
        "agendamento": "Toda quarta-feira às 02:30h"
    }


# Endpoint de restauração via upload de arquivo
from fastapi import File, UploadFile
@router.post("/admin/backup/restaurar-upload")
async def restaurar_backup_upload(
    arquivo: UploadFile = File(...),
    admin: dict = Depends(get_super_admin),
):
    """Restaura o sistema a partir de um arquivo de backup .zip"""
    import tempfile

    if not arquivo.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um .zip gerado pelo sistema de backup")

    # Salvar arquivo temporariamente
    conteudo = await arquivo.read()
    tamanho_mb = len(conteudo) / (1024 * 1024)

    if tamanho_mb > 500:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Maximo: 500MB")

    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, arquivo.filename)

    try:
        with open(zip_path, "wb") as f:
            f.write(conteudo)

        # Extrair o zip
        extract_dir = os.path.join(tmp_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)

        # Verificar metadata.json
        metadata_path = os.path.join(extract_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=400, detail="Arquivo de backup invalido. metadata.json nao encontrado.")

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Restaurar collections do banco
        db_dir = os.path.join(extract_dir, "database")
        if not os.path.exists(db_dir):
            raise HTTPException(status_code=400, detail="Pasta 'database' nao encontrada no backup")

        collections_restauradas = 0
        docs_restaurados = 0

        for json_file in os.listdir(db_dir):
            if not json_file.endswith(".json"):
                continue

            col_name = json_file.replace(".json", "")
            json_path = os.path.join(db_dir, json_file)

            with open(json_path, "r", encoding="utf-8") as f:
                docs = json.load(f)

            if not isinstance(docs, list) or len(docs) == 0:
                continue

            # Limpar collection e reinserir dados
            await db[col_name].delete_many({})
            if docs:
                await db[col_name].insert_many(docs)
                docs_restaurados += len(docs)
                collections_restauradas += 1

        # Restaurar uploads
        uploads_dir = os.path.join(extract_dir, "uploads")
        if os.path.exists(uploads_dir):
            if os.path.exists(UPLOADS_DIR):
                shutil.rmtree(UPLOADS_DIR, ignore_errors=True)
            shutil.copytree(uploads_dir, UPLOADS_DIR, dirs_exist_ok=True)

        # Registrar restauracao
        registro = {
            "id": str(uuid4())[:8],
            "tipo": "restauracao",
            "data_criacao": datetime.now(timezone.utc).isoformat(),
            "admin_id": admin.get("id"),
            "admin_nome": admin.get("nome", "Admin"),
            "arquivo_original": arquivo.filename,
            "backup_original_id": metadata.get("backup_id", "desconhecido"),
            "backup_original_data": metadata.get("data_criacao", "desconhecido"),
            "collections_restauradas": collections_restauradas,
            "docs_restaurados": docs_restaurados,
            "tamanho_mb": round(tamanho_mb, 2),
            "status": "concluido",
        }
        await db.backups.insert_one(registro)

        logger.info(f"[RESTORE] Backup restaurado por {admin.get('nome')}: {collections_restauradas} collections, {docs_restaurados} docs")

        return {
            "sucesso": True,
            "mensagem": f"Backup restaurado com sucesso! {collections_restauradas} collections, {docs_restaurados} documentos.",
            "detalhes": {
                "collections_restauradas": collections_restauradas,
                "docs_restaurados": docs_restaurados,
                "backup_original": metadata.get("data_criacao"),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao restaurar backup: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao restaurar backup: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
