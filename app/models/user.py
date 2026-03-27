import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nothing_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    heart_rates: Mapped[list["HeartRate"]] = relationship(back_populates="user")
    sleep_records: Mapped[list["SleepRecord"]] = relationship(back_populates="user")
    spo2_readings: Mapped[list["SpO2Reading"]] = relationship(back_populates="user")
    steps: Mapped[list["StepRecord"]] = relationship(back_populates="user")
    workouts: Mapped[list["Workout"]] = relationship(back_populates="user")
