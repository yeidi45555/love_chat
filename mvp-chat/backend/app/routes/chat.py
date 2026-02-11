from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException
from app.auth.deps import get_current_user
from app.models import User
from app.repos.conversation_repo import ConversationRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.db import get_db
from app.core.rate_limit import limiter
from app.schemas.chat import ChatStreamIn
from app.services.chat_service import ChatService, QuotaExceededError
from app.repos.usage_repo import UsageRepo
from app.core.config import settings
from datetime import date, datetime, timedelta, timezone

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/stream")
@limiter.limit("30/minute")
async def chat_stream(
    payload: ChatStreamIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = await ConversationRepo.get_owned(db, payload.conversation_id, user.id)
    if not conv:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Comprobar cuota antes de empezar (evita 429 en medio del stream)
    today = date.today()
    usage = await UsageRepo.get_or_create(db, user.id, today)
    if usage.units_used >= settings.daily_units_limit:
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Daily quota exceeded",
                "units_used": usage.units_used,
                "units_limit": settings.daily_units_limit,
                "reset_at": tomorrow.isoformat(),
            },
        )

    service = ChatService()

    async def event_gen():
        try:
            full_text = ""

            async for token in service.stream(
                db=db,
                conversation_id=payload.conversation_id,
                user_id=user.id,
                user_text=payload.content,
            ):
                full_text += token

            yield {
                "event": "message",
                "data": full_text.strip()
            }

        except QuotaExceededError as e:
            yield {
                "event": "error",
                "data": str(e),
            }
        except Exception as e:
            yield {
                "event": "error",
                "data": str(e)
            }


    return EventSourceResponse(event_gen())
