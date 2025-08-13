# ⚙️ Cidadão.AI Core System

## 📋 Overview

The **Core System** provides the foundational **infrastructure**, **configuration management**, and **shared utilities** that power the entire Cidadão.AI platform. This module establishes **system-wide standards**, **logging frameworks**, **error handling**, **monitoring**, and **configuration management** for enterprise-grade operation.

## 🏗️ Architecture

```
src/core/
├── config.py           # Comprehensive configuration management
├── logging.py          # Structured logging system
├── exceptions.py       # Custom exception hierarchy
├── constants.py        # System-wide constants
├── audit.py            # Enterprise audit logging
├── monitoring.py       # Performance monitoring & metrics
├── cache.py           # Caching abstractions
├── oauth_config.py    # OAuth2 configuration
└── __init__.py        # Core module initialization
```

## 🔧 Configuration Management (config.py)

### Enterprise Configuration System

The configuration system uses **Pydantic Settings** for **type-safe**, **environment-aware** configuration management with **validation** and **documentation**.

#### Comprehensive Settings Model
```python
class Settings(BaseSettings):
    """
    Enterprise-grade configuration management
    
    Features:
    - Type-safe configuration with Pydantic
    - Environment variable integration
    - Validation and error handling
    - Multiple environment support
    - Secrets management
    - Feature flags
    - Performance tuning parameters
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application Core
    app_name: str = Field(default="cidadao-ai", description="Application name")
    app_env: str = Field(default="development", description="Environment")
    app_version: str = Field(default="1.0.0", description="Version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of workers")
    
    # Database Configuration (PostgreSQL)
    database_url: str = Field(
        default="postgresql://cidadao:cidadao123@localhost:5432/cidadao_ai",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=10, description="DB pool size")
    database_pool_overflow: int = Field(default=20, description="DB pool overflow")
    database_pool_timeout: int = Field(default=30, description="DB pool timeout")
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_password: Optional[SecretStr] = Field(default=None, description="Redis password")
    redis_pool_size: int = Field(default=10, description="Redis pool size")
```

#### Multi-Provider LLM Configuration
```python
    # LLM Configuration with Multiple Providers
    llm_provider: str = Field(
        default="groq",
        description="LLM provider (groq, together, huggingface)"
    )
    llm_model_name: str = Field(
        default="mixtral-8x7b-32768",
        description="LLM model name"
    )
    llm_temperature: float = Field(default=0.7, description="LLM temperature")
    llm_max_tokens: int = Field(default=2048, description="Max tokens")
    llm_top_p: float = Field(default=0.9, description="Top-p sampling")
    llm_stream: bool = Field(default=True, description="Enable streaming")
    
    # Provider-Specific API Keys
    groq_api_key: Optional[SecretStr] = Field(default=None, description="Groq API key")
    groq_api_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        description="Groq base URL"
    )
    
    together_api_key: Optional[SecretStr] = Field(default=None, description="Together API key")
    together_api_base_url: str = Field(
        default="https://api.together.xyz/v1",
        description="Together base URL"
    )
    
    huggingface_api_key: Optional[SecretStr] = Field(default=None, description="HuggingFace API key")
    huggingface_model_id: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.2",
        description="HuggingFace model ID"
    )
```

#### Vector Store & AI Configuration
```python
    # Vector Store Configuration
    vector_store_type: str = Field(
        default="faiss",
        description="Vector store type (faiss, chromadb)"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model"
    )
    embedding_dimension: int = Field(default=384, description="Embedding dimension")
    vector_index_path: Path = Field(
        default=Path("./vector_store/index.faiss"),
        description="Vector index path"
    )
    
    # ChromaDB Configuration
    chroma_persist_directory: Path = Field(
        default=Path("./chroma_db"),
        description="ChromaDB persist directory"
    )
    chroma_collection_name: str = Field(
        default="cidadao_memory",
        description="ChromaDB collection name"
    )
```

