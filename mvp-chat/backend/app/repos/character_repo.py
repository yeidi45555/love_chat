from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Character


class CharacterRepo:
    @staticmethod
    async def list(db: AsyncSession) -> list[Character]:
        result = await db.execute(select(Character))
        return result.scalars().all()

    @staticmethod
    async def get(db: AsyncSession, character_id: str) -> Character | None:
        result = await db.execute(select(Character).where(Character.id == character_id))
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> Character:
        char = Character(**kwargs)
        db.add(char)
        await db.commit()
        await db.refresh(char)
        return char

    @staticmethod
    async def update(db: AsyncSession, char: Character, **kwargs) -> Character:
        for key, value in kwargs.items():
            if value is not None and hasattr(char, key):
                setattr(char, key, value)
        await db.commit()
        await db.refresh(char)
        return char

    @staticmethod
    async def delete(db: AsyncSession, char: Character) -> None:
        await db.delete(char)
        await db.commit()