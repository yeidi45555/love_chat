from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.repos.character_repo import CharacterRepo
from app.repos.user_repo import UserRepo
from app.repos.user_profile_repo import UserProfileRepo
from app.repos.admin_repo import AdminRepo
from app.schemas.character import CharacterOut
from app.admin.deps import require_admin
from app.admin.schemas import (
    CharacterCreate,
    CharacterUpdate,
    UserAdminOut,
    UserToggleActive,
    MetricsOut,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# ---- Métricas ----
@router.get("/metrics", response_model=MetricsOut)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Conteos de usuarios, personajes, conversaciones y mensajes."""
    return await AdminRepo.get_metrics(db)


# ---- CRUD Personajes ----
@router.get("/characters", response_model=list[CharacterOut])
async def list_characters_admin(db: AsyncSession = Depends(get_db)):
    """Lista todos los personajes."""
    return await CharacterRepo.list(db)


@router.post("/characters", response_model=CharacterOut, status_code=201)
async def create_character(payload: CharacterCreate, db: AsyncSession = Depends(get_db)):
    """Crea un personaje."""
    existing = await CharacterRepo.get(db, payload.id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Character {payload.id} already exists")
    return await CharacterRepo.create(
        db,
        id=payload.id,
        name=payload.name,
        avatar_url=payload.avatar_url,
        tone=payload.tone,
        dominance=payload.dominance,
        affection=payload.affection,
        explicit_level=payload.explicit_level,
        boundaries=payload.boundaries or [],
    )


@router.get("/characters/{character_id}", response_model=CharacterOut)
async def get_character_admin(character_id: str, db: AsyncSession = Depends(get_db)):
    """Obtiene un personaje por id."""
    char = await CharacterRepo.get(db, character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char


@router.patch("/characters/{character_id}", response_model=CharacterOut)
async def update_character(
    character_id: str,
    payload: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Actualiza un personaje (campos opcionales)."""
    char = await CharacterRepo.get(db, character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return char
    return await CharacterRepo.update(db, char, **updates)


@router.delete("/characters/{character_id}", status_code=204)
async def delete_character(character_id: str, db: AsyncSession = Depends(get_db)):
    """Elimina un personaje. Fallará si tiene conversaciones asociadas."""
    char = await CharacterRepo.get(db, character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    try:
        await CharacterRepo.delete(db, char)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete: character may have conversations. {e!s}",
        )


# ---- Gestión Usuarios ----
@router.get("/users", response_model=list[UserAdminOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Lista usuarios con su perfil."""
    users = await UserRepo.list_all(db, limit=limit, offset=offset)
    result = []
    for user in users:
        profile = await UserProfileRepo.get_by_user_id(db, user.id)
        result.append(
            UserAdminOut(
                id=user.id,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
                display_name=profile.display_name if profile else None,
                birthdate=profile.birthdate if profile else None,
                gender=profile.gender if profile else None,
                avatar_url=profile.avatar_url if profile else None,
            )
        )
    return result


@router.get("/users/{user_id}", response_model=UserAdminOut)
async def get_user_admin(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene un usuario por id."""
    user = await UserRepo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = await UserProfileRepo.get_by_user_id(db, user.id)
    return UserAdminOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        display_name=profile.display_name if profile else None,
        birthdate=profile.birthdate if profile else None,
        gender=profile.gender if profile else None,
        avatar_url=profile.avatar_url if profile else None,
    )


@router.patch("/users/{user_id}/active", response_model=UserAdminOut)
async def toggle_user_active(
    user_id: UUID,
    payload: UserToggleActive,
    db: AsyncSession = Depends(get_db),
):
    """Activa o desactiva un usuario."""
    user = await UserRepo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await UserRepo.set_active(db, user, payload.is_active)
    profile = await UserProfileRepo.get_by_user_id(db, user.id)
    return UserAdminOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        display_name=profile.display_name if profile else None,
        birthdate=profile.birthdate if profile else None,
        gender=profile.gender if profile else None,
        avatar_url=profile.avatar_url if profile else None,
    )