#### Security & Authentication
```python
    # Security Configuration
    secret_key: SecretStr = Field(
        default=SecretStr("your-super-secret-key-change-this-in-production"),
        description="Application secret key"
    )
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("your-jwt-secret-key-change-this"),
        description="JWT secret key"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(default=30, description="Access token expiry")
    jwt_refresh_token_expire_days: int = Field(default=7, description="Refresh token expiry")
    bcrypt_rounds: int = Field(default=12, description="Bcrypt rounds")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000", 
            "https://cidadao-ai-frontend.vercel.app",
            "https://*.vercel.app",
            "https://neural-thinker-cidadao-ai-backend.hf.space"
        ],
        description="CORS allowed origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed methods"
    )
    cors_allow_headers: List[str] = Field(default=["*"], description="Allowed headers")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Rate limit per hour")
    rate_limit_per_day: int = Field(default=10000, description="Rate limit per day")
```

#### Advanced Features Configuration
```python
    # ML Configuration
    anomaly_detection_threshold: float = Field(
        default=0.8,
        description="Anomaly detection threshold"
    )
    clustering_min_samples: int = Field(default=5, description="Min clustering samples")
    time_series_seasonality: str = Field(default="yearly", description="Seasonality")
    explainer_max_samples: int = Field(default=100, description="Max explainer samples")
    
    # Feature Flags for Gradual Rollout
    enable_fine_tuning: bool = Field(default=False, description="Enable fine-tuning")
    enable_autonomous_crawling: bool = Field(default=False, description="Enable crawling")
    enable_advanced_visualizations: bool = Field(default=False, description="Advanced viz")
    enable_ethics_guard: bool = Field(default=True, description="Enable ethics guard")
    
    # Development & Debugging
    enable_debug_toolbar: bool = Field(default=True, description="Debug toolbar")
    enable_sql_echo: bool = Field(default=False, description="SQL echo")
    enable_profiling: bool = Field(default=False, description="Enable profiling")
```

#### Configuration Validation & Utilities
```python
    @field_validator("app_env")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if in development mode."""
        return self.app_env == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if in production mode."""
        return self.app_env == "production"
    
    def get_database_url(self, async_mode: bool = True) -> str:
        """Get database URL for async or sync mode."""
        if async_mode and self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url
    
    def dict_for_logging(self) -> Dict[str, Any]:
        """Get safe dict for logging (no secrets)."""
        data = self.model_dump()
        # Remove sensitive fields
        sensitive_fields = [
            "secret_key", "jwt_secret_key", "transparency_api_key",
            "groq_api_key", "together_api_key", "huggingface_api_key",
            "redis_password", "database_url"
        ]
        for field in sensitive_fields:
            if field in data:
                data[field] = "***REDACTED***"
        return data
```

## 📊 Structured Logging System (logging.py)

### Enterprise Logging Framework
```python
import structlog
from typing import Any, Dict
import json
import sys
from datetime import datetime

def configure_logging(
    level: str = "INFO",
    json_format: bool = True,
    include_caller: bool = True
) -> None:
    """
    Configure structured logging for production use
    
    Features:
    - Structured JSON logging
    - Correlation ID tracking
    - Performance metrics
    - Error context capture
    - Security event logging
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            ) if include_caller else structlog.processors.CallsiteParameterAdder(),
            add_correlation_id,
            add_performance_metrics,
            structlog.processors.JSONRenderer() if json_format else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level.upper())),
        logger_factory=structlog.WriteLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

def add_correlation_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID for request tracking"""
    
    # Try to get correlation ID from context
    correlation_id = structlog.contextvars.get_contextvars().get("correlation_id")
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    
    return event_dict

def add_performance_metrics(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add performance metrics to log entries"""
    
    # Add timestamp for performance analysis
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    
    # Add memory usage if available
    try:
        import psutil
        process = psutil.Process()
        event_dict["memory_mb"] = round(process.memory_info().rss / 1024 / 1024, 2)
        event_dict["cpu_percent"] = process.cpu_percent()
    except ImportError:
        pass
    
    return event_dict

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance"""
    return structlog.get_logger(name)

# Specialized loggers for different purposes
def get_security_logger() -> structlog.BoundLogger:
    """Get logger for security events"""
    return structlog.get_logger("security")

def get_performance_logger() -> structlog.BoundLogger:
    """Get logger for performance metrics"""
    return structlog.get_logger("performance")

def get_audit_logger() -> structlog.BoundLogger:
    """Get logger for audit events"""
    return structlog.get_logger("audit")
```

