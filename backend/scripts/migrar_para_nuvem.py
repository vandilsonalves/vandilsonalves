"""
Script de migração: Move arquivos existentes de /app/uploads/ para o Object Storage em nuvem.
Atualiza as URLs no MongoDB para apontar para os novos caminhos na nuvem.
"""

import asyncio
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from services.object_storage import upload_file

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

UPLOADS_DIR = "/app/uploads"
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

# Mapeamento: campo_url -> collection -> pasta na nuvem
FIELD_COLLECTION_MAP = [
    {"collection": "usuarios", "field": "foto_url", "pasta": "perfil"},
    {"collection": "feed_posts", "field": "imagem_url", "pasta": "feed"},
    {"collection": "stories", "field": "imagem_url", "pasta": "stories"},
    {"collection": "equipe_mensagens", "field": "arquivo.caminho", "pasta": "chat"},
    {"collection": "equipe_feed", "field": "arquivo.caminho", "pasta": "chat"},
    {"collection": "corridas_parceiras", "field": "imagem_url", "pasta": "corridas_parceiras"},
    {"collection": "parceiros", "field": "imagem_url", "pasta": "parceiros"},
    {"collection": "instagram_analyses", "field": "foto_url", "pasta": "inside"},
]


async def migrar():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    total_migrados = 0
    total_erros = 0

    # 1. Listar TODOS os arquivos no disco
    arquivos_disco = {}
    for root, _, files in os.walk(UPLOADS_DIR):
        for f in files:
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, UPLOADS_DIR)
            arquivos_disco[rel_path] = filepath

    logger.info(f"📂 {len(arquivos_disco)} arquivos encontrados em {UPLOADS_DIR}")

    # 2. Upload de cada arquivo para a nuvem
    cloud_url_map = {}  # old_url → new_cloud_url
    for rel_path, full_path in arquivos_disco.items():
        try:
            with open(full_path, "rb") as f:
                data = f.read()
            if len(data) == 0:
                continue

            # Determinar pasta
            parts = rel_path.split(os.sep)
            if len(parts) > 1:
                pasta = parts[0]
            else:
                pasta = "perfil"

            result = upload_file(data, os.path.basename(rel_path), pasta=pasta)
            new_url = result["url"]

            # Mapear todas as URLs possíveis que referenciam este arquivo
            old_urls = [
                f"/api/uploads/{rel_path}",
                f"/uploads/{rel_path}",
                f"/api/uploads/{os.path.basename(rel_path)}",
                f"/uploads/{os.path.basename(rel_path)}",
            ]
            for old_url in old_urls:
                cloud_url_map[old_url] = new_url

            total_migrados += 1
            logger.info(f"  ☁️ {rel_path} → nuvem ({result['size']} bytes)")
        except Exception as e:
            total_erros += 1
            logger.error(f"  ❌ {rel_path}: {e}")

    logger.info(f"\n📊 Upload: {total_migrados} migrados, {total_erros} erros")

    # 3. Atualizar URLs no MongoDB
    total_db_updates = 0
    for mapping in FIELD_COLLECTION_MAP:
        coll_name = mapping["collection"]
        field = mapping["field"]
        coll = db[coll_name]

        # Buscar documentos com URLs locais
        filter_query = {field: {"$regex": "^/(api/)?uploads/"}}
        cursor = coll.find(filter_query, {"_id": 1, field: 1})

        async for doc in cursor:
            old_url = doc
            # Navigate nested fields (e.g., "arquivo.caminho")
            for part in field.split("."):
                if isinstance(old_url, dict):
                    old_url = old_url.get(part)
                else:
                    old_url = None
                    break

            if not old_url or not isinstance(old_url, str):
                continue

            new_url = cloud_url_map.get(old_url)
            if not new_url:
                # Tentar com/sem /api prefix
                alt = old_url.replace("/api/uploads/", "/uploads/")
                new_url = cloud_url_map.get(alt)
                if not new_url:
                    alt2 = old_url.replace("/uploads/", "/api/uploads/")
                    new_url = cloud_url_map.get(alt2)

            if new_url:
                await coll.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {field: new_url}}
                )
                total_db_updates += 1

    logger.info(f"🔄 {total_db_updates} URLs atualizadas no MongoDB")
    logger.info(f"\n✅ Migração concluída! {total_migrados} arquivos na nuvem.")

    client.close()


if __name__ == "__main__":
    asyncio.run(migrar())
