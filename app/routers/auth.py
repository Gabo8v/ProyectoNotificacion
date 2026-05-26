import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import create_jwt, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])

PAGE_HEAD = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>{title} - Notificaciones</title>
<!-- PAGE_HEAD v2 -->
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,sans-serif; background:#0d0d0d; color:#e5e5e5; min-height:100vh; display:flex; align-items:center; justify-content:center; }}
.card {{ background:#1a1a1a; padding:2.5rem; border-radius:12px; width:100%; max-width:400px; border:1px solid #2a2a2a; }}
h1 {{ text-align:center; margin-bottom:1.5rem; font-size:1.3rem; font-weight:600; color:#e5e5e5; }}
label {{ display:block; margin-bottom:0.3rem; font-size:0.8rem; color:#888; }}
input {{ width:100%; padding:0.6rem 0.8rem; background:#0d0d0d; border:1px solid #2a2a2a; border-radius:6px; color:#e5e5e5; font-size:0.9rem; margin-bottom:1rem; outline:none; transition:border-color 0.15s; }}
input:focus {{ border-color:#3b82f6; }}
button {{ width:100%; padding:0.6rem; background:#3b82f6; border:none; border-radius:6px; color:white; font-size:0.9rem; font-weight:500; cursor:pointer; }}
button:hover {{ background:#2563eb; }}
.error {{ background:#2a0a0a; color:#ef4444; padding:0.6rem 0.8rem; border-radius:6px; margin-bottom:1rem; text-align:center; font-size:0.82rem; border:1px solid #4a1a1a; }}
.success {{ background:#0a2a1a; color:#22c55e; padding:0.6rem 0.8rem; border-radius:6px; margin-bottom:1rem; text-align:center; font-size:0.82rem; border:1px solid #1a4a2a; }}
.link {{ text-align:center; margin-top:1rem; font-size:0.82rem; }}
.link a {{ color:#3b82f6; text-decoration:none; }}
.link a:hover {{ text-decoration:underline; }}
</style>
</head>
<body>
<div class="card">
"""

PAGE_TAIL = """</div>
</body>
</html>"""

LOGIN_FORM = """<h1>Iniciar Sesion</h1>
{error_html}
<form method="post" action="/login">
<label for="username">Usuario</label>
<input type="text" id="username" name="username" required autofocus>
<label for="password">Contrasena</label>
<input type="password" id="password" name="password" required>
<button type="submit">Ingresar</button>
</form>
<div class="link"><a href="/register">Crear cuenta nueva</a></div>"""

REGISTER_FORM = """<h1>Crear Cuenta</h1>
{error_html}
<form method="post" action="/register">
<label for="username">Nombre de usuario</label>
<input type="text" id="username" name="username" required autofocus>
<label for="password">Contrasena</label>
<input type="password" id="password" name="password" required>
<label for="email">Email</label>
<input type="email" id="email" name="email" required>
<label for="phone">WhatsApp (codigo pais + numero, ej: 5493875123456)</label>
<input type="text" id="phone" name="phone" required placeholder="5493875123456">
<button type="submit">Registrarse</button>
</form>
<div class="link"><a href="/login">Ya tengo cuenta</a></div>"""


def _page(title: str, body: str) -> str:
    return PAGE_HEAD.format(title=title) + body + PAGE_TAIL


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: str = ""):
    from app.auth import decode_jwt, get_current_user

    token = request.cookies.get("session")
    if token:
        payload = decode_jwt(token)
        if payload:
            user = get_current_user(request)
            if user:
                return RedirectResponse(url="/dashboard/", status_code=303)
    error_html = f'<div class="error">{error}</div>' if error else ""
    return HTMLResponse(_page("Iniciar Sesion", LOGIN_FORM.format(error_html=error_html)))


@router.post("/login")
def login_post(username: str = Form(...), password: str = Form(...)):
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.name == username).first()
        if not user or not user.password_hash:
            return RedirectResponse(url="/login?error=Usuario+o+contrasena+incorrectos", status_code=303)
        if not verify_password(password, user.password_hash):
            return RedirectResponse(url="/login?error=Usuario+o+contrasena+incorrectos", status_code=303)
        if not user.is_active:
            return RedirectResponse(url="/login?error=Usuario+inactivo", status_code=303)
        token = create_jwt({"user": username, "role": user.role})
        resp = RedirectResponse(url="/dashboard/", status_code=303)
        resp.set_cookie(
            key="session", value=token,
            httponly=True, samesite="lax",
            max_age=28800,
        )
        return resp
    finally:
        db.close()


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request, error: str = ""):
    error_html = f'<div class="error">{error}</div>' if error else ""
    return HTMLResponse(_page("Crear Cuenta", REGISTER_FORM.format(error_html=error_html)))


@router.post("/register")
def register_post(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
):
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        existing = db.query(User).filter(
            (User.name == username) | (User.email == email)
        ).first()
        if existing:
            return RedirectResponse(url="/register?error=Usuario+o+email+ya+existen", status_code=303)
        user = User(
            name=username,
            email=email,
            phone=phone,
            role="user",
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        return RedirectResponse(url="/login?error=Cuenta+creada+correctamente", status_code=303)
    finally:
        db.close()


@router.post("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session", httponly=True, samesite="lax")
    return resp
