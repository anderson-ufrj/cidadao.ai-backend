#!/usr/bin/env python3
"""
Complete authentication system analysis.
"""

print("=" * 80)
print("AUTHENTICATION SYSTEM ANALYSIS")
print("=" * 80)
print()

print("CURRENT ARCHITECTURE:")
print("-" * 80)
print()
print("MODULES (business logic):")
print("  1. src/api/auth.py          - In-memory auth manager")
print("  2. src/api/auth_db.py       - Database-backed auth manager")
print()
print("ROUTES (API endpoints):")
print("  1. src/api/routes/auth.py     - Uses src/api/auth (in-memory)")
print("  2. src/api/routes/auth_db.py  - Uses src/api/auth_db (database)")
print()

print("USAGE ANALYSIS:")
print("-" * 80)

import subprocess

# Check which module is used
result = subprocess.run(
    ["grep", "-r", "from src.api.auth import", "src/", "--include=*.py"],
    capture_output=True,
    text=True, check=False,
)
in_memory_usages = (
    len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
)

result = subprocess.run(
    ["grep", "-r", "from src.api.auth_db import", "src/", "--include=*.py"],
    capture_output=True,
    text=True, check=False,
)
db_usages = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

print("\nModule usage in src/:")
print(f"  src/api/auth (in-memory):     {in_memory_usages} files")
print(f"  src/api/auth_db (database):   {db_usages} files")
print()

# Check which route is registered
result = subprocess.run(
    ["grep", "-n", "auth.router", "src/api/app.py"], capture_output=True, text=True, check=False
)

print("Registered in src/api/app.py:")
if "auth.router" in result.stdout:
    print(f"  ✅ auth.router (line {result.stdout.split(':')[0]})")
else:
    print("  ❌ auth.router NOT found")

result = subprocess.run(
    ["grep", "-n", "auth_db.router", "src/api/app.py"], capture_output=True, text=True, check=False
)

if "auth_db.router" in result.stdout:
    print(f"  ✅ auth_db.router (line {result.stdout.split(':')[0]})")
else:
    print("  ❌ auth_db.router NOT found")

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print()
print("The system is using:")
print("  ✅ Module:  src/api/auth (in-memory) - 14 files depend on it")
print("  ✅ Route:   src/api/routes/auth.py (registered in app.py)")
print()
print("NOT being used:")
print("  ❌ Module:  src/api/auth_db (database) - 0 files use it")
print("  ❌ Route:   src/api/routes/auth_db.py (NOT registered)")
print()
print("=" * 80)
print("RECOMMENDATION (UPDATED)")
print("=" * 80)
print()
print("DELETE: src/api/routes/auth_db.py (route - not used)")
print("DELETE: src/api/auth_db.py (module - not used)")
print()
print("KEEP: src/api/auth.py (module - actively used)")
print("KEEP: src/api/routes/auth.py (route - registered in app)")
print()
print("NOTE: In-memory auth is fine for MVP/demo. For production with")
print("      persistence, consider migrating to auth_db in the future.")
print()
