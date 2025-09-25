"""
Module: core.exceptions
Description: Custom exceptions for the application
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from typing import Any, Dict, Optional


class CidadaoAIError(Exception):
    """Base exception for all Cidadão.AI errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


# Agent exceptions
class AgentError(CidadaoAIError):
    """Base exception for agent-related errors."""
    pass


class AgentInitializationError(AgentError):
    """Raised when agent initialization fails."""
    pass


class AgentExecutionError(AgentError):
    """Raised when agent execution fails."""
    pass


class AgentCommunicationError(AgentError):
    """Raised when agents fail to communicate."""
    pass


class ReflectionError(AgentError):
    """Raised when agent reflection fails."""
    pass


class DataAnalysisError(AgentError):
    """Raised when data analysis fails."""
    pass


# Investigation exceptions
class InvestigationError(CidadaoAIError):
    """Base exception for investigation errors."""
    pass


class InvestigationNotFoundError(InvestigationError):
    """Raised when investigation is not found."""
    pass


class InvestigationTimeoutError(InvestigationError):
    """Raised when investigation times out."""
    pass


class InvestigationValidationError(InvestigationError):
    """Raised when investigation input is invalid."""
    pass


# Data source exceptions
class DataSourceError(CidadaoAIError):
    """Base exception for data source errors."""
    pass


class TransparencyAPIError(DataSourceError):
    """Raised when Portal Transparência API fails."""
    pass


class DataNotFoundError(DataSourceError):
    """Raised when requested data is not found."""
    pass


class DataValidationError(DataSourceError):
    """Raised when data validation fails."""
    pass


# LLM exceptions
class LLMError(CidadaoAIError):
    """Base exception for LLM-related errors."""
    pass


class LLMProviderError(LLMError):
    """Raised when LLM provider fails."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limit is exceeded."""
    pass


class LLMResponseError(LLMError):
    """Raised when LLM response is invalid."""
    pass


# Memory exceptions
class MemoryError(CidadaoAIError):
    """Base exception for memory-related errors."""
    pass


class MemoryStorageError(MemoryError):
    """Raised when memory storage fails."""
    pass


class MemoryRetrievalError(MemoryError):
    """Raised when memory retrieval fails."""
    pass


class MemoryCorruptionError(MemoryError):
    """Raised when memory is corrupted."""
    pass


# Authentication exceptions
class AuthenticationError(CidadaoAIError):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when token has expired."""
    pass


class UnauthorizedError(AuthenticationError):
    """Raised when user is not authorized."""
    pass


class AccountLockedError(AuthenticationError):
    """Raised when account is locked."""
    pass


# API exceptions
class APIError(CidadaoAIError):
    """Base exception for API errors."""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    pass


class ValidationError(APIError):
    """Raised when input validation fails."""
    pass


class ResourceNotFoundError(APIError):
    """Raised when resource is not found."""
    pass


class ConflictError(APIError):
    """Raised when there's a conflict."""
    pass


# Configuration exceptions
class ConfigurationError(CidadaoAIError):
    """Base exception for configuration errors."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration is invalid."""
    pass


# Cache exceptions
class CacheError(CidadaoAIError):
    """Base exception for cache-related errors."""
    pass


# Database exceptions
class DatabaseError(CidadaoAIError):
    """Base exception for database errors."""
    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass


class QueryError(DatabaseError):
    """Raised when database query fails."""
    pass


class IntegrityError(DatabaseError):
    """Raised when database integrity is violated."""
    pass


# ML/Analysis exceptions
class AnalysisError(CidadaoAIError):
    """Base exception for analysis errors."""
    pass


class AnomalyDetectionError(AnalysisError):
    """Raised when anomaly detection fails."""
    pass


class InsufficientDataError(AnalysisError):
    """Raised when there's insufficient data for analysis."""
    pass


class ModelNotFoundError(AnalysisError):
    """Raised when ML model is not found."""
    pass


# Audit exceptions
class AuditError(CidadaoAIError):
    """Base exception for audit errors."""
    pass


class AuditLogError(AuditError):
    """Raised when audit logging fails."""
    pass


class AuditVerificationError(AuditError):
    """Raised when audit verification fails."""
    pass


# Ethics exceptions
class EthicsError(CidadaoAIError):
    """Base exception for ethics-related errors."""
    pass


class EthicsViolationError(EthicsError):
    """Raised when ethics guidelines are violated."""
    pass


class PrivacyViolationError(EthicsError):
    """Raised when privacy is violated."""
    pass


# Notification exceptions
class NotificationError(CidadaoAIError):
    """Base exception for notification errors."""
    pass


class EmailError(NotificationError):
    """Raised when email sending fails."""
    pass


class WebhookError(NotificationError):
    """Raised when webhook fails."""
    pass


# File handling exceptions
class FileError(CidadaoAIError):
    """Base exception for file-related errors."""
    pass


class FileSizeError(FileError):
    """Raised when file size exceeds limit."""
    pass


class FileTypeError(FileError):
    """Raised when file type is not allowed."""
    pass


class FileProcessingError(FileError):
    """Raised when file processing fails."""
    pass


# External service exceptions
class ExternalServiceError(CidadaoAIError):
    """Base exception for external service errors."""
    pass


class ServiceUnavailableError(ExternalServiceError):
    """Raised when external service is unavailable."""
    pass


class ServiceTimeoutError(ExternalServiceError):
    """Raised when external service times out."""
    pass


# Report generation exceptions
class ReportError(CidadaoAIError):
    """Base exception for report errors."""
    pass


class ReportGenerationError(ReportError):
    """Raised when report generation fails."""
    pass


class ReportTemplateError(ReportError):
    """Raised when report template is invalid."""
    pass


# Orchestration exceptions
class OrchestrationError(CidadaoAIError):
    """Base exception for orchestration errors."""
    pass


# Custom HTTP exception handlers
def create_error_response(
    error: CidadaoAIError,
    status_code: int = 500
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error: The exception instance
        status_code: HTTP status code
        
    Returns:
        Error response dictionary
    """
    return {
        "status": "error",
        "status_code": status_code,
        "error": error.to_dict()
    }