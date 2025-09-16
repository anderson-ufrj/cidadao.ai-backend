"""Unit tests for infrastructure components."""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from src.infrastructure.monitoring import (
    MetricsCollector,
    HealthChecker,
    PerformanceMonitor,
    ResourceMonitor,
    AlertManager
)
from src.infrastructure.database import (
    DatabasePool,
    ConnectionManager,
    TransactionManager,
    QueryOptimizer
)
from src.infrastructure.message_queue import (
    MessageQueue,
    MessageBroker,
    EventBus,
    MessagePriority
)
from src.infrastructure.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerConfig
)
from src.infrastructure.retry import (
    RetryPolicy,
    ExponentialBackoff,
    RetryManager
)


class TestMetricsCollector:
    """Test metrics collection system."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector instance."""
        return MetricsCollector()
    
    def test_counter_metric(self, metrics_collector):
        """Test counter metric collection."""
        # Increment counter
        metrics_collector.increment("api_requests_total", labels={"endpoint": "/health"})
        metrics_collector.increment("api_requests_total", labels={"endpoint": "/health"})
        metrics_collector.increment("api_requests_total", labels={"endpoint": "/api/v1/users"})
        
        # Get metric value
        value = metrics_collector.get_metric_value(
            "api_requests_total",
            labels={"endpoint": "/health"}
        )
        
        assert value == 2
    
    def test_gauge_metric(self, metrics_collector):
        """Test gauge metric collection."""
        # Set gauge values
        metrics_collector.set_gauge("active_connections", 10)
        metrics_collector.set_gauge("active_connections", 15)
        metrics_collector.set_gauge("active_connections", 12)
        
        value = metrics_collector.get_metric_value("active_connections")
        assert value == 12
    
    def test_histogram_metric(self, metrics_collector):
        """Test histogram metric collection."""
        # Record durations
        durations = [0.1, 0.2, 0.15, 0.3, 0.25, 0.4, 0.2, 0.18]
        
        for duration in durations:
            metrics_collector.record_duration(
                "request_duration_seconds",
                duration,
                labels={"method": "GET"}
            )
        
        stats = metrics_collector.get_histogram_stats("request_duration_seconds")
        
        assert stats["count"] == len(durations)
        assert 0.1 <= stats["mean"] <= 0.3
        assert stats["p50"] > 0  # Median
        assert stats["p95"] > stats["p50"]  # 95th percentile > median
    
    def test_metric_labels(self, metrics_collector):
        """Test metric labeling."""
        # Same metric with different labels
        metrics_collector.increment("errors_total", labels={"type": "database"})
        metrics_collector.increment("errors_total", labels={"type": "api"})
        metrics_collector.increment("errors_total", labels={"type": "api"})
        
        db_errors = metrics_collector.get_metric_value(
            "errors_total",
            labels={"type": "database"}
        )
        api_errors = metrics_collector.get_metric_value(
            "errors_total",
            labels={"type": "api"}
        )
        
        assert db_errors == 1
        assert api_errors == 2


