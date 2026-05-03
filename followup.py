# ═══════════════════════════════════════════════
# PRIMYN STUDIO — FOLLOW-UP AUTOMÁTICO
# ═══════════════════════════════════════════════

import json
import os
from datetime import datetime, timedelta
from zapi import enviar_mensagem

FOLLOWUP_FILE = "followups.json"


def carregar_followups():
    """Carrega lista de follow-ups agendados"""
    if os.path.exists(FOLLOWUP_FILE):
        with open(FOLLOWUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_followups(followups):
    """Salva lista de follow-ups"""
    with open(FOLLOWUP_FILE, "w", encoding="utf-8") as f:
        json.dump(followups, f, ensure_ascii=False, indent=2)


def agendar_followup(numero, nome, tipo, dias=2):
    """
    Agenda um follow-up para o futuro.
    tipo: 'pensar' (disse preciso pensar) | 'proposta' (proposta sem resposta) | 'reengajamento'
    """
    followups = carregar_followups()
    
    data_envio = (datetime.now() + timedelta(days=dias)).isoformat()
    
    followup = {
        "numero": numero,
        "nome": nome,
        "tipo": tipo,
        "data_envio": data_envio,
        "tentativas": 0,
        "max_tentativas": 3,
        "status": "agendado"
    }
    
    followups.append(followup)
    salvar_followups(followups)
    print(f"[FOLLOWUP] Agendado para {nome} em {dias} dias")


def executar_followups():
    """
    Verifica e executa follow-ups que já passaram da data.
    Chamar periodicamente (ex: a cada hora via cron/scheduler).
    """
    followups = carregar_followups()
    agora = datetime.now()
    atualizados = []
    
    for fu in followups:
        if fu["status"] != "agendado":
            atualizados.append(fu)
            continue
        
        data_envio = datetime.fromisoformat(fu["data_envio"])
        
        if agora >= data_envio:
            sucesso = enviar_followup(fu)
            
            if sucesso:
                fu["tentativas"] += 1
                
                if fu["tentativas"] >= fu["max_tentativas"]:
                    fu["status"] = "encerrado"
                else:
                    proximo = (agora + timedelta(days=2 * fu["tentativas"])).isoformat()
                    fu["data_envio"] = proximo
        
        atualizados.append(fu)
    
    salvar_followups(atualizados)


def enviar_followup(fu):
    """Envia mensagem de follow-up baseada no tipo"""
    numero = fu["numero"]
    nome = fu["nome"].split()[0] if fu["nome"] else "cliente"
    tipo = fu["tipo"]
    tentativa = fu["tentativas"] + 1
    
    mensagens = {
        "pensar": [
            f"Oi, {nome} ✨ Só passando para saber se ficou alguma dúvida sobre o que conversamos? Estou por aqui se precisar! ✦",
            f"Olá, {nome} ✦ Sua proposta continua disponível. Se quiser retomar, é só me chamar! ✨",
            f"Oi, {nome}! ✨ Última mensagem por aqui — quando quiser retomar seu projeto, estarei à disposição. Enquanto isso, se inspire em @primyn.store ✦"
        ],
        "proposta": [
            f"Oi, {nome} ✨ Vi que enviamos sua proposta recentemente. Ficou alguma dúvida? Estou por aqui para te ajudar! ✦",
            f"Olá, {nome} ✦ Sua proposta personalizada ainda está válida. Se quiser ajustar algo, é só me dizer! ✨",
            f"Oi, {nome}! ✨ Só um lembrete gentil — sua proposta vence em breve. Se quiser prosseguir, estou por aqui! ✦"
        ],
        "reengajamento": [
            f"Olá, {nome}! ✨ Aqui é a Mily, da Primyn. Vi que você conversou com a gente há um tempo. Queria saber se ainda faz sentido para você — temos algumas novidades que podem te interessar. Se quiser retomar, estou por aqui! ✦",
            f"Oi, {nome} ✨ Passando para te mostrar algumas novidades da Primyn. Se quiser dar uma olhada: @primyn.store ✦",
            f"Olá, {nome}! ✦ Última mensagem por aqui. Se em outro momento quiser retomar seu projeto premium, será um prazer te atender. ✨"
        ]
    }
    
    lista = mensagens.get(tipo, mensagens["pensar"])
    indice = min(tentativa - 1, len(lista) - 1)
    mensagem = lista[indice]
    
    resultado = enviar_mensagem(numero, mensagem)
    
    if resultado:
        print(f"[FOLLOWUP] Enviado para {nome} (tentativa {tentativa}): {tipo}")
        return True
    return False
