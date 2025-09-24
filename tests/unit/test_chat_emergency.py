"""Unit tests for emergency chat endpoint"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import Response
import json

from src.api.routes.chat_emergency import (
    router,
    detect_intent,
    try_maritaca,
    ChatRequest,
    ChatResponse
)


class TestDetectIntent:
    """Test intent detection function"""
    
    def test_detect_greeting_intent(self):
        """Test greeting intent detection"""
        greetings = ["olá", "Oi", "bom dia", "Boa tarde", "BOA NOITE", "prazer"]
        for greeting in greetings:
            assert detect_intent(greeting) == "greeting"
            assert detect_intent(f"{greeting}, como vai?") == "greeting"
    
    def test_detect_investigation_intent(self):
        """Test investigation intent detection"""
        investigations = [
            "investigar contratos",
            "verificar gastos",
            "analisar fornecedores",
            "buscar licitações",
            "procurar irregularidades"
        ]
        for text in investigations:
            assert detect_intent(text) == "investigation"
    
    def test_detect_help_intent(self):
        """Test help intent detection"""
        help_texts = [
            "ajuda",
            "pode me ajudar",
            "o que você consegue fazer",
            "como funciona",
            "o que posso perguntar"
        ]
        for text in help_texts:
            assert detect_intent(text) == "help"
    
    def test_detect_default_intent(self):
        """Test default intent for unmatched texts"""
        defaults = [
            "quero saber sobre contratos",
            "mostre gastos de 2024",
            "fornecedor XYZ"
        ]
        for text in defaults:
            assert detect_intent(text) == "default"


class TestTryMaritaca:
    """Test Maritaca AI integration"""
    
    @pytest.mark.asyncio
    async def test_maritaca_without_api_key(self):
        """Test Maritaca returns None without API key"""
        with patch.dict('os.environ', {}, clear=True):
            result = await try_maritaca("test message")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_maritaca_successful_request(self):
        """Test successful Maritaca API call"""
        with patch.dict('os.environ', {'MARITACA_API_KEY': 'test-key'}):
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"answer": "Test response from Maritaca"}
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_instance = mock_client.return_value.__aenter__.return_value
                mock_instance.post.return_value = mock_response
                
                result = await try_maritaca("test message")
                assert result == "Test response from Maritaca"
                
                # Verify API call was made correctly
                mock_instance.post.assert_called_once()
                call_args = mock_instance.post.call_args
                assert call_args[0][0] == "https://chat.maritaca.ai/api/chat/inference"
                assert "authorization" in call_args[1]["headers"]
                assert "Bearer test-key" in call_args[1]["headers"]["authorization"]
    
    @pytest.mark.asyncio
    async def test_maritaca_api_error(self):
        """Test Maritaca API error handling"""
        with patch.dict('os.environ', {'MARITACA_API_KEY': 'test-key'}):
            mock_response = AsyncMock()
            mock_response.status_code = 500
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_instance = mock_client.return_value.__aenter__.return_value
                mock_instance.post.return_value = mock_response
                
                result = await try_maritaca("test message")
                assert result is None
    
    @pytest.mark.asyncio
    async def test_maritaca_network_error(self):
        """Test Maritaca network error handling"""
        with patch.dict('os.environ', {'MARITACA_API_KEY': 'test-key'}):
            with patch('httpx.AsyncClient') as mock_client:
                mock_instance = mock_client.return_value.__aenter__.return_value
                mock_instance.post.side_effect = Exception("Network error")
                
                result = await try_maritaca("test message")
                assert result is None


class TestChatEmergencyEndpoint:
    """Test emergency chat endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_emergency_endpoint_greeting(self, client):
        """Test emergency endpoint with greeting"""
        response = client.post(
            "/api/v1/chat/emergency",
            json={"message": "Olá, bom dia!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert data["agent_id"] == "system"
        assert data["agent_name"] == "Assistente Cidadão.AI"
        assert len(data["message"]) > 0
        assert data["confidence"] == 0.85
        assert len(data["suggested_actions"]) > 0
        assert data["metadata"]["intent"] == "greeting"
        assert data["metadata"]["backend"] == "intelligent_fallback"
    
    def test_emergency_endpoint_investigation(self, client):
        """Test emergency endpoint with investigation request"""
        response = client.post(
            "/api/v1/chat/emergency",
            json={"message": "Quero investigar contratos suspeitos"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["metadata"]["intent"] == "investigation"
        assert "search_contracts" in data["suggested_actions"]
    
    def test_emergency_endpoint_help(self, client):
        """Test emergency endpoint with help request"""
        response = client.post(
            "/api/v1/chat/emergency",
            json={"message": "Como posso usar o sistema?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["metadata"]["intent"] == "help"
        assert any(action in ["help", "examples", "documentation"] for action in data["suggested_actions"])
    
    def test_emergency_endpoint_with_session_id(self, client):
        """Test emergency endpoint preserves session_id"""
        session_id = "test-session-123"
        response = client.post(
            "/api/v1/chat/emergency",
            json={"message": "teste", "session_id": session_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
    
    def test_emergency_endpoint_without_session_id(self, client):
        """Test emergency endpoint generates session_id"""
        response = client.post(
            "/api/v1/chat/emergency",
            json={"message": "teste"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"].startswith("emergency_")
    
    @pytest.mark.asyncio
    async def test_emergency_endpoint_with_maritaca(self, client):
        """Test emergency endpoint using Maritaca"""
        with patch.dict('os.environ', {'MARITACA_API_KEY': 'test-key'}):
            with patch('src.api.routes.chat_emergency.try_maritaca') as mock_maritaca:
                mock_maritaca.return_value = "Response from Maritaca AI"
                
                response = client.post(
                    "/api/v1/chat/emergency",
                    json={"message": "teste com maritaca"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["agent_id"] == "maritaca"
                assert data["agent_name"] == "Assistente Cidadão.AI (Maritaca)"
                assert data["message"] == "Response from Maritaca AI"
                assert data["confidence"] == 0.95
                assert data["metadata"]["backend"] == "maritaca_ai"
                assert data["metadata"]["model"] == "sabia-3"
    
    def test_emergency_endpoint_validation_error(self, client):
        """Test emergency endpoint with invalid input"""
        # Empty message
        response = client.post(
            "/api/v1/chat/emergency",
            json={"message": ""}
        )
        assert response.status_code == 422
        
        # Message too long
        response = client.post(
            "/api/v1/chat/emergency",
            json={"message": "a" * 1001}
        )
        assert response.status_code == 422
        
        # Missing message
        response = client.post(
            "/api/v1/chat/emergency",
            json={}
        )
        assert response.status_code == 422


class TestEmergencyHealthEndpoint:
    """Test emergency health check endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_health_endpoint_without_maritaca(self, client):
        """Test health endpoint without Maritaca API key"""
        with patch.dict('os.environ', {}, clear=True):
            response = client.get("/api/v1/chat/emergency/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "operational"
            assert data["endpoint"] == "/api/v1/chat/emergency"
            assert data["maritaca_configured"] is False
            assert data["fallback_ready"] is True
            assert "timestamp" in data
    
    def test_health_endpoint_with_maritaca(self, client):
        """Test health endpoint with Maritaca API key"""
        with patch.dict('os.environ', {'MARITACA_API_KEY': 'test-key'}):
            response = client.get("/api/v1/chat/emergency/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["maritaca_configured"] is True