# /app/backend/routes/raio_x_routes.py
# Rotas para o RAIO-X do Atleta - Análise completa de performance

from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from config import db
from routes.auth_routes import get_current_user
import statistics

router = APIRouter()


def calcular_pace(tempo_str: str, distancia_km: float) -> Optional[float]:
    """Calcula pace em minutos por km a partir de tempo HH:MM:SS ou MM:SS"""
    if not tempo_str or distancia_km <= 0:
        return None
    try:
        partes = tempo_str.split(':')
        if len(partes) == 3:
            horas, minutos, segundos = map(int, partes)
            total_minutos = horas * 60 + minutos + segundos / 60
        elif len(partes) == 2:
            minutos, segundos = map(int, partes)
            total_minutos = minutos + segundos / 60
        else:
            return None
        return total_minutos / distancia_km
    except:
        return None


def pace_para_string(pace_minutos: float) -> str:
    """Converte pace em minutos para formato MM:SS"""
    if not pace_minutos:
        return "-"
    minutos = int(pace_minutos)
    segundos = int((pace_minutos - minutos) * 60)
    return f"{minutos}:{segundos:02d}"


def tempo_para_minutos(tempo_str: str) -> Optional[float]:
    """Converte tempo HH:MM:SS ou MM:SS para minutos"""
    if not tempo_str:
        return None
    try:
        partes = tempo_str.split(':')
        if len(partes) == 3:
            h, m, s = map(int, partes)
            return h * 60 + m + s / 60
        elif len(partes) == 2:
            m, s = map(int, partes)
            return m + s / 60
        return None
    except:
        return None


