"""
Tests for agent lazy loading service
"""

import asyncio
from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from src.agents.deodoro import BaseAgent
from src.core.exceptions import AgentExecutionError
from src.services.agent_lazy_loader import AgentLazyLoader


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    def __init__(self, name: str = "MockAgent"):
        super().__init__()
        self.name = name
        self.initialized = False

    async def initialize(self):
        self.initialized = True

    async def process(self, *args, **kwargs):
        return {"result": "mock"}


class TestAgentLazyLoader:
    """Test agent lazy loader functionality."""

    @pytest_asyncio.fixture
    async def lazy_loader(self):
        """Create a lazy loader instance."""
        loader = AgentLazyLoader(unload_after_minutes=1, max_loaded_agents=3)
        await loader.start()
        yield loader
        await loader.stop()

    @pytest.mark.asyncio
    async def test_register_agent(self, lazy_loader):
        """Test agent registration."""
        # Register a new agent
        lazy_loader.register_agent(
            name="TestAgent",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Test agent",
            capabilities=["testing"],
            priority=5,
            preload=False,
        )

        # Check registration
        assert "TestAgent" in lazy_loader._registry
        metadata = lazy_loader._registry["TestAgent"]
        assert metadata.name == "TestAgent"
        assert metadata.module_path == "tests.unit.test_agent_lazy_loader"
        assert metadata.class_name == "MockAgent"
        assert metadata.description == "Test agent"
        assert metadata.capabilities == ["testing"]
        assert metadata.priority == 5
        assert metadata.preload is False

    @pytest.mark.asyncio
    async def test_get_agent_class_lazy_load(self, lazy_loader):
        """Test lazy loading of agent class."""
        # Register agent
        lazy_loader.register_agent(
            name="TestAgent",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Test agent",
            capabilities=["testing"],
        )

        # Get agent class (should trigger lazy load)
        agent_class = await lazy_loader.get_agent_class("TestAgent")

        # Verify
        assert agent_class == MockAgent
        assert lazy_loader._stats["cache_misses"] == 1
        assert lazy_loader._stats["total_loads"] == 1

        # Get again (should use cache)
        agent_class2 = await lazy_loader.get_agent_class("TestAgent")
        assert agent_class2 == MockAgent
        assert lazy_loader._stats["cache_hits"] == 1

    @pytest.mark.asyncio
    async def test_create_agent_instance(self, lazy_loader):
        """Test creating agent instance."""
        # Register agent
        lazy_loader.register_agent(
            name="TestAgent",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Test agent",
            capabilities=["testing"],
        )

        # Create instance
        agent = await lazy_loader.create_agent("TestAgent")

        # Verify
        assert isinstance(agent, MockAgent)
        assert agent.initialized  # Should be initialized
        assert len(lazy_loader._instances) == 1

    @pytest.mark.asyncio
    async def test_agent_not_found(self, lazy_loader):
        """Test error when agent not found."""
        with pytest.raises(AgentExecutionError) as exc_info:
            await lazy_loader.get_agent_class("NonExistentAgent")

        assert "not registered" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_preload_agents(self, lazy_loader):
        """Test preloading of high-priority agents."""
        # Register agents with different priorities
        lazy_loader.register_agent(
            name="HighPriority",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="High priority agent",
            capabilities=["high"],
            priority=10,
            preload=True,
        )

        lazy_loader.register_agent(
            name="LowPriority",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Low priority agent",
            capabilities=["low"],
            priority=1,
            preload=False,
        )

        # Preload
        await lazy_loader._preload_agents()

        # Check only high priority is loaded
        assert lazy_loader._registry["HighPriority"].loaded_class is not None
        assert lazy_loader._registry["LowPriority"].loaded_class is None

    @pytest.mark.asyncio
    async def test_memory_pressure_unloading(self, lazy_loader):
        """Test unloading agents under memory pressure."""
        lazy_loader.max_loaded_agents = 2

        # Register and load 3 agents
        for i in range(3):
            lazy_loader.register_agent(
                name=f"Agent{i}",
                module_path="tests.unit.test_agent_lazy_loader",
                class_name="MockAgent",
                description=f"Agent {i}",
                capabilities=[f"cap{i}"],
                preload=False,
            )

            # Load with delay to ensure different timestamps
            await lazy_loader.get_agent_class(f"Agent{i}")
            await asyncio.sleep(0.1)

        # Should have unloaded oldest agent
        loaded_count = sum(1 for m in lazy_loader._registry.values() if m.loaded_class)
        assert loaded_count <= 2

    @pytest.mark.asyncio
    async def test_cleanup_unused_agents(self, lazy_loader):
        """Test cleanup of unused agents."""
        # Register and load agent
        lazy_loader.register_agent(
            name="UnusedAgent",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Unused agent",
            capabilities=["unused"],
            preload=False,
        )

        await lazy_loader.get_agent_class("UnusedAgent")

        # Set last used to past
        metadata = lazy_loader._registry["UnusedAgent"]
        metadata.last_used = datetime.now() - timedelta(minutes=2)

        # Run cleanup
        await lazy_loader._cleanup_unused_agents()

        # Should be unloaded
        assert metadata.loaded_class is None
        assert lazy_loader._stats["total_unloads"] == 1

    @pytest.mark.asyncio
    async def test_get_available_agents(self, lazy_loader):
        """Test getting available agents list."""
        # Register some agents
        lazy_loader.register_agent(
            name="Agent1",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Agent 1",
            capabilities=["cap1"],
            priority=10,
        )

        lazy_loader.register_agent(
            name="Agent2",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Agent 2",
            capabilities=["cap2"],
            priority=5,
        )

        # Get available agents
        agents = lazy_loader.get_available_agents()

        # Check sorted by priority
        assert len(agents) >= 2
        assert agents[0]["priority"] >= agents[1]["priority"]

        # Check fields
        agent1 = next(a for a in agents if a["name"] == "Agent1")
        assert agent1["description"] == "Agent 1"
        assert agent1["capabilities"] == ["cap1"]
        assert agent1["priority"] == 10

    @pytest.mark.asyncio
    async def test_get_stats(self, lazy_loader):
        """Test getting loader statistics."""
        # Perform some operations
        lazy_loader.register_agent(
            name="StatsAgent",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Stats agent",
            capabilities=["stats"],
        )

        await lazy_loader.get_agent_class("StatsAgent")
        await lazy_loader.create_agent("StatsAgent")

        # Get stats
        stats = lazy_loader.get_stats()

        # Verify
        assert stats["total_agents"] >= 1
        assert stats["loaded_agents"] >= 1
        assert stats["active_instances"] >= 1
        assert stats["statistics"]["total_loads"] >= 1
        assert stats["memory_usage"]["max_loaded_agents"] == 3

    @pytest.mark.asyncio
    async def test_unload_with_active_instances(self, lazy_loader):
        """Test that agents with active instances are not unloaded."""
        # Register and create agent
        lazy_loader.register_agent(
            name="ActiveAgent",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="MockAgent",
            description="Active agent",
            capabilities=["active"],
        )

        # Create instance (keeps reference)
        agent = await lazy_loader.create_agent("ActiveAgent")

        # Try to unload
        metadata = lazy_loader._registry["ActiveAgent"]
        await lazy_loader._unload_agent(metadata)

        # Should still be loaded due to active instance
        assert metadata.loaded_class is not None

    @pytest.mark.asyncio
    async def test_invalid_module_path(self, lazy_loader):
        """Test loading agent with invalid module path."""
        # Register with invalid module
        lazy_loader.register_agent(
            name="InvalidAgent",
            module_path="invalid.module.path",
            class_name="MockAgent",
            description="Invalid agent",
            capabilities=["invalid"],
        )

        # Should raise error
        with pytest.raises(AgentExecutionError) as exc_info:
            await lazy_loader.get_agent_class("InvalidAgent")

        assert "Failed to load agent" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_class_name(self, lazy_loader):
        """Test loading agent with invalid class name."""
        # Register with invalid class
        lazy_loader.register_agent(
            name="InvalidClass",
            module_path="tests.unit.test_agent_lazy_loader",
            class_name="NonExistentClass",
            description="Invalid class",
            capabilities=["invalid"],
        )

        # Should raise error
        with pytest.raises(AgentExecutionError):
            await lazy_loader.get_agent_class("InvalidClass")


@pytest.mark.asyncio
async def test_global_lazy_loader():
    """Test global lazy loader instance."""
    from src.services.agent_lazy_loader import get_agent_lazy_loader

    # Get instance
    loader = await get_agent_lazy_loader()

    # Should be started
    assert loader._running

    # Should be same instance
    loader2 = await get_agent_lazy_loader()
    assert loader is loader2

    # Cleanup
    await loader.stop()