class TestHealthChecker:
    """Test health checking system."""
    
    @pytest.fixture
    def health_checker(self):
        """Create health checker instance."""
        return HealthChecker()
    
    @pytest.mark.asyncio
    async def test_component_health_check(self, health_checker):
        """Test individual component health checks."""
        # Register health check functions
        async def database_check():
            return {"status": "healthy", "latency_ms": 5}
        
        async def redis_check():
            return {"status": "healthy", "latency_ms": 2}
        
        health_checker.register_check("database", database_check)
        health_checker.register_check("redis", redis_check)
        
        # Run health checks
        results = await health_checker.check_all()
        
        assert results["status"] == "healthy"
        assert results["components"]["database"]["status"] == "healthy"
        assert results["components"]["redis"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_unhealthy_component(self, health_checker):
        """Test handling unhealthy components."""
        async def failing_check():
            raise Exception("Connection failed")
        
        async def healthy_check():
            return {"status": "healthy"}
        
        health_checker.register_check("failing_service", failing_check)
        health_checker.register_check("healthy_service", healthy_check)
        
        results = await health_checker.check_all()
        
        assert results["status"] == "degraded"
        assert results["components"]["failing_service"]["status"] == "unhealthy"
        assert results["components"]["healthy_service"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_timeout(self, health_checker):
        """Test health check timeout handling."""
        async def slow_check():
            await asyncio.sleep(10)  # Longer than timeout
            return {"status": "healthy"}
        
        health_checker.register_check("slow_service", slow_check, timeout=1)
        
        results = await health_checker.check_all()
        
        assert results["components"]["slow_service"]["status"] == "timeout"
        assert results["status"] == "degraded"


class TestPerformanceMonitor:
    """Test performance monitoring."""
    
    @pytest.fixture
    def perf_monitor(self):
        """Create performance monitor instance."""
        return PerformanceMonitor()
    
    @pytest.mark.asyncio
    async def test_operation_timing(self, perf_monitor):
        """Test timing operations."""
        async with perf_monitor.measure("database_query"):
            await asyncio.sleep(0.1)
        
        async with perf_monitor.measure("api_call"):
            await asyncio.sleep(0.05)
        
        stats = perf_monitor.get_stats()
        
        assert "database_query" in stats
        assert stats["database_query"]["count"] == 1
        assert stats["database_query"]["avg_duration"] >= 0.1
        
        assert "api_call" in stats
        assert stats["api_call"]["avg_duration"] >= 0.05
    
    def test_throughput_calculation(self, perf_monitor):
        """Test throughput calculation."""
        # Record multiple operations
        for _ in range(100):
            perf_monitor.record_operation("process_request")
        
        # Calculate throughput
        throughput = perf_monitor.calculate_throughput("process_request", window_seconds=1)
        
        assert throughput > 0
        assert throughput <= 100  # Can't be more than recorded


class TestCircuitBreaker:
    """Test circuit breaker pattern."""
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker instance."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=5,
            expected_exception=Exception
        )
        return CircuitBreaker("test_service", config)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self, circuit_breaker):
        """Test circuit breaker in closed (normal) state."""
        async def success_operation():
            return "success"
        
        result = await circuit_breaker.call(success_operation)
        
        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self, circuit_breaker):
        """Test circuit breaker opens after threshold failures."""
        async def failing_operation():
            raise Exception("Operation failed")
        
        # Fail multiple times
        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.state == CircuitState.OPEN
        assert circuit_breaker.failure_count == 3
        
        # Should reject calls when open
        with pytest.raises(Exception) as exc_info:
            await circuit_breaker.call(failing_operation)
        assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self, circuit_breaker):
        """Test circuit breaker recovery through half-open state."""
        # Open the circuit
        circuit_breaker.state = CircuitState.OPEN
        circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=10)
        
        async def success_operation():
            return "recovered"
        
        # Should enter half-open and try operation
        result = await circuit_breaker.call(success_operation)
        
        assert result == "recovered"
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0


class TestRetryPolicy:
    """Test retry policies and backoff strategies."""
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        backoff = ExponentialBackoff(
            initial_delay=1,
            max_delay=60,
            multiplier=2
        )
        
        # Calculate delays for successive retries
        delays = [backoff.get_delay(i) for i in range(5)]
        
        assert delays[0] == 1  # Initial delay
        assert delays[1] == 2  # 1 * 2
        assert delays[2] == 4  # 2 * 2
        assert delays[3] == 8  # 4 * 2
        assert delays[4] == 16  # 8 * 2
        
        # Test max delay cap
        delay_10 = backoff.get_delay(10)
        assert delay_10 == 60  # Capped at max_delay
    
    @pytest.mark.asyncio
    async def test_retry_manager(self):
        """Test retry manager with policy."""
        policy = RetryPolicy(
            max_attempts=3,
            backoff=ExponentialBackoff(initial_delay=0.1),
            retryable_exceptions=(ValueError,)
        )
        
        retry_manager = RetryManager(policy)
        
        attempt_count = 0
        
        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = await retry_manager.execute(flaky_operation)
        
        assert result == "success"
        assert attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_with_non_retryable_exception(self):
        """Test retry skips non-retryable exceptions."""
        policy = RetryPolicy(
            max_attempts=3,
            retryable_exceptions=(ValueError,)
        )
        
        retry_manager = RetryManager(policy)
        
        async def failing_operation():
            raise TypeError("Non-retryable error")
        
        with pytest.raises(TypeError):
            await retry_manager.execute(failing_operation)


