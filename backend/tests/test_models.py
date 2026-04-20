"""
test_models.py — Valida estrutura dos modelos SQLAlchemy do GoJohnny.

Verifica que todos os modelos têm user_id como campo e que os campos
obrigatórios estão presentes. Roda sem servidor e sem banco real.
"""
import pytest
from sqlalchemy import inspect as sa_inspect


class TestRunnerProfileModel:
    """Valida o modelo RunnerProfile."""

    @pytest.fixture(scope="class")
    def model(self):
        from app.models.runner_profile import RunnerProfile
        return RunnerProfile

    def test_modelo_importa(self, model):
        """RunnerProfile deve ser importável."""
        assert model is not None

    def test_tem_user_id(self, model):
        """RunnerProfile deve ter campo user_id."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "user_id" in column_names, "RunnerProfile deve ter campo 'user_id'"

    def test_tem_id(self, model):
        """RunnerProfile deve ter chave primária id."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "id" in column_names, "RunnerProfile deve ter campo 'id'"

    def test_tem_name(self, model):
        """RunnerProfile deve ter campo name."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "name" in column_names, "RunnerProfile deve ter campo 'name'"

    def test_tem_level(self, model):
        """RunnerProfile deve ter campo level."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "level" in column_names, "RunnerProfile deve ter campo 'level'"

    def test_tem_weekly_volume_km(self, model):
        """RunnerProfile deve ter campo weekly_volume_km."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "weekly_volume_km" in column_names, "RunnerProfile deve ter campo 'weekly_volume_km'"

    def test_tem_main_goal(self, model):
        """RunnerProfile deve ter campo main_goal."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "main_goal" in column_names, "RunnerProfile deve ter campo 'main_goal'"

    def test_tem_created_at(self, model):
        """RunnerProfile deve ter campo created_at."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "created_at" in column_names, "RunnerProfile deve ter campo 'created_at'"

    def test_tablename_correto(self, model):
        """RunnerProfile deve usar tablename 'runner_profiles'."""
        assert model.__tablename__ == "runner_profiles", (
            f"Tablename deve ser 'runner_profiles', encontrado: {model.__tablename__}"
        )

    def test_user_id_e_unico(self, model):
        """RunnerProfile.user_id deve ter constraint de unicidade."""
        # Acessa a coluna diretamente pela tabela SQLAlchemy
        col = model.__table__.c["user_id"]
        assert col.unique is True, "RunnerProfile.user_id deve ser único"


class TestRunnerMemoryModel:
    """Valida o modelo RunnerMemory."""

    @pytest.fixture(scope="class")
    def model(self):
        from app.models.runner_memory import RunnerMemory
        return RunnerMemory

    def test_modelo_importa(self, model):
        """RunnerMemory deve ser importável."""
        assert model is not None

    def test_tem_user_id(self, model):
        """RunnerMemory deve ter campo user_id."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "user_id" in column_names, "RunnerMemory deve ter campo 'user_id'"

    def test_tem_id(self, model):
        """RunnerMemory deve ter chave primária id."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "id" in column_names

    def test_tem_recent_feedbacks(self, model):
        """RunnerMemory deve ter campo recent_feedbacks (JSON)."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "recent_feedbacks" in column_names, "RunnerMemory deve ter campo 'recent_feedbacks'"

    def test_tem_week_progress(self, model):
        """RunnerMemory deve ter campo week_progress."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "week_progress" in column_names, "RunnerMemory deve ter campo 'week_progress'"

    def test_tem_physical_alerts(self, model):
        """RunnerMemory deve ter campo physical_alerts."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "physical_alerts" in column_names, "RunnerMemory deve ter campo 'physical_alerts'"

    def test_tem_load_adjustments(self, model):
        """RunnerMemory deve ter campo load_adjustments."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "load_adjustments" in column_names, "RunnerMemory deve ter campo 'load_adjustments'"

    def test_tem_chat_observations(self, model):
        """RunnerMemory deve ter campo chat_observations."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "chat_observations" in column_names, "RunnerMemory deve ter campo 'chat_observations'"

    def test_tem_active_plan_id(self, model):
        """RunnerMemory deve ter campo active_plan_id."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "active_plan_id" in column_names, "RunnerMemory deve ter campo 'active_plan_id'"

    def test_tablename_correto(self, model):
        """RunnerMemory deve usar tablename 'runner_memory'."""
        assert model.__tablename__ == "runner_memory", (
            f"Tablename deve ser 'runner_memory', encontrado: {model.__tablename__}"
        )


class TestTrainingPlanModel:
    """Valida o modelo TrainingPlan."""

    @pytest.fixture(scope="class")
    def model(self):
        from app.models.training_plan import TrainingPlan
        return TrainingPlan

    def test_modelo_importa(self, model):
        assert model is not None

    def test_tem_user_id(self, model):
        """TrainingPlan deve ter campo user_id."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "user_id" in column_names, "TrainingPlan deve ter campo 'user_id'"

    def test_tem_plan_data(self, model):
        """TrainingPlan deve ter campo plan_data (JSON)."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "plan_data" in column_names, "TrainingPlan deve ter campo 'plan_data'"

    def test_tem_week_start(self, model):
        """TrainingPlan deve ter campo week_start."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "week_start" in column_names, "TrainingPlan deve ter campo 'week_start'"

    def test_tem_status(self, model):
        """TrainingPlan deve ter campo status."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "status" in column_names, "TrainingPlan deve ter campo 'status'"

    def test_tablename_correto(self, model):
        assert model.__tablename__ == "training_plans"


class TestTrainingFeedbackModel:
    """Valida o modelo TrainingFeedback."""

    @pytest.fixture(scope="class")
    def model(self):
        from app.models.training_feedback import TrainingFeedback
        return TrainingFeedback

    def test_modelo_importa(self, model):
        assert model is not None

    def test_tem_user_id(self, model):
        """TrainingFeedback deve ter campo user_id."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "user_id" in column_names, "TrainingFeedback deve ter campo 'user_id'"

    def test_tem_effort_rating(self, model):
        """TrainingFeedback deve ter campo effort_rating."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "effort_rating" in column_names, "TrainingFeedback deve ter campo 'effort_rating'"

    def test_tem_pain_level(self, model):
        """TrainingFeedback deve ter campo pain_level."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "pain_level" in column_names, "TrainingFeedback deve ter campo 'pain_level'"

    def test_tem_sleep_quality(self, model):
        """TrainingFeedback deve ter campo sleep_quality."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "sleep_quality" in column_names, "TrainingFeedback deve ter campo 'sleep_quality'"

    def test_tem_load_recommendation(self, model):
        """TrainingFeedback deve ter campo load_recommendation."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "load_recommendation" in column_names, (
            "TrainingFeedback deve ter campo 'load_recommendation'"
        )

    def test_tablename_correto(self, model):
        assert model.__tablename__ == "training_feedbacks"


