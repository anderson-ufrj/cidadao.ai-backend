"""
Advanced Agent Orchestrator for Cidadão.AI.
Manages complex agent coordination patterns and workflows.
"""

import asyncio
import time
import weakref
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, BaseAgent
from src.core import get_logger
from src.core.exceptions import OrchestrationError
from src.services.agent_lazy_loader import agent_lazy_loader
from src.services.cache_service import CacheService

logger = get_logger("agent.orchestrator")


class OrchestrationPattern(Enum):
    """Orchestration patterns supported by the system."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    FAN_OUT_FAN_IN = "fan_out_fan_in"
    CONDITIONAL = "conditional"
    SAGA = "saga"
    MAP_REDUCE = "map_reduce"
    EVENT_DRIVEN = "event_driven"


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Circuit breaker for agent fault tolerance."""

    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    half_open_requests: int = 3

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: datetime | None = None
    success_count: int = 0


@dataclass
class WorkflowStep:
    """Represents a step in an orchestrated workflow."""

    step_id: str
    agent_name: str
    action: str
    input_mapping: dict[str, str] = field(default_factory=dict)
    output_mapping: dict[str, str] = field(default_factory=dict)
    conditions: dict[str, Any] = field(default_factory=dict)
    retry_config: dict[str, Any] = field(default_factory=dict)
    timeout: int = 300  # seconds


@dataclass
class WorkflowDefinition:
    """Defines an orchestrated workflow."""

    workflow_id: str
    name: str
    pattern: OrchestrationPattern
    steps: list[WorkflowStep]
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout: int = 1800  # 30 minutes


