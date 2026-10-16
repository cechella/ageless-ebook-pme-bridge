"""
lumen_ana_ageless_bridge.py - AGELESS E-book R$197
Mercado Pago AGELESS -> N8N -> Ana Live WhatsApp
"""
import json, time, os
from pathlib import Path
import requests

INBOX = Path("/opt/atlas/tasks/inbox")
OUTBOX = Path("/opt/atlas/tasks/outbox")
N8N_WEBHOOK_ANA = os.getenv("N8N_WEBHOOK_ANA", "https://n8n.saudeweb.itajai.br/webhook/ana-ebook")

def process_mercadopago_event(payload: dict):
    if payload.get("type") != "payment" or payload.get("data", {}).get("status") != "approved":
        return None
    email = payload["data"]["payer"]["email"]
    requests.post(N8N_WEBHOOK_ANA, json={
        "event": "ebook_pme_venda",
        "email": email,
        "produto": "IA PARA PMEs - Playbook AGELESS R$197",
        "whatsapp_business": "AGELESS"
    }, timeout=10)
    return {"email": email, "status": "entregue_via_ana"}

def main_loop():
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    while True:
        for f in INBOX.glob("*.json"):
            data = json.loads(f.read_text())
            result = process_mercadopago_event(data)
            if result:
                (OUTBOX / f.name).write_text(json.dumps(result))
                f.unlink()
        time.sleep(5)

if __name__ == "__main__":
    main_loop()
