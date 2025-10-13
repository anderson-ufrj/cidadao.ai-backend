"""
Integration tests for main application flows.
Tests end-to-end workflows including investigation, chat, and analysis.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.agents.anita import AnalystAgent
from src.agents.deodoro import AgentResponse, AgentStatus
from src.agents.tiradentes import ReporterAgent
from src.agents.zumbi import InvestigatorAgent
from src.core.exceptions import (
    AgentExecutionError,
)
from src.services.analysis_service import AnalysisService
from src.services.chat_service import ChatService
from src.services.investigation_service import InvestigationService


@pytest.fixture
async def investigation_service():
    """Create investigation service for testing."""
    service = InvestigationService()
    yield service


@pytest.fixture
async def chat_service():
    """Create chat service for testing."""
    service = ChatService()
    yield service


@pytest.fixture
async def analysis_service():
    """Create analysis service for testing."""
    service = AnalysisService()
    yield service


@pytest.fixture
def mock_agent_pool():
    """Mock agent pool for testing."""
    pool = AsyncMock()

    # Mock agent instances
    mock_zumbi = AsyncMock(spec=InvestigatorAgent)
    mock_zumbi.name = "Zumbi"
    mock_zumbi.process.return_value = AgentResponse(
        agent_name="Zumbi",
        status=AgentStatus.COMPLETED,
        result={
            "anomalies_detected": 3,
            "findings": [
                {"type": "price_anomaly", "severity": "high"},
                {"type": "temporal_pattern", "severity": "medium"},
                {"type": "vendor_concentration", "severity": "low"},
            ],
            "confidence": 0.85,
        },
    )

    mock_anita = AsyncMock(spec=AnalystAgent)
    mock_anita.name = "Anita"
    mock_anita.process.return_value = AgentResponse(
        agent_name="Anita",
        status=AgentStatus.COMPLETED,
        result={
            "patterns": ["seasonal_spike", "vendor_clustering"],
            "correlations": [{"field1": "price", "field2": "date", "strength": 0.72}],
            "risk_score": 0.68,
        },
    )

    mock_tiradentes = AsyncMock(spec=ReporterAgent)
    mock_tiradentes.name = "Tiradentes"
    mock_tiradentes.process.return_value = AgentResponse(
        agent_name="Tiradentes",
        status=AgentStatus.COMPLETED,
        result={
            "report": "# Investigation Report\n\n## Summary\nMultiple anomalies detected...",
            "executive_summary": "3 anomalies found with high confidence",
            "recommendations": ["Review vendor contracts", "Audit pricing mechanism"],
        },
    )

    # Mock acquire context manager
    @asynccontextmanager
    async def mock_acquire(agent_type, context):
        if agent_type == InvestigatorAgent:
            yield mock_zumbi
        elif agent_type == AnalystAgent:
            yield mock_anita
        elif agent_type == ReporterAgent:
            yield mock_tiradentes
        else:
            yield AsyncMock()

    pool.acquire = mock_acquire
    return pool


@pytest.fixture
def mock_data_service():
    """Mock data service for testing."""
    service = AsyncMock()
    service.search_contracts.return_value = {
        "contracts": [
            {
                "id": "12345",
                "vendor": "Empresa XYZ",
                "value": 1000000.00,
                "date": "2024-01-15",
                "status": "active",
            },
            {
                "id": "67890",
                "vendor": "Empresa ABC",
                "value": 2500000.00,
                "date": "2024-02-01",
                "status": "active",
            },
        ],
        "total": 2,
        "metadata": {"source": "portal_transparencia"},
    }
    return service


class TestInvestigationFlow:
    """Test complete investigation flow."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_and_run_investigation(
        self, investigation_service, mock_agent_pool, mock_data_service
    ):
        """Test creating and running a complete investigation."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            with patch(
                "src.services.investigation_service.DataService",
                return_value=mock_data_service,
            ):
                # Create investigation
                investigation = await investigation_service.create(
                    user_id="test_user",
                    query="Analyze contracts from company XYZ",
                    data_sources=["portal_transparencia"],
                )

                assert investigation.id is not None
                assert investigation.status == "created"
                assert investigation.user_id == "test_user"

                # Run investigation (would be done by background worker in production)
                result = await investigation_service.run_investigation(investigation.id)

                assert result.status == "completed"
                assert result.confidence_score > 0.7
                assert "anomalies_detected" in result.metadata
                assert result.metadata["anomalies_detected"] == 3

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_investigation_with_multiple_agents(
        self, investigation_service, mock_agent_pool, mock_data_service
    ):
        """Test investigation using multiple agents in sequence."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            with patch(
                "src.services.investigation_service.DataService",
                return_value=mock_data_service,
            ):
                investigation = await investigation_service.create(
                    user_id="test_user",
                    query="Deep analysis of government contracts",
                    analysis_type="comprehensive",
                )

                # Mock the orchestration to use multiple agents
                result = await investigation_service.run_investigation(investigation.id)

                # Verify all agents were called
                assert (
                    mock_agent_pool.acquire.call_count >= 3
                )  # At least Zumbi, Anita, Tiradentes

                # Verify result contains data from all agents
                assert "findings" in result.metadata
                assert "patterns" in result.metadata
                assert "report" in result.metadata

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_investigation_error_handling(
        self, investigation_service, mock_agent_pool
    ):
        """Test investigation error handling."""
        # Make agent fail
        mock_agent_pool.acquire.side_effect = AgentExecutionError("Agent failed")

        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            investigation = await investigation_service.create(
                user_id="test_user", query="Test query"
            )

            with pytest.raises(AgentExecutionError):
                await investigation_service.run_investigation(investigation.id)

            # Check investigation status
            updated = await investigation_service.get(investigation.id)
            assert updated.status == "failed"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_investigation_timeout(self, investigation_service):
        """Test investigation timeout handling."""
        # Create slow mock agent
        slow_agent = AsyncMock()

        async def slow_process(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout

        slow_agent.process = slow_process

        mock_pool = AsyncMock()

        @asynccontextmanager
        async def mock_acquire(agent_type, context):
            yield slow_agent

        mock_pool.acquire = mock_acquire

        with patch("src.agents.get_agent_pool", return_value=mock_pool):
            investigation = await investigation_service.create(
                user_id="test_user", query="Test timeout", timeout=1  # 1 second timeout
            )

            with pytest.raises(asyncio.TimeoutError):
                await investigation_service.run_investigation(investigation.id)


class TestChatFlow:
    """Test complete chat flow."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_conversation_flow(self, chat_service, mock_agent_pool):
        """Test full chat conversation flow."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            # Start session
            session_id = await chat_service.create_session("test_user")

            # Send message
            response = await chat_service.send_message(
                session_id=session_id, message="Analyze recent government contracts"
            )

            assert response.session_id == session_id
            assert response.content is not None
            assert response.metadata.get("agent") == "Zumbi"

            # Continue conversation
            response2 = await chat_service.send_message(
                session_id=session_id, message="Can you provide more details?"
            )

            assert response2.session_id == session_id
            assert (
                len(await chat_service.get_history(session_id)) == 4
            )  # 2 user + 2 assistant

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_with_context_switching(self, chat_service, mock_agent_pool):
        """Test chat with context switching between agents."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            session_id = await chat_service.create_session("test_user")

            # Ask for investigation
            response1 = await chat_service.send_message(
                session_id=session_id, message="Investigate contract anomalies"
            )

            # Ask for analysis
            response2 = await chat_service.send_message(
                session_id=session_id, message="Analyze the patterns found"
            )

            # Ask for report
            response3 = await chat_service.send_message(
                session_id=session_id, message="Generate a report of findings"
            )

            history = await chat_service.get_history(session_id)

            # Verify different agents were used
            agents_used = {
                msg.metadata.get("agent") for msg in history if msg.role == "assistant"
            }
            assert len(agents_used) >= 2  # Multiple agents used

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_streaming(self, chat_service, mock_agent_pool):
        """Test chat streaming functionality."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            session_id = await chat_service.create_session("test_user")

            chunks = []
            async for chunk in chat_service.stream_message(
                session_id=session_id, message="Generate detailed analysis"
            ):
                chunks.append(chunk)

            assert len(chunks) > 0
            complete_response = "".join(chunk.content for chunk in chunks)
            assert len(complete_response) > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_error_recovery(self, chat_service):
        """Test chat error recovery mechanisms."""
        # Mock agent that fails first time, succeeds second time
        attempts = 0

        async def flaky_process(*args, **kwargs):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise Exception("Temporary failure")
            return AgentResponse(
                agent_name="TestAgent",
                status=AgentStatus.COMPLETED,
                result={"message": "Success after retry"},
            )

        mock_agent = AsyncMock()
        mock_agent.process = flaky_process

        mock_pool = AsyncMock()

        @asynccontextmanager
        async def mock_acquire(agent_type, context):
            yield mock_agent

        mock_pool.acquire = mock_acquire

        with patch("src.agents.get_agent_pool", return_value=mock_pool):
            session_id = await chat_service.create_session("test_user")

            # Should succeed after retry
            response = await chat_service.send_message(
                session_id=session_id, message="Test retry mechanism"
            )

            assert response.content is not None
            assert attempts == 2  # Failed once, succeeded on retry


class TestAnalysisFlow:
    """Test complete analysis flow."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(
        self, analysis_service, mock_agent_pool, mock_data_service
    ):
        """Test comprehensive data analysis flow."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            with patch(
                "src.services.analysis_service.DataService",
                return_value=mock_data_service,
            ):
                # Run analysis
                results = await analysis_service.analyze_contracts(
                    filters={"vendor": "Empresa XYZ"},
                    analysis_types=["anomaly", "pattern", "risk"],
                )

                assert "anomalies" in results
                assert "patterns" in results
                assert "risk_assessment" in results
                assert results["anomalies"]["count"] == 3
                assert results["risk_assessment"]["score"] > 0.5

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_parallel_analysis(self, analysis_service, mock_agent_pool):
        """Test parallel analysis with multiple agents."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            # Mock parallel processor
            with patch(
                "src.agents.parallel_processor.parallel_processor"
            ) as mock_parallel:
                mock_parallel.execute_parallel.return_value = [
                    Mock(
                        success=True,
                        result=AgentResponse(
                            agent_name="Zumbi",
                            status=AgentStatus.COMPLETED,
                            result={"anomalies": 5},
                        ),
                    ),
                    Mock(
                        success=True,
                        result=AgentResponse(
                            agent_name="Anita",
                            status=AgentStatus.COMPLETED,
                            result={"patterns": 3},
                        ),
                    ),
                ]

                results = await analysis_service.parallel_analysis(
                    data_sources=["contracts", "payments"], agents=["zumbi", "anita"]
                )

                assert mock_parallel.execute_parallel.called
                assert len(results) == 2
                assert results[0]["agent"] == "Zumbi"
                assert results[1]["agent"] == "Anita"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analysis_caching(self, analysis_service, mock_agent_pool):
        """Test analysis results caching."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            with patch("src.services.cache_service.CacheService") as mock_cache:
                cache_instance = AsyncMock()
                mock_cache.return_value = cache_instance
                cache_instance.get.return_value = None  # First call, no cache

                # First analysis
                results1 = await analysis_service.analyze_with_cache(
                    query_hash="test_hash",
                    analysis_func=AsyncMock(return_value={"data": "results"}),
                )

                # Verify cache was set
                assert cache_instance.set.called

                # Second call should use cache
                cache_instance.get.return_value = {"data": "cached_results"}
                results2 = await analysis_service.analyze_with_cache(
                    query_hash="test_hash", analysis_func=AsyncMock()
                )

                assert results2["data"] == "cached_results"


