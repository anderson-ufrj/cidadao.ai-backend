"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import json
from datetime import datetime

from src.api.app import create_app
from src.models.user import User
from src.models.investigation import Investigation, InvestigationStatus
from src.core.config import get_settings


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            id="test-user-id",
            email="test@example.com",
            hashed_password="$2b$12$hashed_password_here",
            is_active=True,
            role="user"
        )
    
    def test_register_success(self, client, mock_db):
        """Test successful user registration."""
        with patch("src.api.routes.auth.get_db", return_value=mock_db):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "SecurePassword123!",
                    "full_name": "New User"
                }
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data
    
    def test_register_duplicate_email(self, client, mock_db):
        """Test registration with duplicate email."""
        # Mock existing user
        mock_db.execute.return_value.scalar_one_or_none.return_value = MagicMock()
        
        with patch("src.api.routes.auth.get_db", return_value=mock_db):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "Password123!"
                }
            )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, client, mock_db, mock_user):
        """Test successful login."""
        # Mock authentication
        with patch("src.api.auth.authenticate_user", return_value=mock_user):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "test@example.com",
                    "password": "correctpassword"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, mock_db):
        """Test login with invalid credentials."""
        with patch("src.api.auth.authenticate_user", return_value=None):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "test@example.com",
                    "password": "wrongpassword"
                }
            )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_refresh_token_success(self, client, mock_db, mock_user):
        """Test token refresh."""
        # Create valid refresh token
        with patch("src.api.auth.create_refresh_token") as mock_create_refresh:
            mock_create_refresh.return_value = "valid_refresh_token"
            
            with patch("src.api.auth.verify_token") as mock_verify:
                mock_verify.return_value = {"sub": mock_user.id, "type": "refresh"}
                
                with patch("src.api.routes.auth.get_db", return_value=mock_db):
                    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
                    
                    response = client.post(
                        "/api/v1/auth/refresh",
                        json={"refresh_token": "valid_refresh_token"}
                    )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_logout_success(self, client, authenticated_headers):
        """Test logout."""
        response = client.post(
            "/api/v1/auth/logout",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
    
    def test_change_password(self, client, authenticated_headers, mock_db, mock_user):
        """Test password change."""
        with patch("src.api.auth.verify_password", return_value=True):
            with patch("src.api.routes.auth.get_current_user", return_value=mock_user):
                response = client.post(
                    "/api/v1/auth/change-password",
                    headers=authenticated_headers,
                    json={
                        "old_password": "oldpassword",
                        "new_password": "NewSecurePassword123!"
                    }
                )
        
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]


