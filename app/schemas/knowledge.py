from typing import Literal

from pydantic import BaseModel, Field


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    category: Literal[
        "workout",
        "nutrition",
        "general",
    ] | None = None


class KnowledgeSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    category: str
    chunk_index: int
    page_number: int | None
    content: str
    similarity_score: float


class KnowledgeSearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[KnowledgeSearchResult]