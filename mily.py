# ═══════════════════════════════════════════════
# PRIMYN — AGENTE MILY (Lógica) v2
# Correções: fluxo cliente recorrente, validação
# nome+sobrenome, finalização elegante educativa,
# identidade visual trava corrigida.
# ═══════════════════════════════════════════════

import json
import os
from datetime import datetime

DB_FILE = "sessoes.json"

# ═══ TABELA DE PREÇOS ═══
PRECOS = {
    "250":  {"essencial": 378,  "luxo_black": 562,  "luxo_white": 898,  "prestigio": 1297},
    "500":  {"essencial": 475,  "luxo_black": 839,  "luxo_white": 1284, "prestigio": 1682},
    "1000": {"essencial": 588,  "luxo_black": 1184, "luxo_white": 1568, "prestigio": 2567}
}

# ═══ PAPÉIS POR ÁREA ═══
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

# ═══ MENSAGEM DE FINALIZAÇÃO EDUCATIVA ═══
# Usada no handoff e na retomada de lead antigo.
# Ensina o cliente sobre o valor da papelaria premium na percepção da marca.
MSG_EDUCATIVA = (
    "✦ Antes de encerrarmos, um pensamento que vale levar:\n\n"
    "Materiais de papelaria premium não são apenas papel — eles são o primeiro toque "
    "físico que o seu cliente tem com a sua marca. Um cartão com textura, acabamento "
    "em hot stamping ou baixo relevo transmite sofisticação antes mesmo de qualquer "
    "palavra ser dita. Estudos de comportamento do consumidor mostram que materiais "
    "de alta qualidade aumentam em até 3x a percepção de valor de uma marca. "
    "Você não entrega um cartão — você entrega uma experiência.\n\n"
    "Sua marca merece deixar essa impressão. 🤍"
)

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

def validar_nome_completo(msg):
    """
    Valida que o cliente forneceu pelo menos nome e sobrenome.
    Retorna (True, nome_formatado) ou (False, None).
    """
    partes = msg.strip().split()
    partes = [p for p in partes if len(p) > 1]  # remove iniciais soltas tipo "J"
    if len(partes) >= 2:
        return True, " ".join(p.title() for p in partes)
    return False, None

def calcular_media(material, quantidade):
    qtd_str = "250"
    try:
        qtd_num = int(''.join(filter(str.isdigit, str(quantidade))))
        if qtd_num <= 375:
            qtd_str = "250"
        elif qtd_num <= 750:
            qtd_str = "500"
        else:
            qtd_str = "1000"
    except:
        qtd_str = "250"

    material_lower = (material or "").lower()
    if "couche" in material_lower or "couchê" in material_lower:
        tier = "essencial"
    elif "black" in material_lower or "preto" in material_lower or "notturno" in material_lower:
        tier = "luxo_black"
    elif "white" in material_lower or "branco" in material_lower or "rives" in material_lower:
        tier = "luxo_white"
    elif "prestigio" in material_lower or "prestígio" in material_lower or "450" in material_lower:
        tier = "prestigio"
    else:
        tier = "luxo_white"

    return PRECOS.get(qtd_str, {}).get(tier, 898)


