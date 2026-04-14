# /app/backend/routes/exportacoes_routes.py
# Módulo de Exportações em Excel para o Admin

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
import io

from config import db
from routes.auth_routes import get_admin_user

router = APIRouter(tags=["Exportações Admin"])

HEADER_FILL = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
THIN_BORDER = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)


def _style_headers(ws, col_count):
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")


def _style_borders(ws, col_count):
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=col_count):
        for cell in row:
            cell.border = THIN_BORDER


def _make_response(wb, filename):
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# 1. Exportar Atletas Profissional/Amador
@router.get("/admin/exportar/atletas-profissional")
async def exportar_atletas_profissional(admin: dict = Depends(get_admin_user)):
    atletas = await db.usuarios.find(
        {"role": "atleta", "modalidade_usuario": {"$ne": "povao_pace_livre"}},
        {"_id": 0, "password_hash": 0}
    ).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Atletas Pro-Amador"
    headers = ["Nome", "Email", "Equipe", "Cidade", "Estado", "Genero", "Categoria", "Faixa Etaria", "Telefone", "Data Cadastro", "Status"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for a in atletas:
        ws.append([
            a.get("nome", ""), a.get("email", ""),
            a.get("equipe", "") or "Individual",
            a.get("cidade", ""), a.get("estado", ""), a.get("genero", ""),
            a.get("categoria", ""), a.get("faixa_etaria", ""),
            a.get("telefone", ""),
            str(a.get("data_criacao", ""))[:10],
            "Ativo" if a.get("is_active", True) else "Inativo"
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([30, 30, 25, 20, 8, 12, 15, 15, 18, 12, 10]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"atletas_profissional_amador_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 2. Exportar Atletas da Galera
@router.get("/admin/exportar/atletas-galera")
async def exportar_atletas_galera(admin: dict = Depends(get_admin_user)):
    atletas = await db.usuarios.find(
        {"role": "atleta", "modalidade_usuario": "povao_pace_livre"},
        {"_id": 0, "password_hash": 0}
    ).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Atletas Galera"
    headers = ["Nome", "Email", "Equipe", "Cidade", "Estado", "Genero", "Faixa Etaria", "Telefone", "Data Cadastro", "Status"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for a in atletas:
        ws.append([
            a.get("nome", ""), a.get("email", ""),
            a.get("equipe", "") or "Individual",
            a.get("cidade", ""), a.get("estado", ""), a.get("genero", ""),
            a.get("faixa_etaria", ""), a.get("telefone", ""),
            str(a.get("data_criacao", ""))[:10],
            "Ativo" if a.get("is_active", True) else "Inativo"
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([30, 30, 25, 20, 8, 12, 15, 18, 12, 10]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"atletas_galera_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 3. Exportar Atletas Dono de Assessoria
@router.get("/admin/exportar/donos-assessoria")
async def exportar_donos_assessoria(admin: dict = Depends(get_admin_user)):
    donos = await db.usuarios.find(
        {"role": "dono_assessoria"},
        {"_id": 0, "password_hash": 0}
    ).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Donos de Assessoria"
    headers = ["Nome", "Email", "Equipe/Assessoria", "Cidade", "Estado", "Telefone", "Data Cadastro", "Status"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for d in donos:
        ws.append([
            d.get("nome", ""), d.get("email", ""),
            d.get("equipe", ""),
            d.get("cidade", ""), d.get("estado", ""),
            d.get("telefone", ""),
            str(d.get("data_criacao", ""))[:10],
            "Ativo" if d.get("is_active", True) else "Inativo"
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([30, 30, 30, 20, 8, 18, 12, 10]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"donos_assessoria_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 4. Exportar Assessorias
@router.get("/admin/exportar/assessorias")
async def exportar_assessorias(admin: dict = Depends(get_admin_user)):
    assessorias = await db.assessorias.find({}, {"_id": 0}).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Assessorias"
    headers = ["Nome", "Cidade", "Estado", "Dono", "Status", "Selo", "Total Atletas", "Total Pontos", "Data Criacao"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for a in assessorias:
        ws.append([
            a.get("nome", ""), a.get("cidade", ""), a.get("estado", ""),
            a.get("dono_nome", ""), a.get("status", ""),
            a.get("selo", ""), a.get("total_atletas", 0),
            a.get("pontos_total", 0),
            str(a.get("data_criacao", ""))[:10]
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([30, 20, 8, 25, 12, 12, 15, 15, 12]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"assessorias_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 5. Exportar Corridas Parceiras
@router.get("/admin/exportar/corridas-parceiras")
async def exportar_corridas_parceiras(admin: dict = Depends(get_admin_user)):
    corridas = await db.corridas_parceiras.find({}, {"_id": 0}).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Corridas Parceiras"
    headers = ["Nome Evento", "Data", "Cidade", "Estado", "Valor Inscricao", "Link Inscricao", "Clicks", "Ativo", "Data Criacao"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for c in corridas:
        clicks_val = c.get("clicks", 0)
        total_clicks = sum(clicks_val.values()) if isinstance(clicks_val, dict) else (clicks_val or 0)
        ws.append([
            c.get("nome_evento", ""), c.get("data_evento", ""),
            c.get("cidade", ""), c.get("estado", ""),
            c.get("valor_inscricao", ""), c.get("link_inscricao", ""),
            total_clicks,
            "Sim" if c.get("ativo", True) else "Nao",
            str(c.get("data_criacao", ""))[:10]
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([35, 12, 20, 8, 18, 40, 10, 8, 12]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"corridas_parceiras_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 6. Exportar Corridas Avaliadas
@router.get("/admin/exportar/corridas-avaliadas")
async def exportar_corridas_avaliadas(admin: dict = Depends(get_admin_user)):
    corridas = await db.corridas_eventos.find(
        {"total_avaliacoes": {"$gt": 0}},
        {"_id": 0}
    ).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Corridas Avaliadas"
    headers = ["Nome Corrida", "Organizador", "Cidade", "Estado", "Data", "Total Avaliacoes", "Media Geral", "Media Organizacao", "Media Percurso", "Media Kit", "Media Hidratacao"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for c in corridas:
        ws.append([
            c.get("nome_corrida", ""), c.get("organizador", ""),
            c.get("cidade", ""), c.get("estado", ""),
            c.get("data_corrida", ""),
            c.get("total_avaliacoes", 0),
            round(c.get("media_geral", 0), 2),
            round(c.get("media_organizacao", 0), 2),
            round(c.get("media_percurso", 0), 2),
            round(c.get("media_kit", 0) or 0, 2),
            round(c.get("media_hidratacao", 0) or 0, 2)
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([35, 25, 20, 8, 12, 18, 14, 18, 15, 12, 18]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"corridas_avaliadas_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 7. Exportar Média das Avaliações das Corridas
@router.get("/admin/exportar/media-avaliacoes")
async def exportar_media_avaliacoes(admin: dict = Depends(get_admin_user)):
    avaliacoes = await db.avaliacoes_corridas.find({}, {"_id": 0}).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Avaliacoes Detalhadas"
    headers = ["Corrida ID", "Atleta", "Email", "Organizacao", "Percurso", "Kit Atleta", "Hidratacao", "Pos Prova", "Premiacao", "Nota Corrida", "Participou"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for a in avaliacoes:
        ws.append([
            a.get("corrida_id", ""),
            a.get("atleta_nome", ""), a.get("atleta_email", ""),
            a.get("organizacao", 0), a.get("percurso", 0),
            a.get("kit_atleta", 0), a.get("hidratacao", 0),
            a.get("pos_prova", 0), a.get("premiacao", 0),
            a.get("nota_corrida", 0),
            "Sim" if a.get("participei", False) else "Nao"
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([20, 25, 30, 14, 12, 12, 14, 12, 12, 14, 12]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"media_avaliacoes_corridas_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 8. Exportar Engajamento
@router.get("/admin/exportar/engajamento")
async def exportar_engajamento(admin: dict = Depends(get_admin_user)):
    wb = Workbook()

    # Aba 1: Logins por usuario
    ws1 = wb.active
    ws1.title = "Logins"
    headers1 = ["Email", "Nome", "Data/Hora", "Dispositivo", "Navegador", "IP", "Sucesso"]
    ws1.append(headers1)
    _style_headers(ws1, len(headers1))

    logins = await db.login_history.find({}, {"_id": 0}).sort("data_hora", -1).to_list(500)
    for l in logins:
        ws1.append([
            l.get("email", ""), l.get("admin_nome", ""),
            str(l.get("data_hora", ""))[:19].replace("T", " "),
            l.get("dispositivo", ""), l.get("navegador", ""),
            l.get("ip_address", ""),
            "Sim" if l.get("sucesso", False) else "Nao"
        ])
    _style_borders(ws1, len(headers1))
    for i, w in enumerate([30, 25, 20, 15, 15, 18, 8]):
        ws1.column_dimensions[chr(65 + i)].width = w

    # Aba 2: Feed (posts e interacoes)
    ws2 = wb.create_sheet("Feed Posts")
    headers2 = ["Autor", "Equipe", "Tipo", "Conteudo", "Curtidas", "Comentarios", "Data"]
    ws2.append(headers2)
    _style_headers(ws2, len(headers2))

    posts = await db.feed_posts.find({}, {"_id": 0}).sort("data_criacao", -1).to_list(500)
    for p in posts:
        ws2.append([
            p.get("autor_nome", ""), p.get("equipe", ""),
            p.get("tipo", ""), str(p.get("conteudo", ""))[:100],
            p.get("curtidas", 0), p.get("total_comentarios", 0),
            str(p.get("data_criacao", ""))[:19].replace("T", " ")
        ])
    _style_borders(ws2, len(headers2))
    for i, w in enumerate([25, 20, 15, 50, 10, 14, 20]):
        ws2.column_dimensions[chr(65 + i)].width = w

    # Aba 3: Visitas
    ws3 = wb.create_sheet("Visitas Diarias")
    headers3 = ["Data", "Visitas"]
    ws3.append(headers3)
    _style_headers(ws3, len(headers3))

    visitas = await db.visitas_diarias.find({}, {"_id": 0}).sort("data", -1).to_list(None)
    for v in visitas:
        ws3.append([v.get("data", ""), v.get("visitas", 0)])
    _style_borders(ws3, len(headers3))

    return _make_response(wb, f"engajamento_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 9. Exportar Retenção
@router.get("/admin/exportar/retencao")
async def exportar_retencao(admin: dict = Depends(get_admin_user)):
    atletas = await db.usuarios.find(
        {"role": "atleta"},
        {"_id": 0, "password_hash": 0}
    ).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Retencao Atletas"
    headers = ["Nome", "Email", "Equipe", "Estado", "Modalidade", "Data Cadastro", "Ultimo Login", "Status", "Dias Sem Login"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    agora = datetime.now(timezone.utc)
    for a in atletas:
        ultimo_login = a.get("ultimo_login", "")
        dias_sem_login = ""
        if ultimo_login:
            try:
                ul = datetime.fromisoformat(str(ultimo_login).replace("Z", "+00:00"))
                dias_sem_login = (agora - ul).days
            except Exception:
                pass
        ws.append([
            a.get("nome", ""), a.get("email", ""),
            a.get("equipe", "") or "Individual",
            a.get("estado", ""),
            "Galera" if a.get("modalidade_usuario") == "povao_pace_livre" else "Pro/Amador",
            str(a.get("data_criacao", ""))[:10],
            str(ultimo_login)[:10] if ultimo_login else "Nunca",
            "Ativo" if a.get("is_active", True) else "Inativo",
            dias_sem_login
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([30, 30, 25, 8, 15, 12, 12, 10, 15]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"retencao_atletas_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 10. Exportar Aprovações com Logs do Colaborador
@router.get("/admin/exportar/aprovacoes-logs")
async def exportar_aprovacoes_logs(admin: dict = Depends(get_admin_user)):
    # Resultados pendentes e aprovados
    resultados = await db.resultados_pendentes.find({}, {"_id": 0}).sort("data_submissao", -1).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Aprovacoes"
    headers = ["Atleta ID", "Competicao", "Cidade", "Estado", "Data Competicao", "Colocacao", "Tempo", "Distancia", "Status", "Motivo Reprovacao", "Aprovado Por", "Data Submissao"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for r in resultados:
        ws.append([
            r.get("usuario_id", ""),
            r.get("nome_competicao", ""),
            r.get("cidade_competicao", ""), r.get("estado_competicao", ""),
            r.get("data_competicao", ""),
            r.get("colocacao", 0), r.get("tempo", ""),
            r.get("distancia", ""), r.get("status", ""),
            r.get("motivo_reprovacao", ""),
            r.get("aprovado_por", r.get("admin_nome", "")),
            str(r.get("data_submissao", ""))[:19].replace("T", " ")
        ])
    _style_borders(ws, len(headers))

    # Aba 2: Logs administrativos
    ws2 = wb.create_sheet("Logs Colaborador")
    headers2 = ["Admin", "Role", "Acao", "Descricao", "Entidade", "Data/Hora", "IP", "Dispositivo"]
    ws2.append(headers2)
    _style_headers(ws2, len(headers2))

    logs = await db.admin_logs.find({}, {"_id": 0}).sort("data_hora", -1).to_list(500)
    for l in logs:
        ws2.append([
            l.get("admin_nome", ""), l.get("admin_role", ""),
            l.get("tipo_acao", ""), str(l.get("descricao", ""))[:100],
            l.get("entidade_nome", ""),
            str(l.get("data_hora", ""))[:19].replace("T", " "),
            l.get("ip_address", ""), l.get("dispositivo", "")
        ])
    _style_borders(ws2, len(headers2))
    for i, w in enumerate([25, 15, 20, 50, 25, 20, 18, 15]):
        ws2.column_dimensions[chr(65 + i)].width = w

    return _make_response(wb, f"aprovacoes_logs_colaborador_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 11. Exportar Autorizações
@router.get("/admin/exportar/autorizacoes")
async def exportar_autorizacoes(admin: dict = Depends(get_admin_user)):
    autorizacoes = await db.autorizacoes.find({}, {"_id": 0}).to_list(None)

    # Buscar nomes dos atletas
    atleta_ids = list(set(a.get("atleta_id", "") for a in autorizacoes))
    atletas_map = {}
    if atleta_ids:
        atletas_docs = await db.usuarios.find(
            {"id": {"$in": atleta_ids}},
            {"_id": 0, "id": 1, "nome": 1, "email": 1}
        ).to_list(None)
        atletas_map = {a["id"]: a for a in atletas_docs}

    wb = Workbook()
    ws = wb.active
    ws.title = "Autorizacoes"
    headers = ["Atleta", "Email", "Tipo", "Descricao", "Status", "Autorizado Por", "Data Inicio", "Data Expiracao", "Observacao"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for a in autorizacoes:
        atleta = atletas_map.get(a.get("atleta_id", ""), {})
        ws.append([
            atleta.get("nome", a.get("atleta_id", "")),
            atleta.get("email", ""),
            a.get("tipo", ""), a.get("descricao", ""),
            a.get("status", ""),
            a.get("autorizado_por", ""),
            str(a.get("data_inicio", ""))[:10],
            str(a.get("data_expiracao", ""))[:10],
            a.get("observacao", "")
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([25, 30, 15, 30, 12, 20, 12, 12, 30]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"autorizacoes_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 12. Exportar Financeiro
@router.get("/admin/exportar/financeiro")
async def exportar_financeiro_excel(admin: dict = Depends(get_admin_user)):
    txs = await db.payment_transactions.find({}, {"_id": 0}).sort("data_criacao", -1).to_list(None)

    pagas = [t for t in txs if t.get("payment_status") == "paid"]
    receita_total = sum(t.get("amount", 0) for t in pagas)

    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Resumo"
    ws1.append(["RELATORIO FINANCEIRO - RANKING RUN PRO"])
    ws1.merge_cells("A1:D1")
    ws1["A1"].font = Font(bold=True, size=14)
    ws1.append([f"Gerado em: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}"])
    ws1.append([])
    ws1.append(["Metrica", "Valor"])
    ws1.append(["Receita Total", f"R$ {receita_total:.2f}"])
    ws1.append(["Total Transacoes", len(txs)])
    ws1.append(["Transacoes Pagas", len(pagas)])
    ws1.append(["Ticket Medio", f"R$ {(receita_total / len(pagas)):.2f}" if pagas else "R$ 0,00"])
    ws1.column_dimensions["A"].width = 30
    ws1.column_dimensions["B"].width = 20

    ws2 = wb.create_sheet("Transacoes")
    headers = ["Data", "Atleta", "Email", "Tipo", "Valor (R$)", "Status", "Plano", "Gateway"]
    ws2.append(headers)
    _style_headers(ws2, len(headers))

    for tx in txs:
        ws2.append([
            str(tx.get("data_criacao", ""))[:16].replace("T", " "),
            tx.get("user_nome", ""), tx.get("user_email", ""),
            tx.get("tipo", ""), tx.get("amount", 0),
            tx.get("payment_status", ""),
            tx.get("plano_nome", tx.get("plano", "")),
            tx.get("gateway", "")
        ])
    _style_borders(ws2, len(headers))
    for i, w in enumerate([18, 25, 30, 12, 12, 12, 22, 15]):
        ws2.column_dimensions[chr(65 + i)].width = w

    return _make_response(wb, f"financeiro_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 13. Exportar Mensagens Enviadas
@router.get("/admin/exportar/mensagens")
async def exportar_mensagens(admin: dict = Depends(get_admin_user)):
    mensagens = await db.mensagens_admin.find({}, {"_id": 0}).sort("data_envio", -1).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Mensagens Admin"
    headers = ["Titulo", "Mensagem", "Filtro Tipo", "Modalidades", "Generos", "Total Enviados", "Admin", "Data Envio", "Link"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for m in mensagens:
        ws.append([
            m.get("titulo", ""),
            str(m.get("mensagem", ""))[:200],
            m.get("filtro_tipo", ""),
            ", ".join(m.get("filtro_modalidades", [])) if isinstance(m.get("filtro_modalidades"), list) else str(m.get("filtro_modalidades", "")),
            ", ".join(m.get("filtro_generos", [])) if isinstance(m.get("filtro_generos"), list) else str(m.get("filtro_generos", "")),
            m.get("total_enviados", 0),
            m.get("admin_nome", ""),
            str(m.get("data_envio", ""))[:19].replace("T", " "),
            m.get("link", "")
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([30, 60, 15, 25, 20, 15, 20, 20, 30]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"mensagens_enviadas_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 14. Exportar Logs Administrativos
@router.get("/admin/exportar/logs-admin")
async def exportar_logs_admin(admin: dict = Depends(get_admin_user)):
    logs = await db.admin_logs.find({}, {"_id": 0}).sort("data_hora", -1).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Logs Administrativos"
    headers = ["Admin", "Role", "Tipo Acao", "Descricao", "Entidade Tipo", "Entidade Nome", "IP", "Dispositivo", "Data/Hora"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for l in logs:
        ws.append([
            l.get("admin_nome", ""), l.get("admin_role", ""),
            l.get("tipo_acao", ""), str(l.get("descricao", ""))[:150],
            l.get("entidade_tipo", ""), l.get("entidade_nome", ""),
            l.get("ip_address", ""), l.get("dispositivo", ""),
            str(l.get("data_hora", ""))[:19].replace("T", " ")
        ])
    _style_borders(ws, len(headers))
    for i, w in enumerate([25, 15, 20, 60, 18, 25, 18, 15, 20]):
        ws.column_dimensions[chr(65 + i)].width = w
    return _make_response(wb, f"logs_administrativos_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 15. Exportar Dados Submetidos (Resultados Pendentes / Aprovados / Rejeitados)
@router.get("/admin/exportar/dados-submetidos")
async def exportar_dados_submetidos(admin: dict = Depends(get_admin_user)):
    resultados = await db.resultados_pendentes.find({}, {"_id": 0}).sort("data_submissao", -1).to_list(None)

    # Buscar nomes dos atletas
    atleta_ids = list(set(r.get("usuario_id", "") for r in resultados))
    atletas_map = {}
    if atleta_ids:
        atletas_docs = await db.usuarios.find(
            {"id": {"$in": atleta_ids}},
            {"_id": 0, "id": 1, "nome": 1, "email": 1, "equipe": 1, "cidade": 1, "estado": 1}
        ).to_list(None)
        atletas_map = {a["id"]: a for a in atletas_docs}

    wb = Workbook()
    ws = wb.active
    ws.title = "Dados Submetidos"
    headers = [
        "Atleta", "Email", "Equipe", "Cidade Atleta", "Estado Atleta",
        "Competicao", "Cidade Competicao", "Estado Competicao",
        "Data Competicao", "Distancia", "Tempo", "Colocacao",
        "Modalidade", "Link Resultado", "Foto Podio",
        "Status", "Motivo Reprovacao",
        "Data Submissao", "Hora Submissao"
    ]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for r in resultados:
        atleta = atletas_map.get(r.get("usuario_id", ""), {})
        data_sub = str(r.get("data_submissao", ""))
        data_parte = data_sub[:10] if len(data_sub) >= 10 else data_sub
        hora_parte = data_sub[11:19] if len(data_sub) >= 19 else ""
        ws.append([
            atleta.get("nome", r.get("usuario_id", "")),
            atleta.get("email", ""),
            atleta.get("equipe", "") or "Individual",
            atleta.get("cidade", ""),
            atleta.get("estado", ""),
            r.get("nome_competicao", ""),
            r.get("cidade_competicao", ""),
            r.get("estado_competicao", ""),
            r.get("data_competicao", ""),
            r.get("distancia", ""),
            r.get("tempo", ""),
            r.get("colocacao", 0),
            "Galera" if r.get("modalidade") == "povao_pace_livre" else "Pro/Amador",
            r.get("link_resultado", ""),
            r.get("foto_podio_url", ""),
            r.get("status", ""),
            r.get("motivo_reprovacao", ""),
            data_parte,
            hora_parte
        ])
    _style_borders(ws, len(headers))
    col_widths = [25, 30, 20, 18, 8, 30, 18, 8, 14, 10, 12, 12, 15, 45, 40, 12, 30, 14, 10]
    for i, w in enumerate(col_widths):
        ws.column_dimensions[chr(65 + i) if i < 26 else "A" + chr(65 + i - 26)].width = w
    return _make_response(wb, f"dados_submetidos_{datetime.now().strftime('%Y%m%d')}.xlsx")



# ==================== EXPORTAÇÕES DE RANKINGS POR MODALIDADE ====================

# 16. Exportar Ranking Profissional/Amador
@router.get("/admin/exportar/ranking-profissional")
async def exportar_ranking_profissional(admin: dict = Depends(get_admin_user)):
    """Exporta ranking Profissional/Amador com todas as categorias"""
    atletas = await db.usuarios.find(
        {"role": {"$in": ["atleta", "dono_assessoria"]}, "modalidade_usuario": {"$ne": "povao_pace_livre"}},
        {"_id": 0, "password_hash": 0}
    ).sort("pontos_total", -1).to_list(None)

    wb = Workbook()

    categorias = {
        "MASCULINO": lambda a: a.get("genero") == "M" and a.get("categoria", "").upper() in ["NORMAL", ""],
        "FEMININO": lambda a: a.get("genero") == "F" and a.get("categoria", "").upper() in ["NORMAL", ""],
        "PCD_M": lambda a: a.get("genero") == "M" and a.get("categoria", "").upper() == "PCD",
        "PCD_F": lambda a: a.get("genero") == "F" and a.get("categoria", "").upper() == "PCD",
        "CADEIRANTE_M": lambda a: a.get("genero") == "M" and a.get("categoria", "").upper() == "CADEIRANTE",
        "CADEIRANTE_F": lambda a: a.get("genero") == "F" and a.get("categoria", "").upper() == "CADEIRANTE",
    }

    headers = ["Pos", "Nome", "Equipe", "Cidade", "Estado", "Faixa Etaria", "Pontos", "Corridas", "Podios", "Vitorias"]
    first = True
    for cat_nome, filtro_fn in categorias.items():
        if first:
            ws = wb.active
            ws.title = cat_nome
            first = False
        else:
            ws = wb.create_sheet(cat_nome)

        ws.append(headers)
        _style_headers(ws, len(headers))

        filtered = sorted([a for a in atletas if filtro_fn(a)], key=lambda x: -(x.get("pontos_total", 0)))
        for i, a in enumerate(filtered, 1):
            ws.append([
                i, a.get("nome", ""), a.get("equipe", "") or "Individual",
                a.get("cidade", ""), a.get("estado", ""), a.get("faixa_etaria", ""),
                a.get("pontos_total", 0), a.get("total_corridas", 0),
                a.get("total_podios", 0), a.get("total_vitorias", 0),
            ])
        _style_borders(ws, len(headers))
        for j, w in enumerate([6, 30, 25, 20, 8, 12, 10, 10, 10, 10]):
            ws.column_dimensions[chr(65 + j)].width = w

    return _make_response(wb, f"ranking_profissional_amador_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 17. Exportar Ranking da Galera (Pace Livre)
@router.get("/admin/exportar/ranking-galera")
async def exportar_ranking_galera(admin: dict = Depends(get_admin_user)):
    """Exporta ranking da Galera (Pace Livre) por genero"""
    atletas = await db.usuarios.find(
        {"role": {"$in": ["atleta", "dono_assessoria"]}, "modalidade_usuario": "povao_pace_livre"},
        {"_id": 0, "password_hash": 0}
    ).sort("pontos_povao", -1).to_list(None)

    wb = Workbook()
    headers = ["Pos", "Nome", "Equipe", "Cidade", "Estado", "Faixa Etaria", "Pontos", "Corridas", "Distancia Total (km)"]

    for idx, (gen_label, gen_code) in enumerate([("MASCULINO", "M"), ("FEMININO", "F")]):
        if idx == 0:
            ws = wb.active
            ws.title = gen_label
        else:
            ws = wb.create_sheet(gen_label)

        ws.append(headers)
        _style_headers(ws, len(headers))

        filtered = sorted(
            [a for a in atletas if a.get("genero") == gen_code],
            key=lambda x: -(x.get("pontos_povao", 0))
        )
        for i, a in enumerate(filtered, 1):
            ws.append([
                i, a.get("nome", ""), a.get("equipe", "") or "Individual",
                a.get("cidade", ""), a.get("estado", ""), a.get("faixa_etaria", ""),
                a.get("pontos_povao", 0), a.get("total_corridas_povao", a.get("total_corridas", 0)),
                a.get("distancia_total_km", 0),
            ])
        _style_borders(ws, len(headers))
        for j, w in enumerate([6, 30, 25, 20, 8, 12, 10, 10, 18]):
            ws.column_dimensions[chr(65 + j)].width = w

    return _make_response(wb, f"ranking_galera_pace_livre_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 18. Exportar Ranking das Assessorias
@router.get("/admin/exportar/ranking-assessorias")
async def exportar_ranking_assessorias(admin: dict = Depends(get_admin_user)):
    """Exporta ranking completo das assessorias (Liga ROE-RR)"""
    from routes.liga_assessorias_routes import get_ranking_assessorias

    try:
        data = await get_ranking_assessorias(tipo="nacional")
        ranking = data.get("ranking", [])
    except Exception:
        ranking = []

    wb = Workbook()
    ws = wb.active
    ws.title = "Ranking Assessorias"
    headers = ["Pos", "Assessoria", "Cidade", "Estado", "Selo", "Pontos ROE-RR", "Total Atletas", "Total Resultados", "Podios", "Vitorias"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for a in ranking:
        ws.append([
            a.get("posicao", 0), a.get("nome", ""),
            a.get("cidade", ""), a.get("estado", ""),
            (a.get("selo", "") or "").upper(),
            a.get("pontos", 0), a.get("total_atletas", 0),
            a.get("total_resultados", 0),
            a.get("total_podios", 0), a.get("total_vitorias", 0),
        ])
    _style_borders(ws, len(headers))
    for j, w in enumerate([6, 30, 20, 8, 10, 15, 15, 18, 10, 10]):
        ws.column_dimensions[chr(65 + j)].width = w

    return _make_response(wb, f"ranking_assessorias_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 19. Exportar Ranking das Avaliacoes de Corridas
@router.get("/admin/exportar/ranking-corridas-avaliadas")
async def exportar_ranking_corridas_avaliadas(admin: dict = Depends(get_admin_user)):
    """Exporta ranking das corridas melhor avaliadas"""
    corridas = await db.corridas_eventos.find(
        {"total_avaliacoes": {"$gte": 1}},
        {"_id": 0}
    ).to_list(None)

    # Sort by bayesian rating
    total_avaliacoes_global = sum(c.get("total_avaliacoes", 0) for c in corridas)
    num_avaliadas = sum(1 for c in corridas if c.get("total_avaliacoes", 0) > 0)
    if num_avaliadas > 0:
        media_global = sum(c.get("media_geral", 0) * c.get("total_avaliacoes", 0) for c in corridas) / max(total_avaliacoes_global, 1)
        m = max(3, total_avaliacoes_global // max(num_avaliadas, 1))
    else:
        media_global = 0
        m = 3

    for c in corridas:
        v = c.get("total_avaliacoes", 0)
        R = c.get("media_geral", 0)
        c["pontuacao_ranking"] = round((v / (v + m)) * R + (m / (v + m)) * media_global, 2) if v > 0 else 0

    corridas.sort(key=lambda x: (-x.get("pontuacao_ranking", 0), -x.get("total_avaliacoes", 0)))

    wb = Workbook()
    ws = wb.active
    ws.title = "Ranking Corridas"
    headers = ["Pos", "Corrida", "Organizador", "Cidade", "Estado", "Data", "Avaliacoes", "Nota Media", "Pontuacao Ranking", "Organizacao", "Percurso", "Kit", "Hidratacao"]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for i, c in enumerate(corridas, 1):
        ws.append([
            i, c.get("nome_corrida", ""), c.get("organizador", ""),
            c.get("cidade", ""), c.get("estado", ""), c.get("data_corrida", ""),
            c.get("total_avaliacoes", 0), c.get("media_geral", 0),
            c.get("pontuacao_ranking", 0),
            round(c.get("media_organizacao", 0), 2), round(c.get("media_percurso", 0), 2),
            round(c.get("media_kit", 0) or 0, 2), round(c.get("media_hidratacao", 0) or 0, 2),
        ])
    _style_borders(ws, len(headers))
    for j, w in enumerate([6, 35, 25, 20, 8, 12, 12, 12, 18, 14, 12, 8, 14]):
        ws.column_dimensions[chr(65 + j)].width = w

    return _make_response(wb, f"ranking_corridas_avaliadas_{datetime.now().strftime('%Y%m%d')}.xlsx")



# 20. Exportar Todas as Corridas com Links de Acesso
@router.get("/admin/exportar/corridas-completas")
async def exportar_corridas_completas(admin: dict = Depends(get_admin_user)):
    """Exporta todas as corridas inseridas na plataforma com links de acesso"""
    import os

    corridas = await db.corridas_eventos.find({}, {"_id": 0}).sort("data_corrida", -1).to_list(None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Todas as Corridas"
    headers = [
        "N", "Nome da Corrida", "Organizador", "Cidade", "Estado", "Data",
        "Distancias", "Tipo", "Status", "Link Pagina (Instagram/Site)", "Link Inscricao", "Link Resultados",
        "Total Avaliacoes", "Nota Media", "ID"
    ]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for i, c in enumerate(corridas, 1):
        ws.append([
            i,
            c.get("nome_corrida", ""),
            c.get("organizador", ""),
            c.get("cidade", ""),
            c.get("estado", ""),
            c.get("data_corrida", ""),
            c.get("distancias", c.get("distancia", "")),
            c.get("tipo", ""),
            c.get("status", "ativa"),
            c.get("pagina_link", ""),
            c.get("link_inscricao", ""),
            c.get("link_resultados", ""),
            c.get("total_avaliacoes", 0),
            round(c.get("media_geral", 0), 2),
            c.get("id", ""),
        ])

    _style_borders(ws, len(headers))
    for j, w in enumerate([5, 35, 25, 20, 8, 12, 15, 12, 10, 35, 35, 35, 15, 12, 36]):
        col_letter = chr(65 + j) if j < 26 else chr(64 + j // 26) + chr(65 + j % 26)
        ws.column_dimensions[col_letter].width = w

    return _make_response(wb, f"corridas_completas_{datetime.now().strftime('%Y%m%d')}.xlsx")



# 21. Exportar TODAS as Avaliacoes de Corrida (planilha completa)
@router.get("/admin/exportar/avaliacoes-corridas")
async def exportar_avaliacoes_corridas(admin: dict = Depends(get_admin_user)):
    """Exporta todas as avaliacoes de todas as corridas com dados completos dos avaliadores"""
    avaliacoes = await db.avaliacoes_corridas.find({}, {"_id": 0}).sort("data_avaliacao", -1).to_list(None)

    # Buscar nomes das corridas
    corrida_ids = list(set(a.get("corrida_id", "") for a in avaliacoes))
    corridas_map = {}
    if corrida_ids:
        corridas = await db.corridas_eventos.find(
            {"id": {"$in": corrida_ids}},
            {"_id": 0, "id": 1, "nome_corrida": 1, "organizador": 1, "cidade": 1, "estado": 1, "data_corrida": 1}
        ).to_list(None)
        corridas_map = {c["id"]: c for c in corridas}

    # Buscar emails dos avaliadores
    user_ids = list(set(a.get("usuario_id", "") for a in avaliacoes))
    users_map = {}
    if user_ids:
        users = await db.usuarios.find(
            {"id": {"$in": user_ids}},
            {"_id": 0, "id": 1, "email": 1, "nome": 1}
        ).to_list(None)
        users_map = {u["id"]: u for u in users}

    wb = Workbook()
    ws = wb.active
    ws.title = "Todas as Avaliacoes"
    headers = [
        "N", "ID Avaliador", "Nome Avaliador", "Email Avaliador",
        "Corrida Avaliada", "Organizador", "Cidade", "Estado", "Data Corrida",
        "Data/Hora Avaliacao",
        "Organizacao", "Percurso", "Kit", "Hidratacao", "Pos-Prova", "Media Geral",
        "Comentario"
    ]
    ws.append(headers)
    _style_headers(ws, len(headers))

    for i, a in enumerate(avaliacoes, 1):
        corrida = corridas_map.get(a.get("corrida_id", ""), {})
        user = users_map.get(a.get("usuario_id", ""), {})
        data_av = a.get("data_avaliacao", "")
        if data_av:
            try:
                dt = datetime.fromisoformat(data_av.replace("Z", "+00:00"))
                data_formatada = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                data_formatada = data_av
        else:
            data_formatada = ""

        ws.append([
            i,
            a.get("usuario_id", ""),
            a.get("usuario_nome", user.get("nome", "")),
            user.get("email", ""),
            corrida.get("nome_corrida", a.get("corrida_id", "")),
            corrida.get("organizador", ""),
            corrida.get("cidade", ""),
            corrida.get("estado", ""),
            corrida.get("data_corrida", ""),
            data_formatada,
            a.get("organizacao", 0),
            a.get("percurso", 0),
            a.get("kit", 0),
            a.get("hidratacao", 0),
            a.get("pos_prova", 0),
            round(a.get("media", 0), 2),
            a.get("comentario", ""),
        ])

    _style_borders(ws, len(headers))
    for j, w in enumerate([5, 36, 25, 30, 35, 20, 15, 8, 12, 18, 12, 12, 8, 12, 12, 12, 40]):
        col_letter = chr(65 + j) if j < 26 else chr(64 + j // 26) + chr(65 + j % 26)
        ws.column_dimensions[col_letter].width = w

    return _make_response(wb, f"avaliacoes_corridas_completo_{datetime.now().strftime('%Y%m%d')}.xlsx")


# 22. Exportar Avaliacoes de UMA corrida especifica
@router.get("/admin/exportar/avaliacoes-corrida/{corrida_id}")
async def exportar_avaliacoes_corrida_especifica(corrida_id: str, admin: dict = Depends(get_admin_user)):
    """Exporta avaliacoes de uma corrida especifica - ideal para auditoria/revisao"""
    corrida = await db.corridas_eventos.find_one({"id": corrida_id}, {"_id": 0})
    if not corrida:
        raise HTTPException(status_code=404, detail="Corrida nao encontrada")

    avaliacoes = await db.avaliacoes_corridas.find(
        {"corrida_id": corrida_id}, {"_id": 0}
    ).sort("data_avaliacao", -1).to_list(None)

    # Buscar emails dos avaliadores
    user_ids = list(set(a.get("usuario_id", "") for a in avaliacoes))
    users_map = {}
    if user_ids:
        users = await db.usuarios.find(
            {"id": {"$in": user_ids}},
            {"_id": 0, "id": 1, "email": 1, "nome": 1}
        ).to_list(None)
        users_map = {u["id"]: u for u in users}

    nome_corrida = corrida.get("nome_corrida", "Corrida")
    safe_name = nome_corrida.replace(" ", "_")[:30]

    wb = Workbook()

    # Aba 1: Resumo da corrida
    ws_resumo = wb.active
    ws_resumo.title = "Resumo"
    ws_resumo.append(["Corrida", nome_corrida])
    ws_resumo.append(["Organizador", corrida.get("organizador", "")])
    ws_resumo.append(["Cidade/Estado", f"{corrida.get('cidade', '')} - {corrida.get('estado', '')}"])
    ws_resumo.append(["Data da Corrida", corrida.get("data_corrida", "")])
    ws_resumo.append(["Total de Avaliacoes", len(avaliacoes)])
    ws_resumo.append(["Media Geral", round(corrida.get("media_geral", 0), 2)])
    ws_resumo.append(["Media Organizacao", round(corrida.get("media_organizacao", 0), 2)])
    ws_resumo.append(["Media Percurso", round(corrida.get("media_percurso", 0), 2)])
    ws_resumo.append(["Media Kit", round(corrida.get("media_kit", 0) or 0, 2)])
    ws_resumo.append(["Media Hidratacao", round(corrida.get("media_hidratacao", 0) or 0, 2)])
    ws_resumo.column_dimensions["A"].width = 20
    ws_resumo.column_dimensions["B"].width = 40

    # Aba 2: Avaliacoes detalhadas
    ws_av = wb.create_sheet("Avaliacoes Detalhadas")
    headers = [
        "N", "ID Avaliador", "Nome Avaliador", "Email Avaliador",
        "Data/Hora Avaliacao",
        "Organizacao", "Percurso", "Kit", "Hidratacao", "Pos-Prova", "Media",
        "Comentario"
    ]
    ws_av.append(headers)
    _style_headers(ws_av, len(headers))

    for i, a in enumerate(avaliacoes, 1):
        user = users_map.get(a.get("usuario_id", ""), {})
        data_av = a.get("data_avaliacao", "")
        if data_av:
            try:
                dt = datetime.fromisoformat(data_av.replace("Z", "+00:00"))
                data_formatada = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                data_formatada = data_av
        else:
            data_formatada = ""

        ws_av.append([
            i,
            a.get("usuario_id", ""),
            a.get("usuario_nome", user.get("nome", "")),
            user.get("email", ""),
            data_formatada,
            a.get("organizacao", 0),
            a.get("percurso", 0),
            a.get("kit", 0),
            a.get("hidratacao", 0),
            a.get("pos_prova", 0),
            round(a.get("media", 0), 2),
            a.get("comentario", ""),
        ])

    _style_borders(ws_av, len(headers))
    for j, w in enumerate([5, 36, 25, 30, 18, 12, 12, 8, 12, 12, 10, 40]):
        ws_av.column_dimensions[chr(65 + j)].width = w

    return _make_response(wb, f"avaliacoes_{safe_name}_{datetime.now().strftime('%Y%m%d')}.xlsx")
