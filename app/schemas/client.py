from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FitnessGoal(StrEnum):
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    GENERAL_FITNESS = "general_fitness"


class ExperienceLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ClientBase(BaseModel):
    age: int = Field(ge=18, le=100)
    height_cm: float = Field(ge=120, le=230)
    weight_kg: float = Field(ge=35, le=300)

    goal: FitnessGoal
    experience_level: ExperienceLevel

    training_days_per_week: int = Field(ge=1, le=6)
    session_duration_minutes: int = Field(ge=20, le=120)

    available_equipment: list[str] = Field(default_factory=list)
    injuries_or_limitations: list[str] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)

    @field_validator(
        "available_equipment",
        "injuries_or_limitations",
        "dietary_preferences",
        "allergies",
    )
    @classmethod
    def clean_list_values(
        cls,
        values: list[str],
    ) -> list[str]:
        cleaned: list[str] = []

        for value in values:
            item = value.strip().lower()

            if item and item not in cleaned:
                cleaned.append(item)

        return cleaned


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trainer_id: str
    created_at: datetime