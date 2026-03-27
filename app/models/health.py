import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HeartRate(Base):
    __tablename__ = "heart_rates"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    bpm: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(50), default="watch")  # watch, manual
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="heart_rates")


class SleepRecord(Base):
    __tablename__ = "sleep_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    deep_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    light_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rem_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    awake_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="sleep_records")


class SpO2Reading(Base):
    __tablename__ = "spo2_readings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    percentage: Mapped[float] = mapped_column(Float)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="spo2_readings")


class StepRecord(Base):
    __tablename__ = "step_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    count: Mapped[int] = mapped_column(Integer)
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="steps")


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    workout_type: Mapped[str] = mapped_column(String(50))  # running, cycling, swimming, etc.
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="workouts")


class SkinTemperature(Base):
    __tablename__ = "skin_temperatures"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    temperature_celsius: Mapped[float] = mapped_column(Float)
    deviation: Mapped[float | None] = mapped_column(Float, nullable=True)  # deviation from baseline
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="skin_temperatures")


class MenstrualCycle(Base):
    __tablename__ = "menstrual_cycles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    cycle_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    cycle_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cycle_length_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_length_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    predicted_ovulation: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    phase: Mapped[str | None] = mapped_column(String(30), nullable=True)  # menstrual, follicular, ovulation, luteal
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="menstrual_cycles")
