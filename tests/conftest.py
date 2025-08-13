"""
Test configuration and fixtures for the Cidadão.AI Backend.
Provides comprehensive test setup with database, Redis, and API client fixtures.
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from unittest.mock import AsyncMock, patch, Mock

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["TESTING"] = "true"

from src.api.app import create_app
from src.core.database import get_db_session
from src.core.config import Settings, get_settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_database() -> AsyncGenerator[str, None]:
    """Integration test database using testcontainers."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        database_url = postgres.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        
        # Create engine
        engine = create_async_engine(database_url)
        
        # Run migrations (simplified for tests)
        from src.core.database import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield database_url
        
        # Cleanup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        await engine.dispose()


@pytest.fixture(scope="session")
async def test_redis() -> AsyncGenerator[str, None]:
    """Test Redis instance using testcontainers."""
    with RedisContainer("redis:7-alpine") as redis_container:
        redis_url = redis_container.get_connection_url()
        yield redis_url


@pytest.fixture
async def db_session(test_database: str) -> AsyncGenerator[AsyncSession, None]:
    """Database session for individual tests."""
    engine = create_async_engine(test_database)
    
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.rollback()  # Always rollback test transactions
        finally:
            await session.close()
    
    await engine.dispose()


@pytest.fixture
async def test_settings(test_database: str, test_redis: str) -> Settings:
    """Test application settings."""
    return Settings(
        database_url=test_database,
        redis_url=test_redis,
        testing=True,
        secret_key="test-secret-key-do-not-use-in-production",
        transparency_api_key="test-api-key",
        environment="testing"
    )


@pytest.fixture
async def app(test_settings: Settings):
    """FastAPI application for testing."""
    app = create_app(test_settings)
    return app


@pytest.fixture
async def client(app, db_session: AsyncSession, test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Test client with database session override."""
    
    async def get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = get_test_db
    app.dependency_overrides[get_settings] = lambda: test_settings
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated test client with JWT token."""
    # Create test user and get token
    test_user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    # Register test user
    await client.post("/auth/register", json=test_user_data)
    
    # Login and get token
    response = await client.post("/auth/login", data={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Set authorization header
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    yield client


@pytest.fixture
def mock_transparency_api():
    """Mock for transparency API calls."""
    with patch('src.services.transparency_service.TransparencyService') as mock:
        # Configure mock responses
        mock.return_value.get_contracts.return_value = {
            "data": [
                {
                    "id": "123",
                    "objeto": "Test contract",
                    "valor": 100000.00,
                    "dataInicioVigencia": "2024-01-01",
                    "dataFimVigencia": "2024-12-31",
                    "fornecedor": {"nome": "Test Supplier"}
                }
            ],
            "total": 1
        }
        
        mock.return_value.get_expenses.return_value = {
            "data": [
                {
                    "id": "456",
                    "orgaoSuperior": {"nome": "Test Ministry"},
                    "valor": 50000.00,
                    "dataCompetencia": "2024-01-01",
                    "modalidadeAplicacao": {"nome": "Direct Application"}
                }
            ],
            "total": 1
        }
        
        yield mock


@pytest.fixture
def mock_ai_service():
    """Mock for AI service calls."""
    with patch('src.services.ai_service.AIService') as mock:
        # Configure mock responses
        mock.return_value.classify_text.return_value = {
            "label": "corruption",
            "confidence": 0.85,
            "explanation": "High probability of corruption indicators"
        }
        
        mock.return_value.analyze_anomalies.return_value = {
            "anomalies": [
                {
                    "type": "price_anomaly",
                    "severity": "high",
                    "description": "Price 300% above market average"
                }
            ],
            "risk_score": 0.78
        }
        
        yield mock


@pytest.fixture
def mock_agent_system():
    """Mock for agent system."""
    with patch('src.agents.abaporu.MasterAgent') as mock:
        # Configure mock agent responses
        async def mock_process_task(task):
            return {
                "task_id": task.get("id", "test-task"),
                "status": "completed",
                "result": {
                    "analysis": "Test analysis result",
                    "recommendations": ["Test recommendation 1", "Test recommendation 2"],
                    "confidence": 0.9
                },
                "agents_used": ["investigator", "analyst", "reporter"],
                "processing_time": 2.5
            }
        
        mock.return_value.process_task = mock_process_task
        yield mock


@pytest.fixture
def sample_analysis_data():
    """Sample data for analysis tests."""
    return {
        "text": "Contrato de fornecimento de equipamentos de informática no valor de R$ 1.000.000,00",
        "type": "analyze",
        "options": {
            "includeMetrics": True,
            "includeVisualization": False,
            "language": "pt"
        }
    }


@pytest.fixture
def sample_contract_data():
    """Sample contract data for tests."""
    return {
        "numero": "123456/2024",
        "objeto": "Fornecimento de equipamentos de informática",
        "valor": 1000000.00,
        "dataAssinatura": "2024-01-15",
        "dataInicioVigencia": "2024-02-01",
        "dataFimVigencia": "2025-01-31",
        "fornecedor": {
            "cnpj": "12.345.678/0001-90",
            "nome": "Tech Solutions LTDA",
            "endereco": "Rua das Tecnologias, 123"
        },
        "orgao": {
            "codigo": "26000",
            "nome": "Ministério da Educação",
            "sigla": "MEC"
        }
    }


@pytest.fixture
def sample_expense_data():
    """Sample expense data for tests."""
    return {
        "codigo": "789012",
        "valor": 50000.00,
        "dataCompetencia": "2024-01-01",
        "orgaoSuperior": {
            "codigo": "20000",
            "nome": "Presidência da República",
            "sigla": "PR"
        },
        "funcao": {
            "codigo": "04",
            "nome": "Administração"
        },
        "subfuncao": {
            "codigo": "122",
            "nome": "Administração Geral"
        },
        "modalidadeAplicacao": {
            "codigo": "90",
            "nome": "Aplicação Direta"
        }
    }


# Test markers for categorization
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow
pytest.mark.security = pytest.mark.security
pytest.mark.performance = pytest.mark.performance


# Environment setup for tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "security: Security-related tests")
    config.addinivalue_line("markers", "performance: Performance tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to tests without explicit markers
        if not any(marker.name in ["integration", "e2e", "slow", "security", "performance"] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() for keyword in ["database", "redis", "ai", "agent"]):
            item.add_marker(pytest.mark.slow)