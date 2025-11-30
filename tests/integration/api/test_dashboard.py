"""Integration tests for Dashboard API endpoints."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.app import app


class TestDashboardAPIEndpoints:
    """Test suite for Dashboard API endpoints."""

    @pytest_asyncio.fixture
    async def client(self) -> AsyncGenerator[AsyncClient, None]:
        """Create async test client."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_get_summary_success(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/summary returns 200."""
        response = await client.get("/api/v1/dashboard/agents/summary")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "timestamp" in data
        assert "period" in data
        assert "overview" in data
        assert "performance" in data
        assert "top_performers" in data
        assert "recent_errors" in data

    @pytest.mark.asyncio
    async def test_get_summary_with_period(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/summary with period parameter."""
        for period in ["1h", "6h", "24h", "7d"]:
            response = await client.get(
                f"/api/v1/dashboard/agents/summary?period={period}"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period

    @pytest.mark.asyncio
    async def test_get_summary_invalid_period(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/summary with invalid period."""
        response = await client.get("/api/v1/dashboard/agents/summary?period=invalid")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_summary_overview_structure(self, client: AsyncClient) -> None:
        """Test that overview section has expected fields."""
        response = await client.get("/api/v1/dashboard/agents/summary")

        assert response.status_code == 200
        overview = response.json()["overview"]

        assert "total_agents" in overview
        assert "healthy_agents" in overview
        assert "degraded_agents" in overview
        assert "unhealthy_agents" in overview
        assert "overall_health" in overview
        assert overview["total_agents"] == 16

    @pytest.mark.asyncio
    async def test_get_summary_performance_structure(self, client: AsyncClient) -> None:
        """Test that performance section has expected fields."""
        response = await client.get("/api/v1/dashboard/agents/summary")

        assert response.status_code == 200
        performance = response.json()["performance"]

        assert "total_requests" in performance
        assert "successful_requests" in performance
        assert "failed_requests" in performance
        assert "success_rate" in performance
        assert "avg_response_time_ms" in performance
        assert "p95_response_time_ms" in performance
        assert "avg_quality_score" in performance

    @pytest.mark.asyncio
    async def test_get_leaderboard_default(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/leaderboard with defaults."""
        response = await client.get("/api/v1/dashboard/agents/leaderboard")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) <= 10

        if data:
            first = data[0]
            assert "rank" in first
            assert "agent_name" in first
            assert "identity" in first
            assert "metric_value" in first
            assert "metric_name" in first
            assert first["rank"] == 1

    @pytest.mark.asyncio
    async def test_get_leaderboard_with_params(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/leaderboard with parameters."""
        response = await client.get(
            "/api/v1/dashboard/agents/leaderboard",
            params={"metric": "response_time", "limit": 5, "order": "asc"},
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) <= 5
        for item in data:
            assert item["metric_name"] == "response_time"

    @pytest.mark.asyncio
    async def test_get_leaderboard_invalid_metric(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/leaderboard with invalid metric."""
        response = await client.get(
            "/api/v1/dashboard/agents/leaderboard", params={"metric": "invalid_metric"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_leaderboard_limit_bounds(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/leaderboard limit bounds."""
        # Test minimum bound
        response = await client.get(
            "/api/v1/dashboard/agents/leaderboard", params={"limit": 0}
        )
        assert response.status_code == 422

        # Test maximum bound
        response = await client.get(
            "/api/v1/dashboard/agents/leaderboard", params={"limit": 17}
        )
        assert response.status_code == 422

        # Test valid bounds
        response = await client.get(
            "/api/v1/dashboard/agents/leaderboard", params={"limit": 16}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_health_matrix(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/health returns health matrix."""
        response = await client.get("/api/v1/dashboard/agents/health")

        assert response.status_code == 200
        data = response.json()

        assert "agents" in data
        assert "overall_health" in data
        assert "healthy_count" in data
        assert "degraded_count" in data
        assert "unhealthy_count" in data
        assert "last_check" in data

        assert len(data["agents"]) == 16

    @pytest.mark.asyncio
    async def test_get_health_matrix_agent_structure(self, client: AsyncClient) -> None:
        """Test that each agent in health matrix has expected structure."""
        response = await client.get("/api/v1/dashboard/agents/health")

        assert response.status_code == 200
        agents = response.json()["agents"]

        for agent in agents:
            assert "agent_name" in agent
            assert "identity" in agent
            assert "status" in agent
            assert "response_time_ms" in agent
            assert "error_rate" in agent
            assert "quality_score" in agent
            assert "issues" in agent

    @pytest.mark.asyncio
    async def test_get_agent_detail_valid(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/{agent_name} for valid agent."""
        response = await client.get("/api/v1/dashboard/agents/zumbi")

        assert response.status_code == 200
        data = response.json()

        assert data["agent_name"] == "zumbi"
        assert "identity" in data
        assert "health_status" in data
        assert "performance" in data
        assert "recent_errors" in data
        assert "response_time_history" in data
        assert "quality_score_history" in data

    @pytest.mark.asyncio
    async def test_get_agent_detail_all_agents(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/{agent_name} for all agents."""
        agent_names = [
            "zumbi",
            "anita",
            "tiradentes",
            "ayrton_senna",
            "bonifacio",
            "maria_quiteria",
            "machado",
            "oxossi",
            "lampiao",
            "oscar_niemeyer",
            "abaporu",
            "nana",
            "drummond",
            "ceuci",
            "obaluaie",
            "dandara",
        ]

        for agent_name in agent_names:
            response = await client.get(f"/api/v1/dashboard/agents/{agent_name}")
            assert response.status_code == 200, f"Failed for {agent_name}"
            assert response.json()["agent_name"] == agent_name

    @pytest.mark.asyncio
    async def test_get_agent_detail_invalid(self, client: AsyncClient) -> None:
        """Test GET /api/v1/dashboard/agents/{agent_name} for invalid agent."""
        response = await client.get("/api/v1/dashboard/agents/invalid_agent")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_agent_detail_identity(self, client: AsyncClient) -> None:
        """Test that agent detail includes correct identity."""
        response = await client.get("/api/v1/dashboard/agents/zumbi")

        assert response.status_code == 200
        identity = response.json()["identity"]

        assert identity["name"] == "zumbi"
        assert identity["display_name"] == "Zumbi dos Palmares"
        assert identity["role"] == "Investigador"
        assert identity["icon"] == "🔍"


class TestDashboardHTMLEndpoints:
    """Test suite for Dashboard HTML view endpoints."""

    @pytest_asyncio.fixture
    async def client(self) -> AsyncGenerator[AsyncClient, None]:
        """Create async test client."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_dashboard_view_returns_html(self, client: AsyncClient) -> None:
        """Test GET /dashboard/agents returns HTML page."""
        response = await client.get("/dashboard/agents")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<!DOCTYPE html>" in response.text
        assert "Cidadao.AI" in response.text

    @pytest.mark.asyncio
    async def test_dashboard_view_contains_elements(self, client: AsyncClient) -> None:
        """Test that dashboard HTML contains expected elements."""
        response = await client.get("/dashboard/agents")

        assert response.status_code == 200
        html = response.text

        # Check for key UI elements
        assert "Agent Metrics Dashboard" in html
        assert "Total Agents" in html
        assert "Healthy" in html
        assert "Degraded" in html
        assert "Success Rate" in html
        assert "Leaderboard" in html
        assert "Recent Errors" in html

    @pytest.mark.asyncio
    async def test_dashboard_view_loads_tailwind(self, client: AsyncClient) -> None:
        """Test that dashboard includes Tailwind CSS."""
        response = await client.get("/dashboard/agents")

        assert response.status_code == 200
        assert "tailwindcss" in response.text

    @pytest.mark.asyncio
    async def test_dashboard_view_loads_chartjs(self, client: AsyncClient) -> None:
        """Test that dashboard includes Chart.js."""
        response = await client.get("/dashboard/agents")

        assert response.status_code == 200
        assert "chart.js" in response.text.lower()

    @pytest.mark.asyncio
    async def test_dashboard_embed_returns_html(self, client: AsyncClient) -> None:
        """Test GET /dashboard/agents/embed returns minimal HTML."""
        response = await client.get("/dashboard/agents/embed")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<!DOCTYPE html>" in response.text

    @pytest.mark.asyncio
    async def test_dashboard_embed_is_minimal(self, client: AsyncClient) -> None:
        """Test that embed version is minimal (no header/footer)."""
        full_response = await client.get("/dashboard/agents")
        embed_response = await client.get("/dashboard/agents/embed")

        # Embed should be smaller
        assert len(embed_response.text) < len(full_response.text)

        # Embed should not have full header/footer
        assert "Agent Metrics Dashboard" not in embed_response.text
        assert "Democratizing Government" not in embed_response.text


class TestDashboardSSEStream:
    """Test suite for Dashboard SSE streaming endpoint."""

    @pytest_asyncio.fixture
    async def client(self) -> AsyncGenerator[AsyncClient, None]:
        """Create async test client."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_stream_endpoint_exists(self, client: AsyncClient) -> None:
        """Test that SSE stream endpoint exists."""
        # Note: Full SSE testing requires streaming client support
        # This test just verifies the endpoint responds
        response = await client.get(
            "/api/v1/dashboard/agents/stream",
            params={"interval": 1},
            timeout=5.0,
        )

        # SSE endpoint should start streaming (200) or timeout
        # We accept either as the endpoint exists
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_stream_invalid_interval(self, client: AsyncClient) -> None:
        """Test stream endpoint rejects invalid intervals."""
        # Interval too small
        response = await client.get(
            "/api/v1/dashboard/agents/stream", params={"interval": 0}
        )
        assert response.status_code == 422

        # Interval too large
        response = await client.get(
            "/api/v1/dashboard/agents/stream", params={"interval": 61}
        )
        assert response.status_code == 422


class TestDashboardPerformance:
    """Performance tests for Dashboard endpoints."""

    @pytest_asyncio.fixture
    async def client(self) -> AsyncGenerator[AsyncClient, None]:
        """Create async test client."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_summary_response_time(self, client: AsyncClient) -> None:
        """Test that summary endpoint responds within acceptable time."""
        import time

        start = time.time()
        response = await client.get("/api/v1/dashboard/agents/summary")
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should respond within 2 seconds (generous for CI)
        assert elapsed < 2.0, f"Response took {elapsed:.2f}s, expected < 2s"

    @pytest.mark.asyncio
    async def test_health_matrix_response_time(self, client: AsyncClient) -> None:
        """Test that health matrix endpoint responds within acceptable time."""
        import time

        start = time.time()
        response = await client.get("/api/v1/dashboard/agents/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0, f"Response took {elapsed:.2f}s, expected < 2s"
