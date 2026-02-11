from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import UserProfile
from uuid import UUID


class UserProfileRepo:
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id,
        display_name: str,
        birthdate=None,
        gender=None,
    ) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            display_name=display_name,
            birthdate=birthdate,
            gender=gender,
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: UUID) -> UserProfile | None:
        res = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return res.scalars().first()

    @staticmethod
    async def update_avatar(db: AsyncSession, user_id: UUID, avatar_url: str | None) -> UserProfile | None:
        profile = await UserProfileRepo.get_by_user_id(db, user_id)
        if not profile:
            return None
        profile.avatar_url = avatar_url
        await db.commit()
        await db.refresh(profile)
        return profile
