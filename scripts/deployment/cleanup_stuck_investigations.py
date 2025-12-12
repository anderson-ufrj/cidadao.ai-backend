#!/usr/bin/env python3
"""
Cleanup stuck investigations script.

This script identifies and fixes investigations that are stuck in 'running'
status, typically because the Celery worker was not running.

Usage:
    python scripts/deployment/cleanup_stuck_investigations.py

Options:
    --dry-run    Show what would be changed without making changes
    --hours N    Consider investigations stuck after N hours (default: 1)
    --force      Mark stuck investigations as failed instead of cancelled

Author: Anderson H. Silva
Date: 2025-12-12
"""

import argparse
import asyncio
import os
import sys
from datetime import UTC, datetime, timedelta

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


async def cleanup_stuck_investigations(
    hours_threshold: int = 1, dry_run: bool = False, mark_failed: bool = False
):
    """Find and cleanup stuck investigations."""
    from sqlalchemy import select, update

    from src.db.simple_session import get_db_session
    from src.models.investigation import Investigation

    print("=" * 60)
    print("Cidadão.AI - Cleanup Stuck Investigations")
    print("=" * 60)

    cutoff_time = datetime.now(UTC) - timedelta(hours=hours_threshold)
    print(f"Looking for investigations stuck since: {cutoff_time}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Action: {'Mark as FAILED' if mark_failed else 'Mark as CANCELLED'}")
    print("-" * 60)

    async with get_db_session() as db:
        # Find stuck investigations
        query = (
            select(Investigation)
            .where(
                Investigation.status.in_(["running", "pending", "processing"]),
                Investigation.created_at < cutoff_time,
            )
            .order_by(Investigation.created_at.asc())
        )

        result = await db.execute(query)
        stuck = result.scalars().all()

        if not stuck:
            print("✅ No stuck investigations found!")
            return

        print(f"Found {len(stuck)} stuck investigation(s):\n")

        for inv in stuck:
            age = datetime.now(UTC) - inv.created_at.replace(tzinfo=UTC)
            print(f"  ID: {inv.id[:8]}...")
            print(f"  Query: {inv.query[:50]}...")
            print(f"  Status: {inv.status}")
            print(f"  Phase: {inv.current_phase}")
            print(f"  Progress: {inv.progress * 100:.1f}%")
            print(f"  Age: {age}")
            print()

        if dry_run:
            print("DRY RUN - No changes made")
            return

        # Update stuck investigations
        new_status = "failed" if mark_failed else "cancelled"
        error_message = (
            "Investigation timed out - Celery worker was not running. "
            "Please retry the investigation."
        )

        update_stmt = (
            update(Investigation)
            .where(
                Investigation.status.in_(["running", "pending", "processing"]),
                Investigation.created_at < cutoff_time,
            )
            .values(
                status=new_status,
                completed_at=datetime.now(UTC),
                error_message=error_message,
            )
        )

        await db.execute(update_stmt)
        await db.commit()

        print(f"✅ Updated {len(stuck)} investigation(s) to '{new_status}'")


async def show_investigation_stats():
    """Show current investigation statistics."""
    from sqlalchemy import func, select

    from src.db.simple_session import get_db_session
    from src.models.investigation import Investigation

    print("\n📊 Investigation Statistics:")
    print("-" * 40)

    async with get_db_session() as db:
        # Count by status
        query = select(
            Investigation.status, func.count(Investigation.id).label("count")
        ).group_by(Investigation.status)

        result = await db.execute(query)
        stats = result.fetchall()

        total = 0
        for status, count in stats:
            print(f"  {status}: {count}")
            total += count

        print("  ---")
        print(f"  TOTAL: {total}")


def main():
    parser = argparse.ArgumentParser(
        description="Cleanup stuck investigations in the database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=1,
        help="Consider investigations stuck after N hours (default: 1)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Mark stuck investigations as failed instead of cancelled",
    )
    parser.add_argument(
        "--stats-only", action="store_true", help="Only show statistics, don't cleanup"
    )

    args = parser.parse_args()

    async def run():
        if args.stats_only:
            await show_investigation_stats()
        else:
            await cleanup_stuck_investigations(
                hours_threshold=args.hours, dry_run=args.dry_run, mark_failed=args.force
            )
            await show_investigation_stats()

    asyncio.run(run())


if __name__ == "__main__":
    main()
