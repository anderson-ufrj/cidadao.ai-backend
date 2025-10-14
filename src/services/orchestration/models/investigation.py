"""
Investigation Models

Data models for investigation planning and execution.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class InvestigationIntent(str, Enum):
    """Types of investigations supported."""

    SUPPLIER_INVESTIGATION = "supplier_investigation"
    CONTRACT_ANOMALY_DETECTION = "contract_anomaly_detection"
    BUDGET_ANALYSIS = "budget_analysis"
    HEALTH_BUDGET_ANALYSIS = "health_budget_analysis"
    EDUCATION_PERFORMANCE = "education_performance"
    CORRUPTION_INDICATORS = "corruption_indicators"
    GENERAL_QUERY = "general_query"


class InvestigationContext(BaseModel):
    """Context for an investigation."""

    user_query: str
    user_id: str | None = None
    session_id: str | None = None

    # Extracted entities
    company_name: str | None = None
    cnpj: str | None = None
    cpf: str | None = None
    agency_code: str | None = None
    agency_name: str | None = None

    # Time range
    start_date: str | None = None
    end_date: str | None = None
    year: int | None = None

    # Location
    state: str | None = None
    city: str | None = None

    # Additional context
    metadata: dict[str, Any] = Field(default_factory=dict)


class Stage(BaseModel):
    """Execution stage in investigation plan."""

    name: str
    apis: list[str]
    method: str
    parallel: bool = False
    depends_on: list[str] = Field(default_factory=list)
    reason: str
    timeout_seconds: int = 30
    retry_count: int = 3
    cache_ttl: int | None = None


class ExecutionPlan(BaseModel):
    """Complete execution plan for investigation."""

    intent: InvestigationIntent
    entities: dict[str, Any]
    stages: list[Stage]
    estimated_duration_seconds: float
    cache_strategy: str = "aggressive"  # aggressive, moderate, minimal
    created_at: datetime = Field(default_factory=datetime.now)


class StageResult(BaseModel):
    """Result from a single stage execution."""

    stage_name: str
    status: str  # success, partial_success, failed
    data: dict[str, Any]
    api_calls: list[str]
    duration_seconds: float
    errors: list[str] = Field(default_factory=list)


class InvestigationResult(BaseModel):
    """Complete investigation result."""

    investigation_id: str
    intent: InvestigationIntent
    context: InvestigationContext
    plan: ExecutionPlan

    # Results
    stage_results: list[StageResult] = Field(default_factory=list)
    entities_found: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    anomalies: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    total_duration_seconds: float = 0.0
    data_sources_used: list[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    status: str = "pending"  # pending, running, completed, failed

    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    def add_stage_result(self, stage: str, result: StageResult) -> None:
        """Add result from a stage."""
        self.stage_results.append(result)
        self.total_duration_seconds += result.duration_seconds
        self.data_sources_used.extend(result.api_calls)
        # Remove duplicates
        self.data_sources_used = list(set(self.data_sources_used))

    def mark_running(self) -> None:
        """Mark investigation as running."""
        self.status = "running"
        self.started_at = datetime.now()

    def mark_completed(self) -> None:
        """Mark investigation as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Mark investigation as failed."""
        self.status = "failed"
        self.completed_at = datetime.now()
