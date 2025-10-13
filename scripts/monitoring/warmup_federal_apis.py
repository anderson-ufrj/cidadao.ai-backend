#!/usr/bin/env python3
"""
Federal APIs Warm-up Job

Periodically calls Federal API endpoints to:
- Keep metrics updated in Prometheus
- Validate API availability
- Pre-warm caches

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
Date: 2025-10-13

Usage:
    # Run once
    python scripts/monitoring/warmup_federal_apis.py

    # Run continuously (every 5 minutes)
    python scripts/monitoring/warmup_federal_apis.py --daemon

    # Custom interval
    python scripts/monitoring/warmup_federal_apis.py --daemon --interval 300
"""

import argparse
import asyncio
import logging
import sys
import time
from datetime import datetime
from typing import Any

import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
HTTP_OK = 200
BACKEND_URL = "http://localhost:8000"

# Warm-up endpoints to call
WARMUP_ENDPOINTS = [
    {
        "name": "IBGE States",
        "method": "GET",
        "url": f"{BACKEND_URL}/api/v1/federal/ibge/states",
        "data": None,
    },
    {
        "name": "IBGE Municipalities (RJ)",
        "method": "POST",
        "url": f"{BACKEND_URL}/api/v1/federal/ibge/municipalities",
        "data": {"state_code": "33"},
    },
    {
        "name": "DataSUS Search",
        "method": "POST",
        "url": f"{BACKEND_URL}/api/v1/federal/datasus/search",
        "data": {"query": "saúde", "limit": 5},
    },
    {
        "name": "INEP Search (RJ)",
        "method": "POST",
        "url": f"{BACKEND_URL}/api/v1/federal/inep/search-institutions",
        "data": {"state": "RJ", "limit": 5},
    },
]


async def call_endpoint(
    client: httpx.AsyncClient, endpoint: dict[str, Any]
) -> dict[str, Any]:
    """
    Call a single endpoint and return result.

    Args:
        client: Async HTTP client
        endpoint: Endpoint configuration

    Returns:
        Dict with result details
    """
    start_time = time.time()

    try:
        if endpoint["method"] == "GET":
            response = await client.get(endpoint["url"], timeout=10.0)
        else:
            response = await client.post(
                endpoint["url"], json=endpoint["data"], timeout=10.0
            )

        elapsed = time.time() - start_time

        if response.status_code == HTTP_OK:
            logger.info(
                f"✅ {endpoint['name']}: {response.status_code} " f"({elapsed:.2f}s)"
            )
            return {
                "name": endpoint["name"],
                "status": "success",
                "status_code": response.status_code,
                "elapsed": elapsed,
            }

        logger.warning(
            f"⚠️  {endpoint['name']}: {response.status_code} " f"({elapsed:.2f}s)"
        )
        return {
            "name": endpoint["name"],
            "status": "error",
            "status_code": response.status_code,
            "elapsed": elapsed,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ {endpoint['name']}: {str(e)} ({elapsed:.2f}s)")
        return {
            "name": endpoint["name"],
            "status": "failed",
            "error": str(e),
            "elapsed": elapsed,
        }


async def warmup_cycle() -> dict[str, Any]:
    """
    Execute one warmup cycle calling all endpoints.

    Returns:
        Summary of warmup cycle
    """
    logger.info("=" * 60)
    logger.info(f"🔥 Starting Federal APIs Warm-up - {datetime.now()}")
    logger.info("=" * 60)

    results: list[dict[str, Any]] = []

    async with httpx.AsyncClient() as client:
        # Call all endpoints
        for endpoint in WARMUP_ENDPOINTS:
            result = await call_endpoint(client, endpoint)
            results.append(result)
            # Small delay between calls
            await asyncio.sleep(0.5)

    # Calculate summary
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    total_time = sum(r["elapsed"] for r in results)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_endpoints": len(results),
        "success": success_count,
        "errors": error_count,
        "failed": failed_count,
        "total_time": total_time,
        "results": results,
    }

    logger.info("=" * 60)
    logger.info("📊 Warmup Summary:")
    logger.info(f"   ✅ Success: {success_count}/{len(results)}")
    logger.info(f"   ⚠️  Errors:  {error_count}/{len(results)}")
    logger.info(f"   ❌ Failed:  {failed_count}/{len(results)}")
    logger.info(f"   ⏱️  Total:   {total_time:.2f}s")
    logger.info("=" * 60)

    return summary


async def daemon_mode(interval: int = 300):
    """
    Run warmup in daemon mode with periodic execution.

    Args:
        interval: Seconds between warmup cycles (default: 300 = 5 min)
    """
    logger.info(f"🚀 Starting daemon mode (interval: {interval}s)")

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            logger.info(f"\n🔄 Cycle #{cycle_count}")

            await warmup_cycle()

            logger.info(f"😴 Sleeping for {interval}s until next cycle...\n")
            await asyncio.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user. Exiting...")
            break
        except Exception as e:
            logger.error(f"❌ Error in daemon loop: {e}")
            logger.info(f"😴 Waiting {interval}s before retry...")
            await asyncio.sleep(interval)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Federal APIs Warm-up Job")
    parser.add_argument(
        "--daemon", action="store_true", help="Run continuously in daemon mode"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between cycles in seconds (default: 300)",
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    # Update backend URL if provided
    if args.backend_url != "http://localhost:8000":
        # Update all endpoint URLs (modifying in place is acceptable for CLI script)
        for endpoint in WARMUP_ENDPOINTS:
            endpoint["url"] = endpoint["url"].replace(
                "http://localhost:8000", args.backend_url
            )

    if args.daemon:
        await daemon_mode(interval=args.interval)
    else:
        await warmup_cycle()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        sys.exit(0)
