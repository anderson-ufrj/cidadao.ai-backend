#!/usr/bin/env python3
"""
Simple script to test database connection (SQLite or PostgreSQL).
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    exit(1)

# SQLite URLs don't need conversion, PostgreSQL does
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"🔗 Connecting to database...")
print(f"   URL: {DATABASE_URL}")

async def test_connection():
    """Test database connection."""
    try:
        # Create engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,
            pool_pre_ping=True
        )

        # Test connection
        async with engine.begin() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT 1"))
            test = result.scalar()

            print(f"\n✅ Connection successful!")

            # List existing tables (works for both SQLite and PostgreSQL)
            if "sqlite" in DATABASE_URL:
                result = await conn.execute(text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table'
                    ORDER BY name
                """))
            else:
                result = await conn.execute(text("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """))

            tables = result.fetchall()
            print(f"\n📋 Existing tables ({len(tables)}):")
            for table in tables:
                print(f"   - {table[0]}")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
