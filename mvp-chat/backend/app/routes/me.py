from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.core.config import settings
from app.auth.deps import get_current_user
from app.models import UserProfile, User
from app.repos.usage_repo import UsageRepo
from app.repos.user_profile_repo import UserProfileRepo
from app.schemas.user import MeOut, UsageOut
from app.services.storage import get_storage, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES

router = APIRouter(tags=["me"])


@router.get("/me", response_model=MeOut)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = res.scalars().first()

    return MeOut(
        id=user.id,
        email=user.email,
        display_name=profile.display_name if profile else "",
        birthdate=profile.birthdate if profile else None,
        gender=profile.gender if profile else None,
        avatar_url=profile.avatar_url if profile else None,
    )


@router.patch("/me/avatar", response_model=MeOut)
async def update_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sube o actualiza la foto de perfil del usuario."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (jpg, png, webp)")

    ext = (file.filename or "").split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 2 MB)")

    storage = get_storage()
    old_url = None
    profile = await UserProfileRepo.get_by_user_id(db, user.id)
    if profile and profile.avatar_url:
        old_url = profile.avatar_url

    avatar_url = storage.save(content, file.filename or "avatar.jpg", subdir="avatars")

    from app.services.storage import LocalStorageBackend
    if old_url and isinstance(storage, LocalStorageBackend):
        storage.delete(old_url)

    await UserProfileRepo.update_avatar(db, user.id, avatar_url)

    profile = await UserProfileRepo.get_by_user_id(db, user.id)
    return MeOut(
        id=user.id,
        email=user.email,
        display_name=profile.display_name if profile else "",
        birthdate=profile.birthdate if profile else None,
        gender=profile.gender if profile else None,
        avatar_url=avatar_url,
    )


@router.get("/me/usage", response_model=UsageOut)
async def get_usage(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Cuota diaria: unidades usadas, límite, restantes y cuándo se resetea."""
    today = date.today()
    usage = await UsageRepo.get_or_create(db, user.id, today)
    limit = settings.daily_units_limit
    remaining = max(0, limit - usage.units_used)
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return UsageOut(
        units_used_today=usage.units_used,
        units_limit=limit,
        remaining=remaining,
        reset_at=tomorrow,
    )