### Logging Usage Patterns
```python
# Basic structured logging
logger = get_logger(__name__)

logger.info(
    "investigation_started",
    investigation_id="inv_001",
    user_id="user123",
    data_source="contracts",
    filters={"year": 2024, "organization": "20000"}
)

# Performance logging
perf_logger = get_performance_logger()

with perf_logger.bind(operation="anomaly_detection"):
    start_time = time.time()
    # ... perform operation ...
    processing_time = time.time() - start_time
    
    perf_logger.info(
        "anomaly_detection_completed",
        processing_time_ms=processing_time * 1000,
        records_processed=1500,
        anomalies_found=23
    )

# Security logging
security_logger = get_security_logger()

security_logger.warning(
    "suspicious_activity_detected",
    user_id="user123",
    activity="excessive_api_calls",
    requests_count=1000,
    time_window="1_hour",
    ip_address="192.168.1.100"
)
```

## 🚨 Exception Management (exceptions.py)

### Custom Exception Hierarchy
```python
class CidadaoAIError(Exception):
    """Base exception for all Cidadão.AI errors"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "CIDADAO_AI_ERROR",
        details: Dict[str, Any] = None,
        cause: Exception = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

# Domain-specific exceptions
class ValidationError(CidadaoAIError):
    """Data validation errors"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": value}
        )

class DataNotFoundError(CidadaoAIError):
    """Data not found errors"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            error_code="DATA_NOT_FOUND",
            details={"resource": resource, "identifier": identifier}
        )

class AuthenticationError(CidadaoAIError):
    """Authentication errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, error_code="AUTHENTICATION_ERROR")

class UnauthorizedError(CidadaoAIError):
    """Authorization errors"""
    def __init__(self, resource: str, action: str):
        super().__init__(
            f"Unauthorized to {action} {resource}",
            error_code="UNAUTHORIZED",
            details={"resource": resource, "action": action}
        )

class RateLimitError(CidadaoAIError):
    """Rate limiting errors"""
    def __init__(self, limit: int, window: str):
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window}",
            error_code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "window": window}
        )

class LLMError(CidadaoAIError):
    """LLM service errors"""
    def __init__(self, provider: str, model: str, message: str):
        super().__init__(
            f"LLM error ({provider}/{model}): {message}",
            error_code="LLM_ERROR",
            details={"provider": provider, "model": model}
        )

class TransparencyAPIError(CidadaoAIError):
    """Portal da Transparência API errors"""
    def __init__(self, endpoint: str, status_code: int, message: str):
        super().__init__(
            f"Transparency API error ({endpoint}): {message}",
            error_code="TRANSPARENCY_API_ERROR",
            details={"endpoint": endpoint, "status_code": status_code}
        )

class AgentExecutionError(CidadaoAIError):
    """Agent execution errors"""
    def __init__(self, agent_name: str, action: str, message: str):
        super().__init__(
            f"Agent {agent_name} failed to {action}: {message}",
            error_code="AGENT_EXECUTION_ERROR",
            details={"agent": agent_name, "action": action}
        )

# Error response creation
def create_error_response(error: CidadaoAIError, status_code: int = 500) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "status": "error",
        "status_code": status_code,
        "error": error.to_dict()
    }
```

## 📈 Performance Monitoring (monitoring.py)

### System Metrics Collection
```python
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import time
from functools import wraps

# Metrics registry
REGISTRY = CollectorRegistry()

# Core metrics
API_REQUESTS_TOTAL = Counter(
    'cidadao_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

API_REQUEST_DURATION = Histogram(
    'cidadao_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint'],
    registry=REGISTRY
)

ACTIVE_INVESTIGATIONS = Gauge(
    'cidadao_active_investigations',
    'Number of active investigations',
    registry=REGISTRY
)

AGENT_OPERATIONS_TOTAL = Counter(
    'cidadao_agent_operations_total',
    'Total agent operations',
    ['agent_name', 'operation', 'status'],
    registry=REGISTRY
)

ANOMALIES_DETECTED_TOTAL = Counter(
    'cidadao_anomalies_detected_total',
    'Total anomalies detected',
    ['anomaly_type', 'severity'],
    registry=REGISTRY
)

def monitor_api_request(func):
    """Decorator to monitor API requests"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status = "success"
            return result
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            
            # Extract endpoint info
            endpoint = getattr(func, '__name__', 'unknown')
            method = kwargs.get('method', 'unknown')
            
            API_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            API_REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    return wrapper

def monitor_agent_operation(agent_name: str, operation: str):
    """Decorator to monitor agent operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                AGENT_OPERATIONS_TOTAL.labels(
                    agent_name=agent_name,
                    operation=operation,
                    status=status
                ).inc()
        
        return wrapper
    return decorator

def record_anomaly_detection(anomaly_type: str, severity: str):
    """Record anomaly detection metrics"""
    ANOMALIES_DETECTED_TOTAL.labels(
        anomaly_type=anomaly_type,
        severity=severity
    ).inc()

def update_active_investigations(count: int):
    """Update active investigations gauge"""
    ACTIVE_INVESTIGATIONS.set(count)
```

