from fastapi import Header, HTTPException, status

from app.core.config import settings


async def require_admin(x_admin_key: str | None = Header(None, alias="X-Admin-Key")):
    """Exige X-Admin-Key en el header. Solo funciona si ADMIN_SECRET está configurado."""
    if not settings.admin_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin panel not configured (ADMIN_SECRET not set)",
        )
    if not x_admin_key or x_admin_key != settings.admin_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Admin-Key",
        )
