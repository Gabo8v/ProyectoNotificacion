from fastapi import FastAPI
from app.routers import health, notifications, templates

app = FastAPI(
    title="Sistema de Gestion de Notificaciones",
    description="Modulo de notificaciones con Gmail + WhatsApp Bot",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(notifications.router)
app.include_router(templates.router)
