# /app/backend/routes/liga_assessorias_routes.py
# Liga de Assessorias - ROE-RR

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime
import urllib.parse

from config import db
from routes.auth_routes import get_current_user
from routes.assessorias_routes import get_ranking_assessorias

router = APIRouter(prefix="/liga-assessorias", tags=["Liga Assessorias"])


@router.get("/estados")
async def get_estados_com_assessorias():
    """Lista estados que têm assessorias cadastradas"""
    pipeline = [
        {"$match": {"role": "atleta", "equipe": {"$nin": ["", None], "$exists": True}}},
        {"$group": {"_id": "$estado"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [e["_id"] for e in result]


@router.get("/cidades")
async def get_cidades_com_assessorias(estado: str = None):
    """Lista cidades que têm assessorias cadastradas"""
    match_filter = {"role": "atleta", "equipe": {"$nin": ["", None], "$exists": True}}
    if estado:
        match_filter["estado"] = estado
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {"_id": "$cidade"}},
        {"$match": {"_id": {"$nin": [None, ""]}}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.usuarios.aggregate(pipeline).to_list(None)
    return [c["_id"] for c in result]


@router.get("/comparacao-mensal/{nome_equipe}")
async def get_comparacao_mensal_assessoria(nome_equipe: str):
    """
    Retorna comparação de desempenho entre mês atual e mês anterior
    Para uso no Dashboard do Dono de Assessoria
    """
    nome_decoded = urllib.parse.unquote(nome_equipe)
    
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    # Calcular mês anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual
    
    # Formatação de datas
    inicio_mes_atual = f"{ano_atual}-{mes_atual:02d}-01"
    inicio_mes_anterior = f"{ano_anterior}-{mes_anterior:02d}-01"
    fim_mes_anterior = inicio_mes_atual
    
    # Próximo mês para fim do mês atual
    if mes_atual == 12:
        fim_mes_atual = f"{ano_atual + 1}-01-01"
    else:
        fim_mes_atual = f"{ano_atual}-{mes_atual + 1:02d}-01"
    
    # Buscar atletas da equipe
    atletas = await db.usuarios.find(
        {"role": "atleta", "equipe": nome_decoded},
        {"_id": 0, "id": 1, "created_at": 1}
    ).to_list(None)
    
    if not atletas:
        raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    atletas_ids = [a["id"] for a in atletas]
    
    # Resultados do mês atual
    resultados_mes_atual = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_atual, "$lt": fim_mes_atual}
    })
    
    # Resultados do mês anterior
    resultados_mes_anterior = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_anterior, "$lt": fim_mes_anterior}
    })
    
    # Novos atletas no mês atual
    novos_atletas_atual = sum(1 for a in atletas 
        if a.get("created_at", "").startswith(f"{ano_atual}-{mes_atual:02d}"))
    
    # Novos atletas no mês anterior
    novos_atletas_anterior = sum(1 for a in atletas 
        if a.get("created_at", "").startswith(f"{ano_anterior}-{mes_anterior:02d}"))
    
    # Buscar ranking do mês atual
    ranking_atual_data = await get_ranking_assessorias(tipo="nacional", mes=mes_atual)
    posicao_atual = next(
        (e["posicao"] for e in ranking_atual_data["ranking"] if e["nome"] == nome_decoded),
        None
    )
    
    # Buscar ranking do mês anterior
    ranking_anterior_data = await get_ranking_assessorias(tipo="nacional", mes=mes_anterior)
    posicao_anterior = next(
        (e["posicao"] for e in ranking_anterior_data["ranking"] if e["nome"] == nome_decoded),
        None
    )
    
    # Calcular pontos do mês atual e anterior
    corridas_atual = await db.corridas.find({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_atual, "$lt": fim_mes_atual}
    }).to_list(None)
    
    corridas_anterior = await db.corridas.find({
        "usuario_id": {"$in": atletas_ids},
        "data": {"$gte": inicio_mes_anterior, "$lt": fim_mes_anterior}
    }).to_list(None)
    
    def calcular_pontos(corridas_lista):
        pontos = 0
        for c in corridas_lista:
            pontos += 1.0  # Por resultado
            colocacao = c.get("colocacao", 0)
            modalidade = c.get("modalidade", "profissional_amador")
            if modalidade == "profissional_amador" and colocacao > 0:
                if colocacao == 1:
                    pontos += 1.0
                elif 2 <= colocacao <= 5:
                    pontos += 0.5
        return round(pontos, 1)
    
    pontos_atual = calcular_pontos(corridas_atual)
    pontos_anterior = calcular_pontos(corridas_anterior)
    
    # Nomes dos meses
    meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    def calc_variacao(atual, anterior):
        if anterior == 0:
            return 100 if atual > 0 else 0
        return round(((atual - anterior) / anterior) * 100, 1)
    
    return {
        "equipe": nome_decoded,
        "mes_atual": {
            "nome": meses_nomes[mes_atual - 1],
            "numero": mes_atual,
            "ano": ano_atual,
            "resultados": resultados_mes_atual,
            "novos_atletas": novos_atletas_atual,
            "pontos": pontos_atual,
            "posicao_ranking": posicao_atual
        },
        "mes_anterior": {
            "nome": meses_nomes[mes_anterior - 1],
            "numero": mes_anterior,
            "ano": ano_anterior,
            "resultados": resultados_mes_anterior,
            "novos_atletas": novos_atletas_anterior,
            "pontos": pontos_anterior,
            "posicao_ranking": posicao_anterior
        },
        "variacoes": {
            "resultados": calc_variacao(resultados_mes_atual, resultados_mes_anterior),
            "novos_atletas": calc_variacao(novos_atletas_atual, novos_atletas_anterior),
            "pontos": calc_variacao(pontos_atual, pontos_anterior),
            "posicao": (posicao_anterior - posicao_atual) if posicao_atual and posicao_anterior else 0
        }
    }



