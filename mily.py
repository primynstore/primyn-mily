
# ═══════════════════════════════════════════════
# PRIMYN STUDIO — AGENTE MILY v6
# Script oficial + alternativas numeradas
# Sem API de IA — estável e sem bug de reset
# ═══════════════════════════════════════════════

import json
import os
import random
from datetime import datetime

DB_FILE = "sessoes.json"

# ═══════════════════════════════════════════════
# CATÁLOGO COMPLETO PRIMYN
# ═══════════════════════════════════════════════

PRODUTOS = {
    "1": {
        "key": "cartao_visita",
        "nome": "Cartão de Visita / TAG / Cartões similares",
        "minimo": 250,
        "formatos": "5×9 cm (tradicional), 5×8 cm (americano) ou personalizado",
        "aceita_3d": True,
        "medias": {
            "250":  {"essencial": 378,  "luxo_black": 562,  "luxo_white": 898,  "prestigio": 1297},
            "500":  {"essencial": 475,  "luxo_black": 839,  "luxo_white": 1284, "prestigio": 1682},
            "1000": {"essencial": 588,  "luxo_black": 1184, "luxo_white": 1568, "prestigio": 2567}
        }
    },
    "2": {
        "key": "pasta",
        "nome": "Pasta com bolsa ou orelha",
        "minimo": 100,
        "formatos": "31×22 cm (fechada)",
        "aceita_3d": False,
        "medias": {
            "100": {"essencial": 2500, "luxo_black": 2500, "luxo_white": 2500, "prestigio": 2500},
            "250": {"essencial": 3800, "luxo_black": 3800, "luxo_white": 3800, "prestigio": 3800},
            "500": {"essencial": 5500, "luxo_black": 5500, "luxo_white": 5500, "prestigio": 5500}
        }
    },
    "3": {
        "key": "envelope",
        "nome": "Envelope Ofício / Envelope Saco",
        "minimo": 100,
        "formatos": "Ofício: 11,4×22,9 cm | Saco: 22,9×32,4 cm",
        "aceita_3d": False,
        "medias": {
            "100": {"essencial": 720,  "luxo_black": 720,  "luxo_white": 720,  "prestigio": 720},
            "250": {"essencial": 1050, "luxo_black": 1050, "luxo_white": 1050, "prestigio": 1050},
            "500": {"essencial": 1590, "luxo_black": 1590, "luxo_white": 1590, "prestigio": 1590}
        }
    },
    "4": {
        "key": "timbrado",
        "nome": "Papel Timbrado / Receituário",
        "minimo": 250,
        "formatos": "A4 (29,7×21 cm) ou A5 (15×20 cm)",
        "aceita_3d": False,
        "medias": {
            "250":  {"essencial": 650,  "luxo_black": 650,  "luxo_white": 650,  "prestigio": 650},
            "500":  {"essencial": 890,  "luxo_black": 890,  "luxo_white": 890,  "prestigio": 890},
            "1000": {"essencial": 1190, "luxo_black": 1190, "luxo_white": 1190, "prestigio": 1190}
        }
    },
    "5": {
        "key": "papelaria_completa",
        "nome": "Papelaria Completa",
        "minimo": 250,
        "formatos": "Variável conforme composição do kit",
        "aceita_3d": False,
        "medias": {
            "250": {"essencial": 4200, "luxo_black": 4200, "luxo_white": 5800, "prestigio": 5800},
            "500": {"essencial": 5800, "luxo_black": 5800, "luxo_white": 7500, "prestigio": 7500}
        }
    }
}

AREAS = {
    "1": "Advocacia / Direito",
    "2": "Arquitetura / Engenharia",
    "3": "Medicina / Saúde",
    "4": "Moda / Beleza / Lifestyle",
    "5": "Finanças / Executivo",
    "6": "Outro"
}

PAPEIS_POR_AREA = {
    "1": "Notturno Black 450g, Dark Blue 450g ou Rives White 400g",
    "2": "Rives Natural White 400g ou Conqueror Bamboo 400g",
    "3": "Rives Traditional White 400g ou Conqueror Bamboo 400g",
    "4": "Color Plus 240g ou Rives White 400g",
    "5": "Notturno Black 450g, Dark Blue 450g ou Rives White 400g",
    "6": "Conqueror Bamboo 400g (o mais vendido) ou Notturno Black 450g"
}

ACABAMENTOS = {
    "1": "hot_stamping",
    "2": "alto_relevo",
    "3": "baixo_relevo",
    "4": "empastamento",
    "5": "impressao_colorida",
    "6": "combinacao"
}

MSG_EDUCATIVA = (
    "Antes de encerrarmos, um pensamento que vale levar:\n\n"
    "Materiais de papelaria premium não são apenas papel — eles são o primeiro toque "
    "físico que o seu cliente tem com a sua marca. Um cartão com textura e acabamento "
    "em hot stamping ou baixo relevo transmite sofisticação antes mesmo de qualquer "
    "palavra ser dita. Estudos mostram que materiais de alta qualidade aumentam em até "
    "3x a percepção de valor de uma marca. Você não entrega um cartão — você entrega "
    "uma experiência. 👑\n\n"
    "Sua marca merece deixar essa impressão. 🤍"
)

MSG_UPSELL = (
    "Uma observação importante: clientes que investem em papelaria completa — "
    "cartão de visita, papel timbrado, pasta e envelope com a mesma identidade — "
    "transmitem coerência visual que multiplica a percepção de valor da marca. "
    "É a diferença entre parecer profissional e ser reconhecido como premium. 👑\n\n"
    "A Primyn oferece kits completos a partir de R$ 4.200,00 no Couchê e "
    "R$ 5.800,00 em papel especial, variando conforme composição e acabamentos.\n\n"
    "1. Quero conhecer essa opção\n"
    "2. Prefiro seguir só com o cartão"
)

# ═══════════════════════════════════════════════
# VARIAÇÕES DE TEXTO
# ═══════════════════════════════════════════════

def var(*opcoes):
    return random.choice(opcoes)

