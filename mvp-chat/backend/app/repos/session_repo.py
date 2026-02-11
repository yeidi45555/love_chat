from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserSession


class SessionRepo:
    @staticmethod
    async def create(db: AsyncSession, user_id, refresh_jti: str, refresh_token_hash: str, expires_at: datetime):
        s = UserSession(
            user_id=user_id,
            refresh_jti=refresh_jti,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
        )
        db.add(s)
        await db.commit()
        await db.refresh(s)
        return s

    @staticmethod
    async def get_by_jti(db: AsyncSession, jti: str) -> UserSession | None:
        res = await db.execute(select(UserSession).where(UserSession.refresh_jti == jti))
        return res.scalars().first()

    @staticmethod
    async def revoke(db: AsyncSession, session: UserSession):
        session.revoked_at = datetime.utcnow()
        await db.commit()
