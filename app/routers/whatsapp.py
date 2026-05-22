from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.integration_service import IntegrationService

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/webhook")
async def whatsapp_webhook(data: dict, db: Session = Depends(get_db)):
    from_number = data.get("from", "unknown")
    body = data.get("body", "")
    message_id = data.get("messageId", "")

    integration = IntegrationService(db)
    integration.whatsapp_to_email(from_number, body, message_id)

    return {"status": "received", "from": from_number, "body": body}
