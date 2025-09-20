"""
Structured logging implementation with trace context integration.

This module provides enhanced logging capabilities with automatic
trace context injection and structured log formatting.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timezone
from enum import Enum
import traceback
import sys
import threading
from pathlib import Path

from pythonjsonlogger import jsonlogger

from src.core import get_logger
from .correlation import CorrelationContext


class LogLevel(str, Enum):
    """Log levels for structured logging."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEventType(str, Enum):
    """Types of log events for categorization."""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AUDIT = "audit"
    SYSTEM = "system"
    AGENT = "agent"
    INVESTIGATION = "investigation"
    ANOMALY = "anomaly"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"


class StructuredLogRecord:
    """
    Structured log record with standardized fields.
    """
    
    def __init__(
        self,
        message: str,
        level: LogLevel,
        event_type: LogEventType,
        timestamp: Optional[datetime] = None,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        span_id: Optional[str] = None,
        component: Optional[str] = None,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        error_type: Optional[str] = None,
        error_stack: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize structured log record.
        
        Args:
            message: Log message
            level: Log level
            event_type: Type of event
            timestamp: Event timestamp (defaults to now)
            correlation_id: Correlation ID
            request_id: Request ID
            user_id: User ID
            session_id: Session ID
            span_id: Span ID
            component: Component/module name
            operation: Operation name
            duration_ms: Operation duration
            error_type: Error type for error events
            error_stack: Error stack trace
            additional_data: Additional structured data
        """
        self.message = message
        self.level = level
        self.event_type = event_type
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.correlation_id = correlation_id or CorrelationContext.get_correlation_id()
        self.request_id = request_id or CorrelationContext.get_request_id()
        self.user_id = user_id or CorrelationContext.get_user_id()
        self.session_id = session_id or CorrelationContext.get_session_id()
        self.span_id = span_id or CorrelationContext.get_span_id()
        self.component = component
        self.operation = operation
        self.duration_ms = duration_ms
        self.error_type = error_type
        self.error_stack = error_stack
        self.additional_data = additional_data or {}
        
        # Add thread and process information
        self.thread_id = threading.get_ident()
        self.thread_name = threading.current_thread().name
        self.process_id = os.getpid() if 'os' in sys.modules else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        record = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "event_type": self.event_type.value,
            "thread_id": self.thread_id,
            "thread_name": self.thread_name
        }
        
        # Add correlation fields if present
        if self.correlation_id:
            record["correlation_id"] = self.correlation_id
        if self.request_id:
            record["request_id"] = self.request_id
        if self.user_id:
            record["user_id"] = self.user_id
        if self.session_id:
            record["session_id"] = self.session_id
        if self.span_id:
            record["span_id"] = self.span_id
        
        # Add optional fields
        if self.component:
            record["component"] = self.component
        if self.operation:
            record["operation"] = self.operation
        if self.duration_ms is not None:
            record["duration_ms"] = self.duration_ms
        if self.error_type:
            record["error_type"] = self.error_type
        if self.error_stack:
            record["error_stack"] = self.error_stack
        if self.process_id:
            record["process_id"] = self.process_id
        
        # Add additional data
        if self.additional_data:
            record["data"] = self.additional_data
        
        return record
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class TraceContextFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that includes trace context.
    """
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = '%',
        validate: bool = True,
        include_trace_context: bool = True,
        service_name: str = "cidadao-ai-backend",
        service_version: str = "1.0.0"
    ):
        """
        Initialize trace context formatter.
        
        Args:
            fmt: Format string
            datefmt: Date format string
            style: Format style
            validate: Validate format
            include_trace_context: Include trace context in logs
            service_name: Service name
            service_version: Service version
        """
        super().__init__(fmt, datefmt, style, validate)
        self.include_trace_context = include_trace_context
        self.service_name = service_name
        self.service_version = service_version
    
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add service information
        log_record["service"] = {
            "name": self.service_name,
            "version": self.service_version
        }
        
        # Add timestamp in ISO format
        if "timestamp" not in log_record:
            log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Add trace context if enabled
        if self.include_trace_context:
            correlation_id = CorrelationContext.get_correlation_id()
            if correlation_id:
                log_record["correlation_id"] = correlation_id
            
            request_id = CorrelationContext.get_request_id()
            if request_id:
                log_record["request_id"] = request_id
            
            user_id = CorrelationContext.get_user_id()
            if user_id:
                log_record["user_id"] = user_id
            
            session_id = CorrelationContext.get_session_id()
            if session_id:
                log_record["session_id"] = session_id
            
            span_id = CorrelationContext.get_span_id()
            if span_id:
                log_record["span_id"] = span_id
        
        # Add thread information
        log_record["thread_id"] = threading.get_ident()
        log_record["thread_name"] = threading.current_thread().name
        
        # Add file location
        log_record["location"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
            "module": record.module
        }
        
        # Add level name
        log_record["level"] = record.levelname
        
        # Process exception information
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "stack_trace": traceback.format_exception(*record.exc_info)
            }


