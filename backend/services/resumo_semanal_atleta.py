# /app/backend/services/resumo_semanal_atleta.py
"""
Resumo Semanal para Atletas
Toda segunda-feira às 8h, envia uma notificação personalizada
para cada atleta com destaques da semana anterior.
"""

import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


def _get_db():
    from config import db
    return db


async def gerar_resumo_semanal_atletas():
    """Gera e envia resumo semanal personalizado para cada atleta"""
    db = _get_db()
    agora = datetime.now(timezone.utc)
    inicio_semana = (agora - timedelta(days=7)).isoformat()

    logger.info("Iniciando geração de resumo semanal para atletas...")

    from routes.notificacoes_routes import criar_notificacao

    atletas = await db.usuarios.find(
        {"role": "atleta"},
        {"_id": 0, "id": 1, "nome": 1, "modalidade_usuario": 1, "genero": 1, "categoria": 1, "estado": 1}
    ).to_list(None)

    if not atletas:
        logger.info("Nenhum atleta encontrado.")
        return

    enviados = 0
    erros = 0

    for atleta in atletas:
        try:
            uid = atleta["id"]
            nome = atleta.get("nome", "Atleta")
            primeiro_nome = nome.split()[0] if nome else "Atleta"
            modalidade = atleta.get("modalidade_usuario", "profissional_amador")

            # Corridas da semana
            corridas_semana = await db.corridas.find(
                {"usuario_id": uid, "data_criacao": {"$gte": inicio_semana}},
                {"_id": 0, "pontos": 1, "pontos_povao": 1, "nome_corrida": 1}
            ).to_list(None)

            num_corridas = len(corridas_semana)

            if modalidade == "povao_pace_livre":
                pontos_semana = sum(c.get("pontos_povao", 0) for c in corridas_semana)
            else:
                pontos_semana = sum(c.get("pontos", 0) for c in corridas_semana)

            # Posição no ranking
            posicao = None
            pontos_total = 0
            if modalidade == "povao_pace_livre":
                ranking_doc = await db.ranking_povao.find_one(
                    {"usuario_id": uid}, {"_id": 0, "ranking_genero": 1, "colocacao": 1, "pontos_total": 1}
                )
                if ranking_doc:
                    posicao = ranking_doc.get("colocacao") or ranking_doc.get("ranking_genero")
                    pontos_total = ranking_doc.get("pontos_total", 0)
            else:
                ranking_doc = await db.ranking_anual.find_one(
                    {"usuario_id": uid}, {"_id": 0, "ranking_categoria": 1, "ranking_genero": 1, "pontos_total": 1}
                )
                if ranking_doc:
                    posicao = ranking_doc.get("ranking_categoria") or ranking_doc.get("ranking_genero")
                    pontos_total = ranking_doc.get("pontos_total", 0)

            # Total de corridas geral do atleta
            total_corridas_geral = await db.corridas.count_documents({"usuario_id": uid})

            # Montar mensagem
            linhas = [f"Ola, {primeiro_nome}! Aqui esta seu resumo da semana:"]
            linhas.append("")

            if num_corridas > 0:
                corrida_txt = "corrida" if num_corridas == 1 else "corridas"
                linhas.append(f"Corridas na semana: {num_corridas} {corrida_txt}")
                linhas.append(f"Pontos ganhos: +{pontos_semana}")
            else:
                linhas.append("Voce nao registrou corridas esta semana. Bora correr!")

            linhas.append(f"Total de corridas: {total_corridas_geral}")
            linhas.append(f"Pontos acumulados: {pontos_total}")

            if posicao and posicao > 0:
                linhas.append(f"Posicao no ranking: #{posicao}")
            elif pontos_total > 0:
                linhas.append(f"Pontos acumulados: {pontos_total}")
            else:
                linhas.append("Submeta corridas para aparecer no ranking!")

            linhas.append("")
            linhas.append("Continue firme! Cada corrida conta.")

            mensagem = "\n".join(linhas)

            await criar_notificacao(
                usuario_id=uid,
                tipo="resumo_semanal",
                titulo="Seu Resumo Semanal",
                mensagem=mensagem,
                dados_extras={
                    "corridas_semana": num_corridas,
                    "pontos_semana": pontos_semana,
                    "posicao_ranking": posicao,
                    "pontos_total": pontos_total,
                    "total_corridas": total_corridas_geral,
                }
            )
            enviados += 1

        except Exception as e:
            erros += 1
            logger.error(f"Erro ao gerar resumo para {atleta.get('id')}: {e}")

    # Log no banco
    await db.logs_scheduler.insert_one({
        "tipo": "resumo_semanal_atletas",
        "data": agora.isoformat(),
        "total_atletas": len(atletas),
        "enviados": enviados,
        "erros": erros,
    })

    logger.info(f"Resumo semanal: {enviados}/{len(atletas)} atletas notificados, {erros} erros")
    return {"enviados": enviados, "erros": erros, "total": len(atletas)}
