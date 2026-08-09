from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class RetrievedChunkResponse(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    similarity_score: float


class SemanticSearchResponse(BaseModel):
    query: int
    document_id: int
    total_results: int
    results: list[RetrievedChunkResponse]