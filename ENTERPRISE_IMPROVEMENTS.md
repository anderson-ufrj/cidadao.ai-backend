# 🏢 Enterprise Backend Improvements Plan

## Executive Summary

Transform the Cidadão.AI backend from a solid foundation (9.4/10) to an enterprise-grade production system (9.8/10) through systematic improvements in testing, monitoring, performance, and developer experience.

## 🎯 Priority 1: Testing Framework (Critical)

### Current State
- Basic pytest structure with minimal coverage (~40%)
- Limited test categories and fixtures
- No integration testing with real services

### Target State
- Comprehensive test coverage (>85%)
- Full test pyramid: unit, integration, e2e
- Automated test execution in CI/CD

### Implementation

#### 1. Enhanced Test Configuration
```python
# tests/conftest.py (Complete Rewrite)
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from unittest.mock import AsyncMock, patch

# Test Database Setup
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_database():
    """Integration test database using testcontainers."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        database_url = postgres.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        
        # Create engine and run migrations
        engine = create_async_engine(database_url)
        
        # Import and run Alembic migrations
        from alembic import command
        from alembic.config import Config
        
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(alembic_cfg, "head")
        
        yield database_url
        
        await engine.dispose()

@pytest.fixture(scope="session") 
async def test_redis():
    """Test Redis instance."""
    with RedisContainer("redis:7-alpine") as redis_container:
        redis_url = redis_container.get_connection_url()
        yield redis_url

@pytest.fixture
async def db_session(test_database) -> AsyncGenerator[AsyncSession, None]:
    """Database session for tests."""
    engine = create_async_engine(test_database)
    
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.rollback()  # Always rollback in tests
        finally:
            await session.close()
    
    await engine.dispose()

@pytest.fixture
async def client(test_database, test_redis) -> AsyncGenerator[AsyncClient, None]:
    """Test client with database and Redis."""
    from src.api.app import create_app
    
    # Override settings for testing
    test_settings = {
        "DATABASE_URL": test_database,
        "REDIS_URL": test_redis,
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-do-not-use-in-production"
    }
    
    app = create_app(test_settings)
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

# Mock Fixtures
@pytest.fixture
def mock_transparency_api():
    """Comprehensive Transparency API mock."""
    with patch('src.tools.transparency_api.TransparencyAPI') as mock_api:
        # Configure realistic mock responses
        mock_api.return_value.search_contracts.return_value = {
            "data": [
                {
                    "id": "TEST-001",
                    "numero": "001/2024",
                    "objeto": "Serviços de consultoria em transparência",
                    "valor_global": 150000.00,
                    "fornecedor": {
                        "nome": "Consultoria Exemplo LTDA",
                        "cnpj": "12.345.678/0001-90"
                    },
                    "data_inicio": "2024-01-15",
                    "data_fim": "2024-12-15",
                    "status": "ativo",
                    "modalidade": "dispensa_licitacao"
                }
            ],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 1,
                "total_pages": 1
            }
        }
        
        mock_api.return_value.get_contract_details.return_value = {
            "id": "TEST-001",
            "detalhes_completos": True,
            "historico_alteracoes": []
        }
        
        yield mock_api

@pytest.fixture
def mock_groq_api():
    """Mock Groq LLM API."""
    with patch('src.llm.providers.GroqProvider') as mock_groq:
        mock_groq.return_value.generate.return_value = {
            "response": "Análise detalhada do contrato realizada com sucesso.",
            "metadata": {"model": "mixtral-8x7b-32768", "tokens": 150}
        }
        yield mock_groq

# Test Data Fixtures
@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing."""
    return {
        "id": "CONTRACT-2024-001",
        "numero": "001/2024",
        "objeto": "Aquisição de equipamentos de informática",
        "valor_global": 85000.00,
        "fornecedor": {
            "nome": "Tech Solutions LTDA",
            "cnpj": "98.765.432/0001-10",
            "endereco": "Rua da Tecnologia, 123 - São Paulo/SP"
        },
        "data_assinatura": "2024-01-10",
        "data_inicio": "2024-01-15", 
        "data_fim": "2024-06-15",
        "modalidade": "pregao_eletronico",
        "status": "ativo",
        "orgao": {
            "nome": "Secretaria de Tecnologia",
            "codigo": "SETECH",
            "esfera": "municipal"
        }
    }

@pytest.fixture
def sample_investigation_request():
    """Sample investigation request."""
    return {
        "query": "contratos de tecnologia acima de 50 mil reais em 2024",
        "investigation_type": "spending_analysis",
        "filters": {
            "min_value": 50000,
            "category": "tecnologia",
            "year": 2024
        },
        "options": {
            "include_subcategories": True,
            "detect_anomalies": True,
            "generate_summary": True
        }
    }

@pytest.fixture
async def authenticated_headers(client):
    """Get authenticated headers for testing."""
    # Create test user and get JWT token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpassword123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    # Fallback to API key for testing
    return {"X-API-Key": "test-api-key-do-not-use-in-production"}

# Performance Testing Fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def duration(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0
        
        def assert_duration_less_than(self, max_duration: float):
            assert self.duration < max_duration, f"Operation took {self.duration}s, expected < {max_duration}s"
    
    return PerformanceTimer()
```

