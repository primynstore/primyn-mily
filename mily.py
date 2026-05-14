
import json, os, random
from datetime import datetime

DB_FILE = "sessoes.json"

PRODUTOS = {
    "1": {"nome":"Cartão de Visita / TAG","minimo":250,"aceita_3d":True,
          "papeis":["Couchê 300g","Conqueror Bamboo 120g","Conqueror Bamboo 250g","Conqueror Bamboo 400g",
                    "Rives Tradition White 120g","Rives Tradition White 250g","Rives Tradition White 400g",
                    "Rives Tradition Natural 120g","Rives Tradition Natural 250g","Rives Tradition Natural 400g",
                    "Notturno Black 450g","Dark Blue 450g","Kraft Natural 300g"],
          "medias":{"250":{"essencial":378,"luxo_black":562,"luxo_white":898,"prestigio":1297},
                    "500":{"essencial":475,"luxo_black":839,"luxo_white":1284,"prestigio":1682},
                    "1000":{"essencial":588,"luxo_black":1184,"luxo_white":1568,"prestigio":2567},
                    "2000":{"essencial":780,"luxo_black":1580,"luxo_white":2100,"prestigio":3200}}},
    "2": {"nome":"Pasta com bolsa ou orelha","minimo":100,"aceita_3d":False,
          "papeis":["Couchê 300g com laminação fosca","Notturno Black 450g",
                    "Conqueror Bamboo 400g","Rives Tradition White 400g","Rives Tradition Natural 400g"],
          "medias":{"100":{"essencial":1250,"luxo_black":1250,"luxo_white":1250,"prestigio":1250},
                    "250":{"essencial":2200,"luxo_black":2200,"luxo_white":2200,"prestigio":2200},
                    "500":{"essencial":3500,"luxo_black":3500,"luxo_white":3500,"prestigio":3500},
                    "2000":None}},
    "3": {"nome":"Envelope Ofício / Saco","minimo":100,"aceita_3d":False,
          "papeis":["Offset 180g","Conqueror Bamboo 120g","Rives Tradition White 120g",
                    "Rives Tradition Natural 120g","Color Plus 180g (diversas cores)"],
          "medias":{"100":{"essencial":620,"luxo_black":620,"luxo_white":620,"prestigio":620},
                    "250":{"essencial":890,"luxo_black":890,"luxo_white":890,"prestigio":890},
                    "500":{"essencial":1290,"luxo_black":1290,"luxo_white":1290,"prestigio":1290},
                    "2000":None}},
    "4": {"nome":"Papel Timbrado / Receituário","minimo":250,"aceita_3d":False,
          "papeis":["Offset 120g","Offset 180g","Conqueror Bamboo 120g",
                    "Rives Tradition White 120g","Rives Tradition Natural 120g","Color Plus 120g"],
          "medias":{"250":{"essencial":290,"luxo_black":290,"luxo_white":290,"prestigio":290},
                    "500":{"essencial":490,"luxo_black":490,"luxo_white":490,"prestigio":490},
                    "1000":{"essencial":790,"luxo_black":790,"luxo_white":790,"prestigio":790},
                    "2000":None}},
    "5": {"nome":"Papelaria Completa","minimo":250,"aceita_3d":False,
          "papeis":[],
          "medias":{"250":{"essencial":4200,"luxo_black":4200,"luxo_white":5800,"prestigio":5800},
                    "500":{"essencial":5800,"luxo_black":5800,"luxo_white":7500,"prestigio":7500},
                    "2000":None}}
}

ITENS_KIT = {"1","2","3","4"}

AREAS = {"1":"Advocacia / Direito","2":"Arquitetura / Engenharia","3":"Medicina / Saúde",
         "4":"Moda / Beleza / Lifestyle","5":"Finanças / Executivo","6":"Outro"}

PAPEIS_AREA = {
    "1":"Notturno Black 450g, Dark Blue 450g ou Rives Tradition White 400g",
    "2":"Rives Tradition Natural 400g ou Conqueror Bamboo 400g",
    "3":"Rives Tradition White 400g ou Conqueror Bamboo 400g",
    "4":"Color Plus ou Rives Tradition White 400g",
    "5":"Notturno Black 450g, Dark Blue 450g ou Rives Tradition White 400g",
    "6":"Conqueror Bamboo 400g ou Notturno Black 450g"
}

TRANS_AREA = {
    "1":"Advocacia — precisão e autoridade refletidas em cada detalhe.",
    "2":"Arquitetura — sofisticação que comunica antes mesmo das palavras.",
    "3":"Medicina — onde confiança e credibilidade se traduzem em cada peça.",
    "4":"Moda e beleza — estética e identidade que falam por si.",
    "5":"Finanças — onde a percepção de solidez faz toda a diferença.",
    "6":"Cada área tem sua identidade. Vamos encontrar o material que melhor representa a sua."
}

