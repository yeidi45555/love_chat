"""Rate limiting con slowapi. Por usuario (JWT) cuando hay auth, si no por IP."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.auth.security import decode_token


def _key_func(request: Request) -> str:
    """Identificador para rate limit: user_id si hay JWT válido, si no IP."""
    auth = request.headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            try:
                payload = decode_token(token)
                sub = payload.get("sub")
                if sub:
                    return f"user:{sub}"
            except Exception:
                pass
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=_key_func)