## 🛡️ Enterprise Audit System (audit.py)

### Comprehensive Audit Logging
```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import hashlib
import json

class AuditEventType(Enum):
    """Types of audit events"""
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILURE = "authentication_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    API_ACCESS = "api_access"
    INVESTIGATION_STARTED = "investigation_started"
    INVESTIGATION_COMPLETED = "investigation_completed"
    ANOMALY_DETECTED = "anomaly_detected"
    DATA_ACCESS = "data_access"
    SECURITY_VIOLATION = "security_violation"
    COMPLIANCE_CHECK = "compliance_check"
    API_ERROR = "api_error"

class AuditSeverity(Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditContext:
    """Context information for audit events"""
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    host: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None

class AuditLogger:
    """Enterprise audit logging system"""
    
    def __init__(self):
        self.logger = get_audit_logger()
        self._hash_chain = ""  # For integrity verification
    
    async def log_event(
        self,
        event_type: AuditEventType,
        message: str,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        success: bool = True,
        user_id: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log audit event with full context"""
        
        event_data = {
            "event_type": event_type.value,
            "message": message,
            "severity": severity.value,
            "success": success,
            "user_id": user_id,
            "error_code": error_code,
            "error_message": error_message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add context information
        if context:
            event_data["context"] = {
                "ip_address": context.ip_address,
                "user_agent": context.user_agent,
                "host": context.host,
                "session_id": context.session_id,
                "correlation_id": context.correlation_id
            }
        
        # Generate integrity hash
        event_hash = self._generate_event_hash(event_data)
        event_data["event_hash"] = event_hash
        event_data["hash_chain"] = self._hash_chain
        
        # Update hash chain for integrity
        self._hash_chain = hashlib.sha256(
            (self._hash_chain + event_hash).encode()
        ).hexdigest()
        
        # Log the event
        self.logger.info("audit_event", **event_data)
        
        return event_hash
    
    def _generate_event_hash(self, event_data: Dict[str, Any]) -> str:
        """Generate cryptographic hash for event integrity"""
        
        # Create canonical representation for hashing
        canonical_data = json.dumps(event_data, sort_keys=True, default=str)
        event_hash = hashlib.sha256(canonical_data.encode()).hexdigest()
        
        return event_hash
    
    async def verify_integrity(self, events: List[Dict[str, Any]]) -> bool:
        """Verify integrity of audit event chain"""
        
        reconstructed_chain = ""
        
        for event in events:
            event_hash = event.get("event_hash", "")
            expected_chain = event.get("hash_chain", "")
            
            if reconstructed_chain != expected_chain:
                return False
            
            reconstructed_chain = hashlib.sha256(
                (reconstructed_chain + event_hash).encode()
            ).hexdigest()
        
        return True

# Global audit logger instance
audit_logger = AuditLogger()
```

## 🔄 System Constants (constants.py)

