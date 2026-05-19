
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

PALAVRAS_INVALIDAS={
    "eu","ok","sim","não","nao","oi","olá","ola","hey","hi","hello",
    "obrigada","obrigado","certo","claro","perfeito","ótimo","otimo",
    "nada","teste","test","aaa","bbb","xxx","tudo","bem"
}

def email_valido(e):
    e=e.strip().lower()
    parts=e.split("@")
    if len(parts)!=2: return False
    local,domain=parts
    if len(local)<2: return False
    if "." not in domain: return False
    partes_dom=domain.split(".")
    if len(partes_dom[-1])<2: return False
    if len(partes_dom[0])<2: return False
    return True

def nome_valido(n):
    if not n: return False
    partes=[p.lower() for p in n.strip().split() if p.isalpha() and len(p)>=2]
    reais=[p for p in partes if p not in PALAVRAS_INVALIDAS]
    return len(reais)>=2

def extrair_bloco(msg, campos):
    """Extrai campos de uma mensagem em bloco com validação rigorosa."""
    lines=[l.strip() for l in msg.strip().splitlines() if l.strip()]
    resultado={c:"" for c in campos}

    # 1. Tentar extrair por labels (formato com ":")
    for l in lines:
        ll=l.lower()
        if ":" not in l: continue
        val=l.split(":",1)[1].strip()
        if not val: continue
        if "nome" in ll:
            resultado["nome"]=val.title()
        elif any(p in ll for p in ["área","area","atuação","atuacao","profiss","empresa"]):
            resultado["area"]=val.title()
        elif any(p in ll for p in ["e-mail","email","contato"]):
            resultado["email"]=val.lower()
        elif any(p in ll for p in ["material","interesse"]):
            resultado["material"]=val

    # 2. Procurar e-mail em qualquer linha (tem @ e ponto após @)
    if not resultado.get("email"):
        for l in lines:
            tok=l.strip().lower()
            if "@" in tok:
                # Pegar só o token com @
                for word in tok.split():
                    if "@" in word and email_valido(word):
                        resultado["email"]=word; break

    # 3. Fallback sem labels: só se tiver 3+ linhas separadas (cada linha = um campo)
    if not resultado.get("nome") and len(lines)>=3:
        candidato=lines[0].strip()
        # Rejeitar se candidato contém @ ou números ou é muito curto
        if "@" not in candidato and len(candidato)>3:
            resultado["nome"]=candidato.title()
        if not resultado.get("area"):
            resultado["area"]=lines[1].strip().title()
        if not resultado.get("email") and len(lines)>=3:
            resultado["email"]=lines[2].strip().lower()

    return resultado

