"""Unit tests for agent pool management."""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
import uuid

from src.infrastructure.agent_pool import (
    AgentPool,
    AgentPoolConfig,
    AgentInstance,
    AgentHealth,
    PoolMetrics,
    LoadBalancer,
    AgentType
)
from src.agents.deodoro import BaseAgent, AgentStatus, AgentResponse, AgentMessage


class TestAgentInstance:
    """Test agent instance wrapper."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock agent."""
        agent = AsyncMock(spec=BaseAgent)
        agent.agent_id = "test_agent_123"
        agent.name = "Test Agent"
        agent.status = AgentStatus.IDLE
        agent.metrics = {"executions": 0, "errors": 0}
        return agent
    
    def test_agent_instance_creation(self, mock_agent):
        """Test creating agent instance."""
        instance = AgentInstance(
            agent=mock_agent,
            instance_id=str(uuid.uuid4()),
            agent_type=AgentType.INVESTIGATOR
        )
        
        assert instance.agent == mock_agent
        assert instance.agent_type == AgentType.INVESTIGATOR
        assert instance.is_available is True
        assert instance.current_task is None
        assert instance.health == AgentHealth.HEALTHY
    
    @pytest.mark.asyncio
    async def test_agent_instance_health_check(self, mock_agent):
        """Test agent health checking."""
        instance = AgentInstance(
            agent=mock_agent,
            agent_type=AgentType.INVESTIGATOR
        )
        
        # Simulate healthy agent
        mock_agent.health_check = AsyncMock(return_value=True)
        
        health = await instance.check_health()
        assert health == AgentHealth.HEALTHY
        
        # Simulate unhealthy agent
        mock_agent.health_check = AsyncMock(return_value=False)
        
        health = await instance.check_health()
        assert health == AgentHealth.UNHEALTHY
    
    def test_agent_instance_availability(self, mock_agent):
        """Test agent availability tracking."""
        instance = AgentInstance(
            agent=mock_agent,
            agent_type=AgentType.INVESTIGATOR
        )
        
        # Initially available
        assert instance.is_available is True
        
        # Assign task
        instance.assign_task("task_123")
        assert instance.is_available is False
        assert instance.current_task == "task_123"
        
        # Complete task
        instance.complete_task()
        assert instance.is_available is True
        assert instance.current_task is None
        assert instance.tasks_completed == 1


