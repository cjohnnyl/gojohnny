from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: str = "beginner"  # beginner | intermediate | advanced
    weekly_volume_km: Optional[float] = Field(None, gt=0, le=500)
    available_days_per_week: int = Field(3, ge=1, le=7)
    preferred_days: Optional[str] = Field(None, max_length=100)
    comfortable_pace: Optional[str] = Field(None, max_length=10)
    main_goal: Optional[str] = None
    target_race_name: Optional[str] = Field(None, max_length=200)
    target_race_distance_km: Optional[float] = Field(None, gt=0)
    target_race_date: Optional[date] = None
    injury_history: Optional[str] = Field(None, max_length=500)
    physical_limitations: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    extra_context: Optional[str] = Field(None, max_length=500)


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    level: Optional[str] = None
    weekly_volume_km: Optional[float] = Field(None, gt=0, le=500)
    available_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    preferred_days: Optional[str] = Field(None, max_length=100)
    comfortable_pace: Optional[str] = Field(None, max_length=10)
    main_goal: Optional[str] = None
    target_race_name: Optional[str] = Field(None, max_length=200)
    target_race_distance_km: Optional[float] = Field(None, gt=0)
    target_race_date: Optional[date] = None
    injury_history: Optional[str] = Field(None, max_length=500)
    physical_limitations: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    extra_context: Optional[str] = Field(None, max_length=500)


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    level: str
    weekly_volume_km: Optional[float]
    available_days_per_week: int
    preferred_days: Optional[str]
    comfortable_pace: Optional[str]
    main_goal: Optional[str]
    target_race_name: Optional[str]
    target_race_distance_km: Optional[float]
    target_race_date: Optional[date]
    injury_history: Optional[str]
    physical_limitations: Optional[str]
    location: Optional[str]
    extra_context: Optional[str]

    model_config = {"from_attributes": True}
