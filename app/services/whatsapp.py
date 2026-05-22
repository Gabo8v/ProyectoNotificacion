import requests

from app.config import settings


class WhatsAppService:
    def __init__(self, bot_url: str | None = None):
        self.bot_url = bot_url or settings.whatsapp_bot_url

    def send_message(self, to: str, message: str) -> dict | None:
        if not to.endswith("@c.us") and not to.endswith("@lid"):
            to = f"{to}@c.us"
        try:
            resp = requests.post(
                f"{self.bot_url}/send-message",
                json={"to": to, "message": message},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"WhatsApp send error: {e}")
            return None

    def is_healthy(self) -> bool:
        try:
            resp = requests.get(f"{self.bot_url}/health", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False
