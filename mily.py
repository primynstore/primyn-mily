
# ═══════════════════════════════════════════════
# PRIMYN STUDIO — AGENTE MILY v7
# Script oficial + fluxo corrigido
# ═══════════════════════════════════════════════

import json
import os
import random
from datetime import datetime

DB_FILE = "sessoes.json"

PRODUTOS = {
    "1": {"key": "cartao_visita", "nome": "Cartão de Visita / TAG / Cartões similares", "minimo": 250,
          "formatos": "5×9 cm (tradicional), 5×8 cm (americano) ou personalizado", "aceita_3d": True,
          "medias": {"250": {"essencial": 378, "luxo_black": 562, "luxo_white": 898, "prestigio": 1297},
                     "500": {"essencial": 475, "luxo_black": 839, "luxo_white": 1284, "prestigio": 1682},
                     "1000": {"essencial": 588, "luxo_black": 1184, "luxo_white": 1568, "prestigio": 2567}}},
    "2": {"key": "pasta", "nome": "Pasta com bolsa ou orelha", "minimo": 100,
          "formatos": "31×22 cm (fechada)", "aceita_3d": False,
          "medias": {"100": {"essencial": 2500, "luxo_black": 2500, "luxo_white": 2500, "prestigio": 2500},
                     "250": {"essencial": 3800, "luxo_black": 3800, "luxo_white": 3800, "prestigio": 3800},
                     "500": {"essencial": 5500, "luxo_black": 5500, "luxo_white": 5500, "prestigio": 5500}}},
    "3": {"key": "envelope", "nome": "Envelope Ofício / Envelope Saco", "minimo": 100,
          "formatos": "Ofício: 11,4×22,9 cm | Saco: 22,9×32,4 cm", "aceita_3d": False,
          "medias": {"100": {"essencial": 720, "luxo_black": 720, "luxo_white": 720, "prestigio": 720},
                     "250": {"essencial": 1050, "luxo_black": 1050, "luxo_white": 1050, "prestigio": 1050},
                     "500": {"essencial": 1590, "luxo_black": 1590, "luxo_white": 1590, "prestigio": 1590}}},
    "4": {"key": "timbrado", "nome": "Papel Timbrado / Receituário", "minimo": 250,
          "formatos": "A4 (29,7×21 cm) ou A5 (15×20 cm)", "aceita_3d": False,
          "medias": {"250": {"essencial": 650, "luxo_black": 650, "luxo_white": 650, "prestigio": 650},
                     "500": {"essencial": 890, "luxo_black": 890, "luxo_white": 890, "prestigio": 890},
                     "1000": {"essencial": 1190, "luxo_black": 1190, "luxo_white": 1190, "prestigio": 1190}}},
    "5": {"key": "papelaria_completa", "nome": "Papelaria Completa", "minimo": 250,
          "formatos": "Variável conforme composição do kit", "aceita_3d": False,
          "medias": {"250": {"essencial": 4200, "luxo_black": 4200, "luxo_white": 5800, "prestigio": 5800},
                     "500": {"essencial": 5800, "luxo_black": 5800, "luxo_white": 7500, "prestigio": 7500}}}
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
    "6": "Conqueror Bamboo 400g ou Notturno Black 450g"
}

TRANSICOES_AREA = {
    "1": "Advocacia — uma área que exige precisão e autoridade em cada detalhe.",
    "2": "Arquitetura — uma área que exige sofisticação em cada detalhe.",
    "3": "Medicina — confiança e credibilidade que se refletem em cada peça.",
    "4": "Moda e beleza — estética e identidade visual que falam antes das palavras.",
    "5": "Finanças — onde a percepção de solidez faz toda a diferença.",
    "6": "Sua área merece uma identidade visual que reflita seu posicionamento."
}

ACOLHIMENTOS = ["Perfeito", "Ótimo", "Que bom", "Sem problema", "Claro", "Maravilha", "Ótima escolha"]

def acolher():
    return random.choice(ACOLHIMENTOS)

def var(*opcoes):
    return random.choice(opcoes)

def fmt_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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

def validar_quantidade(msg, minimo=100):
    try:
        num = int(''.join(filter(str.isdigit, msg)))
        if num > 0:
            return True, num
    except:
        pass
    return False, None

def detectar_produtos(msg):
    """Detecta múltiplos produtos na mensagem."""
    msg_lower = msg.lower()
    encontrados = []
    mapa = {
        "1": ["1", "cartão", "cartao", "visita", "tag", "cartões", "cartoes"],
        "2": ["2", "pasta", "bolsa", "orelha"],
        "3": ["3", "envelope", "ofício", "oficio", "saco"],
        "4": ["4", "timbrado", "receituário", "receituario"],
        "5": ["5", "papelaria completa", "kit", "completa"]
    }
    for num, palavras in mapa.items():
        for p in palavras:
            if p in msg_lower and num not in encontrados:
                encontrados.append(num)
                break
    return encontrados

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
            "ultimo_contato": datetime.now().isoformat(), "tentativas": 0
        }
        salvar_sessoes(sessoes)
    return sessoes[numero]

