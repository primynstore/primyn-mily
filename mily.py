# ═══════════════════════════════════════════════
# PRIMYN STUDIO — AGENTE MILY (Lógica)
# ═══════════════════════════════════════════════

import json
import os
from datetime import datetime

# Banco de dados simples (arquivo JSON)
DB_FILE = "sessoes.json"

# ═══ TABELA DE PREÇOS ═══
PRECOS = {
    "250": {"essencial": 378, "luxo_black": 562, "luxo_white": 898, "prestigio": 1297},
    "500": {"essencial": 475, "luxo_black": 839, "luxo_white": 1284, "prestigio": 1682},
    "1000": {"essencial": 588, "luxo_black": 1184, "luxo_white": 1568, "prestigio": 2567}
}

# ═══ MAPEAMENTO DE PAPÉIS POR ÁREA ═══
PAPEIS_POR_AREA = {
    "advocacia": "Notturno Black 450g / Dark Blue / Rives White",
    "direito": "Notturno Black 450g / Dark Blue / Rives White",
    "financas": "Notturno Black 450g / Dark Blue / Rives White",
    "executivo": "Notturno Black 450g / Dark Blue / Rives White",
    "arquitetura": "Rives Natural White 400g / Conqueror Bamboo 400g",
    "engenharia": "Rives Natural White 400g / Conqueror Bamboo 400g",
    "design": "Rives Natural White 400g / Conqueror Bamboo 400g",
    "moda": "Color Plus / Rives White",
    "beleza": "Color Plus / Rives White",
    "lifestyle": "Color Plus / Rives White",
    "medicina": "Rives Trad. White / Conqueror Bamboo 400g",
    "saude": "Rives Trad. White / Conqueror Bamboo 400g"
}


def carregar_sessoes():
    """Carrega sessões do arquivo JSON"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_sessoes(sessoes):
    """Salva sessões no arquivo JSON"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(sessoes, f, ensure_ascii=False, indent=2)

def obter_sessao(numero):
    """Obtém ou cria sessão para um número"""
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
    """Atualiza sessão"""
    sessoes = carregar_sessoes()
    sessao["ultimo_contato"] = datetime.now().isoformat()
    sessoes[numero] = sessao
    salvar_sessoes(sessoes)


def calcular_media(material, quantidade):
    """Calcula média de preço com base no material e quantidade"""
    qtd_str = str(quantidade)
    
    # Encontrar quantidade mais próxima
    if int(quantidade) <= 375:
        qtd_str = "250"
    elif int(quantidade) <= 750:
        qtd_str = "500"
    else:
        qtd_str = "1000"
    
    # Mapear material para tier
    material_lower = material.lower() if material else ""
    
    if "couche" in material_lower or "couchê" in material_lower:
        tier = "essencial"
    elif "black" in material_lower or "preto" in material_lower or "notturno" in material_lower:
        tier = "luxo_black"
    elif "white" in material_lower or "branco" in material_lower or "rives" in material_lower:
        tier = "luxo_white"
    elif "prestigio" in material_lower or "prestígio" in material_lower or "450" in material_lower:
        tier = "prestigio"
    else:
        tier = "luxo_white"  # padrão
    
    return PRECOS.get(qtd_str, {}).get(tier, 898)


