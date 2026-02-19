"""Unit tests for AgentDashboardService."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.schemas.dashboard import (
    AgentDashboardSummary,
    AgentDetailedMetrics,
    AgentHealthMatrix,
    AgentRanking,
    HealthStatus,
    TrendDirection,
)
from src.services.dashboard.agent_dashboard_service import (
    AGENT_IDENTITIES,
    HEALTH_THRESHOLDS,
    AgentDashboardService,
)


class TestAgentDashboardService:
    """Test suite for AgentDashboardService."""

    @pytest.fixture
    def service(self) -> AgentDashboardService:
        """Create service instance for testing."""
        return AgentDashboardService()

    @pytest.fixture
    def mock_metrics_service(self) -> MagicMock:
        """Create mock metrics service."""
        mock = MagicMock()
        mock.get_agent_stats = AsyncMock(
            return_value={
                "total_requests": 100,
                "successful_requests": 95,
                "failed_requests": 5,
                "success_rate": 0.95,
                "error_rate": 0.05,
                "response_time": {"mean": 0.250, "p95": 0.500},
                "quality": {"mean": 0.9},
                "last_success_time": datetime.now(UTC).isoformat(),
            }
        )
        mock.get_all_agents_summary = AsyncMock(
            return_value={
                "total_requests": 1000,
                "total_successful": 950,
                "total_failed": 50,
            }
        )
        return mock

    def test_agent_identities_count(self) -> None:
        """Test that all 16 agents have identities defined."""
        assert len(AGENT_IDENTITIES) == 16

    def test_agent_identities_structure(self) -> None:
        """Test that agent identities have required fields."""
        required_fields = {"display_name", "role", "icon", "description"}
        for agent_name, identity in AGENT_IDENTITIES.items():
            for field in required_fields:
                assert field in identity, f"{agent_name} missing {field}"

    def test_zumbi_identity(self) -> None:
        """Test Zumbi agent identity."""
        zumbi = AGENT_IDENTITIES["zumbi"]
        assert zumbi["display_name"] == "Zumbi dos Palmares"
        assert zumbi["role"] == "Investigador"
        assert zumbi["icon"] == "🔍"  # Investigator icon

    def test_health_thresholds_defined(self) -> None:
        """Test that health thresholds are properly defined."""
        assert "response_time" in HEALTH_THRESHOLDS
        assert "error_rate" in HEALTH_THRESHOLDS
        assert "quality_score" in HEALTH_THRESHOLDS

        assert HEALTH_THRESHOLDS["response_time"]["healthy"] == 1000
        assert HEALTH_THRESHOLDS["error_rate"]["healthy"] == 0.05
        assert HEALTH_THRESHOLDS["quality_score"]["healthy"] == 0.8

    def test_calculate_health_status_healthy(
        self, service: AgentDashboardService
    ) -> None:
        """Test health calculation for healthy metrics."""
        status = service._calculate_health_status(
            response_time_ms=500.0,
            error_rate=0.02,
            quality_score=0.9,
        )
        assert status == HealthStatus.HEALTHY

    def test_calculate_health_status_degraded_response_time(
        self, service: AgentDashboardService
    ) -> None:
        """Test health calculation for slow response time."""
        status = service._calculate_health_status(
            response_time_ms=2000.0,
            error_rate=0.02,
            quality_score=0.9,
        )
        assert status == HealthStatus.DEGRADED

    def test_calculate_health_status_degraded_error_rate(
        self, service: AgentDashboardService
    ) -> None:
        """Test health calculation for elevated error rate."""
        status = service._calculate_health_status(
            response_time_ms=500.0,
            error_rate=0.10,
            quality_score=0.9,
        )
        assert status == HealthStatus.DEGRADED

    def test_calculate_health_status_degraded_quality(
        self, service: AgentDashboardService
    ) -> None:
        """Test health calculation for low quality score."""
        status = service._calculate_health_status(
            response_time_ms=500.0,
            error_rate=0.02,
            quality_score=0.7,
        )
        assert status == HealthStatus.DEGRADED

    def test_calculate_health_status_unhealthy(
        self, service: AgentDashboardService
    ) -> None:
        """Test health calculation for unhealthy metrics."""
        status = service._calculate_health_status(
            response_time_ms=5000.0,
            error_rate=0.20,
            quality_score=0.4,
        )
        assert status == HealthStatus.UNHEALTHY

    def test_calculate_health_status_unhealthy_response_time(
        self, service: AgentDashboardService
    ) -> None:
        """Test unhealthy status from response time alone."""
        status = service._calculate_health_status(
            response_time_ms=3001.0,
            error_rate=0.01,
            quality_score=0.9,
        )
        assert status == HealthStatus.UNHEALTHY

    def test_calculate_trend_stable(self, service: AgentDashboardService) -> None:
        """Test trend calculation returns stable for similar values."""
        trend = service._calculate_trend(100.0, [100.0, 100.0, 100.0, 100.0, 100.0])
        assert trend == TrendDirection.STABLE

    def test_calculate_trend_up(self, service: AgentDashboardService) -> None:
        """Test trend calculation returns up for increasing values."""
        trend = service._calculate_trend(150.0, [100.0, 100.0, 100.0, 100.0, 100.0])
        assert trend == TrendDirection.UP

    def test_calculate_trend_down(self, service: AgentDashboardService) -> None:
        """Test trend calculation returns down for decreasing values."""
        trend = service._calculate_trend(80.0, [100.0, 100.0, 100.0, 100.0, 100.0])
        assert trend == TrendDirection.DOWN

    def test_calculate_trend_insufficient_data(
        self, service: AgentDashboardService
    ) -> None:
        """Test trend calculation returns stable with insufficient data."""
        trend = service._calculate_trend(100.0, [])
        assert trend == TrendDirection.STABLE

        trend = service._calculate_trend(100.0, [100.0])
        assert trend == TrendDirection.STABLE

    def test_get_agent_identity_known(self, service: AgentDashboardService) -> None:
        """Test getting identity for known agent."""
        identity = service._get_agent_identity("zumbi")
        assert identity.name == "zumbi"
        assert identity.display_name == "Zumbi dos Palmares"
        assert identity.role == "Investigador"
        assert identity.icon == "🔍"

    def test_get_agent_identity_unknown(self, service: AgentDashboardService) -> None:
        """Test getting identity for unknown agent returns default."""
        identity = service._get_agent_identity("unknown_agent")
        assert identity.name == "unknown_agent"
        assert identity.display_name == "Unknown Agent"
        assert identity.icon == "🤖"

    @pytest.mark.asyncio
    async def test_get_agent_detail_invalid_agent(
        self, service: AgentDashboardService
    ) -> None:
        """Test getting details for invalid agent returns None."""
        result = await service.get_agent_detail("invalid_agent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_summary_returns_valid_structure_mocked(
        self, service: AgentDashboardService, mock_metrics_service: MagicMock
    ) -> None:
        """Test get_summary returns valid structure with mocked service."""
        service._metrics_service = mock_metrics_service

        result = await service.get_summary(period="24h")

        assert isinstance(result, AgentDashboardSummary)
        assert result.period == "24h"
        assert result.overview.total_agents == 16
        assert isinstance(result.performance.success_rate, float)
        assert isinstance(result.top_performers, list)
        assert isinstance(result.recent_errors, list)

    @pytest.mark.asyncio
    async def test_get_leaderboard_mocked(
        self, service: AgentDashboardService, mock_metrics_service: MagicMock
    ) -> None:
        """Test get_leaderboard with mocked service."""
        service._metrics_service = mock_metrics_service

        result = await service.get_leaderboard(metric="success_rate", limit=5)

        assert isinstance(result, list)
        assert len(result) <= 5
        for ranking in result:
            assert isinstance(ranking, AgentRanking)

    @pytest.mark.asyncio
    async def test_get_health_matrix_mocked(
        self, service: AgentDashboardService, mock_metrics_service: MagicMock
    ) -> None:
        """Test get_health_matrix with mocked service."""
        service._metrics_service = mock_metrics_service

        result = await service.get_health_matrix()

        assert isinstance(result, AgentHealthMatrix)
        assert len(result.agents) == 16
        assert isinstance(result.overall_health, HealthStatus)

    @pytest.mark.asyncio
    async def test_get_agent_detail_mocked(
        self, service: AgentDashboardService, mock_metrics_service: MagicMock
    ) -> None:
        """Test get_agent_detail with mocked service."""
        service._metrics_service = mock_metrics_service

        result = await service.get_agent_detail("zumbi")

        assert result is not None
        assert isinstance(result, AgentDetailedMetrics)
        assert result.agent_name == "zumbi"
        assert result.identity.display_name == "Zumbi dos Palmares"


class TestHealthStatusThresholds:
    """Test health status threshold calculations."""

    @pytest.fixture
    def service(self) -> AgentDashboardService:
        """Create service instance for testing."""
        return AgentDashboardService()

    def test_response_time_thresholds(self, service: AgentDashboardService) -> None:
        """Test response time threshold boundaries."""
        # Healthy: <= 1000ms
        status = service._calculate_health_status(1000.0, 0.0, 1.0)
        assert status == HealthStatus.HEALTHY

        # Degraded: > 1000ms and <= 3000ms
        status = service._calculate_health_status(1001.0, 0.0, 1.0)
        assert status == HealthStatus.DEGRADED

        status = service._calculate_health_status(3000.0, 0.0, 1.0)
        assert status == HealthStatus.DEGRADED

        # Unhealthy: > 3000ms
        status = service._calculate_health_status(3001.0, 0.0, 1.0)
        assert status == HealthStatus.UNHEALTHY

    def test_error_rate_thresholds(self, service: AgentDashboardService) -> None:
        """Test error rate threshold boundaries."""
        # Healthy: <= 5%
        status = service._calculate_health_status(100.0, 0.05, 1.0)
        assert status == HealthStatus.HEALTHY

        # Degraded: > 5% and <= 15%
        status = service._calculate_health_status(100.0, 0.051, 1.0)
        assert status == HealthStatus.DEGRADED

        status = service._calculate_health_status(100.0, 0.15, 1.0)
        assert status == HealthStatus.DEGRADED

        # Unhealthy: > 15%
        status = service._calculate_health_status(100.0, 0.151, 1.0)
        assert status == HealthStatus.UNHEALTHY

    def test_quality_score_thresholds(self, service: AgentDashboardService) -> None:
        """Test quality score threshold boundaries."""
        # Healthy: >= 0.8
        status = service._calculate_health_status(100.0, 0.0, 0.8)
        assert status == HealthStatus.HEALTHY

        # Degraded: >= 0.6 and < 0.8
        status = service._calculate_health_status(100.0, 0.0, 0.79)
        assert status == HealthStatus.DEGRADED

        status = service._calculate_health_status(100.0, 0.0, 0.6)
        assert status == HealthStatus.DEGRADED

        # Unhealthy: < 0.6
        status = service._calculate_health_status(100.0, 0.0, 0.59)
        assert status == HealthStatus.UNHEALTHY


class TestAgentIdentities:
    """Test agent identity data."""

    def test_all_agents_have_brazilian_names(self) -> None:
        """Test all agents have Brazilian hero display names."""
        brazilian_heroes = {
            "Zumbi dos Palmares",
            "Anita Garibaldi",
            "Tiradentes",
            "Ayrton Senna",
            "José Bonifácio",
            "Maria Quitéria",
            "Machado de Assis",
            "Oxóssi",
            "Lampião",
            "Oscar Niemeyer",
            "Abaporu",
            "Nanã",
            "Carlos Drummond",
            "Céuci",
            "Obaluaiê",
            "Dandara",
        }
        actual_names = {
            identity["display_name"] for identity in AGENT_IDENTITIES.values()
        }
        assert actual_names == brazilian_heroes

    def test_all_agents_have_unique_icons(self) -> None:
        """Test all agents have unique emoji icons."""
        icons = [identity["icon"] for identity in AGENT_IDENTITIES.values()]
        assert len(icons) == len(set(icons)), "Icons should be unique per agent"

    def test_all_agents_have_roles(self) -> None:
        """Test all agents have defined roles."""
        for agent_name, identity in AGENT_IDENTITIES.items():
            assert identity["role"], f"{agent_name} should have a role"
            assert len(identity["role"]) > 0

    def test_all_agents_have_descriptions(self) -> None:
        """Test all agents have descriptions."""
        for agent_name, identity in AGENT_IDENTITIES.items():
            assert identity["description"], f"{agent_name} should have a description"
            assert len(identity["description"]) > 10


class TestStreamMetrics:
    """Test streaming metrics functionality."""

    @pytest.fixture
    def service(self) -> AgentDashboardService:
        """Create service instance for testing."""
        return AgentDashboardService()

    @pytest.fixture
    def mock_metrics_service(self) -> MagicMock:
        """Create mock metrics service."""
        mock = MagicMock()
        mock.get_agent_stats = AsyncMock(
            return_value={
                "status": "no_data",
            }
        )
        mock.get_all_agents_summary = AsyncMock(
            return_value={
                "total_requests": 0,
                "total_successful": 0,
                "total_failed": 0,
            }
        )
        return mock

    @pytest.mark.asyncio
    async def test_stream_metrics_yields_events(
        self, service: AgentDashboardService, mock_metrics_service: MagicMock
    ) -> None:
        """Test that stream_metrics yields metric events."""
        service._metrics_service = mock_metrics_service

        events_received = 0
        async for event in service.stream_metrics(interval_seconds=0.1):
            events_received += 1
            assert "event" in event
            assert event["event"] == "metrics_update"
            assert "timestamp" in event
            assert "data" in event
            if events_received >= 2:
                break

        assert events_received >= 2
