import json

from openai import APIError, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..main import limiter, _get_user_id_from_token
from ..models.training_feedback import TrainingFeedback
from ..models.training_plan import TrainingPlan
from ..models.user import User
from ..schemas.feedback import FeedbackCreate, FeedbackResponse
from ..services import ai
from ..services.deps import get_current_user

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/hour", key_func=_get_user_id_from_token)
def submit_feedback(
    request: Request,
    body: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Valida ownership do plan_id, se fornecido
    if body.plan_id is not None:
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.id == body.plan_id,
            TrainingPlan.user_id == current_user.id,
        ).first()
        if not plan:
            # Retorna 404 (não 403) para não confirmar existência do recurso
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planilha não encontrada",
            )

    profile = current_user.profile

    # Analisa feedback com a IA (falha silenciosa — não bloqueia o registro)
    analysis = None
    recommendation = None
    try:
        raw, _ = ai.analyze_feedback(
            profile=profile,
            effort=body.effort_rating,
            pain=body.pain_level,
            sleep=body.sleep_quality,
            feeling=body.general_feeling,
            notes=body.notes,
        )
        try:
            parsed = json.loads(raw)
            analysis = parsed.get("analise")
            recommendation = parsed.get("recomendacao")
        except json.JSONDecodeError:
            analysis = raw
    except (BadRequestError, APIError) as e:
        logger.warning(
            f"OpenAI {type(e).__name__} (status={getattr(e, 'status_code', 'N/A')}) "
            "ao analisar feedback. Salvando sem análise."
        )

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
