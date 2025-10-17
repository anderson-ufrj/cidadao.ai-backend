"""
Advanced orchestration tests for multi-agent system.
Tests complex coordination patterns, failure handling, and performance.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import numpy as np
import pytest
import pytest_asyncio

from src.agents import (
    AgentContext,
    AgentMessage,
    AnitaAgent,
    BonifacioAgent,
    MariaQuiteriaAgent,
    ZumbiAgent,
)
from src.services.agent_orchestrator import AgentOrchestrator


@pytest_asyncio.fixture
async def orchestrator():
    """Create agent orchestrator for tests."""
    orch = AgentOrchestrator()
    await orch.initialize()
    return orch


@pytest.fixture
def orchestration_context():
    """Create orchestration context."""
    return AgentContext(
        investigation_id=str(uuid4()),
        user_id="orchestration-tester",
        session_id=str(uuid4()),
        metadata={
            "test_type": "orchestration",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


class TestAdvancedOrchestration:
    """Test advanced orchestration patterns."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_dynamic_agent_selection(self, orchestrator, orchestration_context):
        """Test dynamic agent selection based on task requirements."""

        # Define tasks with different requirements
        tasks = [
            {
                "type": "anomaly_detection",
                "data": {"contract_value": 1_000_000},
                "required_capabilities": ["anomaly_detection", "pattern_analysis"],
            },
            {
                "type": "security_audit",
                "data": {"system_name": "Portal"},
                "required_capabilities": ["security_audit", "threat_detection"],
            },
            {
                "type": "policy_analysis",
                "data": {"policy_name": "Digital Gov"},
                "required_capabilities": ["policy_analysis", "governance"],
            },
        ]

        # Execute dynamic routing
        results = []
        for task in tasks:
            agent = await orchestrator.select_best_agent(task["required_capabilities"])

            assert agent is not None

            message = AgentMessage(
                type=task["type"],
                data=task["data"],
                sender="orchestrator",
                metadata={"dynamic_routing": True},
            )

            response = await agent.process(message, orchestration_context)
            results.append(
                {"task": task["type"], "agent": agent.name, "success": response.success}
            )

        # Verify correct agent selection
        assert results[0]["agent"] in [
            "InvestigatorAgent",
            "AnalystAgent",
        ]  # Anomaly detection
        assert results[1]["agent"] == "MariaQuiteriaAgent"  # Security audit
        assert results[2]["agent"] == "BonifacioAgent"  # Policy analysis

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_adaptive_retry_with_fallback(
        self, orchestrator, orchestration_context
    ):
        """Test adaptive retry mechanism with agent fallback."""

        primary_agent = MariaQuiteriaAgent()
        fallback_agent = ZumbiAgent()

        # Mock primary agent to fail initially
        call_count = 0
        original_process = primary_agent.process

        async def failing_process(message, context):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return await original_process(message, context)

        primary_agent.process = failing_process

        # Configure orchestrator with retry and fallback
        orchestrator.configure_retry_policy(
            {
                "max_retries": 2,
                "backoff_multiplier": 1.5,
                "fallback_agents": {"MariaQuiteriaAgent": "InvestigatorAgent"},
            }
        )

        message = AgentMessage(
            type="security_audit",
            data={"system_name": "Test System"},
            sender="orchestrator",
            metadata={},
        )

        # Execute with retry logic
        result = await orchestrator.execute_with_retry(
            primary_agent, message, orchestration_context, fallback_agent=fallback_agent
        )

        # Should succeed after retries
        assert result.success is True
        assert call_count == 3  # Failed twice, succeeded on third

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_conditional_workflow_branching(
        self, orchestrator, orchestration_context
    ):
        """Test conditional workflow branching based on intermediate results."""

        # Define workflow with conditions
        workflow = {
            "start": "anomaly_detection",
            "steps": {
                "anomaly_detection": {
                    "agent": "zumbi",
                    "next": {
                        "condition": "anomalies_found",
                        "true": "security_audit",
                        "false": "generate_report",
                    },
                },
                "security_audit": {
                    "agent": "maria_quiteria",
                    "next": {
                        "condition": "high_risk",
                        "true": "policy_review",
                        "false": "generate_report",
                    },
                },
                "policy_review": {"agent": "bonifacio", "next": "generate_report"},
                "generate_report": {"agent": "tiradentes", "next": None},
            },
        }

        # Execute conditional workflow
        initial_data = {"contract_id": "test-123", "value": 10_000_000}

        execution_path = await orchestrator.execute_conditional_workflow(
            workflow, initial_data, orchestration_context
        )

        # Verify execution followed correct path
        assert len(execution_path) >= 2  # At least start and report
        assert execution_path[0]["step"] == "anomaly_detection"
        assert execution_path[-1]["step"] == "generate_report"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_parallel_map_reduce_pattern(
        self, orchestrator, orchestration_context
    ):
        """Test map-reduce pattern for parallel data processing."""

        # Data to process in parallel
        contracts = [
            {"id": f"contract-{i}", "value": np.random.randint(100_000, 10_000_000)}
            for i in range(5)
        ]

        # Map phase: Process each contract with appropriate agent
        async def process_contract(contract):
            agent = ZumbiAgent()
            message = AgentMessage(
                type="analyze",
                data={"contract_data": contract},
                sender="mapper",
                metadata={"map_task": True},
            )
            return await agent.process(message, orchestration_context)

        # Execute map phase in parallel
        map_results = await asyncio.gather(*[process_contract(c) for c in contracts])

        # Reduce phase: Aggregate results
        aggregator = AnitaAgent()
        reduce_message = AgentMessage(
            type="aggregate_analysis",
            data={
                "individual_results": [r.data for r in map_results],
                "aggregation_type": "anomaly_summary",
            },
            sender="reducer",
            metadata={"reduce_task": True},
        )

        final_result = await aggregator.process(reduce_message, orchestration_context)

        # Verify map-reduce completed
        assert all(r.success for r in map_results)
        assert final_result.success is True
        assert len(map_results) == len(contracts)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_capability_discovery(self, orchestrator):
        """Test dynamic agent capability discovery and registration."""

        # Get all registered agents
        available_agents = await orchestrator.discover_agents()

        # Verify core agents are discovered
        agent_names = [a["name"] for a in available_agents]
        assert "InvestigatorAgent" in agent_names or "zumbi" in agent_names
        assert "MariaQuiteriaAgent" in agent_names or "maria_quiteria" in agent_names
        assert "BonifacioAgent" in agent_names or "bonifacio" in agent_names

        # Test capability search
        security_agents = await orchestrator.find_agents_with_capability(
            "security_audit"
        )
        assert len(security_agents) >= 1
        assert any("maria" in a["name"].lower() for a in security_agents)

        policy_agents = await orchestrator.find_agents_with_capability(
            "policy_analysis"
        )
        assert len(policy_agents) >= 1
        assert any("bonifacio" in a["name"].lower() for a in policy_agents)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_circuit_breaker_pattern(self, orchestrator, orchestration_context):
        """Test circuit breaker pattern for failing agents."""

        agent = MariaQuiteriaAgent()

        # Configure circuit breaker
        orchestrator.configure_circuit_breaker(
            {"failure_threshold": 3, "recovery_timeout": 5, "half_open_requests": 1}
        )

        # Mock agent to fail consistently
        agent.process = AsyncMock(side_effect=Exception("Service unavailable"))

        message = AgentMessage(
            type="security_audit", data={"test": True}, sender="test", metadata={}
        )

        # Attempt multiple requests
        results = []
        for _ in range(5):
            try:
                result = await orchestrator.execute_with_circuit_breaker(
                    agent, message, orchestration_context
                )
                results.append(("success", result))
            except Exception as e:
                results.append(("failure", str(e)))

            await asyncio.sleep(0.1)

        # Circuit should open after threshold
        failures = [r for r in results if r[0] == "failure"]
        assert len(failures) >= 3

        # Later requests should fail fast
        assert any("Circuit breaker open" in r[1] for r in failures[3:])

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_performance_monitoring(
        self, orchestrator, orchestration_context
    ):
        """Test agent performance monitoring and optimization."""

        agents = [ZumbiAgent(), AnitaAgent(), MariaQuiteriaAgent(), BonifacioAgent()]

        # Execute multiple requests and monitor performance
        performance_stats = {}

        for agent in agents:
            stats = {"response_times": [], "success_rate": 0, "total_requests": 10}

            success_count = 0
            for i in range(stats["total_requests"]):
                message = AgentMessage(
                    type="test_performance",
                    data={"iteration": i},
                    sender="performance_monitor",
                    metadata={},
                )

                start_time = datetime.utcnow()
                try:
                    response = await agent.process(message, orchestration_context)
                    if response.success:
                        success_count += 1
                except Exception:  # noqa: S110
                    pass  # Expected failures in performance monitoring

                elapsed = (datetime.utcnow() - start_time).total_seconds()
                stats["response_times"].append(elapsed)

            stats["success_rate"] = success_count / stats["total_requests"]
            stats["avg_response_time"] = np.mean(stats["response_times"])
            stats["p95_response_time"] = np.percentile(stats["response_times"], 95)

            performance_stats[agent.name] = stats

        # Verify performance metrics
        for _, stats in performance_stats.items():
            assert stats["success_rate"] >= 0.9  # 90% success rate
            assert stats["avg_response_time"] < 5  # Under 5 seconds average
            assert stats["p95_response_time"] < 10  # P95 under 10 seconds

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_distributed_transaction_pattern(
        self, orchestrator, orchestration_context
    ):
        """Test distributed transaction pattern with compensation."""

        # Define transaction steps
        transaction_steps = [
            {
                "agent": ZumbiAgent(),
                "action": "reserve_analysis_slot",
                "compensation": "release_analysis_slot",
            },
            {
                "agent": MariaQuiteriaAgent(),
                "action": "allocate_security_resources",
                "compensation": "deallocate_security_resources",
            },
            {
                "agent": BonifacioAgent(),
                "action": "lock_policy_review",
                "compensation": "unlock_policy_review",
            },
        ]

        completed_steps = []

        try:
            # Execute transaction steps
            for step in transaction_steps:
                message = AgentMessage(
                    type=step["action"],
                    data={"transaction_id": "tx-123"},
                    sender="transaction_manager",
                    metadata={"transaction": True},
                )

                response = await step["agent"].process(message, orchestration_context)

                if not response.success:
                    raise Exception(f"Transaction step failed: {step['action']}")

                completed_steps.append(step)

                # Simulate failure on third step
                if len(completed_steps) == 2:
                    raise Exception("Simulated transaction failure")

            # Commit transaction (not reached in this test)
            await orchestrator.commit_transaction("tx-123")

        except Exception:
            # Compensate completed steps in reverse order
            for step in reversed(completed_steps):
                compensation_message = AgentMessage(
                    type=step["compensation"],
                    data={"transaction_id": "tx-123"},
                    sender="transaction_manager",
                    metadata={"compensation": True},
                )

                await step["agent"].process(compensation_message, orchestration_context)

            # Verify compensation occurred
            assert len(completed_steps) == 2  # Two steps completed before failure


