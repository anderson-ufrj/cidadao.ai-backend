"""
A/B Testing Framework for ML Models

This module provides A/B testing capabilities for comparing model
performance in production environments.
"""

import json
import random
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import numpy as np
from scipy import stats

from src.core import get_logger
from src.core.cache import get_redis_client
from src.ml.training_pipeline import get_training_pipeline

logger = get_logger(__name__)


class ABTestStatus(Enum):
    """Status of an A/B test."""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"


class TrafficAllocationStrategy(Enum):
    """Strategy for allocating traffic between models."""

    RANDOM = "random"
    WEIGHTED = "weighted"
    EPSILON_GREEDY = "epsilon_greedy"
    THOMPSON_SAMPLING = "thompson_sampling"


class ABTestFramework:
    """
    A/B Testing framework for ML models.

    Features:
    - Multiple allocation strategies
    - Statistical significance testing
    - Real-time performance tracking
    - Automatic winner selection
    - Gradual rollout support
    """

    def __init__(self):
        """Initialize the A/B testing framework."""
        self.active_tests = {}
        self.test_results = {}

    async def create_test(
        self,
        test_name: str,
        model_a: tuple[str, Optional[int]],  # (model_id, version)
        model_b: tuple[str, Optional[int]],
        allocation_strategy: TrafficAllocationStrategy = TrafficAllocationStrategy.RANDOM,
        traffic_split: tuple[float, float] = (0.5, 0.5),
        success_metric: str = "f1_score",
        minimum_sample_size: int = 1000,
        significance_level: float = 0.05,
        auto_stop: bool = True,
        duration_hours: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Create a new A/B test.

        Args:
            test_name: Unique name for the test
            model_a: Model A (control) - (model_id, version)
            model_b: Model B (treatment) - (model_id, version)
            allocation_strategy: Traffic allocation strategy
            traffic_split: Traffic split between models (must sum to 1.0)
            success_metric: Metric to optimize
            minimum_sample_size: Minimum samples before analysis
            significance_level: Statistical significance threshold
            auto_stop: Automatically stop when winner found
            duration_hours: Maximum test duration

        Returns:
            Test configuration
        """
        if test_name in self.active_tests:
            raise ValueError(f"Test {test_name} already exists")

        if abs(sum(traffic_split) - 1.0) > 0.001:
            raise ValueError("Traffic split must sum to 1.0")

        # Load models to verify they exist
        pipeline = get_training_pipeline()
        await pipeline.load_model(*model_a)
        await pipeline.load_model(*model_b)

        test_config = {
            "test_id": f"ab_test_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "test_name": test_name,
            "model_a": {"model_id": model_a[0], "version": model_a[1]},
            "model_b": {"model_id": model_b[0], "version": model_b[1]},
            "allocation_strategy": allocation_strategy.value,
            "traffic_split": traffic_split,
            "success_metric": success_metric,
            "minimum_sample_size": minimum_sample_size,
            "significance_level": significance_level,
            "auto_stop": auto_stop,
            "status": ABTestStatus.DRAFT.value,
            "created_at": datetime.now().isoformat(),
            "start_time": None,
            "end_time": None,
            "duration_hours": duration_hours,
            "results": {
                "model_a": {"predictions": 0, "successes": 0, "metrics": {}},
                "model_b": {"predictions": 0, "successes": 0, "metrics": {}},
            },
        }

        # Initialize allocation strategy specific params
        if allocation_strategy == TrafficAllocationStrategy.EPSILON_GREEDY:
            test_config["epsilon"] = 0.1  # 10% exploration
        elif allocation_strategy == TrafficAllocationStrategy.THOMPSON_SAMPLING:
            test_config["thompson_params"] = {
                "model_a": {"alpha": 1, "beta": 1},
                "model_b": {"alpha": 1, "beta": 1},
            }

        self.active_tests[test_name] = test_config

        # Save to Redis
        await self._save_test_config(test_config)

        logger.info(f"Created A/B test: {test_name}")
        return test_config

    async def start_test(self, test_name: str) -> bool:
        """Start an A/B test."""
        if test_name not in self.active_tests:
            # Try to load from Redis
            test_config = await self._load_test_config(test_name)
            if not test_config:
                raise ValueError(f"Test {test_name} not found")
            self.active_tests[test_name] = test_config

        test_config = self.active_tests[test_name]

        if test_config["status"] not in [
            ABTestStatus.DRAFT.value,
            ABTestStatus.PAUSED.value,
        ]:
            raise ValueError(f"Cannot start test in status {test_config['status']}")

        test_config["status"] = ABTestStatus.RUNNING.value
        test_config["start_time"] = datetime.now().isoformat()

        await self._save_test_config(test_config)

        logger.info(f"Started A/B test: {test_name}")
        return True

    async def allocate_model(
        self, test_name: str, user_id: Optional[str] = None
    ) -> tuple[str, int]:
        """
        Allocate a model for a user based on the test configuration.

        Args:
            test_name: Test name
            user_id: User identifier for consistent allocation

        Returns:
            Tuple of (model_id, version)
        """
        test_config = self.active_tests.get(test_name)
        if not test_config:
            test_config = await self._load_test_config(test_name)
            if not test_config:
                raise ValueError(f"Test {test_name} not found")

        if test_config["status"] != ABTestStatus.RUNNING.value:
            raise ValueError(f"Test {test_name} is not running")

        # Select model based on allocation strategy
        strategy = TrafficAllocationStrategy(test_config["allocation_strategy"])

        if strategy == TrafficAllocationStrategy.RANDOM:
            selected = await self._random_allocation(test_config, user_id)
        elif strategy == TrafficAllocationStrategy.WEIGHTED:
            selected = await self._weighted_allocation(test_config)
        elif strategy == TrafficAllocationStrategy.EPSILON_GREEDY:
            selected = await self._epsilon_greedy_allocation(test_config)
        elif strategy == TrafficAllocationStrategy.THOMPSON_SAMPLING:
            selected = await self._thompson_sampling_allocation(test_config)
        else:
            selected = "model_a"  # Default fallback

        # Return model info
        model_info = test_config[selected]
        return (model_info["model_id"], model_info["version"])

    async def _random_allocation(
        self, test_config: dict[str, Any], user_id: Optional[str] = None
    ) -> str:
        """Random allocation with optional user-based consistency."""
        if user_id:
            # Hash user_id for consistent allocation
            hash_val = hash(user_id + test_config["test_id"]) % 100
            threshold = test_config["traffic_split"][0] * 100
            return "model_a" if hash_val < threshold else "model_b"
        else:
            # Pure random
            return (
                "model_a"
                if random.random() < test_config["traffic_split"][0]
                else "model_b"
            )

    async def _weighted_allocation(self, test_config: dict[str, Any]) -> str:
        """Weighted allocation based on traffic split."""
        return np.random.choice(["model_a", "model_b"], p=test_config["traffic_split"])

    async def _epsilon_greedy_allocation(self, test_config: dict[str, Any]) -> str:
        """Epsilon-greedy allocation (explore vs exploit)."""
        epsilon = test_config.get("epsilon", 0.1)

        if random.random() < epsilon:
            # Explore
            return random.choice(["model_a", "model_b"])
        else:
            # Exploit - choose best performing
            results = test_config["results"]
            rate_a = results["model_a"]["successes"] / max(
                results["model_a"]["predictions"], 1
            )
            rate_b = results["model_b"]["successes"] / max(
                results["model_b"]["predictions"], 1
            )

            return "model_a" if rate_a >= rate_b else "model_b"

    async def _thompson_sampling_allocation(self, test_config: dict[str, Any]) -> str:
        """Thompson sampling allocation (Bayesian approach)."""
        params = test_config["thompson_params"]

        # Sample from Beta distributions
        sample_a = np.random.beta(params["model_a"]["alpha"], params["model_a"]["beta"])
        sample_b = np.random.beta(params["model_b"]["alpha"], params["model_b"]["beta"])

        return "model_a" if sample_a >= sample_b else "model_b"

    async def record_prediction(
        self,
        test_name: str,
        model_selection: str,  # "model_a" or "model_b"
        success: bool,
        prediction_metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Record a prediction result for the test.

        Args:
            test_name: Test name
            model_selection: Which model was used
            success: Whether prediction was successful
            prediction_metadata: Additional metadata
        """
        test_config = self.active_tests.get(test_name)
        if not test_config:
            test_config = await self._load_test_config(test_name)
            if not test_config:
                raise ValueError(f"Test {test_name} not found")

        # Update results
        results = test_config["results"][model_selection]
        results["predictions"] += 1
        if success:
            results["successes"] += 1

        # Update Thompson sampling parameters if applicable
        if (
            test_config["allocation_strategy"]
            == TrafficAllocationStrategy.THOMPSON_SAMPLING.value
        ):
            params = test_config["thompson_params"][model_selection]
            if success:
                params["alpha"] += 1
            else:
                params["beta"] += 1

        # Save updated config
        await self._save_test_config(test_config)

        # Check if we should analyze results
        total_predictions = (
            test_config["results"]["model_a"]["predictions"]
            + test_config["results"]["model_b"]["predictions"]
        )

        if total_predictions >= test_config["minimum_sample_size"]:
            analysis = await self.analyze_test(test_name)

            if test_config["auto_stop"] and analysis.get("winner"):
                await self.stop_test(test_name, reason="Winner found")

    async def analyze_test(self, test_name: str) -> dict[str, Any]:
        """
        Analyze test results for statistical significance.

        Returns:
            Analysis results including winner if found
        """
        test_config = self.active_tests.get(test_name)
        if not test_config:
            test_config = await self._load_test_config(test_name)
            if not test_config:
                raise ValueError(f"Test {test_name} not found")

        results_a = test_config["results"]["model_a"]
        results_b = test_config["results"]["model_b"]

        # Calculate conversion rates
        rate_a = results_a["successes"] / max(results_a["predictions"], 1)
        rate_b = results_b["successes"] / max(results_b["predictions"], 1)

        # Perform chi-square test
        contingency_table = np.array(
            [
                [
                    results_a["successes"],
                    results_a["predictions"] - results_a["successes"],
                ],
                [
                    results_b["successes"],
                    results_b["predictions"] - results_b["successes"],
                ],
            ]
        )

        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

        # Calculate confidence intervals
        ci_a = self._calculate_confidence_interval(
            results_a["successes"], results_a["predictions"]
        )
        ci_b = self._calculate_confidence_interval(
            results_b["successes"], results_b["predictions"]
        )

        # Determine winner
        winner = None
        if p_value < test_config["significance_level"]:
            winner = "model_a" if rate_a > rate_b else "model_b"

        # Calculate lift
        lift = ((rate_b - rate_a) / rate_a * 100) if rate_a > 0 else 0

        analysis = {
            "model_a": {
                "conversion_rate": rate_a,
                "confidence_interval": ci_a,
                "sample_size": results_a["predictions"],
            },
            "model_b": {
                "conversion_rate": rate_b,
                "confidence_interval": ci_b,
                "sample_size": results_b["predictions"],
            },
            "p_value": p_value,
            "chi_square": chi2,
            "significant": p_value < test_config["significance_level"],
            "winner": winner,
            "lift": lift,
            "analysis_time": datetime.now().isoformat(),
        }

        # Update test config with latest analysis
        test_config["latest_analysis"] = analysis
        await self._save_test_config(test_config)

        return analysis

    def _calculate_confidence_interval(
        self, successes: int, total: int, confidence_level: float = 0.95
    ) -> tuple[float, float]:
        """Calculate confidence interval for conversion rate."""
        if total == 0:
            return (0.0, 0.0)

        rate = successes / total
        z = stats.norm.ppf((1 + confidence_level) / 2)

        # Wilson score interval
        denominator = 1 + z**2 / total
        center = (rate + z**2 / (2 * total)) / denominator
        margin = (
            z * np.sqrt(rate * (1 - rate) / total + z**2 / (4 * total**2)) / denominator
        )

        return (max(0, center - margin), min(1, center + margin))

    async def stop_test(self, test_name: str, reason: str = "Manual stop") -> bool:
        """Stop an A/B test."""
        test_config = self.active_tests.get(test_name)
        if not test_config:
            test_config = await self._load_test_config(test_name)
            if not test_config:
                raise ValueError(f"Test {test_name} not found")

        test_config["status"] = ABTestStatus.STOPPED.value
        test_config["end_time"] = datetime.now().isoformat()
        test_config["stop_reason"] = reason

        # Perform final analysis
        final_analysis = await self.analyze_test(test_name)
        test_config["final_analysis"] = final_analysis

        await self._save_test_config(test_config)

        # Move to completed tests
        self.test_results[test_name] = test_config
        if test_name in self.active_tests:
            del self.active_tests[test_name]

        logger.info(f"Stopped A/B test {test_name}: {reason}")
        return True

    async def get_test_status(self, test_name: str) -> dict[str, Any]:
        """Get current status of a test."""
        test_config = self.active_tests.get(test_name)
        if not test_config:
            test_config = await self._load_test_config(test_name)
            if not test_config:
                raise ValueError(f"Test {test_name} not found")

        # Add runtime if running
        if (
            test_config["status"] == ABTestStatus.RUNNING.value
            and test_config["start_time"]
        ):
            start = datetime.fromisoformat(test_config["start_time"])
            runtime = (datetime.now() - start).total_seconds() / 3600
            test_config["runtime_hours"] = runtime

            # Check if should auto-stop due to duration
            if (
                test_config.get("duration_hours")
                and runtime >= test_config["duration_hours"]
            ):
                await self.stop_test(test_name, reason="Duration limit reached")

        return test_config

    async def promote_winner(self, test_name: str) -> bool:
        """Promote the winning model to production."""
        test_config = self.test_results.get(test_name)
        if not test_config:
            # Try loading completed test
            test_config = await self._load_test_config(test_name)
            if not test_config or test_config["status"] != ABTestStatus.STOPPED.value:
                raise ValueError(f"Test {test_name} not completed")

        final_analysis = test_config.get("final_analysis", {})
        winner = final_analysis.get("winner")

        if not winner:
            raise ValueError(f"No winner found for test {test_name}")

        # Promote winning model
        model_info = test_config[winner]
        pipeline = get_training_pipeline()
        success = await pipeline.promote_model(
            model_info["model_id"], model_info["version"], "production"
        )

        if success:
            logger.info(f"Promoted {winner} from test {test_name} to production")

        return success

    async def _save_test_config(self, test_config: dict[str, Any]):
        """Save test configuration to Redis."""
        redis_client = await get_redis_client()
        key = f"ab_test:{test_config['test_name']}"
        await redis_client.set(key, json.dumps(test_config), ex=86400 * 90)  # 90 days

    async def _load_test_config(self, test_name: str) -> Optional[dict[str, Any]]:
        """Load test configuration from Redis."""
        redis_client = await get_redis_client()
        key = f"ab_test:{test_name}"
        data = await redis_client.get(key)
        return json.loads(data) if data else None

    async def list_active_tests(self) -> list[dict[str, Any]]:
        """List all active tests."""
        # Load from Redis pattern
        redis_client = await get_redis_client()
        keys = await redis_client.keys("ab_test:*")

        active_tests = []
        for key in keys:
            data = await redis_client.get(key)
            if data:
                test_config = json.loads(data)
                if test_config["status"] in [
                    ABTestStatus.RUNNING.value,
                    ABTestStatus.PAUSED.value,
                ]:
                    active_tests.append(
                        {
                            "test_name": test_config["test_name"],
                            "status": test_config["status"],
                            "model_a": test_config["model_a"]["model_id"],
                            "model_b": test_config["model_b"]["model_id"],
                            "start_time": test_config.get("start_time"),
                            "predictions": (
                                test_config["results"]["model_a"]["predictions"]
                                + test_config["results"]["model_b"]["predictions"]
                            ),
                        }
                    )

        return active_tests


# Global A/B testing framework instance
ab_testing = ABTestFramework()


async def get_ab_testing() -> ABTestFramework:
    """Get the global A/B testing framework instance."""
    return ab_testing
