import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

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
from app.routers import auth, dashboard, health, notifications, polling_control, templates, whatsapp
from app.tasks.polling import run_polling_loop

logger = logging.getLogger(__name__)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_polling_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    logger.info("Servidor detenido correctamente")


app = FastAPI(
    title="Sistema de Gestion de Notificaciones",
    description="Modulo de notificaciones con Gmail + WhatsApp Bot",
    version="0.1.0",
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
        if not is_authenticated(request):
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
