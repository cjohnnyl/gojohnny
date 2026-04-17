"""schema_supabase_auth

Revision ID: 0002
Revises: 8a06f42e4134
Create Date: 2026-04-15

Recria o schema completo alinhado com os modelos atuais:
- user_id usa UUID (string) do Supabase Auth — sem tabela users local
- Remove dependência de FK para tabela users (gerenciada pelo Supabase)
- Adiciona tabela runner_memory
- Corrige tipos de colunas incompatíveis com a migration 0001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "8a06f42e4134"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Elimina todas as tabelas do schema antigo (criado pela migration 0001
    # com user_id INTEGER e FK para tabela users local). Em produção o banco
    # estará vazio; em dev/staging garante estado limpo antes de recriar.
    # ------------------------------------------------------------------
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
    op.execute("DROP TABLE IF EXISTS training_feedbacks CASCADE")
    op.execute("DROP TABLE IF EXISTS training_plans CASCADE")
    op.execute("DROP TABLE IF EXISTS runner_profiles CASCADE")
    op.execute("DROP TABLE IF EXISTS runner_memory CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")

    # ------------------------------------------------------------------
    # runner_profiles — user_id é UUID string do Supabase Auth
    # ------------------------------------------------------------------
    op.create_table(
        "runner_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("level", sa.String(20), nullable=False, server_default=sa.text("'beginner'")),
        sa.Column("weekly_volume_km", sa.Float(), nullable=True),
        sa.Column("available_days_per_week", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("preferred_days", sa.String(50), nullable=True),
        sa.Column("comfortable_pace", sa.String(10), nullable=True),
        sa.Column("main_goal", sa.String(50), nullable=True),
        sa.Column("target_race_name", sa.String(200), nullable=True),
        sa.Column("target_race_distance_km", sa.Float(), nullable=True),
        sa.Column("target_race_date", sa.Date(), nullable=True),
        sa.Column("injury_history", sa.Text(), nullable=True),
        sa.Column("physical_limitations", sa.Text(), nullable=True),
        sa.Column("location", sa.String(100), nullable=True),
        sa.Column("extra_context", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_runner_profiles_id", "runner_profiles", ["id"])
    op.create_index("ix_runner_profiles_user_id", "runner_profiles", ["user_id"])

    # ------------------------------------------------------------------
    # training_plans — user_id é UUID string do Supabase Auth
    # ------------------------------------------------------------------
    op.create_table(
        "training_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("plan_data", sa.JSON(), nullable=False),
        sa.Column("context_snapshot", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("coach_notes", sa.Text(), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_training_plans_id", "training_plans", ["id"])
    op.create_index("ix_training_plans_user_id", "training_plans", ["user_id"])

    # ------------------------------------------------------------------
    # training_feedbacks — user_id é UUID string do Supabase Auth
    # ------------------------------------------------------------------
    op.create_table(
        "training_feedbacks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.Column("training_date", sa.Date(), nullable=False),
        sa.Column("effort_rating", sa.Integer(), nullable=True),
        sa.Column("pain_level", sa.Integer(), nullable=True),
        sa.Column("sleep_quality", sa.Integer(), nullable=True),
        sa.Column("general_feeling", sa.String(20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("ai_analysis", sa.Text(), nullable=True),
        sa.Column("load_recommendation", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["plan_id"], ["training_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_training_feedbacks_id", "training_feedbacks", ["id"])
    op.create_index("ix_training_feedbacks_user_id", "training_feedbacks", ["user_id"])

    # ------------------------------------------------------------------
    # conversations — user_id é UUID string do Supabase Auth
    # ------------------------------------------------------------------
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_id", "conversations", ["id"])
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])

    # ------------------------------------------------------------------
    # messages — FK para conversations
    # ------------------------------------------------------------------
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("model_used", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_id", "messages", ["id"])
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    # ------------------------------------------------------------------
    # runner_memory — estado persistente por usuário Supabase
    # ------------------------------------------------------------------
    op.create_table(
        "runner_memory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("active_plan_id", sa.Integer(), nullable=True),
        sa.Column("plan_week_current", sa.Integer(), nullable=True),
        sa.Column("plan_week_total", sa.Integer(), nullable=True),
        sa.Column("plan_started_at", sa.Date(), nullable=True),
        sa.Column("week_progress", sa.JSON(), nullable=True),
        sa.Column("recent_feedbacks", sa.JSON(), nullable=True),
        sa.Column("physical_alerts", sa.JSON(), nullable=True),
        sa.Column("load_adjustments", sa.JSON(), nullable=True),
        sa.Column("chat_observations", sa.JSON(), nullable=True),
        sa.Column("last_coaching_style", sa.String(20), nullable=True),
        sa.Column("last_session_summary", sa.Text(), nullable=True),
        sa.Column("last_session_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_runner_memory_id", "runner_memory", ["id"])
    op.create_index("ix_runner_memory_user_id", "runner_memory", ["user_id"])


def downgrade() -> None:
    op.drop_table("runner_memory")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("training_feedbacks")
    op.drop_table("training_plans")
    op.drop_table("runner_profiles")
