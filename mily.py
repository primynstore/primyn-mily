
import json, os, random
from datetime import datetime

DB_FILE = "sessoes.json"

# ─── PREÇOS DE REFERÊNCIA ───────────────────────────────────────────
PRECOS = {
    "classico": {
        "cartao_visita":      "R$ 378",
        "timbrado":           "R$ 290",
        "pasta":              "R$ 1.250",
        "envelope":           "R$ 620",
        "papelaria_completa": "R$ 4.200",
    },
    "premium": {
        "cartao_visita":      "R$ 562",
        "timbrado":           "R$ 290",
        "pasta":              "R$ 1.250",
        "envelope":           "R$ 620",
        "papelaria_completa": "R$ 5.800",
    },
    "luxo": {
        "cartao_visita":      "R$ 990",
        "timbrado":           "R$ 490",
        "pasta":              "R$ 2.200",
        "envelope":           "R$ 890",
        "papelaria_completa": "R$ 7.500",
    },
}

LINHAS_ESTILO = {
    "1": "classico",
    "2": "premium",
    "3": "luxo",
}

LABEL_LINHA = {
    "classico": "Papel clássico com acabamento diferenciado",
    "premium":  "Papel premium com presença e textura",
    "luxo":     "Linha luxo com acabamentos sofisticados",
}

LABEL_PROJETO = {
    "1": "Cartão de visita",
    "2": "Papelaria completa",
    "3": "Projeto específico",
    "4": "Projeto completo de identidade visual / logomarca",
}

# ─── UTILS ──────────────────────────────────────────────────────────
def ac():
    return random.choice(["Com certeza,", "Perfeito,", "Ótimo,", "Anotado,", "Entendido,"])

def val_nome(msg):
    parts = [x.strip() for x in msg.strip().split() if len(x.strip()) > 1]
    if len(parts) >= 2:
        return True, " ".join(x.title() for x in parts)
    return False, None

def val_email(msg):
    msg = msg.strip().lower()
    parts = msg.split("@")
    if len(parts) == 2 and "." in parts[1] and len(parts[1].split(".")[-1]) >= 2 and len(parts[0]) > 0:
        return True, msg
    return False, None

def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save(s):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

def get_sessao(num):
    s = load()
    if num not in s:
        s[num] = {
            "etapa": "abertura",
            "dados": {"whatsapp": num, "data": datetime.now().isoformat()},
            "ultimo": datetime.now().isoformat(),
            "tentativas": 0,
        }
        save(s)
    return s[num]

def upd_sessao(num, sessao):
    s = load()
    sessao["ultimo"] = datetime.now().isoformat()
    s[num] = sessao
    save(s)

# ─── TEXTOS DE PREÇO ────────────────────────────────────────────────
def texto_preco(linha_key, projeto_num):
    p = PRECOS[linha_key]
    desc_linha = LABEL_LINHA[linha_key]

    if projeto_num == "1":  # Cartão de visita
        preco_ref = p["cartao_visita"]
        detalhe = (
            f"Para essa proposta em *cartões de visita*, os investimentos costumam variar "
            f"conforme os acabamentos e nível de personalização.\n\n"
            f"Nossos projetos normalmente iniciam a partir de *{preco_ref}+*."
        )
    elif projeto_num == "2":  # Papelaria completa
        preco_ref = p["papelaria_completa"]
        detalhe = (
            f"A papelaria completa reúne cartão de visita, papel timbrado, pasta e envelope "
            f"com a mesma identidade visual — sofisticação em cada ponto de contato da sua marca. 👑\n\n"
            f"Projetos nessa linha iniciam a partir de *{preco_ref}+*.\n\n"
            f"  • Timbrado / Receituário: a partir de *{p['timbrado']}*\n"
            f"  • Pasta com bolsa / orelha: a partir de *{p['pasta']}*\n"
            f"  • Envelope Saco / Ofício: a partir de *{p['envelope']}*"
        )
    else:  # Projetos específicos ou identidade visual
        preco_ref = p["cartao_visita"]
        detalhe = (
            f"Para projetos personalizados na linha *{desc_linha}*, "
            f"o investimento é definido conforme o escopo. "
            f"A referência de entrada para papelaria inicia a partir de *{preco_ref}+*."
        )

    return detalhe