@router.get("/graficos-avancados/{nome_equipe}")
async def get_graficos_avancados(nome_equipe: str, current_user: dict = Depends(get_current_user)):
    """
    Retorna dados para gráficos avançados do Dashboard do Dono
    Inclui: distribuição por gênero, faixa etária, distâncias, ranking histórico, etc.
    """
    import urllib.parse
    from datetime import datetime, timedelta
    
    nome_decoded = urllib.parse.unquote(nome_equipe)
    
    # Verificar permissão
    if current_user.get("role") not in ["admin", "super_admin", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if current_user.get("role") == "dono_assessoria" and current_user.get("equipe") != nome_decoded:
        raise HTTPException(status_code=403, detail="Você só pode ver dados da sua assessoria")
    
    # Buscar atletas da equipe
    atletas = await db.usuarios.find(
        {"equipe": nome_decoded, "role": "atleta"},
        {"_id": 0, "id": 1, "nome": 1, "genero": 1, "categoria": 1, "faixa_etaria": 1, 
         "cidade": 1, "estado": 1, "pontos_total": 1, "total_corridas": 1, "created_at": 1}
    ).to_list(None)
    
    if not atletas:
        raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    atletas_ids = [a["id"] for a in atletas]
    
    # 1. Distribuição por Gênero
    genero_count = {"Masculino": 0, "Feminino": 0}
    for a in atletas:
        g = a.get("genero", "M")
        if g == "M":
            genero_count["Masculino"] += 1
        else:
            genero_count["Feminino"] += 1
    
    grafico_genero = [
        {"name": k, "value": v, "fill": "#3B82F6" if k == "Masculino" else "#EC4899"}
        for k, v in genero_count.items() if v > 0
    ]
    
    # 2. Distribuição por Faixa Etária
    faixa_count = {}
    for a in atletas:
        faixa = a.get("faixa_etaria", "N/A") or "N/A"
        faixa_count[faixa] = faixa_count.get(faixa, 0) + 1
    
    grafico_faixa_etaria = [
        {"faixa": k, "atletas": v}
        for k, v in sorted(faixa_count.items())
    ]
    
    # 3. Distribuição por Categoria
    categoria_count = {}
    for a in atletas:
        cat = a.get("categoria", "normal") or "normal"
        categoria_count[cat] = categoria_count.get(cat, 0) + 1
    
    cores_categoria = {
        "normal": "#10B981",
        "pcd": "#F59E0B", 
        "cadeirante": "#8B5CF6",
        "povao": "#EF4444"
    }
    
    grafico_categoria = [
        {"name": k.upper(), "value": v, "fill": cores_categoria.get(k, "#6B7280")}
        for k, v in categoria_count.items() if v > 0
    ]
    
    # 4. Resultados por Mês (últimos 6 meses)
    agora = datetime.now()
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    resultados_por_mes = []
    
    for i in range(5, -1, -1):
        mes_data = agora - timedelta(days=30 * i)
        mes_num = mes_data.month
        ano_num = mes_data.year
        
        inicio = f"{ano_num}-{mes_num:02d}-01"
        if mes_num == 12:
            fim = f"{ano_num + 1}-01-01"
        else:
            fim = f"{ano_num}-{mes_num + 1:02d}-01"
        
        count = await db.corridas.count_documents({
            "usuario_id": {"$in": atletas_ids},
            "data": {"$gte": inicio, "$lt": fim}
        })
        
        resultados_por_mes.append({
            "mes": meses_nomes[mes_num - 1],
            "resultados": count
        })
    
    # 5. Distâncias mais corridas
    distancias = await db.corridas.find(
        {"usuario_id": {"$in": atletas_ids}},
        {"_id": 0, "distancia": 1}
    ).to_list(None)
    
    distancia_count = {}
    for d in distancias:
        dist = d.get("distancia", "N/A") or "N/A"
        distancia_count[dist] = distancia_count.get(dist, 0) + 1
    
    grafico_distancias = sorted(
        [{"distancia": k, "corridas": v} for k, v in distancia_count.items()],
        key=lambda x: x["corridas"],
        reverse=True
    )[:10]
    
    # 6. Evolução de Atletas (novos cadastros por mês)
    evolucao_atletas = []
    for i in range(5, -1, -1):
        mes_data = agora - timedelta(days=30 * i)
        mes_num = mes_data.month
        ano_num = mes_data.year
        prefixo = f"{ano_num}-{mes_num:02d}"
        
        novos = sum(1 for a in atletas if a.get("created_at", "").startswith(prefixo))
        evolucao_atletas.append({
            "mes": meses_nomes[mes_num - 1],
            "novos_atletas": novos
        })
    
    # 7. Top 10 Atletas por Pontos
    top_atletas = sorted(atletas, key=lambda x: x.get("pontos_total", 0), reverse=True)[:10]
    ranking_interno = [
        {
            "posicao": i + 1,
            "nome": a["nome"],
            "pontos": a.get("pontos_total", 0),
            "corridas": a.get("total_corridas", 0)
        }
        for i, a in enumerate(top_atletas)
    ]
    
    # 8. Distribuição por Estado (se tiver atletas de vários estados)
    estado_count = {}
    for a in atletas:
        est = a.get("estado", "N/A") or "N/A"
        estado_count[est] = estado_count.get(est, 0) + 1
    
    grafico_estados = [
        {"estado": k, "atletas": v}
        for k, v in sorted(estado_count.items(), key=lambda x: x[1], reverse=True)
    ][:10]
    
    # 9. Estatísticas de Performance
    total_atletas = len(atletas)
    total_pontos = sum(a.get("pontos_total", 0) for a in atletas)
    total_corridas = sum(a.get("total_corridas", 0) for a in atletas)
    
    # Buscar podiums
    podiums = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "colocacao": {"$lte": 3, "$gte": 1}
    })
    
    vitorias = await db.corridas.count_documents({
        "usuario_id": {"$in": atletas_ids},
        "colocacao": 1
    })
    
    estatisticas = {
        "total_atletas": total_atletas,
        "total_pontos": total_pontos,
        "total_corridas": total_corridas,
        "total_podiums": podiums,
        "total_vitorias": vitorias,
        "media_pontos_atleta": round(total_pontos / max(1, total_atletas), 1),
        "media_corridas_atleta": round(total_corridas / max(1, total_atletas), 1),
        "taxa_podio": round((podiums / max(1, total_corridas)) * 100, 1) if total_corridas > 0 else 0
    }
    
    return {
        "equipe": nome_decoded,
        "grafico_genero": grafico_genero,
        "grafico_faixa_etaria": grafico_faixa_etaria,
        "grafico_categoria": grafico_categoria,
        "resultados_por_mes": resultados_por_mes,
        "grafico_distancias": grafico_distancias,
        "evolucao_atletas": evolucao_atletas,
        "ranking_interno": ranking_interno,
        "grafico_estados": grafico_estados,
        "estatisticas": estatisticas
    }