class TestEndToEndFlow:
    """Test complete end-to-end application flow."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_investigation_to_report_flow(
        self,
        investigation_service,
        chat_service,
        analysis_service,
        mock_agent_pool,
        mock_data_service,
    ):
        """Test full flow from user request to final report."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            with patch(
                "src.services.investigation_service.DataService",
                return_value=mock_data_service,
            ):
                # 1. User starts chat session
                session_id = await chat_service.create_session("test_user")

                # 2. User requests investigation
                chat_response = await chat_service.send_message(
                    session_id=session_id,
                    message="I want to investigate suspicious contracts from Empresa XYZ",
                )

                # 3. System creates investigation
                investigation = await investigation_service.create(
                    user_id="test_user",
                    query="Investigate Empresa XYZ contracts",
                    session_id=session_id,
                )

                # 4. Run investigation with multiple agents
                investigation_result = await investigation_service.run_investigation(
                    investigation.id
                )

                # 5. Generate analysis
                analysis_results = await analysis_service.analyze_investigation(
                    investigation_id=investigation.id
                )

                # 6. Generate final report
                report_response = await chat_service.send_message(
                    session_id=session_id,
                    message="Generate executive report of findings",
                )

                # Verify complete flow
                assert investigation_result.status == "completed"
                assert analysis_results["anomalies"]["count"] > 0
                assert "executive_summary" in report_response.metadata

                # Verify audit trail
                history = await chat_service.get_history(session_id)
                assert len(history) >= 4  # Initial request + responses

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_user_flows(
        self, investigation_service, chat_service, mock_agent_pool
    ):
        """Test handling multiple concurrent user flows."""
        with patch("src.agents.get_agent_pool", return_value=mock_agent_pool):
            # Create multiple user sessions
            users = ["user1", "user2", "user3"]
            sessions = []

            for user in users:
                session_id = await chat_service.create_session(user)
                sessions.append((user, session_id))

            # Run concurrent investigations
            tasks = []
            for user, session_id in sessions:
                task = investigation_service.create(
                    user_id=user, query=f"Investigation for {user}"
                )
                tasks.append(task)

            investigations = await asyncio.gather(*tasks)

            # Verify all created successfully
            assert len(investigations) == 3
            assert all(inv.user_id in users for inv in investigations)

            # Run concurrent processing
            process_tasks = []
            for inv in investigations:
                task = investigation_service.run_investigation(inv.id)
                process_tasks.append(task)

            results = await asyncio.gather(*process_tasks)

            # Verify all completed
            assert all(r.status == "completed" for r in results)

            # Verify isolation - each investigation has its own data
            user_ids = {r.user_id for r in results}
            assert len(user_ids) == 3