def processar_mensagem(numero, mensagem):
    """
    Processa mensagem e retorna (resposta_texto, handoff_data_ou_none).
    """
    sessao  = obter_sessao(numero)
    etapa   = sessao["etapa"]
    dados   = sessao["dados"]
    fluxo   = sessao.get("fluxo")
    msg     = mensagem.strip()
    msg_lower = msg.lower()
    resposta    = ""
    handoff_data = None

    # ═══════════════════════════════════════════
    # ABERTURA
    # ═══════════════════════════════════════════
    if etapa == "abertura":
        resposta = (
            "😊 Olá! Seja muito bem-vindo(a) à Primyn.\n\n"
            "Sou a Mily, consultora virtual da Primyn. Vou entender o que você procura "
            "e direcionar seu atendimento da forma mais estratégica possível. "
            "Ao final, um especialista dará continuidade para garantir que cada detalhe "
            "fique exatamente como você imagina.\n\n"
            "Para começarmos, você é cliente da Primyn ou é sua primeira vez por aqui?"
        )
        # ↑ CORREÇÃO BUG 1: primeira pergunta é triagem de perfil,
        # NÃO "como você nos conheceu". Origem só faz sentido para novos leads.
        sessao["etapa"] = "triagem_inicial"

    # ═══════════════════════════════════════════
    # TRIAGEM INICIAL (antes do nome)
    # ═══════════════════════════════════════════
    elif etapa == "triagem_inicial":
        if any(p in msg_lower for p in ["já sou", "ja sou", "cliente", "já comprei", "ja comprei", "compro", "sou cliente"]):
            dados["tipo_contato"] = "cliente_recorrente"
            dados["origem_relacional"] = "recompra"
            sessao["fluxo"] = "cliente_recorrente"
            resposta = (
                "Que bom te ver de volta! ✨\n\n"
                "Para localizar seu cadastro e agilizar seu novo pedido, "
                "pode me informar seu nome e sobrenome completo?"
            )
            sessao["etapa"] = "nome"

        elif any(p in msg_lower for p in ["já falei", "ja falei", "voltei", "retomando", "retomar", "antes", "já conversei", "ja conversei", "já fui", "ja fui"]):
            dados["tipo_contato"] = "lead_antigo"
            dados["origem_relacional"] = "retorno"
            sessao["fluxo"] = "lead_antigo"
            resposta = (
                "Que bom que voltou! ✨ Fico feliz em retomar seu atendimento.\n\n"
                "Para localizar seu histórico, pode me dizer seu nome e sobrenome completo?"
            )
            sessao["etapa"] = "nome"

        else:
            # Novo lead — primeiro nome, depois origem
            dados["tipo_contato"] = "novo_lead"
            dados["origem_relacional"] = "primeira_vez"
            sessao["fluxo"] = "novo_lead"
            resposta = (
                "Seja muito bem-vindo(a)! ✨ "
                "Para personalizarmos seu atendimento, pode me dizer seu nome e sobrenome completo?"
            )
            sessao["etapa"] = "nome"

    # ═══════════════════════════════════════════
    # NOME (com validação nome + sobrenome)
    # ═══════════════════════════════════════════
    elif etapa == "nome":
        valido, nome_formatado = validar_nome_completo(msg)

        if not valido:
            # ↑ CORREÇÃO BUG 2: rejeita nome único, pede nome + sobrenome
            resposta = (
                "Para encontrar seu cadastro com precisão, preciso do seu nome e sobrenome completo. "
                "Como posso te chamar?"
            )
        else:
            dados["nome"] = nome_formatado
            primeiro_nome = nome_formatado.split()[0]
            fluxo_atual = sessao.get("fluxo")

            if fluxo_atual == "cliente_recorrente":
                # Lead quente: pula direto para o produto
                resposta = (
                    f"Perfeito, {primeiro_nome} ✦ Já te localizo aqui no sistema.\n\n"
                    f"Me conta: qual material você gostaria de produzir desta vez?"
                )
                sessao["etapa"] = "produto"

            elif fluxo_atual == "lead_antigo":
                resposta = (
                    f"Ótimo, {primeiro_nome} ✨ Encontrei seu histórico.\n\n"
                    f"Você prefere retomar o projeto que conversamos antes "
                    f"ou está pensando em algo novo desta vez?"
                )
                sessao["etapa"] = "retomar_ou_novo"

            else:
                # Novo lead: agora sim perguntar origem
                resposta = (
                    f"Prazer, {primeiro_nome}! ✨ "
                    f"Como você conheceu a Primyn?"
                )
                sessao["etapa"] = "origem"

    # ═══════════════════════════════════════════
    # ORIGEM (só para novos leads)
    # ═══════════════════════════════════════════
    elif etapa == "origem":
        dados["origem"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]
        resposta = (
            f"Que ótimo que nos encontrou por lá! ✦\n\n"
            f"Para que eu possa encaminhar sua proposta de investimento, "
            f"qual é o seu melhor e-mail, {primeiro_nome}?"
        )
        sessao["etapa"] = "email"

    # ═══════════════════════════════════════════
    # RETOMAR OU NOVO (lead antigo)
    # ═══════════════════════════════════════════
    elif etapa == "retomar_ou_novo":
        primeiro_nome = dados.get("nome", "").split()[0]

        if any(p in msg_lower for p in ["novo", "nova", "diferente", "outro", "outra", "começar"]):
            sessao["fluxo"] = "novo_lead"
            resposta = (
                f"Perfeito, {primeiro_nome} ✨ Vamos começar algo novo e especial!\n\n"
                f"Para encaminhar sua proposta, qual é o seu melhor e-mail?"
            )
            sessao["etapa"] = "email"

        else:
            # Retomada: finalização elegante + educativa
            # ↑ CORREÇÃO BUG 3: resposta elaborada e educativa antes do handoff
            resposta = (
                f"Perfeito, {primeiro_nome} ✦ Vou retomar exatamente de onde paramos "
                f"e garantir que sua proposta reflita tudo o que conversamos.\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Em breve um especialista dará continuidade ao seu atendimento com todo o contexto do projeto. 😊"
            )
            dados["status"] = "handoff"
            sessao["etapa"] = "handoff"
            handoff_data = dados

    # ═══════════════════════════════════════════
    # E-MAIL
    # ═══════════════════════════════════════════
    elif etapa == "email":
        dados["email"] = msg.strip()
        primeiro_nome = dados.get("nome", "").split()[0]
        resposta = (
            f"Perfeito, {primeiro_nome} ✨ Agora me conta: qual projeto você gostaria de produzir? "
            f"Um cartão de visita premium, papel timbrado, papelaria completa, "
            f"um convite especial ou outro material?"
        )
        sessao["etapa"] = "produto"

    # ═══════════════════════════════════════════
    # PRODUTO
    # ═══════════════════════════════════════════
    elif etapa == "produto":
        dados["produto"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]
        fluxo_atual = sessao.get("fluxo")

        # Cliente recorrente pula área de atuação e vai direto para arte
        if fluxo_atual == "cliente_recorrente":
            resposta = (
                f"Ótima escolha, {primeiro_nome} ✦ "
                f"Você já tem a arte pronta ou precisa que a gente desenvolva algo novo?"
            )
            sessao["etapa"] = "arte"
        else:
            resposta = (
                f"Ótima escolha, {primeiro_nome} ✨ "
                f"Para indicar o material mais alinhado à sua marca, me conta: em qual área você atua?"
            )
            sessao["etapa"] = "area"

    # ═══════════════════════════════════════════
    # ÁREA DE ATUAÇÃO
    # ═══════════════════════════════════════════
    elif etapa == "area":
        dados["area"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]

        papel_recomendado = None
        for chave, valor in PAPEIS_POR_AREA.items():
            if chave in msg_lower:
                papel_recomendado = valor
                break
        if papel_recomendado:
            dados["papel_recomendado"] = papel_recomendado

        resposta = (
            f"{msg.title()} — uma área que exige sofisticação em cada detalhe. "
            f"Sua marca merece um material à altura do seu trabalho. ✦\n\n"
            f"Você já possui a arte finalizada, tem alguma referência em mente "
            f"ou vai precisar de criação?"
        )
        sessao["etapa"] = "arte"

    # ═══════════════════════════════════════════
    # ARTE
    # ═══════════════════════════════════════════
    elif etapa == "arte":
        primeiro_nome = dados.get("nome", "").split()[0]

        if any(p in msg_lower for p in ["pronta", "tenho", "já tenho", "ja tenho", "finalizada", "referência", "referencia", "envio"]):
            dados["arte"] = "pronta_ou_referencia"
            resposta = (
                f"Perfeito, {primeiro_nome} ✨ Pode me enviar sua arte final ou a referência que deseja usar? "
                f"Assim consigo direcionar sua cotação com mais precisão."
            )
            sessao["etapa"] = "arte_detalhe"

        elif any(p in msg_lower for p in ["criação", "criacao", "criar", "não tenho", "nao tenho", "preciso", "desenvolver"]):
            dados["arte"] = "precisa_criacao"
            resposta = (
                f"Sem problema, {primeiro_nome} ✨ Podemos desenvolver isso para você. Trabalhamos com:\n\n"
                f"• Criação de arte — R$ 74,90\n"
                f"• Criação de cartão 3D — R$ 120,00\n"
                f"• Identidade visual / logomarca\n\n"
                f"Qual dessas opções faz mais sentido para o seu projeto?"
            )
            sessao["etapa"] = "arte_opcao"

        elif any(p in msg_lower for p in ["identidade", "logo", "logomarca", "marca"]):
            dados["arte"] = "identidade_visual"
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
            resposta = (
                f"Perfeito, {primeiro_nome} ✨ Identidade visual é um projeto especial — "
                f"vou encaminhar diretamente para a nossa designer Ane, "
                f"que vai te atender com toda a atenção que esse projeto merece. ✦\n\n"
                f"Antes, me passa seu melhor e-mail para ela entrar em contato?"
                if not dados.get("email") else
                f"Perfeito, {primeiro_nome} ✨ Identidade visual é um projeto especial — "
                f"vou encaminhar diretamente para a nossa designer Ane, "
                f"que vai te atender com toda a atenção que esse projeto merece.\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Em breve ela entrará em contato no seu e-mail cadastrado. 😊"
            )
            if dados.get("email"):
                dados["status"] = "handoff_designer"
                sessao["etapa"] = "handoff"
                handoff_data = dados
            else:
                sessao["etapa"] = "email_design"

        else:
            resposta = (
                f"{primeiro_nome}, me ajuda a entender melhor: você já tem a arte pronta, "
                f"tem alguma referência visual ou prefere que a gente desenvolva para você?"
            )

    # ═══════════════════════════════════════════
    # EMAIL DESIGN (identidade sem e-mail ainda)
    # ═══════════════════════════════════════════
    elif etapa == "email_design":
        dados["email"] = msg.strip()
        primeiro_nome = dados.get("nome", "").split()[0]
        dados["status"] = "handoff_designer"
        resposta = (
            f"Perfeito, {primeiro_nome} ✨ Ane entrará em contato pelo e-mail informado em breve.\n\n"
            f"{MSG_EDUCATIVA}\n\n"
            f"Foi um prazer te atender! 😊"
        )
        sessao["etapa"] = "handoff"
        handoff_data = dados

    # ═══════════════════════════════════════════
    # ARTE OPÇÃO (escolha após listar as opções)
    # ═══════════════════════════════════════════
    elif etapa == "arte_opcao":
        primeiro_nome = dados.get("nome", "").split()[0]

        if "identidade" in msg_lower or "logo" in msg_lower or "logomarca" in msg_lower:
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
            resposta = (
                f"Perfeito, {primeiro_nome} ✨ Vou encaminhar para a nossa designer Ane — "
                f"ela cuida pessoalmente de identidades visuais.\n\n"
                f"{MSG_EDUCATIVA}\n\n"
                f"Em breve ela entrará em contato. 😊"
            )
            dados["status"] = "handoff_designer"
            sessao["etapa"] = "handoff"
            handoff_data = dados
        elif "120" in msg or "3d" in msg_lower:
            dados["criacao"] = "cartao_3d"
            dados["valor_criacao"] = 120.00
            sessao["etapa"] = "arte_detalhe"
            resposta = f"Ótima escolha! ✦ Agora me conta: qual formato você gostaria? 5x9 cm, 5x8 cm ou personalizado?"
        else:
            dados["criacao"] = "criacao_arte"
            dados["valor_criacao"] = 74.90
            sessao["etapa"] = "arte_detalhe"
            resposta = f"Perfeito ✦ Qual formato você gostaria? 5x9 cm (tradicional), 5x8 cm (americano) ou personalizado?"

    # ═══════════════════════════════════════════
    # ARTE DETALHE (arte enviada ou confirmação)
    # ═══════════════════════════════════════════
    elif etapa == "arte_detalhe":
        # ↑ CORREÇÃO BUG 4: etapa sempre avança após qualquer resposta
        dados["arte_detalhe"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]
        resposta = (
            f"Perfeito, {primeiro_nome} ✦ Qual formato você gostaria para o seu projeto? "
            f"Se for cartão de visita: 5x9 cm (tradicional), 5x8 cm (americano) ou formato personalizado?"
        )
        sessao["etapa"] = "formato"

    # ═══════════════════════════════════════════
    # FORMATO
    # ═══════════════════════════════════════════
    elif etapa == "formato":
        dados["formato"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]
        resposta = (
            f"Perfeito ✨ Qual tipo de papel faz mais sentido para o seu projeto: "
            f"Couchê 300g, texturado até 400g ou texturado acima de 400g?"
        )
        sessao["etapa"] = "papel"

    # ═══════════════════════════════════════════
    # PAPEL / MATERIAL
    # ═══════════════════════════════════════════
    elif etapa == "papel":
        dados["material"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]

        if "couche" in msg_lower or "couchê" in msg_lower or "300" in msg:
            resposta = (
                f"O Couchê 300g é nossa opção de entrada — e, para refletir o padrão Primyn, "
                f"trabalhamos obrigatoriamente com hot stamping ou baixo relevo. "
                f"Sem um acabamento premium, ele se torna um cartão comum, "
                f"e isso não representa a sua marca da forma certa. ✦\n\n"
                f"Qual acabamento faz mais sentido para você, ou prefere explorar nossos papéis texturados?"
            )
            sessao["etapa"] = "papel_couche_validar"
        else:
            resposta = (
                f"Perfeito, {primeiro_nome} ✨ E em relação ao acabamento, o que faz mais sentido para a sua marca?\n\n"
                f"• Hot stamping\n"
                f"• Alto relevo seco\n"
                f"• Baixo relevo\n"
                f"• Empastamento / borda sanduíche\n"
                f"• Apenas impressão colorida no papel especial\n"
                f"• Combinação de acabamentos"
            )
            sessao["etapa"] = "acabamento"

    # ═══════════════════════════════════════════
    # VALIDAÇÃO COUCHÊ
    # ═══════════════════════════════════════════
    elif etapa == "papel_couche_validar":
        primeiro_nome = dados.get("nome", "").split()[0]

        if any(p in msg_lower for p in ["texturado", "textura", "explorar", "outro"]):
            dados["material"] = "texturado"
            resposta = f"Perfeito, {primeiro_nome} ✨ Você prefere texturado até 400g ou acima de 400g?"
            sessao["etapa"] = "papel"
        elif any(p in msg_lower for p in ["sem", "não quero", "nao quero", "sem acabamento"]):
            resposta = (
                f"Entendemos perfeitamente, {primeiro_nome}. "
                f"Quando quiser explorar uma proposta alinhada ao padrão premium da Primyn, estaremos por aqui ✦"
            )
            dados["status"] = "fora_escopo"
            sessao["etapa"] = "encerrado"
        else:
            dados["acabamento"] = msg
            resposta = f"Perfeito, {primeiro_nome} ✨ Qual quantidade você está considerando para esse projeto?"
            sessao["etapa"] = "quantidade"

    # ═══════════════════════════════════════════
    # ACABAMENTO
    # ═══════════════════════════════════════════
    elif etapa == "acabamento":
        dados["acabamento"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]
        resposta = f"Perfeito, {primeiro_nome} ✨ Qual quantidade você está considerando para esse projeto?"
        sessao["etapa"] = "quantidade"

    # ═══════════════════════════════════════════
    # QUANTIDADE
    # ═══════════════════════════════════════════
    elif etapa == "quantidade":
        dados["quantidade"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]

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
            f"Perfeito, {primeiro_nome} ✨ Para a configuração que você me passou, "
            f"o investimento médio fica em torno de {media_fmt}. "
            f"Esse valor é uma referência e o orçamento final é personalizado conforme "
            f"material, acabamento, criação e complexidade do projeto. ✦\n\n"
            f"A ideia é que sua papelaria não apenas informe, mas valorize a percepção "
            f"da sua marca desde o primeiro contato.\n\n"
            f"Faz sentido para você prosseguirmos com uma proposta personalizada?"
        )
        sessao["etapa"] = "media_proposta"

    # ═══════════════════════════════════════════
    # MÉDIA / PROPOSTA
    # ═══════════════════════════════════════════
    elif etapa == "media_proposta":
        primeiro_nome = dados.get("nome", "").split()[0]

        if any(p in msg_lower for p in ["sim", "faz", "sentido", "quero", "vamos", "pode", "ok", "claro", "s", "isso"]):
            resposta = f"Perfeito ✨ Você tem algum prazo ou data importante para receber esse material?"
            sessao["etapa"] = "urgencia"

        elif any(p in msg_lower for p in ["pensar", "depois", "calma", "ainda não", "ainda nao", "talvez"]):
            resposta = (
                f"Claro, {primeiro_nome} ✨ Sem pressa. Quando quiser retomar, estaremos por aqui. "
                f"Acompanhe nossos projetos em @primyn.store ✦"
            )
            dados["status"] = "aguardando_resposta"
            sessao["etapa"] = "encerrado"
            try:
                from followup import agendar_followup
                agendar_followup(numero, dados.get("nome", ""), "pensar", dias=2)
            except:
                pass

        elif any(p in msg_lower for p in ["não", "nao", "desisto", "cancelar", "caro"]):
            resposta = (
                f"Sem problema, {primeiro_nome} ✨ Agradeço pelo seu tempo e fico à disposição "
                f"caso queira retomar em outro momento."
            )
            dados["status"] = "perdido"
            sessao["etapa"] = "encerrado"

        else:
            resposta = (
                f"{primeiro_nome}, faz sentido prosseguirmos com uma proposta personalizada "
                f"ou prefere pensar com calma?"
            )

    # ═══════════════════════════════════════════
    # URGÊNCIA
    # ═══════════════════════════════════════════
    elif etapa == "urgencia":
        dados["urgencia"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]

        aviso_urgencia = ""
        if any(p in msg_lower for p in ["urgente", "rápido", "rapido", "pressa", "amanhã", "amanha", "essa semana"]):
            aviso_urgencia = (
                "✦ Projetos com criação e produção premium têm prazo médio de "
                "5 a 8 dias úteis. Vou sinalizar isso no seu encaminhamento.\n\n"
            )

        resposta = (
            f"{aviso_urgencia}"
            f"{MSG_EDUCATIVA}\n\n"
            f"😊 Vou encaminhar seu projeto ao nosso sistema para uma proposta personalizada. "
            f"Em breve, um especialista dará continuidade ao seu atendimento, {primeiro_nome}. ✦"
        )
        dados["status"] = "handoff"
        sessao["etapa"] = "handoff"
        handoff_data = dados

    # ═══════════════════════════════════════════
    # HANDOFF (após enviar dados, coleta feedback)
    # ═══════════════════════════════════════════
    elif etapa == "handoff":
        primeiro_nome = dados.get("nome", "").split()[0]
        resposta = (
            f"Antes de encerrar, {primeiro_nome} ✨ "
            f"como foi sua experiência com este atendimento inicial? "
            f"Sua opinião nos ajuda a melhorar cada vez mais."
        )
        sessao["etapa"] = "feedback"

    # ═══════════════════════════════════════════
    # FEEDBACK
    # ═══════════════════════════════════════════
    elif etapa == "feedback":
        dados["avaliacao"] = msg
        primeiro_nome = dados.get("nome", "").split()[0]
        resposta = (
            f"Muito obrigada pelo feedback, {primeiro_nome}! ✨ "
            f"Foi um prazer te atender. Até breve! ✦"
        )
        sessao["etapa"] = "encerrado"

    # ═══════════════════════════════════════════
    # ENCERRADO (mensagem depois de encerrar)
    # ═══════════════════════════════════════════
    elif etapa == "encerrado":
        primeiro_nome = dados.get("nome", "").split()[0] if dados.get("nome") else ""
        if primeiro_nome:
            resposta = (
                f"Olá novamente, {primeiro_nome}! ✨ "
                f"Quer retomar seu projeto ou precisa de algo mais? Estou por aqui! ✦"
            )
        else:
            resposta = "Olá! ✨ Seja muito bem-vindo(a) de volta à Primyn. Como posso te ajudar?"
        sessao["etapa"] = "produto"

    # ═══════════════════════════════════════════
    # DEFAULT
    # ═══════════════════════════════════════════
    else:
        resposta = (
            "😊 Olá! Seja muito bem-vindo(a) à Primyn.\n\n"
            "Sou a Mily, consultora virtual da Primyn. Como posso te ajudar?"
        )
        sessao["etapa"] = "triagem_inicial"

    sessao["dados"] = dados
    atualizar_sessao(numero, sessao)
    return resposta, handoff_data