# ═══════════════════════════════════════════════
# VALIDAÇÕES
# ═══════════════════════════════════════════════

def validar_nome(msg):
    partes = [p.strip() for p in msg.strip().split() if len(p.strip()) > 1]
    if len(partes) >= 2:
        return True, " ".join(p.title() for p in partes)
    return False, None

def validar_email(msg):
    msg = msg.strip().lower()
    if "@" in msg and "." in msg.split("@")[-1] and len(msg) > 5:
        return True, msg
    return False, None

def validar_opcao(msg, opcoes_validas):
    """
    Aceita número (ex: "1") ou palavra-chave parcial (ex: "pasta", "cartão").
    Retorna a chave da opção ou None.
    """
    msg = msg.strip().lower()
    # Tenta por número
    if msg in opcoes_validas:
        return msg
    # Tenta por palavra-chave
    for chave, valor in opcoes_validas.items():
        nome = valor.lower() if isinstance(valor, str) else valor.get("nome", "").lower()
        palavras = nome.split()
        for palavra in palavras:
            if len(palavra) > 3 and palavra in msg:
                return chave
    return None

def validar_quantidade(msg, minimo=100):
    try:
        num = int(''.join(filter(str.isdigit, msg)))
        if num > 0:
            return True, num
    except:
        pass
    return False, None

def msg_invalida(contexto=""):
    msgs = [
        f"Não consegui entender sua resposta. {contexto}",
        f"Hmm, não reconheci essa opção. {contexto}",
        f"Pode tentar novamente? {contexto}",
    ]
    return random.choice(msgs)

def calcular_media(produto_num, material, quantidade):
    produto = PRODUTOS.get(produto_num)
    if not produto or not produto["medias"]:
        return 0
    medias = produto["medias"]
    faixas = sorted([int(k) for k in medias.keys()])
    qtd_str = str(faixas[0])
    for f in faixas:
        if quantidade >= f:
            qtd_str = str(f)
    m = (material or "").lower()
    if "couche" in m or "couchê" in m:    tier = "essencial"
    elif "black" in m or "notturno" in m: tier = "luxo_black"
    elif "white" in m or "rives" in m:    tier = "luxo_white"
    elif "450" in m or "prestigio" in m:  tier = "prestigio"
    else:                                  tier = "luxo_white"
    return medias.get(qtd_str, {}).get(tier, 0)

