import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import create_jwt, get_admin_hashed_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])

LOGIN_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login - Notificaciones</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#0f172a; color:#e2e8f0; min-height:100vh; display:flex; align-items:center; justify-content:center; }}
.card {{ background:#1e293b; padding:2.5rem; border-radius:12px; width:100%; max-width:400px; }}
h1 {{ text-align:center; margin-bottom:1.5rem; font-size:1.5rem; color:#f1f5f9; }}
label {{ display:block; margin-bottom:0.4rem; font-size:0.9rem; color:#94a3b8; }}
input {{ width:100%; padding:0.7rem 0.9rem; background:#0f172a; border:1px solid #334155; border-radius:8px; color:#e2e8f0; font-size:1rem; margin-bottom:1.2rem; }}
input:focus {{ outline:none; border-color:#3b82f6; }}
button {{ width:100%; padding:0.75rem; background:#3b82f6; border:none; border-radius:8px; color:white; font-size:1rem; font-weight:600; cursor:pointer; }}
button:hover {{ background:#2563eb; }}
.error {{ background:#7f1d1d; color:#fca5a5; padding:0.7rem; border-radius:8px; margin-bottom:1rem; text-align:center; font-size:0.9rem; }}
</style>
</head>
<body>
<div class="card">
<h1>Iniciar Sesion</h1>
{error_html}
<form method="post" action="/login">
<label for="username">Usuario</label>
<input type="text" id="username" name="username" required autofocus>
<label for="password">Contrasena</label>
<input type="password" id="password" name="password" required>
<button type="submit">Ingresar</button>
</form>
</div>
</body>
</html>"""


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: str = ""):
    token = request.cookies.get("session")
    if token:
        from app.auth import decode_jwt
        payload = decode_jwt(token)
        if payload:
            return RedirectResponse(url="/dashboard/", status_code=303)
    error_html = f'<div class="error">{error}</div>' if error else ""
    return HTMLResponse(LOGIN_PAGE.format(error_html=error_html))


@router.post("/login")
def login_post(username: str = Form(...), password: str = Form(...)):
    from app.config import settings
    if username != settings.admin_username:
        return RedirectResponse(url="/login?error=Usuario+o+contrasena+incorrectos", status_code=303)
    if not verify_password(password, get_admin_hashed_password()):
        return RedirectResponse(url="/login?error=Usuario+o+contrasena+incorrectos", status_code=303)
    token = create_jwt({"user": username})
    resp = RedirectResponse(url="/dashboard/", status_code=303)
    resp.set_cookie(
        key="session", value=token,
        httponly=True, samesite="lax",
        max_age=28800,
    )
    return resp


@router.post("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session", httponly=True, samesite="lax")
    return resp
