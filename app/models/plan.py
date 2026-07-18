from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Plan(Base):
    __tablename__ = "plans"

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

    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        index=True,
    )

    workout_json: Mapped[str] = mapped_column(Text)
    nutrition_json: Mapped[str] = mapped_column(Text)
    sources_json: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    client: Mapped["Client"] = relationship(
        back_populates="plans",
    )