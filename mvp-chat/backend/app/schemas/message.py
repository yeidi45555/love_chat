from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