class TestInvestigationEndpoints:
    """Test investigation endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    @pytest.fixture
    def mock_investigation(self):
        """Create mock investigation."""
        return Investigation(
            id="inv-123",
            user_id="user-123",
            title="Test Investigation",
            description="Testing anomaly detection",
            target_entity="Ministry of Health",
            status=InvestigationStatus.PENDING,
            created_at=datetime.utcnow()
        )
    
    def test_create_investigation(self, client, authenticated_headers, mock_db):
        """Test creating new investigation."""
        with patch("src.api.routes.investigations.get_db", return_value=mock_db):
            # Mock the agent execution
            with patch("src.agents.abaporu.MasterAgent.execute") as mock_execute:
                mock_execute.return_value = AsyncMock(
                    status="completed",
                    results={"anomalies": [], "summary": "No anomalies found"}
                )
                
                response = client.post(
                    "/api/v1/investigations",
                    headers=authenticated_headers,
                    json={
                        "title": "Contract Analysis",
                        "description": "Analyze contracts for Ministry of Health",
                        "target_entity": "Ministry of Health",
                        "parameters": {
                            "year": 2024,
                            "min_value": 100000
                        }
                    }
                )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Contract Analysis"
        assert "id" in data
        assert data["status"] == "pending"
    
    def test_list_investigations(self, client, authenticated_headers, mock_db):
        """Test listing investigations."""
        # Mock investigations
        mock_investigations = [
            MagicMock(id="inv-1", title="Investigation 1"),
            MagicMock(id="inv-2", title="Investigation 2")
        ]
        
        mock_db.execute.return_value.scalars.return_value.all.return_value = mock_investigations
        
        with patch("src.api.routes.investigations.get_db", return_value=mock_db):
            response = client.get(
                "/api/v1/investigations",
                headers=authenticated_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Investigation 1"
    
    def test_get_investigation_by_id(self, client, authenticated_headers, mock_db, mock_investigation):
        """Test getting specific investigation."""
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_investigation
        
        with patch("src.api.routes.investigations.get_db", return_value=mock_db):
            response = client.get(
                f"/api/v1/investigations/{mock_investigation.id}",
                headers=authenticated_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == mock_investigation.id
        assert data["title"] == mock_investigation.title
    
    def test_get_investigation_not_found(self, client, authenticated_headers, mock_db):
        """Test getting non-existent investigation."""
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        with patch("src.api.routes.investigations.get_db", return_value=mock_db):
            response = client.get(
                "/api/v1/investigations/non-existent-id",
                headers=authenticated_headers
            )
        
        assert response.status_code == 404
        assert "Investigation not found" in response.json()["detail"]
    
    def test_investigation_websocket(self, client, authenticated_headers):
        """Test investigation real-time updates via WebSocket."""
        with client.websocket_connect(
            "/api/v1/investigations/ws/inv-123",
            headers=authenticated_headers
        ) as websocket:
            # Send initial message
            websocket.send_json({"type": "subscribe"})
            
            # Receive acknowledgment
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["investigation_id"] == "inv-123"


class TestAnalysisEndpoints:
    """Test analysis endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_analyze_contracts(self, client, authenticated_headers):
        """Test contract analysis endpoint."""
        with patch("src.services.analysis_service.AnalysisService.analyze_contracts") as mock_analyze:
            mock_analyze.return_value = {
                "total_contracts": 100,
                "anomalies_detected": 5,
                "total_value": 10000000,
                "risk_score": 0.7
            }
            
            response = client.post(
                "/api/v1/analysis/contracts",
                headers=authenticated_headers,
                json={
                    "entity_code": "26000",
                    "year": 2024,
                    "min_value": 100000
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_contracts"] == 100
        assert data["anomalies_detected"] == 5
    
    def test_analyze_spending_patterns(self, client, authenticated_headers):
        """Test spending pattern analysis."""
        with patch("src.services.analysis_service.AnalysisService.analyze_spending") as mock_analyze:
            mock_analyze.return_value = {
                "patterns": [
                    {
                        "type": "seasonal",
                        "description": "High spending in Q4",
                        "confidence": 0.85
                    }
                ],
                "anomalies": []
            }
            
            response = client.post(
                "/api/v1/analysis/spending-patterns",
                headers=authenticated_headers,
                json={
                    "entity_code": "26000",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["patterns"]) == 1
        assert data["patterns"][0]["type"] == "seasonal"
    
    def test_vendor_concentration_analysis(self, client, authenticated_headers):
        """Test vendor concentration analysis."""
        response = client.post(
            "/api/v1/analysis/vendor-concentration",
            headers=authenticated_headers,
            json={
                "entity_code": "26000",
                "year": 2024,
                "concentration_threshold": 0.7
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "concentration_index" in data
        assert "top_vendors" in data


class TestHealthEndpoints:
    """Test health and monitoring endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_detailed_health_check(self, client):
        """Test detailed health check."""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "redis" in data
        assert "agents" in data
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/health/metrics")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
        assert "cidadao_ai_requests_total" in response.text
    
    def test_metrics_json_endpoint(self, client):
        """Test JSON metrics endpoint."""
        response = client.get("/health/metrics/json")
        
        assert response.status_code == 200
        data = response.json()
        assert "requests" in data
        assert "agents" in data
        assert "anomalies" in data


class TestReportEndpoints:
    """Test report generation endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_generate_investigation_report(self, client, authenticated_headers):
        """Test report generation for investigation."""
        with patch("src.agents.tiradentes.ReporterAgent.generate_report") as mock_generate:
            mock_generate.return_value = {
                "title": "Investigation Report",
                "summary": "5 anomalies detected",
                "sections": [
                    {
                        "title": "Price Anomalies",
                        "content": "Found 3 contracts with unusual pricing"
                    }
                ],
                "recommendations": ["Review contract approval process"]
            }
            
            response = client.post(
                "/api/v1/reports/investigation/inv-123",
                headers=authenticated_headers,
                json={
                    "format": "markdown",
                    "include_evidence": True
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Investigation Report"
        assert len(data["sections"]) == 1
    
    def test_export_report_pdf(self, client, authenticated_headers):
        """Test PDF report export."""
        with patch("src.services.report_service.ReportService.export_pdf") as mock_export:
            mock_export.return_value = b"PDF content here"
            
            response = client.get(
                "/api/v1/reports/investigation/inv-123/export?format=pdf",
                headers=authenticated_headers
            )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == 'attachment; filename="investigation_inv-123.pdf"'


class TestAuditEndpoints:
    """Test audit trail endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_get_audit_logs(self, client, admin_headers):
        """Test retrieving audit logs (admin only)."""
        response = client.get(
            "/api/v1/audit/logs?limit=50",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 50
    
    def test_get_audit_logs_unauthorized(self, client, authenticated_headers):
        """Test audit logs require admin role."""
        response = client.get(
            "/api/v1/audit/logs",
            headers=authenticated_headers
        )
        
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_export_audit_logs(self, client, admin_headers):
        """Test exporting audit logs."""
        response = client.get(
            "/api/v1/audit/export?format=csv&start_date=2024-01-01",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        assert "attachment" in response.headers["content-disposition"]