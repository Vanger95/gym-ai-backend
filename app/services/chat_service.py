from openai import AsyncOpenAI


class ChatService:
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def answer_from_context(
        self,
        question: str,
        contexts: list[str],
    ) -> str:
        context_text = "\n\n".join(
            f"[Context {index + 1}]\n{content}"
            for index, content in enumerate(contexts)
        )

        instructions = """
You are a document question-answering assistant.

Answer using the supplied context.

Rules:
- Ground the answer in the provided context.
- Do not invent information that is not supported by the context.
- If the context is insufficient, clearly say so.
- Keep the answer concise and clear.
"""

        input_text = f"""
Context:

{context_text}

Question:
{question}
"""

        response = await self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=input_text,
        )

        return response.output_text.strip()