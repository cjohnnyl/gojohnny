from datetime import date
from typing import Optional
from pydantic import BaseModel


class ProfileCreate(BaseModel):
    name: str
    level: str = "beginner"  # beginner | intermediate | advanced
    weekly_volume_km: Optional[float] = None
    available_days_per_week: int = 3
    preferred_days: Optional[str] = None
    comfortable_pace: Optional[str] = None
    main_goal: Optional[str] = None
    target_race_name: Optional[str] = None
    target_race_distance_km: Optional[float] = None
    target_race_date: Optional[date] = None
    injury_history: Optional[str] = None
    physical_limitations: Optional[str] = None
    location: Optional[str] = None
    extra_context: Optional[str] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    weekly_volume_km: Optional[float] = None
    available_days_per_week: Optional[int] = None
    preferred_days: Optional[str] = None
    comfortable_pace: Optional[str] = None
    main_goal: Optional[str] = None
    target_race_name: Optional[str] = None
    target_race_distance_km: Optional[float] = None
    target_race_date: Optional[date] = None
    injury_history: Optional[str] = None
    physical_limitations: Optional[str] = None
    location: Optional[str] = None
    extra_context: Optional[str] = None


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
