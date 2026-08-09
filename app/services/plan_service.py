import json

from app.agents.coordinator import PlanCoordinator
from app.agents.nutrition_agent import NutritionAgent
from app.agents.workout_agent import WorkoutAgent
from app.models.client import Client
from app.models.plan import Plan
from app.repositories.client_repository import ClientRepository
from app.repositories.plan_repository import PlanRepository
from app.schemas.plan import (
    GeneratedPlan,
    RegeneratePlanResponse,
    SavedPlanResponse,
)
from app.services.knowledge_service import KnowledgeService


class PlanService:
    def __init__(
        self,
        plan_repository: PlanRepository,
        client_repository: ClientRepository,
        knowledge_service: KnowledgeService,
        workout_agent: WorkoutAgent,
        nutrition_agent: NutritionAgent,
    ) -> None:
        self.plan_repository = plan_repository
        self.client_repository = client_repository
        self.knowledge_service = knowledge_service
        self.workout_agent = workout_agent
        self.nutrition_agent = nutrition_agent

    async def generate_and_save(
        self,
        client_id: str,
        trainer_id: str,
    ) -> SavedPlanResponse:
        client = await self.client_repository.get_by_id(
            client_id
        )

        if client is None:
            raise ValueError("Client not found.")

        if client.trainer_id != trainer_id:
            raise ValueError("Client not found.")

        generated_plan = await self._generate_plan(
            client=client,
            trainer_id=trainer_id,
        )

        return await self.save_generated_plan(
            generated_plan=generated_plan,
            trainer_id=trainer_id,
        )

    async def _generate_plan(
        self,
        client: Client,
        trainer_id: str,
    ) -> GeneratedPlan:
        workout_knowledge = await self.knowledge_service.search(
            query=(
                f"Workout programming for {client.goal}, "
                f"{client.experience_level}, "
                f"{client.training_days_per_week} days per week"
            ),
            trainer_id=trainer_id,
            top_k=5,
            category="workout",
        )

        nutrition_knowledge = await self.knowledge_service.search(
            query=(
                f"Nutrition guidance for {client.goal}, "
                f"adult client weighing {client.weight_kg} kg"
            ),
            trainer_id=trainer_id,
            top_k=5,
            category="nutrition",
        )

        if not workout_knowledge:
            raise ValueError(
                "No workout knowledge is available."
            )

        if not nutrition_knowledge:
            raise ValueError(
                "No nutrition knowledge is available."
            )

        coordinator = PlanCoordinator(
            workout_agent=self.workout_agent,
            nutrition_agent=self.nutrition_agent,
        )

        generated_plan = await coordinator.generate(
            client=client,
            workout_knowledge=workout_knowledge,
            nutrition_knowledge=nutrition_knowledge,
        )

        return generated_plan

    async def save_generated_plan(
        self,
        generated_plan: GeneratedPlan,
        trainer_id: str,
    ) -> SavedPlanResponse:
        workout_json = (
            generated_plan.workout.model_dump_json()
        )

        nutrition_json = (
            generated_plan.nutrition.model_dump_json()
        )

        sources = {
            "workout": (
                generated_plan.workout.source_chunk_ids
            ),
            "nutrition": (
                generated_plan.nutrition.source_chunk_ids
            ),
        }

        plan = Plan(
            trainer_id=trainer_id,
            client_id=generated_plan.client_id,
            workout_json=workout_json,
            nutrition_json=nutrition_json,
            sources_json=json.dumps(sources),
        )

        saved_plan = await self.plan_repository.create(
            plan
        )

        return SavedPlanResponse(
            id=saved_plan.id,
            client_id=saved_plan.client_id,
            workout=generated_plan.workout,
            nutrition=generated_plan.nutrition,
            requires_trainer_review=(
                generated_plan.requires_trainer_review
            ),
            warnings=generated_plan.warnings,
            created_at=saved_plan.created_at,
        )

    async def get_plan(
        self,
        plan_id: str,
        trainer_id: str,
    ) -> SavedPlanResponse | None:
        plan = await self.plan_repository.get_by_id(
            plan_id=plan_id,
            trainer_id=trainer_id,
        )

        if plan is None:
            return None

        return self._to_response(plan)

    async def list_plans(
        self,
        trainer_id: str,
    ) -> list[SavedPlanResponse]:
        plans = await self.plan_repository.list_by_trainer(
            trainer_id
        )

        return [
            self._to_response(plan)
            for plan in plans
        ]

    async def delete_plan(
        self,
        plan_id: str,
        trainer_id: str,
    ) -> bool:
        plan = await self.plan_repository.get_by_id(
            plan_id=plan_id,
            trainer_id=trainer_id,
        )

        if plan is None:
            return False

        await self.plan_repository.delete(plan)

        return True

    async def regenerate_plan(
        self,
        plan_id: str,
        trainer_id: str,
    ) -> RegeneratePlanResponse | None:
        old_plan = await self.plan_repository.get_by_id(
            plan_id=plan_id,
            trainer_id=trainer_id,
        )

        if old_plan is None:
            return None

        client = await self.client_repository.get_by_id(
            old_plan.client_id
        )

        if client is None:
            raise ValueError(
                "The client associated with this plan was not found."
            )

        if client.trainer_id != trainer_id:
            raise ValueError(
                "The client associated with this plan was not found."
            )

        generated_plan = await self._generate_plan(
            client=client,
            trainer_id=trainer_id,
        )

        new_plan = await self.save_generated_plan(
            generated_plan=generated_plan,
            trainer_id=trainer_id,
        )

        return RegeneratePlanResponse(
            id=new_plan.id,
            client_id=new_plan.client_id,
            workout=new_plan.workout,
            nutrition=new_plan.nutrition,
            requires_trainer_review=(
                new_plan.requires_trainer_review
            ),
            warnings=new_plan.warnings,
            created_at=new_plan.created_at,
            regenerated_from_plan_id=plan_id,
        )

    def _to_response(
        self,
        plan: Plan,
    ) -> SavedPlanResponse:
        return SavedPlanResponse(
            id=plan.id,
            client_id=plan.client_id,
            workout=json.loads(
                plan.workout_json
            ),
            nutrition=json.loads(
                plan.nutrition_json
            ),
            requires_trainer_review=True,
            warnings=[
                (
                    "A qualified trainer must review "
                    "this plan before use."
                ),
                (
                    "Nutrition guidance is general fitness "
                    "guidance, not medical advice."
                ),
            ],
            created_at=plan.created_at,
        )