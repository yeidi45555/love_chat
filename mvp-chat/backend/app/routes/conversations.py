from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.repos.character_repo import CharacterRepo
from app.repos.conversation_repo import ConversationRepo
from app.schemas.conversation import ConversationCreate, ConversationOut
from app.auth.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    """Lista las conversaciones del usuario autenticado (más recientes primero)."""
    return await ConversationRepo.list_by_user(db, user.id, limit=limit, offset=offset)


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conversation(payload: ConversationCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    ch = await CharacterRepo.get(db, payload.character_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Character not found")

    conv = await ConversationRepo.create(db, character_id=payload.character_id, user_id=user.id)
    return conv


@router.post("/{conversation_id}/reset")
async def reset_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    conv = await ConversationRepo.get_owned(db, conversation_id, user.id)
    if not conv:
        raise HTTPException(status_code=403, detail="Forbidden")

    # cerrar conversación actual
    await ConversationRepo.close(db, conv)

    # crear nueva con el mismo personaje
    new_conv = await ConversationRepo.create(
    db,
    character_id=conv.character_id,
    user_id=user.id,
    )
    return new_conv

