import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.consulta import Consulta
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["consulta"])
templates = Jinja2Templates(directory="app/templates")


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


@router.get("/consulta")
def consulta_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    if user.role == "admin":
        return RedirectResponse(url="/dashboard/")
    consultas = db.query(Consulta).filter(Consulta.user_id == user.id).order_by(Consulta.created_at.desc()).all()
    return templates.TemplateResponse("consulta.html", {
        "request": request,
        "flash": _get_flash(request),
        "user": user,
        "consultas": consultas,
    })


@router.post("/consulta")
def consulta_create(
    request: Request,
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    if user.role == "admin":
        return RedirectResponse(url="/dashboard/")
    consulta = Consulta(user_id=user.id, subject=subject, message=message)
    db.add(consulta)
    db.commit()
    return _redirect("/dashboard/consulta", "success", "Consulta creada correctamente")
