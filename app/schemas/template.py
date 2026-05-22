from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TemplateOut(BaseModel):
    id: UUID
    name: str
    keywords: str
    subject: str | None
    body: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateCreate(BaseModel):
    name: str
    keywords: str
    subject: str | None = None
    body: str
