from datetime import datetime

from pydantic import BaseModel

from app.schemas.nutrition import NutritionPlan
from app.schemas.workout import WorkoutPlan


class GeneratePlanRequest(BaseModel):
    client_id: str


class GeneratedPlan(BaseModel):
    client_id: str
    workout: WorkoutPlan
    nutrition: NutritionPlan
    requires_trainer_review: bool = True
    warnings: list[str]


class SavedPlanResponse(GeneratedPlan):
    id: str
    created_at: datetime