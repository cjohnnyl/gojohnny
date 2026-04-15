import json

from openai import APIError, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.training_feedback import TrainingFeedback
from ..models.training_plan import TrainingPlan
from ..models.runner_profile import RunnerProfile
from ..schemas.feedback import FeedbackCreate, FeedbackResponse
from ..services import ai, memory_service
from ..services.deps import get_current_user_id

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    request: Request,
    body: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    # Valida ownership do plan_id, se fornecido
    if body.plan_id is not None:
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.id == body.plan_id,
            TrainingPlan.user_id == current_user_id,
        ).first()
        if not plan:
            # Retorna 404 (não 403) para não confirmar existência do recurso
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planilha não encontrada",
            )

    profile = db.query(RunnerProfile).filter(RunnerProfile.user_id == current_user_id).first()

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
        user_id=current_user_id,
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

    # Atualiza memória com o novo feedback
    memory_service.update_after_feedback(
        user_id=current_user_id,
        effort=body.effort_rating,
        pain=body.pain_level,
        sleep=body.sleep_quality,
        feeling=body.general_feeling,
        recommendation=recommendation,
        db=db,
    )

    return feedback


@router.get("", response_model=list[FeedbackResponse])
def list_feedbacks(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    return (
        db.query(TrainingFeedback)
        .filter(TrainingFeedback.user_id == current_user_id)
        .order_by(TrainingFeedback.training_date.desc())
        .limit(30)
        .all()
    )


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    fb = db.query(TrainingFeedback).filter(
        TrainingFeedback.id == feedback_id,
        TrainingFeedback.user_id == current_user_id,
    ).first()
    if not fb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback não encontrado")
    return fb
