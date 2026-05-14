
import json, os, random
from datetime import datetime

DB_FILE = "sessoes.json"

def var(*o): return random.choice(o)

def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE,"r",encoding="utf-8") as f: return json.load(f)
    return {}

def save(s):
    with open(DB_FILE,"w",encoding="utf-8") as f: json.dump(s,f,ensure_ascii=False,indent=2)

def get_sessao(num):
    s=load()
    if num not in s:
        s[num]={"etapa":"abertura","fluxo":None,
                "dados":{"whatsapp":num,"data":datetime.now().isoformat()},
                "ultimo":datetime.now().isoformat(),"tentativas":0}
        save(s)
    return s[num]

def upd_sessao(num,sessao):
    s=load(); sessao["ultimo"]=datetime.now().isoformat(); s[num]=sessao; save(s)

def val_email(msg):
    msg=msg.strip().lower()
    parts=msg.split("@")
    if len(parts)==2 and "." in parts[1] and len(parts[1].split(".")[-1])>=2 and len(parts[0])>0:
        return True,msg
    return False,None

def extrair_dados_bloco(msg):
    """Extrai nome, área e e-mail de uma mensagem em bloco."""
    lines=[l.strip() for l in msg.strip().splitlines() if l.strip()]
    nome=""; area=""; email=""
    for l in lines:
        ll=l.lower()
        if "nome" in ll and ":" in l:
            nome=l.split(":",1)[1].strip()
        elif "área" in ll or "area" in ll and ":" in l:
            area=l.split(":",1)[1].strip()
        elif "e-mail" in ll or "email" in ll or "e mail" in ll and ":" in l:
            email=l.split(":",1)[1].strip()
        elif "@" in l and "." in l:
            email=l.strip()
    # Fallback: se só 3 linhas sem labels
    if not nome and not email and len(lines)>=3:
        nome=lines[0]
        area=lines[1]
        email=lines[2]
    return nome.title(), area.title(), email.lower()

