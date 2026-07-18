from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse


ALLOWED_EXTENSIONS = {".pdf", ".txt"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
}

UPLOAD_DIRECTORY = Path("uploads")
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class InvalidDocumentError(Exception):
    pass


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = DocumentRepository(session)

    async def upload_document(
        self,
        file: UploadFile,
        category: str,
        trainer_id: str = "demo-trainer",
    ) -> DocumentResponse:
        if not file.filename:
            raise InvalidDocumentError("The uploaded file must have a filename.")

        original_filename = Path(file.filename).name
        extension = Path(original_filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise InvalidDocumentError(
                "Only PDF and TXT documents are supported."
            )

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidDocumentError(
                "The uploaded file has an unsupported content type."
            )

        file_contents = await file.read()

        if not file_contents:
            raise InvalidDocumentError("The uploaded file is empty.")

        if len(file_contents) > MAX_UPLOAD_SIZE_BYTES:
            raise InvalidDocumentError(
                "The uploaded file exceeds the 10 MB size limit."
            )

        UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4()}{extension}"
        stored_path = UPLOAD_DIRECTORY / stored_filename

        try:
            stored_path.write_bytes(file_contents)

            document = Document(
                 trainer_id=trainer_id,
                 filename=original_filename,
                 storage_path=str(stored_path),
                 content_type=file.content_type,
                 category=category,
                 status="uploaded",
            )

            created_document = await self.repository.create(document)

        except Exception:
            stored_path.unlink(missing_ok=True)
            raise

        finally:
            await file.close()

        return DocumentResponse.model_validate(created_document)