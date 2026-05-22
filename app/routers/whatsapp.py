from fastapi import APIRouter

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/webhook")
async def whatsapp_webhook(data: dict):
    from_number = data.get("from", "unknown")
    body = data.get("body", "")
    message_id = data.get("messageId", "")

    print(f"[WhatsApp Webhook] De: {from_number} | Mensaje: {body}")

    return {"status": "received", "from": from_number, "body": body}
