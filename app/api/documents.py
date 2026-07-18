from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    DocumentService,
    InvalidDocumentError,
)

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
) -> DocumentResponse:
    service = DocumentService(session)

    try:
        return await service.upload_document(
            file=file,
            category=category,
        )
    except InvalidDocumentError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error