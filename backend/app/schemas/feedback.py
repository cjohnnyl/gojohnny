from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    training_date: date
    plan_id: Optional[int] = None
    effort_rating: Optional[int] = Field(None, ge=1, le=10)
    pain_level: Optional[int] = Field(None, ge=0, le=10)
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)
    general_feeling: Optional[str] = None  # great | good | ok | bad | very_bad
    notes: Optional[str] = Field(None, max_length=1000)


class FeedbackResponse(BaseModel):
    id: int
    training_date: date
    effort_rating: Optional[int]
    pain_level: Optional[int]
    sleep_quality: Optional[int]
    general_feeling: Optional[str]
    notes: Optional[str]
    ai_analysis: Optional[str]
    load_recommendation: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
