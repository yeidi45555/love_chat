from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class CharacterCreate(BaseModel):
    id: str
    name: str
    avatar_url: str | None = None
    tone: str = "playful"
    dominance: float = 0.5
    affection: float = 0.5
    explicit_level: float = 0.4
    boundaries: list[str] = []


class CharacterUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None
    tone: str | None = None
    dominance: float | None = None
    affection: float | None = None
    explicit_level: float | None = None
    boundaries: list[str] | None = None


class UserAdminOut(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime
    display_name: str | None
    birthdate: date | None
    gender: str | None
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class UserToggleActive(BaseModel):
    is_active: bool


class MetricsOut(BaseModel):
    users_count: int
    characters_count: int
    conversations_count: int
    messages_count: int
