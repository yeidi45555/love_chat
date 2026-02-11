from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Character, Conversation, Message


class AdminRepo:
    @staticmethod
    async def get_metrics(db: AsyncSession) -> dict:
        """Retorna conteos de usuarios, personajes, conversaciones y mensajes."""
        users_res = await db.execute(select(func.count()).select_from(User))
        chars_res = await db.execute(select(func.count()).select_from(Character))
        convs_res = await db.execute(select(func.count()).select_from(Conversation))
        msgs_res = await db.execute(select(func.count()).select_from(Message))

        return {
            "users_count": users_res.scalar() or 0,
            "characters_count": chars_res.scalar() or 0,
            "conversations_count": convs_res.scalar() or 0,
            "messages_count": msgs_res.scalar() or 0,
        }
