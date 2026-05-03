# ═══════════════════════════════════════════════
# PRIMYN STUDIO — SERVIDOR PRINCIPAL (COMPLETO)
# ═══════════════════════════════════════════════

from flask import Flask, request, jsonify
from mily import processar_mensagem, carregar_sessoes
from zapi import enviar_mensagem, enviar_documento
from email_service import notificar_andre, enviar_confirmacao_cliente, notificar_designer
from crm import salvar_lead
from proposta_pdf import gerar_proposta
from followup import carregar_followups
from scheduler import iniciar_scheduler
import os

app = Flask(__name__)

# Iniciar scheduler de follow-ups
iniciar_scheduler()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "sistema": "Primyn Studio — Agente Mily",
        "versao": "1.0.0",
        "modulos": ["mily", "crm", "email", "pdf", "followup", "scheduler"]
    })


@app.route("/webhook/mily", methods=["POST"])
def webhook_mily():
    """Recebe mensagens do WhatsApp via Z-API"""
    try:
        dados = request.json
        
        # Ignorar mensagens enviadas por nós
        if dados.get("fromMe", False):
            return jsonify({"status": "ignored", "reason": "fromMe"}), 200
        
        # Extrair número e mensagem
        numero = dados.get("phone", "")
        mensagem = dados.get("body", "") or dados.get("text", {}).get("message", "")
        
        if not numero or not mensagem:
            return jsonify({"status": "ignored", "reason": "no_text"}), 200
        
        numero = numero.replace("@s.whatsapp.net", "").replace("@c.us", "")
        
        print(f"[RECEBIDO] {numero}: {mensagem}")
        
        # Processar com a Mily
        resposta, handoff_data = processar_mensagem(numero, mensagem)
        
        # Enviar resposta
        if resposta:
            enviar_mensagem(numero, resposta)
            print(f"[ENVIADO] {numero}: {resposta[:50]}...")
        
        # Se houve handoff
        if handoff_data:
            acionar_handoff(handoff_data)
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"[ERRO WEBHOOK] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def acionar_handoff(dados):
    """Aciona todas as automações de handoff"""
    try:
        # 1. Salvar no CRM
        salvar_lead(dados)
        print(f"[HANDOFF] CRM atualizado: {dados.get('nome')}")
        
        # 2. Gerar proposta PDF
        caminho_pdf = gerar_proposta(dados)
        print(f"[HANDOFF] PDF gerado: {caminho_pdf}")
        
        # 3. Notificar André
        notificar_andre(dados)
        print(f"[HANDOFF] André notificado")
        
        # 4. Confirmação ao cliente
        email_cliente = dados.get("email")
        nome_cliente = dados.get("nome", "").split()[0]
        if email_cliente:
            enviar_confirmacao_cliente(email_cliente, nome_cliente)
            print(f"[HANDOFF] E-mail enviado ao cliente")
        
        # 5. Notificar designer (se identidade visual)
        if dados.get("criacao") == "identidade_visual":
            notificar_designer(dados)
            print(f"[HANDOFF] Designer notificado")
        
        print(f"[HANDOFF] ✅ Completo para {dados.get('nome')}")
    
    except Exception as e:
        print(f"[ERRO HANDOFF] {e}")


@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Dashboard básico"""
    sessoes = carregar_sessoes()
    
    resumo = {
        "total_leads": len(sessoes),
        "em_qualificacao": 0,
        "aguardando": 0,
        "handoff": 0,
        "encerrado": 0,
        "leads": []
    }
    
    for numero, sessao in sessoes.items():
        status = sessao.get("dados", {}).get("status", sessao.get("etapa", ""))
        
        if status == "handoff":
            resumo["handoff"] += 1
        elif status == "aguardando_resposta":
            resumo["aguardando"] += 1
        elif status == "encerrado" or sessao.get("etapa") == "encerrado":
            resumo["encerrado"] += 1
        else:
            resumo["em_qualificacao"] += 1
        
        resumo["leads"].append({
            "numero": numero,
            "nome": sessao.get("dados", {}).get("nome", "N/A"),
            "etapa": sessao.get("etapa", "N/A"),
            "tipo": sessao.get("dados", {}).get("tipo_contato", "N/A"),
            "produto": sessao.get("dados", {}).get("produto", "N/A"),
            "ultimo_contato": sessao.get("ultimo_contato", "N/A")
        })
    
    return jsonify(resumo)


@app.route("/followups", methods=["GET"])
def ver_followups():
    """Ver follow-ups agendados"""
    return jsonify(carregar_followups())


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
