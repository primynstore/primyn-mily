# ═══════════════════════════════════════════════
# PRIMYN STUDIO — AGENTE MILY v4 (Gemini NLU)
# Compreensão via Google Gemini (gratuito)
# ═══════════════════════════════════════════════

import json
import os
from datetime import datetime
import google.generativeai as genai

# Chave via variável de ambiente GEMINI_API_KEY
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
_model = genai.GenerativeModel("gemini-1.5-flash")

DB_FILE = "sessoes.json"

PRECOS = {
    "250":  {"essencial": 378,  "luxo_black": 562,  "luxo_white": 898,  "prestigio": 1297},
    "500":  {"essencial": 475,  "luxo_black": 839,  "luxo_white": 1284, "prestigio": 1682},
    "1000": {"essencial": 588,  "luxo_black": 1184, "luxo_white": 1568, "prestigio": 2567}
}

PAPEIS_POR_AREA = {
    "advocacia":   "Notturno Black 450g / Dark Blue / Rives White",
    "direito":     "Notturno Black 450g / Dark Blue / Rives White",
    "financas":    "Notturno Black 450g / Dark Blue / Rives White",
    "executivo":   "Notturno Black 450g / Dark Blue / Rives White",
    "arquitetura": "Rives Natural White 400g / Conqueror Bamboo 400g",
    "engenharia":  "Rives Natural White 400g / Conqueror Bamboo 400g",
    "design":      "Rives Natural White 400g / Conqueror Bamboo 400g",
    "moda":        "Color Plus / Rives White",
    "beleza":      "Color Plus / Rives White",
    "lifestyle":   "Color Plus / Rives White",
    "medicina":    "Rives Trad. White / Conqueror Bamboo 400g",
    "saude":       "Rives Trad. White / Conqueror Bamboo 400g"
}

MSG_EDUCATIVA = (
    "👑 Antes de encerrarmos, um pensamento que vale levar:\n\n"
    "Materiais de papelaria premium não são apenas papel — eles são o primeiro toque "
    "físico que o seu cliente tem com a sua marca. Um cartão com textura, acabamento "
    "em hot stamping ou baixo relevo transmite sofisticação antes mesmo de qualquer "
    "palavra ser dita. Estudos de comportamento do consumidor mostram que materiais "
    "de alta qualidade aumentam em até 3x a percepção de valor de uma marca. "
    "Você não entrega um cartão — você entrega uma experiência.\n\n"
    "Sua marca merece deixar essa impressão. 🤍"
)

# ═══════════════════════════════════════════════
# INTERPRETAÇÃO VIA GEMINI
# ═══════════════════════════════════════════════

def interpretar(mensagem: str, contexto: str, opcoes: list) -> str:
    opcoes_str = " | ".join(opcoes)
    prompt = (
        f"Você é um classificador de intenção para atendimento em português.\n"
        f"Contexto: {contexto}\n"
        f"Mensagem do cliente: \"{mensagem}\"\n"
        f"Classifique em UMA opção: {opcoes_str}\n"
        f"Responda APENAS com uma das opções, sem explicação."
    )
    try:
        resp = _model.generate_content(prompt)
        resultado = resp.text.strip().lower()
        for op in opcoes:
            if op.lower() in resultado:
                return op
        return opcoes[-1]
    except Exception as e:
        print(f"[GEMINI] Erro: {e}")
        return opcoes[-1]


def extrair_nome(mensagem: str) -> str:
    prompt = (
        f"Extraia o nome completo (nome e sobrenome) da mensagem abaixo.\n"
        f"Se houver nome e sobrenome, responda APENAS com 'Nome Sobrenome'.\n"
        f"Se houver só primeiro nome ou nenhum nome, responda APENAS: INVALIDO\n"
        f"Mensagem: \"{mensagem}\""
    )
    try:
        resp = _model.generate_content(prompt)
        resultado = resp.text.strip()
        if "INVALIDO" in resultado.upper() or len(resultado.split()) < 2:
            return None
        return resultado.title()
    except Exception as e:
        print(f"[GEMINI NOME] Erro: {e}")
        partes = [p for p in mensagem.strip().split() if len(p) > 1]
        if len(partes) >= 2:
            return " ".join(p.title() for p in partes)
        return None


# ═══════════════════════════════════════════════
# SESSÕES
# ═══════════════════════════════════════════════

def carregar_sessoes():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_sessoes(sessoes):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(sessoes, f, ensure_ascii=False, indent=2)

