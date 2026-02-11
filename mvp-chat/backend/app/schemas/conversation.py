from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ConversationCreate(BaseModel):
    character_id: str


class ConversationOut(BaseModel):
    id: UUID
    character_id: str
    created_at: datetime

    class Config:
        from_attributes = True
