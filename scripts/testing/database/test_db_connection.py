#!/usr/bin/env python3
"""Test database connection to Supabase PostgreSQL"""

import asyncio
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


async def test_connection():
    """Test database connection and basic operations"""

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables!")
        return False

    print("🔍 Testing connection to database...")
    print(f"   URL: {db_url[:30]}...")  # Show only first part for security

    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✅ Successfully connected to database!")

        # Test query
        version = await conn.fetchval("SELECT version()")
        print(f"📊 PostgreSQL version: {version.split(',')[0]}")

        # Check if tables exist
        tables = await conn.fetch(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """
        )

        print(f"\n📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table['tablename']}")

        # Check users table
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"\n👥 Users in database: {user_count}")

        # Close connection
        await conn.close()
        print("\n✅ All tests passed! Database is ready.")
        return True

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if DATABASE_URL is correct in .env file")
        print("2. Verify password encoding (special chars need URL encoding)")
        print("3. Ensure you've run the setup SQL script in Supabase")
        print("4. Check if your IP is allowed in Supabase settings")
        return False


if __name__ == "__main__":
    print("🏛️ Cidadão.AI - Database Connection Test\n")
    asyncio.run(test_connection())
