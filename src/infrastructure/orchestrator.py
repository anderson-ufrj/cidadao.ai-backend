"""
Orchestrador Central do Sistema Cidadão.AI
Integra todos os subsistemas: Database, Cache, ML, Monitoring, Agent Pool
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
from contextlib import asynccontextmanager
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field
import structlog

# Import all infrastructure components
from .database import get_database_manager, cleanup_database, DatabaseManager
from .cache_system import get_cache_manager, cleanup_cache, AdvancedCacheManager
from .monitoring_service import get_monitoring_manager, cleanup_monitoring, ObservabilityManager
from .agent_pool import get_agent_pool_manager, cleanup_agent_pool, AgentPoolManager

# Import ML components
try:
    from ..ml.advanced_pipeline import get_ml_pipeline_manager, MLPipelineManager
    from ..ml.hf_integration import get_cidadao_manager, CidadaoAIHubManager
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Import agent system
try:
    from ..agents.abaporu import MasterAgent
    from ..agents.zumbi import InvestigatorAgent
    from ..agents.anita import AnalystAgent
    from ..agents.tiradentes import ReporterAgent
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

logger = structlog.get_logger(__name__)


class SystemStatus(Enum):
    """Status do sistema"""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    SHUTDOWN = "shutdown"
    ERROR = "error"


class ComponentStatus(Enum):
    """Status de componente"""
    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class ComponentHealth:
    """Status de saúde de componente"""
    name: str
    status: ComponentStatus
    health_score: float = 0.0  # 0-1
    error_message: Optional[str] = None
    last_check: datetime = field(default_factory=datetime.utcnow)
    uptime_seconds: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)


class OrchestratorConfig(BaseModel):
    """Configuração do orchestrador"""
    
    # System settings
    system_name: str = "cidadao-ai"
    version: str = "1.0.0"
    environment: str = "production"
    
    # Component enabling
    enable_database: bool = True
    enable_cache: bool = True
    enable_monitoring: bool = True
    enable_agent_pool: bool = True
    enable_ml_pipeline: bool = True
    enable_cidadao_gpt: bool = True
    
    # Health check settings
    health_check_interval: float = 30.0
    component_timeout: float = 10.0
    max_retries: int = 3
    retry_delay: float = 5.0
    
    # Graceful shutdown
    shutdown_timeout: float = 30.0
    force_shutdown_after: float = 60.0
    
    # Performance
    startup_timeout: float = 120.0
    parallel_initialization: bool = True


class CidadaoAIOrchestrator:
    """Orchestrador central do sistema"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.status = SystemStatus.INITIALIZING
        self.start_time = datetime.utcnow()
        
        # Component managers
        self.components: Dict[str, Any] = {}
        self.component_health: Dict[str, ComponentHealth] = {}
        
        # Control
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Initialization tracking
        self._initialization_order = [
            "monitoring", "database", "cache", "ml_pipeline", 
            "cidadao_gpt", "agent_pool"
        ]
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Configurar handlers de sinal para shutdown graceful"""
        
        def signal_handler(signum, frame):
            logger.info(f"🛑 Recebido sinal {signum}, iniciando shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self) -> bool:
        """Inicializar todos os componentes do sistema"""
        
        logger.info(f"🚀 Inicializando {self.config.system_name} v{self.config.version}...")
        
        try:
            # Initialize components
            if self.config.parallel_initialization:
                success = await self._initialize_parallel()
            else:
                success = await self._initialize_sequential()
            
            if success:
                # Start health monitoring
                await self._start_health_monitoring()
                
                # Register agent factories if available
                if AGENTS_AVAILABLE and self.config.enable_agent_pool:
                    await self._setup_agent_factories()
                
                self.status = SystemStatus.HEALTHY
                self._running = True
                
                uptime = (datetime.utcnow() - self.start_time).total_seconds()
                logger.info(f"✅ Sistema inicializado com sucesso em {uptime:.1f}s")
                
                return True
            else:
                self.status = SystemStatus.ERROR
                logger.error("❌ Falha na inicialização do sistema")
                return False
                
        except asyncio.TimeoutError:
            self.status = SystemStatus.ERROR
            logger.error(f"❌ Timeout na inicialização ({self.config.startup_timeout}s)")
            return False
        except Exception as e:
            self.status = SystemStatus.ERROR
            logger.error(f"❌ Erro na inicialização: {e}")
            return False
    
    async def _initialize_parallel(self) -> bool:
        """Inicialização paralela de componentes"""
        
        logger.info("⚡ Inicializando componentes em paralelo...")
        
        # Create initialization tasks
        tasks = []
        
        if self.config.enable_monitoring:
            tasks.append(self._init_component("monitoring", get_monitoring_manager))
        
        if self.config.enable_database:
            tasks.append(self._init_component("database", get_database_manager))
        
        if self.config.enable_cache:
            tasks.append(self._init_component("cache", get_cache_manager))
        
        if self.config.enable_ml_pipeline and ML_AVAILABLE:
            tasks.append(self._init_component("ml_pipeline", get_ml_pipeline_manager))
        
        if self.config.enable_cidadao_gpt and ML_AVAILABLE:
            tasks.append(self._init_component("cidadao_gpt", get_cidadao_manager))
        
        if self.config.enable_agent_pool:
            tasks.append(self._init_component("agent_pool", get_agent_pool_manager))
        
        # Wait for all components
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.startup_timeout
            )
            
            # Check results
            success_count = sum(1 for result in results if result is True)
            total_count = len(results)
            
            logger.info(f"📊 Componentes inicializados: {success_count}/{total_count}")
            
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização paralela: {e}")
            return False
    
    async def _initialize_sequential(self) -> bool:
        """Inicialização sequencial de componentes"""
        
        logger.info("🔄 Inicializando componentes sequencialmente...")
        
        for component_name in self._initialization_order:
            
            if component_name == "monitoring" and self.config.enable_monitoring:
                success = await self._init_component("monitoring", get_monitoring_manager)
            elif component_name == "database" and self.config.enable_database:
                success = await self._init_component("database", get_database_manager)
            elif component_name == "cache" and self.config.enable_cache:
                success = await self._init_component("cache", get_cache_manager)
            elif component_name == "ml_pipeline" and self.config.enable_ml_pipeline and ML_AVAILABLE:
                success = await self._init_component("ml_pipeline", get_ml_pipeline_manager)
            elif component_name == "cidadao_gpt" and self.config.enable_cidadao_gpt and ML_AVAILABLE:
                success = await self._init_component("cidadao_gpt", get_cidadao_manager)
            elif component_name == "agent_pool" and self.config.enable_agent_pool:
                success = await self._init_component("agent_pool", get_agent_pool_manager)
            else:
                continue
            
            if not success:
                logger.error(f"❌ Falha ao inicializar {component_name}")
                return False
        
        return True
    
    async def _init_component(self, name: str, factory_func) -> bool:
        """Inicializar componente individual"""
        
        self.component_health[name] = ComponentHealth(
            name=name,
            status=ComponentStatus.INITIALIZING
        )
        
        logger.info(f"🔄 Inicializando {name}...")
        
        start_time = datetime.utcnow()
        
        try:
            # Initialize with retries
            for attempt in range(self.config.max_retries):
                try:
                    component = await factory_func()
                    
                    self.components[name] = component
                    self.component_health[name].status = ComponentStatus.READY
                    
                    uptime = (datetime.utcnow() - start_time).total_seconds()
                    self.component_health[name].uptime_seconds = uptime
                    self.component_health[name].health_score = 1.0
                    
                    logger.info(f"✅ {name} inicializado em {uptime:.1f}s")
                    return True
                    
                except Exception as e:
                    logger.warning(f"⚠️ Tentativa {attempt + 1} falhou para {name}: {e}")
                    
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                    else:
                        self.component_health[name].status = ComponentStatus.ERROR
                        self.component_health[name].error_message = str(e)
                        self.component_health[name].health_score = 0.0
                        
                        logger.error(f"❌ {name} falhou após {self.config.max_retries} tentativas")
                        return False
        
        except Exception as e:
            self.component_health[name].status = ComponentStatus.ERROR
            self.component_health[name].error_message = str(e)
            logger.error(f"❌ Erro crítico ao inicializar {name}: {e}")
            return False
    
    async def _setup_agent_factories(self):
        """Configurar factories de agentes no pool"""
        
        if "agent_pool" not in self.components:
            return
        
        agent_pool = self.components["agent_pool"]
        
        try:
            # Register agent factories
            agent_pool.register_agent_factory("master", self._create_master_agent)
            agent_pool.register_agent_factory("investigator", self._create_investigator_agent)
            agent_pool.register_agent_factory("analyst", self._create_analyst_agent)
            agent_pool.register_agent_factory("reporter", self._create_reporter_agent)
            
            # Create initial pools
            await agent_pool.create_agent_pool("investigator", 3)
            await agent_pool.create_agent_pool("analyst", 2)
            await agent_pool.create_agent_pool("reporter", 2)
            await agent_pool.create_agent_pool("master", 1)
            
            logger.info("✅ Agent factories configuradas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar agent factories: {e}")
    
    async def _create_master_agent(self):
        """Factory para MasterAgent"""
        if AGENTS_AVAILABLE:
            return MasterAgent()
        return None
    
    async def _create_investigator_agent(self):
        """Factory para InvestigatorAgent"""
        if AGENTS_AVAILABLE:
            return InvestigatorAgent()
        return None
    
    async def _create_analyst_agent(self):
        """Factory para AnalystAgent"""
        if AGENTS_AVAILABLE:
            return AnalystAgent()
        return None
    
    async def _create_reporter_agent(self):
        """Factory para ReporterAgent"""
        if AGENTS_AVAILABLE:
            return ReporterAgent()
        return None
    
    async def _start_health_monitoring(self):
        """Iniciar monitoramento de saúde"""
        
        async def health_check_loop():
            while self._running and not self._shutdown_event.is_set():
                try:
                    await self._perform_health_checks()
                    await asyncio.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"❌ Erro no health check: {e}")
                    await asyncio.sleep(5.0)
        
        self._health_check_task = asyncio.create_task(health_check_loop())
        logger.info("✅ Health monitoring iniciado")
    
    async def _perform_health_checks(self):
        """Realizar health checks de todos os componentes"""
        
        for name, component in self.components.items():
            try:
                health_score = await self._check_component_health(name, component)
                self.component_health[name].health_score = health_score
                self.component_health[name].last_check = datetime.utcnow()
                
                # Update status based on health score
                if health_score >= 0.8:
                    self.component_health[name].status = ComponentStatus.READY
                elif health_score >= 0.5:
                    if self.component_health[name].status == ComponentStatus.READY:
                        logger.warning(f"⚠️ {name} degradado (score: {health_score:.2f})")
                else:
                    if self.component_health[name].status != ComponentStatus.ERROR:
                        logger.error(f"❌ {name} com problemas (score: {health_score:.2f})")
                        self.component_health[name].status = ComponentStatus.ERROR
                
            except Exception as e:
                logger.error(f"❌ Health check falhou para {name}: {e}")
                self.component_health[name].health_score = 0.0
                self.component_health[name].status = ComponentStatus.ERROR
                self.component_health[name].error_message = str(e)
        
        # Update overall system status
        await self._update_system_status()
    
    async def _check_component_health(self, name: str, component: Any) -> float:
        """Verificar saúde de componente específico"""
        
        try:
            if hasattr(component, 'health_check'):
                health_result = await component.health_check()
                
                if isinstance(health_result, dict):
                    # Parse health result
                    overall_status = health_result.get("overall", {}).get("status", "unknown")
                    
                    if overall_status == "healthy":
                        return 1.0
                    elif overall_status == "degraded":
                        return 0.7
                    elif overall_status == "unhealthy":
                        return 0.3
                    else:
                        return 0.5
                
                elif isinstance(health_result, bool):
                    return 1.0 if health_result else 0.0
                else:
                    return 0.5
            
            elif hasattr(component, 'get_health_status'):
                health_status = await component.get_health_status()
                
                # Calculate score based on component statuses
                healthy_components = 0
                total_components = 0
                
                for comp_name, comp_health in health_status.items():
                    if isinstance(comp_health, dict):
                        total_components += 1
                        if comp_health.get("status") == "healthy":
                            healthy_components += 1
                
                return healthy_components / total_components if total_components > 0 else 0.5
            
            else:
                # Basic connectivity test
                if hasattr(component, 'ping'):
                    await component.ping()
                    return 1.0
                
                # Component exists and is accessible
                return 0.8
        
        except Exception as e:
            logger.debug(f"Health check error for {name}: {e}")
            return 0.0
    
    async def _update_system_status(self):
        """Atualizar status geral do sistema"""
        
        if not self.component_health:
            self.status = SystemStatus.INITIALIZING
            return
        
        # Calculate overall health
        health_scores = [h.health_score for h in self.component_health.values()]
        avg_health = sum(health_scores) / len(health_scores)
        
        error_count = sum(1 for h in self.component_health.values() 
                         if h.status == ComponentStatus.ERROR)
        
        if error_count == 0 and avg_health >= 0.8:
            new_status = SystemStatus.HEALTHY
        elif error_count <= len(self.component_health) // 2 and avg_health >= 0.5:
            new_status = SystemStatus.DEGRADED
        else:
            new_status = SystemStatus.UNHEALTHY
        
        # Log status changes
        if new_status != self.status:
            logger.info(f"📊 Status do sistema: {self.status.value} → {new_status.value}")
            self.status = new_status
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Obter saúde completa do sistema"""
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        health = {
            "system": {
                "name": self.config.system_name,
                "version": self.config.version,
                "environment": self.config.environment,
                "status": self.status.value,
                "uptime_seconds": uptime,
                "uptime_human": self._format_uptime(uptime)
            },
            "components": {},
            "summary": {
                "total_components": len(self.component_health),
                "healthy_components": sum(1 for h in self.component_health.values() 
                                        if h.status == ComponentStatus.READY),
                "error_components": sum(1 for h in self.component_health.values() 
                                      if h.status == ComponentStatus.ERROR),
                "avg_health_score": sum(h.health_score for h in self.component_health.values()) / len(self.component_health) if self.component_health else 0.0
            }
        }
        
        # Component details
        for name, component_health in self.component_health.items():
            health["components"][name] = {
                "status": component_health.status.value,
                "health_score": component_health.health_score,
                "uptime_seconds": component_health.uptime_seconds,
                "last_check": component_health.last_check.isoformat(),
                "error_message": component_health.error_message
            }
        
        return health
    
    def _format_uptime(self, seconds: float) -> str:
        """Formatar uptime legível"""
        
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {secs}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    async def submit_investigation(self, query: str, **kwargs) -> str:
        """Submeter investigação usando o sistema integrado"""
        
        if "agent_pool" not in self.components:
            raise Exception("Agent pool não disponível")
        
        agent_pool = self.components["agent_pool"]
        
        # Submit to master agent
        task_id = await agent_pool.submit_task(
            "master",
            "investigate",
            query,
            **kwargs
        )
        
        return task_id
    
    async def get_investigation_result(self, task_id: str, timeout: float = 60.0) -> Any:
        """Obter resultado de investigação"""
        
        if "agent_pool" not in self.components:
            raise Exception("Agent pool não disponível")
        
        agent_pool = self.components["agent_pool"]
        return await agent_pool.get_task_result(task_id, timeout)
    
    async def analyze_with_ml(self, text: str) -> Dict[str, Any]:
        """Analisar texto usando Cidadão.AI"""
        
        if "cidadao_gpt" not in self.components:
            raise Exception("Cidadão.AI não disponível")
        
        cidadao_manager = self.components["cidadao_gpt"]
        return cidadao_manager.analyze_text(text)
    
    async def cache_data(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Cache de dados"""
        
        if "cache" not in self.components:
            return False
        
        cache_manager = self.components["cache"]
        return await cache_manager.set(key, value, ttl)
    
    async def get_cached_data(self, key: str, default: Any = None) -> Any:
        """Obter dados do cache"""
        
        if "cache" not in self.components:
            return default
        
        cache_manager = self.components["cache"]
        return await cache_manager.get(key, default)
    
    async def log_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Log de métrica"""
        
        if "monitoring" not in self.components:
            return
        
        monitoring = self.components["monitoring"]
        if hasattr(monitoring, 'track_ml_inference_time'):
            monitoring.track_ml_inference_time(value, metric_name)
    
    async def shutdown(self):
        """Shutdown graceful do sistema"""
        
        if self.status == SystemStatus.SHUTDOWN:
            return
        
        logger.info("🛑 Iniciando shutdown graceful...")
        self.status = SystemStatus.SHUTDOWN
        self._running = False
        self._shutdown_event.set()
        
        # Cancel health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await asyncio.wait_for(self._health_check_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        
        # Shutdown components in reverse order
        shutdown_order = list(reversed(self._initialization_order))
        
        for component_name in shutdown_order:
            if component_name in self.components:
                await self._shutdown_component(component_name)
        
        logger.info("✅ Shutdown concluído")
    
    async def _shutdown_component(self, name: str):
        """Shutdown de componente individual"""
        
        logger.info(f"🔄 Finalizando {name}...")
        
        try:
            component = self.components[name]
            
            # Try component-specific shutdown
            if hasattr(component, 'shutdown'):
                await asyncio.wait_for(
                    component.shutdown(),
                    timeout=self.config.shutdown_timeout
                )
            elif hasattr(component, 'cleanup'):
                await asyncio.wait_for(
                    component.cleanup(),
                    timeout=self.config.shutdown_timeout
                )
            
            # Call global cleanup functions
            if name == "database":
                await cleanup_database()
            elif name == "cache":
                await cleanup_cache()
            elif name == "monitoring":
                await cleanup_monitoring()
            elif name == "agent_pool":
                await cleanup_agent_pool()
            
            self.component_health[name].status = ComponentStatus.SHUTDOWN
            logger.info(f"✅ {name} finalizado")
            
        except asyncio.TimeoutError:
            logger.warning(f"⚠️ Timeout ao finalizar {name}")
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar {name}: {e}")
    
    async def wait_for_shutdown(self):
        """Aguardar shutdown"""
        await self._shutdown_event.wait()
    
    @asynccontextmanager
    async def lifespan(self):
        """Context manager para lifecycle do sistema"""
        
        try:
            success = await self.initialize()
            if not success:
                raise Exception("Falha na inicialização")
            
            yield self
            
        finally:
            await self.shutdown()


# Singleton instance
_orchestrator: Optional[CidadaoAIOrchestrator] = None

async def get_orchestrator(config: Optional[OrchestratorConfig] = None) -> CidadaoAIOrchestrator:
    """Obter instância singleton do orchestrador"""
    
    global _orchestrator
    
    if _orchestrator is None:
        config = config or OrchestratorConfig()
        _orchestrator = CidadaoAIOrchestrator(config)
    
    return _orchestrator


async def initialize_system(config: Optional[OrchestratorConfig] = None) -> CidadaoAIOrchestrator:
    """Inicializar sistema completo"""
    
    orchestrator = await get_orchestrator(config)
    
    success = await orchestrator.initialize()
    if not success:
        raise Exception("Falha na inicialização do sistema")
    
    return orchestrator


if __name__ == "__main__":
    # Teste do orchestrador
    import asyncio
    
    async def test_orchestrator():
        """Teste completo do orchestrador"""
        
        print("🧪 Testando orchestrador do sistema...")
        
        # Custom config for testing
        config = OrchestratorConfig(
            enable_agent_pool=True,
            enable_ml_pipeline=False,  # Skip heavy ML for testing
            health_check_interval=5.0
        )
        
        try:
            # Initialize system
            orchestrator = await initialize_system(config)
            
            # Check system health
            health = await orchestrator.get_system_health()
            print(f"✅ Sistema inicializado: {health['system']['status']}")
            print(f"📊 Componentes: {health['summary']['healthy_components']}/{health['summary']['total_components']} saudáveis")
            
            # Test investigation if agents available
            if AGENTS_AVAILABLE and "agent_pool" in orchestrator.components:
                try:
                    task_id = await orchestrator.submit_investigation(
                        "Contratos suspeitos de 2024"
                    )
                    print(f"✅ Investigação submetida: {task_id}")
                    
                    # result = await orchestrator.get_investigation_result(task_id, timeout=10.0)
                    # print(f"✅ Resultado: {result}")
                except Exception as e:
                    print(f"⚠️ Teste de investigação falhou: {e}")
            
            # Test cache
            if "cache" in orchestrator.components:
                await orchestrator.cache_data("test_key", {"test": "data"})
                cached = await orchestrator.get_cached_data("test_key")
                print(f"✅ Cache funcionando: {cached is not None}")
            
            # Wait a bit to see health checks
            print("⏳ Aguardando health checks...")
            await asyncio.sleep(6)
            
            # Final health check
            final_health = await orchestrator.get_system_health()
            print(f"✅ Status final: {final_health['system']['status']}")
            
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
        
        finally:
            # Shutdown
            if _orchestrator:
                await _orchestrator.shutdown()
        
        print("✅ Teste concluído!")
    
    asyncio.run(test_orchestrator())