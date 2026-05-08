
# ═══════════════════════════════════════════════
# PRIMYN — CRM (Google Sheets) v2
# Atualização: aba de Métricas com totais diários,
# por origem, por status e ticket médio.
# ═══════════════════════════════════════════════

import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
SPREADSHEET_NAME = "Primyn — CRM Leads"

CABECALHOS_LEADS = [
    "Data", "Nome", "E-mail", "WhatsApp", "Origem",
    "Tipo de Contato", "Origem Relacional", "Área",
    "Produto", "Arte", "Criação", "Formato",
    "Material", "Acabamento", "Quantidade",
    "Urgência", "Média Apresentada", "Status",
    "Avaliação", "Observações"
]

def conectar_sheets():
    try:
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"[ERRO SHEETS] Conexão falhou: {e}")
        return None

def obter_ou_criar_planilha(client):
    """Obtém ou cria a planilha com abas Leads e Métricas."""
    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(SPREADSHEET_NAME)
        spreadsheet.share("ola@primyn.com", perm_type="user", role="writer")

    # ── ABA LEADS ──────────────────────────────
    try:
        ws_leads = spreadsheet.worksheet("Leads")
    except gspread.WorksheetNotFound:
        ws_leads = spreadsheet.sheet1
        ws_leads.update_title("Leads")
        ws_leads.update("A1:T1", [CABECALHOS_LEADS])
        _formatar_cabecalho(ws_leads, "A1:T1")

    # ── ABA MÉTRICAS ───────────────────────────
    try:
        ws_metricas = spreadsheet.worksheet("Métricas")
    except gspread.WorksheetNotFound:
        ws_metricas = spreadsheet.add_worksheet(title="Métricas", rows=200, cols=10)
        _criar_aba_metricas(ws_metricas)

    return spreadsheet, ws_leads, ws_metricas

def _formatar_cabecalho(worksheet, range_str):
    """Formata cabeçalho com fundo preto e texto dourado."""
    worksheet.format(range_str, {
        "backgroundColor": {"red": 0.1, "green": 0.1, "blue": 0.1},
        "textFormat": {
            "bold": True,
            "foregroundColor": {"red": 0.83, "green": 0.68, "blue": 0.42}
        }
    })

def _criar_aba_metricas(ws):
    """Monta a estrutura inicial da aba de métricas."""
    ws.update("A1", [["PRIMYN — Métricas de Atendimento"]])
    ws.update("A2", [["Atualizado automaticamente a cada novo lead registrado"]])

    # Bloco: Totais gerais
    ws.update("A4:B4", [["TOTAIS GERAIS", ""]])
    ws.update("A5:B9", [
        ["Total de atendimentos",    "=COUNTA(Leads!A2:A)"],
        ["Novos leads",              "=COUNTIF(Leads!F2:F,\"novo_lead\")"],
        ["Clientes recorrentes",     "=COUNTIF(Leads!F2:F,\"cliente_recorrente\")"],
        ["Leads antigos (retorno)",  "=COUNTIF(Leads!F2:F,\"lead_antigo\")"],
        ["Handoffs realizados",      "=COUNTIF(Leads!R2:R,\"handoff\")"],
    ])

    # Bloco: Conversão
    ws.update("A11:B11", [["CONVERSÃO", ""]])
    ws.update("A12:B14", [
        ["Perdidos (não fecharam)",  "=COUNTIF(Leads!R2:R,\"perdido\")"],
        ["Aguardando resposta",      "=COUNTIF(Leads!R2:R,\"aguardando_resposta\")"],
        ["Taxa de handoff (%)",
         "=IFERROR(TEXT(COUNTIF(Leads!R2:R,\"handoff\")/COUNTA(Leads!A2:A),\"0.0%\"),\"—\")"],
    ])

    # Bloco: Ticket médio
    ws.update("A16:B16", [["TICKET MÉDIO", ""]])
    ws.update("A17:B19", [
        ["Ticket médio geral (R$)",
         "=IFERROR(AVERAGEIF(Leads!R2:R,\"handoff\",Leads!Q2:Q),\"—\")"],
        ["Maior ticket (R$)",  "=IFERROR(MAX(Leads!Q2:Q),\"—\")"],
        ["Menor ticket (R$)",  "=IFERROR(MIN(IF(Leads!Q2:Q>0,Leads!Q2:Q)),\"—\")"],
    ])

    # Bloco: Por origem
    ws.update("D4:E4", [["POR ORIGEM", ""]])
    ws.update("D5:E11", [
        ["Instagram",    "=COUNTIF(Leads!E2:E,\"instagram\")"],
        ["Indicação",    "=COUNTIF(Leads!E2:E,\"indicacao\")"],
        ["Google",       "=COUNTIF(Leads!E2:E,\"google\")"],
        ["Site",         "=COUNTIF(Leads!E2:E,\"site\")"],
        ["WhatsApp",     "=COUNTIF(Leads!E2:E,\"whatsapp\")"],
        ["Outro",        "=COUNTIF(Leads!E2:E,\"outro\")"],
        ["Não informado","=COUNTIF(Leads!E2:E,\"\")"],
    ])

    # Bloco: Por produto
    ws.update("D13:E13", [["POR PRODUTO", ""]])
    ws.update("D14:E20", [
        ["Cartão de visita",    "=COUNTIF(Leads!I2:I,\"*cartão*\")"],
        ["Papel timbrado",      "=COUNTIF(Leads!I2:I,\"*timbrado*\")"],
        ["Papelaria completa",  "=COUNTIF(Leads!I2:I,\"*papelaria*\")"],
        ["Convite",             "=COUNTIF(Leads!I2:I,\"*convite*\")"],
        ["Pasta",               "=COUNTIF(Leads!I2:I,\"*pasta*\")"],
        ["Envelope",            "=COUNTIF(Leads!I2:I,\"*envelope*\")"],
        ["Identidade visual",   "=COUNTIF(Leads!I2:I,\"*identidade*\")"],
    ])

    # Bloco: Hoje
    ws.update("G4:H4", [["HOJE", ""]])
    ws.update("G5:H8", [
        ["Atendimentos hoje",
         "=COUNTIF(Leads!A2:A,TEXT(TODAY(),\"DD/MM/YYYY\")&\"*\")"],
        ["Handoffs hoje",
         "=SUMPRODUCT((TEXT(DATEVALUE(MID(Leads!A2:A,1,10)),\"DD/MM/YYYY\")=TEXT(TODAY(),\"DD/MM/YYYY\"))*(Leads!R2:R=\"handoff\"))"],
        ["Perdidos hoje",
         "=SUMPRODUCT((TEXT(DATEVALUE(MID(Leads!A2:A,1,10)),\"DD/MM/YYYY\")=TEXT(TODAY(),\"DD/MM/YYYY\"))*(Leads!R2:R=\"perdido\"))"],
        ["Ticket médio hoje (R$)",
         "=IFERROR(AVERAGEIFS(Leads!Q2:Q,Leads!A2:A,TEXT(TODAY(),\"DD/MM/YYYY\")&\"*\",Leads!R2:R,\"handoff\"),\"—\")"],
    ])

    # Formatações dos títulos
    _formatar_cabecalho(ws, "A4:B4")
    _formatar_cabecalho(ws, "A11:B11")
    _formatar_cabecalho(ws, "A16:B16")
    _formatar_cabecalho(ws, "D4:E4")
    _formatar_cabecalho(ws, "D13:E13")
    _formatar_cabecalho(ws, "G4:H4")

    ws.format("A1", {"textFormat": {"bold": True, "fontSize": 14}})
    ws.format("A2", {
        "textFormat": {
            "italic": True,
            "foregroundColor": {"red": 0.6, "green": 0.6, "blue": 0.6}
        }
    })


