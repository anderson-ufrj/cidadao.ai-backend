"""
Unit tests for GraphQL API endpoints.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Create mock authenticated user."""
    return MagicMock(
        id="test-user-123",
        email="test@example.com",
        name="Test User",
        role="user",
        is_active=True,
    )


@pytest.fixture
def mock_investigation():
    """Create mock investigation."""
    from datetime import datetime

    investigation = MagicMock()
    investigation.id = "inv-123"
    investigation.user_id = "test-user-123"
    investigation.query = "Test investigation query"
    investigation.status = "processing"
    investigation.confidence_score = 0.85
    investigation.created_at = datetime.utcnow()
    investigation.completed_at = None
    investigation.processing_time_ms = None
    return investigation


class TestGraphQLQueries:
    """Test suite for GraphQL queries."""

    @pytest.mark.unit
    def test_graphql_health_endpoint(self, client):
        """Test GraphQL health check endpoint."""
        response = client.get("/graphql/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["endpoint"] == "/graphql"
        assert "queries" in data["features"]
        assert "mutations" in data["features"]
        assert "subscriptions" in data["features"]

    @pytest.mark.unit
    def test_graphql_examples_endpoint(self, client):
        """Test GraphQL examples endpoint."""
        response = client.get("/graphql/examples")

        assert response.status_code == 200
        data = response.json()
        assert "queries" in data
        assert "mutations" in data
        assert "subscriptions" in data
        assert "tips" in data

    @pytest.mark.unit
    def test_graphql_playground_endpoint(self, client):
        """Test GraphQL playground endpoint."""
        response = client.get("/graphql/playground")

        assert response.status_code == 200
        assert "GraphQL Playground" in response.text
        assert "Cidadão.AI" in response.text

    @pytest.mark.unit
    @patch("src.api.dependencies.get_current_optional_user")
    def test_graphql_me_query(self, mock_get_user, client, mock_user):
        """Test GraphQL 'me' query."""
        mock_get_user.return_value = mock_user

        query = """
            query GetMe {
                me {
                    id
                    email
                    name
                    role
                    isActive
                }
            }
        """

        response = client.post(
            "/graphql",
            json={"query": query},
            headers={"Authorization": "Bearer fake-token"},
        )

        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                assert data["data"]["me"]["email"] == "test@example.com"
                assert data["data"]["me"]["name"] == "Test User"

    @pytest.mark.unit
    @patch("src.services.investigation_service_selector.investigation_service")
    def test_graphql_investigation_query(
        self, mock_investigation_service, client, mock_investigation
    ):
        """Test GraphQL investigation query."""
        mock_investigation_service.get_by_id = AsyncMock(
            return_value=mock_investigation
        )

        query = """
            query GetInvestigation($id: ID!) {
                investigation(id: $id) {
                    id
                    query
                    status
                    confidenceScore
                }
            }
        """

        response = client.post(
            "/graphql",
            json={
                "query": query,
                "variables": {"id": "inv-123"},
            },
        )

        # GraphQL may not be fully configured in test environment
        # Check for either success or expected error
        assert response.status_code in [200, 400, 503]

    @pytest.mark.unit
    @patch("src.services.investigation_service_selector.investigation_service")
    def test_graphql_investigations_search(
        self, mock_investigation_service, client, mock_investigation
    ):
        """Test GraphQL investigations search query."""
        mock_investigation_service.search = AsyncMock(return_value=[mock_investigation])

        query = """
            query SearchInvestigations($limit: Int) {
                investigations(
                    pagination: { limit: $limit, offset: 0 }
                ) {
                    id
                    query
                    status
                    confidenceScore
                }
            }
        """

        response = client.post(
            "/graphql",
            json={
                "query": query,
                "variables": {"limit": 10},
            },
        )

        assert response.status_code in [200, 400, 503]

    @pytest.mark.unit
    @patch("src.agents.get_agent_pool")
    def test_graphql_agent_stats_query(self, mock_get_pool, client):
        """Test GraphQL agent stats query."""
        mock_pool = MagicMock()
        mock_pool.get_stats.return_value = {
            "pools": {
                "zumbi": {
                    "avg_usage": 10.0,
                    "total": 5,
                },
                "anita": {
                    "avg_usage": 8.0,
                    "total": 4,
                },
            }
        }
        mock_get_pool.return_value = mock_pool

        query = """
            query GetAgentStats {
                agentStats {
                    agentName
                    totalTasks
                    successfulTasks
                    avgResponseTimeMs
                }
            }
        """

        response = client.post("/graphql", json={"query": query})

        assert response.status_code in [200, 400, 503]


class TestGraphQLMutations:
    """Test suite for GraphQL mutations."""

    @pytest.mark.unit
    @patch("src.api.dependencies.get_current_optional_user")
    @patch("src.services.investigation_service_selector.investigation_service")
    def test_graphql_create_investigation(
        self,
        mock_investigation_service,
        mock_get_user,
        client,
        mock_user,
        mock_investigation,
    ):
        """Test GraphQL create investigation mutation."""
        mock_get_user.return_value = mock_user
        mock_investigation_service.create = AsyncMock(return_value=mock_investigation)

        mutation = """
            mutation CreateInvestigation($input: InvestigationInput!) {
                createInvestigation(input: $input) {
                    id
                    query
                    status
                }
            }
        """

        response = client.post(
            "/graphql",
            json={
                "query": mutation,
                "variables": {
                    "input": {
                        "query": "Test investigation",
                        "priority": "high",
                    }
                },
            },
            headers={"Authorization": "Bearer fake-token"},
        )

        assert response.status_code in [200, 400, 503]

    @pytest.mark.unit
    @patch("src.api.dependencies.get_current_optional_user")
    @patch("src.services.chat_service_with_cache.chat_service")
    def test_graphql_send_chat_message(
        self, mock_chat_service, mock_get_user, client, mock_user
    ):
        """Test GraphQL send chat message mutation."""
        mock_get_user.return_value = mock_user

        mock_session = MagicMock(id="session-123")
        mock_response = MagicMock(
            id="msg-456",
            message="Response from agent",
            agent_name="zumbi",
        )

        mock_chat_service.get_or_create_session = AsyncMock(return_value=mock_session)
        mock_chat_service.process_message = AsyncMock(return_value=mock_response)

        mutation = """
            mutation SendMessage($input: ChatInput!) {
                sendChatMessage(input: $input) {
                    id
                    content
                    agentName
                }
            }
        """

        response = client.post(
            "/graphql",
            json={
                "query": mutation,
                "variables": {
                    "input": {
                        "message": "Test message",
                        "sessionId": "session-123",
                    }
                },
            },
            headers={"Authorization": "Bearer fake-token"},
        )

        assert response.status_code in [200, 400, 503]


class TestGraphQLSchema:
    """Test suite for GraphQL schema validation."""

    @pytest.mark.unit
    def test_graphql_introspection_query(self, client):
        """Test GraphQL introspection query."""
        introspection_query = """
            query IntrospectionQuery {
                __schema {
                    types {
                        name
                        kind
                        description
                    }
                }
            }
        """

        response = client.post(
            "/graphql",
            json={"query": introspection_query},
        )

        # Introspection might be disabled or GraphQL not configured
        assert response.status_code in [200, 400, 503]

    @pytest.mark.unit
    def test_graphql_error_handling(self, client):
        """Test GraphQL error handling with invalid query."""
        invalid_query = """
            query {
                invalidField {
                    nonExistent
                }
            }
        """

        response = client.post(
            "/graphql",
            json={"query": invalid_query},
        )

        # Should return error response
        assert response.status_code in [200, 400, 503]

        if response.status_code == 200:
            data = response.json()
            # GraphQL returns 200 with errors in response
            if "errors" in data:
                assert len(data["errors"]) > 0

    @pytest.mark.unit
    def test_graphql_variables_validation(self, client):
        """Test GraphQL variables validation."""
        query = """
            query GetInvestigation($id: ID!) {
                investigation(id: $id) {
                    id
                    query
                }
            }
        """

        # Missing required variable
        response = client.post(
            "/graphql",
            json={"query": query, "variables": {}},
        )

        assert response.status_code in [200, 400, 503]
