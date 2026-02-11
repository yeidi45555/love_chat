from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repos.conversation_repo import ConversationRepo
from app.repos.message_repo import MessageRepo
from app.repos.character_repo import CharacterRepo
from app.repos.user_profile_repo import UserProfileRepo
from app.repos.usage_repo import UsageRepo
from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder
from app.services.guardrails import Guardrails
from app.services.usage import estimate_text_units
from uuid import UUID

MEMORY_LIMIT = 12


class QuotaExceededError(ValueError):
    """El usuario excedió su cuota diaria."""


class ChatService:
    def __init__(self):
        self.llm = LLMClient()

    async def stream(self, db: AsyncSession, conversation_id, user_id: UUID, user_text: str):
        profile = await UserProfileRepo.get_by_user_id(db, user_id)
        birthdate = profile.birthdate if profile else None
        Guardrails.validate_input(birthdate=birthdate, user_text=user_text)

        # Comprobar cuota antes de procesar
        today = date.today()
        usage = await UsageRepo.get_or_create(db, user_id, today)
        if usage.units_used >= settings.daily_units_limit:
            raise QuotaExceededError(
                f"Daily quota exceeded. Limit: {settings.daily_units_limit} units. "
                f"Used today: {usage.units_used}. Resets at midnight."
            )

        conv = await ConversationRepo.get(db, conversation_id)
        if not conv:
            raise ValueError("Conversation not found")

        character = await CharacterRepo.get(db, conv.character_id)
        if not character:
            raise ValueError("Character not found")

        system_prompt = PromptBuilder.build_system_prompt(character)

        # 1) guardar mensaje user
        await MessageRepo.create(db, conversation_id=conversation_id, role="user", content=user_text)

        # 2) memoria corta: últimos N mensajes (incluye el user que acabas de guardar)
        history = await MessageRepo.list_last(db, conversation_id, limit=MEMORY_LIMIT)

        # 3) construir messages[] para LLM
        llm_messages = [{"role": "system", "content": system_prompt}]
        llm_messages += [{"role": m.role, "content": m.content} for m in history]

        # 4) stream + persist assistant final
        chunks: list[str] = []
        async for token in self.llm.stream_reply(llm_messages):
            chunks.append(token)
            yield token

        final = "".join(chunks).strip()
        await MessageRepo.create(db, conversation_id=conversation_id, role="assistant", content=final)

        # Actualizar cuota (unidades = tokens estimados del output)
        units = estimate_text_units(final)
        if units > 0:
            await UsageRepo.add_units(db, user_id, today, units)
