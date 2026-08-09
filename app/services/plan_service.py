import json

from app.models.plan import Plan
from app.repositories.plan_repository import PlanRepository
from app.schemas.plan import GeneratedPlan, SavedPlanResponse


class PlanService:
    def __init__(
        self,
        repository: PlanRepository,
    ) -> None:
        self.repository = repository

    async def save_generated_plan(
        self,
        generated_plan: GeneratedPlan,
        trainer_id: str,
    ) -> SavedPlanResponse:
        workout_json = generated_plan.workout.model_dump_json()
        nutrition_json = generated_plan.nutrition.model_dump_json()

        sources = {
            "workout": generated_plan.workout.source_chunk_ids,
            "nutrition": generated_plan.nutrition.source_chunk_ids,
        }

        plan = Plan(
            trainer_id=trainer_id,
            client_id=generated_plan.client_id,
            workout_json=workout_json,
            nutrition_json=nutrition_json,
            sources_json=json.dumps(sources),
        )

        saved_plan = await self.repository.create(plan)

        return SavedPlanResponse(
            id=saved_plan.id,
            client_id=saved_plan.client_id,
            workout=generated_plan.workout,
            nutrition=generated_plan.nutrition,
            requires_trainer_review=generated_plan.requires_trainer_review,
            warnings=generated_plan.warnings,
            created_at=saved_plan.created_at,
        )

    async def get_plan(
        self,
        plan_id: str,
        trainer_id: str,
    ) -> SavedPlanResponse | None:
        plan = await self.repository.get_by_id(
            plan_id=plan_id,
            trainer_id=trainer_id,
        )

        if plan is None:
            return None

        workout = json.loads(plan.workout_json)
        nutrition = json.loads(plan.nutrition_json)

        return SavedPlanResponse(
            id=plan.id,
            client_id=plan.client_id,
            workout=workout,
            nutrition=nutrition,
            requires_trainer_review=True,
            warnings=[
                "A qualified trainer must review this plan before use.",
                "Nutrition guidance is general fitness guidance, not medical advice.",
            ],
            created_at=plan.created_at,
        )

    async def list_plans(
        self,
        trainer_id: str,
    ) -> list[SavedPlanResponse]:
        plans = await self.repository.list_by_trainer(
            trainer_id=trainer_id
        )

        return [
            SavedPlanResponse(
                id=plan.id,
                client_id=plan.client_id,
                workout=json.loads(plan.workout_json),
                nutrition=json.loads(plan.nutrition_json),
                requires_trainer_review=True,
                warnings=[
                    "A qualified trainer must review this plan before use.",
                    "Nutrition guidance is general fitness guidance, not medical advice.",
                ],
                created_at=plan.created_at,
            )
            for plan in plans
        ]