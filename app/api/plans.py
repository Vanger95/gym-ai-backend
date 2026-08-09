from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_trainer
from app.models.trainer import Trainer

from app.agents.nutrition_agent import NutritionAgent
from app.agents.workout_agent import WorkoutAgent
from app.core.config import get_settings
from app.database.session import get_db_session
from app.repositories.client_repository import ClientRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.plan_repository import PlanRepository
from app.schemas.plan import (
    GeneratePlanRequest,
    RegeneratePlanResponse,
    SavedPlanResponse,
)
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_service import KnowledgeService
from app.services.plan_service import PlanService


router = APIRouter(
    prefix="/plans",
    tags=["plans"],
)


def build_plan_service(
    session: AsyncSession,
) -> PlanService:
    settings = get_settings()

    client_repository = ClientRepository(
        session
    )

    document_repository = DocumentRepository(
        session
    )

    plan_repository = PlanRepository(
        session
    )

    embedding_service = EmbeddingService(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    knowledge_service = KnowledgeService(
        repository=document_repository,
        embedding_service=embedding_service,
    )

    workout_agent = WorkoutAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    nutrition_agent = NutritionAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    return PlanService(
        plan_repository=plan_repository,
        client_repository=client_repository,
        knowledge_service=knowledge_service,
        workout_agent=workout_agent,
        nutrition_agent=nutrition_agent,
    )


@router.post(
    "/generate",
    response_model=SavedPlanResponse,
)
async def generate_plan(
    request: GeneratePlanRequest,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> SavedPlanResponse:
    service = build_plan_service(
        session
    )
    trainer: Trainer = Depends(get_current_trainer)

    # extract trainer at runtime
    # FastAPI will inject trainer when this endpoint is called
    # get trainer id from dependency

    try:
        return await service.generate_and_save(
            client_id=request.client_id,
            trainer_id=trainer.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

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
    trainer: Trainer = Depends(get_current_trainer),
) -> list[SavedPlanResponse]:
    service = build_plan_service(session)
    return await service.list_plans(trainer_id=trainer.id)


@router.get(
    "/{plan_id}",
    response_model=SavedPlanResponse,
)
async def get_plan(
    plan_id: str,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> SavedPlanResponse:
    service = build_plan_service(session)

    plan = await service.get_plan(
        plan_id=plan_id,
        trainer_id=trainer.id,
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    return plan


@router.delete(
    "/{plan_id}",
    status_code=204,
)
async def delete_plan(
    plan_id: str,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> Response:
    service = build_plan_service(session)

    deleted = await service.delete_plan(
        plan_id=plan_id,
        trainer_id=trainer.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    return Response(
        status_code=204
    )


@router.post(
    "/{plan_id}/regenerate",
    response_model=RegeneratePlanResponse,
)
async def regenerate_plan(
    plan_id: str,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> RegeneratePlanResponse:
    service = build_plan_service(session)

    try:
        regenerated = (
            await service.regenerate_plan(
                plan_id=plan_id,
                trainer_id=trainer.id,
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Plan regeneration failed.",
        ) from error

    if regenerated is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    return regenerated