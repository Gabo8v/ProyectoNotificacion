import asyncio
import logging
import os
import shutil
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from app.auth import is_authenticated
from app.config import settings
from app.limiter import limiter
from app.routers import auth, consulta, dashboard, health, notifications, polling_control, templates, whatsapp

logger = logging.getLogger(__name__)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

WHATSAPP_BOT_URL = settings.whatsapp_bot_url.rstrip("/")
BOT_DIR = str(Path(__file__).resolve().parent.parent / "whatsapp-bot")
NODE_BIN = shutil.which("node") or "node"
PM2_BIN = shutil.which("pm2.cmd") or shutil.which("pm2") or "pm2.cmd"


async def _verificar_bot():
    logger.info("Verificando conexion con WhatsApp bot...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{WHATSAPP_BOT_URL}/health")
            if r.status_code == 200:
                logger.info("WhatsApp bot conectado correctamente")
                return
    except Exception as exc:
        logger.warning("WhatsApp bot no responde (%s)", exc)

    BOT_SCRIPT = str(Path(BOT_DIR) / "index.js")

    def _intentar_iniciar() -> bool:
        result = subprocess.run(
            [PM2_BIN, "start", BOT_SCRIPT, "--name", "whatsapp-bot"],
            capture_output=True, timeout=15, cwd=BOT_DIR,
        )
        if result.returncode == 0:
            return True
        serr = result.stderr.decode("utf-8", errors="replace").strip()[:200]
        logger.warning("pm2 fallo (exit %d): %s", result.returncode, serr)
        result = subprocess.run(
            [NODE_BIN, "index.js"],
            capture_output=True, timeout=10, cwd=BOT_DIR,
        )
        if result.returncode == 0:
            return True
        serr = result.stderr.decode("utf-8", errors="replace").strip()[:200]
        logger.error("Node fallo (exit %d): %s", result.returncode, serr)
        return False

    try:
        ok = await asyncio.to_thread(_intentar_iniciar)
        if ok:
            logger.info("WhatsApp bot iniciado")
            await asyncio.sleep(3)
    except Exception as e:
        logger.error("No se pudo iniciar el WhatsApp bot: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(_verificar_bot())
    yield
    logger.info("Servidor detenido correctamente")


app = FastAPI(
    title="Sistema de Gestion de Notificaciones",
    description="Modulo de notificaciones con Gmail + WhatsApp Bot",
    version="0.2.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.token_encryption_key or settings.admin_password)


@app.middleware("http")
async def dashboard_auth_middleware(request, call_next):
    path = request.url.path
    if path.startswith("/dashboard") and not path.startswith("/login"):
        role = is_authenticated(request)
        if not role:
            return RedirectResponse(url="/login")
    response = await call_next(request)
    return response


app.mount("/static", StaticFiles(directory=Path("app/static")), name="static")

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(notifications.router)
app.include_router(templates.router)
app.include_router(whatsapp.router)
app.include_router(dashboard.router)
app.include_router(polling_control.router)
app.include_router(consulta.router)
