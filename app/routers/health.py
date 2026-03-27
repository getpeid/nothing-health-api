from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, ScopeChecker
from app.models.user import User
from app.models.health import HeartRate, SleepRecord, SpO2Reading, StepRecord, Workout
from app.schemas.health import (
    HeartRateOut,
    SleepOut,
    SpO2Out,
    StepsOut,
    WorkoutOut,
    DataStalenessInfo,
)

router = APIRouter(prefix="/health", tags=["Health Data"])

PAGE_SIZE = 50


# -- Heart Rate --

@router.get("/heart_rate")
async def get_heart_rate(
    start: datetime | None = Query(None, description="ISO 8601 start time"),
    end: datetime | None = Query(None, description="ISO 8601 end time"),
    limit: int = Query(PAGE_SIZE, le=200),
    offset: int = Query(0, ge=0),
    _scope=Depends(ScopeChecker("heart_rate:read")),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(HeartRate).where(HeartRate.user_id == user.id)
    if start:
        query = query.where(HeartRate.timestamp >= start)
    if end:
        query = query.where(HeartRate.timestamp <= end)
    query = query.order_by(HeartRate.timestamp.desc()).offset(offset).limit(limit + 1)

    result = await db.execute(query)
    rows = result.scalars().all()
    has_more = len(rows) > limit
    data = [HeartRateOut.model_validate(r) for r in rows[:limit]]

    # Staleness info
    latest_sync = await db.execute(
        select(func.max(HeartRate.synced_at)).where(HeartRate.user_id == user.id)
    )

    return {
        "data": data,
        "has_more": has_more,
        "staleness": DataStalenessInfo(last_synced_at=latest_sync.scalar()),
    }


# -- Sleep --

@router.get("/sleep")
async def get_sleep(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(PAGE_SIZE, le=200),
    offset: int = Query(0, ge=0),
    _scope=Depends(ScopeChecker("sleep:read")),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SleepRecord).where(SleepRecord.user_id == user.id)
    if start:
        query = query.where(SleepRecord.start_time >= start)
    if end:
        query = query.where(SleepRecord.end_time <= end)
    query = query.order_by(SleepRecord.start_time.desc()).offset(offset).limit(limit + 1)

    result = await db.execute(query)
    rows = result.scalars().all()
    has_more = len(rows) > limit

    latest_sync = await db.execute(
        select(func.max(SleepRecord.synced_at)).where(SleepRecord.user_id == user.id)
    )

    return {
        "data": [SleepOut.model_validate(r) for r in rows[:limit]],
        "has_more": has_more,
        "staleness": DataStalenessInfo(last_synced_at=latest_sync.scalar()),
    }


# -- SpO2 --

@router.get("/spo2")
async def get_spo2(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(PAGE_SIZE, le=200),
    offset: int = Query(0, ge=0),
    _scope=Depends(ScopeChecker("spo2:read")),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SpO2Reading).where(SpO2Reading.user_id == user.id)
    if start:
        query = query.where(SpO2Reading.timestamp >= start)
    if end:
        query = query.where(SpO2Reading.timestamp <= end)
    query = query.order_by(SpO2Reading.timestamp.desc()).offset(offset).limit(limit + 1)

    result = await db.execute(query)
    rows = result.scalars().all()
    has_more = len(rows) > limit

    latest_sync = await db.execute(
        select(func.max(SpO2Reading.synced_at)).where(SpO2Reading.user_id == user.id)
    )

    return {
        "data": [SpO2Out.model_validate(r) for r in rows[:limit]],
        "has_more": has_more,
        "staleness": DataStalenessInfo(last_synced_at=latest_sync.scalar()),
    }


# -- Steps --

@router.get("/steps")
async def get_steps(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(PAGE_SIZE, le=200),
    offset: int = Query(0, ge=0),
    _scope=Depends(ScopeChecker("steps:read")),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(StepRecord).where(StepRecord.user_id == user.id)
    if start:
        query = query.where(StepRecord.date >= start)
    if end:
        query = query.where(StepRecord.date <= end)
    query = query.order_by(StepRecord.date.desc()).offset(offset).limit(limit + 1)

    result = await db.execute(query)
    rows = result.scalars().all()
    has_more = len(rows) > limit

    latest_sync = await db.execute(
        select(func.max(StepRecord.synced_at)).where(StepRecord.user_id == user.id)
    )

    return {
        "data": [StepsOut.model_validate(r) for r in rows[:limit]],
        "has_more": has_more,
        "staleness": DataStalenessInfo(last_synced_at=latest_sync.scalar()),
    }


# -- Workouts --

@router.get("/workouts")
async def get_workouts(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    workout_type: str | None = Query(None, description="Filter by type: running, cycling, etc."),
    limit: int = Query(PAGE_SIZE, le=200),
    offset: int = Query(0, ge=0),
    _scope=Depends(ScopeChecker("workouts:read")),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Workout).where(Workout.user_id == user.id)
    if start:
        query = query.where(Workout.start_time >= start)
    if end:
        query = query.where(Workout.end_time <= end)
    if workout_type:
        query = query.where(Workout.workout_type == workout_type)
    query = query.order_by(Workout.start_time.desc()).offset(offset).limit(limit + 1)

    result = await db.execute(query)
    rows = result.scalars().all()
    has_more = len(rows) > limit

    latest_sync = await db.execute(
        select(func.max(Workout.synced_at)).where(Workout.user_id == user.id)
    )

    return {
        "data": [WorkoutOut.model_validate(r) for r in rows[:limit]],
        "has_more": has_more,
        "staleness": DataStalenessInfo(last_synced_at=latest_sync.scalar()),
    }
