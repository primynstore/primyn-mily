
import json, os, random
from datetime import datetime

DB_FILE = "sessoes.json"

PRODUTOS = {
    "1": {"nome":"Cartão de Visita / TAG","minimo":250,"aceita_3d":True,
          "medias":{"250":{"essencial":378,"luxo_black":562,"luxo_white":898,"prestigio":1297},
                    "500":{"essencial":475,"luxo_black":839,"luxo_white":1284,"prestigio":1682},
                    "1000":{"essencial":588,"luxo_black":1184,"luxo_white":1568,"prestigio":2567}}},
    "2": {"nome":"Pasta com bolsa ou orelha","minimo":100,"aceita_3d":False,
          "medias":{"100":{"essencial":2500,"luxo_black":2500,"luxo_white":2500,"prestigio":2500},
                    "250":{"essencial":3800,"luxo_black":3800,"luxo_white":3800,"prestigio":3800},
                    "500":{"essencial":5500,"luxo_black":5500,"luxo_white":5500,"prestigio":5500}}},
    "3": {"nome":"Envelope Ofício / Saco","minimo":100,"aceita_3d":False,
          "medias":{"100":{"essencial":720,"luxo_black":720,"luxo_white":720,"prestigio":720},
                    "250":{"essencial":1050,"luxo_black":1050,"luxo_white":1050,"prestigio":1050},
                    "500":{"essencial":1590,"luxo_black":1590,"luxo_white":1590,"prestigio":1590}}},
    "4": {"nome":"Papel Timbrado / Receituário","minimo":250,"aceita_3d":False,
          "medias":{"250":{"essencial":650,"luxo_black":650,"luxo_white":650,"prestigio":650},
                    "500":{"essencial":890,"luxo_black":890,"luxo_white":890,"prestigio":890},
                    "1000":{"essencial":1190,"luxo_black":1190,"luxo_white":1190,"prestigio":1190}}},
    "5": {"nome":"Papelaria Completa","minimo":250,"aceita_3d":False,
          "medias":{"250":{"essencial":4200,"luxo_black":4200,"luxo_white":5800,"prestigio":5800},
                    "500":{"essencial":5800,"luxo_black":5800,"luxo_white":7500,"prestigio":7500}}}
}

ITENS_KIT = {"1","2","3","4"}

AREAS = {"1":"Advocacia / Direito","2":"Arquitetura / Engenharia","3":"Medicina / Saúde",
         "4":"Moda / Beleza / Lifestyle","5":"Finanças / Executivo","6":"Outro"}

PAPEIS_AREA = {
    "1":"Notturno Black 450g, Dark Blue 450g ou Rives White 400g",
    "2":"Rives Natural White 400g ou Conqueror Bamboo 400g",
    "3":"Rives Traditional White 400g ou Conqueror Bamboo 400g",
    "4":"Color Plus 240g ou Rives White 400g",
    "5":"Notturno Black 450g, Dark Blue 450g ou Rives White 400g",
    "6":"Conqueror Bamboo 400g ou Notturno Black 450g"
}

TRANS_AREA = {
    "1":"Advocacia — uma área que exige precisão e autoridade em cada detalhe.",
    "2":"Arquitetura — uma área que exige sofisticação em cada detalhe.",
    "3":"Medicina — confiança e credibilidade que se refletem em cada peça.",
    "4":"Moda e beleza — estética e identidade visual que falam antes das palavras.",
    "5":"Finanças — onde a percepção de solidez faz toda a diferença.",
    "6":"Sua área merece uma identidade visual que reflita seu posicionamento."
}

ACOLH = ["Perfeito","Ótimo","Que bom","Claro","Maravilha"]
def ac(): return random.choice(ACOLH)
def var(*o): return random.choice(o)

