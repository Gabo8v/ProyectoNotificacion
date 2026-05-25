import asyncio
import logging

from app.database import SessionLocal
from app.routers.polling_control import POLLING_ENABLED
from app.services.gmail import GmailService
from app.services.integration_service import IntegrationService

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 30


async def poll_gmail():
    if not POLLING_ENABLED:
        await asyncio.sleep(1)
        return

    gmail = GmailService()
    if not gmail.is_ready():
        logger.warning("Polling: Gmail no configurado, skipping")
        return

    db = SessionLocal()
    try:
        integration = IntegrationService(db)
        emails = gmail.read_inbox(max_results=10)
        for email_data in emails:
            gmail_id = email_data.get("id")
            if not gmail_id:
                continue
            integration.email_to_whatsapp(email_data)
            gmail.mark_as_read(gmail_id)
    except Exception as e:
        logger.error(f"Polling error: {e}")
    finally:
        db.close()


async def run_polling_loop():
    while True:
        await poll_gmail()
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
