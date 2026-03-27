from datetime import datetime

from pydantic import BaseModel


# -- Heart Rate --

class HeartRateOut(BaseModel):
    id: str
    timestamp: datetime
    bpm: int
    source: str

    model_config = {"from_attributes": True}


# -- Sleep --

class SleepOut(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    deep_minutes: int | None
    light_minutes: int | None
    rem_minutes: int | None
    awake_minutes: int | None
    sleep_score: int | None

    model_config = {"from_attributes": True}


# -- SpO2 --

class SpO2Out(BaseModel):
    id: str
    timestamp: datetime
    percentage: float

    model_config = {"from_attributes": True}


# -- Steps --

class StepsOut(BaseModel):
    id: str
    date: datetime
    count: int
    distance_meters: float | None
    calories: float | None

    model_config = {"from_attributes": True}


# -- Workouts --

class WorkoutOut(BaseModel):
    id: str
    workout_type: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    calories: float | None
    avg_heart_rate: int | None
    max_heart_rate: int | None
    distance_meters: float | None
    summary: str | None

    model_config = {"from_attributes": True}


# -- Common --

class PaginatedResponse(BaseModel):
    data: list
    next_token: str | None = None
    has_more: bool = False


class DataStalenessInfo(BaseModel):
    """Included in responses to indicate data freshness."""
    last_synced_at: datetime | None
    sync_interval_minutes: int = 30
