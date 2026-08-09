from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client


class ClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, client: Client) -> Client:
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def get_by_id(self, client_id: str) -> Client | None:
        result = await self.session.execute(
            select(Client).where(Client.id == client_id)
        )
        return result.scalar_one_or_none()

    async def list_by_trainer(
        self,
        trainer_id: str,
    ) -> list[Client]:
        result = await self.session.execute(
            select(Client)
            .where(Client.trainer_id == trainer_id)
            .order_by(Client.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_trainer(
        self,
        client_id: str,
        trainer_id: str,
    ) -> Client | None:
        result = await self.session.execute(
            select(Client).where(
                Client.id == client_id,
                Client.trainer_id == trainer_id,
            )
        )
        return result.scalar_one_or_none()