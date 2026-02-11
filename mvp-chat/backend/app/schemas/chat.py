from pydantic import BaseModel
from uuid import UUID

class ChatStreamIn(BaseModel):
    conversation_id: UUID
    content: str
