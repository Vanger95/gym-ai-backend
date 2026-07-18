from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    trainer_id: Mapped[str] = mapped_column(
        String,
        index=True,
        default="demo-trainer",
    )

    age: Mapped[int] = mapped_column(Integer)
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)

    goal: Mapped[str] = mapped_column(String)
    experience_level: Mapped[str] = mapped_column(String)

    training_days_per_week: Mapped[int] = mapped_column(Integer)
    session_duration_minutes: Mapped[int] = mapped_column(Integer)

    available_equipment_json: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )
    injuries_or_limitations_json: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )
    dietary_preferences_json: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )
    allergies_json: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )