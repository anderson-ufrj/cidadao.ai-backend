"""
Academy Gamification Models.

Sistema de gamificacao para o programa de estagio Cidadao.AI Academy.
Parceria: Neural Thinker AI Engineering + IFSULDEMINAS/LabSoft
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class AcademyUser(BaseModel):
    """Perfil do aluno na Academy."""

    __tablename__ = "academy_users"

    # Vinculo com usuario principal
    user_id = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Gamificacao
    total_xp = Column(Integer, default=0, nullable=False)
    current_level = Column(Integer, default=1, nullable=False)
    current_rank = Column(String(50), default="novato", nullable=False)

    # Trilha principal
    main_track = Column(String(50), default="backend", nullable=False)

    # Badges conquistados (lista de IDs)
    badges = Column(JSON, default=list)

    # Streaks
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime, nullable=True)

    # Estatisticas
    total_conversations = Column(Integer, default=0, nullable=False)
    total_missions_completed = Column(Integer, default=0, nullable=False)
    total_contributions = Column(Integer, default=0, nullable=False)

    # Metadados
    profile_data = Column(JSON, default=dict)
    preferences = Column(JSON, default=dict)
    github_username = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    enrolled_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relacionamentos
    conversations = relationship("AcademyConversation", back_populates="user")
    xp_transactions = relationship("AcademyXPTransaction", back_populates="user")

    __table_args__ = (
        Index("idx_academy_users_xp", "total_xp"),
        Index("idx_academy_users_level", "current_level"),
        Index("idx_academy_users_rank", "current_rank"),
        Index("idx_academy_users_track", "main_track"),
    )

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """Convert to dict for API responses."""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "total_xp": self.total_xp,
            "current_level": self.current_level,
            "current_rank": self.current_rank,
            "main_track": self.main_track,
            "badges": self.badges or [],
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "total_conversations": self.total_conversations,
            "total_missions_completed": self.total_missions_completed,
            "github_username": self.github_username,
            "enrolled_at": self.enrolled_at.isoformat() if self.enrolled_at else None,
        }
        if include_private:
            data["email"] = self.email
            data["preferences"] = self.preferences
        return data


class AcademyConversation(BaseModel):
    """Conversa/Aula com um agente."""

    __tablename__ = "academy_conversations"

    # Usuario
    academy_user_id = Column(
        String(36), ForeignKey("academy_users.id"), nullable=False, index=True
    )

    # Agente professor
    agent_name = Column(String(100), nullable=False, index=True)
    agent_display_name = Column(String(255), nullable=True)

    # Trilha e topico
    track = Column(String(50), nullable=False)
    topic = Column(String(255), nullable=True)
    difficulty = Column(String(20), default="beginner", nullable=False)

    # Conteudo da conversa
    title = Column(String(500), nullable=True)
    messages = Column(JSON, default=list)  # Lista de mensagens
    summary = Column(Text, nullable=True)

    # Gamificacao
    xp_earned = Column(Integer, default=0, nullable=False)
    badges_earned = Column(JSON, default=list)

    # Status
    status = Column(String(50), default="active", nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=0, nullable=False)

    # Avaliacao
    rating = Column(Integer, nullable=True)  # 1-5 estrelas
    feedback = Column(Text, nullable=True)

    # Relacionamentos
    user = relationship("AcademyUser", back_populates="conversations")

    __table_args__ = (
        Index("idx_academy_conv_user_agent", "academy_user_id", "agent_name"),
        Index("idx_academy_conv_track", "track"),
        Index("idx_academy_conv_status", "status"),
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for API responses."""
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "agent_display_name": self.agent_display_name,
            "track": self.track,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "title": self.title,
            "messages_count": len(self.messages) if self.messages else 0,
            "xp_earned": self.xp_earned,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "duration_minutes": self.duration_minutes,
            "rating": self.rating,
        }


