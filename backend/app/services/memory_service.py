"""Serviço de gerenciamento de memória do corredor para sessões de coaching."""
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session

from ..models.runner_memory import RunnerMemory


def get_or_create_memory(user_id: str, db: Session) -> RunnerMemory:
    """
    Busca ou cria memória para o usuário.
    """
    memory = db.query(RunnerMemory).filter(RunnerMemory.user_id == user_id).first()
    if not memory:
        memory = RunnerMemory(user_id=user_id)
        db.add(memory)
        db.commit()
        db.refresh(memory)
        logger.info(f"Memória criada para usuário {user_id}")
    return memory


def build_dynamic_context_block(memory: Optional[RunnerMemory]) -> str:
    """
    Monta bloco de contexto dinâmico da memória para injetar no prompt.
    Máximo ~1500 caracteres para não inflar o prompt.
    """
    if not memory:
        return ""

    lines = ["\n--- CONTEXTO DINÂMICO DO HISTÓRICO ---"]

    # Estado do plano
    if memory.active_plan_id:
        lines.append(f"Plano ativo: semana {memory.plan_week_current or '?'}/{memory.plan_week_total or '?'}")
        if memory.plan_started_at:
            lines.append(f"Plano iniciado em: {memory.plan_started_at}")

    # Progresso da semana
    if memory.week_progress:
        progress_str = ", ".join([f"{day}: {status}" for day, status in memory.week_progress.items()])
        lines.append(f"Progresso da semana: {progress_str}")

    # Feedbacks recentes (último)
    if memory.recent_feedbacks and len(memory.recent_feedbacks) > 0:
        last_fb = memory.recent_feedbacks[0]
        effort = last_fb.get("effort")
        pain = last_fb.get("pain")
        feeling = last_fb.get("feeling")
        date_fb = last_fb.get("date", "recentemente")
        feedback_desc = f"Último feedback ({date_fb}): "
        parts = []
        if effort:
            parts.append(f"esforço {effort}/10")
        if pain:
            parts.append(f"dor {pain}/10")
        if feeling:
            parts.append(f"sensação {feeling}")
        if parts:
            feedback_desc += ", ".join(parts)
            lines.append(feedback_desc)

    # Alertas físicos
    if memory.physical_alerts and len(memory.physical_alerts) > 0:
        alerts_list = [f"{a.get('location', 'desconhecido')}" for a in memory.physical_alerts]
        lines.append(f"Alertas físicos ativos: {', '.join(alerts_list)}")

    # Ajustes de carga recentes
    if memory.load_adjustments and len(memory.load_adjustments) > 0:
        last_adj = memory.load_adjustments[0]
        recommendation = last_adj.get("recommendation", "unknown")
        lines.append(f"Último ajuste de carga: {recommendation}")

    # Observações do chat
    if memory.chat_observations and len(memory.chat_observations) > 0:
        obs_list = [o.get("note", "") for o in memory.chat_observations[:3]]
        obs_list = [o for o in obs_list if o]
        if obs_list:
            lines.append(f"Observações capturadas: {'; '.join(obs_list)}")

    lines.append("--- FIM DO CONTEXTO DINÂMICO ---\n")

    context = "\n".join(lines)
    # Limita a 1500 chars
    if len(context) > 1500:
        context = context[:1450] + "...\n"
    return context


def update_after_feedback(
    user_id: str,
    effort: Optional[int],
    pain: Optional[int],
    sleep: Optional[int],
    feeling: Optional[str],
    recommendation: Optional[str],
    db: Session = None,
) -> None:
    """
    Atualiza memória após um feedback ser salvo.
    - Se pain >= 6: adiciona alerta físico
    - Se recommendation != 'maintain': registra ajuste de carga
    - Adiciona entrada compacta em recent_feedbacks (máx 3)
    """
    if not db:
        logger.warning("db não fornecido em update_after_feedback")
        return

    memory = get_or_create_memory(user_id, db)

    # 1. Adiciona entrada em recent_feedbacks
    today = datetime.utcnow().date().isoformat()
    new_fb = {
        "date": today,
        "effort": effort,
        "pain": pain,
        "sleep": sleep,
        "feeling": feeling,
    }

    recent = memory.recent_feedbacks or []
    if not isinstance(recent, list):
        recent = []
    recent.insert(0, new_fb)
    memory.recent_feedbacks = recent[:3]  # Mantém apenas 3 mais recentes

    # 2. Se pain >= 6, adiciona alerta físico (genérico — em produção seria mais específico)
    if pain is not None and pain >= 6:
        alerts = memory.physical_alerts or []
        if not isinstance(alerts, list):
            alerts = []
        # Evita duplicatas
        if not any(a.get("type") == "high_pain" and a.get("noted_at") == today for a in alerts):
            alerts.insert(0, {
                "type": "high_pain",
                "location": "genérico",
                "pain_level": pain,
                "noted_at": today,
            })
            memory.physical_alerts = alerts[:5]  # Mantém últimos 5

    # 3. Se recommendation != maintain, registra ajuste de carga
    if recommendation and recommendation != "maintain":
        adjustments = memory.load_adjustments or []
        if not isinstance(adjustments, list):
            adjustments = []
        adjustments.insert(0, {
            "date": today,
            "recommendation": recommendation,
            "reason": f"pain={pain}, effort={effort}",
        })
        memory.load_adjustments = adjustments[:5]  # Mantém últimos 5

    memory.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(memory)
    logger.info(f"Memória atualizada para usuário {user_id} após feedback")


def update_week_progress(
    user_id: str,
    day: str,
    status: str,  # done | skipped | pending
    db: Session = None,
) -> None:
    """
    Atualiza progresso da semana (ex: "segunda": "done").
    """
    if not db:
        logger.warning("db não fornecido em update_week_progress")
        return

    memory = get_or_create_memory(user_id, db)
    progress = memory.week_progress or {}
    if not isinstance(progress, dict):
        progress = {}

    progress[day] = status
    memory.week_progress = progress
    memory.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(memory)
    logger.info(f"Progresso da semana atualizado para {user_id}: {day} = {status}")


def add_chat_observation(
    user_id: str,
    note: str,
    db: Session = None,
) -> None:
    """
    Adiciona observação capturada no chat (máx 10 itens).
    """
    if not db:
        logger.warning("db não fornecido em add_chat_observation")
        return

    if not note or len(note) > 200:
        return

    memory = get_or_create_memory(user_id, db)
    observations = memory.chat_observations or []
    if not isinstance(observations, list):
        observations = []

    observations.insert(0, {
        "note": note,
        "captured_at": datetime.utcnow().isoformat(),
    })
    memory.chat_observations = observations[:10]  # Mantém últimas 10

    memory.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(memory)
    logger.debug(f"Observação adicionada para {user_id}")


def update_active_plan(
    user_id: str,
    plan_id: Optional[int],
    week_current: Optional[int],
    week_total: Optional[int],
    db: Session = None,
) -> None:
    """
    Atualiza referência ao plano ativo.
    """
    if not db:
        logger.warning("db não fornecido em update_active_plan")
        return

    memory = get_or_create_memory(user_id, db)
    memory.active_plan_id = plan_id
    memory.plan_week_current = week_current
    memory.plan_week_total = week_total
    if plan_id and not memory.plan_started_at:
        memory.plan_started_at = datetime.utcnow().date()
    memory.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(memory)
