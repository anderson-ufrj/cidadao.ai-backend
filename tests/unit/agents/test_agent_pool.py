"""
Unit tests for agent pool system.
Tests pooling, lifecycle management, and resource optimization.
"""

import asyncio

import pytest

from src.agents.simple_agent_pool import AgentPool, AgentPoolEntry
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
)


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    def __init__(self):
        super().__init__(
            name="MockAgent",
            description="Test agent",
            capabilities=["test"],
            max_retries=3,
            timeout=30,
        )
        self.initialized = False
        self.cleaned_up = False
        self.process_count = 0

    async def initialize(self) -> None:
        """Initialize agent."""
        self.initialized = True
        await asyncio.sleep(0.01)  # Simulate initialization work

    async def shutdown(self) -> None:
        """Shutdown agent."""
        self.cleaned_up = True

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """Process message."""
        self.process_count += 1
        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            result={"processed": True},
        )

    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        self.cleaned_up = True


class SlowMockAgent(MockAgent):
    """Slow mock agent for testing timeouts."""

    async def initialize(self) -> None:
        """Slow initialization."""
        await asyncio.sleep(0.5)
        self.initialized = True


@pytest.fixture
async def agent_pool():
    """Create an agent pool for testing."""
    pool = AgentPool(
        min_size=1,
        max_size=3,
        idle_timeout=1,  # 1 second for faster tests
        max_agent_lifetime=10,  # 10 seconds for tests
    )
    await pool.start()
    yield pool
    await pool.stop()


@pytest.fixture
def agent_context():
    """Create agent context for testing."""
    return AgentContext(
        investigation_id="test-pool-123",
        user_id="test_user",
        session_id="test_session",
        metadata={"test": True},
    )


class TestAgentPoolEntry:
    """Test AgentPoolEntry class."""

    @pytest.mark.unit
    def test_entry_initialization(self):
        """Test pool entry initialization."""
        agent = MockAgent()
        entry = AgentPoolEntry(agent)

        assert entry.agent == agent
        assert not entry.in_use
        assert entry.usage_count == 0
        assert entry.idle_time < 1  # Just created

    @pytest.mark.unit
    async def test_entry_acquire_release(self):
        """Test acquiring and releasing agents."""
        agent = MockAgent()
        entry = AgentPoolEntry(agent)

        # Acquire agent
        acquired_agent = await entry.acquire()
        assert acquired_agent == agent
        assert entry.in_use
        assert entry.usage_count == 1

        # Try to acquire again (should fail)
        with pytest.raises(RuntimeError, match="Agent already in use"):
            await entry.acquire()

        # Release agent
        await entry.release()
        assert not entry.in_use
        assert entry.usage_count == 1  # Usage count doesn't decrease

        # Can acquire again
        acquired_agent2 = await entry.acquire()
        assert acquired_agent2 == agent
        assert entry.usage_count == 2


