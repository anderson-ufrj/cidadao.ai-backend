#!/usr/bin/env python3
"""
Script to fix database schema on Railway
"""

import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

async def fix_database():
    # Get DATABASE_URL from environment (Railway provides this)
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Convert postgresql:// to postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    print(f"🔗 Connecting to database...")
    
    try:
        engine = create_async_engine(database_url)
        
        # Fix id column type
        print("🔧 Converting id column from UUID to VARCHAR(255)...")
        async with engine.begin() as conn:
            await conn.execute(text("""
                ALTER TABLE investigations 
                ALTER COLUMN id TYPE VARCHAR(255);
            """))
        
        print("✅ Column type changed successfully!")
        
        # Verify
        print("🔍 Verifying the change...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'investigations' 
                AND column_name = 'id';
            """))
            row = result.fetchone()
            if row:
                print(f"✅ Verification:")
                print(f"   Column: {row[0]}")
                print(f"   Type: {row[1]}")
                print(f"   Max Length: {row[2]}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_database())
