from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class TrainingFeedback(Base):
    """Feedback pós-treino fornecido pelo usuário."""

    __tablename__ = "training_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("training_plans.id"), nullable=True)

    training_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Percepção de esforço (1-10)
    effort_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Dor ou desconforto (0 = nenhum, 10 = intenso)
    pain_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Qualidade do sono (1-5)
    sleep_quality: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Sensação geral: great | good | ok | bad | very_bad
    general_feeling: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Notas livres do usuário
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Análise gerada pelo GoJohnny
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Recomendação de ajuste: maintain | reduce | increase
    load_recommendation: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relacionamentos
    plan: Mapped[Optional["TrainingPlan"]] = relationship("TrainingPlan", back_populates="feedbacks")