# ─── FLUXO PRINCIPAL ────────────────────────────────────────────────
def processar_mensagem(numero, mensagem):
    sessao = get_sessao(numero)
    etapa  = sessao["etapa"]
    dados  = sessao["dados"]
    msg    = mensagem.strip()
    ml     = msg.lower()
    tent   = sessao.get("tentativas", 0)
    resposta    = ""
    handoff_data = None

    # ── ABERTURA ────────────────────────────────────────────────────
    if etapa == "abertura":
        resposta = (
            "Olá, seja muito bem-vindo à *Primyn*, sou a Mily. ✨\n\n"
            "Será um prazer entender o seu projeto. Este é um breve alinhamento inicial "
            "para direcionarmos sua proposta de forma personalizada com um especialista "
            "da nossa equipe.\n\n"
            "Para começarmos — como conheceu a Primyn?\n\n"
            "1. Google\n"
            "2. Instagram\n"
            "3. Indicação"
        )
        sessao["etapa"] = "origem"
        sessao["tentativas"] = 0

    # ── ETAPA 4 — ORIGEM ────────────────────────────────────────────
    elif etapa == "origem":
        if any(p in ml for p in ["1", "google"]):
            dados["origem"] = "Google"
            resposta = "Ótimo! ✨\n\nAgora, para a proposta personalizada:\n\n*Qual o seu nome e sobrenome?*"
            sessao["etapa"] = "dados_nome"
            sessao["tentativas"] = 0
        elif any(p in ml for p in ["2", "instagram", "insta"]):
            dados["origem"] = "Instagram"
            resposta = "Que ótimo que nos encontrou por lá! ✨\n\nPara a proposta personalizada:\n\n*Qual o seu nome e sobrenome?*"
            sessao["etapa"] = "dados_nome"
            sessao["tentativas"] = 0
        elif any(p in ml for p in ["3", "indicação", "indicacao", "indicou"]):
            dados["origem"] = "Indicação"
            resposta = "Que honra! 🤍 Poderia nos dizer quem nos indicou?"
            sessao["etapa"] = "origem_indicacao"
            sessao["tentativas"] = 0
        else:
            tent += 1
            sessao["tentativas"] = tent
            resposta = "Por favor, escolha uma das opções:\n\n1. Google\n2. Instagram\n3. Indicação"

    elif etapa == "origem_indicacao":
        dados["indicado_por"] = msg
        resposta = "Obrigada! Vamos agradecê-lo com carinho. 🤍\n\n*Qual o seu nome e sobrenome?*"
        sessao["etapa"] = "dados_nome"
        sessao["tentativas"] = 0

    # ── ETAPA 5 — DADOS ─────────────────────────────────────────────
    elif etapa == "dados_nome":
        valido, nome_fmt = val_nome(msg)
        if not valido:
            tent += 1
            sessao["tentativas"] = tent
            if tent >= 3:
                nome_fmt = msg.strip().title()
                dados["nome"] = nome_fmt
                primeiro = nome_fmt.split()[0]
                sessao["etapa"] = "dados_area"
                sessao["tentativas"] = 0
                resposta = (
                    f"Prazer, {primeiro}! 😊\n\n"
                    "Qual é a sua *área de atuação*?\n\n"
                    "1. Advocacia / Direito\n"
                    "2. Arquitetura / Engenharia\n"
                    "3. Medicina / Saúde\n"
                    "4. Moda / Beleza / Lifestyle\n"
                    "5. Finanças / Executivo\n"
                    "6. Outro"
                )
            else:
                resposta = "Para personalizar seu atendimento, precisaria do seu *nome e sobrenome*. Como posso te chamar?"
        else:
            dados["nome"] = nome_fmt
            primeiro = nome_fmt.split()[0]
            sessao["tentativas"] = 0
            sessao["etapa"] = "dados_area"
            resposta = (
                f"Prazer, {primeiro}! 😊\n\n"
                "Qual é a sua *área de atuação*?\n\n"
                "1. Advocacia / Direito\n"
                "2. Arquitetura / Engenharia\n"
                "3. Medicina / Saúde\n"
                "4. Moda / Beleza / Lifestyle\n"
                "5. Finanças / Executivo\n"
                "6. Outro"
            )

    elif etapa == "dados_area":
        areas = {
            "1": "Advocacia / Direito",
            "2": "Arquitetura / Engenharia",
            "3": "Medicina / Saúde",
            "4": "Moda / Beleza / Lifestyle",
            "5": "Finanças / Executivo",
            "6": "Outro",
        }
        area_escolhida = None
        for k, v in areas.items():
            pals = v.lower().replace(" / ", " ").split()
            if k in msg or any(p in ml for p in pals if len(p) > 3):
                area_escolhida = v
                break
        if not area_escolhida:
            tent += 1
            sessao["tentativas"] = tent
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Advocacia / Direito\n2. Arquitetura / Engenharia\n"
                "3. Medicina / Saúde\n4. Moda / Beleza / Lifestyle\n"
                "5. Finanças / Executivo\n6. Outro"
            )
        else:
            dados["area"] = area_escolhida
            sessao["tentativas"] = 0
            sessao["etapa"] = "dados_email"
            resposta = "E qual é o seu *e-mail* para o envio da proposta personalizada?"

    elif etapa == "dados_email":
        valido, email_fmt = val_email(msg)
        primeiro = dados.get("nome", "").split()[0]
        if not valido:
            tent += 1
            sessao["tentativas"] = tent
            if tent >= 3:
                dados["email"] = ""
                sessao["tentativas"] = 0
                sessao["etapa"] = "tipo_projeto"
                resposta = (
                    f"Sem problema, {primeiro}! Podemos seguir sem o e-mail por enquanto. 😊\n\n"
                    "O que você deseja desenvolver?\n\n"
                    "1. Cartão de visita\n"
                    "2. Papelaria completa\n"
                    "3. Projeto específico\n"
                    "4. Projeto completo de identidade visual / logomarca"
                )
            else:
                resposta = "Esse endereço não parece estar completo. Pode conferir e enviar novamente?\n\nEx: seunome@gmail.com"
        else:
            dados["email"] = email_fmt
            sessao["tentativas"] = 0
            sessao["etapa"] = "tipo_projeto"
            resposta = (
                f"{ac()} {primeiro}! 😊\n\n"
                "O que você deseja desenvolver?\n\n"
                "1. Cartão de visita\n"
                "2. Papelaria completa\n"
                "3. Projeto específico\n"
                "4. Projeto completo de identidade visual / logomarca"
            )

    # ── ETAPA 1 — TIPO DE PROJETO ────────────────────────────────────
    elif etapa == "tipo_projeto":
        mapa = {
            "1": ["1", "cartão", "cartao", "visita", "tag"],
            "2": ["2", "papelaria completa", "completa", "kit"],
            "3": ["3", "específico", "especifico", "avulso"],
            "4": ["4", "identidade", "logo", "logomarca", "visual", "completo"],
        }
        escolha = None
        for k, pals in mapa.items():
            if any(p in ml for p in pals):
                escolha = k
                break
        if not escolha:
            tent += 1
            sessao["tentativas"] = tent
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Cartão de visita\n"
                "2. Papelaria completa\n"
                "3. Projeto específico\n"
                "4. Projeto completo de identidade visual / logomarca"
            )
        else:
            dados["tipo_projeto"] = LABEL_PROJETO[escolha]
            dados["tipo_projeto_num"] = escolha
            sessao["tentativas"] = 0
            sessao["etapa"] = "estilo"
            resposta = (
                "Qual linha mais representa o *estilo* que você busca para sua marca?\n\n"
                "1️⃣ *Papel clássico com acabamento diferenciado*\n"
                "   Visual elegante e leve, com boa apresentação e simplicidade refinada.\n\n"
                "2️⃣ *Papel premium com presença e textura*\n"
                "   Mais encorpado, com sensação de qualidade e maior impacto visual.\n\n"
                "3️⃣ *Linha luxo com acabamentos sofisticados*\n"
                "   Materiais e acabamentos diferenciados para uma experiência exclusiva e excepcional."
            )

    # ── ETAPA 2 — ESTILO + FILTRO DE VALOR ──────────────────────────
    elif etapa == "estilo":
        escolha = None
        for k in ["1", "2", "3"]:
            if k in msg:
                escolha = k
                break
        if not escolha:
            if any(p in ml for p in ["clássico", "classico", "leve", "simples"]):
                escolha = "1"
            elif any(p in ml for p in ["premium", "textura", "encorpado", "espesso"]):
                escolha = "2"
            elif any(p in ml for p in ["luxo", "sofisticado", "exclusivo", "excepcional"]):
                escolha = "3"
        if not escolha:
            tent += 1
            sessao["tentativas"] = tent
            resposta = (
                "Por favor, escolha a linha que melhor representa o estilo da sua marca:\n\n"
                "1. Papel clássico com acabamento diferenciado\n"
                "2. Papel premium com presença e textura\n"
                "3. Linha luxo com acabamentos sofisticados"
            )
        else:
            linha_key = LINHAS_ESTILO[escolha]
            dados["estilo_linha"] = LABEL_LINHA[linha_key]
            dados["estilo_key"]   = linha_key
            sessao["tentativas"]  = 0
            sessao["etapa"]       = "uso"
            resposta = (
                "Esse projeto será desenvolvido para:\n\n"
                "1. Minha própria marca / empresa\n"
                "2. Um cliente ou projeto terceirizado"
            )

    # ── ETAPA 3 — USO DO PROJETO (FILTRO DE REVENDEDOR) ─────────────
    elif etapa == "uso":
        if any(p in ml for p in ["1", "minha", "própria", "propria", "empresa", "meu negócio", "meu negocio"]):
            dados["uso_projeto"] = "Própria marca/empresa"
            sessao["etapa"] = "apresentacao_preco"
            sessao["tentativas"] = 0
            # Monta apresentação de preço
            linha_key   = dados.get("estilo_key", "classico")
            projeto_num = dados.get("tipo_projeto_num", "1")
            primeiro    = dados.get("nome", "").split()[0]
            detalhe     = texto_preco(linha_key, projeto_num)
            resposta = (
                f"Perfeito! ✨\n\n"
                f"{detalhe}\n\n"
                "Lembrando que esse valor é uma *referência de entrada* — o orçamento final é "
                "personalizado conforme os acabamentos e o nível de personalização da sua marca.\n\n"
                "Deseja prosseguir para uma *proposta personalizada*?\n\n"
                "1. Sim, quero a proposta ✨\n"
                "2. Prefiro pensar um pouco mais"
            )
        elif any(p in ml for p in ["2", "cliente", "terceirizado", "terceiro", "revendedor"]):
            dados["uso_projeto"] = "Cliente / projeto terceirizado"
            # Para revendedores, encaminhar direto ao especialista
            primeiro = dados.get("nome", "").split()[0]
            resposta = (
                f"Entendido, {primeiro}! Para projetos desenvolvidos para clientes, "
                "trabalhamos de forma diferenciada. 😊\n\n"
                "Vou encaminhar você para um especialista da Primyn que irá preparar "
                "uma proposta adequada ao seu modelo de trabalho.\n\n"
                "Em breve nossa equipe entrará em contato. Tenha um excelente dia! 🤍"
            )
            dados["status"] = "handoff_revendedor"
            sessao["etapa"] = "encerrado"
            handoff_data = dados
        else:
            tent += 1
            sessao["tentativas"] = tent
            resposta = (
                "Por favor, escolha uma das opções:\n\n"
                "1. Minha própria marca / empresa\n"
                "2. Um cliente ou projeto terceirizado"
            )

    # ── APRESENTAÇÃO DE PREÇO + DECISÃO ─────────────────────────────
    elif etapa == "apresentacao_preco":
        primeiro = dados.get("nome", "").split()[0]
        if any(p in ml for p in ["1", "sim", "quero", "pode", "vamos", "claro"]):
            sessao["etapa"] = "handoff"
            sessao["tentativas"] = 0
            resposta = (
                f"*Perfeito, {primeiro}!* ✨\n\n"
                "Obrigada pelas informações. Seu atendimento será direcionado para um "
                "*especialista da Primyn*, que irá alinhar todos os detalhes do seu projeto "
                "de forma personalizada — desde materiais e acabamentos até a apresentação "
                "ideal para a sua marca.\n\n"
                "Se necessário, também poderemos agendar uma *reunião estratégica* para "
                "garantir que cada detalhe seja desenvolvido exatamente conforme você deseja.\n\n"
                "Em breve nossa equipe entrará em contato para dar continuidade ao seu "
                "atendimento. Tenha um excelente dia! 🤍\n\n"
                "📸 Enquanto isso, inspire-se em nossos projetos:\n"
                "https://www.instagram.com/primyn.store/"
            )
            dados["status"] = "handoff"
            handoff_data = dados
        else:
            resposta = (
                f"Sem qualquer pressa, {primeiro}. 😊\n\n"
                "Quando quiser retomar, estaremos aqui com o mesmo cuidado e atenção.\n\n"
                "Acompanhe nossos projetos: @primyn.store 🤍"
            )
            dados["status"] = "aguardando_resposta"
            sessao["etapa"] = "encerrado"

    # ── HANDOFF / ENCERRADO ──────────────────────────────────────────
    elif etapa == "handoff":
        primeiro = dados.get("nome", "").split()[0] if dados.get("nome") else ""
        resposta = (
            f"Olá, {primeiro}! Como posso te ajudar? 😊"
            if primeiro else
            "Olá! Como posso te ajudar hoje? 😊"
        )
        sessao["etapa"] = "abertura"

    elif etapa == "encerrado":
        sessao["etapa"] = "abertura"
        sessao["dados"]  = {"whatsapp": numero, "data": datetime.now().isoformat()}
        resposta = (
            "Olá! Seja muito bem-vindo à *Primyn*, sou a Mily. ✨\n\n"
            "Como posso te ajudar hoje?"
        )

    else:
        resposta = "Olá! Como posso te ajudar hoje? 😊"
        sessao["etapa"] = "abertura"

    sessao["dados"] = dados
    upd_sessao(numero, sessao)
    return resposta, handoff_data


# ─── ALIAS / COMPAT ─────────────────────────────────────────────────
carregar_sessoes = load
