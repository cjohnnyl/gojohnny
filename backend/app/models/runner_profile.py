from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class RunnerProfile(Base):
    """Perfil do corredor — contexto central que alimenta todas as recomendações."""

    __tablename__ = "runner_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)

    # Identificação básica
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Nível e experiência
    # beginner | intermediate | advanced
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")

    # Volume e disponibilidade
    weekly_volume_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # Dias disponíveis por semana (1-7)
    available_days_per_week: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    # Dias preferenciais: "seg,qua,sex" (texto livre por ora)
    preferred_days: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Pace (min/km) — ex: "6:30"
    comfortable_pace: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Objetivo principal
    # complete_5k | complete_10k | complete_21k | improve_time | consistency | other
    main_goal: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Prova alvo
    target_race_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    target_race_distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_race_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Histórico e limitações
    injury_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    physical_limitations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Localização (cidade/estado — texto livre)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Contexto adicional livre
    extra_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Nota: user_id agora referencia auth.users.id do Supabase (não mais a tabela users local)
