from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserDailyUsage


class UsageRepo:
    @staticmethod
    async def get_or_create(
        db: AsyncSession,
        user_id: UUID,
        usage_date: date,
    ) -> UserDailyUsage:
        res = await db.execute(
            select(UserDailyUsage).where(
                UserDailyUsage.user_id == user_id,
                UserDailyUsage.date == usage_date,
            )
        )
        row = res.scalars().first()
        if row:
            return row
        row = UserDailyUsage(user_id=user_id, date=usage_date, units_used=0)
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    @staticmethod
    async def add_units(
        db: AsyncSession,
        user_id: UUID,
        usage_date: date,
        units: int,
    ) -> UserDailyUsage:
        row = await UsageRepo.get_or_create(db, user_id, usage_date)
        row.units_used += units
        await db.commit()
        await db.refresh(row)
        return row
