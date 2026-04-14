import json
from datetime import date, timedelta

from openai import APIError, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.training_plan import TrainingPlan
from ..models.user import User
from ..services import ai
from ..services.deps import get_current_user

router = APIRouter()


def _current_week_bounds() -> tuple[date, date]:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # segunda-feira
    week_end = week_start + timedelta(days=6)             # domingo
    return week_start, week_end


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = current_user.profile
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Perfil não encontrado. Crie seu perfil em POST /profile antes de gerar a planilha.",
        )

    week_start, week_end = _current_week_bounds()

    # Arquiva planilha ativa da semana atual, se existir
    existing = (
        db.query(TrainingPlan)
        .filter(
            TrainingPlan.user_id == current_user.id,
            TrainingPlan.week_start == str(week_start),
            TrainingPlan.status == "active",
        )
        .first()
    )
    if existing:
        existing.status = "superseded"

    # Chama Claude Sonnet para gerar a planilha
    try:
        raw, tokens = ai.generate_training_plan(profile)
    except BadRequestError as e:
        logger.error(f"OpenAI BadRequest: {e}")
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED,
                            detail="Saldo insuficiente ou requisição inválida. Verifique sua conta OpenAI.")
    except APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Erro ao se comunicar com o modelo de IA. Tente novamente.")

    try:
        plan_data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao processar resposta da IA. Tente novamente.",
        )

    # Snapshot do contexto para rastreabilidade
    context_snapshot = {
        "level": profile.level,
        "weekly_volume_km": profile.weekly_volume_km,
        "available_days_per_week": profile.available_days_per_week,
        "comfortable_pace": profile.comfortable_pace,
        "main_goal": profile.main_goal,
        "target_race_date": str(profile.target_race_date) if profile.target_race_date else None,
    }

    plan = TrainingPlan(
        user_id=current_user.id,
        week_start=week_start,
        week_end=week_end,
        plan_data=plan_data.get("dias", plan_data),
        context_snapshot=context_snapshot,
        coach_notes=plan_data.get("coach_notes"),
        status="active",
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {
        "id": plan.id,
        "week_start": str(plan.week_start),
        "week_end": str(plan.week_end),
        "coach_notes": plan.coach_notes,
        "plan": plan.plan_data,
        "tokens_used": tokens,
    }


@router.get("/current")
def get_current_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    week_start, _ = _current_week_bounds()
    plan = (
        db.query(TrainingPlan)
        .filter(
            TrainingPlan.user_id == current_user.id,
            TrainingPlan.week_start == str(week_start),
            TrainingPlan.status == "active",
        )
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma planilha ativa para esta semana. Gere uma em POST /plans/generate.",
        )
    return {
        "id": plan.id,
        "week_start": str(plan.week_start),
        "week_end": str(plan.week_end),
        "coach_notes": plan.coach_notes,
        "plan": plan.plan_data,
    }


@router.get("")
def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plans = (
        db.query(TrainingPlan)
        .filter(TrainingPlan.user_id == current_user.id)
        .order_by(TrainingPlan.week_start.desc())
        .limit(12)
        .all()
    )
    return [
        {
            "id": p.id,
            "week_start": str(p.week_start),
            "week_end": str(p.week_end),
            "status": p.status,
            "coach_notes": p.coach_notes,
        }
        for p in plans
    ]
