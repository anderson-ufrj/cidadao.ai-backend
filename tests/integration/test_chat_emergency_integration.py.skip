"""Integration tests for emergency chat endpoint"""

import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.routes.chat_emergency import router


class TestEmergencyEndpointIntegration:
    """Integration tests for emergency chat endpoint"""

    @pytest.fixture
    def app(self):
        """Create FastAPI app with emergency router"""
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    def test_emergency_endpoint_performance(self, client):
        """Test emergency endpoint response time"""
        messages = [
            "Olá!",
            "Quero investigar contratos",
            "Como funciona o sistema?",
            "Mostre gastos de 2024",
            "Analise fornecedor XYZ",
        ]

        response_times = []

        for message in messages:
            start_time = time.time()
            response = client.post("/api/v1/chat/emergency", json={"message": message})
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        # Verify all responses are fast (under 100ms for fallback)
        assert all(t < 0.1 for t in response_times), f"Response times: {response_times}"

        # Average should be very fast
        avg_time = sum(response_times) / len(response_times)
        assert avg_time < 0.05, f"Average response time: {avg_time}"

    def test_emergency_endpoint_concurrent_requests(self, client):
        """Test emergency endpoint under concurrent load"""
        import concurrent.futures

        def make_request(message):
            response = client.post("/api/v1/chat/emergency", json={"message": message})
            return response.status_code, response.json()

        messages = [f"Teste concorrente {i}" for i in range(20)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, msg) for msg in messages]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        assert all(status == 200 for status, _ in results)

        # All should have valid responses
        for _, data in results:
            assert "session_id" in data
            assert "message" in data
            assert len(data["message"]) > 0

    def test_emergency_endpoint_session_continuity(self, client):
        """Test session continuity across multiple messages"""
        session_id = "test-session-continuity"

        messages = ["Olá!", "Quero investigar contratos", "Mostre os mais recentes"]

        for i, message in enumerate(messages):
            response = client.post(
                "/api/v1/chat/emergency",
                json={"message": message, "session_id": session_id},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == session_id

            # Verify response makes sense for the intent
            if i == 0:  # Greeting
                assert data["metadata"]["intent"] == "greeting"
            elif i == 1:  # Investigation
                assert data["metadata"]["intent"] == "investigation"

    def test_emergency_endpoint_error_recovery(self, client):
        """Test emergency endpoint handles errors gracefully"""
        # Test with various edge cases
        edge_cases = [
            {"message": "a"},  # Very short
            {"message": "?" * 100},  # Special characters
            {"message": "SELECT * FROM users"},  # SQL-like
            {"message": "<script>alert('test')</script>"},  # XSS attempt
            {"message": "😀" * 50},  # Emojis
        ]

        for payload in edge_cases:
            response = client.post("/api/v1/chat/emergency", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert len(data["message"]) > 0
            assert "error" not in data

    @pytest.mark.asyncio
    async def test_emergency_endpoint_maritaca_fallback(self, client):
        """Test fallback when Maritaca fails"""
        with patch.dict("os.environ", {"MARITACA_API_KEY": "test-key"}):
            # Mock Maritaca to fail
            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = mock_client.return_value.__aenter__.return_value
                mock_instance.post.side_effect = Exception("API Error")

                response = client.post(
                    "/api/v1/chat/emergency",
                    json={"message": "Test with failed Maritaca"},
                )

                assert response.status_code == 200
                data = response.json()

                # Should fallback to intelligent responses
                assert data["agent_id"] == "system"
                assert data["metadata"]["backend"] == "intelligent_fallback"
                assert len(data["message"]) > 0

    def test_emergency_endpoint_response_variety(self, client):
        """Test that responses vary for same intent"""
        responses = []

        # Send same greeting multiple times
        for _ in range(5):
            response = client.post("/api/v1/chat/emergency", json={"message": "Olá!"})

            assert response.status_code == 200
            data = response.json()
            responses.append(data["message"])

        # Should have some variety in responses
        unique_responses = set(responses)
        assert len(unique_responses) >= 2, "Responses should vary"

    def test_emergency_health_monitoring(self, client):
        """Test health endpoint provides accurate status"""
        # Test without Maritaca
        with patch.dict("os.environ", {}, clear=True):
            response = client.get("/api/v1/chat/emergency/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "operational"
            assert data["maritaca_configured"] is False

        # Test with Maritaca
        with patch.dict("os.environ", {"MARITACA_API_KEY": "test-key"}):
            response = client.get("/api/v1/chat/emergency/health")
            assert response.status_code == 200
            data = response.json()
            assert data["maritaca_configured"] is True

    def test_emergency_endpoint_metadata_consistency(self, client):
        """Test metadata is consistent and complete"""
        response = client.post(
            "/api/v1/chat/emergency", json={"message": "Test metadata"}
        )

        assert response.status_code == 200
        data = response.json()

        # Check required metadata fields
        assert "backend" in data["metadata"]
        assert "timestamp" in data["metadata"]
        assert "intent" in data["metadata"]

        # Timestamp should be valid ISO format
        from datetime import datetime

        timestamp = datetime.fromisoformat(data["metadata"]["timestamp"])
        assert timestamp.year >= 2024
