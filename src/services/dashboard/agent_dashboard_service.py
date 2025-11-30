"""
Agent Dashboard Service.

Unified service for aggregating agent metrics into dashboard views.
Integrates with existing AgentMetricsService and provides:
- Summary dashboard with all agents
- Leaderboard rankings
- Health matrix
- Real-time streaming via SSE
"""

import asyncio
import contextlib
import statistics
from collections import defaultdict
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from src.core import get_logger
from src.schemas.dashboard import (
    AgentDashboardSummary,
    AgentDetailedMetrics,
    AgentError,
    AgentHealthMatrix,
    AgentHealthStatus,
    AgentIdentity,
    AgentPerformanceMetrics,
    AgentRanking,
    DashboardOverview,
    DashboardPerformance,
    HealthStatus,
    TrendDirection,
)
from src.services.agent_metrics import agent_metrics_service

logger = get_logger("dashboard.service")


# Agent identities with Brazilian cultural context
AGENT_IDENTITIES: dict[str, dict[str, str]] = {
    "zumbi": {
        "display_name": "Zumbi dos Palmares",
        "role": "Investigador",
        "icon": "🔍",
        "description": "Detecta anomalias e investiga irregularidades em contratos",
    },
    "anita": {
        "display_name": "Anita Garibaldi",
        "role": "Analista",
        "icon": "📊",
        "description": "Analisa padrões e tendências em dados de transparência",
    },
    "tiradentes": {
        "display_name": "Tiradentes",
        "role": "Relator",
        "icon": "📝",
        "description": "Gera relatórios detalhados das investigações",
    },
    "ayrton_senna": {
        "display_name": "Ayrton Senna",
        "role": "Roteador Semântico",
        "icon": "🏎️",
        "description": "Direciona consultas para os agentes especializados",
    },
    "bonifacio": {
        "display_name": "José Bonifácio",
        "role": "Jurídico",
        "icon": "⚖️",
        "description": "Analisa aspectos legais e normativos",
    },
    "maria_quiteria": {
        "display_name": "Maria Quitéria",
        "role": "Segurança",
        "icon": "🛡️",
        "description": "Audita segurança e conformidade",
    },
    "machado": {
        "display_name": "Machado de Assis",
        "role": "Análise Textual",
        "icon": "✍️",
        "description": "Processa e analisa textos e documentos",
    },
    "oxossi": {
        "display_name": "Oxóssi",
        "role": "Caçador de Dados",
        "icon": "🎯",
        "description": "Busca e coleta dados de múltiplas fontes",
    },
    "lampiao": {
        "display_name": "Lampião",
        "role": "Regional",
        "icon": "🗺️",
        "description": "Especialista em dados regionais e estaduais",
    },
    "oscar_niemeyer": {
        "display_name": "Oscar Niemeyer",
        "role": "Agregador",
        "icon": "🏛️",
        "description": "Consolida e estrutura dados de múltiplas fontes",
    },
    "abaporu": {
        "display_name": "Abaporu",
        "role": "Orquestrador",
        "icon": "🎭",
        "description": "Coordena investigações multi-agentes",
    },
    "nana": {
        "display_name": "Nanã",
        "role": "Memória",
        "icon": "🧠",
        "description": "Gerencia contexto e histórico de investigações",
    },
    "drummond": {
        "display_name": "Carlos Drummond",
        "role": "Comunicação",
        "icon": "💬",
        "description": "Interface de comunicação com usuários",
    },
    "ceuci": {
        "display_name": "Céuci",
        "role": "ETL/Preditivo",
        "icon": "🔮",
        "description": "Processamento de dados e análise preditiva",
    },
    "obaluaie": {
        "display_name": "Obaluaiê",
        "role": "Detecção de Corrupção",
        "icon": "🚨",
        "description": "Identifica padrões de corrupção",
    },
    "dandara": {
        "display_name": "Dandara",
        "role": "Equidade Social",
        "icon": "✊",
        "description": "Analisa impacto social e equidade",
    },
}

# Health thresholds
HEALTH_THRESHOLDS = {
    "response_time": {"healthy": 1000, "degraded": 3000},  # ms
    "error_rate": {"healthy": 0.05, "degraded": 0.15},  # percentage
    "quality_score": {"healthy": 0.8, "degraded": 0.6},  # 0-1
}


