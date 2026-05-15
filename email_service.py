# ═══════════════════════════════════════════════
# PRIMYN STUDIO — SERVIÇO DE E-MAIL
# ═══════════════════════════════════════════════

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, NOTIFY_EMAIL

def enviar_email(destinatario, assunto, corpo_html):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Primyn Studio <{SMTP_EMAIL}>"
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo_html, "html", "utf-8"))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL] Enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"[ERRO EMAIL] {e}")
        return False

def notificar_bela(lead_data):
    """Notifica Bela sobre novo lead qualificado"""
    nome    = lead_data.get("nome", "N/A")
    produto = lead_data.get("produto", "N/A")
    linha   = lead_data.get("linha", "N/A")
    faixa   = lead_data.get("faixa_investimento", "N/A")
    id_vis  = lead_data.get("identidade_visual", "N/A")
    criacao = "Sim" if lead_data.get("criacao_arte") else "Não"

    assunto = f"✦ Novo lead qualificado — {nome} | {produto}"

    corpo = f"""
    <html>
    <body style="font-family:Arial,sans-serif;color:#333;max-width:640px;margin:0 auto">
        <div style="background:#1a1a1a;padding:24px;text-align:center">
            <h2 style="color:#C8A96A;margin:0;letter-spacing:2px">✦ PRIMYN STUDIO</h2>
            <p style="color:#aaa;margin:4px 0 0;font-size:13px">Novo Lead Qualificado pela Mily</p>
        </div>
        <div style="padding:28px;background:#fafafa;border:1px solid #eee">
            <table style="width:100%;border-collapse:collapse;font-size:14px">
                <tr style="border-bottom:1px solid #eee">
                    <td style="padding:10px 8px;color:#888;width:40%"><strong>Nome</strong></td>
                    <td style="padding:10px 8px">{nome}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee;background:#fff">
                    <td style="padding:10px 8px;color:#888"><strong>E-mail</strong></td>
                    <td style="padding:10px 8px">{lead_data.get("email","N/A")}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee">
                    <td style="padding:10px 8px;color:#888"><strong>WhatsApp</strong></td>
                    <td style="padding:10px 8px">{lead_data.get("whatsapp","N/A")}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee;background:#fff">
                    <td style="padding:10px 8px;color:#888"><strong>Origem</strong></td>
                    <td style="padding:10px 8px">{lead_data.get("origem","N/A")}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee">
                    <td style="padding:10px 8px;color:#888"><strong>Área de atuação</strong></td>
                    <td style="padding:10px 8px">{lead_data.get("area","N/A")}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee;background:#fff">
                    <td style="padding:10px 8px;color:#888"><strong>Produto</strong></td>
                    <td style="padding:10px 8px">{produto}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee">
                    <td style="padding:10px 8px;color:#888"><strong>Precisa de criação de arte</strong></td>
                    <td style="padding:10px 8px">{criacao}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee;background:#fff">
                    <td style="padding:10px 8px;color:#888"><strong>Identidade visual</strong></td>
                    <td style="padding:10px 8px">{id_vis}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee">
                    <td style="padding:10px 8px;color:#888"><strong>Linha / Estilo</strong></td>
                    <td style="padding:10px 8px">{linha}</td>
                </tr>
                <tr style="background:#fff">
                    <td style="padding:10px 8px;color:#888"><strong>Faixa de investimento</strong></td>
                    <td style="padding:10px 8px;font-weight:bold;color:#1a1a1a">{faixa}</td>
                </tr>
            </table>
        </div>
        <div style="background:#f0ede8;padding:16px 28px;border:1px solid #eee;border-top:none">
            <p style="margin:0;font-size:13px;color:#555">
                ⚡ <strong>Ação:</strong> Entrar em contato com o cliente para elaborar a proposta personalizada.
            </p>
        </div>
        <div style="text-align:center;padding:20px;color:#bbb;font-size:11px">
            Primyn Studio ✦ ola@primyn.com · primyn.com · @primyn.store
        </div>
    </body>
    </html>
    """
    return enviar_email(NOTIFY_EMAIL, assunto, corpo)

