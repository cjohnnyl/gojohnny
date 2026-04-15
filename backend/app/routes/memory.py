"""Endpoints de gerenciamento de memória do corredor."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from ..core.database import get_db
from ..models.runner_memory import RunnerMemory
from ..services import memory_service
from ..services.deps import get_current_user_id

router = APIRouter()


class WeekProgressUpdate(BaseModel):
    """Atualizar progresso de um dia da semana."""
    day: str  # Ex: "segunda", "terça", etc
    status: str  # done | skipped | pending


class ObservationAdd(BaseModel):
    """Adicionar observação capturada no chat."""
    note: str  # Máx ~200 chars


class MemoryResponse(BaseModel):
    """Resposta com estado completo da memória."""
    user_id: str
    active_plan_id: int | None
    plan_week_current: int | None
    plan_week_total: int | None
    week_progress: dict | None
    recent_feedbacks: list | None
    physical_alerts: list | None
    load_adjustments: list | None
    chat_observations: list | None
    last_coaching_style: str | None
    last_session_summary: str | None
    last_session_at: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=MemoryResponse)
def get_memory(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Retorna memória completa do corredor."""
    memory = memory_service.get_or_create_memory(current_user_id, db)
    return memory


@router.patch("/week-progress", status_code=status.HTTP_200_OK)
def update_week_progress(
    body: WeekProgressUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Atualiza progresso de um dia da semana."""
    if body.status not in ["done", "skipped", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="status deve ser 'done', 'skipped' ou 'pending'",
        )

    memory_service.update_week_progress(current_user_id, body.day, body.status, db)
    return {"ok": True, "day": body.day, "status": body.status}


@router.patch("/observations", status_code=status.HTTP_200_OK)
def add_observation(
    body: ObservationAdd,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Adiciona observação capturada no chat."""
    if not body.note or len(body.note) > 200:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Observação deve ter entre 1 e 200 caracteres",
        )

    memory_service.add_chat_observation(current_user_id, body.note, db)
    return {"ok": True, "note": body.note}
