"""
Module: tests.unit.api.routes.test_agents
Description: Unit tests for agent routes
Author: Anderson H. Silva
Date: 2025-09-25
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from src.api.routes.agents import router, AgentRequest, AgentResponse


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    user = MagicMock()
    user.id = "test_user_123"
    user.username = "testuser"
    return user


@pytest.fixture
def mock_agents():
    """Mock agent instances."""
    with patch("src.api.routes.agents.ZumbiAgent") as mock_zumbi, \
         patch("src.api.routes.agents.AnitaAgent") as mock_anita, \
         patch("src.api.routes.agents.TiradentesAgent") as mock_tiradentes, \
         patch("src.api.routes.agents.BonifacioAgent") as mock_bonifacio:
        
        # Configure mock responses
        mock_result = MagicMock()
        mock_result.data = {"analysis": "test analysis"}
        mock_result.metadata = {
            "processing_time": 0.5,
            "anomalies_detected": 2,
            "patterns_found": 3,
            "compliance_issues": 1,
            "legal_risks": ["risk1"]
        }
        
        # All agents return the same mock result for simplicity
        for mock_agent_class in [mock_zumbi, mock_anita, mock_tiradentes, mock_bonifacio]:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value=mock_result)
            mock_agent_class.return_value = mock_instance
        
        yield {
            "zumbi": mock_zumbi,
            "anita": mock_anita,
            "tiradentes": mock_tiradentes,
            "bonifacio": mock_bonifacio
        }


class TestAgentRoutes:
    """Test agent route endpoints."""
    
    @pytest.mark.asyncio
    async def test_zumbi_agent_endpoint(self, mock_user, mock_agents):
        """Test Zumbi agent endpoint."""
        with patch("src.api.routes.agents.get_current_user", return_value=mock_user), \
             patch("src.api.routes.agents.get_rate_limit_tier", return_value=MagicMock(value="standard")):
            
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            request_data = {
                "query": "Analyze contract anomalies",
                "context": {"session_id": "test_session"},
                "options": {"threshold": 0.8}
            }
            
            response = client.post("/zumbi", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["agent"] == "zumbi_dos_palmares"
            assert data["success"] is True
            assert "result" in data
            assert data["message"] == "Anomaly detection completed successfully"
    
    @pytest.mark.asyncio
    async def test_anita_agent_endpoint(self, mock_user, mock_agents):
        """Test Anita agent endpoint."""
        with patch("src.api.routes.agents.get_current_user", return_value=mock_user), \
             patch("src.api.routes.agents.get_rate_limit_tier", return_value=MagicMock(value="standard")):
            
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            request_data = {
                "query": "Analyze spending patterns",
                "context": {"session_id": "test_session"},
                "options": {}
            }
            
            response = client.post("/anita", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["agent"] == "anita_garibaldi"
            assert data["success"] is True
            assert "result" in data
            assert data["message"] == "Pattern analysis completed successfully"
    
    @pytest.mark.asyncio
    async def test_tiradentes_agent_endpoint(self, mock_user, mock_agents):
        """Test Tiradentes agent endpoint."""
        with patch("src.api.routes.agents.get_current_user", return_value=mock_user), \
             patch("src.api.routes.agents.get_rate_limit_tier", return_value=MagicMock(value="standard")):
            
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            request_data = {
                "query": "Generate investigation report",
                "context": {"session_id": "test_session"},
                "options": {"format": "markdown"}
            }
            
            response = client.post("/tiradentes", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["agent"] == "tiradentes"
            assert data["success"] is True
            assert "result" in data
            assert data["message"] == "Report generation completed successfully"
    
    @pytest.mark.asyncio
    async def test_bonifacio_agent_endpoint(self, mock_user, mock_agents):
        """Test Bonifacio agent endpoint."""
        with patch("src.api.routes.agents.get_current_user", return_value=mock_user), \
             patch("src.api.routes.agents.get_rate_limit_tier", return_value=MagicMock(value="standard")):
            
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            request_data = {
                "query": "Check legal compliance",
                "context": {"session_id": "test_session"},
                "options": {"include_jurisprudence": True}
            }
            
            response = client.post("/bonifacio", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["agent"] == "jose_bonifacio"
            assert data["success"] is True
            assert "result" in data
            assert data["message"] == "Legal and compliance analysis completed successfully"
            assert "metadata" in data
            assert "compliance_issues" in data["metadata"]
            assert "legal_risks" in data["metadata"]
    
    def test_agents_status_endpoint(self, mock_user):
        """Test agents status endpoint."""
        with patch("src.api.routes.agents.get_current_user", return_value=mock_user):
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            response = client.get("/status")
            
            assert response.status_code == 200
            data = response.json()
            assert "agents" in data
            assert "total_active" in data
            assert data["total_active"] == 4
            
            # Check all agents are present
            agent_names = list(data["agents"].keys())
            assert "zumbi_dos_palmares" in agent_names
            assert "anita_garibaldi" in agent_names
            assert "tiradentes" in agent_names
            assert "jose_bonifacio" in agent_names
            
            # Check Bonifacio agent details
            bonifacio = data["agents"]["jose_bonifacio"]
            assert bonifacio["name"] == "José Bonifácio"
            assert bonifacio["role"] == "Legal & Compliance Specialist"
            assert bonifacio["status"] == "active"
            assert len(bonifacio["capabilities"]) == 5
    
    def test_list_agents_endpoint(self):
        """Test list agents endpoint."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Cidadão.AI Agent System"
        assert data["version"] == "2.0.0"
        assert len(data["agents"]) == 4
        
        # Check Bonifacio is in the list
        agent_names = [agent["name"] for agent in data["agents"]]
        assert "José Bonifácio" in agent_names
        
        # Find and check Bonifacio details
        bonifacio = next(a for a in data["agents"] if a["name"] == "José Bonifácio")
        assert bonifacio["endpoint"] == "/api/v1/agents/bonifacio"
        assert "legal and compliance" in bonifacio["description"].lower()
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, mock_user):
        """Test agent error handling."""
        with patch("src.api.routes.agents.get_current_user", return_value=mock_user), \
             patch("src.api.routes.agents.get_rate_limit_tier", return_value=MagicMock(value="standard")), \
             patch("src.api.routes.agents.BonifacioAgent") as mock_bonifacio:
            
            # Make the agent raise an exception
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(side_effect=Exception("Agent processing failed"))
            mock_bonifacio.return_value = mock_instance
            
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            request_data = {
                "query": "Test error",
                "context": {},
                "options": {}
            }
            
            response = client.post("/bonifacio", json=request_data)
            
            assert response.status_code == 500
            assert "Bonifacio agent processing failed" in response.json()["detail"]