# Constants for trend calculation
MIN_VALUES_FOR_TREND = 2


class AgentDashboardService:
    """Service for aggregating agent metrics into dashboard views."""

    def __init__(self) -> None:
        self.logger = logger
        self._metrics_service = agent_metrics_service
        self._activity_buffer: dict[str, list[int]] = defaultdict(
            lambda: [0] * 60
        )  # Last 60 minutes
        self._last_activity_update = datetime.now(UTC)

    def _get_agent_identity(self, agent_name: str) -> AgentIdentity:
        """Get agent identity information."""
        identity_data = AGENT_IDENTITIES.get(
            agent_name,
            {
                "display_name": agent_name.replace("_", " ").title(),
                "role": "Agente",
                "icon": "🤖",
                "description": f"Agente {agent_name}",
            },
        )

        return AgentIdentity(
            name=agent_name,
            display_name=identity_data["display_name"],
            role=identity_data["role"],
            icon=identity_data["icon"],
            description=identity_data.get("description", ""),
        )

    def _calculate_health_status(
        self,
        response_time_ms: float,
        error_rate: float,
        quality_score: float,
    ) -> HealthStatus:
        """Calculate health status based on metrics."""
        # Check for unhealthy conditions
        if (
            response_time_ms > HEALTH_THRESHOLDS["response_time"]["degraded"]
            or error_rate > HEALTH_THRESHOLDS["error_rate"]["degraded"]
            or quality_score < HEALTH_THRESHOLDS["quality_score"]["degraded"]
        ):
            return HealthStatus.UNHEALTHY

        # Check for degraded conditions
        if (
            response_time_ms > HEALTH_THRESHOLDS["response_time"]["healthy"]
            or error_rate > HEALTH_THRESHOLDS["error_rate"]["healthy"]
            or quality_score < HEALTH_THRESHOLDS["quality_score"]["healthy"]
        ):
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def _calculate_trend(
        self, current_value: float, previous_values: list[float]
    ) -> TrendDirection:
        """Calculate trend direction based on recent values."""
        if not previous_values or len(previous_values) < MIN_VALUES_FOR_TREND:
            return TrendDirection.STABLE

        avg_previous = statistics.mean(previous_values[-5:])
        threshold = avg_previous * 0.1  # 10% change threshold

        if current_value > avg_previous + threshold:
            return TrendDirection.UP
        if current_value < avg_previous - threshold:
            return TrendDirection.DOWN

        return TrendDirection.STABLE

    async def _process_agent_for_summary(
        self, agent_name: str
    ) -> tuple[AgentRanking | None, AgentError | None, HealthStatus | None]:
        """Process a single agent for the summary."""
        agent_stats = await self._metrics_service.get_agent_stats(agent_name)

        if agent_stats.get("status") == "no_data":
            return None, None, None

        # Extract metrics
        response_time_data = agent_stats.get("response_time", {})
        quality_data = agent_stats.get("quality", {})

        avg_response_time = response_time_data.get("mean", 0) * 1000  # to ms
        p95_response_time = response_time_data.get("p95", 0) * 1000
        success_rate = agent_stats.get("success_rate", 0)
        error_rate = agent_stats.get("error_rate", 0)
        quality_score = quality_data.get("mean", 0)

        # Calculate health
        health = self._calculate_health_status(
            avg_response_time, error_rate, quality_score
        )

        # Build performance metrics
        performance = AgentPerformanceMetrics(
            total_requests=agent_stats.get("total_requests", 0),
            successful_requests=agent_stats.get("successful_requests", 0),
            failed_requests=agent_stats.get("failed_requests", 0),
            success_rate=success_rate * 100,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            avg_quality_score=quality_score,
            error_rate_5min=error_rate * 100,
        )

        # Build ranking entry
        ranking = AgentRanking(
            rank=0,  # Will be set later
            agent_name=agent_name,
            identity=self._get_agent_identity(agent_name),
            metric_value=success_rate * 100,
            metric_name="success_rate",
            trend=TrendDirection.STABLE,
            performance=performance,
            health_status=health,
        )

        # Check for recent errors
        error_entry = None
        last_error = agent_stats.get("last_error")
        last_failure_time = agent_stats.get("last_failure_time")

        if last_error and last_failure_time:
            with contextlib.suppress(ValueError, TypeError):
                error_entry = AgentError(
                    agent_name=agent_name,
                    error_type="AgentError",
                    message=last_error[:200],
                    timestamp=datetime.fromisoformat(last_failure_time),
                )

        return ranking, error_entry, health

    def _build_summary_response(  # noqa: PLR0913
        self,
        period: str,
        all_stats: dict[str, Any],
        agent_rankings: list[AgentRanking],
        recent_errors: list[AgentError],
        health_counts: tuple[int, int, int],
    ) -> AgentDashboardSummary:
        """Build the summary response object."""
        healthy_count, degraded_count, unhealthy_count = health_counts
        total_agents = len(AGENT_IDENTITIES)

        # Calculate overall health
        if unhealthy_count > total_agents * 0.3:
            overall_health = HealthStatus.UNHEALTHY
        elif degraded_count > total_agents * 0.3 or unhealthy_count > 0:
            overall_health = HealthStatus.DEGRADED
        else:
            overall_health = HealthStatus.HEALTHY

        # Calculate performance totals
        total_requests = all_stats.get("total_requests", 0)
        total_successful = all_stats.get("total_successful", 0)
        total_failed = all_stats.get("total_failed", 0)

        # Calculate averages across all agents
        all_response_times = [
            r.performance.avg_response_time_ms
            for r in agent_rankings
            if r.performance.avg_response_time_ms > 0
        ]
        all_p95_times = [
            r.performance.p95_response_time_ms
            for r in agent_rankings
            if r.performance.p95_response_time_ms > 0
        ]
        all_quality_scores = [
            r.performance.avg_quality_score
            for r in agent_rankings
            if r.performance.avg_quality_score > 0
        ]

        overview = DashboardOverview(
            total_agents=total_agents,
            healthy_agents=healthy_count,
            degraded_agents=degraded_count,
            unhealthy_agents=unhealthy_count,
            overall_health=overall_health,
        )

        perf = DashboardPerformance(
            total_requests=total_requests,
            successful_requests=total_successful,
            failed_requests=total_failed,
            success_rate=(
                (total_successful / total_requests * 100) if total_requests > 0 else 0
            ),
            avg_response_time_ms=(
                statistics.mean(all_response_times) if all_response_times else 0
            ),
            p95_response_time_ms=(
                statistics.mean(all_p95_times) if all_p95_times else 0
            ),
            avg_quality_score=(
                statistics.mean(all_quality_scores) if all_quality_scores else 0
            ),
        )

        # Sort errors by timestamp (most recent first)
        recent_errors.sort(key=lambda x: x.timestamp, reverse=True)

        # Generate activity heatmap data
        activity_heatmap = {
            "last_hour": self._activity_buffer.get("total", [0] * 6)[-6:]
        }

        return AgentDashboardSummary(
            timestamp=datetime.now(UTC),
            period=period,
            overview=overview,
            performance=perf,
            top_performers=agent_rankings[:10],
            recent_errors=recent_errors[:10],
            activity_heatmap=activity_heatmap,
        )

    async def get_summary(self, period: str = "24h") -> AgentDashboardSummary:
        """Get complete dashboard summary."""
        try:
            all_stats = await self._metrics_service.get_all_agents_summary()

            healthy_count = 0
            degraded_count = 0
            unhealthy_count = 0

            agent_rankings: list[AgentRanking] = []
            recent_errors: list[AgentError] = []

            # Process each agent
            for agent_name in AGENT_IDENTITIES:
                ranking, error_entry, health = await self._process_agent_for_summary(
                    agent_name
                )

                if ranking is None:
                    continue

                agent_rankings.append(ranking)

                if error_entry:
                    recent_errors.append(error_entry)

                if health == HealthStatus.HEALTHY:
                    healthy_count += 1
                elif health == HealthStatus.DEGRADED:
                    degraded_count += 1
                else:
                    unhealthy_count += 1

            # Sort rankings by success rate (descending)
            agent_rankings.sort(key=lambda x: x.metric_value, reverse=True)
            for i, ranking in enumerate(agent_rankings):
                ranking.rank = i + 1

            return self._build_summary_response(
                period,
                all_stats,
                agent_rankings,
                recent_errors,
                (healthy_count, degraded_count, unhealthy_count),
            )

        except Exception as e:
            self.logger.error(f"Error getting dashboard summary: {e}")
            return AgentDashboardSummary(
                timestamp=datetime.now(UTC),
                period=period,
                overview=DashboardOverview(total_agents=len(AGENT_IDENTITIES)),
                performance=DashboardPerformance(),
                top_performers=[],
                recent_errors=[],
                activity_heatmap={},
            )

    async def get_leaderboard(
        self,
        metric: str = "success_rate",
        limit: int = 10,
        order: str = "desc",
    ) -> list[AgentRanking]:
        """Get agent leaderboard ranked by specified metric."""
        summary = await self.get_summary()

        rankings = summary.top_performers

        # Re-sort by requested metric
        metric_extractors = {
            "success_rate": lambda r: r.performance.success_rate,
            "response_time": lambda r: r.performance.avg_response_time_ms,
            "requests": lambda r: r.performance.total_requests,
            "quality_score": lambda r: r.performance.avg_quality_score,
        }

        extractor = metric_extractors.get(metric, metric_extractors["success_rate"])
        reverse = order.lower() != "asc"

        # For response_time, lower is better (so reverse the order)
        if metric == "response_time":
            reverse = not reverse

        rankings.sort(key=extractor, reverse=reverse)

        # Update ranks and metric info
        for i, ranking in enumerate(rankings[:limit]):
            ranking.rank = i + 1
            ranking.metric_name = metric
            ranking.metric_value = extractor(ranking)

        return rankings[:limit]

    async def get_agent_detail(self, agent_name: str) -> AgentDetailedMetrics | None:
        """Get detailed metrics for a specific agent."""
        if agent_name not in AGENT_IDENTITIES:
            return None

        agent_stats = await self._metrics_service.get_agent_stats(agent_name)

        if agent_stats.get("status") == "no_data":
            # Return basic info even if no metrics
            return AgentDetailedMetrics(
                agent_name=agent_name,
                identity=self._get_agent_identity(agent_name),
                health_status=HealthStatus.UNKNOWN,
                performance=AgentPerformanceMetrics(),
                recent_errors=[],
                response_time_history=[],
                quality_score_history=[],
                last_activity=None,
                uptime_percentage=100.0,
                metadata={"status": "no_data"},
            )

        # Extract metrics
        response_time_data = agent_stats.get("response_time", {})
        quality_data = agent_stats.get("quality", {})

        avg_response_time = response_time_data.get("mean", 0) * 1000
        error_rate = agent_stats.get("error_rate", 0)
        quality_score = quality_data.get("mean", 0)

        health = self._calculate_health_status(
            avg_response_time, error_rate, quality_score
        )

        performance = AgentPerformanceMetrics(
            total_requests=agent_stats.get("total_requests", 0),
            successful_requests=agent_stats.get("successful_requests", 0),
            failed_requests=agent_stats.get("failed_requests", 0),
            success_rate=agent_stats.get("success_rate", 0) * 100,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=response_time_data.get("p95", 0) * 1000,
            avg_quality_score=quality_score,
            error_rate_5min=error_rate * 100,
        )

        # Parse last activity time
        last_success = agent_stats.get("last_success_time")
        last_activity = None
        if last_success:
            with contextlib.suppress(ValueError, TypeError):
                last_activity = datetime.fromisoformat(last_success)

        # Build recent errors list
        recent_errors = []
        last_error = agent_stats.get("last_error")
        last_failure_time = agent_stats.get("last_failure_time")

        if last_error and last_failure_time:
            with contextlib.suppress(ValueError, TypeError):
                recent_errors.append(
                    AgentError(
                        agent_name=agent_name,
                        error_type="AgentError",
                        message=last_error[:200],
                        timestamp=datetime.fromisoformat(last_failure_time),
                    )
                )

        return AgentDetailedMetrics(
            agent_name=agent_name,
            identity=self._get_agent_identity(agent_name),
            health_status=health,
            performance=performance,
            recent_errors=recent_errors,
            response_time_history=[],  # Would need historical data storage
            quality_score_history=[],  # Would need historical data storage
            last_activity=last_activity,
            uptime_percentage=100.0 - (error_rate * 100),
            metadata={
                "actions": agent_stats.get("actions", {}),
                "reflection": agent_stats.get("reflection", {}),
                "memory_usage": agent_stats.get("memory_usage", {}),
            },
        )

    async def _process_agent_health(
        self, agent_name: str
    ) -> tuple[AgentHealthStatus, HealthStatus]:
        """Process health status for a single agent."""
        agent_stats = await self._metrics_service.get_agent_stats(agent_name)

        if agent_stats.get("status") == "no_data":
            return (
                AgentHealthStatus(
                    agent_name=agent_name,
                    identity=self._get_agent_identity(agent_name),
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0,
                    error_rate=0,
                    quality_score=0,
                    last_activity=None,
                    issues=["No data available"],
                ),
                HealthStatus.UNKNOWN,
            )

        response_time_data = agent_stats.get("response_time", {})
        quality_data = agent_stats.get("quality", {})

        avg_response_time = response_time_data.get("mean", 0) * 1000
        error_rate = agent_stats.get("error_rate", 0)
        quality_score = quality_data.get("mean", 0)

        health = self._calculate_health_status(
            avg_response_time, error_rate, quality_score
        )

        # Identify issues
        issues = []
        if avg_response_time > HEALTH_THRESHOLDS["response_time"]["healthy"]:
            issues.append(f"High response time: {avg_response_time:.0f}ms")
        if error_rate > HEALTH_THRESHOLDS["error_rate"]["healthy"]:
            issues.append(f"High error rate: {error_rate * 100:.1f}%")
        if quality_score < HEALTH_THRESHOLDS["quality_score"]["healthy"]:
            issues.append(f"Low quality score: {quality_score:.2f}")

        # Parse last activity
        last_success = agent_stats.get("last_success_time")
        last_activity = None
        if last_success:
            with contextlib.suppress(ValueError, TypeError):
                last_activity = datetime.fromisoformat(last_success)

        return (
            AgentHealthStatus(
                agent_name=agent_name,
                identity=self._get_agent_identity(agent_name),
                status=health,
                response_time_ms=avg_response_time,
                error_rate=error_rate * 100,
                quality_score=quality_score,
                last_activity=last_activity,
                issues=issues,
            ),
            health,
        )

    async def get_health_matrix(self) -> AgentHealthMatrix:
        """Get health status matrix for all agents."""
        agents_health: list[AgentHealthStatus] = []

        healthy_count = 0
        degraded_count = 0
        unhealthy_count = 0

        for agent_name in AGENT_IDENTITIES:
            agent_health, health_status = await self._process_agent_health(agent_name)
            agents_health.append(agent_health)

            if health_status == HealthStatus.HEALTHY:
                healthy_count += 1
            elif health_status == HealthStatus.DEGRADED:
                degraded_count += 1
            elif health_status == HealthStatus.UNHEALTHY:
                unhealthy_count += 1

        # Calculate overall health
        total = len(AGENT_IDENTITIES)
        if unhealthy_count > total * 0.3:
            overall_health = HealthStatus.UNHEALTHY
        elif degraded_count > total * 0.3 or unhealthy_count > 0:
            overall_health = HealthStatus.DEGRADED
        else:
            overall_health = HealthStatus.HEALTHY

        return AgentHealthMatrix(
            agents=agents_health,
            overall_health=overall_health,
            healthy_count=healthy_count,
            degraded_count=degraded_count,
            unhealthy_count=unhealthy_count,
            last_check=datetime.now(UTC),
        )

    async def stream_metrics(
        self, interval_seconds: int = 5
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream dashboard metrics for real-time updates."""
        while True:
            try:
                summary = await self.get_summary()
                yield {
                    "event": "metrics_update",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "data": summary.model_dump(mode="json"),
                }
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error streaming metrics: {e}")
                yield {
                    "event": "error",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "data": {"error": str(e)},
                }
                await asyncio.sleep(interval_seconds)


# Global service instance
agent_dashboard_service = AgentDashboardService()