class TestConversationModel:
    """Valida o modelo Conversation."""

    @pytest.fixture(scope="class")
    def model(self):
        from app.models.conversation import Conversation
        return Conversation

    def test_modelo_importa(self, model):
        assert model is not None

    def test_tem_user_id(self, model):
        """Conversation deve ter campo user_id."""
        mapper = sa_inspect(model)
        column_names = [c.key for c in mapper.columns]
        assert "user_id" in column_names, "Conversation deve ter campo 'user_id'"

    def test_tablename_correto(self, model):
        assert model.__tablename__ == "conversations"


class TestTodosModelosTêmUserId:
    """Teste integrador: todos os modelos principais têm user_id."""

    def test_todos_modelos_tem_user_id(self):
        """Garante que nenhum modelo principal esqueceu o campo user_id."""
        from app.models.runner_profile import RunnerProfile
        from app.models.runner_memory import RunnerMemory
        from app.models.training_plan import TrainingPlan
        from app.models.training_feedback import TrainingFeedback
        from app.models.conversation import Conversation

        modelos = [
            ("RunnerProfile", RunnerProfile),
            ("RunnerMemory", RunnerMemory),
            ("TrainingPlan", TrainingPlan),
            ("TrainingFeedback", TrainingFeedback),
            ("Conversation", Conversation),
        ]

        for nome, modelo in modelos:
            mapper = sa_inspect(modelo)
            column_names = [c.key for c in mapper.columns]
            assert "user_id" in column_names, (
                f"FALHA: modelo '{nome}' não tem campo 'user_id'"
            )
