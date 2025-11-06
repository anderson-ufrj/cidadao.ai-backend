"""
Performance tests for agent system.
Tests agent response times, throughput, and resource usage.
"""

import asyncio
import statistics
import time

import numpy as np
import psutil
import pytest

from src.agents import (
    AgentContext,
    AgentMessage,
    AnitaAgent,
    BonifacioAgent,
    MariaQuiteriaAgent,
    TiradentesAgent,
    ZumbiAgent,
)
from src.infrastructure.agent_pool import AgentPool


class TestAgentPerformance:
    """Performance tests for individual agents."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_response_times(self):
        """Test response times for all agents."""
        agents = [
            ("zumbi", ZumbiAgent()),
            ("anita", AnitaAgent()),
            ("tiradentes", TiradentesAgent()),
            ("bonifacio", BonifacioAgent()),
            ("maria_quiteria", MariaQuiteriaAgent()),
        ]

        context = AgentContext(
            investigation_id="perf-test",
            user_id="perf-tester",
            session_id="perf-session",
        )

        results = {}

        for agent_name, agent in agents:
            response_times = []

            # Warm up
            message = AgentMessage(
                type="test",
                data={"test": True},
                sender="performance_tester",
                metadata={},
            )
            await agent.process(message, context)

            # Measure response times
            for i in range(20):
                start = time.time()

                message = AgentMessage(
                    type="analyze",
                    data={
                        "iteration": i,
                        "data": {"value": np.random.randint(1000, 1000000)},
                    },
                    sender="performance_tester",
                    metadata={"test_run": i},
                )

                await agent.process(message, context)

                end = time.time()
                response_time = (end - start) * 1000  # Convert to milliseconds
                response_times.append(response_time)

            results[agent_name] = {
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": np.percentile(response_times, 95),
                "p99": np.percentile(response_times, 99),
                "min": min(response_times),
                "max": max(response_times),
            }

        # Verify performance targets
        for agent_name, metrics in results.items():
            assert metrics["mean"] < 2000  # Mean under 2 seconds
            assert metrics["p95"] < 3000  # P95 under 3 seconds
            assert metrics["p99"] < 5000  # P99 under 5 seconds

            print(f"\n{agent_name} Performance:")
            print(f"  Mean: {metrics['mean']:.2f}ms")
            print(f"  P95: {metrics['p95']:.2f}ms")
            print(f"  P99: {metrics['p99']:.2f}ms")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """Test agent performance under concurrent load."""
        agent = ZumbiAgent()
        context = AgentContext(
            investigation_id="concurrent-test",
            user_id="concurrent-tester",
            session_id="concurrent-session",
        )

        async def process_request(request_id):
            message = AgentMessage(
                type="analyze",
                data={
                    "request_id": request_id,
                    "contract_value": np.random.randint(100000, 10000000),
                },
                sender="load_tester",
                metadata={"concurrent": True},
            )

            start = time.time()
            response = await agent.process(message, context)
            elapsed = time.time() - start

            return {
                "request_id": request_id,
                "success": response.success,
                "response_time": elapsed,
            }

        # Test with different concurrency levels
        concurrency_levels = [1, 5, 10, 20]
        results = {}

        for concurrency in concurrency_levels:
            tasks = [process_request(f"req-{i}") for i in range(concurrency * 10)]

            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            total_time = time.time() - start_time

            success_rate = sum(1 for r in responses if r["success"]) / len(responses)
            avg_response_time = statistics.mean(r["response_time"] for r in responses)
            throughput = len(responses) / total_time

            results[concurrency] = {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "throughput": throughput,
                "total_requests": len(responses),
            }

        # Verify performance doesn't degrade significantly
        for concurrency, metrics in results.items():
            assert metrics["success_rate"] >= 0.95  # 95% success rate
            assert metrics["avg_response_time"] < 5  # Under 5 seconds

            print(f"\nConcurrency {concurrency}:")
            print(f"  Success Rate: {metrics['success_rate']:.2%}")
            print(f"  Avg Response: {metrics['avg_response_time']:.2f}s")
            print(f"  Throughput: {metrics['throughput']:.2f} req/s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_pool_performance(self):
        """Test agent pool initialization and management performance."""
        pool = AgentPool(min_instances=1, max_instances=10, idle_timeout=60)

        await pool.initialize()

        # Measure pool scaling performance
        scaling_times = []

        for _i in range(5):
            start = time.time()

            # Request multiple agents to trigger scaling
            agents = await asyncio.gather(*[pool.get_agent("zumbi") for _ in range(5)])

            scaling_time = time.time() - start
            scaling_times.append(scaling_time)

            # Return agents to pool
            for agent in agents:
                await pool.return_agent(agent)

        # Verify pool performance
        avg_scaling_time = statistics.mean(scaling_times)
        assert avg_scaling_time < 1.0  # Scaling should be fast

        stats = await pool.get_stats()
        assert stats["total_instances"] <= 10  # Respects max instances
        assert stats["cache_hit_rate"] > 0.5  # Good cache utilization

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage patterns under sustained load."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        agents = [ZumbiAgent(), MariaQuiteriaAgent(), BonifacioAgent()]

        context = AgentContext(
            investigation_id="memory-test",
            user_id="memory-tester",
            session_id="memory-session",
        )

        # Generate sustained load
        memory_samples = []

        for iteration in range(10):
            # Process batch of requests
            tasks = []
            for agent in agents:
                for i in range(20):
                    message = AgentMessage(
                        type="analyze",
                        data={
                            "iteration": iteration,
                            "request": i,
                            "large_data": "x" * 10000,  # 10KB payload
                        },
                        sender="memory_tester",
                        metadata={},
                    )
                    tasks.append(agent.process(message, context))

            await asyncio.gather(*tasks)

            # Sample memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_samples.append(current_memory)

            # Allow garbage collection
            await asyncio.sleep(0.1)

        # Analyze memory usage
        memory_increase = max(memory_samples) - initial_memory
        memory_variance = statistics.variance(memory_samples)

        # Verify no significant memory leaks
        assert memory_increase < 500  # Less than 500MB increase
        assert memory_variance < 10000  # Stable memory usage

        print("\nMemory Usage:")
        print(f"  Initial: {initial_memory:.2f}MB")
        print(f"  Peak: {max(memory_samples):.2f}MB")
        print(f"  Increase: {memory_increase:.2f}MB")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_startup_times(self):
        """Test agent initialization and startup times."""
        agent_classes = [
            ("zumbi", ZumbiAgent),
            ("anita", AnitaAgent),
            ("tiradentes", TiradentesAgent),
            ("bonifacio", BonifacioAgent),
            ("maria_quiteria", MariaQuiteriaAgent),
        ]

        results = {}

        for agent_name, agent_class in agent_classes:
            startup_times = []

            for _i in range(10):
                start = time.time()
                agent = agent_class()
                if hasattr(agent, "initialize"):
                    await agent.initialize()
                startup_time = (time.time() - start) * 1000  # ms
                startup_times.append(startup_time)

            results[agent_name] = {
                "mean": statistics.mean(startup_times),
                "max": max(startup_times),
                "min": min(startup_times),
            }

        # Verify fast startup
        for agent_name, metrics in results.items():
            assert metrics["mean"] < 100  # Under 100ms average
            assert metrics["max"] < 200  # Under 200ms worst case

            print(f"\n{agent_name} Startup:")
            print(f"  Mean: {metrics['mean']:.2f}ms")
            print(f"  Max: {metrics['max']:.2f}ms")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_throughput_limits(self):
        """Test maximum throughput for each agent."""
        agents = [
            ("zumbi", ZumbiAgent()),
            ("maria_quiteria", MariaQuiteriaAgent()),
            ("bonifacio", BonifacioAgent()),
        ]

        context = AgentContext(
            investigation_id="throughput-test",
            user_id="throughput-tester",
            session_id="throughput-session",
        )

        results = {}

        for agent_name, agent in agents:
            # Test duration
            test_duration = 10  # seconds
            request_count = 0
            error_count = 0

            start_time = time.time()

            while time.time() - start_time < test_duration:
                message = AgentMessage(
                    type="analyze",
                    data={"request": request_count},
                    sender="throughput_tester",
                    metadata={},
                )

                try:
                    response = await agent.process(message, context)
                    if not response.success:
                        error_count += 1
                except Exception:
                    error_count += 1

                request_count += 1

            elapsed = time.time() - start_time
            throughput = request_count / elapsed
            error_rate = error_count / request_count if request_count > 0 else 0

            results[agent_name] = {
                "throughput": throughput,
                "total_requests": request_count,
                "error_rate": error_rate,
            }

        # Verify minimum throughput
        for agent_name, metrics in results.items():
            assert metrics["throughput"] >= 10  # At least 10 req/s
            assert metrics["error_rate"] < 0.01  # Less than 1% errors

            print(f"\n{agent_name} Throughput:")
            print(f"  Rate: {metrics['throughput']:.2f} req/s")
            print(f"  Total: {metrics['total_requests']}")
            print(f"  Errors: {metrics['error_rate']:.2%}")


class TestMultiAgentPerformance:
    """Performance tests for multi-agent scenarios."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_multi_agent_pipeline_performance(self):
        """Test performance of multi-agent processing pipeline."""
        # Create pipeline
        pipeline = [ZumbiAgent(), AnitaAgent(), TiradentesAgent()]

        context = AgentContext(
            investigation_id="pipeline-test",
            user_id="pipeline-tester",
            session_id="pipeline-session",
        )

        # Test different data sizes
        data_sizes = [1, 10, 100]  # KB
        results = {}

        for size_kb in data_sizes:
            processing_times = []

            for i in range(20):
                # Create data payload
                data = {
                    "iteration": i,
                    "payload": "x" * (size_kb * 1024),
                    "results": {},
                }

                start = time.time()

                # Process through pipeline
                for agent in pipeline:
                    message = AgentMessage(
                        type="process",
                        data=data,
                        sender="pipeline",
                        metadata={"stage": agent.name},
                    )

                    response = await agent.process(message, context)
                    data["results"][agent.name] = response.data

                elapsed = time.time() - start
                processing_times.append(elapsed)

            results[f"{size_kb}KB"] = {
                "mean": statistics.mean(processing_times),
                "p95": np.percentile(processing_times, 95),
                "throughput": 1 / statistics.mean(processing_times),
            }

        # Verify performance scales reasonably
        for size, metrics in results.items():
            print(f"\nPipeline Performance ({size}):")
            print(f"  Mean: {metrics['mean']:.3f}s")
            print(f"  P95: {metrics['p95']:.3f}s")
            print(f"  Throughput: {metrics['throughput']:.2f} ops/s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_orchestration_overhead(self):
        """Test overhead of agent orchestration layer."""
        direct_times = []
        orchestrated_times = []

        agent = ZumbiAgent()
        context = AgentContext(
            investigation_id="overhead-test",
            user_id="overhead-tester",
            session_id="overhead-session",
        )

        # Direct agent calls
        for i in range(50):
            message = AgentMessage(
                type="analyze", data={"test": i}, sender="direct", metadata={}
            )

            start = time.time()
            await agent.process(message, context)
            direct_times.append(time.time() - start)

        # Orchestrated calls (with mock orchestrator overhead)
        for i in range(50):
            message = AgentMessage(
                type="analyze", data={"test": i}, sender="orchestrated", metadata={}
            )

            start = time.time()

            # Simulate orchestration overhead
            await asyncio.sleep(0.001)  # 1ms overhead
            await agent.process(message, context)
            await asyncio.sleep(0.001)  # Post-processing

            orchestrated_times.append(time.time() - start)

        # Calculate overhead
        direct_avg = statistics.mean(direct_times)
        orchestrated_avg = statistics.mean(orchestrated_times)
        overhead = orchestrated_avg - direct_avg
        overhead_percentage = (overhead / direct_avg) * 100

        # Verify acceptable overhead
        assert overhead_percentage < 10  # Less than 10% overhead

        print("\nOrchestration Overhead:")
        print(f"  Direct: {direct_avg*1000:.2f}ms")
        print(f"  Orchestrated: {orchestrated_avg*1000:.2f}ms")
        print(f"  Overhead: {overhead*1000:.2f}ms ({overhead_percentage:.1f}%)")
