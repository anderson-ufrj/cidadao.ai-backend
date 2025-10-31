#!/usr/bin/env python3
"""
Script to optimize database performance.

This script can be run manually or scheduled via cron to:
- Analyze and create missing indexes
- Update table statistics
- Vacuum tables with high dead tuple ratio
- Generate performance reports

Usage:
    python scripts/optimize_database.py [options]

Options:
    --dry-run       Show what would be done without making changes
    --analyze-only  Only analyze, don't make any changes
    --force         Force optimization even if recently done
"""

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import get_logger
from src.db.session import get_session
from src.services.database_optimization_service import database_optimization_service

logger = get_logger(__name__)


async def main(args):
    """Main optimization routine."""
    logger.info(
        "database_optimization_started",
        dry_run=args.dry_run,
        analyze_only=args.analyze_only,
    )

    async with get_session() as session:
        # 1. Analyze slow queries
        logger.info("Analyzing slow queries...")
        slow_queries = await database_optimization_service.analyze_slow_queries(
            session=session, limit=50
        )

        print("\n=== SLOW QUERIES ANALYSIS ===")
        print(f"Found {len(slow_queries)} slow queries")

        for i, analysis in enumerate(slow_queries[:10], 1):
            print(f"\n{i}. Query (exec time: {analysis.execution_time:.2f}s):")
            print(f"   {analysis.query[:100]}...")
            print(f"   Calls: {analysis.plan.get('calls', 0)}")
            print(f"   Suggestions: {', '.join(analysis.suggestions)}")

        # 2. Check missing indexes
        logger.info("Checking for missing indexes...")
        missing_indexes = await database_optimization_service.create_missing_indexes(
            session=session, dry_run=True
        )

        print("\n=== MISSING INDEXES ===")
        print(f"Found {len(missing_indexes)} missing indexes")

        for idx in missing_indexes:
            print(f"\n- Table: {idx['table']}, Column: {idx['column']}")
            print(f"  Reason: {idx['reason']}")
            print(f"  Command: {idx['command']}")

        # 3. Create indexes if not in analyze-only mode
        if not args.analyze_only and missing_indexes:
            if args.dry_run:
                print("\n[DRY RUN] Would create the above indexes")
            else:
                print("\nCreating missing indexes...")
                created_indexes = (
                    await database_optimization_service.create_missing_indexes(
                        session=session, dry_run=False
                    )
                )

                created_count = sum(
                    1 for idx in created_indexes if idx.get("status") == "created"
                )
                print(f"Created {created_count} indexes")

        # 4. Update statistics
        if not args.analyze_only:
            if args.dry_run:
                print("\n[DRY RUN] Would update table statistics")
            else:
                print("\nUpdating table statistics...")
                stats_result = (
                    await database_optimization_service.optimize_table_statistics(
                        session=session
                    )
                )

                print(f"Analyzed {len(stats_result['analyzed'])} tables")
                print(f"Vacuumed {len(stats_result['vacuumed'])} tables")

        # 5. Get database stats
        print("\n=== DATABASE STATISTICS ===")
        db_stats = await database_optimization_service.get_database_stats(session)

        print(f"Database size: {db_stats['database_size']['pretty']}")
        print(f"Cache hit ratio: {db_stats['cache_hit_ratio']['ratio']:.1%}")
        print(
            f"Active connections: {db_stats['connections']['active']}/{db_stats['connections']['total']}"
        )

        print("\nLargest tables:")
        for table in db_stats["largest_tables"][:5]:
            print(
                f"- {table['table']}: {table['size_pretty']} ({table['row_count']} rows)"
            )

        # 6. Generate report
        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "slow_queries": len(slow_queries),
            "missing_indexes": len(missing_indexes),
            "created_indexes": (
                created_count if not args.analyze_only and not args.dry_run else 0
            ),
            "database_size": db_stats["database_size"]["pretty"],
            "cache_hit_ratio": db_stats["cache_hit_ratio"]["ratio"],
        }

        # Save report
        report_path = Path("logs/database_optimization_report.json")
        report_path.parent.mkdir(exist_ok=True)

        import json

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print("\n=== OPTIMIZATION COMPLETE ===")
        print(f"Report saved to: {report_path}")

        logger.info("database_optimization_completed", report=report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize database performance")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze, don't make any changes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force optimization even if recently done"
    )

    args = parser.parse_args()

    # Run optimization
    asyncio.run(main(args))