def enviar_confirmacao_cliente(email_cliente, nome):
    """Envia e-mail de confirmação para o cliente"""
    assunto = f"Seu projeto está em boas mãos, {nome} ✦ Primyn Studio"
    corpo = f"""
    <html>
    <body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:0 auto">
        <div style="background:#1a1a1a;padding:24px;text-align:center">
            <h1 style="color:#C8A96A;margin:0;font-size:22px;letter-spacing:2px">✦ PRIMYN STUDIO</h1>
        </div>
        <div style="padding:28px">
            <p>Olá, {nome}! ✨</p>
            <p>Obrigada por escolher a Primyn para o seu projeto. Recebemos todas as informações do seu atendimento e um especialista dará continuidade em breve.</p>
            <p>Enquanto isso, inspire-se nos nossos projetos:</p>
            <p>📷 <a href="https://instagram.com/primyn.store" style="color:#C8A96A">@primyn.store</a></p>
            <p>🌐 <a href="https://primyn.com" style="color:#C8A96A">primyn.com</a></p>
            <br>
            <p>Até breve! ✦</p>
            <p><strong>Equipe Primyn Studio</strong></p>
        </div>
        <div style="text-align:center;padding:20px;color:#bbb;font-size:11px;border-top:1px solid #eee">
            Primyn Studio — Cada detalhe importa. ✦<br>
            ola@primyn.com | primyn.com | @primyn.store
        </div>
    </body>
    </html>
    """
    return enviar_email(email_cliente, assunto, corpo)

def notificar_designer(dados):
    """Notifica Ane sobre projeto de identidade visual"""
    assunto = f"✦ Novo projeto de identidade visual — {dados.get('nome','N/A')}"
    corpo = f"""
    <html>
    <body style="font-family:Arial,sans-serif;color:#333;max-width:640px;margin:0 auto">
        <div style="background:#1a1a1a;padding:24px;text-align:center">
            <h2 style="color:#C8A96A;margin:0;letter-spacing:2px">✦ PRIMYN STUDIO</h2>
            <p style="color:#aaa;margin:4px 0 0;font-size:13px">Novo Projeto de Identidade Visual</p>
        </div>
        <div style="padding:28px;background:#fafafa;border:1px solid #eee">
            <table style="width:100%;border-collapse:collapse;font-size:14px">
                <tr style="border-bottom:1px solid #eee">
                    <td style="padding:10px 8px;color:#888;width:40%"><strong>Cliente</strong></td>
                    <td style="padding:10px 8px">{dados.get("nome","N/A")}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee;background:#fff">
                    <td style="padding:10px 8px;color:#888"><strong>E-mail</strong></td>
                    <td style="padding:10px 8px">{dados.get("email","N/A")}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee">
                    <td style="padding:10px 8px;color:#888"><strong>WhatsApp</strong></td>
                    <td style="padding:10px 8px">{dados.get("whatsapp","N/A")}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee;background:#fff">
                    <td style="padding:10px 8px;color:#888"><strong>Área de atuação</strong></td>
                    <td style="padding:10px 8px">{dados.get("area","N/A")}</td>
                </tr>
                <tr style="border-bottom:1px solid #eee">
                    <td style="padding:10px 8px;color:#888"><strong>Produto de interesse</strong></td>
                    <td style="padding:10px 8px">{dados.get("produto","N/A")}</td>
                </tr>
                <tr style="background:#fff">
                    <td style="padding:10px 8px;color:#888"><strong>Linha / Estilo</strong></td>
                    <td style="padding:10px 8px">{dados.get("linha","N/A")}</td>
                </tr>
            </table>
        </div>
        <div style="background:#f0ede8;padding:16px 28px;border:1px solid #eee;border-top:none">
            <p style="margin:0;font-size:13px;color:#555">
                ⚡ <strong>Ação:</strong> Entrar em contato com o cliente para alinhar o projeto de identidade visual.
            </p>
        </div>
        <div style="text-align:center;padding:20px;color:#bbb;font-size:11px">
            Primyn Studio ✦ ola@primyn.com · primyn.com · @primyn.store
        </div>
    </body>
    </html>
    """
    designer_email = os.getenv("DESIGNER_EMAIL", NOTIFY_EMAIL)
    return enviar_email(designer_email, assunto, corpo)