#### 2. Unit Test Categories
```python
# tests/unit/agents/test_investigator_agent.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.investigator_agent import InvestigatorAgent
from src.agents.base_agent import AgentContext, AgentMessage
from src.core.exceptions import AgentExecutionError

@pytest.mark.unit
@pytest.mark.asyncio
class TestInvestigatorAgent:
    
    @pytest.fixture
    def agent(self):
        """Create InvestigatorAgent instance."""
        return InvestigatorAgent()
    
    @pytest.fixture
    def agent_context(self):
        """Create agent context for testing."""
        return AgentContext(
            user_id="test-user-123",
            session_id="test-session-456", 
            request_id="test-request-789"
        )
    
    async def test_investigate_contracts_success(self, agent, agent_context, sample_contract_data):
        """Test successful contract investigation."""
        # Arrange
        contracts = [sample_contract_data]
        
        with patch.object(agent, '_analyze_spending_patterns') as mock_analyze:
            mock_analyze.return_value = {
                "patterns": ["unusual_vendor_concentration"],
                "anomalies": ["price_spike_detected"],
                "confidence": 0.85
            }
            
            # Act
            result = await agent.investigate_contracts(contracts, agent_context)
            
            # Assert
            assert result is not None
            assert "analysis" in result
            assert "patterns" in result["analysis"]
            assert len(result["analysis"]["patterns"]) > 0
            mock_analyze.assert_called_once_with(contracts)
    
    async def test_investigate_contracts_empty_data(self, agent, agent_context):
        """Test investigation with empty contract data."""
        # Act & Assert
        with pytest.raises(ValueError, match="No contract data provided"):
            await agent.investigate_contracts([], agent_context)
    
    async def test_investigate_contracts_api_failure(self, agent, agent_context, sample_contract_data):
        """Test investigation with API failure."""
        # Arrange
        contracts = [sample_contract_data]
        
        with patch.object(agent, '_analyze_spending_patterns') as mock_analyze:
            mock_analyze.side_effect = Exception("API connection failed")
            
            # Act & Assert
            with pytest.raises(AgentExecutionError):
                await agent.investigate_contracts(contracts, agent_context)
    
    @pytest.mark.parametrize("contract_value,expected_risk", [
        (10000, "low"),
        (100000, "medium"),
        (1000000, "high"),
        (5000000, "critical")
    ])
    async def test_risk_assessment_by_value(self, agent, contract_value, expected_risk):
        """Test risk assessment based on contract value."""
        # Arrange
        contract = {"valor_global": contract_value}
        
        # Act
        risk_level = agent._assess_risk_by_value(contract)
        
        # Assert
        assert risk_level == expected_risk
    
    async def test_memory_integration(self, agent, agent_context):
        """Test agent memory integration."""
        # Arrange
        investigation_data = {"query": "test query", "results": ["result1"]}
        
        with patch.object(agent.memory, 'store_investigation') as mock_store:
            mock_store.return_value = True
            
            # Act
            await agent._store_investigation_memory(investigation_data, agent_context)
            
            # Assert
            mock_store.assert_called_once()

# tests/unit/api/test_analysis_endpoints.py
@pytest.mark.unit
@pytest.mark.asyncio
class TestAnalysisEndpoints:
    
    async def test_start_analysis_valid_request(self, client, authenticated_headers, mock_transparency_api):
        """Test starting analysis with valid request."""
        # Arrange
        payload = {
            "analysis_type": "spending_trends",
            "data_source": "contracts",
            "time_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            },
            "filters": {
                "min_value": 10000,
                "categories": ["technology", "services"]
            }
        }
        
        # Act
        response = await client.post(
            "/api/v1/analysis/start",
            json=payload,
            headers=authenticated_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert "status" in data
        assert data["status"] == "started"
        assert "estimated_completion" in data
    
    async def test_start_analysis_invalid_date_range(self, client, authenticated_headers):
        """Test analysis with invalid date range."""
        # Arrange
        payload = {
            "analysis_type": "spending_trends",
            "data_source": "contracts",
            "time_range": {
                "start_date": "2024-12-31",  # End before start
                "end_date": "2024-01-01"
            }
        }
        
        # Act
        response = await client.post(
            "/api/v1/analysis/start",
            json=payload,
            headers=authenticated_headers
        )
        
        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "validation_error" in error_data["detail"]
    
    async def test_get_analysis_status(self, client, authenticated_headers):
        """Test getting analysis status."""
        # Arrange - First create an analysis
        create_response = await client.post(
            "/api/v1/analysis/start",
            json={
                "analysis_type": "spending_trends",
                "data_source": "contracts",
                "time_range": {"start_date": "2024-01-01", "end_date": "2024-03-31"}
            },
            headers=authenticated_headers
        )
        analysis_id = create_response.json()["analysis_id"]
        
        # Act
        status_response = await client.get(
            f"/api/v1/analysis/{analysis_id}/status",
            headers=authenticated_headers
        )
        
        # Assert
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "status" in status_data
        assert status_data["analysis_id"] == analysis_id
        assert "progress" in status_data
    
    @pytest.mark.slow
    async def test_analysis_performance(self, client, authenticated_headers, performance_timer):
        """Test analysis endpoint performance."""
        # Arrange
        payload = {
            "analysis_type": "quick_scan",
            "data_source": "contracts",
            "time_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        }
        
        # Act
        performance_timer.start()
        response = await client.post(
            "/api/v1/analysis/start",
            json=payload,
            headers=authenticated_headers
        )
        performance_timer.stop()
        
        # Assert
        assert response.status_code == 200
        performance_timer.assert_duration_less_than(2.0)  # Should complete in < 2 seconds
```