def processar_mensagem(numero, mensagem):
    sessao=get_sessao(numero)
    etapa=sessao["etapa"]
    dados=sessao["dados"]
    msg=mensagem.strip()
    ml=msg.lower()
    resposta=""
    handoff_data=None
    tent=sessao.get("tentativas",0)

    SEP="\n━━━━━━━━━━━━━━━"

    def primeiro_nome():
        n=dados.get("nome","")
        return n.split()[0] if n else ""

    # ── ABERTURA ──────────────────────────────────────────────────────────────
    if etapa=="abertura":
        resposta=(
            "✨ Olá, seja muito bem-vindo(a) à Primyn! Sou a Mily.\n\n"
            "Antes de começarmos, quero te contar rapidamente sobre a nossa missão.\n\n"
            "A Primyn não trabalha apenas com impressão personalizada — desenvolvemos experiências visuais "
            "que ajudam marcas e profissionais a transmitir mais autoridade, sofisticação e valor "
            "através da apresentação da sua empresa.\n\n"
            "Cada projeto é pensado estrategicamente para fortalecer a percepção da sua marca "
            "nos mínimos detalhes.\n\n"
            "Será um prazer conhecer melhor o que você procura para direcionarmos seu atendimento "
            "de forma personalizada ao especialista ideal da nossa equipe.\n\n"
            "Para começarmos, como você conheceu a Primyn?\n"
            "(Se preferir mais praticidade, basta responder apenas com o número.)\n\n"
            "1. Google\n"
            "2. Instagram\n"
            "3. Indicação\n"
            "4. Já sou cliente\n"
            "5. Estava em contato anteriormente"
        )
        sessao["etapa"]="origem"; sessao["tentativas"]=0

    # ── ORIGEM ────────────────────────────────────────────────────────────────
    elif etapa=="origem":
        if any(p in ml for p in ["4","já sou","ja sou","sou cliente","já comprei","ja comprei"]):
            dados["origem"]="cliente_recorrente"
            resposta=("Que bom ter você de volta! 😊\n\n"
                      "Para que eu possa direcionar seu atendimento com mais agilidade, "
                      "poderia nos informar:\n\n"
                      "Nome e sobrenome:\nE-mail:\nMaterial de interesse:")
            sessao["etapa"]="coleta_cliente"

        elif any(p in ml for p in ["5","anteriormente","estava em","antes","já falei","ja falei","voltei","em contato"]):
            dados["origem"]="lead_antigo"
            resposta=("Que bom que voltou! 😊\n\n"
                      "Para que eu possa retomar seu atendimento com mais agilidade, "
                      "poderia nos informar:\n\n"
                      "Nome e sobrenome:\nE-mail:\nMaterial de interesse:")
            sessao["etapa"]="coleta_cliente"

        elif any(p in ml for p in ["3","indicação","indicacao","indicou","indicado","indica"]):
            dados["origem"]="Indicação"
            resposta="Que honra! Ficamos muito felizes com a indicação. 😊\n\nPoderia nos dizer quem nos indicou?"
            sessao["etapa"]="origem_indicacao"

        elif any(p in ml for p in ["1","google"]):
            dados["origem"]="Google"
            sessao["etapa"]="coleta_dados"
            resposta=(
                "Que ótimo que nos encontrou pelo Google! ✨\n\n"
                "Perfeito ✨ Para prepararmos uma proposta personalizada para o seu projeto, "
                "poderia nos informar:\n\n"
                "Nome e sobrenome:\nÁrea de atuação da empresa/profissão:\nMelhor e-mail para contato:"
            )

        elif any(p in ml for p in ["2","instagram","insta"]):
            dados["origem"]="Instagram"
            sessao["etapa"]="coleta_dados"
            resposta=(
                "Fico feliz que tenha nos encontrado pelo Instagram! ✨\n\n"
                "Perfeito ✨ Para prepararmos uma proposta personalizada para o seu projeto, "
                "poderia nos informar:\n\n"
                "Nome e sobrenome:\nÁrea de atuação da empresa/profissão:\nMelhor e-mail para contato:"
            )

        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Opção não encontrada. Por favor, escolha uma das opções abaixo:\n\n"
                      "1. Google\n2. Instagram\n3. Indicação\n"
                      "4. Já sou cliente\n5. Estava em contato anteriormente")

    # ── ORIGEM INDICAÇÃO ──────────────────────────────────────────────────────
    elif etapa=="origem_indicacao":
        # Rejeitar se for só número ou muito curto
        indicado=msg.strip()
        if indicado.isdigit() or len(indicado)<3 or not any(c.isalpha() for c in indicado):
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por gentileza, nos informe o nome de quem indicou. "
                      "Ex: Ana Silva, Dr. Carlos...")
        else:
            dados["indicado_por"]=indicado
            sessao["etapa"]="coleta_dados"; sessao["tentativas"]=0
            resposta=(
                "Obrigada! Vamos agradecer com carinho por você. 🤍\n\n"
                "Perfeito ✨ Para prepararmos uma proposta personalizada para o seu projeto, "
                "poderia nos informar:\n\n"
            "Nome e sobrenome:\nÁrea de atuação da empresa/profissão:\nMelhor e-mail para enviar a proposta:"
        )

    # ── COLETA CLIENTE / LEAD ANTIGO ──────────────────────────────────────────
    elif etapa=="coleta_cliente":
        r=extrair_bloco(msg,["nome","email","material"])
        nome_ext=r.get("nome","")
        email_ext=r.get("email","")
        material_ext=r.get("material","")

        erros=[]
        if not nome_valido(nome_ext):
            erros.append("• Nome e sobrenome completos (ex: Maria Silva)")
        # E-mail é opcional para clientes, mas se informado deve ser válido
        if email_ext and not email_valido(email_ext):
            erros.append("• E-mail válido (ex: seunome@gmail.com)")

        if erros:
            tent+=1; sessao["tentativas"]=tent
            if tent>=4:
                # Após muitas tentativas encaminha mesmo assim
                if nome_ext: dados["nome"]=nome_ext
                p=primeiro_nome()
                saudacao=f"Obrigada, {p}! " if p else "Obrigada! "
                sessao["tentativas"]=0; sessao["etapa"]="feedback"
                resposta=(f"{saudacao}Vou encaminhar você agora para um especialista da Primyn, "
                          "que dará continuidade ao seu atendimento de forma personalizada. ✨\n\n"
                          "Antes de encerrar — como foi a sua experiência com este atendimento?\n\n"
                          "1. Ótimo\n2. Bom\n3. Precisa melhorar")
                handoff_data=dados
            else:
                motivo="\n".join(erros)
                resposta=(f"Não consegui identificar corretamente:\n\n{motivo}\n\n"
                          "Por favor, envie nesse formato:\n\n"
                          "Nome e sobrenome: Maria Silva\n"
                          "E-mail: maria@gmail.com\n"
                          "Material de interesse: Cartão de visita")
        else:
            dados["nome"]=nome_ext
            if email_ext: dados["email"]=email_ext
            if material_ext: dados["material_interesse"]=material_ext
            p=primeiro_nome()
            saudacao=f"Obrigada, {p}! " if p else "Obrigada! "
            sessao["tentativas"]=0; sessao["etapa"]="feedback"
            resposta=(f"{saudacao}Vou encaminhar você agora para um especialista da Primyn, "
                      "que dará continuidade ao seu atendimento de forma personalizada. ✨\n\n"
                      "Antes de encerrar — como foi a sua experiência com este atendimento?\n\n"
                      "1. Ótimo\n2. Bom\n3. Precisa melhorar")
            handoff_data=dados

    # ── COLETA DADOS NOVOS ────────────────────────────────────────────────────
    elif etapa=="coleta_dados":
        r=extrair_bloco(msg,["nome","area","email"])
        nome_ext=r.get("nome","")
        email_ext=r.get("email","")
        area_ext=r.get("area","")

        erros=[]
        if not nome_valido(nome_ext):
            erros.append("• Nome e sobrenome (ex: Maria Silva)")
        if not email_valido(email_ext):
            erros.append("• E-mail válido (ex: seunome@gmail.com)")

        if erros:
            tent+=1; sessao["tentativas"]=tent
            if tent>=4 and nome_valido(nome_ext):
                # Após muitas tentativas aceita sem e-mail
                dados["nome"]=nome_ext
                if area_ext: dados["area"]=area_ext
                p=primeiro_nome(); sessao["tentativas"]=0; sessao["etapa"]="produto"
                resposta=(f"Perfeito, {p}! Vamos seguir. ✨\n\n"
                          "O que você deseja desenvolver na Primyn?\n\n"
                          "1. Cartão de visita premium\n"
                          "2. Papelaria personalizada\n"
                          "3. Projeto exclusivo/específico")
            else:
                motivo="\n".join(erros)
                resposta=(f"Não consegui identificar corretamente:\n\n{motivo}\n\n"
                          "Por favor, envie nesse formato:\n\n"
                          "Nome e sobrenome: Maria Silva\n"
                          "Área de atuação: Medicina\n"
                          "Melhor e-mail: maria@gmail.com")
        else:
            dados["nome"]=nome_ext
            if area_ext: dados["area"]=area_ext
            dados["email"]=email_ext
            p=primeiro_nome(); sessao["tentativas"]=0; sessao["etapa"]="produto"
            resposta=(f"Perfeito, {p}! Seus dados foram registrados. ✨\n\n"
                      "O que você deseja desenvolver na Primyn?\n\n"
                      "1. Cartão de visita premium\n"
                      "2. Papelaria personalizada\n"
                      "3. Projeto exclusivo/específico")

    # ── PRODUTO ───────────────────────────────────────────────────────────────
    elif etapa=="produto":
        if any(p in ml for p in ["1","cartão","cartao","visita","card"]):
            dados["produto"]="Cartão de visita premium"
        elif any(p in ml for p in ["2","papelaria","personalizada","kit"]):
            dados["produto"]="Papelaria personalizada"
        elif any(p in ml for p in ["3","projeto","exclusivo","específico","especifico","outro"]):
            dados["produto"]="Projeto exclusivo/específico"
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Cartão de visita premium\n"
                      "2. Papelaria personalizada\n"
                      "3. Projeto exclusivo/específico")
            sessao["dados"]=dados; upd_sessao(numero,sessao)
            return resposta, handoff_data

        sessao["tentativas"]=0; sessao["etapa"]="arte"
        resposta=(
            "Você precisará do desenvolvimento da arte/design do material?\n\n"
            "1. Sim\n"
            "2. Não, já possuo a arte pronta"
        )

    # ── ARTE ──────────────────────────────────────────────────────────────────
    elif etapa=="arte":
        if any(p in ml for p in ["1","sim","preciso","vou precisar","quero","desenvolver"]):
            dados["criacao_arte"]=True
            sessao["etapa"]="identidade_visual"
        elif any(p in ml for p in ["2","não","nao","já possuo","ja possuo","tenho","pronta"]):
            dados["criacao_arte"]=False
            sessao["etapa"]="identidade_visual"
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha:\n\n"
                      "1. Sim\n2. Não, já possuo a arte pronta")
            sessao["dados"]=dados; upd_sessao(numero,sessao)
            return resposta, handoff_data

        sessao["tentativas"]=0
        resposta=(
            "Sua empresa já possui identidade visual/logomarca profissional?\n\n"
            "Caso deseje, também podemos desenvolver uma identidade visual premium e estratégica "
            "para fortalecer o posicionamento da sua marca. Nossa designer Ane, com mais de 10 anos "
            "de experiência, poderá apresentar todos os detalhes desse processo de criação.\n\n"
            "1. Sim, já possuo identidade visual\n"
            "2. Ainda não, e tenho interesse em saber mais\n"
            "3. Ainda não, mas não tenho interesse"
        )

    # ── IDENTIDADE VISUAL ─────────────────────────────────────────────────────
    elif etapa=="identidade_visual":
        ESTILO=(
            "Qual estilo mais representa a experiência que você deseja transmitir com a sua marca?\n\n"
            "1. Clássico e refinado — Elegância discreta, apresentação sofisticada e minimalista.\n\n"
            "2. Premium com presença e textura — Materiais mais encorpados, sensação de qualidade "
            "superior e maior impacto visual.\n\n"
            "3. Luxo com acabamentos exclusivos — Experiência de alto padrão com materiais e "
            "acabamentos sofisticados."
        )
        if any(p in ml for p in ["2","ainda não","ainda nao","interesse","saber mais","não possuo","nao possuo"]) and "3" not in msg:
            dados["identidade_visual"]="interesse"
            dados["contato_designer"]=True
            sessao["tentativas"]=0; sessao["etapa"]="linha_estilo"
            resposta=(
                "Perfeito ✨\n\n"
                "Seu contato foi encaminhado para a nossa designer Ane, responsável pelos projetos "
                "de identidade visual da Primyn, e ela entrará em contato com você o mais breve "
                "possível para entender melhor os detalhes do seu projeto e apresentar as "
                "possibilidades de criação.\n\n"
                "Será um prazer desenvolver algo exclusivo e estratégico para a sua marca.\n\n"
                "Agora vamos continuar. "+ESTILO
            )
        elif any(p in ml for p in ["3","não tenho interesse","nao tenho","sem interesse"]):
            dados["identidade_visual"]="sem_interesse"
            sessao["tentativas"]=0; sessao["etapa"]="linha_estilo"
            resposta=ESTILO
        elif any(p in ml for p in ["1","sim","já possuo","ja possuo","possuo","tenho"]):
            dados["identidade_visual"]="possui"
            sessao["tentativas"]=0; sessao["etapa"]="linha_estilo"
            resposta=ESTILO
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Opção não identificada. Por favor, escolha:\n\n"
                      "1. Sim, já possuo identidade visual\n"
                      "2. Ainda não, e tenho interesse em saber mais\n"
                      "3. Ainda não, mas não tenho interesse")

    # ── LINHA DE ESTILO ───────────────────────────────────────────────────────
    elif etapa=="linha_estilo":
        if any(p in ml for p in ["1","clássico","classico","refinado","minimalista","elegância discreta","elegancia discreta"]):
            dados["linha"]="Clássico e refinado"
        elif any(p in ml for p in ["2","premium","textura","encorpado","impacto"]):
            dados["linha"]="Premium com presença e textura"
        elif any(p in ml for p in ["3","luxo","exclusivo","sofisticado","alto padrão","alto padrao"]):
            dados["linha"]="Luxo com acabamentos exclusivos"
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Opção não identificada. Por favor, escolha:\n\n"
                      "1. Clássico e refinado\n"
                      "2. Premium com presença e textura\n"
                      "3. Luxo com acabamentos exclusivos")
            sessao["dados"]=dados; upd_sessao(numero,sessao)
            return resposta, handoff_data

        sessao["tentativas"]=0; sessao["etapa"]="faixa_investimento"
        resposta=(
            "Para direcionarmos o projeto de forma mais assertiva, qual faixa de investimento "
            "você pretende considerar para essa experiência?\n\n"
            "1. Entre R$ 400 e R$ 700\n"
            "2. Entre R$ 700 e R$ 1.200\n"
            "3. Entre R$ 1.200 e R$ 2.000\n"
            "4. Acima de R$ 2.000"
            "5. Nenhuma das alternativas"
        )

    # ── FAIXA DE INVESTIMENTO ─────────────────────────────────────────────────
    elif etapa=="faixa_investimento":
        faixas={"1":"Entre R$ 400 e R$ 700","2":"Entre R$ 700 e R$ 1.200",
                "3":"Entre R$ 1.200 e R$ 2.000","4":"Acima de R$ 2.000"}
        opcao=None
        for k in faixas:
            if k in msg: opcao=k; break
        if not opcao:
            if "400" in msg or "700" in msg and "1" not in msg: opcao="1"
            elif "700" in msg or "1.200" in msg or "1200" in msg: opcao="2"
            elif "1.200" in msg or "2.000" in msg or "2000" in msg and "acima" not in ml: opcao="3"
            elif "acima" in ml or "2.000" in msg or "2000" in msg: opcao="4"
        if not opcao:
            tent+=1; sessao["tentativas"]=tent
            if "5" in msg or any(p in ml for p in ["nenhuma","nenhum","outro","abaixo"]):
            p=primeiro_nome()
            resposta=(
                f"Entendo perfeitamente{', '+p if p else ''} ✨\n\n"
                "Apenas para te dar uma referência, nossos projetos costumam partir de R$ 400, "
                "pois trabalhamos com materiais e acabamentos mais sofisticados, pensados para "
                "transmitir uma percepção mais premium da marca.\n\n"
                "Quando estiver pronto(a) e quiser explorar as possibilidades, será um prazer "
                "atendê-lo(a). Enquanto isso, nosso Instagram @primyn.store tem muito para "
                "te inspirar ✨"
            )
            dados["faixa_investimento"]="Nenhuma das alternativas"
            dados["status"]="perdido"
            sessao["etapa"]="encerrado"
            sessao["dados"]=dados
            upd_sessao(numero,sessao)
            return resposta, handoff_data
            resposta=("Opção não identificada. Por favor, escolha:\n\n"
                      "1. Entre R$ 400 e R$ 700\n2. Entre R$ 700 e R$ 1.200\n"
                      "3. Entre R$ 1.200 e R$ 2.000\n4. Acima de R$ 2.000")
            sessao["dados"]=dados; upd_sessao(numero,sessao)
            return resposta, handoff_data

        dados["faixa_investimento"]=faixas[opcao]
        sessao["tentativas"]=0; sessao["etapa"]="confirmar_proposta"
        p=primeiro_nome()
        resposta=(
            f"Perfeito{', '+p if p else ''}! ✨ Gostaria de prosseguir para uma proposta exclusiva "
            "com um especialista da Primyn?\n\n"
            "1. Sim, gostaria de continuar\n"
            "2. Vou pensar melhor no momento\n"
            "3. Não desejo prosseguir"
        )

    # ── CONFIRMAR PROPOSTA ────────────────────────────────────────────────────
    elif etapa=="confirmar_proposta":
        if any(p in ml for p in ["1","sim","gostaria","continuar","quero","pode","vamos"]):
            dados["status"]="handoff"
            resposta=("Perfeito. ✨ Vou encaminhar todas as informações para um especialista da Primyn, "
                      "que continuará seu atendimento de forma personalizada.\n\n"
                      "Antes de encerrar — como foi a sua experiência com este atendimento?\n\n"
                      "1. Ótimo\n2. Bom\n3. Precisa melhorar")
            handoff_data=dados; sessao["etapa"]="feedback"

        elif any(p in ml for p in ["2","pensar","talvez","depois","momento","melhor"]):
            resposta=("Sem problemas. ✨ Foi um prazer conhecer um pouco mais sobre o seu projeto. "
                      "Quando desejar, estaremos à disposição para criar algo realmente especial "
                      "para a sua marca.")
            dados["status"]="aguardando"; sessao["etapa"]="encerrado"

        else:
            resposta=("Agradecemos pelo seu contato e pelo interesse na Primyn. ✨ "
                      "Desejamos muito sucesso para sua marca e esperamos poder atender você "
                      "em outro momento.")
            dados["status"]="perdido"; sessao["etapa"]="encerrado"

    # ── FEEDBACK ──────────────────────────────────────────────────────────────
    elif etapa=="feedback":
        avals={"1":"Ótimo","2":"Bom","3":"Precisa melhorar"}
        # Detectar opção por número ou palavra
        opcao=None
        if msg.strip() in avals: opcao=msg.strip()
        elif any(p in ml for p in ["ótimo","otimo","excelente","perfeito"]): opcao="1"
        elif any(p in ml for p in ["bom","boa","gostei","legal"]): opcao="2"
        elif any(p in ml for p in ["melhorar","ruim","mal","péssimo","pessimo","precisa"]): opcao="3"

        if not opcao:
            tent+=1; sessao["tentativas"]=tent
            resposta="Por favor, escolha:\n\n1. Ótimo\n2. Bom\n3. Precisa melhorar"
        else:
            dados["avaliacao"]=avals[opcao]
            p=primeiro_nome()
            if opcao=="3":
                resposta=(f"Obrigada pelo retorno{', '+p if p else ''}. "
                          "Cada feedback nos ajuda a evoluir. 🤍")
            else:
                resposta=(f"Que bom{', '+p if p else ''}! "
                          "Foi um prazer te atender. Até breve! 🤍")
            sessao["etapa"]="encerrado"

    # ── ENCERRADO ─────────────────────────────────────────────────────────────
    elif etapa=="encerrado":
        p=primeiro_nome()
        resposta=(f"Olá{', '+p if p else ''}! Como posso te ajudar? 😊")
        sessao["etapa"]="produto" if dados.get("nome") else "abertura"

    else:
        resposta="Olá! Como posso te ajudar? 😊"
        sessao["etapa"]="abertura"

    sessao["dados"]=dados
    upd_sessao(numero,sessao)
    return resposta, handoff_data

carregar_sessoes = load
