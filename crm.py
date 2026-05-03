# ═══════════════════════════════════════════════
# PRIMYN STUDIO — CRM (Google Sheets)
# ═══════════════════════════════════════════════

import os
import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

# Configuração
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
SPREADSHEET_NAME = "Primyn — CRM Leads"


def conectar_sheets():
    """Conecta ao Google Sheets"""
    try:
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"[ERRO SHEETS] Conexão falhou: {e}")
        return None


def obter_ou_criar_planilha(client):
    """Obtém ou cria a planilha do CRM"""
    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(SPREADSHEET_NAME)
        spreadsheet.share("ola@primyn.com", perm_type="user", role="writer")
        
        worksheet = spreadsheet.sheet1
        worksheet.update_title("Leads")
        cabecalhos = [
            "Data", "Nome", "E-mail", "WhatsApp", "Origem",
            "Tipo de Contato", "Origem Relacional", "Área",
            "Produto", "Arte", "Criação", "Formato",
            "Material", "Acabamento", "Quantidade",
            "Urgência", "Média Apresentada", "Status",
            "Avaliação", "Observações"
        ]
        worksheet.update("A1:T1", [cabecalhos])
        
        worksheet.format("A1:T1", {
            "backgroundColor": {"red": 0.1, "green": 0.1, "blue": 0.1},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 0.84, "blue": 0}}
        })
    
    return spreadsheet


def salvar_lead(dados):
    """Salva dados do lead na planilha"""
    try:
        client = conectar_sheets()
        if not client:
            print("[ERRO CRM] Não conectou ao Google Sheets")
            return False
        
        spreadsheet = obter_ou_criar_planilha(client)
        worksheet = spreadsheet.sheet1
        
        linha = [
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            dados.get("nome", ""),
            dados.get("email", ""),
            dados.get("whatsapp", ""),
            dados.get("origem", ""),
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
            f"R$ {dados.get('media', 0):,.2f}" if dados.get("media") else "",
            dados.get("status", "handoff"),
            dados.get("avaliacao", ""),
            ""
        ]
        
        worksheet.append_row(linha, value_input_option="USER_ENTERED")
        
        print(f"[CRM] Lead salvo: {dados.get('nome')}")
        return True
    
    except Exception as e:
        print(f"[ERRO CRM] {e}")
        return False


def buscar_lead_por_whatsapp(numero):
    """Busca lead pelo número de WhatsApp (para leads antigos)"""
    try:
        client = conectar_sheets()
        if not client:
            return None
        
        spreadsheet = obter_ou_criar_planilha(client)
        worksheet = spreadsheet.sheet1
        
        celula = worksheet.find(numero, in_column=4)
        if celula:
            linha = worksheet.row_values(celula.row)
            return {
                "nome": linha[1] if len(linha) > 1 else "",
                "email": linha[2] if len(linha) > 2 else "",
                "whatsapp": linha[3] if len(linha) > 3 else "",
                "origem": linha[4] if len(linha) > 4 else "",
                "tipo_contato": linha[5] if len(linha) > 5 else "",
                "area": linha[7] if len(linha) > 7 else "",
                "produto": linha[8] if len(linha) > 8 else "",
                "material": linha[12] if len(linha) > 12 else "",
                "status": linha[17] if len(linha) > 17 else ""
            }
        return None
    
    except Exception as e:
        print(f"[ERRO CRM BUSCA] {e}")
        return None


def atualizar_status_lead(numero, novo_status):
    """Atualiza status de um lead existente"""
    try:
        client = conectar_sheets()
        if not client:
            return False
        
        spreadsheet = obter_ou_criar_planilha(client)
        worksheet = spreadsheet.sheet1
        
        celula = worksheet.find(numero, in_column=4)
        if celula:
            worksheet.update_cell(celula.row, 18, novo_status)
            print(f"[CRM] Status atualizado: {numero} → {novo_status}")
            return True
        return False
    
    except Exception as e:
        print(f"[ERRO CRM UPDATE] {e}")
        return False
