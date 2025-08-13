"""
Secret Manager for Cidadão.AI
High-level interface for secret management with Vault integration
"""

import os
import asyncio
from typing import Dict, Any, Optional, Type, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import structlog
from pydantic import BaseModel, SecretStr, Field
import json

from .vault_client import VaultClient, VaultConfig, VaultStatus, get_vault_client

logger = structlog.get_logger(__name__)

T = TypeVar('T')


class SecretSource(Enum):
    """Source of secret value"""
    VAULT = "vault"
    ENVIRONMENT = "environment" 
    DEFAULT = "default"
    NOT_FOUND = "not_found"


@dataclass
class SecretResult(Generic[T]):
    """Result of secret retrieval"""
    value: Optional[T]
    source: SecretSource
    key: str
    cached: bool = False
    error: Optional[str] = None
    
    @property
    def found(self) -> bool:
        """Check if secret was found"""
        return self.value is not None and self.source != SecretSource.NOT_FOUND
    
    def __bool__(self) -> bool:
        return self.found


class SecretSchema(BaseModel):
    """Base class for secret schemas with validation"""
    
    class Config:
        # Don't expose secrets in string representation
        hide_input_in_errors = True
        # Allow arbitrary types for complex secrets
        arbitrary_types_allowed = True
    
    def dict_safe(self, **kwargs) -> Dict[str, Any]:
        """Get dict representation with secrets masked"""
        data = self.dict(**kwargs)
        
        # Mask SecretStr fields
        for field_name, field in self.__fields__.items():
            if field.type_ == SecretStr or (hasattr(field.type_, '__origin__') and field.type_.__origin__ is SecretStr):
                if field_name in data and data[field_name]:
                    data[field_name] = "***MASKED***"
        
        return data


class DatabaseSecrets(SecretSchema):
    """Database connection secrets"""
    url: str = Field(..., description="Database URL")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[SecretStr] = Field(None, description="Database password") 
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: Optional[str] = Field(None, description="Database name")


class JWTSecrets(SecretSchema):
    """JWT signing secrets"""
    secret_key: SecretStr = Field(..., description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiry")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiry")


class APIKeySecrets(SecretSchema):
    """External API keys"""
    transparency_api_key: Optional[SecretStr] = Field(None, description="Portal da Transparência API key")
    groq_api_key: Optional[SecretStr] = Field(None, description="Groq API key")
    together_api_key: Optional[SecretStr] = Field(None, description="Together AI API key") 
    huggingface_api_key: Optional[SecretStr] = Field(None, description="Hugging Face API key")
    openai_api_key: Optional[SecretStr] = Field(None, description="OpenAI API key")


class RedisSecrets(SecretSchema):
    """Redis connection secrets"""
    url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    password: Optional[SecretStr] = Field(None, description="Redis password")
    username: Optional[str] = Field(None, description="Redis username")


class ApplicationSecrets(SecretSchema):
    """Core application secrets"""
    secret_key: SecretStr = Field(..., description="Application secret key")
    encryption_key: Optional[SecretStr] = Field(None, description="Data encryption key")
    signing_key: Optional[SecretStr] = Field(None, description="Request signing key")


class InfrastructureSecrets(SecretSchema):
    """Infrastructure service secrets"""
    minio_access_key: Optional[str] = Field(None, description="MinIO access key")
    minio_secret_key: Optional[SecretStr] = Field(None, description="MinIO secret key")
    chroma_auth_token: Optional[SecretStr] = Field(None, description="ChromaDB auth token")
    pgadmin_password: Optional[SecretStr] = Field(None, description="PgAdmin password")


class UserCredentials(SecretSchema):
    """User account credentials (development only)"""
    admin_email: Optional[str] = Field(None, description="Admin user email")
    admin_password: Optional[SecretStr] = Field(None, description="Admin user password")
    admin_name: Optional[str] = Field(None, description="Admin user name")
    analyst_email: Optional[str] = Field(None, description="Analyst user email") 
    analyst_password: Optional[SecretStr] = Field(None, description="Analyst user password")
    analyst_name: Optional[str] = Field(None, description="Analyst user name")


