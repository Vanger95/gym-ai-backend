from app.services.chat_service import ChatService
from app.services.retrieval_service import RetrievalService


class RAGService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        chat_service: ChatService,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.chat_service = chat_service

    async def ask(
        self,
        question: str,
        document_id: str,
        top_k: int = 5,
    ) -> dict:
        retrieved_chunks = await self.retrieval_service.search(
            query=question,
            document_id=document_id,
            top_k=top_k,
        )

        contexts = [
            item["content"]
            for item in retrieved_chunks
        ]

        answer = await self.chat_service.answer_from_context(
            question=question,
            contexts=contexts,
        )

        sources = [
            {
                "chunk_id": item["chunk_id"],
                "document_id": item["document_id"],
                "chunk_index": item["chunk_index"],
                "similarity_score": item["similarity_score"],
            }
            for item in retrieved_chunks
        ]

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }