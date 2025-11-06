#!/usr/bin/env python3
"""
Test script to compare current vs lazy loading performance.
"""

import os
import shutil
import time

# Set test environment
os.environ["JWT_SECRET_KEY"] = "test"  # noqa: S105
os.environ["SECRET_KEY"] = "test"  # noqa: S105

# Performance testing threshold
LAZY_LOAD_TARGET_MS = 50  # Maximum acceptable lazy import time


def test_current_implementation() -> float:  # noqa: ANN201, PLC0415
    """Test current implementation import time."""
    print("=" * 60)
    print("TESTING CURRENT IMPLEMENTATION")
    print("=" * 60)

    start = time.time()
    from src.agents import InvestigatorAgent

    end = time.time()

    import_time = (end - start) * 1000
    print(f"Import time: {import_time:.2f}ms")

    # Test instantiation
    start = time.time()
    InvestigatorAgent()
    end = time.time()
    init_time = (end - start) * 1000
    print(f"Instantiation time: {init_time:.2f}ms")

    return import_time


def test_lazy_implementation() -> tuple[float, float]:  # noqa: ANN201, PLC0415, F841
    """Test lazy loading implementation."""
    print("\n" + "=" * 60)
    print("TESTING LAZY LOADING IMPLEMENTATION")
    print("=" * 60)

    # Backup original __init__.py
    init_path = "src/agents/__init__.py"
    lazy_path = "src/agents/__init__lazy.py"
    backup_path = "src/agents/__init__.py.backup"

    print(f"\n1. Backing up {init_path}...")
    shutil.copy(init_path, backup_path)

    print("2. Replacing with lazy version...")
    shutil.copy(lazy_path, init_path)

    try:
        # Clear module cache
        import sys

        if "src.agents" in sys.modules:
            del sys.modules["src.agents"]
        if "src.agents.zumbi" in sys.modules:
            del sys.modules["src.agents.zumbi"]
        if "src.agents.anita" in sys.modules:
            del sys.modules["src.agents.anita"]

        print("3. Testing lazy import...")
        start = time.time()
        from src.agents import AnalystAgent, InvestigatorAgent

        end = time.time()

        import_time = (end - start) * 1000
        print(f"Import time (lazy): {import_time:.2f}ms")

        # Test first access (triggers actual import)
        print("\n4. Testing first agent access...")
        start = time.time()
        InvestigatorAgent()
        end = time.time()
        first_access = (end - start) * 1000
        print(f"First access + init: {first_access:.2f}ms")

        # Test cached access
        print("\n5. Testing cached access...")
        start = time.time()
        InvestigatorAgent()
        end = time.time()
        cached_access = (end - start) * 1000
        print(f"Cached access + init: {cached_access:.2f}ms")

        # Test aliases
        print("\n6. Testing aliases...")
        from src.agents import AnitaAgent, ZumbiAgent

        print(f"ZumbiAgent alias works: {ZumbiAgent == InvestigatorAgent}")
        print(f"AnitaAgent alias works: {AnitaAgent == AnalystAgent}")

        return import_time, first_access

    finally:
        print(f"\n7. Restoring original {init_path}...")
        shutil.copy(backup_path, init_path)
        os.remove(backup_path)


def main() -> None:
    """Main test execution."""
    print("\n" + "🚀" * 30)
    print("LAZY LOADING PERFORMANCE TEST")
    print("🚀" * 30 + "\n")

    # Test current
    current_time = test_current_implementation()

    # Test lazy
    lazy_time, first_access = test_lazy_implementation()

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print("\nCurrent implementation:")
    print(f"  Import time: {current_time:.2f}ms")
    print("\nLazy loading:")
    print(f"  Initial import: {lazy_time:.2f}ms")
    print(f"  First agent access: {first_access:.2f}ms")
    print(f"  Total to first agent: {lazy_time + first_access:.2f}ms")

    print("\n✅ IMPROVEMENT:")
    speedup = (
        current_time / (lazy_time + first_access)
        if (lazy_time + first_access) > 0
        else 0
    )
    saved = current_time - (lazy_time + first_access)
    print(f"  Speedup: {speedup:.1f}x faster")
    print(f"  Time saved: {saved:.2f}ms")

    if lazy_time < LAZY_LOAD_TARGET_MS:
        print(f"\n🎯 SUCCESS: Lazy import time {lazy_time:.2f}ms < 50ms target")
    else:
        print(f"\n⚠️  WARNING: Lazy import time {lazy_time:.2f}ms > 50ms target")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