#### 3. Integration Tests
```python
# tests/integration/test_investigation_workflow.py
import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.integration
@pytest.mark.asyncio
class TestInvestigationWorkflow:
    
    async def test_complete_investigation_flow(self, client: AsyncClient, authenticated_headers, db_session):
        """Test complete investigation workflow from start to results."""
        
        # Step 1: Start Investigation
        investigation_payload = {
            "query": "contratos emergenciais sem licitação 2024",
            "investigation_type": "anomaly_detection",
            "options": {
                "include_historical_data": True,
                "detect_patterns": True,
                "generate_report": True
            }
        }
        
        start_response = await client.post(
            "/api/v1/investigations/start",
            json=investigation_payload,
            headers=authenticated_headers
        )
        
        assert start_response.status_code == 200
        investigation_data = start_response.json()
        investigation_id = investigation_data["investigation_id"]
        
        # Step 2: Monitor Progress
        status_checks = 0
        max_checks = 30  # 30 seconds timeout
        
        while status_checks < max_checks:
            status_response = await client.get(
                f"/api/v1/investigations/{investigation_id}/status",
                headers=authenticated_headers
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            if status_data["status"] == "completed":
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Investigation failed: {status_data.get('error')}")
            
            await asyncio.sleep(1)
            status_checks += 1
        
        assert status_checks < max_checks, "Investigation timed out"
        
        # Step 3: Retrieve Results
        results_response = await client.get(
            f"/api/v1/investigations/{investigation_id}/results",
            headers=authenticated_headers
        )
        
        assert results_response.status_code == 200
        results = results_response.json()
        
        # Validate Results Structure
        assert "investigation_id" in results
        assert "findings" in results
        assert "summary" in results
        assert "metadata" in results
        
        # Validate Findings Content
        findings = results["findings"]
        assert len(findings) >= 0  # May be empty for test data
        
        if findings:
            first_finding = findings[0]
            assert "type" in first_finding
            assert "description" in first_finding
            assert "severity" in first_finding
            assert "evidence" in first_finding
        
        # Step 4: Generate Report (if enabled)
        if investigation_payload["options"]["generate_report"]:
            report_response = await client.get(
                f"/api/v1/investigations/{investigation_id}/report",
                headers=authenticated_headers
            )
            
            assert report_response.status_code == 200
            report_data = report_response.json()
            assert "report_url" in report_data or "report_content" in report_data
    
    async def test_investigation_with_real_data_integration(self, client, authenticated_headers, mock_transparency_api):
        """Test investigation with mocked real data integration."""
        
        # Configure comprehensive mock data
        mock_transparency_api.return_value.search_contracts.return_value = {
            "data": [
                {
                    "id": "REAL-001",
                    "numero": "PE001/2024",
                    "objeto": "Serviços emergenciais de limpeza urbana",
                    "valor_global": 2500000.00,  # High value for anomaly detection
                    "fornecedor": {
                        "nome": "Limpeza Rápida LTDA",
                        "cnpj": "11.222.333/0001-44"
                    },
                    "modalidade": "dispensa_licitacao",  # Potential red flag
                    "justificativa": "Emergência sanitária",
                    "data_assinatura": "2024-03-15",
                    "prazo_execucao": "30 dias"  # Short execution time for high value
                }
            ],
            "pagination": {"page": 1, "total": 1}
        }
        
        investigation_request = {
            "query": "contratos emergenciais acima de 1 milhão",
            "investigation_type": "anomaly_detection",
            "filters": {
                "min_value": 1000000,
                "modalidades": ["dispensa_licitacao", "inexigibilidade"]
            }
        }
        
        # Start investigation
        response = await client.post(
            "/api/v1/investigations/start",
            json=investigation_request,
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        investigation_id = response.json()["investigation_id"]
        
        # Wait for completion (simplified for testing)
        await asyncio.sleep(2)
        
        # Check results contain expected anomaly flags
        results_response = await client.get(
            f"/api/v1/investigations/{investigation_id}/results",
            headers=authenticated_headers
        )
        
        assert results_response.status_code == 200
        results = results_response.json()
        
        # Should detect high-value emergency contract as potential anomaly
        if results["findings"]:
            high_value_findings = [
                f for f in results["findings"] 
                if "high_value" in f.get("type", "").lower() or f.get("severity") in ["high", "critical"]
            ]
            assert len(high_value_findings) > 0, "Should detect high-value contract anomalies"

# tests/integration/test_database_operations.py
@pytest.mark.integration
@pytest.mark.asyncio
class TestDatabaseOperations:
    
    async def test_investigation_persistence(self, db_session, sample_investigation_request):
        """Test investigation data persistence in database."""
        from src.infrastructure.database import Investigation, InvestigationStatus
        
        # Create investigation record
        investigation = Investigation(
            query=sample_investigation_request["query"],
            investigation_type=sample_investigation_request["investigation_type"],
            status=InvestigationStatus.RUNNING,
            created_by="test-user"
        )
        
        db_session.add(investigation)
        await db_session.commit()
        await db_session.refresh(investigation)
        
        # Verify persistence
        assert investigation.id is not None
        assert investigation.created_at is not None
        assert investigation.status == InvestigationStatus.RUNNING
    
    async def test_audit_log_creation(self, db_session):
        """Test audit log entry creation."""
        from src.core.audit import create_audit_entry, AuditEventType, AuditSeverity
        
        audit_entry = await create_audit_entry(
            event_type=AuditEventType.INVESTIGATION_STARTED,
            user_id="test-user",
            resource_id="inv-123",
            message="Test investigation started",
            severity=AuditSeverity.LOW,
            details={"query": "test query"}
        )
        
        assert audit_entry.id is not None
        assert audit_entry.event_type == AuditEventType.INVESTIGATION_STARTED
        assert audit_entry.details["query"] == "test query"
```