@dataclass
class OrchestrationMetrics:
    """Metrics for orchestration performance."""

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration_seconds: float = 0.0
    agent_execution_times: dict[str, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    pattern_usage: dict[str, int] = field(default_factory=lambda: defaultdict(int))


class EventBus:
    """Simple event bus for event-driven choreography."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._async_handlers: dict[str, list[Callable]] = defaultdict(list)

    def on(self, event_name: str, handler: Callable):
        """Register an event handler."""
        if asyncio.iscoroutinefunction(handler):
            self._async_handlers[event_name].append(handler)
        else:
            self._handlers[event_name].append(handler)

    async def emit(self, event_name: str, data: Any = None):
        """Emit an event to all registered handlers."""
        event = {"name": event_name, "data": data, "timestamp": datetime.now(UTC)}

        # Call sync handlers
        for handler in self._handlers.get(event_name, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

        # Call async handlers
        tasks = []
        for handler in self._async_handlers.get(event_name, []):
            tasks.append(handler(event))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


class AgentOrchestrator:
    """Advanced orchestrator for multi-agent coordination."""

    def __init__(self):
        self.logger = logger
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._metrics = OrchestrationMetrics()
        self._event_bus = EventBus()
        self._cache = CacheService()
        self._agent_capabilities: dict[str, list[str]] = {}
        self._running_workflows: weakref.WeakValueDictionary = (
            weakref.WeakValueDictionary()
        )

    async def initialize(self):
        """Initialize the orchestrator."""
        self.logger.info("Initializing Agent Orchestrator")

        # Discover agent capabilities
        await self._discover_agent_capabilities()

        # Register default workflows
        self._register_default_workflows()

    async def _discover_agent_capabilities(self):
        """Discover capabilities of all available agents."""
        try:
            agents = agent_lazy_loader.get_available_agents()

            for agent_info in agents:
                agent = await agent_lazy_loader.get_agent(agent_info["name"])
                if hasattr(agent, "capabilities"):
                    self._agent_capabilities[agent_info["name"]] = agent.capabilities

        except Exception as e:
            self.logger.error(f"Error discovering agent capabilities: {e}")

    def _register_default_workflows(self):
        """Register default workflow patterns."""
        # Investigation workflow
        investigation_workflow = WorkflowDefinition(
            workflow_id="default_investigation",
            name="Standard Investigation Workflow",
            pattern=OrchestrationPattern.SEQUENTIAL,
            steps=[
                WorkflowStep(
                    step_id="anomaly_detection",
                    agent_name="zumbi",
                    action="detect_anomalies",
                ),
                WorkflowStep(
                    step_id="pattern_analysis",
                    agent_name="anita",
                    action="analyze_patterns",
                    conditions={"if": "anomalies_found", "gt": 0},
                ),
                WorkflowStep(
                    step_id="report_generation",
                    agent_name="tiradentes",
                    action="generate_report",
                ),
            ],
        )
        self._workflows["default_investigation"] = investigation_workflow

    async def execute_workflow(
        self, workflow_id: str, initial_data: dict[str, Any], context: AgentContext
    ) -> dict[str, Any]:
        """Execute a complete workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise OrchestrationError(f"Workflow {workflow_id} not found")

        self.logger.info(f"Executing workflow: {workflow.name}")
        start_time = time.time()

        try:
            # Track metrics
            self._metrics.total_executions += 1
            self._metrics.pattern_usage[workflow.pattern.value] += 1

            # Execute based on pattern
            if workflow.pattern == OrchestrationPattern.SEQUENTIAL:
                result = await self._execute_sequential(workflow, initial_data, context)
            elif workflow.pattern == OrchestrationPattern.PARALLEL:
                result = await self._execute_parallel(workflow, initial_data, context)
            elif workflow.pattern == OrchestrationPattern.FAN_OUT_FAN_IN:
                result = await self._execute_fan_out_fan_in(
                    workflow, initial_data, context
                )
            elif workflow.pattern == OrchestrationPattern.CONDITIONAL:
                result = await self._execute_conditional(
                    workflow, initial_data, context
                )
            elif workflow.pattern == OrchestrationPattern.SAGA:
                result = await self._execute_saga(workflow, initial_data, context)
            elif workflow.pattern == OrchestrationPattern.MAP_REDUCE:
                result = await self._execute_map_reduce(workflow, initial_data, context)
            else:
                raise OrchestrationError(f"Unsupported pattern: {workflow.pattern}")

            # Update metrics
            duration = time.time() - start_time
            self._metrics.successful_executions += 1
            self._metrics.total_duration_seconds += duration

            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "result": result,
                "duration": duration,
            }

        except Exception as e:
            self._metrics.failed_executions += 1
            raise OrchestrationError(f"Workflow execution failed: {e}")

    async def _execute_sequential(
        self, workflow: WorkflowDefinition, data: dict[str, Any], context: AgentContext
    ) -> dict[str, Any]:
        """Execute workflow steps sequentially."""
        current_data = data.copy()
        results = []

        for step in workflow.steps:
            # Check conditions
            if not self._check_conditions(step.conditions, current_data):
                continue

            # Execute step
            step_result = await self._execute_step(step, current_data, context)
            results.append(step_result)

            # Map output to next input
            for output_key, data_key in step.output_mapping.items():
                if output_key in step_result.get("data", {}):
                    current_data[data_key] = step_result["data"][output_key]

        return {
            "pattern": "sequential",
            "steps_executed": len(results),
            "final_data": current_data,
            "step_results": results,
        }

    async def _execute_parallel(
        self, workflow: WorkflowDefinition, data: dict[str, Any], context: AgentContext
    ) -> dict[str, Any]:
        """Execute workflow steps in parallel."""
        tasks = []

        for step in workflow.steps:
            if self._check_conditions(step.conditions, data):
                tasks.append(self._execute_step(step, data.copy(), context))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "pattern": "parallel",
            "steps_executed": len(results),
            "results": [r for r in results if not isinstance(r, Exception)],
            "errors": [str(r) for r in results if isinstance(r, Exception)],
        }

    async def _execute_step(
        self, step: WorkflowStep, data: dict[str, Any], context: AgentContext
    ) -> dict[str, Any]:
        """Execute a single workflow step."""
        start_time = time.time()

        try:
            # Get agent
            agent = await self._get_agent_with_circuit_breaker(step.agent_name)

            # Prepare input data
            input_data = {}
            for input_key, data_key in step.input_mapping.items():
                if data_key in data:
                    input_data[input_key] = data[data_key]

            # Create message
            message = AgentMessage(
                type=step.action,
                data=input_data or data,
                sender="orchestrator",
                metadata={"workflow_step": step.step_id},
            )

            # Execute with timeout
            response = await asyncio.wait_for(
                agent.process(message, context), timeout=step.timeout
            )

            # Track metrics
            duration = time.time() - start_time
            self._metrics.agent_execution_times[step.agent_name].append(duration)

            return {
                "step_id": step.step_id,
                "agent": step.agent_name,
                "success": response.success,
                "data": response.data,
                "duration": duration,
            }

        except TimeoutError:
            raise OrchestrationError(
                f"Step {step.step_id} timed out after {step.timeout}s"
            )
        except Exception as e:
            raise OrchestrationError(f"Step {step.step_id} failed: {e}")

    def _check_conditions(
        self, conditions: dict[str, Any], data: dict[str, Any]
    ) -> bool:
        """Check if conditions are met for step execution."""
        if not conditions:
            return True

        # Simple condition evaluation
        if "if" in conditions:
            field = conditions["if"]
            if field not in data:
                return False

            value = data[field]

            if "eq" in conditions:
                return value == conditions["eq"]
            if "gt" in conditions:
                return value > conditions["gt"]
            if "lt" in conditions:
                return value < conditions["lt"]
            if "in" in conditions:
                return value in conditions["in"]

        return True

    async def _get_agent_with_circuit_breaker(self, agent_name: str) -> BaseAgent:
        """Get agent with circuit breaker protection."""
        circuit_breaker = self._circuit_breakers.get(agent_name)
        if not circuit_breaker:
            circuit_breaker = CircuitBreaker()
            self._circuit_breakers[agent_name] = circuit_breaker

        # Check circuit state
        if circuit_breaker.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (
                datetime.now(UTC) - circuit_breaker.last_failure_time
            ).seconds > circuit_breaker.recovery_timeout:
                circuit_breaker.state = CircuitState.HALF_OPEN
                circuit_breaker.success_count = 0
            else:
                raise OrchestrationError(f"Circuit breaker open for {agent_name}")

        try:
            agent = await agent_lazy_loader.get_agent(agent_name)

            # Reset on success
            if circuit_breaker.state == CircuitState.HALF_OPEN:
                circuit_breaker.success_count += 1
                if circuit_breaker.success_count >= circuit_breaker.half_open_requests:
                    circuit_breaker.state = CircuitState.CLOSED
                    circuit_breaker.failure_count = 0

            return agent

        except Exception:
            # Update failure count
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = datetime.now(UTC)

            if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                circuit_breaker.state = CircuitState.OPEN

            raise

    async def select_best_agent(
        self, required_capabilities: list[str]
    ) -> BaseAgent | None:
        """Select the best agent based on required capabilities."""
        best_match = None
        best_score = 0

        for agent_name, capabilities in self._agent_capabilities.items():
            # Calculate capability match score
            score = sum(1 for cap in required_capabilities if cap in capabilities)

            if score > best_score:
                best_score = score
                best_match = agent_name

        if best_match:
            return await agent_lazy_loader.get_agent(best_match)

        return None

    async def execute_with_retry(
        self,
        agent: BaseAgent,
        message: AgentMessage,
        context: AgentContext,
        max_retries: int = 3,
        backoff_multiplier: float = 2.0,
        fallback_agent: BaseAgent | None = None,
    ) -> AgentResponse:
        """Execute agent with retry logic and optional fallback."""
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return await agent.process(message, context)
            except Exception as e:
                last_error = e

                if attempt < max_retries:
                    wait_time = (backoff_multiplier**attempt) * 1.0
                    await asyncio.sleep(wait_time)
                    continue

                # Try fallback agent if available
                if fallback_agent:
                    self.logger.warning("Primary agent failed, trying fallback")
                    return await fallback_agent.process(message, context)

                raise

        raise OrchestrationError(f"All retry attempts failed: {last_error}")

    def configure_retry_policy(self, policy: dict[str, Any]):
        """Configure global retry policy."""
        self._retry_policy = policy

    def configure_circuit_breaker(self, config: dict[str, Any]):
        """Configure circuit breaker settings."""
        self._circuit_breaker_config = config

    async def execute_conditional_workflow(
        self,
        workflow_def: dict[str, Any],
        initial_data: dict[str, Any],
        context: AgentContext,
    ) -> list[dict[str, Any]]:
        """Execute a conditional workflow with branching."""
        execution_path = []
        current_step = workflow_def["start"]
        current_data = initial_data.copy()

        while current_step:
            step_def = workflow_def["steps"][current_step]

            # Execute step
            agent_name = step_def["agent"]
            agent = await agent_lazy_loader.get_agent(agent_name)

            message = AgentMessage(
                type="process",
                data=current_data,
                sender="conditional_workflow",
                metadata={"step": current_step},
            )

            response = await agent.process(message, context)

            execution_path.append(
                {
                    "step": current_step,
                    "agent": agent_name,
                    "success": response.success,
                    "data": response.data,
                }
            )

            # Determine next step based on conditions
            next_step_def = step_def.get("next")
            if not next_step_def:
                break

            if isinstance(next_step_def, str):
                current_step = next_step_def
            else:
                # Conditional branching
                condition = next_step_def.get("condition")
                if condition == "anomalies_found":
                    if response.data.get("anomalies_detected", 0) > 0:
                        current_step = next_step_def.get("true")
                    else:
                        current_step = next_step_def.get("false")
                elif condition == "high_risk":
                    if response.data.get("risk_level") == "high":
                        current_step = next_step_def.get("true")
                    else:
                        current_step = next_step_def.get("false")
                else:
                    current_step = next_step_def.get("default")

            # Update data for next step
            current_data.update(response.data)

        return execution_path

    async def discover_agents(self) -> list[dict[str, Any]]:
        """Discover all available agents."""
        return agent_lazy_loader.get_available_agents()

    async def find_agents_with_capability(
        self, capability: str
    ) -> list[dict[str, Any]]:
        """Find agents with a specific capability."""
        matching_agents = []

        for agent_name, capabilities in self._agent_capabilities.items():
            if capability in capabilities:
                agent_info = {"name": agent_name, "capabilities": capabilities}
                matching_agents.append(agent_info)

        return matching_agents

    async def execute_with_circuit_breaker(
        self, agent: BaseAgent, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """Execute agent with circuit breaker protection."""
        agent_name = agent.name
        circuit_breaker = self._circuit_breakers.get(agent_name)

        if not circuit_breaker:
            circuit_breaker = CircuitBreaker(**self._circuit_breaker_config)
            self._circuit_breakers[agent_name] = circuit_breaker

        if circuit_breaker.state == CircuitState.OPEN:
            if (
                datetime.now(UTC) - circuit_breaker.last_failure_time
            ).seconds < circuit_breaker.recovery_timeout:
                raise OrchestrationError(f"Circuit breaker open for {agent_name}")
            circuit_breaker.state = CircuitState.HALF_OPEN

        try:
            response = await agent.process(message, context)

            if circuit_breaker.state == CircuitState.HALF_OPEN:
                circuit_breaker.success_count += 1
                if circuit_breaker.success_count >= circuit_breaker.half_open_requests:
                    circuit_breaker.state = CircuitState.CLOSED
                    circuit_breaker.failure_count = 0

            return response

        except Exception:
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = datetime.now(UTC)

            if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                circuit_breaker.state = CircuitState.OPEN

            raise

    async def start_saga(
        self,
        saga_definition: dict[str, Any],
        initial_data: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Start a saga transaction."""
        saga_state = {
            "saga_id": f"saga_{datetime.now(UTC).timestamp()}",
            "name": saga_definition["name"],
            "current_step": 0,
            "completed_steps": [],
            "compensated_steps": [],
            "data": initial_data,
            "completed": False,
            "failed": False,
        }

        return saga_state

    async def execute_saga_step(
        self, saga_state: dict[str, Any], step: dict[str, Any], context: AgentContext
    ) -> dict[str, Any]:
        """Execute a saga step with compensation support."""
        try:
            agent_name = step["agent"]
            agent = await agent_lazy_loader.get_agent(agent_name)

            message = AgentMessage(
                type=step["service"],
                data=saga_state["data"],
                sender="saga_coordinator",
                metadata={"saga_id": saga_state["saga_id"]},
            )

            response = await agent.process(message, context)

            if response.success:
                saga_state["completed_steps"].append(
                    {"step": step, "result": response.data}
                )
                saga_state["current_step"] += 1

                if saga_state["current_step"] >= len(saga_state.get("total_steps", [])):
                    saga_state["completed"] = True
            else:
                saga_state["failed"] = True
                # Trigger compensation
                await self._compensate_saga(saga_state, context)

        except Exception as e:
            saga_state["failed"] = True
            saga_state["error"] = str(e)
            await self._compensate_saga(saga_state, context)

        return saga_state

    async def _compensate_saga(self, saga_state: dict[str, Any], context: AgentContext):
        """Compensate completed saga steps."""
        for completed_step in reversed(saga_state["completed_steps"]):
            try:
                step = completed_step["step"]
                if "compensation" in step:
                    agent = await agent_lazy_loader.get_agent(step["agent"])

                    compensation_message = AgentMessage(
                        type=step["compensation"],
                        data={
                            "original_data": saga_state["data"],
                            "step_result": completed_step["result"],
                        },
                        sender="saga_compensator",
                        metadata={"saga_id": saga_state["saga_id"]},
                    )

                    await agent.process(compensation_message, context)
                    saga_state["compensated_steps"].append(step)

            except Exception as e:
                self.logger.error(f"Compensation failed for step: {e}")

    def get_event_bus(self) -> EventBus:
        """Get the event bus for choreography."""
        return self._event_bus

    async def get_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "total_executions": self._metrics.total_executions,
            "successful_executions": self._metrics.successful_executions,
            "failed_executions": self._metrics.failed_executions,
            "success_rate": (
                self._metrics.successful_executions / self._metrics.total_executions
                if self._metrics.total_executions > 0
                else 0
            ),
            "average_duration": (
                self._metrics.total_duration_seconds
                / self._metrics.successful_executions
                if self._metrics.successful_executions > 0
                else 0
            ),
            "pattern_usage": dict(self._metrics.pattern_usage),
            "agent_performance": {
                agent: {
                    "executions": len(times),
                    "avg_time": sum(times) / len(times) if times else 0,
                    "min_time": min(times) if times else 0,
                    "max_time": max(times) if times else 0,
                }
                for agent, times in self._metrics.agent_execution_times.items()
            },
            "circuit_breakers": {
                agent: {"state": cb.state.value, "failure_count": cb.failure_count}
                for agent, cb in self._circuit_breakers.items()
            },
        }

    async def _execute_fan_out_fan_in(
        self, workflow: WorkflowDefinition, data: dict[str, Any], context: AgentContext
    ) -> dict[str, Any]:
        """Execute fan-out/fan-in pattern."""
        # Fan-out: execute multiple steps in parallel
        fan_out_results = await self._execute_parallel(workflow, data, context)

        # Fan-in: aggregate results
        aggregated_data = {
            "pattern": "fan_out_fan_in",
            "fan_out_results": fan_out_results["results"],
            "aggregated_data": {},
        }

        # Simple aggregation - can be customized
        for result in fan_out_results["results"]:
            if result.get("success") and "data" in result:
                aggregated_data["aggregated_data"].update(result["data"])

        return aggregated_data

    async def _execute_map_reduce(
        self, workflow: WorkflowDefinition, data: dict[str, Any], context: AgentContext
    ) -> dict[str, Any]:
        """Execute map-reduce pattern."""
        # Map phase
        map_items = data.get("items", [])
        map_results = []

        for item in map_items:
            # Execute map step for each item
            map_step = workflow.steps[0]  # Assuming first step is map
            step_result = await self._execute_step(map_step, {"item": item}, context)
            map_results.append(step_result)

        # Reduce phase
        reduce_step = workflow.steps[1]  # Assuming second step is reduce
        reduce_data = {
            "map_results": [r["data"] for r in map_results if r.get("success")]
        }

        reduce_result = await self._execute_step(reduce_step, reduce_data, context)

        return {
            "pattern": "map_reduce",
            "map_count": len(map_results),
            "reduce_result": (
                reduce_result["data"] if reduce_result.get("success") else None
            ),
        }

    async def _execute_saga(
        self, workflow: WorkflowDefinition, data: dict[str, Any], context: AgentContext
    ) -> dict[str, Any]:
        """Execute saga pattern with compensation."""
        saga_state = await self.start_saga(
            {"name": workflow.name, "steps": workflow.steps}, data, context
        )

        saga_state["total_steps"] = workflow.steps

        for step in workflow.steps:
            saga_state = await self.execute_saga_step(
                saga_state, {"agent": step.agent_name, "service": step.action}, context
            )

            if saga_state["failed"]:
                break

        return {
            "pattern": "saga",
            "saga_id": saga_state["saga_id"],
            "completed": saga_state["completed"],
            "failed": saga_state["failed"],
            "completed_steps": len(saga_state["completed_steps"]),
            "compensated_steps": len(saga_state["compensated_steps"]),
        }


# Global orchestrator instance
orchestrator = AgentOrchestrator()


async def get_orchestrator() -> AgentOrchestrator:
    """Get the global orchestrator instance."""
    return orchestrator
