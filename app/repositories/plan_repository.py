from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan


class PlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, plan: Plan) -> Plan:
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_by_id(
        self,
        plan_id: str,
        trainer_id: str,
    ) -> Plan | None:
        result = await self.session.execute(
            select(Plan).where(
                Plan.id == plan_id,
                Plan.trainer_id == trainer_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_by_trainer(
        self,
        trainer_id: str,
    ) -> list[Plan]:
        result = await self.session.execute(
            select(Plan)
            .where(Plan.trainer_id == trainer_id)
            .order_by(Plan.created_at.desc())
        )

        return list(result.scalars().all())

    async def delete(self, plan: Plan) -> None:
        await self.session.delete(plan)
        await self.session.commit()