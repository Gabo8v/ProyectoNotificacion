import math
import urllib.parse

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.models.template import Template
from app.models.user import User
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")

PER_PAGE = 20


def _redirect(path: str, type: str, message: str) -> RedirectResponse:
    params = urllib.parse.urlencode({"flash_type": type, "flash_msg": message})
    sep = "&" if "?" in path else "?"
    return RedirectResponse(url=f"{path}{sep}{params}", status_code=303)


def _get_flash(request: Request) -> dict | None:
    t = request.query_params.get("flash_type")
    m = request.query_params.get("flash_msg")
    if t and m:
        return {"type": t, "message": m}
    return None


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    total = db.query(Notification).count()
    sent = db.query(Notification).filter(Notification.status == NotificationStatus.SENT).count()
    pending = db.query(Notification).filter(Notification.status == NotificationStatus.PENDING).count()
    failed = db.query(Notification).filter(Notification.status == NotificationStatus.FAILED).count()
    total_users = db.query(User).count()
    total_templates = db.query(Template).count()
    latest = (
        db.query(Notification)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )
    return templates.TemplateResponse("index.html", {
        "request": request,
        "flash": _get_flash(request),
        "total": total,
        "sent": sent,
        "pending": pending,
        "failed": failed,
        "total_users": total_users,
        "total_templates": total_templates,
        "latest": latest,
    })


@router.get("/send")
def send_form(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.name).all()
    tpls = db.query(Template).filter(Template.is_active == True).order_by(Template.name).all()
    return templates.TemplateResponse("send.html", {
        "request": request,
        "flash": _get_flash(request),
        "users": users,
        "templates": tpls,
    })


@router.post("/send")
def send_notification(
    request: Request,
    channel: str = Form(...),
    user_id: str | None = Form(None),
    subject: str | None = Form(None),
    body: str = Form(...),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    try:
        notification = service.send(NotificationCreate(
            user_id=user_id if user_id else None,
            channel=channel,
            subject=subject,
            body=body,
        ))
        user_name = ""
        if user_id:
            u = db.query(User).filter(User.id == user_id).first()
            user_name = f" para {u.name}" if u else ""
        return _redirect("/dashboard/send", "success", f"Notificacion enviada{user_name} (ID: {notification.id})")
    except Exception as e:
        return _redirect("/dashboard/send", "error", f"Error: {e}")


@router.get("/templates")
def list_templates(request: Request, db: Session = Depends(get_db)):
    tpls = db.query(Template).order_by(Template.created_at.desc()).all()
    return templates.TemplateResponse("templates.html", {"request": request, "templates": tpls, "flash": _get_flash(request)})


@router.post("/templates")
def create_template(
    request: Request,
    name: str = Form(...),
    keywords: str = Form(...),
    subject: str | None = Form(None),
    body: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        template = Template(
            name=name,
            keywords=keywords,
            subject=subject,
            body=body,
        )
        db.add(template)
        db.commit()
        return _redirect("/dashboard/templates", "success", f"Template '{name}' creado")
    except Exception as e:
        return _redirect("/dashboard/templates", "error", f"Error: {e}")


@router.post("/templates/{template_id}/delete")
def delete_template(
    request: Request,
    template_id: str,
    db: Session = Depends(get_db),
):
    template = db.query(Template).filter(Template.id == template_id).first()
    if template:
        name = template.name
        db.delete(template)
        db.commit()
        return _redirect("/dashboard/templates", "success", f"Template '{name}' eliminado")
    return _redirect("/dashboard/templates", "error", "Template no encontrado")


@router.get("/history")
def history(
    request: Request,
    channel: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(Notification)
    if channel:
        query = query.filter(Notification.channel == NotificationChannel(channel))
    if status:
        query = query.filter(Notification.status == NotificationStatus(status))

    total = query.count()
    total_pages = max(1, math.ceil(total / PER_PAGE))
    offset = (page - 1) * PER_PAGE

    notifications = (
        query.order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(PER_PAGE)
        .all()
    )
    return templates.TemplateResponse("history.html", {
        "request": request,
        "flash": _get_flash(request),
        "notifications": notifications,
        "page": page,
        "total_pages": total_pages,
    })


@router.get("/users")
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse("users.html", {
        "request": request,
        "flash": _get_flash(request),
        "users": users,
    })


@router.post("/users")
def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        user = User(name=name, email=email, phone=phone)
        db.add(user)
        db.commit()
        return _redirect("/dashboard/users", "success", f"Usuario '{name}' creado")
    except Exception as e:
        return _redirect("/dashboard/users", "error", f"Error: {e}")


@router.post("/users/{user_id}/delete")
def delete_user(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        name = user.name
        db.delete(user)
        db.commit()
        return _redirect("/dashboard/users", "success", f"Usuario '{name}' eliminado")
    return _redirect("/dashboard/users", "error", "Usuario no encontrado")
