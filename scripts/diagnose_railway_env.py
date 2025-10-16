#!/usr/bin/env python3
"""
Railway Environment Diagnostics
Helps identify why DATABASE_URL is not being injected.
"""

import os
import sys

print("=" * 80)
print("🔍 RAILWAY ENVIRONMENT DIAGNOSTICS")
print("=" * 80)
print()

# Check all environment variables
print("📋 ALL ENVIRONMENT VARIABLES:")
print("-" * 80)
env_vars = dict(os.environ)
for key in sorted(env_vars.keys()):
    value = env_vars[key]
    # Mask sensitive values
    if any(x in key.upper() for x in ["KEY", "SECRET", "PASSWORD", "TOKEN"]):
        value = f"{value[:8]}..." if len(value) > 8 else "***"
    print(f"{key:40} = {value}")

print()
print("=" * 80)
print("🎯 CRITICAL VARIABLES:")
print("=" * 80)

critical_vars = [
    "DATABASE_URL",
    "SUPABASE_DB_URL",
    "POSTGRES_URL",
    "POSTGRESQL_URL",
    "REDIS_URL",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
]

for var in critical_vars:
    value = os.getenv(var)
    if value:
        # Show first 40 chars for URLs
        if "URL" in var:
            masked = f"{value[:40]}..." if len(value) > 40 else value
        else:
            masked = f"{value[:12]}..." if len(value) > 12 else "***"
        print(f"✅ {var:35} = {masked}")
    else:
        print(f"❌ {var:35} = NOT SET")

print()
print("=" * 80)
print("🔍 DETECTION RESULTS:")
print("=" * 80)

# Import the detection functions
sys.path.insert(0, "/app")  # Railway app path
try:
    from src.services.investigation_service_selector import (
        _has_postgres_config,
        _has_supabase_rest_config,
        _is_huggingface_spaces,
    )

    postgres_config = _has_postgres_config()
    supabase_config = _has_supabase_rest_config()
    is_hf = _is_huggingface_spaces()

    print(f"Has PostgreSQL config: {'✅ YES' if postgres_config else '❌ NO'}")
    print(f"Has Supabase config:   {'✅ YES' if supabase_config else '❌ NO'}")
    print(f"Is HuggingFace Spaces: {'✅ YES' if is_hf else '❌ NO'}")

    print()
    if postgres_config:
        print("🎉 PostgreSQL should be used!")
    elif is_hf and supabase_config:
        print("🚀 Supabase REST should be used!")
    else:
        print("⚠️  IN-MEMORY will be used (no persistence)!")

except Exception as e:
    print(f"❌ Error importing detection functions: {e}")

print()
print("=" * 80)
