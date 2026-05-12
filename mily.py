# ═══════════════════════════════════════════════
# PRIMYN STUDIO — AGENTE MILY v4 (Gemini NLU)
# Compreensão via Google Gemini (gratuito)
# ═══════════════════════════════════════════════


        # ═══════════════════════════════════════════════
# PRIMYN STUDIO — AGENTE MILY v4 (Claude Haiku)
# Compreensão via Anthropic Claude Haiku
# ═══════════════════════════════════════════════


# ═══════════════════════════════════════════════
# PRIMYN STUDIO — AGENTE MILY v5 FINAL
# Claude Haiku NLU + catálogo completo Primyn
# Emojis apenas no final das frases
# ═══════════════════════════════════════════════

# ═══════════════════════════════════════════════
# PRIMYN STUDIO — AGENTE MILY v5 FINAL
# Claude Haiku NLU + catálogo completo Primyn
# Emojis apenas no final das frases
# ═══════════════════════════════════════════════

import json
import os
from datetime import datetime
import anthropic

_claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
DB_FILE = "sessoes.json"

# ═══════════════════════════════════════════════
# CATÁLOGO COMPLETO PRIMYN
# ═══════════════════════════════════════════════

PRODUTOS = {
    "cartao_visita": {
        "nome": "Cartão de Visita",
        "minimo": 250,
        "formatos": "5×9 cm (tradicional), 5×8 cm (americano) ou personalizado",
        "aceita_3d": True,
        "media_entrada": "R$ 378,00",
        "medias": {
            "250":  {"essencial": 378,  "luxo_black": 562,  "luxo_white": 898,  "prestigio": 1297},
            "500":  {"essencial": 475,  "luxo_black": 839,  "luxo_white": 1284, "prestigio": 1682},
            "1000": {"essencial": 588,  "luxo_black": 1184, "luxo_white": 1568, "prestigio": 2567}
        }
    },
    "tag": {
        "nome": "Tag / Cartão de Agradecimento",
        "minimo": 250,
        "formatos": "5×9 cm (tradicional), 5×8 cm (americano) ou personalizado",
        "aceita_3d": True,
        "media_entrada": "R$ 378,00",
        "medias": {
            "250":  {"essencial": 378,  "luxo_black": 562,  "luxo_white": 898,  "prestigio": 1297},
            "500":  {"essencial": 475,  "luxo_black": 839,  "luxo_white": 1284, "prestigio": 1682},
            "1000": {"essencial": 588,  "luxo_black": 1184, "luxo_white": 1568, "prestigio": 2567}
        }
    },
    "timbrado": {
        "nome": "Papel Timbrado / Receituário",
        "minimo": 250,
        "formatos": "A4 (29,7×21 cm) ou A5 (15×20 cm)",
        "aceita_3d": False,
        "media_entrada": "R$ 650,00",
        "medias": {
            "250":  {"essencial": 650,  "luxo_black": 650,  "luxo_white": 650,  "prestigio": 650},
            "500":  {"essencial": 890,  "luxo_black": 890,  "luxo_white": 890,  "prestigio": 890},
            "1000": {"essencial": 1190, "luxo_black": 1190, "luxo_white": 1190, "prestigio": 1190}
        }
    },
    "pasta": {
        "nome": "Pasta",
        "minimo": 100,
        "formatos": "31×22 cm (fechada) — tipo bolsa ou orelha",
        "aceita_3d": False,
        "media_entrada": "R$ 2.500,00",
        "medias": {
            "100": {"essencial": 2500, "luxo_black": 2500, "luxo_white": 2500, "prestigio": 2500},
            "250": {"essencial": 3800, "luxo_black": 3800, "luxo_white": 3800, "prestigio": 3800},
            "500": {"essencial": 5500, "luxo_black": 5500, "luxo_white": 5500, "prestigio": 5500}
        }
    },
    "envelope_oficio": {
        "nome": "Envelope Ofício",
        "minimo": 100,
        "formatos": "11,4×22,9 cm (padrão ofício)",
        "aceita_3d": False,
        "media_entrada": "R$ 720,00",
        "medias": {
            "100": {"essencial": 720,  "luxo_black": 720,  "luxo_white": 720,  "prestigio": 720},
            "250": {"essencial": 1050, "luxo_black": 1050, "luxo_white": 1050, "prestigio": 1050},
            "500": {"essencial": 1590, "luxo_black": 1590, "luxo_white": 1590, "prestigio": 1590}
        }
    },
    "envelope_saco": {
        "nome": "Envelope Saco",
        "minimo": 100,
        "formatos": "22,9×32,4 cm (padrão saco)",
        "aceita_3d": False,
        "media_entrada": "R$ 720,00",
        "medias": {
            "100": {"essencial": 720,  "luxo_black": 720,  "luxo_white": 720,  "prestigio": 720},
            "250": {"essencial": 1050, "luxo_black": 1050, "luxo_white": 1050, "prestigio": 1050},
            "500": {"essencial": 1590, "luxo_black": 1590, "luxo_white": 1590, "prestigio": 1590}
        }
    },
    "papelaria_completa": {
        "nome": "Papelaria Completa",
        "minimo": 250,
        "formatos": "variável conforme composição do kit",
        "aceita_3d": False,
        "media_entrada": "R$ 4.200,00",
        "medias": {
            "250": {"essencial": 4200, "luxo_black": 4200, "luxo_white": 5800, "prestigio": 5800},
            "500": {"essencial": 5800, "luxo_black": 5800, "luxo_white": 7500, "prestigio": 7500}
        }
    }
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
    "Antes de encerrarmos, um pensamento que vale levar:\n\n"
    "Materiais de papelaria premium não são apenas papel — eles são o primeiro toque "
    "físico que o seu cliente tem com a sua marca. Um cartão com textura, acabamento "
    "em hot stamping ou baixo relevo transmite sofisticação antes mesmo de qualquer "
    "palavra ser dita. Estudos mostram que materiais de alta qualidade aumentam em até "
    "3x a percepção de valor de uma marca. Você não entrega um cartão — você entrega "
    "uma experiência. 👑\n\n"
    "Sua marca merece deixar essa impressão. 🤍"
)

