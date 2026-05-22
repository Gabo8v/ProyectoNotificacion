"""Core notification logic - implements Fase 4."""


class NotificationService:
    def send(self, channel: str, to: str, subject: str | None, body: str):
        raise NotImplementedError("Implementar en Fase 4")

    def get_history(self, filters: dict | None = None):
        raise NotImplementedError("Implementar en Fase 4")
