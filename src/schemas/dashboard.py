"""Dashboard schemas for agent metrics visualization."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Agent health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class TrendDirection(str, Enum):
    """Trend direction for metrics."""

    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class AgentIdentity(BaseModel):
    """Agent identity information with Brazilian cultural context."""

    name: str = Field(..., description="Agent technical name")
    display_name: str = Field(..., description="Agent display name (Brazilian hero)")
    role: str = Field(..., description="Agent role/specialty")
    icon: str = Field(..., description="Emoji icon for the agent")
    description: str = Field(
        default="", description="Brief description of agent capabilities"
    )


class AgentPerformanceMetrics(BaseModel):
    """Performance metrics for a single agent."""

    total_requests: int = Field(default=0, description="Total requests processed")
    successful_requests: int = Field(default=0, description="Successful requests")
    failed_requests: int = Field(default=0, description="Failed requests")
    success_rate: float = Field(default=0.0, description="Success rate percentage")
    avg_response_time_ms: float = Field(
        default=0.0, description="Average response time in ms"
    )
    p95_response_time_ms: float = Field(
        default=0.0, description="P95 response time in ms"
    )
    avg_quality_score: float = Field(
        default=0.0, description="Average quality score (0-1)"
    )
    error_rate_5min: float = Field(
        default=0.0, description="Error rate in last 5 minutes"
    )


class AgentRanking(BaseModel):
    """Agent ranking entry for leaderboard."""

    rank: int = Field(..., description="Position in ranking")
    agent_name: str = Field(..., description="Agent technical name")
    identity: AgentIdentity = Field(..., description="Agent identity info")
    metric_value: float = Field(..., description="Value of the ranked metric")
    metric_name: str = Field(..., description="Name of the metric used for ranking")
    trend: TrendDirection = Field(
        default=TrendDirection.STABLE, description="Trend direction"
    )
    performance: AgentPerformanceMetrics = Field(
        ..., description="Full performance metrics"
    )
    health_status: HealthStatus = Field(
        default=HealthStatus.UNKNOWN, description="Health status"
    )


class AgentHealthStatus(BaseModel):
    """Health status for a single agent."""

    agent_name: str = Field(..., description="Agent technical name")
    identity: AgentIdentity = Field(..., description="Agent identity info")
    status: HealthStatus = Field(..., description="Current health status")
    response_time_ms: float = Field(default=0.0, description="Current response time")
    error_rate: float = Field(default=0.0, description="Current error rate")
    quality_score: float = Field(default=0.0, description="Current quality score")
    last_activity: datetime | None = Field(
        default=None, description="Last activity timestamp"
    )
    issues: list[str] = Field(default_factory=list, description="Current issues if any")


class AgentError(BaseModel):
    """Recent error entry."""

    agent_name: str = Field(..., description="Agent that encountered the error")
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    timestamp: datetime = Field(..., description="When the error occurred")
    count: int = Field(default=1, description="Number of occurrences")


class DashboardOverview(BaseModel):
    """Overview section of the dashboard."""

    total_agents: int = Field(..., description="Total number of agents")
    healthy_agents: int = Field(default=0, description="Agents with healthy status")
    degraded_agents: int = Field(default=0, description="Agents with degraded status")
    unhealthy_agents: int = Field(default=0, description="Agents with unhealthy status")
    overall_health: HealthStatus = Field(
        default=HealthStatus.UNKNOWN, description="Overall system health"
    )


class DashboardPerformance(BaseModel):
    """Performance section of the dashboard."""

    total_requests: int = Field(
        default=0, description="Total requests across all agents"
    )
    successful_requests: int = Field(default=0, description="Total successful requests")
    failed_requests: int = Field(default=0, description="Total failed requests")
    success_rate: float = Field(default=0.0, description="Overall success rate")
    avg_response_time_ms: float = Field(
        default=0.0, description="Average response time"
    )
    p95_response_time_ms: float = Field(default=0.0, description="P95 response time")
    avg_quality_score: float = Field(default=0.0, description="Average quality score")


class ActivityDataPoint(BaseModel):
    """Single data point for activity chart."""

    timestamp: datetime = Field(..., description="Time of the data point")
    value: int = Field(..., description="Number of requests")


class AgentDashboardSummary(BaseModel):
    """Complete dashboard summary response."""

    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    period: str = Field(default="24h", description="Time period for metrics")
    overview: DashboardOverview = Field(..., description="Overview metrics")
    performance: DashboardPerformance = Field(..., description="Performance metrics")
    top_performers: list[AgentRanking] = Field(
        default_factory=list, description="Top performing agents"
    )
    recent_errors: list[AgentError] = Field(
        default_factory=list, description="Recent errors"
    )
    activity_heatmap: dict[str, list[int]] = Field(
        default_factory=dict, description="Activity data for charts"
    )


class AgentDetailedMetrics(BaseModel):
    """Detailed metrics for a single agent."""

    agent_name: str = Field(..., description="Agent technical name")
    identity: AgentIdentity = Field(..., description="Agent identity info")
    health_status: HealthStatus = Field(..., description="Current health status")
    performance: AgentPerformanceMetrics = Field(..., description="Performance metrics")
    recent_errors: list[AgentError] = Field(
        default_factory=list, description="Recent errors"
    )
    response_time_history: list[float] = Field(
        default_factory=list, description="Response time history (last 60 points)"
    )
    quality_score_history: list[float] = Field(
        default_factory=list, description="Quality score history (last 60 points)"
    )
    last_activity: datetime | None = Field(
        default=None, description="Last activity timestamp"
    )
    uptime_percentage: float = Field(default=100.0, description="Uptime percentage")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class AgentHealthMatrix(BaseModel):
    """Health matrix for all agents."""

    agents: list[AgentHealthStatus] = Field(
        default_factory=list, description="Health status per agent"
    )
    overall_health: HealthStatus = Field(
        default=HealthStatus.UNKNOWN, description="Overall health"
    )
    healthy_count: int = Field(default=0, description="Number of healthy agents")
    degraded_count: int = Field(default=0, description="Number of degraded agents")
    unhealthy_count: int = Field(default=0, description="Number of unhealthy agents")
    last_check: datetime = Field(
        default_factory=datetime.utcnow, description="Last health check time"
    )


class LeaderboardRequest(BaseModel):
    """Request parameters for leaderboard."""

    metric: str = Field(
        default="success_rate",
        description="Metric to rank by: success_rate, response_time, requests, quality_score",
    )
    limit: int = Field(
        default=10, ge=1, le=16, description="Number of agents to return"
    )
    order: str = Field(default="desc", description="Sort order: asc or desc")


class StreamMetricsEvent(BaseModel):
    """SSE event for streaming metrics."""

    event_type: str = Field(default="metrics_update", description="Type of event")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp"
    )
    data: AgentDashboardSummary = Field(..., description="Dashboard data")