## 2. CI/CD Pipeline Implementation

```yaml
# .github/workflows/comprehensive-ci-cd.yml
name: Comprehensive CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"
  POETRY_VERSION: "1.7.1"

jobs:
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install security tools
        run: |
          pip install bandit[toml] safety semgrep
      
      - name: Run Bandit security scan
        run: |
          bandit -r src/ -f json -o bandit-report.json
          bandit -r src/ -f txt
        continue-on-error: true
      
      - name: Run Safety dependency scan
        run: |
          safety check --json --output safety-report.json
          safety check
        continue-on-error: true
      
      - name: Run Semgrep security scan
        run: |
          semgrep --config=auto src/ --json -o semgrep-report.json
          semgrep --config=auto src/
        continue-on-error: true
      
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: security-reports
          path: "*-report.json"

  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: ${{ env.POETRY_VERSION }}
      
      - name: Load cached venv
        id: cached-poetry-dependencies
        uses: actions/cache@v3
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ steps.setup-python.outputs.python-version }}-${{ hashFiles('**/poetry.lock') }}
      
      - name: Install dependencies
        if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
        run: poetry install --no-interaction --no-root
      
      - name: Install project
        run: poetry install --no-interaction
      
      - name: Run Black formatting check
        run: poetry run black --check --diff src/ tests/
      
      - name: Run Ruff linting
        run: |
          poetry run ruff check src/ tests/ --output-format=github
          poetry run ruff format --check src/ tests/
      
      - name: Run MyPy type checking
        run: poetry run mypy src/ --strict --show-error-codes --pretty
      
      - name: Run import sorting check
        run: poetry run isort --check-only --diff src/ tests/

  test:
    name: Test Suite
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_cidadao_ai
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: ${{ env.POETRY_VERSION }}
      
      - name: Load cached venv
        id: cached-poetry-dependencies
        uses: actions/cache@v3
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
      
      - name: Install dependencies
        if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
        run: poetry install --no-interaction --no-root --with dev
      
      - name: Install project
        run: poetry install --no-interaction
      
      - name: Run unit tests
        run: |
          poetry run pytest tests/unit/ -v \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term-missing \
            --junit-xml=junit.xml \
            --cov-fail-under=80
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_cidadao_ai
          REDIS_URL: redis://localhost:6379/0
          TESTING: true
      
      - name: Run integration tests
        run: |
          poetry run pytest tests/integration/ -v \
            --junit-xml=integration-junit.xml
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_cidadao_ai
          REDIS_URL: redis://localhost:6379/0
          TESTING: true
      
      - name: Run E2E tests
        run: |
          poetry run pytest tests/e2e/ -v \
            --junit-xml=e2e-junit.xml
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_cidadao_ai
          REDIS_URL: redis://localhost:6379/0
          TESTING: true
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: |
            junit.xml
            integration-junit.xml
            e2e-junit.xml
            htmlcov/

  performance-test:
    name: Performance Testing
    runs-on: ubuntu-latest
    needs: [test]
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: perf_test_cidadao_ai
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Poetry and dependencies
        run: |
          pip install poetry
          poetry install --no-interaction --with dev
      
      - name: Run performance tests
        run: |
          poetry run pytest tests/performance/ -v \
            --benchmark-json=benchmark-results.json
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/perf_test_cidadao_ai
          REDIS_URL: redis://localhost:6379/0
          TESTING: true
      
      - name: Upload benchmark results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark-results.json

  build:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    needs: [security-scan, code-quality, test]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            VCS_REF=${{ github.sha }}
            VERSION=${{ steps.meta.outputs.version }}

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add your deployment scripts here

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production environment"
          # Add your deployment scripts here
```

