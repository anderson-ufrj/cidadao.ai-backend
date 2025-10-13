"""
Module: core.constants
Description: Application constants and enums
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from enum import Enum
from typing import Final

# Application metadata
APP_NAME: Final[str] = "Cidadão.AI"
APP_DESCRIPTION: Final[str] = (
    "Sistema multi-agente de IA para transparência de dados públicos"
)
APP_VERSION: Final[str] = "1.0.0"
APP_AUTHOR: Final[str] = "Anderson H. Silva"
APP_LICENSE: Final[str] = "Proprietary - All rights reserved"

# API versioning
API_V1_PREFIX: Final[str] = "/api/v1"
CURRENT_API_VERSION: Final[str] = "v1"

# Agent names
MASTER_AGENT: Final[str] = "MasterAgent"
CONTEXT_MEMORY_AGENT: Final[str] = "ContextMemoryAgent"
INVESTIGATOR_AGENT: Final[str] = "InvestigatorAgent"
ANALYST_AGENT: Final[str] = "AnalystAgent"
REPORTER_AGENT: Final[str] = "ReporterAgent"

# Memory types
EPISODIC_MEMORY: Final[str] = "episodic"
SEMANTIC_MEMORY: Final[str] = "semantic"
WORKING_MEMORY: Final[str] = "working"

# Investigation statuses
INVESTIGATION_PENDING: Final[str] = "pending"
INVESTIGATION_IN_PROGRESS: Final[str] = "in_progress"
INVESTIGATION_COMPLETED: Final[str] = "completed"
INVESTIGATION_FAILED: Final[str] = "failed"

# Anomaly detection
ANOMALY_LOW_CONFIDENCE: Final[float] = 0.3
ANOMALY_MEDIUM_CONFIDENCE: Final[float] = 0.6
ANOMALY_HIGH_CONFIDENCE: Final[float] = 0.8
ANOMALY_CRITICAL_CONFIDENCE: Final[float] = 0.95

# Rate limiting
DEFAULT_RATE_LIMIT_PER_MINUTE: Final[int] = 60
DEFAULT_RATE_LIMIT_PER_HOUR: Final[int] = 1000
DEFAULT_RATE_LIMIT_PER_DAY: Final[int] = 10000

# Cache keys
CACHE_KEY_PREFIX: Final[str] = "cidadao:cache:"
CACHE_KEY_INVESTIGATION: Final[str] = f"{CACHE_KEY_PREFIX}investigation:"
CACHE_KEY_TRANSPARENCY_API: Final[str] = f"{CACHE_KEY_PREFIX}transparency:"
CACHE_KEY_USER_SESSION: Final[str] = f"{CACHE_KEY_PREFIX}session:"

# File size limits
MAX_UPLOAD_SIZE_MB: Final[int] = 10
MAX_REPORT_SIZE_MB: Final[int] = 50
MAX_DATASET_SIZE_MB: Final[int] = 100

# Timeouts (seconds)
DEFAULT_API_TIMEOUT: Final[int] = 30
LLM_TIMEOUT: Final[int] = 60
TRANSPARENCY_API_TIMEOUT: Final[int] = 45
WEBSOCKET_TIMEOUT: Final[int] = 300

# Pagination
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

# Security
MIN_PASSWORD_LENGTH: Final[int] = 8
MAX_LOGIN_ATTEMPTS: Final[int] = 5
LOCKOUT_DURATION_MINUTES: Final[int] = 30
SESSION_DURATION_HOURS: Final[int] = 24

# Audit log
AUDIT_LOG_VERSION: Final[str] = "1.0"
AUDIT_HASH_CHAIN_VERSION: Final[str] = "1.0"

# ML thresholds
CLUSTERING_EPS: Final[float] = 0.5
CLUSTERING_MIN_CLUSTER_SIZE: Final[int] = 5
TIME_SERIES_CONFIDENCE_INTERVAL: Final[float] = 0.95

# Portal Transparência
TRANSPARENCY_API_VERSION: Final[str] = "v1"
TRANSPARENCY_DATE_FORMAT: Final[str] = "%d/%m/%Y"
TRANSPARENCY_MAX_RECORDS_PER_REQUEST: Final[int] = 500

# Report formats
REPORT_FORMAT_PDF: Final[str] = "pdf"
REPORT_FORMAT_EXCEL: Final[str] = "excel"
REPORT_FORMAT_CSV: Final[str] = "csv"
REPORT_FORMAT_JSON: Final[str] = "json"
REPORT_FORMAT_HTML: Final[str] = "html"

# Notification channels
NOTIFICATION_EMAIL: Final[str] = "email"
NOTIFICATION_WEBHOOK: Final[str] = "webhook"
NOTIFICATION_SMS: Final[str] = "sms"
NOTIFICATION_PUSH: Final[str] = "push"


class AgentStatus(str, Enum):
    """Agent status enumeration."""

    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class InvestigationPriority(str, Enum):
    """Investigation priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    """Types of anomalies detected."""

    PRICE_ANOMALY = "price_anomaly"
    SUPPLIER_ANOMALY = "supplier_anomaly"
    FREQUENCY_ANOMALY = "frequency_anomaly"
    PATTERN_ANOMALY = "pattern_anomaly"
    RELATIONSHIP_ANOMALY = "relationship_anomaly"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    GEOGRAPHICAL_ANOMALY = "geographical_anomaly"
    COMPLIANCE_ANOMALY = "compliance_anomaly"


