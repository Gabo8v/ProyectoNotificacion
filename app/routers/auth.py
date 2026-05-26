import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import create_jwt, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])

PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>Acceso - Notificaciones</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:oklch(0% 0 0);--surface:oklch(7% 0 0);--card:oklch(10% 0 0);--fg:oklch(88% 0 0);--muted:oklch(42% 0 0);--border:oklch(18% 0 0);--accent:oklch(100% 0 0);--radius:12px}
html,body{height:100%;background:var(--bg);color:var(--fg);font:15px/1.5 'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;font-feature-settings:'cv01','ss03';-webkit-font-smoothing:antialiased;display:grid;place-items:center;color-scheme:dark}
.card{width:380px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:40px 36px 36px}
.tabs{display:flex;margin-bottom:32px;border-bottom:1px solid var(--border)}
.tab{flex:1;background:none;border:none;color:var(--muted);font:13px/1 'Inter',sans-serif;letter-spacing:.04em;text-transform:uppercase;padding:0 0 12px;cursor:pointer;position:relative;transition:color .2s}
.tab::after{content:'';position:absolute;bottom:-1px;left:0;right:0;height:1px;background:transparent;transition:background .2s}
.tab.active{color:var(--fg)}.tab.active::after{background:var(--fg)}.tab:hover{color:var(--fg)}
.form{display:flex;flex-direction:column;gap:18px}.form.hidden{display:none}
.field{display:flex;flex-direction:column;gap:5px}
.field label{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.field input{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px 14px;color:var(--fg);font:14px/1.4 'Inter',sans-serif;outline:none;transition:border-color .2s,box-shadow .2s;width:100%}
.field input::placeholder{color:var(--muted);opacity:.6}
.field input:focus{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.btn{margin-top:6px;background:var(--fg);color:var(--bg);border:none;border-radius:8px;padding:13px;font:14px/1 'Inter',sans-serif;font-weight:600;letter-spacing:.02em;cursor:pointer;transition:opacity .2s}.btn:hover{opacity:.85}.btn:active{opacity:.7}
.alert{padding:10px 14px;border-radius:8px;margin-bottom:4px;font-size:13px;text-align:center}
.alert-error{background:rgba(239,68,68,.12);color:#ef4444;border:1px solid rgba(239,68,68,.2)}
.alert-success{background:rgba(16,185,129,.12);color:#10b981;border:1px solid rgba(16,185,129,.2)}
</style>
</head>
<body>
<div class="card">
<div class="tabs">
<button class="tab{tab_login_cls}" data-tab="login">Iniciar sesion</button>
<button class="tab{tab_reg_cls}" data-tab="register">Registrarse</button>
</div>
{alert_html}
<div id="form-login" class="form{form_login_cls}">
<form method="post" action="/login">
<div class="field">
<label for="login-user">Usuario</label>
<input type="text" id="login-user" name="username" placeholder="Tu nombre de usuario" autocomplete="username" required autofocus />
</div>
<div class="field">
<label for="login-pass">Contrasena</label>
<input type="password" id="login-pass" name="password" placeholder="........" autocomplete="current-password" required />
</div>
<button class="btn" type="submit">Iniciar sesion</button>
</form>
</div>
<div id="form-register" class="form{form_reg_cls}">
<form method="post" action="/register">
<div class="field">
<label for="reg-user">Usuario</label>
<input type="text" id="reg-user" name="username" placeholder="Elige un nombre de usuario" autocomplete="username" required />
</div>
<div class="field">
<label for="reg-pass">Contrasena</label>
<input type="password" id="reg-pass" name="password" placeholder="Minimo 8 caracteres" autocomplete="new-password" required />
</div>
<div class="field">
<label for="reg-email">Email</label>
<input type="email" id="reg-email" name="email" placeholder="correo@ejemplo.com" autocomplete="email" required />
</div>
<div class="field">
<label for="reg-whatsapp">WhatsApp</label>
<input type="tel" id="reg-whatsapp" name="phone" placeholder="+52 55 1234 5678" autocomplete="tel" required />
</div>
<button class="btn" type="submit">Crear cuenta</button>
</form>
</div>
</div>
<script>
(function(){var p=new URLSearchParams(location.search),tab=p.get('tab')||'login';['login','register'].forEach(function(t){var el=document.querySelector('[data-tab="'+t+'"]'),form=document.getElementById('form-'+t);if(t===tab){el.classList.add('active');form.classList.remove('hidden')}else{el.classList.remove('active');form.classList.add('hidden')}});document.querySelectorAll('.tab').forEach(function(t){t.addEventListener('click',function(){var target=this.getAttribute('data-tab');['login','register'].forEach(function(t2){var e=document.querySelector('[data-tab="'+t2+'"]'),f=document.getElementById('form-'+t2);if(t2===target){e.classList.add('active');f.classList.remove('hidden')}else{e.classList.remove('active');f.classList.add('hidden')}})})})})();
</script>
</body>
</html>"""


def _page(tab: str = "login", error: str = "", success: str = "") -> str:
    tab_login_cls = " active" if tab == "login" else ""
    tab_reg_cls = " active" if tab == "register" else ""
    form_login_cls = "" if tab == "login" else " hidden"
    form_reg_cls = "" if tab == "register" else " hidden"

    alerts = []
    if error:
        alerts.append(f'<div class="alert alert-error">{error}</div>')
    if success:
        alerts.append(f'<div class="alert alert-success">{success}</div>')
    alert_html = "\n".join(alerts)

    return PAGE \
        .replace("{tab_login_cls}", tab_login_cls) \
        .replace("{tab_reg_cls}", tab_reg_cls) \
        .replace("{form_login_cls}", form_login_cls) \
        .replace("{form_reg_cls}", form_reg_cls) \
        .replace("{alert_html}", alert_html)


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: str = "", success: str = "", tab: str = "login"):
    from app.auth import decode_jwt, get_current_user

    token = request.cookies.get("session")
    if token:
        payload = decode_jwt(token)
        if payload:
            user = get_current_user(request)
            if user:
                return RedirectResponse(url="/dashboard/", status_code=303)
    return HTMLResponse(_page(tab=tab, error=error, success=success))


@router.get("/register", response_class=HTMLResponse)
def register_form_redirect():
    return RedirectResponse(url="/login?tab=register", status_code=303)


@router.post("/login")
def login_post(username: str = Form(...), password: str = Form(...)):
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.name == username).first()
        if not user or not user.password_hash:
            return RedirectResponse(
                url="/login?error=Usuario+o+contrasena+incorrectos&tab=login",
                status_code=303,
            )
        if not verify_password(password, user.password_hash):
            return RedirectResponse(
                url="/login?error=Usuario+o+contrasena+incorrectos&tab=login",
                status_code=303,
            )
        if not user.is_active:
            return RedirectResponse(url="/login?error=Usuario+inactivo&tab=login", status_code=303)
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
            return RedirectResponse(
                url="/login?error=Usuario+o+email+ya+existen&tab=register",
                status_code=303,
            )
        user = User(
            name=username,
            email=email,
            phone=phone,
            role="user",
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        return RedirectResponse(
            url="/login?success=Cuenta+creada+correctamente&tab=login",
            status_code=303,
        )
    finally:
        db.close()


@router.post("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session", httponly=True, samesite="lax")
    return resp
