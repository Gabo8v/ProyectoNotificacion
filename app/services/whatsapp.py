"""WhatsApp bot proxy - placeholder for Fase 3."""


class WhatsAppService:
    def __init__(self, bot_url: str = "http://localhost:3001"):
        self.bot_url = bot_url

    def send_message(self, to: str, message: str):
        raise NotImplementedError("Implementar en Fase 3")
