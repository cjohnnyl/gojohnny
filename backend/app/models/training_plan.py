from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Date, DateTime, ForeignKey, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class TrainingPlan(Base):
    """Planilha semanal de treino gerada pelo GoJohnny."""

    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Semana de referência
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Plano em JSON estruturado
    # Formato: lista de dias com tipo_treino, km, pace_sugerido, orientacoes
    plan_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Contexto snapshot usado na geração (para rastreabilidade)
    context_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Status
    # active | superseded | archived
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    # Observações do treinador
    coach_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relacionamentos
    feedbacks: Mapped[list["TrainingFeedback"]] = relationship("TrainingFeedback", back_populates="plan")