@router.get("/exportar-dados/{nome_equipe}")
async def exportar_dados_assessoria(
    nome_equipe: str,
    formato: str = Query("csv", enum=["csv", "json", "xlsx", "pdf"]),
    current_user: dict = Depends(get_current_user)
):
    """
    Exporta dados da assessoria em CSV, JSON, Excel (XLSX) ou PDF
    Inclui: lista de atletas, estatísticas, resultados por mês
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv
    import json
    
    nome_decoded = urllib.parse.unquote(nome_equipe)
    
    # Verificar permissão
    if current_user.get("role") not in ["admin", "super_admin", "dono_assessoria"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if current_user.get("role") == "dono_assessoria" and current_user.get("equipe") != nome_decoded:
        raise HTTPException(status_code=403, detail="Você só pode exportar dados da sua assessoria")
    
    # Buscar atletas da equipe
    atletas = await db.usuarios.find(
        {"equipe": nome_decoded, "role": "atleta"},
        {"_id": 0, "id": 1, "nome": 1, "email": 1, "genero": 1, "categoria": 1, 
         "faixa_etaria": 1, "cidade": 1, "estado": 1, "pontos_total": 1, 
         "total_corridas": 1, "created_at": 1}
    ).to_list(None)
    
    if not atletas:
        raise HTTPException(status_code=404, detail="Assessoria não encontrada")
    
    atletas_ids = [a["id"] for a in atletas]
    
    # Buscar corridas dos atletas
    corridas = await db.corridas.find(
        {"usuario_id": {"$in": atletas_ids}},
        {"_id": 0, "usuario_id": 1, "nome_corrida": 1, "data": 1, "distancia": 1, 
         "colocacao": 1, "pontos": 1, "modalidade": 1}
    ).to_list(None)
    
    # Mapear nome do atleta para cada corrida
    atletas_map = {a["id"]: a["nome"] for a in atletas}
    for c in corridas:
        c["atleta_nome"] = atletas_map.get(c.get("usuario_id"), "N/A")
    
    # Calcular estatísticas
    total_atletas = len(atletas)
    total_corridas = len(corridas)
    total_pontos = sum(a.get("pontos_total", 0) for a in atletas)
    total_podios = sum(1 for c in corridas if c.get("colocacao", 99) <= 3 and c.get("colocacao", 0) >= 1)
    total_vitorias = sum(1 for c in corridas if c.get("colocacao") == 1)
    
    estatisticas = {
        "total_atletas": total_atletas,
        "total_corridas": total_corridas,
        "total_pontos": total_pontos,
        "total_podios": total_podios,
        "total_vitorias": total_vitorias,
        "media_pontos_atleta": round(total_pontos / max(1, total_atletas), 1),
        "media_corridas_atleta": round(total_corridas / max(1, total_atletas), 1)
    }
    
    if formato == "json":
        dados = {
            "equipe": nome_decoded,
            "data_exportacao": datetime.now().isoformat(),
            "estatisticas": estatisticas,
            "atletas": atletas,
            "corridas": corridas
        }
        
        return StreamingResponse(
            io.BytesIO(json.dumps(dados, ensure_ascii=False, indent=2).encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=assessoria_{nome_decoded.replace(' ', '_')}.json"}
        )
    
    elif formato == "xlsx":
        # Exportar para Excel usando xlsxwriter
        import xlsxwriter
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Formatos
        title_format = workbook.add_format({
            'bold': True, 'font_size': 16, 'font_color': '#1F2937', 
            'align': 'center', 'valign': 'vcenter'
        })
        header_format = workbook.add_format({
            'bold': True, 'font_size': 11, 'font_color': 'white', 
            'bg_color': '#F59E0B', 'border': 1, 'align': 'center'
        })
        cell_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'align': 'left'
        })
        number_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'align': 'center', 'num_format': '#,##0'
        })
        stat_label_format = workbook.add_format({
            'bold': True, 'font_size': 11, 'bg_color': '#E5E7EB', 'border': 1
        })
        stat_value_format = workbook.add_format({
            'font_size': 11, 'border': 1, 'num_format': '#,##0'
        })
        
        # === ABA 1: Resumo ===
        ws_resumo = workbook.add_worksheet('Resumo')
        ws_resumo.set_column('A:A', 25)
        ws_resumo.set_column('B:B', 20)
        
        ws_resumo.merge_range('A1:B1', f'Relatório - {nome_decoded}', title_format)
        ws_resumo.write('A3', 'Data de Exportação:', stat_label_format)
        ws_resumo.write('B3', datetime.now().strftime('%d/%m/%Y %H:%M'), cell_format)
        
        ws_resumo.write('A5', 'Total de Atletas:', stat_label_format)
        ws_resumo.write('B5', total_atletas, stat_value_format)
        ws_resumo.write('A6', 'Total de Corridas:', stat_label_format)
        ws_resumo.write('B6', total_corridas, stat_value_format)
        ws_resumo.write('A7', 'Total de Pontos:', stat_label_format)
        ws_resumo.write('B7', total_pontos, stat_value_format)
        ws_resumo.write('A8', 'Total de Pódios:', stat_label_format)
        ws_resumo.write('B8', total_podios, stat_value_format)
        ws_resumo.write('A9', 'Total de Vitórias:', stat_label_format)
        ws_resumo.write('B9', total_vitorias, stat_value_format)
        ws_resumo.write('A10', 'Média Pontos/Atleta:', stat_label_format)
        ws_resumo.write('B10', estatisticas["media_pontos_atleta"], stat_value_format)
        ws_resumo.write('A11', 'Média Corridas/Atleta:', stat_label_format)
        ws_resumo.write('B11', estatisticas["media_corridas_atleta"], stat_value_format)
        
        # === ABA 2: Atletas ===
        ws_atletas = workbook.add_worksheet('Atletas')
        headers_atletas = ['Nome', 'Email', 'Gênero', 'Categoria', 'Faixa Etária', 'Cidade', 'Estado', 'Pontos', 'Corridas', 'Data Cadastro']
        col_widths = [30, 35, 12, 12, 15, 20, 8, 10, 10, 15]
        
        for col, (header, width) in enumerate(zip(headers_atletas, col_widths)):
            ws_atletas.set_column(col, col, width)
            ws_atletas.write(0, col, header, header_format)
        
        for row, a in enumerate(sorted(atletas, key=lambda x: x.get("pontos_total", 0), reverse=True), 1):
            ws_atletas.write(row, 0, a.get("nome", ""), cell_format)
            ws_atletas.write(row, 1, a.get("email", ""), cell_format)
            ws_atletas.write(row, 2, "Masculino" if a.get("genero") == "M" else "Feminino", cell_format)
            ws_atletas.write(row, 3, (a.get("categoria") or "").upper(), cell_format)
            ws_atletas.write(row, 4, a.get("faixa_etaria", ""), cell_format)
            ws_atletas.write(row, 5, a.get("cidade", ""), cell_format)
            ws_atletas.write(row, 6, a.get("estado", ""), cell_format)
            ws_atletas.write(row, 7, a.get("pontos_total", 0), number_format)
            ws_atletas.write(row, 8, a.get("total_corridas", 0), number_format)
            ws_atletas.write(row, 9, (a.get("created_at", "") or "")[:10], cell_format)
        
        # === ABA 3: Corridas ===
        ws_corridas = workbook.add_worksheet('Corridas')
        headers_corridas = ['Atleta', 'Corrida', 'Data', 'Distância', 'Colocação', 'Pontos', 'Modalidade']
        col_widths_c = [25, 40, 12, 12, 12, 10, 20]
        
        for col, (header, width) in enumerate(zip(headers_corridas, col_widths_c)):
            ws_corridas.set_column(col, col, width)
            ws_corridas.write(0, col, header, header_format)
        
        for row, c in enumerate(sorted(corridas, key=lambda x: x.get("data", ""), reverse=True), 1):
            ws_corridas.write(row, 0, c.get("atleta_nome", ""), cell_format)
            ws_corridas.write(row, 1, c.get("nome_corrida", ""), cell_format)
            ws_corridas.write(row, 2, c.get("data", ""), cell_format)
            ws_corridas.write(row, 3, c.get("distancia", ""), cell_format)
            ws_corridas.write(row, 4, c.get("colocacao", ""), number_format)
            ws_corridas.write(row, 5, c.get("pontos", 0), number_format)
            ws_corridas.write(row, 6, c.get("modalidade", ""), cell_format)
        
        workbook.close()
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=assessoria_{nome_decoded.replace(' ', '_')}.xlsx"}
        )
    
    elif formato == "pdf":
        # Exportar para PDF usando reportlab
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(A4), 
                               rightMargin=1*cm, leftMargin=1*cm,
                               topMargin=1*cm, bottomMargin=1*cm)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'],
            fontSize=18, alignment=TA_CENTER, spaceAfter=20,
            textColor=colors.HexColor('#1F2937')
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle', parent=styles['Heading2'],
            fontSize=14, alignment=TA_LEFT, spaceAfter=10, spaceBefore=15,
            textColor=colors.HexColor('#F59E0B')
        )
        
        elements = []
        
        # Título
        elements.append(Paragraph(f"Relatório da Assessoria: {nome_decoded}", title_style))
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Estatísticas
        elements.append(Paragraph("Estatísticas Gerais", subtitle_style))
        stats_data = [
            ['Métrica', 'Valor'],
            ['Total de Atletas', str(total_atletas)],
            ['Total de Corridas', str(total_corridas)],
            ['Total de Pontos', str(total_pontos)],
            ['Total de Pódios', str(total_podios)],
            ['Total de Vitórias', str(total_vitorias)],
            ['Média Pontos/Atleta', str(estatisticas["media_pontos_atleta"])],
            ['Média Corridas/Atleta', str(estatisticas["media_corridas_atleta"])],
        ]
        
        stats_table = Table(stats_data, colWidths=[200, 100])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Top 20 Atletas
        elements.append(Paragraph("Top 20 Atletas por Pontuação", subtitle_style))
        atletas_sorted = sorted(atletas, key=lambda x: x.get("pontos_total", 0), reverse=True)[:20]
        atletas_data = [['Pos', 'Nome', 'Cidade/UF', 'Pontos', 'Corridas']]
        for i, a in enumerate(atletas_sorted, 1):
            atletas_data.append([
                str(i),
                (a.get("nome", ""))[:30],
                f"{(a.get('cidade', '') or '')[:15]}/{a.get('estado', '')}",
                str(a.get("pontos_total", 0)),
                str(a.get("total_corridas", 0))
            ])
        
        atletas_table = Table(atletas_data, colWidths=[40, 200, 150, 70, 70])
        atletas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ]))
        elements.append(atletas_table)
        elements.append(Spacer(1, 20))
        
        # Últimas 30 Corridas
        if corridas:
            elements.append(Paragraph("Últimas 30 Corridas", subtitle_style))
            corridas_sorted = sorted(corridas, key=lambda x: x.get("data", ""), reverse=True)[:30]
            corridas_data = [['Atleta', 'Corrida', 'Data', 'Dist.', 'Pos.', 'Pts']]
            for c in corridas_sorted:
                corridas_data.append([
                    (c.get("atleta_nome", ""))[:20],
                    (c.get("nome_corrida", ""))[:35],
                    c.get("data", ""),
                    c.get("distancia", ""),
                    str(c.get("colocacao", "")),
                    str(c.get("pontos", 0))
                ])
            
            corridas_table = Table(corridas_data, colWidths=[120, 220, 70, 50, 40, 40])
            corridas_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F9FF')]),
            ]))
            elements.append(corridas_table)
        
        # Rodapé
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Ranking de Corrida de Rua - ROE-RR", 
                                  ParagraphStyle('Footer', fontSize=8, alignment=TA_CENTER, textColor=colors.gray)))
        
        doc.build(elements)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=relatorio_{nome_decoded.replace(' ', '_')}.pdf"}
        )
    
    else:  # CSV
        output = io.StringIO()
        
        # Seção 1: Estatísticas
        output.write("=== ESTATÍSTICAS DA ASSESSORIA ===\n")
        output.write(f"Equipe,{nome_decoded}\n")
        output.write(f"Data Exportação,{datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        output.write(f"Total Atletas,{total_atletas}\n")
        output.write(f"Total Corridas,{total_corridas}\n")
        output.write(f"Total Pontos,{total_pontos}\n")
        output.write(f"Total Pódios,{total_podios}\n")
        output.write(f"Total Vitórias,{total_vitorias}\n")
        output.write(f"Média Pontos/Atleta,{round(total_pontos / max(1, total_atletas), 1)}\n")
        output.write(f"Média Corridas/Atleta,{round(total_corridas / max(1, total_atletas), 1)}\n")
        output.write("\n")
        
        # Seção 2: Lista de Atletas
        output.write("=== LISTA DE ATLETAS ===\n")
        writer = csv.writer(output)
        writer.writerow(["Nome", "Email", "Gênero", "Categoria", "Faixa Etária", "Cidade", "Estado", "Pontos", "Corridas", "Data Cadastro"])
        
        for a in sorted(atletas, key=lambda x: x.get("pontos_total", 0), reverse=True):
            writer.writerow([
                a.get("nome", ""),
                a.get("email", ""),
                "Masculino" if a.get("genero") == "M" else "Feminino",
                a.get("categoria", "").upper(),
                a.get("faixa_etaria", ""),
                a.get("cidade", ""),
                a.get("estado", ""),
                a.get("pontos_total", 0),
                a.get("total_corridas", 0),
                a.get("created_at", "")[:10] if a.get("created_at") else ""
            ])
        
        output.write("\n")
        
        # Seção 3: Histórico de Corridas
        output.write("=== HISTÓRICO DE CORRIDAS ===\n")
        writer.writerow(["Atleta", "Corrida", "Data", "Distância", "Colocação", "Pontos", "Modalidade"])
        
        for c in sorted(corridas, key=lambda x: x.get("data", ""), reverse=True):
            writer.writerow([
                c.get("atleta_nome", ""),
                c.get("nome_corrida", ""),
                c.get("data", ""),
                c.get("distancia", ""),
                c.get("colocacao", ""),
                c.get("pontos", 0),
                c.get("modalidade", "")
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),  # utf-8-sig para Excel
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=assessoria_{nome_decoded.replace(' ', '_')}.csv"}
        )


@router.get("/exportar-graficos/{nome_equipe}")
async def exportar_graficos_assessoria(
    nome_equipe: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Exporta dados dos gráficos avançados em formato JSON para processamento
    Pode ser usado para gerar PDF no frontend ou integrar com outras ferramentas
    """
    # Reutilizar a função de gráficos avançados
    graficos = await get_graficos_avancados(nome_equipe, current_user)
    
    # Adicionar metadados para exportação
    graficos["metadados"] = {
        "data_exportacao": datetime.now().isoformat(),
        "exportado_por": current_user.get("nome", ""),
        "formato": "json_graficos"
    }
    
    return graficos