def fmt(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def val_nome(msg):
    p=[x.strip() for x in msg.strip().split() if len(x.strip())>1]
    if len(p)>=2: return True," ".join(x.title() for x in p)
    return False,None

def val_email(msg):
    msg=msg.strip().lower()
    if "@" in msg and "." in msg.split("@")[-1] and len(msg)>5: return True,msg
    return False,None

def detectar_produtos(msg):
    ml=msg.lower()
    enc=[]
    mapa={"1":["1","cartão","cartao","visita","tag","cartões","cartoes"],
          "2":["2","pasta","bolsa","orelha"],
          "3":["3","envelope","ofício","oficio","saco"],
          "4":["4","timbrado","receituário","receituario"],
          "5":["5","papelaria completa","kit completo","completa"]}
    for num,pals in mapa.items():
        for p in pals:
            if p in ml and num not in enc:
                enc.append(num); break
    if "5" in enc and any(x in enc for x in ITENS_KIT):
        return ["5"]
    return enc

def media_produto(num, material, qtd):
    p=PRODUTOS.get(num)
    if not p or not p["medias"]: return 0
    med=p["medias"]
    faixas=sorted([int(k) for k in med.keys()])
    qs=str(faixas[0])
    for f in faixas:
        if qtd>=f: qs=str(f)
    m=(material or "").lower()
    if "couche" in m or "couchê" in m: t="essencial"
    elif "black" in m or "notturno" in m: t="luxo_black"
    elif "white" in m or "rives" in m: t="luxo_white"
    elif "450" in m or "prestigio" in m: t="prestigio"
    else: t="luxo_white"
    return med.get(qs,{}).get(t,0)

def interp_qtd(msg):
    msg=msg.strip()
    mapa={"1":"menos","2":250,"3":500,"4":1000,"5":"mais"}
    if msg in mapa:
        v=mapa[msg]
        if v in ("menos","mais"): return v,None
        return True,v
    try:
        n=int("".join(filter(str.isdigit,msg)))
        if n>0: return True,n
    except: pass
    return False,None

def calcular_total(produtos_lista, material, qtd, valor_criacao=0):
    linhas=[]; total=0
    for p in produtos_lista:
        if p in PRODUTOS:
            qtd_p=max(qtd, PRODUTOS[p]["minimo"])
            v=media_produto(p, material, qtd_p)
            if v>0:
                linhas.append(f"• {PRODUTOS[p]['nome']}: {fmt(v)}")
                total+=v
    if valor_criacao>0:
        linhas.append(f"• Criação de arte: {fmt(valor_criacao)}")
        total+=valor_criacao
    return linhas, total

def menu_qtd():
    return "1. Menos de 250\n2. 250 unidades\n3. 500 unidades\n4. 1.000 unidades\n5. Mais de 1.000"

def menu_produtos():
    return ("Pode escolher mais de uma opção:\n\n"
            "1. Cartão de Visita / TAG\n"
            "2. Pasta com bolsa ou orelha\n"
            "3. Envelope Ofício / Saco\n"
            "4. Papel Timbrado / Receituário\n"
            "5. Papelaria Completa")

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

def processar_mensagem(numero, mensagem):
    sessao=get_sessao(numero)
    etapa=sessao["etapa"]
    dados=sessao["dados"]
    msg=mensagem.strip()
    ml=msg.lower()
    resposta=""
    handoff_data=None
    tent=sessao.get("tentativas",0)

    if etapa=="abertura":
        resposta=var(
            "Olá! Seja muito bem-vindo(a) à Primyn. 😃\n\n"
            "Sou a Mily, consultora virtual da Primyn. Vou entender melhor o que você "
            "procura para direcionar seu atendimento da forma mais estratégica possível — "
            "e, ao final, um especialista dará continuidade ao seu projeto para garantir "
            "que cada detalhe fique exatamente como você deseja.\n\n"
            "É a sua primeira vez conosco, você já é cliente ou já estava falando conosco anteriormente?",
            "Olá! Que bom ter você por aqui. 😃\n\n"
            "Sou a Mily, consultora virtual da Primyn, e vou te acompanhar neste "
            "primeiro atendimento para entender o seu projeto com mais precisão. "
            "Ao final, um especialista dará continuidade para garantir que cada detalhe "
            "fique exatamente como você deseja.\n\n"
            "É a sua primeira vez conosco, você já é cliente ou já estava falando conosco anteriormente?"
        )
        sessao["etapa"]="triagem_inicial"; sessao["tentativas"]=0

    elif etapa=="triagem_inicial":
        if any(p in ml for p in ["2","já sou","ja sou","cliente","já comprei","ja comprei","sou cliente","já conheço","ja conheco"]):
            dados["tipo_contato"]="cliente_recorrente"; sessao["fluxo"]="cliente_recorrente"
            resposta=var("Que bom te ver de volta! 😃\n\nQual é o seu nome e sobrenome?",
                         "Ótimo ter você de volta! Me diz seu nome e sobrenome.")
            sessao["etapa"]="nome"
        elif any(p in ml for p in ["3","já falei","ja falei","voltei","antes","já conversei","ja conversei","anteriormente"]):
            dados["tipo_contato"]="lead_antigo"; sessao["fluxo"]="lead_antigo"
            resposta=var("Que bom que voltou! 😃\n\nQual é o seu nome e sobrenome?",
                         "Fico feliz que tenha voltado. Me diz seu nome e sobrenome.")
            sessao["etapa"]="nome"
        else:
            dados["tipo_contato"]="novo_lead"; sessao["fluxo"]="novo_lead"
            resposta=var(
                "Que ótimo ter você por aqui! 😃\n\nComo você conheceu a Primyn?\n\n1. Google\n2. Instagram\n3. Indicação",
                "Seja muito bem-vindo(a)! 😃\n\nComo você nos encontrou?\n\n1. Google\n2. Instagram\n3. Indicação"
            )
            sessao["etapa"]="origem"

    elif etapa=="origem":
        if any(p in ml for p in ["1","google"]):
            dados["origem"]="Google"
            resposta="Que ótimo que nos encontrou pelo Google! ✨\n\nQual é o seu nome e sobrenome?"
            sessao["etapa"]="nome"; sessao["tentativas"]=0
        elif any(p in ml for p in ["2","instagram","insta"]):
            dados["origem"]="Instagram"
            resposta="Que ótimo que nos encontrou pelo Instagram! ✨\n\nQual é o seu nome e sobrenome?"
            sessao["etapa"]="nome"; sessao["tentativas"]=0
        elif any(p in ml for p in ["3","indicação","indicacao","indicou","indicado"]):
            dados["origem"]="Indicação"
            resposta="Que incrível! Estamos muito felizes pela indicação. 😃\n\nPoderia nos dizer quem indicou?"
            sessao["etapa"]="origem_indicacao"; sessao["tentativas"]=0
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta="Por favor, escolha:\n\n1. Google\n2. Instagram\n3. Indicação"

    elif etapa=="origem_indicacao":
        dados["indicado_por"]=msg
        resposta="Que atencioso! Vamos agradecer por você. 🤍\n\nQual é o seu nome e sobrenome?"
        sessao["etapa"]="nome"; sessao["tentativas"]=0

    elif etapa=="nome":
        valido,nome_fmt=val_nome(msg)
        if not valido:
            tent+=1
            if tent>=3:
                nome_fmt=msg.strip().title(); dados["nome"]=nome_fmt
                primeiro=nome_fmt.split()[0]; sessao["tentativas"]=0
                if sessao.get("fluxo")=="cliente_recorrente":
                    sessao["etapa"]="produto"
                    resposta=f"Prazer, {primeiro}! Me conta: qual material você gostaria de produzir?\n\n"+menu_produtos()
                else:
                    sessao["etapa"]="email"
                    resposta=f"Prazer, {primeiro}! Qual é o seu melhor e-mail para envio da proposta?"
            else:
                sessao["tentativas"]=tent
                resposta="Pode me dizer seu nome e sobrenome?"
        else:
            dados["nome"]=nome_fmt; primeiro=nome_fmt.split()[0]; sessao["tentativas"]=0
            fluxo=sessao.get("fluxo")
            if fluxo=="cliente_recorrente":
                resposta=var(
                    f"Que prazer, {primeiro}! Já te localizo aqui no sistema. 😃\n\nMe conta: qual material você gostaria de produzir?\n\n"+menu_produtos(),
                    f"Que bom ter você de volta, {primeiro}! Qual projeto você gostaria de produzir? 😃\n\n"+menu_produtos()
                )
                sessao["etapa"]="produto"
            elif fluxo=="lead_antigo":
                resposta=var(
                    f"Encontrei seu histórico, {primeiro}! Como prefere prosseguir?\n\n1. Retomar projeto anterior\n2. Começar projeto novo",
                    f"Ótimo, {primeiro}! Retomamos o projeto anterior ou começa algo novo?\n\n1. Retomar projeto anterior\n2. Começar projeto novo"
                )
                sessao["etapa"]="retomar_ou_novo"
            else:
                resposta=var(
                    f"Prazer, {primeiro}! Qual é o seu melhor e-mail para envio da proposta?",
                    f"Que bom, {primeiro}! Para que sua proposta chegue certinha, qual e-mail prefere usar?"
                )
                sessao["etapa"]="email"

    elif etapa=="email":
        valido,email_fmt=val_email(msg)
        primeiro=dados.get("nome","").split()[0]
        if not valido:
            tent+=1
            if tent>=3:
                dados["email"]=""; sessao["tentativas"]=0; sessao["etapa"]="produto"
                resposta=f"Sem problema! Seguiremos sem o e-mail por enquanto.\n\nQual projeto você gostaria de produzir, {primeiro}?\n\n"+menu_produtos()
            else:
                sessao["tentativas"]=tent
                resposta="Esse e-mail não parece válido. Pode me passar seu endereço completo? Ex: seunome@gmail.com"
        else:
            dados["email"]=email_fmt; sessao["tentativas"]=0
            resposta=var(
                f"Maravilha, {primeiro}! Qual projeto você gostaria de produzir? ✨\n\n"+menu_produtos(),
                f"{ac()}, {primeiro}! Me conta: qual projeto você gostaria de produzir?\n\n"+menu_produtos()
            )
            sessao["etapa"]="produto"

    elif etapa=="retomar_ou_novo":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","retomar","anterior","mesmo","continuar"]):
            resposta=("Incrível! Vou te encaminhar para um especialista que dará continuidade ao seu atendimento, "
                      "com opção de reunião estratégica, caso preferir. 🚀")
            dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados
        else:
            sessao["fluxo"]="novo_lead"
            resposta=f"Que bom! Me conta: qual projeto você gostaria de produzir, {primeiro}? ✨\n\n"+menu_produtos()
            sessao["etapa"]="produto"

    elif etapa=="produto":
        primeiro=dados.get("nome","").split()[0]
        prods=detectar_produtos(msg)
        if not prods:
            tent+=1; sessao["tentativas"]=tent
            resposta="Por favor, escolha uma ou mais opções:\n\n"+menu_produtos()
        else:
            sessao["tentativas"]=0
            outros=[p for p in prods if p!="5"]
            if not outros and "5" in prods:
                dados["produto_num"]="5"; dados["produto"]=PRODUTOS["5"]["nome"]
                dados["produtos_lista"]=["5"]; dados["upsell_feito"]=True
                resposta=(f"Papelaria completa é um projeto especial, {primeiro}. 👑\n\n"
                          "O kit inclui cartão de visita, papel timbrado, pasta e envelope "
                          "com a mesma identidade visual — coerência e sofisticação em cada ponto de contato.\n\n"
                          "Faz sentido prosseguirmos com uma proposta personalizada?\n\n"
                          "1. Sim, quero a proposta\n2. Prefiro pensar um pouco mais")
                sessao["etapa"]="papelaria_completa_confirma"
            else:
                if not outros: outros=prods
                dados["produtos_lista"]=outros; dados["produto_atual_idx"]=0
                dados["produto_num"]=outros[0]; dados["produto"]=PRODUTOS[outros[0]]["nome"]
                dados["upsell_feito"]=False
                if outros[0]=="1" and len(outros)==1 and not dados.get("upsell_feito"):
                    dados["upsell_feito"]=True
                    resposta=(f"Ótima escolha! 🤩\n\n"
                              "Além do cartão, você sabia que a papelaria completa — cartão, timbrado, "
                              "pasta e envelope com a mesma identidade — multiplica a percepção de valor "
                              "da sua marca e posiciona você como referência no seu segmento?\n\n"
                              "Gostaria de conhecer essa opção ou prefere seguir só com o cartão?\n\n"
                              "1. Quero conhecer a papelaria completa\n2. Seguir com o cartão de visita")
                    sessao["etapa"]="upsell_resposta"
                else:
                    if len(outros)>1:
                        nomes=[PRODUTOS[p]["nome"] for p in outros]
                        lista="\n".join([f"• {n}" for n in nomes])
                        intro=f"Ótima escolha! 🤩 Vamos trabalhar nos seguintes projetos:\n\n{lista}\n\n"
                    else:
                        intro="Ótima escolha! 🤩\n\n"
                    resposta=(f"{intro}Em qual área você atua?\n\n"
                              "1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n"
                              "4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro")
                    sessao["etapa"]="area"

    elif etapa=="upsell_resposta":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","quero","sim","papelaria","completa","kit","conhecer"]):
            dados["produto_num"]="5"; dados["produto"]=PRODUTOS["5"]["nome"]
            dados["produtos_lista"]=["5"]
            resposta=(f"Que decisão incrível, {primeiro}! 👑\n\n"
                      "O kit inclui cartão de visita, papel timbrado, pasta e envelope "
                      "com a mesma identidade visual.\n\n"
                      "Faz sentido prosseguirmos com uma proposta personalizada?\n\n"
                      "1. Sim, quero a proposta\n2. Prefiro pensar um pouco mais")
            sessao["etapa"]="papelaria_completa_confirma"
        else:
            dados["produtos_lista"]=["1"]; dados["produto_num"]="1"
            resposta=("Sem problema! Vamos seguir com o cartão. ✨\n\nEm qual área você atua?\n\n"
                      "1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n"
                      "4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro")
            sessao["etapa"]="area"

    elif etapa=="papelaria_completa_confirma":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","quero","pode","vamos"]):
            resposta=("Incrível! Vou te encaminhar para um especialista que dará continuidade ao seu atendimento, "
                      "com opção de reunião estratégica, caso preferir. 🚀")
            dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados
        else:
            resposta=f"Claro, {primeiro}! Sem pressa. Quando quiser retomar, estaremos por aqui. 😃"
            dados["status"]="aguardando_resposta"; sessao["etapa"]="encerrado"

    elif etapa=="area":
        opcao=None
        for k,v in AREAS.items():
            if k in msg or any(p in ml for p in v.lower().split(" / ")):
                opcao=k; break
        primeiro=dados.get("nome","").split()[0]
        if not opcao:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha:\n\n1. Advocacia / Direito\n2. Arquitetura / Engenharia\n"
                      "3. Medicina / Saúde\n4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro")
        else:
            dados["area"]=AREAS[opcao]
            dados["papel_recomendado"]=PAPEIS_AREA.get(opcao,"Conqueror Bamboo 400g ou Notturno Black 450g")
            sessao["tentativas"]=0
            resposta=(f"{TRANS_AREA.get(opcao,'')} ✨\n\n"
                      "Os papéis mais solicitados são o Conqueror Bamboo 400g e o Notturno Black 450g — "
                      "ambos transmitem sofisticação desde o primeiro toque.\n\n"
                      "Você já possui a arte ou tem alguma referência visual para nos enviar?\n\n"
                      "1. Sim, já tenho arte pronta\n"
                      "2. Não, mas tenho referência")
            sessao["etapa"]="arte"

    elif etapa=="arte":
        if any(p in ml for p in ["1","já tenho","ja tenho","tenho arte","pronta","finalizada"]):
            dados["arte"]="pronta"
            resposta=var("Ótimo! Pode me enviar sua arte? Assim consigo direcionar sua cotação.",
                         "Perfeito! Me encaminha a arte final quando puder.")
            sessao["etapa"]="arte_recebida"
        elif any(p in ml for p in ["2","não","nao","referência","referencia"]):
            dados["arte"]="referencia"
            resposta=var("Sem problema! Pode me enviar a referência para orçamento?",
                         "Claro! Me manda a referência visual que você tem em mente.")
            sessao["etapa"]="referencia_recebida"
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta="Por favor, escolha:\n\n1. Sim, já tenho arte pronta\n2. Não, mas tenho referência"

    elif etapa=="arte_recebida":
        dados["arte_enviada"]=True
        resposta=("Recebi! Agora vamos ao material. ✨\n\n"
                  "Qual tipo de papel faz mais sentido para o seu projeto?\n\n"
                  "1. Couchê 300g\n2. Texturado até 400g\n3. Texturado acima de 400g\n\n"
                  "Catálogo de papéis: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
                  "Nossos projetos: https://www.instagram.com/primyn.store/")
        sessao["etapa"]="papel"

    elif etapa=="referencia_recebida":
        dados["referencia_enviada"]=True
        produto_num=dados.get("produto_num","1")
        aceita_3d=PRODUTOS.get(produto_num,{}).get("aceita_3d",False)
        if aceita_3d:
            resposta=("Recebi a referência! Você vai precisar de criação de arte?\n\n"
                      "1. Sim — Criação de arte — R$ 74,90\n"
                      "2. Sim — Criação de arte + amostra 3D — R$ 220,00\n"
                      "3. Quero identidade visual / logomarca\n"
                      "4. Não, vou seguir com a referência")
        else:
            resposta=("Recebi a referência! Você vai precisar de criação de arte?\n\n"
                      "1. Sim — Criação de arte — R$ 74,90\n"
                      "2. Quero identidade visual / logomarca\n"
                      "3. Não, vou seguir com a referência")
        sessao["etapa"]="criacao_pos_ref"

    elif etapa=="criacao_pos_ref":
        produto_num=dados.get("produto_num","1")
        aceita_3d=PRODUTOS.get(produto_num,{}).get("aceita_3d",False)
        primeiro=dados.get("nome","").split()[0]
        id_visual=(any(p in ml for p in ["identidade","logo","logomarca"]) or
                   (aceita_3d and "3" in msg) or (not aceita_3d and "2" in msg))
        _3d=("2" in msg and aceita_3d) or "3d" in ml or "220" in msg
        nao_precisa=(any(p in ml for p in ["não","nao","seguir","referência"]) or
                     ("4" in msg and aceita_3d) or ("3" in msg and not aceita_3d))
        if id_visual:
            dados["criacao"]="identidade_visual"; dados["valor_criacao"]=0
            resposta=("Identidade visual é um projeto especial — vou acionar nossa designer Ane. 👑\n\n"
                      "Enquanto isso, gostaria de seguir com a cotação do material usando a referência enviada?\n\n"
                      "1. Sim, quero seguir com a cotação\n2. Não, prefiro aguardar a identidade visual")
            sessao["etapa"]="identidade_continuar"
        elif _3d and aceita_3d:
            dados["criacao"]="criacao_arte_3d"; dados["valor_criacao"]=220.0
            resposta=("Ótima escolha! A amostra 3D vai te dar uma visão incrível do resultado final. 🤩\n\n"
                      "Qual tipo de papel faz mais sentido?\n\n"
                      "1. Couchê 300g\n2. Texturado até 400g\n3. Texturado acima de 400g\n\n"
                      "Catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
                      "Projetos: https://www.instagram.com/primyn.store/")
            sessao["etapa"]="papel"
        elif nao_precisa:
            dados["criacao"]="sem_criacao"; dados["valor_criacao"]=0
            resposta=("Qual tipo de papel faz mais sentido?\n\n"
                      "1. Couchê 300g\n2. Texturado até 400g\n3. Texturado acima de 400g\n\n"
                      "Catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas")
            sessao["etapa"]="papel"
        else:
            dados["criacao"]="criacao_simples"; dados["valor_criacao"]=74.90
            resposta=("Qual tipo de papel faz mais sentido?\n\n"
                      "1. Couchê 300g\n2. Texturado até 400g\n3. Texturado acima de 400g\n\n"
                      "Catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas")
            sessao["etapa"]="papel"

    elif etapa=="identidade_continuar":
        if any(p in ml for p in ["1","sim","quero","seguir"]):
            resposta=("Qual tipo de papel faz mais sentido?\n\n"
                      "1. Couchê 300g\n2. Texturado até 400g\n3. Texturado acima de 400g\n\n"
                      "Catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas")
            sessao["etapa"]="papel"
        else:
            primeiro=dados.get("nome","").split()[0]
            dados["status"]="handoff_designer"
            resposta=(f"Claro, {primeiro}! Nossa designer Ane entrará em contato em breve.\n\n"
                      "Incrível! Vou te encaminhar para um especialista que dará continuidade. 🚀")
            sessao["etapa"]="handoff"; handoff_data=dados

    elif etapa=="papel":
        if any(p in ml for p in ["1","couche","couchê","300"]):
            dados["material"]="Couchê 300g"
            resposta=("O Couchê 300g é nossa opção de entrada — para refletir o padrão Primyn, "
                      "trabalhamos obrigatoriamente com hot stamping ou relevo. "
                      "Sem acabamento premium, ele se torna um cartão comum.\n\n"
                      "Qual acabamento faz mais sentido?\n\n"
                      "1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n\n"
                      "Ou prefere explorar nossos papéis texturados?\n4. Ver catálogo de texturas")
            sessao["etapa"]="papel_couche_acab"
        elif any(p in ml for p in ["2","até 400","ate 400","texturado até","texturado ate"]):
            resposta=("Veja nosso catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                      "Os mais vendidos são o Conqueror Bamboo 400g e o Notturno Black 450g.\n\n"
                      "Qual você prefere?\n\nProjetos: https://www.instagram.com/primyn.store/")
            sessao["etapa"]="papel_tex_escolha"
        elif any(p in ml for p in ["3","acima","450","texturado acima"]):
            resposta=("Veja nosso catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                      "Os mais vendidos acima de 400g são o Notturno Black 450g e o Rives White 400g.\n\n"
                      "Qual você prefere?\n\nProjetos: https://www.instagram.com/primyn.store/")
            sessao["etapa"]="papel_tex_escolha"
        else:
            dados["material"]=msg
            resposta=("Você já conhece nossos acabamentos premium, como relevo, hot stamp e borda sanduíche?\n\n"
                      "1. Sim, já conheço\n2. Não, gostaria de conhecer")
            sessao["etapa"]="acab_conhece"

    elif etapa=="papel_couche_acab":
        if any(p in ml for p in ["4","catálogo","catalogo","texturado","textura","explorar"]):
            resposta=("Veja nosso catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                      "Os mais vendidos são o Conqueror Bamboo 400g e o Notturno Black 450g.\n\n"
                      "Qual você prefere? Projetos: https://www.instagram.com/primyn.store/")
            sessao["etapa"]="papel_tex_escolha"
        elif any(p in ml for p in ["sem","não quero","nao quero","nenhum"]):
            resposta="Entendemos. Quando quiser explorar uma proposta premium, estaremos por aqui. 😃"
            dados["status"]="fora_escopo"; sessao["etapa"]="encerrado"
        else:
            am={"1":"Hot stamping","2":"Alto relevo seco","3":"Baixo relevo"}
            acab=None
            for k,v in am.items():
                if k in msg or v.lower() in ml: acab=v; break
            if acab:
                dados["acabamento"]=acab
                resposta=f"Qual quantidade você está considerando?\n\n{menu_qtd()}"
                sessao["etapa"]="quantidade"
            else:
                resposta="Por favor, escolha:\n\n1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n4. Ver catálogo de texturas"

    elif etapa=="papel_tex_escolha":
        if len(msg.strip())<2:
            resposta="Pode me dizer qual papel você escolheu?"
        else:
            dados["material"]=msg
            resposta=("Você já conhece nossos acabamentos premium, como relevo, hot stamp e borda sanduíche?\n\n"
                      "1. Sim, já conheço\n2. Não, gostaria de conhecer")
            sessao["etapa"]="acab_conhece"

    elif etapa=="acab_conhece":
        if any(p in ml for p in ["1","sim","já conheço","ja conheco","conheço","conheco"]):
            resposta=("Qual acabamento faz mais sentido para a sua marca?\n\n"
                      "1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n"
                      "4. Empastamento / borda sanduíche\n5. Impressão colorida no papel especial\n"
                      "6. Combinação de acabamentos\n\n"
                      "Veja nossos projetos: https://www.instagram.com/primyn.store/")
        else:
            resposta=("Trabalhamos com os seguintes acabamentos premium:\n\n"
                      "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                      "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                      "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                      "4. Empastamento / borda sanduíche — https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n"
                      "5. Impressão colorida no papel especial\n6. Combinação de acabamentos\n\n"
                      "Projetos: https://www.instagram.com/primyn.store/\n\nQual faz mais sentido para a sua marca?")
        sessao["etapa"]="acabamento"

    elif etapa=="acabamento":
        am={"1":"Hot stamping","2":"Alto relevo seco","3":"Baixo relevo",
            "4":"Empastamento / borda sanduíche","5":"Impressão colorida","6":"Combinação de acabamentos"}
        opcao=None
        for k,v in am.items():
            pals=v.lower().replace(" / "," ").split()
            if k in msg or any(p in ml for p in pals if len(p)>3): opcao=k; break
        if not opcao:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha:\n\n1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n"
                      "4. Empastamento / borda sanduíche\n5. Impressão colorida\n6. Combinação de acabamentos")
        else:
            dados["acabamento"]=am[opcao]; sessao["tentativas"]=0
            if opcao=="4":
                resposta=("O empastamento tem três finalidades: 💎\n\n"
                          "1. Papel mais grosso — mais espessura e rigidez\n"
                          "2. Evitar marcação do relevo — impede que apareça no lado oposto\n"
                          "3. Borda sanduíche — interior colorido revelado ao olhar a borda\n\n"
                          "Saiba mais: https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n\n"
                          "Qual dessas finalidades faz mais sentido?")
                sessao["etapa"]="empastamento_det"
            else:
                resposta=f"Qual quantidade você está considerando?\n\n{menu_qtd()}"
                sessao["etapa"]="quantidade"

    elif etapa=="empastamento_det":
        dados["empastamento_tipo"]=msg
        resposta=f"Qual quantidade você está considerando?\n\n{menu_qtd()}"
        sessao["etapa"]="quantidade"

    elif etapa=="quantidade":
        primeiro=dados.get("nome","").split()[0]
        produtos_lista=dados.get("produtos_lista",["1"])
        resultado,qtd=interp_qtd(msg)
        if resultado=="menos":
            minimo=min(PRODUTOS[p]["minimo"] for p in produtos_lista if p in PRODUTOS)
            resposta=(f"Nossa quantidade mínima é {minimo} unidades. Qual quantidade você gostaria?\n\n"
                      f"2. 250 unidades\n3. 500 unidades\n4. 1.000 unidades\n5. Mais de 1.000")
        elif resultado=="mais":
            resposta="Qual é a quantidade exata que você deseja?"
            sessao["etapa"]="quantidade_exata"
        elif not resultado:
            tent+=1; sessao["tentativas"]=tent
            resposta=f"Por favor, escolha uma das opções:\n\n{menu_qtd()}"
        else:
            sessao["tentativas"]=0
            avisos=[]
            for p in produtos_lista:
                if p in PRODUTOS and qtd<PRODUTOS[p]["minimo"]:
                    avisos.append(f"• {PRODUTOS[p]['nome']}: mínimo {PRODUTOS[p]['minimo']} un.")
            dados["quantidade"]=qtd
            material=dados.get("material","")
            vc=dados.get("valor_criacao",0)
            linhas,total=calcular_total(produtos_lista,material,qtd,vc)
            dados["media"]=total
            aviso_txt=("Atenção nos mínimos:\n"+"\n".join(avisos)+"\n\n") if avisos else ""
            if total==0:
                resposta=(f"{aviso_txt}Para essa composição, o investimento é definido sob consulta.\n\n"
                          "Faz sentido prosseguirmos?\n\n1. Sim, quero a proposta\n2. Preciso pensar\n3. Não, obrigada")
            else:
                det="\n".join(linhas)
                resposta=(f"{aviso_txt}Para a configuração que você me passou: 👑\n\n"
                          f"{det}\n\nTotal estimado: {fmt(total)}\n\n"
                          "Esse valor é uma referência — o orçamento final é personalizado.\n\n"
                          "Faz sentido prosseguirmos com uma proposta personalizada?\n\n"
                          "1. Sim, quero a proposta\n2. Preciso pensar\n3. Não, obrigada")
            sessao["etapa"]="media_proposta"

    elif etapa=="quantidade_exata":
        try:
            qtd=int("".join(filter(str.isdigit,msg)))
            if qtd>0:
                dados["quantidade"]=qtd
                produtos_lista=dados.get("produtos_lista",["1"])
                material=dados.get("material","")
                vc=dados.get("valor_criacao",0)
                linhas,total=calcular_total(produtos_lista,material,qtd,vc)
                dados["media"]=total
                det="\n".join(linhas)
                resposta=(f"Para a configuração que você me passou: 👑\n\n{det}\n\nTotal estimado: {fmt(total)}\n\n"
                          "Esse valor é uma referência — o orçamento final é personalizado.\n\n"
                          "Faz sentido prosseguirmos?\n\n1. Sim, quero a proposta\n2. Preciso pensar\n3. Não, obrigada")
                sessao["etapa"]="media_proposta"
            else:
                resposta="Por favor, informe uma quantidade válida."
        except:
            resposta="Por favor, informe a quantidade em números. Ex: 1500"

    elif etapa=="media_proposta":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","quero","pode","vamos","claro"]):
            resposta=var(f"Maravilha! 😁 Você tem algum prazo ou data importante para receber esse material?",
                         f"Ótimo, {primeiro}! 😁 Existe algum prazo importante que eu deva considerar?")
            sessao["etapa"]="urgencia"
        elif any(p in ml for p in ["2","pensar","depois","calma","talvez"]):
            resposta=var("Claro! Sem pressa. Quando quiser retomar, estaremos por aqui.\n\nAcompanhe em @primyn.store",
                         f"Sem problema, {primeiro}. Quando quiser retomar, será um prazer continuar.")
            dados["status"]="aguardando_resposta"; sessao["etapa"]="encerrado"
            try:
                from followup import agendar_followup
                agendar_followup(numero,dados.get("nome",""),"pensar",dias=2)
            except: pass
        else:
            resposta=var(f"Sem problemas, {primeiro}! Agradeço pelo seu tempo. Fico à disposição.",
                         "Claro! Obrigada pelo contato. Quando quiser, será um prazer te atender.")
            dados["status"]="perdido"; sessao["etapa"]="encerrado"

    elif etapa=="urgencia":
        dados["urgencia"]=msg; primeiro=dados.get("nome","").split()[0]
        urgente=any(p in ml for p in ["urgente","rápido","rapido","pressa","amanhã","amanha","semana","logo","dias"])
        aviso=("Projetos com criação e produção premium têm prazo médio de 7 a 10 dias úteis. "
               "Vou sinalizar no seu direcionamento.\n\n") if urgente else ""
        resposta=(f"{aviso}Incrível! Vou te encaminhar para um especialista que dará continuidade ao seu atendimento, "
                  "com opção de reunião estratégica, caso preferir, para garantir que tudo esteja perfeito "
                  "antes de elaborar a proposta exclusiva para o seu projeto. 🚀")
        dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados

    elif etapa=="handoff":
        primeiro=dados.get("nome","").split()[0]
        resposta=(f"Antes de encerrar, {primeiro}, como foi sua experiência com este atendimento?\n\n"
                  "1. Ótimo\n2. Bom\n3. Ruim")
        sessao["etapa"]="feedback"

    elif etapa=="feedback":
        avals={"1":"Ótimo","2":"Bom","3":"Ruim"}
        av=avals.get(msg.strip(),msg); dados["avaliacao"]=av
        primeiro=dados.get("nome","").split()[0]
        if msg.strip()=="3" or "ruim" in ml:
            resposta=f"Obrigada pelo retorno, {primeiro}. Vamos usar esse feedback para melhorar. 🤍"
        else:
            resposta=f"Que bom, {primeiro}! Foi um prazer te atender. Até breve! 🤍"
        sessao["etapa"]="encerrado"

    elif etapa=="encerrado":
        primeiro=dados.get("nome","").split()[0] if dados.get("nome") else ""
        resposta=(f"Olá, {primeiro}! Quer retomar seu projeto ou precisa de algo mais? 😃"
                  if primeiro else "Olá! Seja muito bem-vindo(a) de volta à Primyn. Como posso te ajudar? 😃")
        sessao["etapa"]="produto"

    else:
        resposta="Olá! Seja muito bem-vindo(a) à Primyn. 😃\n\nSou a Mily. Como posso te ajudar?"
        sessao["etapa"]="triagem_inicial"

    sessao["dados"]=dados
    upd_sessao(numero,sessao)
    return resposta,handoff_data
# Alias para compatibilidade com app.py
carregar_sessoes = load
