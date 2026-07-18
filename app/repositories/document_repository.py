from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_by_id(self, document_id: str) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, document: Document) -> None:
        await self.session.delete(document)
        await self.session.commit()

    async def create_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        self.session.add_all(chunks)
        await self.session.commit()
        for chunk in chunks:
            await self.session.refresh(chunk)
        return chunks
    
    async def update_status(self, document: Document, status: str) -> Document:
        document.status = status
        # self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document
    
    async def update_chunk_embeddings(self, chunks: list[DocumentChunk], embeddings: list[str]) -> list[DocumentChunk]:

        if len(chunks) != len(embeddings):
            raise ValueError("The length of chunks and embeddings must be the same.")
        
        for chunk, embedding_json in zip(chunks, embeddings, strict=True,):

            chunk.embedding_json = embedding_json

        await self.session.commit()

        for chunk in chunks:
            await self.session.refresh(chunk)

        # await self.session.commit()
        # await self.session.refresh(chunk)
        return chunks