def atualizar_sessao(numero, sessao):
    sessoes = carregar_sessoes()
    sessao["ultimo_contato"] = datetime.now().isoformat()
    sessoes[numero] = sessao
    salvar_sessoes(sessoes)

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
            "Me conta: essa é a sua primeira vez conosco, você já é cliente "
            "ou já falou com a gente anteriormente?",

            "Olá! Seja muito bem-vindo(a) à Primyn. ✨\n\n"
            "Sou a Mily, consultora virtual da Primyn, e vou te acompanhar neste "
            "primeiro atendimento para entender o seu projeto com mais precisão. "
            "Ao final, um especialista dará continuidade para garantir que cada detalhe "
            "fique exatamente como você deseja.\n\n"
            "Para começarmos: essa é a sua primeira vez aqui, você já é cliente "
            "ou já conversou com a gente antes?",

            "Olá! Que bom ter você por aqui.\n\n"
            "Sou a Mily, consultora virtual da Primyn, e vou reunir as informações do seu "
            "projeto para direcionar seu atendimento da forma mais estratégica possível. "
            "Ao final, um especialista dará continuidade ao seu projeto.\n\n"
            "Me conta: você já conhece a Primyn ou é a primeira vez que nos procura?"
        )
        sessao["etapa"] = "triagem_inicial"
        sessao["tentativas"] = 0

    # ── TRIAGEM ───────────────────────────────
    elif etapa == "triagem_inicial":
        if any(p in msg_lower for p in ["2", "já sou", "ja sou", "cliente", "já comprei", "ja comprei", "sou cliente"]):
            dados["tipo_contato"] = "cliente_recorrente"
            sessao["fluxo"] = "cliente_recorrente"
            resposta = var(
                "Que bom te ver de volta! 😊\n\nQual é o seu nome e sobrenome?",
                "Ótimo ter você de volta! Me diz seu nome e sobrenome para eu localizar seu cadastro."
            )
            sessao["etapa"] = "nome"

        elif any(p in msg_lower for p in ["3", "já falei", "ja falei", "voltei", "antes", "já conversei", "ja conversei"]):
            dados["tipo_contato"] = "lead_antigo"
            sessao["fluxo"] = "lead_antigo"
            resposta = var(
                "Que bom que voltou! 😊\n\nQual é o seu nome e sobrenome?",
                "Fico feliz que tenha voltado. Me diz seu nome e sobrenome para eu encontrar seu histórico."
            )
            sessao["etapa"] = "nome"

        else:
            dados["tipo_contato"] = "novo_lead"
            sessao["fluxo"] = "novo_lead"
            resposta = var(
                "Que ótimo ter você por aqui! ✨\n\nComo você conheceu a Primyn?\n\n"
                "1. Google\n2. Instagram\n3. Indicação\n4. Outro",
                "Seja muito bem-vindo(a)! Como você nos encontrou?\n\n"
                "1. Google\n2. Instagram\n3. Indicação\n4. Outro"
            )
            sessao["etapa"] = "origem"

    # ── ORIGEM (só novo lead) ─────────────────
    elif etapa == "origem":
        origens = {"1": "Google", "2": "Instagram", "3": "Indicação", "4": "Outro"}
        origem = None
        for k, v in origens.items():
            if k in msg or v.lower() in msg_lower:
                origem = v
                break
        dados["origem"] = origem or msg
        resposta = var(
            "Que ótimo que nos encontrou por lá! ✨\n\nQual é o seu nome e sobrenome?",
            "Fico feliz que tenha chegado até nós! Me conta: qual é o seu nome e sobrenome?"
        )
        sessao["etapa"] = "nome"
        sessao["tentativas"] = 0

    # ── NOME ─────────────────────────────────
    elif etapa == "nome":
        valido, nome_fmt = validar_nome(msg)
        if not valido:
            tentativas += 1
            if tentativas >= 3:
                nome_fmt = msg.strip().title()
                dados["nome"] = nome_fmt
                primeiro = nome_fmt.split()[0]
                sessao["tentativas"] = 0
                fluxo = sessao.get("fluxo")
                if fluxo == "cliente_recorrente":
                    sessao["etapa"] = "produto"
                    resposta = f"Olá, {primeiro}! Me conta: qual material você gostaria de produzir desta vez?\n\n1. Cartão de Visita / TAG / Cartões similares\n2. Pasta com bolsa ou orelha\n3. Envelope Ofício / Envelope Saco\n4. Papel Timbrado / Receituário\n5. Papelaria Completa"
                else:
                    sessao["etapa"] = "email"
                    resposta = f"{acolher()}, {primeiro}! Qual é o seu melhor e-mail para envio da proposta?"
            else:
                sessao["tentativas"] = tentativas
                resposta = var(
                    "Pode me dizer seu nome e sobrenome?",
                    "Para seguirmos, preciso do seu nome e sobrenome."
                )
        else:
            dados["nome"] = nome_fmt
            primeiro = nome_fmt.split()[0]
            sessao["tentativas"] = 0
            fluxo = sessao.get("fluxo")

            if fluxo == "cliente_recorrente":
                resposta = var(
                    f"Que prazer, {primeiro}! Já te localizo aqui no sistema.\n\nMe conta: qual material você gostaria de produzir desta vez?\n\n1. Cartão de Visita / TAG / Cartões similares\n2. Pasta com bolsa ou orelha\n3. Envelope Ofício / Envelope Saco\n4. Papel Timbrado / Receituário\n5. Papelaria Completa",
                    f"Que bom ter você de volta, {primeiro}! Qual projeto você gostaria de produzir?\n\n1. Cartão de Visita / TAG / Cartões similares\n2. Pasta com bolsa ou orelha\n3. Envelope Ofício / Envelope Saco\n4. Papel Timbrado / Receituário\n5. Papelaria Completa"
                )
                sessao["etapa"] = "produto"

            elif fluxo == "lead_antigo":
                resposta = var(
                    f"Encontrei seu histórico, {primeiro}! Como prefere prosseguir?\n\n1. Retomar projeto anterior\n2. Começar projeto novo",
                    f"Ótimo, {primeiro}! Você prefere retomar o projeto anterior ou começar algo novo?\n\n1. Retomar projeto anterior\n2. Começar projeto novo"
                )
                sessao["etapa"] = "retomar_ou_novo"

            else:
                resposta = var(
                    f"{acolher()}, {primeiro}! Qual é o seu melhor e-mail para envio da proposta?",
                    f"Prazer, {primeiro}! Para que sua proposta chegue certinha até você, qual e-mail prefere usar?"
                )
                sessao["etapa"] = "email"

    # ── EMAIL ─────────────────────────────────
    elif etapa == "email":
        valido, email_fmt = validar_email(msg)
        primeiro = dados.get("nome", "").split()[0]
        if not valido:
            tentativas += 1
            if tentativas >= 3:
                dados["email"] = ""
                sessao["tentativas"] = 0
                sessao["etapa"] = "produto"
                resposta = f"Sem problema! Seguiremos sem o e-mail por enquanto.\n\nQual projeto você gostaria de produzir, {primeiro}?\n\n1. Cartão de Visita / TAG / Cartões similares\n2. Pasta com bolsa ou orelha\n3. Envelope Ofício / Envelope Saco\n4. Papel Timbrado / Receituário\n5. Papelaria Completa"
            else:
                sessao["tentativas"] = tentativas
                resposta = "Esse e-mail não parece válido. Pode me passar seu endereço completo? Ex: seunome@gmail.com"
        else:
            dados["email"] = email_fmt
            sessao["tentativas"] = 0
            resposta = var(
                f"Maravilha, {primeiro}! Qual projeto você gostaria de produzir?\n\n1. Cartão de Visita / TAG / Cartões similares\n2. Pasta com bolsa ou orelha\n3. Envelope Ofício / Envelope Saco\n4. Papel Timbrado / Receituário\n5. Papelaria Completa",
                f"{acolher()}, {primeiro}! Me conta: qual projeto você gostaria de produzir?\n\n1. Cartão de Visita / TAG / Cartões similares\n2. Pasta com bolsa ou orelha\n3. Envelope Ofício / Envelope Saco\n4. Papel Timbrado / Receituário\n5. Papelaria Completa"
            )
            sessao["etapa"] = "produto"

    # ── RETOMAR OU NOVO ───────────────────────
    elif etapa == "retomar_ou_novo":
        primeiro = dados.get("nome", "").split()[0]
        if any(p in msg_lower for p in ["1", "retomar", "anterior", "mesmo", "continuar"]):
            resposta = (
                f"Incrível! Vou te encaminhar para um especialista que dará continuidade ao seu atendimento, "
                f"com opção de reunião estratégica, caso preferir, para garantir que tudo esteja perfeito "
                f"antes de elaborar a proposta exclusiva para o seu projeto. 😊"
            )
            dados["status"] = "handoff"
            sessao["etapa"] = "handoff"
            handoff_data = dados
        else:
            sessao["fluxo"] = "novo_lead"
            resposta = f"Que bom! Me conta: qual projeto você gostaria de produzir, {primeiro}?\n\n1. Cartão de Visita / TAG / Cartões similares\n2. Pasta com bolsa ou orelha\n3. Envelope Ofício / Envelope Saco\n4. Papel Timbrado / Receituário\n5. Papelaria Completa"
            sessao["etapa"] = "produto"

    # ── PRODUTO ───────────────────────────────
    elif etapa == "produto":
        primeiro = dados.get("nome", "").split()[0]
        produtos_escolhidos = detectar_produtos(msg)

        if not produtos_escolhidos:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = "Por favor, escolha uma ou mais opções:\n\n1. Cartão de Visita / TAG / Cartões similares\n2. Pasta com bolsa ou orelha\n3. Envelope Ofício / Envelope Saco\n4. Papel Timbrado / Receituário\n5. Papelaria Completa"
        else:
            sessao["tentativas"] = 0
            dados["produtos_escolhidos"] = produtos_escolhidos
            dados["produto_atual_idx"] = 0

            # Se escolheu papelaria completa (opção 5) entre os produtos
            if "5" in produtos_escolhidos and len(produtos_escolhidos) == 1:
                resposta = (
                    f"Papelaria completa é um projeto especial, {primeiro}. 👑\n\n"
                    f"O kit inclui cartão de visita, papel timbrado, pasta e envelope "
                    f"com a mesma identidade visual — coerência e sofisticação em cada ponto de contato.\n\n"
                    f"Faz sentido prosseguirmos com uma proposta personalizada?\n\n"
                    f"1. Sim, quero a proposta\n"
                    f"2. Prefiro pensar um pouco mais"
                )
                dados["produto_num"] = "5"
                dados["produto"] = PRODUTOS["5"]["nome"]
                sessao["etapa"] = "papelaria_completa_confirma"
            else:
                # Filtra papelaria completa se vier junto com outros
                outros = [p for p in produtos_escolhidos if p != "5"]
                if not outros:
                    outros = produtos_escolhidos
                dados["produtos_escolhidos"] = outros
                dados["produto_atual_idx"] = 0
                produto_num = outros[0]
                produto = PRODUTOS[produto_num]
                dados["produto_num"] = produto_num
                dados["produto"] = produto["nome"]

                # Upsell antes do formato (só se escolheu só cartão)
                if produto_num == "1" and len(outros) == 1 and not dados.get("upsell_feito"):
                    dados["upsell_feito"] = True
                    resposta = (
                        f"Ótima escolha! ✨\n\n"
                        f"Além do cartão, você sabia que a papelaria completa — cartão, timbrado, "
                        f"pasta e envelope com a mesma identidade — multiplica a percepção de valor "
                        f"da sua marca e posiciona você como referência no seu segmento?\n\n"
                        f"Gostaria de conhecer essa opção ou prefere seguir só com o cartão?\n\n"
                        f"1. Quero conhecer a papelaria completa\n"
                        f"2. Seguir com o cartão de visita"
                    )
                    sessao["etapa"] = "upsell_resposta"
                else:
                    resposta = (
                        f"Ótima escolha! Para {produto['nome']}, trabalhamos com o formato {produto['formatos']}.\n\n"
                        f"Esse formato atende ao seu projeto?\n\n"
                        f"1. Sim, está ótimo\n"
                        f"2. Prefiro um formato diferente"
                    )
                    sessao["etapa"] = "confirmar_formato"

    # ── UPSELL RESPOSTA ───────────────────────
    elif etapa == "upsell_resposta":
        primeiro = dados.get("nome", "").split()[0]
        if any(p in msg_lower for p in ["1", "quero", "sim", "papelaria", "completa", "kit", "conhecer"]):
            dados["produto_num"] = "5"
            dados["produto"] = PRODUTOS["5"]["nome"]
            resposta = (
                f"Que decisão incrível, {primeiro}! 👑\n\n"
                f"O kit inclui cartão de visita, papel timbrado, pasta e envelope "
                f"com a mesma identidade visual — coerência em cada ponto de contato da sua marca.\n\n"
                f"Faz sentido prosseguirmos com uma proposta personalizada?\n\n"
                f"1. Sim, quero a proposta\n"
                f"2. Prefiro pensar um pouco mais"
            )
            sessao["etapa"] = "papelaria_completa_confirma"
        else:
            produto = PRODUTOS["1"]
            resposta = (
                f"Sem problema! Vamos seguir com o cartão. ✨\n\n"
                f"Para {produto['nome']}, trabalhamos com o formato {produto['formatos']}.\n\n"
                f"Esse formato atende ao seu projeto?\n\n"
                f"1. Sim, está ótimo\n"
                f"2. Prefiro um formato diferente"
            )
            sessao["etapa"] = "confirmar_formato"

    # ── PAPELARIA COMPLETA CONFIRMA ───────────
    elif etapa == "papelaria_completa_confirma":
        primeiro = dados.get("nome", "").split()[0]
        if any(p in msg_lower for p in ["1", "sim", "quero", "pode", "vamos"]):
            resposta = (
                f"Incrível! Vou te encaminhar para um especialista que dará continuidade ao seu atendimento, "
                f"com opção de reunião estratégica, caso preferir, para garantir que tudo esteja perfeito "
                f"antes de elaborar a proposta exclusiva para o seu projeto. 😊"
            )
            dados["status"] = "handoff"
            sessao["etapa"] = "handoff"
            handoff_data = dados
        else:
            resposta = f"Claro, {primeiro}! Sem pressa. Quando quiser retomar, estaremos por aqui. 😊"
            dados["status"] = "aguardando_resposta"
            sessao["etapa"] = "encerrado"

    # ── CONFIRMAR FORMATO ─────────────────────
    elif etapa == "confirmar_formato":
        produto_num = dados.get("produto_num", "1")
        produto = PRODUTOS[produto_num]
        if any(p in msg_lower for p in ["2", "diferente", "personalizado", "outro", "nao", "não"]):
            resposta = "Me conta qual formato você prefere para o seu projeto:"
            sessao["etapa"] = "formato_personalizado"
        else:
            dados["formato"] = produto["formatos"]
            sessao["etapa"] = "area"
            resposta = var(
                "Perfeito! Para recomendarmos o material mais alinhado à sua marca, em qual área você atua?\n\n1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro",
                "Ótimo! Em qual área você atua?\n\n1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro"
            )

    # ── FORMATO PERSONALIZADO ─────────────────
    elif etapa == "formato_personalizado":
        if len(msg.strip()) < 2:
            resposta = "Pode me descrever o formato que você deseja? Ex: 8×5 cm, A5, etc."
        else:
            dados["formato"] = msg
            sessao["etapa"] = "area"
            resposta = "Anotei! Em qual área você atua?\n\n1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro"

    # ── ÁREA ─────────────────────────────────
    elif etapa == "area":
        opcao = None
        for k, v in AREAS.items():
            if k in msg or any(p in msg_lower for p in v.lower().split(" / ")):
                opcao = k
                break
        primeiro = dados.get("nome", "").split()[0]

        if not opcao:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = "Por favor, escolha uma das opções:\n\n1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro"
        else:
            dados["area"] = AREAS[opcao]
            papel_rec = PAPEIS_POR_AREA.get(opcao, "Conqueror Bamboo 400g ou Notturno Black 450g")
            dados["papel_recomendado"] = papel_rec
            sessao["tentativas"] = 0
            transicao = TRANSICOES_AREA.get(opcao, "")

            resposta = (
                f"{transicao}\n\n"
                f"Os papéis mais solicitados para essa área são o Conqueror Bamboo 400g e o Notturno Black 450g — "
                f"ambos transmitem sofisticação desde o primeiro toque.\n\n"
                f"Você já possui a arte ou tem alguma referência visual?\n\n"
                f"1. Já tenho arte pronta\n"
                f"2. Não tenho arte / tenho referência — vou precisar de criação"
            )
            sessao["etapa"] = "arte"

    # ── ARTE ─────────────────────────────────
    elif etapa == "arte":
        primeiro = dados.get("nome", "").split()[0]

        if any(p in msg_lower for p in ["1", "já tenho", "ja tenho", "tenho arte", "pronta", "finalizada"]):
            dados["arte"] = "pronta"
            resposta = var(
                f"Ótimo! Pode me enviar sua arte? Assim consigo direcionar sua cotação com mais precisão.",
                f"Perfeito! Me encaminha a arte final quando puder. Assim sigo com uma cotação mais alinhada."
            )
            sessao["etapa"] = "arte_recebida"

        elif any(p in msg_lower for p in ["2", "não tenho", "nao tenho", "referência", "referencia", "criação", "criacao", "preciso", "precisa"]):
            dados["arte"] = "referencia_ou_criacao"
            resposta = var(
                f"Sem problema! Pode me enviar a referência para orçamento? Assim consigo entender melhor o projeto.",
                f"Claro! Me manda a referência visual que você tem em mente. Isso me ajuda a direcionar a cotação com mais precisão."
            )
            sessao["etapa"] = "referencia_recebida"

        else:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = "Por favor, escolha uma das opções:\n\n1. Já tenho arte pronta\n2. Não tenho arte / tenho referência — vou precisar de criação"

    # ── ARTE RECEBIDA ─────────────────────────
    elif etapa == "arte_recebida":
        dados["arte_enviada"] = True
        resposta = var(
            "Recebi! Agora vamos ao material.\n\nQual tipo de papel faz mais sentido para o seu projeto?\n\n1. Couchê 300g\n2. Ver catálogo de texturas\n3. Não sei, preciso de indicação\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\nProjetos: https://www.instagram.com/primyn.store/",
            "Perfeito, recebi! Qual tipo de papel você imagina para esse projeto?\n\n1. Couchê 300g\n2. Ver catálogo de texturas\n3. Não sei, preciso de indicação\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas"
        )
        sessao["etapa"] = "papel"

    # ── REFERÊNCIA RECEBIDA ───────────────────
    elif etapa == "referencia_recebida":
        dados["referencia_enviada"] = True
        primeiro = dados.get("nome", "").split()[0]
        produto_num = dados.get("produto_num", "1")
        aceita_3d = PRODUTOS.get(produto_num, {}).get("aceita_3d", False)

        if aceita_3d:
            resposta = (
                f"Recebi a referência! Com base nisso, você vai precisar de criação de arte?\n\n"
                f"1. Sim — Criação de arte — R$ 74,90\n"
                f"2. Sim — Criação de arte + amostra 3D — R$ 220,00\n"
                f"3. Sim — Identidade visual / logomarca\n"
                f"4. Não, a referência já é a arte final"
            )
        else:
            resposta = (
                f"Recebi a referência! Com base nisso, você vai precisar de criação de arte?\n\n"
                f"1. Sim — Criação de arte — R$ 74,90\n"
                f"2. Sim — Identidade visual / logomarca\n"
                f"3. Não, a referência já é a arte final"
            )
        sessao["etapa"] = "criacao_pos_referencia"

    # ── CRIAÇÃO PÓS REFERÊNCIA ────────────────
    elif etapa == "criacao_pos_referencia":
        primeiro = dados.get("nome", "").split()[0]
        produto_num = dados.get("produto_num", "1")
        aceita_3d = PRODUTOS.get(produto_num, {}).get("aceita_3d", False)

        if any(p in msg_lower for p in ["identidade", "logo", "logomarca"]) or (aceita_3d and "3" in msg) or (not aceita_3d and "2" in msg):
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
            # Não encerra — pergunta se quer continuar com cotação
            resposta = (
                f"Identidade visual é um projeto especial — vou acionar nossa designer Ane para te atender. 👑\n\n"
                f"Enquanto isso, gostaria de seguir com a cotação do material usando a referência enviada?\n\n"
                f"1. Sim, quero seguir com a cotação também\n"
                f"2. Não, prefiro aguardar a identidade visual primeiro"
            )
            sessao["etapa"] = "identidade_continuar"

        elif ("2" in msg and aceita_3d) or "3d" in msg_lower or "220" in msg:
            dados["criacao"] = "criacao_arte_3d"
            dados["valor_criacao"] = 220.00
            resposta = "Ótima escolha! A amostra 3D vai te dar uma visão incrível do resultado final.\n\nQual tipo de papel faz mais sentido?\n\n1. Couchê 300g\n2. Ver catálogo de texturas\n3. Não sei, preciso de indicação\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\nProjetos: https://www.instagram.com/primyn.store/"
            sessao["etapa"] = "papel"

        elif any(p in msg_lower for p in ["não", "nao", "4" if aceita_3d else "3", "final", "já é", "ja e"]):
            dados["criacao"] = "sem_criacao"
            dados["valor_criacao"] = 0
            resposta = "Ótimo! Qual tipo de papel faz mais sentido para o seu projeto?\n\n1. Couchê 300g\n2. Ver catálogo de texturas\n3. Não sei, preciso de indicação\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\nProjetos: https://www.instagram.com/primyn.store/"
            sessao["etapa"] = "papel"

        else:
            dados["criacao"] = "criacao_simples"
            dados["valor_criacao"] = 74.90
            resposta = "Perfeito! Qual tipo de papel faz mais sentido para o seu projeto?\n\n1. Couchê 300g\n2. Ver catálogo de texturas\n3. Não sei, preciso de indicação\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\nProjetos: https://www.instagram.com/primyn.store/"
            sessao["etapa"] = "papel"

    # ── IDENTIDADE CONTINUAR ──────────────────
    elif etapa == "identidade_continuar":
        if any(p in msg_lower for p in ["1", "sim", "quero", "seguir"]):
            resposta = "Ótimo! Qual tipo de papel faz mais sentido para o seu projeto?\n\n1. Couchê 300g\n2. Ver catálogo de texturas\n3. Não sei, preciso de indicação\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\nProjetos: https://www.instagram.com/primyn.store/"
            sessao["etapa"] = "papel"
        else:
            primeiro = dados.get("nome", "").split()[0]
            dados["status"] = "handoff_designer"
            resposta = (
                f"Claro, {primeiro}! Nossa designer Ane entrará em contato em breve. 😊\n\n"
                f"Incrível! Vou te encaminhar para um especialista que dará continuidade ao seu atendimento, "
                f"com opção de reunião estratégica, caso preferir."
            )
            sessao["etapa"] = "handoff"
            handoff_data = dados

    # ── PAPEL ─────────────────────────────────
    elif etapa == "papel":
        primeiro = dados.get("nome", "").split()[0]

        if any(p in msg_lower for p in ["1", "couche", "couchê", "300"]):
            dados["material"] = "Couchê 300g"
            resposta = (
                f"O Couchê 300g é nossa opção de entrada — e, para refletir o padrão Primyn, "
                f"trabalhamos obrigatoriamente com hot stamping ou relevo. "
                f"Sem um acabamento premium, ele se torna um cartão comum.\n\n"
                f"Qual acabamento faz mais sentido para você?\n\n"
                f"1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                f"2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                f"3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n\n"
                f"Ou prefere explorar nossos papéis texturados?\n"
                f"4. Ver catálogo de texturas"
            )
            sessao["etapa"] = "papel_couche_acabamento"

        elif any(p in msg_lower for p in ["2", "catálogo", "catalogo", "textura", "ver", "link"]):
            resposta = (
                f"Para te ajudar a escolher, veja nosso catálogo: "
                f"https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                f"Os mais vendidos são o Conqueror Bamboo 400g e o Papel Notturno Black 450g. "
                f"Qualquer papel do catálogo será considerado texturado premium.\n\n"
                f"Qual você prefere?\n\n"
                f"Veja também nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "papel_texturado_escolha"

        elif any(p in msg_lower for p in ["3", "não sei", "nao sei", "indicação", "indicacao"]):
            papel_rec = dados.get("papel_recomendado", "Conqueror Bamboo 400g ou Notturno Black 450g")
            resposta = (
                f"Para sua área, recomendamos: {papel_rec}\n\n"
                f"Veja o catálogo completo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
                f"Projetos: https://www.instagram.com/primyn.store/\n\n"
                f"Após ver o catálogo, me diz qual papel você escolheu."
            )
            sessao["etapa"] = "papel_texturado_escolha"

        else:
            dados["material"] = msg
            resposta = "Você já conhece nossos acabamentos premium?\n\n1. Sim, já conheço\n2. Não, gostaria de conhecer"
            sessao["etapa"] = "acabamento_conhece"

    # ── PAPEL COUCHÊ ACABAMENTO ───────────────
    elif etapa == "papel_couche_acabamento":
        if any(p in msg_lower for p in ["4", "catálogo", "catalogo", "texturado", "textura", "explorar"]):
            resposta = (
                f"Ótima escolha! Veja nosso catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                f"Os mais vendidos são o Conqueror Bamboo 400g e o Notturno Black 450g.\n\n"
                f"Qual você prefere?\n\nProjetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"] = "papel_texturado_escolha"
        elif any(p in msg_lower for p in ["sem", "não quero", "nao quero", "nenhum"]):
            resposta = "Entendemos. Quando quiser explorar uma proposta alinhada ao padrão premium da Primyn, estaremos por aqui. 😊"
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
                resposta = "Qual quantidade você está considerando para esse projeto?"
                sessao["etapa"] = "quantidade"
            else:
                resposta = "Por favor, escolha uma das opções:\n\n1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n4. Ver catálogo de texturas"

    # ── PAPEL TEXTURADO ESCOLHA ───────────────
    elif etapa == "papel_texturado_escolha":
        if len(msg.strip()) < 2:
            resposta = "Pode me dizer qual papel você escolheu?"
        else:
            dados["material"] = msg
            resposta = "Você já conhece nossos acabamentos premium?\n\n1. Sim, já conheço\n2. Não, gostaria de conhecer"
            sessao["etapa"] = "acabamento_conhece"

    # ── ACABAMENTO CONHECE ────────────────────
    elif etapa == "acabamento_conhece":
        if any(p in msg_lower for p in ["1", "sim", "já conheço", "ja conheco", "conheço", "conheco"]):
            resposta = (
                "Qual acabamento faz mais sentido para a sua marca?\n\n"
                "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                "4. Empastamento / borda sanduíche — https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n"
                "5. Impressão colorida no papel especial\n"
                "6. Combinação de acabamentos\n\n"
                "Projetos: https://www.instagram.com/primyn.store/"
            )
        else:
            resposta = (
                "Trabalhamos com os seguintes acabamentos premium:\n\n"
                "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                "4. Empastamento / borda sanduíche — https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n"
                "5. Impressão colorida no papel especial\n"
                "6. Combinação de acabamentos\n\n"
                "Se quiser ver projetos: https://www.instagram.com/primyn.store/\n\n"
                "Qual faz mais sentido para a sua marca?"
            )
        sessao["etapa"] = "acabamento"

    # ── ACABAMENTO ────────────────────────────
    elif etapa == "acabamento":
        primeiro = dados.get("nome", "").split()[0]
        acabamento_map = {
            "1": "Hot stamping", "2": "Alto relevo seco", "3": "Baixo relevo",
            "4": "Empastamento / borda sanduíche", "5": "Impressão colorida no papel especial",
            "6": "Combinação de acabamentos"
        }
        opcao = None
        for k, v in acabamento_map.items():
            if k in msg or any(p in msg_lower for p in v.lower().split(" / ")):
                opcao = k
                break

        if not opcao:
            tentativas += 1
            sessao["tentativas"] = tentativas
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                "4. Empastamento / borda sanduíche — https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n"
                "5. Impressão colorida no papel especial\n"
                "6. Combinação de acabamentos"
            )
        else:
            dados["acabamento"] = acabamento_map[opcao]
            sessao["tentativas"] = 0
            if opcao == "4":
                resposta = (
                    f"O empastamento tem três finalidades:\n\n"
                    f"1. Papel mais grosso — mais espessura e rigidez\n"
                    f"2. Evitar marcação do relevo — impede que o relevo apareça no lado oposto\n"
                    f"3. Borda sanduíche — interior colorido revelado ao olhar a borda\n\n"
                    f"Saiba mais: https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n\n"
                    f"Qual dessas finalidades faz mais sentido para o seu projeto?"
                )
                sessao["etapa"] = "empastamento_detalhe"
            else:
                resposta = var(
                    f"Qual quantidade você está considerando para esse projeto?",
                    f"Para calcular a média mais alinhada, qual quantidade você deseja produzir?"
                )
                sessao["etapa"] = "quantidade"

    # ── EMPASTAMENTO DETALHE ──────────────────
    elif etapa == "empastamento_detalhe":
        dados["empastamento_tipo"] = msg
        resposta = "Qual quantidade você está considerando para esse projeto?"
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
            resposta = f"Por favor, informe uma quantidade válida. A quantidade mínima para esse produto é {minimo} unidades."
        else:
            sessao["tentativas"] = 0
            aviso_minimo = ""
            if qtd < minimo:
                aviso_minimo = f"Nossa quantidade mínima para {produto.get('nome', 'esse produto')} é {minimo} unidades. Vou considerar {minimo} na estimativa.\n\n"
                qtd = minimo
            dados["quantidade"] = qtd

            media = calcular_media(produto_num, dados.get("material", ""), qtd)
            valor_criacao = dados.get("valor_criacao", 0)
            if valor_criacao:
                media += valor_criacao
            dados["media"] = media

            media_fmt = fmt_brl(media)
            resposta = (
                f"{aviso_minimo}"
                f"Para a configuração que você me passou, o investimento médio fica em torno de {media_fmt}. "
                f"Esse valor é uma referência — o orçamento final é personalizado conforme acabamento, criação e complexidade. 👑\n\n"
                f"Faz sentido prosseguirmos com uma proposta personalizada?\n\n"
                f"1. Sim, quero a proposta\n"
                f"2. Preciso pensar\n"
                f"3. Não, obrigada"
            )
            sessao["etapa"] = "media_proposta"

    # ── MÉDIA / PROPOSTA ──────────────────────
    elif etapa == "media_proposta":
        primeiro = dados.get("nome", "").split()[0]
        if any(p in msg_lower for p in ["1", "sim", "quero", "pode", "vamos", "claro"]):
            resposta = var(
                f"Maravilha! Você tem algum prazo ou data importante para receber esse material?",
                f"Ótimo, {primeiro}! Existe algum prazo importante que eu deva considerar na sua proposta?"
            )
            sessao["etapa"] = "urgencia"
        elif any(p in msg_lower for p in ["2", "pensar", "depois", "calma", "talvez"]):
            resposta = var(
                f"Claro! Sem pressa. Quando quiser retomar, estaremos por aqui. 😊\n\nAcompanhe nossos projetos em @primyn.store",
                f"Sem problema, {primeiro}. Esse tipo de decisão merece ser feito com calma. Quando quiser retomar, será um prazer continuar."
            )
            dados["status"] = "aguardando_resposta"
            sessao["etapa"] = "encerrado"
            try:
                from followup import agendar_followup
                agendar_followup(numero, dados.get("nome", ""), "pensar", dias=2)
            except:
                pass
        else:
            resposta = var(
                f"Sem problemas, {primeiro}! Agradeço pelo seu tempo e fico à disposição caso queira retomar em outro momento.",
                f"Claro! Obrigada pelo contato. Quando quiser explorar uma proposta com a Primyn, será um prazer te atender."
            )
            dados["status"] = "perdido"
            sessao["etapa"] = "encerrado"

    # ── URGÊNCIA ──────────────────────────────
    elif etapa == "urgencia":
        dados["urgencia"] = msg
        primeiro = dados.get("nome", "").split()[0]
        urgente = any(p in msg_lower for p in ["urgente", "rápido", "rapido", "pressa", "amanhã", "amanha", "semana", "logo", "dias"])
        aviso = ""
        if urgente:
            aviso = (
                "Projetos com criação e produção premium costumam ter prazo médio de 7 a 10 dias úteis. "
                "Vou deixar isso sinalizado no seu direcionamento.\n\n"
            )
        resposta = (
            f"{aviso}"
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
            f"Antes de encerrar, {primeiro}, como foi sua experiência com este atendimento?\n\n"
            f"1. Ótimo\n"
            f"2. Bom\n"
            f"3. Ruim"
        )
        sessao["etapa"] = "feedback"

    # ── FEEDBACK ──────────────────────────────
    elif etapa == "feedback":
        avaliacoes = {"1": "Ótimo", "2": "Bom", "3": "Ruim"}
        avaliacao = avaliacoes.get(msg.strip(), msg)
        dados["avaliacao"] = avaliacao
        primeiro = dados.get("nome", "").split()[0]
        if msg.strip() == "3" or "ruim" in msg_lower:
            resposta = f"Obrigada pelo retorno, {primeiro}. Vamos usar esse feedback para melhorar. 🤍"
        else:
            resposta = f"Que bom, {primeiro}! Foi um prazer te atender. Até breve! 🤍"
        sessao["etapa"] = "encerrado"

    # ── ENCERRADO ─────────────────────────────
    elif etapa == "encerrado":
        primeiro = dados.get("nome", "").split()[0] if dados.get("nome") else ""
        resposta = (
            f"Olá, {primeiro}! Quer retomar seu projeto ou precisa de algo mais? 😊"
            if primeiro else
            "Olá! Seja muito bem-vindo(a) de volta à Primyn. Como posso te ajudar? 😊"
        )
        sessao["etapa"] = "produto"

    else:
        resposta = (
            "Olá! Seja muito bem-vindo(a) à Primyn.\n\n"
            "Sou a Mily. Como posso te ajudar?"
        )
        sessao["etapa"] = "triagem_inicial"

    sessao["dados"] = dados
    atualizar_sessao(numero, sessao)
    return resposta, handoff_data