MSG_UPSELL_PAPELARIA = (
    "Uma observação importante: clientes que investem em papelaria completa — "
    "cartão de visita, papel timbrado, pasta e envelope com a mesma identidade — "
    "transmitem uma coerência visual que multiplica a percepção de valor da marca. "
    "É a diferença entre parecer profissional e ser reconhecido como premium. 👑\n\n"
    "A Primyn oferece kits completos a partir de R$ 4.200,00 no Couchê e "
    "R$ 5.800,00 em papel especial, podendo variar conforme composição e acabamentos.\n\n"
    "Gostaria de conhecer essa opção ou prefere seguir só com o cartão por enquanto?"
)

# ═══════════════════════════════════════════════
# CLAUDE HAIKU — INTERPRETAÇÃO
# ═══════════════════════════════════════════════

def interpretar(mensagem: str, contexto: str, opcoes: list) -> str:
    opcoes_str = " | ".join(opcoes)
    prompt = (
        f"Classificador de intenção em português.\n"
        f"Contexto: {contexto}\n"
        f"Mensagem: \"{mensagem}\"\n"
        f"Classifique em UMA opção: {opcoes_str}\n"
        f"Responda APENAS com uma das opções."
    )
    try:
        resp = _claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}]
        )
        resultado = resp.content[0].text.strip().lower()
        for op in opcoes:
            if op.lower() in resultado:
                return op
        return opcoes[-1]
    except Exception as e:
        print(f"[CLAUDE] Erro: {e}")
        return opcoes[-1]


def identificar_produto(mensagem: str) -> str:
    prompt = (
        f"Identifique o produto de papelaria mencionado.\n"
        f"Mensagem: \"{mensagem}\"\n"
        f"Opções: cartao_visita | tag | timbrado | pasta | envelope_oficio | envelope_saco | papelaria_completa | nao_identificado\n"
        f"Exemplos: 'cartão de visita'=cartao_visita, 'timbrado'=timbrado, "
        f"'receituário'=timbrado, 'pasta'=pasta, 'envelope ofício'=envelope_oficio, "
        f"'envelope saco'=envelope_saco, 'tag'=tag, 'agradecimento'=tag, "
        f"'kit completo'=papelaria_completa, 'papelaria completa'=papelaria_completa, "
        f"'mesmo de antes'=nao_identificado, 'não sei'=nao_identificado\n"
        f"Responda APENAS com uma das opções."
    )
    try:
        resp = _claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}]
        )
        resultado = resp.content[0].text.strip().lower()
        for key in PRODUTOS:
            if key in resultado:
                return key
        return "nao_identificado"
    except Exception as e:
        print(f"[CLAUDE PRODUTO] Erro: {e}")
        return "nao_identificado"


