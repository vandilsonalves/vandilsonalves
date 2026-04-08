"""
Script v2: Enriquecer Regulamento com referências legais.
Extrai texto exato do MongoDB para substituições precisas.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def enriquecer_regulamento_v2():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]

    reg = await db.configuracoes.find_one({"tipo": "regulamento"})
    if not reg:
        print("Regulamento não encontrado!")
        return

    conteudo = reg.get("conteudo", "")
    lines = conteudo.split("\n")
    
    # Debug: print line-by-line around key markers to find exact text
    markers = {
        "### 2. Defini": [],
        "### 6. Momento": [],
        "### 13. Responsabilidade": [],
        "### 14. Isenção": [],
        "### 15. Direito de Moderação": [],
        "### 22. Cláusula de Foro": [],
        "### 19. Cláusula de Liberdade": [],
        "## 1. Propósito da Plataforma": [],
        "Esta política tem como objetivo": [],
    }
    
    for i, line in enumerate(lines):
        for marker in markers:
            if marker in line:
                markers[marker].append(i)
                # Print context: 3 lines before
                start = max(0, i-3)
                print(f"\n=== FOUND '{marker}' at line {i} ===")
                for j in range(start, min(len(lines), i+3)):
                    print(f"  L{j}: |{repr(lines[j])}|")

asyncio.run(enriquecer_regulamento_v2())
