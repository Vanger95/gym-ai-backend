import json
from typing import Any

from app.repositories.document_repository import DocumentRepository
from app.services.embedding_service import EmbeddingService
from app.utils.vector_utils import cosine_similarity


class KnowledgeService:
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
        trainer_id: str,
        top_k: int = 5,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError("Search query cannot be empty.")

        categories: list[str] | None = None

        if category == "workout":
            categories = ["workout", "general"]

        elif category == "nutrition":
            categories = ["nutrition", "general"]

        elif category == "general":
            categories = ["general"]

        chunk_rows = (
            await self.repository.get_trainer_embedded_chunks(
                trainer_id=trainer_id,
                categories=categories,
            )
        )

        if not chunk_rows:
            return []

        query_embeddings = (
            await self.embedding_service.generate_embeddings(
                [clean_query]
            )
        )

        if not query_embeddings:
            raise ValueError(
                "Could not generate query embedding."
            )

        query_embedding = json.loads(
            query_embeddings[0]
        )

        results: list[dict[str, Any]] = []

        for chunk, document in chunk_rows:
            if chunk.embedding_json is None:
                continue

            try:
                chunk_embedding = json.loads(
                    chunk.embedding_json
                )

                score = cosine_similarity(
                    query_embedding,
                    chunk_embedding,
                )

            except (ValueError, TypeError, json.JSONDecodeError):
                continue

            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "filename": document.filename,
                    "category": document.category,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                    "content": chunk.content,
                    "similarity_score": score,
                }
            )

        results.sort(
            key=lambda item: item["similarity_score"],
            reverse=True,
        )

        return results[:top_k]