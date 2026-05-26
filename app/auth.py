import logging
from datetime import datetime, timedelta, timezone

from fastapi import Request, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
JWT_SECRET = settings.token_encryption_key or settings.admin_password
JWT_EXPIRE_MINUTES = 480


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_jwt(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_admin_hashed_password() -> str:
    if not hasattr(get_admin_hashed_password, "_cache"):
        get_admin_hashed_password._cache = hash_password(settings.admin_password)
    return get_admin_hashed_password._cache


def require_auth(request: Request):
    from app.database import SessionLocal
    from app.models.user import User

    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Sesion invalida")
    username = payload.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Sesion invalida")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.name == username).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
        return payload
    finally:
        db.close()


def require_admin(request: Request):
    from app.database import SessionLocal
    from app.models.user import User

    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Sesion invalida")
    username = payload.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Sesion invalida")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.name == username).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Acceso solo para administradores")
        return payload
    finally:
        db.close()


def is_authenticated(request: Request) -> str | None:
    from app.database import SessionLocal
    from app.models.user import User

    token = request.cookies.get("session")
    if not token:
        return None
    payload = decode_jwt(token)
    if not payload:
        return None
    username = payload.get("user")
    if not username:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.name == username).first()
        if user and user.is_active:
            return user.role
        return None
    finally:
        db.close()


def get_current_user(request: Request):
    from app.database import SessionLocal
    from app.models.user import User

    token = request.cookies.get("session")
    if not token:
        return None
    payload = decode_jwt(token)
    if not payload:
        return None
    username = payload.get("user")
    if not username:
        return None
    db = SessionLocal()
    try:
        return db.query(User).filter(User.name == username).first()
    finally:
        db.close()
