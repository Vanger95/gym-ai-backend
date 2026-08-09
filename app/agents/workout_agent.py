import json

from openai import AsyncOpenAI

from app.models.client import Client
from app.schemas.workout import WorkoutPlan


class WorkoutAgent:
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(
        self,
        client: Client,
        knowledge_chunks: list[dict],
    ) -> WorkoutPlan:

        context = "\n\n".join(
            (
                f"[SOURCE: {chunk['chunk_id']}]\n"
                f"{chunk['content']}"
            )
            for chunk in knowledge_chunks
        )

        equipment = json.loads(
            client.available_equipment_json or "[]"
        )

        limitations = json.loads(
            client.injuries_or_limitations_json or "[]"
        )

        prompt = f"""
Create a practical workout plan for this adult client.

CLIENT PROFILE

Age: {client.age}
Height: {client.height_cm} cm
Weight: {client.weight_kg} kg
Goal: {client.goal}
Experience level: {client.experience_level}
Training days per week: {client.training_days_per_week}
Session duration: {client.session_duration_minutes} minutes
Available equipment: {equipment}
Reported limitations: {limitations}

TRAINER KNOWLEDGE

{context}

RULES

- Use the trainer knowledge where relevant.
- Generate exactly {client.training_days_per_week} workout days.
- Respect the client's available equipment.
- Respect reported injuries or limitations.
- Keep training appropriate for the client's experience level.
- Avoid excessive training volume.
- Do not diagnose medical conditions.
- Do not recommend dangerous exercises.
- source_chunk_ids may contain ONLY source IDs supplied above.
- Never invent source IDs.
- This plan requires trainer review before use.
"""

        response = await self.client.responses.parse(
            model=self.model,
            instructions=(
                "You are a fitness programming assistant helping "
                "a gym instructor prepare structured workout plans. "
                "Generate practical and conservative fitness programming."
            ),
            input=prompt,
            text_format=WorkoutPlan,
        )

        plan = response.output_parsed

        if plan is None:
            raise ValueError(
                "The AI did not return a valid workout plan."
            )

        return plan