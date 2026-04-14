import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.training_feedback import TrainingFeedback
from ..models.user import User
from ..schemas.feedback import FeedbackCreate, FeedbackResponse
from ..services import ai
from ..services.deps import get_current_user

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    body: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = current_user.profile

    # Analisa feedback com Claude
    raw, _ = ai.analyze_feedback(
        profile=profile,
        effort=body.effort_rating,
        pain=body.pain_level,
        sleep=body.sleep_quality,
        feeling=body.general_feeling,
        notes=body.notes,
    )

    analysis = None
    recommendation = None
    try:
        parsed = json.loads(raw)
        analysis = parsed.get("analise")
        recommendation = parsed.get("recomendacao")
    except json.JSONDecodeError:
        analysis = raw  # salva o texto bruto se o JSON falhar

    feedback = TrainingFeedback(
        user_id=current_user.id,
        plan_id=body.plan_id,
        training_date=body.training_date,
        effort_rating=body.effort_rating,
        pain_level=body.pain_level,
        sleep_quality=body.sleep_quality,
        general_feeling=body.general_feeling,
        notes=body.notes,
        ai_analysis=analysis,
        load_recommendation=recommendation,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("", response_model=list[FeedbackResponse])
def list_feedbacks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(TrainingFeedback)
        .filter(TrainingFeedback.user_id == current_user.id)
        .order_by(TrainingFeedback.training_date.desc())
        .limit(30)
        .all()
    )


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fb = db.query(TrainingFeedback).filter(
        TrainingFeedback.id == feedback_id,
        TrainingFeedback.user_id == current_user.id,
    ).first()
    if not fb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback não encontrado")
    return fb
