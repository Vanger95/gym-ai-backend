import json

from openai import AsyncOpenAI
from app.core.config import get_settings


class EmbeddingService:
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        if not model:
            raise ValueError("OPENAI_EMBEDDING_MODEL is not configured.")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[str]:
        cleaned_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned_texts:
            return []

        response = await self.client.embeddings.create(
            model=self.model,
            input=cleaned_texts,
            encoding_format="float",
        )

        ordered_data = sorted(
            response.data,
            key=lambda item: item.index,
        )

        return [
            json.dumps(item.embedding)
            for item in ordered_data
        ]
    

    