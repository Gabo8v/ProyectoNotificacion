import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.integration_service import IntegrationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/webhook")
async def whatsapp_webhook(
    data: dict,
    db: Session = Depends(get_db),
    x_api_key: str = Header(default=""),
):
    if settings.webhook_api_key and x_api_key != settings.webhook_api_key:
        logger.warning("Webhook intento sin API key valida")
        raise HTTPException(status_code=403, detail="API key invalida")

    from_number = data.get("from", "unknown")
    body = data.get("body", "")
    message_id = data.get("messageId", "")

    integration = IntegrationService(db)
    integration.whatsapp_to_email(from_number, body, message_id)

    return {"status": "received", "from": from_number, "body": body}
