from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID | None
    channel: str
    status: str
    subject: str | None
    body: str
    created_at: datetime
    sent_at: datetime | None

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    user_id: UUID | None = None
    channel: str = "email"
    subject: str | None = None
    body: str
