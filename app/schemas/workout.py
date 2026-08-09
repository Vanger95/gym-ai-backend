from pydantic import BaseModel, Field


class Exercise(BaseModel):
    name: str
    sets: int = Field(ge=1, le=10)
    reps: str
    rest_seconds: int = Field(ge=0, le=600)
    notes: str | None = None


class WorkoutDay(BaseModel):
    day_number: int = Field(ge=1, le=7)
    title: str
    focus: str
    exercises: list[Exercise]


class WorkoutPlan(BaseModel):
    summary: str
    weekly_schedule: list[WorkoutDay]
    progression_notes: str
    safety_notes: list[str]
    source_chunk_ids: list[str]

class WorkoutGenerateRequest(BaseModel):
    client_id: str