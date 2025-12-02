"""
Sistema de Pool de Agentes e Execução Paralela
Arquitetura distribuída para escalabilidade horizontal de agentes
"""

import asyncio
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class AgentStatus(Enum):
    """Status dos agentes"""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"
    INITIALIZING = "initializing"


class TaskPriority(Enum):
    """Prioridade das tarefas"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ExecutionMode(Enum):
    """Modo de execução"""

    ASYNC = "async"
    THREAD = "thread"
    PROCESS = "process"
    DISTRIBUTED = "distributed"


@dataclass
class AgentTask:
    """Tarefa para execução por agente"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str = ""
    method: str = ""
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: float | None = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any = None
    error: str | None = None
    execution_mode: ExecutionMode = ExecutionMode.ASYNC


@dataclass
class AgentInstance:
    """Instância de agente no pool"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str = ""
    instance: Any = None
    status: AgentStatus = AgentStatus.INITIALIZING
    current_task_id: str | None = None
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_task_time: float = 0.0
    last_activity: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    process_id: int | None = None
    thread_id: int | None = None


class PoolConfig(BaseModel):
    """Configuração do pool de agentes"""

    # Pool sizing
    min_agents_per_type: int = 2
    max_agents_per_type: int = 10
    scale_up_threshold: float = 0.8  # Scale when 80% busy
    scale_down_threshold: float = 0.2  # Scale down when 20% busy

    # Task management
    max_queue_size: int = 1000
    task_timeout_default: float = 300.0  # 5 minutes
    task_retry_delay: float = 1.0

    # Health and monitoring
    health_check_interval: float = 30.0
    agent_idle_timeout: float = 600.0  # 10 minutes
    cleanup_interval: float = 60.0

    # Execution modes
    enable_threading: bool = True
    enable_multiprocessing: bool = True
    thread_pool_size: int = 4
    process_pool_size: int = 2

    # Performance tuning
    batch_size: int = 5
    prefetch_tasks: int = 3
    enable_task_prioritization: bool = True


class AgentPoolManager:
    """Gerenciador avançado de pool de agentes"""

    def __init__(self, config: PoolConfig):
        self.config = config

        # Agent pools by type
        self.agent_pools: dict[str, list[AgentInstance]] = {}
        self.agent_factories: dict[str, Callable] = {}

        # Task management
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(
            maxsize=config.max_queue_size
        )
        self.active_tasks: dict[str, AgentTask] = {}
        self.completed_tasks: dict[str, AgentTask] = {}

        # Execution pools
        self.thread_pool: ThreadPoolExecutor | None = None
        self.process_pool: ProcessPoolExecutor | None = None

        # Control
        self._running = False
        self._worker_tasks: list[asyncio.Task] = []
        self._health_check_task: asyncio.Task | None = None
        self._cleanup_task: asyncio.Task | None = None

        # Metrics
        self.metrics = {
            "tasks_queued": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_task_time": 0.0,
            "avg_queue_time": 0.0,
            "total_agents": 0,
            "busy_agents": 0,
        }

    async def initialize(self) -> bool:
        """Inicializar pool de agentes"""

        try:
            logger.info("Inicializando pool de agentes...")

            # Initialize execution pools
            if self.config.enable_threading:
                self.thread_pool = ThreadPoolExecutor(
                    max_workers=self.config.thread_pool_size,
                    thread_name_prefix="agent_thread",
                )
                logger.info(
                    f"✅ Thread pool criado ({self.config.thread_pool_size} workers)"
                )

            if self.config.enable_multiprocessing:
                self.process_pool = ProcessPoolExecutor(
                    max_workers=self.config.process_pool_size
                )
                logger.info(
                    f"✅ Process pool criado ({self.config.process_pool_size} workers)"
                )

            # Start worker tasks
            await self._start_worker_tasks()

            # Start monitoring tasks
            await self._start_monitoring_tasks()

            self._running = True
            logger.info("✅ Pool de agentes inicializado")

            return True

        except Exception as e:
            logger.error(f"❌ Falha na inicialização do pool: {e}")
            return False

    def register_agent_factory(self, agent_type: str, factory_function: Callable):
        """Registrar factory function para tipo de agente"""

        self.agent_factories[agent_type] = factory_function
        logger.info(f"✅ Factory registrada para agente '{agent_type}'")

    async def create_agent_pool(
        self, agent_type: str, initial_size: int = None
    ) -> bool:
        """Criar pool inicial para tipo de agente"""

        if agent_type not in self.agent_factories:
            logger.error(f"❌ Factory não encontrada para agente '{agent_type}'")
            return False

        initial_size = initial_size or self.config.min_agents_per_type
        self.agent_pools[agent_type] = []

        try:
            for i in range(initial_size):
                agent_instance = await self._create_agent_instance(agent_type)
                if agent_instance:
                    self.agent_pools[agent_type].append(agent_instance)

            logger.info(
                f"✅ Pool criado para '{agent_type}' com {len(self.agent_pools[agent_type])} agentes"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao criar pool para '{agent_type}': {e}")
            return False

    async def _create_agent_instance(self, agent_type: str) -> AgentInstance | None:
        """Criar nova instância de agente"""

        try:
            factory = self.agent_factories[agent_type]
            agent = (
                await factory() if asyncio.iscoroutinefunction(factory) else factory()
            )

            instance = AgentInstance(
                agent_type=agent_type, instance=agent, status=AgentStatus.IDLE
            )

            logger.debug(f"✅ Agente '{agent_type}' criado: {instance.id}")
            return instance

        except Exception as e:
            logger.error(f"❌ Erro ao criar agente '{agent_type}': {e}")
            return None

    async def submit_task(
        self,
        agent_type: str,
        method: str,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: float | None = None,
        execution_mode: ExecutionMode = ExecutionMode.ASYNC,
        **kwargs,
    ) -> str:
        """Submeter tarefa para execução"""

        task = AgentTask(
            agent_type=agent_type,
            method=method,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout or self.config.task_timeout_default,
            execution_mode=execution_mode,
        )

        # Add to queue with priority (lower number = higher priority)
        priority_value = (
            5 - priority.value
        )  # Invert for queue (lower = higher priority)

        try:
            await self.task_queue.put((priority_value, time.time(), task))
            self.metrics["tasks_queued"] += 1

            logger.debug(f"✅ Tarefa submetida: {task.id} para {agent_type}.{method}")
            return task.id

        except asyncio.QueueFull:
            logger.error(f"❌ Queue cheia! Tarefa rejeitada: {task.id}")
            raise Exception("Task queue is full")

    async def get_task_result(self, task_id: str, timeout: float = None) -> Any:
        """Obter resultado de tarefa"""

        start_time = time.time()
        timeout = timeout or 60.0

        while time.time() - start_time < timeout:
            # Check if task is completed
            if task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
                if task.error:
                    raise Exception(f"Task failed: {task.error}")
                return task.result

            # Check if task is still active
            if task_id in self.active_tasks:
                await asyncio.sleep(0.1)
                continue

            # Task not found
            break

        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")

    async def _start_worker_tasks(self):
        """Iniciar tasks de workers"""

        # Create multiple worker tasks for parallel processing
        num_workers = max(4, len(self.agent_factories) * 2)

        for i in range(num_workers):
            worker_task = asyncio.create_task(self._worker_loop(f"worker_{i}"))
            self._worker_tasks.append(worker_task)

        logger.info(f"✅ {num_workers} workers iniciados")

    async def _worker_loop(self, worker_name: str):
        """Loop principal do worker"""

        logger.debug(f"Worker {worker_name} iniciado")

        while self._running:
            try:
                # Get task from queue (with timeout to avoid blocking)
                try:
                    priority, queued_time, task = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                except TimeoutError:
                    continue

                # Calculate queue wait time
                queue_time = time.time() - queued_time
                self.metrics["avg_queue_time"] = (
                    self.metrics["avg_queue_time"] * 0.9 + queue_time * 0.1
                )

                # Execute task
                await self._execute_task(task, worker_name)

            except Exception as e:
                logger.error(f"❌ Erro no worker {worker_name}: {e}")
                await asyncio.sleep(1.0)

        logger.debug(f"Worker {worker_name} finalizado")

    async def _execute_task(self, task: AgentTask, worker_name: str):
        """Executar tarefa"""

        task.started_at = datetime.now(UTC)
        self.active_tasks[task.id] = task

        logger.debug(f"🔄 Executando tarefa {task.id} no worker {worker_name}")

        try:
            # Get available agent
            agent_instance = await self._get_available_agent(task.agent_type)

            if not agent_instance:
                # Try to scale up
                await self._scale_up_pool(task.agent_type)
                agent_instance = await self._get_available_agent(task.agent_type)

                if not agent_instance:
                    raise Exception(f"No agents available for type {task.agent_type}")

            # Mark agent as busy
            agent_instance.status = AgentStatus.BUSY
            agent_instance.current_task_id = task.id
            agent_instance.last_activity = datetime.now(UTC)

            # Execute based on mode
            start_time = time.time()

            if task.execution_mode == ExecutionMode.ASYNC:
                result = await self._execute_async(agent_instance, task)
            elif task.execution_mode == ExecutionMode.THREAD:
                result = await self._execute_in_thread(agent_instance, task)
            elif task.execution_mode == ExecutionMode.PROCESS:
                result = await self._execute_in_process(agent_instance, task)
            else:
                raise Exception(f"Unsupported execution mode: {task.execution_mode}")

            execution_time = time.time() - start_time

            # Update task
            task.result = result
            task.completed_at = datetime.now(UTC)

            # Update agent statistics
            agent_instance.total_tasks += 1
            agent_instance.successful_tasks += 1
            agent_instance.average_task_time = (
                agent_instance.average_task_time * 0.9 + execution_time * 0.1
            )

            # Update metrics
            self.metrics["tasks_completed"] += 1
            self.metrics["avg_task_time"] = (
                self.metrics["avg_task_time"] * 0.9 + execution_time * 0.1
            )

            logger.debug(f"✅ Tarefa {task.id} concluída em {execution_time:.2f}s")

        except Exception as e:
            # Handle task error
            task.error = str(e)
            task.completed_at = datetime.now(UTC)

            if agent_instance:
                agent_instance.failed_tasks += 1
                agent_instance.status = (
                    AgentStatus.ERROR
                    if task.retry_count >= task.max_retries
                    else AgentStatus.IDLE
                )

            self.metrics["tasks_failed"] += 1

            logger.error(f"❌ Tarefa {task.id} falhou: {e}")

            # Retry if possible
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                await asyncio.sleep(self.config.task_retry_delay)
                await self.task_queue.put(
                    (1, time.time(), task)
                )  # High priority for retry
                logger.info(f"🔄 Tentativa {task.retry_count} para tarefa {task.id}")

        finally:
            # Clean up
            if agent_instance:
                agent_instance.status = AgentStatus.IDLE
                agent_instance.current_task_id = None
                agent_instance.last_activity = datetime.now(UTC)

            # Move task to completed
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            self.completed_tasks[task.id] = task

    async def _execute_async(
        self, agent_instance: AgentInstance, task: AgentTask
    ) -> Any:
        """Executar tarefa assíncrona"""

        agent = agent_instance.instance
        method = getattr(agent, task.method)

        if asyncio.iscoroutinefunction(method):
            return await method(*task.args, **task.kwargs)
        return method(*task.args, **task.kwargs)

    async def _execute_in_thread(
        self, agent_instance: AgentInstance, task: AgentTask
    ) -> Any:
        """Executar tarefa em thread"""

        if not self.thread_pool:
            raise Exception("Thread pool not available")

        loop = asyncio.get_event_loop()

        def sync_execute():
            agent = agent_instance.instance
            method = getattr(agent, task.method)
            return method(*task.args, **task.kwargs)

        return await loop.run_in_executor(self.thread_pool, sync_execute)

    async def _execute_in_process(
        self, agent_instance: AgentInstance, task: AgentTask
    ) -> Any:
        """Executar tarefa em processo separado"""

        if not self.process_pool:
            raise Exception("Process pool not available")

        # Note: This is a simplified implementation
        # For full process execution, we'd need to serialize agent state
        raise NotImplementedError("Process execution not fully implemented")

    async def _get_available_agent(self, agent_type: str) -> AgentInstance | None:
        """Obter agente disponível"""

        if agent_type not in self.agent_pools:
            return None

        for agent in self.agent_pools[agent_type]:
            if agent.status == AgentStatus.IDLE:
                return agent

        return None

    async def _scale_up_pool(self, agent_type: str) -> bool:
        """Escalar pool para cima"""

        if agent_type not in self.agent_pools:
            return False

        current_size = len(self.agent_pools[agent_type])
        if current_size >= self.config.max_agents_per_type:
            return False

        # Create new agent
        new_agent = await self._create_agent_instance(agent_type)
        if new_agent:
            self.agent_pools[agent_type].append(new_agent)
            logger.info(
                f"✅ Pool '{agent_type}' escalado para {current_size + 1} agentes"
            )
            return True

        return False

    async def _scale_down_pool(self, agent_type: str) -> bool:
        """Escalar pool para baixo"""

        if agent_type not in self.agent_pools:
            return False

        current_size = len(self.agent_pools[agent_type])
        if current_size <= self.config.min_agents_per_type:
            return False

        # Find idle agent to remove
        for i, agent in enumerate(self.agent_pools[agent_type]):
            if agent.status == AgentStatus.IDLE:
                # Check if idle for long enough
                idle_time = (datetime.now(UTC) - agent.last_activity).total_seconds()
                if idle_time > self.config.agent_idle_timeout:
                    self.agent_pools[agent_type].pop(i)
                    logger.info(
                        f"✅ Pool '{agent_type}' reduzido para {current_size - 1} agentes"
                    )
                    return True

        return False

    async def _start_monitoring_tasks(self):
        """Iniciar tasks de monitoramento"""

        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("✅ Tasks de monitoramento iniciadas")

    async def _health_check_loop(self):
        """Loop de health check"""

        while self._running:
            try:
                await self._perform_health_checks()
                await self._auto_scale_pools()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                logger.error(f"❌ Erro no health check: {e}")
                await asyncio.sleep(5.0)

    async def _cleanup_loop(self):
        """Loop de limpeza"""

        while self._running:
            try:
                await self._cleanup_completed_tasks()
                await asyncio.sleep(self.config.cleanup_interval)
            except Exception as e:
                logger.error(f"❌ Erro na limpeza: {e}")
                await asyncio.sleep(5.0)

    async def _perform_health_checks(self):
        """Realizar health checks dos agentes"""

        for agent_type, agents in self.agent_pools.items():
            for agent in agents:
                # Check if agent is stuck
                if agent.status == AgentStatus.BUSY:
                    time_since_activity = (
                        datetime.now(UTC) - agent.last_activity
                    ).total_seconds()
                    if time_since_activity > self.config.task_timeout_default:
                        logger.warning(f"⚠️ Agente {agent.id} possivelmente travado")
                        agent.status = AgentStatus.ERROR

    async def _auto_scale_pools(self):
        """Auto-scaling dos pools"""

        for agent_type, agents in self.agent_pools.items():
            if not agents:
                continue

            # Calculate utilization
            busy_count = sum(1 for agent in agents if agent.status == AgentStatus.BUSY)
            utilization = busy_count / len(agents)

            # Scale up if needed
            if utilization > self.config.scale_up_threshold:
                await self._scale_up_pool(agent_type)

            # Scale down if needed
            elif utilization < self.config.scale_down_threshold:
                await self._scale_down_pool(agent_type)

    async def _cleanup_completed_tasks(self):
        """Limpar tasks antigas"""

        # Keep only last 1000 completed tasks
        if len(self.completed_tasks) > 1000:
            # Sort by completion time and keep newest 1000
            sorted_tasks = sorted(
                self.completed_tasks.items(),
                key=lambda x: x[1].completed_at or datetime.min,
                reverse=True,
            )

            self.completed_tasks = dict(sorted_tasks[:1000])

    def get_pool_status(self) -> dict[str, Any]:
        """Obter status dos pools"""

        status = {
            "pools": {},
            "metrics": self.metrics.copy(),
            "queue_size": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
        }

        for agent_type, agents in self.agent_pools.items():
            pool_status = {
                "total_agents": len(agents),
                "idle_agents": sum(1 for a in agents if a.status == AgentStatus.IDLE),
                "busy_agents": sum(1 for a in agents if a.status == AgentStatus.BUSY),
                "error_agents": sum(1 for a in agents if a.status == AgentStatus.ERROR),
                "avg_task_time": (
                    sum(a.average_task_time for a in agents) / len(agents)
                    if agents
                    else 0
                ),
                "total_tasks": sum(a.total_tasks for a in agents),
                "successful_tasks": sum(a.successful_tasks for a in agents),
                "failed_tasks": sum(a.failed_tasks for a in agents),
            }
            status["pools"][agent_type] = pool_status

        return status

    async def shutdown(self):
        """Shutdown graceful do pool"""

        logger.info("🔄 Iniciando shutdown do pool de agentes...")

        self._running = False

        # Cancel monitoring tasks
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Cancel worker tasks
        for task in self._worker_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)

        # Shutdown execution pools
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        if self.process_pool:
            self.process_pool.shutdown(wait=True)

        logger.info("✅ Pool de agentes finalizado")


# Singleton instance
_agent_pool_manager: AgentPoolManager | None = None


async def get_agent_pool_manager() -> AgentPoolManager:
    """Obter instância singleton do pool manager"""

    global _agent_pool_manager

    if _agent_pool_manager is None:
        config = PoolConfig()
        _agent_pool_manager = AgentPoolManager(config)
        await _agent_pool_manager.initialize()

    return _agent_pool_manager


async def cleanup_agent_pool():
    """Cleanup global do pool de agentes"""

    global _agent_pool_manager

    if _agent_pool_manager:
        await _agent_pool_manager.shutdown()
        _agent_pool_manager = None


if __name__ == "__main__":
    # Teste do sistema
    import asyncio

    # Mock agent for testing
    class MockAgent:
        def __init__(self, name: str):
            self.name = name

        async def investigate(self, query: str) -> dict[str, Any]:
            await asyncio.sleep(0.1)  # Simulate work
            return {"result": f"Investigation of '{query}' by {self.name}"}

        async def analyze(self, data: dict) -> dict[str, Any]:
            await asyncio.sleep(0.05)  # Simulate work
            return {"analysis": f"Analysis by {self.name}", "data_size": len(data)}

    async def test_agent_pool():
        """Teste completo do pool de agentes"""

        print("🧪 Testando pool de agentes...")

        # Get pool manager
        pool = await get_agent_pool_manager()

        # Register agent factories
        pool.register_agent_factory("investigator", lambda: MockAgent("Investigator"))
        pool.register_agent_factory("analyst", lambda: MockAgent("Analyst"))

        # Create pools
        await pool.create_agent_pool("investigator", 2)
        await pool.create_agent_pool("analyst", 2)

        # Submit tasks
        task_ids = []

        for i in range(5):
            task_id = await pool.submit_task(
                "investigator",
                "investigate",
                f"Query {i}",
                priority=TaskPriority.NORMAL,
            )
            task_ids.append(task_id)

        for i in range(3):
            task_id = await pool.submit_task(
                "analyst",
                "analyze",
                {"data": f"dataset_{i}"},
                priority=TaskPriority.HIGH,
            )
            task_ids.append(task_id)

        # Wait for results
        results = []
        for task_id in task_ids:
            try:
                result = await pool.get_task_result(task_id, timeout=10.0)
                results.append(result)
                print(f"✅ Task {task_id}: {result}")
            except Exception as e:
                print(f"❌ Task {task_id} failed: {e}")

        # Check pool status
        status = pool.get_pool_status()
        print(f"📊 Pool status: {status['metrics']['tasks_completed']} tasks completed")

        # Cleanup
        await cleanup_agent_pool()
        print("✅ Teste concluído!")

    asyncio.run(test_agent_pool())
