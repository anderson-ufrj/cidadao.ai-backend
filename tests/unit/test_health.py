"""Unit tests for health check endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


class TestSimpleHealth:
    """Tests for GET /health/ — fast check with no external dependencies."""

    @pytest.mark.unit
    def test_returns_200(self):
        """Simple health endpoint must return HTTP 200."""
        response = client.get("/health/")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_status_field_is_ok(self):
        """Response body must contain status == 'ok'."""
        response = client.get("/health/")
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.unit
    def test_timestamp_field_present(self):
        """Response body must include a timestamp field."""
        response = client.get("/health/")
        data = response.json()
        assert "timestamp" in data

    @pytest.mark.unit
    def test_content_type_is_json(self):
        """Response must be JSON."""
        response = client.get("/health/")
        assert "application/json" in response.headers["content-type"]


class TestLivenessProbe:
    """Tests for GET /health/live — Kubernetes liveness probe."""

    @pytest.mark.unit
    def test_returns_200(self):
        """Liveness probe must return HTTP 200."""
        response = client.get("/health/live")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_status_field_is_alive(self):
        """Response body must contain status == 'alive'."""
        response = client.get("/health/live")
        data = response.json()
        assert data["status"] == "alive"

    @pytest.mark.unit
    def test_timestamp_field_present(self):
        """Response body must include a timestamp field."""
        response = client.get("/health/live")
        data = response.json()
        assert "timestamp" in data


_HEALTHY_TRANSPARENCY = {
    "status": "healthy",
    "response_time": 0.1,
    "last_checked": "2026-01-01T00:00:00+00:00",
    "endpoint": "Portal da Transparência API",
}


class TestReadinessProbe:
    """Tests for GET /health/ready — readiness probe with mocked external call."""

    @pytest.mark.unit
    def test_returns_200_when_transparency_healthy(self):
        """Ready endpoint returns 200 when external API is healthy."""
        with patch(
            "src.api.routes.health._check_transparency_api",
            new=AsyncMock(return_value=_HEALTHY_TRANSPARENCY),
        ):
            response = client.get("/health/ready")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_status_is_ready(self):
        """Response body must contain status == 'ready'."""
        with patch(
            "src.api.routes.health._check_transparency_api",
            new=AsyncMock(return_value=_HEALTHY_TRANSPARENCY),
        ):
            response = client.get("/health/ready")
        assert response.json()["status"] == "ready"

    @pytest.mark.unit
    def test_still_ready_when_transparency_degraded(self):
        """Ready endpoint stays 200 even when external API is degraded."""
        degraded = {**_HEALTHY_TRANSPARENCY, "status": "unhealthy"}
        with patch(
            "src.api.routes.health._check_transparency_api",
            new=AsyncMock(return_value=degraded),
        ):
            response = client.get("/health/ready")
        data = response.json()
        assert response.status_code == 200
        assert data["status"] == "ready"
        assert data.get("degraded") is True


_HEALTHY_DB = {
    "status": "healthy",
    "response_time": 0.01,
    "last_checked": "2026-01-01T00:00:00+00:00",
    "connection": "active",
}

_HEALTHY_REDIS = {
    "status": "healthy",
    "response_time": 0.005,
    "last_checked": "2026-01-01T00:00:00+00:00",
    "connection": "active",
    "redis_version": "7.0.0",
}


class TestFullHealthStatus:
    """Tests for GET /health/status — comprehensive check with all services mocked."""

    @pytest.fixture(autouse=True)
    def mock_all_services(self):
        with (
            patch(
                "src.api.routes.health._check_transparency_api",
                new=AsyncMock(return_value=_HEALTHY_TRANSPARENCY),
            ),
            patch(
                "src.api.routes.health._check_database",
                new=AsyncMock(return_value=_HEALTHY_DB),
            ),
            patch(
                "src.api.routes.health._check_redis",
                new=AsyncMock(return_value=_HEALTHY_REDIS),
            ),
        ):
            yield

    @pytest.mark.unit
    def test_returns_200(self):
        """Status endpoint returns HTTP 200 when all services are healthy."""
        response = client.get("/health/status")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_overall_status_is_healthy(self):
        """Response body must report overall status == 'healthy'."""
        response = client.get("/health/status")
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.unit
    def test_services_dict_contains_expected_keys(self):
        """Response must include transparency_api, database and redis in services."""
        response = client.get("/health/status")
        services = response.json()["services"]
        assert "transparency_api" in services
        assert "database" in services
        assert "redis" in services

    @pytest.mark.unit
    def test_status_degraded_when_one_service_unhealthy(self):
        """Overall status must be 'degraded' when any service is unhealthy."""
        unhealthy_db = {**_HEALTHY_DB, "status": "unhealthy"}
        with patch(
            "src.api.routes.health._check_database",
            new=AsyncMock(return_value=unhealthy_db),
        ):
            response = client.get("/health/status")
        assert response.json()["status"] == "degraded"
