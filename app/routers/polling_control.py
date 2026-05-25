import logging

from fastapi import APIRouter, Depends

from app.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/polling", tags=["polling"], dependencies=[Depends(require_auth)])

POLLING_ENABLED = True


@router.get("/status")
def status():
    return {"enabled": POLLING_ENABLED}


@router.post("/toggle")
def toggle():
    global POLLING_ENABLED
    POLLING_ENABLED = not POLLING_ENABLED
    state = "activado" if POLLING_ENABLED else "detenido"
    logger.info(f"Polling {state}")
    return {"enabled": POLLING_ENABLED, "message": f"Polling {state}"}