class TestAgentPool:
    """Test AgentPool class."""

    @pytest.mark.unit
    async def test_pool_initialization(self):
        """Test agent pool initialization."""
        pool = AgentPool(min_size=2, max_size=5)

        assert pool.min_size == 2
        assert pool.max_size == 5
        assert pool.idle_timeout == 300
        assert pool.max_agent_lifetime == 3600
        assert not pool._running

        # Start pool
        await pool.start()
        assert pool._running
        assert pool._cleanup_task is not None

        # Stop pool
        await pool.stop()
        assert not pool._running

    @pytest.mark.unit
    async def test_acquire_and_release(self, agent_pool, agent_context):
        """Test acquiring and releasing agents from pool."""
        # First acquisition - should create new agent
        async with agent_pool.acquire(MockAgent, agent_context) as agent:
            assert isinstance(agent, MockAgent)
            assert agent.initialized
            assert agent.context == agent_context

        # After release, context should be cleared
        assert agent.context is None

        # Check statistics
        assert agent_pool._stats["created"] == 1
        assert agent_pool._stats["reused"] == 0

        # Second acquisition - should reuse agent
        async with agent_pool.acquire(MockAgent, agent_context) as agent2:
            assert isinstance(agent2, MockAgent)
            # Should be the same agent instance
            assert agent2 == agent

        # Check statistics
        assert agent_pool._stats["created"] == 1
        assert agent_pool._stats["reused"] == 1

    @pytest.mark.unit
    async def test_pool_max_size_limit(self, agent_pool, agent_context):
        """Test pool respects max size limit."""
        agent_pool.max_size = 2

        # Acquire two agents
        async with agent_pool.acquire(MockAgent, agent_context) as agent1:
            async with agent_pool.acquire(MockAgent, agent_context) as agent2:
                assert agent1 != agent2
                assert agent_pool._stats["created"] == 2

                # Try to acquire third agent - should wait
                acquire_task = asyncio.create_task(
                    agent_pool._get_or_create_agent(MockAgent)
                )

                # Give it some time
                await asyncio.sleep(0.1)

                # Task should still be running (waiting)
                assert not acquire_task.done()

                # Cancel the waiting task
                acquire_task.cancel()
                try:
                    await acquire_task
                except asyncio.CancelledError:
                    pass

    @pytest.mark.unit
    async def test_multiple_agent_types(self, agent_pool, agent_context):
        """Test pool handles multiple agent types."""
        # Create agents of different types
        async with agent_pool.acquire(MockAgent, agent_context) as mock_agent:
            assert isinstance(mock_agent, MockAgent)

        async with agent_pool.acquire(SlowMockAgent, agent_context) as slow_agent:
            assert isinstance(slow_agent, SlowMockAgent)

        # Check separate pools
        assert len(agent_pool._pools) == 2
        assert MockAgent in agent_pool._pools
        assert SlowMockAgent in agent_pool._pools
        assert len(agent_pool._pools[MockAgent]) == 1
        assert len(agent_pool._pools[SlowMockAgent]) == 1

    @pytest.mark.unit
    async def test_cleanup_idle_agents(self, agent_context):
        """Test cleanup of idle agents."""
        # Create pool with short idle timeout
        pool = AgentPool(idle_timeout=0.5, max_agent_lifetime=10)
        await pool.start()

        try:
            # Create and release an agent
            async with pool.acquire(MockAgent, agent_context) as agent:
                pass

            # Check agent exists in pool
            assert len(pool._pools[MockAgent]) == 1

            # Wait for cleanup
            await asyncio.sleep(1.0)

            # Force cleanup cycle
            await pool._cleanup_idle_agents()

            # Agent should be removed due to idle timeout
            assert len(pool._pools[MockAgent]) == 0
            assert pool._stats["evicted"] == 1

        finally:
            await pool.stop()

    @pytest.mark.unit
    async def test_cleanup_old_agents(self, agent_context):
        """Test cleanup of agents exceeding lifetime."""
        # Create pool with short lifetime
        pool = AgentPool(idle_timeout=60, max_agent_lifetime=0.5)
        await pool.start()

        try:
            # Create and release an agent
            async with pool.acquire(MockAgent, agent_context) as agent:
                pass

            # Check agent exists in pool
            assert len(pool._pools[MockAgent]) == 1

            # Wait for agent to exceed lifetime
            await asyncio.sleep(0.6)

            # Force cleanup cycle
            await pool._cleanup_idle_agents()

            # Agent should be removed due to lifetime
            assert len(pool._pools[MockAgent]) == 0
            assert pool._stats["evicted"] == 1

        finally:
            await pool.stop()

    @pytest.mark.unit
    async def test_prewarm_pool(self, agent_context):
        """Test pre-warming the agent pool."""
        pool = AgentPool(min_size=3, max_size=5)
        await pool.start()

        try:
            # Pre-warm pool for MockAgent
            await pool.prewarm([MockAgent])

            # Should have created min_size agents
            assert len(pool._pools[MockAgent]) == 3
            assert pool._stats["created"] == 3

            # All agents should be initialized but not in use
            for entry in pool._pools[MockAgent]:
                assert entry.agent.initialized
                assert not entry.in_use

        finally:
            await pool.stop()

    @pytest.mark.unit
    async def test_get_stats(self, agent_pool, agent_context):
        """Test getting pool statistics."""
        # Create some activity
        async with agent_pool.acquire(MockAgent, agent_context) as agent1:
            pass
        async with agent_pool.acquire(MockAgent, agent_context) as agent2:
            pass

        stats = agent_pool.get_stats()

        assert "global_stats" in stats
        assert stats["global_stats"]["created"] == 1
        assert stats["global_stats"]["reused"] == 1
        assert stats["global_stats"]["evicted"] == 0
        assert stats["global_stats"]["errors"] == 0
        assert "pools" in stats
        assert "MockAgent" in stats["pools"]
        assert stats["pools"]["MockAgent"]["total"] == 1
        assert stats["pools"]["MockAgent"]["in_use"] == 0
        assert stats["pools"]["MockAgent"]["available"] == 1
        assert stats["total_agents"] == 1

    @pytest.mark.unit
    async def test_error_handling(self, agent_context):
        """Test error handling in agent creation."""

        class ErrorAgent(BaseAgent):
            """Agent that fails to initialize."""

            def __init__(self):
                raise ValueError("Initialization error")

            async def initialize(self) -> None:
                pass

            async def shutdown(self) -> None:
                pass

            async def process(self, message, context):
                pass

        pool = AgentPool()
        await pool.start()

        try:
            # Should raise error when trying to create agent
            with pytest.raises(ValueError, match="Initialization error"):
                await pool._create_agent(ErrorAgent)

            # Check error statistics
            assert pool._stats["errors"] == 1

        finally:
            await pool.stop()

    @pytest.mark.unit
    async def test_concurrent_access(self, agent_pool, agent_context):
        """Test concurrent access to the pool."""

        async def acquire_and_process(pool, context, results: list):
            """Acquire agent and do some work."""
            async with pool.acquire(MockAgent, context) as agent:
                await asyncio.sleep(0.01)  # Simulate work
                results.append(agent.process_count)
                await agent.process(
                    AgentMessage(
                        sender="test", recipient="MockAgent", action="test", payload={}
                    ),
                    context,
                )
                results.append(agent.process_count)

        # Run multiple concurrent acquisitions
        results = []
        tasks = [
            acquire_and_process(agent_pool, agent_context, results) for _ in range(5)
        ]

        await asyncio.gather(*tasks)

        # Check all tasks completed
        assert len(results) == 10  # 2 results per task

        # Check pool created appropriate number of agents
        # (max 3 due to pool limit)
        assert len(agent_pool._pools[MockAgent]) <= 3
        assert agent_pool._stats["created"] <= 3
        assert agent_pool._stats["reused"] >= 2  # At least some reuse


class TestGlobalAgentPool:
    """Test global agent pool functions."""

    @pytest.mark.unit
    async def test_get_agent_pool(self):
        """Test getting the global agent pool instance."""
        from src.agents.simple_agent_pool import agent_pool as global_pool
        from src.agents.simple_agent_pool import get_agent_pool

        # Get pool instance
        pool = await get_agent_pool()

        # Should return the global instance
        assert pool is global_pool

        # Should be properly initialized
        assert isinstance(pool, AgentPool)

    @pytest.mark.unit
    async def test_maintain_minimum_pool(self):
        """Test maintaining minimum pool size."""
        pool = AgentPool(min_size=2, max_size=5)
        await pool.start()

        try:
            # Pre-warm with agents
            await pool.prewarm([MockAgent])
            assert len(pool._pools[MockAgent]) == 2

            # Manually remove an agent (simulate eviction)
            pool._pools[MockAgent].pop()
            assert len(pool._pools[MockAgent]) == 1

            # Run maintain minimum
            await pool._maintain_minimum_pool()

            # Should have restored to minimum
            assert len(pool._pools[MockAgent]) == 2

        finally:
            await pool.stop()
