"""
test_memory_service.py — Valida funções críticas do memory_service.

Verifica existência, assinaturas e lógica básica das funções do serviço de memória.
Roda sem servidor e sem banco de dados real.
"""
import inspect
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime


@pytest.fixture(scope="module")
def memory_service():
    """Importa o módulo memory_service."""
    from app.services import memory_service
    return memory_service


class TestFuncoesExistem:
    """Valida que todas as funções críticas existem no memory_service."""

    def test_get_or_create_memory_existe(self, memory_service):
        assert hasattr(memory_service, "get_or_create_memory"), (
            "memory_service deve ter 'get_or_create_memory'"
        )

    def test_build_dynamic_context_block_existe(self, memory_service):
        assert hasattr(memory_service, "build_dynamic_context_block"), (
            "memory_service deve ter 'build_dynamic_context_block'"
        )

    def test_update_after_feedback_existe(self, memory_service):
        assert hasattr(memory_service, "update_after_feedback"), (
            "memory_service deve ter 'update_after_feedback'"
        )

    def test_update_week_progress_existe(self, memory_service):
        assert hasattr(memory_service, "update_week_progress"), (
            "memory_service deve ter 'update_week_progress'"
        )

    def test_add_chat_observation_existe(self, memory_service):
        assert hasattr(memory_service, "add_chat_observation"), (
            "memory_service deve ter 'add_chat_observation'"
        )

    def test_update_active_plan_existe(self, memory_service):
        assert hasattr(memory_service, "update_active_plan"), (
            "memory_service deve ter 'update_active_plan'"
        )


class TestAssinaturasGetOrCreateMemory:
    """Valida assinatura de get_or_create_memory."""

    def test_parametro_user_id(self, memory_service):
        sig = inspect.signature(memory_service.get_or_create_memory)
        assert "user_id" in sig.parameters, "get_or_create_memory deve ter 'user_id'"

    def test_parametro_db(self, memory_service):
        sig = inspect.signature(memory_service.get_or_create_memory)
        assert "db" in sig.parameters, "get_or_create_memory deve ter 'db'"


class TestAssinaturasUpdateAfterFeedback:
    """Valida assinatura de update_after_feedback."""

    def test_parametro_user_id(self, memory_service):
        sig = inspect.signature(memory_service.update_after_feedback)
        assert "user_id" in sig.parameters

    def test_parametro_effort(self, memory_service):
        sig = inspect.signature(memory_service.update_after_feedback)
        assert "effort" in sig.parameters

    def test_parametro_pain(self, memory_service):
        sig = inspect.signature(memory_service.update_after_feedback)
        assert "pain" in sig.parameters

    def test_parametro_sleep(self, memory_service):
        sig = inspect.signature(memory_service.update_after_feedback)
        assert "sleep" in sig.parameters

    def test_parametro_feeling(self, memory_service):
        sig = inspect.signature(memory_service.update_after_feedback)
        assert "feeling" in sig.parameters

    def test_parametro_recommendation(self, memory_service):
        sig = inspect.signature(memory_service.update_after_feedback)
        assert "recommendation" in sig.parameters

    def test_parametro_db(self, memory_service):
        sig = inspect.signature(memory_service.update_after_feedback)
        assert "db" in sig.parameters


class TestAssinaturasUpdateWeekProgress:
    """Valida assinatura de update_week_progress."""

    def test_parametro_user_id(self, memory_service):
        sig = inspect.signature(memory_service.update_week_progress)
        assert "user_id" in sig.parameters

    def test_parametro_day(self, memory_service):
        sig = inspect.signature(memory_service.update_week_progress)
        assert "day" in sig.parameters

    def test_parametro_status(self, memory_service):
        sig = inspect.signature(memory_service.update_week_progress)
        assert "status" in sig.parameters


class TestAssinaturasAddChatObservation:
    """Valida assinatura de add_chat_observation."""

    def test_parametro_user_id(self, memory_service):
        sig = inspect.signature(memory_service.add_chat_observation)
        assert "user_id" in sig.parameters

    def test_parametro_note(self, memory_service):
        sig = inspect.signature(memory_service.add_chat_observation)
        assert "note" in sig.parameters


class TestAssinaturasUpdateActivePlan:
    """Valida assinatura de update_active_plan."""

    def test_parametro_user_id(self, memory_service):
        sig = inspect.signature(memory_service.update_active_plan)
        assert "user_id" in sig.parameters

    def test_parametro_plan_id(self, memory_service):
        sig = inspect.signature(memory_service.update_active_plan)
        assert "plan_id" in sig.parameters

    def test_parametro_week_current(self, memory_service):
        sig = inspect.signature(memory_service.update_active_plan)
        assert "week_current" in sig.parameters

    def test_parametro_week_total(self, memory_service):
        sig = inspect.signature(memory_service.update_active_plan)
        assert "week_total" in sig.parameters


