import re

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.models.template import Template
from app.schemas.notification import NotificationCreate
from app.services.gmail import GmailService
from app.services.whatsapp import WhatsAppService
from app.services.notification_service import NotificationService


def _extract_email(raw: str) -> str:
    match = re.search(r'<(.+?)>', raw)
    return match.group(1) if match else raw.strip()


def _strip_wa_suffix(phone: str) -> str:
    for suffix in ("@c.us", "@lid", "@g.us"):
        if phone.endswith(suffix):
            return phone[:-len(suffix)]
    return phone


class IntegrationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.gmail = GmailService()
        self.whatsapp = WhatsAppService()

    def email_to_whatsapp(self, email_data: dict) -> Notification | None:
        from_raw = email_data.get("from", "")
        from_email = _extract_email(from_raw)
        subject = email_data.get("subject", "")
        body = email_data.get("snippet", "")
        gmail_id = email_data.get("id", "")

        conversation_ref = f"gmail:{from_email}"

        user = self.notification_service.get_user_by_email(from_email)
        if not user or not user.phone:
            self.notification_service.log(
                "email", "warning",
                f"Gmail -> WA: usuario no encontrado para {from_email}",
            )
            return None

        notif = self.notification_service.send(NotificationCreate(
            user_id=user.id,
            channel="whatsapp",
            subject=subject,
            body=f"[Reenviado de Gmail]\nDe: {from_raw}\nAsunto: {subject}\n\n{body}",
        ))

        result = self.whatsapp.send_message(
            to=user.phone,
            message=f"[Gmail] {subject}\n\n{body}\n\n---\nRespondé este mensaje para contestar por mail.",
        )

        if result:
            self.notification_service.mark_sent(notif.id, external_id=gmail_id)
            self.notification_service.log(
                "whatsapp", "info",
                f"Gmail -> WA enviado a {user.phone}",
            )
            notif.conversation_ref = conversation_ref
            self.db.commit()
            self.db.refresh(notif)
        else:
            self.notification_service.mark_failed(notif.id, "Error al enviar por WhatsApp")

        return notif

    def whatsapp_to_email(self, from_number: str, wa_body: str, wa_message_id: str) -> Notification | None:
        templates = self.db.query(Template).filter(Template.is_active == True).all()

        matched_template: Template | None = None
        for tpl in templates:
            keywords = [k.strip().lower() for k in tpl.keywords.split(",")]
            if any(kw in wa_body.lower() for kw in keywords):
                matched_template = tpl
                break

        if not matched_template:
            self.notification_service.log(
                "whatsapp", "info",
                f"WA -> Gmail: sin template匹配 para {from_number}",
            )
            return None

        user = self.notification_service.get_user_by_phone(_strip_wa_suffix(from_number))
        if not user:
            self.notification_service.log(
                "whatsapp", "warning",
                f"WA -> Gmail: usuario no encontrado para {from_number}",
            )
            return None

        email_subject = matched_template.subject or "Respuesta automatica"
        notif = self.notification_service.send(NotificationCreate(
            user_id=user.id,
            channel="email",
            subject=email_subject,
            body=matched_template.body,
        ))

        result = self.gmail.send_email(
            to=user.email,
            subject=email_subject,
            body=notif.body,
        )

        if result:
            self.notification_service.mark_sent(notif.id, external_id=result.get("id"))
            self.notification_service.log(
                "email", "info",
                f"WA -> Gmail: respuesta enviada a {user.email}",
            )
        else:
            self.notification_service.mark_failed(notif.id, "Error al enviar por Gmail")

        return notif
