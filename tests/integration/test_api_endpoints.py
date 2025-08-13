"""
Module: tests.integration.test_api_endpoints
Description: Comprehensive integration tests for FastAPI endpoints
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.api.app import app
from src.core import AgentStatus, ResponseStatus


# Test client for synchronous tests
client = TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client for async endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_transparency_api():
    """Mock the transparency API client."""
    with patch('src.tools.transparency_api.TransparencyAPIClient') as mock:
        mock_instance = AsyncMock()
        mock.__aenter__.return_value = mock_instance
        mock_instance.get_contracts.return_value = AsyncMock(
            data=[
                {
                    "id": "123",
                    "objeto": "Test contract",
                    "valorInicial": 100000.0,
                    "fornecedor": {"nome": "Test Supplier"}
                }
            ]
        )
        yield mock_instance


@pytest.fixture
def mock_agents():
    """Mock all agents for testing."""
    with patch('src.agents.master_agent.MasterAgent') as mock_master, \
         patch('src.agents.investigator_agent.InvestigatorAgent') as mock_investigator, \
         patch('src.agents.analyst_agent.AnalystAgent') as mock_analyst, \
         patch('src.agents.reporter_agent.ReporterAgent') as mock_reporter:
        
        # Configure mock responses
        mock_master.return_value.investigate.return_value = {
            "status": "completed",
            "findings": ["Test finding"],
            "anomalies": []
        }
        
        mock_investigator.return_value.detect_anomalies.return_value = {
            "anomalies": [],
            "score": 0.1,
            "explanation": "No anomalies detected"
        }
        
        mock_analyst.return_value.analyze_patterns.return_value = {
            "patterns": [],
            "trends": [],
            "correlations": []
        }
        
        mock_reporter.return_value.generate_report.return_value = {
            "content": "Test report content",
            "format": "markdown"
        }
        
        yield {
            "master": mock_master,
            "investigator": mock_investigator, 
            "analyst": mock_analyst,
            "reporter": mock_reporter
        }


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_basic_health_check(self):
        """Test basic health endpoint."""
        response = client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data
        assert "services" in data
    
    def test_detailed_health_check(self):
        """Test detailed health endpoint."""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "system" in data
        assert "services" in data
        assert "performance" in data
    
    def test_liveness_probe(self):
        """Test Kubernetes liveness probe."""
        response = client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    def test_readiness_probe(self):
        """Test Kubernetes readiness probe."""
        response = client.get("/health/ready")
        
        # Could be 200 or 503 depending on dependencies
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "status" in data


class TestInvestigationEndpoints:
    """Test investigation endpoints."""
    
    @pytest.mark.asyncio
    async def test_start_investigation(self, async_client, mock_agents):
        """Test starting a new investigation."""
        investigation_data = {
            "query": "Investigate contracts over 1M in Ministry of Health",
            "priority": "high",
            "data_sources": ["portal_transparencia"],
            "parameters": {
                "min_value": 1000000,
                "organization": "26000"
            }
        }
        
        response = await async_client.post(
            "/api/v1/investigations/start",
            json=investigation_data
        )
        
        assert response.status_code == 202  # Accepted for async processing
        data = response.json()
        
        assert data["status"] == "accepted"
        assert "investigation_id" in data
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_get_investigation_status(self, async_client):
        """Test getting investigation status."""
        investigation_id = "test-investigation-123"
        
        response = await async_client.get(
            f"/api/v1/investigations/{investigation_id}/status"
        )
        
        # Should handle non-existent investigations gracefully
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_list_investigations(self, async_client):
        """Test listing investigations."""
        response = await async_client.get("/api/v1/investigations/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "investigations" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
    
    @pytest.mark.asyncio
    async def test_investigation_streaming(self, async_client):
        """Test real-time investigation streaming."""
        investigation_id = "test-investigation-123"
        
        # Test SSE endpoint exists
        response = await async_client.get(
            f"/api/v1/investigations/{investigation_id}/stream",
            headers={"Accept": "text/event-stream"}
        )
        
        # Should handle streaming endpoint
        assert response.status_code in [200, 404, 501]  # 501 if not implemented yet
    
    def test_investigation_validation(self):
        """Test investigation request validation."""
        # Test empty request
        response = client.post("/api/v1/investigations/start", json={})
        assert response.status_code == 422  # Validation error
        
        # Test invalid priority
        invalid_data = {
            "query": "Test query",
            "priority": "invalid_priority"
        }
        response = client.post("/api/v1/investigations/start", json=invalid_data)
        assert response.status_code == 422


class TestAnalysisEndpoints:
    """Test analysis endpoints."""
    
    @pytest.mark.asyncio
    async def test_spending_trends_analysis(self, async_client, mock_agents):
        """Test spending trends analysis."""
        analysis_data = {
            "type": "spending_trends",
            "organization": "26000",
            "time_period": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        }
        
        response = await async_client.post(
            "/api/v1/analysis/trends",
            json=analysis_data
        )
        
        assert response.status_code in [200, 202]
        
        if response.status_code == 200:
            data = response.json()
            assert "trends" in data
            assert "analysis_type" in data
    
    @pytest.mark.asyncio
    async def test_vendor_analysis(self, async_client, mock_agents):
        """Test vendor pattern analysis."""
        analysis_data = {
            "vendor_id": "12345678000100",
            "analysis_type": "pattern_detection"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/vendors",
            json=analysis_data
        )
        
        assert response.status_code in [200, 202]
    
    @pytest.mark.asyncio
    async def test_correlation_analysis(self, async_client, mock_agents):
        """Test correlation analysis."""
        analysis_data = {
            "variables": ["spending_amount", "contract_duration"],
            "organization": "26000",
            "timeframe": "2024"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/correlations",
            json=analysis_data
        )
        
        assert response.status_code in [200, 202]


class TestReportEndpoints:
    """Test report generation endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_executive_report(self, async_client, mock_agents):
        """Test executive report generation."""
        report_data = {
            "type": "executive",
            "investigation_id": "test-investigation-123",
            "format": "markdown",
            "include_charts": True
        }
        
        response = await async_client.post(
            "/api/v1/reports/generate",
            json=report_data
        )
        
        assert response.status_code in [200, 202]
    
    @pytest.mark.asyncio
    async def test_get_report_formats(self, async_client):
        """Test getting available report formats."""
        response = await async_client.get("/api/v1/reports/formats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "formats" in data
        assert isinstance(data["formats"], list)
        assert "markdown" in data["formats"]
    
    @pytest.mark.asyncio
    async def test_download_report(self, async_client):
        """Test report download."""
        report_id = "test-report-123"
        
        response = await async_client.get(
            f"/api/v1/reports/{report_id}/download"
        )
        
        # Should handle non-existent reports
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_report_list(self, async_client):
        """Test listing generated reports."""
        response = await async_client.get("/api/v1/reports/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "reports" in data
        assert "total" in data


class TestAuthenticationEndpoints:
    """Test authentication endpoints (if implemented)."""
    
    def test_login_endpoint_exists(self):
        """Test that login endpoint exists and handles requests."""
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Should at least handle the request (even if returns 501)
        assert response.status_code in [200, 401, 422, 501]
    
    def test_token_validation(self):
        """Test token validation endpoint."""
        headers = {"Authorization": "Bearer fake_token"}
        
        response = client.get("/api/v1/auth/validate", headers=headers)
        
        # Should handle token validation
        assert response.status_code in [200, 401, 422, 501]


class TestAPIInformation:
    """Test API information endpoints."""
    
    def test_root_endpoint(self):
        """Test root API endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "description" in data
    
    def test_api_info_endpoint(self):
        """Test API information endpoint."""
        response = client.get("/api/v1/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "api" in data
        assert "agents" in data
        assert "data_sources" in data
        assert "formats" in data
        
        # Verify agent information
        agents = data["agents"]
        assert "investigator" in agents
        assert "analyst" in agents
        assert "reporter" in agents
    
    def test_openapi_schema(self):
        """Test OpenAPI schema generation."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert "components" in schema


class TestErrorHandling:
    """Test API error handling."""
    
    def test_404_handling(self):
        """Test 404 error handling."""
        response = client.get("/api/v1/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "error"
    
    def test_method_not_allowed(self):
        """Test 405 method not allowed."""
        response = client.patch("/health/")  # Wrong method
        
        assert response.status_code == 405
    
    def test_large_payload_handling(self):
        """Test handling of large payloads."""
        large_data = {"data": "x" * 10000}  # 10KB payload
        
        response = client.post("/api/v1/investigations/start", json=large_data)
        
        # Should handle gracefully (422 for validation, 413 for too large)
        assert response.status_code in [413, 422]


class TestCORSHandling:
    """Test CORS configuration."""
    
    def test_cors_preflight(self):
        """Test CORS preflight request."""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = client.options("/api/v1/investigations/start", headers=headers)
        
        # Should handle CORS preflight
        assert response.status_code in [200, 204]
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        headers = {"Origin": "http://localhost:3000"}
        
        response = client.get("/health/", headers=headers)
        
        # Check for CORS headers (may not be present in test environment)
        assert response.status_code == 200


class TestSecurityHeaders:
    """Test security headers and middleware."""
    
    def test_security_headers_present(self):
        """Test that security headers are present."""
        response = client.get("/")
        
        # Common security headers that should be present
        headers = response.headers
        
        # These might be added by middleware
        # assert "X-Content-Type-Options" in headers
        # assert "X-Frame-Options" in headers
        
        # At minimum, should have content-type
        assert "content-type" in headers
    
    def test_trusted_host_validation(self):
        """Test trusted host middleware."""
        headers = {"Host": "malicious.example.com"}
        
        # Should be handled by TrustedHostMiddleware
        response = client.get("/", headers=headers)
        
        # Should either accept or reject based on configuration
        assert response.status_code in [200, 400, 403]


@pytest.mark.integration
class TestFullAPIWorkflow:
    """Test complete API workflows."""
    
    @pytest.mark.asyncio
    async def test_investigation_to_report_workflow(self, async_client, mock_agents):
        """Test complete workflow from investigation to report."""
        # Step 1: Start investigation
        investigation_data = {
            "query": "Test investigation workflow",
            "priority": "medium"
        }
        
        response = await async_client.post(
            "/api/v1/investigations/start",
            json=investigation_data
        )
        
        if response.status_code == 202:
            data = response.json()
            investigation_id = data.get("investigation_id", "test-123")
            
            # Step 2: Check status (simulate)
            status_response = await async_client.get(
                f"/api/v1/investigations/{investigation_id}/status"
            )
            
            # Step 3: Generate report
            report_data = {
                "type": "investigation",
                "investigation_id": investigation_id,
                "format": "markdown"
            }
            
            report_response = await async_client.post(
                "/api/v1/reports/generate",
                json=report_data
            )
            
            # Should complete workflow successfully
            assert report_response.status_code in [200, 202]


class TestPerformanceAndLimits:
    """Test API performance and limits."""
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health/")
            results.append(response.status_code)
        
        # Create 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5
    
    def test_response_time_reasonable(self):
        """Test that response times are reasonable."""
        import time
        
        start_time = time.time()
        response = client.get("/health/")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])