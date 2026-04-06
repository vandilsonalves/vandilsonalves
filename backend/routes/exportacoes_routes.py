# /app/backend/routes/exportacoes_routes.py
# Módulo de Exportações em Excel para o Admin

from fastapi import APIRouter, Depends
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
