# ═══════════════════════════════════════════════
# PRIMYN STUDIO — SERVIÇO DE E-MAIL
# ═══════════════════════════════════════════════

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, NOTIFY_EMAIL

def enviar_email(destinatario, assunto, corpo_html):
    """Envia e-mail via SMTP UOL"""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Primyn Studio <{SMTP_EMAIL}>"
        msg["To"] = destinatario
        msg["Subject"] = assunto
        
        html_part = MIMEText(corpo_html, "html", "utf-8")
        msg.attach(html_part)
        
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"[EMAIL] Enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"[ERRO EMAIL] {e}")
        return False

def notificar_andre(lead_data):
    """Notifica André sobre novo lead qualificado"""
    assunto = f"✦ Novo lead qualificado — {lead_data.get('nome', 'N/A')} | {lead_data.get('produto', 'N/A')}"
    
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #1a1a1a;">✦ Novo Lead Qualificado — Primyn Studio</h2>
        <hr>
        <table style="width:100%; border-collapse:collapse;">
            <tr><td><strong>Nome:</strong></td><td>{lead_data.get('nome', 'N/A')}</td></tr>
            <tr><td><strong>E-mail:</strong></td><td>{lead_data.get('email', 'N/A')}</td></tr>
            <tr><td><strong>WhatsApp:</strong></td><td>{lead_data.get('whatsapp', 'N/A')}</td></tr>
            <tr><td><strong>Origem:</strong></td><td>{lead_data.get('origem', 'N/A')}</td></tr>
            <tr><td><strong>Tipo de contato:</strong></td><td>{lead_data.get('tipo_contato', 'N/A')}</td></tr>
            <tr><td><strong>Área:</strong></td><td>{lead_data.get('area', 'N/A')}</td></tr>
            <tr><td><strong>Produto:</strong></td><td>{lead_data.get('produto', 'N/A')}</td></tr>
            <tr><td><strong>Arte:</strong></td><td>{lead_data.get('arte', 'N/A')}</td></tr>
            <tr><td><strong>Formato:</strong></td><td>{lead_data.get('formato', 'N/A')}</td></tr>
            <tr><td><strong>Material:</strong></td><td>{lead_data.get('material', 'N/A')}</td></tr>
            <tr><td><strong>Acabamento:</strong></td><td>{lead_data.get('acabamento', 'N/A')}</td></tr>
            <tr><td><strong>Quantidade:</strong></td><td>{lead_data.get('quantidade', 'N/A')}</td></tr>
            <tr><td><strong>Urgência:</strong></td><td>{lead_data.get('urgencia', 'N/A')}</td></tr>
            <tr><td><strong>Média apresentada:</strong></td><td>R$ {lead_data.get('media', 'N/A')}</td></tr>
        </table>
        <hr>
        <p><em>Ação necessária: entrar em contato para proposta personalizada.</em></p>
    </body>
    </html>
    """
    
    return enviar_email(NOTIFY_EMAIL, assunto, corpo)

def enviar_confirmacao_cliente(email_cliente, nome):
    """Envia e-mail de confirmação para o cliente"""
    assunto = f"Seu projeto está em boas mãos, {nome} ✦ Primyn Studio"
    
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: #1a1a1a; font-size: 24px;">✦ Primyn Studio</h1>
        </div>
        <div style="padding: 20px;">
            <p>Olá, {nome}! ✨</p>
            <p>Obrigado por escolher a Primyn para o seu projeto. Recebemos todas as informações do seu atendimento e um especialista dará continuidade em breve.</p>
            <p>Enquanto isso, se quiser se inspirar com nossos projetos:</p>
            <p>📷 <a href="https://instagram.com/primyn.store">@primyn.store</a></p>
            <p>🌐 <a href="https://primyn.com">primyn.com</a></p>
            <br>
            <p>Até breve! ✦</p>
            <p><strong>Equipe Primyn Studio</strong></p>
        </div>
        <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
            <p>Primyn Studio — Cada detalhe importa. ✦</p>
            <p>ola@primyn.com | primyn.com | @primyn.store</p>
        </div>
    </body>
    </html>
    """
    
    return enviar_email(email_cliente, assunto, corpo)

def notificar_designer(dados):
    """Notifica designer sobre projeto de identidade visual"""
    assunto = f"✦ Novo projeto de identidade visual — {dados.get('nome', 'N/A')}"
    
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #1a1a1a;">✦ Novo Projeto de Identidade Visual</h2>
        <hr>
        <table style="width:100%; border-collapse:collapse;">
            <tr><td><strong>Cliente:</strong></td><td>{dados.get('nome', 'N/A')}</td></tr>
            <tr><td><strong>E-mail:</strong></td><td>{dados.get('email', 'N/A')}</td></tr>
            <tr><td><strong>WhatsApp:</strong></td><td>{dados.get('whatsapp', 'N/A')}</td></tr>
            <tr><td><strong>Área de atuação:</strong></td><td>{dados.get('area', 'N/A')}</td></tr>
            <tr><td><strong>Produto:</strong></td><td>{dados.get('produto', 'N/A')}</td></tr>
            <tr><td><strong>Urgência:</strong></td><td>{dados.get('urgencia', 'Sem urgência informada')}</td></tr>
        </table>
        <hr>
        <p><strong>Ação:</strong> Entrar em contato com o cliente pelo e-mail para alinhar o projeto de identidade visual.</p>
        <p><em>Primyn Studio ✦</em></p>
    </body>
    </html>
    """
    
    designer_email = os.getenv("DESIGNER_EMAIL", NOTIFY_EMAIL)
    return enviar_email(designer_email, assunto, corpo)
