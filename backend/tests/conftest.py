"""
conftest.py — Fixtures compartilhadas para testes GoJohnny.
Todos os testes rodam sem servidor ativo e sem chamadas a APIs externas.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Garante que o módulo app seja encontrado
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# --- Patch de variáveis de ambiente antes de qualquer import da app ---
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake-key-for-tests")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_gojohnny.db")
os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "fake-anon-key")


@pytest.fixture
def mock_profile():
    """Fixture: perfil simulado de corredor."""
    from app.models.runner_profile import RunnerProfile
    profile = MagicMock(spec=RunnerProfile)
    profile.name = "João Corredor"
    profile.level = "intermediate"
    profile.main_goal = "complete_21k"
    profile.weekly_volume_km = 30.0
    profile.available_days_per_week = 4
    profile.preferred_days = "seg,qua,qui,sab"
    profile.comfortable_pace = "6:00"
    profile.target_race_name = "Meia de SP"
    profile.target_race_distance_km = 21.0
    profile.target_race_date = None
    profile.injury_history = None
    profile.physical_limitations = None
    profile.location = "São Paulo"
    profile.extra_context = None
    profile.user_id = "user-uuid-1234"
    return profile


@pytest.fixture
def mock_memory():
    """Fixture: memória simulada de corredor."""
    from app.models.runner_memory import RunnerMemory
    memory = MagicMock(spec=RunnerMemory)
    memory.active_plan_id = 1
    memory.plan_week_current = 2
    memory.plan_week_total = 8
    memory.plan_started_at = "2025-04-01"
    memory.week_progress = {"segunda": "done", "quarta": "pending"}
    memory.recent_feedbacks = [
        {"date": "2025-04-14", "effort": 7, "pain": 2, "feeling": "good"}
    ]
    memory.physical_alerts = []
    memory.load_adjustments = []
    memory.chat_observations = [
        {"note": "treina melhor de manhã", "captured_at": "2025-04-14T08:00:00"}
    ]
    memory.user_id = "user-uuid-1234"
    return memory


@pytest.fixture
def mock_db():
    """Fixture: sessão de banco de dados mockada."""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db