def salvar_lead(dados):
    """Salva dados do lead na aba Leads."""
    try:
        client = conectar_sheets()
        if not client:
            print("[ERRO CRM] Não conectou ao Google Sheets")
            return False

        spreadsheet, ws_leads, _ = obter_ou_criar_planilha(client)

        # Normaliza valor da média para número puro (facilita AVERAGE no Sheets)
        media_raw = dados.get("media", "")
        try:
            media_val = float(
                str(media_raw)
                .replace("R$", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
        except:
            media_val = ""

        linha = [
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            dados.get("nome", ""),
            dados.get("email", ""),
            dados.get("whatsapp", ""),
            dados.get("origem", "").lower().strip(),
            dados.get("tipo_contato", ""),
            dados.get("origem_relacional", ""),
            dados.get("area", ""),
            dados.get("produto", ""),
            dados.get("arte", ""),
            dados.get("criacao", ""),
            dados.get("formato", ""),
            dados.get("material", ""),
            dados.get("acabamento", ""),
            dados.get("quantidade", ""),
            dados.get("urgencia", ""),
            media_val,
            dados.get("status", "handoff"),
            dados.get("avaliacao", ""),
            ""  # Observações (preenchido manualmente)
        ]

        ws_leads.append_row(linha, value_input_option="USER_ENTERED")
        print(f"[CRM] Lead salvo: {dados.get('nome')} | status: {dados.get('status')}")
        return True

    except Exception as e:
        print(f"[ERRO CRM] {e}")
        return False


def buscar_lead_por_whatsapp(numero):
    """Busca lead pelo WhatsApp para retomada de atendimento."""
    try:
        client = conectar_sheets()
        if not client:
            return None

        spreadsheet, ws_leads, _ = obter_ou_criar_planilha(client)
        celula = ws_leads.find(numero, in_column=4)

        if celula:
            linha = ws_leads.row_values(celula.row)
            return {
                "nome":         linha[1]  if len(linha) > 1  else "",
                "email":        linha[2]  if len(linha) > 2  else "",
                "whatsapp":     linha[3]  if len(linha) > 3  else "",
                "origem":       linha[4]  if len(linha) > 4  else "",
                "tipo_contato": linha[5]  if len(linha) > 5  else "",
                "area":         linha[7]  if len(linha) > 7  else "",
                "produto":      linha[8]  if len(linha) > 8  else "",
                "material":     linha[12] if len(linha) > 12 else "",
                "status":       linha[17] if len(linha) > 17 else ""
            }
        return None

    except Exception as e:
        print(f"[ERRO CRM BUSCA] {e}")
        return None


def atualizar_status_lead(numero, novo_status):
    """Atualiza o status de um lead existente."""
    try:
        client = conectar_sheets()
        if not client:
            return False

        spreadsheet, ws_leads, _ = obter_ou_criar_planilha(client)
        celula = ws_leads.find(numero, in_column=4)

        if celula:
            ws_leads.update_cell(celula.row, 18, novo_status)
            print(f"[CRM] Status atualizado: {numero} → {novo_status}")
            return True
        return False

    except Exception as e:
        print(f"[ERRO CRM UPDATE] {e}")
        return False