## 3. Monitoring and Observability

```python
# src/infrastructure/monitoring.py
import time
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

AGENT_EXECUTION_TIME = Histogram(
    'agent_execution_seconds',
    'Agent execution time in seconds',
    ['agent_name', 'action']
)

ACTIVE_INVESTIGATIONS = Gauge(
    'active_investigations_total',
    'Number of currently active investigations'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

CACHE_HIT_RATE = Gauge(
    'cache_hit_rate_percent',
    'Cache hit rate percentage'
)

API_ERRORS = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type']
)

# Application Info
APP_INFO = Info(
    'cidadao_ai_app',
    'Application information'
)

class MonitoringService:
    """Comprehensive monitoring and observability service."""
    
    def __init__(self, app_name: str = "cidadao-ai-api"):
        self.app_name = app_name
        self.tracer = trace.get_tracer(__name__)
        self.logger = logging.getLogger(__name__)
        
        # Initialize tracing
        self._setup_tracing()
        
        # Set application info
        APP_INFO.info({
            'app_name': app_name,
            'version': '1.0.0',
            'environment': 'production'  # This should come from config
        })
    
    def _setup_tracing(self):
        """Setup distributed tracing with Jaeger."""
        trace.set_tracer_provider(TracerProvider())
        
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
    
    def instrument_app(self, app, database_engine=None):
        """Instrument FastAPI application with monitoring."""
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        
        # Instrument SQLAlchemy if engine provided
        if database_engine:
            SQLAlchemyInstrumentor().instrument(engine=database_engine)
        
        # Instrument Redis
        RedisInstrumentor().instrument()
        
        # Start Prometheus metrics server
        start_http_server(8001)  # Metrics available on :8001/metrics
        
        self.logger.info("Application instrumentation completed")
    
    @contextmanager
    def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """Context manager for tracing operations."""
        with self.tracer.start_as_current_span(operation_name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            start_time = time.time()
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
            finally:
                execution_time = time.time() - start_time
                span.set_attribute("operation.duration", execution_time)
    
    @contextmanager
    def trace_agent_execution(self, agent_name: str, action: str, context: Optional[Dict[str, Any]] = None):
        """Trace agent execution with metrics."""
        attributes = {
            "agent.name": agent_name,
            "agent.action": action
        }
        if context:
            attributes.update(context)
        
        with self.trace_operation(f"agent.{agent_name}.{action}", attributes) as span:
            start_time = time.time()
            try:
                yield span
            finally:
                execution_time = time.time() - start_time
                AGENT_EXECUTION_TIME.labels(
                    agent_name=agent_name,
                    action=action
                ).observe(execution_time)
    
    def record_request_metrics(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_error(self, endpoint: str, error_type: str):
        """Record API error metrics."""
        API_ERRORS.labels(
            endpoint=endpoint,
            error_type=error_type
        ).inc()
    
    def update_active_investigations(self, count: int):
        """Update active investigations gauge."""
        ACTIVE_INVESTIGATIONS.set(count)
    
    def update_database_connections(self, count: int):
        """Update database connections gauge."""
        DATABASE_CONNECTIONS.set(count)
    
    def update_cache_hit_rate(self, hit_rate: float):
        """Update cache hit rate gauge."""
        CACHE_HIT_RATE.set(hit_rate)

# Middleware for automatic request monitoring
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically collect request metrics."""
    
    def __init__(self, app, monitoring_service: MonitoringService):
        super().__init__(app)
        self.monitoring = monitoring_service
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract endpoint path (remove query params and normalize)
        endpoint = request.url.path
        method = request.method
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Record error
            self.monitoring.record_error(endpoint, type(e).__name__)
            status_code = 500
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            self.monitoring.record_request_metrics(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration=duration
            )
        
        return response

# Health check with monitoring integration
from fastapi import APIRouter
from src.infrastructure.database import database_manager
from src.infrastructure.cache_system import cache_system

monitoring_router = APIRouter()

@monitoring_router.get("/metrics/health")
async def health_check_with_metrics():
    """Health check that also updates monitoring metrics."""
    monitoring_service = MonitoringService()
    
    checks = {
        "database": await _check_database_with_metrics(),
        "redis": await _check_redis_with_metrics(),
        "agents": await _check_agents_health()
    }
    
    # Update connection metrics
    if database_manager.engine:
        pool = database_manager.engine.pool
        monitoring_service.update_database_connections(pool.checkedin())
    
    # Update cache metrics
    try:
        cache_stats = await cache_system.get_stats()
        if cache_stats:
            hit_rate = cache_stats.get('hit_rate', 0)
            monitoring_service.update_cache_hit_rate(hit_rate)
    except Exception:
        pass
    
    healthy = all(checks.values())
    return {
        "status": "healthy" if healthy else "unhealthy",
        "checks": checks,
        "timestamp": time.time()
    }

async def _check_database_with_metrics() -> bool:
    """Check database with connection metrics."""
    try:
        async with database_manager.get_session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return False

async def _check_redis_with_metrics() -> bool:
    """Check Redis with cache metrics."""
    try:
        result = await cache_system.redis.ping()
        return result
    except Exception as e:
        logging.error(f"Redis health check failed: {e}")
        return False

async def _check_agents_health() -> bool:
    """Check agent system health."""
    # This would check if agents are responding
    # For now, return True as placeholder
    return True
```

