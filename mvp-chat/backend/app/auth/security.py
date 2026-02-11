from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from uuid import UUID
import secrets

from app.core.config import settings


#import hashlib

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def _now() -> datetime:
    return datetime.now(timezone.utc)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: UUID) -> str:
    exp = _now() + timedelta(minutes=settings.access_token_exp_minutes)
    payload = {"sub": str(user_id), "exp": exp, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: UUID) -> tuple[str, str, datetime]:
    # jti único para poder revocar/rotar
    jti = secrets.token_hex(32)  # 64 chars
    exp = _now() + timedelta(days=settings.jwt_refresh_days)
    payload = {"sub": str(user_id), "exp": exp, "type": "refresh", "jti": jti}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti, exp


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=settings.jwt_algorithm)
