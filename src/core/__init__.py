"""
Module: core
Description: Core functionality initialization
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from .config import get_settings, settings
from .constants import (
    APP_NAME,
    APP_VERSION,
    AgentStatus,
    AnomalyType,
    DataSource,
    InvestigationPriority,
    MemoryImportance,
    ReflectionType,
    ResponseStatus,
    UserRole,
)
from .exceptions import (
    AgentError,
    AgentExecutionError,
    CidadaoAIError,
    ConfigurationError,
    DataAnalysisError,
    InvestigationError,
    LLMError,
    ValidationError,
)
from .llm_pool import get_llm_pool, llm_pool
from .logging import get_logger, setup_logging

__all__ = [
    # Config
    "get_settings",
    "settings",
    # Constants
    "APP_NAME",
    "APP_VERSION",
    "AgentStatus",
    "AnomalyType",
    "DataSource",
    "InvestigationPriority",
    "MemoryImportance",
    "ReflectionType",
    "ResponseStatus",
    "UserRole",
    # Exceptions
    "CidadaoAIError",
    "AgentError",
    "AgentExecutionError",
    "DataAnalysisError",
    "InvestigationError",
    "LLMError",
    "ValidationError",
    "ConfigurationError",
    # Logging
    "get_logger",
    "setup_logging",
    # LLM Pool
    "llm_pool",
    "get_llm_pool",
]

# Initialize logging on import
setup_logging()