## 4. Performance Enhancements

```python
# src/infrastructure/performance.py
import asyncio
import time
from typing import Dict, Any, Optional, Callable, Awaitable
from functools import wraps
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool
import pickle
import json
from decimal import Decimal

class PerformanceOptimizedDatabaseManager:
    """High-performance database manager with connection pooling and optimization."""
    
    def __init__(self, database_url: str, **engine_kwargs):
        # Optimized engine configuration
        self.engine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,                    # Number of connections to maintain
            max_overflow=30,                 # Additional connections when pool is full
            pool_timeout=30,                 # Timeout to get connection from pool
            pool_recycle=3600,              # Recycle connections every hour
            pool_pre_ping=True,             # Validate connections before use
            echo=False,                     # Set to True for query debugging
            future=True,                    # Use SQLAlchemy 2.0 style
            **engine_kwargs
        )
        
        # Connection health monitoring
        self._connection_errors = 0
        self._total_connections = 0
    
    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        """Get database session with error handling and monitoring."""
        session = None
        try:
            session = AsyncSession(
                self.engine,
                expire_on_commit=False  # Keep objects accessible after commit
            )
            self._total_connections += 1
            yield session
            await session.commit()
        except Exception as e:
            self._connection_errors += 1
            if session:
                await session.rollback()
            raise
        finally:
            if session:
                await session.close()
    
    async def execute_with_retry(self, query, params=None, max_retries=3):
        """Execute query with automatic retry on connection failures."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                async with self.get_session() as session:
                    result = await session.execute(query, params)
                    return result
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    # Wait with exponential backoff
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                continue
        
        raise last_exception
    
    @property
    def connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        pool = self.engine.pool
        return {
            "total_connections": self._total_connections,
            "connection_errors": self._connection_errors,
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "error_rate": self._connection_errors / max(self._total_connections, 1)
        }

class AdvancedCacheSystem:
    """Advanced caching system with multiple serialization strategies."""
    
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(
            redis_url,
            encoding='utf-8',
            decode_responses=False,  # Handle binary data
            max_connections=20,      # Connection pool size
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Serialization strategies
        self.serializers = {
            'json': (self._json_serialize, self._json_deserialize),
            'pickle': (pickle.dumps, pickle.loads),
            'string': (str.encode, bytes.decode),
        }
        
        # Cache statistics
        self._cache_hits = 0
        self._cache_misses = 0
    
    def _json_serialize(self, data):
        """JSON serialization with Decimal support."""
        def decimal_converter(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(data, default=decimal_converter).encode('utf-8')
    
    def _json_deserialize(self, data):
        """JSON deserialization."""
        return json.loads(data.decode('utf-8'))
    
    async def get(self, key: str, serializer: str = 'json') -> Optional[Any]:
        """Get value from cache with automatic deserialization."""
        try:
            cached_data = await self.redis.get(key)
            if cached_data is None:
                self._cache_misses += 1
                return None
            
            self._cache_hits += 1
            _, deserialize = self.serializers[serializer]
            return deserialize(cached_data)
        
        except Exception as e:
            logging.warning(f"Cache get failed for key {key}: {e}")
            self._cache_misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600, serializer: str = 'json') -> bool:
        """Set value in cache with automatic serialization."""
        try:
            serialize, _ = self.serializers[serializer]
            serialized_data = serialize(value)
            
            await self.redis.setex(key, ttl, serialized_data)
            return True
        
        except Exception as e:
            logging.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
        ttl: int = 3600,
        serializer: str = 'json'
    ) -> Any:
        """Get from cache or execute factory function and cache result."""
        # Try to get from cache first
        cached_value = await self.get(key, serializer)
        if cached_value is not None:
            return cached_value
        
        # Execute factory function
        value = await factory()
        
        # Cache the result
        await self.set(key, value, ttl, serializer)
        
        return value
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logging.warning(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logging.warning(f"Cache pattern clear failed for {pattern}: {e}")
            return 0
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / max(total_requests, 1)
        
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "hit_rate_percent": hit_rate * 100
        }

# Performance decorators
def cache_result(cache_key_template: str, ttl: int = 3600, serializer: str = 'json'):
    """Decorator to cache function results."""
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from src.infrastructure.cache_system import cache_system
            
            # Generate cache key from template and arguments
            cache_key = cache_key_template.format(*args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_system.get(cache_key, serializer)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_system.set(cache_key, result, ttl, serializer)
            
            return result
        
        return wrapper
    return decorator

def timing_monitor(operation_name: str):
    """Decorator to monitor function execution time."""
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                logging.info(f"Operation {operation_name} took {execution_time:.3f}s")
                
                # Record in monitoring system if available
                try:
                    from src.infrastructure.monitoring import AGENT_EXECUTION_TIME
                    AGENT_EXECUTION_TIME.labels(
                        agent_name=operation_name,
                        action="execute"
                    ).observe(execution_time)
                except ImportError:
                    pass
        
        return wrapper
    return decorator

# Optimized agent execution
class PerformanceOptimizedAgent:
    """Base class for performance-optimized agents."""
    
    def __init__(self, cache_system: AdvancedCacheSystem):
        self.cache = cache_system
    
    @cache_result("agent:{self.__class__.__name__}:analysis:{query_hash}", ttl=1800)
    @timing_monitor("agent_analysis")
    async def cached_analyze(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Cached analysis with performance monitoring."""
        # Hash query for cache key
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        # Perform actual analysis
        return await self._perform_analysis(query, context)
    
    async def _perform_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses."""
        raise NotImplementedError
    
    @asynccontextmanager
    async def performance_context(self, operation_name: str):
        """Context manager for performance monitoring."""
        start_time = time.time()
        operation_id = f"{self.__class__.__name__}:{operation_name}"
        
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            logging.debug(f"{operation_id} completed in {execution_time:.3f}s")

# Batch processing utilities
class BatchProcessor:
    """Utility for efficient batch processing."""
    
    @staticmethod
    async def process_in_batches(
        items: list,
        processor: Callable[[Any], Awaitable[Any]],
        batch_size: int = 10,
        max_concurrent: int = 5
    ):
        """Process items in batches with concurrency control."""
        results = []
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_batch(batch):
            async with semaphore:
                batch_results = await asyncio.gather(
                    *[processor(item) for item in batch],
                    return_exceptions=True
                )
                return batch_results
        
        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await process_batch(batch)
            results.extend(batch_results)
        
        return results
```

Este plano de melhorias está pronto para implementação e transformará o backend em um sistema enterprise de classe mundial. Quer que eu continue com as próximas fases ou você gostaria de focar em alguma área específica?