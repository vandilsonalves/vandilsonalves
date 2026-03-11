# /app/backend/scripts/corrigir_colocacoes.py
# Script para corrigir colocações inválidas e recalcular rankings

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os

# Importar serviços de cálculo de pontos
import sys
sys.path.insert(0, '/app/backend')
from services import calcular_pontos_colocacao, calcular_pontos_povao


async def corrigir_dados():
    """
    Corrige todas as colocações inválidas:
    1. Povão: zera todas as colocações (pontua apenas por distância)
    2. Profissional/Amador Normal: remove colocações > 10
    3. PCD/Cadeirante: remove colocações > 3
    """
    
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client['test_database']
    
    print("=" * 60)
    print("🔧 INICIANDO CORREÇÃO DE COLOCAÇÕES E RECÁLCULO DE RANKINGS")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().isoformat()}")
    print()
    
    # Estatísticas
    stats = {
        "povao_corrigidos": 0,
        "normal_corrigidos": 0,
        "pcd_corrigidos": 0,
        "cadeirante_corrigidos": 0,
        "rankings_recalculados": 0
    }
    
    # ==================== 1. CORRIGIR ATLETAS DO POVÃO ====================
    print("📌 [1/4] Corrigindo Ranking do Povão (zerando colocações)...")
    
    # Buscar todos os resultados de atletas Povão com colocação > 0
    povao_usuarios = await db.usuarios.find(
        {"modalidade_usuario": "povao_pace_livre"},
        {"_id": 0, "id": 1, "nome": 1}
    ).to_list(None)
    
    povao_ids = [u["id"] for u in povao_usuarios]
    
    # Corrigir resultados pendentes
    result = await db.resultados_pendentes.update_many(
        {"usuario_id": {"$in": povao_ids}, "colocacao": {"$gt": 0}},
        {"$set": {"colocacao": 0}}
    )
    stats["povao_corrigidos"] += result.modified_count
    print(f"   ✓ {result.modified_count} resultados pendentes corrigidos")
    
    # Corrigir resultados aprovados
    result = await db.resultados_aprovados.update_many(
        {"usuario_id": {"$in": povao_ids}, "colocacao": {"$gt": 0}},
        {"$set": {"colocacao": 0}}
    )
    stats["povao_corrigidos"] += result.modified_count
    print(f"   ✓ {result.modified_count} resultados aprovados corrigidos")
    
    # Corrigir corridas
    result = await db.corridas.update_many(
        {"usuario_id": {"$in": povao_ids}, "colocacao": {"$gt": 0}},
        {"$set": {"colocacao": 0}}
    )
    stats["povao_corrigidos"] += result.modified_count
    print(f"   ✓ {result.modified_count} corridas corrigidas")
    
    # ==================== 2. CORRIGIR ATLETAS NORMAL (colocação > 10) ====================
    print("\n📌 [2/4] Corrigindo Ranking Profissional/Amador Normal (removendo colocações > 10)...")
    
    normal_usuarios = await db.usuarios.find(
        {"modalidade_usuario": "profissional_amador", "categoria": "normal"},
        {"_id": 0, "id": 1, "nome": 1}
    ).to_list(None)
    
    normal_ids = [u["id"] for u in normal_usuarios]
    
    # Marcar resultados inválidos (colocação > 10) como rejeitados
    result = await db.resultados_pendentes.update_many(
        {"usuario_id": {"$in": normal_ids}, "colocacao": {"$gt": 10}},
        {"$set": {"status": "rejeitado", "motivo_rejeicao": "Colocação inválida (> 10º lugar)"}}
    )
    stats["normal_corrigidos"] += result.modified_count
    print(f"   ✓ {result.modified_count} resultados pendentes marcados como rejeitados")
    
    # Remover corridas com colocação inválida
    result = await db.corridas.delete_many(
        {"usuario_id": {"$in": normal_ids}, "colocacao": {"$gt": 10}}
    )
    stats["normal_corrigidos"] += result.deleted_count
    print(f"   ✓ {result.deleted_count} corridas inválidas removidas")
    
    # ==================== 3. CORRIGIR ATLETAS PCD (colocação > 3) ====================
    print("\n📌 [3/4] Corrigindo Atletas PCD (removendo colocações > 3)...")
    
    pcd_usuarios = await db.usuarios.find(
        {"modalidade_usuario": "profissional_amador", "categoria": "pcd"},
        {"_id": 0, "id": 1, "nome": 1}
    ).to_list(None)
    
    pcd_ids = [u["id"] for u in pcd_usuarios]
    
    result = await db.resultados_pendentes.update_many(
        {"usuario_id": {"$in": pcd_ids}, "colocacao": {"$gt": 3}},
        {"$set": {"status": "rejeitado", "motivo_rejeicao": "Colocação inválida para PCD (> 3º lugar)"}}
    )
    stats["pcd_corrigidos"] += result.modified_count
    print(f"   ✓ {result.modified_count} resultados pendentes marcados como rejeitados")
    
    result = await db.corridas.delete_many(
        {"usuario_id": {"$in": pcd_ids}, "colocacao": {"$gt": 3}}
    )
    stats["pcd_corrigidos"] += result.deleted_count
    print(f"   ✓ {result.deleted_count} corridas inválidas removidas")
    
    # ==================== 4. CORRIGIR ATLETAS CADEIRANTE (colocação > 3) ====================
    print("\n📌 [4/4] Corrigindo Atletas Cadeirante (removendo colocações > 3)...")
    
    cadeirante_usuarios = await db.usuarios.find(
        {"modalidade_usuario": "profissional_amador", "categoria": "cadeirante"},
        {"_id": 0, "id": 1, "nome": 1}
    ).to_list(None)
    
    cadeirante_ids = [u["id"] for u in cadeirante_usuarios]
    
    result = await db.resultados_pendentes.update_many(
        {"usuario_id": {"$in": cadeirante_ids}, "colocacao": {"$gt": 3}},
        {"$set": {"status": "rejeitado", "motivo_rejeicao": "Colocação inválida para Cadeirante (> 3º lugar)"}}
    )
    stats["cadeirante_corrigidos"] += result.modified_count
    print(f"   ✓ {result.modified_count} resultados pendentes marcados como rejeitados")
    
    result = await db.corridas.delete_many(
        {"usuario_id": {"$in": cadeirante_ids}, "colocacao": {"$gt": 3}}
    )
    stats["cadeirante_corrigidos"] += result.deleted_count
    print(f"   ✓ {result.deleted_count} corridas inválidas removidas")
    
    # ==================== RECALCULAR RANKINGS ====================
    print("\n" + "=" * 60)
    print("📊 RECALCULANDO RANKINGS...")
    print("=" * 60)
    
    # Recalcular ranking_anual para cada atleta Profissional/Amador
    print("\n🏆 Recalculando Ranking Anual (Profissional/Amador)...")
    
    for usuario in await db.usuarios.find(
        {"modalidade_usuario": "profissional_amador", "role": "atleta"},
        {"_id": 0}
    ).to_list(None):
        
        usuario_id = usuario["id"]
        categoria = usuario.get("categoria", "normal")
        genero = usuario.get("genero", "M")
        
        # Buscar corridas válidas do atleta
        corridas = await db.corridas.find(
            {"usuario_id": usuario_id},
            {"_id": 0}
        ).to_list(None)
        
        # Calcular pontos totais
        pontos_total = 0
        for corrida in corridas:
            colocacao = corrida.get("colocacao", 0)
            if colocacao > 0:
                pontos = calcular_pontos_colocacao(colocacao, categoria)
                pontos_total += pontos
        
        # Atualizar ranking_anual
        await db.ranking_anual.update_one(
            {"usuario_id": usuario_id, "ano": 2025},
            {"$set": {
                "pontos_total": pontos_total,
                "total_corridas": len(corridas),
                "categoria": categoria,
                "genero": genero,
                "atualizado_em": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        stats["rankings_recalculados"] += 1
    
    print(f"   ✓ {stats['rankings_recalculados']} rankings Profissional/Amador recalculados")
    
    # Recalcular ranking_povao
    print("\n🏃 Recalculando Ranking Povão (por distância)...")
    povao_recalc = 0
    
    for usuario in povao_usuarios:
        usuario_id = usuario["id"]
        
        # Buscar usuário completo
        user_data = await db.usuarios.find_one({"id": usuario_id}, {"_id": 0})
        if not user_data:
            continue
        
        genero = user_data.get("genero", "M")
        
        # Buscar corridas do atleta
        corridas = await db.corridas.find(
            {"usuario_id": usuario_id},
            {"_id": 0}
        ).to_list(None)
        
        # Calcular pontos por distância
        pontos_total = 0
        distancia_total = 0
        
        for corrida in corridas:
            distancia_str = corrida.get("distancia", "0")
            pontos = calcular_pontos_povao(distancia_str)
            pontos_total += pontos
            
            # Extrair km numérico
            try:
                km = float(str(distancia_str).upper().replace("KM", "").replace("K", "").strip())
                distancia_total += km
            except:
                pass
        
        # Atualizar ranking_povao
        await db.ranking_povao.update_one(
            {"usuario_id": usuario_id, "ano": 2025},
            {"$set": {
                "pontos_total": pontos_total,
                "total_corridas": len(corridas),
                "distancia_total": distancia_total,
                "genero": genero,
                "atualizado_em": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        povao_recalc += 1
    
    print(f"   ✓ {povao_recalc} rankings Povão recalculados")
    
    # ==================== ATUALIZAR POSIÇÕES NOS RANKINGS ====================
    print("\n📈 Atualizando posições nos rankings...")
    
    # Ranking Anual - por categoria e gênero
    for categoria in ["normal", "pcd", "cadeirante"]:
        for genero in ["M", "F"]:
            cursor = db.ranking_anual.find(
                {"categoria": categoria, "genero": genero, "ano": 2025},
                {"_id": 0}
            ).sort([("pontos_total", -1), ("total_corridas", -1)])
            
            posicao = 1
            async for ranking in cursor:
                await db.ranking_anual.update_one(
                    {"usuario_id": ranking["usuario_id"], "ano": 2025},
                    {"$set": {"ranking_categoria": posicao}}
                )
                posicao += 1
    
    print("   ✓ Posições do Ranking Anual atualizadas")
    
    # Ranking Povão - por gênero
    for genero in ["M", "F"]:
        cursor = db.ranking_povao.find(
            {"genero": genero, "ano": 2025},
            {"_id": 0}
        ).sort([("pontos_total", -1), ("total_corridas", -1), ("distancia_total", -1)])
        
        posicao = 1
        async for ranking in cursor:
            await db.ranking_povao.update_one(
                {"usuario_id": ranking["usuario_id"], "ano": 2025},
                {"$set": {"ranking_genero": posicao}}
            )
            posicao += 1
    
    print("   ✓ Posições do Ranking Povão atualizadas")
    
    # ==================== RESUMO FINAL ====================
    print("\n" + "=" * 60)
    print("✅ CORREÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"""
📊 ESTATÍSTICAS:
   • Povão - Colocações zeradas: {stats['povao_corrigidos']}
   • Normal - Registros corrigidos: {stats['normal_corrigidos']}
   • PCD - Registros corrigidos: {stats['pcd_corrigidos']}
   • Cadeirante - Registros corrigidos: {stats['cadeirante_corrigidos']}
   • Rankings recalculados: {stats['rankings_recalculados'] + povao_recalc}

📌 REGRAS APLICADAS:
   • Povão: Colocação = 0 (pontua apenas por distância)
   • Normal: Aceita apenas 1º a 10º lugar
   • PCD: Aceita apenas 1º a 3º lugar
   • Cadeirante: Aceita apenas 1º a 3º lugar
""")
    
    return stats


if __name__ == "__main__":
    asyncio.run(corrigir_dados())
