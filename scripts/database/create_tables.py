#!/usr/bin/env python3
"""
Create database tables.
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from src.models.base import Base
from src.models.investigation import Investigation

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./cidadao_ai.db")

async def create_tables():
    """Create all tables in the database."""
    print(f"🔧 Creating tables in: {DATABASE_URL}")

    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("\n✅ Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