MSG_EDUCATIVA = (
    "Antes de encaminhar, quero compartilhar um pensamento:\n\n"
    "Materiais de papelaria premium não são apenas papel — são o primeiro toque físico "
    "que o seu cliente tem com a sua marca. Um cartão com textura e acabamento em "
    "hot stamping ou baixo relevo transmite sofisticação antes mesmo de qualquer palavra. "
    "Estudos mostram que materiais de alta qualidade aumentam em até 3x a percepção de valor. "
    "Você não entrega um cartão — você entrega uma experiência. 👑\n\n"
    "Sua marca merece deixar essa impressão. 🤍"
)

ACOLH = ["Com certeza,","Entendido,","Anotado,","Perfeito,","Ótimo,","Que bom,"]
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
    parts=msg.split("@")
    if len(parts)==2 and "." in parts[1] and len(parts[1].split(".")[-1])>=2 and len(parts[0])>0:
        return True,msg
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
    val=med.get(qs)
    if val is None: return -1  # acima do limite
    m=(material or "").lower()
    if "couche" in m or "couchê" in m or "offset" in m or "color plus" in m: t="essencial"
    elif "black" in m or "notturno" in m or "dark blue" in m: t="luxo_black"
    elif "rives" in m or "conqueror" in m: t="luxo_white"
    else: t="luxo_white"
    return val.get(t,list(val.values())[0]) if val else 0

def calcular_total(produtos_lista, material, qtd, valor_criacao=0):
    linhas=[]; total=0; acima_limite=False
    for p in produtos_lista:
        if p in PRODUTOS:
            qtd_p=max(qtd, PRODUTOS[p]["minimo"])
            v=media_produto(p, material, qtd_p)
            if v==-1:
                acima_limite=True
            elif v>0:
                linhas.append(f"• {PRODUTOS[p]['nome']}: {fmt(v)}")
                total+=v
    if valor_criacao>0:
        linhas.append(f"• Criação de arte: {fmt(valor_criacao)}")
        total+=valor_criacao
    return linhas, total, acima_limite

def interp_qtd(msg):
    msg=msg.strip()
    mapa={"1":"menos","2":250,"3":500,"4":1000,"5":2000,"6":"acima"}
    if msg in mapa:
        v=mapa[msg]
        if v in ("menos","acima"): return v,None
        return True,v
    try:
        n=int("".join(filter(str.isdigit,msg)))
        if n>0:
            if n>2000: return "acima",None
            if n<100: return "menos",None
            return True,n
    except: pass
    return False,None

def menu_qtd(minimo=100):
    opcoes=[]
    if minimo<=250: opcoes.append("1. Menos de 250")
    opcoes.append("2. 250 unidades")
    opcoes.append("3. 500 unidades")
    opcoes.append("4. 1.000 unidades")
    opcoes.append("5. 2.000 unidades")
    opcoes.append("6. Acima de 2.000")
    return "\n".join(opcoes)

def menu_produtos():
    return ("Pode digitar o número da opção ou o nome do material:\n\n"
            "1. Cartão de Visita / TAG\n"
            "2. Pasta com bolsa ou orelha\n"
            "3. Envelope Ofício / Saco\n"
            "4. Papel Timbrado / Receituário\n"
            "5. Papelaria Completa")

