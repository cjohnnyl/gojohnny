"""
test_ai_structure.py — Valida assinaturas e estrutura das funções de IA.

Verifica que as funções chat, generate_training_plan e analyze_feedback
existem com as assinaturas corretas, sem chamar APIs externas.
"""
import inspect
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(scope="module")
def ai_module():
    """Importa o módulo ai com OpenAI mockado."""
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = MagicMock()
        import app.services.ai as ai
    return ai


class TestFuncaoChatExiste:
    """Valida existência e assinatura da função chat."""

    def test_chat_existe(self, ai_module):
        """Função chat deve existir no módulo."""
        assert hasattr(ai_module, "chat"), "Módulo ai deve ter função 'chat'"

    def test_chat_e_callable(self, ai_module):
        """chat deve ser callable."""
        assert callable(ai_module.chat), "chat deve ser uma função callable"

    def test_chat_parametro_messages(self, ai_module):
        """chat deve aceitar parâmetro 'messages'."""
        sig = inspect.signature(ai_module.chat)
        assert "messages" in sig.parameters, "chat deve ter parâmetro 'messages'"

    def test_chat_parametro_profile(self, ai_module):
        """chat deve aceitar parâmetro 'profile' (opcional)."""
        sig = inspect.signature(ai_module.chat)
        assert "profile" in sig.parameters, "chat deve ter parâmetro 'profile'"
        param = sig.parameters["profile"]
        assert param.default is not inspect.Parameter.empty, "profile deve ter valor padrão (Optional)"

    def test_chat_parametro_memory(self, ai_module):
        """chat deve aceitar parâmetro 'memory' (opcional)."""
        sig = inspect.signature(ai_module.chat)
        assert "memory" in sig.parameters, "chat deve ter parâmetro 'memory'"
        param = sig.parameters["memory"]
        assert param.default is not inspect.Parameter.empty, "memory deve ter valor padrão (Optional)"

    def test_chat_parametro_model(self, ai_module):
        """chat deve aceitar parâmetro 'model' (opcional)."""
        sig = inspect.signature(ai_module.chat)
        assert "model" in sig.parameters, "chat deve ter parâmetro 'model'"

    def test_chat_retorna_tuple(self, ai_module):
        """chat deve retornar tuple (str, int) segundo docstring/type hints."""
        sig = inspect.signature(ai_module.chat)
        # Verifica annotation de retorno se disponível
        if sig.return_annotation != inspect.Parameter.empty:
            return_str = str(sig.return_annotation)
            assert "tuple" in return_str.lower() or "Tuple" in return_str, (
                "chat deve ter anotação de retorno tuple"
            )


class TestFuncaoGenerateTrainingPlan:
    """Valida existência e assinatura da função generate_training_plan."""

    def test_generate_training_plan_existe(self, ai_module):
        """Função generate_training_plan deve existir."""
        assert hasattr(ai_module, "generate_training_plan"), (
            "Módulo ai deve ter função 'generate_training_plan'"
        )

    def test_generate_training_plan_callable(self, ai_module):
        """generate_training_plan deve ser callable."""
        assert callable(ai_module.generate_training_plan), (
            "generate_training_plan deve ser callable"
        )

    def test_generate_training_plan_parametro_profile(self, ai_module):
        """generate_training_plan deve aceitar parâmetro 'profile'."""
        sig = inspect.signature(ai_module.generate_training_plan)
        assert "profile" in sig.parameters, (
            "generate_training_plan deve ter parâmetro 'profile'"
        )

    def test_generate_training_plan_retorna_tuple(self, ai_module):
        """generate_training_plan deve retornar tuple."""
        sig = inspect.signature(ai_module.generate_training_plan)
        if sig.return_annotation != inspect.Parameter.empty:
            return_str = str(sig.return_annotation)
            assert "tuple" in return_str.lower() or "Tuple" in return_str, (
                "generate_training_plan deve ter anotação de retorno tuple"
            )


