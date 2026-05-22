import asyncio
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import dashboard, health, notifications, templates, whatsapp
from app.tasks.polling import run_polling_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_polling_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Sistema de Gestion de Notificaciones",
    description="Modulo de notificaciones con Gmail + WhatsApp Bot",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=Path("app/static")), name="static")

app.include_router(health.router)
app.include_router(notifications.router)
app.include_router(templates.router)
app.include_router(whatsapp.router)
app.include_router(dashboard.router)
