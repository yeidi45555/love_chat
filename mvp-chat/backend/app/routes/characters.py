from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.repos.character_repo import CharacterRepo
from app.schemas.character import CharacterOut

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("", response_model=list[CharacterOut])
async def list_characters(db: AsyncSession = Depends(get_db)):
    characters = await CharacterRepo.list(db)
    return characters
