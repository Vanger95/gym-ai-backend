from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.session import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.schemas.knowledge import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_service import KnowledgeService
from app.core.auth import get_current_trainer
from app.models.trainer import Trainer


router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
)


@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> KnowledgeSearchResponse:
    settings = get_settings()

    repository = DocumentRepository(session)

    embedding_service = EmbeddingService(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    service = KnowledgeService(
        repository=repository,
        embedding_service=embedding_service,
    )

    try:
        results = await service.search(
            query=request.query,
            trainer_id=trainer.id,
            top_k=request.top_k,
            category=request.category,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return KnowledgeSearchResponse(
        query=request.query,
        total_results=len(results),
        results=results,
    )