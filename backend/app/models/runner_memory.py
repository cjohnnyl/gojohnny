"""Memória persistente do corredor — contexto dinâmico para sessões de coaching."""
from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, String, Integer, Date, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSON
from ..core.database import Base


class RunnerMemory(Base):
    """
    Armazena estado e histórico compacto do corredor para enriquecer prompts do coach.
    Uma entrada por usuário, atualizada após feedbacks e sessões.
    """

    __tablename__ = "runner_memory"

    id = Column(Integer, primary_key=True, index=True)

    # user_id do Supabase Auth (UUID como string)
    user_id = Column(String(36), unique=True, nullable=False, index=True)

    # --- ESTADO DO PLANO ---
    # ID da planilha ativa (se houver)
    active_plan_id = Column(Integer, nullable=True)
    # Semana atual do plano (1-based)
    plan_week_current = Column(Integer, nullable=True)
    # Número total de semanas do plano
    plan_week_total = Column(Integer, nullable=True)
    # Data de início do plano
    plan_started_at = Column(Date, nullable=True)

    # --- PROGRESSO DA SEMANA ---
    # JSON: {"segunda": "done", "terça": "skipped", "quarta": "pending", ...}
    # Valores: done | skipped | pending
    week_progress = Column(JSON, nullable=True)

    # --- HISTÓRICO COMPACTO ---
    # JSON: lista de até 3 feedbacks recentes
    # [{"date": "2025-04-14", "effort": 8, "pain": 3, "feeling": "good"}, ...]
    recent_feedbacks = Column(JSON, nullable=True)

    # --- ALERTAS E AJUSTES ---
    # JSON: lista de alertas físicos ativos
    # [{"type": "high_pain", "location": "joelho", "noted_at": "2025-04-14"}, ...]
    physical_alerts = Column(JSON, nullable=True)

    # JSON: histórico de ajustes de carga
    # [{"date": "2025-04-14", "recommendation": "reduce", "reason": "high pain"}, ...]
    load_adjustments = Column(JSON, nullable=True)

    # --- OBSERVAÇÕES DO CHAT ---
    # JSON: lista de observações capturadas no chat (máx 10)
    # [{"note": "treina melhor de manhã", "captured_at": "2025-04-14T10:30:00"}, ...]
    chat_observations = Column(JSON, nullable=True)

    # --- CONTEXTO DA ÚLTIMA SESSÃO ---
    # Estilo de coaching usado: motivador | técnico | desafiador | conservador
    last_coaching_style = Column(String(20), nullable=True)

    # Resumo/notas da última sessão
    last_session_summary = Column(Text, nullable=True)

    # Timestamp da última sessão
    last_session_at = Column(DateTime, nullable=True)

    # --- RASTREAMENTO ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
