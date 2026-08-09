import json

from openai import AsyncOpenAI

from app.models.client import Client
from app.schemas.nutrition import NutritionPlan


class NutritionAgent:
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
    ) -> NutritionPlan:

        context = "\n\n".join(
            (
                f"[SOURCE: {chunk['chunk_id']}]\n"
                f"{chunk['content']}"
            )
            for chunk in knowledge_chunks
        )

        dietary_preferences = json.loads(
            client.dietary_preferences_json or "[]"
        )

        allergies = json.loads(
            client.allergies_json or "[]"
        )

        prompt = f"""
Create a practical general fitness nutrition plan for this adult client.

CLIENT PROFILE

Age: {client.age}
Height: {client.height_cm} cm
Weight: {client.weight_kg} kg
Goal: {client.goal}
Experience level: {client.experience_level}
Training days per week: {client.training_days_per_week}
Dietary preferences: {dietary_preferences}
Allergies: {allergies}

TRAINER KNOWLEDGE

{context}

RULES

- Use the supplied trainer knowledge where relevant.
- Respect all listed allergies.
- Respect dietary preferences.
- Keep recommendations practical and sustainable.
- Support the client's stated fitness goal.
- Do not prescribe extreme calorie restriction or overeating.
- Do not diagnose or treat medical conditions.
- Do not present the plan as medical nutrition therapy.
- Provide 7 days of practical meal suggestions.
- Avoid foods that conflict with reported allergies.
- source_chunk_ids may contain ONLY SOURCE IDs supplied above.
- Never invent source IDs.
- The plan requires trainer review before use.
"""

        response = await self.client.responses.parse(
            model=self.model,
            instructions=(
                "You are a general fitness nutrition planning assistant "
                "helping a gym instructor prepare practical nutrition "
                "guidance for adult clients. Do not provide medical "
                "nutrition treatment."
            ),
            input=prompt,
            text_format=NutritionPlan,
        )

        plan = response.output_parsed

        if plan is None:
            raise ValueError(
                "The AI did not return a valid nutrition plan."
            )

        return plan
    