### Centralized Constants Management
```python
from enum import Enum

# System-wide constants
class SystemConstants:
    """Core system constants"""
    
    # Application
    APP_NAME = "Cidadão.AI"
    APP_DESCRIPTION = "Plataforma de Transparência Pública com IA"
    API_VERSION = "v1"
    
    # Timeouts (seconds)
    DEFAULT_REQUEST_TIMEOUT = 30
    DATABASE_QUERY_TIMEOUT = 60
    LLM_REQUEST_TIMEOUT = 120
    AGENT_EXECUTION_TIMEOUT = 300
    
    # Limits
    MAX_CONCURRENT_INVESTIGATIONS = 10
    MAX_AGENT_RETRIES = 3
    MAX_FILE_SIZE_MB = 50
    MAX_RESULTS_PER_PAGE = 100
    
    # Cache TTLs (seconds)
    CACHE_TTL_SHORT = 300      # 5 minutes
    CACHE_TTL_MEDIUM = 3600    # 1 hour
    CACHE_TTL_LONG = 86400     # 24 hours
    
    # ML Constants
    ANOMALY_THRESHOLD_DEFAULT = 0.8
    CONFIDENCE_THRESHOLD_MIN = 0.6
    MIN_SAMPLES_FOR_TRAINING = 100

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"

class InvestigationStatus(Enum):
    """Investigation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataSource(Enum):
    """Supported data sources"""
    CONTRACTS = "contracts"
    EXPENSES = "expenses"
    AGREEMENTS = "agreements"
    BIDDINGS = "biddings"
    SERVANTS = "servants"
    SANCTIONED_COMPANIES = "sanctioned_companies"

class AnomalyType(Enum):
    """Types of anomalies detected"""
    PRICE_OUTLIER = "price_outlier"
    VENDOR_CONCENTRATION = "vendor_concentration"
    TEMPORAL_SUSPICION = "temporal_suspicion"
    DUPLICATE_CONTRACT = "duplicate_contract"
    PAYMENT_IRREGULARITY = "payment_irregularity"
    PATTERN_DEVIATION = "pattern_deviation"

class ReflectionType(Enum):
    """Agent reflection types"""
    QUALITY_ASSESSMENT = "quality_assessment"
    STRATEGY_ADAPTATION = "strategy_adaptation"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE_REVIEW = "performance_review"
```

## 🧪 Usage Examples

### Configuration Usage
```python
from src.core.config import get_settings

# Get settings instance
settings = get_settings()

# Use configuration
print(f"Running {settings.app_name} v{settings.app_version}")
print(f"Environment: {settings.app_env}")
print(f"Debug mode: {settings.debug}")

# Database URL with async support
db_url = settings.get_database_url(async_mode=True)

# Safe logging configuration
log_config = settings.dict_for_logging()
logger.info("application_configured", **log_config)
```

### Structured Logging
```python
from src.core.logging import get_logger, get_security_logger

# Basic logging
logger = get_logger(__name__)

logger.info(
    "user_investigation_started",
    user_id="user123",
    investigation_id="inv_001",
    data_source="contracts",
    organization="20000"
)

# Security logging
security_logger = get_security_logger()

security_logger.warning(
    "failed_authentication_attempt",
    ip_address="192.168.1.100",
    attempted_username="admin",
    failure_reason="invalid_password"
)
```

### Exception Handling
```python
from src.core.exceptions import ValidationError, DataNotFoundError, create_error_response

try:
    # Some operation that might fail
    result = await process_investigation(data)
except ValidationError as e:
    # Handle validation error
    error_response = create_error_response(e, 400)
    return JSONResponse(content=error_response, status_code=400)
except DataNotFoundError as e:
    # Handle not found error
    error_response = create_error_response(e, 404)
    return JSONResponse(content=error_response, status_code=404)
```

### Monitoring Integration
```python
from src.core.monitoring import monitor_api_request, record_anomaly_detection

@monitor_api_request
async def investigate_contracts(request: InvestigationRequest):
    """Monitored API endpoint"""
    
    # Process investigation
    results = await process_investigation(request)
    
    # Record detected anomalies
    for anomaly in results.get("anomalies", []):
        record_anomaly_detection(
            anomaly_type=anomaly["type"],
            severity=anomaly["severity"]
        )
    
    return results
```

### Audit Logging
```python
from src.core.audit import audit_logger, AuditEventType, AuditSeverity, AuditContext

# Log security event
context = AuditContext(
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    user_id="user123"
)

await audit_logger.log_event(
    event_type=AuditEventType.INVESTIGATION_STARTED,
    message="User started transparency investigation",
    severity=AuditSeverity.MEDIUM,
    success=True,
    user_id="user123",
    details={"investigation_type": "contracts", "organization": "20000"},
    context=context
)
```

---

This comprehensive core system provides the **foundational infrastructure** for enterprise-grade operation, ensuring **consistency**, **reliability**, and **observability** across the entire Cidadão.AI platform.