class AcademyXPTransaction(BaseModel):
    """Transacao de XP (ganho ou gasto)."""

    __tablename__ = "academy_xp_transactions"

    # Usuario
    academy_user_id = Column(
        String(36), ForeignKey("academy_users.id"), nullable=False, index=True
    )

    # Transacao
    amount = Column(Integer, nullable=False)  # Positivo = ganho, Negativo = gasto
    balance_after = Column(Integer, nullable=False)

    # Origem
    source_type = Column(
        String(50), nullable=False
    )  # conversation, mission, badge, bonus
    source_id = Column(String(36), nullable=True)  # ID da conversa, missao, etc.
    description = Column(String(500), nullable=False)

    # Metadados
    metadata = Column(JSON, default=dict)

    # Relacionamentos
    user = relationship("AcademyUser", back_populates="xp_transactions")

    __table_args__ = (
        Index("idx_academy_xp_user", "academy_user_id"),
        Index("idx_academy_xp_source", "source_type"),
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for API responses."""
        return {
            "id": self.id,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "source_type": self.source_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AcademyMission(BaseModel):
    """Missao/Quest disponivel."""

    __tablename__ = "academy_missions"

    # Identificacao
    code = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Categoria
    track = Column(String(50), nullable=False, index=True)
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard, expert
    category = Column(String(50), nullable=False)  # bug-fix, feature, docs, test

    # Recompensas
    xp_reward = Column(Integer, nullable=False)
    badge_reward = Column(String(100), nullable=True)

    # Requisitos
    required_level = Column(Integer, default=1, nullable=False)
    prerequisites = Column(JSON, default=list)  # Lista de mission codes

    # GitHub
    github_issue_url = Column(String(500), nullable=True)
    github_repo = Column(String(255), nullable=True)

    # Recursos de aprendizado
    resources = Column(JSON, default=list)  # Lista de {type, title, url}
    video_url = Column(String(500), nullable=True)

    # Agente recomendado
    recommended_agent = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)

    # Estatisticas
    times_completed = Column(Integer, default=0, nullable=False)
    avg_completion_time = Column(Float, nullable=True)

    __table_args__ = (
        Index("idx_academy_mission_track_diff", "track", "difficulty"),
        Index("idx_academy_mission_active", "is_active"),
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for API responses."""
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "track": self.track,
            "difficulty": self.difficulty,
            "category": self.category,
            "xp_reward": self.xp_reward,
            "badge_reward": self.badge_reward,
            "required_level": self.required_level,
            "prerequisites": self.prerequisites or [],
            "github_issue_url": self.github_issue_url,
            "resources": self.resources or [],
            "video_url": self.video_url,
            "recommended_agent": self.recommended_agent,
            "is_featured": self.is_featured,
            "times_completed": self.times_completed,
        }


class AcademyUserMission(BaseModel):
    """Progresso do usuario em uma missao."""

    __tablename__ = "academy_user_missions"

    # Usuario e Missao
    academy_user_id = Column(
        String(36), ForeignKey("academy_users.id"), nullable=False, index=True
    )
    mission_id = Column(
        String(36), ForeignKey("academy_missions.id"), nullable=False, index=True
    )

    # Status
    status = Column(String(50), default="in_progress", nullable=False)
    # in_progress, completed, abandoned

    # Datas
    started_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # GitHub
    pull_request_url = Column(String(500), nullable=True)
    is_pr_merged = Column(Boolean, default=False, nullable=False)

    # Avaliacao
    mentor_feedback = Column(Text, nullable=True)
    xp_awarded = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("idx_academy_user_mission", "academy_user_id", "mission_id"),
        Index("idx_academy_user_mission_status", "status"),
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for API responses."""
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "pull_request_url": self.pull_request_url,
            "is_pr_merged": self.is_pr_merged,
            "xp_awarded": self.xp_awarded,
        }


class AcademyBadge(BaseModel):
    """Badge disponivel para conquistar."""

    __tablename__ = "academy_badges"

    # Identificacao
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Visual
    icon = Column(String(100), nullable=False)  # Nome do icone ou emoji
    color = Column(String(20), nullable=True)
    rarity = Column(String(20), default="common", nullable=False)
    # common, uncommon, rare, epic, legendary

    # Categoria
    category = Column(String(50), nullable=False)
    # contribution, learning, community, streak, special

    # Bonus
    xp_bonus = Column(Integer, default=0, nullable=False)

    # Requisitos para conquistar
    requirement_type = Column(String(50), nullable=False)
    # count, streak, milestone, special
    requirement_target = Column(Integer, default=1, nullable=False)
    requirement_metric = Column(String(100), nullable=False)
    # conversations, missions, contributions, streak_days, etc.

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_secret = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("idx_academy_badge_category", "category"),
        Index("idx_academy_badge_rarity", "rarity"),
    )

    def to_dict(self, hide_secret: bool = True) -> dict[str, Any]:
        """Convert to dict for API responses."""
        if hide_secret and self.is_secret:
            return {
                "code": self.code,
                "name": "???",
                "description": "Badge secreto - continue explorando!",
                "icon": "mystery",
                "rarity": self.rarity,
                "is_secret": True,
            }
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "rarity": self.rarity,
            "category": self.category,
            "xp_bonus": self.xp_bonus,
            "is_secret": self.is_secret,
        }
