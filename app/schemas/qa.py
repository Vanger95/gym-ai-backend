from pydantic import BaseModel, Field


class AskDocumentRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class AnswerSource(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    similarity_score: float


class AskDocumentResponse(BaseModel):
    question: str
    answer: str
    sources: list[AnswerSource]