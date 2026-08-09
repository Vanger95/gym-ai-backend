from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    DocumentService,
    InvalidDocumentError,
)
from app.core.auth import get_current_trainer
from app.models.trainer import Trainer

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> DocumentResponse:
    service = DocumentService(session)

    try:
        return await service.upload_document(
            file=file,
            category=category,
            trainer_id=trainer.id,
        )
    except InvalidDocumentError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error



@router.get(
    "",
    response_model=list[DocumentResponse],
)
async def list_documents(
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> list[DocumentResponse]:
    service = DocumentService(session)

    return await service.list_documents(trainer_id=trainer.id)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> DocumentResponse:
    service = DocumentService(session)

    document = await service.get_document(
        document_id=document_id,
        trainer_id=trainer.id,
    )

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> Response:
    service = DocumentService(session)

    deleted = await service.delete_document(
        document_id=document_id,
        trainer_id=trainer.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)