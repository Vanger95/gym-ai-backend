from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClientBase(BaseModel):
    age: int = Field(ge=13, le=100)
    height_cm: float = Field(gt=0, le=300)
    weight_kg: float = Field(gt=0, le=500)

    goal: str = Field(min_length=2, max_length=100)
    experience_level: str = Field(min_length=2, max_length=50)

    training_days_per_week: int = Field(ge=1, le=7)
    session_duration_minutes: int = Field(ge=10, le=300)

    available_equipment: list[str] = Field(default_factory=list)
    injuries_or_limitations: list[str] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trainer_id: str
    created_at: datetime