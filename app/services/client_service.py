import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientResponse


class ClientService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.repository = ClientRepository(session)

    async def create_client(
        self,
        payload: ClientCreate,
        trainer_id: str,
    ) -> ClientResponse:
        client = Client(
            trainer_id=trainer_id,
            age=payload.age,
            height_cm=payload.height_cm,
            weight_kg=payload.weight_kg,
            goal=payload.goal,
            experience_level=payload.experience_level,
            training_days_per_week=payload.training_days_per_week,
            session_duration_minutes=payload.session_duration_minutes,
            available_equipment_json=json.dumps(
                payload.available_equipment
            ),
            injuries_or_limitations_json=json.dumps(
                payload.injuries_or_limitations
            ),
            dietary_preferences_json=json.dumps(
                payload.dietary_preferences
            ),
            allergies_json=json.dumps(
                payload.allergies
            ),
        )

        created_client = await self.repository.create(
            client
        )

        return self._to_response(
            created_client
        )

    async def list_clients(
        self,
        trainer_id: str,
    ) -> list[ClientResponse]:
        clients = await self.repository.list_by_trainer(
            trainer_id=trainer_id
        )

        return [
            self._to_response(client)
            for client in clients
        ]

    async def get_client(
        self,
        client_id: str,
        trainer_id: str,
    ) -> ClientResponse | None:
        client = await self.repository.get_by_id_and_trainer(
            client_id=client_id,
            trainer_id=trainer_id,
        )

        if client is None:
            return None

        return self._to_response(
            client
        )

    def _to_response(
        self,
        client: Client,
    ) -> ClientResponse:
        return ClientResponse(
            id=client.id,
            trainer_id=client.trainer_id,
            age=client.age,
            height_cm=client.height_cm,
            weight_kg=client.weight_kg,
            goal=client.goal,
            experience_level=client.experience_level,
            training_days_per_week=client.training_days_per_week,
            session_duration_minutes=client.session_duration_minutes,
            available_equipment=json.loads(
                client.available_equipment_json or "[]"
            ),
            injuries_or_limitations=json.loads(
                client.injuries_or_limitations_json or "[]"
            ),
            dietary_preferences=json.loads(
                client.dietary_preferences_json or "[]"
            ),
            allergies=json.loads(
                client.allergies_json or "[]"
            ),
            created_at=client.created_at,
        )