class TestFuncaoAnalyzeFeedback:
    """Valida existência e assinatura da função analyze_feedback."""

    def test_analyze_feedback_existe(self, ai_module):
        """Função analyze_feedback deve existir."""
        assert hasattr(ai_module, "analyze_feedback"), (
            "Módulo ai deve ter função 'analyze_feedback'"
        )

    def test_analyze_feedback_callable(self, ai_module):
        """analyze_feedback deve ser callable."""
        assert callable(ai_module.analyze_feedback), "analyze_feedback deve ser callable"

    def test_analyze_feedback_parametro_profile(self, ai_module):
        """analyze_feedback deve aceitar parâmetro 'profile'."""
        sig = inspect.signature(ai_module.analyze_feedback)
        assert "profile" in sig.parameters, "analyze_feedback deve ter parâmetro 'profile'"

    def test_analyze_feedback_parametro_effort(self, ai_module):
        """analyze_feedback deve aceitar parâmetro 'effort'."""
        sig = inspect.signature(ai_module.analyze_feedback)
        assert "effort" in sig.parameters, "analyze_feedback deve ter parâmetro 'effort'"

    def test_analyze_feedback_parametro_pain(self, ai_module):
        """analyze_feedback deve aceitar parâmetro 'pain'."""
        sig = inspect.signature(ai_module.analyze_feedback)
        assert "pain" in sig.parameters, "analyze_feedback deve ter parâmetro 'pain'"

    def test_analyze_feedback_parametro_sleep(self, ai_module):
        """analyze_feedback deve aceitar parâmetro 'sleep'."""
        sig = inspect.signature(ai_module.analyze_feedback)
        assert "sleep" in sig.parameters, "analyze_feedback deve ter parâmetro 'sleep'"

    def test_analyze_feedback_parametro_feeling(self, ai_module):
        """analyze_feedback deve aceitar parâmetro 'feeling'."""
        sig = inspect.signature(ai_module.analyze_feedback)
        assert "feeling" in sig.parameters, "analyze_feedback deve ter parâmetro 'feeling'"

    def test_analyze_feedback_parametro_notes(self, ai_module):
        """analyze_feedback deve aceitar parâmetro 'notes'."""
        sig = inspect.signature(ai_module.analyze_feedback)
        assert "notes" in sig.parameters, "analyze_feedback deve ter parâmetro 'notes'"


class TestFuncaoBuildContextBlock:
    """Valida a função auxiliar _build_context_block."""

    def test_build_context_block_existe(self, ai_module):
        """Função _build_context_block deve existir."""
        assert hasattr(ai_module, "_build_context_block"), (
            "Módulo ai deve ter função '_build_context_block'"
        )

    def test_build_context_block_sem_profile(self, ai_module):
        """_build_context_block com None deve retornar string com orientação."""
        result = ai_module._build_context_block(None)
        assert isinstance(result, str), "_build_context_block deve retornar string"
        assert len(result) > 0, "Resultado não deve ser string vazia com profile=None"

    def test_build_context_block_com_profile(self, ai_module, mock_profile):
        """_build_context_block com profile deve incluir nome do corredor."""
        result = ai_module._build_context_block(mock_profile)
        assert isinstance(result, str), "_build_context_block deve retornar string"
        assert mock_profile.name in result, "Resultado deve conter o nome do corredor"

    def test_build_context_block_com_profile_inclui_nivel(self, ai_module, mock_profile):
        """_build_context_block com profile deve incluir nível."""
        result = ai_module._build_context_block(mock_profile)
        assert mock_profile.level in result, "Resultado deve conter o nível do corredor"


class TestSystemBase:
    """Valida que _SYSTEM_BASE é uma string válida e substancial."""

    def test_system_base_e_string(self, ai_module):
        """_SYSTEM_BASE deve ser uma string."""
        assert isinstance(ai_module._SYSTEM_BASE, str), "_SYSTEM_BASE deve ser uma string"

    def test_system_base_nao_vazio(self, ai_module):
        """_SYSTEM_BASE não deve ser vazio."""
        assert len(ai_module._SYSTEM_BASE) > 100, "_SYSTEM_BASE deve ter conteúdo substancial"

    def test_system_base_versao_2(self, ai_module):
        """_SYSTEM_BASE deve ser versão 2.0 (expandida)."""
        # Verificamos pelo tamanho — v2 tem mais de 5000 chars
        assert len(ai_module._SYSTEM_BASE) > 5000, (
            "_SYSTEM_BASE v2.0 deve ter mais de 5000 caracteres"
        )