class DataSource(str, Enum):
    """Available data sources."""

    PORTAL_TRANSPARENCIA = "portal_transparencia"
    TCU = "tcu"
    CGU = "cgu"
    RECEITA_FEDERAL = "receita_federal"
    DADOS_ABERTOS = "dados_abertos"
    USER_UPLOAD = "user_upload"
    WEB_SCRAPING = "web_scraping"


class UserRole(str, Enum):
    """User roles in the system."""

    ANONYMOUS = "anonymous"
    USER = "user"
    ANALYST = "analyst"
    AUDITOR = "auditor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ResponseStatus(str, Enum):
    """API response statuses."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class TaskStatus(str, Enum):
    """Async task statuses."""

    PENDING = "pending"
    STARTED = "started"
    RETRY = "retry"
    FAILURE = "failure"
    SUCCESS = "success"
    REVOKED = "revoked"


class ReflectionType(str, Enum):
    """Types of agent reflection."""

    QUALITY_CHECK = "quality_check"
    COMPLETENESS_CHECK = "completeness_check"
    RELEVANCE_CHECK = "relevance_check"
    ACCURACY_CHECK = "accuracy_check"
    ETHICS_CHECK = "ethics_check"


class MemoryImportance(int, Enum):
    """Memory importance levels."""

    TRIVIAL = 1
    LOW = 3
    MEDIUM = 5
    HIGH = 7
    CRITICAL = 10


# Regex patterns
REGEX_CPF: Final[str] = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
REGEX_CNPJ: Final[str] = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"
REGEX_EMAIL: Final[str] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
REGEX_PHONE: Final[str] = r"^\+?55?\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}$"

# Error messages
ERROR_INVALID_CREDENTIALS: Final[str] = "Credenciais inválidas"
ERROR_UNAUTHORIZED: Final[str] = "Não autorizado"
ERROR_NOT_FOUND: Final[str] = "Recurso não encontrado"
ERROR_RATE_LIMIT: Final[str] = "Limite de requisições excedido"
ERROR_INTERNAL_SERVER: Final[str] = "Erro interno do servidor"
ERROR_INVALID_INPUT: Final[str] = "Entrada inválida"
ERROR_TIMEOUT: Final[str] = "Tempo limite excedido"
ERROR_SERVICE_UNAVAILABLE: Final[str] = "Serviço indisponível"

# Success messages
SUCCESS_LOGIN: Final[str] = "Login realizado com sucesso"
SUCCESS_LOGOUT: Final[str] = "Logout realizado com sucesso"
SUCCESS_CREATED: Final[str] = "Recurso criado com sucesso"
SUCCESS_UPDATED: Final[str] = "Recurso atualizado com sucesso"
SUCCESS_DELETED: Final[str] = "Recurso removido com sucesso"
SUCCESS_INVESTIGATION_STARTED: Final[str] = "Investigação iniciada"
SUCCESS_REPORT_GENERATED: Final[str] = "Relatório gerado com sucesso"
