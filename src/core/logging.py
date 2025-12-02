"""
Module: core.logging
Description: Structured logging configuration
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder

from .config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            CallsiteParameterAdder(
                parameters=[
                    CallsiteParameter.FILENAME,
                    CallsiteParameter.FUNC_NAME,
                    CallsiteParameter.LINENO,
                ]
            ),
            structlog.processors.dict_tracebacks,
            (
                structlog.processors.JSONRenderer()
                if settings.is_production
                else structlog.dev.ConsoleRenderer(colors=True)
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.enable_sql_echo else logging.WARNING
    )

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name, typically __name__

    Returns:
        Configured logger instance
    """
    return structlog.stdlib.get_logger(name)


class LogContext:
    """Context manager for adding temporary context to logs."""

    def __init__(self, logger: structlog.stdlib.BoundLogger, **kwargs: Any) -> None:
        """Initialize log context."""
        self.logger = logger
        self.context = kwargs
        self.token: Any | None = None

    def __enter__(self) -> "LogContext":
        """Enter context and bind values."""
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and unbind values."""
        if self.token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_performance(func_name: str, duration_ms: float, **kwargs: Any) -> None:
    """
    Log performance metrics.

    Args:
        func_name: Name of the function
        duration_ms: Duration in milliseconds
        **kwargs: Additional context
    """
    logger = get_logger(__name__)
    logger.info(
        "performance_metric", function=func_name, duration_ms=duration_ms, **kwargs
    )


def log_api_request(
    method: str, path: str, status_code: int, duration_ms: float, **kwargs: Any
) -> None:
    """
    Log API request details.

    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration
        **kwargs: Additional context
    """
    logger = get_logger(__name__)
    logger.info(
        "api_request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs,
    )


def log_agent_action(
    agent_name: str, action: str, success: bool, **kwargs: Any
) -> None:
    """
    Log agent actions.

    Args:
        agent_name: Name of the agent
        action: Action performed
        success: Whether action succeeded
        **kwargs: Additional context
    """
    logger = get_logger(__name__)
    logger.info(
        "agent_action", agent=agent_name, action=action, success=success, **kwargs
    )


def log_investigation(
    investigation_id: str,
    query: str,
    findings_count: int,
    confidence_score: float,
    **kwargs: Any,
) -> None:
    """
    Log investigation details.

    Args:
        investigation_id: Unique investigation ID
        query: Investigation query
        findings_count: Number of findings
        confidence_score: Confidence score
        **kwargs: Additional context
    """
    logger = get_logger(__name__)
    logger.info(
        "investigation",
        investigation_id=investigation_id,
        query=query,
        findings_count=findings_count,
        confidence_score=confidence_score,
        **kwargs,
    )


def log_error(error_type: str, error_message: str, **kwargs: Any) -> None:
    """
    Log error details.

    Args:
        error_type: Type of error
        error_message: Error message
        **kwargs: Additional context
    """
    logger = get_logger(__name__)
    logger.error(
        "error_occurred", error_type=error_type, error_message=error_message, **kwargs
    )


def create_audit_log_entry(
    action: str,
    user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    changes: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create an audit log entry.

    Args:
        action: Action performed
        user_id: User who performed action
        resource_type: Type of resource
        resource_id: ID of resource
        changes: Changes made
        **kwargs: Additional context

    Returns:
        Audit log entry dict
    """
    return {
        "action": action,
        "user_id": user_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "changes": changes,
        "metadata": kwargs,
    }
