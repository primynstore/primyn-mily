# ═══════════════════════════════════════════════
# PRIMYN STUDIO — CONFIGURAÇÕES
# ═══════════════════════════════════════════════

import os

# Z-API
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "3F28A6AD20C7224DCBD06244BF24326C")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "3F28A6AD20C7224DCBD06244BF24326C")
ZAPI_BASE_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}"

# E-MAIL (UOL)
SMTP_HOST = os.getenv("SMTP_HOST", "smtps.uhserver.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ola@primyn.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Colocar no Railway como variável de ambiente

# NOTIFICAÇÕES
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "ola@primyn.com")  # André recebe aqui

# WEBHOOK
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "primyn2024")
