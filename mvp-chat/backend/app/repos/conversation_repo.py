from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Conversation
from sqlalchemy import select
from uuid import UUID


class ConversationRepo:
    @staticmethod
    async def create(db, character_id: str, user_id):
        conv = Conversation(
            character_id=character_id,
            user_id=user_id,
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    
    @staticmethod
    async def get(db: AsyncSession, conversation_id) -> Conversation | None:
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        return result.scalars().first()
    
    @staticmethod
    async def close(db: AsyncSession, conv: Conversation) -> None:
        conv.status = "closed"
        await db.commit()

    @staticmethod
    async def get_owned(db: AsyncSession, conversation_id: UUID, user_id: UUID) -> Conversation | None:
        res = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        return res.scalars().first()

    @staticmethod
    async def list_by_user(
        db: AsyncSession,
        user_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
