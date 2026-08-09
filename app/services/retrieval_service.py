import json
from typing import Any

from app.repositories.document_repository import DocumentRepository
from app.services.embedding_service import EmbeddingService
from app.utils.vector_utils import cosine_similarity


class RetrievalService:
    def __init__(
        self,
        repository: DocumentRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self.repository = repository
        self.embedding_service = embedding_service

    async def search(
        self,
        query: str,
        document_id: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError("Search query cannot be empty.")

        document = await self.repository.get_by_id(document_id)

        if document is None:
            raise ValueError("Document not found.")

        if document.status != "processed":
            raise ValueError("Document is not ready for search.")

        chunks = await self.repository.get_embedded_chunks(
            document_id=document_id,
        )

        if not chunks:
            raise ValueError("No embedded chunks found.")

        query_embeddings = (
            await self.embedding_service.generate_embeddings(
                [clean_query]
            )
        )

        query_embedding = json.loads(query_embeddings[0])

        results: list[dict[str, Any]] = []

        for chunk in chunks:
            if chunk.embedding_json is None:
                continue

            chunk_embedding = json.loads(
                chunk.embedding_json
            )

            score = cosine_similarity(
                query_embedding,
                chunk_embedding,
            )

            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity_score": score,
                }
            )

        results.sort(
            key=lambda item: item["similarity_score"],
            reverse=True,
        )

        return results[:top_k]