"""
Module: core.config
Description: Application configuration management
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import will be available after initialization
from .secret_manager import SecretManager
from .vault_client import VaultConfig


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
        default="sqlite+aiosqlite:///./cidadao_ai.db",
        description="Database connection URL (PostgreSQL for production, SQLite for dev/testing)",
    )
    database_pool_size: int = Field(default=10, description="DB pool size")
    database_pool_overflow: int = Field(default=20, description="DB pool overflow")
    database_pool_timeout: int = Field(default=30, description="DB pool timeout")

    # Supabase (Optional - only needed for HuggingFace Spaces fallback)
    supabase_url: str | None = Field(
        default=None,
        description="Supabase project URL (optional, only for HuggingFace Spaces)",
    )
    supabase_service_role_key: SecretStr | None = Field(
        default=None,
        description="Supabase service role key (optional, only for HuggingFace Spaces)",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_password: SecretStr | None = Field(default=None, description="Redis password")
    redis_pool_size: int = Field(default=10, description="Redis pool size")

    # Portal Transparência API
    transparency_api_key: SecretStr | None = Field(
        default=None, description="Portal da Transparência API key"
    )
    transparency_api_base_url: str = Field(
        default="https://api.portaldatransparencia.gov.br",
        description="Portal da Transparência base URL",
    )
    transparency_api_timeout: int = Field(default=30, description="API timeout")
    transparency_api_max_retries: int = Field(default=3, description="Max retries")
    transparency_api_header_key: str = Field(
        default="chave-api-dados",
        description="Portal da Transparência API header key name",
    )

    # Dados.gov.br API Configuration
    dados_gov_api_key: SecretStr | None = Field(
        default=None, description="Dados.gov.br API key (if required)"
    )

    # LLM Configuration
    llm_provider: str = Field(
        default="groq",
        description="LLM provider (groq, together, huggingface, maritaca)",
    )
    llm_model_name: str = Field(
        default="mixtral-8x7b-32768", description="LLM model name"
    )
    llm_temperature: float = Field(default=0.7, description="LLM temperature")
    llm_max_tokens: int = Field(default=2048, description="Max tokens")
    llm_top_p: float = Field(default=0.9, description="Top-p sampling")
    llm_stream: bool = Field(default=True, description="Enable streaming")

    # Provider API Keys
    groq_api_key: SecretStr | None = Field(default=None, description="Groq API key")
    groq_api_base_url: str = Field(
        default="https://api.groq.com/openai/v1", description="Groq base URL"
    )

    together_api_key: SecretStr | None = Field(
        default=None, description="Together API key"
    )
    together_api_base_url: str = Field(
        default="https://api.together.xyz/v1", description="Together base URL"
    )

    huggingface_api_key: SecretStr | None = Field(
        default=None, description="HuggingFace API key"
    )
    huggingface_model_id: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.2", description="HuggingFace model ID"
    )

    # Maritaca AI Configuration
    maritaca_api_key: SecretStr | None = Field(
        default=None, description="Maritaca AI API key"
    )
    maritaca_api_base_url: str = Field(
        default="https://chat.maritaca.ai/api", description="Maritaca AI base URL"
    )
    maritaca_model: str = Field(
        default="sabiazinho-3",
        description="Default Maritaca AI model (sabiazinho-3, sabia-3, sabia-3-medium, sabia-3-large)",
    )

    # Anthropic Claude Configuration
    anthropic_api_key: SecretStr | None = Field(  # noqa: UP007
        default=None, description="Anthropic Claude API key"
    )
    anthropic_api_base_url: str = Field(
        default="https://api.anthropic.com", description="Anthropic API base URL"
    )
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Default Claude model (claude-sonnet-4-20250514, claude-opus-4-20250514, claude-3-7-sonnet-20250219)",
    )

    # Google Cloud Speech API Configuration (Voice Integration)
    google_credentials_path: str | None = Field(
        default=None,
        description="Path to Google Cloud service account JSON file for Speech API",
    )
    google_credentials_base64: str | None = Field(
        default=None,
        description="Base64-encoded Google Cloud service account JSON (for Railway/cloud deployments)",
    )
    google_cloud_project_id: str | None = Field(
        default=None,
        description="Google Cloud project ID for Speech API services",
    )
    google_speech_language_code: str = Field(
        default="pt-BR",
        description="Default language code for Speech-to-Text (pt-BR for Brazilian Portuguese)",
    )
    google_tts_voice_name: str = Field(
        default="pt-BR-Wavenet-A",
        description="Default Text-to-Speech voice (pt-BR-Wavenet-A: female, pt-BR-Wavenet-B: male)",
    )
    google_tts_speaking_rate: float = Field(
        default=1.0,
        description="Default TTS speaking rate (0.25-4.0, default: 1.0 is normal speed)",
    )
    google_tts_pitch: float = Field(
        default=0.0,
        description="Default TTS pitch adjustment (-20.0 to 20.0, default: 0.0 is normal pitch)",
    )

    # Vector Store
    vector_store_type: str = Field(
        default="faiss", description="Vector store type (faiss, chromadb)"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model"
    )
    embedding_dimension: int = Field(default=384, description="Embedding dimension")
    vector_index_path: Path = Field(
        default=Path("./vector_store/index.faiss"), description="Vector index path"
    )

    # ChromaDB
    chroma_persist_directory: Path = Field(
        default=Path("./chroma_db"), description="ChromaDB persist directory"
    )
    chroma_collection_name: str = Field(
        default="cidadao_memory", description="ChromaDB collection name"
    )

    # Security - REQUIRED in production
    secret_key: SecretStr = Field(description="Application secret key (REQUIRED)")
    jwt_secret_key: SecretStr = Field(description="JWT secret key (REQUIRED)")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="Access token expiry"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiry"
    )
    bcrypt_rounds: int = Field(default=12, description="Bcrypt rounds")

    # CORS
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "https://cidadao-ai-frontend.vercel.app",
            "https://cidadao-ai.vercel.app",
            "https://*.vercel.app",
            "https://neural-thinker-cidadao-ai-backend.hf.space",
            "https://*.hf.space",
            "http://cidadao-api-production.up.railway.app",
            "https://cidadao-api-production.up.railway.app",
            "https://*.railway.app",
        ],
        description="CORS allowed origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials")
    cors_allow_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
        description="Allowed methods",
    )
    cors_allow_headers: list[str] = Field(default=["*"], description="Allowed headers")
    cors_exposed_headers: list[str] = Field(
        default=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Request-ID",
            "X-Total-Count",
        ],
        description="Exposed headers",
    )
    cors_max_age: int = Field(default=3600, description="CORS max age in seconds")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Rate limit per hour")
    rate_limit_per_day: int = Field(default=10000, description="Rate limit per day")

    # IP Whitelist
    ip_whitelist_enabled: bool = Field(
        default=True, description="Enable IP whitelist in production"
    )
    ip_whitelist_strict: bool = Field(
        default=False, description="Strict mode - reject if IP unknown"
    )
    ip_whitelist_cache_ttl: int = Field(
        default=300, description="IP whitelist cache TTL seconds"
    )

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", description="Celery result backend"
    )
    celery_task_serializer: str = Field(default="json", description="Task serializer")
    celery_result_serializer: str = Field(
        default="json", description="Result serializer"
    )
    celery_accept_content: list[str] = Field(
        default=["json"], description="Accept content"
    )
    celery_timezone: str = Field(default="America/Sao_Paulo", description="Timezone")
    celery_enable_utc: bool = Field(default=True, description="Enable UTC")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    prometheus_port: int = Field(default=9090, description="Prometheus port")
    grafana_port: int = Field(default=3000, description="Grafana port")

    # OpenTelemetry
    otel_service_name: str = Field(default="cidadao-ai", description="Service name")
    otel_exporter_otlp_endpoint: str = Field(
        default="http://localhost:4317", description="OTLP endpoint"
    )
    otel_exporter_otlp_insecure: bool = Field(default=True, description="OTLP insecure")
    otel_traces_exporter: str = Field(default="otlp", description="Traces exporter")
    otel_metrics_exporter: str = Field(default="otlp", description="Metrics exporter")
    otel_logs_exporter: str = Field(default="otlp", description="Logs exporter")

    # Audit
    audit_log_enabled: bool = Field(default=True, description="Enable audit logging")
    audit_log_path: Path = Field(
        default=Path("./audit_logs"), description="Audit log path"
    )
    audit_log_rotation: str = Field(default="daily", description="Log rotation")
    audit_log_retention_days: int = Field(default=90, description="Log retention days")
    audit_hash_algorithm: str = Field(default="sha256", description="Hash algorithm")

    # Models API Configuration
    models_api_enabled: bool = Field(default=True, description="Enable models API")
    models_api_url: str = Field(
        default="https://neural-thinker-cidadao-ai-models.hf.space",
        description="Models API URL",
    )
    models_api_timeout: int = Field(
        default=30, description="Models API timeout seconds"
    )
    models_fallback_local: bool = Field(
        default=True, description="Use local ML as fallback"
    )
    models_circuit_breaker_failures: int = Field(
        default=3, description="Max failures before circuit break"
    )

    # ML Configuration
    anomaly_detection_threshold: float = Field(
        default=0.8, description="Anomaly detection threshold"
    )
    clustering_min_samples: int = Field(default=5, description="Min clustering samples")
    time_series_seasonality: str = Field(default="yearly", description="Seasonality")
    explainer_max_samples: int = Field(default=100, description="Max explainer samples")

    # Cache
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL")
    cache_max_size: int = Field(default=1000, description="Max cache size")

    # Compression
    compression_enabled: bool = Field(
        default=True, description="Enable response compression"
    )
    compression_min_size: int = Field(
        default=1024, description="Min size to compress (bytes)"
    )
    compression_gzip_level: int = Field(
        default=6, description="Gzip compression level (1-9)"
    )
    compression_brotli_quality: int = Field(
        default=4, description="Brotli quality (0-11)"
    )
    compression_algorithms: list[str] = Field(
        default=["gzip", "br", "deflate"], description="Enabled compression algorithms"
    )

    # Feature Flags
    enable_fine_tuning: bool = Field(default=False, description="Enable fine-tuning")
    enable_autonomous_crawling: bool = Field(
        default=False, description="Enable crawling"
    )
    enable_advanced_visualizations: bool = Field(
        default=False, description="Advanced viz"
    )
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

    def dict_for_logging(self) -> dict[str, Any]:
        """Get safe dict for logging (no secrets)."""
        data = self.model_dump()
        # Remove sensitive fields
        sensitive_fields = [
            "secret_key",
            "jwt_secret_key",
            "transparency_api_key",
            "groq_api_key",
            "together_api_key",
            "huggingface_api_key",
            "maritaca_api_key",
            "anthropic_api_key",
            "redis_password",
            "database_url",
            "supabase_service_role_key",
            "google_credentials_path",
            "google_cloud_project_id",
        ]
        for field in sensitive_fields:
            if field in data:
                data[field] = "***REDACTED***"
        return data

    @classmethod
    async def from_vault(cls, vault_config: VaultConfig | None = None) -> "Settings":
        """
        Create Settings instance with secrets loaded from Vault

        This method initializes a SecretManager with Vault integration
        and loads secrets with proper fallback to environment variables.
        """
        # Create vault config from environment if not provided
        if vault_config is None:
            vault_config = VaultConfig(
                url=os.getenv("VAULT_URL", "http://localhost:8200"),
                token=os.getenv("VAULT_TOKEN"),
                namespace=os.getenv("VAULT_NAMESPACE"),
                secret_path=os.getenv("VAULT_SECRET_PATH", "secret/cidadao-ai"),
                fallback_to_env=os.getenv("VAULT_FALLBACK_TO_ENV", "true").lower()
                == "true",
                require_vault=os.getenv("VAULT_REQUIRE", "false").lower() == "true",
            )

        # Initialize secret manager
        secret_manager = SecretManager(vault_config)
        await secret_manager.initialize()

        # Load all secret schemas
        database_secrets = await secret_manager.get_secrets_schema("database")
        jwt_secrets = await secret_manager.get_secrets_schema("jwt")
        api_secrets = await secret_manager.get_secrets_schema("api_keys")
        app_secrets = await secret_manager.get_secrets_schema("application")
        redis_secrets = await secret_manager.get_secrets_schema("redis")
        infra_secrets = await secret_manager.get_secrets_schema("infrastructure")

        # Build configuration data
        config_data = {}

        # Core application
        if app_secrets and app_secrets.secret_key:
            config_data["secret_key"] = app_secrets.secret_key

        # JWT configuration
        if jwt_secrets:
            if jwt_secrets.secret_key:
                config_data["jwt_secret_key"] = jwt_secrets.secret_key
            config_data["jwt_algorithm"] = jwt_secrets.algorithm
            config_data["jwt_access_token_expire_minutes"] = (
                jwt_secrets.access_token_expire_minutes
            )
            config_data["jwt_refresh_token_expire_days"] = (
                jwt_secrets.refresh_token_expire_days
            )

        # Database configuration
        if database_secrets and database_secrets.url:
            config_data["database_url"] = database_secrets.url

        # Redis configuration
        if redis_secrets:
            config_data["redis_url"] = redis_secrets.url
            if redis_secrets.password:
                config_data["redis_password"] = redis_secrets.password

        # API Keys
        if api_secrets:
            if api_secrets.transparency_api_key:
                config_data["transparency_api_key"] = api_secrets.transparency_api_key
            if api_secrets.groq_api_key:
                config_data["groq_api_key"] = api_secrets.groq_api_key
            if api_secrets.together_api_key:
                config_data["together_api_key"] = api_secrets.together_api_key
            if api_secrets.huggingface_api_key:
                config_data["huggingface_api_key"] = api_secrets.huggingface_api_key
            if (
                hasattr(api_secrets, "dados_gov_api_key")
                and api_secrets.dados_gov_api_key
            ):
                config_data["dados_gov_api_key"] = api_secrets.dados_gov_api_key

        # Create Settings instance with secrets
        # Environment variables will still be used for non-secret configuration
        settings = cls(**config_data)

        # Store reference to secret manager for cleanup
        settings._secret_manager = secret_manager

        return settings

    async def close_vault_connection(self):
        """Close Vault connection if it exists"""
        if hasattr(self, "_secret_manager") and self._secret_manager:
            await self._secret_manager.close()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


async def get_settings_with_vault(
    vault_config: VaultConfig | None = None,
) -> Settings:
    """Get settings instance with Vault integration"""
    return await Settings.from_vault(vault_config)


# Global settings instance
settings = get_settings()
