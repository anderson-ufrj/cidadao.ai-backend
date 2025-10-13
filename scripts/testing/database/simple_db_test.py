#!/usr/bin/env python3
"""Simple database connection info"""

import os
from pathlib import Path

# Load .env file manually
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

db_url = os.getenv('DATABASE_URL', 'NOT FOUND')

print("🏛️ Cidadão.AI - Database Configuration\n")
print("✅ .env file found!" if env_path.exists() else "❌ .env file not found!")
print(f"📊 DATABASE_URL: {db_url[:50]}...")
print("\n📝 Next steps:")
print("1. Go to Supabase SQL Editor")
print("2. Run the script from: scripts/setup_database.sql")
print("3. After tables are created, run: make install-dev")
print("4. Then test with: make run-dev")