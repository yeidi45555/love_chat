from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Message


class MessageRepo:
    @staticmethod
    async def create(db: AsyncSession, conversation_id, role: str, content: str) -> Message:
        msg = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg

    @staticmethod
    async def list_last(db: AsyncSession, conversation_id, limit: int = 12) -> list[Message]:
        # Trae los últimos N en DESC y luego invierte para devolverlos cronológicos
        q = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(q)
        items = list(result.scalars().all())
        return list(reversed(items))
