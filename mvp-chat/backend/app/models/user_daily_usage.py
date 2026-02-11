from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserDailyUsage(Base):
    """Unidades de uso por usuario y día. 1 token de texto ≈ 1 unidad (escalable a imagen/audio)."""

    __tablename__ = "user_daily_usage"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    date: Mapped[date] = mapped_column(Date(), primary_key=True)
    units_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
