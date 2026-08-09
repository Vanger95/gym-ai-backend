from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trainer import Trainer


class TrainerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, trainer: Trainer) -> Trainer:
        self.session.add(trainer)
        await self.session.commit()
        await self.session.refresh(trainer)
        return trainer

    async def get_by_email(self, email: str) -> Trainer | None:
        result = await self.session.execute(
            select(Trainer).where(Trainer.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, trainer_id: str) -> Trainer | None:
        result = await self.session.execute(
            select(Trainer).where(Trainer.id == trainer_id)
        )
        return result.scalar_one_or_none()