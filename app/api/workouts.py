from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.workout_agent import WorkoutAgent
from app.core.config import get_settings
from app.database.session import get_db_session
from app.repositories.client_repository import ClientRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.workout import WorkoutGenerateRequest, WorkoutPlan
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_service import KnowledgeService
from app.core.auth import get_current_trainer
from app.models.trainer import Trainer


router = APIRouter(
    prefix="/workouts",
    tags=["workouts"],
)


@router.post(
    "/generate",
    response_model=WorkoutPlan,
)
async def generate_workout(
    request: WorkoutGenerateRequest,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> WorkoutPlan:
    settings = get_settings()

    trainer_id = trainer.id

    client_repository = ClientRepository(session)

    client = await client_repository.get_by_id(
        request.client_id
    )

    if client is None or client.trainer_id != trainer_id:
        raise HTTPException(
            status_code=404,
            detail="Client not found.",
        )

    document_repository = DocumentRepository(session)

    embedding_service = EmbeddingService(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    knowledge_service = KnowledgeService(
        repository=document_repository,
        embedding_service=embedding_service,
    )

    knowledge_chunks = await knowledge_service.search(
        query=(
            f"Workout programming for a {client.experience_level} "
            f"client with goal {client.goal}, training "
            f"{client.training_days_per_week} days per week"
        ),
        trainer_id=trainer_id,
        top_k=5,
        category="workout",
    )

    if not knowledge_chunks:
        raise HTTPException(
            status_code=400,
            detail="No workout knowledge is available.",
        )

    workout_agent = WorkoutAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    try:
        plan = await workout_agent.generate(
            client=client,
            knowledge_chunks=knowledge_chunks,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Workout generation failed.",
        ) from error

    valid_source_ids = {
        chunk["chunk_id"]
        for chunk in knowledge_chunks
    }

    plan.source_chunk_ids = [
        source_id
        for source_id in plan.source_chunk_ids
        if source_id in valid_source_ids
    ]

    if len(plan.weekly_schedule) != client.training_days_per_week:
        raise HTTPException(
            status_code=500,
            detail="Generated workout plan has an invalid number of training days.",
        )

    return plan