from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import date


class UsageOut(BaseModel):
    """Cuota diaria de uso. Para el frontend."""
    units_used_today: int
    units_limit: int
    remaining: int
    reset_at: datetime


class MeOut(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str
    birthdate: date | None = None
    gender: str | None = None
    avatar_url: str | None = None
