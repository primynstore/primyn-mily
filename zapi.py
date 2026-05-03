# ═══════════════════════════════════════════════
# PRIMYN STUDIO — INTEGRAÇÃO Z-API
# ═══════════════════════════════════════════════

import requests
from config import ZAPI_BASE_URL

def enviar_mensagem(numero, texto):
    """Envia mensagem de texto pelo WhatsApp via Z-API"""
    url = f"{ZAPI_BASE_URL}/send-text"
    payload = {
        "phone": numero,
        "message": texto
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[ERRO Z-API] {e}")
        return None

def enviar_documento(numero, url_documento, nome_arquivo):
    """Envia documento/PDF pelo WhatsApp via Z-API"""
    url = f"{ZAPI_BASE_URL}/send-document/{nome_arquivo}"
    payload = {
        "phone": numero,
        "document": url_documento
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[ERRO Z-API DOC] {e}")
        return None

def enviar_link(numero, titulo, descricao, link_url):
    """Envia link com preview pelo WhatsApp via Z-API"""
    url = f"{ZAPI_BASE_URL}/send-link"
    payload = {
        "phone": numero,
        "message": descricao,
        "image": "",
        "linkUrl": link_url,
        "title": titulo,
        "linkDescription": descricao
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[ERRO Z-API LINK] {e}")
        return None
