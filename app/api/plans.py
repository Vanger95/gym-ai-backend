from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.coordinator import PlanCoordinator
from app.agents.nutrition_agent import NutritionAgent
from app.agents.workout_agent import WorkoutAgent
from app.core.config import get_settings
from app.database.session import get_db_session
from app.repositories.client_repository import ClientRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.plan_repository import PlanRepository
from app.schemas.plan import (
    GeneratePlanRequest,
    SavedPlanResponse,
)
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_service import KnowledgeService
from app.services.plan_service import PlanService


router = APIRouter(
    prefix="/plans",
    tags=["plans"],
)


@router.post(
    "/generate",
    response_model=SavedPlanResponse,
)
async def generate_plan(
    request: GeneratePlanRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SavedPlanResponse:
    settings = get_settings()

    # Temporary until authentication is implemented.
    trainer_id = "demo-trainer"

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

    workout_knowledge = await knowledge_service.search(
        query=(
            f"Workout programming for {client.goal}, "
            f"{client.experience_level}, "
            f"{client.training_days_per_week} days per week"
        ),
        trainer_id=trainer_id,
        top_k=5,
        category="workout",
    )

    nutrition_knowledge = await knowledge_service.search(
        query=(
            f"Nutrition guidance for {client.goal}, "
            f"adult client weighing {client.weight_kg} kg"
        ),
        trainer_id=trainer_id,
        top_k=5,
        category="nutrition",
    )

    if not workout_knowledge:
        raise HTTPException(
            status_code=400,
            detail="No workout knowledge is available.",
        )

    if not nutrition_knowledge:
        raise HTTPException(
            status_code=400,
            detail="No nutrition knowledge is available.",
        )

    workout_agent = WorkoutAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    nutrition_agent = NutritionAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    coordinator = PlanCoordinator(
        workout_agent=workout_agent,
        nutrition_agent=nutrition_agent,
    )

    try:
        generated_plan = await coordinator.generate(
            client=client,
            workout_knowledge=workout_knowledge,
            nutrition_knowledge=nutrition_knowledge,
        )

        plan_repository = PlanRepository(session)
        plan_service = PlanService(plan_repository)

        saved_plan = await plan_service.save_generated_plan(
            generated_plan=generated_plan,
            trainer_id=trainer_id,
        )

        return saved_plan

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Plan generation failed.",
        ) from error


@router.get(
    "",
    response_model=list[SavedPlanResponse],
)
async def list_plans(
    session: AsyncSession = Depends(get_db_session),
) -> list[SavedPlanResponse]:
    trainer_id = "demo-trainer"

    repository = PlanRepository(session)
    service = PlanService(repository)

    return await service.list_plans(
        trainer_id=trainer_id,
    )


@router.get(
    "/{plan_id}",
    response_model=SavedPlanResponse,
)
async def get_plan(
    plan_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> SavedPlanResponse:
    trainer_id = "demo-trainer"

    repository = PlanRepository(session)
    service = PlanService(repository)

    plan = await service.get_plan(
        plan_id=plan_id,
        trainer_id=trainer_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    return plan