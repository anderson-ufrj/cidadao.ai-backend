"""
Module: core.config
Description: Application configuration management
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = Field(default="cidadao-ai", description="Application name")
    app_env: str = Field(default="development", description="Environment")
    app_version: str = Field(default="1.0.0", description="Version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of workers")
    
    # Database
    database_url: str = Field(
        default="postgresql://cidadao:cidadao123@localhost:5432/cidadao_ai",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=10, description="DB pool size")
    database_pool_overflow: int = Field(default=20, description="DB pool overflow")
    database_pool_timeout: int = Field(default=30, description="DB pool timeout")
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_password: Optional[SecretStr] = Field(default=None, description="Redis password")
    redis_pool_size: int = Field(default=10, description="Redis pool size")
    
    # Portal Transparência API
    transparency_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Portal da Transparência API key"
    )
    transparency_api_base_url: str = Field(
        default="https://api.portaldatransparencia.gov.br",
        description="Portal da Transparência base URL"
    )
    transparency_api_timeout: int = Field(default=30, description="API timeout")
    transparency_api_max_retries: int = Field(default=3, description="Max retries")
    transparency_api_header_key: str = Field(
        default="chave-api-dados",
        description="Portal da Transparência API header key name"
    )
    
    # LLM Configuration
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
    
    # Provider API Keys
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
    
    # Vector Store
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
    
    # ChromaDB
    chroma_persist_directory: Path = Field(
        default=Path("./chroma_db"),
        description="ChromaDB persist directory"
    )
    chroma_collection_name: str = Field(
        default="cidadao_memory",
        description="ChromaDB collection name"
    )
    
    # Security
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
    
    # CORS
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
    
    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend"
    )
    celery_task_serializer: str = Field(default="json", description="Task serializer")
    celery_result_serializer: str = Field(default="json", description="Result serializer")
    celery_accept_content: List[str] = Field(default=["json"], description="Accept content")
    celery_timezone: str = Field(default="America/Sao_Paulo", description="Timezone")
    celery_enable_utc: bool = Field(default=True, description="Enable UTC")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    prometheus_port: int = Field(default=9090, description="Prometheus port")
    grafana_port: int = Field(default=3000, description="Grafana port")
    
    # OpenTelemetry
    otel_service_name: str = Field(default="cidadao-ai", description="Service name")
    otel_exporter_otlp_endpoint: str = Field(
        default="http://localhost:4317",
        description="OTLP endpoint"
    )
    otel_exporter_otlp_insecure: bool = Field(default=True, description="OTLP insecure")
    otel_traces_exporter: str = Field(default="otlp", description="Traces exporter")
    otel_metrics_exporter: str = Field(default="otlp", description="Metrics exporter")
    otel_logs_exporter: str = Field(default="otlp", description="Logs exporter")
    
    # Audit
    audit_log_enabled: bool = Field(default=True, description="Enable audit logging")
    audit_log_path: Path = Field(
        default=Path("./audit_logs"),
        description="Audit log path"
    )
    audit_log_rotation: str = Field(default="daily", description="Log rotation")
    audit_log_retention_days: int = Field(default=90, description="Log retention days")
    audit_hash_algorithm: str = Field(default="sha256", description="Hash algorithm")
    
    # ML Configuration
    anomaly_detection_threshold: float = Field(
        default=0.8,
        description="Anomaly detection threshold"
    )
    clustering_min_samples: int = Field(default=5, description="Min clustering samples")
    time_series_seasonality: str = Field(default="yearly", description="Seasonality")
    explainer_max_samples: int = Field(default=100, description="Max explainer samples")
    
    # Cache
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL")
    cache_max_size: int = Field(default=1000, description="Max cache size")
    
    # Feature Flags
    enable_fine_tuning: bool = Field(default=False, description="Enable fine-tuning")
    enable_autonomous_crawling: bool = Field(default=False, description="Enable crawling")
    enable_advanced_visualizations: bool = Field(default=False, description="Advanced viz")
    enable_ethics_guard: bool = Field(default=True, description="Enable ethics guard")
    
    # Development
    enable_debug_toolbar: bool = Field(default=True, description="Debug toolbar")
    enable_sql_echo: bool = Field(default=False, description="SQL echo")
    enable_profiling: bool = Field(default=False, description="Enable profiling")
    
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
    
    @property
    def is_testing(self) -> bool:
        """Check if in testing mode."""
        return self.app_env == "testing"
    
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()