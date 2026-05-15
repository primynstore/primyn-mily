# ═══════════════════════════════════════════════
# PRIMYN STUDIO — SERVIDOR PRINCIPAL (COMPLETO)
# ═══════════════════════════════════════════════

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from mily import processar_mensagem, carregar_sessoes
from zapi import enviar_mensagem, enviar_documento
from email_service import notificar_bela, enviar_confirmacao_cliente, notificar_designer
from crm import salvar_lead
from proposta_pdf import gerar_proposta
from followup import carregar_followups
from scheduler import iniciar_scheduler
import os, json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

iniciar_scheduler()

# ═══════════════════════════════════════════════
# LISTA DE BLOQUEIO — números que a Mily ignora
# (clientes que você já está atendendo manualmente)
# ═══════════════════════════════════════════════
BLOQUEIO_FILE = "bloqueio.json"

def carregar_bloqueio():
    if os.path.exists(BLOQUEIO_FILE):
        with open(BLOQUEIO_FILE, "r") as f:
            return json.load(f)
    return []

def salvar_bloqueio(lista):
    with open(BLOQUEIO_FILE, "w") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)


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
    try:
        dados = request.json
        if dados.get("fromMe", False):
            return jsonify({"status": "ignored", "reason": "fromMe"}), 200
        numero = dados.get("phone", "")
        mensagem = dados.get("body", "") or dados.get("text", {}).get("message", "")
        if not numero or not mensagem:
            return jsonify({"status": "ignored", "reason": "no_text"}), 200
        numero = numero.replace("@s.whatsapp.net", "").replace("@c.us", "")

        # ── VERIFICAR BLOQUEIO ──────────────────────
        bloqueio = carregar_bloqueio()
        if numero in bloqueio:
            print(f"[BLOQUEADO] {numero} — Mily ignorando (atendimento manual)")
            return jsonify({"status": "blocked"}), 200

        print(f"[RECEBIDO] {numero}: {mensagem}")
        resposta, handoff_data = processar_mensagem(numero, mensagem)
        if resposta:
            enviar_mensagem(numero, resposta)
            print(f"[ENVIADO] {numero}: {resposta[:50]}...")
        if handoff_data:
            acionar_handoff(handoff_data)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"[ERRO WEBHOOK] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def acionar_handoff(dados):
    try:
        salvar_lead(dados)
        print(f"[HANDOFF] CRM atualizado: {dados.get('nome')}")
        caminho_pdf = gerar_proposta(dados)
        print(f"[HANDOFF] PDF gerado: {caminho_pdf}")
        notificar_bela(dados)
        print(f"[HANDOFF] Bela notificada")
        email_cliente = dados.get("email")
        nome_cliente = dados.get("nome", "").split()[0]
        if email_cliente:
            enviar_confirmacao_cliente(email_cliente, nome_cliente)
            print(f"[HANDOFF] E-mail enviado ao cliente")
        if dados.get("identidade_visual") == "interesse":
            notificar_designer(dados)
            print(f"[HANDOFF] Designer (Ane) notificada")
        print(f"[HANDOFF] ✅ Completo para {dados.get('nome')}")
    except Exception as e:
        print(f"[ERRO HANDOFF] {e}")


# ═══════════════════════════════════════════════
# ROTAS DE BLOQUEIO — gerenciar via API
# ═══════════════════════════════════════════════

@app.route("/bloqueio", methods=["GET"])
def ver_bloqueio():
    """Lista todos os números bloqueados."""
    return jsonify({"bloqueados": carregar_bloqueio()})

@app.route("/bloqueio/add", methods=["POST"])
def adicionar_bloqueio():
    """Bloqueia um número. Body: {"numero": "5511999999999"}"""
    numero = request.json.get("numero", "").strip()
    if not numero:
        return jsonify({"erro": "numero obrigatório"}), 400
    lista = carregar_bloqueio()
    if numero not in lista:
        lista.append(numero)
        salvar_bloqueio(lista)
    return jsonify({"status": "bloqueado", "numero": numero, "total": len(lista)})

@app.route("/bloqueio/remove", methods=["POST"])
def remover_bloqueio():
    """Desbloqueia um número. Body: {"numero": "5511999999999"}"""
    numero = request.json.get("numero", "").strip()
    lista = carregar_bloqueio()
    if numero in lista:
        lista.remove(numero)
        salvar_bloqueio(lista)
    return jsonify({"status": "desbloqueado", "numero": numero, "total": len(lista)})


# ═══════════════════════════════════════════════
# ROTAS EXISTENTES
# ═══════════════════════════════════════════════

@app.route("/dashboard", methods=["GET"])
def dashboard():
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
    return jsonify(carregar_followups())


@app.route("/painel", methods=["GET"])
def painel():
    return send_file(os.path.join(os.path.dirname(__file__), "painel_mily.html"))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/test", methods=["POST"])
def test_mily():
    d = request.json
    resp, handoff = processar_mensagem(d.get("phone", "test"), d.get("message", ""))
    return jsonify({"resposta": resp, "dados": handoff})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
