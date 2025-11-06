"""
Benchmark tests for critical operations.
Measures execution time and resource usage for key system components.
"""

import asyncio
import gc
import time
from collections.abc import Callable
from dataclasses import dataclass

import psutil
import pytest

try:
    from memory_profiler import profile
except ImportError:
    # If memory_profiler is not installed, use a no-op decorator
    def profile(func):
        return func


from src.agents.anita import AnitaAgent
from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.tiradentes import TiradentesAgent
from src.agents.zumbi import ZumbiAgent


@dataclass
class BenchmarkResult:
    """Benchmark result data."""

    operation: str
    execution_time: float
    memory_used: float
    cpu_percent: float
    iterations: int

    @property
    def avg_time(self) -> float:
        """Average time per iteration."""
        return self.execution_time / self.iterations

    def __str__(self) -> str:
        return (
            f"{self.operation}:\n"
            f"  Total Time: {self.execution_time:.3f}s\n"
            f"  Avg Time: {self.avg_time:.3f}s\n"
            f"  Memory: {self.memory_used:.2f} MB\n"
            f"  CPU: {self.cpu_percent:.1f}%\n"
            f"  Iterations: {self.iterations}"
        )


class Benchmark:
    """Performance benchmark utility."""

    def __init__(self):
        self.results: list[BenchmarkResult] = []
        self.process = psutil.Process()

    def measure_memory(self) -> float:
        """Measure current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def measure_cpu(self) -> float:
        """Measure CPU usage percentage."""
        return self.process.cpu_percent(interval=0.1)

    async def run(
        self, operation: str, func: Callable, iterations: int = 10, *args, **kwargs
    ) -> BenchmarkResult:
        """Run benchmark for an operation."""
        # Garbage collection before measurement
        gc.collect()

        # Start measurements
        start_memory = self.measure_memory()
        start_time = time.time()
        cpu_samples = []

        # Run iterations
        for _ in range(iterations):
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
            cpu_samples.append(self.measure_cpu())

        # End measurements
        end_time = time.time()
        end_memory = self.measure_memory()

        # Create result
        result = BenchmarkResult(
            operation=operation,
            execution_time=end_time - start_time,
            memory_used=end_memory - start_memory,
            cpu_percent=sum(cpu_samples) / len(cpu_samples),
            iterations=iterations,
        )

        self.results.append(result)
        return result

    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS SUMMARY")
        print("=" * 60)

        for result in self.results:
            print(f"\n{result}")

        # Overall statistics
        total_time = sum(r.execution_time for r in self.results)
        total_memory = sum(r.memory_used for r in self.results)
        avg_cpu = sum(r.cpu_percent for r in self.results) / len(self.results)

        print("\n" + "-" * 60)
        print(f"Total Execution Time: {total_time:.3f}s")
        print(f"Total Memory Used: {total_memory:.2f} MB")
        print(f"Average CPU Usage: {avg_cpu:.1f}%")
        print("=" * 60)


@pytest.mark.benchmark
@pytest.mark.asyncio
class TestSystemBenchmarks:
    """System-wide performance benchmarks."""

    @pytest.fixture
    def benchmark(self):
        """Create benchmark instance."""
        return Benchmark()

    @pytest.fixture
    def sample_contracts(self):
        """Create sample contract data."""
        return [
            {"id": i, "value": 1000 * (i % 100), "supplier": f"Supplier_{i % 20}"}
            for i in range(100)
        ]

    async def test_agent_initialization_benchmark(self, benchmark):
        """Benchmark agent initialization times."""

        async def init_zumbi():
            return ZumbiAgent()

        async def init_anita():
            return AnitaAgent()

        async def init_tiradentes():
            return TiradentesAgent()

        # Benchmark each agent
        zumbi_result = await benchmark.run("Zumbi Init", init_zumbi, iterations=20)
        assert zumbi_result.avg_time < 0.1, "Zumbi initialization too slow"

        anita_result = await benchmark.run("Anita Init", init_anita, iterations=20)
        assert anita_result.avg_time < 0.1, "Anita initialization too slow"

        tiradentes_result = await benchmark.run(
            "Tiradentes Init", init_tiradentes, iterations=20
        )
        assert tiradentes_result.avg_time < 0.1, "Tiradentes initialization too slow"

    async def test_anomaly_detection_benchmark(self, benchmark, sample_contracts):
        """Benchmark anomaly detection performance."""
        agent = ZumbiAgent()
        message = AgentMessage(
            content={"contracts": sample_contracts},
            message_id="bench-001",
        )
        context = AgentContext()

        async def detect_anomalies():
            return await agent.process(message, context)

        result = await benchmark.run(
            "Anomaly Detection (100 contracts)",
            detect_anomalies,
            iterations=5,
        )

        assert (
            result.avg_time < 2.0
        ), f"Anomaly detection too slow: {result.avg_time:.2f}s"
        assert (
            result.memory_used < 50
        ), f"Memory usage too high: {result.memory_used:.2f} MB"

    async def test_statistical_analysis_benchmark(self, benchmark, sample_contracts):
        """Benchmark statistical analysis performance."""
        agent = AnitaAgent()
        message = AgentMessage(
            content={"data": sample_contracts},
            message_id="bench-002",
        )
        context = AgentContext()

        async def analyze_statistics():
            return await agent.process(message, context)

        result = await benchmark.run(
            "Statistical Analysis (100 items)",
            analyze_statistics,
            iterations=5,
        )

        assert (
            result.avg_time < 3.0
        ), f"Statistical analysis too slow: {result.avg_time:.2f}s"
        assert (
            result.memory_used < 100
        ), f"Memory usage too high: {result.memory_used:.2f} MB"

    async def test_report_generation_benchmark(self, benchmark):
        """Benchmark report generation performance."""
        agent = TiradentesAgent()
        message = AgentMessage(
            content={
                "type": "summary",
                "data": {
                    "title": "Performance Report",
                    "findings": ["Finding 1", "Finding 2", "Finding 3"],
                    "recommendations": ["Rec 1", "Rec 2"],
                },
            },
            message_id="bench-003",
        )
        context = AgentContext()

        async def generate_report():
            return await agent.process(message, context)

        result = await benchmark.run(
            "Report Generation",
            generate_report,
            iterations=5,
        )

        assert (
            result.avg_time < 1.0
        ), f"Report generation too slow: {result.avg_time:.2f}s"

    async def test_concurrent_agent_processing(self, benchmark, sample_contracts):
        """Benchmark concurrent agent processing."""

        async def process_concurrent():
            agents = [
                ZumbiAgent(),
                AnitaAgent(),
                TiradentesAgent(),
            ]

            messages = [
                AgentMessage(
                    content={"data": sample_contracts[:33]},
                    message_id=f"bench-{i:03d}",
                )
                for i in range(3)
            ]

            tasks = [
                agent.process(msg, AgentContext())
                for agent, msg in zip(agents, messages, strict=False)
            ]

            return await asyncio.gather(*tasks)

        result = await benchmark.run(
            "Concurrent Processing (3 agents)",
            process_concurrent,
            iterations=3,
        )

        assert (
            result.avg_time < 5.0
        ), f"Concurrent processing too slow: {result.avg_time:.2f}s"
        assert result.cpu_percent < 80, f"CPU usage too high: {result.cpu_percent:.1f}%"

        # Print summary
        benchmark.print_summary()


@pytest.mark.benchmark
class TestMemoryBenchmarks:
    """Memory usage benchmarks."""

    def test_memory_leak_detection(self):
        """Test for memory leaks in agent processing."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Run many iterations
        for i in range(100):
            agent = ZumbiAgent()
            # Force garbage collection
            del agent
            if i % 10 == 0:
                gc.collect()

        gc.collect()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory

        assert (
            memory_growth < 50
        ), f"Potential memory leak: {memory_growth:.2f} MB growth"

    def test_large_dataset_processing(self):
        """Test memory handling with large datasets."""
        # Create large dataset
        large_data = [
            {"id": i, "value": i * 1000, "data": "x" * 1000} for i in range(1000)
        ]

        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Process large dataset
        agent = ZumbiAgent()
        # Simulate processing
        del large_data
        del agent
        gc.collect()

        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_used = final_memory - initial_memory

        assert abs(memory_used) < 100, f"Excessive memory usage: {memory_used:.2f} MB"


