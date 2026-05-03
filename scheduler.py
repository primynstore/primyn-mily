# ═══════════════════════════════════════════════
# PRIMYN STUDIO — SCHEDULER (Follow-ups)
# ═══════════════════════════════════════════════

import threading
import time
from followup import executar_followups


def iniciar_scheduler():
    """Inicia verificação de follow-ups a cada 1 hora"""
    def loop():
        while True:
            try:
                print("[SCHEDULER] Verificando follow-ups...")
                executar_followups()
            except Exception as e:
                print(f"[ERRO SCHEDULER] {e}")
            time.sleep(3600)  # Verifica a cada 1 hora
    
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    print("[SCHEDULER] Iniciado — verificando follow-ups a cada 1h")
