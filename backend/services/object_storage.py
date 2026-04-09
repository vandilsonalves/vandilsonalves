"""
Serviço de Object Storage em Nuvem (Emergent)
Centraliza upload/download de arquivos para armazenamento em nuvem.
Inclui compressão automática de imagens (max 1200px, qualidade 80%).
"""

import os
import io
import uuid
import logging
import requests
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "rankingrun"

storage_key: Optional[str] = None

MAX_DIMENSION = 1200
JPEG_QUALITY = 80

MIME_TYPES = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "gif": "image/gif", "webp": "image/webp", "svg": "image/svg+xml",
    "pdf": "application/pdf", "json": "application/json",
    "csv": "text/csv", "txt": "text/plain",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "mp4": "video/mp4", "mp3": "audio/mpeg",
}

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


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


def compress_image(data: bytes, ext: str) -> tuple:
    """
    Comprime imagem: redimensiona para max 1200px e salva com qualidade 80%.
    Retorna (bytes_comprimidos, extensao_final).
    GIFs e SVGs não são comprimidos.
    """
    try:
        img = Image.open(io.BytesIO(data))

        # Converter RGBA para RGB (JPEG não suporta alpha)
        if img.mode in ("RGBA", "P") and ext in ("jpg", "jpeg"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Redimensionar se maior que MAX_DIMENSION
        w, h = img.size
        if w > MAX_DIMENSION or h > MAX_DIMENSION:
            ratio = min(MAX_DIMENSION / w, MAX_DIMENSION / h)
            new_size = (int(w * ratio), int(h * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            logger.info(f"Imagem redimensionada: {w}x{h} → {new_size[0]}x{new_size[1]}")

        # Salvar comprimida
        buf = io.BytesIO()
        if ext == "png":
            img.save(buf, format="PNG", optimize=True)
        elif ext == "webp":
            img.save(buf, format="WEBP", quality=JPEG_QUALITY)
        else:
            img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            ext = "jpg"

        compressed = buf.getvalue()
        saved = len(data) - len(compressed)
        if saved > 0:
            pct = (saved / len(data)) * 100
            logger.info(f"Imagem comprimida: {len(data):,}B → {len(compressed):,}B ({pct:.0f}% economia)")
        return compressed, ext
    except Exception as e:
        logger.warning(f"Compressão falhou (enviando original): {e}")
        return data, ext


def upload_file(data: bytes, filename: str, pasta: str = "geral", content_type: str = None) -> dict:
    """
    Faz upload de um arquivo para o storage em nuvem.
    Imagens são automaticamente comprimidas (max 1200px, qualidade 80%).
    Retorna {"path": "...", "size": ..., "url": "..."}
    """
    key = init_storage()
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"

    # Compressão automática de imagens
    if ext in IMAGE_EXTENSIONS:
        data, ext = compress_image(data, ext)

    cloud_filename = f"{uuid.uuid4().hex}.{ext}"
    cloud_path = f"{APP_NAME}/{pasta}/{cloud_filename}"

    if not content_type:
        content_type = get_content_type(f"file.{ext}")

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