class TestAgentPoolConfig:
    """Test agent pool configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AgentPoolConfig()
        
        assert config.min_agents_per_type == 2
        assert config.max_agents_per_type == 10
        assert config.scale_up_threshold == 0.8
        assert config.scale_down_threshold == 0.2
        assert config.health_check_interval == 60
        assert config.max_retries == 3
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = AgentPoolConfig(
            min_agents_per_type=5,
            max_agents_per_type=20,
            scale_up_threshold=0.7,
            enable_auto_scaling=True
        )
        
        assert config.min_agents_per_type == 5
        assert config.max_agents_per_type == 20
        assert config.scale_up_threshold == 0.7
        assert config.enable_auto_scaling is True


class TestLoadBalancer:
    """Test load balancing strategies."""
    
    @pytest.fixture
    def agents(self):
        """Create test agent instances."""
        agents = []
        for i in range(3):
            agent = AsyncMock()
            agent.agent_id = f"agent_{i}"
            instance = AgentInstance(
                agent=agent,
                instance_id=f"instance_{i}",
                agent_type=AgentType.INVESTIGATOR
            )
            agents.append(instance)
        return agents
    
    def test_round_robin_balancing(self, agents):
        """Test round-robin load balancing."""
        balancer = LoadBalancer(strategy="round_robin")
        
        # Should cycle through agents
        assert balancer.select_agent(agents) == agents[0]
        assert balancer.select_agent(agents) == agents[1]
        assert balancer.select_agent(agents) == agents[2]
        assert balancer.select_agent(agents) == agents[0]  # Back to first
    
    def test_least_loaded_balancing(self, agents):
        """Test least-loaded balancing."""
        balancer = LoadBalancer(strategy="least_loaded")
        
        # Simulate different loads
        agents[0].tasks_completed = 10
        agents[1].tasks_completed = 5
        agents[2].tasks_completed = 15
        
        # Should select least loaded
        selected = balancer.select_agent(agents)
        assert selected == agents[1]
    
    def test_random_balancing(self, agents):
        """Test random load balancing."""
        balancer = LoadBalancer(strategy="random")
        
        # Should select randomly
        selections = [balancer.select_agent(agents) for _ in range(10)]
        
        # Should have some variety
        unique_selections = set(selections)
        assert len(unique_selections) > 1
    
    def test_balancer_skip_unavailable(self, agents):
        """Test balancer skips unavailable agents."""
        balancer = LoadBalancer(strategy="round_robin")
        
        # Make first agent unavailable
        agents[0].is_available = False
        
        # Should skip to next available
        assert balancer.select_agent(agents) == agents[1]


class TestAgentPool:
    """Test agent pool management."""
    
    @pytest.fixture
    def pool_config(self):
        """Create test pool configuration."""
        return AgentPoolConfig(
            min_agents_per_type=2,
            max_agents_per_type=5,
            enable_auto_scaling=True
        )
    
    @pytest.fixture
    def agent_pool(self, pool_config):
        """Create agent pool instance."""
        return AgentPool(config=pool_config)
    
    @pytest.mark.asyncio
    async def test_pool_initialization(self, agent_pool):
        """Test pool initialization with minimum agents."""
        await agent_pool.initialize()
        
        # Should have minimum agents for each type
        for agent_type in AgentType:
            agents = agent_pool._agents[agent_type]
            assert len(agents) >= agent_pool.config.min_agents_per_type
            
            # All should be healthy
            for instance in agents:
                assert instance.health == AgentHealth.HEALTHY
    
    @pytest.mark.asyncio
    async def test_get_agent(self, agent_pool):
        """Test getting an agent from pool."""
        await agent_pool.initialize()
        
        # Get an investigator
        agent = await agent_pool.get_agent(AgentType.INVESTIGATOR)
        
        assert agent is not None
        assert isinstance(agent, BaseAgent)
        
        # Agent should be marked as busy
        instance = agent_pool._find_instance(agent)
        assert instance.is_available is False
    
    @pytest.mark.asyncio
    async def test_return_agent(self, agent_pool):
        """Test returning agent to pool."""
        await agent_pool.initialize()
        
        # Get and return agent
        agent = await agent_pool.get_agent(AgentType.ANALYST)
        await agent_pool.return_agent(agent)
        
        # Should be available again
        instance = agent_pool._find_instance(agent)
        assert instance.is_available is True
        assert instance.tasks_completed == 1
    
    @pytest.mark.asyncio
    async def test_pool_auto_scaling_up(self, agent_pool):
        """Test pool scales up under load."""
        await agent_pool.initialize()
        
        initial_count = len(agent_pool._agents[AgentType.INVESTIGATOR])
        
        # Get all available agents to simulate high load
        agents = []
        for _ in range(initial_count):
            agent = await agent_pool.get_agent(AgentType.INVESTIGATOR)
            agents.append(agent)
        
        # Request one more (should trigger scale up)
        await agent_pool._check_scaling(AgentType.INVESTIGATOR)
        
        # Should have scaled up
        new_count = len(agent_pool._agents[AgentType.INVESTIGATOR])
        assert new_count > initial_count
    
    @pytest.mark.asyncio
    async def test_pool_auto_scaling_down(self, agent_pool):
        """Test pool scales down when underutilized."""
        await agent_pool.initialize()
        
        agent_type = AgentType.REPORTER
        
        # Add extra agents
        for _ in range(3):
            await agent_pool._create_agent(agent_type)
        
        initial_count = len(agent_pool._agents[agent_type])
        
        # Simulate low utilization
        await agent_pool._check_scaling(agent_type)
        
        # Should scale down
        new_count = len(agent_pool._agents[agent_type])
        assert new_count < initial_count
        assert new_count >= agent_pool.config.min_agents_per_type
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, agent_pool):
        """Test health monitoring and recovery."""
        await agent_pool.initialize()
        
        # Make an agent unhealthy
        unhealthy_instance = agent_pool._agents[AgentType.INVESTIGATOR][0]
        unhealthy_instance.health = AgentHealth.UNHEALTHY
        unhealthy_instance.agent.health_check = AsyncMock(return_value=False)
        
        # Run health check
        await agent_pool.health_check()
        
        # Unhealthy agent should be replaced
        agents = agent_pool._agents[AgentType.INVESTIGATOR]
        assert unhealthy_instance not in agents
        assert all(a.health == AgentHealth.HEALTHY for a in agents)
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_requests(self, agent_pool):
        """Test handling concurrent agent requests."""
        await agent_pool.initialize()
        
        # Request multiple agents concurrently
        tasks = []
        for _ in range(10):
            task = asyncio.create_task(
                agent_pool.get_agent(AgentType.INVESTIGATOR)
            )
            tasks.append(task)
        
        agents = await asyncio.gather(*tasks)
        
        # All should be valid agents
        assert len(agents) == 10
        assert all(agent is not None for agent in agents)
        
        # No duplicates
        agent_ids = [a.agent_id for a in agents]
        assert len(set(agent_ids)) == len(agent_ids)
    
    @pytest.mark.asyncio
    async def test_pool_metrics(self, agent_pool):
        """Test pool metrics collection."""
        await agent_pool.initialize()
        
        # Perform operations
        agent1 = await agent_pool.get_agent(AgentType.INVESTIGATOR)
        agent2 = await agent_pool.get_agent(AgentType.ANALYST)
        await agent_pool.return_agent(agent1)
        
        metrics = agent_pool.get_metrics()
        
        assert metrics.total_agents > 0
        assert metrics.available_agents > 0
        assert metrics.busy_agents >= 1  # agent2 still busy
        assert metrics.tasks_completed >= 1
        assert AgentType.INVESTIGATOR in metrics.agents_by_type
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, agent_pool):
        """Test graceful pool shutdown."""
        await agent_pool.initialize()
        
        # Get some agents
        agent1 = await agent_pool.get_agent(AgentType.INVESTIGATOR)
        agent2 = await agent_pool.get_agent(AgentType.ANALYST)
        
        # Start shutdown
        await agent_pool.shutdown(graceful=True)
        
        # Should wait for agents to complete
        assert agent_pool._shutting_down is True
        
        # Return agents
        await agent_pool.return_agent(agent1)
        await agent_pool.return_agent(agent2)
        
        # Complete shutdown
        await agent_pool.shutdown(graceful=False)
        
        # Pool should be empty
        for agent_type in AgentType:
            assert len(agent_pool._agents[agent_type]) == 0


class TestAgentPoolRecovery:
    """Test agent pool recovery scenarios."""
    
    @pytest.fixture
    def recovery_pool(self):
        """Create pool with recovery features."""
        config = AgentPoolConfig(
            min_agents_per_type=2,
            max_retries=3,
            enable_circuit_breaker=True
        )
        return AgentPool(config=config)
    
    @pytest.mark.asyncio
    async def test_agent_crash_recovery(self, recovery_pool):
        """Test recovery from agent crashes."""
        await recovery_pool.initialize()
        
        # Get agent and simulate crash
        agent = await recovery_pool.get_agent(AgentType.INVESTIGATOR)
        
        # Simulate agent crash during execution
        agent.execute = AsyncMock(side_effect=Exception("Agent crashed"))
        
        # Try to use crashed agent
        message = AgentMessage(
            sender="test",
            recipient=agent.agent_id,
            action="test"
        )
        
        with pytest.raises(Exception):
            await agent.execute(message)
        
        # Return crashed agent
        await recovery_pool.return_agent(agent, failed=True)
        
        # Pool should mark agent as unhealthy
        instance = recovery_pool._find_instance(agent)
        assert instance.health == AgentHealth.UNHEALTHY
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self, recovery_pool):
        """Test circuit breaker pattern."""
        await recovery_pool.initialize()
        
        agent_type = AgentType.INVESTIGATOR
        
        # Simulate multiple failures
        for _ in range(5):
            agent = await recovery_pool.get_agent(agent_type)
            await recovery_pool.return_agent(agent, failed=True)
        
        # Circuit should be open
        assert recovery_pool._circuit_breakers[agent_type].is_open
        
        # Should not provide agents when circuit is open
        with pytest.raises(Exception) as exc_info:
            await recovery_pool.get_agent(agent_type)
        assert "Circuit breaker open" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_retry_with_different_agent(self, recovery_pool):
        """Test retry logic with different agents."""
        await recovery_pool.initialize()
        
        # Create custom retry handler
        async def retry_operation():
            attempts = 0
            max_attempts = recovery_pool.config.max_retries
            
            while attempts < max_attempts:
                agent = await recovery_pool.get_agent(AgentType.INVESTIGATOR)
                try:
                    if attempts < 2:
                        # Simulate failure
                        raise Exception("Operation failed")
                    else:
                        # Success on third attempt
                        return "Success"
                except Exception:
                    await recovery_pool.return_agent(agent, failed=True)
                    attempts += 1
            
            return None
        
        result = await retry_operation()
        assert result == "Success"