def obter_sessao(numero):
    sessoes = carregar_sessoes()
    if numero not in sessoes:
        sessoes[numero] = {
            "etapa": "abertura",
            "fluxo": None,
            "dados": {
                "whatsapp": numero,
                "data_primeiro_contato": datetime.now().isoformat()
            },
            "ultimo_contato": datetime.now().isoformat()
        }
        salvar_sessoes(sessoes)
    return sessoes[numero]

def atualizar_sessao(numero, sessao):
    sessoes = carregar_sessoes()
    sessao["ultimo_contato"] = datetime.now().isoformat()
    sessoes[numero] = sessao
    salvar_sessoes(sessoes)

def calcular_media(material, quantidade):
    qtd_str = "250"
    try:
        qtd_num = int(''.join(filter(str.isdigit, str(quantidade))))
        if qtd_num <= 375:   qtd_str = "250"
        elif qtd_num <= 750: qtd_str = "500"
        else:                qtd_str = "1000"
    except:
        qtd_str = "250"

    m = (material or "").lower()
    if "couche" in m or "couchê" in m:    tier = "essencial"
    elif "black" in m or "notturno" in m: tier = "luxo_black"
    elif "white" in m or "rives" in m:    tier = "luxo_white"
    elif "450" in m or "prestigio" in m:  tier = "prestigio"
    else:                                  tier = "luxo_white"

    return PRECOS.get(qtd_str, {}).get(tier, 898)


# ═══════════════════════════════════════════════
# PROCESSAMENTO PRINCIPAL
# ═══════════════════════════════════════════════