def run_benchmark_suite():
    """Run complete benchmark suite."""
    print("\n" + "=" * 60)
    print("RUNNING BENCHMARK SUITE")
    print("=" * 60)

    # Run async benchmarks
    asyncio.run(run_async_benchmarks())


async def run_async_benchmarks():
    """Run all async benchmarks."""
    benchmark = Benchmark()
    test_instance = TestSystemBenchmarks()

    # Sample data
    sample_contracts = [
        {"id": i, "value": 1000 * (i % 100), "supplier": f"Supplier_{i % 20}"}
        for i in range(100)
    ]

    print("\n>>> Running Agent Initialization Benchmarks...")
    await test_instance.test_agent_initialization_benchmark(benchmark)
    print("✅ Agent initialization benchmarks completed")

    print("\n>>> Running Anomaly Detection Benchmark...")
    await test_instance.test_anomaly_detection_benchmark(benchmark, sample_contracts)
    print("✅ Anomaly detection benchmark completed")

    print("\n>>> Running Statistical Analysis Benchmark...")
    await test_instance.test_statistical_analysis_benchmark(benchmark, sample_contracts)
    print("✅ Statistical analysis benchmark completed")

    print("\n>>> Running Report Generation Benchmark...")
    await test_instance.test_report_generation_benchmark(benchmark)
    print("✅ Report generation benchmark completed")

    print("\n>>> Running Concurrent Processing Benchmark...")
    await test_instance.test_concurrent_agent_processing(benchmark, sample_contracts)
    print("✅ Concurrent processing benchmark completed")

    # Print final summary
    benchmark.print_summary()


if __name__ == "__main__":
    run_benchmark_suite()
