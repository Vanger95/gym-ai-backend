class TextChunker:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        cleaned_text = " ".join(text.split())

        if not cleaned_text:
            return []

        chunks: list[str] = []
        start = 0

        while start < len(cleaned_text):
            end = min(start + self.chunk_size, len(cleaned_text))
            chunk = cleaned_text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == len(cleaned_text):
                break

            start = end - self.chunk_overlap

        return chunks