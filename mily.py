
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
                    "500":{"essencial":3500,"luxo_black":3500,"luxo_white":3500,"prestigio":3500}}},
    "3": {"nome":"Envelope Ofício / Saco","minimo":100,"aceita_3d":False,
          "papeis":["Offset 180g","Conqueror Bamboo 120g",
                    "Rives Tradition White 120g","Rives Tradition Natural 120g",
                    "Color Plus 180g (diversas cores)"],
          "medias":{"100":{"essencial":620,"luxo_black":620,"luxo_white":620,"prestigio":620},
                    "250":{"essencial":890,"luxo_black":890,"luxo_white":890,"prestigio":890},
                    "500":{"essencial":1290,"luxo_black":1290,"luxo_white":1290,"prestigio":1290}}},
    "4": {"nome":"Papel Timbrado / Receituário","minimo":100,"aceita_3d":False,
          "papeis":["Offset 120g","Offset 180g","Conqueror Bamboo 120g",
                    "Rives Tradition White 120g","Rives Tradition Natural 120g","Color Plus 120g"],
          "medias":{"100":{"essencial":290,"luxo_black":290,"luxo_white":290,"prestigio":290},
                    "250":{"essencial":490,"luxo_black":490,"luxo_white":490,"prestigio":490},
                    "500":{"essencial":790,"luxo_black":790,"luxo_white":790,"prestigio":790},
                    "1000":{"essencial":1190,"luxo_black":1190,"luxo_white":1190,"prestigio":1190}}},
    "5": {"nome":"Papelaria Completa","minimo":250,"aceita_3d":False,
          "papeis":[],
          "medias":{"250":{"essencial":4200,"luxo_black":4200,"luxo_white":5800,"prestigio":5800},
                    "500":{"essencial":5800,"luxo_black":5800,"luxo_white":7500,"prestigio":7500}}}
}

ITENS_KIT = {"1","2","3","4"}

AREAS = {"1":"Advocacia / Direito","2":"Arquitetura / Engenharia","3":"Medicina / Saúde",
         "4":"Moda / Beleza / Lifestyle","5":"Finanças / Executivo","6":"Outro"}

