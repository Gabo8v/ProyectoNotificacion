import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.models.log import Log, LogLevel
from app.schemas.notification import NotificationCreate


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def send(self, data: NotificationCreate) -> Notification:
        notification = Notification(
            user_id=data.user_id,
            channel=NotificationChannel(data.channel),
            status=NotificationStatus.PENDING,
            subject=data.subject,
            body=data.body,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_sent(self, notification_id: uuid.UUID, external_id: str | None = None):
        notif = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if notif:
            notif.status = NotificationStatus.SENT
            notif.sent_at = datetime.utcnow()
            if external_id:
                notif.external_id = external_id
            self.db.commit()

    def mark_failed(self, notification_id: uuid.UUID, error: str):
        notif = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if notif:
            notif.status = NotificationStatus.FAILED
            notif.error_message = error
            self.db.commit()

    def get_history(
        self,
        channel: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        query = self.db.query(Notification)
        if channel:
            query = query.filter(Notification.channel == NotificationChannel(channel))
        if status:
            query = query.filter(Notification.status == NotificationStatus(status))
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    def log(self, channel: str | None, level: str, message: str, details: str | None = None):
        log = Log(
            channel=NotificationChannel(channel) if channel else None,
            level=LogLevel(level),
            message=message,
            details=details,
        )
        self.db.add(log)
        self.db.commit()

    def find_by_conversation_ref(self, ref: str) -> Notification | None:
        return (
            self.db.query(Notification)
            .filter(Notification.conversation_ref == ref)
            .order_by(Notification.created_at.desc())
            .first()
        )

    def get_user_by_email(self, email: str):
        from app.models.user import User
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_phone(self, phone: str):
        from app.models.user import User
        return self.db.query(User).filter(User.phone == phone).first()
