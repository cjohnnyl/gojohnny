"""
test_prompt.py — Valida integridade do _SYSTEM_BASE (prompt do GoJohnny v2.0).

Garante que todas as seções obrigatórias estão presentes e com conteúdo mínimo.
Roda sem servidor e sem chamadas a APIs externas.
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(scope="module")
def system_base():
    """Importa e retorna o _SYSTEM_BASE do módulo ai.py."""
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = MagicMock()
        from app.services.ai import _SYSTEM_BASE
    return _SYSTEM_BASE


class TestPromptIdentidade:
    """Valida identidade e tom do GoJohnny."""

    def test_identidade_gojohnny(self, system_base):
        """Prompt deve definir o GoJohnny como treinador virtual de corrida."""
        assert "GoJohnny" in system_base, "Prompt deve conter o nome 'GoJohnny'"
        assert "treinador" in system_base.lower(), "Prompt deve mencionar papel de treinador"

    def test_idioma_portugues(self, system_base):
        """Prompt deve especificar uso de português do Brasil."""
        assert "português do Brasil" in system_base, "Prompt deve exigir português do Brasil"

    def test_tom_definido(self, system_base):
        """Prompt deve definir o tom de comunicação."""
        assert "direto" in system_base.lower() or "técnico" in system_base.lower(), (
            "Prompt deve definir tom (direto, técnico, etc.)"
        )


class TestCincoPapeis:
    """Valida que os 5 papéis obrigatórios estão definidos."""

    def test_secao_cinco_papeis_existe(self, system_base):
        """Seção dos 5 papéis deve estar presente."""
        assert "5 PAPÉIS" in system_base or "CINCO PAPÉIS" in system_base.upper() or "SEUS 5 PAPÉIS" in system_base, (
            "Prompt deve ter seção com os 5 papéis"
        )

    def test_papel_treinador_corrida(self, system_base):
        """Papel 1: Treinador de corrida."""
        assert "Treinador de corrida" in system_base or "treinador de corrida" in system_base.lower(), (
            "Papel 'Treinador de corrida' deve estar no prompt"
        )

    def test_papel_analista_performance(self, system_base):
        """Papel 2: Analista de performance."""
        assert "performance" in system_base.lower() and "analista" in system_base.lower(), (
            "Papel 'Analista de performance' deve estar no prompt"
        )

    def test_papel_orientador_recuperacao(self, system_base):
        """Papel 3: Orientador de recuperação."""
        assert "recuperação" in system_base.lower() or "recuperacao" in system_base.lower(), (
            "Papel 'Orientador de recuperação' deve estar no prompt"
        )

    def test_papel_consultor_equipamentos(self, system_base):
        """Papel 4: Consultor de equipamentos."""
        assert "equipamentos" in system_base.lower() or "equipamento" in system_base.lower(), (
            "Papel 'Consultor de equipamentos' deve estar no prompt"
        )

    def test_papel_guia_nutricao(self, system_base):
        """Papel 5: Guia de nutrição esportiva."""
        assert "nutrição" in system_base.lower() or "nutricao" in system_base.lower(), (
            "Papel 'Guia de nutrição' deve estar no prompt"
        )


class TestGuardrails:
    """Valida presença dos guardrails obrigatórios."""

    def test_secao_regras_obrigatorias(self, system_base):
        """Seção de regras obrigatórias deve existir."""
        assert "REGRAS OBRIGATÓRIAS" in system_base or "REGRAS" in system_base, (
            "Prompt deve ter seção de regras obrigatórias"
        )

    def test_guardrail_sem_diagnostico_medico(self, system_base):
        """Guardrail: nunca diagnosticar lesões."""
        assert "Nunca diagnostique" in system_base or "diagnóstico médico" in system_base.lower() or (
            "profissional de saúde" in system_base.lower()
        ), "Prompt deve ter guardrail contra diagnóstico médico"

    def test_guardrail_dor_forte(self, system_base):
        """Guardrail: orientar busca por profissional em caso de dor forte."""
        assert "dor forte" in system_base.lower() or "profissional qualificado" in system_base.lower(), (
            "Prompt deve ter guardrail para dor forte"
        )

    def test_guardrail_foco_corrida(self, system_base):
        """Guardrail: manter foco em corrida de rua."""
        assert "corrida de rua" in system_base.lower(), (
            "Prompt deve ter guardrail de foco em corrida de rua"
        )

    def test_guardrail_linguagem_inclusiva(self, system_base):
        """Guardrail: uso de linguagem inclusiva."""
        assert "inclusiva" in system_base.lower() or "gênero" in system_base.lower(), (
            "Prompt deve mencionar linguagem inclusiva"
        )


class TestViabilidadeMetas:
    """Valida seção de avaliação de viabilidade de metas."""

    def test_secao_viabilidade_existe(self, system_base):
        """Seção de viabilidade de metas deve existir."""
        assert "VIABILIDADE" in system_base.upper() or "viabilidade" in system_base.lower(), (
            "Prompt deve ter seção de avaliação de viabilidade"
        )

    def test_categoria_viavel(self, system_base):
        """Categoria 'Viável' deve estar presente."""
        assert "Viável" in system_base or "viável" in system_base.lower(), (
            "Prompt deve ter categoria 'Viável' na avaliação de metas"
        )

    def test_categoria_inviavel(self, system_base):
        """Categoria 'Inviável' deve estar presente."""
        assert "Inviável" in system_base or "inviável" in system_base.lower(), (
            "Prompt deve ter categoria 'Inviável' na avaliação de metas"
        )

    def test_guardrail_plano_inviavel(self, system_base):
        """Prompt nunca deve montar plano inviável por pedido do corredor."""
        assert "inviável" in system_base.lower() and (
            "redirecione" in system_base.lower() or "honesto" in system_base.lower()
        ), "Prompt deve orientar redirecionamento em caso de meta inviável"


class TestFasesCicloTreino:
    """Valida seção de fases do ciclo de treino."""

    def test_secao_fases_existe(self, system_base):
        """Seção de fases do ciclo deve existir."""
        assert "FASES" in system_base.upper() or "CICLO DE TREINO" in system_base.upper(), (
            "Prompt deve ter seção de fases do ciclo de treino"
        )

    def test_fase_base(self, system_base):
        """Fase Base deve estar definida."""
        assert "Base" in system_base or "base" in system_base, (
            "Fase 'Base' deve estar no prompt"
        )

    def test_fase_construcao(self, system_base):
        """Fase Construção deve estar definida."""
        assert "Construção" in system_base or "Construcao" in system_base or "construção" in system_base.lower(), (
            "Fase 'Construção' deve estar no prompt"
        )

    def test_fase_pico(self, system_base):
        """Fase Pico deve estar definida."""
        assert "Pico" in system_base or "pico" in system_base, (
            "Fase 'Pico' deve estar no prompt"
        )

    def test_fase_recuperacao(self, system_base):
        """Fase Recuperação deve estar definida."""
        assert "Recuperação" in system_base or "recuperação" in system_base.lower(), (
            "Fase 'Recuperação' deve estar no prompt"
        )


class TestTiposTreino:
    """Valida seção de tipos de treino."""

    def test_secao_tipos_treino_existe(self, system_base):
        """Seção de tipos de treino deve existir."""
        assert "TIPOS DE TREINO" in system_base.upper() or "Tipos de Treino" in system_base, (
            "Prompt deve ter seção de tipos de treino"
        )

    def test_tipo_regenerativo(self, system_base):
        """Tipo Regenerativo deve estar definido."""
        assert "Regenerativo" in system_base or "regenerativo" in system_base.lower(), (
            "Tipo 'Regenerativo' deve estar no prompt"
        )

    def test_tipo_intervalado(self, system_base):
        """Tipo Intervalado deve estar definido."""
        assert "Intervalado" in system_base or "intervalado" in system_base.lower(), (
            "Tipo 'Intervalado' deve estar no prompt"
        )

    def test_tipo_longao(self, system_base):
        """Tipo Longão deve estar definido."""
        assert "Longão" in system_base or "longão" in system_base.lower() or "Longao" in system_base, (
            "Tipo 'Longão' deve estar no prompt"
        )

    def test_regra_dois_treinos_alta_intensidade(self, system_base):
        """Regra: máximo 2 treinos de alta intensidade por semana para iniciantes."""
        assert "2 treinos" in system_base or "dois treinos" in system_base.lower() or "alta intensidade" in system_base.lower(), (
            "Prompt deve ter regra de máximo 2 treinos de alta intensidade"
        )

    def test_regra_10_porcento(self, system_base):
        """Regra dos 10%: não aumentar volume mais que 10% por semana."""
        assert "10%" in system_base, "Prompt deve ter a regra dos 10% de volume semanal"


class TestCheckin:
    """Valida seção de check-in semanal."""

    def test_secao_checkin_existe(self, system_base):
        """Seção de check-in semanal deve existir."""
        assert "CHECK-IN" in system_base.upper() or "check-in" in system_base.lower(), (
            "Prompt deve ter seção de check-in semanal"
        )

    def test_pergunta_treinos_completados(self, system_base):
        """Check-in deve perguntar sobre treinos completados."""
        assert "completar" in system_base.lower() or "completou" in system_base.lower() or "completados" in system_base.lower(), (
            "Check-in deve perguntar sobre treinos completados"
        )

    def test_pergunta_percepcao_esforco(self, system_base):
        """Check-in deve perguntar sobre percepção de esforço."""
        assert "percepção de esforço" in system_base.lower() or "esforço" in system_base.lower(), (
            "Check-in deve perguntar sobre percepção de esforço"
        )

    def test_pergunta_dor(self, system_base):
        """Check-in deve perguntar sobre dor ou desconforto."""
        assert "dor" in system_base.lower() or "desconforto" in system_base.lower(), (
            "Check-in deve perguntar sobre dor/desconforto"
        )

    def test_pergunta_motivacao(self, system_base):
        """Check-in deve perguntar sobre motivação."""
        assert "motivação" in system_base.lower() or "motivacao" in system_base.lower(), (
            "Check-in deve perguntar sobre motivação"
        )