def processar_mensagem(numero, mensagem):
    sessao       = obter_sessao(numero)
    etapa        = sessao["etapa"]
    dados        = sessao["dados"]
    msg          = mensagem.strip()
    resposta     = ""
    handoff_data = None

    if etapa == "abertura":
        resposta = (
            "😊 Olá! Seja muito bem-vindo(a) à Primyn.\n\n"
            "Sou a Mily, consultora virtual da Primyn. Vou entender o que você procura "
            "e direcionar seu atendimento da forma mais estratégica possível. "
            "Ao final, um especialista dará continuidade para garantir que cada detalhe "
            "fique exatamente como você imagina.\n\n"
            "Para começarmos, você é cliente da Primyn ou é sua primeira vez por aqui?"
        )
        sessao["etapa"] = "triagem_inicial"

    elif etapa == "triagem_inicial":
        intencao = interpretar(
            msg,
            "O cliente está respondendo se já é cliente, se é a primeira vez, ou se já falou antes.",
            ["ja_sou_cliente", "primeira_vez", "ja_falei_antes"]
        )
        if intencao == "ja_sou_cliente":
            dados["tipo_contato"] = "cliente_recorrente"
            dados["origem_relacional"] = "recompra"
            sessao["fluxo"] = "cliente_recorrente"
            resposta = (
                "Que bom te ver de volta! 😊\n\n"
                "Para localizar seu cadastro e agilizar seu novo pedido, "
                "pode me informar seu nome e sobrenome completo?"
            )
        elif intencao == "ja_falei_antes":
            dados["tipo_contato"] = "lead_antigo"
            dados["origem_relacional"] = "retorno"
            sessao["fluxo"] = "lead_antigo"
            resposta = (
                "Que bom que voltou! 😊\n\n"
                "Para localizar seu histórico, pode me dizer seu nome e sobrenome completo?"
            )
        else:
            dados["tipo_contato"] = "novo_lead"
            dados["origem_relacional"] = "primeira_vez"
            sessao["fluxo"] = "novo_lead"
            resposta = (
                "Seja muito bem-vindo(a)! ✨ "
                "Para personalizarmos seu atendimento, pode me dizer seu nome e sobrenome completo?"
            )
        sessao["etapa"] = "nome"

    elif etapa == "nome":
        nome_extraido = extrair_nome(msg)
        if not nome_extraido:
            resposta = (
                "Para encontrar seu cadastro com precisão, preciso do seu nome e sobrenome completo. "
                "Como posso te chamar?"
            )
        else:
            dados["nome"] = nome_extraido
            primeiro = nome_extraido.split()[0]
            fluxo = sessao.get("fluxo")

            if fluxo == "cliente_recorrente":
                resposta = (
                    f"Perfeito, {primeiro} 😊 Já te localizo aqui no sistema.\n\n"
                    f"Me conta: qual material você gostaria de produzir desta vez?"
                )
                sessao["etapa"] = "produto"
            elif fluxo == "lead_antigo":
                resposta = (
                    f"Ótimo, {primeiro} 😊 Encontrei seu histórico.\n\n"
                    f"Você prefere retomar o projeto anterior ou começar algo novo?"
                )
                sessao["etapa"] = "retomar_ou_novo"
            else:
                resposta = f"Prazer, {primeiro}! ✨ Como você conheceu a Primyn?"
                sessao["etapa"] = "origem"

    elif etapa == "origem":
        dados["origem"] = msg
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Que ótimo que nos encontrou por lá! 🚀\n\n"
            f"Qual é o seu melhor e-mail, {primeiro}?"
        )
        sessao["etapa"] = "email"

    elif etapa == "retomar_ou_novo":
        primeiro = dados.get("nome", "").split()[0]
        intencao = interpretar(
            msg,
            "O cliente quer retomar projeto anterior ou começar projeto novo.",
            ["retomar", "novo_projeto"]
        )
        if intencao == "novo_projeto":
            sessao["fluxo"] = "novo_lead"
            resposta = (
                f"Perfeito, {primeiro} ✨ Vamos começar algo novo!\n\n"
                f"Qual é o seu melhor e-mail?"
            )
            sessao["etapa"] = "email"
        else:
            resposta = (
                f"Perfeito, {primeiro} 👑 Vou retomar exatamente de onde paramos.\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Em breve um especialista dará continuidade. 😊"
            )
            dados["status"] = "handoff"
            sessao["etapa"] = "handoff"
            handoff_data = dados

    elif etapa == "email":
        dados["email"] = msg.strip()
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Perfeito, {primeiro} ✨ Qual projeto você gostaria de produzir? "
            f"Cartão de visita, papel timbrado, papelaria completa, convite ou outro material?"
        )
        sessao["etapa"] = "produto"

    elif etapa == "produto":
        dados["produto"] = msg
        primeiro = dados.get("nome", "").split()[0]
        if sessao.get("fluxo") == "cliente_recorrente":
            resposta = (
                f"Ótima escolha, {primeiro} 👑 "
                f"Você já tem a arte pronta ou precisa que a gente desenvolva algo novo?"
            )
            sessao["etapa"] = "arte"
        else:
            resposta = (
                f"Ótima escolha, {primeiro} ✨ "
                f"Em qual área você atua?"
            )
            sessao["etapa"] = "area"

    elif etapa == "area":
        dados["area"] = msg
        primeiro = dados.get("nome", "").split()[0]
        for chave, valor in PAPEIS_POR_AREA.items():
            if chave in msg.lower():
                dados["papel_recomendado"] = valor
                break
        resposta = (
            f"{msg.title()} — uma área que exige sofisticação em cada detalhe. 👑\n\n"
            f"Você já possui a arte finalizada, tem alguma referência "
            f"ou vai precisar de criação?"
        )
        sessao["etapa"] = "arte"

    elif etapa == "arte":
        primeiro = dados.get("nome", "").split()[0]
        intencao = interpretar(
            msg,
            "O cliente está respondendo sobre a arte do projeto gráfico.",
            ["arte_pronta", "precisa_criacao", "identidade_visual"]
        )
        if intencao == "arte_pronta":
            dados["arte"] = "pronta_ou_referencia"
            resposta = (
                f"Perfeito, {primeiro} ✨ Pode me enviar sua arte ou referência? "
                f"Assim consigo direcionar sua cotação com mais precisão."
            )
            sessao["etapa"] = "arte_detalhe"
        elif intencao == "identidade_visual":
            dados["arte"] = "identidade_visual"
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
            if dados.get("email"):
                resposta = (
                    f"Perfeito, {primeiro} 👑 Identidade visual é um projeto especial — "
                    f"vou encaminhar para a nossa designer Ane.\n\n"
                    f"{MSG_EDUCATIVA}\n\n"
                    f"Em breve ela entrará em contato. 😊"
                )
                dados["status"] = "handoff_designer"
                sessao["etapa"] = "handoff"
                handoff_data = dados
            else:
                resposta = (
                    f"Perfeito, {primeiro} 👑 Vou encaminhar para a nossa designer Ane. "
                    f"Qual é o seu melhor e-mail?"
                )
                sessao["etapa"] = "email_design"
        else:
            dados["arte"] = "precisa_criacao"
            resposta = (
                f"Sem problema, {primeiro} 🚀 Podemos desenvolver para você:\n\n"
                f"• Criação de arte — R$ 74,90\n"
                f"• Criação de cartão 3D — R$ 120,00\n"
                f"• Identidade visual / logomarca\n\n"
                f"Qual faz mais sentido para o seu projeto?"
            )
            sessao["etapa"] = "arte_opcao"

    elif etapa == "email_design":
        dados["email"] = msg.strip()
        primeiro = dados.get("nome", "").split()[0]
        dados["status"] = "handoff_designer"
        resposta = (
            f"Perfeito, {primeiro} ✨ Ane entrará em contato em breve.\n\n"
            f"{MSG_EDUCATIVA}\n\n"
            f"Foi um prazer te atender! 😊"
        )
        sessao["etapa"] = "handoff"
        handoff_data = dados

    elif etapa == "arte_opcao":
        primeiro = dados.get("nome", "").split()[0]
        intencao = interpretar(
            msg,
            "O cliente escolhe entre criação de arte simples (R$74,90), cartão 3D (R$120) ou identidade visual.",
            ["criacao_simples", "cartao_3d", "identidade_visual"]
        )
        if intencao == "identidade_visual":
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
            resposta = (
                f"Perfeito, {primeiro} 👑 Vou encaminhar para a nossa designer Ane.\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Em breve ela entrará em contato. 😊"
            )
            dados["status"] = "handoff_designer"
            sessao["etapa"] = "handoff"
            handoff_data = dados
        elif intencao == "cartao_3d":
            dados["criacao"] = "cartao_3d"
            dados["valor_criacao"] = 120.00
            resposta = f"Ótima escolha! 🚀 Qual formato? 5x9 cm, 5x8 cm ou personalizado?"
            sessao["etapa"] = "arte_detalhe"
        else:
            dados["criacao"] = "criacao_arte"
            dados["valor_criacao"] = 74.90
            resposta = f"Perfeito 😊 Qual formato? 5x9 cm (tradicional), 5x8 cm (americano) ou personalizado?"
            sessao["etapa"] = "arte_detalhe"

    elif etapa == "arte_detalhe":
        dados["arte_detalhe"] = msg
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Perfeito, {primeiro} 😊 Qual formato para o seu projeto? "
            f"5x9 cm (tradicional), 5x8 cm (americano) ou personalizado?"
        )
        sessao["etapa"] = "formato"

    elif etapa == "formato":
        dados["formato"] = msg
        resposta = (
            f"Perfeito ✨ Qual papel faz mais sentido: "
            f"Couchê 300g, texturado até 400g ou texturado acima de 400g?"
        )
        sessao["etapa"] = "papel"

    elif etapa == "papel":
        dados["material"] = msg
        primeiro = dados.get("nome", "").split()[0]
        if "couche" in msg.lower() or "couchê" in msg.lower() or "300" in msg:
            resposta = (
                f"O Couchê 300g é nossa opção de entrada — e para refletir o padrão Primyn, "
                f"trabalhamos com hot stamping ou baixo relevo obrigatoriamente. 👑\n\n"
                f"Qual acabamento prefere, ou quer explorar nossos papéis texturados?"
            )
            sessao["etapa"] = "papel_couche_validar"
        else:
            resposta = (
                f"Perfeito, {primeiro} ✨ Qual acabamento faz mais sentido:\n\n"
                f"• Hot stamping\n"
                f"• Alto relevo seco\n"
                f"• Baixo relevo\n"
                f"• Empastamento / borda sanduíche\n"
                f"• Impressão colorida no papel especial\n"
                f"• Combinação de acabamentos"
            )
            sessao["etapa"] = "acabamento"

    elif etapa == "papel_couche_validar":
        primeiro = dados.get("nome", "").split()[0]
        intencao = interpretar(
            msg,
            "O cliente responde sobre acabamento do Couchê 300g.",
            ["quer_texturado", "recusa_acabamento", "escolheu_acabamento"]
        )
        if intencao == "quer_texturado":
            dados["material"] = "texturado"
            resposta = f"Perfeito, {primeiro} ✨ Texturado até 400g ou acima de 400g?"
            sessao["etapa"] = "papel"
        elif intencao == "recusa_acabamento":
            resposta = (
                f"Entendemos, {primeiro}. "
                f"Quando quiser explorar uma proposta premium, estaremos por aqui 😊"
            )
            dados["status"] = "fora_escopo"
            sessao["etapa"] = "encerrado"
        else:
            dados["acabamento"] = msg
            resposta = f"Perfeito, {primeiro} ✨ Qual quantidade você está considerando?"
            sessao["etapa"] = "quantidade"

    elif etapa == "acabamento":
        dados["acabamento"] = msg
        primeiro = dados.get("nome", "").split()[0]
        resposta = f"Perfeito, {primeiro} ✨ Qual quantidade você está considerando?"
        sessao["etapa"] = "quantidade"

    elif etapa == "quantidade":
        dados["quantidade"] = msg
        primeiro = dados.get("nome", "").split()[0]
        try:
            media = calcular_media(dados.get("material", ""), msg)
        except:
            media = 898
        valor_criacao = dados.get("valor_criacao", 0)
        if valor_criacao:
            media += valor_criacao
        dados["media"] = media
        media_fmt = f"R$ {media:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        resposta = (
            f"Perfeito, {primeiro} 🚀 Para a configuração que você me passou, "
            f"o investimento médio fica em torno de {media_fmt}. "
            f"O orçamento final é personalizado conforme material, acabamento e complexidade. 👑\n\n"
            f"Faz sentido prosseguirmos com uma proposta personalizada?"
        )
        sessao["etapa"] = "media_proposta"

    elif etapa == "media_proposta":
        primeiro = dados.get("nome", "").split()[0]
        intencao = interpretar(
            msg,
            "O cliente responde se quer prosseguir com a proposta.",
            ["sim_quero", "precisa_pensar", "nao_quero"]
        )
        if intencao == "sim_quero":
            resposta = f"Perfeito ✨ Você tem algum prazo importante para receber esse material?"
            sessao["etapa"] = "urgencia"
        elif intencao == "nao_quero":
            resposta = (
                f"Sem problema, {primeiro} 😊 Agradeço pelo seu tempo. "
                f"Fico à disposição quando quiser retomar!"
            )
            dados["status"] = "perdido"
            sessao["etapa"] = "encerrado"
        else:
            resposta = (
                f"Claro, {primeiro} 😊 Sem pressa. Quando quiser retomar, estaremos por aqui. "
                f"Acompanhe em @primyn.store 🚀"
            )
            dados["status"] = "aguardando_resposta"
            sessao["etapa"] = "encerrado"
            try:
                from followup import agendar_followup
                agendar_followup(numero, dados.get("nome", ""), "pensar", dias=2)
            except:
                pass

    elif etapa == "urgencia":
        dados["urgencia"] = msg
        primeiro = dados.get("nome", "").split()[0]
        intencao = interpretar(
            msg,
            "O cliente informa se o projeto é urgente ou não.",
            ["urgente", "sem_pressa"]
        )
        aviso = ""
        if intencao == "urgente":
            aviso = "Projetos premium têm prazo médio de 5 a 8 dias úteis. Vou sinalizar no encaminhamento. 🚀\n\n"
        resposta = (
            f"{aviso}"
            f"{MSG_EDUCATIVA}\n\n"
            f"😊 Vou encaminhar seu projeto para uma proposta personalizada. "
            f"Em breve um especialista dará continuidade, {primeiro}. ✨"
        )
        dados["status"] = "handoff"
        sessao["etapa"] = "handoff"
        handoff_data = dados

    elif etapa == "handoff":
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Antes de encerrar, {primeiro} 😊 "
            f"como foi sua experiência com este atendimento?"
        )
        sessao["etapa"] = "feedback"

    elif etapa == "feedback":
        dados["avaliacao"] = msg
        primeiro = dados.get("nome", "").split()[0]
        resposta = f"Muito obrigada, {primeiro}! 🤍 Foi um prazer te atender. Até breve! 😊"
        sessao["etapa"] = "encerrado"

    elif etapa == "encerrado":
        primeiro = dados.get("nome", "").split()[0] if dados.get("nome") else ""
        resposta = (
            f"Olá novamente, {primeiro}! 😊 Quer retomar ou precisa de algo mais? ✨"
            if primeiro else
            "Olá! 😊 Seja muito bem-vindo(a) de volta à Primyn. Como posso te ajudar?"
        )
        sessao["etapa"] = "produto"

    else:
        resposta = (
            "😊 Olá! Seja muito bem-vindo(a) à Primyn.\n\n"
            "Sou a Mily. Como posso te ajudar?"
        )
        sessao["etapa"] = "triagem_inicial"

    sessao["dados"] = dados
    atualizar_sessao(numero, sessao)
    return resposta, handoff_data