class StructuredLogger:
    """
    Enhanced logger with structured logging capabilities.
    """
    
    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        component: Optional[str] = None
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            level: Default log level
            component: Component name for all logs
        """
        self.name = name
        self.component = component
        self.logger = get_logger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Configure JSON formatter if not already configured
        if not any(isinstance(h.formatter, TraceContextFormatter) for h in self.logger.handlers):
            self._configure_json_logging()
    
    def _configure_json_logging(self):
        """Configure JSON logging for the logger."""
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add console handler with JSON formatter
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = TraceContextFormatter()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _log_structured(
        self,
        record: StructuredLogRecord
    ):
        """Log a structured record."""
        # Convert to standard logging extra
        extra = record.to_dict()
        message = extra.pop("message")
        level_name = extra.pop("level")
        
        # Log with appropriate level
        log_method = getattr(self.logger, level_name.lower())
        log_method(message, extra=extra)
    
    def debug(
        self,
        message: str,
        event_type: LogEventType = LogEventType.SYSTEM,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        **kwargs
    ):
        """Log debug message."""
        record = StructuredLogRecord(
            message=message,
            level=LogLevel.DEBUG,
            event_type=event_type,
            component=self.component,
            operation=operation,
            duration_ms=duration_ms,
            additional_data=kwargs
        )
        self._log_structured(record)
    
    def info(
        self,
        message: str,
        event_type: LogEventType = LogEventType.SYSTEM,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        **kwargs
    ):
        """Log info message."""
        record = StructuredLogRecord(
            message=message,
            level=LogLevel.INFO,
            event_type=event_type,
            component=self.component,
            operation=operation,
            duration_ms=duration_ms,
            additional_data=kwargs
        )
        self._log_structured(record)
    
    def warning(
        self,
        message: str,
        event_type: LogEventType = LogEventType.SYSTEM,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        **kwargs
    ):
        """Log warning message."""
        record = StructuredLogRecord(
            message=message,
            level=LogLevel.WARNING,
            event_type=event_type,
            component=self.component,
            operation=operation,
            duration_ms=duration_ms,
            additional_data=kwargs
        )
        self._log_structured(record)
    
    def error(
        self,
        message: str,
        event_type: LogEventType = LogEventType.ERROR,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        error: Optional[Exception] = None,
        **kwargs
    ):
        """Log error message."""
        error_type = None
        error_stack = None
        
        if error:
            error_type = type(error).__name__
            error_stack = traceback.format_exc()
        
        record = StructuredLogRecord(
            message=message,
            level=LogLevel.ERROR,
            event_type=event_type,
            component=self.component,
            operation=operation,
            duration_ms=duration_ms,
            error_type=error_type,
            error_stack=error_stack,
            additional_data=kwargs
        )
        self._log_structured(record)
    
    def critical(
        self,
        message: str,
        event_type: LogEventType = LogEventType.ERROR,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        error: Optional[Exception] = None,
        **kwargs
    ):
        """Log critical message."""
        error_type = None
        error_stack = None
        
        if error:
            error_type = type(error).__name__
            error_stack = traceback.format_exc()
        
        record = StructuredLogRecord(
            message=message,
            level=LogLevel.CRITICAL,
            event_type=event_type,
            component=self.component,
            operation=operation,
            duration_ms=duration_ms,
            error_type=error_type,
            error_stack=error_stack,
            additional_data=kwargs
        )
        self._log_structured(record)
    
    # Business-specific logging methods
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_agent: Optional[str] = None,
        client_ip: Optional[str] = None
    ):
        """Log HTTP request."""
        self.info(
            f"{method} {path} - {status_code}",
            event_type=LogEventType.REQUEST,
            operation="http_request",
            duration_ms=duration_ms,
            method=method,
            path=path,
            status_code=status_code,
            user_agent=user_agent,
            client_ip=client_ip
        )
    
    def log_investigation(
        self,
        investigation_id: str,
        action: str,
        query: Optional[str] = None,
        confidence_score: Optional[float] = None,
        duration_ms: Optional[float] = None
    ):
        """Log investigation event."""
        self.info(
            f"Investigation {action}: {investigation_id}",
            event_type=LogEventType.INVESTIGATION,
            operation=f"investigation_{action}",
            duration_ms=duration_ms,
            investigation_id=investigation_id,
            query=query,
            confidence_score=confidence_score
        )
    
    def log_agent_task(
        self,
        agent_name: str,
        task_type: str,
        action: str,
        duration_ms: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log agent task execution."""
        level = LogLevel.INFO if success else LogLevel.ERROR
        message = f"Agent {agent_name} {action} {task_type}"
        
        if success:
            self.info(
                message,
                event_type=LogEventType.AGENT,
                operation=f"agent_{action}",
                duration_ms=duration_ms,
                agent_name=agent_name,
                task_type=task_type,
                success=success
            )
        else:
            self.error(
                message,
                event_type=LogEventType.AGENT,
                operation=f"agent_{action}",
                duration_ms=duration_ms,
                agent_name=agent_name,
                task_type=task_type,
                success=success,
                error_message=error_message
            )
    
    def log_anomaly(
        self,
        anomaly_type: str,
        severity: str,
        confidence_score: float,
        data_source: str,
        description: str,
        investigation_id: Optional[str] = None
    ):
        """Log anomaly detection."""
        self.warning(
            f"Anomaly detected: {anomaly_type}",
            event_type=LogEventType.ANOMALY,
            operation="anomaly_detection",
            anomaly_type=anomaly_type,
            severity=severity,
            confidence_score=confidence_score,
            data_source=data_source,
            description=description,
            investigation_id=investigation_id
        )
    
    def log_database_operation(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        rows_affected: Optional[int] = None,
        success: bool = True
    ):
        """Log database operation."""
        level = LogLevel.DEBUG if success else LogLevel.ERROR
        message = f"Database {operation} on {table}"
        
        if success:
            self.debug(
                message,
                event_type=LogEventType.DATABASE,
                operation=f"db_{operation}",
                duration_ms=duration_ms,
                table=table,
                rows_affected=rows_affected,
                success=success
            )
        else:
            self.error(
                message,
                event_type=LogEventType.DATABASE,
                operation=f"db_{operation}",
                duration_ms=duration_ms,
                table=table,
                rows_affected=rows_affected,
                success=success
            )
    
    def log_cache_operation(
        self,
        operation: str,
        cache_key: str,
        hit: Optional[bool] = None,
        duration_ms: Optional[float] = None,
        cache_type: str = "redis"
    ):
        """Log cache operation."""
        self.debug(
            f"Cache {operation}: {cache_key}",
            event_type=LogEventType.CACHE,
            operation=f"cache_{operation}",
            duration_ms=duration_ms,
            cache_key=cache_key,
            cache_hit=hit,
            cache_type=cache_type
        )
    
    def log_external_api(
        self,
        service_name: str,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        success: bool = True
    ):
        """Log external API call."""
        level = LogLevel.INFO if success else LogLevel.ERROR
        message = f"External API {method} {service_name}{endpoint} - {status_code}"
        
        if success:
            self.info(
                message,
                event_type=LogEventType.EXTERNAL_API,
                operation="external_api_call",
                duration_ms=duration_ms,
                service_name=service_name,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                success=success
            )
        else:
            self.error(
                message,
                event_type=LogEventType.EXTERNAL_API,
                operation="external_api_call",
                duration_ms=duration_ms,
                service_name=service_name,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                success=success
            )
    
    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        threshold_ms: float = 1000.0,
        **metrics
    ):
        """Log performance metrics."""
        is_slow = duration_ms > threshold_ms
        level = LogLevel.WARNING if is_slow else LogLevel.DEBUG
        message = f"Performance: {operation} took {duration_ms:.2f}ms"
        
        if is_slow:
            self.warning(
                message,
                event_type=LogEventType.PERFORMANCE,
                operation=operation,
                duration_ms=duration_ms,
                threshold_ms=threshold_ms,
                slow_operation=True,
                **metrics
            )
        else:
            self.debug(
                message,
                event_type=LogEventType.PERFORMANCE,
                operation=operation,
                duration_ms=duration_ms,
                threshold_ms=threshold_ms,
                slow_operation=False,
                **metrics
            )


def get_structured_logger(
    name: str,
    component: Optional[str] = None
) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        component: Component name
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, component=component)


import os  # Add missing import