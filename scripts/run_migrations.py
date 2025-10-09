#!/usr/bin/env python3
"""
Script to run Supabase migrations on Railway deployment.

Applies SQL migrations from migrations/supabase/ directory to the Supabase database.

Author: Anderson Henrique da Silva
Created: 2025-10-09
License: Proprietary - All rights reserved
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from src.core import get_logger

logger = get_logger(__name__)


async def run_migrations():
    """Run all SQL migrations from migrations/supabase/."""

    # Get database URL from environment
    database_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

    if not database_url:
        logger.error("SUPABASE_DB_URL or DATABASE_URL environment variable required")
        logger.error("Get it from: Railway Dashboard > Your Project > Variables")
        return False

    logger.info(f"Connecting to database...")

    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        logger.info("✅ Connected to Supabase PostgreSQL")

        # Get migrations directory
        migrations_dir = Path(__file__).parent.parent / "migrations" / "supabase"

        if not migrations_dir.exists():
            logger.error(f"Migrations directory not found: {migrations_dir}")
            return False

        # Find all SQL migration files
        migration_files = sorted(migrations_dir.glob("*.sql"))

        if not migration_files:
            logger.warning("No migration files found")
            return True

        logger.info(f"Found {len(migration_files)} migration files")

        # Apply each migration
        for migration_file in migration_files:
            logger.info(f"📝 Applying migration: {migration_file.name}")

            # Read migration SQL
            migration_sql = migration_file.read_text()

            try:
                # Execute migration
                await conn.execute(migration_sql)
                logger.info(f"✅ Migration applied: {migration_file.name}")

            except asyncpg.exceptions.PostgresError as e:
                # Check if error is due to already existing objects
                if "already exists" in str(e).lower():
                    logger.warning(f"⚠️  Migration already applied (skipping): {migration_file.name}")
                else:
                    logger.error(f"❌ Migration failed: {migration_file.name}")
                    logger.error(f"Error: {e}")
                    raise

        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)

        logger.info(f"\n📊 Database tables ({len(tables)}):")
        for table in tables:
            logger.info(f"   - {table['table_name']}")

        # Check investigations table specifically
        investigations_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'investigations'
            )
        """)

        if investigations_exists:
            logger.info("\n✅ Investigations table exists!")

            # Get table stats
            count = await conn.fetchval("SELECT COUNT(*) FROM investigations")
            logger.info(f"   Records: {count}")

        else:
            logger.error("\n❌ Investigations table not found!")
            return False

        await conn.close()
        logger.info("\n🎉 All migrations applied successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        return False


async def verify_connection():
    """Verify Supabase connection before running migrations."""

    database_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

    if not database_url:
        logger.error("❌ SUPABASE_DB_URL or DATABASE_URL not set")
        logger.info("\nTo set up Railway + Supabase:")
        logger.info("1. Go to Railway Dashboard")
        logger.info("2. Select your project")
        logger.info("3. Go to Variables")
        logger.info("4. Add: SUPABASE_DB_URL=postgresql://...")
        logger.info("5. Get URL from: Supabase Dashboard > Settings > Database > Connection string")
        return False

    try:
        conn = await asyncpg.connect(database_url, timeout=10)
        version = await conn.fetchval("SELECT version()")
        await conn.close()

        logger.info("✅ Database connection verified")
        logger.info(f"   PostgreSQL version: {version.split(',')[0]}")
        return True

    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        logger.info("\nTroubleshooting:")
        logger.info("- Check if SUPABASE_DB_URL is correct")
        logger.info("- Verify Supabase project is active")
        logger.info("- Check network/firewall settings")
        logger.info("- Railway should allow port 5432 by default")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("Cidadão.AI - Supabase Migrations Runner")
    print("Railway Deployment")
    print("=" * 60)
    print()

    # Verify connection first
    print("Step 1: Verifying database connection...")
    if not asyncio.run(verify_connection()):
        print("\n❌ Connection verification failed")
        sys.exit(1)

    print("\nStep 2: Running migrations...")
    success = asyncio.run(run_migrations())

    if success:
        print("\n✅ SUCCESS: All migrations applied!")
        print("\nNext steps:")
        print("1. Restart your Railway deployment")
        print("2. Check logs: railway logs")
        print("3. Test API: curl https://your-app.railway.app/health")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Migrations failed")
        print("\nCheck logs above for errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