class SecretManager:
    """
    High-level secret management interface
    
    Features:
    - Vault integration with fallback to environment
    - Typed secret schemas with validation
    - Intelligent caching and refresh
    - Audit logging of secret access
    - Health monitoring and metrics
    """
    
    def __init__(self, vault_config: Optional[VaultConfig] = None):
        self.vault_config = vault_config
        self._vault_client: Optional[VaultClient] = None
        self._initialized = False
        
        # Secret schemas registry
        self._schemas: Dict[str, Type[SecretSchema]] = {
            "database": DatabaseSecrets,
            "jwt": JWTSecrets, 
            "api_keys": APIKeySecrets,
            "redis": RedisSecrets,
            "application": ApplicationSecrets,
            "infrastructure": InfrastructureSecrets,
            "users": UserCredentials,
        }
        
        # Access statistics
        self._access_stats = {
            "total_requests": 0,
            "vault_hits": 0,
            "env_fallbacks": 0,
            "cache_hits": 0,
            "errors": 0
        }
        
        logger.info(
            "secret_manager_created",
            schemas=list(self._schemas.keys()),
            vault_configured=vault_config is not None
        )
    
    async def initialize(self):
        """Initialize secret manager and Vault client"""
        if self._initialized:
            return
        
        try:
            self._vault_client = await get_vault_client(self.vault_config)
            self._initialized = True
            
            logger.info(
                "secret_manager_initialized",
                vault_status=self._vault_client._status.value if self._vault_client else "not_configured"
            )
            
        except Exception as e:
            logger.error("secret_manager_initialization_failed", error=str(e))
            
            # Continue without Vault if fallback is enabled
            if not (self.vault_config and self.vault_config.require_vault):
                self._initialized = True
                logger.warning("secret_manager_fallback_mode")
            else:
                raise
    
    async def close(self):
        """Clean up resources"""
        if self._vault_client:
            await self._vault_client.close()
            self._vault_client = None
        
        self._initialized = False
        logger.info("secret_manager_closed")
    
    async def get_secret(
        self, 
        key: str, 
        default: Optional[T] = None,
        cast_to: Optional[Type[T]] = None
    ) -> SecretResult[T]:
        """
        Get a single secret value with type casting
        
        Args:
            key: Secret key (e.g., "database/password") 
            default: Default value if not found
            cast_to: Type to cast the result to
            
        Returns:
            SecretResult with value, source, and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        self._access_stats["total_requests"] += 1
        
        try:
            # Try Vault first
            if self._vault_client and self._vault_client._status in [VaultStatus.HEALTHY, VaultStatus.DEGRADED]:
                vault_value = await self._vault_client.get_secret(key)
                if vault_value is not None:
                    self._access_stats["vault_hits"] += 1
                    
                    # Cast type if requested
                    if cast_to:
                        vault_value = self._cast_value(vault_value, cast_to)
                    
                    logger.debug(
                        "secret_retrieved",
                        key=key,
                        source="vault",
                        has_value=vault_value is not None
                    )
                    
                    return SecretResult(
                        value=vault_value,
                        source=SecretSource.VAULT,
                        key=key,
                        cached=True  # Vault client handles caching
                    )
            
            # Fallback to environment
            env_key = key.upper().replace("/", "_").replace("-", "_")
            env_value = os.getenv(env_key)
            
            if env_value is not None:
                self._access_stats["env_fallbacks"] += 1
                
                # Cast type if requested
                if cast_to:
                    env_value = self._cast_value(env_value, cast_to)
                
                logger.debug(
                    "secret_retrieved",
                    key=key,
                    env_key=env_key,
                    source="environment",
                    has_value=env_value is not None
                )
                
                return SecretResult(
                    value=env_value,
                    source=SecretSource.ENVIRONMENT,
                    key=key
                )
            
            # Use default if provided
            if default is not None:
                logger.debug(
                    "secret_using_default",
                    key=key,
                    has_default=default is not None
                )
                
                return SecretResult(
                    value=default,
                    source=SecretSource.DEFAULT,
                    key=key
                )
            
            # Not found
            logger.warning("secret_not_found", key=key)
            
            return SecretResult(
                value=None,
                source=SecretSource.NOT_FOUND,
                key=key,
                error="Secret not found in any source"
            )
            
        except Exception as e:
            self._access_stats["errors"] += 1
            
            logger.error(
                "secret_retrieval_error",
                key=key,
                error=str(e)
            )
            
            return SecretResult(
                value=default,
                source=SecretSource.DEFAULT if default is not None else SecretSource.NOT_FOUND,
                key=key,
                error=str(e)
            )
    
    def _cast_value(self, value: Any, target_type: Type[T]) -> T:
        """Cast value to target type with error handling"""
        try:
            if target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == bool:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            elif target_type == str:
                return str(value)
            else:
                # Try direct casting
                return target_type(value)
                
        except (ValueError, TypeError) as e:
            logger.warning(
                "secret_cast_failed",
                value_type=type(value).__name__,
                target_type=target_type.__name__,
                error=str(e)
            )
            return value
    
    async def get_secrets_schema(self, schema_name: str) -> Optional[SecretSchema]:
        """
        Get all secrets for a specific schema with validation
        
        Args:
            schema_name: Name of the schema (e.g., "database", "jwt")
            
        Returns:
            Validated schema instance or None if schema not found
        """
        if schema_name not in self._schemas:
            logger.error("unknown_secret_schema", schema=schema_name)
            return None
        
        schema_class = self._schemas[schema_name]
        schema_data = {}
        
        # Get all fields from the schema
        for field_name, field in schema_class.__fields__.items():
            # Build secret key path
            secret_key = f"{schema_name}/{field_name}"
            
            # Get the secret
            result = await self.get_secret(secret_key)
            
            if result.found:
                schema_data[field_name] = result.value
            elif field.required:
                # Log missing required field
                logger.warning(
                    "required_secret_missing",
                    schema=schema_name,
                    field=field_name,
                    key=secret_key
                )
        
        try:
            # Validate and create schema instance
            schema_instance = schema_class(**schema_data)
            
            logger.info(
                "secret_schema_loaded",
                schema=schema_name,
                fields_loaded=len(schema_data),
                total_fields=len(schema_class.__fields__)
            )
            
            return schema_instance
            
        except Exception as e:
            logger.error(
                "secret_schema_validation_failed",
                schema=schema_name,
                error=str(e),
                data_keys=list(schema_data.keys())
            )
            return None
    
    async def set_secret(self, key: str, value: str, metadata: Optional[Dict] = None) -> bool:
        """
        Store a secret value in Vault
        
        Args:
            key: Secret key
            value: Secret value
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._vault_client:
            logger.error("vault_not_available", operation="set_secret", key=key)
            return False
        
        try:
            success = await self._vault_client.set_secret(key, value, metadata)
            
            if success:
                logger.info(
                    "secret_stored",
                    key=key,
                    has_metadata=metadata is not None
                )
            
            return success
            
        except Exception as e:
            logger.error("secret_store_failed", key=key, error=str(e))
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of secret management system"""
        status = {
            "initialized": self._initialized,
            "vault_status": "not_configured",
            "access_stats": self._access_stats.copy(),
            "schemas_available": list(self._schemas.keys())
        }
        
        if self._vault_client:
            vault_stats = self._vault_client.get_stats()
            status.update({
                "vault_status": vault_stats["status"],
                "vault_stats": vault_stats
            })
        
        return status
    
    def register_schema(self, name: str, schema_class: Type[SecretSchema]):
        """Register a custom secret schema"""
        self._schemas[name] = schema_class
        
        logger.info(
            "secret_schema_registered",
            name=name,
            fields=list(schema_class.__fields__.keys())
        )


# Global secret manager instance
_secret_manager: Optional[SecretManager] = None


async def get_secret_manager(config: Optional[VaultConfig] = None) -> SecretManager:
    """Get or create global secret manager instance"""
    global _secret_manager
    
    if _secret_manager is None:
        _secret_manager = SecretManager(config)
        await _secret_manager.initialize()
    
    return _secret_manager


async def close_secret_manager():
    """Close global secret manager"""
    global _secret_manager
    
    if _secret_manager:
        await _secret_manager.close()
        _secret_manager = None


# Convenience functions for common secret types
async def get_database_secrets() -> Optional[DatabaseSecrets]:
    """Get database secrets with validation"""
    manager = await get_secret_manager()
    return await manager.get_secrets_schema("database")


async def get_jwt_secrets() -> Optional[JWTSecrets]:
    """Get JWT secrets with validation"""
    manager = await get_secret_manager()
    return await manager.get_secrets_schema("jwt")


async def get_api_key_secrets() -> Optional[APIKeySecrets]:
    """Get API key secrets with validation"""
    manager = await get_secret_manager()
    return await manager.get_secrets_schema("api_keys")