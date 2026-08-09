import asyncio

from app.agents.nutrition_agent import NutritionAgent
from app.agents.workout_agent import WorkoutAgent
from app.models.client import Client
from app.schemas.plan import GeneratedPlan


class PlanCoordinator:
    def __init__(
        self,
        workout_agent: WorkoutAgent,
        nutrition_agent: NutritionAgent,
    ) -> None:
        self.workout_agent = workout_agent
        self.nutrition_agent = nutrition_agent

    async def generate(
        self,
        client: Client,
        workout_knowledge: list[dict],
        nutrition_knowledge: list[dict],
    ) -> GeneratedPlan:
        workout_task = asyncio.create_task(
            self.workout_agent.generate(
                client=client,
                knowledge_chunks=workout_knowledge,
            )
        )

        nutrition_task = asyncio.create_task(
            self.nutrition_agent.generate(
                client=client,
                knowledge_chunks=nutrition_knowledge,
            )
        )

        try:
            workout_plan, nutrition_plan = await asyncio.gather(
                workout_task,
                nutrition_task,
            )
        except Exception:
            workout_task.cancel()
            nutrition_task.cancel()
            raise

        valid_workout_sources = {
            chunk["chunk_id"]
            for chunk in workout_knowledge
        }

        valid_nutrition_sources = {
            chunk["chunk_id"]
            for chunk in nutrition_knowledge
        }

        workout_plan.source_chunk_ids = [
            source_id
            for source_id in workout_plan.source_chunk_ids
            if source_id in valid_workout_sources
        ]

        nutrition_plan.source_chunk_ids = [
            source_id
            for source_id in nutrition_plan.source_chunk_ids
            if source_id in valid_nutrition_sources
        ]

        return GeneratedPlan(
            client_id=client.id,
            workout=workout_plan,
            nutrition=nutrition_plan,
            requires_trainer_review=True,
            warnings=[
                "A qualified trainer must review this plan before use.",
                "Nutrition guidance is general fitness guidance, not medical advice.",
            ],
        )