def papeis_do_produto(produto_num):
    p=PRODUTOS.get(produto_num,{})
    papeis=p.get("papeis",[])
    if not papeis: return ""
    return "Os papéis disponíveis para esse material são:\n" + "\n".join(f"• {pp}" for pp in papeis)

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

    # ABERTURA
    if etapa=="abertura":
        resposta=var(
            "Olá! Seja muito bem-vindo(a) à Primyn. 😃\n\n"
            "Sou a Mily, consultora virtual da Primyn. Estou aqui para entender o seu projeto "
            "e direcionar seu atendimento da forma mais estratégica possível. "
            "Ao final, um especialista dará continuidade para garantir que cada detalhe "
            "fique exatamente como você imagina.\n\n"
            "Antes de começarmos: essa é a sua primeira vez conosco, você já é cliente "
            "ou já esteve em contato com a Primyn anteriormente?\n\n"
            "💡 Você pode digitar apenas o número da opção:\n"
            "1. Primeira vez\n2. Já sou cliente\n3. Já falei com vocês antes",

            "Olá! Que bom ter você por aqui. 😃\n\n"
            "Sou a Mily, consultora virtual da Primyn, e vou te acompanhar neste "
            "primeiro atendimento para entender o seu projeto com mais precisão. "
            "Ao final, um especialista assume para garantir que tudo fique perfeito.\n\n"
            "Para começarmos — você pode digitar o número:\n\n"
            "1. Primeira vez na Primyn\n2. Já sou cliente\n3. Já conversei com vocês antes"
        )
        sessao["etapa"]="triagem_inicial"; sessao["tentativas"]=0

    # TRIAGEM
    elif etapa=="triagem_inicial":
        if any(p in ml for p in ["2","já sou","ja sou","cliente","já comprei","ja comprei","sou cliente","já conheço","ja conheco"]):
            dados["tipo_contato"]="cliente_recorrente"; sessao["fluxo"]="cliente_recorrente"
            resposta=var("Que bom te ver de volta! 😃\n\nPode me informar seu nome e sobrenome?",
                         "Uma alegria ter você de volta! 😃\n\nSeu nome e sobrenome, por favor.")
            sessao["etapa"]="nome"
        elif any(p in ml for p in ["3","já falei","ja falei","voltei","antes","já conversei","ja conversei","anteriormente"]):
            dados["tipo_contato"]="lead_antigo"; sessao["fluxo"]="lead_antigo"
            resposta=var("Olá! Fico feliz que tenha voltado. 😃\n\nPode me dizer seu nome e sobrenome?",
                         "Que bom! 😃 Me diz seu nome e sobrenome para eu continuar seu atendimento.")
            sessao["etapa"]="nome"
        else:
            dados["tipo_contato"]="novo_lead"; sessao["fluxo"]="novo_lead"
            resposta=var(
                "Seja muito bem-vindo(a) à Primyn! 😃\n\nComo você conheceu a Primyn?\n\n1. Google\n2. Instagram\n3. Indicação",
                "Que prazer receber você! 😃\n\nComo chegou até nós?\n\n1. Google\n2. Instagram\n3. Indicação"
            )
            sessao["etapa"]="origem"

    # ORIGEM
    elif etapa=="origem":
        if any(p in ml for p in ["1","google"]):
            dados["origem"]="Google"
            resposta="Que ótimo que nos encontrou pelo Google! ✨\n\nPode me dizer seu nome e sobrenome?"
            sessao["etapa"]="nome"; sessao["tentativas"]=0
        elif any(p in ml for p in ["2","instagram","insta"]):
            dados["origem"]="Instagram"
            resposta="Que bom que nos encontrou pelo Instagram! ✨\n\nPode me dizer seu nome e sobrenome?"
            sessao["etapa"]="nome"; sessao["tentativas"]=0
        elif any(p in ml for p in ["3","indicação","indicacao","indicou","indicado"]):
            dados["origem"]="Indicação"
            resposta="Que incrível! Ficamos muito felizes com a indicação. 😃\n\nPoderia nos dizer quem indicou?"
            sessao["etapa"]="origem_indicacao"; sessao["tentativas"]=0
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta="Por favor, escolha uma das opções:\n\n1. Google\n2. Instagram\n3. Indicação"

    # ORIGEM INDICAÇÃO
    elif etapa=="origem_indicacao":
        dados["indicado_por"]=msg
        resposta="Obrigada! Vamos agradecer especialmente por você. 🤍\n\nPode me dizer seu nome e sobrenome?"
        sessao["etapa"]="nome"; sessao["tentativas"]=0

    # NOME
    elif etapa=="nome":
        valido,nome_fmt=val_nome(msg)
        if not valido:
            tent+=1
            if tent>=3:
                nome_fmt=msg.strip().title(); dados["nome"]=nome_fmt
                primeiro=nome_fmt.split()[0]; sessao["tentativas"]=0
                fluxo=sessao.get("fluxo")
                if fluxo=="cliente_recorrente":
                    sessao["etapa"]="produto"
                    resposta=(f"Olá, {primeiro}! Como posso te ajudar hoje?\n\n"+menu_produtos())
                else:
                    sessao["etapa"]="email"
                    resposta=f"Prazer, {primeiro}! Qual é o seu melhor e-mail para envio da proposta?"
            else:
                sessao["tentativas"]=tent
                resposta="Precisaria do seu nome e sobrenome completos para continuar. Como posso te chamar?"
        else:
            dados["nome"]=nome_fmt; primeiro=nome_fmt.split()[0]; sessao["tentativas"]=0
            fluxo=sessao.get("fluxo")
            if fluxo=="cliente_recorrente":
                resposta=var(
                    f"Que prazer, {primeiro}! Já te localizo aqui. 😃\n\nQual material você gostaria de produzir desta vez?\n\n"+menu_produtos(),
                    f"Olá, {primeiro}! Feliz em te atender novamente. 😃\n\nQual projeto você traz pra gente hoje?\n\n"+menu_produtos()
                )
                sessao["etapa"]="produto"
            elif fluxo=="lead_antigo":
                resposta=var(
                    f"Olá, {primeiro}! Como posso te ajudar hoje?\n\n1. Retomar um projeto anterior\n2. Começar algo novo",
                    f"Que bom, {primeiro}! O que posso fazer por você?\n\n1. Retomar um projeto anterior\n2. Começar algo novo"
                )
                sessao["etapa"]="retomar_ou_novo"
            else:
                resposta=var(
                    f"Prazer, {primeiro}! Qual é o seu melhor e-mail para envio da proposta?",
                    f"Muito bom ter você aqui, {primeiro}! Para onde envio a proposta? Pode me passar seu e-mail?"
                )
                sessao["etapa"]="email"

    # EMAIL
    elif etapa=="email":
        valido,email_fmt=val_email(msg)
        primeiro=dados.get("nome","").split()[0]
        if not valido:
            tent+=1
            if tent>=3:
                dados["email"]=""; sessao["tentativas"]=0; sessao["etapa"]="produto"
                resposta=(f"Sem problema, {primeiro}! Podemos seguir sem o e-mail por agora.\n\n"
                          f"Qual projeto você gostaria de produzir?\n\n"+menu_produtos())
            else:
                sessao["tentativas"]=tent
                resposta=("Esse e-mail não parece estar completo. "
                          "Pode conferir e me enviar novamente? Ex: seunome@gmail.com")
        else:
            dados["email"]=email_fmt; sessao["tentativas"]=0
            resposta=var(
                f"Perfeito, {primeiro}! Qual projeto você gostaria de produzir?\n\n"+menu_produtos(),
                f"Anotado, {primeiro}! Me conta agora: o que você gostaria de produzir?\n\n"+menu_produtos()
            )
            sessao["etapa"]="produto"

    # RETOMAR OU NOVO
    elif etapa=="retomar_ou_novo":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","retomar","anterior","mesmo","continuar"]):
            resposta=(f"Com prazer! Vou encaminhar você para um especialista que dará continuidade "
                      f"ao seu atendimento, com opção de reunião estratégica, se preferir. 🚀")
            dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados
        else:
            sessao["fluxo"]="novo_lead"
            resposta=(f"Ótimo, vamos começar! O que você gostaria de produzir, {primeiro}?\n\n"+menu_produtos())
            sessao["etapa"]="produto"

    # PRODUTO
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
                resposta=(f"A papelaria completa é um projeto muito especial, {primeiro}. 👑\n\n"
                          f"O kit reúne cartão de visita, papel timbrado, pasta e envelope "
                          f"com a mesma identidade visual — criando coerência e sofisticação "
                          f"em cada ponto de contato da sua marca.\n\n"
                          f"Gostaria de prosseguir com uma proposta personalizada?\n\n"
                          f"1. Sim, quero a proposta\n2. Prefiro pensar um pouco mais")
                sessao["etapa"]="papelaria_completa_confirma"
            else:
                if not outros: outros=prods
                dados["produtos_lista"]=outros; dados["produto_atual_idx"]=0
                dados["produto_num"]=outros[0]; dados["produto"]=PRODUTOS[outros[0]]["nome"]
                dados["upsell_feito"]=False
                if outros[0]=="1" and len(outros)==1 and not dados.get("upsell_feito"):
                    dados["upsell_feito"]=True
                    resposta=(f"Ótima escolha! ✨\n\n"
                              f"Antes de seguirmos — sabia que clientes que investem em papelaria completa "
                              f"(cartão, timbrado, pasta e envelope com a mesma identidade) multiplicam "
                              f"a percepção de valor da marca e se tornam referência no seu segmento?\n\n"
                              f"Gostaria de conhecer essa opção ou prefere seguir só com o cartão?\n\n"
                              f"1. Quero conhecer a papelaria completa\n2. Seguir com o cartão de visita")
                    sessao["etapa"]="upsell_resposta"
                else:
                    if len(outros)>1:
                        nomes=[PRODUTOS[p]["nome"] for p in outros]
                        lista="\n".join([f"• {n}" for n in nomes])
                        intro=f"Ótima escolha! Vamos trabalhar nos seguintes projetos:\n\n{lista}\n\n"
                    else:
                        intro="Ótima escolha! ✨\n\n"
                    resposta=(f"{intro}Em qual área você atua?\n\n"
                              "1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n"
                              "4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro")
                    sessao["etapa"]="area"

    # UPSELL
    elif etapa=="upsell_resposta":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","quero","sim","papelaria","completa","kit","conhecer"]):
            dados["produto_num"]="5"; dados["produto"]=PRODUTOS["5"]["nome"]
            dados["produtos_lista"]=["5"]
            resposta=(f"Que escolha incrível, {primeiro}! 👑\n\n"
                      f"O kit reúne cartão de visita, papel timbrado, pasta e envelope — "
                      f"todos com a mesma identidade visual.\n\n"
                      f"Gostaria de prosseguir com uma proposta personalizada?\n\n"
                      f"1. Sim, quero a proposta\n2. Prefiro pensar um pouco mais")
            sessao["etapa"]="papelaria_completa_confirma"
        else:
            dados["produtos_lista"]=["1"]; dados["produto_num"]="1"
            resposta=("Perfeito! Vamos seguir com o cartão. ✨\n\nEm qual área você atua?\n\n"
                      "1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n"
                      "4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro")
            sessao["etapa"]="area"

    # PAPELARIA COMPLETA CONFIRMA
    elif etapa=="papelaria_completa_confirma":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","quero","pode","vamos"]):
            resposta=("Com prazer! Vou encaminhar você para um especialista que dará continuidade "
                      "ao seu atendimento, com opção de reunião estratégica, se preferir. 🚀")
            dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados
        else:
            resposta=f"Sem pressa, {primeiro}. Quando quiser retomar, estamos por aqui. 😊"
            dados["status"]="aguardando_resposta"; sessao["etapa"]="encerrado"

    # ÁREA
    elif etapa=="area":
        opcao=None
        for k,v in AREAS.items():
            if k in msg or any(p in ml for p in v.lower().split(" / ")):
                opcao=k; break
        if not opcao:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n"
                      "4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro")
        else:
            dados["area"]=AREAS[opcao]
            dados["papel_recomendado"]=PAPEIS_AREA.get(opcao,"")
            sessao["tentativas"]=0
            resposta=(f"{TRANS_AREA.get(opcao,'')} ✨\n\n"
                      f"Os papéis mais escolhidos pelos nossos clientes para essa área são "
                      f"o Conqueror Bamboo 400g e o Notturno Black 450g — "
                      f"ambos transmitem sofisticação desde o primeiro toque.\n\n"
                      f"Você já tem a arte finalizada ou possui alguma referência visual?\n\n"
                      f"1. Sim, já tenho arte pronta\n"
                      f"2. Sim, tenho referência")
            sessao["etapa"]="arte"

    # ARTE
    elif etapa=="arte":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","já tenho","ja tenho","tenho arte","pronta","finalizada"]):
            dados["arte"]="pronta"
            resposta=var(
                "Ótimo! E qual tipo de papel você está considerando para o seu projeto?\n\n"+
                papeis_do_produto(dados.get("produto_num","1"))+
                "\n\nSe quiser explorar as opções, veja nosso catálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
                "E para se inspirar nos nossos projetos: https://www.instagram.com/primyn.store/",

                "Perfeito! Vamos ao material.\n\n"+
                papeis_do_produto(dados.get("produto_num","1"))+
                "\n\nNosso catálogo completo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
                "Projetos no Instagram: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"]="papel_escolha"
        elif any(p in ml for p in ["2","sim","referência","referencia","tenho ref","ref"]):
            dados["arte"]="referencia"
            resposta=var(
                "Que bom! Pode nos enviar quando quiser — não há pressa. 😊\n\n"
                "Se precisar de inspiração antes, temos projetos lindos no Instagram: "
                "https://www.instagram.com/primyn.store/\n\n"
                "Enquanto isso, vamos ao material. Qual papel você está considerando?\n\n"+
                papeis_do_produto(dados.get("produto_num","1"))+
                "\n\nCatálogo completo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas",

                "Com certeza! Pode mandar quando estiver pronta — a referência nos ajuda muito a afinar a proposta. 😊\n\n"
                "Enquanto isso, qual papel você imagina para esse projeto?\n\n"+
                papeis_do_produto(dados.get("produto_num","1"))+
                "\n\nInspire-se nos nossos projetos: https://www.instagram.com/primyn.store/"
            )
            sessao["etapa"]="papel_escolha"
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Sim, já tenho arte pronta\n"
                      "2. Sim, tenho referência")

    # PAPEL ESCOLHA (após confirmar arte)
    elif etapa=="papel_escolha":
        primeiro=dados.get("nome","").split()[0]
        produto_num=dados.get("produto_num","1")
        papeis=PRODUTOS.get(produto_num,{}).get("papeis",[])

        # Detectar se escolheu papel da lista ou pediu ajuda
        if any(p in ml for p in ["não sei","nao sei","ajuda","sugestão","sugestao","indica","qual"]):
            papel_rec=dados.get("papel_recomendado","Conqueror Bamboo 400g")
            resposta=(f"Para a sua área, costumamos recomendar {papel_rec}. "
                      f"São papéis que transmitem sofisticação desde o toque. ✨\n\n"
                      f"Veja o catálogo completo para se inspirar:\n"
                      f"https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                      f"Quando decidir, me conta qual papel escolheu!")
        else:
            # Aceita qualquer resposta como escolha de papel
            if len(msg.strip())<2:
                resposta="Pode me dizer qual papel você escolheu?"
            else:
                dados["material"]=msg
                sessao["tentativas"]=0

                # Verificar se é Couchê (só para produtos que aceitam)
                if ("couche" in ml or "couchê" in ml) and produto_num in ["1","2"]:
                    resposta=(f"O Couchê 300g é nossa opção de entrada — e, para manter o padrão Primyn, "
                              f"trabalhamos obrigatoriamente com hot stamping ou relevo. "
                              f"Sem um acabamento premium, ele perde a sofisticação que sua marca merece.\n\n"
                              f"Qual acabamento faz mais sentido para você?\n\n"
                              f"1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n\n"
                              f"Ou prefere explorar nossos papéis especiais?\n4. Ver catálogo de texturas")
                    sessao["etapa"]="papel_couche_acab"
                else:
                    resposta=("Você já conhece nossos acabamentos, como relevo, hot stamping e borda sanduíche?\n\n"
                              "1. Sim, já conheço\n2. Não, gostaria de conhecer")
                    sessao["etapa"]="acab_conhece"

    # REFERÊNCIA RECEBIDA (após confirmar que tem referência e perguntar papel)
    elif etapa=="referencia_recebida":
        dados["referencia_enviada"]=True
        produto_num=dados.get("produto_num","1")
        aceita_3d=PRODUTOS.get(produto_num,{}).get("aceita_3d",False)
        if aceita_3d:
            resposta=("Recebemos! Com base na referência, você precisará de criação de arte?\n\n"
                      "1. Sim — Criação de arte — R$ 74,90\n"
                      "2. Sim — Criação de arte + amostra 3D — R$ 220,00\n"
                      "3. Não, vou fazer em outro lugar")
        else:
            resposta=("Recebemos! Você precisará de criação de arte?\n\n"
                      "1. Sim — Criação de arte — R$ 74,90\n"
                      "2. Não, vou fazer em outro lugar")
        sessao["etapa"]="criacao_pos_ref"

    # CRIAÇÃO PÓS REFERÊNCIA
    elif etapa=="criacao_pos_ref":
        produto_num=dados.get("produto_num","1")
        aceita_3d=PRODUTOS.get(produto_num,{}).get("aceita_3d",False)
        primeiro=dados.get("nome","").split()[0]
        id_visual=any(p in ml for p in ["identidade","logo","logomarca"])
        _3d=("2" in msg and aceita_3d) or "3d" in ml or "220" in msg
        nao_precisa=(any(p in ml for p in ["3","não","nao","outro lugar","outro"]) and not _3d and not id_visual)

        if id_visual:
            dados["criacao"]="identidade_visual"; dados["valor_criacao"]=0
            resposta=("Identidade visual é um projeto muito especial — vou acionar nossa designer Ane. 👑\n\n"
                      "Enquanto isso, gostaria de seguir com a cotação do material?\n\n"
                      "1. Sim, vamos continuar\n2. Não, prefiro aguardar a identidade visual")
            sessao["etapa"]="identidade_continuar"
        elif _3d and aceita_3d:
            dados["criacao"]="criacao_arte_3d"; dados["valor_criacao"]=220.0
            resposta=("Ótima escolha! A amostra 3D vai te dar uma visão real do resultado final. 🤩\n\n"
                      "Agora, qual papel você imagina para esse projeto?\n\n"+
                      papeis_do_produto(produto_num)+
                      "\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas")
            sessao["etapa"]="papel_escolha"
        elif nao_precisa or ("1" not in msg and not _3d):
            dados["criacao"]="sem_criacao"; dados["valor_criacao"]=0
            resposta=("Entendido! Qual papel você imagina para esse projeto?\n\n"+
                      papeis_do_produto(produto_num)+
                      "\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas")
            sessao["etapa"]="papel_escolha"
        else:
            dados["criacao"]="criacao_simples"; dados["valor_criacao"]=74.90
            resposta=("Perfeito! Qual papel você imagina para esse projeto?\n\n"+
                      papeis_do_produto(produto_num)+
                      "\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas")
            sessao["etapa"]="papel_escolha"

    # IDENTIDADE CONTINUAR
    elif etapa=="identidade_continuar":
        if any(p in ml for p in ["1","sim","quero","seguir","continuar"]):
            produto_num=dados.get("produto_num","1")
            resposta=("Qual papel você imagina para esse projeto?\n\n"+
                      papeis_do_produto(produto_num)+
                      "\n\nCatálogo: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas")
            sessao["etapa"]="papel_escolha"
        else:
            primeiro=dados.get("nome","").split()[0]
            dados["status"]="handoff_designer"
            resposta=(f"Com prazer! Nossa designer Ane entrará em contato em breve, {primeiro}. 🤍\n\n"
                      f"Vou encaminhar para um especialista que dará sequência ao seu atendimento. 🚀")
            sessao["etapa"]="handoff"; handoff_data=dados

    # PAPEL COUCHÊ ACABAMENTO
    elif etapa=="papel_couche_acab":
        if any(p in ml for p in ["4","catálogo","catalogo","texturado","textura","explorar","especial"]):
            produto_num=dados.get("produto_num","1")
            resposta=("Com prazer! Veja nosso catálogo completo de papéis:\n"
                      "https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                      "Os mais escolhidos pelos nossos clientes são o Conqueror Bamboo 400g "
                      "e o Notturno Black 450g — sofisticação desde o primeiro toque. ✨\n\n"
                      "E para se inspirar nos nossos projetos:\n"
                      "https://www.instagram.com/primyn.store/\n\n"
                      "Quando decidir, me conta qual papel você escolheu!")
            sessao["etapa"]="papel_escolha"
        elif any(p in ml for p in ["sem","não quero","nao quero","nenhum"]):
            primeiro=dados.get("nome","").split()[0]
            resposta=(f"Entendemos, {primeiro}. Quando quiser explorar uma proposta "
                      f"alinhada ao padrão Primyn, estaremos aqui com prazer. 😊")
            dados["status"]="fora_escopo"; sessao["etapa"]="encerrado"
        else:
            am={"1":"Hot stamping","2":"Alto relevo seco","3":"Baixo relevo"}
            acab=None
            for k,v in am.items():
                if k in msg or v.lower() in ml: acab=v; break
            if acab:
                dados["acabamento"]=acab
                resposta=(f"Qual quantidade você está considerando?\n\n{menu_qtd(PRODUTOS.get(dados.get('produto_num','1'),{}).get('minimo',100))}")
                sessao["etapa"]="quantidade"
            else:
                resposta="Por favor, escolha:\n\n1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n4. Ver catálogo de texturas"

    # ACABAMENTO CONHECE
    elif etapa=="acab_conhece":
        if any(p in ml for p in ["1","sim","já conheço","ja conheco","conheço","conheco"]):
            resposta=("Qual acabamento faz mais sentido para a sua marca?\n\n"
                      "1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n"
                      "4. Empastamento / borda sanduíche\n5. Impressão colorida no papel especial\n"
                      "6. Combinação de acabamentos\n\n"
                      "Inspire-se nos nossos projetos: https://www.instagram.com/primyn.store/")
        else:
            resposta=("Saiba mais sobre cada acabamento clicando nos links abaixo. "
                      "E se quiser ver projetos reais, conheça nosso Instagram! 😊\n\n"
                      "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                      "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                      "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                      "4. Empastamento / borda sanduíche — https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n"
                      "5. Impressão colorida no papel especial\n"
                      "6. Combinação de acabamentos\n\n"
                      "📸 Nossos projetos: https://www.instagram.com/primyn.store/\n\n"
                      "Qual deles conversa melhor com a identidade da sua marca?")
        sessao["etapa"]="acabamento"

    # ACABAMENTO
    elif etapa=="acabamento":
        am={"1":"Hot stamping","2":"Alto relevo seco","3":"Baixo relevo",
            "4":"Empastamento / borda sanduíche","5":"Impressão colorida","6":"Combinação de acabamentos"}
        opcao=None
        for k,v in am.items():
            pals=v.lower().replace(" / "," ").split()
            if k in msg or any(p in ml for p in pals if len(p)>3): opcao=k; break
        if not opcao:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n"
                      "4. Empastamento / borda sanduíche\n5. Impressão colorida\n6. Combinação")
        else:
            dados["acabamento"]=am[opcao]; sessao["tentativas"]=0
            if opcao=="4":
                resposta=("O empastamento tem três finalidades possíveis: 💎\n\n"
                          "1. Papel mais grosso — mais espessura e rigidez ao cartão\n"
                          "2. Evitar a marcação do relevo — impede que apareça no verso\n"
                          "3. Borda sanduíche — interior colorido revelado ao olhar a borda\n\n"
                          "Saiba mais: https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n\n"
                          "Qual dessas finalidades faz mais sentido para o seu projeto?")
                sessao["etapa"]="empastamento_det"
            else:
                produto_num=dados.get("produto_num","1")
                minimo=PRODUTOS.get(produto_num,{}).get("minimo",100)
                resposta=f"Qual quantidade você está considerando?\n\n{menu_qtd(minimo)}"
                sessao["etapa"]="quantidade"

    # EMPASTAMENTO DETALHE
    elif etapa=="empastamento_det":
        dados["empastamento_tipo"]=msg
        produto_num=dados.get("produto_num","1")
        minimo=PRODUTOS.get(produto_num,{}).get("minimo",100)
        resposta=f"Qual quantidade você está considerando?\n\n{menu_qtd(minimo)}"
        sessao["etapa"]="quantidade"

    # QUANTIDADE
    elif etapa=="quantidade":
        primeiro=dados.get("nome","").split()[0]
        produtos_lista=dados.get("produtos_lista",["1"])
        resultado,qtd=interp_qtd(msg)
        minimo=min(PRODUTOS[p]["minimo"] for p in produtos_lista if p in PRODUTOS)

        if resultado=="menos":
            resposta=(f"Nossa quantidade mínima é {minimo} unidades. "
                      f"Qual opção se encaixa melhor no seu projeto?\n\n"
                      f"2. 250 unidades\n3. 500 unidades\n4. 1.000 unidades\n5. 2.000 unidades\n6. Acima de 2.000")
        elif resultado=="acima":
            resposta=("Para volumes acima de 2.000 unidades, preparamos uma proposta personalizada "
                      "com condições especiais. Vou encaminhar você para um especialista! 🚀\n\n"
                      "Pode me confirmar a quantidade aproximada?")
            dados["quantidade_acima"]=True
            dados["status"]="handoff_premium"
            sessao["etapa"]="handoff"
            handoff_data=dados
        elif not resultado:
            tent+=1; sessao["tentativas"]=tent
            resposta=f"Por favor, escolha uma das opções:\n\n{menu_qtd(minimo)}"
        else:
            sessao["tentativas"]=0
            avisos=[]
            for p in produtos_lista:
                if p in PRODUTOS and qtd<PRODUTOS[p]["minimo"]:
                    avisos.append(f"• {PRODUTOS[p]['nome']}: mínimo {PRODUTOS[p]['minimo']} un.")
            dados["quantidade"]=qtd
            material=dados.get("material","")
            vc=dados.get("valor_criacao",0)
            linhas,total,acima_lim=calcular_total(produtos_lista,material,qtd,vc)
            dados["media"]=total
            aviso_txt=("Atenção nos mínimos:\n"+"\n".join(avisos)+"\n\n") if avisos else ""
            if acima_lim or total==0:
                resposta=(f"{aviso_txt}Para essa composição, o investimento é definido sob consulta.\n\n"
                          "Vou encaminhar para um especialista preparar a proposta ideal.\n\n"
                          "1. Sim, quero a proposta\n2. Preciso pensar\n3. Não, obrigada")
            else:
                det="\n".join(linhas)
                resposta=(f"{aviso_txt}Para a configuração que você me passou: 👑\n\n"
                          f"{det}\n\nTotal estimado: {fmt(total)}\n\n"
                          "Esse valor é uma referência — o orçamento final é personalizado "
                          "conforme acabamento, criação e complexidade.\n\n"
                          "Faz sentido prosseguirmos com uma proposta personalizada?\n\n"
                          "1. Sim, quero a proposta\n2. Preciso pensar\n3. Não, obrigada")
            sessao["etapa"]="media_proposta"

    # MEDIA PROPOSTA
    elif etapa=="media_proposta":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","quero","pode","vamos","claro"]):
            resposta=var(f"Que ótimo! 😁 Você tem algum prazo ou data importante para receber esse material?",
                         f"Maravilha, {primeiro}! 😁 Existe algum prazo que eu deva considerar na proposta?")
            sessao["etapa"]="urgencia"
        elif any(p in ml for p in ["2","pensar","depois","calma","talvez"]):
            resposta=var("Claro! Sem qualquer pressa. Quando quiser retomar, estaremos aqui. 😊\n\nAcompanhe nossos projetos em @primyn.store",
                         f"Com certeza, {primeiro}. Essas decisões merecem calma. Quando quiser continuar, é só chamar. 😊")
            dados["status"]="aguardando_resposta"; sessao["etapa"]="encerrado"
            try:
                from followup import agendar_followup
                agendar_followup(numero,dados.get("nome",""),"pensar",dias=2)
            except: pass
        else:
            resposta=var(f"Sem problema algum, {primeiro}. Fico à disposição sempre que quiser retomar. 😊",
                         "Entendido! Quando quiser explorar uma proposta com a Primyn, será um prazer. 😊")
            dados["status"]="perdido"; sessao["etapa"]="encerrado"

    # URGÊNCIA
    elif etapa=="urgencia":
        dados["urgencia"]=msg; primeiro=dados.get("nome","").split()[0]
        urgente=any(p in ml for p in ["urgente","rápido","rapido","pressa","amanhã","amanha","semana","logo","dias"])
        aviso=("Projetos com criação e produção premium têm prazo médio de 7 a 10 dias úteis. "
               "Vou sinalizar a urgência no encaminhamento. 🚀\n\n") if urgente else ""
        resposta=(f"{aviso}"
                  f"{MSG_EDUCATIVA}\n\n"
                  f"Vou encaminhar você para um especialista que dará continuidade ao seu atendimento, "
                  f"com opção de reunião estratégica, se preferir. 🚀")
        dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados

    # HANDOFF
    elif etapa=="handoff":
        primeiro=dados.get("nome","").split()[0]
        resposta=(f"Antes de encerrar, {primeiro} — como foi a sua experiência com este atendimento?\n\n"
                  "1. Ótimo\n2. Bom\n3. Precisa melhorar")
        sessao["etapa"]="feedback"

    # FEEDBACK
    elif etapa=="feedback":
        avals={"1":"Ótimo","2":"Bom","3":"Precisa melhorar"}
        av=avals.get(msg.strip(),msg); dados["avaliacao"]=av
        primeiro=dados.get("nome","").split()[0]
        if msg.strip()=="3" or "melhorar" in ml or "ruim" in ml:
            resposta=f"Obrigada pelo retorno honesto, {primeiro}. Cada feedback nos ajuda a evoluir. 🤍"
        else:
            resposta=f"Que bom, {primeiro}! Foi um prazer te atender. Até breve! 🤍"
        sessao["etapa"]="encerrado"

    # ENCERRADO
    elif etapa=="encerrado":
        primeiro=dados.get("nome","").split()[0] if dados.get("nome") else ""
        if primeiro:
            resposta=f"Olá, {primeiro}! Como posso te ajudar? 😊"
        else:
            resposta="Olá! Seja muito bem-vindo(a) à Primyn. Como posso te ajudar? 😊"
        sessao["etapa"]="produto" if primeiro else "triagem_inicial"

    else:
        resposta="Olá! Seja muito bem-vindo(a) à Primyn. 😃\n\nSou a Mily. Como posso te ajudar?"
        sessao["etapa"]="triagem_inicial"

    sessao["dados"]=dados
    upd_sessao(numero,sessao)
    return resposta,handoff_data
    carregar_sessoes = load
