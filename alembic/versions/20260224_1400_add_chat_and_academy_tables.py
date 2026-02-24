"""add chat persistence and academy tables

Revision ID: a1b2c3d4e5f6
Revises: 0dba430d74c4
Create Date: 2026-02-24 14:00:00.000000-03:00

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "0dba430d74c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # CHAT PERSISTENCE TABLES
    # =========================================================================

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # User (nullable for anonymous sessions)
        sa.Column("user_id", sa.String(255), nullable=True, index=True),
        # Session metadata
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("agent_id", sa.String(100), nullable=True),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="active",
            index=True,
        ),
        sa.Column("current_investigation_id", sa.String(36), nullable=True),
        sa.Column("context", sa.JSON(), server_default="{}"),
        sa.Column("last_message_at", sa.DateTime(), nullable=True),
        sa.Column("message_count", sa.Integer(), server_default="0"),
    )

    op.create_index(
        "idx_chat_sessions_user_status", "chat_sessions", ["user_id", "status"]
    )
    op.create_index(
        "idx_chat_sessions_last_message", "chat_sessions", ["last_message_at"]
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # Session reference
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Message content
        sa.Column(
            "role", sa.String(20), nullable=False
        ),  # user, assistant, system
        sa.Column("content", sa.Text(), nullable=False),
        # Agent info
        sa.Column("agent_id", sa.String(100), nullable=True, index=True),
        sa.Column("intent", sa.String(100), nullable=True),
        # References
        sa.Column("investigation_id", sa.String(36), nullable=True),
        # Extra data
        sa.Column("metadata", sa.JSON(), server_default="{}"),
    )

    op.create_index(
        "idx_chat_messages_session_created",
        "chat_messages",
        ["session_id", "created_at"],
    )

    # =========================================================================
    # ACADEMY TABLES
    # =========================================================================

    op.create_table(
        "academy_users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # Identity
        sa.Column("user_id", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        # Gamification
        sa.Column("total_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "current_rank", sa.String(50), nullable=False, server_default="novato"
        ),
        # Track
        sa.Column(
            "main_track", sa.String(50), nullable=False, server_default="backend"
        ),
        # Badges
        sa.Column("badges", sa.JSON(), server_default="[]"),
        # Streaks
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_activity_date", sa.DateTime(), nullable=True),
        # Stats
        sa.Column(
            "total_conversations", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_missions_completed", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_contributions", sa.Integer(), nullable=False, server_default="0"
        ),
        # Metadata
        sa.Column("profile_data", sa.JSON(), server_default="{}"),
        sa.Column("preferences", sa.JSON(), server_default="{}"),
        sa.Column("github_username", sa.String(255), nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("enrolled_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("idx_academy_users_xp", "academy_users", ["total_xp"])
    op.create_index("idx_academy_users_level", "academy_users", ["current_level"])
    op.create_index("idx_academy_users_rank", "academy_users", ["current_rank"])
    op.create_index("idx_academy_users_track", "academy_users", ["main_track"])

    op.create_table(
        "academy_conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # User
        sa.Column(
            "academy_user_id",
            sa.String(36),
            sa.ForeignKey("academy_users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Agent
        sa.Column("agent_name", sa.String(100), nullable=False, index=True),
        sa.Column("agent_display_name", sa.String(255), nullable=True),
        # Track/topic
        sa.Column("track", sa.String(50), nullable=False),
        sa.Column("topic", sa.String(255), nullable=True),
        sa.Column(
            "difficulty", sa.String(20), nullable=False, server_default="beginner"
        ),
        # Content
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("messages", sa.JSON(), server_default="[]"),
        sa.Column("summary", sa.Text(), nullable=True),
        # Gamification
        sa.Column("xp_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("badges_earned", sa.JSON(), server_default="[]"),
        # Status
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="active"
        ),
        sa.Column(
            "started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
        # Rating
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
    )

    op.create_index(
        "idx_academy_conv_user_agent",
        "academy_conversations",
        ["academy_user_id", "agent_name"],
    )
    op.create_index("idx_academy_conv_track", "academy_conversations", ["track"])
    op.create_index("idx_academy_conv_status", "academy_conversations", ["status"])

    op.create_table(
        "academy_xp_transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # User
        sa.Column(
            "academy_user_id",
            sa.String(36),
            sa.ForeignKey("academy_users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Transaction
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        # Source
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        # Metadata
        sa.Column("metadata", sa.JSON(), server_default="{}"),
    )

    op.create_index(
        "idx_academy_xp_user", "academy_xp_transactions", ["academy_user_id"]
    )
    op.create_index(
        "idx_academy_xp_source", "academy_xp_transactions", ["source_type"]
    )

    op.create_table(
        "academy_missions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # Identity
        sa.Column("code", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        # Category
        sa.Column("track", sa.String(50), nullable=False, index=True),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        # Rewards
        sa.Column("xp_reward", sa.Integer(), nullable=False),
        sa.Column("badge_reward", sa.String(100), nullable=True),
        # Requirements
        sa.Column("required_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("prerequisites", sa.JSON(), server_default="[]"),
        # GitHub
        sa.Column("github_issue_url", sa.String(500), nullable=True),
        sa.Column("github_repo", sa.String(255), nullable=True),
        # Resources
        sa.Column("resources", sa.JSON(), server_default="[]"),
        sa.Column("video_url", sa.String(500), nullable=True),
        # Agent
        sa.Column("recommended_agent", sa.String(100), nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        # Stats
        sa.Column(
            "times_completed", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("avg_completion_time", sa.Float(), nullable=True),
    )

    op.create_index(
        "idx_academy_mission_track_diff",
        "academy_missions",
        ["track", "difficulty"],
    )
    op.create_index(
        "idx_academy_mission_active", "academy_missions", ["is_active"]
    )

    op.create_table(
        "academy_user_missions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # User and Mission
        sa.Column(
            "academy_user_id",
            sa.String(36),
            sa.ForeignKey("academy_users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "mission_id",
            sa.String(36),
            sa.ForeignKey("academy_missions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Status
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="in_progress"
        ),
        # Dates
        sa.Column(
            "started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        # GitHub
        sa.Column("pull_request_url", sa.String(500), nullable=True),
        sa.Column(
            "is_pr_merged", sa.Boolean(), nullable=False, server_default="false"
        ),
        # Evaluation
        sa.Column("mentor_feedback", sa.Text(), nullable=True),
        sa.Column("xp_awarded", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_index(
        "idx_academy_user_mission",
        "academy_user_missions",
        ["academy_user_id", "mission_id"],
    )
    op.create_index(
        "idx_academy_user_mission_status", "academy_user_missions", ["status"]
    )

    op.create_table(
        "academy_badges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # Identity
        sa.Column("code", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        # Visual
        sa.Column("icon", sa.String(100), nullable=False),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column(
            "rarity", sa.String(20), nullable=False, server_default="common"
        ),
        # Category
        sa.Column("category", sa.String(50), nullable=False),
        # Bonus
        sa.Column("xp_bonus", sa.Integer(), nullable=False, server_default="0"),
        # Requirements
        sa.Column("requirement_type", sa.String(50), nullable=False),
        sa.Column(
            "requirement_target", sa.Integer(), nullable=False, server_default="1"
        ),
        sa.Column("requirement_metric", sa.String(100), nullable=False),
        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_secret", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_index("idx_academy_badge_category", "academy_badges", ["category"])
    op.create_index("idx_academy_badge_rarity", "academy_badges", ["rarity"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("academy_badges")
    op.drop_table("academy_user_missions")
    op.drop_table("academy_missions")
    op.drop_table("academy_xp_transactions")
    op.drop_table("academy_conversations")
    op.drop_table("academy_users")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
