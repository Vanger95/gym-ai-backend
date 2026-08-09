from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.nutrition_agent import NutritionAgent
from app.core.config import get_settings
from app.database.session import get_db_session
from app.repositories.client_repository import ClientRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.nutrition import NutritionGenerateRequest, NutritionPlan
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_service import KnowledgeService


router = APIRouter(
    prefix="/nutrition",
    tags=["nutrition"],
)


@router.post(
    "/generate",
    response_model=NutritionPlan,
)
async def generate_nutrition_plan(
    request: NutritionGenerateRequest,
    session: AsyncSession = Depends(get_db_session),
) -> NutritionPlan:

    settings = get_settings()

    # Temporary until authentication is implemented.
    trainer_id = "demo-trainer"

    # 1. Find client
    client_repository = ClientRepository(session)

    client = await client_repository.get_by_id(
        request.client_id
    )

    if client is None or client.trainer_id != trainer_id:
        raise HTTPException(
            status_code=404,
            detail="Client not found.",
        )

    # 2. Create services
    document_repository = DocumentRepository(session)

    embedding_service = EmbeddingService(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    knowledge_service = KnowledgeService(
        repository=document_repository,
        embedding_service=embedding_service,
    )

    # 3. Retrieve relevant nutrition knowledge
    knowledge_chunks = await knowledge_service.search(
        query=(
            f"Nutrition guidance for an adult client with goal "
            f"{client.goal}, training "
            f"{client.training_days_per_week} days per week"
        ),
        trainer_id=trainer_id,
        top_k=5,
        category="nutrition",
    )

    if not knowledge_chunks:
        raise HTTPException(
            status_code=400,
            detail="No nutrition knowledge is available.",
        )

    # 4. Generate nutrition plan
    nutrition_agent = NutritionAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    try:
        plan = await nutrition_agent.generate(
            client=client,
            knowledge_chunks=knowledge_chunks,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Nutrition plan generation failed.",
        ) from error

    # 5. Validate AI-generated source IDs
    valid_source_ids = {
        chunk["chunk_id"]
        for chunk in knowledge_chunks
    }

    plan.source_chunk_ids = [
        source_id
        for source_id in plan.source_chunk_ids
        if source_id in valid_source_ids
    ]

    # 6. Validate 7-day plan
    if len(plan.meal_plan) != 7:
        raise HTTPException(
            status_code=500,
            detail="Generated nutrition plan must contain 7 days.",
        )

    return plan