"""Gmail API module - placeholder for Fase 2."""


class GmailService:
    def __init__(self):
        self.service = None

    def authenticate(self):
        raise NotImplementedError("Implementar en Fase 2")

    def send_email(self, to: str, subject: str, body: str):
        raise NotImplementedError("Implementar en Fase 2")

    def read_inbox(self):
        raise NotImplementedError("Implementar en Fase 2")
