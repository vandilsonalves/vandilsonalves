"""
Serviço de Object Storage em Nuvem (Emergent)
Centraliza upload/download de arquivos para armazenamento em nuvem.
"""

import os
import uuid
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "rankingrun"

storage_key: Optional[str] = None

MIME_TYPES = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "gif": "image/gif", "webp": "image/webp", "svg": "image/svg+xml",
    "pdf": "application/pdf", "json": "application/json",
    "csv": "text/csv", "txt": "text/plain",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "mp4": "video/mp4", "mp3": "audio/mpeg",
}


def init_storage() -> str:
    """Inicializa o storage uma vez. Retorna storage_key reutilizável."""
    global storage_key
    if storage_key:
        return storage_key
    if not EMERGENT_KEY:
        raise RuntimeError("EMERGENT_LLM_KEY não configurada no .env")
    resp = requests.post(
        f"{STORAGE_URL}/init",
        json={"emergent_key": EMERGENT_KEY},
        timeout=30
    )
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    logger.info("Object Storage inicializado com sucesso")
    return storage_key


def get_content_type(filename: str) -> str:
    """Retorna o content-type baseado na extensão do arquivo."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return MIME_TYPES.get(ext, "application/octet-stream")


def upload_file(data: bytes, filename: str, pasta: str = "geral", content_type: str = None) -> dict:
    """
    Faz upload de um arquivo para o storage em nuvem.
    Retorna {"path": "...", "size": ..., "url": "..."}
    """
    key = init_storage()
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    cloud_filename = f"{uuid.uuid4().hex}.{ext}"
    cloud_path = f"{APP_NAME}/{pasta}/{cloud_filename}"

    if not content_type:
        content_type = get_content_type(filename)

    resp = requests.put(
        f"{STORAGE_URL}/objects/{cloud_path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data,
        timeout=120
    )
    resp.raise_for_status()
    result = resp.json()

    return {
        "path": result["path"],
        "size": result.get("size", len(data)),
        "content_type": content_type,
        "original_filename": filename,
        "url": f"/api/cloud-files/{result['path']}"
    }


def download_file(path: str) -> tuple:
    """
    Baixa um arquivo do storage em nuvem.
    Retorna (bytes, content_type).
    """
    key = init_storage()
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key},
        timeout=60
    )
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "application/octet-stream")
    return resp.content, content_type
