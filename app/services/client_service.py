import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientResponse


class ClientService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ClientRepository(session)

    async def create_client(
        self,
        payload: ClientCreate,
        trainer_id: str = "demo-trainer",
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
            available_equipment_json=json.dumps(payload.available_equipment),
            injuries_or_limitations_json=json.dumps(
                payload.injuries_or_limitations
            ),
            dietary_preferences_json=json.dumps(
                payload.dietary_preferences
            ),
            allergies_json=json.dumps(payload.allergies),
        )

        created_client = await self.repository.create(client)

        return ClientResponse(
            id=created_client.id,
            trainer_id=created_client.trainer_id,
            age=created_client.age,
            height_cm=created_client.height_cm,
            weight_kg=created_client.weight_kg,
            goal=created_client.goal,
            experience_level=created_client.experience_level,
            training_days_per_week=created_client.training_days_per_week,
            session_duration_minutes=created_client.session_duration_minutes,
            available_equipment=json.loads(
                created_client.available_equipment_json
            ),
            injuries_or_limitations=json.loads(
                created_client.injuries_or_limitations_json
            ),
            dietary_preferences=json.loads(
                created_client.dietary_preferences_json
            ),
            allergies=json.loads(created_client.allergies_json),
            created_at=created_client.created_at,
        )