def processar_mensagem(numero, mensagem):
    sessao=get_sessao(numero)
    etapa=sessao["etapa"]
    dados=sessao["dados"]
    msg=mensagem.strip()
    ml=msg.lower()
    resposta=""
    handoff_data=None
    tent=sessao.get("tentativas",0)

    def hdoff():
        return ("Vou encaminhar você agora para um especialista da nossa equipe, "
                "que dará continuidade ao seu atendimento de forma personalizada. 🚀\n\n"
                "Antes de encerrar — como foi a sua experiência com este atendimento?\n\n"
                "1. Ótimo\n2. Bom\n3. Precisa melhorar")

    # ── ABERTURA ──────────────────────────────────────────────────────────────
    if etapa=="abertura":
        resposta=(
            "Olá, seja muito bem-vindo(a) à Primyn! ✨\n\n"
            "Sou a Mily, e será um prazer entender o seu projeto. "
            "Este é um breve alinhamento inicial para que eu possa direcionar "
            "o seu atendimento de forma personalizada a um especialista da nossa equipe.\n\n"
            "Para começarmos — como você conheceu a Primyn? "
            "Digite apenas o número se quiser mais praticidade:\n\n"
            "1. Google\n"
            "2. Instagram\n"
            "3. Indicação\n"
            "4. Já sou cliente\n"
            "5. Estava em contato anteriormente"
        )
        sessao["etapa"]="origem"; sessao["tentativas"]=0

    # ── ORIGEM ────────────────────────────────────────────────────────────────
    elif etapa=="origem":
        if any(p in ml for p in ["4","já sou","ja sou","cliente","já comprei","ja comprei"]):
            dados["origem"]="cliente_recorrente"
            resposta=("Que bom ter você de volta! 😊\n\n"
                      "Para que eu possa direcionar seu atendimento com mais agilidade, "
                      "poderia nos informar:\n\n"
                      "Seu nome e sobrenome:\nE-mail:\nMaterial de interesse:")
            dados["status"]="handoff_cliente"; sessao["etapa"]="coleta_cliente"

        elif any(p in ml for p in ["5","anteriormente","contato","antes","já falei","ja falei","voltei"]):
            dados["origem"]="lead_antigo"
            resposta=("Que bom que voltou! 😊\n\n"
                      "Para que eu possa direcionar seu atendimento com mais agilidade, "
                      "poderia nos informar:\n\n"
                      "Seu nome e sobrenome:\nE-mail:\nMaterial de interesse:")
            dados["status"]="handoff_antigo"; sessao["etapa"]="coleta_cliente"

        elif any(p in ml for p in ["3","indicação","indicacao","indicou","indicado"]):
            dados["origem"]="Indicação"
            resposta=("Que honra! Ficamos muito felizes com a indicação. 😊\n\n"
                      "Poderia nos dizer quem nos indicou?")
            sessao["etapa"]="origem_indicacao"

        elif any(p in ml for p in ["1","google"]):
            dados["origem"]="Google"
            sessao["etapa"]="coleta_dados"
            resposta=(
                "Que ótimo que nos encontrou por lá! ✨\n\n"
                "Para envio da proposta personalizada, poderia nos informar:\n\n"
                "Seu nome e sobrenome:\nÁrea de atuação:\nE-mail:"
            )

        elif any(p in ml for p in ["2","instagram","insta"]):
            dados["origem"]="Instagram"
            sessao["etapa"]="coleta_dados"
            resposta=(
                "Fico feliz que tenha nos encontrado pelo Instagram! ✨\n\n"
                "Para envio da proposta personalizada, poderia nos informar:\n\n"
                "Seu nome e sobrenome:\nÁrea de atuação:\nE-mail:"
            )

        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Google\n2. Instagram\n3. Indicação\n"
                      "4. Já sou cliente\n5. Estava em contato anteriormente")

    # ── ORIGEM INDICAÇÃO ──────────────────────────────────────────────────────
    elif etapa=="origem_indicacao":
        dados["indicado_por"]=msg
        sessao["etapa"]="coleta_dados"
        resposta=(
            "Obrigada! Vamos agradecer com carinho por você. 🤍\n\n"
            "Para envio da proposta personalizada, poderia nos informar:\n\n"
            "Seu nome e sobrenome:\nÁrea de atuação:\nE-mail:"
        )

    # ── COLETA DE DADOS (nome + área + e-mail em bloco) ───────────────────────
    elif etapa=="coleta_dados":
        nome,area,email=extrair_dados_bloco(msg)

        # Fallback: aceita msg livre se tiver pelo menos nome
        if not nome and len(msg.split())>=2:
            partes=msg.split()
            nome=" ".join(p.title() for p in partes[:2])

        if not nome:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Não consegui identificar todos os dados. Por favor, envie nesse formato:\n\n"
                      "Seu nome e sobrenome:\nÁrea de atuação:\nE-mail:")
        else:
            dados["nome"]=nome
            if area: dados["area"]=area
            if email: dados["email"]=email
            primeiro=nome.split()[0]
            sessao["tentativas"]=0
            sessao["etapa"]="produto"
            resposta=(
                f"Prazer, {primeiro}! Seus dados foram anotados. 😊\n\n"
                "O que você deseja desenvolver?\n\n"
                "1. Cartão de visita\n"
                "2. Papelaria personalizada\n"
                "3. Projeto específico"
            )

    # ── PRODUTO ───────────────────────────────────────────────────────────────
    elif etapa=="produto":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","cartão","cartao","visita","card"]):
            dados["produto"]="Cartão de visita"
        elif any(p in ml for p in ["2","papelaria","personalizada","kit"]):
            dados["produto"]="Papelaria personalizada"
        elif any(p in ml for p in ["3","projeto","específico","especifico","outro"]):
            dados["produto"]="Projeto específico"
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Cartão de visita\n2. Papelaria personalizada\n3. Projeto específico")
            sessao["dados"]=dados; upd_sessao(numero,sessao)
            return resposta, handoff_data

        sessao["tentativas"]=0
        sessao["etapa"]="arte"
        resposta=(
            f"Ótima escolha! ✨\n\n"
            "Você vai precisar de criação de arte?\n\n"
            "1. Sim\n"
            "2. Não"
        )

    # ── ARTE ──────────────────────────────────────────────────────────────────
    elif etapa=="arte":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","preciso","vou precisar","quero"]):
            dados["criacao_arte"]=True
            sessao["etapa"]="arte_opcao"
            resposta=(
                "Temos duas opções de criação:\n\n"
                "1. Criação de arte — R$ 74,90\n"
                "2. Criação de arte + amostra 3D — R$ 220,00\n\n"
                "Qual faz mais sentido para o seu projeto?"
            )
        elif any(p in ml for p in ["2","não","nao","já tenho","ja tenho","tenho"]):
            dados["criacao_arte"]=False
            sessao["etapa"]="linha_estilo"
            resposta=(
                "Entendido! Qual linha representa melhor o estilo que você busca para sua marca?\n\n"
                "1. Clássico com acabamento diferenciado — visual elegante e leve, com boa apresentação e simplicidade refinada\n\n"
                "2. Premium com presença e textura — mais encorpado, qualidade com elegância e maior impacto visual\n\n"
                "3. Luxo com acabamentos sofisticados — materiais e acabamentos exclusivos para uma experiência de alto padrão"
            )
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta="Por favor, escolha:\n\n1. Sim, vou precisar de criação de arte\n2. Não, já tenho arte"

    # ── ARTE OPÇÃO ────────────────────────────────────────────────────────────
    elif etapa=="arte_opcao":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["2","3d","220","amostra"]):
            dados["criacao_opcao"]="arte_3d"
            dados["valor_criacao"]=220.0
        else:
            dados["criacao_opcao"]="arte_simples"
            dados["valor_criacao"]=74.90

        sessao["etapa"]="identidade_visual"
        resposta=(
            "Anotado! ✨\n\n"
            "Gostaria da criação de identidade visual / logomarca premium "
            "para fortalecer a visibilidade profissional da sua empresa?\n\n"
            "1. Sim, adoraria\n"
            "2. Não, já tenho a minha"
        )

    # ── IDENTIDADE VISUAL ─────────────────────────────────────────────────────
    elif etapa=="identidade_visual":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","adoraria","quero","gostaria"]):
            dados["identidade_visual"]=True
            resposta=(
                "Que ótimo, {primeiro}! Nossa designer Ane entrará em contato "
                "para apresentar todos os detalhes do projeto. 👑\n\n"
                "Enquanto isso, vamos seguir com o alinhamento.\n\n"
                "Qual linha representa melhor o estilo que você busca para sua marca?\n\n"
                "1. Clássico com acabamento diferenciado — visual elegante e leve, com boa apresentação e simplicidade refinada\n\n"
                "2. Premium com presença e textura — mais encorpado, qualidade com elegância e maior impacto visual\n\n"
                "3. Luxo com acabamentos sofisticados — materiais e acabamentos exclusivos para uma experiência de alto padrão"
            ).replace("{primeiro}", primeiro)
        else:
            dados["identidade_visual"]=False
            resposta=(
                "Qual linha representa melhor o estilo que você busca para sua marca?\n\n"
                "1. Clássico com acabamento diferenciado — visual elegante e leve, com boa apresentação e simplicidade refinada\n\n"
                "2. Premium com presença e textura — mais encorpado, qualidade com elegância e maior impacto visual\n\n"
                "3. Luxo com acabamentos sofisticados — materiais e acabamentos exclusivos para uma experiência de alto padrão"
            )
        sessao["etapa"]="linha_estilo"

    # ── LINHA DE ESTILO ───────────────────────────────────────────────────────
    elif etapa=="linha_estilo":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","clássico","classico","elegante","leve","simples"]):
            dados["linha"]="Clássico com acabamento diferenciado"
        elif any(p in ml for p in ["2","premium","textura","encorpado","impacto"]):
            dados["linha"]="Premium com presença e textura"
        elif any(p in ml for p in ["3","luxo","sofisticado","exclusivo","alto padrão","alto padrao"]):
            dados["linha"]="Luxo com acabamentos sofisticados"
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das linhas:\n\n"
                      "1. Clássico com acabamento diferenciado\n"
                      "2. Premium com presença e textura\n"
                      "3. Luxo com acabamentos sofisticados")
            sessao["dados"]=dados; upd_sessao(numero,sessao)
            return resposta, handoff_data

        sessao["tentativas"]=0
        sessao["etapa"]="faixa_investimento"
        resposta=(
            "Para direcionarmos seu projeto da forma mais adequada, "
            "qual faixa de investimento você pretende considerar?\n\n"
            "1. Entre R$ 400 e R$ 500\n"
            "2. Entre R$ 700 e R$ 900\n"
            "3. Entre R$ 1.200 e R$ 1.500\n"
            "4. Acima de R$ 2.000"
        )

    # ── FAIXA DE INVESTIMENTO ─────────────────────────────────────────────────
    elif etapa=="faixa_investimento":
        primeiro=dados.get("nome","").split()[0]
        faixas={
            "1":"Entre R$ 400 e R$ 500",
            "2":"Entre R$ 700 e R$ 900",
            "3":"Entre R$ 1.200 e R$ 1.500",
            "4":"Acima de R$ 2.000"
        }
        opcao=None
        for k,v in faixas.items():
            if k in msg or any(p in ml for p in v.lower().split()):
                if k in msg: opcao=k; break
        if not opcao:
            for k in faixas:
                if k in msg: opcao=k; break
        if not opcao:
            if "400" in msg or "500" in msg: opcao="1"
            elif "700" in msg or "900" in msg: opcao="2"
            elif "1.200" in msg or "1200" in msg or "1.500" in msg or "1500" in msg: opcao="3"
            elif "2.000" in msg or "2000" in msg or "acima" in ml: opcao="4"

        if not opcao:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Entre R$ 400 e R$ 500\n2. Entre R$ 700 e R$ 900\n"
                      "3. Entre R$ 1.200 e R$ 1.500\n4. Acima de R$ 2.000")
        else:
            dados["faixa_investimento"]=faixas[opcao]
            sessao["tentativas"]=0
            sessao["etapa"]="confirmar_proposta"
            resposta=(
                f"Perfeito, {primeiro}! 😊\n\n"
                "Gostaria de prosseguir para uma proposta exclusiva com o nosso especialista?\n\n"
                "1. Sim, quero a proposta\n"
                "2. Vou pensar\n"
                "3. Não, obrigada"
            )

    # ── CONFIRMAR PROPOSTA ────────────────────────────────────────────────────
    elif etapa=="confirmar_proposta":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","quero","pode","vamos","claro"]):
            dados["status"]="handoff"
            resposta=hdoff()
            sessao["etapa"]="feedback"
            handoff_data=dados
        elif any(p in ml for p in ["2","pensar","talvez","depois","calma"]):
            resposta=var(
                f"Claro, {primeiro}! Sem qualquer pressa. Quando quiser retomar, estaremos aqui. 😊\n\nAcompanhe nossos projetos em @primyn.store",
                f"Com certeza. Essas decisões merecem calma. Quando quiser, é só chamar. 😊"
            )
            dados["status"]="aguardando"; sessao["etapa"]="encerrado"
        else:
            resposta=var(
                f"Obrigada pelo seu tempo, {primeiro}! Quando quiser explorar uma proposta, será um prazer. 😊",
                f"Entendido! Fico à disposição sempre que quiser retomar. 😊"
            )
            dados["status"]="perdido"; sessao["etapa"]="encerrado"

    # ── COLETA CLIENTE / LEAD ANTIGO ─────────────────────────────────────────
    elif etapa=="coleta_cliente":
        lines=[l.strip() for l in msg.strip().splitlines() if l.strip()]
        nome=""; email=""; material=""
        for l in lines:
            ll=l.lower()
            if "nome" in ll and ":" in l:
                nome=l.split(":",1)[1].strip().title()
            elif ("e-mail" in ll or "email" in ll) and ":" in l:
                email=l.split(":",1)[1].strip().lower()
            elif "material" in ll and ":" in l:
                material=l.split(":",1)[1].strip()
            elif "@" in l and "." in l:
                email=l.strip().lower()
        if not nome and len(lines)>=1: nome=lines[0].title()
        if not email:
            for l in lines[1:]:
                if "@" in l: email=l.strip().lower(); break
        if not material and len(lines)>=3: material=lines[-1]
        if nome: dados["nome"]=nome
        if email: dados["email"]=email
        if material: dados["material_interesse"]=material
        primeiro=nome.split()[0] if nome else ""
        saudacao=f"Obrigada, {primeiro}! " if primeiro else "Obrigada! "
        resposta=(f"{saudacao}Vou encaminhar você agora para um especialista "
                  "que dará continuidade ao seu atendimento de forma personalizada. 🚀\n\n"
                  "Antes de encerrar — como foi a sua experiência?\n\n"
                  "1. Ótimo\n2. Bom\n3. Precisa melhorar")
        handoff_data=dados; sessao["etapa"]="feedback"

    # ── FEEDBACK ──────────────────────────────────────────────────────────────
    elif etapa=="feedback":
        avals={"1":"Ótimo","2":"Bom","3":"Precisa melhorar"}
        av=avals.get(msg.strip(),msg); dados["avaliacao"]=av
        primeiro=dados.get("nome","").split()[0] if dados.get("nome") else ""
        saudacao=f"Que bom, {primeiro}! " if primeiro else "Que bom! "
        if msg.strip()=="3" or "melhorar" in ml or "ruim" in ml:
            resposta=f"Obrigada pelo retorno{', '+primeiro if primeiro else ''}. Cada feedback nos ajuda a evoluir. 🤍"
        else:
            resposta=f"{saudacao}Foi um prazer te atender. Até breve! 🤍"
        sessao["etapa"]="encerrado"

    # ── ENCERRADO ─────────────────────────────────────────────────────────────
    elif etapa=="encerrado":
        primeiro=dados.get("nome","").split()[0] if dados.get("nome") else ""
        resposta=f"Olá, {primeiro}! Como posso te ajudar? 😊" if primeiro else "Olá! Como posso te ajudar? 😊"
        sessao["etapa"]="produto" if primeiro else "abertura"

    else:
        resposta="Olá! Como posso te ajudar? 😊"
        sessao["etapa"]="abertura"

    sessao["dados"]=dados
    upd_sessao(numero,sessao)
    return resposta, handoff_data

carregar_sessoes = load
