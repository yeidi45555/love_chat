from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.core.db import get_db
from app.repos.user_repo import UserRepo
from app.repos.user_profile_repo import UserProfileRepo
from app.schemas.auth import RegisterIn, LoginIn, TokenOut, RefreshIn
from app.repos.session_repo import SessionRepo
from app.auth.security import verify_password, create_access_token, create_refresh_token, hash_password
from app.auth.security import decode_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=201)
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    existing = await UserRepo.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = await UserRepo.create(db, email=payload.email, password_hash=hash_password(payload.password))
    await UserProfileRepo.create(
        db,
        user_id=user.id,
        display_name=payload.display_name,
        birthdate=payload.birthdate,
        gender=payload.gender,
    )

    token = create_access_token(str(user.id))



    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    user = await UserRepo.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(user.id)
    refresh, jti, exp = create_refresh_token(user.id)

    # Guardar refresh token hasheado (no en claro)
    await SessionRepo.create(
        db,
        user_id=user.id,
        refresh_jti=jti,
        refresh_token_hash=hash_password(refresh),
        expires_at=exp,
    )

    return TokenOut(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenOut)
async def refresh_token(payload: RefreshIn, db: AsyncSession = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = data.get("jti")
    user_id = data.get("sub")

    session = await SessionRepo.get_by_jti(db, jti)
    if not session or session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Session revoked")

    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Rotar: revocar el viejo
    await SessionRepo.revoke(db, session)

    # Emitir nuevos tokens
    access = create_access_token(user_id)
    refresh, new_jti, exp = create_refresh_token(user_id)

    await SessionRepo.create(
        db,
        user_id=user_id,
        refresh_jti=new_jti,
        refresh_token_hash=hash_password(refresh),
        expires_at=exp,
    )

    return TokenOut(access_token=access, refresh_token=refresh)


@router.post("/logout")
async def logout(payload: RefreshIn, db: AsyncSession = Depends(get_db)):
    """Revoca la sesión asociada al refresh token. Idempotente: si ya está revocada, responde 200."""
    try:
        data = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = data.get("jti")
    session = await SessionRepo.get_by_jti(db, jti)
    if session and session.revoked_at is None:
        await SessionRepo.revoke(db, session)

    return {"status": "ok"}