class TestBuildDynamicContextBlock:
    """Valida lógica de build_dynamic_context_block."""

    def test_retorna_string_vazia_sem_memory(self, memory_service):
        """Com memory=None deve retornar string vazia."""
        result = memory_service.build_dynamic_context_block(None)
        assert result == "", "Deve retornar string vazia quando memory é None"

    def test_retorna_string_com_memory(self, memory_service, mock_memory):
        """Com memory preenchida deve retornar bloco de contexto."""
        result = memory_service.build_dynamic_context_block(mock_memory)
        assert isinstance(result, str), "Deve retornar string"
        assert len(result) > 0, "String não deve ser vazia com memory preenchida"

    def test_contexto_inclui_semana_plano(self, memory_service, mock_memory):
        """Contexto deve incluir informações da semana do plano."""
        result = memory_service.build_dynamic_context_block(mock_memory)
        assert "semana" in result.lower() or "plano" in result.lower(), (
            "Contexto deve mencionar plano/semana"
        )

    def test_contexto_inclui_progresso_semana(self, memory_service, mock_memory):
        """Contexto deve incluir progresso da semana quando disponível."""
        result = memory_service.build_dynamic_context_block(mock_memory)
        # mock_memory.week_progress = {"segunda": "done", "quarta": "pending"}
        assert "segunda" in result or "progresso" in result.lower(), (
            "Contexto deve incluir progresso da semana"
        )

    def test_contexto_inclui_feedback_recente(self, memory_service, mock_memory):
        """Contexto deve incluir feedback mais recente."""
        result = memory_service.build_dynamic_context_block(mock_memory)
        assert "feedback" in result.lower() or "esforço" in result.lower() or "effort" in result.lower(), (
            "Contexto deve mencionar feedback recente"
        )

    def test_contexto_limita_tamanho(self, memory_service, mock_memory):
        """Contexto não deve ultrapassar 1500 caracteres."""
        result = memory_service.build_dynamic_context_block(mock_memory)
        assert len(result) <= 1500, f"Contexto não deve ultrapassar 1500 chars (atual: {len(result)})"

    def test_contexto_inclui_observacoes_chat(self, memory_service, mock_memory):
        """Contexto deve incluir observações do chat."""
        result = memory_service.build_dynamic_context_block(mock_memory)
        assert "manhã" in result or "observações" in result.lower() or "capturadas" in result.lower(), (
            "Contexto deve incluir observações do chat"
        )


class TestUpdateAfterFeedbackLogica:
    """Testa lógica básica de update_after_feedback com mocks."""

    def test_sem_db_retorna_sem_erro(self, memory_service):
        """Chamar update_after_feedback sem db não deve lançar exceção."""
        try:
            memory_service.update_after_feedback(
                user_id="user-123",
                effort=7,
                pain=3,
                sleep=4,
                feeling="good",
                recommendation="maintain",
                db=None,
            )
        except Exception as e:
            pytest.fail(f"update_after_feedback sem db lançou exceção inesperada: {e}")

    def test_com_db_mock_cria_memoria_se_nao_existe(self, memory_service, mock_db):
        """update_after_feedback deve chamar get_or_create_memory via db."""
        from app.models.runner_memory import RunnerMemory

        # Simula memória retornada pelo banco
        mock_memory_obj = MagicMock(spec=RunnerMemory)
        mock_memory_obj.recent_feedbacks = []
        mock_memory_obj.physical_alerts = []
        mock_memory_obj.load_adjustments = []
        mock_memory_obj.updated_at = datetime.utcnow()

        mock_db.query.return_value.filter.return_value.first.return_value = mock_memory_obj

        # Não deve lançar exceção
        memory_service.update_after_feedback(
            user_id="user-123",
            effort=5,
            pain=2,
            sleep=4,
            feeling="good",
            recommendation="maintain",
            db=mock_db,
        )

        # db.commit deve ter sido chamado
        mock_db.commit.assert_called()


class TestUpdateWeekProgressLogica:
    """Testa lógica básica de update_week_progress."""

    def test_sem_db_retorna_sem_erro(self, memory_service):
        """Chamar update_week_progress sem db não deve lançar exceção."""
        try:
            memory_service.update_week_progress(
                user_id="user-123",
                day="segunda",
                status="done",
                db=None,
            )
        except Exception as e:
            pytest.fail(f"update_week_progress sem db lançou exceção inesperada: {e}")


class TestAddChatObservationLogica:
    """Testa lógica básica de add_chat_observation."""

    def test_sem_db_retorna_sem_erro(self, memory_service):
        """Chamar add_chat_observation sem db não deve lançar exceção."""
        try:
            memory_service.add_chat_observation(
                user_id="user-123",
                note="treina melhor de manhã",
                db=None,
            )
        except Exception as e:
            pytest.fail(f"add_chat_observation sem db lançou exceção inesperada: {e}")

    def test_note_longa_demais_ignorada(self, memory_service, mock_db):
        """Observações com mais de 200 chars devem ser ignoradas silenciosamente."""
        from app.models.runner_memory import RunnerMemory
        mock_memory_obj = MagicMock(spec=RunnerMemory)
        mock_memory_obj.chat_observations = []
        mock_memory_obj.updated_at = datetime.utcnow()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_memory_obj

        long_note = "x" * 201
        # Não deve lançar exceção, e não deve chamar commit (note ignorada)
        memory_service.add_chat_observation(
            user_id="user-123",
            note=long_note,
            db=mock_db,
        )
        # commit não deve ter sido chamado pois note é inválida
        mock_db.commit.assert_not_called()