class TestErrorRecoveryFlow:
    """Test error recovery and resilience flows."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(
        self, investigation_service, mock_data_service
    ):
        """Test circuit breaker integration in main flows."""
        from src.infrastructure.resilience.circuit_breaker import (
            circuit_breaker_manager,
        )

        # Mock data service to fail multiple times
        mock_data_service.search_contracts.side_effect = [
            Exception("Service unavailable"),
            Exception("Service unavailable"),
            Exception("Service unavailable"),
            {"contracts": [], "total": 0},  # Eventually succeeds
        ]

        with patch(
            "src.services.investigation_service.DataService",
            return_value=mock_data_service,
        ):
            # First investigations should fail and open circuit
            for i in range(3):
                investigation = await investigation_service.create(
                    user_id="test_user", query=f"Test {i}"
                )

                with pytest.raises(Exception):
                    await investigation_service.run_investigation(investigation.id)

            # Check circuit breaker status
            stats = circuit_breaker_manager.get_all_stats()
            # Circuit should be open for the failed service

            # Wait for recovery timeout
            await asyncio.sleep(1.1)

            # Next attempt should work
            investigation = await investigation_service.create(
                user_id="test_user", query="Test recovery"
            )

            result = await investigation_service.run_investigation(investigation.id)
            assert result.status == "completed"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_fallback_mechanisms(self, chat_service):
        """Test fallback mechanisms in main flows."""
        # Mock all agents to fail
        failed_agent = AsyncMock()
        failed_agent.process.side_effect = Exception("Agent unavailable")

        mock_pool = AsyncMock()

        @asynccontextmanager
        async def mock_acquire(agent_type, context):
            yield failed_agent

        mock_pool.acquire = mock_acquire

        with patch("src.agents.get_agent_pool", return_value=mock_pool):
            # Mock emergency chat to work
            with patch(
                "src.services.chat_emergency.emergency_chat_handler"
            ) as mock_emergency:
                mock_emergency.handle_message.return_value = {
                    "response": "Emergency response",
                    "status": "fallback",
                }

                session_id = await chat_service.create_session("test_user")

                # Should fall back to emergency handler
                response = await chat_service.send_message(
                    session_id=session_id, message="Test message", use_fallback=True
                )

                assert response.content == "Emergency response"
                assert response.metadata["status"] == "fallback"


from contextlib import asynccontextmanager


@asynccontextmanager
async def mock_acquire(agent_type, context):
    """Mock context manager for agent pool acquire."""
    yield AsyncMock()
