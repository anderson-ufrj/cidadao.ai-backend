#!/usr/bin/env python3
"""
Fix database schema issues in production
"""

import asyncio
import os
from dotenv import load_dotenv
import asyncpg

load_dotenv()


async def fix_database_schema():
    """Add missing columns to investigations table"""

    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL not set")
        return

    # Convert to asyncpg format if needed
    if database_url.startswith("postgresql://"):
        db_url = database_url
    elif database_url.startswith("postgres://"):
        db_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        db_url = database_url

    print(f"🔗 Connecting to database...")

    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)

        # Check if investigation_metadata column exists
        check_query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'investigations'
        AND column_name = 'investigation_metadata'
        """

        result = await conn.fetch(check_query)

        if not result:
            print("📝 Adding investigation_metadata column...")

            # Add the column
            alter_query = """
            ALTER TABLE investigations
            ADD COLUMN IF NOT EXISTS investigation_metadata JSONB DEFAULT '{}'::jsonb
            """

            await conn.execute(alter_query)

            # Create index for better performance
            index_query = """
            CREATE INDEX IF NOT EXISTS ix_investigations_metadata
            ON investigations USING gin(investigation_metadata)
            """

            await conn.execute(index_query)

            print("✅ Column investigation_metadata added successfully")
        else:
            print("✅ Column investigation_metadata already exists")

        # List all columns for verification
        list_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'investigations'
        ORDER BY ordinal_position
        """

        columns = await conn.fetch(list_query)

        print("\n📊 Current investigations table schema:")
        for col in columns:
            print(f"   - {col['column_name']}: {col['data_type']}")

        # Close connection
        await conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(fix_database_schema())