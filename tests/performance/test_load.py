"""
Load testing suite for Cidadão.AI backend.
Simulates multiple users and high traffic scenarios.
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime

import pytest
from httpx import AsyncClient


@dataclass
class LoadTestConfig:
    """Load test configuration."""

    base_url: str = "http://localhost:8000"
    num_users: int = 50
    ramp_up_time: int = 10  # seconds
    test_duration: int = 60  # seconds
    think_time: float = 1.0  # seconds between requests


@dataclass
class LoadTestResult:
    """Load test result metrics."""

    start_time: datetime
    end_time: datetime
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: list[float] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    requests_per_second: float = 0.0

    def calculate_metrics(self):
        """Calculate performance metrics."""
        duration = (self.end_time - self.start_time).total_seconds()
        self.requests_per_second = self.total_requests / duration if duration > 0 else 0

        if self.response_times:
            sorted_times = sorted(self.response_times)
            n = len(sorted_times)
            return {
                "duration": duration,
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": (
                    (self.successful_requests / self.total_requests * 100)
                    if self.total_requests > 0
                    else 0
                ),
                "requests_per_second": self.requests_per_second,
                "min_response_time": sorted_times[0],
                "max_response_time": sorted_times[-1],
                "avg_response_time": sum(sorted_times) / n,
                "p50_response_time": sorted_times[int(n * 0.5)],
                "p95_response_time": (
                    sorted_times[int(n * 0.95)] if n > 20 else sorted_times[-1]
                ),
                "p99_response_time": (
                    sorted_times[int(n * 0.99)] if n > 100 else sorted_times[-1]
                ),
            }
        return {}


class VirtualUser:
    """Simulates a virtual user making requests."""

    def __init__(self, user_id: int, config: LoadTestConfig):
        self.user_id = user_id
        self.config = config
        self.client: AsyncClient = None
        self.request_count = 0
        self.errors = []

    async def __aenter__(self):
        """Enter context manager."""
        self.client = AsyncClient(
            base_url=self.config.base_url,
            timeout=30.0,
            headers={"User-Agent": f"LoadTest-User-{self.user_id}"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self.client:
            await self.client.aclose()

    async def make_request(self, endpoint: str, method: str = "GET", data: dict = None):
        """Make a single request."""
        start_time = time.time()

        try:
            if method == "GET":
                response = await self.client.get(endpoint)
            elif method == "POST":
                response = await self.client.post(endpoint, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            elapsed = time.time() - start_time
            self.request_count += 1

            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": elapsed,
                "endpoint": endpoint,
            }

        except Exception as e:
            elapsed = time.time() - start_time
            self.errors.append(str(e))
            return {
                "success": False,
                "status_code": 0,
                "response_time": elapsed,
                "endpoint": endpoint,
                "error": str(e),
            }

    async def run_scenario(self) -> list[dict]:
        """Run a user scenario."""
        results = []

        # Scenario: Browse -> Search -> Chat
        scenarios = [
            # Browse agents
            ("GET", "/api/v1/agents/", None),
            # Check health
            ("GET", "/health/", None),
            # Send chat message
            (
                "POST",
                "/api/v1/chat/message",
                {"message": f"User {self.user_id}: Analyze contracts"},
            ),
            # GraphQL query
            (
                "POST",
                "/graphql",
                {"query": "{ agentStats { agentName totalTasks } }"},
            ),
        ]

        for method, endpoint, data in scenarios:
            result = await self.make_request(endpoint, method, data)
            results.append(result)

            # Think time between requests
            await asyncio.sleep(
                random.uniform(
                    self.config.think_time * 0.5, self.config.think_time * 1.5
                )
            )

        return results


class LoadTest:
    """Main load testing orchestrator."""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.result = LoadTestResult(start_time=datetime.now(), end_time=datetime.now())
        self.active_users = []

    async def spawn_user(self, user_id: int) -> list[dict]:
        """Spawn a virtual user."""
        async with VirtualUser(user_id, self.config) as user:
            return await user.run_scenario()

    async def run(self) -> LoadTestResult:
        """Run the load test."""
        self.result.start_time = datetime.now()
        print(f"\n🚀 Starting load test with {self.config.num_users} users")
        print(f"   Ramp-up time: {self.config.ramp_up_time}s")
        print(f"   Test duration: {self.config.test_duration}s")

        # Calculate delay between user spawns
        spawn_delay = self.config.ramp_up_time / self.config.num_users

        # Create user tasks
        tasks = []
        for i in range(self.config.num_users):
            # Spawn users with ramp-up delay
            await asyncio.sleep(spawn_delay)
            task = asyncio.create_task(self.spawn_user(i))
            tasks.append(task)

            if (i + 1) % 10 == 0:
                print(f"   Spawned {i + 1}/{self.config.num_users} users...")

        print("   All users spawned. Running scenarios...")

        # Wait for all users to complete
        all_results = await asyncio.gather(*tasks)

        # Aggregate results
        for user_results in all_results:
            for result in user_results:
                self.result.total_requests += 1
                if result["success"]:
                    self.result.successful_requests += 1
                    self.result.response_times.append(result["response_time"])
                else:
                    self.result.failed_requests += 1
                    if "error" in result:
                        self.result.errors.append(result["error"])

        self.result.end_time = datetime.now()
        return self.result


@pytest.mark.load
@pytest.mark.asyncio
class TestLoadScenarios:
    """Load test scenarios."""

    async def test_basic_load(self):
        """Basic load test with moderate traffic."""
        config = LoadTestConfig(
            num_users=10,
            ramp_up_time=5,
            test_duration=30,
        )

        load_test = LoadTest(config)
        result = await load_test.run()
        metrics = result.calculate_metrics()

        print("\n📊 Basic Load Test Results:")
        print(f"   Total Requests: {metrics['total_requests']}")
        print(f"   Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   RPS: {metrics['requests_per_second']:.1f}")
        print(f"   Avg Response Time: {metrics['avg_response_time']:.3f}s")
        print(f"   P95 Response Time: {metrics['p95_response_time']:.3f}s")

        assert metrics["success_rate"] >= 95, "Success rate below 95%"
        assert metrics["avg_response_time"] < 2.0, "Average response time too high"

    async def test_spike_load(self):
        """Spike test with sudden traffic increase."""
        config = LoadTestConfig(
            num_users=50,
            ramp_up_time=2,  # Fast ramp-up for spike
            test_duration=20,
        )

        load_test = LoadTest(config)
        result = await load_test.run()
        metrics = result.calculate_metrics()

        print("\n📊 Spike Load Test Results:")
        print(f"   Total Requests: {metrics['total_requests']}")
        print(f"   Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   RPS: {metrics['requests_per_second']:.1f}")
        print(f"   Avg Response Time: {metrics['avg_response_time']:.3f}s")
        print(f"   P95 Response Time: {metrics['p95_response_time']:.3f}s")

        assert metrics["success_rate"] >= 80, "Success rate below 80% during spike"
        assert metrics["p95_response_time"] < 5.0, "P95 response time too high"

    async def test_sustained_load(self):
        """Sustained load test for stability."""
        config = LoadTestConfig(
            num_users=20,
            ramp_up_time=10,
            test_duration=120,  # 2 minutes sustained
            think_time=2.0,
        )

        load_test = LoadTest(config)
        result = await load_test.run()
        metrics = result.calculate_metrics()

        print("\n📊 Sustained Load Test Results:")
        print(f"   Duration: {metrics['duration']:.1f}s")
        print(f"   Total Requests: {metrics['total_requests']}")
        print(f"   Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   RPS: {metrics['requests_per_second']:.1f}")
        print(f"   Avg Response Time: {metrics['avg_response_time']:.3f}s")
        print(f"   P50 Response Time: {metrics['p50_response_time']:.3f}s")
        print(f"   P95 Response Time: {metrics['p95_response_time']:.3f}s")
        print(f"   P99 Response Time: {metrics['p99_response_time']:.3f}s")

        assert (
            metrics["success_rate"] >= 90
        ), "Success rate degraded during sustained load"
        assert metrics["avg_response_time"] < 3.0, "Performance degraded over time"


def run_load_test_suite():
    """Run complete load test suite."""
    print("\n" + "=" * 60)
    print("RUNNING LOAD TEST SUITE")
    print("=" * 60)

    asyncio.run(run_all_load_tests())


async def run_all_load_tests():
    """Run all load test scenarios."""
    test_instance = TestLoadScenarios()

    print("\n>>> Running Basic Load Test...")
    await test_instance.test_basic_load()
    print("✅ Basic load test completed")

    print("\n>>> Running Spike Load Test...")
    await test_instance.test_spike_load()
    print("✅ Spike load test completed")

    print("\n>>> Running Sustained Load Test...")
    await test_instance.test_sustained_load()
    print("✅ Sustained load test completed")

    print("\n" + "=" * 60)
    print("LOAD TEST SUITE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_load_test_suite()
