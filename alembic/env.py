"""Alembic Environment Configuration for Cidadão.AI Backend.

This module configures the Alembic migration environment for Railway PostgreSQL.
It reads the database URL from environment variables and sets up SQLAlchemy
for both online and offline migration modes.

Author: Anderson Henrique da Silva
Created: 2025-10-13
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import all models to ensure they are registered with Base
try:
    from src.models.entity_graph import (  # noqa: F401
        Base,
        EntityNode,
        EntityRelationship,
        SuspiciousNetwork,
    )
except ImportError:
    # Fallback if models not available
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

# Read DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")

if database_url:
    # PostgreSQL URLs from Railway/Supabase may use 'postgres://'
    # but SQLAlchemy requires 'postgresql://'
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Override the sqlalchemy.url from alembic.ini
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Get configuration from alembic.ini
    configuration = config.get_section(config.config_ini_section)

    # Get database URL
    db_url = configuration.get("sqlalchemy.url")

    # Ensure URL is valid
    if not db_url or db_url.startswith(("http://", "https://", "${", "None")):
        print(
            "⚠️  WARNING: No valid DATABASE_URL found. Skipping migrations.\n"
            "To enable migrations:\n"
            "1. Add PostgreSQL database in Railway dashboard\n"
            "2. DATABASE_URL will be automatically provided by Railway\n"
            "3. Redeploy the application"
        )
        return

    # Create engine
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't use connection pooling for migrations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
