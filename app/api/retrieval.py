from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.session import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.schemas.retrieval import (
    RetrievedChunkResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.core.auth import get_current_trainer
from app.models.trainer import Trainer


router = APIRouter(
    prefix="/documents",
    tags=["retrieval"],
)


@router.post(
    "/{document_id}/search",
    response_model=SemanticSearchResponse,
)
async def semantic_search(
    document_id: str,
    request: SemanticSearchRequest,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> SemanticSearchResponse:
    settings = get_settings()

    repository = DocumentRepository(session)

    # ensure trainer owns the document
    document = await repository.get_by_id(document_id)
    if document is None or document.trainer_id != trainer.id:
        raise HTTPException(status_code=404, detail="Document not found.")

    embedding_service = EmbeddingService(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    service = RetrievalService(
        repository=repository,
        embedding_service=embedding_service,
    )

    try:
        results = await service.search(
            query=request.query,
            document_id=document_id,
            top_k=request.top_k,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return SemanticSearchResponse(
        query=request.query,
        document_id=document_id,
        total_results=len(results),
        results=[
            RetrievedChunkResponse(**result)
            for result in results
        ],
    )