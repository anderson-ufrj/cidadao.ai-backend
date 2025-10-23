#!/usr/bin/env python3
"""
Apply Pending Database Migrations

Ensures all Alembic migrations are applied to the production database.
Run this when Railway is not automatically applying migrations.

Usage:
    python scripts/deployment/apply_pending_migrations.py
"""

import logging
import sys
from pathlib import Path

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def apply_migrations():
    """Apply all pending migrations to head."""
    try:
        # Create Alembic config
        alembic_ini = project_root / "alembic.ini"
        if not alembic_ini.exists():
            logger.error(f"alembic.ini not found at {alembic_ini}")
            return False

        alembic_cfg = Config(str(alembic_ini))

        logger.info("Checking current migration state...")
        command.current(alembic_cfg)

        logger.info("Applying pending migrations to head...")
        command.upgrade(alembic_cfg, "head")

        logger.info("✅ All migrations applied successfully!")
        command.current(alembic_cfg)

        return True

    except Exception as e:
        logger.error(f"❌ Failed to apply migrations: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = apply_migrations()
    sys.exit(0 if success else 1)