class TestDatabasePool:
    """Test database connection pooling."""
    
    @pytest.fixture
    def db_pool(self):
        """Create database pool instance."""
        return DatabasePool(
            min_size=2,
            max_size=10,
            max_idle_time=300
        )
    
    @pytest.mark.asyncio
    async def test_connection_acquisition(self, db_pool):
        """Test getting connections from pool."""
        # Mock connection
        mock_conn = AsyncMock()
        mock_conn.is_closed.return_value = False
        
        with patch.object(db_pool, '_create_connection', return_value=mock_conn):
            # Get connection
            async with db_pool.acquire() as conn:
                assert conn is not None
                assert conn == mock_conn
            
            # Connection should be returned to pool
            assert db_pool.size > 0
    
    @pytest.mark.asyncio
    async def test_connection_pool_limits(self, db_pool):
        """Test pool size limits."""
        connections = []
        
        # Mock connection creation
        with patch.object(db_pool, '_create_connection') as mock_create:
            mock_create.return_value = AsyncMock()
            
            # Acquire max connections
            for _ in range(10):
                conn = await db_pool.acquire()
                connections.append(conn)
            
            assert db_pool.size == 10  # Max size
            
            # Try to acquire one more (should wait or fail)
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(db_pool.acquire(), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_connection_health_check(self, db_pool):
        """Test connection health checking."""
        # Create healthy and unhealthy connections
        healthy_conn = AsyncMock()
        healthy_conn.is_closed.return_value = False
        healthy_conn.ping.return_value = True
        
        unhealthy_conn = AsyncMock()
        unhealthy_conn.is_closed.return_value = True
        
        db_pool._connections = [healthy_conn, unhealthy_conn]
        
        # Run health check
        await db_pool.health_check()
        
        # Unhealthy connection should be removed
        assert unhealthy_conn not in db_pool._connections
        assert healthy_conn in db_pool._connections


class TestMessageQueue:
    """Test message queue system."""
    
    @pytest.fixture
    def message_queue(self):
        """Create message queue instance."""
        return MessageQueue()
    
    @pytest.mark.asyncio
    async def test_message_publish_subscribe(self, message_queue):
        """Test pub/sub functionality."""
        received_messages = []
        
        async def handler(message):
            received_messages.append(message)
        
        # Subscribe to topic
        await message_queue.subscribe("test.topic", handler)
        
        # Publish messages
        await message_queue.publish("test.topic", {"data": "message1"})
        await message_queue.publish("test.topic", {"data": "message2"})
        
        # Allow time for processing
        await asyncio.sleep(0.1)
        
        assert len(received_messages) == 2
        assert received_messages[0]["data"] == "message1"
        assert received_messages[1]["data"] == "message2"
    
    @pytest.mark.asyncio
    async def test_message_priority_queue(self, message_queue):
        """Test priority message processing."""
        processed_order = []
        
        async def handler(message):
            processed_order.append(message["id"])
        
        await message_queue.subscribe("priority.topic", handler)
        
        # Publish with different priorities
        await message_queue.publish(
            "priority.topic",
            {"id": "low", "data": "low priority"},
            priority=MessagePriority.LOW
        )
        await message_queue.publish(
            "priority.topic",
            {"id": "high", "data": "high priority"},
            priority=MessagePriority.HIGH
        )
        await message_queue.publish(
            "priority.topic",
            {"id": "medium", "data": "medium priority"},
            priority=MessagePriority.MEDIUM
        )
        
        # Process queue
        await message_queue.process_priority_queue()
        
        # High priority should be processed first
        assert processed_order[0] == "high"
        assert processed_order[-1] == "low"
    
    @pytest.mark.asyncio
    async def test_message_persistence(self, message_queue):
        """Test message persistence for reliability."""
        # Enable persistence
        message_queue.enable_persistence(True)
        
        # Publish message
        message_id = await message_queue.publish(
            "persistent.topic",
            {"important": "data"},
            persistent=True
        )
        
        # Simulate failure before processing
        # Message should be recoverable
        recovered = await message_queue.recover_messages()
        
        assert len(recovered) > 0
        assert any(msg["id"] == message_id for msg in recovered)