def fmt_brl(valor):
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
            "ultimo_contato": datetime.now().isoformat(),
            "tentativas": 0
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
    msg_lower    = msg.lower()
    resposta     = ""
    handoff_data = None
    tentativas   = sessao.get("tentativas", 0)

    # ── ABERTURA ──────────────────────────────
    if etapa == "abertura":
        resposta = var(
            "Olá! Seja muito bem-vindo(a) à Primyn. ✨\n\n"
            "Sou a Mily, consultora virtual da Primyn. Vou entender melhor o que você "
            "procura para direcionar seu atendimento da forma mais estratégica possível — "
            "e, ao final, um especialista dará continuidade ao seu projeto para garantir "
            "que cada detalhe fique exatamente como você deseja.\n\n"
            "Para começarmos, você é cliente da Primyn ou é sua primeira vez por aqui?\n\n"
            "1. Primeira vez\n"
            "2. Já sou cliente\n"
            "3. Já falei com vocês antes",

            "Olá! Seja muito bem-vindo(a) à Primyn. ✨\n\n"
            "Sou a Mily, consultora virtual da Primyn, e vou te acompanhar neste "
            "primeiro atendimento para entender o seu projeto com mais precisão.\n\n"
            "Para começarmos:\n\n"
            "1. Primeira vez\n"
            "2. Já sou cliente\n"
            "3. Já falei com vocês antes"
        )
        sessao["etapa"] = "triagem_inicial"
        sessao["tentativas"] = 0

    # ── TRIAGEM ───────────────────────────────
    elif etapa == "triagem_inicial":
        if any(p in msg_lower for p in ["2", "já sou", "ja sou", "cliente", "já comprei", "ja comprei", "sou cliente"]):
            dados["tipo_contato"] = "cliente_recorrente"
            sessao["fluxo"] = "cliente_recorrente"
            resposta = var(
                "Que bom te ver de volta! 😊\n\n"
                "Para localizar seu cadastro, pode me informar seu nome e sobrenome completo?",
                "Ótimo ter você de volta! 😊\n\n"
                "Me conta seu nome e sobrenome para eu localizar seu cadastro."
            )
            sessao["etapa"] = "nome"

        elif any(p in msg_lower for p in ["3", "já falei", "ja falei", "voltei", "antes", "já conversei", "ja conversei"]):
            dados["tipo_contato"] = "lead_antigo"
            sessao["fluxo"] = "lead_antigo"
            resposta = var(
                "Que bom que voltou! 😊\n\n"
                "Para localizar seu histórico, pode me dizer seu nome e sobrenome completo?",
                "Fico feliz que tenha voltado! 😊\n\n"
                "Me diz seu nome e sobrenome para eu encontrar seu histórico."
            )
            sessao["etapa"] = "nome"

        elif any(p in msg_lower for p in ["1", "primeira", "novo", "nova", "não sou", "nao sou"]):
            dados["tipo_contato"] = "novo_lead"
            sessao["fluxo"] = "novo_lead"
            resposta = var(
                "Seja muito bem-vindo(a) à Primyn! ✨\n\n"
                "Como você conheceu a Primyn?",
                "Que ótimo ter você por aqui! ✨\n\n"
                "Antes de seguirmos, como você conheceu a Primyn?"
            )
            sessao["etapa"] = "origem"

        else:
            tentativas += 1
            if tentativas >= 2:
                # Assume novo lead após 2 tentativas inválidas
                dados["tipo_contato"] = "novo_lead"
                sessao["fluxo"] = "novo_lead"
                resposta = "Como você conheceu a Primyn?"
                sessao["etapa"] = "origem"
            else:
                resposta = (
                    "Por favor, escolha uma das opções:\n\n"
                    "1. Primeira vez\n"
                    "2. Já sou cliente\n"
                    "3. Já falei com vocês antes"
                )
            sessao["tentativas"] = tentativas

    # ── ORIGEM ───────────────────────────────
    elif etapa == "origem":
        dados["origem"] = msg
        resposta = var(
            "Que ótimo que nos encontrou por lá! ✨\n\n"
            "Para personalizar o seu atendimento, como posso te chamar?",
            "Fico feliz que tenha chegado até nós! ✨\n\n"
            "Me conta: como posso te chamar?"
        )
        sessao["etapa"] = "nome"
        sessao["tentativas"] = 0

    # ── NOME ─────────────────────────────────
    elif etapa == "nome":
        valido, nome_fmt = validar_nome(msg)
        if not valido:
            tentativas += 1
            if tentativas >= 3:
                # Aceita nome parcial após 3 tentativas
                nome_fmt = msg.strip().title()
                dados["nome"] = nome_fmt
                primeiro = nome_fmt.split()[0]
                sessao["tentativas"] = 0
                sessao["etapa"] = "email" if sessao.get("fluxo") != "cliente_recorrente" else "produto"
                resposta = (
                    f"Obrigada, {primeiro}! ✨\n\n"
                    + ("Qual é o seu melhor e-mail para envio da proposta?"
                       if sessao["etapa"] == "email"
                       else "Me conta: qual material você gostaria de produzir desta vez?")
                )
            else:
                resposta = (
                    "Para encontrar seu cadastro com precisão, preciso do seu "
                    "nome e sobrenome completo. Como posso te chamar? 😊"
                )
                sessao["tentativas"] = tentativas
        else:
            dados["nome"] = nome_fmt
            primeiro = nome_fmt.split()[0]
            sessao["tentativas"] = 0
            fluxo = sessao.get("fluxo")

            if fluxo == "cliente_recorrente":
                resposta = var(
                    f"Que prazer, {primeiro}! Já te localizo aqui no sistema. 😊\n\n"
                    f"Me conta: qual material você gostaria de produzir desta vez?\n\n"
                    f"1. Cartão de Visita / TAG / Cartões similares\n"
                    f"2. Pasta com bolsa ou orelha\n"
                    f"3. Envelope Ofício / Envelope Saco\n"
                    f"4. Papel Timbrado / Receituário\n"
                    f"5. Papelaria Completa",

                    f"Que bom ter você de volta, {primeiro}! 😊\n\n"
                    f"Qual projeto você gostaria de produzir desta vez?\n\n"
                    f"1. Cartão de Visita / TAG / Cartões similares\n"
                    f"2. Pasta com bolsa ou orelha\n"
                    f"3. Envelope Ofício / Envelope Saco\n"
                    f"4. Papel Timbrado / Receituário\n"
                    f"5. Papelaria Completa"
                )
                sessao["etapa"] = "produto"

            elif fluxo == "lead_antigo":
                resposta = var(
                    f"Encontrei seu histórico, {primeiro}! 😊\n\n"
                    f"Você prefere retomar o projeto anterior ou começar algo novo?\n\n"
                    f"1. Retomar projeto anterior\n"
                    f"2. Começar projeto novo",

                    f"Ótimo, {primeiro}! Encontrei seu cadastro. 😊\n\n"
                    f"Como prefere prosseguir?\n\n"
                    f"1. Retomar projeto anterior\n"
                    f"2. Começar projeto novo"
                )
                sessao["etapa"] = "retomar_ou_novo"

            else:
                resposta = var(
                    f"Perfeito, {primeiro}! ✨\n\n"
                    f"Qual é o seu melhor e-mail para envio da proposta?",
                    f"Ótimo, {primeiro}! ✨\n\n"
                    f"Para que sua proposta chegue certinha até você, qual e-mail prefere usar?"
                )
                sessao["etapa"] = "email"

    # ── EMAIL ─────────────────────────────────
    elif etapa == "email":
        valido, email_fmt = validar_email(msg)
        primeiro = dados.get("nome", "").split()[0]
        if not valido:
            tentativas += 1
            if tentativas >= 3:
                # Segue sem e-mail após 3 tentativas
                dados["email"] = ""
                sessao["tentativas"] = 0
                resposta = (
                    f"Sem problema, {primeiro}! Seguiremos sem o e-mail por enquanto. 😊\n\n"
                    f"Qual projeto você gostaria de produzir?\n\n"
                    f"1. Cartão de Visita / TAG / Cartões similares\n"
                    f"2. Pasta com bolsa ou orelha\n"
                    f"3. Envelope Ofício / Envelope Saco\n"
                    f"4. Papel Timbrado / Receituário\n"
                    f"5. Papelaria Completa"
                )
                sessao["etapa"] = "produto"
            else:
                resposta = (
                    "Esse e-mail não parece válido. 😊\n\n"
                    "Pode me passar seu endereço completo? Ex: seunome@gmail.com"
                )
                sessao["tentativas"] = tentativas
        else:
            dados["email"] = email_fmt
            sessao["tentativas"] = 0
            resposta = var(
                f"Maravilha, {primeiro}! ✨\n\n"
                f"Agora me conta: qual projeto você gostaria de produzir?\n\n"
                f"1. Cartão de Visita / TAG / Cartões similares\n"
                f"2. Pasta com bolsa ou orelha\n"
                f"3. Envelope Ofício / Envelope Saco\n"
                f"4. Papel Timbrado / Receituário\n"
                f"5. Papelaria Completa",

                f"Perfeito, {primeiro}! ✨\n\n"
                f"Qual projeto você gostaria de produzir?\n\n"
                f"1. Cartão de Visita / TAG / Cartões similares\n"
                f"2. Pasta com bolsa ou orelha\n"
                f"3. Envelope Ofício / Envelope Saco\n"
                f"4. Papel Timbrado / Receituário\n"
                f"5. Papelaria Completa"
            )
            sessao["etapa"] = "produto"

    # ── RETOMAR OU NOVO ───────────────────────
    elif etapa == "retomar_ou_novo":
        primeiro = dados.get("nome", "").split()[0]
        if any(p in msg_lower for p in ["1", "retomar", "anterior", "mesmo", "igual", "continuar"]):
            resposta = (
                f"Vou retomar exatamente de onde paramos, {primeiro}.\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Em breve um especialista dará continuidade ao seu atendimento. 😊"
            )
            dados["status"] = "handoff"
            sessao["etapa"] = "handoff"
            handoff_data = dados
        elif any(p in msg_lower for p in ["2", "novo", "nova", "diferente", "outro"]):
            sessao["fluxo"] = "novo_lead"
            resposta = var(
                f"Vamos começar algo novo e especial, {primeiro}! ✨\n\n"
                f"Qual projeto você gostaria de produzir?\n\n"
                f"1. Cartão de Visita / TAG / Cartões similares\n"
                f"2. Pasta com bolsa ou orelha\n"
                f"3. Envelope Ofício / Envelope Saco\n"
                f"4. Papel Timbrado / Receituário\n"
                f"5. Papelaria Completa",
            )
            sessao["etapa"] = "produto"
        else:
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Retomar projeto anterior\n"
                "2. Começar projeto novo"
            )

    # ── PRODUTO ───────────────────────────────
    elif etapa == "produto":
        primeiro = dados.get("nome", "").split()[0]
        opcao = validar_opcao(msg, {k: v["nome"] for k, v in PRODUTOS.items()})

        if not opcao:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Cartão de Visita / TAG / Cartões similares\n"
                "2. Pasta com bolsa ou orelha\n"
                "3. Envelope Ofício / Envelope Saco\n"
                "4. Papel Timbrado / Receituário\n"
                "5. Papelaria Completa"
            )
        else:
            produto = PRODUTOS[opcao]
            dados["produto_num"] = opcao
            dados["produto"] = produto["nome"]
            dados["produto_key"] = produto["key"]
            dados["upsell_feito"] = False
            sessao["tentativas"] = 0

            if opcao == "5":  # Papelaria completa
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
                    f"Ótima escolha, {primeiro}! ✨\n\n"
                    f"Para {produto['nome']}, trabalhamos com o formato {produto['formatos']}.\n\n"
                    f"Esse formato atende ao seu projeto?\n\n"
                    f"1. Sim, esse formato está ótimo\n"
                    f"2. Prefiro um formato diferente / personalizado"
                )
                sessao["etapa"] = "confirmar_formato"

    # ── CONFIRMAR FORMATO ─────────────────────
    elif etapa == "confirmar_formato":
        produto_num = dados.get("produto_num", "1")
        produto = PRODUTOS[produto_num]
        if any(p in msg_lower for p in ["2", "diferente", "personalizado", "outro", "nao", "não"]):
            resposta = (
                "Sem problema! Me conta qual formato você prefere para o seu projeto:"
            )
            sessao["etapa"] = "formato_personalizado"
        else:
            dados["formato"] = produto["formatos"]
            sessao["etapa"] = "area" if sessao.get("fluxo") != "cliente_recorrente" else "arte"
            if sessao["etapa"] == "area":
                resposta = var(
                    "Perfeito! ✨\n\n"
                    "Para recomendarmos o material mais alinhado à sua marca, em qual área você atua?\n\n"
                    "1. Advocacia / Direito\n"
                    "2. Arquitetura / Engenharia\n"
                    "3. Medicina / Saúde\n"
                    "4. Moda / Beleza / Lifestyle\n"
                    "5. Finanças / Executivo\n"
                    "6. Outro",

                    "Formato confirmado! ✨\n\n"
                    "Em qual área você atua?\n\n"
                    "1. Advocacia / Direito\n"
                    "2. Arquitetura / Engenharia\n"
                    "3. Medicina / Saúde\n"
                    "4. Moda / Beleza / Lifestyle\n"
                    "5. Finanças / Executivo\n"
                    "6. Outro"
                )
            else:
                resposta = (
                    "Formato confirmado! 😊\n\n"
                    "Você já possui a arte finalizada ou vai precisar de criação?\n\n"
                    "1. Já tenho a arte criada\n"
                    "2. Tenho referência de arte\n"
                    "3. Não, vou precisar de criação de arte"
                )

    # ── FORMATO PERSONALIZADO ─────────────────
    elif etapa == "formato_personalizado":
        if len(msg.strip()) < 3:
            resposta = "Pode me descrever o formato que você deseja? Ex: 8×5 cm, A5, etc."
        else:
            dados["formato"] = msg
            sessao["etapa"] = "area" if sessao.get("fluxo") != "cliente_recorrente" else "arte"
            primeiro = dados.get("nome", "").split()[0]
            if sessao["etapa"] == "area":
                resposta = (
                    f"Anotei o formato, {primeiro}! ✨\n\n"
                    f"Em qual área você atua?\n\n"
                    f"1. Advocacia / Direito\n"
                    f"2. Arquitetura / Engenharia\n"
                    f"3. Medicina / Saúde\n"
                    f"4. Moda / Beleza / Lifestyle\n"
                    f"5. Finanças / Executivo\n"
                    f"6. Outro"
                )
            else:
                resposta = (
                    f"Anotei o formato! 😊\n\n"
                    f"Você já possui a arte finalizada ou vai precisar de criação?\n\n"
                    f"1. Já tenho a arte criada\n"
                    f"2. Tenho referência de arte\n"
                    f"3. Não, vou precisar de criação de arte"
                )

    # ── ÁREA ─────────────────────────────────
    elif etapa == "area":
        opcao = validar_opcao(msg, AREAS)
        primeiro = dados.get("nome", "").split()[0]

        if not opcao:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Advocacia / Direito\n"
                "2. Arquitetura / Engenharia\n"
                "3. Medicina / Saúde\n"
                "4. Moda / Beleza / Lifestyle\n"
                "5. Finanças / Executivo\n"
                "6. Outro"
            )
        else:
            area_nome = AREAS[opcao]
            dados["area"] = area_nome
            papel_rec = PAPEIS_POR_AREA.get(opcao)
            if papel_rec:
                dados["papel_recomendado"] = papel_rec
            sessao["tentativas"] = 0

            transicoes = {
                "1": f"Advocacia — uma área que exige precisão e autoridade em cada detalhe.",
                "2": f"Arquitetura — uma área que exige sofisticação em cada detalhe.",
                "3": f"Medicina — uma área onde confiança e credibilidade são essenciais.",
                "4": f"Moda e beleza — uma área que vive de estética e identidade visual forte.",
                "5": f"Finanças — uma área onde a percepção de solidez faz toda a diferença.",
                "6": f"Sua área exige uma identidade visual que reflita seu posicionamento."
            }
            transicao = transicoes.get(opcao, "")

            resposta = var(
                f"{transicao} Sua marca merece um material à altura do seu trabalho. ✨\n\n"
                f"Você já possui a arte finalizada ou vai precisar de criação?\n\n"
                f"1. Já tenho a arte criada\n"
                f"2. Tenho referência de arte\n"
                f"3. Não, vou precisar de criação de arte",

                f"Perfeito! {transicao} ✨\n\n"
                f"Você já tem a arte pronta, tem alguma referência ou prefere que a gente desenvolva?\n\n"
                f"1. Já tenho a arte criada\n"
                f"2. Tenho referência de arte\n"
                f"3. Não, vou precisar de criação de arte"
            )
            sessao["etapa"] = "arte"

    # ── ARTE ─────────────────────────────────
    elif etapa == "arte":
        primeiro = dados.get("nome", "").split()[0]
        produto_num = dados.get("produto_num", "1")
        aceita_3d = PRODUTOS.get(produto_num, {}).get("aceita_3d", False)

        if any(p in msg_lower for p in ["1", "já tenho", "ja tenho", "tenho arte", "tenho a arte", "pronta", "finalizada"]):
            dados["arte"] = "pronta"
            resposta = var(
                f"Perfeito, {primeiro}! ✨\n\n"
                f"Pode me enviar sua arte final? Assim consigo direcionar sua cotação com mais precisão.",
                f"Ótimo, {primeiro}! ✨\n\n"
                f"Pode me encaminhar sua arte final? Assim sigo com uma cotação mais alinhada ao que você imagina."
            )
            sessao["etapa"] = "papel"

        elif any(p in msg_lower for p in ["2", "referência", "referencia", "tenho referencia", "tenho referência"]):
            dados["arte"] = "referencia"
            resposta = var(
                f"Perfeito, {primeiro}! ✨\n\n"
                f"Pode me enviar a referência que deseja usar? Assim consigo direcionar sua cotação com mais precisão.",
                f"Ótimo! ✨\n\n"
                f"Se puder, me envie a referência visual. Assim consigo seguir com mais precisão na sua cotação."
            )
            sessao["etapa"] = "papel"

        elif any(p in msg_lower for p in ["3", "criação", "criacao", "preciso", "não tenho", "nao tenho", "precisa"]):
            dados["arte"] = "precisa_criacao"
            if aceita_3d:
                resposta = var(
                    f"Sem problema, {primeiro}! Podemos desenvolver isso para você. ✨\n\n"
                    f"Trabalhamos com:\n\n"
                    f"1. Criação de arte — R$ 74,90\n"
                    f"2. Criação de arte + amostra 3D — R$ 220,00\n"
                    f"3. Identidade visual / logomarca\n\n"
                    f"Qual faz mais sentido para o seu projeto?",

                    f"Sem problema! Podemos cuidar dessa parte para você. ✨\n\n"
                    f"As opções são:\n\n"
                    f"1. Criação de arte — R$ 74,90\n"
                    f"2. Criação de arte + amostra 3D — R$ 220,00\n"
                    f"3. Identidade visual / logomarca\n\n"
                    f"Qual delas faz mais sentido para o seu projeto?"
                )
            else:
                resposta = (
                    f"Sem problema, {primeiro}! Podemos desenvolver isso para você. ✨\n\n"
                    f"As opções são:\n\n"
                    f"1. Criação de arte — R$ 74,90\n"
                    f"2. Identidade visual / logomarca\n\n"
                    f"Qual faz mais sentido para o seu projeto?"
                )
            sessao["etapa"] = "arte_opcao"

        else:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Já tenho a arte criada\n"
                "2. Tenho referência de arte\n"
                "3. Não, vou precisar de criação de arte"
            )

    # ── ARTE OPÇÃO ────────────────────────────
    elif etapa == "arte_opcao":
        primeiro = dados.get("nome", "").split()[0]
        produto_num = dados.get("produto_num", "1")
        aceita_3d = PRODUTOS.get(produto_num, {}).get("aceita_3d", False)

        if any(p in msg_lower for p in ["3", "identidade", "logo", "logomarca", "marca"]):
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
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

        elif any(p in msg_lower for p in ["2", "3d", "amostra", "220"]) and aceita_3d:
            dados["criacao"] = "criacao_arte_3d"
            dados["valor_criacao"] = 220.00
            resposta = (
                f"Ótima escolha! A amostra 3D vai te dar uma visão incrível do resultado final. 🚀\n\n"
                f"Agora vamos ao material. Qual tipo de papel faz mais sentido para o seu projeto?\n\n"
                f"1. Couchê 300g\n"
                f"2. Ver catálogo de texturas (link abaixo)\n"
                f"3. Não sei, preciso de indicação\n\n"
                f"Se quiser conhecer melhor as texturas: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
                f"Veja também nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "papel"

        elif any(p in msg_lower for p in ["1", "simples", "74", "arte"]):
            dados["criacao"] = "criacao_simples"
            dados["valor_criacao"] = 74.90
            resposta = (
                f"Nossa equipe vai criar algo incrível para você. 😊\n\n"
                f"Agora vamos ao material. Qual tipo de papel faz mais sentido para o seu projeto?\n\n"
                f"1. Couchê 300g\n"
                f"2. Ver catálogo de texturas (link abaixo)\n"
                f"3. Não sei, preciso de indicação\n\n"
                f"Se quiser conhecer melhor as texturas: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
                f"Veja também nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "papel"

        else:
            tentativas += 1
            sessao["tentativas"] = tentativas
            opcoes = (
                "1. Criação de arte — R$ 74,90\n"
                "2. Criação de arte + amostra 3D — R$ 220,00\n"
                "3. Identidade visual / logomarca"
                if aceita_3d else
                "1. Criação de arte — R$ 74,90\n"
                "2. Identidade visual / logomarca"
            )
            resposta = f"Por favor, escolha uma das opções:\n\n{opcoes}"

    # ── PAPEL ─────────────────────────────────
    elif etapa == "papel":
        primeiro = dados.get("nome", "").split()[0]

        if any(p in msg_lower for p in ["1", "couche", "couchê", "300"]):
            dados["material"] = "Couchê 300g"
            resposta = (
                f"O Couchê 300g é nossa opção de entrada — e, para refletir o padrão Primyn, "
                f"trabalhamos obrigatoriamente com hot stamping ou relevo. "
                f"Sem um acabamento premium, ele se torna um cartão comum, "
                f"e isso não representa a sua marca da forma certa. ✨\n\n"
                f"Qual acabamento faz mais sentido para você?\n\n"
                f"1. Hot stamping\n"
                f"2. Alto relevo seco\n"
                f"3. Baixo relevo\n\n"
                f"Ou prefere explorar nossos papéis texturados?\n"
                f"4. Ver catálogo de texturas"
            )
            sessao["etapa"] = "papel_couche_acabamento"

        elif any(p in msg_lower for p in ["2", "catálogo", "catalogo", "textura", "ver", "link"]):
            resposta = (
                f"Para te ajudar a escolher o papel ideal, veja nosso catálogo completo: "
                f"https://www.primyn.com/pagina/tipos-de-papeis-e-texturas ✨\n\n"
                f"Os mais vendidos são o Conqueror Bamboo 400g e o Papel Notturno Black 450g — "
                f"ambos transmitem sofisticação desde o primeiro toque.\n\n"
                f"Qualquer papel do catálogo será considerado texturado premium. "
                f"Qual você prefere ou qual se aproxima mais da sua visão de marca?\n\n"
                f"Inspire-se também nos nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "papel_texturado_escolha"

        elif any(p in msg_lower for p in ["3", "não sei", "nao sei", "indicação", "indicacao", "sugestão", "sugestao"]):
            area = dados.get("area", "")
            papel_rec = dados.get("papel_recomendado", "Conqueror Bamboo 400g ou Notturno Black 450g")
            resposta = (
                f"Para a sua área, recomendamos especialmente: {papel_rec}\n\n"
                f"Esses papéis transmitem sofisticação e são os mais escolhidos pelos nossos clientes. ✨\n\n"
                f"Veja o catálogo completo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
                f"E nossos projetos: https://www.instagram.com/primyn.store/\n\n"
                f"Após ver o catálogo, me diz qual papel você escolheu:"
            )
            sessao["etapa"] = "papel_texturado_escolha"

        else:
            # Cliente digitou o nome de um papel diretamente
            dados["material"] = msg
            resposta = (
                f"Ótima escolha! ✨\n\n"
                f"Agora, em relação ao acabamento. Você já conhece nossos acabamentos premium?\n\n"
                f"1. Sim, já conheço\n"
                f"2. Não, gostaria de conhecer antes de escolher"
            )
            sessao["etapa"] = "acabamento_conhece"

    # ── PAPEL COUCHÊ ACABAMENTO ───────────────
    elif etapa == "papel_couche_acabamento":
        if any(p in msg_lower for p in ["4", "catálogo", "catalogo", "texturado", "textura", "explorar"]):
            resposta = (
                f"Ótima escolha explorar os texturados! ✨\n\n"
                f"Veja nosso catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                f"Os mais vendidos são o Conqueror Bamboo 400g e o Papel Notturno Black 450g.\n\n"
                f"Qual você prefere?\n\n"
                f"Inspire-se nos nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "papel_texturado_escolha"
        elif any(p in msg_lower for p in ["sem", "não quero", "nao quero", "nenhum", "só impressão", "so impressao"]):
            resposta = (
                f"Entendemos perfeitamente. "
                f"Quando quiser explorar uma proposta alinhada ao padrão premium da Primyn, estaremos por aqui. 😊"
            )
            dados["status"] = "fora_escopo"
            sessao["etapa"] = "encerrado"
        else:
            acabamento_map = {"1": "Hot stamping", "2": "Alto relevo seco", "3": "Baixo relevo"}
            acabamento = None
            for k, v in acabamento_map.items():
                if k in msg or v.lower() in msg_lower:
                    acabamento = v
                    break
            if acabamento:
                dados["acabamento"] = acabamento
                dados["material"] = dados.get("material", "Couchê 300g")
                resposta = f"Qual quantidade você está considerando para esse projeto? ✨"
                sessao["etapa"] = "quantidade"
            else:
                resposta = (
                    "Por favor, escolha uma das opções:\n\n"
                    "1. Hot stamping\n"
                    "2. Alto relevo seco\n"
                    "3. Baixo relevo\n"
                    "4. Ver catálogo de texturas"
                )

    # ── PAPEL TEXTURADO ESCOLHA ───────────────
    elif etapa == "papel_texturado_escolha":
        if len(msg.strip()) < 2:
            resposta = "Pode me dizer qual papel você escolheu no catálogo?"
        else:
            dados["material"] = msg
            resposta = (
                f"Ótima escolha! ✨\n\n"
                f"Você já conhece nossos acabamentos premium ou prefere que eu te apresente antes da escolha?\n\n"
                f"1. Sim, já conheço\n"
                f"2. Não, gostaria de conhecer"
            )
            sessao["etapa"] = "acabamento_conhece"

    # ── ACABAMENTO CONHECE ────────────────────
    elif etapa == "acabamento_conhece":
        if any(p in msg_lower for p in ["1", "sim", "já conheço", "ja conheco", "conheço", "conheco"]):
            resposta = var(
                "Perfeito! ✨\n\n"
                "Qual acabamento faz mais sentido para a sua marca?\n\n"
                "1. Hot stamping\n"
                "2. Alto relevo seco\n"
                "3. Baixo relevo\n"
                "4. Empastamento / borda sanduíche\n"
                "5. Impressão colorida no papel especial\n"
                "6. Combinação de acabamentos",

                "Ótimo! ✨\n\n"
                "Qual acabamento você escolheu para o seu material?\n\n"
                "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                "4. Empastamento / borda sanduíche\n"
                "5. Impressão colorida no papel especial\n"
                "6. Combinação de acabamentos\n\n"
                "Veja nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "acabamento"
        else:
            resposta = (
                "Perfeito! ✨ Trabalhamos com os seguintes acabamentos premium:\n\n"
                "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                "4. Empastamento / borda sanduíche\n"
                "5. Impressão colorida no papel especial\n"
                "6. Combinação de acabamentos\n\n"
                "Se quiser ver projetos com esses acabamentos: https://www.instagram.com/primyn.store/\n\n"
                "Qual faz mais sentido para a sua marca?"
            )
            sessao["etapa"] = "acabamento"

    # ── ACABAMENTO ────────────────────────────
    elif etapa == "acabamento":
        primeiro = dados.get("nome", "").split()[0]

        acabamento_map = {
            "1": "Hot stamping",
            "2": "Alto relevo seco",
            "3": "Baixo relevo",
            "4": "Empastamento / borda sanduíche",
            "5": "Impressão colorida no papel especial",
            "6": "Combinação de acabamentos"
        }
        opcao = validar_opcao(msg, acabamento_map)

        if not opcao:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                "4. Empastamento / borda sanduíche\n"
                "5. Impressão colorida no papel especial\n"
                "6. Combinação de acabamentos"
            )
        else:
            acabamento_nome = acabamento_map[opcao]
            dados["acabamento"] = acabamento_nome
            sessao["tentativas"] = 0

            if opcao == "4":
                resposta = (
                    f"Ótima escolha! O empastamento tem três finalidades: 👑\n\n"
                    f"1. Papel mais grosso — colar dois papéis para dar mais espessura e rigidez\n"
                    f"2. Evitar marcação do relevo — impede que o baixo relevo ou hot stamping "
                    f"apareça no lado oposto do papel\n"
                    f"3. Borda sanduíche (borda colorida) — o interior fica colorido, "
                    f"revelando uma cor especial ao olhar a borda do cartão\n\n"
                    f"Qual dessas finalidades faz mais sentido para o seu projeto?\n\n"
                    f"Saiba mais sobre empastamento: https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n\n"
                    f"Veja nossos projetos: https://www.instagram.com/primyn.store/"
                )
                sessao["etapa"] = "empastamento_detalhe"
            else:
                resposta = var(
                    f"Perfeito, {primeiro}! ✨\n\n"
                    f"Qual quantidade você está considerando para esse projeto?",
                    f"Ótimo! ✨\n\n"
                    f"Para calcular a média mais alinhada ao seu projeto, qual quantidade você está considerando?"
                )
                sessao["etapa"] = "quantidade"

    # ── EMPASTAMENTO DETALHE ──────────────────
    elif etapa == "empastamento_detalhe":
        if len(msg.strip()) < 2:
            resposta = (
                "Pode escolher a finalidade:\n\n"
                "1. Papel mais grosso\n"
                "2. Evitar marcação do relevo\n"
                "3. Borda sanduíche (borda colorida)"
            )
        else:
            dados["empastamento_tipo"] = msg
            resposta = "Qual quantidade você está considerando para esse projeto? ✨"
            sessao["etapa"] = "quantidade"

    # ── QUANTIDADE ────────────────────────────
    elif etapa == "quantidade":
        primeiro = dados.get("nome", "").split()[0]
        produto_num = dados.get("produto_num", "1")
        produto = PRODUTOS.get(produto_num, {})
        minimo = produto.get("minimo", 100)

        valido, qtd = validar_quantidade(msg, minimo)
        if not valido:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = (
                f"Por favor, informe uma quantidade válida. "
                f"A quantidade mínima para esse produto é {minimo} unidades.\n\n"
                f"Ex: 250, 500, 1000"
            )
        else:
            sessao["tentativas"] = 0
            aviso_minimo = ""
            if qtd < minimo:
                aviso_minimo = (
                    f"Nossa quantidade mínima para {produto.get('nome', 'esse produto')} "
                    f"é {minimo} unidades. Vou considerar {minimo} unidades na estimativa.\n\n"
                )
                qtd = minimo

            dados["quantidade"] = qtd
            media = calcular_media(produto_num, dados.get("material", ""), qtd)
            valor_criacao = dados.get("valor_criacao", 0)
            if valor_criacao:
                media += valor_criacao
            dados["media"] = media

            if media == 0:
                resposta = (
                    f"{aviso_minimo}"
                    f"Para essa composição, o investimento é definido sob consulta, {primeiro}. 😊\n\n"
                    f"Vou encaminhar seu projeto para um especialista preparar a proposta ideal.\n\n"
                    f"Gostaria de prosseguir com a proposta personalizada?\n\n"
                    f"1. Sim, quero a proposta\n"
                    f"2. Preciso pensar\n"
                    f"3. Não, obrigada"
                )
            else:
                media_fmt = fmt_brl(media)
                resposta_base = (
                    f"{aviso_minimo}"
                    f"Perfeito, {primeiro}! ✨\n\n"
                    f"Para a configuração que você me passou, o investimento médio fica em torno de {media_fmt}. "
                    f"Esse valor é uma referência e o orçamento final é personalizado conforme "
                    f"acabamento, criação e complexidade do projeto. 👑\n\n"
                    f"Faz sentido para você prosseguirmos com uma proposta personalizada?\n\n"
                    f"1. Sim, quero a proposta\n"
                    f"2. Preciso pensar\n"
                    f"3. Não, obrigada"
                )

                # Upsell só para cartão de visita
                if produto_num == "1" and not dados.get("upsell_feito"):
                    dados["upsell_feito"] = True
                    resposta = resposta_base + f"\n\n{MSG_UPSELL}"
                    sessao["etapa"] = "upsell_resposta"
                else:
                    resposta = resposta_base
                    sessao["etapa"] = "media_proposta"

    # ── UPSELL RESPOSTA ───────────────────────
    elif etapa == "upsell_resposta":
        primeiro = dados.get("nome", "").split()[0]
        if any(p in msg_lower for p in ["1", "quero conhecer", "sim", "papelaria", "completa", "kit"]):
            dados["produto"] = "Papelaria Completa"
            dados["produto_num"] = "5"
            resposta = (
                f"Que decisão incrível, {primeiro}! 👑\n\n"
                f"A papelaria completa transmite coerência visual em cada ponto de contato.\n\n"
                f"O investimento parte de R$ 4.200,00 no Couchê e R$ 5.800,00 em papel especial, "
                f"variando conforme composição e acabamentos.\n\n"
                f"Em breve um especialista vai preparar a proposta completa para você."
            )
            dados["status"] = "handoff"
            sessao["etapa"] = "handoff"
            handoff_data = dados
        else:
            resposta = (
                f"Sem problema! Vamos seguir com o cartão. 😊\n\n"
                f"Faz sentido prosseguirmos com a proposta personalizada?\n\n"
                f"1. Sim, quero a proposta\n"
                f"2. Preciso pensar\n"
                f"3. Não, obrigada"
            )
            sessao["etapa"] = "media_proposta"

    # ── MÉDIA / PROPOSTA ──────────────────────
    elif etapa == "media_proposta":
        primeiro = dados.get("nome", "").split()[0]

        if any(p in msg_lower for p in ["1", "sim", "quero", "pode", "ok", "vamos", "claro", "s"]):
            resposta = var(
                f"Maravilha! ✨\n\n"
                f"Só preciso de mais uma informação: você tem algum prazo ou data importante "
                f"para receber esse material?",
                f"Ótimo, {primeiro}! ✨\n\n"
                f"Para concluir seu atendimento, existe algum prazo importante para receber esse material?"
            )
            sessao["etapa"] = "urgencia"

        elif any(p in msg_lower for p in ["2", "pensar", "depois", "calma", "ainda não", "ainda nao", "talvez"]):
            resposta = var(
                f"Claro! ✨ Sem pressa. Quando quiser retomar, estaremos por aqui.\n\n"
                f"Se desejar, acompanhe nossos projetos em @primyn.store",
                f"Sem problema algum, {primeiro}. Esse tipo de decisão merece ser feito com calma. "
                f"Quando quiser retomar, será um prazer continuar seu atendimento."
            )
            dados["status"] = "aguardando_resposta"
            sessao["etapa"] = "encerrado"
            try:
                from followup import agendar_followup
                agendar_followup(numero, dados.get("nome", ""), "pensar", dias=2)
            except:
                pass

        elif any(p in msg_lower for p in ["3", "não", "nao", "obrigada", "obrigado", "cancelar"]):
            resposta = var(
                f"Sem problemas, {primeiro}! ✨\n\n"
                f"Agradeço pelo seu tempo e fico à disposição caso queira retomar seu projeto em outro momento.",
                f"Claro! Obrigada pelo seu contato. "
                f"Quando quiser explorar uma proposta com a Primyn, será um prazer te atender."
            )
            dados["status"] = "perdido"
            sessao["etapa"] = "encerrado"

        else:
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Sim, quero a proposta\n"
                "2. Preciso pensar\n"
                "3. Não, obrigada"
            )

    # ── URGÊNCIA ──────────────────────────────
    elif etapa == "urgencia":
        dados["urgencia"] = msg
        primeiro = dados.get("nome", "").split()[0]

        urgente = any(p in msg_lower for p in [
            "urgente", "rápido", "rapido", "pressa", "amanhã", "amanha",
            "essa semana", "semana", "logo", "dias"
        ])

        aviso = ""
        if urgente:
            aviso = (
                "Perfeito! Projetos com criação e produção premium costumam ter prazo médio "
                "de 7 a 10 dias úteis. Vou deixar isso sinalizado no seu direcionamento "
                "para que seu especialista considere essa prioridade.\n\n"
            )

        resposta = (
            f"{aviso}"
            f"{MSG_EDUCATIVA}\n\n"
            f"Incrível! Vou te encaminhar para um especialista que dará continuidade ao seu atendimento, "
            f"com opção de reunião estratégica, caso preferir, para garantir que tudo esteja perfeito "
            f"antes de elaborar a proposta exclusiva para o seu projeto. 😊"
        )
        dados["status"] = "handoff"
        sessao["etapa"] = "handoff"
        handoff_data = dados

    # ── HANDOFF ───────────────────────────────
    elif etapa == "handoff":
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Antes de encerrar, {primeiro}, como foi sua experiência "
            f"com este atendimento inicial? 😊\n\n"
            f"Sua opinião nos ajuda a melhorar cada vez mais."
        )
        sessao["etapa"] = "feedback"

    # ── FEEDBACK ──────────────────────────────
    elif etapa == "feedback":
        dados["avaliacao"] = msg
        primeiro = dados.get("nome", "").split()[0]
        resposta = (
            f"Muito obrigada pelo feedback, {primeiro}! "
            f"Foi um prazer te atender. Até breve! 🤍"
        )
        sessao["etapa"] = "encerrado"

    # ── ENCERRADO ─────────────────────────────
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
            "Sou a Mily. Como posso te ajudar?\n\n"
            "1. Primeira vez\n"
            "2. Já sou cliente\n"
            "3. Já falei com vocês antes"
        )
        sessao["etapa"] = "triagem_inicial"

    sessao["dados"] = dados
    atualizar_sessao(numero, sessao)
    return resposta, handoff_data