def minutos_para_tempo(minutos: float) -> str:
    """Converte minutos para formato HH:MM:SS"""
    if not minutos:
        return "-"
    horas = int(minutos // 60)
    mins = int(minutos % 60)
    segs = int((minutos * 60) % 60)
    if horas > 0:
        return f"{horas}:{mins:02d}:{segs:02d}"
    return f"{mins}:{segs:02d}"


@router.get("/raio-x/evolucao")
async def get_evolucao_atleta(
    periodo: str = Query("12_meses", description="6_meses, 12_meses, all"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna dados de evolução do atleta para gráficos.
    Inclui: distância, pace, tempo, número de provas por período.
    """
    usuario_id = current_user["id"]
    
    # Definir filtro de data
    filtro = {"usuario_id": usuario_id}
    if periodo == "6_meses":
        data_inicio = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        filtro["data"] = {"$gte": data_inicio}
    elif periodo == "12_meses":
        data_inicio = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        filtro["data"] = {"$gte": data_inicio}
    
    corridas = await db.corridas.find(filtro, {"_id": 0}).sort("data", 1).to_list(None)
    
    if not corridas:
        return {
            "tem_dados": False,
            "mensagem": "Você ainda não tem corridas registradas"
        }
    
    # Agrupar por mês
    evolucao_mensal = {}
    for c in corridas:
        data = c.get("data", "")[:7]  # YYYY-MM
        if data not in evolucao_mensal:
            evolucao_mensal[data] = {
                "mes": data,
                "distancia_total": 0,
                "tempo_total_min": 0,
                "num_provas": 0,
                "paces": []
            }
        
        distancia = c.get("distancia_km") or c.get("distancia", 0)
        if isinstance(distancia, str):
            try:
                distancia = float(distancia.replace("km", "").replace(",", ".").strip())
            except:
                distancia = 0
        
        tempo_min = tempo_para_minutos(c.get("tempo", ""))
        pace = calcular_pace(c.get("tempo", ""), distancia)
        
        evolucao_mensal[data]["distancia_total"] += distancia
        if tempo_min:
            evolucao_mensal[data]["tempo_total_min"] += tempo_min
        evolucao_mensal[data]["num_provas"] += 1
        if pace:
            evolucao_mensal[data]["paces"].append(pace)
    
    # Calcular médias
    evolucao_lista = []
    for mes, dados in sorted(evolucao_mensal.items()):
        pace_medio = statistics.mean(dados["paces"]) if dados["paces"] else None
        evolucao_lista.append({
            "mes": mes,
            "mes_formatado": datetime.strptime(mes, "%Y-%m").strftime("%b/%Y"),
            "distancia_total_km": round(dados["distancia_total"], 2),
            "tempo_total_horas": round(dados["tempo_total_min"] / 60, 2),
            "num_provas": dados["num_provas"],
            "pace_medio": pace_para_string(pace_medio) if pace_medio else "-",
            "pace_medio_valor": round(pace_medio, 2) if pace_medio else None
        })
    
    # Totais gerais
    total_distancia = sum(e["distancia_total_km"] for e in evolucao_lista)
    total_tempo = sum(e["tempo_total_horas"] for e in evolucao_lista)
    total_provas = sum(e["num_provas"] for e in evolucao_lista)
    
    return {
        "tem_dados": True,
        "periodo": periodo,
        "evolucao_mensal": evolucao_lista,
        "totais": {
            "distancia_total_km": round(total_distancia, 2),
            "tempo_total_horas": round(total_tempo, 2),
            "total_provas": total_provas,
            "media_km_por_prova": round(total_distancia / total_provas, 2) if total_provas > 0 else 0
        }
    }


@router.get("/raio-x/records")
async def get_records_pessoais(current_user: dict = Depends(get_current_user)):
    """
    Retorna os Records Pessoais (RPs) do atleta.
    Melhor pace, maior distância, melhores tempos por categoria.
    """
    usuario_id = current_user["id"]
    
    corridas = await db.corridas.find(
        {"usuario_id": usuario_id},
        {"_id": 0}
    ).to_list(None)
    
    if not corridas:
        return {"tem_dados": False, "records": {}}
    
    # Categorias de distância
    categorias = {
        "5km": {"min": 4.5, "max": 5.5, "melhor_tempo": None, "data": None, "corrida": None},
        "10km": {"min": 9.5, "max": 10.5, "melhor_tempo": None, "data": None, "corrida": None},
        "21km": {"min": 20, "max": 22, "melhor_tempo": None, "data": None, "corrida": None},
        "42km": {"min": 41, "max": 43, "melhor_tempo": None, "data": None, "corrida": None}
    }
    
    melhor_pace = {"valor": float('inf'), "data": None, "corrida": None, "distancia": 0}
    maior_distancia = {"valor": 0, "data": None, "corrida": None, "tempo": None}
    historico_rps = []
    
    for c in corridas:
        distancia = c.get("distancia_km") or c.get("distancia", 0)
        if isinstance(distancia, str):
            try:
                distancia = float(distancia.replace("km", "").replace(",", ".").strip())
            except:
                continue
        
        tempo_min = tempo_para_minutos(c.get("tempo", ""))
        pace = calcular_pace(c.get("tempo", ""), distancia)
        
        # Verificar melhor pace (mínimo 3km para contar)
        if pace and distancia >= 3 and pace < melhor_pace["valor"]:
            melhor_pace = {
                "valor": pace,
                "valor_formatado": pace_para_string(pace),
                "data": c.get("data"),
                "corrida": c.get("nome_competicao", c.get("nome", "Corrida")),
                "distancia": distancia
            }
            historico_rps.append({
                "tipo": "Melhor Pace",
                "valor": pace_para_string(pace),
                "data": c.get("data"),
                "corrida": c.get("nome_competicao", "")
            })
        
        # Verificar maior distância
        if distancia > maior_distancia["valor"]:
            maior_distancia = {
                "valor": distancia,
                "data": c.get("data"),
                "corrida": c.get("nome_competicao", c.get("nome", "Corrida")),
                "tempo": c.get("tempo")
            }
        
        # Verificar RPs por categoria
        for cat, config in categorias.items():
            if config["min"] <= distancia <= config["max"]:
                if tempo_min:
                    if config["melhor_tempo"] is None or tempo_min < config["melhor_tempo"]:
                        categorias[cat]["melhor_tempo"] = tempo_min
                        categorias[cat]["data"] = c.get("data")
                        categorias[cat]["corrida"] = c.get("nome_competicao", "")
                        historico_rps.append({
                            "tipo": f"RP {cat}",
                            "valor": c.get("tempo"),
                            "data": c.get("data"),
                            "corrida": c.get("nome_competicao", "")
                        })
    
    # Formatar categorias
    rps_categorias = {}
    for cat, config in categorias.items():
        if config["melhor_tempo"]:
            rps_categorias[cat] = {
                "tempo": minutos_para_tempo(config["melhor_tempo"]),
                "tempo_minutos": round(config["melhor_tempo"], 2),
                "data": config["data"],
                "corrida": config["corrida"],
                "pace": pace_para_string(config["melhor_tempo"] / float(cat.replace("km", "")))
            }
    
    return {
        "tem_dados": True,
        "records": {
            "melhor_pace": melhor_pace if melhor_pace["valor"] != float('inf') else None,
            "maior_distancia": maior_distancia if maior_distancia["valor"] > 0 else None,
            "por_categoria": rps_categorias
        },
        "historico_rps": sorted(historico_rps, key=lambda x: x["data"] or "", reverse=True)[:20]
    }


@router.get("/raio-x/comparativo")
async def get_comparativo_mensal(current_user: dict = Depends(get_current_user)):
    """
    Compara performance do mês atual vs mês anterior.
    Você vs Você do mês passado.
    """
    usuario_id = current_user["id"]
    
    hoje = datetime.now()
    mes_atual = hoje.strftime("%Y-%m")
    mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    
    corridas = await db.corridas.find(
        {"usuario_id": usuario_id},
        {"_id": 0}
    ).to_list(None)
    
    def calcular_metricas(corridas_mes):
        if not corridas_mes:
            return None
        
        distancia_total = 0
        tempo_total = 0
        paces = []
        
        for c in corridas_mes:
            dist = c.get("distancia_km") or c.get("distancia", 0)
            if isinstance(dist, str):
                try:
                    dist = float(dist.replace("km", "").replace(",", ".").strip())
                except:
                    continue
            
            tempo_min = tempo_para_minutos(c.get("tempo", ""))
            pace = calcular_pace(c.get("tempo", ""), dist)
            
            distancia_total += dist
            if tempo_min:
                tempo_total += tempo_min
            if pace:
                paces.append(pace)
        
        pace_medio = statistics.mean(paces) if paces else None
        
        return {
            "distancia_total_km": round(distancia_total, 2),
            "tempo_total_horas": round(tempo_total / 60, 2),
            "num_provas": len(corridas_mes),
            "pace_medio": pace_para_string(pace_medio) if pace_medio else "-",
            "pace_medio_valor": round(pace_medio, 2) if pace_medio else None
        }
    
    corridas_mes_atual = [c for c in corridas if c.get("data", "").startswith(mes_atual)]
    corridas_mes_anterior = [c for c in corridas if c.get("data", "").startswith(mes_anterior)]
    
    metricas_atual = calcular_metricas(corridas_mes_atual)
    metricas_anterior = calcular_metricas(corridas_mes_anterior)
    
    # Calcular variações
    variacoes = {}
    if metricas_atual and metricas_anterior:
        if metricas_anterior["distancia_total_km"] > 0:
            var_dist = ((metricas_atual["distancia_total_km"] - metricas_anterior["distancia_total_km"]) / metricas_anterior["distancia_total_km"]) * 100
            variacoes["distancia"] = round(var_dist, 1)
        
        if metricas_anterior["num_provas"] > 0:
            var_provas = ((metricas_atual["num_provas"] - metricas_anterior["num_provas"]) / metricas_anterior["num_provas"]) * 100
            variacoes["provas"] = round(var_provas, 1)
        
        if metricas_anterior["pace_medio_valor"] and metricas_atual["pace_medio_valor"]:
            # Para pace, menor é melhor, então invertemos
            var_pace = ((metricas_anterior["pace_medio_valor"] - metricas_atual["pace_medio_valor"]) / metricas_anterior["pace_medio_valor"]) * 100
            variacoes["pace"] = round(var_pace, 1)
    
    # Melhor performance do mês atual
    melhor_do_mes = None
    if corridas_mes_atual:
        melhor_pace_mes = float('inf')
        for c in corridas_mes_atual:
            dist = c.get("distancia_km") or c.get("distancia", 0)
            if isinstance(dist, str):
                try:
                    dist = float(dist.replace("km", "").replace(",", ".").strip())
                except:
                    continue
            pace = calcular_pace(c.get("tempo", ""), dist)
            if pace and pace < melhor_pace_mes and dist >= 3:
                melhor_pace_mes = pace
                melhor_do_mes = {
                    "corrida": c.get("nome_competicao", "Corrida"),
                    "data": c.get("data"),
                    "distancia": dist,
                    "tempo": c.get("tempo"),
                    "pace": pace_para_string(pace)
                }
    
    return {
        "mes_atual": {
            "periodo": mes_atual,
            "periodo_formatado": hoje.strftime("%B/%Y"),
            "metricas": metricas_atual
        },
        "mes_anterior": {
            "periodo": mes_anterior,
            "periodo_formatado": (hoje.replace(day=1) - timedelta(days=1)).strftime("%B/%Y"),
            "metricas": metricas_anterior
        },
        "variacoes": variacoes,
        "melhor_performance_mes": melhor_do_mes
    }


@router.get("/raio-x/previsoes")
async def get_previsoes_ia(current_user: dict = Depends(get_current_user)):
    """
    Previsões inteligentes baseadas no histórico do atleta.
    Tempo estimado para diferentes distâncias.
    """
    usuario_id = current_user["id"]
    
    corridas = await db.corridas.find(
        {"usuario_id": usuario_id},
        {"_id": 0}
    ).to_list(None)
    
    if len(corridas) < 3:
        return {
            "tem_dados": False,
            "mensagem": "Precisamos de pelo menos 3 corridas para fazer previsões"
        }
    
    # Coletar dados de pace por distância
    dados_corridas = []
    for c in corridas:
        dist = c.get("distancia_km") or c.get("distancia", 0)
        if isinstance(dist, str):
            try:
                dist = float(dist.replace("km", "").replace(",", ".").strip())
            except:
                continue
        
        pace = calcular_pace(c.get("tempo", ""), dist)
        if pace and dist >= 3:
            dados_corridas.append({"distancia": dist, "pace": pace, "data": c.get("data")})
    
    if not dados_corridas:
        return {"tem_dados": False, "mensagem": "Dados insuficientes para previsões"}
    
    # Usar últimas 10 corridas para média ponderada (mais recentes = mais peso)
    dados_recentes = sorted(dados_corridas, key=lambda x: x["data"] or "", reverse=True)[:10]
    
    # Calcular pace base (média ponderada)
    pesos = list(range(len(dados_recentes), 0, -1))
    soma_pesos = sum(pesos)
    pace_base = sum(d["pace"] * p for d, p in zip(dados_recentes, pesos)) / soma_pesos
    
    # Fator de fadiga por distância (aproximado)
    # Quanto maior a distância, maior o pace
    def prever_tempo(distancia_alvo: float) -> dict:
        # Fator de ajuste baseado na distância
        if distancia_alvo <= 5:
            fator = 0.95  # Corridas curtas são mais rápidas
        elif distancia_alvo <= 10:
            fator = 1.0
        elif distancia_alvo <= 21:
            fator = 1.05
        else:
            fator = 1.12  # Maratona é mais lenta
        
        pace_previsto = pace_base * fator
        tempo_previsto = pace_previsto * distancia_alvo
        
        return {
            "distancia": f"{int(distancia_alvo)}km",
            "tempo_previsto": minutos_para_tempo(tempo_previsto),
            "pace_previsto": pace_para_string(pace_previsto),
            "confianca": "Alta" if len(dados_recentes) >= 5 else "Média"
        }
    
    previsoes = {
        "5km": prever_tempo(5),
        "10km": prever_tempo(10),
        "21km": prever_tempo(21.1),
        "42km": prever_tempo(42.2)
    }
    
    # Probabilidade de bater RP
    prob_rp = "Baixa"
    if len(dados_recentes) >= 3:
        ultimos_3_paces = [d["pace"] for d in dados_recentes[:3]]
        if statistics.mean(ultimos_3_paces) < pace_base * 0.98:
            prob_rp = "Alta"
        elif statistics.mean(ultimos_3_paces) < pace_base:
            prob_rp = "Média"
    
    return {
        "tem_dados": True,
        "pace_base": pace_para_string(pace_base),
        "previsoes": previsoes,
        "probabilidade_rp_proxima": prob_rp,
        "corridas_analisadas": len(dados_recentes),
        "dica": "Suas últimas corridas mostram boa consistência!" if prob_rp in ["Alta", "Média"] else "Continue treinando para melhorar seu pace!"
    }


@router.get("/raio-x/score")
async def get_score_consistencia(current_user: dict = Depends(get_current_user)):
    """
    Calcula o Score de Consistência do atleta (0-100%).
    Baseado em participações no mês (máx 4 = 100%).
    """
    usuario_id = current_user["id"]
    
    hoje = datetime.now()
    mes_atual = hoje.strftime("%Y-%m")
    
    corridas = await db.corridas.find(
        {"usuario_id": usuario_id},
        {"_id": 0}
    ).to_list(None)
    
    # Corridas do mês atual
    corridas_mes = [c for c in corridas if c.get("data", "").startswith(mes_atual)]
    num_corridas_mes = len(corridas_mes)
    
    # Score de consistência: 1=25%, 2=50%, 3=75%, 4+=100%
    score_consistencia = min(num_corridas_mes * 25, 100)
    
    # Calcular score por mês dos últimos 6 meses
    historico_scores = []
    for i in range(6):
        data_ref = hoje - timedelta(days=30 * i)
        mes_ref = data_ref.strftime("%Y-%m")
        corridas_ref = len([c for c in corridas if c.get("data", "").startswith(mes_ref)])
        historico_scores.append({
            "mes": mes_ref,
            "mes_formatado": data_ref.strftime("%b/%Y"),
            "corridas": corridas_ref,
            "score": min(corridas_ref * 25, 100)
        })
    
    # Média dos últimos 6 meses
    media_score = statistics.mean([h["score"] for h in historico_scores]) if historico_scores else 0
    
    # Classificação
    if media_score >= 80:
        classificacao = "Excelente"
        emoji = "🏆"
    elif media_score >= 60:
        classificacao = "Muito Bom"
        emoji = "🥇"
    elif media_score >= 40:
        classificacao = "Bom"
        emoji = "🥈"
    elif media_score >= 20:
        classificacao = "Regular"
        emoji = "🥉"
    else:
        classificacao = "Iniciante"
        emoji = "🎯"
    
    return {
        "score_mes_atual": score_consistencia,
        "corridas_mes_atual": num_corridas_mes,
        "meta_mensal": 4,
        "media_6_meses": round(media_score, 1),
        "classificacao": classificacao,
        "emoji": emoji,
        "historico": list(reversed(historico_scores)),
        "dica": f"Faltam {max(0, 4 - num_corridas_mes)} corrida(s) para atingir 100% este mês!" if num_corridas_mes < 4 else "Parabéns! Você atingiu 100% de consistência este mês!"
    }


@router.get("/raio-x/heatmap")
async def get_heatmap_corridas(current_user: dict = Depends(get_current_user)):
    """
    Retorna dados para heatmap de corridas (dias da semana e meses).
    """
    usuario_id = current_user["id"]
    
    corridas = await db.corridas.find(
        {"usuario_id": usuario_id},
        {"_id": 0, "data": 1}
    ).to_list(None)
    
    # Contar corridas por dia da semana
    dias_semana = {"Seg": 0, "Ter": 0, "Qua": 0, "Qui": 0, "Sex": 0, "Sáb": 0, "Dom": 0}
    dias_map = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
    
    # Contar por mês
    meses = {}
    
    for c in corridas:
        data_str = c.get("data", "")
        if data_str:
            try:
                data = datetime.strptime(data_str[:10], "%Y-%m-%d")
                dia = dias_map[data.weekday()]
                dias_semana[dia] += 1
                
                mes = data.strftime("%Y-%m")
                meses[mes] = meses.get(mes, 0) + 1
            except:
                pass
    
    # Preparar dados para heatmap
    heatmap_data = []
    for mes in sorted(meses.keys()):
        heatmap_data.append({
            "mes": mes,
            "corridas": meses[mes]
        })
    
    return {
        "dias_semana": dias_semana,
        "por_mes": heatmap_data[-12:],  # Últimos 12 meses
        "dia_favorito": max(dias_semana, key=dias_semana.get) if any(dias_semana.values()) else None,
        "total_corridas": sum(dias_semana.values())
    }


@router.get("/raio-x/completo")
async def get_raio_x_completo(current_user: dict = Depends(get_current_user)):
    """
    Retorna TODOS os dados do RAIO-X em uma única chamada.
    Otimizado para carregar a página completa.
    """
    # Chamar todas as funções e consolidar
    evolucao = await get_evolucao_atleta("12_meses", current_user)
    records = await get_records_pessoais(current_user)
    comparativo = await get_comparativo_mensal(current_user)
    previsoes = await get_previsoes_ia(current_user)
    score = await get_score_consistencia(current_user)
    heatmap = await get_heatmap_corridas(current_user)
    
    # Dados do usuário
    usuario = await db.usuarios.find_one(
        {"id": current_user["id"]},
        {"_id": 0, "nome": 1, "foto_url": 1, "categoria": 1, "equipe": 1}
    )
    
    return {
        "atleta": usuario,
        "evolucao": evolucao,
        "records": records,
        "comparativo": comparativo,
        "previsoes": previsoes,
        "score": score,
        "heatmap": heatmap,
        "gerado_em": datetime.now(timezone.utc).isoformat()
    }
