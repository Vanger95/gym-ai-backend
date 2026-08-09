from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.session import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.schemas.qa import (
    AskDocumentRequest,
    AskDocumentResponse,
)
from app.services.chat_service import ChatService
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService


router = APIRouter(
    prefix="/documents",
    tags=["RAG"],
)


@router.post(
    "/{document_id}/ask",
    response_model=AskDocumentResponse,
)
async def ask_document(
    document_id: str,
    request: AskDocumentRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AskDocumentResponse:
    settings = get_settings()

    repository = DocumentRepository(session)

    embedding_service = EmbeddingService(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    retrieval_service = RetrievalService(
        repository=repository,
        embedding_service=embedding_service,
    )

    chat_service = ChatService(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        chat_service=chat_service,
    )

    try:
        result = await rag_service.ask(
            question=request.question,
            document_id=document_id,
            top_k=request.top_k,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return AskDocumentResponse(**result)