PAPEIS_AREA = {
    "1":"Notturno Black 450g, Dark Blue 450g ou Rives Tradition White 400g",
    "2":"Rives Tradition Natural 400g ou Conqueror Bamboo 400g",
    "3":"Rives Tradition White 400g ou Conqueror Bamboo 400g",
    "4":"Color Plus ou Rives Tradition White 400g",
    "5":"Notturno Black 450g ou Rives Tradition White 400g",
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
    if val is None: return -1
    m=(material or "").lower()
    if "couche" in m or "couchê" in m or "offset" in m or "color plus" in m: t="essencial"
    elif "black" in m or "notturno" in m or "dark blue" in m: t="luxo_black"
    elif "rives" in m or "conqueror" in m: t="luxo_white"
    else: t="luxo_white"
    return val.get(t, list(val.values())[0]) if val else 0

def calcular_total(produtos_lista, material, qtd, valor_criacao=0):
    linhas=[]; total=0; acima_lim=False
    for p in produtos_lista:
        if p in PRODUTOS:
            qtd_p=max(qtd, PRODUTOS[p]["minimo"])
            v=media_produto(p, material, qtd_p)
            if v==-1: acima_lim=True
            elif v>0:
                linhas.append(f"• {PRODUTOS[p]['nome']}: {fmt(v)}")
                total+=v
    if valor_criacao>0:
        linhas.append(f"• Criação de arte: {fmt(valor_criacao)}")
        total+=valor_criacao
    return linhas, total, acima_lim

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
            return True,n
    except: pass
    return False,None

def menu_qtd(minimo=100):
    linhas=[]
    if minimo<=250: linhas.append("1. Menos de 250")
    linhas += ["2. 250 unidades","3. 500 unidades","4. 1.000 unidades","5. 2.000 unidades","6. Acima de 2.000"]
    return "\n".join(linhas)

def menu_produtos():
    return ("Pode escolher mais de uma opção — e se quiser praticidade, basta digitar o número:\n\n"
            "1. Cartão de Visita / TAG\n"
            "2. Pasta com bolsa ou orelha\n"
            "3. Envelope Ofício / Saco\n"
            "4. Papel Timbrado / Receituário\n"
            "5. Papelaria Completa")

def papeis_do_produto(produto_num):
    p=PRODUTOS.get(produto_num,{})
    papeis=p.get("papeis",[])
    if not papeis: return ""
    return "Papéis disponíveis para esse material:\n" + "\n".join(f"• {pp}" for pp in papeis)

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

    AREAS_MENU = ("1. Advocacia / Direito\n2. Arquitetura / Engenharia\n3. Medicina / Saúde\n"
                  "4. Moda / Beleza / Lifestyle\n5. Finanças / Executivo\n6. Outro")

    def hdoff():
        return ("Vou te encaminhar agora para um especialista que dará continuidade ao seu atendimento, "
                "com opção de reunião estratégica, se preferir. 🚀")

    if etapa=="abertura":
        resposta=var(
            "Olá! É um prazer enorme ter você aqui. 😊\n\n"
            "Eu sou a Mily, consultora da Primyn — estou aqui para entender o seu projeto "
            "com toda a atenção que ele merece. Ao final, um especialista garante que "
            "cada detalhe fique exatamente como você imagina.\n\n"
            "Antes de começarmos: é a sua primeira vez conosco, você já é cliente "
            "ou já esteve em contato com a gente anteriormente?\n\n"
            "1. Primeira vez\n2. Já sou cliente\n3. Já conversei com vocês antes",

            "Olá! Que bom receber você por aqui. 😊\n\n"
            "Sou a Mily, da Primyn, e estou aqui para te orientar com cuidado e atenção. "
            "Ao final, um especialista assume para que tudo saia exatamente como você deseja.\n\n"
            "Para começarmos:\n\n"
            "1. Primeira vez\n2. Já sou cliente\n3. Já conversei com vocês antes"
        )
        sessao["etapa"]="triagem_inicial"; sessao["tentativas"]=0

    elif etapa=="triagem_inicial":
        if any(p in ml for p in ["2","já sou","ja sou","cliente","já comprei","ja comprei","sou cliente","já conheço","ja conheco"]):
            dados["tipo_contato"]="cliente_recorrente"; sessao["fluxo"]="cliente_recorrente"
            resposta=var("Que prazer ter você de volta! 😊\n\nPode me informar seu nome e sobrenome?",
                         "Uma alegria recebê-la novamente! 😊\n\nSeu nome e sobrenome, por favor.")
            sessao["etapa"]="nome"
        elif any(p in ml for p in ["3","já falei","ja falei","voltei","antes","já conversei","ja conversei","anteriormente"]):
            dados["tipo_contato"]="lead_antigo"; sessao["fluxo"]="lead_antigo"
            resposta=var("Olá! Fico feliz que tenha voltado. 😊\n\nPode me dizer seu nome e sobrenome?",
                         "Que bom! Estamos aqui para continuar. 😊\n\nSeu nome e sobrenome, por favor.")
            sessao["etapa"]="nome"
        else:
            dados["tipo_contato"]="novo_lead"; sessao["fluxo"]="novo_lead"
            resposta=var(
                "Seja bem-vindo(a)! 😃\n\nComo você conheceu a Primyn?\n\n1. Google\n2. Instagram\n3. Indicação",
                "Que prazer receber você! 😃\n\nComo chegou até nós?\n\n1. Google\n2. Instagram\n3. Indicação"
            )
            sessao["etapa"]="origem"

    elif etapa=="origem":
        if any(p in ml for p in ["1","google"]):
            dados["origem"]="Google"
            resposta="Que ótimo que nos encontrou por lá! ✨\n\nPode me dizer seu nome e sobrenome?"
            sessao["etapa"]="nome"; sessao["tentativas"]=0
        elif any(p in ml for p in ["2","instagram","insta"]):
            dados["origem"]="Instagram"
            resposta="Fico feliz que tenha nos encontrado pelo Instagram! ✨\n\nPode me dizer seu nome e sobrenome?"
            sessao["etapa"]="nome"; sessao["tentativas"]=0
        elif any(p in ml for p in ["3","indicação","indicacao","indicou","indicado"]):
            dados["origem"]="Indicação"
            resposta="Que honra! Ficamos muito felizes com a indicação. 😊\n\nPoderia nos dizer quem nos indicou?"
            sessao["etapa"]="origem_indicacao"; sessao["tentativas"]=0
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta="Por favor, escolha uma das opções:\n\n1. Google\n2. Instagram\n3. Indicação"

    elif etapa=="origem_indicacao":
        dados["indicado_por"]=msg
        resposta="Obrigada! Vamos agradecer com carinho por você. 🤍\n\nPode me dizer seu nome e sobrenome?"
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
                    resposta=f"Olá, {primeiro}! O que posso fazer por você hoje?\n\n"+menu_produtos()
                else:
                    sessao["etapa"]="email"
                    resposta=f"Prazer, {primeiro}! Qual é o seu melhor e-mail para envio da proposta?"
            else:
                sessao["tentativas"]=tent
                resposta="Para personalizar seu atendimento, precisaria do seu nome e sobrenome. Como posso te chamar?"
        else:
            dados["nome"]=nome_fmt; primeiro=nome_fmt.split()[0]; sessao["tentativas"]=0
            fluxo=sessao.get("fluxo")
            if fluxo=="cliente_recorrente":
                resposta=var(
                    f"Que prazer, {primeiro}! Já te localizo aqui. 😊\n\nQual material você gostaria de produzir desta vez?\n\n"+menu_produtos(),
                    f"Olá, {primeiro}! Uma alegria te atender novamente. 😊\n\nO que você gostaria de produzir hoje?\n\n"+menu_produtos()
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
                    f"Muito bom ter você aqui, {primeiro}! Para onde envio a proposta?"
                )
                sessao["etapa"]="email"

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
                resposta="Esse endereço não parece estar completo. Pode conferir e enviar novamente? Ex: seunome@gmail.com"
        else:
            dados["email"]=email_fmt; sessao["tentativas"]=0
            resposta=var(
                f"Perfeito, {primeiro}! Me conta: o que você gostaria de produzir?\n\n"+menu_produtos(),
                f"Anotado, {primeiro}! Qual projeto você traz para a gente hoje?\n\n"+menu_produtos()
            )
            sessao["etapa"]="produto"

    elif etapa=="retomar_ou_novo":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","retomar","anterior","mesmo","continuar"]):
            resposta=hdoff()
            dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados
        else:
            sessao["fluxo"]="novo_lead"
            resposta=f"Ótimo! O que você gostaria de produzir, {primeiro}?\n\n"+menu_produtos()
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
                dados["produtos_lista"]=["5"]
                resposta=(f"A papelaria completa é um projeto muito especial, {primeiro}. 👑\n\n"
                          "O kit reúne cartão de visita, papel timbrado, pasta e envelope "
                          "com a mesma identidade visual — coerência e sofisticação "
                          "em cada ponto de contato da sua marca.\n\n"
                          "Gostaria de prosseguir com uma proposta personalizada?\n\n"
                          "1. Sim, quero a proposta\n2. Prefiro pensar um pouco mais")
                sessao["etapa"]="papelaria_completa_confirma"
            else:
                if not outros: outros=prods
                dados["produtos_lista"]=outros
                dados["produto_num"]=outros[0]; dados["produto"]=PRODUTOS[outros[0]]["nome"]
                if len(outros)>1:
                    nomes=[PRODUTOS[p]["nome"] for p in outros]
                    lista="\n".join([f"• {n}" for n in nomes])
                    intro=f"Ótima escolha! Vamos trabalhar nesses projetos:\n\n{lista}\n\n"
                else:
                    intro="Ótima escolha! ✨\n\n"
                resposta=(f"{intro}Em qual área você atua?\n\n{AREAS_MENU}")
                sessao["etapa"]="area"

    elif etapa=="papelaria_completa_confirma":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","quero","pode","vamos"]):
            resposta=hdoff()
            dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados
        else:
            resposta=f"Sem pressa, {primeiro}. Quando quiser retomar, estamos aqui. 😊"
            dados["status"]="aguardando_resposta"; sessao["etapa"]="encerrado"

    elif etapa=="area":
        opcao=None
        for k,v in AREAS.items():
            if k in msg or any(p in ml for p in v.lower().split(" / ")):
                opcao=k; break
        if not opcao:
            tent+=1; sessao["tentativas"]=tent
            resposta=f"Por favor, escolha uma das opções:\n\n{AREAS_MENU}"
        else:
            dados["area"]=AREAS[opcao]
            dados["papel_recomendado"]=PAPEIS_AREA.get(opcao,"")
            sessao["tentativas"]=0
            resposta=(f"{TRANS_AREA.get(opcao,'')} ✨\n\n"
                      "Você já tem a arte finalizada ou possui alguma referência visual?\n\n"
                      "1. Sim, já tenho arte pronta\n"
                      "2. Sim, tenho referência")
            sessao["etapa"]="arte"

    elif etapa=="arte":
        produto_num=dados.get("produto_num","1")
        papeis=papeis_do_produto(produto_num)
        cats=("\n\nCatálogo de papéis: https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n"
              "Nossos projetos: https://www.instagram.com/primyn.store/")

        if any(p in ml for p in ["1","já tenho","ja tenho","tenho arte","pronta","finalizada"]):
            dados["arte"]="pronta"
            resposta=var(
                f"Perfeito! Qual papel você está considerando para esse projeto?\n\n{papeis}{cats}",
                f"Ótimo! Vamos ao material.\n\n{papeis}{cats}"
            )
            sessao["etapa"]="papel_escolha"
        elif any(p in ml for p in ["2","sim","referência","referencia","ref"]):
            dados["arte"]="referencia"
            resposta=var(
                f"Que bom! Pode nos enviar quando quiser — sem pressa. 😊\n\n"
                f"Se quiser inspiração antes, temos projetos lindos no Instagram:\nhttps://www.instagram.com/primyn.store/\n\n"
                f"Enquanto isso, qual papel você imagina para esse projeto?\n\n{papeis}{cats}",
                f"Com certeza! A referência nos ajuda muito a afinar a proposta. 😊\n\n"
                f"Qual papel você imagina para esse projeto?\n\n{papeis}{cats}"
            )
            sessao["etapa"]="papel_escolha"
        else:
            tent+=1; sessao["tentativas"]=tent
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Sim, já tenho arte pronta\n2. Sim, tenho referência")

    elif etapa=="papel_escolha":
        produto_num=dados.get("produto_num","1")
        if any(p in ml for p in ["não sei","nao sei","ajuda","sugestão","sugestao","indica","qual"]):
            papel_rec=dados.get("papel_recomendado","Conqueror Bamboo 400g")
            resposta=(f"Para a sua área, costumamos recomendar {papel_rec}. ✨\n\n"
                      "Veja o catálogo para se inspirar:\n"
                      "https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                      "Quando decidir, me conta qual papel você escolheu.")
        elif len(msg.strip())<2:
            resposta="Pode me dizer qual papel você escolheu?"
        else:
            dados["material"]=msg; sessao["tentativas"]=0
            if ("couche" in ml or "couchê" in ml) and produto_num in ["1","2"]:
                resposta=("O Couchê 300g é nossa opção de entrada — e, para manter o padrão Primyn, "
                          "trabalhamos obrigatoriamente com hot stamping ou relevo. "
                          "Sem um acabamento especial, ele perde a sofisticação que sua marca merece.\n\n"
                          "Qual acabamento faz mais sentido para você?\n\n"
                          "1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n\n"
                          "Ou prefere explorar nossos papéis especiais?\n4. Ver catálogo de texturas")
                sessao["etapa"]="papel_couche_acab"
            else:
                resposta=("Você já conhece nossos acabamentos — como relevo, hot stamping e borda sanduíche?\n\n"
                          "1. Sim, já conheço\n2. Não, gostaria de conhecer")
                sessao["etapa"]="acab_conhece"

    elif etapa=="papel_couche_acab":
        if any(p in ml for p in ["4","catálogo","catalogo","texturado","textura","explorar","especial"]):
            resposta=("Com prazer! Veja nosso catálogo completo:\n"
                      "https://www.primyn.com/pagina/tipos-de-papeis-e-texturas\n\n"
                      "Para se inspirar nos nossos projetos:\nhttps://www.instagram.com/primyn.store/\n\n"
                      "Quando decidir, me conta qual papel você escolheu.")
            sessao["etapa"]="papel_escolha"
        elif any(p in ml for p in ["sem","não quero","nao quero","nenhum"]):
            primeiro=dados.get("nome","").split()[0]
            resposta=(f"Entendemos, {primeiro}. Quando quiser explorar uma proposta "
                      "alinhada ao padrão Primyn, estaremos aqui. 😊")
            dados["status"]="fora_escopo"; sessao["etapa"]="encerrado"
        else:
            am={"1":"Hot stamping","2":"Alto relevo seco","3":"Baixo relevo"}
            acab=None
            for k,v in am.items():
                if k in msg or v.lower() in ml: acab=v; break
            if acab:
                dados["acabamento"]=acab
                produto_num=dados.get("produto_num","1")
                minimo=PRODUTOS.get(produto_num,{}).get("minimo",100)
                resposta=f"Qual quantidade você está considerando?\n\n{menu_qtd(minimo)}"
                sessao["etapa"]="quantidade"
            else:
                resposta="Por favor, escolha:\n\n1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n4. Ver catálogo de texturas"

    elif etapa=="acab_conhece":
        if any(p in ml for p in ["1","sim","já conheço","ja conheco","conheço","conheco"]):
            resposta=("Qual acabamento conversa melhor com a identidade da sua marca?\n\n"
                      "1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n"
                      "4. Empastamento / borda sanduíche\n5. Impressão colorida no papel especial\n"
                      "6. Combinação de acabamentos\n\n"
                      "Veja nossos projetos: https://www.instagram.com/primyn.store/")
        else:
            resposta=("Conheça cada acabamento nos links abaixo — e, se quiser ver projetos reais, "
                      "dê uma olhada no nosso Instagram. 😊\n\n"
                      "1. Hot stamping — https://www.primyn.com/pagina/o-que-e-hot-stamping-foil\n"
                      "2. Alto relevo seco — https://www.primyn.com/pagina/o-que-e-alto-relevo-seco\n"
                      "3. Baixo relevo — https://www.primyn.com/pagina/o-que-e-letterpress\n"
                      "4. Empastamento / borda sanduíche — https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n"
                      "5. Impressão colorida no papel especial\n"
                      "6. Combinação de acabamentos\n\n"
                      "📸 https://www.instagram.com/primyn.store/\n\n"
                      "Qual deles faz mais sentido para o projeto da sua marca?")
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
            resposta=("Por favor, escolha uma das opções:\n\n"
                      "1. Hot stamping\n2. Alto relevo seco\n3. Baixo relevo\n"
                      "4. Empastamento / borda sanduíche\n5. Impressão colorida\n6. Combinação")
        else:
            dados["acabamento"]=am[opcao]; sessao["tentativas"]=0
            if opcao=="4":
                resposta=("O empastamento tem três finalidades possíveis: 💎\n\n"
                          "1. Papel mais encorpado — mais espessura e presença ao toque\n"
                          "2. Proteção do relevo — evita que o acabamento apareça no verso\n"
                          "3. Borda sanduíche — interior colorido revelado ao olhar a borda do cartão\n\n"
                          "Saiba mais: https://www.primyn.com/pagina/o-que-e-empastamento-de-papeis\n\n"
                          "Qual dessas finalidades faz mais sentido para o seu projeto?")
                sessao["etapa"]="empastamento_det"
            else:
                produto_num=dados.get("produto_num","1")
                minimo=PRODUTOS.get(produto_num,{}).get("minimo",100)
                resposta=f"Qual quantidade você está considerando?\n\n{menu_qtd(minimo)}"
                sessao["etapa"]="quantidade"

    elif etapa=="empastamento_det":
        dados["empastamento_tipo"]=msg
        produto_num=dados.get("produto_num","1")
        minimo=PRODUTOS.get(produto_num,{}).get("minimo",100)
        resposta=f"Qual quantidade você está considerando?\n\n{menu_qtd(minimo)}"
        sessao["etapa"]="quantidade"

    elif etapa=="quantidade":
        primeiro=dados.get("nome","").split()[0]
        produtos_lista=dados.get("produtos_lista",["1"])
        resultado,qtd=interp_qtd(msg)
        minimo=min(PRODUTOS[p]["minimo"] for p in produtos_lista if p in PRODUTOS)

        if resultado=="menos":
            resposta=(f"Nossa quantidade mínima é {minimo} unidades. "
                      f"Qual opção se encaixa melhor?\n\n"
                      f"2. 250 unidades\n3. 500 unidades\n4. 1.000 unidades\n5. 2.000 unidades\n6. Acima de 2.000")
        elif resultado=="acima":
            resposta=("Para volumes acima de 2.000 unidades, preparamos uma proposta com condições especiais. "
                      "Vou encaminhar você para um especialista! 🚀")
            dados["quantidade_acima"]=True; dados["status"]="handoff_premium"
            sessao["etapa"]="handoff"; handoff_data=dados
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
            aviso_txt=("Atenção aos mínimos:\n"+"\n".join(avisos)+"\n\n") if avisos else ""
            if acima_lim or total==0:
                resposta=(f"{aviso_txt}Para essa composição, o investimento é definido sob consulta.\n\n"
                          "Vou encaminhar para um especialista preparar a proposta ideal.\n\n"
                          "1. Sim, quero a proposta\n2. Prefiro pensar\n3. Não, obrigada")
            else:
                det="\n".join(linhas)
                resposta=(f"{aviso_txt}Para a configuração que você me passou: 👑\n\n"
                          f"{det}\n\nTotal estimado: {fmt(total)}\n\n"
                          "Esse valor é uma referência — o orçamento final é personalizado "
                          "conforme acabamento, criação e complexidade.\n\n"
                          "Faz sentido prosseguirmos com uma proposta personalizada?\n\n"
                          "1. Sim, quero a proposta\n2. Prefiro pensar\n3. Não, obrigada")
            sessao["etapa"]="media_proposta"

    elif etapa=="media_proposta":
        primeiro=dados.get("nome","").split()[0]
        if any(p in ml for p in ["1","sim","quero","pode","vamos","claro"]):
            resposta=var(f"Que ótimo! 😁 Você tem algum prazo importante para receber esse material?",
                         f"Maravilha, {primeiro}! 😁 Existe algum prazo que eu deva considerar na proposta?")
            sessao["etapa"]="urgencia"
        elif any(p in ml for p in ["2","pensar","depois","calma","talvez"]):
            resposta=var("Claro! Sem qualquer pressa. Quando quiser retomar, estaremos aqui. 😊\n\nAcompanhe em @primyn.store",
                         f"Com certeza, {primeiro}. Quando quiser continuar, é só chamar. 😊")
            dados["status"]="aguardando_resposta"; sessao["etapa"]="encerrado"
            try:
                from followup import agendar_followup
                agendar_followup(numero,dados.get("nome",""),"pensar",dias=2)
            except: pass
        else:
            resposta=var(f"Sem problema, {primeiro}. Fico à disposição sempre que quiser retomar. 😊",
                         "Entendido! Quando quiser explorar uma proposta, será um prazer. 😊")
            dados["status"]="perdido"; sessao["etapa"]="encerrado"

    elif etapa=="urgencia":
        dados["urgencia"]=msg
        urgente=any(p in ml for p in ["urgente","rápido","rapido","pressa","amanhã","amanha","semana","logo","dias"])
        aviso=("Projetos com criação e produção premium têm prazo médio de 7 a 10 dias úteis. "
               "Vou sinalizar a urgência no encaminhamento.\n\n") if urgente else ""
        resposta=f"{aviso}{hdoff()}"
        dados["status"]="handoff"; sessao["etapa"]="handoff"; handoff_data=dados

    elif etapa=="handoff":
        primeiro=dados.get("nome","").split()[0]
        resposta=(f"Antes de encerrar, {primeiro} — como foi a sua experiência com este atendimento?\n\n"
                  "1. Ótimo\n2. Bom\n3. Precisa melhorar")
        sessao["etapa"]="feedback"

    elif etapa=="feedback":
        avals={"1":"Ótimo","2":"Bom","3":"Precisa melhorar"}
        av=avals.get(msg.strip(),msg); dados["avaliacao"]=av
        primeiro=dados.get("nome","").split()[0]
        if msg.strip()=="3" or "melhorar" in ml or "ruim" in ml:
            resposta=f"Obrigada pelo retorno, {primeiro}. Cada feedback nos ajuda a evoluir. 🤍"
        else:
            resposta=f"Que bom, {primeiro}! Foi um prazer te atender. Até breve! 🤍"
        sessao["etapa"]="encerrado"

    elif etapa=="encerrado":
        primeiro=dados.get("nome","").split()[0] if dados.get("nome") else ""
        resposta=f"Olá, {primeiro}! Como posso te ajudar? 😊" if primeiro else "Olá! Como posso te ajudar hoje? 😊"
        sessao["etapa"]="produto" if primeiro else "triagem_inicial"

    else:
        resposta="Olá! Como posso te ajudar hoje? 😊"
        sessao["etapa"]="triagem_inicial"

    sessao["dados"]=dados
    upd_sessao(numero,sessao)
    return resposta,handoff_data

carregar_sessoes = load
