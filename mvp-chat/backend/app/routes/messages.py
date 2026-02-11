from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.auth.deps import get_current_user
from app.models import User
from app.repos.conversation_repo import ConversationRepo
from app.repos.message_repo import MessageRepo
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/conversations", tags=["messages"])


@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=201)
async def create_message(
    conversation_id: UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = await ConversationRepo.get_owned(db, conversation_id, user.id)
    if not conv:
        raise HTTPException(status_code=403, detail="Forbidden")

    msg = await MessageRepo.create(db, conversation_id=conversation_id, role=payload.role, content=payload.content)
    return msg


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = await ConversationRepo.get_owned(db, conversation_id, user.id)
    if not conv:
        raise HTTPException(status_code=403, detail="Forbidden")

    msgs = await MessageRepo.list_last(db, conversation_id, limit=limit)
    return msgs
