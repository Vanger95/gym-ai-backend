from pydantic import BaseModel, Field


class MealSuggestion(BaseModel):
    meal_name: str
    foods: list[str]
    notes: str | None = None


class NutritionDay(BaseModel):
    day_number: int = Field(ge=1, le=7)
    meals: list[MealSuggestion]


class NutritionPlan(BaseModel):
    summary: str
    daily_guidance: list[str]
    meal_plan: list[NutritionDay]
    hydration_guidance: str
    progression_notes: str
    safety_notes: list[str]
    source_chunk_ids: list[str]


class NutritionGenerateRequest(BaseModel):
    client_id: str