def extrair_e_validar(mensagem: str, tipo: str) -> tuple:
    if tipo == "nome":
        prompt = (
            f"Extraia o nome completo (nome e sobrenome) da mensagem.\n"
            f"Se houver nome E sobrenome válidos: responda VALIDO: Nome Sobrenome\n"
            f"Se houver só primeiro nome ou apelido: responda INVALIDO\n"
            f"Mensagem: \"{mensagem}\""
        )
        max_tok = 50
    else:
        prompt = (
            f"Verifique se há e-mail válido (formato: texto@dominio.extensao).\n"
            f"Se válido: responda VALIDO: email@dominio.com\n"
            f"Se inválido: responda INVALIDO\n"
            f"Mensagem: \"{mensagem}\""
        )
        max_tok = 60
    try:
        resp = _claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tok,
            messages=[{"role": "user", "content": prompt}]
        )
        resultado = resp.content[0].text.strip()
        if resultado.upper().startswith("VALIDO:"):
            valor = resultado.split(":", 1)[1].strip()
            return True, valor.title() if tipo == "nome" else valor.lower()
        return False, None
    except Exception as e:
        print(f"[CLAUDE VALIDAR] Erro: {e}")
        if tipo == "nome":
            partes = [p for p in mensagem.strip().split() if len(p) > 1]
            if len(partes) >= 2:
                return True, " ".join(p.title() for p in partes)
        elif "@" in mensagem and "." in mensagem:
            return True, mensagem.strip().lower()
        return False, None


def calcular_media(produto_key: str, material: str, quantidade: str) -> float:
    produto = PRODUTOS.get(produto_key)
    if not produto or not produto["medias"]:
        return 0

    try:
        qtd = int(''.join(filter(str.isdigit, str(quantidade))))
    except:
        qtd = produto.get("minimo") or 250

    medias = produto["medias"]
    faixas = sorted([int(k) for k in medias.keys()])
    qtd_str = str(faixas[0])
    for f in faixas:
        if qtd >= f:
            qtd_str = str(f)

    m = (material or "").lower()
    if "couche" in m or "couchê" in m:    tier = "essencial"
    elif "black" in m or "notturno" in m: tier = "luxo_black"
    elif "white" in m or "rives" in m:    tier = "luxo_white"
    elif "450" in m or "prestigio" in m:  tier = "prestigio"
    else:                                  tier = "luxo_white"

    return medias.get(qtd_str, {}).get(tier, 0)


def fmt_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


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
            "etapa": "abertura", "fluxo": None,
            "dados": {"whatsapp": numero, "data_primeiro_contato": datetime.now().isoformat()},
            "ultimo_contato": datetime.now().isoformat()
        }
        salvar_sessoes(sessoes)
    return sessoes[numero]