class TestOrchestrationPatterns:
    """Test specific orchestration patterns."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_saga_pattern(self, orchestrator, orchestration_context):
        """Test saga pattern for long-running transactions."""

        saga_definition = {
            "name": "investigation_saga",
            "steps": [
                {"service": "anomaly_detection", "agent": "zumbi"},
                {"service": "pattern_analysis", "agent": "anita"},
                {"service": "security_check", "agent": "maria_quiteria"},
                {"service": "policy_review", "agent": "bonifacio"},
                {"service": "report_generation", "agent": "tiradentes"},
            ],
        }

        saga_state = await orchestrator.start_saga(
            saga_definition, {"investigation_id": "saga-123"}, orchestration_context
        )

        # Process saga steps
        while not saga_state["completed"]:
            next_step = saga_state["current_step"]
            if next_step >= len(saga_definition["steps"]):
                break

            step = saga_definition["steps"][next_step]
            saga_state = await orchestrator.execute_saga_step(
                saga_state, step, orchestration_context
            )

        # Verify saga completed
        assert saga_state["completed"] is True
        assert len(saga_state["completed_steps"]) == len(saga_definition["steps"])

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_event_driven_choreography(self, orchestrator, orchestration_context):
        """Test event-driven agent choreography."""

        # Setup event bus
        event_bus = orchestrator.get_event_bus()

        # Register agent event handlers
        agents_triggered = []

        async def on_anomaly_detected(event):
            agents_triggered.append("security_audit")
            await event_bus.emit("security_audit_required", event.data)

        async def on_security_audit_required(event):
            agents_triggered.append("policy_review")
            await event_bus.emit("policy_review_required", event.data)

        async def on_policy_review_required(event):
            agents_triggered.append("report_generation")
            await event_bus.emit("report_ready", event.data)

        event_bus.on("anomaly_detected", on_anomaly_detected)
        event_bus.on("security_audit_required", on_security_audit_required)
        event_bus.on("policy_review_required", on_policy_review_required)

        # Trigger initial event
        await event_bus.emit(
            "anomaly_detected", {"severity": "high", "contract_id": "test-123"}
        )

        # Allow events to propagate
        await asyncio.sleep(0.5)

        # Verify choreography executed
        assert "security_audit" in agents_triggered
        assert "policy_review" in agents_triggered
        assert "report_generation" in agents_triggered
        assert len(agents_triggered) == 3
