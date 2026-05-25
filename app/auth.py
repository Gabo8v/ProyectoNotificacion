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
JWT_EXPIRE_MINUTES = 480  # 8 horas


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
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = decode_jwt(token)
    if not payload or payload.get("user") != settings.admin_username:
        raise HTTPException(status_code=401, detail="Sesion invalida")
    return payload


def is_authenticated(request: Request) -> bool:
    token = request.cookies.get("session")
    if not token:
        return False
    payload = decode_jwt(token)
    return bool(payload and payload.get("user") == settings.admin_username)
