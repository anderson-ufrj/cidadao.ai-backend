#!/usr/bin/env python3
"""
Performance profiling script to identify bottlenecks.
Measures startup time, agent initialization, and API response times.
"""

import asyncio
import cProfile
import io

# Set test environment variables
import os
import pstats
import time
from datetime import datetime

os.environ["JWT_SECRET_KEY"] = "test"  # noqa: S105
os.environ["SECRET_KEY"] = "test"  # noqa: S105


async def profile_agent_initialization():
    """Profile agent initialization time."""
    print("\n" + "=" * 60)
    print("🔍 PROFILING: Agent Initialization")
    print("=" * 60)

    from src.agents import AnalystAgent, InvestigatorAgent, ReporterAgent

    agents_to_test = [
        ("Zumbi (InvestigatorAgent)", InvestigatorAgent),
        ("Anita (AnalystAgent)", AnalystAgent),
        ("Tiradentes (ReporterAgent)", ReporterAgent),
    ]

    results = []

    for agent_name, agent_class in agents_to_test:
        start = time.time()
        _ = agent_class()  # Initialize but don't need to keep reference
        end = time.time()
        elapsed = (end - start) * 1000  # ms

        results.append({"agent": agent_name, "time_ms": elapsed})

        print(f"  {agent_name}: {elapsed:.2f}ms")

    avg_time = sum(r["time_ms"] for r in results) / len(results)
    print(f"\n  📊 Average initialization: {avg_time:.2f}ms")

    return results


async def profile_agent_pool():
    """Profile agent pool operations."""
    print("\n" + "=" * 60)
    print("🔍 PROFILING: Agent Pool")
    print("=" * 60)

    try:
        from src.infrastructure.agent_pool import AgentPool

        start = time.time()
        pool = AgentPool()
        await pool.initialize()
        end = time.time()

        init_time = (end - start) * 1000
        print(f"  Pool initialization: {init_time:.2f}ms")

        # Test agent retrieval
        start = time.time()
        _ = await pool.get_agent("zumbi")
        end = time.time()

        get_time = (end - start) * 1000
        print(f"  Get agent (first call): {get_time:.2f}ms")

        # Test cached retrieval
        start = time.time()
        _ = await pool.get_agent("zumbi")
        end = time.time()

        cached_time = (end - start) * 1000
        print(f"  Get agent (cached): {cached_time:.2f}ms")
        print(f"  ⚡ Cache speedup: {get_time/cached_time:.1f}x")

    except Exception as e:
        print(f"  ❌ Error: {e}")


async def profile_imports():
    """Profile import times of heavy modules."""
    print("\n" + "=" * 60)
    print("🔍 PROFILING: Module Imports")
    print("=" * 60)

    import_tests = [
        ("FastAPI", "from fastapi import FastAPI"),
        ("SQLAlchemy", "from sqlalchemy import create_engine"),
        ("Agents", "from src.agents import InvestigatorAgent"),
        (
            "Services",
            "from src.services.investigation_service_selector import investigation_service",
        ),
        ("LLM Client", "from src.services.maritaca_client import MaritacaClient"),
    ]

    for name, import_stmt in import_tests:
        start = time.time()
        try:
            exec(import_stmt)  # noqa: S102
            end = time.time()
            elapsed = (end - start) * 1000
            print(f"  {name}: {elapsed:.2f}ms")
        except Exception as e:
            print(f"  {name}: ❌ Error - {e}")


async def profile_database_operations():
    """Profile database operations."""
    print("\n" + "=" * 60)
    print("🔍 PROFILING: Database Operations")
    print("=" * 60)

    try:
        from src.infrastructure.database import SessionLocal

        # Test connection
        start = time.time()
        session = SessionLocal()
        end = time.time()
        conn_time = (end - start) * 1000
        print(f"  Session creation: {conn_time:.2f}ms")

        # Test simple query
        start = time.time()
        _ = session.execute("SELECT 1")
        end = time.time()
        query_time = (end - start) * 1000
        print(f"  Simple query (SELECT 1): {query_time:.2f}ms")

        session.close()

    except Exception as e:
        print(f"  ℹ️  Database: {e} (expected in memory mode)")


def profile_with_cprofile(func):
    """Run function with cProfile and print stats."""
    pr = cProfile.Profile()
    pr.enable()

    result = asyncio.run(func())

    pr.disable()

    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(20)  # Top 20 slowest

    return result, s.getvalue()


async def main():
    """Main profiling routine."""
    print("\n" + "🚀" * 30)
    print("CIDADÃO.AI - PERFORMANCE PROFILING")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀" * 30)

    # Profile imports
    await profile_imports()

    # Profile agent initialization
    await profile_agent_initialization()

    # Profile agent pool
    await profile_agent_pool()

    # Profile database
    await profile_database_operations()

    print("\n" + "=" * 60)
    print("✅ PROFILING COMPLETE")
    print("=" * 60)

    print("\n📋 RECOMMENDATIONS:")
    print("  1. Agents <50ms init: ✅ Good")
    print("  2. Agents 50-100ms: ⚠️  Consider lazy loading")
    print("  3. Agents >100ms: ❌ Needs optimization")
    print("  4. Pool init <100ms: ✅ Good")
    print("  5. Cached access <1ms: ✅ Excellent")

    print("\n💡 TIP: Run with --profile-detailed for cProfile analysis")


if __name__ == "__main__":
    import sys

    if "--profile-detailed" in sys.argv:
        print("\n🔬 Running detailed cProfile analysis...")
        result, stats = profile_with_cprofile(main)
        print("\n" + "=" * 60)
        print("TOP 20 SLOWEST FUNCTIONS (cumulative time)")
        print("=" * 60)
        print(stats)
    else:
        asyncio.run(main())
