from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse

from app.models.document_chunk import DocumentChunk
from app.parsers.pdf_parser import PDFParser
from app.parsers.txt_parser import TXTParser
from app.processing.chunker import TextChunker
from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService


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
            # created_document = await self.repository.create(document)

            document = Document(
                 trainer_id=trainer_id,
                 filename=original_filename,
                 storage_path=str(stored_path),
                 content_type=file.content_type,
                 category=category,
                 status="uploaded",
            )
            created_document = await self.repository.create(document)

            created_document = await self.repository.update_status(
                 created_document,
                "processed",
            )

            if extension == ".pdf":
                extracted_text = PDFParser().extract_text(str(stored_path))
            else:
                extracted_text = TXTParser().extract_text(str(stored_path)) 

            chunk_texts = TextChunker(
                chunk_size=1000,
                chunk_overlap=150,
            ).split(extracted_text)

            if not chunk_texts:
                raise InvalidDocumentError(
                    "No readable text could be extracted from the document."
                )
            document_chunks = [
            DocumentChunk(
                document_id=created_document.id,
                chunk_index=index,
                content=chunk_text,
                page_number=None,
                embedding_json=None,
                )
                for index, chunk_text in enumerate(chunk_texts)
            ]   

            await self.repository.create_chunks(document_chunks)

            settings = get_settings()

            embedding_service = EmbeddingService(
                api_key=settings.openai_api_key,
                model=settings.openai_embedding_model,
            )

            embedding_json_values = await embedding_service.generate_embeddings(
                 [chunk.content for chunk in document_chunks]
            )

           

            await self.repository.create_chunks(document_chunks)

            # embedding_service = EmbeddingService(
            #     api_key=settings.openai_api_key,
            #     model=settings.openai_embedding_model,
            # )

            await self.repository.update_chunk_embeddings(
                document_chunks,
                embedding_json_values,
            )
            created_document = await self.repository.update_status(
                created_document,
                "processed",
            )         
            

        except Exception:
            if "created_document" is not None():
                try:
                    created_document = await self.repository.update_status(
                    created_document,
                    "failed",
                    )
                except Exception:
                    await self.repository.sesson.rollback()
                
            
            raise

        finally:
            await file.close()

        return DocumentResponse.model_validate(created_document)    