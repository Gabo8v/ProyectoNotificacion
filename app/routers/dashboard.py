import logging
import math

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.limiter import limiter
from app.models.consulta import Consulta
from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.models.template import Template
from app.models.user import User
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")

PER_PAGE = 20


def _redirect(path: str, type: str, message: str) -> RedirectResponse:
    resp = RedirectResponse(url=path, status_code=303)
    resp.set_cookie(key="flash_type", value=type, httponly=True, samesite="lax", max_age=10)
    resp.set_cookie(key="flash_msg", value=message[:500], httponly=True, samesite="lax", max_age=10)
    return resp


def _get_flash(request: Request) -> dict | None:
    t = request.cookies.get("flash_type")
    m = request.cookies.get("flash_msg")
    if t and m:
        return {"type": t, "message": m}
    return None


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    consultas_total = 0
    consultas_respondidas = 0
    total = sent = pending = failed = 0
    total_users = total_templates = 0
    latest = []
    if user and user.role == "admin":
        total = db.query(Notification).count()
        sent = db.query(Notification).filter(Notification.status == NotificationStatus.SENT).count()
        pending = db.query(Notification).filter(Notification.status == NotificationStatus.PENDING).count()
        failed = db.query(Notification).filter(Notification.status == NotificationStatus.FAILED).count()
        total_users = db.query(User).count()
        total_templates = db.query(Template).count()
        latest = db.query(Notification).order_by(Notification.created_at.desc()).limit(10).all()
    if user:
        consultas_total = db.query(Consulta).filter(Consulta.user_id == user.id).count()
        consultas_respondidas = db.query(Consulta).filter(Consulta.user_id == user.id, Consulta.response.isnot(None)).count()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "flash": _get_flash(request),
        "user": user,
        "total": total,
        "sent": sent,
        "pending": pending,
        "failed": failed,
        "total_users": total_users,
        "total_templates": total_templates,
        "latest": latest,
        "consultas_total": consultas_total,
        "consultas_respondidas": consultas_respondidas,
    })


@router.get("/send")
def send_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/")
    users = db.query(User).order_by(User.name).all()
    tpls = db.query(Template).filter(Template.is_active == True).order_by(Template.name).all()
    pending_consultas = (
        db.query(Consulta)
        .filter(Consulta.response.is_(None))
        .order_by(Consulta.created_at.desc())
        .limit(20)
        .all()
    )
    return templates.TemplateResponse("send.html", {
        "request": request,
        "flash": _get_flash(request),
        "user": user,
        "users": users,
        "templates": tpls,
        "pending_consultas": pending_consultas,
    })


@router.post("/send")
@limiter.limit("5/minute")
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
        return _redirect("/dashboard/send", "success", f"Notificacion enviada{user_name}")
    except Exception as e:
        logger.error(f"Error al enviar notificacion: {e}")
        return _redirect("/dashboard/send", "error", "Error interno al enviar la notificacion")


@router.get("/templates")
def list_templates(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/")
    tpls = db.query(Template).order_by(Template.created_at.desc()).all()
    return templates.TemplateResponse("templates.html", {"request": request, "user": user, "templates": tpls, "flash": _get_flash(request)})


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
        logger.error(f"Error al crear template: {e}")
        return _redirect("/dashboard/templates", "error", "Error interno al crear el template")


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
    user = get_current_user(request)
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/")
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
        "user": user,
        "notifications": notifications,
        "page": page,
        "total_pages": total_pages,
    })


@router.get("/users")
def list_users(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard/")
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse("users.html", {
        "request": request,
        "flash": _get_flash(request),
        "user": user,
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
        logger.error(f"Error al crear usuario: {e}")
        return _redirect("/dashboard/users", "error", "Error interno al crear el usuario")


@router.post("/users/{user_id}/delete")
def delete_user(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request)
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        if current_user and str(current_user.id) == str(user.id):
            return _redirect("/dashboard/users", "error", "No puedes eliminarte a ti mismo")
        name = user.name
        db.delete(user)
        db.commit()
        return _redirect("/dashboard/users", "success", f"Usuario '{name}' eliminado")
    return _redirect("/dashboard/users", "error", "Usuario no encontrado")
