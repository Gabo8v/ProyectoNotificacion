from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/send", response_model=NotificationOut)
def send_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    service = NotificationService(db)
    notification = service.send(data)
    return notification


@router.get("/history", response_model=list[NotificationOut])
def get_history(
    channel: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    return service.get_history(channel=channel, status=status, limit=limit, offset=offset)
