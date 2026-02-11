from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepo:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        res = await db.execute(select(User).where(User.email == email))
        return res.scalars().first()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> User | None:
        res = await db.execute(select(User).where(User.id == user_id))
        return res.scalars().first()

    @staticmethod
    async def list_all(
        db: AsyncSession,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        res = await db.execute(
            select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        )
        return list(res.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def set_active(db: AsyncSession, user: User, is_active: bool) -> User:
        user.is_active = is_active
        await db.commit()
        await db.refresh(user)
        return user