def atualizar_sessao(numero, sessao):
    sessoes = carregar_sessoes()
    sessao["ultimo_contato"] = datetime.now().isoformat()
    sessoes[numero] = sessao
    salvar_sessoes(sessoes)


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
            "Olá! Seja muito bem-vindo(a) à Primyn. 😊\n\n"
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
            "O cliente responde se já é cliente da Primyn, se é a primeira vez, ou se já falou antes.",
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
                "Seja muito bem-vindo(a) à Primyn! ✨\n\n"
                "Para personalizarmos seu atendimento, pode me dizer seu nome e sobrenome completo?"
            )
        sessao["etapa"] = "nome"

    elif etapa == "nome":
        valido, nome_extraido = extrair_e_validar(msg, "nome")
        if not valido:
            resposta = (
                "Para encontrar seu cadastro com precisão, preciso do seu nome "
                "e sobrenome completo. Como posso te chamar? 😊"
            )
        else:
            dados["nome"] = nome_extraido
            primeiro = nome_extraido.split()[0]
            fluxo = sessao.get("fluxo")
            if fluxo == "cliente_recorrente":
                resposta = (
                    f"Que prazer, {primeiro}! Já te localizo aqui no sistema. 😊\n\n"
                    f"Me conta: qual material você gostaria de produzir desta vez?"
                )
                sessao["etapa"] = "produto"
            elif fluxo == "lead_antigo":
                resposta = (
                    f"Encontrei seu histórico, {primeiro}! 😊\n\n"
                    f"Você prefere retomar o projeto anterior ou começar algo novo?"
                )
                sessao["etapa"] = "retomar_ou_novo"
            else:
                resposta = (
                    f"Prazer, {primeiro}! ✨\n\n"
                    f"Como você conheceu a Primyn?"
                )
                sessao["etapa"] = "origem"

    elif etapa == "origem":
        dados["origem"] = msg
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Que ótimo que nos encontrou por lá! 🚀\n\n"
            f"Para encaminharmos sua proposta de investimento, "
            f"qual é o seu melhor e-mail, {primeiro}?"
        )
        sessao["etapa"] = "email"

    elif etapa == "email":
        valido, email_extraido = extrair_e_validar(msg, "email")
        if not valido:
            resposta = (
                "Esse e-mail não parece válido. "
                "Pode me passar seu endereço completo? Ex: seunome@gmail.com 😊"
            )
        else:
            dados["email"] = email_extraido
            primeiro = dados.get("nome", "").split()[0]
            resposta = (
                f"Perfeito, {primeiro}! ✨\n\n"
                f"Qual projeto você gostaria de produzir?\n\n"
                f"• Cartão de visita\n"
                f"• Tag / Cartão de agradecimento\n"
                f"• Papel timbrado / Receituário\n"
                f"• Pasta\n"
                f"• Envelope (ofício ou saco)\n"
                f"• Papelaria completa (kit)"
            )
            sessao["etapa"] = "produto"

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
                f"Vamos começar algo novo e especial, {primeiro}! ✨\n\n"
                f"Qual é o seu melhor e-mail?"
            )
            sessao["etapa"] = "email"
        else:
            resposta = (
                f"Vou retomar exatamente de onde paramos, {primeiro}.\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Em breve um especialista dará continuidade ao seu atendimento."
            )
            dados["status"] = "handoff"
            sessao["etapa"] = "handoff"
            handoff_data = dados

    elif etapa == "produto":
        primeiro = dados.get("nome", "").split()[0]
        produto_key = identificar_produto(msg)

        if produto_key == "nao_identificado":
            resposta = (
                f"Para prepararmos a melhor proposta para você, {primeiro}, "
                f"qual produto você gostaria?\n\n"
                f"• Cartão de visita\n"
                f"• Tag / Cartão de agradecimento\n"
                f"• Papel timbrado / Receituário\n"
                f"• Pasta\n"
                f"• Envelope (ofício ou saco)\n"
                f"• Papelaria completa (kit)"
            )
        else:
            produto = PRODUTOS[produto_key]
            dados["produto"] = produto["nome"]
            dados["produto_key"] = produto_key
            dados["upsell_feito"] = False

            if produto_key == "papelaria_completa":
                if dados.get("email"):
                    resposta = (
                        f"Papelaria completa é um projeto especial, {primeiro}. 👑\n\n"
                        f"O kit inclui cartão de visita, papel timbrado, pasta e envelope "
                        f"com a mesma identidade visual — transmitindo coerência e sofisticação "
                        f"em cada ponto de contato da sua marca.\n\n"
                        f"O investimento parte de R$ 4.200,00 no Couchê e R$ 5.800,00 em papel especial, "
                        f"variando conforme composição e acabamentos.\n\n"
                        f"Em breve um especialista entrará em contato para montar a proposta ideal."
                    )
                    dados["status"] = "handoff"
                    sessao["etapa"] = "handoff"
                    handoff_data = dados
                else:
                    resposta = (
                        f"Papelaria completa é um projeto especial, {primeiro}. 👑\n\n"
                        f"O kit parte de R$ 4.200,00 no Couchê e R$ 5.800,00 em papel especial.\n\n"
                        f"Para preparar a proposta ideal, qual é o seu melhor e-mail?"
                    )
                    sessao["etapa"] = "email"
            else:
                resposta = (
                    f"Ótima escolha! ✨\n\n"
                    f"Para {produto['nome']}, trabalhamos com o formato {produto['formatos']}.\n\n"
                    f"Esse formato atende ao seu projeto ou prefere algo personalizado?"
                )
                sessao["etapa"] = "confirmar_formato"

    elif etapa == "confirmar_formato":
        primeiro = dados.get("nome", "").split()[0]
        produto_key = dados.get("produto_key", "cartao_visita")
        produto = PRODUTOS[produto_key]

        intencao = interpretar(
            msg,
            "O cliente confirma o formato sugerido ou quer formato diferente/personalizado.",
            ["confirma", "quer_outro"]
        )
        if intencao == "quer_outro":
            dados["formato"] = msg
        else:
            dados["formato"] = produto["formatos"]

        if sessao.get("fluxo") == "cliente_recorrente":
            resposta = (
                f"Formato anotado! 😊\n\n"
                f"Você já tem a arte pronta ou precisa que desenvolvamos algo novo?"
            )
            sessao["etapa"] = "arte"
        else:
            resposta = (
                f"Formato anotado! 😊\n\n"
                f"Em qual área você atua?"
            )
            sessao["etapa"] = "area"

    elif etapa == "area":
        dados["area"] = msg
        for chave, valor in PAPEIS_POR_AREA.items():
            if chave in msg.lower():
                dados["papel_recomendado"] = valor
                break
        resposta = (
            f"Que área incrível — sofisticação em cada detalhe. 👑\n\n"
            f"Você já possui a arte finalizada, tem alguma referência "
            f"ou vai precisar de criação?"
        )
        sessao["etapa"] = "arte"

    elif etapa == "arte":
        primeiro = dados.get("nome", "").split()[0]
        produto_key = dados.get("produto_key", "cartao_visita")
        aceita_3d = PRODUTOS.get(produto_key, {}).get("aceita_3d", False)

        intencao = interpretar(
            msg,
            "O cliente responde sobre arte: se já tem arte pronta/referência, se precisa criar, ou se quer identidade visual.",
            ["arte_pronta", "precisa_criacao", "identidade_visual"]
        )

        if intencao == "arte_pronta":
            dados["arte"] = "pronta_ou_referencia"
            resposta = (
                f"Pode me enviar sua arte ou referência? "
                f"Assim consigo direcionar sua cotação com mais precisão. ✨"
            )
            sessao["etapa"] = "papel"

        elif intencao == "identidade_visual":
            dados["arte"] = "identidade_visual"
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
            if dados.get("email"):
                resposta = (
                    f"Identidade visual é um projeto especial, {primeiro}. 👑\n\n"
                    f"Vou encaminhar você para a nossa designer Ane, "
                    f"que vai te atender com toda a atenção que esse projeto merece.\n\n"
                    f"{MSG_EDUCATIVA}\n\n"
                    f"Em breve ela entrará em contato."
                )
                dados["status"] = "handoff_designer"
                sessao["etapa"] = "handoff"
                handoff_data = dados
            else:
                resposta = (
                    f"Identidade visual é um projeto especial, {primeiro}. 👑\n\n"
                    f"Vou encaminhar para a nossa designer Ane. "
                    f"Qual é o seu melhor e-mail para ela entrar em contato?"
                )
                sessao["etapa"] = "email_design"

        else:
            dados["arte"] = "precisa_criacao"
            if aceita_3d:
                resposta = (
                    f"Sem problema, podemos desenvolver para você. 🚀\n\n"
                    f"Opções de criação:\n\n"
                    f"• Criação de arte — R$ 74,90\n"
                    f"• Criação de arte + amostra 3D — R$ 220,00\n"
                    f"• Criação de identidade visual\n\n"
                    f"Qual faz mais sentido para o seu projeto?"
                )
            else:
                resposta = (
                    f"Sem problema, podemos desenvolver para você. 🚀\n\n"
                    f"Opções de criação:\n\n"
                    f"• Criação de arte — R$ 74,90\n"
                    f"• Criação de identidade visual\n\n"
                    f"Qual faz mais sentido para o seu projeto?"
                )
            sessao["etapa"] = "arte_opcao"

    elif etapa == "email_design":
        valido, email_extraido = extrair_e_validar(msg, "email")
        if not valido:
            resposta = "Pode me passar seu e-mail completo? Ex: seunome@gmail.com 😊"
        else:
            dados["email"] = email_extraido
            primeiro = dados.get("nome", "").split()[0]
            dados["status"] = "handoff_designer"
            resposta = (
                f"Perfeito, {primeiro}! A Ane entrará em contato em breve. ✨\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Foi um prazer te atender!"
            )
            sessao["etapa"] = "handoff"
            handoff_data = dados

    elif etapa == "arte_opcao":
        primeiro = dados.get("nome", "").split()[0]
        produto_key = dados.get("produto_key", "cartao_visita")
        aceita_3d = PRODUTOS.get(produto_key, {}).get("aceita_3d", False)

        intencao = interpretar(
            msg,
            "O cliente escolhe entre: criação de arte simples (R$74,90), criação de arte com amostra 3D (R$220), ou identidade visual.",
            ["criacao_simples", "criacao_3d", "identidade_visual"]
        )

        if intencao == "identidade_visual":
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
            resposta = (
                f"Identidade visual é um projeto especial, {primeiro}. 👑\n\n"
                f"Vou encaminhar para a nossa designer Ane.\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Em breve ela entrará em contato."
            )
            dados["status"] = "handoff_designer"
            sessao["etapa"] = "handoff"
            handoff_data = dados

        elif intencao == "criacao_3d" and aceita_3d:
            dados["criacao"] = "criacao_arte_3d"
            dados["valor_criacao"] = 220.00
            resposta = (
                f"Ótima escolha! A amostra 3D vai te dar uma visão incrível do resultado final. 🚀\n\n"
                f"Qual tipo de papel faz mais sentido para o seu projeto?\n\n"
                f"Couchê 300g, texturado até 400g ou texturado acima de 400g?"
            )
            sessao["etapa"] = "papel"

        else:
            dados["criacao"] = "criacao_simples"
            dados["valor_criacao"] = 74.90
            resposta = (
                f"Nossa equipe vai criar algo incrível para você. 😊\n\n"
                f"Qual tipo de papel faz mais sentido para o seu projeto?\n\n"
                f"Couchê 300g, texturado até 400g ou texturado acima de 400g?"
            )
            sessao["etapa"] = "papel"

    elif etapa == "papel":
        dados["material"] = msg
        primeiro = dados.get("nome", "").split()[0]
        if "couche" in msg.lower() or "couchê" in msg.lower() or "300" in msg:
            resposta = (
                f"O Couchê 300g é nossa opção de entrada. Para refletir o padrão Primyn, "
                f"trabalhamos obrigatoriamente com hot stamping ou baixo relevo — "
                f"sem acabamento premium, ele se torna um cartão comum. 👑\n\n"
                f"Qual acabamento prefere, ou quer explorar nossos papéis texturados?\n\n"
                f"Veja nossos tipos de papel e texturas: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas"
            )
            sessao["etapa"] = "papel_couche_validar"
        else:
            resposta = (
                f"Para te ajudar a escolher o papel ideal, veja nosso catálogo completo de texturas: "
                f"https://www.primyn.com/pagina/tipos-de-papeis-e-texturas ✨\n\n"
                f"Os mais vendidos são o Conqueror Bamboo 400g e o Papel Notturno Black 450g — "
                f"ambos transmitem sofisticação desde o primeiro toque.\n\n"
                f"Qualquer papel do catálogo que você escolher será considerado texturado premium. "
                f"Qual você prefere ou qual se aproxima mais da sua visão de marca?\n\n"
                f"E para se inspirar nos nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "papel_escolhido"

    elif etapa == "papel_escolhido":
        dados["material"] = msg
        resposta = (
            f"Ótima escolha! Agora, em relação ao acabamento — cada um transforma "
            f"completamente a percepção do material. 👑\n\n"
            f"Veja os detalhes de cada opção:\n\n"
            f"• Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
            f"• Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
            f"• Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
            f"• Empastamento de papéis\n"
            f"• Impressão colorida no papel especial\n"
            f"• Combinação de acabamentos\n\n"
            f"Qual faz mais sentido para a sua marca?"
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
            resposta = (
                f"Ótima escolha explorar os texturados! ✨\n\n"
                f"Veja nosso catálogo completo: "
                f"https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                f"Os mais vendidos são o Conqueror Bamboo 400g e o Papel Notturno Black 450g. "
                f"Qualquer papel do catálogo será considerado texturado premium.\n\n"
                f"Qual você prefere ou qual se aproxima mais da sua visão de marca?\n\n"
                f"Inspire-se nos nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "papel_escolhido"
        elif intencao == "recusa_acabamento":
            resposta = (
                f"Entendemos, {primeiro}. "
                f"Quando quiser explorar uma proposta premium, estaremos por aqui. 😊"
            )
            dados["status"] = "fora_escopo"
            sessao["etapa"] = "encerrado"
        else:
            dados["acabamento"] = msg
            resposta = "Qual quantidade você está considerando para esse projeto? ✨"
            sessao["etapa"] = "quantidade"

    elif etapa == "acabamento":
        primeiro = dados.get("nome", "").split()[0]
        msg_lower = msg.lower()
        if any(p in msg_lower for p in ["empastamento", "borda", "sanduiche", "sanduíche"]):
            dados["acabamento"] = msg
            resposta = (
                f"Ótima escolha! O empastamento tem três finalidades: 👑\n\n"
                f"• Papel mais grosso — colar dois papéis para dar mais espessura e rigidez\n"
                f"• Evitar marcação do relevo — impede que o baixo relevo ou hot stamping "
                f"apareça no lado oposto do papel\n"
                f"• Borda sanduíche (borda colorida) — o interior fica colorido, "
                f"revelando uma cor especial ao olhar a borda do cartão\n\n"
                f"Qual dessas finalidades faz mais sentido para o seu projeto?\n\n"
                f"Veja nossos projetos para se inspirar: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "empastamento_detalhe"
        else:
            dados["acabamento"] = msg
            resposta = "Qual quantidade você está considerando para esse projeto? ✨"
            sessao["etapa"] = "quantidade"

    elif etapa == "empastamento_detalhe":
        dados["empastamento_tipo"] = msg
        resposta = "Qual quantidade você está considerando para esse projeto? ✨"
        sessao["etapa"] = "quantidade"

    elif etapa == "quantidade":
        dados["quantidade"] = msg
        primeiro = dados.get("nome", "").split()[0]
        produto_key = dados.get("produto_key", "cartao_visita")
        produto = PRODUTOS.get(produto_key, {})

        media = calcular_media(produto_key, dados.get("material", ""), msg)
        valor_criacao = dados.get("valor_criacao", 0)
        if valor_criacao:
            media += valor_criacao
        dados["media"] = media

        # Verifica quantidade mínima
        aviso_minimo = ""
        minimo = produto.get("minimo")
        if minimo:
            try:
                qtd_num = int(''.join(filter(str.isdigit, str(msg))))
                if qtd_num < minimo:
                    aviso_minimo = (
                        f"Nossa quantidade mínima para {produto['nome']} é {minimo} unidades. "
                        f"Vou considerar {minimo} unidades na estimativa.\n\n"
                    )
            except:
                pass

        media_fmt = fmt_brl(media)
        resposta = (
            f"{aviso_minimo}"
            f"Para a configuração que você me passou, o investimento médio fica em torno de {media_fmt}. 🚀\n\n"
            f"Esse valor é uma referência — o orçamento final é personalizado conforme "
            f"material, acabamento e complexidade. 👑\n\n"
            f"Faz sentido prosseguirmos com uma proposta personalizada?"
        )

        # Upsell apenas para cartão de visita e se ainda não foi feito
        if produto_key == "cartao_visita" and not dados.get("upsell_feito"):
            dados["upsell_feito"] = True
            resposta += f"\n\n{MSG_UPSELL_PAPELARIA}"
            sessao["etapa"] = "upsell_resposta"
        else:
            sessao["etapa"] = "media_proposta"

    elif etapa == "upsell_resposta":
        primeiro = dados.get("nome", "").split()[0]
        intencao = interpretar(
            msg,
            "O cliente responde se quer conhecer a opção de papelaria completa ou prefere seguir só com o cartão.",
            ["quer_papelaria_completa", "prefere_so_cartao"]
        )
        if intencao == "quer_papelaria_completa":
            dados["produto"] = "Papelaria Completa"
            dados["produto_key"] = "papelaria_completa"
            resposta = (
                f"Que decisão incrível, {primeiro}! 👑\n\n"
                f"A papelaria completa transmite coerência visual em cada ponto de contato — "
                f"cartão de visita, papel timbrado, pasta e envelope com a mesma identidade.\n\n"
                f"O investimento parte de R$ 4.200,00 no Couchê e R$ 5.800,00 em papel especial, "
                f"variando conforme composição e acabamentos.\n\n"
                f"Em breve um especialista vai preparar a proposta completa para você."
            )
            dados["status"] = "handoff"
            sessao["etapa"] = "handoff"
            handoff_data = dados
        else:
            resposta = (
                f"Sem problema, {primeiro}! Vamos seguir com o cartão. 😊\n\n"
                f"Faz sentido prosseguirmos com a proposta personalizada?"
            )
            sessao["etapa"] = "media_proposta"

    elif etapa == "media_proposta":
        primeiro = dados.get("nome", "").split()[0]
        intencao = interpretar(
            msg,
            "O cliente responde se quer prosseguir com a proposta personalizada.",
            ["sim_quero", "precisa_pensar", "nao_quero"]
        )
        if intencao == "sim_quero":
            resposta = "Você tem algum prazo importante para receber esse material? ✨"
            sessao["etapa"] = "urgencia"
        elif intencao == "nao_quero":
            resposta = (
                f"Sem problema, {primeiro}. Agradeço pelo seu tempo e fico à disposição "
                f"quando quiser retomar! 😊"
            )
            dados["status"] = "perdido"
            sessao["etapa"] = "encerrado"
        else:
            resposta = (
                f"Claro, {primeiro}! Sem pressa. Quando quiser retomar, estaremos por aqui. 😊\n\n"
                f"Acompanhe nossos projetos em @primyn.store"
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
            aviso = (
                "Projetos com criação e produção premium têm prazo médio de 5 a 8 dias úteis. "
                "Vou sinalizar a urgência no encaminhamento. 🚀\n\n"
            )
        resposta = (
            f"{aviso}"
            f"{MSG_EDUCATIVA}\n\n"
            f"Vou encaminhar seu projeto para uma proposta personalizada. "
            f"Em breve um especialista dará continuidade ao seu atendimento, {primeiro}. 😊"
        )
        dados["status"] = "handoff"
        sessao["etapa"] = "handoff"
        handoff_data = dados

    elif etapa == "handoff":
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Antes de encerrar, {primeiro}, como foi sua experiência "
            f"com este atendimento inicial? 😊\n\n"
            f"Sua opinião nos ajuda a melhorar cada vez mais."
        )
        sessao["etapa"] = "feedback"

    elif etapa == "feedback":
        dados["avaliacao"] = msg
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Muito obrigada pelo feedback, {primeiro}! "
            f"Foi um prazer te atender. Até breve! 🤍"
        )
        sessao["etapa"] = "encerrado"

    elif etapa == "encerrado":
        primeiro = dados.get("nome", "").split()[0] if dados.get("nome") else ""
        resposta = (
            f"Olá novamente, {primeiro}! Quer retomar seu projeto ou precisa de algo mais? 😊"
            if primeiro else
            "Olá! Seja muito bem-vindo(a) de volta à Primyn. Como posso te ajudar? 😊"
        )
        sessao["etapa"] = "produto"

    else:
        resposta = (
            "Olá! Seja muito bem-vindo(a) à Primyn. 😊\n\n"
            "Sou a Mily. Como posso te ajudar?"
        )
        sessao["etapa"] = "triagem_inicial"

    sessao["dados"] = dados
    atualizar_sessao(numero, sessao)
    return resposta, handoff_data
