from sqlalchemy import Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Character(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # ej: "luna"
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    tone: Mapped[str] = mapped_column(String(40), nullable=False, default="playful")
    dominance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    affection: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    explicit_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.4)

    boundaries: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