def processar_mensagem(numero, mensagem):
    """
    Processa mensagem recebida e retorna resposta da Mily.
    Retorna: (resposta_texto, dados_handoff_ou_none)
    """
    sessao = obter_sessao(numero)
    etapa = sessao["etapa"]
    dados = sessao["dados"]
    fluxo = sessao.get("fluxo")
    msg = mensagem.strip()
    msg_lower = msg.lower()
    
    resposta = ""
    handoff_data = None
    
    # ═══════════════════════════════════════
    # ABERTURA
    # ═══════════════════════════════════════
    if etapa == "abertura":
        resposta = (
            "Olá! ✨ Seja muito bem-vindo(a) à Primyn.\n\n"
            "Sou a Mily, consultora virtual da Primyn. Vou entender melhor o que você procura "
            "para direcionar seu atendimento da forma mais estratégica possível — e, ao final, "
            "um especialista dará continuidade ao seu projeto para garantir que cada detalhe "
            "fique exatamente como você deseja.\n\n"
            "Para começarmos, como você conheceu a Primyn?"
        )
        sessao["etapa"] = "origem"
    
    # ═══════════════════════════════════════
    # ORIGEM
    # ═══════════════════════════════════════
    elif etapa == "origem":
        dados["origem"] = msg
        resposta = "Que ótimo que nos encontrou por lá! ✦ Para personalizar o seu atendimento, como posso te chamar?"
        sessao["etapa"] = "nome"
    
    # ═══════════════════════════════════════
    # NOME
    # ═══════════════════════════════════════
    elif etapa == "nome":
        dados["nome"] = msg.title()
        nome = dados["nome"].split()[0]
        resposta = (
            f"Perfeito, {nome} ✨ Antes de seguirmos, me conta: "
            "é sua primeira vez com a Primyn, você já é cliente ou já falou com a nossa equipe antes?"
        )
        sessao["etapa"] = "triagem"
    
    # ═══════════════════════════════════════
    # TRIAGEM
    # ═══════════════════════════════════════
    elif etapa == "triagem":
        nome = dados.get("nome", "").split()[0]
        
        if any(palavra in msg_lower for palavra in ["primeira", "primeiro", "nunca", "nova", "novo", "não conheço"]):
            dados["tipo_contato"] = "novo_lead"
            dados["origem_relacional"] = "primeira_vez"
            sessao["fluxo"] = "novo_lead"
            resposta = (
                f"Que ótimo ter você por aqui pela primeira vez! ✨ "
                f"Vou te guiar por um atendimento completo para entender o seu projeto com toda a atenção que ele merece. ✦\n\n"
                f"Para que eu possa encaminhar sua proposta de investimento, qual é o seu melhor e-mail?"
            )
            sessao["etapa"] = "email"
        
        elif any(palavra in msg_lower for palavra in ["cliente", "já comprei", "ja comprei", "já sou", "ja sou", "compro"]):
            dados["tipo_contato"] = "cliente_recorrente"
            dados["origem_relacional"] = "recompra"
            sessao["fluxo"] = "cliente_recorrente"
            resposta = (
                f"Que bom te ver de volta! ✨ Como você já conhece a Primyn, vou direto ao ponto "
                f"para agilizar seu novo pedido. ✦\n\n"
                f"Me conta, {nome}: qual material você busca produzir desta vez?"
            )
            sessao["etapa"] = "produto"
        
        elif any(palavra in msg_lower for palavra in ["já falei", "ja falei", "voltei", "retomando", "retomar", "antes", "já conversei", "ja conversei"]):
            dados["tipo_contato"] = "lead_antigo"
            dados["origem_relacional"] = "retorno"
            sessao["fluxo"] = "lead_antigo"
            resposta = (
                f"Que bom que voltou a nos procurar! ✨ Fico feliz em retomar seu atendimento. ✦\n\n"
                f"{nome}, você gostaria de retomar o mesmo projeto que conversamos antes ou está buscando algo novo desta vez?"
            )
            sessao["etapa"] = "retomar_ou_novo"
        
        else:
            # Não entendeu — assumir novo lead
            dados["tipo_contato"] = "novo_lead"
            dados["origem_relacional"] = "primeira_vez"
            sessao["fluxo"] = "novo_lead"
            resposta = (
                f"Perfeito, {nome} ✨ Vou te guiar por um atendimento completo!\n\n"
                f"Para que eu possa encaminhar sua proposta de investimento, qual é o seu melhor e-mail?"
            )
            sessao["etapa"] = "email"
    
    # ═══════════════════════════════════════
    # RETOMAR OU NOVO (lead antigo)
    # ═══════════════════════════════════════
    elif etapa == "retomar_ou_novo":
        nome = dados.get("nome", "").split()[0]
        if any(palavra in msg_lower for palavra in ["novo", "nova", "diferente", "outro"]):
            resposta = (
                f"Perfeito, {nome} ✨ Vamos começar do zero então!\n\n"
                f"Para que eu possa encaminhar sua proposta de investimento, qual é o seu melhor e-mail?"
            )
            sessao["etapa"] = "email"
            sessao["fluxo"] = "novo_lead"
        else:
            resposta = (
                f"Ótimo, {nome} ✦ Vou retomar de onde paramos.\n\n"
                f"Me confirma seu melhor e-mail para eu te enviar a proposta atualizada?"
            )
            sessao["etapa"] = "email"
    
    # ═══════════════════════════════════════
    # E-MAIL
    # ═══════════════════════════════════════
    elif etapa == "email":
        dados["email"] = msg.strip()
        nome = dados.get("nome", "").split()[0]
        
        if sessao.get("fluxo") == "cliente_recorrente":
            resposta = f"Perfeito, {nome} ✨ Me conta: qual material você busca produzir desta vez?"
            sessao["etapa"] = "produto"
        else:
            resposta = (
                f"Perfeito, {nome} ✨ Agora me conta: qual projeto você gostaria de produzir? "
                f"Um cartão de visita premium, uma papelaria completa, uma identidade visual "
                f"que posicione sua marca de vez ou algum outro material especial?"
            )
            sessao["etapa"] = "produto"
    
    # ═══════════════════════════════════════
    # PRODUTO
    # ═══════════════════════════════════════
    elif etapa == "produto":
        dados["produto"] = msg
        nome = dados.get("nome", "").split()[0]
        
        if sessao.get("fluxo") == "cliente_recorrente":
            resposta = (
                f"Ótima escolha, {nome} ✦ Você já tem a arte pronta ou precisa que a gente desenvolva algo novo?"
            )
            sessao["etapa"] = "arte"
        else:
            resposta = (
                f"Ótima escolha, {nome} ✨ Para eu indicar o material mais alinhado à sua marca, "
                f"me conta: em qual área você atua?"
            )
            sessao["etapa"] = "area"
    
    # ═══════════════════════════════════════
    # ÁREA DE ATUAÇÃO
    # ═══════════════════════════════════════
    elif etapa == "area":
        dados["area"] = msg
        nome = dados.get("nome", "").split()[0]
        area = msg.strip()
        
        # Buscar papéis recomendados
        papel_recomendado = None
        for chave, valor in PAPEIS_POR_AREA.items():
            if chave in msg_lower:
                papel_recomendado = valor
                break
        
        if papel_recomendado:
            dados["papel_recomendado"] = papel_recomendado
        
        resposta = (
            f"{area.title()} — uma área que exige sofisticação em cada detalhe. "
            f"Sua marca merece um material à altura do seu trabalho. ✦\n\n"
            f"Agora me conta: você já possui a arte finalizada, tem alguma referência em mente ou vai precisar de criação?"
        )
        sessao["etapa"] = "arte"
    
    # ═══════════════════════════════════════
    # ARTE
    # ═══════════════════════════════════════
    elif etapa == "arte":
        nome = dados.get("nome", "").split()[0]
        
        if any(palavra in msg_lower for palavra in ["pronta", "tenho", "ja tenho", "já tenho", "finalizada", "referência", "referencia"]):
            dados["arte"] = "pronta_ou_referencia"
            resposta = (
                f"Perfeito, {nome} ✨ Pode me enviar sua arte final ou a referência que deseja usar? "
                f"Assim consigo direcionar sua cotação com mais precisão."
            )
            sessao["etapa"] = "arte_detalhe"
        
        elif any(palavra in msg_lower for palavra in ["criação", "criacao", "criar", "não tenho", "nao tenho", "preciso", "desenvolver"]):
            dados["arte"] = "precisa_criacao"
            resposta = (
                f"Sem problema, {nome} ✨ Podemos desenvolver isso para você. Trabalhamos com:\n\n"
                f"• Criação de arte — R$ 74,90\n"
                f"• Criação de cartão 3D — R$ 120,00\n"
                f"• Identidade visual / logomarca\n\n"
                f"Qual dessas opções faz mais sentido para o seu projeto?"
            )
            sessao["etapa"] = "arte_detalhe"
        
        else:
            resposta = (
                f"{nome}, me ajuda a entender melhor: você já tem a arte pronta, "
                f"tem alguma referência visual ou prefere que a gente desenvolva essa parte para você?"
            )
    
    # ═══════════════════════════════════════
    # ARTE DETALHE
    # ═══════════════════════════════════════
    elif etapa == "arte_detalhe":
        nome = dados.get("nome", "").split()[0]
        
        # Processar escolha de criação
        if "74" in msg or "arte" in msg_lower:
            dados["criacao"] = "criacao_arte"
            dados["valor_criacao"] = 74.90
        elif "120" in msg or "3d" in msg_lower or "3D" in msg:
            dados["criacao"] = "cartao_3d"
            dados["valor_criacao"] = 120.00
        elif "identidade" in msg_lower or "logo" in msg_lower or "logomarca" in msg_lower:
            dados["criacao"] = "identidade_visual"
            dados["valor_criacao"] = 0
        else:
            dados["arte_detalhe"] = msg
        
        resposta = (
            f"Perfeito, {nome} ✦ Agora me conta um detalhe importante do projeto: "
            f"qual formato você gostaria? Se for cartão de visita: 5x9 cm (tradicional), "
            f"5x8 cm (americano) ou formato personalizado?"
        )
        sessao["etapa"] = "formato"
    
    # ═══════════════════════════════════════
    # FORMATO / TAMANHO
    # ═══════════════════════════════════════
    elif etapa == "formato":
        dados["formato"] = msg
        nome = dados.get("nome", "").split()[0]
        resposta = (
            f"Perfeito ✨ Qual tipo de papel faz mais sentido para o seu projeto: "
            f"Couchê 300g, texturado até 400g ou texturado acima de 400g?"
        )
        sessao["etapa"] = "papel"
    
    # ═══════════════════════════════════════
    # PAPEL / MATERIAL
    # ═══════════════════════════════════════
    elif etapa == "papel":
        dados["material"] = msg
        nome = dados.get("nome", "").split()[0]
        
        if "couche" in msg_lower or "couchê" in msg_lower or "300" in msg:
            resposta = (
                f"O Couchê 300g é a nossa opção de entrada — e, para refletir o padrão Primyn, "
                f"trabalhamos obrigatoriamente com hot stamping ou relevo. Sem um acabamento premium, "
                f"ele se torna um cartão comum, e isso não representa a sua marca da forma certa. ✦\n\n"
                f"Qual acabamento faz mais sentido para você, ou prefere explorar nossos papéis texturados?"
            )
            sessao["etapa"] = "papel_couche_validar"
        else:
            resposta = (
                f"Perfeito, {nome} ✨ E em relação ao acabamento, o que faz mais sentido para a sua marca?\n\n"
                f"• Hot stamping\n"
                f"• Alto relevo seco\n"
                f"• Baixo relevo\n"
                f"• Empastamento / borda sanduíche\n"
                f"• Apenas impressão colorida no papel especial\n"
                f"• Combinação de acabamentos"
            )
            sessao["etapa"] = "acabamento"
    
    # ═══════════════════════════════════════
    # VALIDAÇÃO COUCHÊ 300g
    # ═══════════════════════════════════════
    elif etapa == "papel_couche_validar":
        nome = dados.get("nome", "").split()[0]
        
        if any(palavra in msg_lower for palavra in ["texturado", "textura", "explorar", "outro"]):
            dados["material"] = "texturado"
            resposta = (
                f"Perfeito, {nome} ✨ Você prefere texturado até 400g ou texturado acima de 400g?"
            )
            sessao["etapa"] = "papel"
        elif any(palavra in msg_lower for palavra in ["sem", "não quero", "nao quero", "sem acabamento"]):
            resposta = (
                f"Entendemos perfeitamente, {nome}. Quando quiser explorar uma proposta "
                f"mais alinhada ao padrão premium da Primyn, estaremos por aqui ✦"
            )
            sessao["etapa"] = "encerrado"
        else:
            dados["acabamento"] = msg
            resposta = f"Perfeito, {nome} ✨ Qual quantidade você está considerando para esse projeto?"
            sessao["etapa"] = "quantidade"
    
    # ═══════════════════════════════════════
    # ACABAMENTO
    # ═══════════════════════════════════════
    elif etapa == "acabamento":
        dados["acabamento"] = msg
        nome = dados.get("nome", "").split()[0]
        resposta = f"Perfeito, {nome} ✨ Qual quantidade você está considerando para esse projeto?"
        sessao["etapa"] = "quantidade"
    
    # ═══════════════════════════════════════
    # QUANTIDADE
    # ═══════════════════════════════════════
    elif etapa == "quantidade":
        dados["quantidade"] = msg
        nome = dados.get("nome", "").split()[0]
        
        # Calcular média
        try:
            qtd_num = ''.join(filter(str.isdigit, msg))
            media = calcular_media(dados.get("material", ""), qtd_num)
        except:
            media = 898  # fallback
        
        # Adicionar criação se houver
        valor_criacao = dados.get("valor_criacao", 0)
        if valor_criacao:
            media += valor_criacao
        
        dados["media"] = media
        
        resposta = (
            f"Perfeito, {nome} ✨ Para a configuração que você me passou, o investimento médio "
            f"fica em torno de R$ {media:,.2f}. Esse valor é uma referência e o orçamento final "
            f"é personalizado conforme acabamento, criação e complexidade do projeto. ✦\n\n"
            f"Faz sentido para você prosseguirmos com uma proposta personalizada?"
        )
        sessao["etapa"] = "media_proposta"
    
    # ═══════════════════════════════════════
    # MÉDIA / PROPOSTA
    # ═══════════════════════════════════════
    elif etapa == "media_proposta":
        nome = dados.get("nome", "").split()[0]
        
        if any(palavra in msg_lower for palavra in ["sim", "faz", "sentido", "quero", "vamos", "pode", "ok", "claro"]):
            resposta = f"Perfeito ✨ Você tem algum prazo ou data importante para receber esse material?"
            sessao["etapa"] = "urgencia"
        
        elif any(palavra in msg_lower for palavra in ["pensar", "depois", "calma", "ainda não", "ainda nao"]):
            resposta = (
                f"Claro, {nome} ✨ Sem pressa. Quando quiser retomar, estaremos por aqui. "
                f"Se desejar, acompanhe nossos projetos em @primyn.store ✦"
            )
            dados["status"] = "aguardando_resposta"
            sessao["etapa"] = "encerrado"
            # Agendar follow-up
            try:
                from followup import agendar_followup
                agendar_followup(numero, dados.get("nome", ""), "pensar", dias=2)
            except:
                pass
        
        elif any(palavra in msg_lower for palavra in ["não", "nao", "desisto", "cancelar"]):
            resposta = (
                f"Sem problema, {nome} ✨ Agradeço pelo seu tempo e fico à disposição "
                f"caso queira retomar em outro momento."
            )
            dados["status"] = "perdido"
            sessao["etapa"] = "encerrado"
        
        else:
            resposta = (
                f"{nome}, me conta: faz sentido prosseguirmos com uma proposta personalizada "
                f"ou prefere pensar com calma?"
            )
    
    # ═══════════════════════════════════════
    # URGÊNCIA
    # ═══════════════════════════════════════
    elif etapa == "urgencia":
        dados["urgencia"] = msg
        nome = dados.get("nome", "").split()[0]
        
        if any(palavra in msg_lower for palavra in ["urgente", "rápido", "rapido", "pressa", "amanhã", "amanha", "essa semana"]):
            resposta = (
                f"Perfeito ✦ Projetos com criação e produção premium têm prazo médio de "
                f"5 a 8 dias úteis. Vou sinalizar isso no seu direcionamento.\n\n"
                f"Perfeito 😊 Vou encaminhar seu projeto ao nosso sistema para uma proposta "
                f"personalizada. Em breve, um especialista dará continuidade ao seu atendimento, {nome}. ✦"
            )
        else:
            resposta = (
                f"Perfeito 😊 Vou encaminhar seu projeto ao nosso sistema para uma proposta "
                f"personalizada. Em breve, um especialista dará continuidade ao seu atendimento, {nome}. ✦"
            )
        
        dados["status"] = "handoff"
        sessao["etapa"] = "handoff"
        handoff_data = dados
    
    # ═══════════════════════════════════════
    # HANDOFF (após enviar dados)
    # ═══════════════════════════════════════
    elif etapa == "handoff":
        nome = dados.get("nome", "").split()[0]
        resposta = f"Antes de encerrar, {nome} ✨ como foi sua experiência com este atendimento inicial?"
        sessao["etapa"] = "feedback"
    
    # ═══════════════════════════════════════
    # FEEDBACK
    # ═══════════════════════════════════════
    elif etapa == "feedback":
        dados["avaliacao"] = msg
        nome = dados.get("nome", "").split()[0]
        resposta = (
            f"Muito obrigada pelo feedback, {nome}! ✨ "
            f"Foi um prazer te atender. Até breve! ✦"
        )
        sessao["etapa"] = "encerrado"
    
    # ═══════════════════════════════════════
    # ENCERRADO (se mandar mensagem depois)
    # ═══════════════════════════════════════
    elif etapa == "encerrado":
        nome = dados.get("nome", "").split()[0] if dados.get("nome") else ""
        if nome:
            resposta = (
                f"Olá novamente, {nome}! ✨ Quer retomar seu projeto ou precisa de algo mais? "
                f"Estou por aqui! ✦"
            )
        else:
            resposta = (
                "Olá! ✨ Seja muito bem-vindo(a) de volta à Primyn. "
                "Como posso te ajudar?"
            )
        sessao["etapa"] = "produto"
    
    # ═══════════════════════════════════════
    # DEFAULT
    # ═══════════════════════════════════════
    else:
        resposta = (
            "Olá! ✨ Seja muito bem-vindo(a) à Primyn.\n\n"
            "Sou a Mily, consultora virtual da Primyn. Como posso te ajudar?"
        )
        sessao["etapa"] = "origem"
    
    # Salvar sessão atualizada
    sessao["dados"] = dados
    atualizar_sessao(numero, sessao)
    
    return resposta, handoff_data
