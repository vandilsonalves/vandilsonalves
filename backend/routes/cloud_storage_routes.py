"""
Rotas de proxy para servir arquivos armazenados na nuvem (Emergent Object Storage).
Serve como intermediário: Frontend → Backend → Cloud Storage → Response
"""

from fastapi import APIRouter, HTTPException, Response
from services.object_storage import download_file, init_storage
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cloud-files/{path:path}")
async def serve_cloud_file(path: str):
    """Proxy: serve um arquivo armazenado na nuvem."""
    try:
        data, content_type = download_file(path)
        return Response(
            content=data,
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        logger.error(f"Erro ao servir arquivo da nuvem: {path} - {e}")
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")


@router.get("/storage/health")
async def storage_health():
    """Verifica se o Object Storage está acessível."""
    try:
        key = init_storage()
        return {"status": "ok", "storage_key_set": bool(key)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
